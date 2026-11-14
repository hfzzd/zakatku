"""Antarmuka baris perintah ZakatKu."""

import argparse
import os
import sys
from datetime import date

from . import __version__, model, pengingat, zakat


def _angka(teks):
    """Ubah teks menjadi angka; tolak dengan pesan ramah bila bukan angka."""
    try:
        nilai = float(teks)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"'{teks}' bukan angka — tulis tanpa pemisah ribuan, contoh: 10000000."
        )
    if nilai < 0:
        raise argparse.ArgumentTypeError("angka tidak boleh negatif.")
    return nilai


def _bilangan_bulat(teks):
    nilai = _angka(teks)
    if nilai != int(nilai):
        raise argparse.ArgumentTypeError("harus bilangan bulat, contoh: 4.")
    return int(nilai)


def _tanggal(teks):
    """Ubah teks menjadi tanggal; tolak bila bukan YYYY-MM-DD yang valid."""
    try:
        return date.fromisoformat(teks)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"'{teks}' bukan tanggal yang valid — pakai format YYYY-MM-DD, contoh: 2026-11-14."
        )


def _tahun(teks):
    nilai = _bilangan_bulat(teks)
    if nilai < 1 or nilai > 9999:
        raise argparse.ArgumentTypeError("tahun harus antara 1 dan 9999.")
    return nilai


def _buat_parser():
    parser = argparse.ArgumentParser(
        prog="zakatku",
        description="Kalkulator zakat & infaq (profesi, mal, fitrah).",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--data",
        default=os.environ.get("ZAKATKU_DATA", model.DEFAULT_DATA_FILE),
        help="File data JSON (bawaan: zakatku.json atau $ZAKATKU_DATA).",
    )
    sub = parser.add_subparsers(dest="perintah", required=True)

    p_config = sub.add_parser("config", help="Lihat / ubah harga acuan.")
    sub_config = p_config.add_subparsers(dest="aksi_config", required=True)
    sub_config.add_parser("lihat", help="Tampilkan harga acuan & nisab.")
    p_atur = sub_config.add_parser("atur", help="Ubah harga acuan.")
    p_atur.add_argument("--harga-emas", type=_angka, help="Harga emas per gram (Rp).")
    p_atur.add_argument("--harga-beras", type=_angka, help="Harga beras per kg (Rp).")

    p_hitung = sub.add_parser("hitung", help="Hitung zakat.")
    sub_hitung = p_hitung.add_subparsers(dest="jenis", required=True)
    p_profesi = sub_hitung.add_parser("profesi", help="Zakat profesi.")
    p_profesi.add_argument("--penghasilan", type=_angka, required=True,
                           help="Penghasilan satu bulan (Rp).")
    p_fitrah = sub_hitung.add_parser("fitrah", help="Zakat fitrah.")
    p_fitrah.add_argument("--jiwa", type=_bilangan_bulat, required=True,
                          help="Jumlah jiwa.")
    p_mal = sub_hitung.add_parser("mal", help="Zakat mal (tabungan & emas).")
    p_mal.add_argument("--tabungan", type=_angka, required=True,
                       help="Saldo tabungan (Rp).")
    p_mal.add_argument("--emas-gram", type=_angka, default=0,
                       help="Berat emas yang dimiliki (gram).")

    p_bayar = sub.add_parser("bayar", help="Catat pembayaran zakat.")
    sub_bayar = p_bayar.add_subparsers(dest="aksi_bayar", required=True)
    p_catat = sub_bayar.add_parser("catat", help="Catat satu pembayaran zakat.")
    p_catat.add_argument("--jenis", choices=model.JENIS_ZAKAT, required=True,
                         help="Jenis zakat: profesi, mal, atau fitrah.")
    p_catat.add_argument("--jumlah", type=_angka, required=True,
                         help="Jumlah yang dibayar (Rp, harus > 0).")
    p_catat.add_argument("--tanggal", type=_tanggal, required=True,
                         help="Tanggal pembayaran (YYYY-MM-DD).")
    p_catat.add_argument("--catatan", default=None,
                         help="Catatan tambahan (opsional).")

    p_laporan = sub.add_parser("laporan", help="Laporan pembayaran zakat setahun.")
    p_laporan.add_argument("--tahun", type=_tahun, required=True,
                           help="Tahun laporan (YYYY).")

    p_harta = sub.add_parser("harta", help="Catat / lihat harta untuk pengingat haul.")
    sub_harta = p_harta.add_subparsers(dest="aksi_harta", required=True)
    p_harta_catat = sub_harta.add_parser("catat", help="Catat tanggal harta mencapai nisab.")
    p_harta_catat.add_argument("--tanggal", type=_tanggal, required=True,
                               help="Tanggal harta mencapai nisab (YYYY-MM-DD).")
    p_harta_catat.add_argument("--tabungan", type=_angka, required=True,
                               help="Saldo tabungan saat itu (Rp).")
    p_harta_catat.add_argument("--emas-gram", type=_angka, default=0,
                               help="Berat emas saat itu (gram).")
    sub_harta.add_parser("lihat", help="Tampilkan riwayat catatan harta.")

    p_ingatkan = sub.add_parser("ingatkan", help="Pengingat haul, nisab & Idulfitri.")
    p_ingatkan.add_argument("--penghasilan", type=_angka, default=None,
                            help="Penghasilan bulanan (Rp) untuk cek nisab profesi.")
    p_ingatkan.add_argument("--idulfitri", type=_tanggal, default=None,
                            help="Tanggal Idulfitri (YYYY-MM-DD) untuk hitung mundur fitrah.")
    return parser


