from abc import ABC, abstractmethod
import itertools
from models.exceptions import JenisKelaminTidakValidError

JENIS_KELAMIN_VALID = {"Laki-laki", "Perempuan"}


class GenotipePasien:
    """
    Merepresentasikan informasi genotipe sepasang alel milik satu individu.

    COMPOSITION — class ini diciptakan di dalam Individu, dimiliki sepenuhnya
    oleh Individu, dan tidak memiliki makna di luar konteks Individu tersebut.
    """

    def __init__(self, alel1: str, alel2: str):
        self.__alel1 = alel1   # simpan langsung, bukan rekursif
        self.__alel2 = alel2

    @property
    def alel1(self) -> str:
        return self.__alel1

    @property
    def alel2(self) -> str:
        return self.__alel2

    def get_alel(self) -> tuple:
        return (self.__alel1, self.__alel2)

    def __str__(self) -> str:
        return f"({self.__alel1},{self.__alel2})"

    def __repr__(self) -> str:
        return f"GenotipePasien(alel1={self.__alel1!r}, alel2={self.__alel2!r})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, GenotipePasien):
            return NotImplemented
        return self.get_alel() == other.get_alel()


class SerializableMixin:
    """Mixin untuk serialisasi objek pasien ke/dari dict (JSON)."""

    def to_dict(self) -> dict:
        a1, a2 = self.get_genotipe()
        return {
            "id": self.id_pasien,
            "nama": self.nama,
            "jenis_kelamin": self.jenis_kelamin,
            "alel1": a1,
            "alel2": a2,
            "status": self.__class__.__name__,
        }

    @classmethod
    def from_dict(cls, data: dict):
        from models.individu import Normal, Carrier, Penderita
        peta = {"Normal": Normal, "Carrier": Carrier, "Penderita": Penderita}
        kelas = peta.get(data["status"])
        if kelas is None:
            raise ValueError(f"Status tidak dikenal: {data['status']}")
        return kelas(data["id"], data["nama"], data["jenis_kelamin"])


class Individu(SerializableMixin, ABC):
    """Base class abstrak untuk semua individu dalam sistem genetik thalasemia."""

    def __init__(self, id_pasien: str, nama: str, jenis_kelamin: str, alel1: str, alel2: str):
        self.id_pasien = id_pasien
        self.nama = nama
        self.jenis_kelamin = jenis_kelamin
        self.__genotipe = GenotipePasien(alel1, alel2)  # COMPOSITION — diciptakan & dimiliki di sini

    @property
    def jenis_kelamin(self) -> str:
        return self.__jenis_kelamin

    @jenis_kelamin.setter
    def jenis_kelamin(self, nilai: str):
        if nilai not in JENIS_KELAMIN_VALID:
            raise JenisKelaminTidakValidError(nilai)
        self.__jenis_kelamin = nilai

    @property
    def alel1(self) -> str:
        return self.__genotipe.alel1

    @property
    def alel2(self) -> str:
        return self.__genotipe.alel2

    def get_genotipe(self) -> tuple:
        return self.__genotipe.get_alel()

    def info_genotipe(self) -> GenotipePasien:
        """Akses langsung ke objek GenotipePasien."""
        return self.__genotipe

    def __str__(self) -> str:
        return (f"[{self.id_pasien}] {self.nama} ({self.jenis_kelamin}) "
                f"— {self.__class__.__name__} {self.__genotipe}")

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}(id={self.id_pasien!r}, "
                f"nama={self.nama!r}, jk={self.jenis_kelamin!r})")

    def __eq__(self, other) -> bool:
        if not isinstance(other, Individu):
            return NotImplemented
        return self.id_pasien == other.id_pasien

    def __hash__(self):
        return hash(self.id_pasien)

    def __add__(self, other):
        """Operator + : simulasikan persilangan self x other → dict probabilitas keturunan."""
        if not isinstance(other, Individu):
            return NotImplemented
        kombinasi = list(itertools.product(self.get_genotipe(), other.get_genotipe()))
        hasil = {"Normal": 0, "Carrier": 0, "Penderita": 0}
        for k in kombinasi:
            if k == ("N", "N"):
                hasil["Normal"] += 1
            elif "t" in k and "N" in k:
                hasil["Carrier"] += 1
            elif k == ("t", "t"):
                hasil["Penderita"] += 1
        return {s: (n / 4) * 100 for s, n in hasil.items()}

    @abstractmethod
    def deskripsi_fenotipe(self) -> str:
        pass

    @abstractmethod
    def risiko_level(self) -> str:
        """Level risiko: 'rendah', 'sedang', 'tinggi'."""
        pass


class Normal(Individu):
    """Individu dengan genotipe NN — tidak membawa gen thalasemia."""

    def __init__(self, id_pasien: str, nama: str, jenis_kelamin: str):
        super().__init__(id_pasien, nama, jenis_kelamin, "N", "N")

    def deskripsi_fenotipe(self) -> str:
        return "Sehat — tidak membawa gen Thalasemia"

    def risiko_level(self) -> str:
        return "rendah"


class Carrier(Individu):
    """Individu dengan genotipe Nt — pembawa gen thalasemia (Thalasemia Minor)."""

    def __init__(self, id_pasien: str, nama: str, jenis_kelamin: str):
        super().__init__(id_pasien, nama, jenis_kelamin, "N", "t")

    def deskripsi_fenotipe(self) -> str:
        return "Thalasemia Minor / Carrier — pembawa gen"

    def risiko_level(self) -> str:
        return "sedang"


class Penderita(Individu):
    """Individu dengan genotipe tt — penderita Thalasemia Mayor."""

    def __init__(self, id_pasien: str, nama: str, jenis_kelamin: str):
        super().__init__(id_pasien, nama, jenis_kelamin, "t", "t")

    def deskripsi_fenotipe(self) -> str:
        return "Thalasemia Mayor — membutuhkan perawatan rutin"

    def risiko_level(self) -> str:
        return "tinggi"
