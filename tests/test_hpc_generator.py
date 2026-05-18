"""Tests du générateur de scripts HPC."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from hpc_generator import generate_script, list_schedulers


class TestGenerateScript:

    def test_slurm_has_sbatch_directives(self):
        script = generate_script("slurm", "test_job", 16, 64, "24:00:00",
                                  "compute", "ORCA/5.0.4", "mol.inp")
        assert "#SBATCH" in script

    def test_pbs_has_pbs_directives(self):
        script = generate_script("pbs", "test_job", 16, 64, "24:00:00",
                                  "compute", "ORCA/5.0.4", "mol.inp")
        assert "#PBS" in script

    def test_sge_has_sge_directives(self):
        script = generate_script("sge", "test_job", 16, 64, "24:00:00",
                                  "compute", "ORCA/5.0.4", "mol.inp")
        assert "#$" in script

    def test_cores_in_script(self):
        script = generate_script("slurm", "myjob", 32, 128, "48:00:00",
                                  "large", "ORCA/5.0.4", "mol.inp")
        assert "32" in script

    def test_mem_gb_in_slurm_script(self):
        script = generate_script("slurm", "myjob", 16, 256, "24:00:00",
                                  "compute", "ORCA/5.0.4", "mol.inp")
        assert "256" in script

    def test_orca_module_in_script(self):
        script = generate_script("slurm", "myjob", 16, 64, "24:00:00",
                                  "compute", "ORCA/5.0.4-gompi-2022a", "mol.inp")
        assert "ORCA/5.0.4-gompi-2022a" in script

    def test_input_file_in_script(self):
        script = generate_script("slurm", "myjob", 16, 64, "24:00:00",
                                  "compute", "ORCA/5.0.4", "my_molecule.inp")
        assert "my_molecule.inp" in script

    def test_invalid_scheduler_raises(self):
        with pytest.raises(ValueError, match="Scheduler inconnu"):
            generate_script("unknown_scheduler", "job", 8, 32, "1:00:00",
                             "q", "ORCA/5", "mol.inp")

    def test_job_name_in_script(self):
        script = generate_script("slurm", "myspecialjob", 8, 32, "1:00:00",
                                  "default", "ORCA/5.0.4", "mol.inp")
        assert "myspecialjob" in script

    def test_list_schedulers(self):
        sched = list_schedulers()
        names = {s["value"] for s in sched}
        assert {"slurm", "pbs", "sge"}.issubset(names)
