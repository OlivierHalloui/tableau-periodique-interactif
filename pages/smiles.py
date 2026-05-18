"""pages/smiles.py — Page Analyse SMILES (RDKit)."""
import dash
from smiles_tab import create_smiles_layout, register_callbacks

dash.register_page(__name__, path="/smiles", order=12)

register_callbacks()

layout = create_smiles_layout()
