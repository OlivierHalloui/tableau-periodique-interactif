"""
pages/tendances.py — Page Tendances périodiques.
Страница периодических тенденций.
"""
import dash
from data_loader import build_dataframe
from trends_tab import create_trends_layout, register_callbacks

dash.register_page(__name__, path="/tendances", order=2)

_df = build_dataframe()
register_callbacks(_df)

layout = create_trends_layout()
