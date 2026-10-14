"""Halaman percakapan pencarian ayat dan panduan kueri."""

import streamlit as st

from ayatqu_core import AyatQu
from ui import (
    get_engine,
    render_ayat_card,
    render_footer,
    render_header,
    render_sidebar_author,
)

CONTOH_KUERI = [
    "ayat tentang sabar",
    "ayat tentang berbakti kepada orang tua",
    "ayat tentang rezeki",
    "ayat yang bikin hati tenang",
]


def _show_error(error):
    st.error(f"Mesin pencarian belum dapat dimuat: {error}")
    st.info(
        "Pastikan notebook sudah dijalankan dan file data serta models/best_config.json tersedia."
    )
    render_sidebar_author()
    render_footer()


def _show_turn(engine, turn):
    result = turn.get("result")
    if turn.get("error"):
        st.error(turn["error"])
        return

    if turn.get("process") is not None:
        with st.expander("Proses kueri", expanded=False):
            st.json(turn["process"])
            st.write("Skor ternormalisasi teratas:", turn.get("top_score", 0.0))
            st.write("Ambang skor:", turn.get("threshold", engine.threshold))

    if result["status"] == "tidak_ditemukan":
        st.info(result["ringkasan"])
        return

    if result["status"] == "ditolak_fatwa":
        st.warning(result["ringkasan"])
    for hit in result["hits"]:
        render_ayat_card(engine, hit)

    if result["status"] in ("ok", "ringkasan_cadangan") and result["ringkasan"]:
        st.subheader("Keterkaitan dengan pertanyaanmu")
        st.write(result["ringkasan"])


def _search(engine, query, mode, show_process):
    method, use_qe = AyatQu.METHODS[mode]
    try:
        result = engine.answer(query, method=method, use_qe=use_qe)
        turn = {"query": query, "result": result, "process": None}
        if show_process:
            turn["process"] = engine.explain_query(query, use_qe=use_qe)
            turn["top_score"] = (
                result["hits"][0]["norm_score"] if result["hits"] else 0.0
            )
            turn["threshold"] = engine.threshold
        return turn
    except Exception as error:
        return {"query": query, "error": f"Pencarian gagal ({type(error).__name__})."}


def _show_how_to():
    st.subheader("Cara kerja pencarian")
    steps = [
        (
            "Tulis topik",
            "Gunakan bahasa sehari-hari, misalnya sabar saat menghadapi ujian.",
        ),
        (
            "Kueri diproses",
            "Kata umum dibersihkan dan istilah yang cocok diperluas dengan kamus.",
        ),
        (
            "Ayat diberi peringkat",
            "BM25 atau TF-IDF mengurutkan ayat berdasarkan kecocokan.",
        ),
        (
            "Hasil disaring",
            "Ambang skor dan relevansi otomatis membatasi ayat yang ditampilkan.",
        ),
        (
            "Ringkasan dibuat",
            "Ringkasan menjelaskan hubungan kata kueri dan ayat, bukan tafsir.",
        ),
    ]
    for index, (title, body) in enumerate(steps, start=1):
        st.markdown(f"**{index}. {title}**  \n{body}")

    good, weak = st.columns(2)
    with good:
        st.markdown("#### Kueri yang membantu")
        st.success("ayat tentang sabar saat menghadapi ujian")
        st.success("ayat tentang berbakti kepada orang tua")
    with weak:
        st.markdown("#### Kueri yang terlalu luas")
        st.info("topik bagus")
        st.info("tolong jelaskan semuanya")

    st.markdown("#### Arti status jawaban")
    st.markdown(
        "- **Ringkasan cadangan**: ayat ditemukan, ringkasan lokal dipakai tanpa model bahasa.\n"
        "- **Ringkasan tervalidasi**: ringkasan lolos pemeriksaan rujukan dan guardrail.\n"
        "- **Tidak ditemukan**: tidak ada hasil yang melewati ambang skor.\n"
        "- **Ditolak sebagai fatwa**: pertanyaan meminta hukum atau keputusan agama."
    )
    st.warning("AyatQu tidak menafsirkan ayat dan tidak memberikan hukum atau fatwa.")


def main():
    render_header(
        "Pencarian Ayat",
        "Temukan ayat berdasarkan topik dengan kata-kata yang biasa kamu gunakan.",
    )
    try:
        engine = get_engine()
    except Exception as error:
        _show_error(error)
        return

    with st.sidebar:
        st.subheader("Pengaturan pencarian")
        mode = st.selectbox(
            "Metode pencarian", list(AyatQu.METHODS), key="search_method"
        )
        show_process = st.checkbox("Tampilkan proses kueri", key="show_query_process")
    render_sidebar_author()

    chatbot_tab, guide_tab = st.tabs(["Chatbot", "Cara Mencari Ayat"])
    with chatbot_tab:
        if "ayatqu_chat_history" not in st.session_state:
            st.session_state["ayatqu_chat_history"] = []

        history = st.session_state["ayatqu_chat_history"]
        pending_query = st.session_state.pop("ayatqu_pending_query", None)
        submitted_query = st.chat_input("Tulis topik atau pertanyaanmu")
        query = pending_query or submitted_query
        if query:
            with st.spinner("Mencari ayat..."):
                turn = _search(engine, query, mode, show_process)
            st.session_state["ayatqu_chat_history"].append(turn)
            history = st.session_state["ayatqu_chat_history"]

        if not history:
            st.markdown("Mulai dengan salah satu contoh ini")
            columns = st.columns(2)
            for index, example in enumerate(CONTOH_KUERI):
                if columns[index % 2].button(
                    example, use_container_width=True, key=f"example_{index}"
                ):
                    st.session_state["ayatqu_pending_query"] = example
                    st.rerun()

        for turn in history:
            with st.chat_message("user"):
                st.write(turn["query"])
            with st.chat_message("assistant"):
                _show_turn(engine, turn)

        clear_col, _ = st.columns([1, 4])
        with clear_col:
            if st.button("Hapus percakapan", disabled=not history):
                st.session_state["ayatqu_chat_history"] = []
                st.rerun()

    with guide_tab:
        _show_how_to()

    render_footer()


main()
