"""Halaman profil, teknologi, sumber, dan etika penggunaan AyatQu."""

from html import escape

import streamlit as st

from ui import (
    DOSEN,
    STREAMLIT_URL,
    MATA_KULIAH,
    NAMA,
    NIM,
    PRODI,
    TAHUN,
    UNIVERSITAS,
    render_footer,
    render_header,
)


def _technology_chips():
    technologies = [
        "Python",
        "scikit-learn",
        "PySastrawi",
        "Streamlit",
        "BM25",
        "TF-IDF",
        "RAG",
    ]
    chips = "".join(
        f'<span class="ayq-chip">{escape(item)}</span>' for item in technologies
    )
    st.markdown(chips, unsafe_allow_html=True)


def _author_card():
    streamlit_link = (
        f'<a href="{escape(STREAMLIT_URL, quote=True)}" target="_blank" rel="noopener noreferrer">'
        "Buka Aplikasi Streamlit</a>"
        if STREAMLIT_URL
        else "Belum diisi"
    )
    st.markdown(
        f"""
        <section class="ayq-card">
          <div class="ayq-card-label">Profil penulis</div>
          <p><strong>Nama</strong>: {escape(NAMA)}<br>
          <strong>NIM</strong>: {escape(NIM)}<br>
          <strong>Program studi</strong>: {escape(PRODI)}<br>
          <strong>Mata kuliah</strong>: {escape(MATA_KULIAH)}<br>
          <strong>Universitas</strong>: {escape(UNIVERSITAS)}<br>
          <strong>Dosen</strong>: {escape(DOSEN)}<br>
          <strong>Tahun</strong>: {escape(TAHUN)}<br>
          <strong>Aplikasi</strong>: {streamlit_link}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def main():
    render_header(
        "Tentang Aplikasi", "Latar belakang, teknologi, dan prinsip penggunaan AyatQu."
    )

    st.markdown("### Mengapa AyatQu dibuat")
    st.write(
        "Kueri sehari-hari tidak selalu memakai kosakata yang sama dengan terjemahan Al-Qur'an. "
        "Perbedaan ini dapat membuat pencarian kata langsung melewatkan ayat yang berkaitan."
    )
    st.write(
        "AyatQu menjembatani kesenjangan tersebut dengan preprocessing, kamus perluasan kueri, "
        "dan pemeringkatan BM25 atau TF-IDF. Ayat yang ditampilkan tetap diambil dari data sumber."
    )

    st.markdown("### Teknologi")
    _technology_chips()

    st.markdown("### Pengaman dan etika")
    safeguards = [
        "Ambang skor membantu menahan kueri yang tidak cukup cocok.",
        "Permintaan hukum atau fatwa ditolak oleh guardrail aplikasi.",
        "Rujukan ringkasan diperiksa terhadap ayat hasil pencarian.",
        "Teks Arab dan terjemahan selalu ditampilkan dari data asli, bukan ditulis ulang model.",
    ]
    for item in safeguards:
        st.markdown(f"- {item}")
    st.warning("AyatQu adalah alat bantu pencarian, bukan sumber tafsir atau fatwa.")

    st.markdown("### Sumber data")
    st.write(
        "Teks Arab Uthmani dan terjemahan bahasa Indonesia dari Kementerian Agama RI "
        "bersumber dari Tanzil.net. Periksa ketentuan penggunaan Tanzil dan cantumkan "
        "tanggal akses serta atribusi yang diminta pada laporan proyek."
    )

    st.markdown("### Profil proyek")
    _author_card()

    st.markdown("### Rujukan")
    references = [
        "Manning, Raghavan, dan Schutze (2008), Introduction to Information Retrieval.",
        "Robertson dan Zaragoza (2009), pembahasan model BM25.",
        "Jarvelin dan Kekalainen (2002), evaluasi pencarian dengan nDCG.",
        "Tala (2003), stemming bahasa Indonesia.",
        "Lewis dan rekan (2020), Retrieval-Augmented Generation.",
    ]
    for reference in references:
        st.markdown(f"- {reference}")
    st.caption(
        "Lengkapi detail bibliografi dan tautan sumber sebelum menyerahkan laporan akademik."
    )

    render_footer()


main()
