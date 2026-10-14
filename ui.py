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
GITHUB_URL = ""


def load_css():
    """Memuat gaya tema, komponen, dan tampilan responsif."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Inter:wght@400;500;600;700;800&display=swap');
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
        [data-testid="stSidebar"] { border-right: 1px solid var(--ayq-border); }
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
        [data-testid="stSidebarNav"]::before { content: "AyatQu"; display: block; margin: .4rem 1rem .8rem;
          padding: .35rem 0 .8rem; border-bottom: 1px solid var(--ayq-border); color: var(--ayq-emerald);
          font-size: 2rem; font-weight: 800; line-height: 1.2; }
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
        .ayq-sidebar-author { margin-top: 1.2rem; padding: .9rem .2rem .3rem; border-top: 1px solid var(--ayq-border);
          color: color-mix(in srgb, var(--text-color) 72%, transparent); font-size: .76rem; line-height: 1.6; overflow-wrap: anywhere; }
        .ayq-author-title { margin-bottom: .4rem; color: var(--ayq-gold); font-weight: 800; }
        .ayq-author-row { margin: .2rem 0; }
        .ayq-section { padding-top: .25rem; }
        @media (prefers-color-scheme: dark) {
          :root { --ayq-surface: color-mix(in srgb, var(--secondary-background-color) 86%, #0f766e); }
          .ayq-card { box-shadow: 0 7px 20px rgba(0, 0, 0, .18); }
        }
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


def render_sidebar_author():
    """Menampilkan identitas proyek di bagian bawah sidebar navigasi."""
    st.sidebar.markdown(
        '<div class="ayq-sidebar-author">'
        '<div class="ayq-author-title">⭐ Dibuat oleh ⭐</div>'
        f'<div class="ayq-author-row">👤 Nama: {escape(NAMA)}</div>'
        f'<div class="ayq-author-row">🪪 NIM: {escape(NIM)}</div>'
        f'<div class="ayq-author-row">👩‍🏫 Dosen: {escape(DOSEN)}</div>'
        f'<div class="ayq-author-row">📚 Mata kuliah: {escape(MATA_KULIAH)}</div>'
        f'<div class="ayq-author-row">🏛️ {escape(UNIVERSITAS)} · {escape(TAHUN)}</div>'
        "</div>",
        unsafe_allow_html=True,
    )
