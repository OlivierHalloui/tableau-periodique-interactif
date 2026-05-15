"""
molecule_assistant.py — Analyse de formule moléculaire et recommandation de calcul.
Анализ молекулярной формулы и рекомендация метода расчёта.
Molecular formula analysis and computational method recommendation.
"""
from __future__ import annotations

import re
from functools import reduce

# Éléments triés du plus long au plus court pour éviter les ambiguïtés (He avant H)
_SYMBOLS_SORTED = [
    "He","Li","Be","Ne","Na","Mg","Al","Si","Cl","Ar","Ca","Sc","Ti","Cr","Mn","Fe","Co","Ni","Cu","Zn",
    "Ga","Ge","As","Se","Br","Kr","Rb","Sr","Zr","Nb","Mo","Tc","Ru","Rh","Pd","Ag","Cd","In","Sn","Sb",
    "Te","Xe","Cs","Ba","La","Ce","Pr","Nd","Pm","Sm","Eu","Gd","Tb","Dy","Ho","Er","Tm","Yb","Lu","Hf",
    "Ta","Re","Os","Ir","Pt","Au","Hg","Tl","Pb","Bi","Po","At","Rn","Fr","Ra","Ac","Th","Pa","Np","Pu",
    "Am","Cm","Bk","Cf","Es","Fm","Md","No","Lr","Rf","Db","Sg","Bh","Hs","Mt","Ds","Rg","Cn","Nh","Fl",
    "Mc","Lv","Ts","Og","Yb","Y","W","V","U","I","F","N","O","B","C","H","P","S","K",
]
# Remove duplicates preserving order
_seen: set[str] = set()
SYMBOLS: list[str] = []
for _s in _SYMBOLS_SORTED:
    if _s not in _seen:
        SYMBOLS.append(_s)
        _seen.add(_s)


def parse_formula(formula: str) -> dict[str, int]:
    """
    Parse a molecular formula string into a dict {symbol: count}.
    Handles: H2O, FeCl3, Ca(NO3)2, Fe2(SO4)3, [Fe(CO)5], Cp2Fe.
    """
    formula = formula.strip().replace("[", "(").replace("]", ")")

    def parse_seg(s: str, mult: int = 1) -> dict[str, int]:
        counts: dict[str, int] = {}
        i = 0
        while i < len(s):
            if s[i] == "(":
                # Find matching closing paren
                depth, j = 1, i + 1
                while j < len(s) and depth > 0:
                    if s[j] == "(":
                        depth += 1
                    elif s[j] == ")":
                        depth -= 1
                    j += 1
                inner = s[i + 1: j - 1]
                # Get multiplier after the closing paren
                k = j
                while k < len(s) and s[k].isdigit():
                    k += 1
                sub_mult = int(s[j:k]) if k > j else 1
                sub = parse_seg(inner, mult * sub_mult)
                for sym, cnt in sub.items():
                    counts[sym] = counts.get(sym, 0) + cnt
                i = k
            else:
                # Try to match an element symbol
                matched = None
                for sym in SYMBOLS:
                    if s[i:].startswith(sym):
                        matched = sym
                        break
                if matched:
                    k = i + len(matched)
                    while k < len(s) and s[k].isdigit():
                        k += 1
                    n = int(s[i + len(matched):k]) if k > i + len(matched) else 1
                    counts[matched] = counts.get(matched, 0) + n * mult
                    i = k
                else:
                    i += 1  # skip unknown character
        return counts

    return parse_seg(formula)


def _z_for_symbol(sym: str, elements_by_sym: dict[str, dict]) -> int:
    return elements_by_sym.get(sym, {}).get("atomic_number", 0)


def _block_for_z(z: int) -> str:
    s_set = {1,2,3,4,11,12,19,20,37,38,55,56,87,88}
    p_set = set(range(5,11))|set(range(13,19))|set(range(31,37))|set(range(49,55))|set(range(81,87))|set(range(113,119))
    d_set = set(range(21,31))|set(range(39,49))|set(range(72,81))|set(range(104,113))
    if z in s_set: return "s"
    if z in p_set: return "p"
    if z in d_set: return "d"
    return "f"


