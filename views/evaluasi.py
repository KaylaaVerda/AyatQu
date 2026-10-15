"""Halaman evaluasi model dan analisis hasil eksperimen."""

import altair as alt
import pandas as pd
import streamlit as st

from ui import (
    ROOT,
    load_csv,
    load_json,
    render_footer,
    render_header,
)

METRICS = ["P@5", "P@5_ketat", "MRR", "nDCG@5", "Recall@10"]


def _show_image(filename, caption):
    path = ROOT / "figures" / filename
    if path.is_file():
        st.image(str(path), caption=caption, use_container_width=True)
    else:
        st.info(f"Grafik {filename} belum tersedia.")


def _show_missing_outputs():
    expected = [
        "hasil_perbandingan.csv",
        "ablasi_preprocessing_dev.csv",
        "tuning_k1_b_dev.csv",
        "tuning_qe_weight_dev.csv",
        "uji_wilcoxon.csv",
        "analisis_error.csv",
        "skor_ambang.csv",
        "chatbot_rubrik.csv",
    ]
    missing = [name for name in expected if not (ROOT / "outputs" / name).is_file()]
    if missing:
        st.info(
            "Sebagian hasil evaluasi belum tersedia. Jalankan semua sel pada "
            "AyatQu_Pipeline.ipynb. File yang belum ada: " + ", ".join(missing)
        )


def _load_config():
    return load_json("models/best_config.json") or {}


def _comparison_tab():
    st.subheader("Perbandingan sistem")
    results = load_csv("outputs/hasil_perbandingan.csv")
    if results is None or not {"subset", "sistem", *METRICS}.issubset(results.columns):
        st.info(
            "Tabel perbandingan belum tersedia atau kolomnya belum lengkap. Jalankan notebook sampai selesai."
        )
        return

    subset = st.radio(
        "Subset kueri", ["test", "dev", "semua"], horizontal=True, index=0
    )
    current = results[results["subset"].astype(str).str.lower() == subset].copy()
    if current.empty:
        st.info(f"Belum ada hasil untuk subset {subset}.")
        return

    current[METRICS] = current[METRICS].apply(pd.to_numeric, errors="coerce")
    ranked = current.dropna(subset=["nDCG@5"]).sort_values("nDCG@5", ascending=False)
    if not ranked.empty:
        best = ranked.iloc[0]
        tfidf = current[current["sistem"] == "TF-IDF"]
        gap = (
            float(best["nDCG@5"] - tfidf.iloc[0]["nDCG@5"]) if not tfidf.empty else None
        )
        metric_cols = st.columns(2)
        metric_cols[0].metric(
            "Sistem terbaik · nDCG@5", str(best["sistem"]), f"{best['nDCG@5']:.4f}"
        )
        metric_cols[1].metric(
            "Selisih terhadap TF-IDF",
            f"{gap:+.4f}" if gap is not None else "Tidak tersedia",
            "nDCG@5",
        )

    styled = current.style.highlight_max(subset=METRICS, axis=0, color="#d8eee8")
    st.dataframe(styled, hide_index=True, use_container_width=True)

    long_data = current.melt(
        id_vars=["sistem"], value_vars=METRICS, var_name="metrik", value_name="nilai"
    )
    long_data["nilai"] = pd.to_numeric(long_data["nilai"], errors="coerce")
    chart = (
        alt.Chart(long_data.dropna(subset=["nilai"]))
        .mark_bar(cornerRadiusEnd=3)
        .encode(
            x=alt.X("metrik:N", title=None, axis=alt.Axis(labelAngle=0)),
            xOffset="sistem:N",
            y=alt.Y("nilai:Q", title="Nilai", scale=alt.Scale(domain=[0, 1])),
            color=alt.Color(
                "sistem:N", title="Sistem", scale=alt.Scale(scheme="tableau10")
            ),
            tooltip=["sistem:N", "metrik:N", alt.Tooltip("nilai:Q", format=".4f")],
        )
        .properties(height=330)
    )
    st.altair_chart(chart, use_container_width=True)

    csv = current.to_csv(index=False).encode("utf-8-sig")
    st.download_button("Unduh hasil subset ini", csv, f"hasil_{subset}.csv", "text/csv")
    with st.expander("Grafik evaluasi dari notebook"):
        _show_image(
            "perbandingan_sistem_test.png", "Perbandingan sistem pada kueri test"
        )
        _show_image("sebaran_ndcg_per_kueri.png", "Sebaran nDCG@5 per kueri")


