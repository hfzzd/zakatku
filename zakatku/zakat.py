"""Aturan hitung zakat (fungsi murni, tanpa I/O).

Acuan yang dipakai adalah pendapat yang umum diamalkan di Indonesia:
nisab 85 gram emas, kadar zakat 2,5%, zakat fitrah 2,5 kg beras per jiwa.
Harga acuan (emas & beras) berasal dari config dan bisa diubah pengguna.
"""

from decimal import ROUND_HALF_UP, Decimal

KADAR_ZAKAT = 0.025
NISAB_EMAS_GRAM = 85
FITRAH_KG_PER_JIWA = 2.5

# Harga acuan bawaan — sesuaikan dengan harga pasar saat ini lewat
# `zakatku config atur`.
HARGA_EMAS_DEFAULT = 2_509_000  # Rp/gram, Antam Logam Mulia, 13 Nov 2026
HARGA_BERAS_DEFAULT = 13_693  # Rp/kg, beras medium Bapanas, 12 Nov 2026


def _bulat_rupiah(nilai):
    """Bulatkan ke rupiah terdekat, setengah ke atas (bukan banker's rounding)."""
    return int(Decimal(str(nilai)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def nisab_tahunan(harga_emas):
    """Nisab satu tahun: 85 gram emas dalam rupiah."""
    return NISAB_EMAS_GRAM * harga_emas


def nisab_bulanan(harga_emas):
    """Nisab bulanan zakat profesi: nisab tahunan dibagi 12."""
    return nisab_tahunan(harga_emas) / 12


def zakat_profesi(penghasilan, harga_emas):
    """Zakat profesi dari penghasilan satu bulan.

    Wajib bila penghasilan mencapai nisab bulanan; zakatnya 2,5% dari
    penghasilan. Mengembalikan dict dengan kunci: wajib, nisab,
    penghasilan, jumlah.
    """
    nisab = nisab_bulanan(harga_emas)
    wajib = penghasilan >= nisab
    jumlah = _bulat_rupiah(penghasilan * KADAR_ZAKAT) if wajib else 0
    return {
        "wajib": wajib,
        "nisab": nisab,
        "penghasilan": penghasilan,
        "jumlah": jumlah,
    }


def zakat_mal(tabungan, emas_gram, harga_emas):
    """Zakat mal dari tabungan dan emas.

    Total harta = tabungan + emas_gram × harga_emas. Wajib bila total
    harta mencapai nisab tahunan (85 gram emas) dan sudah haul 1 tahun;
    zakatnya 2,5% dari total harta. Mengembalikan dict dengan kunci:
    wajib, nisab, tabungan, emas_gram, nilai_emas, total, jumlah.
    """
    nilai_emas = emas_gram * harga_emas
    total = tabungan + nilai_emas
    nisab = nisab_tahunan(harga_emas)
    wajib = total >= nisab
    jumlah = _bulat_rupiah(total * KADAR_ZAKAT) if wajib else 0
    return {
        "wajib": wajib,
        "nisab": nisab,
        "tabungan": tabungan,
        "emas_gram": emas_gram,
        "nilai_emas": nilai_emas,
        "total": total,
        "jumlah": jumlah,
    }


def zakat_fitrah(jiwa, harga_beras):
    """Zakat fitrah: 2,5 kg beras per jiwa, dinilai dengan harga beras.

    Mengembalikan dict dengan kunci: jiwa, kg_per_jiwa, per_jiwa,
    total_kg, jumlah.
    """
    per_jiwa = _bulat_rupiah(FITRAH_KG_PER_JIWA * harga_beras)
    return {
        "jiwa": jiwa,
        "kg_per_jiwa": FITRAH_KG_PER_JIWA,
        "per_jiwa": per_jiwa,
        "total_kg": FITRAH_KG_PER_JIWA * jiwa,
        "jumlah": per_jiwa * jiwa,
    }


def format_rupiah(nilai):
    """Format angka menjadi 'Rp213.265.000' ala Indonesia."""
    return "Rp" + f"{_bulat_rupiah(nilai):,}".replace(",", ".")
