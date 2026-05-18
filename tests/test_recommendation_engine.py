"""
Tests du moteur de recommandations.
Тесты движка рекомендаций.

Exécution : pytest tests/test_recommendation_engine.py -v
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from recommendation_engine import (
    recommend,
    _select_basis,
    _select_functional,
    _relativistic_level,
    list_methods,
    list_properties,
)


# ---------------------------------------------------------------------------
# Sélection de basis sets
# ---------------------------------------------------------------------------

def test_nmr_basis_all_electron():
    """NMR (GIAO) : ECP = None — calcul tous-électrons obligatoire."""
    _, _, ecp = _select_basis(26, "nmr")
    assert ecp is None, "ECP doit être absent pour NMR (calcul tous-électrons)"


def test_epr_basis_all_electron():
    """EPR/RPE : ECP = None — calcul tous-électrons obligatoire."""
    _, _, ecp = _select_basis(26, "magnetism")
    assert ecp is None, "ECP doit être absent pour les propriétés magnétiques"


def test_lanthanide_sarc_basis():
    """Lanthanides (Z=60, Nd) → bases SARC-DKH2."""
    basis, _, _ = _select_basis(60, "geometry")
    assert "SARC" in basis, f"Attendu SARC pour Z=60, obtenu : {basis}"


def test_h_he_cc_basis():
    """H/He (Z=1-2) → cc-pVTZ."""
    basis, _, ecp = _select_basis(1, "geometry")
    assert "cc-pVTZ" in basis
    assert ecp is None


def test_light_main_group_no_ecp():
    """Éléments Z ≤ 18 → pas d'ECP."""
    for z in [1, 6, 10, 18]:
        _, _, ecp = _select_basis(z, "geometry")
        assert ecp is None, f"Z={z} ne doit pas avoir d'ECP"


def test_heavy_element_has_ecp():
    """Éléments Z > 36 → ECP présent (sauf NMR/EPR)."""
    _, _, ecp = _select_basis(79, "geometry")  # Au
    assert ecp is not None, "Z=79 (Au) doit avoir un ECP pour geometry"


def test_aug_basis_for_excitation():
    """États excités → base augmentée."""
    basis, _, _ = _select_basis(6, "excitation")
    assert "aug" in basis.lower(), f"Attendu une base augmentée pour excitation, obtenu: {basis}"


# ---------------------------------------------------------------------------
# Sélection de fonctionnelles
# ---------------------------------------------------------------------------

def test_wf_method_no_functional():
    """Méthodes fonction d'onde (HF, MP2, CCSD) → fonctionnelle = None."""
    for method in ("hf", "mp2", "ccsd"):
        func, disp = _select_functional(6, "p", method, "geometry")
        assert func is None, f"{method} ne doit pas avoir de fonctionnelle"
        assert disp is None


def test_dft_method_has_functional():
    """Méthodes DFT → fonctionnelle non nulle."""
    for method in ("dft_gga", "dft_hybrid", "dft_meta", "dft_rs"):
        func, _ = _select_functional(6, "p", method, "geometry")
        assert func is not None, f"{method} doit avoir une fonctionnelle"


def test_d_block_has_functional():
    """Bloc d + DFT hybride → fonctionnelle TPSS ou PBE0."""
    func, _ = _select_functional(26, "d", "dft_hybrid", "geometry")
    assert func is not None
    assert any(f in func for f in ("PBE0", "TPSS", "TPSSh", "M06")), \
        f"Fonctionnelle inattendue pour bloc d : {func}"


# ---------------------------------------------------------------------------
# Niveaux relativistes
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("z,expected_substr", [
    (1,  "Négligeable"),
    (18, "Négligeable"),
    (19, "optionnel"),
    (36, "optionnel"),
    (37, "DKH2"),
    (54, "DKH2"),
    (55, "spin-orbite"),
    (86, "spin-orbite"),
    (87, "X2C"),
    (118, "X2C"),
])
def test_relativistic_thresholds(z, expected_substr):
    level = _relativistic_level(z)
    assert expected_substr in level, \
        f"Z={z}: attendu '{expected_substr}' dans '{level}'"


