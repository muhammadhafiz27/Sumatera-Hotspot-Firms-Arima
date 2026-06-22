# ============================================================
# forecast_component.py
# Komponen visualisasi SARIMA forecast — Dark Theme
# ============================================================

import plotly.graph_objects as go
import pandas as pd

BG_CARD    = "#1A1F2E"
GRID_COLOR = "rgba(255,255,255,0.05)"
FONT_COLOR = "#D1D5DB"
AXIS_COLOR = "#6B7280"

WARNA_HISTORIS = "#2E7D32"
WARNA_FORECAST = "#EF4444"
WARNA_FITTED   = "#E07B39"


def grafik_forecast(df_forecast):
    df_historis = df_forecast[df_forecast['tipe'] == 'historis'].copy()
    df_future   = df_forecast[df_forecast['tipe'] == 'forecast'].copy()

    fig = go.Figure()

    # Confidence interval (shaded area)
    fig.add_trace(go.Scatter(
        x=pd.concat([df_future['tanggal'], df_future['tanggal'][::-1]]),
        y=pd.concat([df_future['batas_atas'], df_future['batas_bawah'][::-1]]),
        fill='toself',
        fillcolor='rgba(239,68,68,0.1)',
        line=dict(color='rgba(0,0,0,0)'),
        name='Interval Kepercayaan 95%',
        hoverinfo='skip',
        showlegend=True
    ))

    # Data historis
    fig.add_trace(go.Scatter(
        x=df_historis['tanggal'],
        y=df_historis['jumlah_hotspot'],
        mode='lines',
        name='Data Historis',
        line=dict(color=WARNA_HISTORIS, width=2.5),
        hovertemplate="<b>%{x|%B %Y}</b><br>Historis: %{y:,}<extra></extra>"
    ))

    # Fitted values
    fig.add_trace(go.Scatter(
        x=df_historis['tanggal'],
        y=df_historis['fitted'],
        mode='lines',
        name='Fitted SARIMA',
        line=dict(color=WARNA_FITTED, width=1.5, dash='dot'),
        hovertemplate="<b>%{x|%B %Y}</b><br>Fitted: %{y:,.0f}<extra></extra>"
    ))

    # Forecast
    fig.add_trace(go.Scatter(
        x=df_future['tanggal'],
        y=df_future['forecast'],
        mode='lines+markers',
        name='Forecast 2026–2027',
        line=dict(color=WARNA_FORECAST, width=2.5, dash='dash'),
        marker=dict(size=7, color=WARNA_FORECAST,
                    line=dict(color='#fff', width=1)),
        hovertemplate="<b>%{x|%B %Y}</b><br>Prediksi: %{y:,}<extra></extra>"
    ))

    # Garis vertikal pemisah (manual via shape)
    fig.add_shape(
        type="line",
        x0="2026-07-01", x1="2026-07-01",
        y0=0, y1=1, yref="paper",
        line=dict(color="#6B7280", width=1.5, dash="dot")
    )
    fig.add_annotation(
        x="2026-07-01", y=0.98, yref="paper",
        text="← Historis  |  Forecast →",
        showarrow=False,
        font=dict(size=11, color="#6B7280"),
        xanchor="center", yanchor="top",
        bgcolor="rgba(26,31,46,0.8)",
        bordercolor="#374151", borderwidth=1, borderpad=4
    )

    fig.update_layout(
        paper_bgcolor=BG_CARD,
        plot_bgcolor=BG_CARD,
        font=dict(color=FONT_COLOR, family="Inter, sans-serif"),
        title=dict(
            text="Forecast Hotspot Kebakaran Hutan Sumatera<br><sup>Model SARIMA(1,1,1)(1,1,1,12)</sup>",
            font=dict(color="#FFFFFF", size=15)
        ),
        xaxis=dict(gridcolor=GRID_COLOR, color=AXIS_COLOR,
                   title="Periode", showgrid=True),
        yaxis=dict(gridcolor=GRID_COLOR, color=AXIS_COLOR,
                   title="Jumlah Hotspot", showgrid=True),
        hovermode="x unified",
        height=460,
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=FONT_COLOR),
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="left", x=0
        ),
        margin=dict(l=40, r=20, t=80, b=40)
    )

    return fig


def tabel_forecast(df_forecast):
    df_future = df_forecast[df_forecast['tipe'] == 'forecast'].copy()
    df_future['Periode'] = pd.to_datetime(df_future['periode']).dt.strftime('%B %Y')
    df_future['Musim'] = pd.to_datetime(df_future['periode']).dt.month.apply(
        lambda m: '🟠 Kemarau' if m in [5,6,7,8,9,10] else '🔵 Hujan'
    )
    df_future['batas_bawah'] = df_future['batas_bawah'].clip(lower=0)
    df_future = df_future.rename(columns={
        'forecast'    : 'Prediksi',
        'batas_bawah' : 'Batas Bawah (95%)',
        'batas_atas'  : 'Batas Atas (95%)',
    })
    return df_future[['Periode','Prediksi','Batas Bawah (95%)','Batas Atas (95%)','Musim']]
