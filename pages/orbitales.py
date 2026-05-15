"""
pages/orbitales.py — Page Visualisation 3D des orbitales.
Страница 3D-визуализации орбиталей.
"""
import dash
from orbital_viewer import create_orbital_layout, register_callbacks

dash.register_page(__name__, path="/orbitales", order=4)

register_callbacks()

layout = create_orbital_layout()
