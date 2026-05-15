"""
pages/comparateur.py — Page Comparateur d'éléments.
Страница сравнения элементов.
"""
import dash
from data_loader import build_dataframe
from comparator_tab import create_comparator_layout, register_callbacks

dash.register_page(__name__, path="/comparateur", order=3)

_df = build_dataframe()
register_callbacks(_df)

layout = create_comparator_layout(_df)
