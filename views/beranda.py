"""Landing page AyatQu dengan ringkasan data pencarian dan evaluasi."""

from html import escape
import math
from pathlib import Path

import streamlit as st

from ui import (
    NAMA,
    NIM,
    TAHUN,
    get_engine,
    load_csv,
    load_json,
    load_landing_css,
    render_footer,
)

ROOT = Path(__file__).resolve().parents[1]
CONTOH_KUERI = "ayat tentang sabar"


@st.cache_data(show_spinner=False)
def _cached_preview(_engine, query):
    hits = _engine.search(query, method="bm25", use_qe=True, k=3)
    results = []
    for hit in hits:
        verse = _engine.verse(hit["id"])
        results.append(
            {
                "label": f"QS. {verse['surah_nama']} {verse['surah_no']}:{verse['ayat_no']}",
                "score": float(hit["norm_score"]),
            }
        )
    return results, _engine.explain_query(query, use_qe=True)


def _chips(items):
    if not items:
        return '<span class="ayq-preview-note">Belum ada istilah yang cocok.</span>'
    return "".join(
        f'<span class="ayq-data-chip">{escape(str(item))}</span>' for item in items
    )


def _comparison_data():
    results = load_csv("outputs/hasil_perbandingan.csv")
    required = {"subset", "sistem", "nDCG@5"}
    if results is None or not required.issubset(results.columns):
        return None
    test_results = results[
        results["subset"].astype(str).str.lower() == "test"
    ].copy()
    if test_results.empty:
        return None
    test_results["nDCG@5"] = test_results["nDCG@5"].map(_as_float)
    return test_results.dropna(subset=["nDCG@5"])


