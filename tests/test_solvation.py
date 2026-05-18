"""Tests du module de solvants (données JSON + keywords)."""
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

_SOLVENTS = json.loads(
    (Path(__file__).parent.parent / "data" / "solvents.json").read_text(encoding="utf-8")
)


class TestSolventsData:

    def test_water_epsilon(self):
        assert abs(_SOLVENTS["water"]["epsilon"] - 78.36) < 0.1

    def test_water_orca_keyword(self):
        assert "CPCM(Water)" in _SOLVENTS["water"]["orca_kw"]

    def test_water_gaussian_keyword(self):
        kw = _SOLVENTS["water"]["gaussian_kw"]
        assert "SCRF=" in kw or "PCM" in kw

    def test_gas_phase_no_keyword(self):
        sv = _SOLVENTS["none"]
        assert sv["orca_kw"] is None
        assert sv["gaussian_kw"] is None

    def test_epsilon_in_result(self):
        """L'eau a ε ≈ 78.36."""
        assert 78.0 < _SOLVENTS["water"]["epsilon"] < 80.0

    def test_acetonitrile_high_epsilon(self):
        """L'acétonitrile a ε > 30."""
        assert _SOLVENTS["acetonitrile"]["epsilon"] > 30

    def test_hexane_low_epsilon(self):
        """L'hexane est peu polaire (ε < 3)."""
        assert _SOLVENTS["hexane"]["epsilon"] < 3.0

    def test_all_solvents_have_labels(self):
        for k, v in _SOLVENTS.items():
            assert "label_fr" in v and len(v["label_fr"]) > 0, f"label_fr manquant pour {k}"
            assert "label_ru" in v and len(v["label_ru"]) > 0, f"label_ru manquant pour {k}"

    def test_at_least_ten_solvents(self):
        assert len(_SOLVENTS) >= 10

    def test_custom_solvent_exists(self):
        assert "custom" in _SOLVENTS
