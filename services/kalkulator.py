import itertools
from models.exceptions import JenisKelaminSamaError, PeranTidakSesuaiError


class KalkulatorGenetik:
    """Kalkulator simulasi persilangan genetik Thalasemia (Hukum Mendel)."""

    @classmethod
    def validasi_pasangan(cls, ayah, ibu):
        if ayah.jenis_kelamin != "Laki-laki":
            raise PeranTidakSesuaiError(ayah.nama, ayah.jenis_kelamin, "Ayah")
        if ibu.jenis_kelamin != "Perempuan":
            raise PeranTidakSesuaiError(ibu.nama, ibu.jenis_kelamin, "Ibu")
        if ayah.jenis_kelamin == ibu.jenis_kelamin:
            raise JenisKelaminSamaError(ayah.jenis_kelamin)

    @staticmethod
    def hitung_kombinasi(gen_ayah: tuple, gen_ibu: tuple) -> dict:
        kombinasi = list(itertools.product(gen_ayah, gen_ibu))
        hasil = {"Normal": 0, "Carrier": 0, "Penderita": 0}
        for k in kombinasi:
            if k == ("N", "N"):
                hasil["Normal"] += 1
            elif "t" in k and "N" in k:
                hasil["Carrier"] += 1
            elif k == ("t", "t"):
                hasil["Penderita"] += 1
        return {s: (n / 4) * 100 for s, n in hasil.items()}

    @classmethod
    def simulasi(cls, ayah, ibu) -> dict:
        cls.validasi_pasangan(ayah, ibu)
        hasil_pct = ayah + ibu
        return {
            "ayah": ayah,
            "ibu": ibu,
            "gen_ayah": ayah.get_genotipe(),
            "gen_ibu": ibu.get_genotipe(),
            "kombinasi": list(itertools.product(ayah.get_genotipe(), ibu.get_genotipe())),
            "hasil": hasil_pct,
        }
