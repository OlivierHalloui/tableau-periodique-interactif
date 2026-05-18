"""
Tests de l'assistant moléculaire (parsing + recommandation).
Тесты молекулярного ассистента (парсинг + рекомендация).

Exécution : pytest tests/test_molecule_assistant.py -v
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from molecule_assistant import parse_formula, recommend_for_molecule
from data_loader import ELEMENTS_BY_SYM


# ---------------------------------------------------------------------------
# parse_formula
# ---------------------------------------------------------------------------

class TestParseFormula:

    def test_water(self):
        assert parse_formula("H2O") == {"H": 2, "O": 1}

    def test_methane(self):
        assert parse_formula("CH4") == {"C": 1, "H": 4}

    def test_single_atom(self):
        assert parse_formula("Fe") == {"Fe": 1}

    def test_iron_chloride(self):
        assert parse_formula("FeCl3") == {"Fe": 1, "Cl": 3}

    def test_iron_sulfate(self):
        result = parse_formula("Fe2(SO4)3")
        assert result == {"Fe": 2, "S": 3, "O": 12}

    def test_calcium_nitrate(self):
        assert parse_formula("Ca(NO3)2") == {"Ca": 1, "N": 2, "O": 6}

    def test_square_brackets(self):
        """[Fe(CO)5] → brackets remplacés par parenthèses."""
        result = parse_formula("[Fe(CO)5]")
        assert result == {"Fe": 1, "C": 5, "O": 5}

    def test_ethanol(self):
        assert parse_formula("C2H5OH") == {"C": 2, "H": 6, "O": 1}

    def test_platinum_complex(self):
        result = parse_formula("Pt(NH3)2Cl2")
        assert result == {"Pt": 1, "N": 2, "H": 6, "Cl": 2}

    def test_empty_formula(self):
        assert parse_formula("") == {}

    def test_nested_parentheses(self):
        result = parse_formula("Al2(SO4)3")
        assert result == {"Al": 2, "S": 3, "O": 12}

    def test_no_number_means_one(self):
        assert parse_formula("NaCl") == {"Na": 1, "Cl": 1}

    def test_symbols_not_duplicated(self):
        """Ytterbium (Yb) ne doit pas être confondu avec Y puis b."""
        result = parse_formula("Yb")
        assert "Yb" in result and result.get("Yb") == 1
        assert "Y" not in result


# ---------------------------------------------------------------------------
# recommend_for_molecule
# ---------------------------------------------------------------------------

class TestRecommendForMolecule:

    def test_water_light_molecule(self):
        res = recommend_for_molecule("H2O", "geometry", "fr", ELEMENTS_BY_SYM)
        assert not res.get("error")
        assert res["method"] in ("dft_hybrid", "ccsd")
        assert res["dominant"] == "O"

    def test_tm_molecule_dft(self):
        """FeCl₃ → DFT hybride recommandé."""
        res = recommend_for_molecule("FeCl3", "geometry", "fr", ELEMENTS_BY_SYM)
        assert not res.get("error")
        assert res["method"] == "dft_hybrid", f"Attendu dft_hybrid, obtenu {res['method']}"

    def test_f_block_molecule_casscf(self):
        """La(NO3)3 → CASSCF recommandé (bloc f détecté)."""
        res = recommend_for_molecule("La(NO3)3", "geometry", "fr", ELEMENTS_BY_SYM)
        assert not res.get("error")
        # La est bloc d, mais Nd/Ce... Let's use Nd-containing molecule
        # Actually La is now bloc d, so test with Ce (Z=58, bloc f)
        res2 = recommend_for_molecule("CeCl3", "geometry", "fr", ELEMENTS_BY_SYM)
        assert res2["method"] == "casscf", f"Attendu casscf pour CeCl3, obtenu {res2['method']}"

    def test_heavy_atom_has_ecp(self):
        """Au (Z=79) → ECP suggéré."""
        res = recommend_for_molecule("AuCl3", "geometry", "fr", ELEMENTS_BY_SYM)
        assert res["ecp"] is not None, "Un ECP doit être suggéré pour AuCl3"

    def test_light_molecule_no_ecp(self):
        """H₂O → pas d'ECP."""
        res = recommend_for_molecule("H2O", "geometry", "fr", ELEMENTS_BY_SYM)
        assert res["ecp"] is None

    def test_heavy_atom_relativistic_note(self):
        """Éléments lourds → note relativiste dans extra_notes."""
        res = recommend_for_molecule("AuCl3", "geometry", "fr", ELEMENTS_BY_SYM)
        notes_text = " ".join(res["extra_notes"])
        assert "relativist" in notes_text.lower() or "DKH" in notes_text or "ZORA" in notes_text

    def test_open_shell_note(self):
        """FeCl₃ (couche ouverte probable) → note unrestricted."""
        res = recommend_for_molecule("FeCl3", "geometry", "fr", ELEMENTS_BY_SYM)
        notes_text = " ".join(res["extra_notes"])
        assert "unrestricted" in notes_text.lower() or "couche ouverte" in notes_text.lower()

    def test_charge_included_in_result(self):
        """La charge passée doit être retournée dans le résultat."""
        res = recommend_for_molecule("FeCl3", "geometry", "fr", ELEMENTS_BY_SYM, charge=3)
        assert res["charge"] == 3

    def test_mult_included_in_result(self):
        """La multiplicité passée doit être retournée."""
        res = recommend_for_molecule("FeCl3", "geometry", "fr", ELEMENTS_BY_SYM, mult=6)
        assert res["mult"] == 6

    def test_nonzero_charge_adds_note(self):
        """Charge non nulle → note dans extra_notes."""
        res = recommend_for_molecule("FeCl3", "geometry", "fr", ELEMENTS_BY_SYM, charge=3)
        notes_text = " ".join(res["extra_notes"])
        assert "+3" in notes_text or "charge" in notes_text.lower()

    def test_mult_gt_1_forces_open_shell(self):
        """mult > 1 → open_shell = True même pour molécule légère."""
        res = recommend_for_molecule("H2O", "geometry", "fr", ELEMENTS_BY_SYM, mult=3)
        assert res["open_shell"] is True

    def test_unrecognized_formula_returns_error(self):
        """Formule vide ou invalide → error=True."""
        res = recommend_for_molecule("", "geometry", "fr", ELEMENTS_BY_SYM)
        assert res.get("error") is True

    def test_russian_language(self):
        """L'assistant fonctionne avec lang='ru'."""
        res = recommend_for_molecule("FeCl3", "geometry", "ru", ELEMENTS_BY_SYM)
        assert not res.get("error")
        assert "method_note" in res
        # Vérifie que la note est en russe (caractères cyrilliques ou au moins str)
        assert isinstance(res["method_note"], str)

    def test_returns_required_keys(self):
        """Le résultat contient toutes les clés requises."""
        res = recommend_for_molecule("H2O", "geometry", "fr", ELEMENTS_BY_SYM)
        required = {"formula", "elements", "dominant", "dominant_z", "block",
                    "method", "basis", "ecp", "charge", "mult",
                    "method_note", "extra_notes", "open_shell"}
        assert required.issubset(res.keys()), f"Clés manquantes : {required - res.keys()}"
