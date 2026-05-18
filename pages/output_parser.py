"""pages/output_parser.py — Page Parseur de sorties ORCA/Gaussian."""
import dash
from output_parser_tab import create_output_parser_layout, register_callbacks

dash.register_page(__name__, path="/output-parser", order=10)

register_callbacks()

layout = create_output_parser_layout()