def _as_float(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return number if math.isfinite(number) else float("nan")


def _comparison_card(comparison, config):
    if comparison is None or comparison.empty:
        return ""

    rows = []
    for _, row in comparison.iterrows():
        score = min(max(float(row["nDCG@5"]), 0.0), 1.0)
        label = escape(str(row["sistem"]))
        rows.append(
            f'<div class="ayq-ndcg-row"><span>{label}</span>'
            f'<span class="ayq-ndcg-track"><span class="ayq-ndcg-fill" style="width:{score * 100:.1f}%"></span></span>'
            f'<strong>{score:.1%}</strong></div>'
        )

    status = str(config.get("status_qrels", "")) if config else ""
    draft_label = (
        '<span class="ayq-draft-label">Kunci jawaban draf</span>'
        if "draf" in status.lower()
        else ""
    )
    return (
        '<article class="ayq-float-card"><div class="ayq-float-title">'
        "Perbandingan Sistem</div>"
        '<div class="ayq-preview-note">nDCG@5 · kueri uji</div>'
        f'{"".join(rows)}{draft_label}</article>'
    )


def _preview_stack(engine, comparison, config):
    if engine is None:
        results_html = (
            '<div class="ayq-preview-note">Contoh hasil belum dapat dimuat. '
            "Pastikan data indeks tersedia.</div>"
        )
        process_html = (
            '<div class="ayq-preview-note">Proses kueri akan tampil setelah mesin pencarian siap.</div>'
        )
    else:
        try:
            results, explanation = _cached_preview(engine, CONTOH_KUERI)
            result_rows = []
            for result in results:
                score = min(max(float(result["score"]), 0.0), 1.0)
                result_rows.append(
                    '<div class="ayq-result-row">'
                    f'<span>{escape(result["label"])}</span>'
                    f'<strong>{score:.0%}</strong>'
                    '<span class="ayq-score-track">'
                    f'<span class="ayq-score-fill" style="width:{score * 100:.1f}%"></span>'
                    "</span></div>"
                )
            results_html = "".join(result_rows) or (
                '<div class="ayq-preview-note">Belum ada ayat yang cocok untuk contoh ini.</div>'
            )
            process_html = (
                '<div class="ayq-preview-note">Token kueri</div>'
                f'<div class="ayq-data-chips">{_chips(explanation.get("token_kueri", []))}</div>'
                '<div class="ayq-preview-note" style="margin-top:.55rem">Topik kamus yang cocok</div>'
                f'<div class="ayq-data-chips">{_chips(explanation.get("topik_kamus_cocok", []))}</div>'
                '<div class="ayq-preview-note" style="margin-top:.55rem">Istilah ekspansi</div>'
                f'<div class="ayq-data-chips">{_chips(explanation.get("istilah_ekspansi", []))}</div>'
            )
        except Exception:
            results_html = (
                '<div class="ayq-preview-note">Contoh pencarian belum dapat ditampilkan.</div>'
            )
            process_html = (
                '<div class="ayq-preview-note">Rincian proses kueri belum tersedia.</div>'
            )

    search_card = (
        '<article class="ayq-float-card"><div class="ayq-float-title">'
        "Contoh Pencarian</div>"
        f'<div class="ayq-query-sample">{escape(CONTOH_KUERI)}</div>'
        f"{results_html}</article>"
    )
    process_card = (
        '<article class="ayq-float-card"><div class="ayq-float-title">'
        f"Proses Kueri</div>{process_html}</article>"
    )
    comparison_card = _comparison_card(comparison, config)
    return (
        '<div class="ayq-preview-stack">'
        f"{search_card}{process_card}{comparison_card}"
        '<div class="ayq-book-orbit" aria-hidden="true">📖</div></div>'
    )


def _format_count(value):
    return f"{int(value):,}".replace(",", ".")


def _configuration_label(config):
    if not config:
        return "Belum tersedia"
    method = str(config.get("metode", "")).strip()
    method_label = {"bm25": "BM25", "tfidf": "TF-IDF"}.get(
        method.lower(), method
    )
    if config.get("ekspansi_kueri"):
        method_label = f"{method_label} + ekspansi" if method_label else "Ekspansi kueri"
    preprocessing = str(config.get("preprocessing_config", "")).strip()
    parts = [part for part in (method_label, preprocessing) if part]
    return " · ".join(parts) if parts else "Belum tersedia"


def _render_stats(engine, comparison, config):
    verse_count = len(engine.df) if engine is not None else None
    surah_count = engine.df["surah_no"].nunique() if engine is not None else None

    queries = load_csv("data/eval/queries.csv")
    if queries is not None and "split" in queries.columns:
        query_count = int((queries["split"].astype(str).str.lower() == "test").sum())
        query_value = _format_count(query_count)
    else:
        query_value = "Belum tersedia"

    system_count = (
        int(comparison["sistem"].dropna().astype(str).nunique())
        if comparison is not None
        else None
    )
    verse_value = (
        f'{_format_count(verse_count)} ayat<br><small>{_format_count(surah_count)} surah</small>'
        if verse_count is not None
        else "Belum tersedia"
    )
    stats = [
        ("Korpus Al-Qur'an", verse_value),
        ("Kueri uji", query_value),
        (
            "Sistem dibandingkan",
            _format_count(system_count) if system_count is not None else "Belum tersedia",
        ),
        ("Konfigurasi terpilih", escape(_configuration_label(config))),
    ]

    columns = st.columns(len(stats), gap="medium")
    for column, (label, value) in zip(columns, stats):
        with column:
            st.markdown(
                f'<div class="ayq-stat-card"><div class="ayq-stat-label">{escape(label)}</div>'
                f'<div class="ayq-stat-value">{value}</div></div>',
                unsafe_allow_html=True,
            )


def _render_info_cards(items, numbered=False):
    columns = st.columns(len(items), gap="medium")
    for index, (title, body) in enumerate(items, start=1):
        number = (
            f'<div class="ayq-step-number">{index}</div>' if numbered else ""
        )
        with columns[index - 1]:
            st.markdown(
                '<article class="ayq-info-card">'
                f"{number}<div class=\"ayq-info-title\">{escape(title)}</div>"
                f'<div class="ayq-info-copy">{escape(body)}</div></article>',
                unsafe_allow_html=True,
            )


def main():
    load_landing_css()
    st.markdown('<div class="ayq-landing"></div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="ayq-home-badges">'
        '<span class="ayq-home-badge">Information Retrieval</span>'
        '<span class="ayq-home-badge">BM25 + Perluasan Kueri</span>'
        '<span class="ayq-home-badge">RAG dengan Guardrail</span></div>',
        unsafe_allow_html=True,
    )

    hero_left, hero_right = st.columns([1.5, 0.8], gap="large")
    with hero_left:
        st.markdown(
            '<h1 class="ayq-home-title">Menemukan<br>'
            '<span class="ayq-title-green">Ayat</span> Al-Qur\'an dari<br>'
            '<span class="ayq-title-gold">Topik</span> yang Kamu Ingat</h1>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="ayq-home-copy">Tulis topik dengan bahasa sehari-hari, '
            'misalnya “ayat tentang sabar”. AyatQu menampilkan teks Arab, '
            'terjemahan, nama surah, dan nomor ayat dari data sumber. '
            'AyatQu membantu pencarian, bukan menafsirkan atau memberi fatwa.</p>',
            unsafe_allow_html=True,
        )
        primary, secondary = st.columns(2, gap="small")
        with primary:
            if st.button(
                "Coba Sekarang",
                type="primary",
                use_container_width=True,
                key="beranda_coba_sekarang",
            ):
                st.switch_page("views/pencarian.py")
        with secondary:
            if st.button(
                "Lihat Evaluasi",
                type="secondary",
                use_container_width=True,
                key="beranda_lihat_evaluasi",
            ):
                st.switch_page("views/evaluasi.py")

    try:
        engine = get_engine()
    except Exception:
        engine = None
    comparison = _comparison_data()
    loaded_config = load_json("models/best_config.json")
    config = loaded_config if isinstance(loaded_config, dict) else {}

    with hero_right:
        st.markdown(
            _preview_stack(engine, comparison, config), unsafe_allow_html=True
        )

    _render_stats(engine, comparison, config)

    st.markdown(
        '<h2 class="ayq-home-section">Cara Kerja Singkat</h2>',
        unsafe_allow_html=True,
    )
    _render_info_cards(
        [
            ("Tulis topikmu", "Gunakan kata-kata yang kamu ingat dari keseharian."),
            (
                "Kueri diperluas dan dicari",
                "AyatQu mencocokkan istilah terkait lalu memberi peringkat dengan BM25.",
            ),
            (
                "Ayat dan keterkaitan tampil",
                "Baca ayat sumber dan ringkasan hubungan kueri dengan hasil pencarian.",
            ),
        ],
        numbered=True,
    )

    st.markdown(
        '<h2 class="ayq-home-section">Kenapa AyatQu</h2>',
        unsafe_allow_html=True,
    )
    _render_info_cards(
        [
            (
                "Bahasa sehari-hari dipahami",
                "Perluasan kueri membantu menghubungkan topik dengan istilah terkait.",
            ),
            (
                "Ayat berasal dari data asli",
                "Teks Arab dan terjemahan ditampilkan dari sumber, bukan ditulis ulang model.",
            ),
            (
                "Aman dan tidak menafsirkan",
                "Permintaan fatwa ditolak, skor disaring, dan rujukan ringkasan divalidasi.",
            ),
        ]
    )

    st.markdown(
        '<div class="ayq-home-cta"><div class="ayq-home-cta-title">'
        "Mulai dari topik yang kamu ingat</div>"
        '<div class="ayq-info-copy">Temukan ayat yang berkaitan, lalu baca sumbernya langsung.</div></div>',
        unsafe_allow_html=True,
    )
    if st.button(
        "Coba Sekarang",
        type="primary",
        use_container_width=True,
        key="beranda_coba_sekarang_bawah",
    ):
        st.switch_page("views/pencarian.py")

    st.markdown(
        '<div class="ayq-byline">'
        f'Dibuat oleh {escape(NAMA)} ({escape(NIM)}) | Proyek STKI | {escape(TAHUN)}'
        "</div>",
        unsafe_allow_html=True,
    )
    render_footer()


main()