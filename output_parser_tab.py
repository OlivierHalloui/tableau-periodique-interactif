"""
output_parser_tab.py — Onglet parseur de sorties ORCA / Gaussian.
Вкладка парсера выходных файлов ORCA / Gaussian.
"""
from __future__ import annotations

from dash import html, dcc, Input, Output, State, callback
from output_parser import parse, detect_software


def create_output_parser_layout() -> html.Div:
    return html.Div(className="tab-content-pad", children=[
        html.H2("Parseur de sorties ORCA / Gaussian", id="op-title"),
        html.P(
            "Collez le contenu d'un fichier de sortie ORCA ou Gaussian pour extraire "
            "automatiquement les grandeurs clés : énergie, convergence, T₁, gap HOMO-LUMO…",
            id="op-subtitle",
        ),
        dcc.Textarea(
            id="op-text",
            placeholder="Collez ici votre sortie ORCA ou Gaussian…",
            style={
                "width": "100%", "height": "200px", "fontFamily": "monospace",
                "fontSize": "0.80em", "background": "#1a1a2e", "color": "#e0e0e0",
                "border": "1px solid #444", "borderRadius": "4px", "padding": "10px",
                "resize": "vertical",
            },
        ),
        html.Button("Analyser", id="op-btn", className="action-btn",
                    style={"marginTop": "10px"}),
        html.Div(id="op-result", style={"marginTop": "16px"}),
    ])


def register_callbacks(app=None):
    @callback(
        Output("op-title",    "children"),
        Output("op-subtitle", "children"),
        Output("op-text",     "placeholder"),
        Input("lang", "data"),
    )
    def _lang(lang):
        lang = lang or "fr"
        if lang == "ru":
            return (
                "Парсер выходных файлов ORCA / Gaussian",
                "Вставьте содержимое выходного файла ORCA или Gaussian для автоматического извлечения ключевых величин.",
                "Вставьте здесь вывод ORCA или Gaussian…",
            )
        return (
            "Parseur de sorties ORCA / Gaussian",
            "Collez le contenu d'un fichier de sortie ORCA ou Gaussian pour extraire les grandeurs clés.",
            "Collez ici votre sortie ORCA ou Gaussian…",
        )

    @callback(
        Output("op-result", "children"),
        Input("op-btn", "n_clicks"),
        State("op-text", "value"),
        State("lang", "data"),
        prevent_initial_call=True,
    )
    def _parse(n_clicks, text, lang):
        lang = lang or "fr"
        if not text or not text.strip():
            return html.P(
                "Collez une sortie de calcul avant d'analyser." if lang == "fr"
                else "Вставьте выходной файл перед анализом.",
                style={"color": "#aaa"},
            )

        result = parse(text)
        sw = result.get("software", "unknown")

        if sw == "unknown":
            return html.Div([
                html.P(
                    "⚠ Logiciel non reconnu. Assurez-vous de coller une sortie ORCA ou Gaussian complète."
                    if lang == "fr" else
                    "⚠ Программа не распознана. Убедитесь, что вы вставляете полный вывод ORCA или Gaussian.",
                    style={"color": "#e57373"},
                )
            ])

        sw_label = {"orca": "ORCA", "gaussian": "Gaussian"}.get(sw, sw)

        def _card(icon: str, label: str, value, unit: str = "", warn: bool = False) -> html.Div:
            color = "#e57373" if warn else "#e0e0e0"
            val_str = str(value) if value is not None else ("N/A" if lang == "fr" else "Н/П")
            return html.Div(style={
                "background": "#1e2a3a", "borderRadius": "6px",
                "padding": "10px 14px", "minWidth": "160px", "flex": "1",
            }, children=[
                html.Div(f"{icon} {label}", style={"fontSize": "0.78em", "color": "#aaa"}),
                html.Div(f"{val_str} {unit}", style={"fontWeight": "bold", "fontSize": "1.05em",
                                                      "color": color}),
            ])

        # Build cards
        e = result.get("final_energy")
        t1 = result.get("t1_diagnostic")
        gap = result.get("homo_lumo_gap_ev")
        scf = result.get("scf_converged")
        freqs = result.get("frequencies", [])
        n_imag = result.get("n_imaginary", 0)

        t1_warn = (t1 is not None and t1 > 0.02)

        lbl_energy = "Énergie finale" if lang == "fr" else "Итоговая энергия"
        lbl_t1     = "T₁ diagnostic"
        lbl_gap    = "Gap HOMO-LUMO"
        lbl_scf    = "Convergence SCF"
        lbl_freq   = "Fréquences imag." if lang == "fr" else "Мним. частоты"
        scf_val    = ("✓ Oui" if scf else "✗ Non") if lang == "fr" else ("✓ Да" if scf else "✗ Нет")

        cards = html.Div(style={"display": "flex", "gap": "10px", "flexWrap": "wrap",
                                 "marginBottom": "14px"}, children=[
            _card("⚡", lbl_energy, f"{e:.6f}" if e is not None else None, "Eₕ"),
            _card("🔬", lbl_t1, f"{t1:.3f}" if t1 is not None else None, warn=t1_warn),
            _card("↕", lbl_gap, f"{gap:.2f}" if gap is not None else None, "eV"),
            _card("🔄", lbl_scf, scf_val, warn=not scf if scf is not None else False),
            _card("〰", lbl_freq, n_imag, warn=n_imag > 0),
        ])

        # Warnings
        warnings = result.get("warnings", [])
        warn_divs = []
        for w in warnings:
            warn_divs.append(
                html.Div(w, className="orbital-disclaimer",
                         style={"marginBottom": "6px", "fontSize": "0.88em"})
            )

        # Mulliken charges
        charges = result.get("mulliken_charges", [])
        charge_section = html.Span()
        if charges:
            lbl_q = "Charges de Mulliken (5 premiers atomes)" if lang == "fr" else "Заряды Малликена (5 первых атомов)"
            charge_section = html.Div([
                html.Strong(lbl_q + " : "),
                html.Code(", ".join(f"{q:+.3f}" for q in charges),
                          style={"background": "#1e2a3a", "padding": "2px 8px", "borderRadius": "3px"}),
            ], style={"marginTop": "10px"})

        # Frequencies list
        freq_section = html.Span()
        if freqs:
            lbl_f = "Premières fréquences (cm⁻¹)" if lang == "fr" else "Первые частоты (см⁻¹)"
            freq_section = html.Div([
                html.Strong(lbl_f + " : "),
                html.Code(", ".join(f"{f:.1f}" for f in freqs),
                          style={"background": "#1e2a3a", "padding": "2px 8px", "borderRadius": "3px",
                                 "fontSize": "0.85em"}),
            ], style={"marginTop": "10px"})

        header_label = f"Analyse — {sw_label}"

        return html.Div([
            html.H4(header_label, style={"marginBottom": "12px"}),
            cards,
            *warn_divs,
            charge_section,
            freq_section,
        ])
