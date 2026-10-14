"""
ayatqu_core.py
Mesin pencari AyatQu. Logikanya sama dengan notebook AyatQu_Pipeline.ipynb.
Aturan utama: teks Arab dan terjemahan tidak pernah diubah. Pembersihan dan stemming hanya pada salinan indexing.
"""
import json
import math
import re
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

ROOT = Path(__file__).resolve().parent

STOPWORDS = set("""
yang dan di ke dari pada untuk dengan atau akan telah sudah adalah ialah itu ini maka jika apabila karena
agar supaya sebagai oleh dalam saja pula lagi kepada para bagi hanya serta tetapi tetapilah sedang sedangkan
kamu kami kita mereka dia ia aku engkau kalian nya lah kah pun juga yaitu yakni ketika sebelum sesudah setelah
hingga sampai antara bahwa sehingga seperti sebagaimana dapat bisa harus mau ada dengannya padanya olehnya
atasnya bagimu bagi mereka mu ku dll dsb sebab walau walaupun meskipun namun kecuali selain seraya sambil
""".split())
NEGASI = {"tidak", "bukan", "jangan", "tiada", "tanpa", "belum"}
STOPWORDS -= NEGASI

QUERY_STOPWORDS = set("""
ayat tentang mengenai soal terkait quran alquran al qur an surah surat yang bikin apa ya dong nih
tolong carikan cari bagaimana gimana bisa ada
""".split())

CONFIGS = {
    "C1_dasar":     {"stop": False, "stem": False},
    "C2_stopword":  {"stop": True,  "stem": False},
    "C3_stem":      {"stop": False, "stem": True},
    "C4_stop_stem": {"stop": True,  "stem": True},
}

_TYPO_I = re.compile(r"(?<=[a-z])I(?=[a-z])")


