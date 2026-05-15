# =============================================================================
# app.py — Point d'entrée multi-pages.
# app.py — Точка входа многостраничного приложения.
# =============================================================================

import dash
from dash import html, dcc, Input, Output, State, callback, ctx
from translations import LANG

# ─── App ─────────────────────────────────────────────────────────────────────

app = dash.Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
)
server = app.server

# Register REST API routes
from api import register_api_routes
from data_loader import ELEMENTS_BY_Z
register_api_routes(server, ELEMENTS_BY_Z)

# ─── Layout ──────────────────────────────────────────────────────────────────

app.layout = html.Div(
    className="app-container",
    children=[
        dcc.Store(id="lang", data="fr"),
        dcc.Store(id="selected-element-z", data=None),
        dcc.Store(id="selected-element-block", data=None),
        dcc.Store(id="last-recommendation", data=None),
        dcc.Location(id="url"),

        # ── Header ──────────────────────────────────────────────────────────
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
                    "Propriétés atomiques, recommandations de méthodes de calcul (ECP, bases, fonctionnelles DFT), génération de fichiers d'entrée ORCA/Gaussian/PySCF, visualisation 3D des orbitales et comparateur d'éléments.",
                    id="app-subtitle",
                ),
            ],
        ),

        # ── Navigation ───────────────────────────────────────────────────────
        html.Nav(
            className="main-tabs-bar",
            children=[
                dcc.Link("Tableau",       href="/",            id="nav-tableau",  className="main-tab"),
                dcc.Link("Tendances",     href="/tendances",   id="nav-tendances", className="main-tab"),
                dcc.Link("Comparateur",   href="/comparateur", id="nav-comp",      className="main-tab"),
                dcc.Link("Orbitales 3D",  href="/orbitales",   id="nav-orb",       className="main-tab"),
            ],
        ),

        # ── Page content ─────────────────────────────────────────────────────
        dash.page_container,

        # ── Footer ───────────────────────────────────────────────────────────
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


# ─── Global callbacks ────────────────────────────────────────────────────────

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
    Output("nav-tableau", "children"),
    Output("nav-tendances", "children"),
    Output("nav-comp", "children"),
    Output("nav-orb", "children"),
    Input("lang", "data"),
)
def update_global_language(lang):
    lang = lang or "fr"
    lk   = lang if lang in ("fr", "ru") else "fr"
    t    = LANG[lang]
    active   = "lang-btn active"
    inactive = "lang-btn"
    return (
        t["title"],
        t["subtitle"],
        t["footer_data"],
        t["footer_credit"],
        active if lk == "fr" else inactive,
        active if lk == "ru" else inactive,
        t["nav_table"],
        t["nav_trends"],
        t["nav_comp"],
        t["nav_orb"],
    )


@callback(
    Output("nav-tableau",  "className"),
    Output("nav-tendances", "className"),
    Output("nav-comp",     "className"),
    Output("nav-orb",      "className"),
    Input("url", "pathname"),
)
def update_active_nav(pathname):
    base = "main-tab"
    sel  = "main-tab main-tab--selected"
    return (
        sel  if pathname in ("/", "")    else base,
        sel  if pathname == "/tendances"  else base,
        sel  if pathname == "/comparateur" else base,
        sel  if pathname == "/orbitales"  else base,
    )


if __name__ == "__main__":
    app.run(debug=True)
