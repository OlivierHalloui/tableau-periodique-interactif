"""Tests des données de benchmark."""
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

_DATA = json.loads(
    (Path(__file__).parent.parent / "data" / "benchmarks.json").read_text(encoding="utf-8")
)


class TestBenchmarkData:

    def test_data_loaded(self):
        assert "results" in _DATA
        assert "sets" in _DATA

    def test_at_least_five_methods_in_gmtkn55(self):
        methods = {r["method"] for r in _DATA["results"] if r["set"] == "GMTKN55"}
        assert len(methods) >= 5

    def test_ccsd_best_mad_gmtkn55(self):
        """CCSD(T) doit avoir le MAD le plus bas dans GMTKN55."""
        gmtkn = [r for r in _DATA["results"] if r["set"] == "GMTKN55"]
        best  = min(gmtkn, key=lambda x: x["mad_kcal"])
        assert "CCSD" in best["method"], f"Attendu CCSD(T) comme meilleur, obtenu {best['method']}"

    def test_filter_by_set_s22(self):
        s22 = [r for r in _DATA["results"] if r["set"] == "S22"]
        assert len(s22) >= 3
        assert all(r["set"] == "S22" for r in s22)

    def test_dft_higher_mad_than_ccsd(self):
        """B3LYP a un MAD plus élevé que CCSD(T) sur GMTKN55."""
        b3lyp = next((r for r in _DATA["results"]
                      if r["method"] == "B3LYP" and r["set"] == "GMTKN55"), None)
        ccsd  = next((r for r in _DATA["results"]
                      if r["method"] == "CCSD(T)" and r["set"] == "GMTKN55"), None)
        assert b3lyp is not None and ccsd is not None
        assert b3lyp["mad_kcal"] > ccsd["mad_kcal"]

    def test_all_results_have_required_fields(self):
        required = {"method", "set", "mad_kcal", "cost_rel"}
        for r in _DATA["results"]:
            missing = required - r.keys()
            assert not missing, f"Champs manquants dans {r}: {missing}"

    def test_sets_have_urls(self):
        for k, v in _DATA["sets"].items():
            assert "url" in v and v["url"].startswith("http"), f"URL manquante pour {k}"

    def test_dispersion_field_present(self):
        for r in _DATA["results"]:
            assert "dispersion" in r, f"Champ dispersion manquant pour {r['method']}"
