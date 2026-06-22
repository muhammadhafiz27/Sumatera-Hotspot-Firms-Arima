# ============================================================
# utils.py
# Fungsi bantuan: load data, filter, format
# ============================================================

import pandas as pd
import numpy as np
import joblib
import json
import streamlit as st


# ============================================================
# LOAD DATA (dengan cache agar tidak load berulang)
# ============================================================

@st.cache_data
def load_detail():
    """Load data detail per titik hotspot."""
    df = pd.read_csv("data/processed/hotspot_sumatera_detail.csv", low_memory=False)
    df['acq_date'] = pd.to_datetime(df['acq_date'])
    return df


@st.cache_data
def load_bulanan():
    """Load data agregasi bulanan."""
    df = pd.read_csv("data/processed/hotspot_sumatera_bulanan.csv")
    df['tanggal'] = pd.to_datetime(df['tanggal'])
    return df


@st.cache_data
def load_forecast():
    """Load data forecast SARIMA."""
    df = pd.read_csv("data/processed/hotspot_bulanan_dengan_forecast.csv")
    df['tanggal'] = pd.to_datetime(df['periode'])
    return df


@st.cache_resource
def load_model():
    """Load model SARIMA tersimpan."""
    return joblib.load("models/sarima_model.pkl")


def load_model_info():
    """Load metadata model SARIMA."""
    with open("models/sarima_model_info.json", "r") as f:
        return json.load(f)


# ============================================================
# FILTER DATA
# ============================================================

def filter_detail(df, tahun_range, musim=None, min_confidence=30):
    """Filter data detail berdasarkan tahun, musim, dan confidence."""
    mask = (
        (df['year'] >= tahun_range[0]) &
        (df['year'] <= tahun_range[1]) &
        (df['confidence'] >= min_confidence)
    )
    if musim and musim != "Semua":
        mask &= (df['musim'] == musim)
    return df[mask].copy()


def filter_bulanan(df, tahun_range, musim=None):
    """Filter data bulanan berdasarkan tahun dan musim."""
    mask = (
        (df['year'] >= tahun_range[0]) &
        (df['year'] <= tahun_range[1])
    )
    if musim and musim != "Semua":
        mask &= (df['musim'] == musim)
    return df[mask].copy()


# ============================================================
# FORMAT & HELPER
# ============================================================

def format_angka(n):
    """Format angka dengan pemisah ribuan."""
    return f"{int(n):,}"


def get_warna_frp(frp):
    """Warna marker berdasarkan intensitas FRP."""
    if frp >= 100:
        return "#8B0000"   # merah tua — sangat tinggi
    elif frp >= 50:
        return "#FF4500"   # oranye merah — tinggi
    elif frp >= 20:
        return "#FF8C00"   # oranye — sedang
    else:
        return "#FFD700"   # kuning — rendah


def get_radius_frp(frp):
    """Radius marker berdasarkan FRP."""
    if frp >= 100:
        return 8
    elif frp >= 50:
        return 6
    elif frp >= 20:
        return 4
    else:
        return 3


def statistik_ringkas(df):
    """Hitung statistik ringkas dari data detail."""
    return {
        "total_hotspot"   : len(df),
        "rata_frp"        : round(df['frp'].mean(), 2),
        "max_frp"         : round(df['frp'].max(), 2),
        "rata_confidence" : round(df['confidence'].mean(), 1),
    }
