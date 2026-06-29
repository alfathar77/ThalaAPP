import json
import os
from models.user import User, ROLE_ADMIN, ROLE_USER
from models.exceptions import UsernameSudahAdaError, LoginGagalError, ValidasiInputError

ADMIN_DEFAULT_USERNAME = "admin"
ADMIN_DEFAULT_PASSWORD = "admin123"


class AuthService:
    """Lapisan persistensi JSON untuk akun pengguna (registrasi & login)."""

    def __init__(self, file_path: str = "data/users.json"):
        self.file_path = file_path
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            self._save_data([])
        self._seed_admin()

    def _load_data(self) -> list:
        with open(self.file_path, "r") as f:
            return json.load(f)

    def _save_data(self, data: list):
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def _seed_admin(self):
        data = self._load_data()
        if not any(u.get("role") == ROLE_ADMIN for u in data):
            admin = User(ADMIN_DEFAULT_USERNAME, User.hash_password(ADMIN_DEFAULT_PASSWORD), role=ROLE_ADMIN)
            data.append(admin.to_dict())
            self._save_data(data)

    def register(self, username: str, password: str, konfirmasi: str) -> User:
        username = (username or "").strip()
        if not username or not password:
            raise ValidasiInputError("Username dan password tidak boleh kosong.")
        if len(password) < 4:
            raise ValidasiInputError("Password minimal 4 karakter.")
        if password != konfirmasi:
            raise ValidasiInputError("Konfirmasi password tidak cocok.")
        data = self._load_data()
        if any(u["username"].lower() == username.lower() for u in data):
            raise UsernameSudahAdaError(username)
        user = User(username, User.hash_password(password), role=ROLE_USER)
        data.append(user.to_dict())
        self._save_data(data)
        return user

    def login(self, username: str, password: str, role_diharapkan: str = None) -> User:
        username = (username or "").strip()
        if not username or not password:
            raise ValidasiInputError("Username dan password tidak boleh kosong.")
        for u in self._load_data():
            if u["username"].lower() == username.lower():
                user = User.from_dict(u)
                cocok_role = role_diharapkan is None or user.role == role_diharapkan
                if user.cek_password(password) and cocok_role:
                    return user
                break
        raise LoginGagalError()

    def update_user(self, user: User):
        data = self._load_data()
        for u in data:
            if u["username"] == user.username:
                u.update(user.to_dict())
                self._save_data(data)
                return
