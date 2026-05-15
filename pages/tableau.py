"""
pages/tableau.py — Page tableau périodique (unique page de la V1.5).
Страница таблицы Менделеева (единственная страница V1.5).
"""
from __future__ import annotations

import dash
from dash import html, dcc, Input, Output, State, callback, ctx

from data import build_dataframe, CATEGORY_COLORS, COLOR_DEFAULT
from translations import LANG
from figure import build_periodic_figure

dash.register_page(__name__, path="/", name="Tableau", order=1)

# ─── Module-level data ───────────────────────────────────────────────────────

_df = build_dataframe()

# ─── Layout ──────────────────────────────────────────────────────────────────

layout = html.Div(
    className="tab-content-pad",
    children=[
        html.Div(
            className="controls-row",
            children=[
                dcc.Dropdown(
                    id="group-filter",
                    options=[
                        {"label": f"Groupe {int(g)}", "value": int(g)}
                        for g in sorted(_df[_df["row"] <= 7]["group"].unique())
                    ],
                    placeholder="Filtrer par groupe",
                    clearable=True,
                    className="filter-dropdown",
                ),
                dcc.Dropdown(
                    id="block-filter",
                    options=[
                        {"label": "Bloc s  (alcalins, alcalino-terreux, H, He)", "value": "s"},
                        {"label": "Bloc p  (non-métaux, halogènes, gaz nobles…)", "value": "p"},
                        {"label": "Bloc d  (métaux de transition)", "value": "d"},
                        {"label": "Bloc f  (lanthanides & actinides)", "value": "f"},
                    ],
                    placeholder="Filtrer par bloc",
                    clearable=True,
                    className="filter-dropdown",
                ),
                dcc.Dropdown(
                    id="ecp-filter",
                    options=[
                        {"label": "Tous-électrons (Z ≤ 18)", "value": "Tous-électrons"},
                        {"label": "ECP optionnel (Z 19–36)", "value": "ECP optionnel"},
                        {"label": "ECP recommandé (Z 37–54)", "value": "ECP recommandé"},
                        {"label": "ECP requis (Z 55–86)", "value": "ECP requis"},
                        {"label": "ECP / relativiste (Z ≥ 87)", "value": "ECP/relativiste"},
                    ],
                    placeholder="Filtrer par traitement ECP",
                    clearable=True,
                    className="filter-dropdown",
                ),
                dcc.Input(
                    id="search-input",
                    type="text",
                    placeholder="Rechercher par nom ou symbole",
                    className="search-input",
                ),
            ],
        ),
        html.Div(
            id="legend-row",
            className="legend-row",
            children=[
                html.Span([
                    html.Span(className="legend-dot", style={"background": color}),
                    html.Span(label, className="legend-label"),
                ], className="legend-item")
                for label, color in CATEGORY_COLORS.items()
            ],
        ),
        html.Div(
            className="main-grid",
            children=[
                html.Div(
                    className="chart-card",
                    children=[
                        dcc.Graph(
                            id="periodic-figure",
                            config={"displayModeBar": False},
                            className="periodic-graph",
                        )
                    ],
                ),
                html.Div(
                    className="detail-card",
                    children=[
                        html.H2("Détails de l'élément", id="detail-card-title"),
                        html.Div(
                            id="element-details",
                            className="details-content",
                            children=[html.P("Cliquez sur une case du tableau pour afficher les propriétés de l'élément.")],
                        ),
                    ],
                ),
            ],
        ),
    ],
)


# ─── Callbacks ───────────────────────────────────────────────────────────────

@callback(
    Output("periodic-figure", "figure"),
    Input("group-filter", "value"),
    Input("block-filter", "value"),
    Input("ecp-filter", "value"),
    Input("search-input", "value"),
    Input("lang", "data"),
)
def update_graph(group_value, block_value, ecp_value, search_value, lang):
    return build_periodic_figure(_df, group_value, block_value, ecp_value, search_value, lang or "fr")


