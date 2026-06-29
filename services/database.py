import json
import os
from models.individu import SerializableMixin
from models.exceptions import PasienTidakDitemukanError, IDSudahAdaError


class DatabaseJSON:
    """Lapisan persistensi JSON untuk data pasien."""

    def __init__(self, file_path: str = "data/pasien.json"):
        self.file_path = file_path
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            self._save_data([])

    def _save_data(self, data: list):
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def _load_data(self) -> list:
        with open(self.file_path, "r") as f:
            return json.load(f)

    def tambah_pasien(self, pasien):
        data = self._load_data()
        if any(p["id"] == pasien.id_pasien for p in data):
            raise IDSudahAdaError(pasien.id_pasien)
        data.append(pasien.to_dict())
        self._save_data(data)

    def ambil_semua_pasien(self) -> list:
        return self._load_data()

    def cari_pasien(self, id_pasien: str):
        if not id_pasien:
            return None
        for p in self._load_data():
            if p["id"] == id_pasien:
                return p
        return None

    def get_pasien_obj(self, id_pasien: str):
        data = self.cari_pasien(id_pasien)
        if data is None:
            raise PasienTidakDitemukanError(id_pasien)
        return SerializableMixin.from_dict(data)

    def update_pasien(self, id_pasien: str, nama_baru: str, jk_baru: str, status_baru: str):
        alel_map = {
            "Normal": ("N", "N"),
            "Carrier": ("N", "t"),
            "Penderita": ("t", "t"),
        }
        data = self._load_data()
        for p in data:
            if p["id"] == id_pasien:
                p["nama"] = nama_baru
                p["jenis_kelamin"] = jk_baru
                p["status"] = status_baru
                p["alel1"], p["alel2"] = alel_map[status_baru]
                self._save_data(data)
                return
        raise PasienTidakDitemukanError(id_pasien)

    def hapus_pasien(self, id_pasien: str):
        data = self._load_data()
        data_baru = [p for p in data if p["id"] != id_pasien]
        if len(data_baru) == len(data):
            raise PasienTidakDitemukanError(id_pasien)
        self._save_data(data_baru)
