"""pages/cost.py — Page Estimateur de coût CPU/RAM."""
import dash
from cost_estimator_tab import create_cost_layout, register_callbacks

dash.register_page(__name__, path="/cost", order=5)

register_callbacks()

layout = create_cost_layout()
