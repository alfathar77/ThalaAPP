import hashlib

ROLE_ADMIN = "admin"
ROLE_USER = "user"


class User:
    """Merepresentasikan satu akun aplikasi (admin atau user biasa).

    Setiap akun bertipe `user` memiliki pranala (link) ke dua data pasien:
    - pasien_id   : data dirinya sendiri
    - pasangan_id : data pasangannya
    Akun bertipe `admin` tidak terikat pada data pasien manapun karena
    admin dapat mengelola seluruh data (full CRUD).
    """

    def __init__(self, username: str, password_hash: str, role: str = ROLE_USER,
                 pasien_id: str = None, pasangan_id: str = None):
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.pasien_id = pasien_id
        self.pasangan_id = pasangan_id

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def cek_password(self, password: str) -> bool:
        return self.password_hash == User.hash_password(password)

    @property
    def is_admin(self) -> bool:
        return self.role == ROLE_ADMIN

    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "password_hash": self.password_hash,
            "role": self.role,
            "pasien_id": self.pasien_id,
            "pasangan_id": self.pasangan_id,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            username=data["username"],
            password_hash=data["password_hash"],
            role=data.get("role", ROLE_USER),
            pasien_id=data.get("pasien_id"),
            pasangan_id=data.get("pasangan_id"),
        )

    def __str__(self):
        return f"{self.username} ({self.role})"

    def __repr__(self):
        return f"User(username={self.username!r}, role={self.role!r})"
