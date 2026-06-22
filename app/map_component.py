# ============================================================
# map_component.py
# Komponen peta Folium — Dark Theme + TimestampedGeoJson + Forecast Layer
# ============================================================

import folium
from folium.plugins import HeatMap, MarkerCluster, TimestampedGeoJson
import pandas as pd
from app.utils import get_warna_frp, get_radius_frp

# Koordinat pusat 8 provinsi Sumatera
PROVINSI_COORDS = {
    "Aceh"             : (4.695135,  96.749397),
    "Sumatera Utara"   : (2.115210,  99.543495),
    "Sumatera Barat"   : (-0.739817, 100.800049),
    "Riau"             : (0.293419,  101.706940),
    "Jambi"            : (-1.612302, 103.611824),
    "Sumatera Selatan" : (-3.319392, 103.914399),
    "Bengkulu"         : (-3.793928, 102.260094),
    "Lampung"          : (-4.557573, 105.405170),
}

# Bounding box kasar tiap provinsi [lat_min, lat_max, lon_min, lon_max]
PROVINSI_BBOX = {
    "Aceh"             : ( 2.0,  6.0,  95.0,  98.5),
    "Sumatera Utara"   : ( 1.0,  4.0,  97.5, 100.5),
    "Sumatera Barat"   : (-3.0,  1.0,  99.0, 101.5),
    "Riau"             : (-1.5,  3.0, 100.0, 106.5),
    "Jambi"            : (-3.5, -0.5, 101.5, 105.0),
    "Sumatera Selatan" : (-5.0, -1.5, 102.5, 107.0),
    "Bengkulu"         : (-5.5, -2.0, 101.5, 104.0),
    "Lampung"          : (-6.0, -3.5, 103.5, 107.0),
}

# JS snippet untuk set default speed slider ke 50 (skala 0–100)
_JS_DEFAULT_SPEED = """
<script>
document.addEventListener("DOMContentLoaded", function() {
    var checkReady = setInterval(function() {
        var sliders = document.querySelectorAll('.timecontrol-speed input[type=range]');
        if (sliders.length > 0) {
            sliders.forEach(function(slider) {
                slider.value = 50;
                slider.dispatchEvent(new Event('input'));
                slider.dispatchEvent(new Event('change'));
            });
            clearInterval(checkReady);
        }
    }, 300);
});
</script>
"""


def _assign_provinsi(lat, lon):
    """Tentukan provinsi berdasarkan koordinat (bounding box sederhana)."""
    for prov, (lat_min, lat_max, lon_min, lon_max) in PROVINSI_BBOX.items():
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            return prov
    return "Lainnya"


def _base_map():
    peta = folium.Map(
        location=[0.5, 101.5],
        zoom_start=6,
        tiles="CartoDB dark_matter"
    )
    folium.TileLayer("CartoDB positron", name="Light Mode").add_to(peta)
    folium.TileLayer("OpenStreetMap",    name="OpenStreetMap").add_to(peta)
    return peta


