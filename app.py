# =============================================================================
# app.py — Point d'entrée multi-pages V1.5.
# app.py — Точка входа многостраничного приложения V1.5.
# =============================================================================

import dash
from dash import html, dcc, Input, Output, State, callback, ctx

from translations import LANG

app = dash.Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
)
server = app.server

app.layout = html.Div(
    className="app-container",
    children=[
        dcc.Store(id="lang", data="fr"),
        dcc.Location(id="url"),
        html.Header(
            className="hero",
            children=[
                html.Div(
                    className="hero-top",
                    children=[
                        html.H1("Tableau périodique interactif", id="app-title"),
                        html.Div(
                            className="lang-toggle",
                            children=[
                                html.Button("FR", id="btn-fr", className="lang-btn active", n_clicks=0),
                                html.Button("RU", id="btn-ru", className="lang-btn", n_clicks=0),
                            ],
                        ),
                    ],
                ),
                html.P(
                    "Explorez les 118 éléments chimiques avec leurs propriétés scientifiques et une interface responsive en français.",
                    id="app-subtitle",
                ),
            ],
        ),
        dash.page_container,
        html.Footer(
            className="footer",
            children=[
                html.P(id="footer-data",
                       children="Données scientifiques : IUPAC, CRC Handbook, NIST · Basis Set Exchange (basissetexchange.org)"),
                html.P(id="footer-credit",
                       className="footer-credit",
                       children="Développé par Saloua EL FAKIR — Master 1 Chimie Informatique"),
            ],
        ),
    ],
)


@callback(
    Output("lang", "data"),
    Input("btn-fr", "n_clicks"),
    Input("btn-ru", "n_clicks"),
    State("lang", "data"),
    prevent_initial_call=True,
)
def toggle_lang(n_fr, n_ru, current_lang):
    triggered = ctx.triggered_id
    if triggered == "btn-fr": return "fr"
    if triggered == "btn-ru": return "ru"
    return current_lang


@callback(
    Output("app-title", "children"),
    Output("app-subtitle", "children"),
    Output("footer-data", "children"),
    Output("footer-credit", "children"),
    Output("btn-fr", "className"),
    Output("btn-ru", "className"),
    Input("lang", "data"),
)
def update_global_language(lang):
    lang = lang or "fr"
    t = LANG[lang]
    active, inactive = "lang-btn active", "lang-btn"
    return (
        t["title"], t["subtitle"],
        t["footer_data"], t["footer_credit"],
        active if lang == "fr" else inactive,
        active if lang == "ru" else inactive,
    )


if __name__ == "__main__":
    app.run(debug=True)
