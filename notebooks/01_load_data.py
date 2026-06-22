# ============================================================
# 01_load_data.py
# Tujuan : Load dan eksplorasi awal dataset NASA FIRMS
# Input  : data/raw/fire_archive_M-C61_758573.csv
#          data/raw/fire_nrt_M-C61_758573.csv
# ============================================================

import pandas as pd

# Sesuaikan path ke lokasi file CSV kamu
ARCHIVE_PATH = "data/raw/fire_archive_M-C61_758573.csv"
NRT_PATH     = "data/raw/fire_nrt_M-C61_758573.csv"

# Load kedua file
archive = pd.read_csv(ARCHIVE_PATH, low_memory=False)
nrt     = pd.read_csv(NRT_PATH, low_memory=False)

for nama, df in [("ARCHIVE", archive), ("NRT", nrt)]:
    df['acq_date'] = pd.to_datetime(df['acq_date'])
    print(f"\n--- {nama} ---")
    print(f"Total baris   : {len(df):,}")
    print(f"Rentang waktu : {df['acq_date'].min().date()} s/d {df['acq_date'].max().date()}")
    print(f"Tahun unik    : {sorted(df['acq_date'].dt.year.unique().tolist())}")
    print(f"Kolom         : {list(df.columns)}")
    print(f"Missing values:\n{df.isnull().sum()[df.isnull().sum() > 0]}")
