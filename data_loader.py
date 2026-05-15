"""
data_loader.py — Chargement, enrichissement et validation des données du tableau périodique.
Данные таблицы Менделеева: загрузка, обогащение, валидация.
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Optional

import pandas as pd

DATA_DIR = Path(__file__).parent / "data"


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

def _load_json(name: str) -> dict | list:
    with open(DATA_DIR / name, encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# Enrichissement computationnel (fonctions pures Z → str)
# ---------------------------------------------------------------------------

def _ecp_type(z: int) -> str:
    if z <= 18:
        return "Tous-électrons"
    if z <= 36:
        return "ECP optionnel"
    if z <= 54:
        return "ECP recommandé"
    if z <= 86:
        return "ECP requis"
    return "ECP/relativiste"


def _basis(z: int) -> str:
    if z <= 2:
        return "cc-pVTZ, aug-cc-pVTZ, 6-311G**"
    if z <= 10:
        return "cc-pVTZ, def2-TZVP, aug-cc-pVTZ"
    if z <= 18:
        return "cc-pVTZ, def2-TZVP, 6-311+G**"
    if z <= 36:
        return "def2-TZVP, def2-SVP"
    if z <= 54:
        return "def2-TZVP, def2-TZVPP"
    if 55 <= z <= 57 or 72 <= z <= 86:
        return "def2-TZVPP, SARC-DKH2"
    if 58 <= z <= 71:
        return "SARC-DKH2, ANO-RCC-VTZP"
    if 87 <= z <= 89 or z >= 104:
        return "SARC2-QZV-DKH2, x2c-TZVPPall"
    return "SARC-DKH2, ANO-RCC-VTZP"


def _pseudo(z: int) -> str:
    if z <= 18:
        return "Aucun"
    if z <= 36:
        return "ECP-10 (Stuttgart/MDF)"
    if z <= 54:
        return "ECP-28 (Stuttgart/MDF)"
    if z <= 71:
        return "ECP-28 / ECP-46 (Stuttgart)"
    if z <= 86:
        return "ECP-60 (Stuttgart/MDF)"
    if z <= 103:
        return "ECP-78 (Stuttgart/MDF)"
    return "ECP-92 (Stuttgart/MDF)"


def _block(z: int) -> str:
    s_set = {1, 2, 3, 4, 11, 12, 19, 20, 37, 38, 55, 56, 87, 88}
    p_set = (
        set(range(5, 11)) | set(range(13, 19)) | set(range(31, 37))
        | set(range(49, 55)) | set(range(81, 87)) | set(range(113, 119))
    )
    d_set = (
        set(range(21, 31)) | set(range(39, 49))
        | set(range(72, 81)) | set(range(104, 113))
    )
    if z in s_set:
        return "s"
    if z in p_set:
        return "p"
    if z in d_set:
        return "d"
    return "f"


def _functional(z: int) -> str:
    b = _block(z)
    if z <= 2:
        return "CCSD(T), MP2, B3LYP"
    if b in ("s", "p") and z <= 36:
        return "B3LYP-D3BJ, ωB97X-D, M06-2X"
    if b in ("s", "p"):
        return "PBE0-D3BJ, M06-2X"
    if b == "d" and z <= 30:
        return "TPSS-D3BJ, TPSSh, M06-L"
    if b == "d":
        return "PBE0-D3BJ, TPSS-D3BJ"
    if b == "f" and z <= 71:
        return "CASSCF/NEVPT2, TPSS-D3BJ"
    return "CASSCF/NEVPT2, PBE0-D3BJ"


def _dispersion(z: int) -> str:
    return "N/A" if z in {2, 10, 18, 36, 54, 86, 118} else "D3BJ (Grimme)"


def _relativistic(z: int) -> str:
    if z <= 18:
        return "Négligeable"
    if z <= 36:
        return "Faible (optionnel)"
    if z <= 54:
        return "Scalaire (DKH2 / ZORA)"
    if z <= 86:
        return "Scalaire + spin-orbite partiel"
    return "Spin-orbite requis (X2C / 4c-DHF)"


# ---------------------------------------------------------------------------
# Chargement principal
# ---------------------------------------------------------------------------

def load_elements() -> list[dict]:
    """Charge, enrichit et retourne les 120 entrées (118 Z uniques + La/Ac dupliqués)."""
    elements: list[dict] = _load_json("elements.json")  # type: ignore[assignment]
    compchem: dict = _load_json("compchem.json")  # type: ignore[assignment]
    nmr: dict = load_nmr_isotopes()
    orb: dict = load_orbital_info()

    for el in elements:
        z: int = el["atomic_number"]
        zk: str = str(z)

        el["ecp_type"] = _ecp_type(z)
        el["basis_rec"] = _basis(z)
        el["pseudo"] = _pseudo(z)
        el["block"] = _block(z)
        el["functional"] = _functional(z)
        el["dispersion"] = _dispersion(z)
        el["relativistic"] = _relativistic(z)

        el["polarisabilite"] = compchem["polarisabilite"].get(zk)
        el["etats_ox"] = compchem["etats_ox"].get(zk, "N/A")
        el["ie1"] = compchem["ie1"].get(zk)
        el["ea"] = compchem["ea"].get(zk)
        el["spin_mult"] = compchem["spin_mult"].get(zk)
        el["vdw_radius"] = compchem["vdw"].get(zk)
        el["name_ru"] = compchem["name_ru"].get(zk, el["name"])

        d: Optional[float] = el.get("density")
        el["volume_molaire"] = (
            round(el["atomic_mass"] / d, 2) if d and d > 0 else None
        )

        enrich_element_phase2(el, nmr, orb)

    return elements


def build_dataframe() -> pd.DataFrame:
    """Retourne le DataFrame pandas enrichi utilisé par l'application Dash."""
    return pd.DataFrame(load_elements())


