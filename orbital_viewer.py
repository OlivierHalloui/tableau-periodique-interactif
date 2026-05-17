"""
orbital_viewer.py — Visualisation 3D des orbitales atomiques hydrogénoïdes.
3D-визуализация водородоподобных атомных орбиталей.
3D visualization of hydrogen-like atomic orbitals.

Implémentation : calcul numérique ψ_nlm sur grille 3D, isosurface Plotly.
"""
from __future__ import annotations

import numpy as np
from dash import html, dcc, Input, Output, State, callback
import plotly.graph_objs as go

# ─── Catalogue des orbitales disponibles ────────────────────────────────────

ORBITALS: list[dict] = [
    {"label": "1s",     "n": 1, "l": 0, "m": 0,  "ml": "0"},
    {"label": "2s",     "n": 2, "l": 0, "m": 0,  "ml": "0"},
    {"label": "2p_z",   "n": 2, "l": 1, "m": 0,  "ml": "0"},
    {"label": "2p_x",   "n": 2, "l": 1, "m": 1,  "ml": "+1c"},
    {"label": "2p_y",   "n": 2, "l": 1, "m": 1,  "ml": "+1s"},
    {"label": "3s",     "n": 3, "l": 0, "m": 0,  "ml": "0"},
    {"label": "3p_z",   "n": 3, "l": 1, "m": 0,  "ml": "0"},
    {"label": "3d_z²",  "n": 3, "l": 2, "m": 0,  "ml": "0"},
    {"label": "3d_xz",  "n": 3, "l": 2, "m": 1,  "ml": "+1c"},
    {"label": "3d_x²y²","n": 3, "l": 2, "m": 2,  "ml": "+2c"},
    {"label": "4s",     "n": 4, "l": 0, "m": 0,  "ml": "0"},
    {"label": "4p_z",   "n": 4, "l": 1, "m": 0,  "ml": "0"},
    {"label": "4d_z²",  "n": 4, "l": 2, "m": 0,  "ml": "0"},
    {"label": "4f_z³",  "n": 4, "l": 3, "m": 0,  "ml": "0"},
]

# ─── Fonctions radiales ──────────────────────────────────────────────────────

def _R(n: int, l: int, r: np.ndarray, Z: float = 1.0) -> np.ndarray:
    """Radial wavefunction R_nl(r) for hydrogen-like atom (Z=1 unless specified)."""
    rho = 2.0 * Z * r / n
    if n == 1 and l == 0:
        return 2.0 * np.exp(-rho / 2)
    if n == 2 and l == 0:
        return (1.0 / (2.0 * np.sqrt(2))) * (2 - rho) * np.exp(-rho / 2)
    if n == 2 and l == 1:
        return (1.0 / (2.0 * np.sqrt(6))) * rho * np.exp(-rho / 2)
    if n == 3 and l == 0:
        return (2.0 / 81.0 / np.sqrt(3)) * (27 - 18 * rho + 2 * rho**2) * np.exp(-rho / 2)
    if n == 3 and l == 1:
        return (8.0 / 27.0 / np.sqrt(6)) * (6 - rho) * rho * np.exp(-rho / 2)
    if n == 3 and l == 2:
        return (4.0 / 81.0 / np.sqrt(30)) * rho**2 * np.exp(-rho / 2)
    if n == 4 and l == 0:
        return (1.0 / 96.0) * (24 - 36 * rho + 12 * rho**2 - rho**3) * np.exp(-rho / 2)
    if n == 4 and l == 1:
        return (1.0 / 32.0 / np.sqrt(15)) * (20 - 10 * rho + rho**2) * rho * np.exp(-rho / 2)
    if n == 4 and l == 2:
        return (1.0 / 96.0 / np.sqrt(5)) * (6 - rho) * rho**2 * np.exp(-rho / 2)
    if n == 4 and l == 3:
        return (1.0 / 96.0 / np.sqrt(35)) * rho**3 * np.exp(-rho / 2)
    return np.zeros_like(r)


# ─── Harmoniques sphériques réelles ─────────────────────────────────────────

def _Y_real(l: int, m: int, ml_type: str, theta: np.ndarray, phi: np.ndarray) -> np.ndarray:
    """Real spherical harmonics Y_lm for selected cases."""
    c, s = np.cos(theta), np.sin(theta)
    cp, sp = np.cos(phi), np.sin(phi)
    cp2, sp2 = np.cos(2 * phi), np.sin(2 * phi)

    if l == 0:
        return np.full_like(theta, 1.0 / np.sqrt(4 * np.pi))

    if l == 1:
        if m == 0:          # pz
            return np.sqrt(3 / (4 * np.pi)) * c
        if ml_type == "+1c": # px
            return np.sqrt(3 / (4 * np.pi)) * s * cp
        return              np.sqrt(3 / (4 * np.pi)) * s * sp  # py

    if l == 2:
        if m == 0:           # dz²
            return np.sqrt(5 / (16 * np.pi)) * (3 * c**2 - 1)
        if ml_type == "+1c": # dxz
            return np.sqrt(15 / (4 * np.pi)) * s * c * cp
        if ml_type == "+1s": # dyz
            return np.sqrt(15 / (4 * np.pi)) * s * c * sp
        if ml_type == "+2c": # dx²-y²
            return np.sqrt(15 / (16 * np.pi)) * s**2 * cp2
        return              np.sqrt(15 / (16 * np.pi)) * s**2 * sp2  # dxy

    if l == 3:
        if m == 0:            # fz³
            return np.sqrt(7 / (16 * np.pi)) * c * (5 * c**2 - 3)
        if ml_type == "+1c":  # fxz²
            return np.sqrt(21 / (32 * np.pi)) * s * cp * (5 * c**2 - 1)
        if ml_type == "+2c":  # fx(x²-3y²)
            return np.sqrt(105 / (4 * np.pi)) * s**2 * c * cp2
        return np.sqrt(35 / (32 * np.pi)) * s**3 * cp  # fxyz

    return np.zeros_like(theta)


