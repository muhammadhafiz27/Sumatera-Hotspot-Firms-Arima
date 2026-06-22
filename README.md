# 🔥 Hotspot Sumatera Dashboard
### Visualisasi Spasio-Temporal Kebakaran Hutan dan Lahan di Pulau Sumatera

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?logo=streamlit&logoColor=white)
![NASA FIRMS](https://img.shields.io/badge/Data-NASA%20FIRMS-0B3D91?logo=nasa&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

Aplikasi visualisasi interaktif sebaran titik panas (*hotspot*) kebakaran hutan dan lahan di Pulau Sumatera menggunakan data satelit MODIS NASA FIRMS, dilengkapi forecasting SARIMA untuk proyeksi 12 bulan ke depan.

> 📚 Tugas Akhir Mata Kuliah **Visualisasi Data Spasio-Temporal** — Universitas Andalas

---

## ✨ Fitur Utama

| Fitur | Deskripsi |
|-------|-----------|
| 🗺️ **Peta Heatmap** | Visualisasi kepadatan hotspot berbasis FRP per km² |
| 📅 **Time Series Interaktif** | Animasi persebaran hotspot per bulan dengan slider waktu |
| 🔮 **Forecast Peta** | Bubble prediksi per provinsi berdasarkan model SARIMA |
| 🔵 **Cluster Geografis** | Pengelompokan otomatis hotspot berdasarkan kedekatan lokasi |
| 📊 **Analisis Temporal** | Grafik tren bulanan, tahunan, musiman, dan distribusi FRP |
| 📈 **Forecast SARIMA** | Proyeksi 12 bulan ke depan dengan interval kepercayaan 95% |
| ⚙️ **Filter Dinamis** | Rentang tahun, musim, dan minimum confidence yang reaktif |

---

## 🖼️ Tampilan Aplikasi

> *Screenshot dashboard dapat ditambahkan di sini setelah deployment.*

---

## 🗂️ Struktur Folder

```
sumatera-hotspot-firms-arima/
├── data/
│   ├── raw/                              # File CSV mentah dari NASA FIRMS
│   │   ├── fire_archive_M-C61_758573.csv
│   │   └── fire_nrt_M-C61_758573.csv
│   └── processed/                        # Output hasil preprocessing
│       ├── hotspot_sumatera_detail.csv
│       ├── hotspot_sumatera_bulanan.csv
│       ├── hotspot_bulanan_dengan_forecast.csv
│       └── forecast_2027.csv
├── notebooks/                            # Pipeline analisis (jalankan berurutan)
│   ├── 01_load_data.py
│   ├── 02_preprocessing.py
│   ├── 03_eda.py
│   └── 04_arima_modeling.py
├── app/                                  # Aplikasi Streamlit
│   ├── main.py                           # Entry point utama
│   ├── map_component.py                  # Komponen peta Folium
│   ├── forecast_component.py             # Komponen grafik SARIMA
│   ├── charts.py                         # Grafik EDA Plotly
│   └── utils.py                          # Fungsi bantuan & loader data
├── models/                               # Model SARIMA tersimpan
├── assets/                               # Output plot EDA & forecast
├── requirements.txt
└── README.md
```

---

## ⚙️ Instalasi

### Prasyarat
- Python 3.9 atau lebih baru
- pip

### Langkah Instalasi

```bash
# 1. Clone repositori
git clone https://github.com/username/sumatera-hotspot-firms-arima.git
cd sumatera-hotspot-firms-arima

# 2. (Opsional) Buat virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Salin file CSV ke folder data/raw/
#    Download dari: https://firms.modaps.eosdis.nasa.gov/
#    - fire_archive_M-C61_758573.csv
#    - fire_nrt_M-C61_758573.csv
```

---

## 🚀 Cara Menjalankan

### Langkah 1 — Jalankan pipeline preprocessing & modeling

```bash
# Jalankan dari folder root proyek, secara berurutan
python notebooks/01_load_data.py
python notebooks/02_preprocessing.py
python notebooks/03_eda.py
python notebooks/04_arima_modeling.py
```

> ⏱️ Proses `04_arima_modeling.py` membutuhkan beberapa menit karena fitting SARIMA dan Auto ARIMA.

### Langkah 2 — Jalankan aplikasi Streamlit

```bash
streamlit run app/main.py
```

Aplikasi akan terbuka otomatis di browser pada `http://localhost:8501`.

---

## 📦 Dataset

| Atribut | Detail |
|---------|--------|
| **Sumber** | [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/) — Fire Information for Resource Management System |
| **Instrumen** | MODIS Collection 6.1 + VIIRS S-NPP (NRT) |
| **Wilayah** | Pulau Sumatera, Indonesia |
| **Rentang Waktu** | Januari 2020 – Juni 2026 (78 bulan) |
| **Total Data Mentah** | 47.494 baris |
| **Setelah Preprocessing** | 41.677 titik hotspot |

### Tahapan Preprocessing

1. **Merge** data arsip dan near-real-time (NRT)
2. **Filter confidence** ≥ 30% (standar deteksi MODIS)
3. **Filter tipe** — hanya vegetasi (0), statis (2), dan NRT (-1)
4. **Drop duplikat** berdasarkan koordinat, tanggal, dan waktu akuisisi
5. **Penanganan anomali** — winsorizing Sep–Okt 2023 (El Niño)
6. **Agregasi bulanan** untuk pemodelan SARIMA

---

## 🤖 Model Forecasting

| Atribut | Detail |
|---------|--------|
| **Model** | SARIMA(1,1,1)(1,1,1,12) |
| **Library** | `statsmodels` |
| **Data Train** | Januari 2020 – Desember 2025 (72 bulan) |
| **Data Test** | Januari 2026 – Juni 2026 (6 bulan) |
| **Forecast** | Juli 2026 – Juni 2027 (12 bulan) |
| **Pemilihan Orde** | Auto ARIMA berbasis AIC (stepwise search) |

### Metrik Evaluasi

| Metrik | SARIMA Manual | Auto ARIMA | Terbaik |
|--------|:-------------:|:----------:|:-------:|
| MAE | **268** | 277 | ✅ Manual |
| RMSE | **360** | 386 | ✅ Manual |
| MAPE | 112.84% | **109.48%** | ✅ Auto |

> ℹ️ MAPE tinggi disebabkan nilai aktual yang mendekati nol di musim hujan, sehingga error relatif membesar secara proporsional. MAE dan RMSE lebih representatif untuk dataset ini.

---

## 🛠️ Tech Stack

| Komponen | Library |
|----------|---------|
| Dashboard | `streamlit` |
| Peta Interaktif | `folium`, `streamlit-folium` |
| Visualisasi | `plotly`, `matplotlib` |
| Pemodelan | `statsmodels`, `pmdarima` |
| Data Processing | `pandas`, `numpy` |
| ML Metrics | `scikit-learn` |

---

## 📄 Lisensi

Proyek ini dibuat untuk keperluan akademik. Data bersumber dari NASA FIRMS yang bersifat publik.

© NASA FIRMS · MODIS Collection 6.1 & VIIRS S-NPP

---

<div align="center">
    <sub>Muhammad Hafiz</sub><br>
    <sub>2311532007</sub><br>
    <sub>Tugas Akhir Mata Kuliah Visualisasi Data Spasio-Temporal</sub><br>
    <sub>Universitas Andalas</sub>
</div>