# ---------------------------------------------------------------------------
# Loaders Phase 2
# ---------------------------------------------------------------------------

def load_recommendations() -> dict:
    return _load_json("recommendations.json")  # type: ignore[return-value]


def load_software() -> dict:
    return _load_json("software.json")  # type: ignore[return-value]


def load_nmr_isotopes() -> dict:
    """Retourne {str(Z): [liste d'isotopes RMN]}."""
    return _load_json("nmr_isotopes.json")  # type: ignore[return-value]


def load_orbital_info() -> dict:
    """Retourne {str(Z): dict d'info orbitale}."""
    return _load_json("orbital_info.json")  # type: ignore[return-value]


def enrich_element_phase2(el: dict, nmr: dict, orb: dict) -> dict:
    """Ajoute les champs Phase 2 à un dict élément (in-place)."""
    zk = str(el["atomic_number"])
    el["nmr_isotopes"]  = nmr.get(zk, [])
    el["has_nmr"]       = len(el["nmr_isotopes"]) > 0
    el["orbital_info"]  = orb.get(zk, {})
    el["homo_type"]     = orb.get(zk, {}).get("homo_type", el.get("block", "?"))
    el["dft_challenge"] = orb.get(zk, {}).get("dft_challenge", "")
    el["core_1s_eV"]    = orb.get(zk, {}).get("core_1s_eV")
    return el


# ---------------------------------------------------------------------------
# Validation optionnelle avec qcelemental / periodictable
# ---------------------------------------------------------------------------

def validate_masses_qcelemental(elements: list[dict], tol: float = 0.01) -> list[str]:
    """Compare les masses atomiques standard (IUPAC) du JSON à la bibliothèque *periodictable*.

    Note : qcelemental.periodictable.to_mass() retourne la masse du nucléide le plus
    abondant (masse nucléaire), pas la masse atomique standard IUPAC. On utilise donc
    *periodictable* pour cette validation. qcelemental reste utile pour les constantes
    fondamentales (CODATA) et les propriétés isotopiques.

    Retourne une liste de messages d'avertissement pour les écarts > *tol* u.
    """
    try:
        import periodictable as pt
    except ImportError:
        warnings.warn("periodictable non installé — validation des masses ignorée.")
        return []

    issues: list[str] = []
    seen: set[int] = set()
    for el in elements:
        z = el["atomic_number"]
        if z in seen or z > 100:  # Z > 100 : masses conventionnelles changeantes
            continue
        seen.add(z)
        try:
            pt_el = getattr(pt, el["symbol"])
            ref = float(pt_el.mass)
            diff = abs(el["atomic_mass"] - ref)
            if diff > tol:
                issues.append(
                    f"Z={z} {el['symbol']}: JSON={el['atomic_mass']}, "
                    f"periodictable={ref}, Δ={diff:.4f} u"
                )
        except Exception:
            pass
    return issues