def _process_tab(config):
    st.subheader("Proses eksperimen")
    st.caption(
        "Pemilihan konfigurasi dan parameter dilakukan memakai kueri dev. Kueri test disimpan untuk pelaporan akhir."
    )

    st.markdown("#### Ablasi preprocessing")
    st.write(
        "Tahap ini membandingkan dampak stopword, stemming, dan ekspansi terhadap kualitas retrieval."
    )
    ablation = load_csv("outputs/ablasi_preprocessing_dev.csv")
    if ablation is None:
        st.info("Tabel ablasi belum tersedia.")
    else:
        st.dataframe(ablation, hide_index=True, use_container_width=True)
    _show_image("ablasi_preprocessing.png", "Ablasi preprocessing pada kueri dev")

    st.markdown("#### Tuning parameter BM25")
    st.write(
        "Grid dev membantu memilih k1 dan b tanpa menggunakan hasil test untuk tuning."
    )
    tuning = load_csv("outputs/tuning_k1_b_dev.csv")
    if tuning is None:
        st.info("Tabel tuning k1 dan b belum tersedia.")
    else:
        tuning = tuning.copy()
        first_col = tuning.columns[0]
        tuning = tuning.rename(columns={first_col: "k1"})
        tuning["k1"] = pd.to_numeric(tuning["k1"], errors="coerce")
        heat_data = tuning.melt(id_vars=["k1"], var_name="b", value_name="nDCG@5")
        heat_data["b"] = pd.to_numeric(heat_data["b"], errors="coerce")
        heat_data["nDCG@5"] = pd.to_numeric(heat_data["nDCG@5"], errors="coerce")
        st.altair_chart(
            alt.Chart(heat_data.dropna())
            .mark_rect(stroke="white", strokeWidth=1)
            .encode(
                x=alt.X("b:O", title="b"),
                y=alt.Y("k1:O", title="k1"),
                color=alt.Color(
                    "nDCG@5:Q", title="nDCG@5", scale=alt.Scale(scheme="greens")
                ),
                tooltip=["k1:Q", "b:Q", alt.Tooltip("nDCG@5:Q", format=".4f")],
            )
            .properties(height=260),
            use_container_width=True,
        )
        st.dataframe(tuning, hide_index=True, use_container_width=True)
    _show_image("tuning_k1_b.png", "Heatmap tuning k1 dan b dari notebook")

    st.markdown("#### Bobot ekspansi kueri")
    st.write(
        "Bobot ekspansi dipilih dari dev agar istilah tambahan tidak mengalahkan kata utama pengguna."
    )
    qe = load_csv("outputs/tuning_qe_weight_dev.csv")
    if qe is None:
        st.info("Tabel tuning bobot ekspansi belum tersedia.")
    else:
        st.dataframe(qe, hide_index=True, use_container_width=True)

    st.markdown("#### Konfigurasi terpilih")
    values = [
        ("Preprocessing", config.get("preprocessing_config")),
        ("k1", config.get("k1")),
        ("b", config.get("b")),
        ("Bobot ekspansi", config.get("qe_weight")),
        ("Ambang skor", config.get("ambang_skor_ternormalisasi")),
    ]
    columns = st.columns(len(values))
    for column, (label, value) in zip(columns, values):
        column.metric(label, str(value) if value is not None else "Tidak tersedia")


def _significance_tab():
    st.subheader("Uji signifikansi")
    st.caption(
        "Jumlah kueri test kecil sehingga daya uji statistik rendah. Tidak signifikan bukan bukti bahwa kedua sistem setara."
    )
    results = load_csv("outputs/uji_wilcoxon.csv")
    if results is None or "subset" not in results.columns:
        st.info("Hasil uji Wilcoxon belum tersedia.")
        return
    subsets = sorted(results["subset"].dropna().astype(str).unique())
    if not subsets:
        st.info("Belum ada baris hasil uji Wilcoxon untuk ditampilkan.")
        return
    subset = st.selectbox("Subset uji", subsets)
    current = results[results["subset"].astype(str) == subset].copy()
    if "signifikan_0.05" in current.columns:
        current["hasil"] = (
            current["signifikan_0.05"]
            .map({"ya": "Signifikan", "tidak": "Belum signifikan"})
            .fillna("Tidak diketahui")
        )
        current = current.style.apply(
            lambda row: [
                (
                    "background-color: #0f766e; color: white"
                    if row.get("hasil") == "Signifikan"
                    else ""
                )
                for _ in row
            ],
            axis=1,
        )
    st.dataframe(current, hide_index=True, use_container_width=True)


