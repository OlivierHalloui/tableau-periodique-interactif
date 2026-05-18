"""pages/ligand_field.py — Page Diagramme de champ de ligand."""
import dash
from ligand_field_tab import create_ligand_field_layout, register_callbacks

dash.register_page(__name__, path="/ligand-field", order=8)

register_callbacks()

layout = create_ligand_field_layout()