def _tambah_css_dan_legenda(peta, show_frp_legend=True):
    if show_frp_legend:
        legenda_html = """
        <div style="position:fixed; bottom:80px; left:24px; z-index:1000;
                    background:rgba(26,31,46,0.95); backdrop-filter:blur(8px);
                    padding:14px 16px; border-radius:12px;
                    border:1px solid rgba(255,255,255,0.08);
                    font-family:Inter,Arial,sans-serif; font-size:12px;
                    box-shadow:0 4px 20px rgba(0,0,0,0.4); color:#D1D5DB;">
            <div style="font-weight:600; font-size:11px; text-transform:uppercase;
                        letter-spacing:0.06em; color:#9CA3AF; margin-bottom:10px;">
                Intensitas FRP
            </div>
            <div style="display:flex; flex-direction:column; gap:7px;">
                <div style="display:flex; align-items:center; gap:8px;">
                    <div style="width:10px;height:10px;border-radius:50%;background:#FFD700;flex-shrink:0;"></div>
                    <span>&lt; 20 MW — Rendah</span>
                </div>
                <div style="display:flex; align-items:center; gap:8px;">
                    <div style="width:10px;height:10px;border-radius:50%;background:#FF8C00;flex-shrink:0;"></div>
                    <span>20–50 MW — Sedang</span>
                </div>
                <div style="display:flex; align-items:center; gap:8px;">
                    <div style="width:10px;height:10px;border-radius:50%;background:#FF4500;flex-shrink:0;"></div>
                    <span>50–100 MW — Tinggi</span>
                </div>
                <div style="display:flex; align-items:center; gap:8px;">
                    <div style="width:10px;height:10px;border-radius:50%;background:#8B0000;flex-shrink:0;"></div>
                    <span>&gt; 100 MW — Sangat Tinggi</span>
                </div>
            </div>
        </div>
        """
        peta.get_root().html.add_child(folium.Element(legenda_html))

    css = """
    <style>
        .leaflet-popup-content-wrapper {
            background:#1A1F2E !important;
            border:1px solid rgba(255,255,255,0.08) !important;
            border-radius:10px !important;
            box-shadow:0 4px 20px rgba(0,0,0,0.5) !important;
            padding:0 !important;
        }
        .leaflet-popup-content { margin:0 !important; color:#D1D5DB !important; }
        .leaflet-popup-tip { background:#1A1F2E !important; }
        .leaflet-popup-close-button { color:#9CA3AF !important; }
        .leaflet-popup-close-button:hover { color:#fff !important; }
        .leaflet-control-layers {
            background:rgba(26,31,46,0.95) !important;
            border:1px solid rgba(255,255,255,0.08) !important;
            border-radius:10px !important;
        }
        .leaflet-control-layers label { color:#D1D5DB !important; }
        .leaflet-control-timecontrol {
            background:rgba(26,31,46,0.95) !important;
            border:1px solid rgba(255,255,255,0.08) !important;
            border-radius:10px !important;
            color:#D1D5DB !important;
        }
        .timecontrol-slider input[type=range] { accent-color:#E07B39; }
        .timecontrol-date { color:#E07B39 !important; font-weight:600 !important; }
        .timecontrol-play { background:#E07B39 !important; border-color:#E07B39 !important; }
    </style>
    """
    peta.get_root().html.add_child(folium.Element(css))
    folium.LayerControl(collapsed=False, position='topright').add_to(peta)


# ============================================================
# PETA 1: HEATMAP STATIS
# ============================================================
def buat_peta_heatmap(df_filtered):
    peta = _base_map()
    if df_filtered.empty:
        _tambah_css_dan_legenda(peta)
        return peta

    heat_data = [
        [row['latitude'], row['longitude'], min(row['frp'], 200)]
        for _, row in df_filtered.iterrows()
    ]
    HeatMap(
        heat_data,
        name="🌡️ Heatmap FRP",
        min_opacity=0.35, radius=14, blur=12,
        gradient={"0.0":"#000000","0.3":"#FFD700","0.6":"#FF8C00","0.8":"#FF4500","1.0":"#8B0000"}
    ).add_to(peta)

    _tambah_css_dan_legenda(peta)
    return peta


