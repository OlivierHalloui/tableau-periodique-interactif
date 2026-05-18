"""
benchmark_tab.py — Onglet benchmark de méthodes DFT/WF.
Вкладка бенчмарка методов DFT/ВФТ.
"""
from __future__ import annotations

import json
from pathlib import Path

import plotly.graph_objs as go
from dash import html, dcc, Input, Output, callback

_DATA = json.loads(
    (Path(__file__).parent / "data" / "benchmarks.json").read_text(encoding="utf-8")
)

_ALL_SETS     = list(_DATA["sets"].keys())
_ALL_METHODS  = sorted({r["method"] for r in _DATA["results"]})
_METRIC_KEYS  = {"mad": "mad_kcal", "max": "max_kcal", "cost": "cost_rel"}

_RUNG_COLORS  = {1: "#e74c3c", 2: "#e67e22", 3: "#f1c40f", 4: "#2ecc71", 5: "#9b59b6"}


def create_benchmark_layout() -> html.Div:
    return html.Div(className="tab-content-pad", children=[
        html.H2("Benchmark de méthodes de calcul", id="bm-title"),
        html.P(
            "Comparaison de la précision des fonctionnelles DFT et méthodes WF sur les ensembles "
            "de référence GMTKN55, S22, W4-17 et BARRIER.",
            id="bm-subtitle",
        ),
        html.Div(className="trend-controls-row", children=[
            html.Div([
                html.Label("Ensembles de référence", id="bm-sets-label"),
                dcc.Checklist(
                    id="bm-sets",
                    options=[{"label": k, "value": k} for k in _ALL_SETS],
                    value=["GMTKN55"],
                    labelStyle={"display": "inline-block", "marginRight": "10px"},
                ),
            ], className="cost-field"),
            html.Div([
                html.Label("Méthodes", id="bm-methods-label"),
                dcc.Dropdown(
                    id="bm-methods",
                    options=[{"label": m, "value": m} for m in _ALL_METHODS],
                    value=["B3LYP", "PBE0-D3BJ", "ωB97X-D", "CCSD(T)"],
                    multi=True,
                    className="filter-dropdown",
                ),
            ], className="cost-field", style={"minWidth": "300px"}),
            html.Div([
                html.Label("Métrique", id="bm-metric-label"),
                dcc.RadioItems(
                    id="bm-metric",
                    options=[
                        {"label": "MAD (kcal/mol)", "value": "mad"},
                        {"label": "Erreur max (kcal/mol)", "value": "max"},
                        {"label": "Coût relatif", "value": "cost"},
                    ],
                    value="mad",
                    labelStyle={"display": "inline-block", "marginRight": "12px"},
                ),
            ], className="cost-field"),
        ]),
        dcc.Graph(id="bm-graph", config={"displayModeBar": False}),
        html.Div(id="bm-table-div", style={"marginTop": "16px"}),
        html.Div(id="bm-refs", style={"marginTop": "12px", "fontSize": "0.8em", "color": "#aaa"}),
    ])


def register_callbacks(app=None):
    @callback(
        Output("bm-title",       "children"),
        Output("bm-subtitle",    "children"),
        Output("bm-sets-label",  "children"),
        Output("bm-methods-label","children"),
        Output("bm-metric-label","children"),
        Input("lang", "data"),
    )
    def _lang(lang):
        lang = lang or "fr"
        if lang == "ru":
            return (
                "Бенчмарк методов расчёта",
                "Сравнение точности функционалов DFT и методов ВФТ на наборах GMTKN55, S22, W4-17 и BARRIER.",
                "Тестовые наборы", "Методы", "Метрика",
            )
        return (
            "Benchmark de méthodes de calcul",
            "Comparaison de la précision des méthodes sur GMTKN55, S22, W4-17 et BARRIER.",
            "Ensembles de référence", "Méthodes", "Métrique",
        )

    @callback(
        Output("bm-graph",     "figure"),
        Output("bm-table-div", "children"),
        Output("bm-refs",      "children"),
        Input("bm-sets",    "value"),
        Input("bm-methods", "value"),
        Input("bm-metric",  "value"),
        Input("lang", "data"),
    )
    def _update(sets, methods, metric, lang):
        lang = lang or "fr"
        sets    = sets    or _ALL_SETS
        methods = methods or _ALL_METHODS
        metric  = metric  or "mad"
        metric_key = _METRIC_KEYS.get(metric, "mad_kcal")

        rows = [r for r in _DATA["results"]
                if r["set"] in sets and r["method"] in methods]

        fig = go.Figure()
        for bm_set in sets:
            set_rows = [r for r in rows if r["set"] == bm_set]
            set_rows.sort(key=lambda x: x.get(metric_key, 999))
            if not set_rows:
                continue
            color = _RUNG_COLORS.get(set_rows[0].get("rung", 3), "#888")
            fig.add_trace(go.Bar(
                name=bm_set,
                x=[r["method"] for r in set_rows],
                y=[r.get(metric_key, 0) for r in set_rows],
                marker_color=[_RUNG_COLORS.get(r.get("rung", 3), "#888") for r in set_rows],
                text=[f"{r.get(metric_key, 0):.2f}" for r in set_rows],
                textposition="outside",
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    f"{metric_key}: " + "%{y:.2f}<extra>" + bm_set + "</extra>"
                ),
            ))

        metric_labels = {
            "mad":  "MAD (kcal/mol)" if lang == "fr" else "СПО (ккал/моль)",
            "max":  "Erreur max (kcal/mol)" if lang == "fr" else "Макс. погрешность",
            "cost": "Coût relatif (DFT GGA = 1)" if lang == "fr" else "Относит. стоимость",
        }

        fig.update_layout(
            barmode="group",
            height=380,
            margin={"t": 10, "b": 100, "l": 60, "r": 10},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e0e0e0",
            yaxis_title=metric_labels.get(metric, ""),
            xaxis_tickangle=-30,
            legend_title="Ensemble" if lang == "fr" else "Набор",
        )

        # Summary table
        seen = {}
        for r in rows:
            k = r["method"]
            if k not in seen:
                seen[k] = r
        table_rows = sorted(seen.values(), key=lambda x: x.get("mad_kcal", 999))

        hdr = (["Méthode", "Rung", "MAD (kcal/mol)", "Coût rel.", "Dispersion"]
               if lang == "fr" else
               ["Метод", "Ступень", "СПО (ккал/моль)", "Относит. стоимость", "Дисперсия"])
        disp_yes = "✓" if lang == "fr" else "Да"
        disp_no  = "—"

        t_rows = [html.Tr([
            html.Td(r["method"]),
            html.Td(str(r.get("rung", "?"))),
            html.Td(f"{r['mad_kcal']:.2f}"),
            html.Td(f"{r['cost_rel']:.1f}×"),
            html.Td(disp_yes if r.get("dispersion") else disp_no),
        ]) for r in table_rows]

        table = html.Table(
            [html.Thead(html.Tr([html.Th(h) for h in hdr])),
             html.Tbody(t_rows)],
            className="cost-table",
        )

        refs = html.Div([
            html.Strong("Sources : " if lang == "fr" else "Источники: "),
            *[html.Span([html.A(k, href=v["url"], target="_blank"), " · "])
              for k, v in _DATA["sets"].items()],
        ])

        return fig, table, refs
