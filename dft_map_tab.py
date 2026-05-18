"""
dft_map_tab.py — Onglet carte interactive des fonctionnelles DFT (Jacob's Ladder).
Вкладка интерактивной карты функционалов DFT (лестница Якоба).
"""
from __future__ import annotations

import json
from pathlib import Path

import plotly.graph_objs as go
from dash import html, dcc, Input, Output, callback

_FUNCTIONALS = json.loads(
    (Path(__file__).parent / "data" / "dft_functionals.json").read_text(encoding="utf-8")
)

_RUNG_LABELS_FR = {
    1: "Rung 1 — LDA",
    2: "Rung 2 — GGA",
    3: "Rung 3 — méta-GGA",
    4: "Rung 4 — hybride / méta-hybride / RSH",
    5: "Rung 5 — double-hybride / WFT",
}
_RUNG_LABELS_RU = {
    1: "Ступень 1 — ЛДП",
    2: "Ступень 2 — ОПГ",
    3: "Ступень 3 — мета-ОПГ",
    4: "Ступень 4 — гибридный / мета-гибридный / РСО",
    5: "Ступень 5 — двойной гибридный / ВФТ",
}
_RUNG_COLORS = {1: "#e74c3c", 2: "#e67e22", 3: "#f1c40f", 4: "#2ecc71", 5: "#9b59b6"}