# ============================================================
# PETA 2: TIME SERIES HISTORIS (TimestampedGeoJson)
# ============================================================
def buat_peta_timeseries(df_filtered, max_per_bulan=300):
    peta = _base_map()
    if df_filtered.empty:
        _tambah_css_dan_legenda(peta)
        return peta

    df_ts = df_filtered.copy()
    df_ts['acq_date'] = pd.to_datetime(df_ts['acq_date'])
    df_ts['periode']  = df_ts['acq_date'].dt.to_period('M').astype(str)

    df_sampled = (
        df_ts.groupby('periode', group_keys=False)
        .apply(lambda g: g.nlargest(max_per_bulan, 'frp'))
        .reset_index(drop=True)
    )

    features = []
    for _, row in df_sampled.iterrows():
        warna     = get_warna_frp(row['frp'])
        tgl       = row['acq_date']
        timestamp = tgl.strftime('%Y-%m-%dT00:00:00') if hasattr(tgl, 'strftime') else str(tgl)
        tgl_str   = tgl.strftime('%d %b %Y') if hasattr(tgl, 'strftime') else str(tgl)

        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row['longitude'], row['latitude']]
            },
            "properties": {
                "time"     : timestamp,
                "popup"    : (
                    f"<div style='font-family:Inter,Arial;font-size:12px;"
                    f"background:#1A1F2E;color:#D1D5DB;padding:12px;"
                    f"border-radius:8px;min-width:160px;'>"
                    f"<b style='color:#fff;'>📅 {tgl_str}</b><br>"
                    f"<span style='color:#9CA3AF;'>FRP:</span> "
                    f"<span style='color:{warna};font-weight:600;'>{row['frp']:.1f} MW</span><br>"
                    f"<span style='color:#9CA3AF;'>Confidence:</span> "
                    f"<span style='color:#fff;'>{row['confidence']:.0f}%</span><br>"
                    f"<span style='color:#9CA3AF;'>Satelit:</span> "
                    f"<span style='color:#fff;'>{row['satellite']}</span><br>"
                    f"<span style='color:#9CA3AF;'>Musim:</span> "
                    f"<span style='color:#fff;'>{'🟠 Kemarau' if row['musim'] == 'Kemarau' else '🔵 Hujan'}</span>"
                    f"</div>"
                ),
                "icon"     : "circle",
                "iconstyle": {
                    "fillColor"  : warna,
                    "fillOpacity": 0.75,
                    "stroke"     : True,
                    "color"      : warna,
                    "weight"     : 1,
                    "radius"     : get_radius_frp(row['frp']) + 2
                }
            }
        })

    TimestampedGeoJson(
        data={"type": "FeatureCollection", "features": features},
        period="P1M",
        duration="P1M",
        auto_play=False,
        loop=False,
        max_speed=5,
        loop_button=True,
        date_options="YYYY-MM",
        time_slider_drag_update=True,
        add_last_point=False,
        transition_time=1000,   # ← 1000ms per frame, naikkan untuk lebih lambat
    ).add_to(peta)

    # Set default speed slider ke 50
    peta.get_root().html.add_child(folium.Element(_JS_DEFAULT_SPEED))

    _tambah_css_dan_legenda(peta)
    return peta


