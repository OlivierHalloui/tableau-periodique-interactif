"""
input_generator.py — Génération de fichiers d'entrée ORCA / Gaussian / PySCF.
Генерация входных файлов ORCA / Gaussian / PySCF.
Input file generation for ORCA / Gaussian / PySCF.
"""
from __future__ import annotations

# ─── ORCA keyword mappings ──────────────────────────────────────────────────

ORCA_FUNCTIONAL: dict[str, str] = {
    "B3LYP":        "B3LYP",
    "B3LYP-D3BJ":   "B3LYP",
    "PBE0":         "PBE0",
    "PBE0-D3BJ":    "PBE0",
    "TPSSh":        "TPSSh",
    "TPSS-D3BJ":    "TPSS",
    "TPSSh-D3BJ":   "TPSSh",
    "M06-2X":       "M062X",
    "M06-L":        "M06L",
    "PBE":          "PBE",
    "BP86":         "BP86",
    "ωB97X-D":      "wB97X-D3",
    "CAM-B3LYP":    "CAM-B3LYP",
    "CASSCF/NEVPT2":"CASSCF",
    "PBE0-D3BJ / TPSS-D3BJ": "PBE0",
    "B3LYP-D3BJ, ωB97X-D, M06-2X": "B3LYP",
    "TPSS-D3BJ, TPSSh, M06-L": "TPSS",
    "PBE0-D3BJ, TPSS-D3BJ": "PBE0",
    "CASSCF/NEVPT2, TPSS-D3BJ": "CASSCF",
    "CASSCF/NEVPT2, PBE0-D3BJ": "CASSCF",
    "CCSD(T), MP2, B3LYP": "CCSD(T)",
}

ORCA_WF: dict[str, str] = {
    "hf":     "HF",
    "mp2":    "RI-MP2",
    "ccsd":   "CCSD(T)",
    "casscf": "CASSCF(2,2)",
}

ORCA_PROP_KW: dict[str, str] = {
    "geometry":    "OPT",
    "energy":      "",
    "excitation":  "TD-DFT",
    "nmr":         "NMR",
    "magnetism":   "EPR",
    "dispersion":  "OPT",
    "ionization":  "",
    "spin_density":"EPR",
}

ORCA_PROP_BLOCK: dict[str, str] = {
    "excitation": "%tddft\n  nroots 5\n  maxdim  5\nend\n",
    "nmr":        "%eprnmr\n  nuclei = all H { shift }\n  nuclei = all C { shift }\nend\n",
    "magnetism":  "%eprnmr\n  dtensor full\nend\n",
}

# ─── Gaussian keyword mappings ──────────────────────────────────────────────

GAUSS_FUNCTIONAL: dict[str, str] = {
    "B3LYP":     "B3LYP",
    "B3LYP-D3BJ":"B3LYP EmpiricalDispersion=GD3BJ",
    "PBE0":      "PBE1PBE",
    "PBE0-D3BJ": "PBE1PBE EmpiricalDispersion=GD3BJ",
    "TPSSh":     "TPSSh",
    "TPSS-D3BJ": "TPSS",
    "ωB97X-D":   "wB97XD",
    "CAM-B3LYP": "CAM-B3LYP",
    "M06-2X":    "M062X",
    "M06-L":     "M06L",
}

GAUSS_WF: dict[str, str] = {
    "hf":     "HF",
    "mp2":    "MP2",
    "ccsd":   "CCSD(T)",
    "casscf": "CASSCF(2,2)",
}

GAUSS_PROP_KW: dict[str, str] = {
    "geometry":    "Opt",
    "energy":      "SP",
    "excitation":  "TD",
    "nmr":         "NMR=GIAO",
    "magnetism":   "EPR",
    "dispersion":  "Opt",
    "ionization":  "SP",
    "spin_density":"Pop=NBO",
}

# ─── PySCF class / import mappings ──────────────────────────────────────────

PYSCF_CLASS: dict[str, str] = {
    "hf":     "scf.RHF",
    "dft_gga":    "dft.RKS",
    "dft_hybrid": "dft.RKS",
    "dft_meta":   "dft.RKS",
    "dft_rs":     "dft.RKS",
    "mp2":    "mp2.MP2",
    "ccsd":   "cc.CCSD",
    "casscf": "mcscf.CASSCF",
}

PYSCF_IMPORTS: dict[str, str] = {
    "hf":     "from pyscf import gto, scf",
    "dft_gga":    "from pyscf import gto, dft",
    "dft_hybrid": "from pyscf import gto, dft",
    "dft_meta":   "from pyscf import gto, dft",
    "dft_rs":     "from pyscf import gto, dft",
    "mp2":    "from pyscf import gto, scf, mp",
    "ccsd":   "from pyscf import gto, scf, cc",
    "casscf": "from pyscf import gto, scf, mcscf",
}


# ─── Helper ─────────────────────────────────────────────────────────────────

def _clean_basis(basis: str) -> str:
    """Return first basis set from a comma-separated list."""
    return basis.split(",")[0].strip()


