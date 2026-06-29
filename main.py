from models.individu import Normal, Carrier, Penderita
from models.user import ROLE_ADMIN, ROLE_USER
from models.exceptions import ThalasemiaAppError
from services.database import DatabaseJSON
from services.auth_service import AuthService
from services.kalkulator import KalkulatorGenetik

db = DatabaseJSON()
auth = AuthService()


def make_obj(status, id_p, nama, jk):
    return {"Normal": Normal, "Carrier": Carrier, "Penderita": Penderita}[status](id_p, nama, jk)


def input_jk():
    print("1. Laki-laki | 2. Perempuan")
    pilihan = input("Pilih Jenis Kelamin (1/2): ")
    return {"1": "Laki-laki", "2": "Perempuan"}.get(pilihan)


def input_status():
    print("1. Normal | 2. Carrier | 3. Penderita")
    pilihan = input("Pilih Status Genetik (1/2/3): ")
    return {"1": "Normal", "2": "Carrier", "3": "Penderita"}.get(pilihan)


def cetak_hasil_simulasi(hasil):
    ayah, ibu = hasil["ayah"], hasil["ibu"]
    print(f"\n👨 Ayah : {ayah}")
    print(f"👩 Ibu  : {ibu}")
    print("\nTabel Punnett:", hasil["kombinasi"])
    print("\nProbabilitas Keturunan:")
    for status, pct in hasil["hasil"].items():
        print(f"  {status:10s}: {pct:.0f}%")


# ════════════════════════════════════════════════════════════════════════
# MENU USER — hanya boleh kelola data dirinya & pasangannya
# ════════════════════════════════════════════════════════════════════════
def kelola_data(user, field_attr: str, label: str):
    existing_id = getattr(user, field_attr)
    record = db.cari_pasien(existing_id)

    if record:
        print(f"\n--- {label} (saat ini) ---")
        print(f"[{record['id']}] {record['nama']} - {record['status']} "
              f"({record['jenis_kelamin']}) ({record['alel1']},{record['alel2']})")
        ubah = input("Update data ini? (y/n): ").strip().lower()
        if ubah == 'y':
            nama = input("Nama baru: ")
            jk = input_jk()
            status = input_status()
            if not jk or not status:
                print("❌ Pilihan tidak valid.")
                return
            try:
                db.update_pasien(record["id"], nama.strip(), jk, status)
                print("✅ Data berhasil diupdate.")
            except ThalasemiaAppError as e:
                print(f"⚠️ {e.pesan}")
    else:
        print(f"\n{label} belum diisi.")
        id_p = input("ID: ")
        nama = input("Nama: ")
        jk = input_jk()
        status = input_status()
        if not id_p.strip() or not nama.strip() or not jk or not status:
            print("❌ Input tidak lengkap / tidak valid.")
            return
        try:
            obj = make_obj(status, id_p.strip(), nama.strip(), jk)
            db.tambah_pasien(obj)
            setattr(user, field_attr, obj.id_pasien)
            auth.update_user(user)
            print("✅ Data berhasil disimpan.")
        except ThalasemiaAppError as e:
            print(f"⚠️ {e.pesan}")


def kalkulasi_user(user):
    if not user.pasien_id or not user.pasangan_id:
        print("ℹ️ Lengkapi Data Saya dan Data Pasangan terlebih dahulu.")
        return
    diri = db.get_pasien_obj(user.pasien_id)
    pasangan = db.get_pasien_obj(user.pasangan_id)
    ayah, ibu = (diri, pasangan) if diri.jenis_kelamin == "Laki-laki" else (pasangan, diri)
    try:
        hasil = KalkulatorGenetik.simulasi(ayah, ibu)
        cetak_hasil_simulasi(hasil)
    except ThalasemiaAppError as e:
        print(f"⚠️ {e.pesan}")


def menu_user(user):
    while True:
        print("\n" + "=" * 40)
        print(f"MENU USER — {user.username}")
        print("=" * 40)
        print("1. Data Saya")
        print("2. Data Pasangan")
        print("3. Kalkulasi")
        print("0. Logout")
        pilihan = input("Pilih menu (0-3): ")

        if pilihan == '1':
            kelola_data(user, "pasien_id", "Data Saya")
        elif pilihan == '2':
            kelola_data(user, "pasangan_id", "Data Pasangan")
        elif pilihan == '3':
            kalkulasi_user(user)
        elif pilihan == '0':
            break
        else:
            print("❌ Pilihan tidak dikenali.")


