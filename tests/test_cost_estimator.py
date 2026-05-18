"""Tests de l'estimateur de coût CPU/RAM."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from cost_estimator import estimate_cost, list_methods, list_basis, list_element_types


class TestEstimateCost:

    def test_invalid_method_raises(self):
        with pytest.raises(ValueError, match="Méthode inconnue"):
            estimate_cost(10, "nonexistent_method", "tz")

    def test_invalid_basis_raises(self):
        with pytest.raises(ValueError, match="Qualité de base inconnue"):
            estimate_cost(10, "dft_hybrid", "6311g")

    def test_scaling_monotone_ccsd_gt_mp2_gt_dft(self):
        """CCSD(T) doit coûter plus que MP2, qui coûte plus que DFT hybride (même N)."""
        r_dft  = estimate_cost(20, "dft_hybrid", "tz")
        r_mp2  = estimate_cost(20, "mp2", "tz")
        r_ccsd = estimate_cost(20, "ccsd_t", "tz")
        # All feasible on HPC
        t_dft  = r_dft["platforms"]["hpc"]["time_h"]
        t_mp2  = r_mp2["platforms"]["hpc"]["time_h"]
        t_ccsd = r_ccsd["platforms"]["hpc"]["time_h"]
        assert t_ccsd > t_mp2 > t_dft, f"Scaling non monotone: ccsd_t={t_ccsd}, mp2={t_mp2}, dft={t_dft}"

    def test_ram_grows_with_basis(self):
        """QZ doit demander plus de RAM que TZ, qui demande plus que DZ."""
        r_dz = estimate_cost(15, "dft_hybrid", "dz")
        r_tz = estimate_cost(15, "dft_hybrid", "tz")
        r_qz = estimate_cost(15, "dft_hybrid", "qz")
        ram_dz = r_dz["platforms"]["laptop"]["ram_gb"]
        ram_tz = r_tz["platforms"]["laptop"]["ram_gb"]
        ram_qz = r_qz["platforms"]["laptop"]["ram_gb"]
        assert ram_qz >= ram_tz >= ram_dz, f"RAM non croissante: dz={ram_dz}, tz={ram_tz}, qz={ram_qz}"

    def test_casscf_returns_warning(self):
        """CASSCF → warning=True, pas de platforms."""
        res = estimate_cost(10, "casscf", "tz")
        assert res["warning"] is True
        assert res["platforms"] == {}
        assert "note_fr" in res and len(res["note_fr"]) > 0

    def test_result_structure(self):
        """Le résultat contient les clés attendues."""
        res = estimate_cost(10, "dft_hybrid", "tz")
        assert not res["warning"]
        assert "n_bf" in res
        assert "platforms" in res
        for pk in ("laptop", "workstation", "hpc"):
            assert pk in res["platforms"]
            pv = res["platforms"][pk]
            assert "time_h" in pv
            assert "ram_gb" in pv
            assert "feasible" in pv

    def test_more_atoms_more_time(self):
        """Plus d'atomes → plus de temps."""
        small = estimate_cost(5, "ccsd", "tz")
        large = estimate_cost(30, "ccsd", "tz")
        assert large["platforms"]["hpc"]["time_h"] > small["platforms"]["hpc"]["time_h"]

    def test_list_methods_nonempty(self):
        methods = list_methods()
        assert len(methods) >= 5
        assert all("value" in m and "label_fr" in m for m in methods)

    def test_list_basis_has_three(self):
        bases = list_basis()
        assert {b["value"] for b in bases} >= {"dz", "tz", "qz"}

    def test_list_element_types(self):
        et = list_element_types()
        assert {e["value"] for e in et} >= {"light", "tm", "heavy"}