def _orca_basis(basis: str) -> str:
    b = _clean_basis(basis)
    # ORCA uses hyphens for def2 bases
    return b.replace("def2-", "def2-")


def _orca_ecp_block(ecp: str | None, z: int, sym: str) -> str:
    if not ecp:
        return ""
    # Stuttgart ECPs in ORCA via %basis
    core_electrons = {
        "ECP-10": 10, "ECP-28": 28, "ECP-46": 46, "ECP-60": 60,
        "ECP-78": 78, "ECP-92": 92,
    }
    for tag, n in core_electrons.items():
        if tag in ecp:
            return f"%basis\n  NewECP {sym}\n    \"def2-ECP\"\n  end\nend\n"
    return ""


def _spin2s(mult: int | None) -> int:
    if mult is None:
        return 0
    return int(mult) - 1


def _casscf_active_space(z: int, block: str, spin_mult: int) -> str:
    """Return a CASSCF(n_el, n_orb) string adapted to the element's block.

    Rules (minimal reasonable active space):
    - bloc d : n_d electrons in 5 d-orbitals → (n_unpaired, 5)
    - bloc f : n_f electrons in 7 f-orbitals → (n_unpaired + 2, 7)  minimal
    - other  : (2, 2) minimal with warning comment
    """
    n_unpaired = spin_mult - 1
    if block == "d":
        n_el  = max(n_unpaired, 2)
        n_orb = 5
        return f"CASSCF({n_el},{n_orb})"
    if block == "f":
        n_el  = max(n_unpaired, 2)
        n_orb = 7
        return f"CASSCF({n_el},{n_orb})"
    return "CASSCF(2,2)"


# ─── ORCA ───────────────────────────────────────────────────────────────────

def generate_orca_input(
    element: dict,
    method_key: str,
    prop_key:   str,
    basis:      str,
    ecp:        str | None,
    functional: str | None,
    dispersion: str | None,
) -> str:
    sym  = element["symbol"]
    z    = element["atomic_number"]
    mult = int(element.get("spin_mult") or 1)
    name = element.get("name", sym)
    charge = 0

    # Method / functional keyword
    block = element.get("block", "s")
    if functional:
        # Use the first recommended functional
        f = functional.split(",")[0].split("+")[0].strip()
        method_kw = ORCA_FUNCTIONAL.get(f, ORCA_FUNCTIONAL.get(functional, f.split("-D3")[0]))
    elif method_key == "casscf":
        method_kw = _casscf_active_space(z, block, mult)
    else:
        method_kw = ORCA_WF.get(method_key, "HF")

    basis_kw = _orca_basis(basis)

    # Dispersion
    disp_kw = "D3BJ" if dispersion and "D3BJ" in (dispersion or "") else ""
    # Avoid D3BJ duplication if already in functional name
    if method_kw.endswith("-D3BJ") or "D3BJ" in method_kw:
        disp_kw = ""

    # Relativistic
    if z > 54:
        relat_kw = "ZORA"
        if "DKH" in basis or "SARC" in basis:
            relat_kw = "DKH"
    elif z > 36 and ("DKH" in basis or "SARC" in basis):
        relat_kw = "DKH2"
    else:
        relat_kw = ""

    # Property
    prop_kw = ORCA_PROP_KW.get(prop_key, "")

    kws = [k for k in [method_kw, basis_kw, disp_kw, relat_kw, prop_kw] if k]
    keywords_line = "! " + " ".join(kws)

    ecp_block   = _orca_ecp_block(ecp, z, sym)
    prop_block  = ORCA_PROP_BLOCK.get(prop_key, "")
    open_shell  = mult > 1

    pal_block = "%pal\n  nprocs 4\nend\n"

    return (
        f"# ORCA input — {name} ({sym}, Z={z})\n"
        f"# Method: {method_key} | Property: {prop_key}\n"
        f"# Generated by Mendeliev interactive periodic table\n\n"
        f"{keywords_line}\n\n"
        f"%maxcore 4000\n"
        f"{pal_block}"
        f"{ecp_block}"
        f"{prop_block}\n"
        f"* xyz {charge} {mult}\n"
        f"  {sym}  0.0  0.0  0.0\n"
        f"*\n"
    )


# ─── Gaussian ───────────────────────────────────────────────────────────────

