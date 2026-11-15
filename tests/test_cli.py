"""Test end-to-end CLI ZakatKu lewat subprocess di folder sementara.

Setiap test memakai folder /tmp sendiri + file data --data sendiri,
jadi tidak menyentuh data pengguna mana pun.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

from zakatku import __version__

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def jalankan(*args, cwd):
    """Jalankan `python -m zakatku ...` dan kembalikan CompletedProcess."""
    env = dict(os.environ)
    env["PYTHONPATH"] = REPO_ROOT + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, "-m", "zakatku", *args],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data = os.path.join(self.tmp.name, "zakatku.json")

    def tearDown(self):
        self.tmp.cleanup()

    def _cli(self, *args):
        # --data harus sebelum subcommand (argparse hanya mengenalnya
        # di parser utama).
        return jalankan("--data", self.data, *args, cwd=self.tmp.name)

    def test_version(self):
        hasil = jalankan("--version", cwd=self.tmp.name)
        self.assertEqual(hasil.returncode, 0)
        self.assertIn(__version__, hasil.stdout)
        self.assertIn("0.2.0", hasil.stdout)

    def test_alur_lengkap(self):
        """config lihat -> hitung profesi/fitrah/mal -> bayar catat -> laporan."""
        # 1. Lihat harga acuan & nisab bawaan.
        hasil = self._cli("config", "lihat")
        self.assertEqual(hasil.returncode, 0)
        self.assertIn("Rp2.509.000", hasil.stdout)
        self.assertIn("Rp13.693", hasil.stdout)
        self.assertIn("Rp213.265.000", hasil.stdout)
        self.assertIn("Rp17.772.083", hasil.stdout)

        # 2. Zakat profesi Rp20.000.000 -> Rp500.000.
        hasil = self._cli("hitung", "profesi", "--penghasilan", "20000000")
        self.assertEqual(hasil.returncode, 0)
        self.assertIn("Rp500.000", hasil.stdout)

        # 3. Zakat fitrah 4 jiwa -> Rp136.932.
        hasil = self._cli("hitung", "fitrah", "--jiwa", "4")
        self.assertEqual(hasil.returncode, 0)
        self.assertIn("Rp136.932", hasil.stdout)
        self.assertIn("Rp34.233", hasil.stdout)

        # 4. Zakat mal: tabungan 250jt + emas 10 gram -> Rp6.877.250.
        hasil = self._cli(
            "hitung", "mal", "--tabungan", "250000000", "--emas-gram", "10"
        )
        self.assertEqual(hasil.returncode, 0)
        self.assertIn("Rp275.090.000", hasil.stdout)
        self.assertIn("Rp6.877.250", hasil.stdout)

        # 5. Catat ketiga pembayaran, lalu cek isi file datanya.
        for jenis, jumlah, tanggal in [
            ("profesi", "500000", "2026-11-14"),
            ("fitrah", "136932", "2026-03-20"),
            ("mal", "6877250", "2026-11-14"),
        ]:
            hasil = self._cli(
                "bayar", "catat", "--jenis", jenis,
                "--jumlah", jumlah, "--tanggal", tanggal,
            )
            self.assertEqual(hasil.returncode, 0, hasil.stderr)
            self.assertIn("Tercatat", hasil.stdout)
        with open(self.data, encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(len(data["pembayaran"]), 3)
        self.assertEqual(
            [p["jenis"] for p in data["pembayaran"]],
            ["profesi", "fitrah", "mal"],
        )

        # 6. Laporan 2026: total Rp500.000 + Rp136.932 + Rp6.877.250
        #    = Rp7.514.182.
        hasil = self._cli("laporan", "--tahun", "2026")
        self.assertEqual(hasil.returncode, 0)
        self.assertIn("Rp500.000", hasil.stdout)
        self.assertIn("Rp136.932", hasil.stdout)
        self.assertIn("Rp6.877.250", hasil.stdout)
        self.assertIn("Rp7.514.182", hasil.stdout)

    def test_config_atur_tersimpan_dan_dipakai_hitung(self):
        hasil = self._cli(
            "config", "atur", "--harga-beras", "14000"
        )
        self.assertEqual(hasil.returncode, 0)
        self.assertIn("Rp14.000", hasil.stdout)

        # Harga beras baru dipakai hitung fitrah: 2,5 kg x Rp14.000.
        hasil = self._cli("hitung", "fitrah", "--jiwa", "1")
        self.assertIn("Rp35.000", hasil.stdout)

        # Tetap tersimpan di file data.
        with open(self.data, encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["config"]["harga_beras"], 14_000)
        self.assertEqual(data["config"]["harga_emas"], 2_509_000)

    def test_config_atur_tanpa_argumen_ditolak(self):
        hasil = self._cli("config", "atur")
        self.assertNotEqual(hasil.returncode, 0)
        self.assertIn("Tidak ada yang diubah", hasil.stderr)

    def test_laporan_tahun_kosong_ramah(self):
        hasil = self._cli("laporan", "--tahun", "2025")
        self.assertEqual(hasil.returncode, 0)
        self.assertIn("Belum ada pembayaran", hasil.stdout)

    def test_profesi_belum_wajib(self):
        hasil = self._cli("hitung", "profesi", "--penghasilan", "10000000")
        self.assertEqual(hasil.returncode, 0)
        self.assertIn("Belum wajib zakat", hasil.stdout)

    def test_mal_belum_wajib(self):
        hasil = self._cli("hitung", "mal", "--tabungan", "100000000")
        self.assertEqual(hasil.returncode, 0)
        self.assertIn("Belum wajib zakat", hasil.stdout)

    def test_input_salah_keluar_bukan_nol(self):
        # Penghasilan bukan angka.
        hasil = self._cli("hitung", "profesi", "--penghasilan", "sepuluhjuta")
        self.assertNotEqual(hasil.returncode, 0)
        self.assertIn("bukan angka", hasil.stderr)

        # Jumlah jiwa bukan bilangan bulat.
        hasil = self._cli("hitung", "fitrah", "--jiwa", "2.5")
        self.assertNotEqual(hasil.returncode, 0)

        # Jenis zakat tidak dikenal.
        hasil = self._cli(
            "bayar", "catat", "--jenis", "infaq",
            "--jumlah", "100000", "--tanggal", "2026-11-14",
        )
        self.assertNotEqual(hasil.returncode, 0)

        # Jumlah nol ditolak.
        hasil = self._cli(
            "bayar", "catat", "--jenis", "mal",
            "--jumlah", "0", "--tanggal", "2026-11-14",
        )
        self.assertEqual(hasil.returncode, 1)

        # Tanggal tidak valid (30 Februari tidak ada).
        hasil = self._cli(
            "bayar", "catat", "--jenis", "mal",
            "--jumlah", "100000", "--tanggal", "2026-02-30",
        )
        self.assertNotEqual(hasil.returncode, 0)


class TestCLIPengingatDanEkspor(unittest.TestCase):
    """harta catat / ingatkan / ekspor lewat CLI di folder sementara."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data = os.path.join(self.tmp.name, "zakatku.json")

    def tearDown(self):
        self.tmp.cleanup()

    def _cli(self, *args):
        return jalankan("--data", self.data, *args, cwd=self.tmp.name)

    def _catat_tiga_pembayaran_contoh(self):
        """Tiga pembayaran contoh Day-1; laporan 2026 = Rp7.514.182."""
        for jenis, jumlah, tanggal in [
            ("profesi", "500000", "2026-11-14"),
            ("fitrah", "136932", "2026-03-20"),
            ("mal", "6877250", "2026-11-14"),
        ]:
            hasil = self._cli(
                "bayar", "catat", "--jenis", jenis,
                "--jumlah", jumlah, "--tanggal", tanggal,
            )
            self.assertEqual(hasil.returncode, 0, hasil.stderr)

    def test_harta_catat_di_bawah_nisab_ditolak_exit_1(self):
        hasil = self._cli(
            "harta", "catat", "--tanggal", "2026-11-14",
            "--tabungan", "100000000",
        )
        self.assertEqual(hasil.returncode, 1)
        self.assertIn("di bawah nisab", hasil.stderr)
        # Ditolak sebelum simpan: file data boleh belum ada (belum pernah
        # tersimpan), atau bila ada, riwayat hartanya kosong.
        if os.path.exists(self.data):
            with open(self.data, encoding="utf-8") as f:
                data = json.load(f)
            self.assertEqual(data["harta"], [])

    def test_harta_catat_lalu_ingatkan(self):
        # Tabungan 250jt + emas 10 gram >= nisab Rp213.265.000.
        hasil = self._cli(
            "harta", "catat", "--tanggal", "2026-11-14",
            "--tabungan", "250000000", "--emas-gram", "10",
        )
        self.assertEqual(hasil.returncode, 0, hasil.stderr)
        self.assertIn("Tercatat", hasil.stdout)
        self.assertIn("2027-11-03", hasil.stdout)  # haul = +354 hari

        hasil = self._cli("harta", "lihat")
        self.assertEqual(hasil.returncode, 0)
        self.assertIn("2026-11-14", hasil.stdout)
        self.assertIn("Rp275.090.000", hasil.stdout)

        hasil = self._cli("ingatkan")
        self.assertEqual(hasil.returncode, 0)
        self.assertIn("2026-11-14", hasil.stdout)
        self.assertIn("hari lagi", hasil.stdout)

    def test_ingatkan_tanpa_data_ditolak_exit_1(self):
        hasil = self._cli("ingatkan")
        self.assertEqual(hasil.returncode, 1)
        self.assertIn("Tidak ada yang bisa diingatkan", hasil.stderr)

    def test_ekspor_laporan_tanpa_tahun_ditolak_exit_1(self):
        self._catat_tiga_pembayaran_contoh()
        hasil = self._cli("ekspor", "--jenis", "laporan")
        self.assertEqual(hasil.returncode, 1)
        self.assertIn("--tahun", hasil.stderr)

    def test_ekspor_tanpa_data_ditolak_exit_1(self):
        hasil = self._cli("ekspor", "--jenis", "pembayaran")
        self.assertEqual(hasil.returncode, 1)
        self.assertIn("Belum ada pembayaran", hasil.stderr)

    def test_ekspor_keluar_menulis_file(self):
        self._catat_tiga_pembayaran_contoh()

        keluar_bayar = os.path.join(self.tmp.name, "pembayaran.csv")
        hasil = self._cli(
            "ekspor", "--jenis", "pembayaran", "--keluar", keluar_bayar,
        )
        self.assertEqual(hasil.returncode, 0, hasil.stderr)
        self.assertIn("Diekspor ke", hasil.stdout)
        with open(keluar_bayar, encoding="utf-8") as f:
            isi = f.read()
        self.assertIn("tanggal,jenis,jumlah,catatan", isi)
        # Urut tanggal: fitrah 2026-03-20 paling dulu.
        self.assertLess(
            isi.index("2026-03-20"), isi.index("2026-11-14")
        )
        self.assertIn("2026-11-14,mal,6877250", isi)

        keluar_laporan = os.path.join(self.tmp.name, "laporan-2026.csv")
        hasil = self._cli(
            "ekspor", "--jenis", "laporan", "--tahun", "2026",
            "--keluar", keluar_laporan,
        )
        self.assertEqual(hasil.returncode, 0, hasil.stderr)
        with open(keluar_laporan, encoding="utf-8") as f:
            isi = f.read()
        self.assertIn("TOTAL,7514182", isi)
        self.assertIn("profesi,500000", isi)


if __name__ == "__main__":
    unittest.main()
