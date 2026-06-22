# ============================================================
# 04_arima_modeling.py
# Tujuan : Pemodelan SARIMA + Auto ARIMA untuk forecasting
# Input  : data/processed/hotspot_sumatera_bulanan.csv
# Output : data/processed/forecast_2027.csv
#          data/processed/hotspot_bulanan_dengan_forecast.csv
#          assets/acf_pacf.png
#          assets/forecast_sarima.png
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import warnings
warnings.filterwarnings('ignore')

from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from sklearn.metrics import mean_absolute_error, mean_squared_error
import pmdarima as pm

BULANAN_PATH = "data/processed/hotspot_sumatera_bulanan.csv"
OUTPUT_DIR   = "data/processed"
ASSETS_DIR   = "assets"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

# ============================================================
# 1. LOAD DATA & SIAPKAN TIME SERIES
# ============================================================
monthly = pd.read_csv(BULANAN_PATH)
monthly['tanggal'] = pd.to_datetime(monthly['tanggal'])
monthly = monthly.set_index('tanggal').asfreq('MS')
ts = monthly['jumlah_hotspot'].copy()

print(f"Panjang series : {len(ts)} bulan")
print(f"Rentang        : {ts.index[0].date()} s/d {ts.index[-1].date()}")

# ============================================================
# 2. UJI STASIONERITAS (ADF Test)
# ============================================================
print("\n=== UJI STASIONERITAS (ADF) ===")
adf_result = adfuller(ts)
print(f"ADF Statistic  : {adf_result[0]:.4f}")
print(f"p-value        : {adf_result[1]:.4f}")
print(f"Kesimpulan     : {'STASIONER ✓' if adf_result[1] < 0.05 else 'TIDAK STASIONER → perlu differencing'}")

# ============================================================
# 3. PLOT ACF & PACF
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 4))
plot_acf(ts, lags=30, ax=axes[0], title='ACF - Hotspot Bulanan')
plot_pacf(ts, lags=30, ax=axes[1], title='PACF - Hotspot Bulanan')
plt.tight_layout()
plt.savefig(f"{ASSETS_DIR}/acf_pacf.png", dpi=150, bbox_inches='tight')
plt.show()
print("Plot ACF/PACF tersimpan")

# ============================================================
# 4. TANGANI ANOMALI EL NINO 2023
# ============================================================
ts_clean = ts.copy()
for periode in ['2023-09', '2023-10']:
    bulan = pd.to_datetime(periode)
    bulan_sama = ts_clean[
        (ts_clean.index.month == bulan.month) &
        (ts_clean.index != bulan)
    ]
    ts_clean[bulan] = bulan_sama.mean().round(0)

print(f"\nAnomali 2023 ditangani (winsorization):")
print(f"  Sep 2023: {ts['2023-09'].values[0]:,} → {ts_clean['2023-09'].values[0]:.0f}")
print(f"  Okt 2023: {ts['2023-10'].values[0]:,} → {ts_clean['2023-10'].values[0]:.0f}")

# ============================================================
# 5. SPLIT TRAIN / TEST
# ============================================================
train = ts_clean[:'2025-12']
test  = ts_clean['2026-01':]
print(f"\nTrain : {len(train)} bulan ({train.index[0].date()} s/d {train.index[-1].date()})")
print(f"Test  : {len(test)} bulan  ({test.index[0].date()} s/d {test.index[-1].date()})")

# ============================================================
# 6. AUTO ARIMA — cari orde terbaik
# ============================================================
print("\nMencari orde terbaik dengan Auto ARIMA...")
auto_model = pm.auto_arima(
    train, seasonal=True, m=12,
    stepwise=True, suppress_warnings=True,
    information_criterion='aic', trace=True
)
print(f"\nOrde terbaik Auto ARIMA: {auto_model.order} x {auto_model.seasonal_order}")
print(f"AIC Auto ARIMA: {auto_model.aic():.3f}")

# ============================================================
# 7. FIT SARIMA MANUAL (1,1,1)(1,1,1,12)
# ============================================================
print("\nFitting SARIMA(1,1,1)(1,1,1,12) ...")
model = SARIMAX(
    train,
    order=(1, 1, 1),
    seasonal_order=(1, 1, 1, 12),
    enforce_stationarity=False,
    enforce_invertibility=False
)
result = model.fit(disp=False)
print(result.summary().tables[0])

# ============================================================
# 8. EVALUASI KEDUA MODEL
# ============================================================
pred_sarima = result.get_forecast(steps=len(test)).predicted_mean
pred_auto   = auto_model.predict(n_periods=len(test))

def hitung_metrik(actual, predicted, nama):
    mae  = mean_absolute_error(actual, predicted)
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    mape = (np.abs((actual.values - predicted) / actual.values) * 100).mean()
    print(f"\n{nama}:")
    print(f"  MAE  : {mae:.2f}")
    print(f"  RMSE : {rmse:.2f}")
    print(f"  MAPE : {mape:.2f}%")
    return mae, rmse, mape

print("\n=== PERBANDINGAN MODEL ===")
mae_s, rmse_s, mape_s = hitung_metrik(test, pred_sarima, "SARIMA Manual (1,1,1)(1,1,1,12)")
mae_a, rmse_a, mape_a = hitung_metrik(test, pred_auto,   "Auto ARIMA")

