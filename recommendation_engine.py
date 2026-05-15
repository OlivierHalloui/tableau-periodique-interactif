"""
recommendation_engine.py — Moteur de recommandations computationnelles.
Рекомендательный движок вычислительной химии.

API principale : recommend(z, block, method_key, prop_key, lang) -> dict
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional
import json

DATA_DIR = Path(__file__).parent / "data"


# ─────────────────────────── loaders (cached) ──────────────────────────

@lru_cache(maxsize=None)
def _load(name: str) -> dict | list:
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


def _rec() -> dict:  return _load("recommendations.json")   # type: ignore[return-value]
def _sw()  -> dict:  return _load("software.json")          # type: ignore[return-value]
def _nmr() -> dict:  return _load("nmr_isotopes.json")      # type: ignore[return-value]
def _orb() -> dict:  return _load("orbital_info.json")      # type: ignore[return-value]


# ─────────────────────────── basis selection ────────────────────────────

def _z_to_basis_cat(z: int) -> dict:
    cats = _rec()["basis_categories"]
    for cat in cats.values():
        if cat["z_min"] <= z <= cat["z_max"]:
            return cat
    return cats["SHE"]


def _select_basis(z: int, prop_key: str) -> tuple[str, Optional[str], Optional[str]]:
    """Returns (basis, aux_basis, ecp)."""
    cat = _z_to_basis_cat(z)
    prop = _rec()["properties"].get(prop_key, {})
    quality = prop.get("basis_quality", "triple_zeta")

    if quality == "nmr_special":
        basis = cat.get("nmr", cat["triple_zeta"])
        ecp = None  # NMR (GIAO) exige un calcul tous-électrons
    elif quality == "epr_special":
        basis = cat.get("epr", cat["triple_zeta"])
        ecp = None  # RPE exige un calcul tous-électrons
    elif quality == "aug_triple_zeta":
        basis = cat.get("aug", cat["triple_zeta"])
        ecp = cat.get("ecp")
    else:
        basis = cat["triple_zeta"]
        ecp = cat.get("ecp")

    return basis, cat.get("aux"), ecp


# ─────────────────────────── functional selection ───────────────────────

def _select_functional(z: int, block: str, method_key: str, prop_key: str
                        ) -> tuple[Optional[str], Optional[str]]:
    """Returns (functional, dispersion) or (None, None) for WF methods."""
    method = _rec()["methods"].get(method_key, {})
    if not method.get("needs_functional"):
        return None, None

    rules = _rec()["functional_rules"]
    best: Optional[dict] = None
    best_score = -1

    for rule in rules:
        z_ok  = rule.get("z_min", 0) <= z <= rule.get("z_max", 999)
        blk_ok = rule.get("block") is None or rule.get("block") == block
        m_ok  = method_key in rule.get("methods", [])
        p_ok  = rule.get("prop") is None or rule.get("prop") == prop_key

        if z_ok and blk_ok and m_ok and p_ok:
            score = (blk_ok and rule.get("block") is not None) + (p_ok and rule.get("prop") is not None)
            if score > best_score:
                best_score = score
                best = rule

    if best:
        return best["functional"], best.get("dispersion")
    # Fallback
    if block in ("s", "p"):
        return "PBE0-D3BJ", "D3BJ"
    if block == "d":
        return "TPSS-D3BJ", "D3BJ"
    return "TPSS-D3BJ", "D3BJ"


# ─────────────────────────── relativistic level ─────────────────────────

def _relativistic_level(z: int) -> str:
    if z <= 18: return "Négligeable"
    if z <= 36: return "Faible (optionnel)"
    if z <= 54: return "Scalaire (DKH2 / ZORA)"
    if z <= 86: return "Scalaire + spin-orbite partiel"
    return "Spin-orbite requis (X2C / 4c-DHF)"


def _relativistic_level_ru(z: int) -> str:
    if z <= 18: return "Пренебрежимо малы"
    if z <= 36: return "Слабые (учёт не обязателен)"
    if z <= 54: return "Скалярные (DKH2 / ZORA)"
    if z <= 86: return "Скалярные + частичный спин-орбитальный"
    return "Требуется спин-орбитальный (X2C / 4c-DHF)"


# ─────────────────────────── software compatibility ──────────────────────

def _compatible_software(z: int, method_key: str) -> list[dict]:
    result = []
    for key, prog in _sw().items():
        if z > prog.get("z_limit", 118):
            continue
        if method_key in prog.get("methods", []):
            result.append({
                "key": key,
                "name": prog["name"],
                "url": prog["url"],
                "free": prog.get("free_academic", False),
                "badge_color": prog.get("badge_color", "#888"),
                "label_fr": prog.get("label_fr", prog["name"]),
                "label_ru": prog.get("label_ru", prog["name"]),
            })
    return result


def _keyword_example(software_key: str, method_key: str, prop_key: str,
                      z: int, block: str) -> Optional[str]:
    prog = _sw().get(software_key, {})
    kw = prog.get("keyword_examples", {})
    # Try specific match first
    for candidate in [
        f"{method_key}+{prop_key}",
        f"{method_key}+{block}_block" if block in ("d", "f") else None,
        f"heavy_ecp" if z > 36 and software_key == "gaussian" else None,
        f"dft_hybrid+geometry",
    ]:
        if candidate and candidate in kw:
            return kw[candidate]
    return None


# ─────────────────────────── smart links ────────────────────────────────

_BSE_BASE = "https://www.basissetexchange.org/basis/{basis}/format/{fmt}/?version=1&elements={z}"
_BSE_FMT  = {"orca": "orca", "gaussian": "gaussian", "psi4": "psi4", "default": "gaussian"}

def _bse_name(basis: str) -> str:
    """Normalise basis name for BSE URL (lowercase, spaces→hyphens)."""
    return basis.lower().replace(" ", "-").split("/")[0].split(",")[0].strip()

def _smart_links(z: int, basis: str, ecp: Optional[str]) -> list[dict]:
    links: list[dict] = []
    bse_name = _bse_name(basis)

    # BSE links for each format
    for label, fmt in [("ORCA", "orca"), ("Gaussian", "gaussian"), ("Psi4", "psi4")]:
        url = _BSE_BASE.format(basis=bse_name, fmt=fmt, z=z)
        links.append({"label": f"BSE — {basis} ({label})", "url": url, "type": "basis"})

    # Stuttgart ECP if needed
    if ecp and "Stuttgart" in ecp:
        links.append({
            "label": f"Pseudopotentiels Stuttgart",
            "url": "https://www.tc.uni-koeln.de/PP/clickpse.en.html",
            "type": "ecp",
        })

    # Benchmark databases
    for k, b in _rec()["benchmark_links"].items():
        links.append({"label": b["desc_fr"][:50] + "…" if len(b["desc_fr"]) > 50 else b["desc_fr"],
                      "url": b["url"], "type": "benchmark"})
    return links


# ─────────────────────────── notes generation ───────────────────────────

def _notes(z: int, block: str, method_key: str, prop_key: str,
           basis: str, ecp: Optional[str], functional: Optional[str],
           dispersion: Optional[str], lang: str) -> str:
    orb = _orb().get(str(z), {})
    is_open = orb.get("is_open_shell", False)
    relat    = _relativistic_level(z) if lang == "fr" else _relativistic_level_ru(z)
    method   = _rec()["methods"].get(method_key, {})
    prop     = _rec()["properties"].get(prop_key, {})

    if lang == "fr":
        lines = [f"**Méthode** : {method.get('label_fr', method_key)} — complexité {method.get('scaling', '?')}"]
        lines.append(f"**Propriété** : {prop.get('label_fr', prop_key)}")
        lines.append(f"**Base** : {basis}" + (f" + {ecp}" if ecp else ""))
        if functional:
            lines.append(f"**Fonctionnelle** : {functional}" + (f" + {dispersion}" if dispersion else ""))
        lines.append(f"**Relativiste** : {relat}")
        if is_open:
            lines.append("⚠ Couche ouverte — utiliser le calcul unrestricted (UKS/ROHF)")
        if block == "f":
            lines.append("⚠ Élément f — envisager CASSCF/NEVPT2 si la multireférence est suspectée")
        if prop_key == "nmr":
            lines.append("ℹ RMN : méthode GIAO recommandée ; base spéciale pcSseg-3 ou IGLO-III")
        if prop_key == "dispersion":
            lines.append("ℹ Correction D3BJ obligatoire ; utiliser la correction counterpoise (BSSE)")
        if prop_key == "excitation":
            lines.append("ℹ TD-DFT : fonctionnelle à séparation de portée (ωB97X-D, CAM-B3LYP) préférable")
    else:  # ru
        lines = [f"**Метод**: {method.get('label_ru', method_key)} — сложность {method.get('scaling', '?')}"]
        lines.append(f"**Свойство**: {prop.get('label_ru', prop_key)}")
        lines.append(f"**Базис**: {basis}" + (f" + {ecp}" if ecp else ""))
        if functional:
            lines.append(f"**Функционал**: {functional}" + (f" + {dispersion}" if dispersion else ""))
        lines.append(f"**Релятивистика**: {relat}")
        if is_open:
            lines.append("⚠ Незакрытая оболочка — использовать unrestricted расчёт (UKS/ROHF)")
        if block == "f":
            lines.append("⚠ f-элемент — рассмотреть CASSCF/NEVPT2 при подозрении на мультиреференс")
        if prop_key == "nmr":
            lines.append("ℹ ЯМР: рекомендуется метод GIAO; специальные базисы pcSseg-3 или IGLO-III")
        if prop_key == "dispersion":
            lines.append("ℹ Поправка D3BJ обязательна; применять counterpoise-коррекцию (BSSE)")
        if prop_key == "excitation":
            lines.append("ℹ ВТ-ТФТ: предпочтительны функционалы с разделением диапазона (ωB97X-D)")

    return "\n\n".join(lines)


# ─────────────────────────── public API ─────────────────────────────────

def recommend(z: int, block: str, method_key: str, prop_key: str,
              lang: str = "fr") -> dict:
    """Calcule une recommandation complète pour (Z, bloc, méthode, propriété).

    Returns
    -------
    dict with keys: basis, aux_basis, ecp, functional, dispersion,
                    relativistic, software, links, notes, orca_snippet,
                    method_info, property_info
    """
    basis, aux, ecp   = _select_basis(z, prop_key)
    functional, disp  = _select_functional(z, block, method_key, prop_key)
    relat             = _relativistic_level(z) if lang == "fr" else _relativistic_level_ru(z)
    software          = _compatible_software(z, method_key)
    links             = _smart_links(z, basis, ecp)
    notes             = _notes(z, block, method_key, prop_key, basis, ecp, functional, disp, lang)

    # ORCA snippet from first compatible software (orca)
    orca_snippet = _keyword_example("orca", method_key, prop_key, z, block)
    gaussian_snippet = _keyword_example("gaussian", method_key, prop_key, z, block)

    return {
        "basis":          basis,
        "aux_basis":      aux,
        "ecp":            ecp,
        "functional":     functional,
        "dispersion":     disp,
        "relativistic":   relat,
        "software":       software,
        "links":          links,
        "notes":          notes,
        "orca_snippet":   orca_snippet,
        "gaussian_snippet": gaussian_snippet,
        "method_info":    _rec()["methods"].get(method_key, {}),
        "property_info":  _rec()["properties"].get(prop_key, {}),
    }


def get_nmr_isotopes(z: int) -> list[dict]:
    return _nmr().get(str(z), [])


def get_orbital_info(z: int) -> dict:
    return _orb().get(str(z), {})


def list_methods(lang: str = "fr") -> list[dict]:
    key = "label_fr" if lang == "fr" else "label_ru"
    return [{"value": k, "label": v[key]} for k, v in _rec()["methods"].items()]


def list_properties(lang: str = "fr") -> list[dict]:
    key = "label_fr" if lang == "fr" else "label_ru"
    return [{"value": k, "label": v[key]} for k, v in _rec()["properties"].items()]


# ─────────────────────────── CLI self-test ──────────────────────────────

if __name__ == "__main__":
    import pprint
    r = recommend(24, "d", "dft_hybrid", "magnetism", "fr")
    print("=== Cr (Z=24), DFT hybride, Propriétés magnétiques ===")
    print("Basis    :", r["basis"], "| ECP:", r["ecp"])
    print("Functional:", r["functional"], "| Dispersion:", r["dispersion"])
    print("Software  :", [s["name"] for s in r["software"]])
    print("ORCA      :", r["orca_snippet"])
    print("\nNotes:\n", r["notes"])
    print("\nNMR (Platine Z=78):", get_nmr_isotopes(78))
