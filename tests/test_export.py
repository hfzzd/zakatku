"""Unit test ekspor CSV (zakatku.export).

Contoh angka laporan 2026 sama dengan contoh Day-1 (test_cli.py):
profesi Rp500.000 + fitrah Rp136.932 + mal Rp6.877.250
= Rp7.514.182.
"""

import csv
import io
import unittest

from zakatku import export

# Pembayaran contoh Day-1, sengaja tidak urut tanggal.
BAYAR_2026 = [
    {"jenis": "mal", "jumlah": 6_877_250, "tanggal": "2026-11-14",
     "catatan": "via bank"},
    {"jenis": "profesi", "jumlah": 500_000, "tanggal": "2026-11-14"},
    {"jenis": "fitrah", "jumlah": 136_932, "tanggal": "2026-03-20",
     "catatan": "4 jiwa"},
]


def _baris(teks_csv):
    """Urai teks CSV menjadi list baris (list kolom) untuk perbandingan."""
    return list(csv.reader(io.StringIO(teks_csv)))


class TestCsvPembayaran(unittest.TestCase):
    def test_header(self):
        baris = _baris(export.csv_pembayaran([]))
        self.assertEqual(baris, [["tanggal", "jenis", "jumlah", "catatan"]])

    def test_diurutkan_berdasarkan_tanggal(self):
        baris = _baris(export.csv_pembayaran(BAYAR_2026))
        self.assertEqual(
            [b[0] for b in baris[1:]],
            ["2026-03-20", "2026-11-14", "2026-11-14"],
        )

    def test_isi_baris_lengkap(self):
        baris = _baris(export.csv_pembayaran(BAYAR_2026))
        self.assertEqual(
            baris[1:], [
                ["2026-03-20", "fitrah", "136932", "4 jiwa"],
                ["2026-11-14", "mal", "6877250", "via bank"],
                ["2026-11-14", "profesi", "500000", ""],
            ],
        )

    def test_catatan_kosong_jadi_sel_kosong(self):
        baris = _baris(export.csv_pembayaran(
            [{"jenis": "mal", "jumlah": 100_000, "tanggal": "2026-01-05"}]
        ))
        self.assertEqual(baris[1], ["2026-01-05", "mal", "100000", ""])

    def test_pembayaran_tahun_lain_ikut_disertakan(self):
        bayar = BAYAR_2026 + [
            {"jenis": "profesi", "jumlah": 400_000, "tanggal": "2025-12-01"},
        ]
        baris = _baris(export.csv_pembayaran(bayar))
        self.assertEqual(len(baris), 5)  # header + 4 pembayaran
        self.assertEqual(baris[1][0], "2025-12-01")


class TestCsvLaporan(unittest.TestCase):
    def test_header_dan_total_2026(self):
        baris = _baris(export.csv_laporan(BAYAR_2026, 2026))
        self.assertEqual(baris[0], ["jenis", "jumlah"])
        # Baris terakhir selalu TOTAL: 500.000 + 136.932 + 6.877.250.
        self.assertEqual(baris[-1], ["TOTAL", "7514182"])

    def test_per_jenis_urut_jenis_zakat(self):
        baris = _baris(export.csv_laporan(BAYAR_2026, 2026))
        self.assertEqual(
            baris[1:], [
                ["profesi", "500000"],
                ["mal", "6877250"],
                ["fitrah", "136932"],
                ["TOTAL", "7514182"],
            ],
        )

    def test_hanya_tahun_yang_diminta(self):
        bayar = BAYAR_2026 + [
            {"jenis": "profesi", "jumlah": 400_000, "tanggal": "2025-12-01"},
        ]
        baris = _baris(export.csv_laporan(bayar, 2026))
        self.assertEqual(baris[-1], ["TOTAL", "7514182"])
        baris_2025 = _baris(export.csv_laporan(bayar, 2025))
        self.assertEqual(
            baris_2025,
            [["jenis", "jumlah"], ["profesi", "400000"], ["TOTAL", "400000"]],
        )

    def test_tahun_kosong_hanya_total_nol(self):
        baris = _baris(export.csv_laporan(BAYAR_2026, 2024))
        self.assertEqual(baris, [["jenis", "jumlah"], ["TOTAL", "0"]])

    def test_jenis_tanpa_pembayaran_tidak_muncul(self):
        baris = _baris(export.csv_laporan(
            [{"jenis": "fitrah", "jumlah": 34_233, "tanggal": "2026-03-20"}],
            2026,
        ))
        self.assertEqual(
            baris,
            [["jenis", "jumlah"], ["fitrah", "34233"], ["TOTAL", "34233"]],
        )


if __name__ == "__main__":
    unittest.main()
