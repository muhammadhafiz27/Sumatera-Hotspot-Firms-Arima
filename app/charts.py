# ============================================================
# charts.py
# Grafik EDA interaktif menggunakan Plotly — Dark Theme
# ============================================================

import plotly.graph_objects as go
import pandas as pd

WARNA_KEMARAU = "#E07B39"
WARNA_HUJAN   = "#3B82F6"
WARNA_HIJAU   = "#2E7D32"
BG_CARD       = "#1A1F2E"
GRID_COLOR    = "rgba(255,255,255,0.05)"
FONT_COLOR    = "#D1D5DB"
AXIS_COLOR    = "#6B7280"

LAYOUT_BASE = dict(
    paper_bgcolor=BG_CARD,
    plot_bgcolor=BG_CARD,
    font=dict(color=FONT_COLOR, family="Inter, sans-serif"),
    title_font=dict(color="#FFFFFF", size=15),
    xaxis=dict(gridcolor=GRID_COLOR, color=AXIS_COLOR, showgrid=True, linecolor=GRID_COLOR),
    yaxis=dict(gridcolor=GRID_COLOR, color=AXIS_COLOR, showgrid=True, linecolor=GRID_COLOR),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=FONT_COLOR)),
    margin=dict(l=40, r=20, t=50, b=40),
)


def grafik_tren_bulanan(df_bulanan):
    colors = [WARNA_KEMARAU if m == "Kemarau" else WARNA_HUJAN for m in df_bulanan['musim']]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_bulanan['tanggal'],
        y=df_bulanan['jumlah_hotspot'],
        marker_color=colors,
        marker_line_width=0,
        name="Jumlah Hotspot",
        hovertemplate="<b>%{x|%B %Y}</b><br>Hotspot: %{y:,}<extra></extra>"
    ))

    idx_max = df_bulanan['jumlah_hotspot'].idxmax()
    baris_max = df_bulanan.loc[idx_max]
    fig.add_annotation(
        x=baris_max['tanggal'],
        y=baris_max['jumlah_hotspot'],
        text=f"El Niño 2023<br><b>{int(baris_max['jumlah_hotspot']):,}</b>",
        showarrow=True, arrowhead=2, arrowcolor="#EF4444",
        font=dict(color="#EF4444", size=11),
        bgcolor="rgba(239,68,68,0.1)", bordercolor="#EF4444",
        borderwidth=1, borderpad=4, ay=-50
    )

    fig.update_layout(
        **LAYOUT_BASE,
        title="Tren Jumlah Hotspot per Bulan",
        xaxis_title="Periode", yaxis_title="Jumlah Hotspot",
        hovermode="x unified", height=380,
        showlegend=False
    )
    return fig


def grafik_tahunan(df_bulanan):
    yearly = df_bulanan.groupby('year')['jumlah_hotspot'].sum().reset_index()
    fig = go.Figure(go.Bar(
        x=yearly['year'].astype(str),
        y=yearly['jumlah_hotspot'],
        marker_color=WARNA_KEMARAU,
        marker_line_width=0,
        text=yearly['jumlah_hotspot'].apply(lambda x: f"{int(x):,}"),
        textposition="outside",
        textfont=dict(color=FONT_COLOR, size=11),
        hovertemplate="<b>%{x}</b><br>Total: %{y:,}<extra></extra>"
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        title="Total Hotspot per Tahun",
        xaxis_title="Tahun", yaxis_title="Total Hotspot",
        height=350
    )
    return fig


def grafik_musiman(df_bulanan):
    seasonal = df_bulanan.groupby('month')['jumlah_hotspot'].mean().reset_index()
    bulan_nama = ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des']
    seasonal['bulan_nama'] = seasonal['month'].apply(lambda x: bulan_nama[x-1])
    colors = [WARNA_KEMARAU if m in [5,6,7,8,9,10] else WARNA_HUJAN for m in seasonal['month']]

    fig = go.Figure(go.Bar(
        x=seasonal['bulan_nama'],
        y=seasonal['jumlah_hotspot'],
        marker_color=colors,
        marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>Rata-rata: %{y:.0f}<extra></extra>"
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        title="Rata-rata Hotspot per Bulan",
        xaxis_title="Bulan", yaxis_title="Rata-rata Hotspot",
        height=350
    )
    return fig


def grafik_frp_bulanan(df_bulanan):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_bulanan['tanggal'],
        y=df_bulanan['rata_frp'],
        mode='lines+markers',
        name='Rata-rata FRP',
        line=dict(color="#C62828", width=2),
        marker=dict(size=5, color="#C62828"),
        fill='tozeroy',
        fillcolor='rgba(198,40,40,0.08)',
        hovertemplate="<b>%{x|%B %Y}</b><br>FRP: %{y:.1f} MW<extra></extra>"
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        title="Rata-rata FRP per Bulan",
        xaxis_title="Periode", yaxis_title="FRP (MW)",
        height=350, showlegend=False
    )
    return fig


def grafik_perbandingan_musim(df_bulanan):
    fig = go.Figure()
    for musim, warna in [("Kemarau", WARNA_KEMARAU), ("Hujan", WARNA_HUJAN)]:
        data_musim = df_bulanan[df_bulanan['musim'] == musim]['jumlah_hotspot']
        fig.add_trace(go.Box(
            y=data_musim,
            name=musim,
            marker_color=warna,
            line_color=warna,
            fillcolor=f"rgba(224,123,57,0.2)" if warna == WARNA_KEMARAU else "rgba(59,130,246,0.2)",
            boxmean=True
        ))
    fig.update_layout(
        **LAYOUT_BASE,
        title="Distribusi Hotspot per Musim",
        yaxis_title="Jumlah Hotspot",
        height=350
    )
    return fig
