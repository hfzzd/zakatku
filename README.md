# ZakatKu

Kalkulator zakat & infaq — CLI Python tanpa dependensi, data tersimpan
lokal sebagai JSON, berbahasa Indonesia.

Hitung kewajiban zakatmu dengan cepat: zakat profesi dari penghasilan
bulanan, zakat mal dari tabungan dan emas, serta zakat fitrah per jiwa.
Semua angka memakai acuan yang bisa kamu ubah sendiri (harga emas dan
harga beras), supaya hasil hitungannya selalu mengikuti harga yang
berlaku di sekitarmu.

> **Catatan:** ZakatKu adalah alat bantu hitung, bukan fatwa. Aturan yang
> dipakai di sini adalah pendapat yang umum diamalkan di Indonesia
> (nisab 85 gram emas, kadar 2,5%, zakat fitrah 2,5 kg beras per jiwa).
> Bila ragu, tanyakan ke ustaz atau lembaga amil zakat setempat.

## Aturan yang dipakai

| Jenis zakat | Nisab | Kadar | Keterangan |
| --- | --- | --- | --- |
| Profesi | 85 gram emas / tahun (dibagi 12 per bulan) | 2,5% dari penghasilan | Wajib bila penghasilan bulanan mencapai nisab bulanan |
| Mal (uang & emas) | 85 gram emas | 2,5% dari total harta | Wajib bila harta mencapai nisab dan sudah haul 1 tahun |
| Fitrah | — | 2,5 kg beras per jiwa | Dibayar di bulan Ramadan sebelum salat Idulfitri |

Harga acuan bawaan (bisa diubah dengan `zakatku config atur`):

- Harga emas: **Rp2.509.000/gram** (Antam Logam Mulia, 13 Nov 2026)
- Harga beras: **Rp13.693/kg** (beras medium, Panel Harga Pangan
  Bapanas, 12 Nov 2026)

Dengan harga acuan di atas, nisab tahunan = 85 × Rp2.509.000 =
**Rp213.265.000**, dan nisab bulanan profesi = **Rp17.772.083**.

## Cara memakai

```bash
# Lihat harga acuan & nisab yang sedang dipakai
python -m zakatku config lihat

# Ubah harga acuan mengikuti harga pasar saat ini
python -m zakatku config atur --harga-emas 2509000 --harga-beras 14000

# Zakat profesi dari gaji bulanan Rp10.000.000
python -m zakatku hitung profesi --penghasilan 10000000

# Zakat fitrah untuk 4 jiwa
python -m zakatku hitung fitrah --jiwa 4

# Zakat mal dari tabungan Rp250.000.000 + emas 10 gram
python -m zakatku hitung mal --tabungan 250000000 --emas-gram 10

# Catat pembayaran zakat yang sudah ditunaikan
python -m zakatku bayar catat --jenis profesi --jumlah 250000 --tanggal 2026-11-14

# Laporan zakat tahun 2026
python -m zakatku laporan --tahun 2026

# Catat harta mencapai nisab, untuk pengingat haul
python -m zakatku harta catat --tanggal 2026-11-15 --tabungan 250000000 --emas-gram 10

# Pengingat: haul zakat mal, nisab profesi, hitung mundur Idulfitri
python -m zakatku ingatkan --penghasilan 20000000 --idulfitri 2027-03-20

# Ekspor pembayaran dan laporan 2026 ke CSV
python -m zakatku ekspor --jenis pembayaran --keluar pembayaran.csv
python -m zakatku ekspor --jenis laporan --tahun 2026 --keluar laporan-2026.csv
```

Data tersimpan di `zakatku.json` di folder kerja (atau file lain lewat
`--data`, atau variabel lingkungan `ZAKATKU_DATA`).

### Zakat mal

Zakat mal dihitung dari total harta: tabungan ditambah nilai emas yang
dimiliki (berat emas × harga emas per gram). Wajib dibayar bila total
harta mencapai nisab tahunan (85 gram emas) dan sudah haul 1 tahun,
dengan kadar 2,5% dari total harta.

```bash
# Contoh: tabungan Rp250.000.000 + emas 10 gram
python -m zakatku hitung mal --tabungan 250000000 --emas-gram 10
# Total harta Rp275.090.000 ≥ nisab Rp213.265.000 → zakat Rp6.877.250
```

### Mencatat pembayaran & laporan tahunan

Setiap zakat yang sudah ditunaikan bisa dicatat, lalu dilihat
rekapnya per tahun — total per jenis zakat, total keseluruhan, dan
daftar pembayarannya.

```bash
# Catat pembayaran zakat mal Rp6.877.250 pada 14 Nov 2026
python -m zakatku bayar catat --jenis mal --jumlah 6877250 --tanggal 2026-11-14

# Catat dengan catatan tambahan
python -m zakatku bayar catat --jenis fitrah --jumlah 136930 --tanggal 2026-03-20 --catatan "4 jiwa, via masjid"

# Laporan semua pembayaran di tahun 2026
python -m zakatku laporan --tahun 2026
```

## Pengingat haul & nisab

Zakat mal baru wajib setelah harta mencapai nisab **dan** sudah haul —
kepemilikan selama 1 tahun Hijriah, dihitung **354 hari**. Supaya tidak
lupa, catat tanggal hartamu pertama kali mencapai nisab; ZakatKu akan
menghitung tanggal haulnya dan mengingatkanmu.

