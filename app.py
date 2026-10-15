"""Entry point navigasi multi-halaman AyatQu."""

from pathlib import Path

import streamlit as st

from ui import load_css

ROOT = Path(__file__).resolve().parent

st.set_page_config(page_title="AyatQu", layout="wide")
load_css()

pages = [
    st.Page(
        str(ROOT / "views" / "beranda.py"),
        title="Beranda",
        default=True,
    ),
    st.Page(
        str(ROOT / "views" / "pencarian.py"),
        title="Pencarian Ayat",
    ),
    st.Page(str(ROOT / "views" / "evaluasi.py"), title="Evaluasi"),
    st.Page(str(ROOT / "views" / "ringkasan.py"), title="Ringkasan"),
    st.Page(str(ROOT / "views" / "tentang.py"), title="Tentang Aplikasi"),
]

st.navigation(pages, position="top").run()
