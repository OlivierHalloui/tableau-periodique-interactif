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
                        html.H1("СПЕКТР", id="app-title"),
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
                    "Système Périodique des Éléments pour les Calculs Quantico-chimiques Théoriques et les Recommandations",
                    id="app-subtitle",
                ),
            ],
        ),

        # ── Navigation ───────────────────────────────────────────────────────
        html.Nav(
            className="main-tabs-bar",
            children=[
                dcc.Link("Tableau",       href="/",              id="nav-tableau",    className="main-tab"),
                dcc.Link("Tendances",     href="/tendances",     id="nav-tendances",  className="main-tab"),
                dcc.Link("Comparateur",   href="/comparateur",   id="nav-comp",       className="main-tab"),
                dcc.Link("Orbitales 3D",  href="/orbitales",     id="nav-orb",        className="main-tab"),
                dcc.Link("Coût CPU/RAM",  href="/cost",          id="nav-cost",       className="main-tab"),
                dcc.Link("HPC Script",    href="/hpc",           id="nav-hpc",        className="main-tab"),
                dcc.Link("Solvant",       href="/solvation",     id="nav-solv",       className="main-tab"),
                dcc.Link("Champ ligand",  href="/ligand-field",  id="nav-lf",         className="main-tab"),
                dcc.Link("Benchmark",     href="/benchmark",     id="nav-bm",         className="main-tab"),
                dcc.Link("Parser sortie", href="/output-parser", id="nav-op",         className="main-tab"),
                dcc.Link("DFT Map",       href="/dft-map",       id="nav-dft",        className="main-tab"),
                dcc.Link("SMILES",        href="/smiles",        id="nav-smiles",     className="main-tab"),
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
    Output("app-title",    "children"),
    Output("app-subtitle", "children"),
    Output("footer-data",  "children"),
    Output("footer-credit","children"),
    Output("btn-fr",  "className"),
    Output("btn-ru",  "className"),
    Output("nav-tableau",  "children"),
    Output("nav-tendances","children"),
    Output("nav-comp",     "children"),
    Output("nav-orb",      "children"),
    Output("nav-cost",     "children"),
    Output("nav-hpc",      "children"),
    Output("nav-solv",     "children"),
    Output("nav-lf",       "children"),
    Output("nav-bm",       "children"),
    Output("nav-op",       "children"),
    Output("nav-dft",      "children"),
    Output("nav-smiles",   "children"),
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
        t["nav_cost"],
        t["nav_hpc"],
        t["nav_solv"],
        t["nav_lf"],
        t["nav_bm"],
        t["nav_op"],
        t["nav_dft"],
        t["nav_smiles"],
    )


@callback(
    Output("nav-tableau",  "className"),
    Output("nav-tendances","className"),
    Output("nav-comp",     "className"),
    Output("nav-orb",      "className"),
    Output("nav-cost",     "className"),
    Output("nav-hpc",      "className"),
    Output("nav-solv",     "className"),
    Output("nav-lf",       "className"),
    Output("nav-bm",       "className"),
    Output("nav-op",       "className"),
    Output("nav-dft",      "className"),
    Output("nav-smiles",   "className"),
    Input("url", "pathname"),
)
def update_active_nav(pathname):
    base = "main-tab"
    sel  = "main-tab main-tab--selected"
    return (
        sel if pathname in ("/", "")         else base,
        sel if pathname == "/tendances"       else base,
        sel if pathname == "/comparateur"     else base,
        sel if pathname == "/orbitales"       else base,
        sel if pathname == "/cost"            else base,
        sel if pathname == "/hpc"             else base,
        sel if pathname == "/solvation"       else base,
        sel if pathname == "/ligand-field"    else base,
        sel if pathname == "/benchmark"       else base,
        sel if pathname == "/output-parser"   else base,
        sel if pathname == "/dft-map"         else base,
        sel if pathname == "/smiles"          else base,
    )


if __name__ == "__main__":
    app.run(debug=True)
