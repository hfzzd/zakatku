"""Unit test aturan hitung zakat (zakatku.zakat).

Harga acuan yang dipakai di sini sama dengan bawaan aplikasi:
emas Rp2.509.000/gram (Antam, 13 Nov 2026), beras Rp13.693/kg
(Bapanas, 12 Nov 2026). Semua angka di bawah cocok hitungan tangan.
"""

import unittest

from zakatku import zakat

HARGA_EMAS = 2_509_000
HARGA_BERAS = 13_693


class TestNisab(unittest.TestCase):
    def test_nisab_tahunan_85_gram_emas(self):
        # 85 x Rp2.509.000 = Rp213.265.000
        self.assertEqual(zakat.nisab_tahunan(HARGA_EMAS), 213_265_000)

    def test_nisab_bulanan_sepertiga_dua_belas_tahunan(self):
        # Rp213.265.000 / 12 = Rp17.772.083,33...
        self.assertAlmostEqual(
            zakat.nisab_bulanan(HARGA_EMAS), 213_265_000 / 12
        )
        # Ditampilkan dibulatkan: Rp17.772.083
        self.assertEqual(
            zakat.format_rupiah(zakat.nisab_bulanan(HARGA_EMAS)),
            "Rp17.772.083",
        )

    def test_nisab_tahunan_mengikuti_harga_emas(self):
        self.assertEqual(zakat.nisab_tahunan(3_000_000), 255_000_000)


class TestZakatProfesi(unittest.TestCase):
    def test_wajib_20_juta(self):
        # 2,5% x Rp20.000.000 = Rp500.000 (>= nisab bulanan Rp17.772.083)
        hasil = zakat.zakat_profesi(20_000_000, HARGA_EMAS)
        self.assertTrue(hasil["wajib"])
        self.assertEqual(hasil["jumlah"], 500_000)

    def test_belum_wajib_10_juta(self):
        # Rp10.000.000 < nisab bulanan Rp17.772.083
        hasil = zakat.zakat_profesi(10_000_000, HARGA_EMAS)
        self.assertFalse(hasil["wajib"])
        self.assertEqual(hasil["jumlah"], 0)

    def test_wajib_tepat_di_nisab(self):
        nisab = zakat.nisab_bulanan(HARGA_EMAS)
        hasil = zakat.zakat_profesi(nisab, HARGA_EMAS)
        self.assertTrue(hasil["wajib"])
        self.assertEqual(hasil["jumlah"], 444_302)  # 2,5% x Rp17.772.083,33

    def test_belum_wajib_se_rupiah_di_bawah_nisab(self):
        nisab = zakat.nisab_bulanan(HARGA_EMAS)
        hasil = zakat.zakat_profesi(nisab - 1, HARGA_EMAS)
        self.assertFalse(hasil["wajib"])
        self.assertEqual(hasil["jumlah"], 0)


class TestZakatFitrah(unittest.TestCase):
    def test_per_jiwa(self):
        # 2,5 kg x Rp13.693 = Rp34.232,5 -> dibulatkan setengah ke atas
        # menjadi Rp34.233 (bukan Rp34.232 seperti banker's rounding).
        hasil = zakat.zakat_fitrah(1, HARGA_BERAS)
        self.assertEqual(hasil["per_jiwa"], 34_233)
        self.assertEqual(hasil["jumlah"], 34_233)
        self.assertEqual(hasil["total_kg"], 2.5)

    def test_empat_jiwa(self):
        # 4 x Rp34.233 = Rp136.932
        hasil = zakat.zakat_fitrah(4, HARGA_BERAS)
        self.assertEqual(hasil["per_jiwa"], 34_233)
        self.assertEqual(hasil["jumlah"], 136_932)
        self.assertEqual(hasil["total_kg"], 10.0)

    def test_mengikuti_harga_beras(self):
        # 2,5 kg x Rp14.000 = Rp35.000 per jiwa
        hasil = zakat.zakat_fitrah(2, 14_000)
        self.assertEqual(hasil["per_jiwa"], 35_000)
        self.assertEqual(hasil["jumlah"], 70_000)


class TestZakatMal(unittest.TestCase):
    def test_wajib_tabungan_250_juta_emas_10_gram(self):
        # Total harta: Rp250.000.000 + 10 x Rp2.509.000 = Rp275.090.000
        # >= nisab Rp213.265.000 -> 2,5% = Rp6.877.250
        hasil = zakat.zakat_mal(250_000_000, 10, HARGA_EMAS)
        self.assertTrue(hasil["wajib"])
        self.assertEqual(hasil["nilai_emas"], 25_090_000)
        self.assertEqual(hasil["total"], 275_090_000)
        self.assertEqual(hasil["jumlah"], 6_877_250)

    def test_wajib_tanpa_emas(self):
        # Tabungan Rp250.000.000 saja sudah di atas nisab.
        hasil = zakat.zakat_mal(250_000_000, 0, HARGA_EMAS)
        self.assertTrue(hasil["wajib"])
        self.assertEqual(hasil["total"], 250_000_000)
        self.assertEqual(hasil["jumlah"], 6_250_000)

    def test_belum_wajib_tabungan_100_juta(self):
        # Rp100.000.000 < nisab Rp213.265.000
        hasil = zakat.zakat_mal(100_000_000, 0, HARGA_EMAS)
        self.assertFalse(hasil["wajib"])
        self.assertEqual(hasil["jumlah"], 0)

    def test_belum_wajib_tabungan_kecil_tapi_emas_besar(self):
        # Rp50.000.000 + 50 gram emas (Rp125.450.000) = Rp175.450.000
        # masih di bawah nisab Rp213.265.000.
        hasil = zakat.zakat_mal(50_000_000, 50, HARGA_EMAS)
        self.assertFalse(hasil["wajib"])
        self.assertEqual(hasil["total"], 175_450_000)


class TestFormatRupiah(unittest.TestCase):
    def test_format_umum(self):
        self.assertEqual(zakat.format_rupiah(213_265_000), "Rp213.265.000")
        self.assertEqual(zakat.format_rupiah(136_932), "Rp136.932")
        self.assertEqual(zakat.format_rupiah(500_000), "Rp500.000")
        self.assertEqual(zakat.format_rupiah(0), "Rp0")

    def test_pembulatan_half_up_bukan_bankers_rounding(self):
        # 2,5 x Rp13.693 = Rp34.232,5 -> Rp34.233 (half-up),
        # bukan Rp34.232 (banker's rounding membulatkan ke genap).
        self.assertEqual(zakat.format_rupiah(34_232.5), "Rp34.233")
        self.assertEqual(zakat.format_rupiah(2.5), "Rp3")
        self.assertEqual(zakat.format_rupiah(3.5), "Rp4")


if __name__ == "__main__":
    unittest.main()
