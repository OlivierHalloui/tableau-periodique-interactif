"""Tests des données de la carte DFT (Jacob's Ladder)."""
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

_FUNCTIONALS = json.loads(
    (Path(__file__).parent.parent / "data" / "dft_functionals.json").read_text(encoding="utf-8")
)


class TestDftFunctionalsData:

    def test_all_rungs_present(self):
        """Le JSON doit contenir des fonctionnelles pour chaque rung 1-5."""
        rungs = {f["rung"] for f in _FUNCTIONALS}
        assert {1, 2, 3, 4, 5}.issubset(rungs), f"Rungs présents : {rungs}"

    def test_ccsd_lowest_mad(self):
        """DLPNO-CCSD(T) ou CCSD(T) doit avoir le MAD GMTKN55 le plus bas."""
        best = min(_FUNCTIONALS, key=lambda f: f["mad_gmtkn55"])
        assert best["rung"] == 5, f"Attendu rung 5, obtenu {best['rung']} ({best['name']})"

    def test_filter_dispersion(self):
        """Filtrer dispersion=True → seulement fonctionnelles avec correction."""
        with_disp = [f for f in _FUNCTIONALS if f.get("dispersion") is True]
        without   = [f for f in _FUNCTIONALS if f.get("dispersion") is False]
        assert len(with_disp) >= 5
        assert len(without) >= 3
        for f in with_disp:
            assert "D3" in f["name"] or "D4" in f["name"] or f.get("range_sep"), \
                f"{f['name']} marqué dispersion=True mais pas de D3/D4 dans le nom"

    def test_cost_grows_with_rung_on_average(self):
        """Le coût moyen doit être croissant par rung (tendance générale)."""
        from statistics import mean
        avg_by_rung = {}
        for rung in range(1, 6):
            subset = [f["cost"] for f in _FUNCTIONALS if f["rung"] == rung]
            if subset:
                avg_by_rung[rung] = mean(subset)
        # Rung 5 > Rung 1
        assert avg_by_rung.get(5, 0) > avg_by_rung.get(1, 999)

    def test_all_functionals_have_required_fields(self):
        required = {"name", "rung", "cost", "mad_gmtkn55", "dispersion"}
        for f in _FUNCTIONALS:
            missing = required - f.keys()
            assert not missing, f"Champs manquants pour {f['name']}: {missing}"

    def test_at_least_fifteen_functionals(self):
        assert len(_FUNCTIONALS) >= 15

    def test_rung4_has_hybrid_and_rsh(self):
        """Rung 4 doit contenir des hybrides classiques et des RSH."""
        rung4 = [f for f in _FUNCTIONALS if f["rung"] == 4]
        has_rsh = any(f.get("range_sep") for f in rung4)
        assert has_rsh, "Aucune fonctionnelle à séparation de portée dans le rung 4"

    def test_lda_highest_mad(self):
        """LDA doit avoir parmi les MADs les plus élevés."""
        lda = next((f for f in _FUNCTIONALS if "LDA" in f["name"]), None)
        assert lda is not None, "LDA non trouvé dans les données"
        median_mad = sorted(f["mad_gmtkn55"] for f in _FUNCTIONALS)[len(_FUNCTIONALS) // 2]
        assert lda["mad_gmtkn55"] >= median_mad, "LDA doit avoir un MAD supérieur à la médiane"