# ============================================================
# PETA 3: FORECAST SARIMA di PETA (Bubble per Provinsi)
# ============================================================
def buat_peta_forecast(df_detail, df_forecast):
    """
    Tampilkan prediksi SARIMA per bulan sebagai bubble di peta.
    Distribusi spasial dihitung dari proporsi hotspot historis per provinsi.
    """
    peta = _base_map()

    # Hitung proporsi historis per provinsi
    df_hist = df_detail.copy()
    if 'provinsi' not in df_hist.columns:
        df_hist['provinsi'] = df_hist.apply(
            lambda r: _assign_provinsi(r['latitude'], r['longitude']), axis=1
        )

    total_prov = df_hist[df_hist['provinsi'] != 'Lainnya']['provinsi'].value_counts()
    total_all  = total_prov.sum()
    proporsi   = (total_prov / total_all).to_dict()

    # Ambil data forecast (tipe = 'forecast')
    df_fc = df_forecast[df_forecast['tipe'] == 'forecast'].copy()
    df_fc['tanggal'] = pd.to_datetime(df_fc['periode'])

    # Buat GeoJSON features per bulan per provinsi
    features = []
    for _, baris in df_fc.iterrows():
        total_pred = max(int(baris['forecast']), 0)
        bulan_str  = baris['tanggal'].strftime('%B %Y')
        timestamp  = baris['tanggal'].strftime('%Y-%m-%dT00:00:00')
        musim      = '🟠 Kemarau' if baris['tanggal'].month in [5,6,7,8,9,10] else '🔵 Hujan'

        for prov, prop in proporsi.items():
            if prov not in PROVINSI_COORDS:
                continue

            pred_prov = int(total_pred * prop)
            if pred_prov == 0:
                continue

            lat, lon = PROVINSI_COORDS[prov]
            # Radius proporsional terhadap prediksi (max radius 30)
            radius = max(5, min(30, int(pred_prov / 15)))
            # Warna berdasarkan jumlah prediksi
            if pred_prov >= 300:
                warna = "#8B0000"
            elif pred_prov >= 150:
                warna = "#FF4500"
            elif pred_prov >= 50:
                warna = "#FF8C00"
            else:
                warna = "#FFD700"

            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "properties": {
                    "time"     : timestamp,
                    "popup"    : (
                        f"<div style='font-family:Inter,Arial;font-size:12px;"
                        f"background:#1A1F2E;color:#D1D5DB;padding:14px;"
                        f"border-radius:8px;min-width:180px;'>"
                        f"<div style='display:flex;align-items:center;gap:8px;"
                        f"margin-bottom:10px;padding-bottom:8px;"
                        f"border-bottom:1px solid rgba(255,255,255,0.08);'>"
                        f"<div style='width:10px;height:10px;border-radius:50%;"
                        f"background:{warna};'></div>"
                        f"<b style='color:#fff;font-size:13px;'>📍 {prov}</b>"
                        f"</div>"
                        f"<table style='width:100%;border-collapse:collapse;'>"
                        f"<tr><td style='color:#9CA3AF;font-size:11px;padding:3px 0;'>📅 Periode</td>"
                        f"<td style='color:#fff;font-size:11px;text-align:right;'>{bulan_str}</td></tr>"
                        f"<tr><td style='color:#9CA3AF;font-size:11px;padding:3px 0;'>🔮 Prediksi</td>"
                        f"<td style='color:{warna};font-size:12px;font-weight:600;"
                        f"text-align:right;'>{pred_prov:,} hotspot</td></tr>"
                        f"<tr><td style='color:#9CA3AF;font-size:11px;padding:3px 0;'>📊 Total Sumatera</td>"
                        f"<td style='color:#fff;font-size:11px;text-align:right;'>{total_pred:,}</td></tr>"
                        f"<tr><td style='color:#9CA3AF;font-size:11px;padding:3px 0;'>🌤️ Musim</td>"
                        f"<td style='color:#fff;font-size:11px;text-align:right;'>{musim}</td></tr>"
                        f"</table>"
                        f"<div style='margin-top:10px;padding-top:8px;"
                        f"border-top:1px solid rgba(255,255,255,0.08);"
                        f"color:#6B7280;font-size:10px;'>"
                        f"⚠️ Prediksi berbasis distribusi historis"
                        f"</div>"
                        f"</div>"
                    ),
                    "icon"     : "circle",
                    "iconstyle": {
                        "fillColor"  : warna,
                        "fillOpacity": 0.6,
                        "stroke"     : True,
                        "color"      : warna,
                        "weight"     : 2,
                        "radius"     : radius
                    }
                }
            })

    if features:
        TimestampedGeoJson(
            data={"type": "FeatureCollection", "features": features},
            period="P1M",
            duration="P1M",
            auto_play=False,
            loop=False,
            max_speed=3,
            loop_button=True,
            date_options="YYYY-MM",
            time_slider_drag_update=True,
            add_last_point=False,
        ).add_to(peta)

        # Set default speed slider ke 50
        peta.get_root().html.add_child(folium.Element(_JS_DEFAULT_SPEED))

    # Legenda forecast
    legenda_html = """
    <div style="position:fixed; bottom:80px; left:24px; z-index:1000;
                background:rgba(26,31,46,0.95); backdrop-filter:blur(8px);
                padding:14px 16px; border-radius:12px;
                border:1px solid rgba(255,255,255,0.08);
                font-family:Inter,Arial,sans-serif; font-size:12px;
                box-shadow:0 4px 20px rgba(0,0,0,0.4); color:#D1D5DB;">
        <div style="font-weight:600; font-size:11px; text-transform:uppercase;
                    letter-spacing:0.06em; color:#9CA3AF; margin-bottom:10px;">
            Prediksi Hotspot
        </div>
        <div style="display:flex; flex-direction:column; gap:7px;">
            <div style="display:flex; align-items:center; gap:8px;">
                <div style="width:10px;height:10px;border-radius:50%;background:#FFD700;flex-shrink:0;"></div>
                <span>&lt; 50 — Rendah</span>
            </div>
            <div style="display:flex; align-items:center; gap:8px;">
                <div style="width:10px;height:10px;border-radius:50%;background:#FF8C00;flex-shrink:0;"></div>
                <span>50–150 — Sedang</span>
            </div>
            <div style="display:flex; align-items:center; gap:8px;">
                <div style="width:10px;height:10px;border-radius:50%;background:#FF4500;flex-shrink:0;"></div>
                <span>150–300 — Tinggi</span>
            </div>
            <div style="display:flex; align-items:center; gap:8px;">
                <div style="width:10px;height:10px;border-radius:50%;background:#8B0000;flex-shrink:0;"></div>
                <span>&gt; 300 — Sangat Tinggi</span>
            </div>
            <div style="margin-top:8px; padding-top:8px;
                        border-top:1px solid rgba(255,255,255,0.08);
                        color:#6B7280; font-size:10px; line-height:1.4;">
                🔮 Model SARIMA(1,1,1)(1,1,1,12)<br>
                Ukuran bubble ∝ jumlah prediksi
            </div>
        </div>
    </div>
    """
    peta.get_root().html.add_child(folium.Element(legenda_html))

    css = """
    <style>
        .leaflet-popup-content-wrapper {
            background:#1A1F2E !important;
            border:1px solid rgba(255,255,255,0.08) !important;
            border-radius:10px !important;
            box-shadow:0 4px 20px rgba(0,0,0,0.5) !important;
            padding:0 !important;
        }
        .leaflet-popup-content { margin:0 !important; }
        .leaflet-popup-tip { background:#1A1F2E !important; }
        .leaflet-popup-close-button { color:#9CA3AF !important; }
        .leaflet-control-layers {
            background:rgba(26,31,46,0.95) !important;
            border:1px solid rgba(255,255,255,0.08) !important;
            border-radius:10px !important;
        }
        .leaflet-control-layers label { color:#D1D5DB !important; }
        .leaflet-control-timecontrol {
            background:rgba(26,31,46,0.95) !important;
            border:1px solid rgba(255,255,255,0.08) !important;
            border-radius:10px !important;
            color:#D1D5DB !important;
        }
        .timecontrol-slider input[type=range] { accent-color:#E07B39; }
        .timecontrol-date { color:#E07B39 !important; font-weight:600 !important; }
        .timecontrol-play { background:#E07B39 !important; border-color:#E07B39 !important; }
    </style>
    """
    peta.get_root().html.add_child(folium.Element(css))
    folium.LayerControl(collapsed=False, position='topright').add_to(peta)

    return peta


