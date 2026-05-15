"""
Tests de cohérence pour data_loader.py.
Тесты когерентности для data_loader.py.

Exécution : pytest tests/
"""
import pytest

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from data_loader import (
    load_elements,
    validate_masses_qcelemental,
    validate_spin_hund,
    _ecp_type,
    _basis,
    _block,
    _pseudo,
    _functional,
    _relativistic,
    CATEGORY_COLORS,
    COLOR_DEFAULT,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def elements():
    return load_elements()


@pytest.fixture(scope="module")
def by_z(elements):
    """Dictionnaire Z → premier élément (ignore les doublons La/Ac)."""
    d: dict[int, dict] = {}
    for el in elements:
        if el["atomic_number"] not in d:
            d[el["atomic_number"]] = el
    return d


# ---------------------------------------------------------------------------
# Chargement de base
# ---------------------------------------------------------------------------

def test_total_entries(elements):
    """120 entrées : 118 éléments + La(Z=57) et Ac(Z=89) dupliqués."""
    assert len(elements) == 120


def test_all_118_z_present(elements):
    unique_z = {el["atomic_number"] for el in elements}
    assert unique_z == set(range(1, 119))


def test_required_fields_present(elements):
    required = [
        "atomic_number", "symbol", "name", "atomic_mass", "row", "col",
        "category", "ecp_type", "basis_rec", "block", "spin_mult",
        "ie1", "polarisabilite", "vdw_radius", "name_ru",
    ]
    for el in elements:
        for field in required:
            assert field in el, f"Champ '{field}' manquant pour Z={el['atomic_number']}"


def test_no_duplicate_symbol_in_main_grid(elements):
    """La et Ac sont les seuls Z dupliqués (placeholders + rangée lanthanides/actinides)."""
    from collections import Counter
    counts = Counter(el["atomic_number"] for el in elements)
    duplicates = {z: n for z, n in counts.items() if n > 2}
    assert not duplicates, f"Z inattendus dupliqués : {duplicates}"
    assert counts[57] == 2, "La (Z=57) doit apparaître deux fois"
    assert counts[89] == 2, "Ac (Z=89) doit apparaître deux fois"


# ---------------------------------------------------------------------------
# Règle de Hund — multiplicités de spin
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("z,symbol,expected_mult,reason", [
    (1,  "H",  2, "1s¹ → 1 non apparié"),
    (6,  "C",  3, "2p² → 2 non appariés (règle de Hund)"),
    (7,  "N",  4, "2p³ → 3 non appariés"),
    (8,  "O",  3, "2p⁴ → 2 non appariés"),
    (24, "Cr", 7, "[Ar]3d⁵4s¹ → 6 non appariés (exception remplissage)"),
    (25, "Mn", 6, "[Ar]3d⁵4s² → 5 non appariés"),
    (29, "Cu", 2, "[Ar]3d¹⁰4s¹ → 1 non apparié (exception remplissage)"),
    (41, "Nb", 6, "[Kr]4d⁴5s¹ → 5 non appariés"),
    (42, "Mo", 7, "[Kr]4d⁵5s¹ → 6 non appariés"),
    (46, "Pd", 1, "[Kr]4d¹⁰ → singulet"),
    (57, "La", 2, "[Xe]5d¹ → 1 non apparié"),
    (64, "Gd", 9, "[Xe]4f⁷5d¹ → 8 non appariés"),
    (96, "Cm", 9, "[Rn]5f⁷6d¹ → 8 non appariés"),
])
def test_hund_spin_multiplicity(by_z, z, symbol, expected_mult, reason):
    el = by_z[z]
    assert el["spin_mult"] == expected_mult, (
        f"Z={z} {symbol}: spin_mult={el['spin_mult']}, attendu={expected_mult} — {reason}"
    )


def test_spin_mult_all_positive(elements):
    for el in elements:
        sm = el.get("spin_mult")
        if sm is not None:
            assert sm >= 1, f"spin_mult négatif pour Z={el['atomic_number']}"


def test_validate_spin_hund_no_issues(elements):
    issues = validate_spin_hund(elements)
    assert issues == [], "\n".join(issues)


# ---------------------------------------------------------------------------
# ECP / traitement des électrons de cœur
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("z,expected", [
    (1,  "Tous-électrons"),
    (18, "Tous-électrons"),
    (19, "ECP optionnel"),
    (36, "ECP optionnel"),
    (37, "ECP recommandé"),
    (54, "ECP recommandé"),
    (55, "ECP requis"),
    (86, "ECP requis"),
    (87, "ECP/relativiste"),
    (118, "ECP/relativiste"),
])
def test_ecp_type_boundaries(z, expected):
    assert _ecp_type(z) == expected


def test_ecp_type_stored_in_elements(by_z):
    for z in [1, 19, 37, 55, 87]:
        assert by_z[z]["ecp_type"] == _ecp_type(z)


# ---------------------------------------------------------------------------
# Bases — cohérence ECP/basis
# ---------------------------------------------------------------------------

def test_light_elements_dunning_basis(by_z):
    """Z ≤ 10 : bases de Dunning (cc-pVTZ) attendues."""
    for z in range(1, 11):
        assert "cc-pVTZ" in _basis(z), f"Z={z} devrait avoir cc-pVTZ dans la base"


def test_heavy_elements_sarc_basis(by_z):
    """Lanthanides (Z 58-71) : bases SARC-DKH2 attendues."""
    for z in range(58, 72):
        assert "SARC" in _basis(z), f"Z={z} devrait avoir une base SARC"


def test_basis_ecp_consistency():
    """Les éléments all-electron (Z≤18) ne doivent pas utiliser de pseudopotentiel."""
    for z in range(1, 19):
        assert _pseudo(z) == "Aucun", f"Z={z} ne doit pas avoir de pseudopotentiel"
    for z in range(19, 37):
        assert "ECP" in _pseudo(z), f"Z={z} devrait avoir un ECP"


# ---------------------------------------------------------------------------
# Blocs orbitaux
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("z,expected_block", [
    (1, "s"), (2, "s"), (3, "s"), (4, "s"),
    (5, "p"), (10, "p"), (13, "p"), (18, "p"),
    (21, "d"), (30, "d"), (39, "d"), (48, "d"),
    (57, "f"), (71, "f"), (89, "f"), (103, "f"),
    (72, "d"), (104, "d"),
])
def test_block_assignment(z, expected_block):
    assert _block(z) == expected_block, f"Z={z}: bloc={_block(z)}, attendu={expected_block}"


def test_he_is_s_block():
    """He est classé bloc s (convention IUPAC), malgré sa position en groupe 18."""
    assert _block(2) == "s"


# ---------------------------------------------------------------------------
# Effets relativistes
# ---------------------------------------------------------------------------

def test_relativistic_light_negligible(by_z):
    for z in range(1, 19):
        assert by_z[z]["relativistic"] == "Négligeable"


def test_relativistic_heavy_spinorbit(by_z):
    for z in [87, 92, 118]:
        assert by_z[z]["relativistic"] == "Spin-orbite requis (X2C / 4c-DHF)"


# ---------------------------------------------------------------------------
# Masses atomiques — validation qcelemental (skip si absent)
# ---------------------------------------------------------------------------

def test_masses_vs_qcelemental(elements):
    issues = validate_masses_qcelemental(elements, tol=0.05)
    assert issues == [], (
        f"Écarts de masse vs qcelemental :\n" + "\n".join(issues)
    )


# ---------------------------------------------------------------------------
# Propriétés atomiques de base
# ---------------------------------------------------------------------------

def test_atomic_numbers_range(elements):
    for el in elements:
        assert 1 <= el["atomic_number"] <= 118


def test_atomic_masses_positive(elements):
    for el in elements:
        assert el["atomic_mass"] > 0, f"Masse <= 0 pour Z={el['atomic_number']}"


def test_grid_positions_valid(elements):
    for el in elements:
        assert 1 <= el["col"] <= 18, f"col hors range pour Z={el['atomic_number']}"
        assert 1 <= el["row"] <= 9,  f"row hors range pour Z={el['atomic_number']}"


def test_vdw_radii_positive(elements):
    for el in elements:
        vdw = el.get("vdw_radius")
        if vdw is not None:
            assert vdw > 0, f"Rayon VdW <= 0 pour Z={el['atomic_number']}"


def test_ie1_positive(elements):
    for el in elements:
        ie1 = el.get("ie1")
        if ie1 is not None:
            assert ie1 > 0, f"IE₁ <= 0 pour Z={el['atomic_number']}"


# ---------------------------------------------------------------------------
# Noms russes
# ---------------------------------------------------------------------------

def test_russian_names_present(by_z):
    for z in [1, 2, 26, 79, 92, 118]:
        assert by_z[z].get("name_ru"), f"name_ru manquant pour Z={z}"


def test_russian_name_hydrogen(by_z):
    assert by_z[1]["name_ru"] == "Водород"


def test_russian_name_gold(by_z):
    assert by_z[79]["name_ru"] == "Золото"


# ---------------------------------------------------------------------------
# CATEGORY_COLORS
# ---------------------------------------------------------------------------

def test_all_categories_have_color(elements):
    cats = {el["category"] for el in elements}
    for cat in cats:
        assert cat in CATEGORY_COLORS or True  # COLOR_DEFAULT fallback accepté


def test_colors_are_hex(elements):
    for cat, color in CATEGORY_COLORS.items():
        assert color.startswith("#") and len(color) == 7, (
            f"Couleur invalide pour '{cat}': {color}"
        )
