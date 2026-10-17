<div align="center">

# 📖 AyatQu

### Temukan ayat Al-Qur'an dari topik yang kamu ingat, cukup dengan bahasa sehari-hari.

**[🚀 Coba AyatQu Sekarang](https://ayatqu.streamlit.app/)**

</div>

---

## ✨ Apa itu AyatQu?

Pernah ingat topiknya tapi lupa nama surah dan nomor ayatnya? AyatQu dibuat untuk situasi itu.

Ketik saja pertanyaanmu, misalnya **"ayat tentang sabar"** atau **"ayat tentang berbakti kepada orang tua"**. AyatQu akan menampilkan ayat yang paling terkait lengkap dengan **teks Arab, terjemahan Indonesia, nama surah, dan nomor ayat**, lalu memberi ringkasan singkat tentang mengapa ayat tersebut cocok dengan pertanyaanmu.

> ⚠️ **AyatQu adalah alat bantu pencarian, bukan sumber tafsir atau fatwa.** Untuk pemahaman yang lebih dalam dan untuk urusan hukum, rujuklah tafsir resmi dan ulama yang terpercaya.

## 🎯 Masalah yang Ingin Diselesaikan

Pencarian biasa hanya berhasil kalau kata yang kamu ketik sama persis dengan kata di terjemahan. Padahal bahasa sehari-hari sering berbeda. Contohnya, kata *"syukur"* dan *"tawakal"* tidak muncul di terjemahan Kementerian Agama RI, yang ada adalah *"bersyukur"* dan *"bertawakkal"*.

AyatQu menjembatani perbedaan ini dengan **perluasan kueri**: kata dari pengguna dicocokkan dengan kamus istilah awam, lalu diperluas ke kata-kata yang benar-benar dipakai di terjemahan.

## 🚀 Cara Mencoba

1. Buka **[ayatqu.streamlit.app](https://ayatqu.streamlit.app/)**.
2. Klik **Coba Sekarang**, lalu tulis topik atau pertanyaanmu di kolom chat.
3. Baca ayat yang muncul beserta ringkasan keterkaitannya.

> 💤 Aplikasi gratis di Streamlit bisa tertidur saat lama tidak dipakai. Kalau muncul tombol untuk membangunkannya, klik saja lalu tunggu beberapa saat.

### Contoh pertanyaan

| Kamu menulis | AyatQu mencari |
|---|---|
| `ayat tentang sabar` | Ayat yang membahas kesabaran |
| `ayat tentang berbakti kepada orang tua` | Ayat tentang berbuat baik kepada ibu bapak |
| `ayat tentang rezeki` | Ayat tentang rezeki dan karunia Allah |
| `ayat yang bikin hati tenang` | Ayat tentang ketenangan hati |

### Tips menulis pertanyaan

- Sebutkan **topiknya dengan jelas**, misalnya "ayat tentang sabar saat ujian".
- Pakai **kata yang umum**, tidak perlu istilah Arab.
- Kalau hasilnya kurang pas, coba **ganti kata kuncinya** dengan sinonim.

## 🧭 Isi Aplikasi

| Halaman | Isinya |
|---|---|
| 🏠 **Beranda** | Pengenalan singkat dan tombol untuk mulai mencoba |
| 🔎 **Pencarian Ayat** | Chatbot pencari ayat, lengkap dengan panduan cara mencari |
| 📊 **Evaluasi** | Hasil pengujian dan perbandingan metode pencarian |
| 📝 **Ringkasan** | Temuan utama, alur sistem, dan kesimpulan |
| ℹ️ **Tentang Aplikasi** | Latar belakang, teknologi, sumber data, dan penulis |

## ⚙️ Bagaimana AyatQu Bekerja

```mermaid
flowchart LR
    A[Pertanyaanmu] --> B[Pembersihan kata]
    B --> C[Perluasan kueri dengan kamus istilah awam]
    C --> D[Pencarian BM25 pada 6.236 ayat]
    D --> E[Penyaringan ayat yang relevan]
    E --> F[Ayat ditampilkan dari data asli]
    F --> G[Ringkasan keterkaitan]
```

1. **Pembersihan kata.** Pertanyaanmu dirapikan dan diubah ke bentuk dasar kata agar mudah dicocokkan.
2. **Perluasan kueri.** Kata sehari-hari diperluas ke kata yang dipakai di terjemahan, sehingga "syukur" juga menemukan ayat dengan kata "bersyukur".
3. **Pencarian BM25.** Setiap ayat diberi skor kecocokan dengan pertanyaanmu, lalu diurutkan.
4. **Penyaringan.** Hanya ayat dengan skor cukup tinggi yang ditampilkan. Jika tidak ada yang cocok, AyatQu jujur menjawab bahwa ayat tidak ditemukan.
5. **Tampil dari data asli.** Teks Arab dan terjemahan selalu diambil langsung dari sumbernya dan tidak pernah ditulis ulang oleh AI.
6. **Ringkasan keterkaitan.** Ringkasan singkat hanya berdasarkan ayat yang ditemukan, tanpa tafsir.

### Dibuat dengan prinsip kehati-hatian

- 🔒 **Ayat tidak diubah.** Teks Arab dan terjemahan tampil persis seperti sumber aslinya.
- 🚫 **Tidak memberi fatwa.** Pertanyaan seperti "apakah ini haram?" tidak dijawab dengan hukum, AyatQu hanya menawarkan ayat yang terkait.
- ✅ **Rujukan diperiksa.** Ringkasan hanya boleh menyebut ayat yang memang ditemukan oleh pencarian.
- 🙋 **Jujur saat tidak tahu.** Pertanyaan di luar topik dijawab dengan "tidak ditemukan", bukan dipaksakan.

## 🛠️ Teknologi

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)

**Metode:** Information Retrieval, BM25, TF-IDF, Query Expansion, Retrieval-Augmented Generation (RAG), dan stemming bahasa Indonesia dengan PySastrawi.

## 📚 Sumber Data

Teks Al-Qur'an (Uthmani) dan terjemahan Indonesia dari Kementerian Agama RI, diambil dari [Tanzil.net](https://tanzil.net).

## 📝 Catatan

AyatQu adalah proyek akademik yang masih terus dikembangkan, sehingga hasil pencarian belum tentu sempurna. Gunakan hasilnya sebagai titik awal, lalu pastikan pemahamanmu melalui sumber dan ulama yang terpercaya.

## 👩‍💻 Penulis

**Kayla Verda Fawnia Heses**
NIM: A11.2024.15689
Proyek mata kuliah **Sistem Temu Kembali Informasi (STKI)**

---

<div align="center">

*AyatQu adalah alat bantu pencarian, bukan sumber tafsir atau fatwa.*

</div>
