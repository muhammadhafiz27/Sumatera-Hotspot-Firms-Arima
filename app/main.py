import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
from streamlit_folium import st_folium

from app.utils import (
    load_detail, load_bulanan, load_forecast, load_model_info,
    filter_detail, filter_bulanan, format_angka, statistik_ringkas
)
from app.map_component import buat_peta
from app.charts import (
    grafik_tren_bulanan, grafik_tahunan,
    grafik_musiman, grafik_frp_bulanan,
    grafik_perbandingan_musim
)
from app.forecast_component import grafik_forecast, tabel_forecast

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Hotspot Sumatera — NASA FIRMS",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# CSS — mengikuti palette TSX
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

/* ── Base ── */
html, body, .stApp, [data-testid="stAppViewContainer"] {
    background-color: #0F1117 !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
}
[data-testid="stHeader"] { background-color: #0F1117 !important; }
[data-testid="stMainBlockContainer"] { padding-top: 24px !important; padding-bottom: 48px !important; }

/* ── Typography ── */
.stApp p, .stApp span, .stApp div, .stApp label, .stApp li { color: #D1D5DB; font-family: 'Inter', -apple-system, sans-serif; }
h1,h2,h3,h4 { color:#fff !important; font-family:'Inter',-apple-system,sans-serif !important; }

/* ── Tabs — pill style dari TSX ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
    display: inline-flex !important;
    width: auto !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #9CA3AF !important;
    border-radius: 9px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    padding: 8px 18px !important;
    border: none !important;
    transition: all 0.18s !important;
}
.stTabs [aria-selected="true"] { background: #E07B39 !important; color: #fff !important; }
.stTabs [data-baseweb="tab-panel"] { background: transparent !important; padding-top: 16px !important; }

/* ── Selectbox ── */
.stSelectbox [data-baseweb="select"] > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #fff !important;
    border-radius: 8px !important;
}
.stSelectbox [data-baseweb="select"] span { color: #fff !important; }
[data-baseweb="popover"] { background: #1A1F2E !important; }
[data-baseweb="menu"] li { color: #D1D5DB !important; background: #1A1F2E !important; }
[data-baseweb="menu"] li:hover { background: rgba(255,255,255,0.06) !important; }

/* ── Slider ── */
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
    background: #E07B39 !important;
    border-color: #E07B39 !important;
    box-shadow: 0 0 0 3px rgba(224,123,57,0.3) !important;
}
[data-testid="stSlider"] [data-baseweb="slider"] [data-testid="stTickBar"] { display: none; }

/* ── Radio — mode peta buttons ── */
.stRadio > div { gap: 6px !important; flex-wrap: wrap !important; }
.stRadio label {
    background: transparent !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    padding: 6px 11px !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    color: #9CA3AF !important;
    cursor: pointer !important;
    transition: all 0.18s !important;
}
.stRadio label:has(input:checked) {
    background: rgba(224,123,57,0.14) !important;
    border-color: #E07B39 !important;
    color: #E07B39 !important;
}
.stRadio [data-testid="stMarkdownContainer"] p { color: inherit !important; font-size: inherit !important; }
/* hide actual radio circles */
.stRadio input[type="radio"] { display: none !important; }

/* ── Metric ── */
[data-testid="stMetric"] {
    background: #1A1F2E !important;
    border-radius: 14px !important;
    padding: 16px !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-top: 2px solid #E07B39 !important;
}
[data-testid="stMetricLabel"] { color: #6B7280 !important; font-size: 10px !important; font-weight: 700 !important; text-transform: uppercase !important; letter-spacing: 0.1em !important; }
[data-testid="stMetricValue"] { color: #fff !important; font-size: 17px !important; font-weight: 700 !important; }
[data-testid="stMetricDelta"] { color: #9CA3AF !important; font-size: 11px !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    background: #1A1F2E !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    overflow: hidden !important;
}
[data-testid="stDataFrame"] th {
    background: rgba(255,255,255,0.04) !important;
    color: #6B7280 !important;
    font-size: 10px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    padding: 8px 12px !important;
    border-bottom: 1px solid rgba(255,255,255,0.08) !important;
}
[data-testid="stDataFrame"] td { color: #D1D5DB !important; font-size: 13px !important; padding: 10px 12px !important; }
[data-testid="stDataFrame"] tr:hover td { background: rgba(255,255,255,0.025) !important; }

/* ── Progress bar ── */
[data-testid="stProgress"] > div {
    background: rgba(255,255,255,0.07) !important;
    border-radius: 3px !important;
    height: 6px !important;
}
[data-testid="stProgress"] > div > div {
    background: #E07B39 !important;
    border-radius: 3px !important;
    transition: width 0.5s ease !important;
}
.prog-hujan [data-testid="stProgress"] > div > div { background: #3B82F6 !important; }

/* ── Container border ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #1A1F2E !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 14px !important;
    padding: 4px 4px !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: #E07B39 !important; }

/* ── Caption ── */
.stCaption { color: #6B7280 !important; font-size: 12px !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #E07B39; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden !important; display: none !important; }

/* ── Map iframe ── */
iframe { border-radius: 12px !important; }

/* ── Warning ── */
[data-testid="stAlert"] { background: rgba(224,123,57,0.08) !important; border-color: rgba(224,123,57,0.3) !important; border-radius: 10px !important; }

/* ── HR ── */
hr { border-color: rgba(255,255,255,0.07) !important; margin: 0 !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# HELPERS
# ============================================================
def card(content_html, extra_style=""):
    """Wrapper dark card."""
    return f"""<div style="background:#1A1F2E; border:1px solid rgba(255,255,255,0.06);
        border-radius:14px; padding:20px; {extra_style}">{content_html}</div>"""

def label_upper(text):
    return f'<p style="font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#6B7280;margin:0 0 10px 0;">{text}</p>'

def kpi_card(icon, accent, title, value, sub):
    return f"""
    <div style="background:#1A1F2E; border:1px solid rgba(255,255,255,0.06);
                border-radius:14px; padding:20px;
                border-top:2px solid {accent};
                display:flex; gap:14px; align-items:flex-start;">
        <div style="background:{accent}1F; border-radius:10px; padding:10px 11px;
                    flex-shrink:0; font-size:20px; line-height:1;">{icon}</div>
        <div>
            <p style="font-size:10px;font-weight:700;letter-spacing:0.1em;
                      text-transform:uppercase;color:#6B7280;margin:0 0 6px 0;">{title}</p>
            <p style="font-size:24px;font-weight:800;color:#fff;line-height:1.1;margin:0 0 4px 0;">{value}</p>
            <p style="font-size:11px;color:#9CA3AF;margin:0;">{sub}</p>
        </div>
    </div>"""

def badge(text, color):
    return f'<span style="font-size:11px;padding:3px 10px;border-radius:20px;font-weight:600;background:{color}22;color:{color};">{text}</span>'

# ============================================================
# LOAD DATA
# ============================================================
df_detail        = load_detail()
df_bulanan       = load_bulanan()
df_forecast_full = load_forecast()
model_info       = load_model_info()

tahun_min = int(df_detail['year'].min())
tahun_max = int(df_detail['year'].max())

# ============================================================
# HEADER  —  dari TSX: logo + title
# ============================================================
st.markdown(f"""
<div style="padding:4px 0 20px; border-bottom:1px solid rgba(255,255,255,0.07);
            display:flex; align-items:center; gap:14px; margin-bottom:20px;">
    <div style="background:rgba(224,123,57,0.14); border:1px solid rgba(224,123,57,0.28);
                border-radius:12px; padding:10px 13px; font-size:24px;
                line-height:1; flex-shrink:0;">🔥</div>
    <div style="flex:1;">
        <h1 style="font-size:26px;font-weight:800;margin:0;letter-spacing:-0.025em;color:#fff;">
            Hotspot Sumatera Dashboard
        </h1>
        <p style="font-size:14px;color:#6B7280;margin:3px 0 0;font-weight:400;">
            Visualisasi data titik api NASA FIRMS dengan pemodelan prediksi SARIMA · Sumatera, Indonesia
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# FILTER BAR
# ============================================================
st.markdown(label_upper("⚙️ Filter & Pengaturan Peta"), unsafe_allow_html=True)

# Inject CSS untuk styling container
st.markdown("""
<style>
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] > div:first-child {
    background: #1A1F2E !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 14px !important;
    padding: 20px 24px !important;
    margin-bottom: 20px !important;
}
</style>
""", unsafe_allow_html=True)

with st.container(border=True):
    fc1, fc2, fc3, fc4 = st.columns([3, 1, 2, 3])
    with fc1:
        tahun_range = st.slider(
            "Rentang Tahun",
            min_value=tahun_min, max_value=tahun_max,
            value=(2020, tahun_max), step=1,
            help="Seret untuk mengubah rentang tahun data"
        )
    with fc2:
        musim_filter = st.selectbox(
            "Musim",
            options=["Semua", "Kemarau", "Hujan"],
            index=0
        )
    with fc3:
        min_confidence = st.slider(
            "Min. Confidence (%)",
            min_value=0, max_value=100, value=30, step=5
        )
    with fc4:
        mode_peta = st.radio(
            "Mode Peta",
            options=["heatmap", "timeseries", "forecast", "cluster"],
            format_func=lambda x: {
                "heatmap"   : "Heatmap",
                "timeseries": "Time Series",
                "forecast"  : "Forecast",
                "cluster"   : "Cluster"
            }[x],
            horizontal=True,
            index=0
        )

# ============================================================
# FILTER DATA
# ============================================================
df_filtered   = filter_detail(df_detail, tahun_range, musim_filter, min_confidence)
df_bul_filter = filter_bulanan(df_bulanan, tahun_range, musim_filter)
stats         = statistik_ringkas(df_filtered)

# ============================================================
# KPI CARDS  —  dari TSX: border-top accent, icon tinted bg
# ============================================================
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(kpi_card("🔥", "#E07B39", "Total Hotspot",
        format_angka(stats['total_hotspot']),
        f"{tahun_range[0]}–{tahun_range[1]} · Sumatera"), unsafe_allow_html=True)
with c2:
    st.markdown(kpi_card("⚡", "#2E7D32", "Rata-rata FRP",
        f"{stats['rata_frp']} MW",
        "Fire Radiative Power rata-rata"), unsafe_allow_html=True)
with c3:
    st.markdown(kpi_card("🌡️", "#C62828", "FRP Tertinggi",
        f"{stats['max_frp']} MW",
        "Puncak intensitas kebakaran"), unsafe_allow_html=True)
with c4:
    st.markdown(kpi_card("🎯", "#1565C0", "Rata-rata Confidence",
        f"{stats['rata_confidence']}%",
        "Tingkat kepercayaan deteksi"), unsafe_allow_html=True)

st.markdown('<div style="height:24px;"></div>', unsafe_allow_html=True)

# ============================================================
# TABS
# ============================================================
tab1, tab2, tab3 = st.tabs([
    "🗺️  Peta Sebaran",
    "📊  Analisis Temporal",
    "📈  Forecast SARIMA"
])

# ============================================================
# TAB 1 — PETA SEBARAN  (dari TSX: TabMap)
# ============================================================
with tab1:
    col_info, col_peta_area = st.columns([1, 3])

    with col_info:
        # ── Filter aktif card ──
        total_pts = len(df_filtered)
        st.markdown(f"""
        <div style="background:#1A1F2E; border:1px solid rgba(255,255,255,0.06);
                    border-radius:14px; padding:16px; margin-bottom:12px;">
            {label_upper("Filter Aktif")}
            <div style="display:flex;justify-content:space-between;margin-bottom:8px;font-size:13px;">
                <span style="color:#9CA3AF;">Tahun</span>
                <span style="color:#fff;font-weight:600;">{tahun_range[0]}–{tahun_range[1]}</span>
            </div>
            <div style="display:flex;justify-content:space-between;margin-bottom:8px;font-size:13px;">
                <span style="color:#9CA3AF;">Musim</span>
                <span style="color:#fff;font-weight:600;">{"Semua" if musim_filter=="Semua" else ("Kemarau 🌞" if musim_filter=="Kemarau" else "Hujan 🌧")}</span>
            </div>
            <div style="display:flex;justify-content:space-between;margin-bottom:12px;font-size:13px;">
                <span style="color:#9CA3AF;">Confidence</span>
                <span style="color:#fff;font-weight:600;">≥ {min_confidence}%</span>
            </div>
            <div style="border-top:1px solid rgba(255,255,255,0.07);padding-top:10px;
                        display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:13px;color:#9CA3AF;">Total</span>
                <span style="font-size:12px;font-weight:700;background:rgba(224,123,57,0.17);
                             color:#E07B39;padding:2px 10px;border-radius:20px;">
                    {format_angka(total_pts)}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Legenda FRP card ──
        st.markdown(f"""
        <div style="background:#1A1F2E; border:1px solid rgba(255,255,255,0.06);
                    border-radius:14px; padding:16px; margin-bottom:12px;">
            {label_upper("Intensitas FRP")}
            {"".join([
                f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;font-size:13px;">'
                f'<div style="width:10px;height:10px;border-radius:50%;background:{c};flex-shrink:0;"></div>'
                f'<span style="color:#fff;flex:1;">{l}</span>'
                f'<span style="color:#6B7280;font-size:11px;">{r}</span>'
                f'</div>'
                for c,l,r in [
                    ("#FBBF24","Rendah","< 20 MW"),
                    ("#FF8C00","Sedang","20–50 MW"),
                    ("#FF4500","Tinggi","50–100 MW"),
                    ("#8B0000","Ekstrem","> 100 MW"),
                ]
            ])}
        </div>
        """, unsafe_allow_html=True)

        # ── Distribusi Musim — native components ──
        if not df_filtered.empty:
            dist  = df_filtered['musim'].value_counts()
            total = len(df_filtered)

            st.markdown(f"""
            <style>
            [data-testid="stVerticalBlockBorderWrapper"] {{
                background:#1A1F2E !important;
                border:1px solid rgba(255,255,255,0.06) !important;
                border-radius:14px !important;
            }}
            </style>
            """, unsafe_allow_html=True)

            with st.container(border=True):
                st.markdown(label_upper("Distribusi Musim"), unsafe_allow_html=True)
                for m, count in dist.items():
                    pct        = count / total
                    emoji      = "🌞" if m == "Kemarau" else "🌧"
                    warna_teks = "#E07B39" if m == "Kemarau" else "#3B82F6"
                    is_hujan   = (m != "Kemarau")

                    col_l, col_r = st.columns([3, 1])
                    with col_l:
                        st.markdown(
                            f"<p style='color:{warna_teks};font-size:13px;margin:4px 0 6px 0;font-weight:500;'>"
                            f"{emoji} {m}</p>",
                            unsafe_allow_html=True
                        )
                    with col_r:
                        st.markdown(
                            f"<p style='color:#fff;font-size:13px;font-weight:700;"
                            f"text-align:right;margin:4px 0 6px 0;'>{pct*100:.0f}%</p>",
                            unsafe_allow_html=True
                        )
                    if is_hujan:
                        st.markdown('<div class="prog-hujan">', unsafe_allow_html=True)
                    st.progress(pct)
                    if is_hujan:
                        st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)

    with col_peta_area:
        # ── Mode info label ──
        mode_desc = {
            "heatmap"   : "Mode Heatmap — kepadatan titik api divisualisasikan menggunakan intensitas warna per km²",
            "timeseries": "Mode Time Series — distribusi hotspot dianimasikan per bulan sesuai filter tahun",
            "forecast"  : "Mode Forecast — bubble prediksi per provinsi berdasarkan model SARIMA Jul 2026–Jun 2027",
            "cluster"   : "Mode Cluster — pengelompokan hotspot otomatis berdasarkan kedekatan geografis",
        }
        st.markdown(
            f"<p style='font-size:11px;color:#6B7280;margin:0 0 8px 0;'>{mode_desc[mode_peta]}</p>",
            unsafe_allow_html=True
        )

        if df_filtered.empty:
            st.markdown("""
            <div style="background:#1A1F2E;border:1px solid rgba(255,255,255,0.06);
                        border-radius:14px;padding:60px;text-align:center;">
                <p style="font-size:36px;margin:0 0 10px 0;">🔍</p>
                <p style="color:#9CA3AF;font-size:14px;margin:0;">Tidak ada data untuk filter ini.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # ── Total badge overlay info ──
            st.markdown(
                f"<div style='display:flex;justify-content:flex-end;margin-bottom:6px;'>"
                f"<span style='font-size:11px;font-weight:700;background:rgba(0,0,0,0.75);"
                f"color:#E07B39;padding:5px 12px;border-radius:8px;"
                f"border:1px solid rgba(255,255,255,0.1);'>"
                f"🔥 {format_angka(total_pts)} titik api</span></div>",
                unsafe_allow_html=True
            )
            with st.spinner("Memuat peta..."):
                if mode_peta == "forecast":
                    peta = buat_peta(df_filtered, mode=mode_peta,
                                     df_forecast=df_forecast_full,
                                     df_detail_full=df_detail)
                else:
                    peta = buat_peta(df_filtered, mode=mode_peta)
                st_folium(peta, width=None, height=520, returned_objects=[])

        # ── NASA FIRMS attribution ──
        st.markdown(
            "<p style='font-size:10px;color:#4B5563;margin:6px 0 0 0;'>NASA FIRMS · MODIS Collection 6.1 & VIIRS S-NPP</p>",
            unsafe_allow_html=True
        )

# ============================================================
# TAB 2 — ANALISIS TEMPORAL  (dari TSX: TabTemporal)
# ============================================================
with tab2:
    if df_bul_filter.empty:
        st.warning("Tidak ada data untuk filter yang dipilih.")
    else:
        # ── Tren bulanan full width ──
        st.markdown("""
        <div style="background:#1A1F2E;border:1px solid rgba(255,255,255,0.06);
                    border-radius:14px;padding:20px 20px 8px 20px;margin-bottom:16px;">
            <p style="color:#fff;font-weight:700;font-size:14px;margin:0 0 3px 0;">Tren Bulanan — Jumlah Hotspot</p>
            <p style="color:#6B7280;font-size:12px;margin:0 0 0 0;">
                <span style="color:#E07B39;">■ Kemarau</span>&nbsp;&nbsp;
                <span style="color:#3B82F6;">■ Hujan</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(grafik_tren_bulanan(df_bul_filter), use_container_width=True)

        # ── 2-kolom: tahunan + seasonal ──
        col_a, col_b = st.columns(2)
        with col_a:
            st.plotly_chart(grafik_tahunan(df_bul_filter), use_container_width=True)
        with col_b:
            st.plotly_chart(grafik_musiman(df_bul_filter), use_container_width=True)

        # ── 2-kolom: FRP + box plot ──
        col_c, col_d = st.columns(2)
        with col_c:
            st.plotly_chart(grafik_frp_bulanan(df_bul_filter), use_container_width=True)
        with col_d:
            st.plotly_chart(grafik_perbandingan_musim(df_bul_filter), use_container_width=True)

        st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)

        # ── Metric cards — dari TSX: border-top accent per warna ──
        rata_val = int(round(df_bul_filter['jumlah_hotspot'].mean()))
        med_val  = int(round(df_bul_filter['jumlah_hotspot'].median()))
        idx_max  = df_bul_filter['jumlah_hotspot'].idxmax()
        idx_min  = df_bul_filter['jumlah_hotspot'].idxmin()

        accents = ["#E07B39", "#3B82F6", "#EF4444", "#10B981"]
        cs1, cs2, cs3, cs4 = st.columns(4)
        for col, lbl, val, sub, acc in zip(
            [cs1, cs2, cs3, cs4],
            ["Rata-rata Bulanan", "Median Bulanan", "Bulan Tertinggi", "Bulan Terendah"],
            [format_angka(rata_val), format_angka(med_val),
             df_bul_filter.loc[idx_max, 'periode'],
             df_bul_filter.loc[idx_min, 'periode']],
            ["hotspot/bulan", "nilai tengah distribusi",
             f"{format_angka(int(df_bul_filter.loc[idx_max,'jumlah_hotspot']))} hotspot",
             f"{format_angka(int(df_bul_filter.loc[idx_min,'jumlah_hotspot']))} hotspot"],
            accents
        ):
            with col:
                st.markdown(f"""
                <div style="background:#1A1F2E;border:1px solid rgba(255,255,255,0.06);
                            border-radius:14px;padding:16px;border-top:2px solid {acc};">
                    <p style="font-size:10px;font-weight:700;letter-spacing:0.1em;
                              text-transform:uppercase;color:#6B7280;margin:0 0 8px 0;">{lbl}</p>
                    <p style="font-size:17px;font-weight:700;color:#fff;margin:0 0 4px 0;">{val}</p>
                    <p style="font-size:11px;color:#9CA3AF;margin:0;">{sub}</p>
                </div>
                """, unsafe_allow_html=True)

# ============================================================
# TAB 3 — FORECAST SARIMA  (dari TSX: TabForecast)
# ============================================================
with tab3:
    # ── Header 2 kolom: model info + metrik ──
    col_m, col_met = st.columns([1, 1])

    with col_m:
        st.markdown(f"""
        <div style="background:#1A1F2E;border:1px solid rgba(255,255,255,0.06);
                    border-radius:14px;padding:20px;">
            {label_upper("Model Forecasting")}
            <p style="font-size:21px;font-weight:900;color:#E07B39;font-family:monospace;
                      letter-spacing:-0.02em;margin:0 0 10px 0;">SARIMA(1,1,1)(1,1,1,12)</p>
            <p style="font-size:13px;color:#9CA3AF;line-height:1.65;margin:0 0 14px 0;">
                Model Seasonal ARIMA dilatih Jan 2020 – Des 2025 (72 bulan).
                Orde dipilih via Auto ARIMA (AIC). Komponen musiman periode 12 bulan
                menangkap pola kemarau/hujan tahunan Sumatera.
                Forecast: <b style="color:#E07B39;">Jul 2026 – Jun 2027</b>.
            </p>
            <div style="display:flex;flex-wrap:wrap;gap:6px;">
                {"".join([
                    f'<span style="font-size:10px;padding:3px 9px;border-radius:20px;'
                    f'background:rgba(255,255,255,0.06);color:#9CA3AF;">{t}</span>'
                    for t in ["SARIMA","Seasonal 12M","NASA FIRMS","2020–2025","statsmodels"]
                ])}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_met:
        st.markdown("### Metrik Evaluasi Model")
        
        col_mae, col_rmse, col_mape = st.columns(3)
        with col_mae:
            st.metric("MAE", f"{model_info['mae']:.2f}")
        with col_rmse:
            st.metric("RMSE", f"{model_info['rmse']:.2f}")
        with col_mape:
            st.metric("MAPE", f"{model_info['mape']:.2f}%")

    st.markdown('<div style="height:16px;"></div>', unsafe_allow_html=True)

    # ── Forecast chart ──
    st.plotly_chart(grafik_forecast(df_forecast_full), use_container_width=True)

    st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)

    # ── Forecast table ──
    st.markdown(f"""
    <div style="background:#1A1F2E;border:1px solid rgba(255,255,255,0.06);
                border-radius:14px;padding:16px 20px;margin-bottom:12px;">
        <p style="color:#fff;font-size:14px;font-weight:700;margin:0;">Tabel Prediksi Bulanan</p>
    </div>
    """, unsafe_allow_html=True)

    df_tabel = tabel_forecast(df_forecast_full)
    st.dataframe(df_tabel, use_container_width=True, hide_index=True)
    st.caption("Batas bawah negatif diclip ke 0. MAPE tinggi karena nilai aktual sangat rendah di musim hujan.")

# ============================================================
# FOOTER
# ============================================================
st.markdown("""
<div style="margin-top:48px;padding-top:20px;border-top:1px solid rgba(255,255,255,0.05);text-align:center;">
    <p style="font-size:12px;color:#6B7280;margin:0;">
        Sumber data: <span style="color:#9CA3AF;">NASA FIRMS (Fire Information for Resource Management System)</span>
        &nbsp;· MODIS Collection 6.1 & VIIRS S-NPP · © NASA
    </p>
    <p style="font-size:12px;color:#6B7280;margin:4px 0 0 0;">
        Model: <span style="color:#9CA3AF;">SARIMA(1,1,1)(1,1,1,12)</span>
        &nbsp;· Visualisasi Data Spasio-Temporal — Universitas Andalas
    </p>
</div>
""", unsafe_allow_html=True)