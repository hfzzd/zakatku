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
```

Data tersimpan di `zakatku.json` di folder kerja (atau file lain lewat
`--data`, atau variabel lingkungan `ZAKATKU_DATA`).

## Rencana

- [x] Zakat profesi & zakat fitrah + CLI dasar
- [ ] Zakat mal + pencatatan pembayaran + laporan tahunan
- [ ] Unit test + data contoh + polish CLI
- [ ] Pengingat haul & nisab, ekspor CSV