# ---------------------------------------------------------------------------
# Validation des paramètres
# ---------------------------------------------------------------------------

def test_invalid_method_raises():
    """Méthode inconnue → ValueError."""
    with pytest.raises(ValueError, match="Méthode inconnue"):
        recommend(1, "s", "methode_inexistante", "geometry")


def test_invalid_prop_raises():
    """Propriété inconnue → ValueError."""
    with pytest.raises(ValueError, match="Propriété inconnue"):
        recommend(1, "s", "hf", "propriete_inexistante")


# ---------------------------------------------------------------------------
# Notes générées
# ---------------------------------------------------------------------------

def test_ccsd_d_block_t1_warning():
    """CCSD(T) sur métal de transition → warning T₁ dans les notes."""
    rec = recommend(26, "d", "ccsd", "energy", "fr")
    assert "T₁" in rec["notes"] or "T1" in rec["notes"], \
        "Le warning T₁ doit apparaître pour CCSD(T) sur un métal de transition"


def test_ccsd_d_block_t1_warning_ru():
    """CCSD(T) sur métal de transition → warning T₁ en russe."""
    rec = recommend(26, "d", "ccsd", "energy", "ru")
    assert "T₁" in rec["notes"] or "T1" in rec["notes"], \
        "Le warning T₁ doit apparaître en russe aussi"


def test_ccsd_light_no_t1_warning():
    """CCSD(T) sur élément léger (bloc s/p) → pas de warning T₁."""
    rec = recommend(6, "p", "ccsd", "energy", "fr")
    assert "T₁" not in rec["notes"] and "T1" not in rec["notes"], \
        "Pas de warning T₁ pour un élément léger"


def test_nmr_note_giao():
    """Propriété NMR → mention GIAO dans les notes."""
    rec = recommend(6, "p", "dft_hybrid", "nmr", "fr")
    assert "GIAO" in rec["notes"], "La note NMR doit mentionner GIAO"


def test_dispersion_note_counterpoise():
    """Propriété dispersion → mention counterpoise dans les notes."""
    rec = recommend(6, "p", "dft_hybrid", "dispersion", "fr")
    assert "counterpoise" in rec["notes"].lower() or "BSSE" in rec["notes"], \
        "La note de dispersion doit mentionner counterpoise/BSSE"


def test_excitation_note_td_dft():
    """États excités → mention TD-DFT dans les notes."""
    rec = recommend(6, "p", "dft_rs", "excitation", "fr")
    assert "TD-DFT" in rec["notes"], "La note d'excitation doit mentionner TD-DFT"


# ---------------------------------------------------------------------------
# Structure du résultat
# ---------------------------------------------------------------------------

def test_recommend_returns_required_keys():
    """La recommandation retourne toutes les clés attendues."""
    rec = recommend(26, "d", "dft_hybrid", "geometry", "fr")
    required = {"basis", "aux_basis", "ecp", "functional", "dispersion",
                "relativistic", "software", "links", "notes",
                "orca_snippet", "gaussian_snippet", "method_info", "property_info"}
    assert required.issubset(rec.keys()), f"Clés manquantes : {required - rec.keys()}"


def test_recommend_software_list():
    """La liste des logiciels compatibles est non vide pour DFT hybride."""
    rec = recommend(6, "p", "dft_hybrid", "geometry", "fr")
    assert len(rec["software"]) > 0, "Aucun logiciel compatible trouvé pour DFT hybride"


def test_list_methods_fr():
    """list_methods() retourne les méthodes en français."""
    methods = list_methods("fr")
    keys = [m["value"] for m in methods]
    assert "hf" in keys and "dft_hybrid" in keys and "casscf" in keys


def test_list_properties_ru():
    """list_properties() retourne les propriétés en russe."""
    props = list_properties("ru")
    keys = [p["value"] for p in props]
    assert "geometry" in keys and "nmr" in keys
