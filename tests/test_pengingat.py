"""Unit test pengingat haul & nisab (zakatku.pengingat, zakatku.model).

Haul adalah 1 tahun Hijriah = 354 hari. Semua tanggal di bawah
dihitung tangan dari tanggal mulai, bukan dari fungsi yang dites.
"""

import unittest
from datetime import date

from zakatku import model, pengingat


class TestTanggalHaul(unittest.TestCase):
    def test_haul_adalah_354_hari(self):
        self.assertEqual(pengingat.HAUL_HARI, 354)

    def test_haul_dari_14_november_2026(self):
        # 14 Nov 2026 + 354 hari = 3 Nov 2027.
        self.assertEqual(
            pengingat.tanggal_haul(date(2026, 11, 14)),
            date(2027, 11, 3),
        )

    def test_haul_dari_1_januari_2026(self):
        # 1 Jan 2026 + 354 hari = 21 Des 2026 (2026 bukan tahun kabisat).
        self.assertEqual(
            pengingat.tanggal_haul(date(2026, 1, 1)),
            date(2026, 12, 21),
        )

    def test_haul_dari_15_november_2025(self):
        # Contoh dari smoke test Sesi 1: 15 Nov 2025 + 354 hari = 4 Nov 2026.
        self.assertEqual(
            pengingat.tanggal_haul(date(2025, 11, 15)),
            date(2026, 11, 4),
        )


class TestStatusHaul(unittest.TestCase):
    def test_belum_haul(self):
        # Harta mencapai nisab 14 Nov 2026; dicek 15 Nov 2026:
        # haul 3 Nov 2027, masih 353 hari lagi.
        status = pengingat.status_haul(date(2026, 11, 14), date(2026, 11, 15))
        self.assertEqual(status["tanggal_mulai"], date(2026, 11, 14))
        self.assertEqual(status["tanggal_haul"], date(2027, 11, 3))
        self.assertFalse(status["sudah_haul"])
        self.assertEqual(status["hari_lagi"], 353)

    def test_sehari_sebelum_haul(self):
        # Dicek 2 Nov 2027: haul besok, 1 hari lagi.
        status = pengingat.status_haul(date(2026, 11, 14), date(2027, 11, 2))
        self.assertFalse(status["sudah_haul"])
        self.assertEqual(status["hari_lagi"], 1)

    def test_tepat_di_hari_haul(self):
        # Dicek tepat 3 Nov 2027: hari_lagi 0, sudah haul.
        status = pengingat.status_haul(date(2026, 11, 14), date(2027, 11, 3))
        self.assertTrue(status["sudah_haul"])
        self.assertEqual(status["hari_lagi"], 0)

    def test_sudah_haul(self):
        # Harta mencapai nisab 15 Nov 2025; dicek 15 Nov 2026:
        # haul 4 Nov 2026, sudah lewat 11 hari.
        status = pengingat.status_haul(date(2025, 11, 15), date(2026, 11, 15))
        self.assertEqual(status["tanggal_haul"], date(2026, 11, 4))
        self.assertTrue(status["sudah_haul"])
        self.assertEqual(status["hari_lagi"], -11)


class TestHitungMundurFitrah(unittest.TestCase):
    def test_125_hari_menuju_idulfitri(self):
        # 15 Nov 2026 -> 20 Mar 2027: 15 (sisa Nov) + 31 (Des)
        # + 31 (Jan) + 28 (Feb 2027) + 20 (Mar) = 125 hari.
        self.assertEqual(
            pengingat.hitung_mundur_fitrah(date(2027, 3, 20), date(2026, 11, 15)),
            125,
        )

    def test_idulfitri_hari_ini(self):
        self.assertEqual(
            pengingat.hitung_mundur_fitrah(date(2026, 11, 15), date(2026, 11, 15)),
            0,
        )

    def test_idulfitri_sudah_lewat(self):
        # Idulfitri 20 Mar 2026, dicek 15 Nov 2026: sudah lewat 240 hari.
        self.assertEqual(
            pengingat.hitung_mundur_fitrah(date(2026, 3, 20), date(2026, 11, 15)),
            -240,
        )


class TestCatatHarta(unittest.TestCase):
    def setUp(self):
        self.data = model._data_kosong()

    def test_harta_terakhir_kosong_adalah_none(self):
        self.assertIsNone(model.harta_terakhir(self.data))
        self.assertEqual(self.data["harta"], [])

    def test_catat_harta_menyimpan_entri(self):
        entri = model.catat_harta(self.data, "2026-11-14", 250_000_000, 10)
        self.assertEqual(entri["tanggal"], "2026-11-14")
        self.assertEqual(entri["tabungan"], 250_000_000)
        self.assertEqual(entri["emas_gram"], 10)
        self.assertEqual(len(self.data["harta"]), 1)

    def test_harta_terakhir_adalah_catatan_terbaru(self):
        model.catat_harta(self.data, "2025-11-15", 250_000_000, 10)
        model.catat_harta(self.data, "2026-11-14", 300_000_000, 0)
        terakhir = model.harta_terakhir(self.data)
        self.assertEqual(terakhir["tanggal"], "2026-11-14")
        self.assertEqual(terakhir["tabungan"], 300_000_000)
        self.assertEqual(len(self.data["harta"]), 2)

    def test_catat_harta_tidak_menyentuh_pembayaran(self):
        model.catat_harta(self.data, "2026-11-14", 250_000_000, 10)
        self.assertEqual(self.data["pembayaran"], [])


if __name__ == "__main__":
    unittest.main()
