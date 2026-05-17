"""
comparator_tab.py — Comparateur d'éléments : radar + tableau.
Сравнение элементов: радарная диаграмма + таблица.
Element Comparator: radar chart + property table.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from dash import html, dcc, Input, Output, State, callback
import plotly.graph_objs as go

# Properties shown in radar/table
COMP_PROPS: list[dict] = [
    {"key": "ie1",               "fr": "IE₁ (eV)",             "ru": "IE₁ (эВ)",              "en": "IE₁ (eV)"},
    {"key": "ea",                "fr": "EA (eV)",               "ru": "EA (эВ)",               "en": "EA (eV)"},
    {"key": "electronegativity", "fr": "Électronégativité",     "ru": "Электроотриц.",         "en": "Electronegativity"},
    {"key": "atomic_radius",     "fr": "Rayon atomique (pm)",   "ru": "Рад. ат. (пм)",         "en": "Atomic Radius (pm)"},
    {"key": "vdw_radius",        "fr": "Rayon VdW (Å)",         "ru": "Рад. ВдВ (Å)",          "en": "VdW Radius (Å)"},
    {"key": "polarisabilite",    "fr": "Polarisab. (Å³)",       "ru": "Поляриз. (Å³)",         "en": "Polarizab. (Å³)"},
    {"key": "density",           "fr": "Densité (g/cm³)",       "ru": "Плотность (г/см³)",     "en": "Density (g/cm³)"},
    {"key": "melting_point",     "fr": "Fusion (K)",            "ru": "Пл. плавл. (К)",        "en": "Melting Pt (K)"},
]

RADAR_COLORS = ["#64b5f6", "#81c784", "#ffb74d", "#f48fb1"]


def _elem_options(df_main: pd.DataFrame, lang: str) -> list[dict]:
    name_col = "name_ru" if lang == "ru" else "name"
    dff = df_main.drop_duplicates(subset="atomic_number", keep="first").sort_values("atomic_number")
    return [
        {"label": f"({int(r['atomic_number'])}) {r['symbol']} — {r.get(name_col, r['name'])}", "value": int(r["atomic_number"])}
        for _, r in dff.iterrows()
    ]


def create_comparator_layout(df_main: pd.DataFrame) -> html.Div:
    opts = _elem_options(df_main, "fr")
    return html.Div(className="tab-content-pad", children=[
        html.Div(className="comp-controls-row", children=[
            dcc.Dropdown(
                id="comp-elem-select",
                options=opts,
                value=[1, 6, 14, 26],
                multi=True,
                placeholder="Sélectionner 2–4 éléments…",
                className="filter-dropdown comp-multiselect",
            ),
        ]),
        html.Div(className="comp-charts-row", children=[
            html.Div(className="comp-radar", children=[
                dcc.Graph(id="comp-radar-chart",
                          style={"height": "100%"},
                          config={"displayModeBar": False}),
            ]),
            html.Div(id="comp-table", className="comp-table-wrap"),
        ]),
    ])


def _normalize_col(series: pd.Series) -> pd.Series:
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series(0.5, index=series.index)
    return (series - mn) / (mx - mn)


def register_callbacks(df_main: pd.DataFrame) -> None:

    @callback(
        Output("comp-radar-chart", "figure"),
        Output("comp-table", "children"),
        Input("comp-elem-select", "value"),
        State("lang", "data"),
    )
    def update_comparator(zs: list[int] | None, lang: str | None) -> tuple:
        lang = lang or "fr"
        lk   = lang if lang in ("fr", "ru") else "fr"
        name_col = "name_ru" if lang == "ru" else "name"

        if not zs or len(zs) < 2:
            no_sel = {"fr": "Sélectionnez au moins 2 éléments.",
                      "ru": "Выберите не менее 2 элементов.",
                      "en": "Select at least 2 elements."}[lk]
            return go.Figure(), html.P(no_sel, className="reco-hint")

        # Limit to 4
        zs = list(zs)[:4]
        dff = (df_main
               .drop_duplicates(subset="atomic_number", keep="first")
               .set_index("atomic_number")
               .loc[[z for z in zs if z in df_main["atomic_number"].values]])

        prop_keys = [p["key"] for p in COMP_PROPS]
        prop_labels = [p[lk] for p in COMP_PROPS]

        # Normalize across all 118 elements for the radar
        dfall = df_main.drop_duplicates(subset="atomic_number", keep="first")
        norms: dict[str, pd.Series] = {}
        for pk in prop_keys:
            col = pd.to_numeric(dfall[pk], errors="coerce")
            norms[pk] = _normalize_col(col)

        fig = go.Figure()
        for i, (z, row) in enumerate(dff.iterrows()):
            el_name = row.get(name_col, row["name"])
            sym = row["symbol"]
            radar_vals: list[float] = []
            for pk in prop_keys:
                idx = dfall[dfall["atomic_number"] == z].index
                val = norms[pk].reindex(idx).iloc[0] if len(idx) > 0 else 0.0
                radar_vals.append(float(val) if not np.isnan(float(val)) else 0.0)
            # Close the radar
            radar_vals_closed = radar_vals + [radar_vals[0]]
            labels_closed     = prop_labels + [prop_labels[0]]
            fig.add_trace(go.Scatterpolar(
                r=radar_vals_closed,
                theta=labels_closed,
                fill="toself",
                name=f"{sym} — {el_name}",
                line=dict(color=RADAR_COLORS[i % 4], width=2),
                fillcolor=RADAR_COLORS[i % 4].replace(")", ",0.15)").replace("rgb", "rgba"),
                opacity=0.85,
            ))

        fig.update_layout(
            polar=dict(
                bgcolor="#0d1b25",
                radialaxis=dict(visible=True, range=[0, 1], color="#90a4ae",
                                gridcolor="#1e3040", tickfont=dict(size=8)),
                angularaxis=dict(color="#cfd8dc", gridcolor="#1e3040"),
            ),
            showlegend=True,
            legend=dict(font=dict(color="#cfd8dc", size=11), bgcolor="rgba(0,0,0,0)"),
            paper_bgcolor="#102027",
            plot_bgcolor="#102027",
            margin=dict(l=30, r=30, t=30, b=30),
            font=dict(color="#cfd8dc", family="Inter"),
            height=448,
            autosize=True,
        )

        # Table
        headers_lbl = {"fr": "Propriété", "ru": "Свойство", "en": "Property"}[lk]
        head_cells = [html.Th(headers_lbl, className="comp-th")]
        for z, row in dff.iterrows():
            head_cells.append(html.Th(f"{row['symbol']} (Z={z})", className="comp-th"))

        body_rows = []
        for p in COMP_PROPS:
            cells = [html.Td(p[lk], className="comp-td-label")]
            for z, row in dff.iterrows():
                raw = row.get(p["key"])
                try:
                    val = f"{float(raw):.4g}" if raw is not None else "—"
                except (TypeError, ValueError):
                    val = "—"
                cells.append(html.Td(val, className="comp-td"))
            body_rows.append(html.Tr(cells))

        table = html.Table(
            className="comp-table",
            children=[
                html.Thead(html.Tr(head_cells)),
                html.Tbody(body_rows),
            ],
        )

        return fig, table

    @callback(
        Output("comp-elem-select", "options"),
        Output("comp-elem-select", "placeholder"),
        Input("lang", "data"),
    )
    def update_comparator_lang(lang: str | None) -> tuple:
        lang = lang or "fr"
        lk   = lang if lang in ("fr", "ru") else "fr"
        ph = {
            "fr": "Sélectionner 2–4 éléments…",
            "ru": "Выберите 2–4 элемента…",
            "en": "Select 2–4 elements…",
        }[lk]
        return _elem_options(df_main, lang), ph
