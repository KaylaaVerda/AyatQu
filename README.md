# AyatQu

Pengembangan Chatbot AyatQu untuk Pencarian Ayat Al-Qur'an Berbasis Topik Menggunakan Retrieval-Augmented Generation dengan Perbandingan TF-IDF dan BM25 serta Perluasan Kueri Bahasa Awam.

Proyek mata kuliah Sistem Temu Kembali Informasi (STKI). Repo ini berisi pipeline evaluasi dan aplikasi Streamlit multi-halaman untuk pencarian ayat.

## Cara menjalankan

Pasang dependensi dari folder proyek:

```bash
python -m pip install -r requirements.txt
```

Jalankan semua sel `AyatQu_Pipeline.ipynb` dari atas ke bawah untuk membangun data, konfigurasi, tabel evaluasi, dan grafik. Notebook harus dijalankan dari folder ini (atau subfoldernya). PySastrawi wajib dipasang agar konfigurasi stemming (C3 dan C4) ikut berjalan.

Setelah notebook selesai, jalankan chatbot:

```bash
python -m streamlit run app.py
```

Di Windows, bila perintah `python` tidak dikenali, gunakan launcher:

```powershell
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

Navigasi aplikasi berisi **Pencarian Ayat**, **Evaluasi**, **Ringkasan**, dan **Tentang Aplikasi**. Untuk memakai ringkasan model bahasa, isi API key pada widget password di halaman Pencarian Ayat. API key tidak perlu dimasukkan untuk menggunakan pencarian dan ringkasan lokal.

## Isi folder

```
ayatqu/
├── app.py                      entrypoint navigasi Streamlit
├── ui.py                       komponen UI, tema, dan loader data
├── views/                      empat halaman aplikasi
├── .streamlit/config.toml      tema Streamlit
├── ayatqu_core.py              mesin retrieval dan guardrail
├── AyatQu_Pipeline.ipynb        notebook utama (preprocessing sampai ekspor konfigurasi)
├── expansion_dict.json          kamus query expansion (untuk divalidasi dosen atau ustaz)
├── requirements.txt
├── data/
│   ├── raw/                     file asli Tanzil (JANGAN DIEDIT)
│   │   ├── id_indonesian.txt        terjemahan Indonesia (Kemenag RI)
│   │   └── quran-uthmani.txt        teks Arab Uthmani
│   ├── processed/
│   │   └── quran_master.csv         tabel gabungan 6.236 ayat (hasil src/build_dataset.py)
│   └── eval/
│       ├── queries.csv              36 kueri uji (30 topik + 6 luar topik), dengan split dev dan test
│       ├── qrels.csv                kunci jawaban DRAF (lihat peringatan di bawah)
│       ├── qrels_lembar_validasi.csv   lembar untuk dua penilai manusia
│       └── expansion_dict_report.csv   frekuensi tiap istilah kamus di korpus
├── src/build_dataset.py         membangun quran_master.csv dari file mentah (dengan validasi)
├── outputs/                     (terisi setelah notebook dijalankan) tabel hasil, rubrik chatbot, dll
├── figures/                     (terisi setelah notebook dijalankan) grafik untuk laporan
└── models/best_config.json      (terisi setelah notebook dijalankan) konfigurasi untuk aplikasi
```

## Peringatan penting

1. **`data/eval/qrels.csv` adalah DRAF yang dibuat oleh asisten AI** dengan membaca teks terjemahan. Berkas ini **belum divalidasi manusia**.
   Sebelum angka hasil dipakai di laporan atau diuji, serahkan `qrels_lembar_validasi.csv` ke dosen atau ustaz
   (idealnya dua penilai), hitung Cohen's kappa dengan `finalize_qrels_from_validation()`, lalu jalankan ulang notebook dengan `qrels_final.csv`.
2. **Kamus ekspansi** (`expansion_dict.json`) disusun manual dan perlu divalidasi.
3. Kunci jawaban dikumpulkan dengan pooling dari sistem yang diuji, sehingga cenderung menguntungkan BM25 + ekspansi.
4. Sistem ini alat bantu pencarian, **bukan sumber tafsir atau fatwa**.
5. Teks Arab dan terjemahan yang ditampilkan tidak pernah diubah. Pembersihan, stopword, dan stemming hanya pada salinan indexing.

## Sumber data

Tanzil.net: teks Al-Qur'an Uthmani dan terjemahan Indonesia dari Kementerian Agama RI. Baca ketentuan penggunaan di situs resminya,
lalu catat tanggal akses dan kutipan lisensinya di laporan. Terjemahan sumber memiliki typo huruf "I" kapital menggantikan "l"
(misalnya `SuIaiman`) pada 16 kata, yang hanya diperbaiki pada salinan indexing.
