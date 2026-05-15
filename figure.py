"""
figure.py — Construction de la figure Plotly du tableau périodique.
Построение фигуры Plotly для таблицы Менделеева.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objs as go

from translations import LANG


def build_periodic_figure(df: pd.DataFrame,
                          group_filter=None, block_filter=None, ecp_filter=None,
                          search_value="", lang="fr") -> go.Figure:
    search_value = (search_value or "").strip().lower()
    is_match = pd.Series(True, index=df.index)

    if group_filter is not None: is_match &= df["group"]    == group_filter
    if block_filter is not None: is_match &= df["block"]    == block_filter
    if ecp_filter   is not None: is_match &= df["ecp_type"] == ecp_filter
    if search_value:
        name_col = "name_ru" if lang == "ru" else "name"
        is_match &= df.apply(
            lambda row: search_value in row[name_col].lower() or search_value in row["symbol"].lower(),
            axis=1,
        )

    customdata_cols = df[[
        "atomic_number", "symbol", "name", "group", "period",
        "block", "ecp_type", "basis_rec", "pseudo",
        "polarisabilite", "etats_ox", "volume_molaire",
        "ie1", "ea", "spin_mult", "vdw_radius",
        "functional", "dispersion", "relativistic", "name_ru",
    ]].values

    t = LANG[lang]
    name_idx = 19 if lang == "ru" else 2
    hover = (
        f"%{{customdata[1]}}<br>%{{customdata[{name_idx}]}}"
        f"<br>Z = %{{customdata[0]}} · {t['hover_bloc']} %{{customdata[5]}}"
        f"<br>IE₁ = %{{customdata[12]}} eV<extra></extra>"
    )

    fig = go.Figure()
    for idx, el in df.iterrows():
        matched = bool(is_match[idx])
        fig.add_shape(
            type="rect",
            x0=el["col"] - 0.46, x1=el["col"] + 0.46,
            y0=el["row"] - 0.46, y1=el["row"] + 0.46,
            fillcolor=el["color"],
            opacity=1.0 if matched else 0.14,
            line=dict(color="#1a2a33" if matched else "#37474f", width=1),
            layer="below",
        )

    fig.add_trace(go.Scatter(
        x=df["col"], y=df["row"],
        mode="markers+text",
        marker=dict(size=2, color="rgba(0,0,0,0)", symbol="square"),
        text=df["symbol"],
        textposition="middle center",
        textfont=dict(
            color=["rgba(255,255,255,1)" if m else "rgba(255,255,255,0.18)" for m in is_match],
            size=11, family="Inter",
        ),
        customdata=customdata_cols,
        hovertemplate=hover,
        showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=df["col"] - 0.33, y=df["row"] - 0.33,
        mode="text",
        text=[str(int(n)) for n in df["atomic_number"]],
        textfont=dict(
            color=[f"rgba(255,255,255,{0.7 if m else 0.08})" for m in is_match],
            size=7, family="Inter",
        ),
        hoverinfo="skip", showlegend=False,
    ))

    for period in sorted(df[df["row"] <= 7]["period"].unique()):
        fig.add_annotation(x=0.3, y=period, xanchor="right", text=f"P{int(period)}",
                           showarrow=False, font=dict(color="#eceff1", size=11))
    fig.add_annotation(x=0.3, y=8, xanchor="right", text="6*", showarrow=False,
                       font=dict(color="#cfd8dc", size=10))
    fig.add_annotation(x=0.3, y=9, xanchor="right", text="7*", showarrow=False,
                       font=dict(color="#cfd8dc", size=10))

    fig.update_xaxes(
        title="", tickmode="array",
        tickvals=list(range(1, 19)), ticktext=[str(n) for n in range(1, 19)],
        range=[0.5, 18.5], showgrid=False, zeroline=False, showline=False,
        tickfont=dict(color="#cfd8dc", size=10), fixedrange=True,
    )
    fig.update_yaxes(
        title="", tickmode="array",
        tickvals=[1, 2, 3, 4, 5, 6, 7, 8, 9],
        ticktext=["1", "2", "3", "4", "5", "6", "7", "6*", "7*"],
        range=[9.5, 0.5], showgrid=False, zeroline=False, showline=False,
        tickfont=dict(color="#cfd8dc", size=10),
        scaleanchor="x", scaleratio=1, fixedrange=True,
    )
    fig.update_layout(
        plot_bgcolor="#102027", paper_bgcolor="#102027",
        margin=dict(l=20, r=20, t=15, b=25),
        hoverlabel=dict(bgcolor="#263238", font_size=12, font_family="Inter"),
        dragmode=False, showlegend=False, hoverdistance=40,
    )
    return fig
