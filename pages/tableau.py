"""
pages/tableau.py — Page principale : tableau périodique interactif.
Главная страница: интерактивная таблица Менделеева.
"""
from __future__ import annotations

import dash
import pandas as pd
from dash import html, dcc, Input, Output, State, callback, ctx, no_update
import plotly.graph_objs as go

from translations import LANG
from data_loader import (
    ELEMENTS_BY_Z, ELEMENTS_BY_SYM,
    CATEGORY_COLORS, COLOR_DEFAULT, build_dataframe,
)
from recommendation_engine import recommend, list_methods, list_properties
from input_generator import generate_input
from molecule_assistant import recommend_for_molecule

dash.register_page(__name__, path="/", name="Tableau", order=1)

# ─── Module-level data ───────────────────────────────────────────────────────

_df = build_dataframe()
_df["color"] = _df["category"].map(CATEGORY_COLORS).fillna(COLOR_DEFAULT)

_INIT_METHODS = list_methods("fr")
_INIT_PROPS   = list_properties("fr")

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
                    className="right-panel",
                    children=[
                        dcc.Tabs(
                            id="right-tabs",
                            value="tab-details",
                            className="right-tabs",
                            children=[
                                dcc.Tab(
                                    label="Détails",
                                    value="tab-details",
                                    id="tab-label-details",
                                    className="panel-tab",
                                    selected_className="panel-tab--selected",
                                    children=[
                                        html.Div(
                                            className="detail-card",
                                            children=[
                                                html.H2("Détails de l'élément", id="detail-card-title"),
                                                html.Div(
                                                    id="element-details",
                                                    className="details-content",
                                                    children=[html.P("Cliquez sur une case du tableau.")],
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                                dcc.Tab(
                                    label="Recommandations",
                                    value="tab-reco",
                                    id="tab-label-reco",
                                    className="panel-tab",
                                    selected_className="panel-tab--selected",
                                    children=[
                                        html.Div(
                                            className="reco-card",
                                            children=[
                                                html.Div(
                                                    className="reco-controls-row",
                                                    children=[
                                                        dcc.Dropdown(
                                                            id="method-filter",
                                                            options=_INIT_METHODS,
                                                            placeholder="Méthode de calcul",
                                                            clearable=True,
                                                            optionHeight=40,
                                                            className="filter-dropdown",
                                                        ),
                                                        dcc.Dropdown(
                                                            id="prop-filter",
                                                            options=_INIT_PROPS,
                                                            placeholder="Propriété cible",
                                                            clearable=True,
                                                            optionHeight=40,
                                                            className="filter-dropdown",
                                                        ),
                                                    ],
                                                ),
                                                html.Div(
                                                    id="recommendations-output",
                                                    className="reco-output",
                                                    children=[html.P("← Cliquez sur un élément.", className="reco-hint")],
                                                ),
                                                html.Hr(className="reco-separator"),
                                                html.Details(
                                                    className="export-section",
                                                    children=[
                                                        html.Summary(
                                                            "Exporter le fichier d'entrée",
                                                            id="export-summary",
                                                            className="export-summary",
                                                        ),
                                                        html.Div(className="export-controls", children=[
                                                            dcc.Dropdown(
                                                                id="export-sw-select",
                                                                options=[
                                                                    {"label": "ORCA", "value": "orca"},
                                                                    {"label": "Gaussian 16", "value": "gaussian"},
                                                                    {"label": "PySCF (Python)", "value": "pyscf"},
                                                                ],
                                                                value="orca",
                                                                clearable=False,
                                                                className="filter-dropdown",
                                                            ),
                                                            html.Button(
                                                                "Générer le fichier",
                                                                id="export-btn",
                                                                className="export-btn",
                                                                n_clicks=0,
                                                            ),
                                                        ]),
                                                        html.Pre(
                                                            id="export-output",
                                                            className="snippet-pre export-pre",
                                                            children="Générez d'abord une recommandation ci-dessus.",
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        html.Details(
            className="mol-assistant-section",
            children=[
                html.Summary(
                    "Assistant moléculaire",
                    id="mol-summary",
                    className="export-summary",
                ),
                html.Div(className="mol-controls-row", children=[
                    dcc.Input(
                        id="mol-formula-input",
                        type="text",
                        placeholder="Formule moléculaire (ex : H2O, FeCl3)",
                        className="search-input mol-input",
                    ),
                    dcc.Dropdown(
                        id="mol-prop-select",
                        options=_INIT_PROPS,
                        value="geometry",
                        clearable=False,
                        className="filter-dropdown mol-prop-dd",
                    ),
                    dcc.Input(
                        id="mol-charge-input",
                        type="number",
                        value=0,
                        min=-6,
                        max=6,
                        step=1,
                        placeholder="Charge",
                        className="search-input mol-charge-input",
                    ),
                    dcc.Input(
                        id="mol-mult-input",
                        type="number",
                        value=1,
                        min=1,
                        max=15,
                        step=1,
                        placeholder="Mult.",
                        className="search-input mol-mult-input",
                    ),
                    html.Button(
                        "Analyser",
                        id="mol-analyse-btn",
                        className="export-btn",
                        n_clicks=0,
                    ),
                ]),
                html.Div(
                    id="mol-output",
                    className="mol-output",
                    children=[html.P("Entrez une formule et cliquez sur Analyser.", className="reco-hint")],
                ),
            ],
        ),
    ],
)


# ─── Periodic figure builder ─────────────────────────────────────────────────

def _build_periodic_figure(group_filter=None, block_filter=None, ecp_filter=None,
                            search_value="", lang="fr") -> go.Figure:
    search_value = (search_value or "").strip().lower()
    is_match = pd.Series(True, index=_df.index)

    if group_filter is not None: is_match &= _df["group"]    == group_filter
    if block_filter is not None: is_match &= _df["block"]    == block_filter
    if ecp_filter   is not None: is_match &= _df["ecp_type"] == ecp_filter
    if search_value:
        name_col = "name_ru" if lang == "ru" else "name"
        is_match &= _df.apply(
            lambda row: search_value in row[name_col].lower() or search_value in row["symbol"].lower(),
            axis=1,
        )

    customdata_cols = _df[[
        "atomic_number", "symbol", "name", "group", "period",
        "block", "ecp_type", "basis_rec", "pseudo",
        "polarisabilite", "etats_ox", "volume_molaire",
        "ie1", "ea", "spin_mult", "vdw_radius",
        "functional", "dispersion", "relativistic", "name_ru",
    ]].values

    t = LANG[lang]
    name_idx = 19 if lang == "ru" else 2
    hover = (
        f"%{{customdata[1]}}<br>%{{customdata[{name_idx}]}}"
        f"<br>Z = %{{customdata[0]}} · {t['hover_bloc']} %{{customdata[5]}}"
        f"<br>IE₁ = %{{customdata[12]}} eV<extra></extra>"
    )

    fig = go.Figure()
    for idx, el in _df.iterrows():
        matched = bool(is_match[idx])
        fig.add_shape(
            type="rect",
            x0=el["col"] - 0.46, x1=el["col"] + 0.46,
            y0=el["row"] - 0.46, y1=el["row"] + 0.46,
            fillcolor=el["color"],
            opacity=1.0 if matched else 0.14,
            line=dict(color="#1a2a33" if matched else "#37474f", width=1),
            layer="below",
        )

    fig.add_trace(go.Scatter(
        x=_df["col"], y=_df["row"],
        mode="markers+text",
        marker=dict(size=2, color="rgba(0,0,0,0)", symbol="square"),
        text=_df["symbol"],
        textposition="middle center",
        textfont=dict(
            color=["rgba(255,255,255,1)" if m else "rgba(255,255,255,0.18)" for m in is_match],
            size=11, family="Inter",
        ),
        customdata=customdata_cols,
        hovertemplate=hover,
        showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=_df["col"] - 0.33, y=_df["row"] - 0.33,
        mode="text",
        text=[str(int(n)) for n in _df["atomic_number"]],
        textfont=dict(
            color=[f"rgba(255,255,255,{0.7 if m else 0.08})" for m in is_match],
            size=7, family="Inter",
        ),
        hoverinfo="skip", showlegend=False,
    ))

    for period in sorted(_df[_df["row"] <= 7]["period"].unique()):
        fig.add_annotation(x=0.3, y=period, xanchor="right", text=f"P{int(period)}",
                           showarrow=False, font=dict(color="#eceff1", size=11))
    fig.add_annotation(x=0.3, y=8, xanchor="right", text="6*", showarrow=False,
                       font=dict(color="#cfd8dc", size=10))
    fig.add_annotation(x=0.3, y=9, xanchor="right", text="7*", showarrow=False,
                       font=dict(color="#cfd8dc", size=10))

    fig.update_xaxes(
        title="", tickmode="array",
        tickvals=list(range(1, 19)), ticktext=[str(n) for n in range(1, 19)],
        range=[0.5, 18.5], showgrid=False, zeroline=False, showline=False,
        tickfont=dict(color="#cfd8dc", size=10), fixedrange=True,
    )
    fig.update_yaxes(
        title="", tickmode="array",
        tickvals=[1, 2, 3, 4, 5, 6, 7, 8, 9],
        ticktext=["1", "2", "3", "4", "5", "6", "7", "6*", "7*"],
        range=[9.5, 0.5], showgrid=False, zeroline=False, showline=False,
        tickfont=dict(color="#cfd8dc", size=10),
        scaleanchor="x", scaleratio=1, fixedrange=True,
    )
    fig.update_layout(
        plot_bgcolor="#102027", paper_bgcolor="#102027",
        margin=dict(l=20, r=20, t=15, b=25),
        hoverlabel=dict(bgcolor="#263238", font_size=12, font_family="Inter"),
        dragmode=False, showlegend=False, hoverdistance=40,
    )
    return fig


# ─── Callbacks ───────────────────────────────────────────────────────────────

@callback(
    Output("periodic-figure", "figure"),
    Input("group-filter", "value"),
    Input("block-filter", "value"),
    Input("ecp-filter", "value"),
    Input("search-input", "value"),
    State("lang", "data"),
)
def update_graph(group_value, block_value, ecp_value, search_value, lang):
    return _build_periodic_figure(group_value, block_value, ecp_value, search_value, lang or "fr")


@callback(
    Output("selected-element-z", "data"),
    Output("selected-element-block", "data"),
    Input("periodic-figure", "clickData"),
)
def update_selected_element(click_data):
    if not click_data or not click_data.get("points"):
        return no_update, no_update
    d = click_data["points"][0]["customdata"]
    return int(d[0]), d[5]


@callback(
    Output("element-details", "children"),
    Input("periodic-figure", "clickData"),
    State("lang", "data"),
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

    result = [
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
    ]

    el_data = ELEMENTS_BY_Z.get(z, {})
    nmr_isotopes = el_data.get("nmr_isotopes", [])
    notes_key = f"notes_{lang}"
    if nmr_isotopes:
        nmr_items = []
        for iso in nmr_isotopes:
            mass  = iso.get("mass", "?")
            spin  = iso.get("spin", "?")
            abund = iso.get("abund", "?")
            basis = iso.get("basis_rec", "")
            note  = iso.get(notes_key, "")
            line  = f"{sym}-{mass}  ·  spin={spin}  ·  {abund}%"
            if basis:
                line += f"  ·  {basis}"
            children_li = [line]
            if note:
                children_li += [html.Br(), html.Em(note, style={"color": "#90a4ae", "fontSize": "0.72rem"})]
            nmr_items.append(html.Li(children_li))
        result.append(html.Div(className="detail-section", children=[
            html.H4(t["sec_nmr"], className="detail-section-title"),
            html.Ul(className="detail-list", children=nmr_items),
        ]))
    else:
        result.append(html.Div(className="detail-section", children=[
            html.H4(t["sec_nmr"], className="detail-section-title"),
            html.P(t["no_nmr"], style={"fontSize": "0.78rem", "color": "#90a4ae", "margin": "4px 0"}),
        ]))

    orbital_info = el_data.get("orbital_info", {})
    if orbital_info:
        orb_rows = []
        if orbital_info.get("homo_type"):
            orb_rows.append((t["lbl_homo_type"], orbital_info["homo_type"]))
        if orbital_info.get("dft_challenge"):
            orb_rows.append((t["lbl_dft_challenge"], orbital_info["dft_challenge"]))
        if orbital_info.get("core_1s_eV") is not None:
            orb_rows.append((t["lbl_core_1s"], f"{orbital_info['core_1s_eV']} eV"))
        if orb_rows:
            result.append(section(t["sec_orbital"], orb_rows))

    result.append(html.Div(className="bse-link", children=[
        html.A(t["bse_link"], href="https://www.basissetexchange.org/",
               target="_blank", className="bse-anchor"),
    ]))
    return result


@callback(
    Output("recommendations-output", "children"),
    Output("last-recommendation", "data"),
    Input("periodic-figure", "clickData"),
    Input("method-filter", "value"),
    Input("prop-filter", "value"),
    State("lang", "data"),
    prevent_initial_call=True,
)
def update_recommendations(click_data, method_key, prop_key, lang):
    lang = lang or "fr"
    t = LANG[lang]

    if not click_data or not click_data.get("points"):
        return [html.P(t["reco_no_element"], className="reco-hint")], None

    d     = click_data["points"][0]["customdata"]
    z     = int(d[0])
    block = d[5]

    if not method_key or not prop_key:
        return [html.P(t["reco_no_filters"], className="reco-hint")], None

    el_data = ELEMENTS_BY_Z.get(z, {})
    el_name = el_data.get("name_ru", el_data.get("name", "?")) if lang == "ru" else el_data.get("name", "?")
    sym     = el_data.get("symbol", "?")

    rec = recommend(z, block, method_key, prop_key, lang)

    store_data = {
        "z": z, "method_key": method_key, "prop_key": prop_key,
        "basis": rec["basis"], "ecp": rec["ecp"],
        "functional": rec["functional"], "dispersion": rec["dispersion"],
    }

    children = []
    method_lbl = rec["method_info"].get(f"label_{lang}", method_key)
    prop_lbl   = rec["property_info"].get(f"label_{lang}", prop_key)
    children.append(html.Div(className="reco-header", children=[
        html.H3(f"{el_name} ({sym})  ·  Z = {z}"),
        html.P(f"{method_lbl}  →  {prop_lbl}", className="reco-subheader"),
    ]))

    rows = [(t["reco_basis_lbl"], rec["basis"])]
    if rec["aux_basis"]:
        rows.append((t["reco_aux_lbl"], rec["aux_basis"]))
    ecp_display = rec["ecp"] if rec["ecp"] else t["na_ecp"]
    rows.append((t["reco_ecp_lbl"], ecp_display))
    # Note explicative quand l'ECP est absent pour NMR/EPR
    if not rec["ecp"] and prop_key in ("nmr", "magnetism"):
        rows.append(("", t.get("ecp_nmr_note", "")))
    if rec["functional"]:
        disp = f"  +  {rec['dispersion']}" if rec["dispersion"] else ""
        rows.append((t["reco_func_lbl"], rec["functional"] + disp))
    rows.append((t["reco_relat_lbl"], rec["relativistic"]))
    children.append(html.Div(className="reco-summary-box detail-section", children=[
        html.Ul(className="detail-list", children=[
            html.Li([html.Strong(lbl + " : "), val]) for lbl, val in rows
        ])
    ]))

    if rec["notes"]:
        children.append(html.Div(className="reco-notes detail-section", children=[
            html.H4(t["reco_notes_lbl"], className="detail-section-title"),
            dcc.Markdown(rec["notes"], className="reco-notes-text"),
        ]))

    if rec["software"]:
        badges = [
            html.A(
                href=sw["url"], target="_blank", className="sw-badge",
                style={"background": sw.get("badge_color", "#888")},
                children=[
                    html.Span(sw.get(f"label_{lang}", sw["name"]), className="sw-badge-name"),
                    html.Span(t["free_badge"] if sw.get("free") else t["commercial_badge"], className="sw-badge-type"),
                ],
            )
            for sw in rec["software"]
        ]
        children.append(html.Div(className="reco-software detail-section", children=[
            html.H4(t["reco_software_lbl"], className="detail-section-title"),
            html.Div(badges, className="sw-badges-row"),
        ]))

    if rec["orca_snippet"]:
        children.append(html.Div(className="reco-snippet detail-section", children=[
            html.H4(t["reco_snippet_orca"], className="detail-section-title"),
            html.Pre(rec["orca_snippet"], className="snippet-pre"),
        ]))
    if rec["gaussian_snippet"]:
        children.append(html.Div(className="reco-snippet detail-section", children=[
            html.H4(t["reco_snippet_gaussian"], className="detail-section-title"),
            html.Pre(rec["gaussian_snippet"], className="snippet-pre"),
        ]))

    if rec["links"]:
        children.append(html.Div(className="reco-links detail-section", children=[
            html.H4(t["reco_links_lbl"], className="detail-section-title"),
            html.Ul(className="detail-list", children=[
                html.Li(html.A(lnk["label"], href=lnk["url"], target="_blank", className="reco-link"))
                for lnk in rec["links"]
            ]),
        ]))

    return children, store_data


@callback(
    Output("export-output", "children"),
    Input("export-btn", "n_clicks"),
    State("last-recommendation", "data"),
    State("export-sw-select", "value"),
    State("lang", "data"),
    prevent_initial_call=True,
)
def generate_export(n_clicks, store_data, software, lang):
    lang = lang or "fr"
    t = LANG[lang]
    if not store_data:
        return t["export_no_reco"]
    z  = store_data["z"]
    el = ELEMENTS_BY_Z.get(z, {})
    return generate_input(
        software or "orca", el,
        store_data["method_key"], store_data["prop_key"],
        store_data["basis"], store_data["ecp"],
        store_data["functional"], store_data["dispersion"],
    )


@callback(
    Output("mol-output", "children"),
    Output("mol-prop-select", "options"),
    Output("mol-prop-select", "placeholder"),
    Input("mol-analyse-btn", "n_clicks"),
    State("mol-formula-input", "value"),
    State("mol-prop-select", "value"),
    State("mol-charge-input", "value"),
    State("mol-mult-input", "value"),
    State("lang", "data"),
    prevent_initial_call=False,
)
def analyse_molecule(n_clicks, formula, prop_key, charge, mult, lang):
    lang = lang or "fr"
    t = LANG[lang]
    lk = lang if lang in ("fr", "ru") else "fr"
    opts = list_properties(lk)
    ph = t["reco_prop_ph"]

    if not formula or not n_clicks:
        return html.P(t["mol_no_result"], className="reco-hint"), opts, ph

    charge = int(charge) if charge is not None else 0
    mult   = max(1, int(mult)) if mult is not None else 1

    res = recommend_for_molecule(
        formula.strip(), prop_key or "geometry", lang, ELEMENTS_BY_SYM,
        charge=charge, mult=mult,
    )
    if res.get("error"):
        err = {
            "fr": f"Formule non reconnue : « {formula} »",
            "ru": f"Формула не распознана: «{formula}»",
        }.get(lk, f"Unrecognized formula: '{formula}'")
        return html.P(err, className="reco-hint"), opts, ph

    elem_str = "  ·  ".join(f"{s}×{c}" for s, c in sorted(res["elements"].items()))
    ecp_str  = res["ecp"] or t["mol_none"]

    children = [
        html.Div(className="reco-header", children=[
            html.H3(res["formula"]),
            html.P(elem_str, className="reco-subheader"),
        ]),
        html.Div(className="reco-summary-box detail-section", children=[
            html.Ul(className="detail-list", children=[
                html.Li([html.Strong(t["mol_method"] + " : "), res["method"]]),
                html.Li([html.Strong(t["mol_basis"]  + " : "), res["basis"]]),
                html.Li([html.Strong(t["mol_ecp"]    + " : "), ecp_str]),
                html.Li([
                    html.Strong("Charge / Multiplicité : "),
                    f"{res['charge']:+d}  /  {res['mult']}",
                ]),
            ])
        ]),
        html.Div(className="detail-section", children=[
            html.H4("Notes", className="detail-section-title"),
            html.P(res["method_note"], style={"fontSize": "0.78rem", "color": "#cfd8dc"}),
            *[html.P(note, style={"fontSize": "0.78rem", "color": "#ffb74d"})
              for note in res["extra_notes"]],
        ]),
    ]
    return children, opts, ph


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
    Output("tab-label-details", "label"),
    Output("tab-label-reco", "label"),
    Output("method-filter", "options"),
    Output("method-filter", "placeholder"),
    Output("prop-filter", "options"),
    Output("prop-filter", "placeholder"),
    Output("export-summary", "children"),
    Output("mol-summary", "children"),
    Input("lang", "data"),
)
def update_tableau_language(lang):
    lang = lang or "fr"
    lk = lang if lang in ("fr", "ru") else "fr"
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
        t["tab_details"],
        t["tab_reco"],
        list_methods(lk), t["reco_method_ph"],
        list_properties(lk), t["reco_prop_ph"],
        t["export_title"],
        t["mol_title"],
    )