# ============================================================
# WRAPPER UTAMA (dipanggil dari main.py)
# ============================================================
def buat_peta(df_filtered, mode="heatmap", df_forecast=None, df_detail_full=None):
    if mode == "heatmap":
        return buat_peta_heatmap(df_filtered)
    elif mode == "timeseries":
        return buat_peta_timeseries(df_filtered)
    elif mode == "forecast":
        return buat_peta_forecast(df_detail_full, df_forecast)
    elif mode == "cluster":
        peta = _base_map()
        if df_filtered.empty:
            _tambah_css_dan_legenda(peta)
            return peta
        cluster = MarkerCluster(name="🔵 Cluster Hotspot").add_to(peta)
        df_plot = df_filtered.nlargest(2000, 'frp') if len(df_filtered) > 2000 else df_filtered
        for _, row in df_plot.iterrows():
            tgl   = row['acq_date'].date() if hasattr(row['acq_date'], 'date') else row['acq_date']
            warna = get_warna_frp(row['frp'])
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(
                    f"<div style='font-family:Inter,Arial;font-size:12px;"
                    f"background:#1A1F2E;color:#D1D5DB;padding:12px;border-radius:8px;'>"
                    f"<b style='color:#fff;'>{tgl}</b><br>"
                    f"FRP: <span style='color:{warna};font-weight:600;'>{row['frp']:.1f} MW</span><br>"
                    f"Confidence: {row['confidence']:.0f}%"
                    f"</div>",
                    max_width=200
                ),
                tooltip=f"FRP: {row['frp']:.1f} MW"
            ).add_to(cluster)
        _tambah_css_dan_legenda(peta)
        return peta
    else:
        return buat_peta_heatmap(df_filtered)