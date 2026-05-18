"""
cost_estimator.py — Estimateur de coût CPU/RAM pour calculs de chimie computationnelle.
Оценщик стоимости CPU/RAM для расчётов вычислительной химии.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

_DATA = json.loads((Path(__file__).parent / "data" / "scaling_data.json").read_text(encoding="utf-8"))


def _n_basis_functions(n_atoms: int, basis_key: str, element_type: str) -> int:
    bf = _DATA["basis_factors"][basis_key]
    et = _DATA["element_type_factors"][element_type]
    nbf_per_atom = bf["nbf_per_atom_light"] * et["nbf_scale"]
    return max(1, int(n_atoms * nbf_per_atom))


def estimate_cost(n_atoms: int, method_key: str, basis_key: str,
                  element_type: str = "light") -> dict:
    """
    Retourne un dict avec le temps estimé (heures) et la RAM (Go)
    pour chaque plateforme définie dans scaling_data.json.

    Raises ValueError si method_key, basis_key ou element_type est inconnu.
    """
    methods  = _DATA["methods"]
    bases    = _DATA["basis_factors"]
    eltypes  = _DATA["element_type_factors"]
    platforms = _DATA["platforms"]

    if method_key not in methods:
        raise ValueError(f"Méthode inconnue : {method_key!r}. Valides : {list(methods)}")
    if basis_key not in bases:
        raise ValueError(f"Qualité de base inconnue : {basis_key!r}. Valides : {list(bases)}")
    if element_type not in eltypes:
        raise ValueError(f"Type d'élément inconnu : {element_type!r}. Valides : {list(eltypes)}")

    method = methods[method_key]

    if method["scaling"] == "exp":
        return {
            "method_key": method_key,
            "basis_key":  basis_key,
            "n_atoms":    n_atoms,
            "warning":    True,
            "note_fr":    method["note_fr"],
            "note_ru":    method["note_ru"],
            "platforms":  {},
        }

    n_bf    = _n_basis_functions(n_atoms, basis_key, element_type)
    n_ref   = _DATA["reference"]["n_bf_ref"]
    scaling = float(method["scaling"])
    t_ref   = float(method["ref_time_h"])

    ratio = (n_bf / n_ref) ** scaling
    t_serial_h = t_ref * ratio

    ram_dft_gb  = max(0.1, (n_bf ** 2 * 8) / 1e9)
    ram_postHF_gb = max(0.1, (n_bf ** 4 * 8) / 1e9) if scaling >= 5.0 else ram_dft_gb
    ram_gb = ram_postHF_gb * method["mem_factor"]
    ram_gb = max(1.0, ram_gb)

    result: dict = {
        "method_key": method_key,
        "basis_key":  basis_key,
        "n_atoms":    n_atoms,
        "n_bf":       n_bf,
        "warning":    False,
        "platforms":  {},
    }

    for pk, plat in platforms.items():
        speedup = plat["speedup"]
        t_h     = t_serial_h / speedup
        result["platforms"][pk] = {
            "label_fr":  plat["label_fr"],
            "label_ru":  plat["label_ru"],
            "cores":     plat["cores"],
            "time_h":    round(t_h, 2),
            "time_days": round(t_h / 24, 2),
            "ram_gb":    round(ram_gb, 1),
            "feasible":  ram_gb <= (16 if pk == "laptop" else 64 if pk == "workstation" else 512),
        }

    return result


def list_methods() -> list[dict]:
    return [
        {"value": k, "label_fr": v["label_fr"], "label_ru": v["label_ru"],
         "is_exp": v["scaling"] == "exp"}
        for k, v in _DATA["methods"].items()
    ]


def list_basis() -> list[dict]:
    return [{"value": k, "label_fr": v["label_fr"], "label_ru": v["label_ru"]}
            for k, v in _DATA["basis_factors"].items()]


def list_element_types() -> list[dict]:
    return [{"value": k, "label_fr": v["label_fr"], "label_ru": v["label_ru"]}
            for k, v in _DATA["element_type_factors"].items()]