def generate_gaussian_input(
    element: dict,
    method_key: str,
    prop_key:   str,
    basis:      str,
    ecp:        str | None,
    functional: str | None,
    dispersion: str | None,
) -> str:
    sym  = element["symbol"]
    z    = element["atomic_number"]
    mult = int(element.get("spin_mult") or 1)
    name = element.get("name", sym)
    charge = 0

    # Method
    block = element.get("block", "s")
    if functional:
        f = functional.split(",")[0].split("+")[0].strip()
        method_kw = GAUSS_FUNCTIONAL.get(f, GAUSS_FUNCTIONAL.get(functional, f.split("-D3")[0]))
    elif method_key == "casscf":
        method_kw = _casscf_active_space(z, block, mult)
    else:
        method_kw = GAUSS_WF.get(method_key, "HF")

    # Basis with ECP handling
    b = _clean_basis(basis)
    if ecp and z > 18:
        basis_kw = f"{b}/gen"
        gen_section = f"\n{sym} 0\n{b}\n****\n\n{sym} 0\n{ecp.split(' ')[0]}\n\n"
    else:
        basis_kw = b
        gen_section = ""

    prop_kw = GAUSS_PROP_KW.get(prop_key, "SP")

    # Relativistic (Gaussian uses DKH keyword)
    relat_kw = ""
    if z > 54 and "DKH" not in (basis or ""):
        relat_kw = "DKH"

    route = f"# {method_kw}/{basis_kw} {prop_kw} {relat_kw}".strip()

    open_shell_note = "! Note: use UHF/UDFT for open-shell (mult > 1)\n" if mult > 1 else ""

    return (
        f"%nprocshared=4\n"
        f"%mem=8GB\n"
        f"%chk={sym}_{method_key}_{prop_key}.chk\n"
        f"{route}\n\n"
        f"{name} ({sym}, Z={z}) — {method_key} / {prop_key}\n"
        f"# Generated by Mendeliev interactive periodic table\n"
        f"{open_shell_note}\n"
        f"{charge} {mult}\n"
        f"{sym}   0.00000   0.00000   0.00000\n"
        f"{gen_section}\n"
    )


# ─── PySCF ──────────────────────────────────────────────────────────────────

def generate_pyscf_script(
    element: dict,
    method_key: str,
    prop_key:   str,
    basis:      str,
    ecp:        str | None,
    functional: str | None,
    dispersion: str | None,
) -> str:
    sym  = element["symbol"]
    z    = element["atomic_number"]
    mult = int(element.get("spin_mult") or 1)
    name = element.get("name", sym)
    spin_2s = _spin2s(mult)
    charge  = 0

    imports = PYSCF_IMPORTS.get(method_key, "from pyscf import gto, scf")
    cls     = PYSCF_CLASS.get(method_key, "scf.RHF")

    b = _clean_basis(basis)
    ecp_line   = f"mol.ecp   = '{b}'  # Stuttgart ECP — see pyscf docs for element-specific ECP\n" if ecp else ""
    xc_line    = f"mf.xc = '{functional.split(',')[0].strip()}'\n" if functional else ""
    disp_line  = "# Grimme D3BJ: pip install dftd3 → from dftd3.pyscf import D3Dispersion; mf = D3Dispersion(mf).run()\n" if dispersion and dispersion != "N/A" else ""
    relat_note = "# Note: enable scalar relativistic via mf.with_x2c() for Z > 36\n" if z > 36 else ""

    prop_code: dict[str, str] = {
        "geometry":   "from pyscf.geomopt.geometric_solver import optimize\nmol_opt = optimize(mf)\n",
        "nmr":        "from pyscf.prop import nmr\nnmr_obj = nmr.RHF(mf).kernel()\n",
        "excitation": "from pyscf import tddft\ntd = tddft.TDDFT(mf)\ntd.nstates = 5\ntd.kernel()\n",
        "magnetism":  "# EPR / hyperfine: use pyscf.prop.epr\nfrom pyscf.prop import epr\n",
        "dispersion": "# NCI / SAPT: see pyscf.tools\n",
    }
    prop_snippet = prop_code.get(prop_key, "")

    use_u = "U" if spin_2s > 0 else ""
    cls_final = cls.replace("RKS", f"{use_u}KS").replace("RHF", f"{use_u}HF")

    return (
        f"# PySCF script — {name} ({sym}, Z={z})\n"
        f"# Method: {method_key} | Property: {prop_key}\n"
        f"# Generated by Mendeliev interactive periodic table\n\n"
        f"{imports}\n\n"
        f"mol = gto.Mole()\n"
        f"mol.verbose = 4\n"
        f"mol.atom    = '{sym} 0 0 0'\n"
        f"mol.basis   = '{b}'\n"
        f"{ecp_line}"
        f"mol.charge  = {charge}\n"
        f"mol.spin    = {spin_2s}   # 2S = {spin_2s}, mult = {mult}\n"
        f"mol.build()\n\n"
        f"mf = {cls_final}(mol)\n"
        f"{xc_line}"
        f"{relat_note}"
        f"{disp_line}"
        f"energy = mf.kernel()\n"
        f"print(f'Energy: {{energy:.8f}} Ha')\n\n"
        f"{prop_snippet}"
    )


# ─── Dispatcher ─────────────────────────────────────────────────────────────

def generate_input(
    software:   str,
    element:    dict,
    method_key: str,
    prop_key:   str,
    basis:      str,
    ecp:        str | None,
    functional: str | None,
    dispersion: str | None,
) -> str:
    """Return input file content for the given software."""
    dispatch = {
        "orca":     generate_orca_input,
        "gaussian": generate_gaussian_input,
        "pyscf":    generate_pyscf_script,
    }
    fn = dispatch.get(software, generate_orca_input)
    return fn(element, method_key, prop_key, basis, ecp, functional, dispersion)
