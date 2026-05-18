"""pages/dft_map.py — Page Carte des fonctionnelles DFT (Jacob's Ladder)."""
import dash
from dft_map_tab import create_dft_map_layout, register_callbacks

dash.register_page(__name__, path="/dft-map", order=11)

register_callbacks()

layout = create_dft_map_layout()
