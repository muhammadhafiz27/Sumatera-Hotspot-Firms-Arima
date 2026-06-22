# ============================================================
# 03_eda.py
# Tujuan : Exploratory Data Analysis hotspot Sumatera
# Input  : data/processed/hotspot_sumatera_bulanan.csv
# Output : assets/eda_hotspot_sumatera.png
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import warnings
warnings.filterwarnings('ignore')
import os

BULANAN_PATH = "data/processed/hotspot_sumatera_bulanan.csv"
OUTPUT_DIR   = "assets"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load data bulanan
monthly = pd.read_csv(BULANAN_PATH)
monthly['tanggal'] = pd.to_datetime(monthly['tanggal'])

# ============================================================
# PLOT 1-3: EDA Tiga Panel
# ============================================================
fig, axes = plt.subplots(3, 1, figsize=(14, 12))
fig.suptitle('EDA Hotspot Kebakaran Hutan Sumatera 2020–2026',
             fontsize=14, fontweight='bold')

legend_elements = [
    mpatches.Patch(facecolor='#E07B39', label='Kemarau'),
    mpatches.Patch(facecolor='#4A90D9', label='Hujan')
]

# --- Plot 1: Tren bulanan ---
ax1 = axes[0]
colors = ['#E07B39' if m == 'Kemarau' else '#4A90D9' for m in monthly['musim']]
ax1.bar(monthly['tanggal'], monthly['jumlah_hotspot'],
        color=colors, width=25, alpha=0.85)
ax1.set_title('Jumlah Hotspot per Bulan')
ax1.set_ylabel('Jumlah Hotspot')

# Annotasi anomali El Nino 2023
idx_max = monthly['jumlah_hotspot'].idxmax()
ax1.annotate(
    f"El Niño 2023\n{monthly.loc[idx_max,'jumlah_hotspot']:,}",
    xy=(monthly.loc[idx_max,'tanggal'], monthly.loc[idx_max,'jumlah_hotspot']),
    xytext=(monthly.loc[idx_max,'tanggal'], monthly.loc[idx_max,'jumlah_hotspot'] + 200),
    fontsize=8, ha='center', color='red',
    arrowprops=dict(arrowstyle='->', color='red', lw=1)
)
ax1.legend(handles=legend_elements, loc='upper left', fontsize=8)

# --- Plot 2: Total per tahun ---
ax2 = axes[1]
yearly = monthly.groupby('year')['jumlah_hotspot'].sum().reset_index()
bars = ax2.bar(yearly['year'], yearly['jumlah_hotspot'],
               color='#2E7D32', alpha=0.8, width=0.6)
ax2.set_title('Total Hotspot per Tahun')
ax2.set_ylabel('Jumlah Hotspot')
ax2.set_xlabel('Tahun')
for bar, val in zip(bars, yearly['jumlah_hotspot']):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
             f'{val:,}', ha='center', va='bottom', fontsize=8)

# --- Plot 3: Rata-rata per bulan (pola musiman) ---
ax3 = axes[2]
seasonal = monthly.groupby('month')['jumlah_hotspot'].mean().reset_index()
month_names = ['Jan','Feb','Mar','Apr','Mei','Jun',
               'Jul','Agu','Sep','Okt','Nov','Des']
seasonal_colors = ['#E07B39' if m in [5,6,7,8,9,10] else '#4A90D9'
                   for m in seasonal['month']]
ax3.bar(range(1,13), seasonal['jumlah_hotspot'],
        color=seasonal_colors, alpha=0.85)
ax3.set_xticks(range(1,13))
ax3.set_xticklabels(month_names)
ax3.set_title('Rata-rata Hotspot per Bulan (Pola Musiman)')
ax3.set_ylabel('Rata-rata Hotspot')
ax3.set_xlabel('Bulan')
ax3.legend(handles=legend_elements, loc='upper left', fontsize=8)

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/eda_hotspot_sumatera.png", dpi=150, bbox_inches='tight')
plt.show()

# ============================================================
# STATISTIK DESKRIPTIF
# ============================================================
print("\n=== STATISTIK DESKRIPTIF ===")
print(f"Rata-rata hotspot/bulan : {monthly['jumlah_hotspot'].mean():.0f}")
print(f"Median hotspot/bulan    : {monthly['jumlah_hotspot'].median():.0f}")
print(f"Bulan tertinggi         : {monthly.loc[monthly['jumlah_hotspot'].idxmax(), 'periode']} ({monthly['jumlah_hotspot'].max():,})")
print(f"Bulan terendah          : {monthly.loc[monthly['jumlah_hotspot'].idxmin(), 'periode']} ({monthly['jumlah_hotspot'].min():,})")
print(f"\nRata-rata per musim:")
print(monthly.groupby('musim')['jumlah_hotspot'].mean().round(1).to_string())
print(f"\nPlot tersimpan: {OUTPUT_DIR}/eda_hotspot_sumatera.png")