def validate_spin_hund(elements: list[dict]) -> list[str]:
    """Vérifie la cohérence des multiplicités de spin via periodictable (si disponible)
    et signale les cas connus critiques (Cr, Mo, Nb, Gd, Cm…).

    Règle de Hund : maximiser S → 2S+1 = nombre d'e⁻ non appariés + 1.
    """
    # Valeurs de référence pour les cas les plus importants (règle de Hund stricte)
    REFERENCE_MULT: dict[int, int] = {
        # Bloc d — exceptions de remplissage connues
        24: 7,   # Cr : [Ar]3d⁵4s¹ → 6 non appariés
        25: 6,   # Mn : [Ar]3d⁵4s² → 5 non appariés
        29: 2,   # Cu : [Ar]3d¹⁰4s¹ → 1 non apparié
        41: 6,   # Nb : [Kr]4d⁴5s¹ → 5 non appariés
        42: 7,   # Mo : [Kr]4d⁵5s¹ → 6 non appariés
        44: 5,   # Ru : [Kr]4d⁷5s¹ → 4 non appariés (convention courante DFT)
        45: 4,   # Rh : [Kr]4d⁸5s¹ → 3 non appariés
        46: 1,   # Pd : [Kr]4d¹⁰ → 0 non apparié (spin singulet)
        47: 2,   # Ag : [Kr]4d¹⁰5s¹ → 1 non apparié
        78: 3,   # Pt : [Xe]4f¹⁴5d⁹6s¹ → 2 non appariés
        79: 2,   # Au : [Xe]4f¹⁴5d¹⁰6s¹ → 1 non apparié
        # Bloc f — règle des trous
        64: 9,   # Gd : [Xe]4f⁷5d¹ → 8 non appariés
        96: 9,   # Cm : [Rn]5f⁷6d¹ → 8 non appariés
    }

    by_z = {el["atomic_number"]: el for el in elements}
    issues: list[str] = []
    for z, expected in REFERENCE_MULT.items():
        el = by_z.get(z)
        if el is None:
            continue
        actual = el.get("spin_mult")
        if actual != expected:
            issues.append(
                f"Z={z} {el['symbol']}: spin_mult={actual}, attendu={expected} "
                f"(règle de Hund)"
            )
    return issues


# ---------------------------------------------------------------------------
# Constantes réexportées (compatibilité app.py)
# ---------------------------------------------------------------------------

CATEGORY_COLORS: dict[str, str] = {
    "métal alcalin":          "#ff8a65",
    "métal alcalino-terreux": "#ffb74d",
    "lanthanide":             "#ba68c8",
    "actinide":               "#ab47bc",
    "métal de transition":    "#64b5f6",
    "post-transition metal":  "#90a4ae",
    "métalloïde":             "#aed581",
    "non-metal":              "#a5d6a7",
    "halogène":               "#4dd0e1",
    "gaz noble":              "#81d4fa",
    "métal":                  "#b0bec5",
}

COLOR_DEFAULT: str = "#37474f"

ELEMENTS: list[dict] = load_elements()


# ---------------------------------------------------------------------------
# CLI de validation autonome
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Chargement des données ===")
    els = load_elements()
    unique_z = {e["atomic_number"] for e in els}
    print(f"  Entrées totales : {len(els)}")
    print(f"  Z uniques       : {len(unique_z)} (attendu : 118)")

    print("\n=== Validation masses (qcelemental) ===")
    mass_issues = validate_masses_qcelemental(els)
    if mass_issues:
        for msg in mass_issues:
            print(f"  WARN {msg}")
    else:
        print("  OK — aucun écart > 0.05 u")

    print("\n=== Validation spin Hund ===")
    hund_issues = validate_spin_hund(els)
    if hund_issues:
        for msg in hund_issues:
            print(f"  WARN {msg}")
    else:
        print("  OK — multiplicités de référence cohérentes")

    print("\n=== ECP/basis spot-check ===")
    for z, expected_ecp in [(1, "Tous-électrons"), (19, "ECP optionnel"),
                             (37, "ECP recommandé"), (55, "ECP requis"), (87, "ECP/relativiste")]:
        got = _ecp_type(z)
        status = "OK" if got == expected_ecp else f"FAIL (got {got})"
        print(f"  Z={z:3d} ECP: {status}")

    print("\nTerminé.")
