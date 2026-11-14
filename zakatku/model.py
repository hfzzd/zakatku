"""Penyimpanan data lokal (JSON): harga acuan + catatan pembayaran zakat."""

import json
import os

from .zakat import HARGA_BERAS_DEFAULT, HARGA_EMAS_DEFAULT

DEFAULT_DATA_FILE = "zakatku.json"

# Jenis zakat yang dikenal untuk pencatatan pembayaran.
JENIS_ZAKAT = ("profesi", "mal", "fitrah")


def tambah_pembayaran(data, jenis, jumlah, tanggal, catatan=None):
    """Tambah satu pembayaran ke data["pembayaran"].

    Memanggil fungsi ini mengasumsikan jenis sudah dikenal, jumlah > 0,
    dan tanggal sudah dalam format YYYY-MM-DD yang valid.
    """
    entri = {"jenis": jenis, "jumlah": jumlah, "tanggal": tanggal}
    if catatan:
        entri["catatan"] = catatan
    data.setdefault("pembayaran", []).append(entri)
    return entri


def _data_kosong():
    return {
        "config": {
            "harga_emas": HARGA_EMAS_DEFAULT,
            "harga_beras": HARGA_BERAS_DEFAULT,
        },
        "pembayaran": [],
    }


def muat(path):
    """Muat data dari file JSON; bila belum ada, kembalikan data kosong."""
    if not os.path.exists(path):
        return _data_kosong()
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("config", {})
    data["config"].setdefault("harga_emas", HARGA_EMAS_DEFAULT)
    data["config"].setdefault("harga_beras", HARGA_BERAS_DEFAULT)
    data.setdefault("pembayaran", [])
    return data


def simpan(path, data):
    """Simpan data ke file JSON."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
