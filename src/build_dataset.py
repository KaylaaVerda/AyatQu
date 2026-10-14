"""
build_dataset.py
Menggabungkan terjemahan (dan teks Arab bila tersedia) menjadi satu tabel.
File di data/raw/ HANYA DIBACA, tidak pernah ditulis ulang.

Format baris Tanzil: nomor_surah|nomor_ayat|teks
Teks Arab (opsional): data/raw/quran-uthmani.txt (format sama, dari Tanzil.net)
"""
from pathlib import Path
import unicodedata
import pandas as pd

RAW = Path("data/raw")
OUT = Path("data/processed")
OUT.mkdir(parents=True, exist_ok=True)

SURAH_NAMA = ["Al-Fatihah","Al-Baqarah","Ali 'Imran","An-Nisa'","Al-Ma'idah","Al-An'am","Al-A'raf","Al-Anfal","At-Taubah","Yunus","Hud","Yusuf","Ar-Ra'd","Ibrahim","Al-Hijr","An-Nahl","Al-Isra'","Al-Kahf","Maryam","Taha","Al-Anbiya'","Al-Hajj","Al-Mu'minun","An-Nur","Al-Furqan","Asy-Syu'ara'","An-Naml","Al-Qasas","Al-'Ankabut","Ar-Rum","Luqman","As-Sajdah","Al-Ahzab","Saba'","Fatir","Yasin","As-Saffat","Sad","Az-Zumar","Gafir","Fussilat","Asy-Syura","Az-Zukhruf","Ad-Dukhan","Al-Jasiyah","Al-Ahqaf","Muhammad","Al-Fath","Al-Hujurat","Qaf","Az-Zariyat","At-Tur","An-Najm","Al-Qamar","Ar-Rahman","Al-Waqi'ah","Al-Hadid","Al-Mujadalah","Al-Hasyr","Al-Mumtahanah","As-Saff","Al-Jumu'ah","Al-Munafiqun","At-Tagabun","At-Talaq","At-Tahrim","Al-Mulk","Al-Qalam","Al-Haqqah","Al-Ma'arij","Nuh","Al-Jinn","Al-Muzzammil","Al-Muddassir","Al-Qiyamah","Al-Insan","Al-Mursalat","An-Naba'","An-Nazi'at","'Abasa","At-Takwir","Al-Infitar","Al-Mutaffifin","Al-Insyiqaq","Al-Buruj","At-Tariq","Al-A'la","Al-Gasyiyah","Al-Fajr","Al-Balad","Asy-Syams","Al-Lail","Ad-Duha","Asy-Syarh","At-Tin","Al-'Alaq","Al-Qadr","Al-Bayyinah","Az-Zalzalah","Al-'Adiyat","Al-Qari'ah","At-Takasur","Al-'Asr","Al-Humazah","Al-Fil","Quraisy","Al-Ma'un","Al-Kausar","Al-Kafirun","An-Nasr","Al-Masad","Al-Ikhlas","Al-Falaq","An-Nas"]
assert len(SURAH_NAMA) == 114

def read_tanzil(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip() or line.startswith("#"):
                continue  # lewati baris kosong dan blok komentar lisensi
            s, a, teks = line.split("|", 2)
            rows.append((int(s), int(a), teks))
    return pd.DataFrame(rows, columns=["surah_no", "ayat_no", "teks"])


def _kerangka(kata):
    """Hilangkan harakat dan tatwil, hanya untuk MEMBANDINGKAN, bukan untuk disimpan."""
    return "".join(c for c in kata if unicodedata.category(c) != "Mn" and c != "\u0640")

BASMALAH_KERANGKA = ["بسم", "ٱلله", "ٱلرحمن", "ٱلرحيم"]

def buang_basmalah(surah_no, ayat_no, teks):
    """
    File Uthmani Tanzil menempelkan basmalah di depan ayat 1 setiap surah.
    Basmalah bukan ayat tersendiri (kecuali Al-Fatihah:1), jadi dibuang dari ayat 1
    surah 2 sampai 114 (At-Taubah memang tidak punya). Hanya awalan 4 kata yang dibuang,
    sisa teks Arab tidak diubah sama sekali.
    """
    if ayat_no != 1 or surah_no in (1, 9):
        return teks
    kata = teks.split(" ")
    assert [_kerangka(k) for k in kata[:4]] == BASMALAH_KERANGKA, f"Basmalah tidak ditemukan di {surah_no}:1"
    sisa = " ".join(kata[4:])
    assert sisa.strip(), f"Ayat {surah_no}:1 kosong setelah basmalah dibuang"
    return sisa

terj = read_tanzil(RAW / "id_indonesian.txt").rename(columns={"teks": "terjemahan"})
arab_path = RAW / "quran-uthmani.txt"
if arab_path.exists():
    arab = read_tanzil(arab_path)
    arab["teks"] = [buang_basmalah(s, a, t) for s, a, t in zip(arab.surah_no, arab.ayat_no, arab.teks)]
    arab = arab.rename(columns={"teks": "teks_arab"})
    df = terj.merge(arab, on=["surah_no", "ayat_no"], how="outer", validate="1:1", indicator=True)
    assert (df["_merge"] == "both").all(), "Ada ayat yang tidak cocok antara file Arab dan terjemahan"
    df = df.drop(columns="_merge")
else:
    print("PERINGATAN: quran-uthmani.txt belum ada, kolom teks_arab dikosongkan.")
    df = terj.assign(teks_arab="")

df = df.sort_values(["surah_no", "ayat_no"]).reset_index(drop=True)
df["id"] = range(1, len(df) + 1)
df["surah_nama"] = df["surah_no"].map(lambda n: SURAH_NAMA[n - 1])
df = df[["id", "surah_no", "surah_nama", "ayat_no", "teks_arab", "terjemahan"]]

# ---------- VALIDASI ----------
JUMLAH_AYAT = [7,286,200,176,120,165,206,75,129,109,123,111,43,52,99,128,111,110,98,135,112,78,118,64,77,227,93,88,69,60,34,30,73,54,45,83,182,88,75,85,54,53,89,59,37,35,38,29,18,45,60,49,62,55,78,96,29,22,24,13,14,11,11,18,12,12,30,52,52,44,28,28,20,56,40,31,50,40,46,42,29,19,36,25,22,17,19,26,30,20,15,21,11,8,8,19,5,8,8,11,11,8,3,9,5,4,7,3,6,3,5,4,5,6]
assert len(df) == 6236, f"Jumlah ayat {len(df)}, seharusnya 6236"
assert df["surah_no"].nunique() == 114, "Jumlah surah bukan 114"
per_surah = df.groupby("surah_no").size().tolist()
assert per_surah == JUMLAH_AYAT, "Jumlah ayat per surah tidak sesuai standar"
assert not df.duplicated(["surah_no", "ayat_no"]).any(), "Ada duplikat"
assert df["terjemahan"].str.strip().ne("").all(), "Ada terjemahan kosong"
if arab_path.exists():
    assert df["teks_arab"].str.strip().ne("").all(), "Ada teks Arab kosong"

df.to_csv(OUT / "quran_master.csv", index=False, encoding="utf-8-sig")
print(f"OK: {len(df)} ayat, {df['surah_no'].nunique()} surah -> {OUT/'quran_master.csv'}")
