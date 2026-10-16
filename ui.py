"""Komponen antarmuka bersama untuk aplikasi AyatQu."""

from html import escape
from pathlib import Path
import json

import pandas as pd
import streamlit as st

from ayatqu_core import AyatQu, FOOTNOTE

ROOT = Path(__file__).resolve().parent

NAMA = "Kayla Verda Fawnia Heses"
NIM = "A11.2024.15689"
PRODI = "Teknik Informatika"
MATA_KULIAH = "Sistem Temu Kembali Informasi"
UNIVERSITAS = "Universitas Dian Nuswantoro"
TAHUN = "2026"
DOSEN = "Junta Zeniarja, M.Kom"
STREAMLIT_URL = ""


def load_css():
    """Memuat gaya tema, komponen, dan tampilan responsif."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Inter:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700&display=swap');
        :root {
          --ayq-emerald: #0f766e;
          --ayq-deep: #115e59;
          --ayq-gold: #d4a017;
          --ayq-text: var(--text-color);
          --ayq-surface: color-mix(in srgb, var(--secondary-background-color) 92%, var(--ayq-emerald));
          --ayq-border: color-mix(in srgb, var(--text-color) 14%, transparent);
        }
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
        .stApp { background: var(--background-color); }
        .block-container { max-width: 1180px; padding-top: 2rem; padding-bottom: 1rem; }
        .stApp header[data-testid="stHeader"] {
          z-index: 1000; background: rgba(255, 255, 255, .86) !important;
          border-bottom: 1px solid rgba(255, 255, 255, .75); box-shadow: 0 5px 20px rgba(23, 61, 58, .1);
          backdrop-filter: blur(18px) saturate(150%); -webkit-backdrop-filter: blur(18px) saturate(150%);
        }
        [data-testid="stToolbar"] > div:first-child { align-items: center; }
        [data-testid="stToolbar"] > div:first-child::before {
          content: "AyatQu"; flex: 0 0 auto; margin: 0 1.1rem 0 .85rem; color: var(--ayq-emerald);
          font-family: 'Playfair Display', Georgia, serif; font-size: 1.45rem; font-weight: 700; white-space: nowrap;
        }
        @media (min-width: 701px) {
          [data-testid="stToolbar"] .rc-overflow { margin-left: clamp(7rem, 15vw, 14rem); }
        }
        [data-testid="stTopNavLink"] { margin: .1rem .12rem; padding: .48rem .72rem; border-radius: 10px;
          color: var(--ayq-text) !important; font-weight: 600; transition: background-color .18s ease, color .18s ease; }
        [data-testid="stTopNavLink"]:hover { background: color-mix(in srgb, var(--ayq-emerald) 9%, var(--background-color)); }
        [data-testid="stTopNavLink"][aria-current="page"] { background: color-mix(in srgb, var(--ayq-emerald) 13%, var(--background-color));
          color: var(--ayq-emerald) !important; }
        .ayq-hero {
          position: relative; overflow: hidden; padding: 1.55rem 1.8rem; margin: 0.25rem 0 1.4rem;
          color: #f3fffc; border: 1px solid rgba(255,255,255,.18); border-radius: 16px;
          background: linear-gradient(115deg, #0f766e 0%, #115e59 68%, #173f3d 100%);
          box-shadow: 0 12px 34px rgba(15,118,110,.16);
        }
        .ayq-hero:after { content: ''; position: absolute; right: -44px; top: -76px; width: 210px; height: 210px;
          border: 1px solid rgba(255,255,255,.14); border-radius: 50%; box-shadow: 0 0 0 25px rgba(255,255,255,.035), 0 0 0 52px rgba(255,255,255,.025); }
        .ayq-hero h1 { margin: 0; font-size: 2rem; color: #fff; }
        .ayq-hero p { margin: .45rem 0 0; color: rgba(255,255,255,.84); max-width: 760px; }
        .ayq-kicker { display: inline-block; color: #f7d77c; font-size: .76rem; font-weight: 700; margin-bottom: .45rem; }
        .ayq-card { padding: 1rem 1.15rem; margin: .55rem 0; border: 1px solid var(--ayq-border); border-left: 3px solid var(--ayq-gold);
          border-radius: 14px; background: var(--ayq-surface); box-shadow: 0 5px 18px rgba(15, 40, 38, .06); }
        .ayq-card-label { color: var(--ayq-emerald); font-size: .84rem; font-weight: 700; }
        .ayq-arab { margin: .65rem 0; color: var(--ayq-text); font-family: 'Amiri', 'Traditional Arabic', serif;
          font-size: 2.15rem; line-height: 1.85; direction: rtl; text-align: right; overflow-wrap: anywhere; }
        .ayq-translation { color: var(--ayq-text); line-height: 1.75; }
        .ayq-chip { display: inline-block; padding: .28rem .62rem; margin: .18rem .2rem .18rem 0; border-radius: 999px;
          color: var(--ayq-emerald); background: color-mix(in srgb, var(--ayq-emerald) 12%, var(--secondary-background-color));
          border: 1px solid color-mix(in srgb, var(--ayq-emerald) 24%, transparent); font-size: .8rem; font-weight: 600; }
        .ayq-note { padding: .85rem 1rem; border-radius: 12px; border: 1px solid var(--ayq-border); background: var(--ayq-surface); }
        .ayq-footer { margin-top: 2.4rem; padding: 1rem .25rem .4rem; border-top: 1px solid var(--ayq-border);
          text-align: center; color: color-mix(in srgb, var(--text-color) 72%, transparent); font-size: .78rem; line-height: 1.7; }
        .ayq-footer strong { color: var(--ayq-emerald); }
        .ayq-section { padding-top: .25rem; }
        @media (max-width: 700px) {
          .block-container { padding: 1rem .8rem 1rem; }
          .ayq-hero { padding: 1.2rem 1.1rem; border-radius: 14px; }
          .ayq-hero h1 { font-size: 1.55rem; }
          .ayq-card { padding: .85rem .9rem; }
          .ayq-arab { font-size: 1.7rem; }
          [role="tablist"] { flex-wrap: wrap !important; overflow-x: visible !important; height: auto !important; gap: .25rem .4rem; }
          [role="tablist"] > [role="tab"] { flex: 0 0 auto !important; white-space: normal !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def load_landing_css():
    """Memuat gaya khusus halaman Beranda tanpa mengubah halaman lain."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700&display=swap');
        .stApp:has(.ayq-landing) {
          --landing-ink: var(--text-color);
          --landing-muted: color-mix(in srgb, var(--text-color) 74%, transparent);
          --landing-surface: color-mix(in srgb, var(--secondary-background-color) 90%, transparent);
          background: linear-gradient(128deg, color-mix(in srgb, var(--secondary-background-color) 60%, #b9e5d8),
            color-mix(in srgb, var(--background-color) 90%, #f4d879));
        }
        .ayq-landing { height: 0; }
        .ayq-home-badges { display: flex; flex-wrap: wrap; gap: .5rem; margin: .2rem 0 1.15rem; }
        .ayq-home-badge { padding: .32rem .68rem; border-radius: 999px; color: var(--ayq-emerald);
          background: color-mix(in srgb, var(--ayq-emerald) 10%, var(--secondary-background-color));
          border: 1px solid color-mix(in srgb, var(--ayq-emerald) 20%, transparent); font-size: .74rem; font-weight: 700; }
        .ayq-home-title { max-width: 740px; margin: 0; color: var(--landing-ink) !important; font-family: 'Playfair Display', Georgia, serif !important;
          font-size: 1.65rem !important; font-weight: 600; line-height: 1.16; }
        .ayq-home-title .ayq-title-green { color: #0f766e; }
        .ayq-home-title .ayq-title-gold { color: #a77800; }
        .ayq-home-copy { max-width: 630px; margin: 1.1rem 0 1.35rem; color: var(--landing-muted); font-size: 1.03rem; line-height: 1.8; }
        .ayq-home-actions { margin-top: .25rem; }
        .stApp:has(.ayq-landing) div[data-testid="stButton"] button { min-height: 2.9rem; border-radius: 999px; font-weight: 700; }
        .stApp:has(.ayq-landing) div[data-testid="stButton"] button[kind="primary"] {
          background: #0f766e; border-color: #0f766e; color: #fff; box-shadow: 0 7px 18px rgba(15,118,110,.2); }
        .stApp:has(.ayq-landing) div[data-testid="stButton"] button[kind="secondary"] {
          background: color-mix(in srgb, var(--background-color) 72%, transparent); border: 1px solid #0f766e; color: var(--landing-ink); }
        .ayq-preview-stack { position: relative; padding: .5rem 0 .6rem .5rem; }
        .ayq-float-card { position: relative; z-index: 1; margin: .75rem 0; padding: 1rem 1.05rem; border: 1px solid color-mix(in srgb, var(--text-color) 12%, transparent);
          border-radius: 16px; background: var(--landing-surface); backdrop-filter: blur(12px); box-shadow: 0 14px 36px rgba(25,61,54,.12);
          animation: ayq-drift 6s ease-in-out infinite; }
        .ayq-float-card:nth-child(2) { margin-left: 1.65rem; animation-delay: -1.8s; }
        .ayq-float-card:nth-child(3) { margin-right: 1.2rem; animation-delay: -3.2s; }
        .ayq-float-title { margin-bottom: .65rem; color: var(--ayq-emerald); font-size: .82rem; font-weight: 800; }
        .ayq-query-sample { margin-bottom: .6rem; padding: .5rem .7rem; border-radius: 9px; color: var(--landing-muted); background: color-mix(in srgb, var(--secondary-background-color) 78%, transparent); font-size: .8rem; }
        .ayq-result-row { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: .5rem; align-items: center; margin: .45rem 0; color: var(--landing-ink); font-size: .78rem; }
        .ayq-score-track { grid-column: 1 / -1; height: 5px; overflow: hidden; border-radius: 99px; background: color-mix(in srgb, var(--text-color) 10%, transparent); }
        .ayq-score-fill { display: block; height: 100%; border-radius: inherit; background: linear-gradient(90deg, #0f766e, #61b99e); }
        .ayq-data-chips { display: flex; flex-wrap: wrap; gap: .35rem; }
        .ayq-data-chip { display: inline-block; max-width: 100%; padding: .28rem .55rem; border-radius: 999px; color: var(--landing-ink);
          background: color-mix(in srgb, var(--ayq-gold) 16%, var(--secondary-background-color)); font-size: .72rem; overflow-wrap: anywhere; }
        .ayq-preview-note { color: var(--landing-muted); font-size: .76rem; line-height: 1.55; }
        .ayq-ndcg-row { display: grid; grid-template-columns: minmax(90px, 1fr) 1.25fr auto; gap: .55rem; align-items: center; margin: .48rem 0; color: var(--landing-ink); font-size: .72rem; }
        .ayq-ndcg-track { height: 7px; overflow: hidden; border-radius: 99px; background: color-mix(in srgb, var(--text-color) 10%, transparent); }
        .ayq-ndcg-fill { display: block; height: 100%; border-radius: inherit; background: #d4a017; }
        .ayq-draft-label { display: inline-block; margin-top: .45rem; padding: .2rem .48rem; border-radius: 999px; color: #765400;
          background: color-mix(in srgb, #d4a017 22%, var(--secondary-background-color)); font-size: .68rem; font-weight: 700; }
        .ayq-book-orbit { position: absolute; z-index: 2; top: 37%; right: -.25rem; display: grid; place-items: center; width: 3.4rem; aspect-ratio: 1;
          border: 4px solid color-mix(in srgb, var(--background-color) 80%, transparent); border-radius: 50%; background: #0f766e;
          box-shadow: 0 10px 24px rgba(15,118,110,.25); font-size: 1.5rem; }
        .ayq-stat-card { min-height: 112px; padding: .95rem 1rem; border: 1px solid color-mix(in srgb, var(--text-color) 10%, transparent);
          border-radius: 14px; background: var(--landing-surface); box-shadow: 0 8px 24px rgba(25,61,54,.07); }
        .ayq-stat-label { color: var(--landing-muted); font-size: .75rem; font-weight: 700; }
        .ayq-stat-value { margin-top: .42rem; color: var(--ayq-emerald); font-size: 1.18rem; font-weight: 800; line-height: 1.35; overflow-wrap: anywhere; }
        .ayq-home-section { margin: 3rem 0 1rem; color: var(--landing-ink); font: 600 1.8rem/1.2 'Playfair Display', Georgia, serif; }
        .ayq-info-card { height: 100%; min-height: 142px; padding: 1.15rem; border: 1px solid color-mix(in srgb, var(--text-color) 10%, transparent);
          border-radius: 16px; background: var(--landing-surface); box-shadow: 0 8px 24px rgba(25,61,54,.07); }
        .ayq-step-number { display: grid; place-items: center; width: 2rem; height: 2rem; margin-bottom: .8rem; border-radius: 50%;
          color: #fff; background: #0f766e; font-weight: 800; }
        .ayq-info-title { margin-bottom: .4rem; color: var(--landing-ink); font-weight: 800; }
        .ayq-info-copy { color: var(--landing-muted); font-size: .88rem; line-height: 1.65; }
        .ayq-home-cta { margin-top: 2.8rem; padding: 1.5rem; border-radius: 16px; background: color-mix(in srgb, var(--ayq-emerald) 10%, var(--secondary-background-color)); }
        .ayq-home-cta-title { margin-bottom: .35rem; color: var(--landing-ink); font: 600 1.55rem/1.3 'Playfair Display', Georgia, serif; }
        .ayq-byline { margin-top: 1rem; color: var(--landing-muted); font-size: .78rem; text-align: center; line-height: 1.8; }
        @keyframes ayq-drift { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
        @media (min-width: 701px) {
          .stApp:has(.ayq-landing) .block-container { max-width: 1400px; }
          .ayq-home-title { font-size: 2.75rem !important; line-height: 1.12; }
          .ayq-home-copy { max-width: 760px; font-size: 1.2rem !important; }
          .ayq-home-section { font-size: 2.1rem !important; }
          .ayq-home-badge { font-size: .82rem; }
          .ayq-float-title { font-size: .92rem; }
          .ayq-query-sample { font-size: .9rem; }
          .ayq-result-row { font-size: .88rem; }
          .ayq-data-chip { font-size: .8rem; }
          .ayq-preview-note { font-size: .84rem; }
          .ayq-ndcg-row { font-size: .8rem; }
          .ayq-draft-label { font-size: .76rem; }
          .ayq-stat-label { font-size: .82rem; }
          .ayq-stat-value { font-size: 1.3rem; }
          .ayq-info-copy { font-size: .96rem; }
          .stApp:has(.ayq-landing) div[data-testid="stButton"] button { font-size: 1.05rem !important; }
        }
        @media (max-width: 700px) {
          .ayq-home-title { font-size: 1.3rem !important; }
          .ayq-home-copy { font-size: .94rem; }
          .ayq-preview-stack { padding: 0; }
          .ayq-float-card, .ayq-float-card:nth-child(2), .ayq-float-card:nth-child(3) { margin: .7rem 0; animation: none; }
          .ayq-book-orbit { top: 31%; right: .35rem; }
          .ayq-stat-card { min-height: 96px; }
          .ayq-home-section { margin-top: 2.25rem; }
          .stApp:has(.ayq-landing) div[data-testid="stButton"] { width: 100%; }
        }
        @media (prefers-reduced-motion: reduce) {
          .ayq-float-card { animation: none; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_engine():
    """Memuat mesin pencarian sekali per proses Streamlit."""
    return _load_engine()


@st.cache_resource(show_spinner="Menyiapkan indeks AyatQu...")
def _load_engine():
    return AyatQu(root=ROOT)


@st.cache_data(show_spinner=False)
def load_csv(relative_path):
    """Membaca CSV bila tersedia dan mengembalikan None untuk file bermasalah."""
    path = _resolve_path(relative_path)
    if not path.is_file() or path.stat().st_size == 0:
        return None
    try:
        return pd.read_csv(path, encoding="utf-8-sig")
    except (
        OSError,
        UnicodeError,
        pd.errors.EmptyDataError,
        pd.errors.ParserError,
        ValueError,
    ):
        return None


@st.cache_data(show_spinner=False)
def load_json(relative_path):
    """Membaca JSON bila tersedia dan mengembalikan None untuk file bermasalah."""
    path = _resolve_path(relative_path)
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None


def _resolve_path(relative_path):
    path = Path(relative_path)
    return path if path.is_absolute() else ROOT / path


def render_header(judul, subjudul):
    """Menampilkan banner halaman dengan teks yang sudah di-escape."""
    st.markdown(
        f'<header class="ayq-hero"><span class="ayq-kicker">AyatQu</span>'
        f"<h1>{escape(str(judul))}</h1><p>{escape(str(subjudul))}</p></header>",
        unsafe_allow_html=True,
    )


def render_ayat_card(engine, hit):
    """Menampilkan teks ayat asli dengan escape untuk seluruh isi data."""
    verse = engine.verse(int(hit["id"]))
    label = f"QS. {verse['surah_nama']} {verse['surah_no']}:{verse['ayat_no']}"
    st.markdown(
        f'<article class="ayq-card"><div class="ayq-card-label">{escape(label)}</div>'
        f'<div class="ayq-arab">{escape(str(verse["teks_arab"]))}</div>'
        f'<div class="ayq-translation">{escape(str(verse["terjemahan"]))}</div></article>',
        unsafe_allow_html=True,
    )


def render_footer():
    """Menampilkan batas penggunaan dan sumber data aplikasi."""
    st.markdown(
        f'<footer class="ayq-footer"><strong>{escape(FOOTNOTE)}</strong><br>'
        "Sumber data Tanzil.net</footer>",
        unsafe_allow_html=True,
    )