def _rapi(nilai):
    """Tampilkan angka tanpa .0 bila bulat (10.0 -> 10)."""
    return int(nilai) if float(nilai) == int(nilai) else nilai


def _cmd_config_lihat(data):
    cfg = data["config"]
    harga_emas = cfg["harga_emas"]
    harga_beras = cfg["harga_beras"]
    print("Harga acuan yang dipakai:")
    print(f"  Emas  : {zakat.format_rupiah(harga_emas)}/gram")
    print(f"  Beras : {zakat.format_rupiah(harga_beras)}/kg")
    print(f"Nisab tahunan (85 gram emas): {zakat.format_rupiah(zakat.nisab_tahunan(harga_emas))}")
    print(f"Nisab bulanan profesi       : {zakat.format_rupiah(zakat.nisab_bulanan(harga_emas))}")
    print(f"Zakat fitrah per jiwa (2,5 kg): {zakat.format_rupiah(2.5 * harga_beras)}")
    print("Ubah dengan: zakatku config atur --harga-emas N --harga-beras N")
    return 0


def _cmd_config_atur(data, path, args):
    if args.harga_emas is None and args.harga_beras is None:
        print("Tidak ada yang diubah. Contoh: zakatku config atur --harga-emas 2509000",
              file=sys.stderr)
        return 1
    if args.harga_emas is not None:
        data["config"]["harga_emas"] = args.harga_emas
    if args.harga_beras is not None:
        data["config"]["harga_beras"] = args.harga_beras
    model.simpan(path, data)
    print("Harga acuan diperbarui & tersimpan di " + path + ".")
    return _cmd_config_lihat(data)


def _cmd_hitung_profesi(data, args):
    hasil = zakat.zakat_profesi(args.penghasilan, data["config"]["harga_emas"])
    print(f"Penghasilan bulanan : {zakat.format_rupiah(hasil['penghasilan'])}")
    print(f"Nisab bulanan       : {zakat.format_rupiah(hasil['nisab'])}")
    if hasil["wajib"]:
        print(f"Zakat profesi (2,5%) : {zakat.format_rupiah(hasil['jumlah'])} — wajib dibayar.")
    else:
        print("Belum wajib zakat: penghasilan di bawah nisab bulanan.")
        print("Tetap boleh berinfak bila berkenan.")
    return 0


def _cmd_hitung_fitrah(data, args):
    hasil = zakat.zakat_fitrah(args.jiwa, data["config"]["harga_beras"])
    print(f"Jumlah jiwa         : {hasil['jiwa']} jiwa")
    print(f"Per jiwa            : {hasil['kg_per_jiwa']} kg beras = "
          f"{zakat.format_rupiah(hasil['per_jiwa'])}")
    print(f"Total               : {_rapi(hasil['total_kg'])} kg beras = "
          f"{zakat.format_rupiah(hasil['jumlah'])}")
    print("Dibayar di bulan Ramadan, sebelum salat Idulfitri.")
    return 0


