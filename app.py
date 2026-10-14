"""
AyatQu: chatbot pencarian ayat Al-Qur'an berbasis topik.
Jalankan dari folder proyek (yang berisi models/, data/, expansion_dict.json):
    streamlit run app.py
"""
import html
import os

import streamlit as st

from ayatqu_core import AyatQu, FOOTNOTE, make_anthropic_llm

st.set_page_config(page_title="AyatQu", page_icon="📖", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap');
.arab { font-family: 'Amiri', 'Scheherazade New', 'Traditional Arabic', serif; font-size: 1.9rem; line-height: 2.4rem;
        direction: rtl; text-align: right; margin: 0.4rem 0 0.6rem 0; }
.kartu { border: 1px solid rgba(128,128,128,0.35); border-radius: 12px; padding: 14px 18px; margin-bottom: 14px; }
.label { font-size: 0.85rem; opacity: 0.75; font-weight: 600; }
.catatan { font-size: 0.8rem; opacity: 0.7; margin-top: 2rem; text-align: center; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner="Menyiapkan indeks pencarian...")
def load_engine():
    return AyatQu()


try:
    engine = load_engine()
except Exception as e:
    st.error(f"Aplikasi belum bisa dimulai: {e}")
    st.stop()

st.title("📖 AyatQu")
st.caption("Cari ayat Al-Qur'an berdasarkan topik dengan bahasa sehari-hari.")

with st.sidebar:
    st.header("Pengaturan")
    mode = st.selectbox("Metode pencarian", list(AyatQu.METHODS.keys()), index=0,
                        help="Pilihan lain berguna untuk demo perbandingan metode.")
    tampil_proses = st.checkbox("Tampilkan proses kueri", value=False)

    st.divider()
    pakai_llm = st.checkbox("Ringkasan dengan model bahasa (RAG)", value=False,
                            help="Bila mati, ringkasan disusun dengan template tanpa model bahasa.")
    api_key = ""
    if pakai_llm:
        api_key = st.text_input("API key", type="password", value=os.environ.get("ANTHROPIC_API_KEY", ""))
        st.caption("Kunci tidak disimpan. Ayat tetap ditampilkan dari data asli, model hanya merangkum.")

    st.divider()
    st.caption(f"Ayat yang tampil otomatis: skor minimal {int(engine.rasio_relatif * 100)}% dari ayat teratas (maksimal {engine.maks_tampil}).")
    st.caption(f"Konfigurasi: {engine.config} | k1={engine.k1}, b={engine.b}, ambang={engine.threshold}")
    st.caption(f"Status kunci jawaban: {engine.cfg.get('status_qrels', '-')}")

contoh = ["ayat tentang sabar", "ayat tentang berbakti kepada orang tua", "ayat tentang rezeki", "ayat yang bikin hati tenang"]
cols = st.columns(len(contoh))
for c, q in zip(cols, contoh):
    if c.button(q, use_container_width=True):
        st.session_state["query"] = q

query = st.text_input("Tulis topik atau pertanyaanmu", key="query", placeholder="contoh: ayat tentang sabar saat ujian")
cari = st.button("Cari ayat", type="primary")

if query and (cari or query):
    method, use_qe = AyatQu.METHODS[mode]
    llm_fn = None
    if pakai_llm and api_key:
        try:
            llm_fn = make_anthropic_llm(api_key=api_key)
        except Exception as e:
            st.warning(f"Model bahasa tidak bisa dipakai ({type(e).__name__}). Memakai ringkasan template.")

    with st.spinner("Mencari ayat..."):
        res = engine.answer(query, llm_fn=llm_fn, method=method, use_qe=use_qe)

    if tampil_proses:
        with st.expander("Proses kueri", expanded=True):
            st.json(engine.explain_query(query, use_qe=use_qe))
            if res["hits"]:
                st.write("Skor ternormalisasi teratas:", round(res["hits"][0]["norm_score"], 3), "| ambang:", engine.threshold)

    if res["status"] == "tidak_ditemukan":
        st.info(res["ringkasan"])
    else:
        if res["status"] == "ditolak_fatwa":
            st.warning(res["ringkasan"])
        for h in res["hits"]:
            v = engine.verse(h["id"])
            st.markdown(f"""
<div class="kartu">
  <div class="label">{html.escape(v['surah_nama'])} ({v['surah_no']}):{v['ayat_no']}</div>
  <div class="arab">{html.escape(v['teks_arab'])}</div>
  <div>{html.escape(v['terjemahan'])}</div>
</div>""", unsafe_allow_html=True)
        if res["status"] in ("ok", "ringkasan_cadangan") and res["ringkasan"]:
            st.subheader("Keterkaitan dengan pertanyaanmu")
            st.write(res["ringkasan"])
            if res["status"] == "ringkasan_cadangan" and llm_fn is not None:
                st.caption("Jawaban model bahasa tidak lolos validasi, jadi ditampilkan ringkasan cadangan.")

st.markdown(f"<div class='catatan'>{FOOTNOTE}<br>Sumber data: Tanzil.net (teks Uthmani dan terjemahan Kementerian Agama RI).</div>", unsafe_allow_html=True)
