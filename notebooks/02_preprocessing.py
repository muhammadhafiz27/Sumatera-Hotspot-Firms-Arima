# ============================================================
# 02_preprocessing.py
# Tujuan : Preprocessing data NASA FIRMS untuk wilayah Sumatera
# Input  : data/raw/fire_archive_M-C61_758573.csv
#          data/raw/fire_nrt_M-C61_758573.csv
# Output : data/processed/hotspot_sumatera_detail.csv
#          data/processed/hotspot_sumatera_bulanan.csv
# ============================================================

import pandas as pd
import os

ARCHIVE_PATH = "data/raw/fire_archive_M-C61_758573.csv"
NRT_PATH     = "data/raw/fire_nrt_M-C61_758573.csv"
OUTPUT_DIR   = "data/processed"

# ============================================================
# 1. LOAD & GABUNG DATA
# ============================================================
archive = pd.read_csv(ARCHIVE_PATH, low_memory=False)
nrt     = pd.read_csv(NRT_PATH, low_memory=False)

# NRT tidak punya kolom 'type', isi dengan -1 (unknown)
nrt['type'] = -1

df = pd.concat([archive, nrt], ignore_index=True)
print(f"Gabungan awal  : {len(df):,} baris")

# ============================================================
# 2. PARSE TANGGAL & TAMBAH KOLOM TEMPORAL
# ============================================================
df['acq_date']   = pd.to_datetime(df['acq_date'])
df['year']       = df['acq_date'].dt.year
df['month']      = df['acq_date'].dt.month
df['month_name'] = df['acq_date'].dt.strftime('%b')
df['day']        = df['acq_date'].dt.day
df['periode']    = df['acq_date'].dt.to_period('M').astype(str)

# ============================================================
# 3. FILTER CONFIDENCE >= 30
# ============================================================
df['confidence'] = pd.to_numeric(df['confidence'], errors='coerce').fillna(0)
before = len(df)
df = df[df['confidence'] >= 30].copy()
print(f"Filter confidence >= 30: {before:,} → {len(df):,} baris")

# ============================================================
# 4. FILTER TIPE KEBAKARAN
# ============================================================
# type: 0=vegetasi, 2=statis, -1=NRT (dipertahankan), 3=offshore (dibuang)
before = len(df)
df = df[df['type'].isin([0, 2, -1])].copy()
print(f"Filter tipe 0+2+NRT    : {before:,} → {len(df):,} baris")

# ============================================================
# 5. DROP DUPLIKAT
# ============================================================
before = len(df)
df = df.drop_duplicates(subset=['latitude', 'longitude', 'acq_date', 'acq_time'])
print(f"Drop duplikat          : {before:,} → {len(df):,} baris")

# ============================================================
# 6. TAMBAH KOLOM MUSIM & SUMBER DATA
# ============================================================
def get_musim(m):
    return 'Kemarau' if m in [5, 6, 7, 8, 9, 10] else 'Hujan'

df['musim']  = df['month'].apply(get_musim)
df['sumber'] = df['type'].apply(lambda x: 'NRT' if x == -1 else 'Archive')

# ============================================================
# 7. RINGKASAN HASIL
# ============================================================
print(f"\n=== HASIL PREPROCESSING ===")
print(f"Total baris final      : {len(df):,}")
print(f"Rentang waktu          : {df['acq_date'].min().date()} s/d {df['acq_date'].max().date()}")
print(f"\nDistribusi per tahun:")
print(df['year'].value_counts().sort_index().to_string())
print(f"\nDistribusi musim:")
print(df['musim'].value_counts().to_string())

# ============================================================
# 8. AGREGASI BULANAN (untuk ARIMA)
# ============================================================
monthly = (
    df.groupby(['year', 'month', 'musim', 'periode'])
    .agg(
        jumlah_hotspot  = ('latitude', 'count'),
        rata_frp        = ('frp', 'mean'),
        max_frp         = ('frp', 'max'),
        rata_confidence = ('confidence', 'mean')
    )
    .reset_index()
    .sort_values(['year', 'month'])
)

monthly['tanggal']         = pd.to_datetime(monthly['periode'])
monthly['rata_frp']        = monthly['rata_frp'].round(2)
monthly['max_frp']         = monthly['max_frp'].round(2)
monthly['rata_confidence'] = monthly['rata_confidence'].round(1)

print(f"\nAgregasi bulanan ({len(monthly)} bulan)")

# ============================================================
# 9. SIMPAN OUTPUT
# ============================================================
os.makedirs(OUTPUT_DIR, exist_ok=True)

df.to_csv(f"{OUTPUT_DIR}/hotspot_sumatera_detail.csv", index=False)
monthly.to_csv(f"{OUTPUT_DIR}/hotspot_sumatera_bulanan.csv", index=False)

print(f"\nFile tersimpan:")
print(f"  {OUTPUT_DIR}/hotspot_sumatera_detail.csv  ({len(df):,} baris)")
print(f"  {OUTPUT_DIR}/hotspot_sumatera_bulanan.csv ({len(monthly)} baris)")
print("\n=== SELESAI ===")