def _cmd_hitung_mal(data, args):
    hasil = zakat.zakat_mal(args.tabungan, args.emas_gram,
                            data["config"]["harga_emas"])
    print(f"Tabungan            : {zakat.format_rupiah(hasil['tabungan'])}")
    print(f"Emas                : {_rapi(hasil['emas_gram'])} gram = "
          f"{zakat.format_rupiah(hasil['nilai_emas'])}")
    print(f"Total harta         : {zakat.format_rupiah(hasil['total'])}")
    print(f"Nisab tahunan       : {zakat.format_rupiah(hasil['nisab'])}")
    if hasil["wajib"]:
        print(f"Zakat mal (2,5%)    : {zakat.format_rupiah(hasil['jumlah'])} — wajib dibayar.")
        print("Pastikan harta sudah haul 1 tahun sebelum membayar.")
    else:
        print("Belum wajib zakat: total harta di bawah nisab tahunan.")
        print("Tetap boleh berinfak bila berkenan.")
    return 0


def _cmd_bayar_catat(data, path, args):
    if args.jumlah <= 0:
        print("Jumlah harus lebih dari 0.", file=sys.stderr)
        return 1
    tanggal = args.tanggal.isoformat()
    model.tambah_pembayaran(data, args.jenis, args.jumlah, tanggal, args.catatan)
    model.simpan(path, data)
    print(f"Tercatat: zakat {args.jenis} {zakat.format_rupiah(args.jumlah)} "
          f"pada {tanggal}.")
    if args.catatan:
        print(f"Catatan: {args.catatan}")
    return 0


def _cmd_laporan(data, args):
    tahun = str(args.tahun)
    bayar = [p for p in data.get("pembayaran", [])
             if p.get("tanggal", "").startswith(tahun + "-")]
    if not bayar:
        print(f"Belum ada pembayaran zakat yang tercatat di tahun {tahun}.")
        print("Catat pembayaran dengan: zakatku bayar catat --jenis ... "
              "--jumlah N --tanggal YYYY-MM-DD")
        return 0
    total_per_jenis = {}
    for p in bayar:
        total_per_jenis[p["jenis"]] = total_per_jenis.get(p["jenis"], 0) + p["jumlah"]
    print(f"Laporan zakat tahun {tahun}:")
    for jenis in model.JENIS_ZAKAT:
        if jenis in total_per_jenis:
            print(f"  {jenis:<8}: {zakat.format_rupiah(total_per_jenis[jenis])}")
    print(f"  Total   : {zakat.format_rupiah(sum(total_per_jenis.values()))}")
    print()
    print("Pembayaran:")
    for p in sorted(bayar, key=lambda x: x["tanggal"]):
        baris = f"  {p['tanggal']}  {p['jenis']:<8} {zakat.format_rupiah(p['jumlah'])}"
        if p.get("catatan"):
            baris += f"  ({p['catatan']})"
        print(baris)
    return 0


def _cmd_harta_catat(data, path, args):
    harga_emas = data["config"]["harga_emas"]
    hasil = zakat.zakat_mal(args.tabungan, args.emas_gram, harga_emas)
    if not hasil["wajib"]:
        print(f"Total harta {zakat.format_rupiah(hasil['total'])} masih di bawah "
              f"nisab {zakat.format_rupiah(hasil['nisab'])} — belum perlu dicatat.",
              file=sys.stderr)
        print("Catat lagi bila total harta sudah mencapai nisab.", file=sys.stderr)
        return 1
    tanggal = args.tanggal.isoformat()
    model.catat_harta(data, tanggal, args.tabungan, args.emas_gram)
    model.simpan(path, data)
    haul = pengingat.tanggal_haul(args.tanggal)
    print(f"Tercatat: harta {zakat.format_rupiah(hasil['total'])} mencapai nisab "
          f"pada {tanggal}.")
    print(f"Haul (1 tahun Hijriah) tercapai pada {haul.isoformat()}.")
    return 0


