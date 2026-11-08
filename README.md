# Algoritma dan Pemrograman - Emergency Services App

Aplikasi Layanan Darurat (Emergency App) berbasis GUI menggunakan Python & Kivy, dilengkapi dengan sistem autentikasi pengguna, pelaporan berita darurat, panggilan layanan tanggap darurat, dan manajemen profil serta kontak darurat.

## 🚀 Fitur Utama
- **Autentikasi & Keamanan:** Enkripsi password menggunakan PBKDF2 dengan SHA-256 dan device hash session.
- **Layanan Panggilan Darurat:** Panggilan cepat Polisi (110), Pemadam Kebakaran (113), dan Medis (119) melalui integrasi Plyer.
- **Berita & Laporan Darurat:** Akses dan publikasi informasi darurat terkini.
- **Manajemen Profil & Kontak Darurat:** Pengaturan data pribadi dan nomor darurat keluarga/kerabat.

## 📁 Struktur Proyek
```text
.
├── main.py                     # Entry point aplikasi
├── Tubes.py                    # Wrapper kompatibilitas
├── app/
│   ├── security.py             # Enkripsi & validasi keamanan
│   ├── device_manager.py       # Session & local storage manager
│   ├── database.py             # SQLite database layer
│   └── screens/                # Modular screens UI (Kivy)
│       ├── base.py
│       ├── auth.py
│       ├── main_menu.py
│       ├── emergency.py
│       ├── news.py
│       └── profile.py
└── app_frs2/
    └── logoo.jpg               # Asset logo aplikasi
```

## 🛠️ Cara Menjalankan
1. Pastikan dependensi terpasang:
   ```bash
   pip install kivy plyer
   ```
2. Jalankan aplikasi:
   ```bash
   python main.py
   ```
