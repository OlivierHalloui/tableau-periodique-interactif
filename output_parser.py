"""
output_parser.py — Parseur de sorties ORCA et Gaussian.
Парсер выходных файлов ORCA и Gaussian.
"""
from __future__ import annotations

import re
from typing import Optional


def detect_software(text: str) -> str:
    """Détecte le logiciel qui a produit la sortie."""
    if "O   R   C   A" in text:
        return "orca"
    if "Gaussian" in text and ("Revision" in text or "gaussian.com" in text):
        return "gaussian"
    return "unknown"


def _extract_float(text: str, pattern: str) -> Optional[float]:
    m = re.search(pattern, text, re.IGNORECASE)
    if m:
        try:
            return float(m.group(1))
        except (ValueError, IndexError):
            return None
    return None


def _extract_int(text: str, pattern: str) -> Optional[int]:
    m = re.search(pattern, text, re.IGNORECASE)
    if m:
        try:
            return int(m.group(1))
        except (ValueError, IndexError):
            return None
    return None


def _extract_str(text: str, pattern: str) -> Optional[str]:
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(1).strip() if m else None


def parse_orca(text: str) -> dict:
    """
    Extrait les grandeurs clés d'une sortie ORCA.

    Returns dict with keys:
        final_energy, t1_diagnostic, scf_converged, scf_cycles,
        dipole_debye, homo_lumo_gap_ev, warnings, geometry_converged,
        frequencies (list), mulliken_charges (list)
    """
    result: dict = {}

    result["final_energy"] = _extract_float(
        text, r"FINAL SINGLE POINT ENERGY\s+([-\d.]+)")

    result["t1_diagnostic"] = _extract_float(
        text, r"T1 diagnostic\s*=\s*([\d.]+)")

    result["scf_cycles"] = _extract_int(
        text, r"SCF CONVERGED AFTER\s+(\d+)\s+CYCLES")
    result["scf_converged"] = "SCF CONVERGED" in text

    result["dipole_debye"] = _extract_float(
        text, r"Magnitude\s+\(Debye\)\s*:\s*([\d.]+)")

    result["homo_lumo_gap_ev"] = _extract_float(
        text, r"HOMO-LUMO Gap.*?([\d.]+)\s*eV")

    result["geometry_converged"] = (
        "OPTIMIZATION RUN DONE" in text or "THE OPTIMIZATION HAS CONVERGED" in text
    )

    # Extract frequencies (up to 10)
    freqs = re.findall(r"(\d+):\s+([-\d.]+)\s+cm\*\*-1", text)
    result["frequencies"] = [float(f[1]) for f in freqs[:10]]

    # Imaginary frequencies count
    result["n_imaginary"] = sum(1 for f in result["frequencies"] if f < 0)

    # Mulliken charges (first 5 atoms)
    mulliken_block = re.search(
        r"MULLIKEN ATOMIC CHARGES\s*-+\s*((?:\d+\s+\w+\s*:\s*[-\d.]+\s*\n?)+)",
        text)
    if mulliken_block:
        charges = re.findall(r"\d+\s+\w+\s*:\s*([-\d.]+)", mulliken_block.group(1))
        result["mulliken_charges"] = [float(c) for c in charges[:5]]
    else:
        result["mulliken_charges"] = []

    # Warnings
    warnings = []
    if result.get("t1_diagnostic") and result["t1_diagnostic"] > 0.02:
        warnings.append(f"T₁ = {result['t1_diagnostic']:.3f} > 0.02 : caractère multiréférence suspecté")
    if result.get("n_imaginary", 0) > 0:
        warnings.append(f"{result['n_imaginary']} fréquence(s) imaginaire(s) : structure non stationnaire")
    if not result.get("scf_converged"):
        warnings.append("Convergence SCF non atteinte")
    result["warnings"] = warnings

    return result


def parse_gaussian(text: str) -> dict:
    """
    Extrait les grandeurs clés d'une sortie Gaussian.
    """
    result: dict = {}

    result["final_energy"] = _extract_float(
        text, r"SCF Done.*?=\s*([-\d.]+)")

    result["t1_diagnostic"] = _extract_float(
        text, r"T1 Diagnostic\s*=\s*([\d.]+)")

    result["scf_converged"] = "SCF Done" in text
    result["scf_cycles"] = _extract_int(text, r"in\s+(\d+)\s+cycles")

    result["dipole_debye"] = _extract_float(
        text, r"Tot=\s*([\d.]+)")

    result["homo_lumo_gap_ev"] = None

    result["geometry_converged"] = "Optimization completed" in text or "Stationary point found" in text

    # Frequencies
    freqs_raw = re.findall(r"Frequencies\s+--\s+([-\d.\s]+)", text)
    freqs: list[float] = []
    for block in freqs_raw:
        freqs.extend([float(f) for f in block.split()])
    result["frequencies"] = freqs[:10]
    result["n_imaginary"] = sum(1 for f in freqs if f < 0)

    # Mulliken
    mulliken_block = re.search(
        r"Mulliken charges:\s*\n\s*1\s*\n((?:\s*\d+\s+\w+\s+[-\d.]+\s*\n)+)", text)
    if mulliken_block:
        charges = re.findall(r"\d+\s+\w+\s+([-\d.]+)", mulliken_block.group(1))
        result["mulliken_charges"] = [float(c) for c in charges[:5]]
    else:
        result["mulliken_charges"] = []

    warnings = []
    if result.get("t1_diagnostic") and result["t1_diagnostic"] > 0.02:
        warnings.append(f"T₁ = {result['t1_diagnostic']:.3f} > 0.02 : caractère multiréférence suspecté")
    if result.get("n_imaginary", 0) > 0:
        warnings.append(f"{result['n_imaginary']} fréquence(s) imaginaire(s)")
    result["warnings"] = warnings

    return result


def parse(text: str) -> dict:
    """Détecte le logiciel et parse automatiquement."""
    if not text or not text.strip():
        return {"software": "unknown", "error": "Texte vide"}

    software = detect_software(text)
    if software == "orca":
        parsed = parse_orca(text)
    elif software == "gaussian":
        parsed = parse_gaussian(text)
    else:
        parsed = {}

    parsed["software"] = software
    return parsed
