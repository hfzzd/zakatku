"""Pengingat zakat: haul zakat mal, nisab profesi, dan Idulfitri.

Haul adalah 1 tahun Hijriah kepemilikan harta — dihitung 354 hari
(kalender Hijriah rata-rata 354,36 hari; selisih sehari dua hari
tidak mengubah kewajiban, tapi bila ragu tanyakan ke ustaz).
"""

from datetime import timedelta

# Satu tahun Hijriah ≈ 354 hari.
HAUL_HARI = 354


def tanggal_haul(tanggal_mulai):
    """Tanggal haul: 354 hari setelah harta mencapai nisab."""
    return tanggal_mulai + timedelta(days=HAUL_HARI)


def status_haul(tanggal_mulai, hari_ini):
    """Status haul dari tanggal harta pertama kali mencapai nisab.

    Mengembalikan dict dengan kunci: tanggal_mulai, tanggal_haul,
    sudah_haul (bool), hari_lagi (bisa negatif bila sudah lewat).
    """
    haul = tanggal_haul(tanggal_mulai)
    hari_lagi = (haul - hari_ini).days
    return {
        "tanggal_mulai": tanggal_mulai,
        "tanggal_haul": haul,
        "sudah_haul": hari_lagi <= 0,
        "hari_lagi": hari_lagi,
    }


def hitung_mundur_fitrah(tanggal_idulfitri, hari_ini):
    """Jumlah hari menuju Idulfitri (negatif bila sudah lewat)."""
    return (tanggal_idulfitri - hari_ini).days
