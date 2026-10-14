"""Halaman ikhtisar dataset, hasil utama, dan alur sistem."""

import pandas as pd
import streamlit as st

from ui import (
    get_engine,
    load_csv,
    render_footer,
    render_header,
    render_sidebar_author,
)


def _metric_value(frame, system, metric="nDCG@5"):
    if frame is None or not {"sistem", metric}.issubset(frame.columns):
        return None
    row = frame[frame["sistem"] == system]
    if row.empty:
        return None
    return pd.to_numeric(row.iloc[0][metric], errors="coerce")


def _format_delta(value):
    return f"{value:+.4f}" if pd.notna(value) else "tidak tersedia"


def _wilcoxon_summary(frame, subset):
    if frame is None or not {"subset", "signifikan_0.05"}.issubset(frame.columns):
        return f"Hasil uji Wilcoxon untuk subset {subset} belum tersedia."
    rows = frame[frame["subset"].astype(str).str.lower() == subset]
    if rows.empty:
        return f"Hasil uji Wilcoxon untuk subset {subset} belum tersedia."
    significant = rows["signifikan_0.05"].astype(str).str.lower().eq("ya").any()
    conclusion = (
        "terdapat hasil signifikan"
        if significant
        else "belum ada hasil yang signifikan"
    )
    return f"Pada subset {subset}, {conclusion} pada perbandingan yang diuji."


def main():
    render_header("Ringkasan", "Ikhtisar data, temuan evaluasi, dan alur kerja AyatQu.")
    try:
        engine = get_engine()
    except Exception as error:
        st.error(f"Data pencarian belum siap: {error}")
        st.info(
            "Jalankan semua sel AyatQu_Pipeline.ipynb, lalu buka kembali halaman ini."
        )
        render_sidebar_author()
        render_footer()
        return

    queries = load_csv("data/eval/queries.csv")
    comparison = load_csv("outputs/hasil_perbandingan.csv")
    wilcoxon = load_csv("outputs/uji_wilcoxon.csv")
    config = engine.cfg

    metric_cols = st.columns(4)
    metric_cols[0].metric("Jumlah ayat", f"{len(engine.df):,}")
    metric_cols[1].metric("Jumlah surah", f"{engine.df['surah_no'].nunique():,}")
    metric_cols[2].metric(
        "Kueri uji", f"{len(queries):,}" if queries is not None else "Tidak tersedia"
    )
    systems = (
        comparison["sistem"].nunique()
        if comparison is not None and "sistem" in comparison.columns
        else None
    )
    metric_cols[3].metric(
        "Sistem dibandingkan",
        f"{systems:,}" if systems is not None else "Tidak tersedia",
    )

    st.markdown("#### Konfigurasi terpilih")
    cfg_cols = st.columns(5)
    selected_values = [
        ("Preprocessing", config.get("preprocessing_config")),
        ("Metode", config.get("metode")),
        ("k1", config.get("k1")),
        ("b", config.get("b")),
        ("Bobot ekspansi", config.get("qe_weight")),
    ]
    for column, (label, value) in zip(cfg_cols, selected_values):
        column.metric(label, str(value) if value is not None else "Tidak tersedia")

    st.markdown("#### Temuan utama")
    test = (
        comparison[comparison["subset"].astype(str).str.lower() == "test"].copy()
        if comparison is not None and "subset" in comparison.columns
        else None
    )
    if test is None or test.empty or "nDCG@5" not in test.columns:
        st.info(
            "Hasil perbandingan test belum tersedia. Jalankan notebook sampai tahap ekspor hasil."
        )
    else:
        test["nDCG@5"] = pd.to_numeric(test["nDCG@5"], errors="coerce")
        test = test.dropna(subset=["nDCG@5"])
        if test.empty:
            st.info("Kolom nDCG@5 belum berisi angka evaluasi.")
        else:
            best = test.sort_values("nDCG@5", ascending=False).iloc[0]
            st.markdown(
                f"- Sistem dengan nDCG@5 tertinggi pada test adalah **{best['sistem']}** ({best['nDCG@5']:.4f})."
            )
            bm25 = _metric_value(test, "BM25")
            tfidf = _metric_value(test, "TF-IDF")
            bm25_qe = _metric_value(test, "BM25 + QE")
            if pd.notna(bm25) and pd.notna(tfidf):
                st.markdown(
                    f"- Selisih BM25 terhadap TF-IDF pada nDCG@5 adalah **{_format_delta(bm25 - tfidf)}**."
                )
            else:
                st.markdown(
                    "- Perbandingan BM25 dan TF-IDF belum lengkap pada CSV hasil."
                )
            if pd.notna(bm25_qe) and pd.notna(bm25):
                st.markdown(
                    f"- Selisih BM25 + ekspansi terhadap BM25 pada nDCG@5 adalah **{_format_delta(bm25_qe - bm25)}**."
                )
            else:
                st.markdown(
                    "- Dampak ekspansi pada BM25 belum dapat dihitung dari CSV hasil."
                )

    st.markdown("#### Uji Wilcoxon")
    st.write(_wilcoxon_summary(wilcoxon, "test"))
    st.write(_wilcoxon_summary(wilcoxon, "semua"))
    st.caption(
        "Interpretasikan hasil dengan hati-hati. Jumlah kueri terbatas dan uji statistik berdaya rendah."
    )

    st.markdown("#### Alur sistem")
    st.graphviz_chart(
        """
        digraph AyatQu {
          graph [rankdir=LR, bgcolor="transparent", nodesep="0.28", ranksep="0.42", pad="0.16"];
          node [shape=box, style="rounded,filled", color="#0F766E", fillcolor="#E6F3EF", fontname="Arial", fontsize=10, margin="0.14,0.10"];
          edge [color="#D4A017", penwidth=1.6, arrowsize=0.7];
          kueri [label="Kueri"];
          preprocessing [label="Preprocessing"];
          ekspansi [label="Perluasan Kueri"];
          bm25 [label="BM25 / TF-IDF"];
          ambang [label="Ambang dan\nPemilihan Ayat"];
          tampil [label="Tampil Ayat"];
          rag [label="Ringkasan RAG\ndan Validasi"];
          kueri -> preprocessing -> ekspansi -> bm25 -> ambang -> tampil -> rag;
        }
        """,
        use_container_width=True,
    )

    st.markdown("#### Keterbatasan dan langkah lanjut")
    st.markdown(
        "- Kumpulan kueri uji masih terbatas dan perlu diperluas, terutama kueri di luar topik.\n"
        "- Kamus ekspansi perlu ditinjau oleh validator yang memahami konteks bahasa.\n"
        "- Hasil pooling dapat menguntungkan sistem yang ikut membentuk kumpulan kandidat.\n"
        "- Ringkasan otomatis dibatasi pada hubungan dengan terjemahan dan bukan pengganti tafsir."
    )
    st.markdown(
        "**Kesimpulan.** AyatQu menyediakan pencarian topik dengan penghubung kosakata awam, pemeringkatan ayat, ambang penolakan, dan ringkasan yang divalidasi."
    )
    st.write(
        "**Saran pengembangan:** validasi qrels, tambah variasi kueri, dan uji konsistensi hasil dengan penilai manusia."
    )
    render_sidebar_author()
    render_footer()


main()