def recommend_for_molecule(
    formula:    str,
    prop_key:   str,
    lang:       str,
    elements_by_sym: dict[str, dict],
) -> dict:
    """
    Analyse la formule et retourne des recommandations de calcul.
    Returns dict with keys: elements, dominant_z, block, method, basis, notes.
    """
    counts = parse_formula(formula)
    if not counts:
        return {"error": True, "formula": formula}

    # Identify element Z values
    elem_zs: dict[str, int] = {sym: _z_for_symbol(sym, elements_by_sym) for sym in counts}
    max_z   = max(elem_zs.values(), default=1)
    # Dominant heavy atom (highest Z)
    dominant_sym = max(elem_zs, key=lambda s: elem_zs[s])
    dominant_z   = elem_zs[dominant_sym]
    block        = _block_for_z(dominant_z)

    has_tm   = any(21 <= z <= 30 or 39 <= z <= 48 or 72 <= z <= 80 for z in elem_zs.values())
    has_f    = any(57 <= z <= 71 or 89 <= z <= 103 for z in elem_zs.values())
    has_heavy = max_z > 36
    open_shell_likely = (block in ("d", "f")) or has_tm or has_f

    # Method heuristic
    if has_f:
        method = "casscf"
        method_note = {"fr": "Bloc f détecté — CASSCF/NEVPT2 recommandé pour les effets multiréférences.",
                       "ru": "Обнаружен f-блок — рекомендован CASSCF/NEVPT2 для мультиреференсных эффектов.",
                       "en": "f-block element detected — CASSCF/NEVPT2 recommended for multireference effects."}
    elif has_tm:
        method = "dft_hybrid"
        method_note = {"fr": "Métal de transition — DFT hybride (TPSSh, PBE0) recommandé.",
                       "ru": "Переходный металл — рекомендована гибридная ДФТ (TPSSh, PBE0).",
                       "en": "Transition metal — hybrid DFT (TPSSh, PBE0) recommended."}
    elif max_z <= 18 and prop_key == "energy":
        method = "ccsd"
        method_note = {"fr": "Molécule légère — CCSD(T) peut être envisagé pour la haute précision.",
                       "ru": "Лёгкая молекула — можно применить CCSD(T) для высокой точности.",
                       "en": "Light molecule — CCSD(T) feasible for high accuracy."}
    else:
        method = "dft_hybrid"
        method_note = {"fr": "DFT hybride recommandé.", "ru": "Рекомендована гибридная ДФТ.", "en": "Hybrid DFT recommended."}

    # Basis heuristic (for the whole molecule, use the basis suitable for the heaviest atom)
    if has_heavy:
        if has_f:
            basis = "SARC-DKH2 (heavy) / cc-pVTZ (light)"
        else:
            basis = "def2-TZVP (all)"
    else:
        basis = "cc-pVTZ (all)" if max_z <= 18 else "def2-TZVP (all)"

    # ECP
    ecp = None
    if max_z > 36:
        ecp = "def2-ECP (heavy atoms)"

    # Extra notes
    extra: list[str] = []
    if open_shell_likely:
        extra.append({"fr": "⚠ Couche ouverte probable — utiliser le calcul unrestricted (UKS/ROHF).",
                      "ru": "⚠ Вероятна незакрытая оболочка — использовать unrestricted расчёт.",
                      "en": "⚠ Open-shell likely — use unrestricted calculation (UKS/ROHF)."}.get(lang, ""))
    if has_heavy:
        extra.append({"fr": "ℹ Éléments lourds — les effets relativistes scalaires (DKH2/ZORA) sont recommandés.",
                      "ru": "ℹ Тяжёлые элементы — рекомендованы скалярные релятивистские поправки (DKH2/ZORA).",
                      "en": "ℹ Heavy elements — scalar relativistic effects (DKH2/ZORA) recommended."}.get(lang, ""))

    lk = lang if lang in ("fr", "ru") else "fr"
    return {
        "error":         False,
        "formula":       formula,
        "elements":      counts,
        "dominant":      dominant_sym,
        "dominant_z":    dominant_z,
        "block":         block,
        "method":        method,
        "basis":         basis,
        "ecp":           ecp,
        "method_note":   method_note.get(lk, method_note["fr"]),
        "extra_notes":   [e for e in extra if e],
        "open_shell":    open_shell_likely,
    }
