from models.individu import Individu, Penderita


class RumahSakit:
    """
    Merepresentasikan sebuah Rumah Sakit yang menampung pasien Thalasemia.

    AGGREGATION — RumahSakit memiliki daftar Individu (pasien), tetapi
    objek Individu diciptakan di luar dan tidak ikut musnah jika objek
    RumahSakit ini dihapus. Pasien bisa saja pindah ke klinik lain.
    """

    def __init__(self, nama_rs: str):
        self.nama_rs = nama_rs
        self.daftar_pasien: list[
            Individu
        ] = []  # Aggregation — list referensi, bukan kepemilikan

    # ── Terima pasien dari luar ──────────────────────────────────────────
    def terima_pasien(self, pasien: Individu):
        """Menambahkan objek pasien ke daftar rumah sakit."""
        if any(p.id_pasien == pasien.id_pasien for p in self.daftar_pasien):
            print(f"⚠️  Pasien '{pasien.nama}' sudah terdaftar di {self.nama_rs}.")
            return
        self.daftar_pasien.append(
            pasien
        )  # pasien datang dari luar, bukan diciptakan di sini
        print(f"✅  Pasien '{pasien.nama}' diterima di {self.nama_rs}.")

    # ── Rujuk / keluarkan pasien (objeknya tetap hidup) ─────────────────
    def rujuk_pasien(self, id_pasien: str):
        """Mengeluarkan pasien dari daftar, objek Individu-nya TIDAK dihapus."""
        for p in self.daftar_pasien:
            if p.id_pasien == id_pasien:
                self.daftar_pasien.remove(p)
                print(f"🔄  Pasien '{p.nama}' dirujuk keluar dari {self.nama_rs}.")
                return
        print(f"⚠️  Pasien ID '{id_pasien}' tidak ditemukan di {self.nama_rs}.")

    # ── Filter pasien kritis ─────────────────────────────────────────────
    def tampilkan_pasien_kritis(self) -> list[Penderita]:
        """
        Mengembalikan daftar pasien berstatus Penderita (Thalasemia Mayor)
        yang membutuhkan transfusi darah segera.
        """
        kritis = [p for p in self.daftar_pasien if isinstance(p, Penderita)]
        return kritis

    # ── Dunder ──────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return f"RumahSakit('{self.nama_rs}', {len(self.daftar_pasien)} pasien)"

    def __repr__(self) -> str:
        return f"RumahSakit(nama_rs={self.nama_rs!r})"

    def __len__(self) -> int:
        return len(self.daftar_pasien)
