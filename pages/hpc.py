"""pages/hpc.py — Page Générateur de scripts HPC."""
import dash
from hpc_tab import create_hpc_layout, register_callbacks

dash.register_page(__name__, path="/hpc", order=6)

register_callbacks()

layout = create_hpc_layout()