def clean_text(text):
    t = _TYPO_I.sub("l", text)
    t = t.lower()
    t = t.replace("'", "").replace("\u2019", "").replace("`", "")
    t = re.sub(r"[-\u2010-\u2015]", " ", t)
    t = re.sub(r"[^a-z\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


class Stemmer:
    """Pembungkus Sastrawi dengan cache per kata."""
    def __init__(self, cache_path):
        self.cache_path = Path(cache_path)
        self.cache = json.loads(self.cache_path.read_text(encoding="utf-8")) if self.cache_path.exists() else {}
        try:
            from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
        except ImportError as e:
            raise RuntimeError("Konfigurasi terpilih memakai stemming, tetapi PySastrawi belum terpasang. "
                               "Jalankan: pip install PySastrawi") from e
        self._s = StemmerFactory().create_stemmer()
        self._dirty = False

    def stem(self, w):
        if w not in self.cache:
            self.cache[w] = self._s.stem(w)
            self._dirty = True
        return self.cache[w]

    def save(self):
        if self._dirty:
            self.cache_path.write_text(json.dumps(self.cache, ensure_ascii=False), encoding="utf-8")
            self._dirty = False


class BM25Index:
    def __init__(self, docs_tokens, k1=1.5, b=0.75):
        self.k1, self.b = k1, b
        self.cv = CountVectorizer(analyzer=str.split)
        X = self.cv.fit_transform([" ".join(t) for t in docs_tokens]).tocsc().astype(np.float64)
        self.X, self.vocab, self.N = X, self.cv.vocabulary_, X.shape[0]
        self.dl = np.asarray(X.sum(axis=1)).ravel()
        self.avgdl = self.dl.mean()
        dfreq = np.asarray((X > 0).sum(axis=0)).ravel()
        self.idf = np.log(1.0 + (self.N - dfreq + 0.5) / (dfreq + 0.5))
        self.idf_oov = np.log(1.0 + (self.N + 0.5) / 0.5)

    def score(self, qweights):
        scores = np.zeros(self.N)
        norm = self.k1 * (1.0 - self.b + self.b * self.dl / self.avgdl)
        for t, w in qweights.items():
            j = self.vocab.get(t)
            if j is None:
                continue
            s, e = self.X.indptr[j], self.X.indptr[j + 1]
            rows, tf = self.X.indices[s:e], self.X.data[s:e]
            scores[rows] += w * self.idf[j] * tf * (self.k1 + 1.0) / (tf + norm[rows])
        return scores

    def max_score(self, qweights):
        total = 0.0
        for t, w in qweights.items():
            idf = self.idf[self.vocab[t]] if t in self.vocab else self.idf_oov
            total += w * idf * (self.k1 + 1.0)
        return total


class TFIDFIndex:
    def __init__(self, docs_tokens):
        self.vec = TfidfVectorizer(analyzer=str.split, sublinear_tf=True, norm="l2")
        self.M = self.vec.fit_transform([" ".join(t) for t in docs_tokens]).tocsr()
        self.vocab, self.idf, self.N = self.vec.vocabulary_, self.vec.idf_, self.M.shape[0]

    def score(self, qweights):
        cols, vals = [], []
        for t, w in qweights.items():
            j = self.vocab.get(t)
            if j is not None:
                cols.append(j)
                vals.append(w * self.idf[j])
        if not cols:
            return np.zeros(self.N)
        q = np.zeros(len(self.vocab))
        q[cols] = vals
        q /= np.linalg.norm(q)
        return np.asarray(self.M.dot(q)).ravel()

    def max_score(self, qweights):
        return 1.0


# ---------------------------------------------------------------------------
# Guardrail dan RAG
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """Kamu adalah AyatQu, alat bantu pencarian ayat Al-Qur'an berdasarkan topik.

Aturan yang tidak boleh dilanggar:
1. Gunakan HANYA ayat yang diberikan pada bagian KONTEKS. Jangan menambahkan ayat lain dan jangan mengutip dari ingatanmu.
2. Tugasmu hanya menjelaskan secara singkat (2 sampai 4 kalimat) mengapa ayat-ayat tersebut berkaitan dengan pertanyaan pengguna, berdasarkan isi terjemahan yang diberikan.
3. Jangan menafsirkan, jangan menyimpulkan makna di luar teks terjemahan, jangan menyebut pendapat ulama atau ahli tafsir.
4. Jangan memberi hukum, fatwa, atau penilaian halal, haram, wajib, dosa, dan sejenisnya.
5. Rujuk setiap ayat dengan format (QS. Nama-Surah nomor-surah:nomor-ayat), contoh (QS. Al-Baqarah 2:153).
6. Jangan menulis teks Arab.
7. Akhiri dengan satu kalimat yang mengarahkan pengguna ke tafsir resmi atau ulama untuk pemahaman lebih lanjut.
8. Gunakan bahasa Indonesia yang sopan dan sederhana."""

REFUSAL_FATWA = ("AyatQu adalah alat bantu pencarian ayat dan tidak memberikan hukum atau fatwa. "
                 "Berikut ayat-ayat yang berkaitan dengan topik pertanyaanmu. "
                 "Untuk hukumnya, silakan bertanya kepada ulama atau lembaga fatwa yang terpercaya.")
NOT_FOUND = "Maaf, AyatQu tidak menemukan ayat yang sesuai dengan pertanyaan tersebut. Coba gunakan kata kunci topik yang lain."
FOOTNOTE = "AyatQu adalah alat bantu pencarian, bukan sumber tafsir atau fatwa."

_CITE = re.compile(r"(\d{1,3})\s*:\s*(\d{1,3})(?:\s*[-\u2013]\s*(\d{1,3}))?")
_BANNED = re.compile(r"\b(menurut (para )?(ulama|ahli tafsir|mufassir|tafsir)|tafsirnya|hukumnya|berdosa|haram hukumnya|halal hukumnya|wajib hukumnya|fatwa)\b", re.I)
_ARAB = re.compile(r"[\u0600-\u06FF]")


def is_ruling_request(q):
    t = clean_text(q)
    explicit_ayat = bool(re.match(r"^(ayat|surah|surat|carikan ayat|cari ayat)\b", t))
    strong = re.search(r"\b(apakah|apa)\b.*\b(halal|haram|boleh|dosa|wajib|makruh|sah|batal)\b", t) \
        or re.search(r"\b(halal atau haram|boleh atau tidak|boleh tidak|fatwa)\b", t)
    weak = re.search(r"\b(hukum|hukumnya|bolehkah|haramkah|halalkah|wajibkah)\b", t)
    return bool(strong) or (bool(weak) and not explicit_ayat)


class AyatQu:
    METHODS = {
        "BM25 + ekspansi (terbaik)": ("bm25", True),
        "BM25": ("bm25", False),
        "TF-IDF": ("tfidf", False),
        "TF-IDF + ekspansi": ("tfidf", True),
    }

    def __init__(self, root=ROOT):
        root = Path(root)
        cfg_path = root / "models" / "best_config.json"
        if not cfg_path.exists():
            raise FileNotFoundError("models/best_config.json tidak ditemukan. Jalankan dulu AyatQu_Pipeline.ipynb sampai selesai.")
        self.cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        self.config = self.cfg["preprocessing_config"]
        self.k1, self.b = float(self.cfg["k1"]), float(self.cfg["b"])
        self.qe_weight = float(self.cfg["qe_weight"])
        self.threshold = float(self.cfg["ambang_skor_ternormalisasi"])
        self.top_k = int(self.cfg.get("top_k", 5))
        # Jumlah ayat yang tampil dibuat dinamis: ayat dengan skor minimal (rasio x skor ayat teratas), maksimal sekian ayat
        self.rasio_relatif = float(self.cfg.get("rasio_skor_relatif", 0.6))
        self.maks_tampil = int(self.cfg.get("maks_ayat_tampil", 8))
        flags = CONFIGS[self.config]
        self.use_stop, self.use_stem = flags["stop"], flags["stem"]

        self.df = pd.read_csv(root / "data" / "processed" / "quran_master.csv", encoding="utf-8-sig", dtype=str, keep_default_na=False)
        for c in ["id", "surah_no", "ayat_no"]:
            self.df[c] = self.df[c].astype(int)
        assert len(self.df) == 6236, "Data harus berisi 6236 ayat"

        self.kamus = json.loads((root / "expansion_dict.json").read_text(encoding="utf-8"))["kamus"]
        self.stemmer = Stemmer(root / "data" / "processed" / "stem_cache.json") if self.use_stem else None

        tokens = [self.preprocess(t) for t in self.df["terjemahan"]]
        if self.stemmer:
            self.stemmer.save()
        self.indexes = {"bm25": BM25Index(tokens, self.k1, self.b), "tfidf": TFIDFIndex(tokens)}

    # ---- preprocessing ----
    def preprocess(self, text, is_query=False):
        toks = clean_text(text).split()
        if is_query:
            toks = [t for t in toks if t not in QUERY_STOPWORDS]
        if self.use_stop:
            toks = [t for t in toks if t not in STOPWORDS]
        if self.use_stem:
            toks = [self.stemmer.stem(t) for t in toks]
        return toks

    # ---- ekspansi kueri ----
    def expansion_terms(self, query):
        q_tokens = self.preprocess(query, is_query=True)
        matched, extra, covered = [], [], set()
        for g in self.kamus:
            hit = False
            for key in g["kunci"]:
                kt = self.preprocess(key, is_query=True)
                if kt and any(q_tokens[i:i + len(kt)] == kt for i in range(len(q_tokens) - len(kt) + 1)):
                    hit = True
                    covered.update(kt)
                    break
            if hit:
                matched.append(g["topik"])
                for term in g["istilah"]:
                    for tok in self.preprocess(term, is_query=True):
                        if tok not in q_tokens and tok not in extra:
                            extra.append(tok)
        return q_tokens, extra, matched, covered

    def build_qweights(self, query, use_qe):
        q_tokens, extra, matched, covered = self.expansion_terms(query)
        qw = {}
        for t in q_tokens:
            qw[t] = qw.get(t, 0.0) + 1.0
        if use_qe:
            for t in extra:
                qw[t] = qw.get(t, 0.0) + self.qe_weight
        return qw, q_tokens, (extra if use_qe else []), (matched if use_qe else []), (covered if use_qe else set())

    # ---- pencarian ----
    def search(self, query, method="bm25", use_qe=True, k=None):
        k = k or self.top_k
        idx = self.indexes[method]
        qw, _, _, _, covered = self.build_qweights(query, use_qe)
        scores = idx.score(qw)
        order = [i for i in np.argsort(-scores, kind="stable")[:k] if scores[i] > 0]
        norm_qw = {t: w for t, w in qw.items() if not (t in covered and t not in idx.vocab)}
        max_s = idx.max_score(norm_qw)
        return [{"id": int(self.df.iloc[i]["id"]), "score": float(scores[i]),
                 "norm_score": float(scores[i] / max_s) if max_s > 0 else 0.0} for i in order]

    def select_relevant(self, hits):
        """Pertahankan hanya ayat yang skornya cukup dekat dengan ayat teratas. Minimal 1 ayat."""
        if not hits:
            return hits
        batas = self.rasio_relatif * hits[0]["score"]
        return [h for h in hits if h["score"] >= batas][: self.maks_tampil]

    def explain_query(self, query, use_qe=True):
        _, q_tokens, extra, matched, _ = self.build_qweights(query, use_qe)
        return {"token_kueri": q_tokens, "topik_kamus_cocok": matched, "istilah_ekspansi": extra}

    # ---- tampilan ayat (selalu dari tabel asli) ----
    def verse(self, ayat_id):
        r = self.df.iloc[ayat_id - 1]
        return {"id": int(r["id"]), "surah_no": int(r["surah_no"]), "surah_nama": r["surah_nama"],
                "ayat_no": int(r["ayat_no"]), "teks_arab": r["teks_arab"], "terjemahan": r["terjemahan"]}

    def ref_label(self, ayat_id):
        v = self.verse(ayat_id)
        return f"QS. {v['surah_nama']} {v['surah_no']}:{v['ayat_no']}"

    # ---- RAG ----
    def build_user_prompt(self, query, hits):
        ctx = "\n".join(f"[{self.verse(h['id'])['surah_no']}:{self.verse(h['id'])['ayat_no']}] "
                        f"({self.verse(h['id'])['surah_nama']}) {self.verse(h['id'])['terjemahan']}" for h in hits)
        return f"Pertanyaan pengguna: {query}\n\nKONTEKS (terjemahan ayat hasil pencarian):\n{ctx}\n\nTulis ringkasan keterkaitan sesuai aturan."

    def validate_answer(self, text, hits):
        allowed = {(self.verse(h["id"])["surah_no"], self.verse(h["id"])["ayat_no"]) for h in hits}
        cited = set()
        for m in _CITE.finditer(text):
            s, a1 = int(m.group(1)), int(m.group(2))
            a2 = int(m.group(3)) if m.group(3) else a1
            for a in range(a1, max(a1, a2) + 1):
                cited.add((s, a))
        di_luar = sorted(cited - allowed)
        flagged = _BANNED.findall(text)
        out = {"rujukan_di_luar_hasil": di_luar, "ada_frasa_tafsir_hukum": bool(flagged), "ada_teks_arab": bool(_ARAB.search(text))}
        out["lolos"] = (not di_luar) and (not flagged) and (not out["ada_teks_arab"])
        return out

    def offline_summary(self, query, hits):
        topik = " ".join(self.preprocess(query, is_query=True)) or "topik yang ditanyakan"
        refs = ", ".join(f"({self.ref_label(h['id'])})" for h in hits)
        return (f"Ayat-ayat berikut memuat kata-kata yang berkaitan dengan \"{topik}\": {refs}. "
                "Silakan membaca terjemahan lengkapnya pada kartu ayat. "
                "Untuk pemahaman lebih lanjut, rujuklah tafsir resmi atau ulama.")

    def answer(self, query, llm_fn=None, method="bm25", use_qe=True, k=None, max_retry=1):
        """
        llm_fn: fungsi (system, user) -> str. Bila None, dipakai ringkasan cadangan tanpa model bahasa.
        k: bila None, jumlah ayat ditentukan otomatis (hanya yang relevan). Bila diisi, dipakai jumlah tetap k.
        status: ok, ringkasan_cadangan, tidak_ditemukan, ditolak_fatwa
        """
        if k is None:
            hits = self.select_relevant(self.search(query, method=method, use_qe=use_qe, k=self.maks_tampil))
        else:
            hits = self.search(query, method=method, use_qe=use_qe, k=k)
        layak = bool(hits) and hits[0]["norm_score"] >= self.threshold
        res = {"query": query, "status": None, "hits": hits if layak else [], "ringkasan": "", "validasi": None, "lemah": bool(hits) and not layak}
        if is_ruling_request(query):
            res.update(status="ditolak_fatwa", ringkasan=REFUSAL_FATWA)
            return res
        if not layak:
            res.update(status="tidak_ditemukan", ringkasan=NOT_FOUND)
            return res
        if llm_fn is not None:
            for _ in range(max_retry + 1):
                try:
                    teks = llm_fn(SYSTEM_PROMPT, self.build_user_prompt(query, hits))
                except Exception as e:
                    res["catatan"] = f"Model bahasa gagal dipanggil: {type(e).__name__}"
                    break
                v = self.validate_answer(teks, hits)
                if v["lolos"]:
                    res.update(status="ok", ringkasan=teks, validasi=v)
                    return res
        teks = self.offline_summary(query, hits)
        res.update(status="ringkasan_cadangan", ringkasan=teks, validasi=self.validate_answer(teks, hits))
        return res


def make_anthropic_llm(model=None, api_key=None):
    """Pembungkus opsional. Perlu: pip install anthropic dan ANTHROPIC_API_KEY. Periksa nama model terbaru di dokumentasi."""
    import os
    from anthropic import Anthropic
    client = Anthropic(api_key=api_key) if api_key else Anthropic()
    model = model or os.environ.get("AYATQU_MODEL", "claude-haiku-5-5")

    def llm(system, user):
        msg = client.messages.create(model=model, max_tokens=400, temperature=0, system=system,
                                     messages=[{"role": "user", "content": user}])
        return msg.content[0].text
    return llm
