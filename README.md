# SiGen-Thal — Sistem Manajemen Genetik Thalasemia

## Cara Menjalankan

### 1. Aplikasi Web (Streamlit) — direkomendasikan
```bash
pip install -r requirements.txt
streamlit run app.py
```

### 2. Aplikasi CLI (Terminal)
```bash
python main.py
```

## Alur Aplikasi

1. **Landing Page** — pilih masuk sebagai **User** atau **Admin**.
2. **User**:
   - Bisa **Daftar** akun baru atau **Login**.
   - Setelah login, masuk ke halaman utama untuk mengisi **ID, Nama, Jenis Kelamin, Status Genetik** miliknya sendiri (Data Saya) dan data pasangannya (Data Pasangan).
   - User hanya dapat **Create** & **Update** data dirinya dan pasangannya saja, lalu menjalankan **Kalkulasi** risiko keturunan dari kedua data tersebut.
3. **Admin**:
   - Login dengan akun admin (default: `admin` / `admin123` — disarankan diganti).
   - Memiliki akses **full CRUD** (Create, Read, Update, Delete) atas seluruh data pasien dalam sistem, serta dapat menjalankan simulasi persilangan antar pasien manapun.

## Struktur Project
```
ThalasemiaAPP/
├── app.py                   # Aplikasi web Streamlit (landing, login, user/admin)
├── main.py                  # Aplikasi CLI dengan alur yang sama
├── models/
│   ├── individu.py          # Individu (ABC), Normal, Carrier, Penderita
│   ├── user.py              # Model akun (User)
│   └── exceptions.py        # Custom exception (muncul hanya saat input salah)
├── services/
│   ├── database.py          # CRUD data pasien (JSON)
│   ├── auth_service.py      # Registrasi & login akun
│   └── kalkulator.py        # Simulasi persilangan genetik (Hukum Mendel)
└── data/
    ├── pasien.json          # Data pasien
    └── users.json           # Data akun (dibuat otomatis saat pertama dijalankan)
```

## Catatan
- Pesan error hanya muncul saat terjadi input yang benar-benar salah (ID duplikat, password salah, dsb) — bukan ditampilkan terus-menerus sebagai label.
- Tidak ada lagi halaman "Peta OOP" — tampilan difokuskan pada fungsi aplikasi.
"# ThalaAPP" 
