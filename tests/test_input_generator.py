"""
Tests du générateur de fichiers d'entrée ORCA / Gaussian / PySCF.
Тесты генератора входных файлов ORCA / Gaussian / PySCF.

Exécution : pytest tests/test_input_generator.py -v
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from input_generator import (
    generate_orca_input,
    generate_gaussian_input,
    generate_pyscf_script,
    generate_input,
    _casscf_active_space,
    _clean_basis,
)


# ---------------------------------------------------------------------------
# Fixtures — éléments de test
# ---------------------------------------------------------------------------

@pytest.fixture
def fe():
    """Fer (Z=26, bloc d, multiplicité 5)."""
    return {
        "symbol": "Fe", "name": "Fer", "atomic_number": 26,
        "spin_mult": 5, "block": "d",
    }


@pytest.fixture
def h():
    """Hydrogène (Z=1, bloc s, multiplicité 2)."""
    return {
        "symbol": "H", "name": "Hydrogène", "atomic_number": 1,
        "spin_mult": 2, "block": "s",
    }


@pytest.fixture
def au():
    """Or (Z=79, bloc d, multiplicité 2)."""
    return {
        "symbol": "Au", "name": "Or", "atomic_number": 79,
        "spin_mult": 2, "block": "d",
    }


@pytest.fixture
def gd():
    """Gadolinium (Z=64, bloc f, multiplicité 9)."""
    return {
        "symbol": "Gd", "name": "Gadolinium", "atomic_number": 64,
        "spin_mult": 9, "block": "f",
    }


# ---------------------------------------------------------------------------
# _casscf_active_space
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("z,block,mult,expected_prefix", [
    (26, "d", 5, "CASSCF(4,5)"),   # Fe, 4 unpaired d-electrons, 5 d-orbs
    (64, "f", 9, "CASSCF(8,7)"),   # Gd, 8 unpaired f-electrons, 7 f-orbs
    (6,  "p", 3, "CASSCF(2,2)"),   # C, light element → minimal (2,2)
])
def test_casscf_active_space(z, block, mult, expected_prefix):
    result = _casscf_active_space(z, block, mult)
    assert result == expected_prefix, f"Z={z}: attendu {expected_prefix}, obtenu {result}"


def test_casscf_d_block_at_least_5_orbs():
    """Bloc d → toujours 5 orbitales dans l'espace actif."""
    result = _casscf_active_space(25, "d", 6)
    assert ",5)" in result


def test_casscf_f_block_at_least_7_orbs():
    """Bloc f → toujours 7 orbitales dans l'espace actif."""
    result = _casscf_active_space(60, "f", 5)
    assert ",7)" in result


# ---------------------------------------------------------------------------
# ORCA
# ---------------------------------------------------------------------------

def test_orca_output_starts_with_comment(h):
    out = generate_orca_input(h, "hf", "geometry", "cc-pVTZ", None, None, None)
    assert out.startswith("# ORCA input"), "Le fichier ORCA doit commencer par un commentaire"


def test_orca_output_has_keywords_line(h):
    out = generate_orca_input(h, "hf", "geometry", "cc-pVTZ", None, None, None)
    assert "! HF" in out, "La ligne de mots-clés ORCA doit contenir HF"
    assert "cc-pVTZ" in out, "La ligne de mots-clés ORCA doit contenir la base"


def test_orca_open_shell_multiplicity(fe):
    """Fe (mult=5) → ligne xyz avec charge 0 mult 5."""
    out = generate_orca_input(fe, "dft_hybrid", "geometry", "def2-TZVP", None, "PBE0-D3BJ", "D3BJ")
    assert "* xyz 0 5" in out, "La multiplicité 5 doit apparaître dans le fichier ORCA"


def test_orca_ecp_block_heavy(au):
    """Au (Z=79) avec ECP → bloc %basis NewECP dans le fichier."""
    out = generate_orca_input(
        au, "dft_hybrid", "geometry", "def2-TZVPP",
        "ECP-60 (Stuttgart/MDF)", "PBE0-D3BJ", "D3BJ"
    )
    assert "%basis" in out and "NewECP" in out, "Le bloc ECP ORCA est manquant pour Z=79"


def test_orca_relativistic_heavy(au):
    """Au (Z=79) → mot-clé relativiste (ZORA ou DKH) dans les keywords."""
    out = generate_orca_input(au, "dft_hybrid", "geometry", "def2-TZVPP", None, "PBE0-D3BJ", None)
    assert "ZORA" in out or "DKH" in out, "Un mot-clé relativiste est attendu pour Z=79"