def _make_figure(funcs: list[dict], lang: str) -> go.Figure:
    rung_labels = _RUNG_LABELS_RU if lang == "ru" else _RUNG_LABELS_FR
    note_key    = "note_ru" if lang == "ru" else "note_fr"

    fig = go.Figure()

    for rung in sorted(_RUNG_COLORS):
        subset = [f for f in funcs if f["rung"] == rung]
        if not subset:
            continue
        fig.add_trace(go.Scatter(
            x=[f["cost"] for f in subset],
            y=[f["mad_gmtkn55"] for f in subset],
            mode="markers+text",
            name=rung_labels.get(rung, f"Rung {rung}"),
            marker=dict(
                size=[8 + f.get("popularity", 3) * 3 for f in subset],
                color=_RUNG_COLORS[rung],
                line=dict(width=1.5, color="#111"),
                symbol=["diamond" if f.get("double_hybrid") else
                        "star" if f.get("range_sep") else "circle"
                        for f in subset],
            ),
            text=[f["name"] for f in subset],
            textposition="top center",
            textfont=dict(size=10, color="#e0e0e0"),
            hovertemplate=(
                "<b>%{text}</b><br>"
                + ("Rung: " if lang == "fr" else "Ступень: ")
                + str(rung) + "<br>"
                + ("MAD GMTKN55: " if lang == "fr" else "СПО GMTKN55: ")
                + "%{y:.2f} kcal/mol<br>"
                + ("Coût relatif: " if lang == "fr" else "Относит. стоимость: ")
                + "%{x:.1f}×"
                + "<extra></extra>"
            ),
        ))

    xaxis_title = ("Coût relatif (DFT GGA = 1)" if lang == "fr"
                   else "Относительная стоимость (ОПГ = 1)")
    yaxis_title = ("MAD GMTKN55 (kcal/mol)\n← Plus petit = meilleur" if lang == "fr"
                   else "СПО GMTKN55 (ккал/моль)\n← Меньше = лучше")

    fig.update_layout(
        height=500,
        margin={"t": 30, "b": 60, "l": 70, "r": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(18,24,38,1)",
        font_color="#e0e0e0",
        xaxis=dict(title=xaxis_title, gridcolor="#2a2a4a", type="log",
                   tickformat=".1f"),
        yaxis=dict(title=yaxis_title, gridcolor="#2a2a4a", autorange="reversed"),
        legend=dict(title="Jacob's Ladder" if lang == "fr" else "Лестница Якоба",
                    bgcolor="rgba(0,0,0,0)"),
        hovermode="closest",
    )

    # Horizontal band annotations for rungs
    rung_y_bounds = [(5.5, 8.0), (3.5, 5.5), (2.8, 3.5), (1.0, 2.8), (0.0, 1.0)]
    for rung, (y_lo, y_hi) in zip(range(1, 6), rung_y_bounds):
        fig.add_hrect(y0=y_lo, y1=y_hi,
                      fillcolor=_RUNG_COLORS[rung],
                      opacity=0.05, layer="below", line_width=0)

    return fig


def create_dft_map_layout() -> html.Div:
    all_rungs = sorted({f["rung"] for f in _FUNCTIONALS})
    return html.Div(className="tab-content-pad", children=[
        html.H2("Carte interactive des fonctionnelles DFT", id="dft-title"),
        html.P(
            "Positionnement des fonctionnelles selon la loi de Jacob (Perdew) : "
            "coût relatif (axe X) vs précision GMTKN55 (axe Y). "
            "Taille des points ∝ popularité. ◆ = double-hybride, ★ = séparation de portée.",
            id="dft-subtitle",
        ),
        html.Div(className="trend-controls-row", children=[
            html.Div([
                html.Label("Rungs (niveaux d'approximation)", id="dft-rung-label"),
                dcc.Checklist(
                    id="dft-rungs",
                    options=[{"label": _RUNG_LABELS_FR[r], "value": r} for r in all_rungs],
                    value=list(all_rungs),
                    labelStyle={"display": "block", "marginBottom": "4px"},
                ),
            ], className="cost-field", style={"minWidth": "280px"}),
            html.Div([
                html.Label("Filtres", id="dft-filter-label"),
                dcc.Checklist(
                    id="dft-filters",
                    options=[
                        {"label": "Avec correction de dispersion (D3/D4)", "value": "disp"},
                        {"label": "Séparation de portée (RSH, ωB97X…)", "value": "rsh"},
                        {"label": "Double-hybride uniquement", "value": "dh"},
                    ],
                    value=[],
                    labelStyle={"display": "block", "marginBottom": "4px"},
                ),
            ], className="cost-field"),
        ]),
        dcc.Graph(id="dft-map-graph", config={"displayModeBar": True}),
        html.Div(id="dft-legend-note"),
    ])


def register_callbacks(app=None):
    @callback(
        Output("dft-title",       "children"),
        Output("dft-subtitle",    "children"),
        Output("dft-rung-label",  "children"),
        Output("dft-filter-label","children"),
        Output("dft-rungs",       "options"),
        Output("dft-filters",     "options"),
        Input("lang", "data"),
    )
    def _lang(lang):
        lang = lang or "fr"
        all_rungs = sorted({f["rung"] for f in _FUNCTIONALS})
        rl = _RUNG_LABELS_RU if lang == "ru" else _RUNG_LABELS_FR
        if lang == "ru":
            return (
                "Интерактивная карта функционалов DFT",
                "Расположение функционалов по лестнице Якоба: стоимость (ось X) vs точность GMTKN55 (ось Y).",
                "Ступени (уровни приближения)", "Фильтры",
                [{"label": rl[r], "value": r} for r in all_rungs],
                [
                    {"label": "С дисперсионной поправкой (D3/D4)", "value": "disp"},
                    {"label": "Разделение диапазона (РСО)", "value": "rsh"},
                    {"label": "Только двойные гибридные", "value": "dh"},
                ],
            )
        return (
            "Carte interactive des fonctionnelles DFT",
            "Positionnement selon la loi de Jacob : coût (axe X) vs précision GMTKN55 (axe Y).",
            "Rungs (niveaux d'approximation)", "Filtres",
            [{"label": rl[r], "value": r} for r in all_rungs],
            [
                {"label": "Avec correction de dispersion (D3/D4)", "value": "disp"},
                {"label": "Séparation de portée (RSH)", "value": "rsh"},
                {"label": "Double-hybride uniquement", "value": "dh"},
            ],
        )

    @callback(
        Output("dft-map-graph",   "figure"),
        Output("dft-legend-note", "children"),
        Input("dft-rungs",   "value"),
        Input("dft-filters", "value"),
        Input("lang", "data"),
    )
    def _update(rungs, filters, lang):
        lang    = lang    or "fr"
        rungs   = rungs   or []
        filters = filters or []

        funcs = [f for f in _FUNCTIONALS if f["rung"] in rungs]

        if "disp" in filters:
            funcs = [f for f in funcs if f.get("dispersion")]
        if "rsh" in filters:
            funcs = [f for f in funcs if f.get("range_sep")]
        if "dh" in filters:
            funcs = [f for f in funcs if f.get("double_hybrid")]

        fig = _make_figure(funcs, lang)

        note = html.P(
            "Source des données GMTKN55 : Goerigk et al., PCCP, 2017 (DOI: 10.1039/c7cp04913g). "
            "Les valeurs de coût sont approximatives et dépendent du système et de l'implémentation."
            if lang == "fr" else
            "Данные GMTKN55: Goerigk et al., PCCP, 2017 (DOI: 10.1039/c7cp04913g). "
            "Значения стоимости приблизительны и зависят от системы и реализации.",
            style={"fontSize": "0.78em", "color": "#aaa", "marginTop": "8px"},
        )
        return fig, note
