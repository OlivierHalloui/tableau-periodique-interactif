"""Tests du module champ de ligand."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from ligand_field import compute_cfse, fill_electrons, list_geometries, list_transition_metals


class TestFillElectrons:

    def test_d0_all_empty(self):
        f = fill_electrons(0, "octahedral", True)
        assert sum(f.values()) == 0

    def test_d10_all_full(self):
        f = fill_electrons(10, "octahedral", True)
        assert sum(f.values()) == 10

    def test_d6_high_spin_octahedral(self):
        """d⁶ Oh haut spin : t2g=4, eg=2."""
        f = fill_electrons(6, "octahedral", True)
        assert f["t2g"] == 4
        assert f["eg"] == 2

    def test_d6_low_spin_octahedral(self):
        """d⁶ Oh bas spin : t2g=6, eg=0."""
        f = fill_electrons(6, "octahedral", False)
        assert f["t2g"] == 6
        assert f["eg"] == 0

    def test_total_electrons_conserved(self):
        for n in range(11):
            for geo in ("octahedral", "tetrahedral", "square_planar"):
                f = fill_electrons(n, geo, True)
                assert sum(f.values()) == n, f"Electrons non conservés pour n={n}, geo={geo}"


class TestComputeCFSE:

    def test_d0_zero_cfse(self):
        cfse, _, _ = compute_cfse(0, "octahedral", True, 10000)
        assert cfse == 0.0

    def test_d10_zero_cfse(self):
        cfse, _, _ = compute_cfse(10, "octahedral", True, 10000)
        assert cfse == 0.0

    def test_d3_oh_cfse_negative(self):
        """d³ Oh haut spin : CFSE = -1.2 Δₒ (négatif = stabilisation)."""
        delta_o = 10000
        cfse, filling, config = compute_cfse(3, "octahedral", True, delta_o)
        expected = -1.2 * delta_o
        assert abs(cfse - expected) < 1.0, f"CFSE attendu ≈ {expected}, obtenu {cfse}"

    def test_d6_oh_hs_cfse(self):
        """d⁶ Oh haut spin : CFSE = -0.4 Δₒ."""
        delta_o = 10000
        cfse, _, _ = compute_cfse(6, "octahedral", True, delta_o)
        expected = -0.4 * delta_o
        assert abs(cfse - expected) < 1.0, f"CFSE attendu ≈ {expected}, obtenu {cfse}"

    def test_d6_oh_ls_cfse(self):
        """d⁶ Oh bas spin : CFSE = -2.4 Δₒ."""
        delta_o = 10000
        cfse, _, _ = compute_cfse(6, "octahedral", False, delta_o)
        expected = -2.4 * delta_o
        assert abs(cfse - expected) < 1.0, f"CFSE attendu ≈ {expected}, obtenu {cfse}"

    def test_tetrahedral_smaller_delta(self):
        """Δₜ ≈ 4/9 Δₒ : le CFSE tétraédrique doit être plus petit (abs) que l'octaédrique."""
        delta_o = 10000
        delta_t = int(10000 * 4 / 9)
        cfse_oh, _, _ = compute_cfse(3, "octahedral",  True, delta_o)
        cfse_td, _, _ = compute_cfse(3, "tetrahedral", True, delta_t)
        assert abs(cfse_td) < abs(cfse_oh)

    def test_config_string_not_empty(self):
        _, _, config = compute_cfse(5, "octahedral", True, 10000)
        assert len(config) > 0

    def test_invalid_geometry_raises(self):
        with pytest.raises(ValueError, match="Géométrie inconnue"):
            compute_cfse(5, "nonexistent", True, 10000)


class TestListFunctions:

    def test_list_geometries_fr(self):
        geoms = list_geometries("fr")
        values = {g["value"] for g in geoms}
        assert {"octahedral", "tetrahedral", "square_planar"}.issubset(values)

    def test_list_transition_metals_nonempty(self):
        metals = list_transition_metals()
        assert len(metals) >= 10
        syms = {m["symbol"] for m in metals}
        assert "Fe" in syms and "Cr" in syms and "Pt" in syms