def test_orca_casscf_active_space(fe):
    """CASSCF sur Fe (bloc d, mult=5) → espace actif adapté dans les keywords."""
    out = generate_orca_input(fe, "casscf", "geometry", "def2-TZVP", None, None, None)
    assert "CASSCF" in out and ",5)" in out, "L'espace actif CASSCF doit être adapté pour le bloc d"


def test_orca_nmr_prop_block(h):
    """Propriété NMR → bloc %eprnmr dans le fichier."""
    out = generate_orca_input(h, "dft_hybrid", "nmr", "pcSseg-3", None, "PBE0-D3BJ", None)
    assert "%eprnmr" in out, "Le bloc NMR doit apparaître pour la propriété nmr"


def test_orca_excitation_tddft_block(h):
    """Propriété excitation → mot-clé TD-DFT et bloc %tddft."""
    out = generate_orca_input(h, "dft_rs", "excitation", "aug-cc-pVTZ", None, "ωB97X-D", None)
    assert "TD-DFT" in out or "%tddft" in out, "Le bloc TDDFT est attendu pour excitation"


# ---------------------------------------------------------------------------
# Gaussian
# ---------------------------------------------------------------------------

def test_gaussian_route_line(h):
    """Gaussian → ligne route commençant par #."""
    out = generate_gaussian_input(h, "hf", "geometry", "cc-pVTZ", None, None, None)
    route_lines = [l for l in out.splitlines() if l.startswith("#")]
    assert route_lines, "La ligne de route Gaussian doit commencer par '#'"


def test_gaussian_charge_mult_line(fe):
    """Gaussian → ligne charge multiplicité après le titre."""
    out = generate_gaussian_input(fe, "dft_hybrid", "geometry", "def2-TZVP", None, "PBE0", None)
    assert "0 5" in out, "La ligne charge/mult Gaussian doit contenir '0 5' pour Fe"


def test_gaussian_open_shell_note(fe):
    """Fe ouvert → note UHF/UDFT dans le fichier."""
    out = generate_gaussian_input(fe, "dft_hybrid", "geometry", "def2-TZVP", None, "PBE0", None)
    assert "UHF" in out or "UDFT" in out or "unrestricted" in out.lower(), \
        "Une note couche ouverte doit apparaître dans le fichier Gaussian"


# ---------------------------------------------------------------------------
# PySCF
# ---------------------------------------------------------------------------

def test_pyscf_output_imports(h):
    """PySCF → imports depuis pyscf."""
    out = generate_pyscf_script(h, "hf", "geometry", "cc-pVTZ", None, None, None)
    assert "from pyscf import" in out


def test_pyscf_mol_build(h):
    """PySCF → appel mol.build()."""
    out = generate_pyscf_script(h, "hf", "geometry", "cc-pVTZ", None, None, None)
    assert "mol.build()" in out


def test_pyscf_open_shell_spin(fe):
    """Fe (mult=5, 2S=4) → mol.spin = 4."""
    out = generate_pyscf_script(fe, "dft_hybrid", "geometry", "def2-TZVP", None, "PBE0-D3BJ", "D3BJ")
    assert "mol.spin    = 4" in out, "2S = spin_mult - 1 = 4 pour Fe"


def test_pyscf_nmr_property(h):
    """NMR → import du module nmr dans PySCF."""
    out = generate_pyscf_script(h, "dft_hybrid", "nmr", "pcSseg-3", None, "PBE0-D3BJ", None)
    assert "nmr" in out


def test_pyscf_dft_xc_line(fe):
    """DFT hybride → ligne mf.xc."""
    out = generate_pyscf_script(fe, "dft_hybrid", "geometry", "def2-TZVP", None, "PBE0-D3BJ", None)
    assert "mf.xc" in out


# ---------------------------------------------------------------------------
# Dispatcher generate_input
# ---------------------------------------------------------------------------

def test_dispatcher_orca(h):
    out = generate_input("orca", h, "hf", "geometry", "cc-pVTZ", None, None, None)
    assert "ORCA input" in out


def test_dispatcher_gaussian(h):
    out = generate_input("gaussian", h, "hf", "geometry", "cc-pVTZ", None, None, None)
    assert out.startswith("%")


def test_dispatcher_pyscf(h):
    out = generate_input("pyscf", h, "hf", "geometry", "cc-pVTZ", None, None, None)
    assert "from pyscf import" in out


def test_dispatcher_unknown_fallback_orca(h):
    """Logiciel inconnu → fallback ORCA."""
    out = generate_input("inconnu", h, "hf", "geometry", "cc-pVTZ", None, None, None)
    assert "ORCA input" in out
