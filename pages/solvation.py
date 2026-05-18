"""pages/solvation.py — Page Effets de solvant PCM/COSMO."""
import dash
from solvation_tab import create_solvation_layout, register_callbacks

dash.register_page(__name__, path="/solvation", order=7)

register_callbacks()

layout = create_solvation_layout()