# ─── Calcul de la grille ────────────────────────────────────────────────────

def compute_orbital(n: int, l: int, m: int, ml_type: str, grid: int = 35) -> tuple:
    """Return (x, y, z, psi_sq) on a regular grid."""
    extent = max(2 * n**2 + 2, 8)
    ax = np.linspace(-extent, extent, grid)
    X, Y, Z = np.meshgrid(ax, ax, ax, indexing="ij")

    r     = np.sqrt(X**2 + Y**2 + Z**2) + 1e-12
    theta = np.arccos(Z / r)
    phi   = np.arctan2(Y, X)

    R   = _R(n, l, r)
    Ylm = _Y_real(l, m, ml_type, theta, phi)
    psi = R * Ylm

    return X.ravel(), Y.ravel(), Z.ravel(), (psi**2).ravel()


# ─── Figure Plotly ──────────────────────────────────────────────────────────

def build_orbital_figure(orbital_label: str, lang: str = "fr") -> go.Figure:
    orb = next((o for o in ORBITALS if o["label"] == orbital_label), ORBITALS[0])
    n, l, m, ml = orb["n"], orb["l"], orb["m"], orb["ml"]

    x, y, z, vals = compute_orbital(n, l, m, ml)

    # Isosurface at 25 % of max density
    vmax    = float(vals.max()) if vals.max() > 0 else 1.0
    isomin  = vmax * 0.04
    isomax  = vmax * 0.7

    title_map = {
        "fr": f"Orbitale {orbital_label} — densité de probabilité |ψ|²",
        "ru": f"Орбиталь {orbital_label} — плотность вероятности |ψ|²",
        "en": f"Orbital {orbital_label} — probability density |ψ|²",
    }

    fig = go.Figure(go.Volume(
        x=x.tolist(), y=y.tolist(), z=z.tolist(),
        value=vals.tolist(),
        isomin=isomin,
        isomax=isomax,
        opacity=0.12,
        surface_count=5,
        colorscale=[
            [0.0,  "rgba(100,181,246,0.0)"],
            [0.25, "rgba(100,181,246,0.6)"],
            [0.5,  "rgba(129,199,132,0.8)"],
            [0.75, "rgba(255,183,77,0.9)"],
            [1.0,  "rgba(239,83,80,1.0)"],
        ],
        showscale=False,
        caps=dict(x_show=False, y_show=False, z_show=False),
    ))

    ax_style = dict(showbackground=False, color="#cfd8dc",
                    gridcolor="#1a2d3a", zerolinecolor="#1a2d3a",
                    tickfont=dict(color="#90a4ae", size=9))
    fig.update_layout(
        scene=dict(
            xaxis=dict(title="x (a₀)", **ax_style),
            yaxis=dict(title="y (a₀)", **ax_style),
            zaxis=dict(title="z (a₀)", **ax_style),
            bgcolor="#102027",
        ),
        paper_bgcolor="#102027",
        margin=dict(l=0, r=0, t=30, b=0),
        title=dict(text=title_map.get(lang, title_map["en"]),
                   font=dict(color="#cfd8dc", size=13), x=0.5),
        font=dict(color="#cfd8dc", family="Inter"),
    )
    return fig


# ─── Layout + callbacks ──────────────────────────────────────────────────────

def create_orbital_layout() -> html.Div:
    orb_options = [{"label": o["label"], "value": o["label"]} for o in ORBITALS]
    return html.Div(className="tab-content-pad", children=[
        html.Div(className="trend-controls-row", children=[
            dcc.Dropdown(
                id="orbital-select",
                options=orb_options,
                value="2p_z",
                clearable=False,
                className="filter-dropdown",
            ),
            html.Div(className="orbital-info-box", id="orbital-info-text",
                     children=[]),
        ]),
        dcc.Graph(
            id="orbital-3d-chart",
            className="orbital-chart",
            config={"displayModeBar": True,
                    "toImageButtonOptions": {"format": "png", "filename": "orbital"}},
        ),
    ])


def register_callbacks() -> None:

    @callback(
        Output("orbital-3d-chart", "figure"),
        Output("orbital-info-text", "children"),
        Input("orbital-select", "value"),
        State("lang", "data"),
    )
    def update_orbital(orbital_label: str | None, lang: str | None) -> tuple:
        lang = lang or "fr"
        label = orbital_label or "2p_z"
        orb   = next((o for o in ORBITALS if o["label"] == label), ORBITALS[0])

        fig   = build_orbital_figure(label, lang)

        n, l, m = orb["n"], orb["l"], orb["m"]
        info_map = {
            "fr": f"n = {n}  ·  ℓ = {l}  ·  mℓ = {m}  |  Nœuds radiaux : {n-l-1}  ·  Nœuds angulaires : {l}",
            "ru": f"n = {n}  ·  ℓ = {l}  ·  mℓ = {m}  |  Радиальных узлов: {n-l-1}  ·  Угловых узлов: {l}",
            "en": f"n = {n}  ·  ℓ = {l}  ·  mℓ = {m}  |  Radial nodes: {n-l-1}  ·  Angular nodes: {l}",
        }
        return fig, html.Span(info_map.get(lang, info_map["en"]), className="orbital-info-span")
