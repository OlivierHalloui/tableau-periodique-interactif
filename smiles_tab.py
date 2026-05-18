"""
smiles_tab.py — Onglet entrée SMILES + RDKit.
Вкладка ввода SMILES + RDKit.

RDKit est optionnel : si non installé, un message d'information est affiché.
"""
from __future__ import annotations

import base64
import io

from dash import html, dcc, Input, Output, State, callback, no_update
from data_loader import ELEMENTS_BY_SYM
from molecule_assistant import recommend_for_molecule

try:
    from rdkit import Chem
    from rdkit.Chem import Draw, rdMolDescriptors
    _RDKIT_OK = True
except ImportError:
    _RDKIT_OK = False


def _smiles_to_formula_and_img(smiles: str) -> tuple[str, str | None, str | None]:
    """
    Returns (formula, img_src_base64, error_msg).
    img_src_base64 : "data:image/png;base64,..." ou None
    """
    if not _RDKIT_OK:
        return "", None, "RDKit non installé — pip install rdkit"

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return "", None, f"SMILES invalide : {smiles!r}"

    # Formula
    formula = rdMolDescriptors.CalcMolFormula(mol)

    # Image (PNG → base64)
    img = Draw.MolToImage(mol, size=(300, 200), kekulize=True)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    img_b64 = base64.b64encode(buf.getvalue()).decode()
    img_src  = f"data:image/png;base64,{img_b64}"

    return formula, img_src, None


def create_smiles_layout() -> html.Div:
    return html.Div(className="tab-content-pad", children=[
        html.H2("Analyse SMILES", id="smiles-title"),
        html.P(
            "Entrez un SMILES pour extraire automatiquement la formule brute "
            "et obtenir les recommandations de calcul.",
            id="smiles-subtitle",
        ),

        html.Div(className="trend-controls-row", children=[
            html.Div([
                html.Label("SMILES", id="smiles-label"),
                dcc.Input(
                    id="smiles-input",
                    type="text",
                    placeholder="ex : O, [Fe](Cl)(Cl)Cl, CC(=O)O",
                    style={"width": "320px"},
                    className="cost-input",
                ),
            ], className="cost-field"),
            html.Div([
                html.Label("Propriété cible", id="smiles-prop-label"),
                dcc.Dropdown(
                    id="smiles-prop",
                    options=[
                        {"label": "Géométrie / optimisation", "value": "geometry"},
                        {"label": "Énergie / thermochimie",   "value": "energy"},
                        {"label": "États excités (TD-DFT)",   "value": "excitation"},
                        {"label": "RMN",                      "value": "nmr"},
                        {"label": "Propriétés magnétiques",   "value": "magnetism"},
                        {"label": "Dispersion",               "value": "dispersion"},
                    ],
                    value="geometry",
                    clearable=False,
                    className="filter-dropdown",
                    style={"minWidth": "220px"},
                ),
            ], className="cost-field"),
            html.Button("Analyser", id="smiles-btn", className="action-btn"),
        ]),

        html.Div(id="smiles-result", style={"marginTop": "16px"}),
    ])