```bash
# Catat harta mencapai nisab 15 Nov 2026 (tabungan Rp250.000.000 + emas 10 gram)
python -m zakatku harta catat --tanggal 2026-11-15 --tabungan 250000000 --emas-gram 10
# Tercatat: harta Rp275.090.000 mencapai nisab pada 2026-11-15.
# Haul (1 tahun Hijriah) tercapai pada 2027-11-04.

# Lihat riwayat catatan harta
python -m zakatku harta lihat
# Riwayat catatan harta (tanggal mencapai nisab):
#   2026-11-15  total Rp275.090.000 (tabungan Rp250.000.000, emas 10 gram)
```

Catatan di bawah nisab ditolak dengan pesan ramah — belum perlu dicatat
sampai total harta mencapai nisab tahunan Rp213.265.000.

Perintah `ingatkan` menampilkan status haul, mengecek nisab profesi
dari penghasilan bulanan, dan menghitung mundur ke Idulfitri untuk
zakat fitrah. Jumlah hari dihitung dari tanggal hari ini, jadi
angkanya berubah setiap hari — contoh di bawah dijalankan 15 Nov 2026:

```bash
python -m zakatku ingatkan --penghasilan 20000000 --idulfitri 2027-03-20
# Zakat mal — harta mencapai nisab pada 2026-11-15.
#   Haul tercapai 2027-11-04 — 354 hari lagi.
# Zakat profesi — penghasilan Rp20.000.000 vs nisab bulanan Rp17.772.083:
#   Sudah mencapai nisab — zakat Rp500.000 wajib dibayar bulan ini.
# Zakat fitrah — Idulfitri 125 hari lagi (2027-03-20). Bayar sebelum salat Id.
```

Ketiga bagian boleh dipakai sendiri-sendiri: `ingatkan` tanpa argumen
menampilkan status haul dari catatan harta; tambah `--penghasilan N`
untuk cek nisab profesi (contoh: Rp10.000.000 → belum wajib), dan
`--idulfitri YYYY-MM-DD` untuk hitung mundur fitrah (0 bila hari ini,
negatif bila sudah lewat). Input yang salah ditolak dengan pesan yang
jelas, contohnya `--penghasilan abc` atau `--idulfitri 20-03-2027`.

## Ekspor CSV

Dua jenis ekspor, keduanya bisa ditampilkan di layar atau ditulis ke
file dengan `--keluar`. Contoh di bawah memakai data contoh
(`contoh/zakatku-contoh.json`) lewat `--data`, jadi bisa dicoba tanpa
menyalin apa pun:

```bash
# Ekspor seluruh pembayaran (urut tanggal)
python -m zakatku --data contoh/zakatku-contoh.json ekspor --jenis pembayaran
# tanggal,jenis,jumlah,catatan
# 2026-03-20,fitrah,136932,"Zakat fitrah 4 jiwa (4 x Rp34.233), via masjid"
# 2026-11-14,profesi,500000,"Zakat profesi November 2026 (2,5% x Rp20.000.000)"
# 2026-11-14,mal,6877250,"Zakat mal (2,5% x Rp275.090.000: tabungan Rp250.000.000 + emas 10 gram)"

# Ekspor rekap setahun (total per jenis + baris TOTAL)
python -m zakatku --data contoh/zakatku-contoh.json ekspor --jenis laporan --tahun 2026
# jenis,jumlah
# profesi,500000
# mal,6877250
# fitrah,136932
# TOTAL,7514182
```

Cek hitungan tangan: 500.000 + 6.877.250 + 136.932 = **7.514.182**,
cocok dengan total laporan tahun 2026. Ekspor laporan wajib memakai
`--tahun`; ekspor tanpa data tercatat ditolak dengan pesan ramah.
File CSV-nya bisa dibuka langsung di Excel atau LibreOffice Calc.

## Data contoh

File `contoh/zakatku-contoh.json` berisi harga acuan bawaan plus tiga
contoh pembayaran yang semuanya cocok hitungan tangan: zakat profesi
Rp500.000 (2,5% × Rp20.000.000), zakat fitrah Rp136.932 (4 jiwa ×
Rp34.233), dan zakat mal Rp6.877.250 (2,5% × Rp275.090.000 — tabungan
Rp250.000.000 + emas 10 gram). Coba sendiri:

```bash
# Salin ke folder kerja lalu lihat laporannya (total Rp7.514.182)
cp contoh/zakatku-contoh.json zakatku.json
python -m zakatku laporan --tahun 2026

# Atau pakai langsung tanpa menyalin
python -m zakatku --data contoh/zakatku-contoh.json laporan --tahun 2026
```

## Menjalankan test

```bash
python3 -m unittest discover -s tests
```

Ada 55 test: aturan hitung (nisab, profesi, fitrah, mal, format
rupiah, pembulatan half-up), pengingat haul (tanggal haul 354 hari,
status haul, hitung mundur fitrah), ekspor CSV (pembayaran & laporan),
dan alur CLI end-to-end (config, hitung, bayar catat, laporan, harta
catat, ingatkan, ekspor, input salah).

## Rencana

- [x] Zakat profesi & zakat fitrah + CLI dasar
- [x] Zakat mal + pencatatan pembayaran + laporan tahunan
- [x] Unit test + data contoh + polish CLI
- [x] Pengingat haul & nisab, ekspor CSV
- [ ] Pengingat jadwal catat harta berkala
- [ ] Mode interaktif (tanya-jawab langkah demi langkah)
- [ ] Ringkasan multi-tahun
