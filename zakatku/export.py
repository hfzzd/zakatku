"""Ekspor data ZakatKu ke CSV (fungsi murni, tanpa I/O)."""

import csv
import io

from .model import JENIS_ZAKAT


def csv_pembayaran(pembayaran):
    """CSV seluruh pembayaran: tanggal, jenis, jumlah, catatan.

    Diurutkan berdasarkan tanggal; catatan kosong jadi sel kosong.
    """
    out = io.StringIO()
    tulis = csv.writer(out)
    tulis.writerow(["tanggal", "jenis", "jumlah", "catatan"])
    for p in sorted(pembayaran, key=lambda x: x.get("tanggal", "")):
        tulis.writerow([p.get("tanggal", ""), p.get("jenis", ""),
                        p.get("jumlah", ""), p.get("catatan", "")])
    return out.getvalue()


def csv_laporan(pembayaran, tahun):
    """CSV rekap setahun: total per jenis zakat + baris TOTAL."""
    total_per_jenis = {}
    for p in pembayaran:
        if str(p.get("tanggal", "")).startswith(str(tahun) + "-"):
            total_per_jenis[p["jenis"]] = total_per_jenis.get(p["jenis"], 0) + p["jumlah"]
    out = io.StringIO()
    tulis = csv.writer(out)
    tulis.writerow(["jenis", "jumlah"])
    for jenis in JENIS_ZAKAT:
        if jenis in total_per_jenis:
            tulis.writerow([jenis, total_per_jenis[jenis]])
    tulis.writerow(["TOTAL", sum(total_per_jenis.values())])
    return out.getvalue()