@callback(
    Output("element-details", "children"),
    Input("periodic-figure", "clickData"),
    Input("lang", "data"),
)
def display_element_details(click_data, lang):
    lang = lang or "fr"
    t = LANG[lang]

    if not click_data or not click_data.get("points"):
        return [html.P(t["click_hint"])]

    d = click_data["points"][0]["customdata"]
    z, sym = int(d[0]), d[1]
    name = d[19] if lang == "ru" else d[2]
    group, period, block = int(d[3]), int(d[4]), d[5]

    def fmt(v, unit="", decimals=3):
        return f"{round(v, decimals)} {unit}".strip() if v is not None else t["na"]

    def section(title, rows):
        return html.Div(className="detail-section", children=[
            html.H4(title, className="detail-section-title"),
            html.Ul(className="detail-list", children=[
                html.Li([html.Strong(lbl + " : "), val]) for lbl, val in rows
            ]),
        ])

    ecp_val   = t["ecp_values"].get(d[6], d[6])
    relat_val = t["relat_values"].get(d[18], d[18])
    disp_val  = t["disp_values"].get(d[17], d[17])
    pseudo_val = t["pseudo_none"] if d[8] == "Aucun" else d[8]

    return [
        html.Div(className="detail-header", children=[
            html.H3(f"{name} ({sym})"),
            html.Span(
                f"Z = {z}  ·  {t['lbl_group']} {group}  ·  {t['lbl_period']} {period}  ·  {t['lbl_block']} {block}",
                className="detail-subtitle",
            ),
        ]),
        section(t["sec_electronic"], [
            (t["lbl_ox"],   d[10]),
            (t["lbl_spin"], str(int(d[14])) if d[14] is not None else t["na"]),
            (t["lbl_ie1"],  fmt(d[12], "eV")),
            (t["lbl_ea"],   fmt(d[13], "eV")),
        ]),
        section(t["sec_atomic"], [
            (t["lbl_alpha"], fmt(d[9], "Å³")),
            (t["lbl_vdw"],   fmt(d[15], "Å")),
            (t["lbl_vol"],   fmt(d[11], "cm³/mol", 2)),
        ]),
        section(t["sec_compchem"], [
            (t["lbl_ecp"],   ecp_val),
            (t["lbl_basis"], d[7]),
            (t["lbl_pseudo"], pseudo_val),
            (t["lbl_func"],  d[16]),
            (t["lbl_disp"],  disp_val),
            (t["lbl_relat"], relat_val),
        ]),
        html.Div(className="bse-link", children=[
            html.A(t["bse_link"], href="https://www.basissetexchange.org/",
                   target="_blank", className="bse-anchor"),
        ]),
    ]


@callback(
    Output("detail-card-title", "children"),
    Output("group-filter", "options"),
    Output("group-filter", "placeholder"),
    Output("block-filter", "options"),
    Output("block-filter", "placeholder"),
    Output("ecp-filter", "options"),
    Output("ecp-filter", "placeholder"),
    Output("search-input", "placeholder"),
    Output("legend-row", "children"),
    Input("lang", "data"),
)
def update_tableau_language(lang):
    lang = lang or "fr"
    t = LANG[lang]
    groups = [
        {"label": f"{t['group_label']} {int(g)}", "value": int(g)}
        for g in sorted(_df[_df["row"] <= 7]["group"].unique())
    ]
    legend = [
        html.Span([
            html.Span(className="legend-dot", style={"background": color}),
            html.Span(t["categories"].get(cat, cat), className="legend-label"),
        ], className="legend-item")
        for cat, color in CATEGORY_COLORS.items()
    ]
    return (
        t["detail_title"],
        groups, t["group_ph"],
        t["blocks"], t["block_ph"],
        t["ecps"], t["ecp_ph"],
        t["search_ph"],
        legend,
    )
