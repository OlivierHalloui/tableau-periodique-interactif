"""
ligand_field.py — Calcul du champ de ligand : splitting, remplissage électronique, CFSE.
Расчёт поля лигандов: расщепление, заполнение электронами, СЭПП.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_DATA = json.loads((Path(__file__).parent / "data" / "ligand_field.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def _geometry_data(geometry_key: str) -> dict:
    if geometry_key not in _DATA["geometries"]:
        raise ValueError(f"Géométrie inconnue : {geometry_key!r}. Valides : {list(_DATA['geometries'])}")
    return _DATA["geometries"][geometry_key]


def _sorted_levels(geometry_key: str) -> list[tuple[str, float, int]]:
    """Retourne [(orbital_key, energy_frac, degeneracy)] triés par énergie croissante."""
    levels = _geometry_data(geometry_key)["levels"]
    return sorted(
        [(k, v["energy_frac"], v["degeneracy"]) for k, v in levels.items()],
        key=lambda x: x[1]
    )


def fill_electrons(n_d: int, geometry_key: str, high_spin: bool) -> dict[str, int]:
    """
    Remplit n_d électrons dans les niveaux de champ de ligand.

    Returns dict {orbital_key: n_electrons_in_orbital}
    """
    levels = _sorted_levels(geometry_key)
    filling: dict[str, int] = {k: 0 for k, _, _ in levels}

    if high_spin:
        # Remplir un électron dans chaque orbital (Hund), puis doubler
        remaining = n_d
        # Pass 1 : un électron par niveau (alpha)
        for k, _, deg in levels:
            placed = min(remaining, deg)
            filling[k] += placed
            remaining -= placed
            if remaining == 0:
                break
        # Pass 2 : électrons beta (chaque orbital peut porter 2 électrons)
        for k, _, deg in levels:
            if remaining == 0:
                break
            already  = filling[k]
            can_add  = 2 * deg - already   # max 2 e⁻ par orbital
            placed   = min(remaining, can_add)
            filling[k] += placed
            remaining -= placed
    else:
        # Bas spin : remplir les niveaux les plus bas d'abord (paires forcées)
        remaining = n_d
        for k, _, deg in levels:
            if remaining == 0:
                break
            placed = min(remaining, 2 * deg)
            filling[k] += placed
            remaining -= placed

    return filling


def compute_cfse(n_d: int, geometry_key: str, high_spin: bool,
                 delta_o: float) -> tuple[float, dict[str, int], str]:
    """
    Calcule la CFSE (Crystal Field Stabilization Energy).

    Returns
    -------
    (cfse_cm1, filling_dict, config_str)
    cfse_cm1 : CFSE en cm⁻¹
    filling_dict : {orbital_key: n_electrons}
    config_str : représentation texte de la configuration
    """
    levels = _sorted_levels(geometry_key)
    level_map = {k: ef for k, ef, _ in levels}
    filling = fill_electrons(n_d, geometry_key, high_spin)

    cfse = sum(filling[k] * level_map[k] * delta_o for k in filling)

    geom_data = _geometry_data(geometry_key)
    parts = []
    for k, v in geom_data["levels"].items():
        ne = filling[k]
        if ne > 0:
            parts.append(f"{v['label']}^{ne}")
    config_str = " ".join(parts)

    return round(cfse, 1), filling, config_str


def list_geometries(lang: str = "fr") -> list[dict]:
    key = "label_fr" if lang == "fr" else "label_ru"
    return [{"value": k, "label": v[key]}
            for k, v in _DATA["geometries"].items()]


def list_transition_metals() -> list[dict]:
    return [
        {"value": int(z), "label": f"({z}) {v['symbol']} — {v['name_fr']}",
         "symbol": v["symbol"], "d_electrons_0": v["d_electrons_0"]}
        for z, v in sorted(_DATA["transition_metals"].items(), key=lambda x: int(x[0]))
    ]