def _cmd_harta_lihat(data):
    riwayat = data.get("harta", [])
    if not riwayat:
        print("Belum ada catatan harta.")
        print("Catat dengan: zakatku harta catat --tanggal YYYY-MM-DD "
              "--tabungan N [--emas-gram N]")
        return 0
    harga_emas = data["config"]["harga_emas"]
    print("Riwayat catatan harta (tanggal mencapai nisab):")
    for entri in riwayat:
        hasil = zakat.zakat_mal(entri["tabungan"], entri["emas_gram"], harga_emas)
        print(f"  {entri['tanggal']}  total {zakat.format_rupiah(hasil['total'])} "
              f"(tabungan {zakat.format_rupiah(entri['tabungan'])}, "
              f"emas {_rapi(entri['emas_gram'])} gram)")
    return 0


def _cmd_ingatkan(data, args):
    hari_ini = date.today()
    ada_info = False

    harta = model.harta_terakhir(data)
    if harta is not None:
        ada_info = True
        mulai = date.fromisoformat(harta["tanggal"])
        status = pengingat.status_haul(mulai, hari_ini)
        print(f"Zakat mal — harta mencapai nisab pada {status['tanggal_mulai']}.")
        if status["sudah_haul"]:
            print(f"  Sudah haul sejak {status['tanggal_haul']} "
                  f"({-status['hari_lagi']} hari lalu) — zakat mal wajib dibayar "
                  f"bila harta masih di atas nisab.")
        else:
            print(f"  Haul tercapai {status['tanggal_haul']} — "
                  f"{status['hari_lagi']} hari lagi.")
    else:
        print("Zakat mal — belum ada catatan harta.")
        print("  Catat dulu dengan: zakatku harta catat --tanggal YYYY-MM-DD "
              "--tabungan N [--emas-gram N]")

    if args.penghasilan is not None:
        ada_info = True
        hasil = zakat.zakat_profesi(args.penghasilan, data["config"]["harga_emas"])
        print(f"Zakat profesi — penghasilan {zakat.format_rupiah(args.penghasilan)} "
              f"vs nisab bulanan {zakat.format_rupiah(hasil['nisab'])}:")
        if hasil["wajib"]:
            print(f"  Sudah mencapai nisab — zakat {zakat.format_rupiah(hasil['jumlah'])} "
                  f"wajib dibayar bulan ini.")
        else:
            print("  Belum mencapai nisab — belum wajib zakat bulan ini.")

    if args.idulfitri is not None:
        ada_info = True
        sisa = pengingat.hitung_mundur_fitrah(args.idulfitri, hari_ini)
        if sisa > 0:
            print(f"Zakat fitrah — Idulfitri {sisa} hari lagi "
                  f"({args.idulfitri.isoformat()}). Bayar sebelum salat Id.")
        elif sisa == 0:
            print("Zakat fitrah — Idulfitri hari ini! Bayar sebelum salat Id.")
        else:
            print(f"Zakat fitrah — Idulfitri sudah lewat {-sisa} hari lalu.")

    if not ada_info:
        print("Tidak ada yang bisa diingatkan: belum ada catatan harta, "
              "--penghasilan, atau --idulfitri.", file=sys.stderr)
        print("Contoh: zakatku ingatkan --penghasilan 20000000 "
              "--idulfitri 2027-03-20", file=sys.stderr)
        return 1
    return 0


def main(argv=None):
    parser = _buat_parser()
    args = parser.parse_args(argv)
    data = model.muat(args.data)

    if args.perintah == "config" and args.aksi_config == "lihat":
        return _cmd_config_lihat(data)
    if args.perintah == "config" and args.aksi_config == "atur":
        return _cmd_config_atur(data, args.data, args)
    if args.perintah == "hitung" and args.jenis == "profesi":
        return _cmd_hitung_profesi(data, args)
    if args.perintah == "hitung" and args.jenis == "fitrah":
        return _cmd_hitung_fitrah(data, args)
    if args.perintah == "hitung" and args.jenis == "mal":
        return _cmd_hitung_mal(data, args)
    if args.perintah == "bayar" and args.aksi_bayar == "catat":
        return _cmd_bayar_catat(data, args.data, args)
    if args.perintah == "laporan":
        return _cmd_laporan(data, args)
    if args.perintah == "harta" and args.aksi_harta == "catat":
        return _cmd_harta_catat(data, args.data, args)
    if args.perintah == "harta" and args.aksi_harta == "lihat":
        return _cmd_harta_lihat(data)
    if args.perintah == "ingatkan":
        return _cmd_ingatkan(data, args)
    parser.error("perintah tidak dikenal")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