def register_callbacks(app=None):
    @callback(
        Output("smiles-title",      "children"),
        Output("smiles-subtitle",   "children"),
        Output("smiles-label",      "children"),
        Output("smiles-prop-label", "children"),
        Output("smiles-prop",       "options"),
        Input("lang", "data"),
    )
    def _lang(lang):
        lang = lang or "fr"
        props_fr = [
            {"label": "Géométrie / optimisation", "value": "geometry"},
            {"label": "Énergie / thermochimie",   "value": "energy"},
            {"label": "États excités (TD-DFT)",   "value": "excitation"},
            {"label": "RMN",                      "value": "nmr"},
            {"label": "Propriétés magnétiques",   "value": "magnetism"},
            {"label": "Dispersion",               "value": "dispersion"},
        ]
        props_ru = [
            {"label": "Геометрия / оптимизация",  "value": "geometry"},
            {"label": "Энергия / термохимия",     "value": "energy"},
            {"label": "Возбуждённые состояния",   "value": "excitation"},
            {"label": "ЯМР",                      "value": "nmr"},
            {"label": "Магнитные свойства",       "value": "magnetism"},
            {"label": "Дисперсия",                "value": "dispersion"},
        ]
        if lang == "ru":
            return (
                "Анализ SMILES",
                "Введите SMILES для автоматического извлечения формулы и получения рекомендаций по расчёту.",
                "SMILES", "Целевое свойство", props_ru,
            )
        return (
            "Analyse SMILES",
            "Entrez un SMILES pour extraire la formule brute et obtenir les recommandations.",
            "SMILES", "Propriété cible", props_fr,
        )

    @callback(
        Output("smiles-result", "children"),
        Input("smiles-btn",  "n_clicks"),
        State("smiles-input", "value"),
        State("smiles-prop",  "value"),
        State("lang", "data"),
        prevent_initial_call=True,
    )
    def _analyse(n_clicks, smiles, prop_key, lang):
        lang = lang or "fr"

        if not _RDKIT_OK:
            install_msg = (
                "RDKit n'est pas installé dans cet environnement. "
                "Pour activer cette fonctionnalité : pip install rdkit"
                if lang == "fr" else
                "RDKit не установлен в этой среде. "
                "Для активации функции: pip install rdkit"
            )
            return html.Div([
                html.Div(className="orbital-disclaimer", children=[
                    html.Strong("⚠ RDKit non disponible"),
                    html.P(install_msg),
                    html.P(
                        "Astuce : utilisez l'onglet Tableau pour entrer directement une formule brute."
                        if lang == "fr" else
                        "Совет: используйте вкладку Таблица для ввода формулы напрямую."
                    ),
                ])
            ])

        if not smiles or not smiles.strip():
            return html.P(
                "Entrez un SMILES valide." if lang == "fr" else "Введите допустимый SMILES.",
                style={"color": "#aaa"},
            )

        formula, img_src, error = _smiles_to_formula_and_img(smiles.strip())
        if error:
            return html.P(f"⚠ {error}", style={"color": "#e57373"})

        # Get recommendations
        prop_key = prop_key or "geometry"
        rec = recommend_for_molecule(formula, prop_key, lang, ELEMENTS_BY_SYM)

        if rec.get("error"):
            img_div = html.Img(src=img_src, style={"maxWidth": "300px", "borderRadius": "6px"}) if img_src else html.Span()
            return html.Div([
                img_div,
                html.P(f"Formule extraite : {formula}", style={"marginTop": "8px"}),
                html.P(
                    f"⚠ Aucune recommandation disponible : {rec.get('error_msg', '')}",
                    style={"color": "#e57373"},
                ),
            ])

        lbl = "label_ru" if lang == "ru" else "label_fr"

        def _row(label: str, value) -> html.Tr:
            return html.Tr([html.Td(label, style={"fontWeight": "bold", "paddingRight": "12px"}),
                            html.Td(str(value) if value is not None else "—")])

        if lang == "ru":
            rows = [
                _row("Формула", formula),
                _row("Доминирующий элемент", f"{rec['dominant']} (Z={rec['dominant_z']})"),
                _row("Метод", rec["method"]),
                _row("Базис", rec["basis"]),
                _row("ЭКП", rec["ecp"] or "Нет"),
                _row("Заряд", rec.get("charge", 0)),
                _row("Мультиплетность", rec.get("mult", 1)),
            ]
        else:
            rows = [
                _row("Formule", formula),
                _row("Élément dominant", f"{rec['dominant']} (Z={rec['dominant_z']})"),
                _row("Méthode", rec["method"]),
                _row("Base", rec["basis"]),
                _row("ECP", rec["ecp"] or "Aucun"),
                _row("Charge", rec.get("charge", 0)),
                _row("Multiplicité", rec.get("mult", 1)),
            ]

        notes = rec.get("extra_notes", [])
        notes_div = html.Div([
            html.Div(n, style={"fontSize": "0.85em", "color": "#aaa", "marginTop": "4px"})
            for n in notes
        ]) if notes else html.Span()

        return html.Div(style={"display": "flex", "gap": "20px", "flexWrap": "wrap"}, children=[
            html.Div(style={"flex": "0 0 auto"}, children=[
                html.Img(src=img_src,
                         style={"maxWidth": "280px", "borderRadius": "6px",
                                "background": "#fff", "padding": "6px"})
                if img_src else html.Span(),
            ]),
            html.Div(style={"flex": "1"}, children=[
                html.Table(html.Tbody(rows), className="cost-table"),
                notes_div,
            ]),
        ])
