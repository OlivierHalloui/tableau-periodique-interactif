"""
solvation_tab.py — Onglet effets de solvant (PCM / COSMO / SMD).
Вкладка эффектов растворителя.
"""
from __future__ import annotations

import json
from pathlib import Path

from dash import html, dcc, Input, Output, State, callback, ctx

_SOLVENTS = json.loads(
    (Path(__file__).parent / "data" / "solvents.json").read_text(encoding="utf-8")
)

_MODELS = {
    "cpcm":    {"label_fr": "CPCM (ORCA)",      "label_ru": "ЦПКМ (ORCA)"},
    "pcm":     {"label_fr": "PCM (Gaussian)",    "label_ru": "ПКМ (Gaussian)"},
    "smd":     {"label_fr": "SMD (universel)",   "label_ru": "SMD (универсальный)"},
}


def _solvent_options(lang: str) -> list[dict]:
    lk = "label_ru" if lang == "ru" else "label_fr"
    return [{"value": k, "label": v[lk]} for k, v in _SOLVENTS.items()]


def create_solvation_layout() -> html.Div:
    opts = _solvent_options("fr")
    return html.Div(className="tab-content-pad", children=[
        html.H2("Effets de solvant implicite", id="solv-title"),
        html.P(
            "Sélectionnez un solvant pour obtenir les mots-clés PCM/CPCM/SMD à insérer "
            "dans vos fichiers d'entrée ORCA, Gaussian ou PySCF.",
            id="solv-subtitle",
        ),
        html.Div(className="trend-controls-row", children=[
            html.Div([
                html.Label("Solvant", id="solv-label"),
                dcc.Dropdown(
                    id="solv-select",
                    options=opts,
                    value="water",
                    clearable=False,
                    className="filter-dropdown",
                ),
            ], className="cost-field"),
            html.Div([
                html.Label("Modèle de solvatation", id="solv-model-label"),
                dcc.RadioItems(
                    id="solv-model",
                    options=[
                        {"label": "CPCM (ORCA)", "value": "cpcm"},
                        {"label": "PCM (Gaussian)", "value": "pcm"},
                        {"label": "SMD", "value": "smd"},
                    ],
                    value="cpcm",
                    labelStyle={"display": "inline-block", "marginRight": "14px"},
                ),
            ], className="cost-field"),
            html.Div(
                id="solv-custom-div",
                style={"display": "none"},
                children=[
                    html.Label("Constante diélectrique ε personnalisée"),
                    dcc.Input(id="solv-custom-eps", type="number", min=1.0, step=0.1,
                              placeholder="ex : 36.7", className="cost-input"),
                ],
            ),
        ]),
        html.Div(id="solv-result", style={"marginTop": "16px"}),
    ])


def register_callbacks(app=None):
    @callback(
        Output("solv-title",       "children"),
        Output("solv-subtitle",    "children"),
        Output("solv-label",       "children"),
        Output("solv-model-label", "children"),
        Output("solv-select",      "options"),
        Input("lang", "data"),
    )
    def _lang(lang):
        lang = lang or "fr"
        opts = _solvent_options(lang)
        if lang == "ru":
            return (
                "Эффекты неявного растворителя",
                "Выберите растворитель, чтобы получить ключевые слова PCM/CPCM/SMD для входных файлов.",
                "Растворитель", "Модель сольватации", opts,
            )
        return (
            "Effets de solvant implicite",
            "Sélectionnez un solvant pour obtenir les mots-clés PCM/CPCM/SMD.",
            "Solvant", "Modèle de solvatation", opts,
        )

    @callback(
        Output("solv-custom-div", "style"),
        Input("solv-select", "value"),
    )
    def _show_custom(solvent):
        if solvent == "custom":
            return {"display": "block"}
        return {"display": "none"}

    @callback(
        Output("solv-result", "children"),
        Input("solv-select",  "value"),
        Input("solv-model",   "value"),
        Input("solv-custom-eps", "value"),
        State("lang", "data"),
    )
    def _update(solvent_key, model, custom_eps, lang):
        lang = lang or "fr"
        if not solvent_key:
            return html.P("")

        sv = _SOLVENTS.get(solvent_key, {})
        lk = "label_ru" if lang == "ru" else "label_fr"

        eps = sv.get("epsilon")
        if solvent_key == "custom" and custom_eps is not None:
            eps = float(custom_eps)

        if solvent_key == "none":
            msg = ("Phase gazeuse sélectionnée — aucun mot-clé solvant à ajouter."
                   if lang == "fr" else "Газовая фаза — ключевые слова растворителя не добавляются.")
            return html.P(msg, style={"color": "#aaa"})

        def _kw_badge(label: str, kw: str | None) -> html.Div:
            return html.Div(style={"marginBottom": "12px"}, children=[
                html.Strong(label + " : "),
                html.Code(kw or ("N/A — non supporté" if lang == "fr" else "Н/П"),
                          style={"background": "#1e2a3a", "padding": "2px 8px",
                                 "borderRadius": "3px", "fontSize": "0.9em"}),
            ])

        # Select keyword according to model
        if model == "cpcm":
            orca_kw   = sv.get("orca_kw")
            gauss_kw  = f"SCRF=(CPCM,Solvent={solvent_key.capitalize()})" if solvent_key != "custom" else "SCRF=(CPCM,Eps={eps})"
            pyscf_kw  = sv.get("pyscf_kw")
        elif model == "smd":
            orca_kw   = f"SMD" if solvent_key != "custom" else "SMD"
            gauss_kw  = f"SCRF=(SMD,Solvent={solvent_key.capitalize()})" if solvent_key != "custom" else None
            pyscf_kw  = None
        else:  # pcm
            orca_kw   = sv.get("orca_kw", "").replace("CPCM", "PCM") if sv.get("orca_kw") else None
            gauss_kw  = sv.get("gaussian_kw")
            pyscf_kw  = sv.get("pyscf_kw")

        eps_str = f"{eps:.2f}" if eps is not None else "?"
        note_fr = (
            f"ℹ La constante diélectrique du solvant est ε = {eps_str}. "
            "Le solvant implicite modifie les énergies de ±1–15 kcal/mol. "
            "Vérifiez la convergence SCF en solution."
        )
        note_ru = (
            f"ℹ Диэлектрическая постоянная растворителя ε = {eps_str}. "
            "Неявный растворитель изменяет энергии на ±1–15 ккал/моль. "
            "Проверьте сходимость SCF в растворе."
        )
        note = note_ru if lang == "ru" else note_fr

        ecp_warn = None
        if solvent_key not in ("none",):
            ecp_warn = html.Div(className="orbital-disclaimer", style={"marginBottom": "12px"}, children=[
                html.Strong("Note : " if lang == "fr" else "Примечание: "),
                html.Span(
                    "Pour les propriétés magnétiques (RMN/RPE), utilisez un calcul tous-électrons "
                    "même en présence de solvant." if lang == "fr" else
                    "Для магнитных свойств (ЯМР/ЭПР) используйте расчёт всех электронов даже в растворе."
                ),
            ])

        return html.Div([
            html.H4(sv[lk] if lk in sv else solvent_key, style={"marginBottom": "12px"}),
            ecp_warn or html.Span(),
            _kw_badge("ORCA",    orca_kw),
            _kw_badge("Gaussian", gauss_kw),
            _kw_badge("PySCF",   pyscf_kw),
            html.P(note, style={"fontSize": "0.85em", "color": "#aaa", "marginTop": "12px"}),
        ])
