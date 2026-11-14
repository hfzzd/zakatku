"""Antarmuka baris perintah ZakatKu."""

import argparse
import os
import sys

from . import __version__, model, zakat


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
    return parser


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
    print(f"Total               : {hasil['total_kg']} kg beras = "
          f"{zakat.format_rupiah(hasil['jumlah'])}")
    print("Dibayar di bulan Ramadan, sebelum salat Idulfitri.")
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
    parser.error("perintah tidak dikenal")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
