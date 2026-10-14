"""Entry point navigasi multi-halaman AyatQu."""

from pathlib import Path

import streamlit as st

from ui import load_css

ROOT = Path(__file__).resolve().parent

st.set_page_config(page_title="AyatQu", page_icon="📖", layout="wide")
load_css()

pages = [
    st.Page(
        str(ROOT / "views" / "pencarian.py"),
        title="Pencarian Ayat",
        icon="🔎",
        default=True,
    ),
    st.Page(str(ROOT / "views" / "evaluasi.py"), title="Evaluasi", icon="📊"),
    st.Page(str(ROOT / "views" / "ringkasan.py"), title="Ringkasan", icon="📝"),
    st.Page(str(ROOT / "views" / "tentang.py"), title="Tentang Aplikasi", icon="ℹ️"),
]

st.navigation(pages, position="sidebar").run()