# ════════════════════════════════════════════════════════════════════════
# MENU ADMIN — full CRUD
# ════════════════════════════════════════════════════════════════════════
def menu_admin():
    while True:
        print("\n" + "=" * 40)
        print("MENU ADMIN")
        print("=" * 40)
        print("1. Tambah Pasien Baru (CREATE)")
        print("2. Lihat Semua Pasien (READ)")
        print("3. Update Data Pasien (UPDATE)")
        print("4. Hapus Pasien (DELETE)")
        print("5. Simulasi Persilangan (KALKULATOR)")
        print("0. Logout")
        pilihan = input("Pilih menu (0-5): ")

        if pilihan == '1':
            id_p = input("ID Pasien: ")
            nama = input("Nama: ")
            jk = input_jk()
            status = input_status()
            if not id_p.strip() or not nama.strip() or not jk or not status:
                print("❌ Input tidak lengkap / tidak valid.")
                continue
            try:
                obj = make_obj(status, id_p.strip(), nama.strip(), jk)
                db.tambah_pasien(obj)
                print("✅ Pasien berhasil ditambahkan.")
            except ThalasemiaAppError as e:
                print(f"⚠️ {e.pesan}")

        elif pilihan == '2':
            data = db.ambil_semua_pasien()
            print("\n--- DAFTAR PASIEN ---")
            if not data:
                print("Data masih kosong.")
            for p in data:
                print(f"[{p['id']}] {p['nama']} - {p['status']} "
                      f"({p['jenis_kelamin']}) ({p['alel1']},{p['alel2']})")

        elif pilihan == '3':
            id_p = input("ID Pasien yang akan diupdate: ")
            nama = input("Nama Baru: ")
            jk = input_jk()
            status = input_status()
            if not jk or not status:
                print("❌ Pilihan tidak valid.")
                continue
            try:
                db.update_pasien(id_p, nama.strip(), jk, status)
                print("✅ Data berhasil diupdate.")
            except ThalasemiaAppError as e:
                print(f"⚠️ {e.pesan}")

        elif pilihan == '4':
            id_p = input("ID Pasien yang akan dihapus: ")
            try:
                db.hapus_pasien(id_p)
                print("✅ Pasien berhasil dihapus.")
            except ThalasemiaAppError as e:
                print(f"⚠️ {e.pesan}")

        elif pilihan == '5':
            id_ayah = input("ID Pasien Ayah: ")
            id_ibu = input("ID Pasien Ibu: ")
            try:
                ayah = db.get_pasien_obj(id_ayah)
                ibu = db.get_pasien_obj(id_ibu)
                hasil = KalkulatorGenetik.simulasi(ayah, ibu)
                cetak_hasil_simulasi(hasil)
            except ThalasemiaAppError as e:
                print(f"⚠️ {e.pesan}")

        elif pilihan == '0':
            break
        else:
            print("❌ Pilihan tidak dikenali.")


# ════════════════════════════════════════════════════════════════════════
# AUTENTIKASI
# ════════════════════════════════════════════════════════════════════════
def alur_user():
    while True:
        print("\n--- Akun User ---")
        print("1. Login")
        print("2. Daftar")
        print("0. Kembali")
        pilihan = input("Pilih (0-2): ")

        if pilihan == '1':
            u = input("Username: ")
            p = input("Password: ")
            try:
                user = auth.login(u, p, role_diharapkan=ROLE_USER)
                menu_user(user)
            except ThalasemiaAppError as e:
                print(f"⚠️ {e.pesan}")
        elif pilihan == '2':
            u = input("Username baru: ")
            p = input("Password: ")
            p2 = input("Konfirmasi Password: ")
            try:
                auth.register(u, p, p2)
                print("✅ Pendaftaran berhasil, silakan login.")
            except ThalasemiaAppError as e:
                print(f"⚠️ {e.pesan}")
        elif pilihan == '0':
            break
        else:
            print("❌ Pilihan tidak dikenali.")


def alur_admin():
    print("\n--- Login Admin ---")
    u = input("Username: ")
    p = input("Password: ")
    try:
        auth.login(u, p, role_diharapkan=ROLE_ADMIN)
        menu_admin()
    except ThalasemiaAppError as e:
        print(f"⚠️ {e.pesan}")


def main():
    while True:
        print("\n" + "=" * 40)
        print("SISTEM MANAJEMEN GENETIK THALASEMIA")
        print("=" * 40)
        print("1. Masuk sebagai User")
        print("2. Masuk sebagai Admin")
        print("0. Keluar")
        pilihan = input("Pilih menu (0-2): ")

        if pilihan == '1':
            alur_user()
        elif pilihan == '2':
            alur_admin()
        elif pilihan == '0':
            print("Keluar dari program. Sampai jumpa!")
            break
        else:
            print("❌ Pilihan tidak dikenali.")


if __name__ == "__main__":
    main()
