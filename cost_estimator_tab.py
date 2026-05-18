"""
cost_estimator_tab.py — Onglet estimateur de coût CPU/RAM.
Вкладка оценки стоимости CPU/ОЗУ.
"""
from __future__ import annotations

import plotly.graph_objs as go
from dash import html, dcc, Input, Output, State, callback
from translations import LANG
from cost_estimator import estimate_cost, list_methods, list_basis, list_element_types


def create_cost_layout() -> html.Div:
    methods  = list_methods()
    bases    = list_basis()
    eltypes  = list_element_types()

    return html.Div(className="tab-content-pad", children=[
        html.H2("Estimateur de coût de calcul", id="cost-title"),
        html.P(
            "Estimation du temps CPU et de la RAM pour un calcul de chimie quantique "
            "en fonction du système, de la méthode et de la base.",
            id="cost-subtitle",
        ),
        html.Div(className="trend-controls-row", children=[
            html.Div([
                html.Label("Nombre d'atomes", id="cost-natoms-label"),
                dcc.Input(id="cost-natoms", type="number", value=10, min=1, max=500,
                          step=1, className="cost-input"),
            ], className="cost-field"),
            html.Div([
                html.Label("Méthode de calcul", id="cost-method-label"),
                dcc.Dropdown(
                    id="cost-method",
                    options=[{"value": m["value"], "label": m["label_fr"]} for m in methods],
                    value="dft_hybrid",
                    clearable=False,
                    className="filter-dropdown",
                ),
            ], className="cost-field"),
            html.Div([
                html.Label("Qualité de la base", id="cost-basis-label"),
                dcc.Dropdown(
                    id="cost-basis",
                    options=[{"value": b["value"], "label": b["label_fr"]} for b in bases],
                    value="tz",
                    clearable=False,
                    className="filter-dropdown",
                ),
            ], className="cost-field"),
            html.Div([
                html.Label("Type d'éléments", id="cost-eltype-label"),
                dcc.Dropdown(
                    id="cost-eltype",
                    options=[{"value": e["value"], "label": e["label_fr"]} for e in eltypes],
                    value="light",
                    clearable=False,
                    className="filter-dropdown",
                ),
            ], className="cost-field"),
            html.Button("Estimer", id="cost-btn", className="action-btn"),
        ]),
        html.Div(id="cost-result"),
    ])


def register_callbacks(app=None):
    @callback(
        Output("cost-title",    "children"),
        Output("cost-subtitle", "children"),
        Output("cost-natoms-label",  "children"),
        Output("cost-method-label",  "children"),
        Output("cost-basis-label",   "children"),
        Output("cost-eltype-label",  "children"),
        Output("cost-method", "options"),
        Output("cost-basis",  "options"),
        Output("cost-eltype", "options"),
        Input("lang", "data"),
    )
    def _update_lang(lang):
        lang = lang or "fr"
        methods  = list_methods()
        bases    = list_basis()
        eltypes  = list_element_types()
        lk       = "label_ru" if lang == "ru" else "label_fr"
        if lang == "ru":
            return (
                "Оценка стоимости вычислений",
                "Оценка времени CPU и ОЗУ для квантово-химического расчёта.",
                "Число атомов", "Метод расчёта", "Качество базиса", "Тип элементов",
                [{"value": m["value"], "label": m[lk]} for m in methods],
                [{"value": b["value"], "label": b[lk]} for b in bases],
                [{"value": e["value"], "label": e[lk]} for e in eltypes],
            )
        return (
            "Estimateur de coût de calcul",
            "Estimation du temps CPU et de la RAM pour un calcul de chimie quantique.",
            "Nombre d'atomes", "Méthode de calcul", "Qualité de la base", "Type d'éléments",
            [{"value": m["value"], "label": m[lk]} for m in methods],
            [{"value": b["value"], "label": b[lk]} for b in bases],
            [{"value": e["value"], "label": e[lk]} for e in eltypes],
        )

    @callback(
        Output("cost-result", "children"),
        Input("cost-btn", "n_clicks"),
        State("cost-natoms",  "value"),
        State("cost-method",  "value"),
        State("cost-basis",   "value"),
        State("cost-eltype",  "value"),
        State("lang", "data"),
        prevent_initial_call=True,
    )
    def _compute(n_clicks, n_atoms, method_key, basis_key, element_type, lang):
        lang = lang or "fr"
        if not n_atoms or not method_key or not basis_key:
            return html.P("Remplissez tous les champs." if lang == "fr"
                          else "Заполните все поля.")
        try:
            res = estimate_cost(int(n_atoms), method_key, basis_key, element_type or "light")
        except ValueError as e:
            return html.P(str(e), style={"color": "red"})

        if res.get("warning"):
            note = res["note_fr"] if lang == "fr" else res["note_ru"]
            return html.Div([
                html.Div(className="orbital-disclaimer", children=[
                    html.Strong("⚠ CASSCF/NEVPT2 — croissance factorielle"),
                    html.P(note),
                    html.P("Contactez un expert pour dimensionner l'espace actif et les ressources." if lang == "fr"
                           else "Обратитесь к эксперту для выбора активного пространства и ресурсов."),
                ])
            ])

        lk_plat = "label_fr" if lang == "fr" else "label_ru"
        plats   = res["platforms"]
        rows    = []
        for pk, pv in plats.items():
            feasible = pv["feasible"]
            color    = "#2ecc71" if feasible else "#e74c3c"
            t_str    = f"{pv['time_h']:.1f} h" if pv["time_h"] < 24 else f"{pv['time_days']:.1f} j"
            rows.append(html.Tr([
                html.Td(pv[lk_plat]),
                html.Td(f"{pv['cores']} cœurs"),
                html.Td(t_str, style={"color": color, "fontWeight": "bold"}),
                html.Td(f"{pv['ram_gb']:.0f} Go", style={"color": color}),
            ]))

        header_fr = ["Plateforme", "Cœurs", "Temps estimé", "RAM estimée"]
        header_ru = ["Платформа",  "Ядра",  "Время (оценка)", "ОЗУ (оценка)"]
        headers   = header_ru if lang == "ru" else header_fr

        nbf_note = (f"N_bf ≈ {res['n_bf']} fonctions de base"
                    if lang == "fr" else f"N_bf ≈ {res['n_bf']} базисных функций")

        fig = go.Figure(go.Bar(
            x=[plats[pk]["time_h"] for pk in plats],
            y=[plats[pk][lk_plat] for pk in plats],
            orientation="h",
            marker_color=["#2ecc71" if plats[pk]["feasible"] else "#e74c3c" for pk in plats],
            text=[f"{plats[pk]['time_h']:.1f} h" for pk in plats],
            textposition="outside",
        ))
        fig.update_layout(
            margin={"t": 10, "b": 10, "l": 10, "r": 10},
            height=180,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="Heures (log)" if lang == "fr" else "Часы (log)",
            xaxis_type="log",
            font_color="#e0e0e0",
        )

        return html.Div([
            html.P(nbf_note, style={"fontStyle": "italic", "fontSize": "0.85em"}),
            html.Table(
                [html.Thead(html.Tr([html.Th(h) for h in headers])),
                 html.Tbody(rows)],
                className="cost-table",
            ),
            dcc.Graph(figure=fig, config={"displayModeBar": False}),
            html.P(
                "⚠ Estimation indicative basée sur la loi de scaling théorique. "
                "Les temps réels varient selon l'implémentation et le matériel." if lang == "fr"
                else "⚠ Индикативная оценка на основе теоретического закона масштабирования.",
                style={"fontSize": "0.8em", "color": "#aaa", "marginTop": "8px"},
            ),
        ])
