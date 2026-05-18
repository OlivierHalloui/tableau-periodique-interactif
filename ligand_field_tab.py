"""
ligand_field_tab.py — Onglet diagramme champ de ligand.
Вкладка диаграммы поля лигандов.
"""
from __future__ import annotations

import plotly.graph_objs as go
from dash import html, dcc, Input, Output, State, callback
from ligand_field import compute_cfse, list_geometries, list_transition_metals, _DATA


def _make_level_diagram(geometry_key: str, filling: dict[str, int],
                        delta_o: float, lang: str) -> go.Figure:
    """Construit la figure du diagramme à niveaux d'énergie."""
    geom = _DATA["geometries"][geometry_key]
    levels = geom["levels"]

    fig = go.Figure()
    x_positions = {"octahedral": {"eg": 2, "t2g": 0},
                   "tetrahedral": {"e": 2, "t2": 0},
                   "square_planar": {"dx2y2": 3, "dxy": 2, "dz2": 1, "dxzdyz": 0}}
    x_pos = x_positions.get(geometry_key, {})

    colors = {"filled": "#64b5f6", "empty": "#555"}

    for k, v in levels.items():
        x = x_pos.get(k, 1)
        y = v["energy_frac"] * delta_o
        label = v["label"]
        ne = filling.get(k, 0)
        deg = v["degeneracy"]

        for slot in range(deg):
            x_base = x + slot * 0.25
            # Horizontal bar
            fig.add_shape(type="line",
                          x0=x_base - 0.1, x1=x_base + 0.1,
                          y0=y, y1=y,
                          line=dict(color="#aaa", width=3))

        # Electron arrows
        for e_idx in range(ne):
            x_base = x + (e_idx % deg) * 0.25
            direction = 1 if e_idx < deg else -1
            fig.add_annotation(
                x=x_base, y=y,
                text="↑" if direction == 1 else "↓",
                showarrow=False,
                font=dict(size=20, color="#64b5f6"),
            )

        fig.add_annotation(
            x=x + (deg - 1) * 0.25 / 2, y=y,
            text=label,
            showarrow=False,
            yshift=15,
            font=dict(size=13, color="#e0e0e0"),
        )

    delta_label = geom.get("delta_label", "Δ")
    yaxis_title = f"Énergie (fraction de {delta_label})" if lang == "fr" else f"Энергия (доля {delta_label})"

    fig.update_layout(
        height=380,
        margin={"t": 10, "b": 40, "l": 60, "r": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(title=yaxis_title, tickformat=".1f", gridcolor="#333",
                   zeroline=True, zerolinecolor="#555"),
        font_color="#e0e0e0",
    )
    fig.add_hline(y=0, line_dash="dot", line_color="#555")
    return fig


def create_ligand_field_layout() -> html.Div:
    metals = list_transition_metals()
    geometries_fr = list_geometries("fr")

    return html.Div(className="tab-content-pad", children=[
        html.H2("Diagramme de champ de ligand", id="lf-title"),
        html.P(
            "Visualisez le splitting des niveaux d selon la géométrie, "
            "le nombre d'électrons d et calculez l'énergie de stabilisation du champ cristallin (CFSE).",
            id="lf-subtitle",
        ),
        html.Div(className="trend-controls-row", children=[
            html.Div([
                html.Label("Métal de transition", id="lf-metal-label"),
                dcc.Dropdown(
                    id="lf-metal",
                    options=[{"value": m["value"], "label": m["label"]} for m in metals],
                    value=26,
                    clearable=False,
                    className="filter-dropdown",
                    style={"minWidth": "200px"},
                ),
            ], className="cost-field"),
            html.Div([
                html.Label("Nombre d'électrons d (ndₑ)", id="lf-nd-label"),
                dcc.Slider(id="lf-nd", min=0, max=10, step=1, value=6,
                           marks={i: str(i) for i in range(11)}),
            ], className="cost-field", style={"minWidth": "220px"}),
            html.Div([
                html.Label("Géométrie", id="lf-geom-label"),
                dcc.Dropdown(
                    id="lf-geometry",
                    options=geometries_fr,
                    value="octahedral",
                    clearable=False,
                    className="filter-dropdown",
                ),
            ], className="cost-field"),
            html.Div([
                html.Label("Spin", id="lf-spin-label"),
                dcc.RadioItems(
                    id="lf-spin",
                    options=[
                        {"label": "Haut spin (HS)", "value": "hs"},
                        {"label": "Bas spin (BS)", "value": "ls"},
                    ],
                    value="hs",
                    labelStyle={"display": "inline-block", "marginRight": "14px"},
                ),
            ], className="cost-field"),
            html.Div([
                html.Label("Δₒ (cm⁻¹)", id="lf-delta-label"),
                dcc.Input(id="lf-delta", type="number", value=10000, min=1000, max=60000,
                          step=100, className="cost-input"),
            ], className="cost-field"),
        ]),
        dcc.Graph(id="lf-diagram", config={"displayModeBar": False}),
        html.Div(id="lf-result"),
    ])


def register_callbacks(app=None):
    @callback(
        Output("lf-title",      "children"),
        Output("lf-subtitle",   "children"),
        Output("lf-metal-label","children"),
        Output("lf-nd-label",   "children"),
        Output("lf-geom-label", "children"),
        Output("lf-spin-label", "children"),
        Output("lf-delta-label","children"),
        Output("lf-geometry",   "options"),
        Input("lang", "data"),
    )
    def _lang(lang):
        lang = lang or "fr"
        geoms = list_geometries(lang)
        if lang == "ru":
            return (
                "Диаграмма поля лигандов",
                "Визуализируйте расщепление d-уровней и рассчитайте энергию стабилизации кристаллического поля (ЭСКП).",
                "Переходный металл", "Число d-электронов (ndₑ)", "Геометрия",
                "Спиновое состояние", "Δₒ (см⁻¹)", geoms,
            )
        return (
            "Diagramme de champ de ligand",
            "Visualisez le splitting des niveaux d et calculez la CFSE.",
            "Métal de transition", "Nombre d'électrons d (ndₑ)", "Géométrie",
            "Spin", "Δₒ (cm⁻¹)", geoms,
        )

    @callback(
        Output("lf-diagram", "figure"),
        Output("lf-result",  "children"),
        Input("lf-nd",       "value"),
        Input("lf-geometry", "value"),
        Input("lf-spin",     "value"),
        Input("lf-delta",    "value"),
        State("lang", "data"),
    )
    def _update(n_d, geometry_key, spin, delta_o, lang):
        lang = lang or "fr"
        n_d      = int(n_d or 0)
        delta_o  = float(delta_o or 10000)
        high_spin = (spin == "hs")

        try:
            cfse, filling, config_str = compute_cfse(n_d, geometry_key or "octahedral",
                                                      high_spin, delta_o)
        except Exception as e:
            empty = go.Figure()
            empty.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            return empty, html.P(str(e), style={"color": "red"})

        fig = _make_level_diagram(geometry_key or "octahedral", filling, delta_o, lang)

        geom_data = _DATA["geometries"].get(geometry_key or "octahedral", {})
        delta_label = geom_data.get("delta_label", "Δ")

        cfse_frac = cfse / delta_o if delta_o else 0
        cfse_sign = "−" if cfse < 0 else ("+" if cfse > 0 else "")
        cfse_str  = f"{cfse_sign}{abs(cfse_frac):.2f} {delta_label}  =  {cfse:.0f} cm⁻¹"

        spin_label = ("Haut spin" if high_spin else "Bas spin") if lang == "fr" else ("Высокоспиновый" if high_spin else "Низкоспиновый")

        if lang == "ru":
            info = html.Div([
                html.Div([html.Strong("Конфигурация : "), html.Span(config_str)]),
                html.Div([html.Strong("ЭСКП : "), html.Span(cfse_str,
                    style={"color": "#81c784" if cfse < 0 else "#e57373", "fontWeight": "bold"})]),
                html.Div([html.Strong("Спиновое состояние : "), html.Span(spin_label)]),
            ], style={"marginTop": "12px", "lineHeight": "1.8"})
        else:
            info = html.Div([
                html.Div([html.Strong("Configuration : "), html.Span(config_str)]),
                html.Div([html.Strong("CFSE : "), html.Span(cfse_str,
                    style={"color": "#81c784" if cfse < 0 else "#e57373", "fontWeight": "bold"})]),
                html.Div([html.Strong("État de spin : "), html.Span(spin_label)]),
            ], style={"marginTop": "12px", "lineHeight": "1.8"})

        return fig, info