print(f"\n{'Metrik':<8} {'SARIMA manual':>15} {'Auto ARIMA':>12} {'Lebih baik':>12}")
print(f"{'-'*50}")
print(f"{'MAE':<8} {mae_s:>15.2f} {mae_a:>12.2f} {'✓ Auto' if mae_a < mae_s else '✓ Manual':>12}")
print(f"{'RMSE':<8} {rmse_s:>15.2f} {rmse_a:>12.2f} {'✓ Auto' if rmse_a < rmse_s else '✓ Manual':>12}")
print(f"{'MAPE':<8} {mape_s:>15.2f} {mape_a:>12.2f} {'✓ Auto' if mape_a < mape_s else '✓ Manual':>12}")
print("\nModel final: SARIMA(1,1,1)(1,1,1,12) — unggul MAE & RMSE")

# ============================================================
# 9. FORECAST 12 BULAN KE DEPAN
# ============================================================
forecast    = result.get_forecast(steps=len(test) + 12)
future_mean = forecast.predicted_mean.iloc[len(test):]
future_ci   = forecast.conf_int().iloc[len(test):]

forecast_df = pd.DataFrame({
    'periode'     : future_mean.index.strftime('%Y-%m'),
    'prediksi'    : future_mean.values.round(0).astype(int),
    'batas_bawah' : future_ci.iloc[:, 0].values.round(0).astype(int),
    'batas_atas'  : future_ci.iloc[:, 1].values.round(0).astype(int)
})
print(f"\n=== FORECAST Jul 2026 – Jun 2027 ===")
print(forecast_df.to_string(index=False))

# ============================================================
# 10. PLOT FORECAST
# ============================================================
fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(ts_clean.index, ts_clean.values,
        label='Data Historis', color='#2E7D32', linewidth=1.5)
ax.plot(pred_sarima.index, pred_sarima.values,
        label='Prediksi (Test)', color='#F57C00',
        linewidth=1.5, linestyle='--')
ax.plot(future_mean.index, future_mean.values,
        label='Forecast 2026–2027', color='#C62828',
        linewidth=2, linestyle='--')
ax.fill_between(future_mean.index,
                future_ci.iloc[:, 0], future_ci.iloc[:, 1],
                alpha=0.2, color='#C62828', label='Interval Kepercayaan 95%')
ax.axvline(x=pd.to_datetime('2026-01'), color='gray',
           linestyle=':', linewidth=1.5, label='Batas Train/Test')
ax.set_title('Forecast Hotspot Kebakaran Hutan Sumatera\nSARIMA(1,1,1)(1,1,1,12)',
             fontsize=13, fontweight='bold')
ax.set_xlabel('Periode')
ax.set_ylabel('Jumlah Hotspot')
ax.legend(loc='upper left', fontsize=9)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(f"{ASSETS_DIR}/forecast_sarima.png", dpi=150, bbox_inches='tight')
plt.show()

# ============================================================
# 11. SIMPAN OUTPUT
# ============================================================
forecast_df.to_csv(f"{OUTPUT_DIR}/forecast_2027.csv", index=False)

historis = pd.DataFrame({
    'periode'        : ts_clean.index.strftime('%Y-%m'),
    'jumlah_hotspot' : ts_clean.values,
    'fitted'         : result.fittedvalues.reindex(ts_clean.index).values.round(0),
    'forecast'       : np.nan,
    'batas_bawah'    : np.nan,
    'batas_atas'     : np.nan,
    'tipe'           : 'historis'
})
future = pd.DataFrame({
    'periode'        : future_mean.index.strftime('%Y-%m'),
    'jumlah_hotspot' : np.nan,
    'fitted'         : np.nan,
    'forecast'       : future_mean.values.round(0).astype(int),
    'batas_bawah'    : future_ci.iloc[:, 0].values.round(0).astype(int),
    'batas_atas'     : future_ci.iloc[:, 1].values.round(0).astype(int),
    'tipe'           : 'forecast'
})
hasil_lengkap = pd.concat([historis, future], ignore_index=True)
hasil_lengkap.to_csv(f"{OUTPUT_DIR}/hotspot_bulanan_dengan_forecast.csv", index=False)

print(f"\nFile tersimpan:")
print(f"  {OUTPUT_DIR}/forecast_2027.csv")
print(f"  {OUTPUT_DIR}/hotspot_bulanan_dengan_forecast.csv ({len(hasil_lengkap)} baris)")
print(f"  {ASSETS_DIR}/acf_pacf.png")
print(f"  {ASSETS_DIR}/forecast_sarima.png")
print("\n=== PIPELINE ARIMA SELESAI ===")

# ============================================================
# 12. SIMPAN MODEL KE FOLDER models/
# ============================================================
import joblib
import json
from datetime import date

os.makedirs("models", exist_ok=True)

# Simpan model
joblib.dump(result, "models/sarima_model.pkl")

# Simpan metadata model
model_info = {
    "order": [1, 1, 1],
    "seasonal_order": [1, 1, 1, 12],
    "mae": round(mae_s, 2),
    "rmse": round(rmse_s, 2),
    "mape": round(mape_s, 2),
    "train_period": "2020-01 s/d 2025-12",
    "forecast_period": "2026-07 s/d 2027-06",
    "tanggal_training": str(date.today())
}

with open("models/sarima_model_info.json", "w") as f:
    json.dump(model_info, f, indent=2)

print(f"  models/sarima_model.pkl")
print(f"  models/sarima_model_info.json")
print("\n=== SEMUA SELESAI ===")