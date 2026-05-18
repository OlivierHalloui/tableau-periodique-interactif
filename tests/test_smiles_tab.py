"""
Tests du module SMILES (test de la logique de parsing, pas de l'UI Dash).
Si RDKit n'est pas installé, les tests spécifiques à RDKit sont sautés.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

try:
    from rdkit import Chem
    from rdkit.Chem import rdMolDescriptors
    _RDKIT_OK = True
except ImportError:
    _RDKIT_OK = False


def _formula(smiles: str) -> str:
    """Helper : calcule la formule brute d'un SMILES (requiert RDKit)."""
    mol = Chem.MolFromSmiles(smiles)
    assert mol is not None, f"SMILES invalide : {smiles!r}"
    return rdMolDescriptors.CalcMolFormula(mol)


@pytest.mark.skipif(not _RDKIT_OK, reason="RDKit non installé")
class TestRDKitFormula:

    def test_water_smiles(self):
        assert _formula("O") == "H2O"

    def test_methane_smiles(self):
        assert _formula("C") == "CH4"

    def test_co2_smiles(self):
        assert _formula("O=C=O") == "CO2"

    def test_iron_chloride_smiles(self):
        formula = _formula("[Fe](Cl)(Cl)Cl")
        assert "Fe" in formula
        assert "Cl" in formula

    def test_invalid_smiles_returns_none(self):
        mol = Chem.MolFromSmiles("INVALID_SMILES_XYZ")
        assert mol is None

    def test_ferrocene_contains_fe(self):
        # Ferrocene simplifié
        formula = _formula("[Fe]")
        assert "Fe" in formula

    def test_ethanol_formula(self):
        formula = _formula("CCO")
        assert "C" in formula and "O" in formula and "H" in formula

    def test_acetic_acid_formula(self):
        formula = _formula("CC(=O)O")
        assert formula == "C2H4O2"


class TestRDKitFallback:

    def test_rdkit_flag_is_bool(self):
        """_RDKIT_OK doit être un booléen."""
        assert isinstance(_RDKIT_OK, bool)

    def test_smiles_tab_importable(self):
        """smiles_tab doit s'importer sans erreur même sans RDKit."""
        import smiles_tab
        assert hasattr(smiles_tab, "create_smiles_layout")
        assert hasattr(smiles_tab, "register_callbacks")

    def test_smiles_layout_returns_div(self):
        """create_smiles_layout() retourne un composant Dash."""
        from smiles_tab import create_smiles_layout
        from dash import html
        layout = create_smiles_layout()
        assert isinstance(layout, html.Div)