def _error_tab():
    st.subheader("Analisis error")
    errors = load_csv("outputs/analisis_error.csv")
    if errors is None:
        st.info("Analisis error belum tersedia.")
        return
    for _, row in errors.iterrows():
        query = str(row.get("kueri", "Kueri tidak tersedia"))
        score = pd.to_numeric(row.get("nDCG@5"), errors="coerce")
        with st.container(border=True):
            st.markdown(f"**{query}**")
            columns = st.columns([1, 4])
            columns[0].metric("nDCG@5", f"{score:.3f}" if pd.notna(score) else "-")
            columns[1].write(str(row.get("dugaan_penyebab", "Penyebab belum dicatat")))


def _threshold_tab(config):
    st.subheader("Ambang skor dan rubrik chatbot")
    scores = load_csv("outputs/skor_ambang.csv")
    if scores is None or "norm_top1" not in scores.columns:
        st.info("Data skor ambang belum tersedia.")
    else:
        scores = scores.copy()
        scores["norm_top1"] = pd.to_numeric(scores["norm_top1"], errors="coerce")
        scores["jenis"] = scores["in_scope"].map(
            {
                1: "Kueri topik",
                0: "Di luar topik",
                "1": "Kueri topik",
                "0": "Di luar topik",
            }
        )
        if "split" not in scores.columns:
            scores["split"] = "tidak diketahui"
        else:
            scores["split"] = scores["split"].fillna("tidak diketahui")
        threshold = pd.to_numeric(
            config.get("ambang_skor_ternormalisasi"), errors="coerce"
        )
        points = (
            alt.Chart(scores.dropna(subset=["norm_top1", "jenis"]))
            .mark_circle(size=80, opacity=0.75)
            .encode(
                x=alt.X(
                    "norm_top1:Q",
                    title="Skor teratas ternormalisasi",
                    scale=alt.Scale(domain=[0, 1]),
                ),
                y=alt.Y("jenis:N", title=None),
                color=alt.Color(
                    "split:N", title="Split", scale=alt.Scale(scheme="tableau10")
                ),
                tooltip=[
                    "query_id:N",
                    "kueri:N",
                    "jenis:N",
                    "split:N",
                    alt.Tooltip("norm_top1:Q", format=".3f"),
                ],
            )
        )
        chart = points
        if pd.notna(threshold):
            rule = (
                alt.Chart(pd.DataFrame({"ambang": [threshold]}))
                .mark_rule(color="#d4a017", strokeDash=[6, 4], size=2)
                .encode(x="ambang:Q")
            )
            chart = points + rule
        st.altair_chart(chart.properties(height=240), use_container_width=True)
        st.dataframe(scores, hide_index=True, use_container_width=True)

    st.markdown("#### Rubrik chatbot")
    rubric = load_csv("outputs/chatbot_rubrik.csv")
    if rubric is None or not {"jenis", "status"}.issubset(rubric.columns):
        st.info("Ringkasan rubrik chatbot belum tersedia.")
        return
    counts = (
        rubric.groupby(["jenis", "status"], dropna=False)
        .size()
        .rename("jumlah")
        .reset_index()
    )
    st.dataframe(counts, hide_index=True, use_container_width=True)
    st.caption(
        "Kolom R2, R3, dan R4 yang memerlukan penilaian manusia harus diisi secara manual."
    )


def main():
    render_header(
        "Evaluasi",
        "Bandingkan sistem, telusuri proses eksperimen, dan periksa batas hasil.",
    )
    config = _load_config()
    _show_missing_outputs()
    tabs = st.tabs(
        [
            "Perbandingan Sistem",
            "Proses Eksperimen",
            "Uji Signifikansi",
            "Analisis Error",
            "Ambang Skor dan Chatbot",
        ]
    )
    with tabs[0]:
        _comparison_tab()
    with tabs[1]:
        _process_tab(config)
    with tabs[2]:
        _significance_tab()
    with tabs[3]:
        _error_tab()
    with tabs[4]:
        _threshold_tab(config)
    render_footer()


main()
