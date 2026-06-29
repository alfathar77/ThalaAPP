import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from models.individu import Normal, Carrier, Penderita
from models.user import ROLE_ADMIN, ROLE_USER
from models.exceptions import ThalasemiaAppError, ValidasiInputError
from services.database import DatabaseJSON
from services.auth_service import AuthService
from services.kalkulator import KalkulatorGenetik
from models.rumah_sakit import RumahSakit

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(page_title="SiGen-Thal", page_icon="🧬", layout="wide")

BASE_DIR = os.path.dirname(__file__)
db   = DatabaseJSON(os.path.join(BASE_DIR, "data", "pasien.json"))
auth = AuthService(os.path.join(BASE_DIR, "data", "users.json"))

# ── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:#0f1117}
[data-testid="stSidebar"]{background:#161b27}
h1{background:linear-gradient(90deg,#7b61ff,#00c9a7);-webkit-background-clip:text;
   -webkit-text-fill-color:transparent;font-size:2rem}
.badge{display:inline-block;padding:3px 12px;border-radius:20px;
       font-size:.78rem;font-weight:600;margin:2px}
.bn{background:#1a3a2a;color:#4ade80}
.bc{background:#3a2a10;color:#fbbf24}
.bp{background:#3a1010;color:#f87171}
.bm{background:#1a2a3a;color:#60a5fa}
.bf{background:#1a1a3a;color:#a78bfa}
.card{background:#1e2436;border-radius:12px;padding:18px 22px;
      border:1px solid #2a3150;margin-bottom:8px}
.role-card{background:#1e2436;border-radius:16px;padding:36px 24px;
      border:1px solid #2a3150;text-align:center;margin-bottom:8px}
</style>
""", unsafe_allow_html=True)

# ── Konstanta tampilan ───────────────────────────────────────────────────
STATUS_LIST = ["Normal", "Carrier", "Penderita"]
JK_LIST     = ["Laki-laki", "Perempuan"]
STATUS_CLS  = {"Normal": "bn", "Carrier": "bc", "Penderita": "bp"}
RISIKO_CLR  = {"rendah": "#4ade80", "sedang": "#fbbf24", "tinggi": "#f87171"}


def badge(text, cls):
    return f'<span class="badge {cls}">{text}</span>'


def make_obj(status, id_p, nama, jk):
    return {"Normal": Normal, "Carrier": Carrier, "Penderita": Penderita}[status](id_p, nama, jk)


def show_err(e):
    """Menampilkan pesan error HANYA ketika sebuah exception benar-benar terjadi."""
    if isinstance(e, ThalasemiaAppError):
        st.error(f"⚠️ {e.pesan}")
    else:
        st.error(str(e))


def pasien_card(p: dict) -> str:
    jk = p.get("jenis_kelamin", "-")
    return f"""<div class="card">
      <b>ID:</b> {p['id']} &nbsp; <b>Nama:</b> {p['nama']}<br>
      {badge(jk, 'bm' if jk == 'Laki-laki' else 'bf')}
      {badge(p['status'], STATUS_CLS[p['status']])}
      <br><code>Genotipe: ({p['alel1']},{p['alel2']})</code>
    </div>"""


def render_hasil_simulasi(hasil: dict):
    """Menampilkan hasil simulasi persilangan (Punnett table + probabilitas)."""
    ayah_obj, ibu_obj = hasil["ayah"], hasil["ibu"]

    ca, ci = st.columns(2)
    for col, obj, ikon in [(ca, ayah_obj, "👨"), (ci, ibu_obj, "👩")]:
        with col:
            rv = obj.risiko_level()
            st.markdown(f"""<div class="card">
              <b>{ikon} {obj.nama}</b><br>
              {badge(obj.jenis_kelamin, 'bm' if obj.jenis_kelamin == 'Laki-laki' else 'bf')}
              {badge(obj.__class__.__name__, STATUS_CLS[obj.__class__.__name__])}<br>
              <code>Genotipe: {obj.get_genotipe()}</code><br>
              <small style="color:#8892b0">{obj.deskripsi_fenotipe()}</small><br>
              <small>Risiko: <b style="color:{RISIKO_CLR[rv]}">{rv.upper()}</b></small>
            </div>""", unsafe_allow_html=True)

    st.markdown("### 🔲 Tabel Punnett")
    gen_a, gen_i = hasil["gen_ayah"], hasil["gen_ibu"]
    color_map = {
        ("N", "N"): ("#1a3a2a", "#4ade80", "Normal"),
        ("N", "t"): ("#3a2a10", "#fbbf24", "Carrier"),
        ("t", "N"): ("#3a2a10", "#fbbf24", "Carrier"),
        ("t", "t"): ("#3a1010", "#f87171", "Penderita"),
    }
    hdr = '<table style="border-collapse:separate;border-spacing:6px;margin:auto">'
    hdr += '<tr><td style="padding:12px;background:#2a3150;border-radius:8px;color:#8892b0;text-align:center;min-width:90px">♂ \\ ♀</td>'
    for g in gen_i:
        hdr += f'<td style="padding:12px;background:#2a3150;border-radius:8px;font-weight:700;color:#cdd6f4;text-align:center;min-width:110px">{g}</td>'
    hdr += "</tr>"
    rows_html = ""
    for ga in gen_a:
        rows_html += f'<tr><td style="padding:12px;background:#2a3150;border-radius:8px;font-weight:700;color:#cdd6f4;text-align:center">{ga}</td>'
        for gi in gen_i:
            bg, fg, lbl = color_map.get((ga, gi), ("#1e2436", "#cdd6f4", "?"))
            rows_html += (f'<td style="padding:14px;background:{bg};border-radius:8px;'
                          f'text-align:center;font-weight:600;color:{fg}">'
                          f'{ga}{gi}<br><small>{lbl}</small></td>')
        rows_html += "</tr>"
    st.markdown(f'<div style="overflow-x:auto">{hdr}{rows_html}</table></div>', unsafe_allow_html=True)

    st.markdown("### 📊 Probabilitas Keturunan")
    clrs = {"Normal": "#4ade80", "Carrier": "#fbbf24", "Penderita": "#f87171"}
    cols = st.columns(3)
    for i, (s, pct) in enumerate(hasil["hasil"].items()):
        with cols[i]:
            st.markdown(f"""<div class="card" style="text-align:center;border-color:{clrs[s]}40">
              <div style="color:{clrs[s]};font-size:2.4rem;font-weight:700">{pct:.0f}%</div>
              <div style="color:#8892b0">{s}</div>
              <div style="background:{clrs[s]}30;border-radius:8px;height:8px;margin-top:10px">
                <div style="background:{clrs[s]};height:8px;border-radius:8px;width:{pct:.0f}%"></div>
              </div>
            </div>""", unsafe_allow_html=True)

    pct_p = hasil["hasil"]["Penderita"]
    if pct_p > 0:
        st.warning(f"⚠️ Ada risiko **{pct_p:.0f}%** keturunan menderita Thalasemia Mayor.")
    elif hasil["hasil"]["Carrier"] > 0:
        st.info("ℹ️ Tidak ada risiko Thalasemia Mayor, namun keturunan bisa menjadi Carrier.")
    else:
        st.success("✅ Tidak ada risiko genetik Thalasemia pada keturunan.")


# ── Session state & navigasi ────────────────────────────────────────────
if "view" not in st.session_state:
    st.session_state.view = "landing"
if "user" not in st.session_state:
    st.session_state.user = None
if "rumah_sakit" not in st.session_state:
    st.session_state.rumah_sakit = RumahSakit("RS Thalasemia Nusantara")

def goto(view):
    st.session_state.view = view
    st.rerun()


def logout():
    st.session_state.user = None
    st.session_state.view = "landing"
    st.rerun()


# ════════════════════════════════════════════════════════════════════════
# LANDING PAGE
# ════════════════════════════════════════════════════════════════════════
def render_landing():
    st.markdown("# 🧬 SiGen-Thal")
    st.caption("Sistem Manajemen Genetik Thalasemia")
    st.markdown("#### Masuk sebagai:")
    st.markdown("")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""<div class="role-card">
          <div style="font-size:2.6rem">👤</div>
          <h3>User</h3>
          <p style="color:#8892b0">Daftar / login, lalu kelola data Anda &amp; pasangan
          untuk menghitung simulasi keturunan.</p>
        </div>""", unsafe_allow_html=True)
        if st.button("Lanjut sebagai User", use_container_width=True, type="primary"):
            goto("user_auth")
    with c2:
        st.markdown("""<div class="role-card">
          <div style="font-size:2.6rem">🛡️</div>
          <h3>Admin</h3>
          <p style="color:#8892b0">Login untuk mengelola seluruh data pasien
          dalam sistem (Create, Read, Update, Delete).</p>
        </div>""", unsafe_allow_html=True)
        if st.button("Lanjut sebagai Admin", use_container_width=True):
            goto("admin_auth")


# ════════════════════════════════════════════════════════════════════════
# AUTENTIKASI USER (Login / Daftar)
# ════════════════════════════════════════════════════════════════════════
def render_user_auth():
    st.markdown("# 👤 Masuk sebagai User")
    if st.button("← Kembali"):
        goto("landing")
    st.markdown("")

    tab_login, tab_daftar = st.tabs(["🔑 Login", "📝 Daftar Akun Baru"])

    with tab_login:
        with st.form("form_login_user"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True, type="primary")
        if submit:
            try:
                user = auth.login(u, p, role_diharapkan=ROLE_USER)
                st.session_state.user = user
                goto("user_app")
            except ThalasemiaAppError as e:
                show_err(e)

    with tab_daftar:
        with st.form("form_daftar_user"):
            u  = st.text_input("Username Baru")
            p  = st.text_input("Password", type="password")
            p2 = st.text_input("Konfirmasi Password", type="password")
            submit = st.form_submit_button("Daftar", use_container_width=True)
        if submit:
            try:
                auth.register(u, p, p2)
                st.success("✅ Pendaftaran berhasil! Silakan login pada tab di sebelah.")
            except ThalasemiaAppError as e:
                show_err(e)


# ════════════════════════════════════════════════════════════════════════
# AUTENTIKASI ADMIN (Login saja)
# ════════════════════════════════════════════════════════════════════════
def render_admin_auth():
    st.markdown("# 🛡️ Login Admin")
    if st.button("← Kembali"):
        goto("landing")
    st.markdown("")

    with st.form("form_login_admin"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", use_container_width=True, type="primary")
    if submit:
        try:
            user = auth.login(u, p, role_diharapkan=ROLE_ADMIN)
            st.session_state.user = user
            goto("admin_app")
        except ThalasemiaAppError as e:
            show_err(e)


# ════════════════════════════════════════════════════════════════════════
# APLIKASI USER — hanya boleh kelola data dirinya & pasangannya
# ════════════════════════════════════════════════════════════════════════
def render_form_data(user, field_attr: str, judul: str):
    """Form Create/Update data pasien milik akun user (untuk dirinya atau pasangannya)."""
    st.markdown(f"# {judul}")

    existing_id = getattr(user, field_attr)
    record = db.cari_pasien(existing_id)

    if record:
        st.markdown(pasien_card(record), unsafe_allow_html=True)
        st.markdown("#### ✏️ Perbarui Data")
        with st.form(f"form_update_{field_attr}"):
            nama_baru = st.text_input("Nama", value=record["nama"])
            jk_baru   = st.selectbox("Jenis Kelamin", JK_LIST,
                            index=JK_LIST.index(record.get("jenis_kelamin", "Laki-laki")))
            status_baru = st.selectbox("Status Genetik", STATUS_LIST,
                            index=STATUS_LIST.index(record["status"]))
            submitted = st.form_submit_button("💾 Update", use_container_width=True)
        if submitted:
            try:
                if not nama_baru.strip():
                    raise ValidasiInputError("Nama tidak boleh kosong.")
                db.update_pasien(record["id"], nama_baru.strip(), jk_baru, status_baru)
                st.success("✅ Data berhasil diperbarui!")
                st.rerun()
            except ThalasemiaAppError as e:
                show_err(e)
    else:
        st.info("Data belum diisi. Silakan lengkapi form di bawah ini.")
        with st.form(f"form_create_{field_attr}"):
            id_p   = st.text_input("ID", placeholder="mis. 007")
            nama   = st.text_input("Nama", placeholder="mis. Budi Santoso")
            jk     = st.selectbox("Jenis Kelamin", JK_LIST)
            status = st.selectbox("Status Genetik", STATUS_LIST)
            submitted = st.form_submit_button("💾 Simpan", use_container_width=True, type="primary")
        if submitted:
            try:
                if not id_p.strip() or not nama.strip():
                    raise ValidasiInputError("ID dan Nama tidak boleh kosong.")
                obj = make_obj(status, id_p.strip(), nama.strip(), jk)
                db.tambah_pasien(obj)
                setattr(user, field_attr, obj.id_pasien)
                auth.update_user(user)
                st.session_state.user = user
                st.success("✅ Data berhasil disimpan!")
                st.rerun()
            except ThalasemiaAppError as e:
                show_err(e)


def render_kalkulasi_user(user):
    st.markdown("# 🧬 Kalkulasi Risiko Keturunan")

    if not user.pasien_id or not user.pasangan_id:
        st.info("Lengkapi **Data Saya** dan **Data Pasangan** terlebih dahulu untuk menjalankan kalkulasi.")
        return

    diri     = db.get_pasien_obj(user.pasien_id)
    pasangan = db.get_pasien_obj(user.pasangan_id)
    ayah, ibu = (diri, pasangan) if diri.jenis_kelamin == "Laki-laki" else (pasangan, diri)

    cd, cp = st.columns(2)
    with cd:
        st.markdown("**Data Saya**")
        st.markdown(pasien_card(db.cari_pasien(user.pasien_id)), unsafe_allow_html=True)
    with cp:
        st.markdown("**Data Pasangan**")
        st.markdown(pasien_card(db.cari_pasien(user.pasangan_id)), unsafe_allow_html=True)

    if st.button("🔬 Jalankan Kalkulasi", type="primary", use_container_width=True):
        try:
            hasil = KalkulatorGenetik.simulasi(ayah, ibu)
            st.markdown("---")
            render_hasil_simulasi(hasil)
        except ThalasemiaAppError as e:
            show_err(e)


def render_user_app():
    user = st.session_state.user
    if user is None:
        goto("landing")
        return

    with st.sidebar:
        st.markdown("## 🧬 SiGen-Thal")
        st.caption(f"👤 {user.username}")
        st.markdown("---")
        menu = st.radio("", ["🏠 Data Saya", "💑 Data Pasangan", "🧬 Kalkulasi"],
                         label_visibility="collapsed")
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout()

    if menu == "🏠 Data Saya":
        render_form_data(user, "pasien_id", "🏠 Data Saya")
    elif menu == "💑 Data Pasangan":
        render_form_data(user, "pasangan_id", "💑 Data Pasangan")
    elif menu == "🧬 Kalkulasi":
        render_kalkulasi_user(user)


# ════════════════════════════════════════════════════════════════════════
# APLIKASI ADMIN — full CRUD atas seluruh data pasien
# ════════════════════════════════════════════════════════════════════════
def render_dashboard():
    st.markdown("# 📊 Dashboard Pasien")
    data = db.ambil_semua_pasien()

    total     = len(data)
    lk        = sum(1 for p in data if p.get("jenis_kelamin") == "Laki-laki")
    pr        = sum(1 for p in data if p.get("jenis_kelamin") == "Perempuan")
    normal    = sum(1 for p in data if p["status"] == "Normal")
    carrier   = sum(1 for p in data if p["status"] == "Carrier")
    penderita = sum(1 for p in data if p["status"] == "Penderita")

    cols = st.columns(6)
    for col, lbl, num, clr in [
        (cols[0], "Total",     total,     "#7b61ff"),
        (cols[1], "👨 L",      lk,        "#60a5fa"),
        (cols[2], "👩 P",      pr,        "#f472b6"),
        (cols[3], "Normal",    normal,    "#4ade80"),
        (cols[4], "Carrier",   carrier,   "#fbbf24"),
        (cols[5], "Penderita", penderita, "#f87171"),
    ]:
        with col:
            st.markdown(f"""<div class="card" style="text-align:center">
            <div style="color:#8892b0;font-size:.75rem">{lbl}</div>
            <div style="color:{clr};font-size:2rem;font-weight:700">{num}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Daftar Pasien")
    if not data:
        st.info("Belum ada data pasien.")
        return

    rows = ""
    for p in data:
        jk = p.get("jenis_kelamin", "?")
        rows += f"""<tr>
          <td style="padding:9px 12px;color:#cdd6f4">{p['id']}</td>
          <td style="padding:9px 12px;color:#cdd6f4">{p['nama']}</td>
          <td style="padding:9px 12px">{badge(jk, 'bm' if jk=='Laki-laki' else 'bf')}</td>
          <td style="padding:9px 12px">{badge(p['status'], STATUS_CLS[p['status']])}</td>
          <td style="padding:9px 12px;color:#8892b0;font-family:monospace">
            ({p['alel1']},{p['alel2']})</td>
        </tr>"""
    st.markdown(f"""<table style="width:100%;border-collapse:collapse;
      background:#1e2436;border-radius:12px;overflow:hidden">
      <thead><tr style="background:#2a3150">
        <th style="padding:9px 12px;text-align:left;color:#8892b0">ID</th>
        <th style="padding:9px 12px;text-align:left;color:#8892b0">Nama</th>
        <th style="padding:9px 12px;text-align:left;color:#8892b0">Jenis Kelamin</th>
        <th style="padding:9px 12px;text-align:left;color:#8892b0">Status</th>
        <th style="padding:9px 12px;text-align:left;color:#8892b0">Genotipe</th>
      </tr></thead><tbody>{rows}</tbody></table>""", unsafe_allow_html=True)


def render_tambah_pasien():
    st.markdown("# ➕ Tambah Pasien Baru")
    with st.form("form_tambah", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            id_p = st.text_input("ID Pasien", placeholder="mis. 007")
            nama = st.text_input("Nama Pasien", placeholder="mis. Budi Santoso")
        with col2:
            jk     = st.selectbox("Jenis Kelamin", JK_LIST)
            status = st.selectbox("Status Genetik", STATUS_LIST)

        alel_info = {"Normal": "NN", "Carrier": "Nt", "Penderita": "tt"}
        desc_info = {
            "Normal":    "✅ Sehat, tidak membawa gen thalasemia",
            "Carrier":   "⚠️ Thalasemia Minor — pembawa gen",
            "Penderita": "🔴 Thalasemia Mayor — butuh perawatan rutin",
        }
        st.markdown(f"**Genotipe:** `{alel_info[status]}` · {desc_info[status]}")
        submitted = st.form_submit_button("💾 Simpan", use_container_width=True, type="primary")

    if submitted:
        try:
            if not id_p.strip() or not nama.strip():
                raise ValidasiInputError("ID dan Nama tidak boleh kosong.")
            obj = make_obj(status, id_p.strip(), nama.strip(), jk)
            db.tambah_pasien(obj)
            st.success(f"✅ Pasien **{nama}** berhasil ditambahkan!")
        except ThalasemiaAppError as e:
            show_err(e)


def render_update_pasien():
    st.markdown("# ✏️ Update Data Pasien")
    data = db.ambil_semua_pasien()
    if not data:
        st.info("Belum ada data pasien.")
        return

    opts    = {f"[{p['id']}] {p['nama']} ({p['status']})": p for p in data}
    pilihan = st.selectbox("Pilih Pasien", list(opts.keys()))
    p_lama  = opts[pilihan]

    with st.form("form_update"):
        st.markdown(f"**ID:** `{p_lama['id']}`")
        col1, col2 = st.columns(2)
        with col1:
            nama_baru = st.text_input("Nama Baru", value=p_lama["nama"])
            jk_baru   = st.selectbox("Jenis Kelamin", JK_LIST,
                            index=JK_LIST.index(p_lama.get("jenis_kelamin", "Laki-laki")))
        with col2:
            st_baru = st.selectbox("Status Baru", STATUS_LIST,
                            index=STATUS_LIST.index(p_lama["status"]))
        submitted = st.form_submit_button("💾 Update", use_container_width=True, type="primary")

    if submitted:
        try:
            if not nama_baru.strip():
                raise ValidasiInputError("Nama tidak boleh kosong.")
            db.update_pasien(p_lama["id"], nama_baru.strip(), jk_baru, st_baru)
            st.success(f"✅ Data **{nama_baru}** berhasil diupdate!")
        except ThalasemiaAppError as e:
            show_err(e)


def render_hapus_pasien():
    st.markdown("# 🗑️ Hapus Pasien")
    data = db.ambil_semua_pasien()
    if not data:
        st.info("Belum ada data pasien.")
        return

    opts    = {f"[{p['id']}] {p['nama']} ({p['status']})": p for p in data}
    pilihan = st.selectbox("Pilih Pasien", list(opts.keys()))
    p_hapus = opts[pilihan]

    st.markdown(pasien_card(p_hapus), unsafe_allow_html=True)

    if st.button("🗑️ Hapus", type="primary", use_container_width=True):
        try:
            db.hapus_pasien(p_hapus["id"])
            st.success("✅ Pasien berhasil dihapus!")
            st.rerun()
        except ThalasemiaAppError as e:
            show_err(e)


def render_simulasi_admin():
    st.markdown("# 🔬 Simulasi Persilangan Genetik")
    data = db.ambil_semua_pasien()
    if len(data) < 2:
        st.warning("Minimal 2 pasien diperlukan.")
        return

    laki   = [p for p in data if p.get("jenis_kelamin") == "Laki-laki"]
    wanita = [p for p in data if p.get("jenis_kelamin") == "Perempuan"]

    if not laki:
        st.error("Tidak ada pasien Laki-laki di database. Tambahkan dulu.")
        return
    if not wanita:
        st.error("Tidak ada pasien Perempuan di database. Tambahkan dulu.")
        return

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### 👨 Ayah (Laki-laki)")
        sel_ayah = st.selectbox("Pilih Ayah", [f"[{p['id']}] {p['nama']} ({p['status']})" for p in laki])
    with col_b:
        st.markdown("#### 👩 Ibu (Perempuan)")
        sel_ibu = st.selectbox("Pilih Ibu", [f"[{p['id']}] {p['nama']} ({p['status']})" for p in wanita])

    if st.button("🔬 Jalankan Simulasi", type="primary", use_container_width=True):
        try:
            id_ayah = sel_ayah.split("]")[0][1:]
            id_ibu  = sel_ibu.split("]")[0][1:]
            ayah_obj = db.get_pasien_obj(id_ayah)
            ibu_obj  = db.get_pasien_obj(id_ibu)
            hasil = KalkulatorGenetik.simulasi(ayah_obj, ibu_obj)
            st.markdown("---")
            render_hasil_simulasi(hasil)
        except ThalasemiaAppError as e:
            show_err(e)
            
def render_rumah_sakit():
    rs = st.session_state.rumah_sakit  # ambil dari session_state, bukan variabel modul

    st.markdown(f"# 🏥 {rs.nama_rs}")
    st.caption("Aggregation — pasien dikelola rumah sakit, namun tetap hidup di luar sistem ini.")

    data_semua = db.ambil_semua_pasien()
    if not data_semua:
        st.info("Belum ada data pasien di database.")
        return

    # ── Terima pasien ────────────────────────────────────────────────────
    st.markdown("### ➕ Terima Pasien")
    id_terdaftar = {p.id_pasien for p in rs.daftar_pasien}
    belum_masuk  = [p for p in data_semua if p["id"] not in id_terdaftar]

    if belum_masuk:
        opts_masuk = {f"[{p['id']}] {p['nama']} ({p['status']})": p for p in belum_masuk}
        pilihan_masuk = st.selectbox("Pilih pasien untuk diterima", list(opts_masuk.keys()),
                                      key="select_terima")
        if st.button("✅ Terima Pasien", use_container_width=True):
            obj = db.get_pasien_obj(opts_masuk[pilihan_masuk]["id"])
            rs.terima_pasien(obj)
            st.success(f"Pasien **{obj.nama}** diterima di {rs.nama_rs}.")
            st.rerun()
    else:
        st.info("Semua pasien dari database sudah terdaftar di rumah sakit ini.")

    st.markdown("---")

    # ── Daftar pasien aktif ──────────────────────────────────────────────
    st.markdown(f"### 📋 Pasien Aktif ({len(rs)} orang)")
    if not rs.daftar_pasien:
        st.info("Belum ada pasien yang diterima.")
    else:
        for p in rs.daftar_pasien:
            col_info, col_btn = st.columns([5, 1])
            with col_info:
                st.markdown(pasien_card(p.to_dict()), unsafe_allow_html=True)
            with col_btn:
                if st.button("🔄 Rujuk", key=f"rujuk_{p.id_pasien}", use_container_width=True):
                    rs.rujuk_pasien(p.id_pasien)
                    st.success(f"Pasien **{p.nama}** dirujuk keluar.")
                    st.rerun()

    st.markdown("---")

    # ── Pasien kritis ────────────────────────────────────────────────────
    st.markdown("### 🚨 Pasien Kritis (Thalasemia Mayor — butuh transfusi segera)")
    kritis = rs.tampilkan_pasien_kritis()
    if not kritis:
        st.success("✅ Tidak ada pasien kritis saat ini.")
    else:
        st.error(f"⚠️ Terdapat **{len(kritis)} pasien** yang membutuhkan transfusi segera!")
        for p in kritis:
            st.markdown(pasien_card(p.to_dict()), unsafe_allow_html=True)


def render_admin_app():
    user = st.session_state.user
    if user is None:
        goto("landing")
        return

    with st.sidebar:
        st.markdown("## 🧬 SiGen-Thal")
        st.caption(f"🛡️ Admin: {user.username}")
        st.markdown("---")
        menu = st.radio("", [
            "📊 Dashboard",
            "➕ Tambah Pasien",
            "✏️ Update Pasien",
            "🗑️ Hapus Pasien",
            "🔬 Simulasi Persilangan",
            "🏥 Manajemen Rumah Sakit",
        ], label_visibility="collapsed")
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout()

    if menu == "📊 Dashboard":
        render_dashboard()
    elif menu == "➕ Tambah Pasien":
        render_tambah_pasien()
    elif menu == "✏️ Update Pasien":
        render_update_pasien()
    elif menu == "🗑️ Hapus Pasien":
        render_hapus_pasien()
    elif menu == "🔬 Simulasi Persilangan":
        render_simulasi_admin()
    elif menu == "🏥 Manajemen Rumah Sakit":
        render_rumah_sakit()


# ── Router ─────────────────────────────────────────────────────────────
ROUTES = {
    "landing":   render_landing,
    "user_auth": render_user_auth,
    "admin_auth": render_admin_auth,
    "user_app":  render_user_app,
    "admin_app": render_admin_app,
}
ROUTES.get(st.session_state.view, render_landing)()
