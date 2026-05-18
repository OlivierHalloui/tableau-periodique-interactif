"""
hpc_generator.py — Générateur de scripts de soumission HPC (SLURM / PBS / SGE).
Генератор скриптов для отправки задач на HPC (SLURM / PBS / SGE).
"""
from __future__ import annotations

import json
from pathlib import Path

_TEMPLATES = json.loads(
    (Path(__file__).parent / "data" / "hpc_templates.json").read_text(encoding="utf-8")
)


def generate_script(scheduler: str, job_name: str, n_cores: int, mem_gb: int,
                    walltime: str, partition: str, module_orca: str,
                    input_file: str) -> str:
    """
    Génère un script de soumission HPC pour ORCA.

    Parameters
    ----------
    scheduler : "slurm" | "pbs" | "sge"
    job_name  : nom du job (sans espaces)
    n_cores   : nombre de cœurs MPI
    mem_gb    : RAM totale en Go
    walltime  : durée max ("HH:MM:SS")
    partition : nom de la queue/partition
    module_orca : identifiant du module ORCA (ex: "ORCA/5.0.4-gompi-2022a")
    input_file  : chemin vers le fichier .inp

    Returns
    -------
    str : contenu du script

    Raises
    ------
    ValueError si le scheduler est inconnu.
    """
    if scheduler not in _TEMPLATES:
        raise ValueError(f"Scheduler inconnu : {scheduler!r}. Valides : {list(_TEMPLATES)}")

    template = _TEMPLATES[scheduler]["template"]
    mem_per_core = max(1, mem_gb // max(1, n_cores))

    return template.format(
        job_name=job_name or "orca_job",
        cores=n_cores,
        mem_gb=mem_gb,
        mem_per_core=mem_per_core,
        walltime=walltime or "24:00:00",
        partition=partition or "compute",
        module_orca=module_orca or "ORCA/5.0.4",
        input_file=input_file or "molecule.inp",
    )


def list_schedulers() -> list[dict]:
    return [{"value": k, "label": v["label"], "extension": v["extension"]}
            for k, v in _TEMPLATES.items()]
