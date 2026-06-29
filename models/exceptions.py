"""
Custom Exception untuk SiGen-Thal.
Semua exception di sini hanya dipicu ketika user melakukan input yang salah
(ID duplikat, pasien tidak ditemukan, kombinasi tidak valid, dsb).
"""


class ThalasemiaAppError(Exception):
    """Base exception untuk seluruh aplikasi SiGen-Thal."""
    def __init__(self, pesan: str):
        super().__init__(pesan)
        self.pesan = pesan

    def __str__(self):
        return self.pesan


class ValidasiInputError(ThalasemiaAppError):
    """Raised untuk kesalahan input umum (field kosong, password tidak cocok, dll)."""
    pass


class PasienTidakDitemukanError(ThalasemiaAppError):
    """Raised ketika ID pasien tidak ada di database."""
    def __init__(self, id_pasien: str):
        super().__init__(f"Pasien dengan ID '{id_pasien}' tidak ditemukan.")
        self.id_pasien = id_pasien


class IDSudahAdaError(ThalasemiaAppError):
    """Raised ketika ID pasien yang diinput sudah dipakai pasien lain."""
    def __init__(self, id_pasien: str):
        super().__init__(f"ID '{id_pasien}' sudah digunakan oleh pasien lain.")
        self.id_pasien = id_pasien


class JenisKelaminTidakValidError(ThalasemiaAppError):
    """Raised ketika nilai jenis kelamin yang diinput tidak dikenali."""
    def __init__(self, nilai: str):
        super().__init__(f"Jenis kelamin '{nilai}' tidak valid.")
        self.nilai = nilai


class JenisKelaminSamaError(ThalasemiaAppError):
    """Raised ketika dua individu yang disilangkan berjenis kelamin sama."""
    def __init__(self, jk: str):
        super().__init__(
            f"Simulasi tidak valid: kedua individu berjenis kelamin '{jk}'. "
            "Persilangan membutuhkan satu Laki-laki dan satu Perempuan."
        )
        self.jenis_kelamin = jk


class PeranTidakSesuaiError(ThalasemiaAppError):
    """Raised ketika peran (Ayah/Ibu) tidak sesuai jenis kelamin pasien."""
    def __init__(self, nama: str, jk: str, peran: str):
        super().__init__(f"'{nama}' berjenis kelamin {jk} tidak bisa berperan sebagai {peran}.")
        self.nama = nama
        self.peran = peran


class UsernameSudahAdaError(ThalasemiaAppError):
    """Raised ketika username yang didaftarkan sudah dipakai."""
    def __init__(self, username: str):
        super().__init__(f"Username '{username}' sudah digunakan, silakan pilih yang lain.")
        self.username = username


class LoginGagalError(ThalasemiaAppError):
    """Raised ketika kombinasi username/password salah."""
    def __init__(self):
        super().__init__("Username atau password salah.")
