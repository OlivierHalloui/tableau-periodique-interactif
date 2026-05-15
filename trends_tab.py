"""
trends_tab.py — Onglet Tendances : visualisation des tendances périodiques.
Вкладка Тенденции: визуализация периодических трендов.
Trends Tab: periodic trend visualization.
"""
from __future__ import annotations

import pandas as pd
from dash import html, dcc, Input, Output, callback

import plotly.graph_objs as go

BLOCK_COLORS: dict[str, str] = {
    "s": "#64b5f6",
    "p": "#81c784",
    "d": "#ffb74d",
    "f": "#ce93d8",
}

TREND_PROPS: dict[str, dict[str, str]] = {
    "ie1":               {"fr": "1ère énergie d'ionisation (eV)",   "ru": "Потенциал ионизации IE₁ (эВ)",     "en": "1st Ionization Energy (eV)"},
    "ea":                {"fr": "Affinité électronique (eV)",        "ru": "Сродство к электрону (эВ)",        "en": "Electron Affinity (eV)"},
    "electronegativity": {"fr": "Électronégativité (Pauling)",       "ru": "Электроотрицательность (Полинг)",  "en": "Electronegativity (Pauling)"},
    "atomic_radius":     {"fr": "Rayon atomique (pm)",               "ru": "Атомный радиус (пм)",              "en": "Atomic Radius (pm)"},
    "vdw_radius":        {"fr": "Rayon de van der Waals (Å)",        "ru": "Радиус Ван-дер-Ваальса (Å)",       "en": "VdW Radius (Å)"},
    "polarisabilite":    {"fr": "Polarisabilité (Å³)",               "ru": "Поляризуемость (Å³)",              "en": "Polarizability (Å³)"},
    "density":           {"fr": "Densité (g/cm³)",                   "ru": "Плотность (г/см³)",                "en": "Density (g/cm³)"},
    "melting_point":     {"fr": "Point de fusion (K)",               "ru": "Температура плавления (К)",        "en": "Melting Point (K)"},
    "boiling_point":     {"fr": "Point d'ébullition (K)",            "ru": "Температура кипения (К)",          "en": "Boiling Point (K)"},
    "spin_mult":         {"fr": "Multiplicité de spin (2S+1)",       "ru": "Мультиплетность (2S+1)",           "en": "Spin Multiplicity (2S+1)"},
}

VIEW_OPTIONS: dict[str, list[dict]] = {
    "fr": [
        {"label": "Par numéro atomique (Z)", "value": "z"},
        {"label": "Par groupe",              "value": "group"},
        {"label": "Par période",             "value": "period"},
    ],
    "ru": [
        {"label": "По атомному номеру (Z)",  "value": "z"},
        {"label": "По группе",               "value": "group"},
        {"label": "По периоду",              "value": "period"},
    ],
    "en": [
        {"label": "By Atomic Number (Z)",    "value": "z"},
        {"label": "By Group",                "value": "group"},
        {"label": "By Period",               "value": "period"},
    ],
}


def _prop_options(lang: str) -> list[dict]:
    k = lang if lang in ("fr", "ru") else "fr"
    return [{"label": v[k], "value": key} for key, v in TREND_PROPS.items()]


def create_trends_layout() -> html.Div:
    return html.Div(className="tab-content-pad", children=[
        html.Div(className="trend-controls-row", children=[
            dcc.Dropdown(
                id="trend-prop-select",
                options=_prop_options("fr"),
                value="ie1",
                clearable=False,
                className="filter-dropdown",
            ),
            dcc.Dropdown(
                id="trend-view-select",
                options=VIEW_OPTIONS["fr"],
                value="z",
                clearable=False,
                className="filter-dropdown",
            ),
        ]),
        dcc.Graph(
            id="trend-chart",
            className="trend-chart",
            config={"displayModeBar": True, "toImageButtonOptions": {"format": "svg", "filename": "tendances_periodiques"}},
        ),
    ])


def register_callbacks(df_main: pd.DataFrame) -> None:

    @callback(
        Output("trend-chart", "figure"),
        Output("trend-prop-select", "options"),
        Output("trend-view-select", "options"),
        Input("trend-prop-select", "value"),
        Input("trend-view-select", "value"),
        Input("lang", "data"),
    )
    def update_trend(prop: str | None, view: str | None, lang: str | None) -> tuple:
        lang  = lang  or "fr"
        prop  = prop  or "ie1"
        view  = view  or "z"
        lk    = lang if lang in ("fr", "ru") else "fr"
        y_lbl = TREND_PROPS.get(prop, {}).get(lk, prop)

        # Deduplicate by Z (La/Ac appear twice)
        dff = (df_main
               .drop_duplicates(subset="atomic_number", keep="first")
               .dropna(subset=[prop])
               .copy())
        dff[prop] = pd.to_numeric(dff[prop], errors="coerce")
        dff = dff.dropna(subset=[prop])

        name_col = "name_ru" if lang == "ru" else "name"

        fig = go.Figure()

        if view == "z":
            x_col = "atomic_number"
            x_title = {"fr": "Numéro atomique (Z)", "ru": "Атомный номер (Z)", "en": "Atomic Number (Z)"}[lk]
        elif view == "group":
            x_col = "group"
            dff = dff.dropna(subset=["group"])
            x_title = {"fr": "Groupe", "ru": "Группа", "en": "Group"}[lk]
        else:
            x_col = "period"
            dff = dff.dropna(subset=["period"])
            x_title = {"fr": "Période", "ru": "Период", "en": "Period"}[lk]

        for block, grp in dff.groupby("block"):
            grp = grp.sort_values(x_col)
            connect = (view == "z")
            fig.add_trace(go.Scatter(
                x=grp[x_col],
                y=grp[prop],
                mode="markers+lines" if connect else "markers",
                name=f"Bloc {block.upper()}",
                marker=dict(color=BLOCK_COLORS.get(block, "#aaa"), size=8,
                            line=dict(color="#102027", width=0.5)),
                line=dict(color=BLOCK_COLORS.get(block, "#aaa"), width=1, dash="dot") if connect else None,
                text=grp.apply(
                    lambda r: f"<b>{r['symbol']}</b> — {r.get(name_col, r['name'])}<br>Z = {int(r['atomic_number'])}",
                    axis=1,
                ),
                hovertemplate="%{text}<br>" + y_lbl + " = <b>%{y:.3g}</b><extra></extra>",
            ))

        fig.update_layout(
            plot_bgcolor="#102027",
            paper_bgcolor="#102027",
            xaxis=dict(title=x_title, color="#cfd8dc", gridcolor="#1a2d3a",
                       showgrid=True, zeroline=False),
            yaxis=dict(title=y_lbl, color="#cfd8dc", gridcolor="#1a2d3a",
                       showgrid=True, zeroline=False),
            legend=dict(font=dict(color="#cfd8dc", size=11),
                        bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)"),
            margin=dict(l=60, r=20, t=20, b=60),
            hoverlabel=dict(bgcolor="#263238", font_size=12, font_family="Inter"),
            font=dict(color="#cfd8dc", family="Inter"),
            hovermode="closest",
        )

        return fig, _prop_options(lang), VIEW_OPTIONS.get(lang, VIEW_OPTIONS["fr"])
