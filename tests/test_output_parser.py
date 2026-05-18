"""Tests du parseur de sorties ORCA / Gaussian."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from output_parser import detect_software, parse_orca, parse_gaussian, parse

# --- Minimal synthetic outputs for testing ---

_ORCA_SAMPLE = """\
               O   R   C   A
                           Version 5.0.4

FINAL SINGLE POINT ENERGY       -76.382519842

SCF CONVERGED AFTER   9 CYCLES

Magnitude (Debye)          :    1.832

HOMO-LUMO Gap             0.3954 au
  ==> 10.756 eV

T1 diagnostic              =   0.015

MULLIKEN ATOMIC CHARGES
-----------------------------------
   0 O :   -0.854
   1 H :    0.427
   2 H :    0.427

OPTIMIZATION RUN DONE
"""

_ORCA_T1_HIGH = """\
               O   R   C   A

FINAL SINGLE POINT ENERGY       -2634.123456

T1 diagnostic              =   0.028

SCF CONVERGED AFTER   12 CYCLES
"""

_GAUSS_SAMPLE = """\
 Gaussian 16  Revision A.03
 gaussian.com

 SCF Done:  E(RB3LYP) =  -76.3824  A.U. after   10 cycles

 Optimization completed.
  Stationary point found.

 Total  0.8234D-01
 Tot=    1.8329

 T1 Diagnostic                    =   0.013
"""

_UNKNOWN_TEXT = "This is just some random text without any chemistry output."


class TestDetectSoftware:

    def test_detect_orca(self):
        assert detect_software(_ORCA_SAMPLE) == "orca"

    def test_detect_gaussian(self):
        assert detect_software(_GAUSS_SAMPLE) == "gaussian"

    def test_detect_unknown(self):
        assert detect_software(_UNKNOWN_TEXT) == "unknown"

    def test_detect_empty(self):
        assert detect_software("") == "unknown"


class TestParseOrca:

    def test_parse_energy(self):
        res = parse_orca(_ORCA_SAMPLE)
        assert res["final_energy"] is not None
        assert abs(res["final_energy"] - (-76.382519842)) < 1e-6

    def test_scf_converged(self):
        res = parse_orca(_ORCA_SAMPLE)
        assert res["scf_converged"] is True

    def test_scf_cycles(self):
        res = parse_orca(_ORCA_SAMPLE)
        assert res["scf_cycles"] == 9

    def test_t1_diagnostic_low(self):
        res = parse_orca(_ORCA_SAMPLE)
        assert res["t1_diagnostic"] is not None
        assert abs(res["t1_diagnostic"] - 0.015) < 1e-4

    def test_t1_warning_triggered(self):
        """T₁ > 0.02 → avertissement dans warnings."""
        res = parse_orca(_ORCA_T1_HIGH)
        assert res["t1_diagnostic"] > 0.02
        warnings_text = " ".join(res["warnings"])
        assert "multiréférence" in warnings_text or "T₁" in warnings_text

    def test_dipole(self):
        res = parse_orca(_ORCA_SAMPLE)
        assert res["dipole_debye"] is not None
        assert abs(res["dipole_debye"] - 1.832) < 0.01

    def test_geometry_converged(self):
        res = parse_orca(_ORCA_SAMPLE)
        assert res["geometry_converged"] is True

    def test_mulliken_charges(self):
        res = parse_orca(_ORCA_SAMPLE)
        assert len(res["mulliken_charges"]) >= 1
        assert abs(res["mulliken_charges"][0] - (-0.854)) < 0.01


class TestParseGaussian:

    def test_parse_energy(self):
        res = parse_gaussian(_GAUSS_SAMPLE)
        assert res["final_energy"] is not None
        assert abs(res["final_energy"] - (-76.3824)) < 0.01

    def test_scf_converged(self):
        res = parse_gaussian(_GAUSS_SAMPLE)
        assert res["scf_converged"] is True

    def test_geometry_converged(self):
        res = parse_gaussian(_GAUSS_SAMPLE)
        assert res["geometry_converged"] is True

    def test_t1_gaussian(self):
        res = parse_gaussian(_GAUSS_SAMPLE)
        assert res["t1_diagnostic"] is not None
        assert abs(res["t1_diagnostic"] - 0.013) < 1e-4


class TestParseDispatch:

    def test_parse_unknown_returns_no_crash(self):
        res = parse(_UNKNOWN_TEXT)
        assert res["software"] == "unknown"
        assert "error" not in res or isinstance(res.get("error"), str)

    def test_parse_empty_returns_error(self):
        res = parse("")
        assert res["software"] == "unknown"
        assert "error" in res

    def test_parse_orca_dispatches(self):
        res = parse(_ORCA_SAMPLE)
        assert res["software"] == "orca"
        assert "final_energy" in res

    def test_parse_gaussian_dispatches(self):
        res = parse(_GAUSS_SAMPLE)
        assert res["software"] == "gaussian"
        assert "final_energy" in res
