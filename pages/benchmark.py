"""pages/benchmark.py — Page Benchmark de méthodes."""
import dash
from benchmark_tab import create_benchmark_layout, register_callbacks

dash.register_page(__name__, path="/benchmark", order=9)

register_callbacks()

layout = create_benchmark_layout()
