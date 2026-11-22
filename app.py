from pathlib import Path
from datetime import datetime
import json

import streamlit as st
import streamlit.components.v2 as components
from web3 import Web3

# =========================================================
# 1. KONFIGURASI HALAMAN DAN TEMA
# =========================================================
st.set_page_config(
    page_title="Rekam Medis Blockchain",
    page_icon="🏥",
    layout="wide",
)

st.markdown("""
<style>
.stApp { background: #FFF8FB; color: #352A32; }
[data-testid="stMain"] { background: #FFF8FB; }
h1, h2, h3, h4 { color: #713B59 !important; }
p, label, li, [data-testid="stMarkdownContainer"] {
    color: #493943;
}
[data-testid="stSidebar"] { background: #F8E2EE; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {
    color: #713B59 !important;
}
.stTextInput input, .stNumberInput input, .stTextArea textarea {
    background: #FFFFFF !important;
    color: #352A32 !important;
    border: 1px solid #E6BBD0 !important;
    border-radius: 9px !important;
}
.stButton > button, .stFormSubmitButton > button {
    background: #D96B9B !important;
    color: #FFFFFF !important;
    border: 0 !important;
    border-radius: 9px !important;
    font-weight: 600 !important;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    background: #BD4F82 !important;
    color: #FFFFFF !important;
}
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #F0D2E1;
    padding: 16px;
    border-radius: 13px;
}
[data-testid="stMetricValue"] { color: #713B59 !important; }
hr { border-color: #EBD1DE !important; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. KONFIGURASI BLOCKCHAIN, ABI, DAN SMART CONTRACT
# =========================================================
PROJECT_DIR = Path(__file__).parent
RPC_DEFAULT = "http://127.0.0.1:8545"
DEPLOYMENT_PATH = PROJECT_DIR / "deployment.json"
ARTIFACT_PATH = (
    PROJECT_DIR / "artifacts" / "contracts"
    / "RekamMedis.sol" / "RekamMedis.json"
)

st.sidebar.title("Pengaturan Blockchain")
rpc_url = st.sidebar.text_input("RPC URL", value=RPC_DEFAULT)

if not DEPLOYMENT_PATH.exists():
    st.error("File deployment.json tidak ditemukan. Deploy smart contract terlebih dahulu.")
    st.stop()

if not ARTIFACT_PATH.exists():
    st.error("Artifact RekamMedis.json tidak ditemukan. Jalankan compile Hardhat terlebih dahulu.")
    st.stop()

try:
    with open(DEPLOYMENT_PATH, "r", encoding="utf-8") as f:
        deployment = json.load(f)
    contract_address_default = deployment["address"]
    with open(ARTIFACT_PATH, "r", encoding="utf-8") as f:
        artifact = json.load(f)
    contract_abi = artifact["abi"]
except (KeyError, json.JSONDecodeError, OSError) as e:
    st.error(f"Gagal membaca deployment atau ABI: {e}")
    st.stop()

contract_address_input = st.sidebar.text_input(
    "Alamat Smart Contract",
    value=contract_address_default,
)

if not Web3.is_address(contract_address_input):
    st.error("Alamat smart contract tidak valid.")
    st.stop()

contract_address = Web3.to_checksum_address(contract_address_input)
w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 10}))

if not w3.is_connected():
    st.error("Tidak dapat terhubung ke Hardhat. Pastikan `npx hardhat node` sedang berjalan.")
    st.stop()

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# =========================================================
# 3. KOMPONEN KONEKSI METAMASK
#    Komponen ini membaca alamat dan chain ID wallet.
# =========================================================
WALLET_HTML = """
<div>
  <button id="connect-wallet" type="button">Hubungkan MetaMask</button>
  <p id="wallet-status">Wallet belum terhubung.</p>
</div>
"""

WALLET_CSS = """
button {
    padding: 10px 16px;
    border: 0;
    border-radius: 9px;
    background: #D96B9B;
    color: white;
    font-weight: 600;
    cursor: pointer;
}
p { color: #493943; overflow-wrap: anywhere; }
"""

WALLET_JS = """
export default function(component) {
    const { parentElement, setStateValue } = component;
    const button = parentElement.querySelector("#connect-wallet");
    const status = parentElement.querySelector("#wallet-status");
    let mounted = true;

    async function readWallet() {
        if (!window.ethereum) {
            status.textContent = "MetaMask tidak ditemukan.";
            return;
        }
        const accounts = await window.ethereum.request({
            method: "eth_accounts"
        });
        const chainId = await window.ethereum.request({
            method: "eth_chainId"
        });

        if (!mounted) return;
        if (accounts && accounts.length > 0) {
            setStateValue("wallet", {
                address: accounts[0],
                chainId: chainId,
                connected: true
            });
            status.textContent = "Wallet terhubung: " + accounts[0];
        } else {
            setStateValue("wallet", {
                address: "",
                chainId: chainId,
                connected: false
            });
            status.textContent = "Wallet belum terhubung.";
        }
    }

    async function connectWallet() {
        if (!window.ethereum) {
            status.textContent = "MetaMask tidak ditemukan. Pasang ekstensi MetaMask.";
            return;
        }
        try {
            status.textContent = "Menunggu persetujuan MetaMask...";
            await window.ethereum.request({ method: "eth_requestAccounts" });
            await readWallet();
        } catch (error) {
            status.textContent = "Koneksi gagal: " + (error.message || "Kesalahan");
        }
    }

    const accountChanged = () => readWallet().catch(() => {});
    const chainChanged = () => readWallet().catch(() => {});
    button.addEventListener("click", connectWallet);

    if (window.ethereum) {
        window.ethereum.on("accountsChanged", accountChanged);
        window.ethereum.on("chainChanged", chainChanged);
        readWallet().catch(() => {});
    }

    return () => {
        mounted = false;
        button.removeEventListener("click", connectWallet);
        if (window.ethereum && window.ethereum.removeListener) {
            window.ethereum.removeListener("accountsChanged", accountChanged);
            window.ethereum.removeListener("chainChanged", chainChanged);
        }
    };
}
"""

wallet_component = components.component(
    name="ehr_metamask_component",
    html=WALLET_HTML,
    css=WALLET_CSS,
    js=WALLET_JS,
)

# =========================================================
# 4. HEADER DAN STATUS WALLET
# =========================================================
st.title("🏥 Rekam Medis Pasien Berbasis Blockchain")
st.caption("Electronic Health Record (EHR) | Solidity • Hardhat • Web3.py • Streamlit")

chain_id = w3.eth.chain_id
latest_block = w3.eth.block_number
col_a, col_b = st.columns(2)
col_a.metric("Chain ID", chain_id)
col_b.metric("Block Terbaru", latest_block)

wallet_result = wallet_component(key="ehr_wallet", default={})
wallet = getattr(wallet_result, "wallet", {}) or {}

wallet_address = None
wallet_ready = False
wallet_chain_id = None

if wallet.get("connected") and wallet.get("address"):
    try:
        wallet_address = Web3.to_checksum_address(wallet["address"])
        wallet_chain_id = int(wallet.get("chainId", "0x0"), 16)
        wallet_ready = wallet_chain_id == chain_id
        if wallet_ready:
            st.success("MetaMask terhubung dan jaringan sesuai dengan RPC.")
        else:
            st.warning(
                f"Jaringan MetaMask (Chain ID {wallet_chain_id}) berbeda "
                f"dengan jaringan RPC (Chain ID {chain_id})."
            )
        st.caption("Alamat wallet aktif")
        st.code(wallet_address)
    except (ValueError, TypeError):
        st.error("Informasi wallet tidak valid.")
else:
    st.info("Hubungkan MetaMask untuk membuka fitur berdasarkan wallet.")

# =========================================================
# 5. HELPER FUNCTION
# =========================================================
STATUS_RUJUKAN = {
    0: "Belum Ada",
    1: "Menunggu",
    2: "Diterima",
    3: "Ditolak",
    4: "Selesai",
}

def require_wallet():
    if not wallet_ready or not wallet_address:
        st.warning("Hubungkan MetaMask dan pastikan jaringannya sesuai dengan Hardhat.")
        return False
    return True

def send_transaction(function_call, label):
    """
    Mengirim transaksi melalui akun lokal Hardhat yang tidak terkunci.
    Untuk demo lokal, wallet MetaMask harus menggunakan salah satu akun Hardhat.
    """
    try:
        tx_hash = function_call.transact({
            "from": wallet_address,
            "gas": 3_000_000,
        })
        tx_hash_hex = tx_hash.hex()
        st.info(f"Transaksi dikirim: {label}")
        st.code(tx_hash_hex)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

        if receipt.status == 1:
            st.success("Transaksi berhasil dikonfirmasi blockchain.")
            st.write(f"Block: {receipt.blockNumber}")
            st.write(f"Gas digunakan: {receipt.gasUsed}")
            st.session_state["last_tx"] = {
                "label": label,
                "hash": tx_hash_hex,
                "status": "Berhasil",
                "block": receipt.blockNumber,
            }
            return True
        else:
            st.error("Transaksi gagal (receipt status 0).")
            st.session_state["last_tx"] = {
                "label": label,
                "hash": tx_hash_hex,
                "status": "Gagal",
                "block": receipt.blockNumber,
            }
            return False
    except Exception as e:
        st.error(f"Transaksi {label} gagal: {e}")
        st.caption(
            "Pastikan wallet memakai akun Hardhat yang tersedia dan akun tersebut "
            "tidak terkunci oleh node lokal."
        )
        st.session_state["last_tx"] = {
            "label": label,
            "hash": "-",
            "status": "Gagal / belum terkirim",
            "block": "-",
        }
        return False

def get_patient_list():
    if not require_wallet():
        return []
    return contract.functions.lihatDaftarPasien().call({"from": wallet_address})

def get_patient_name(patient_id):
    return contract.functions.namaPasienTerdaftar(patient_id).call()

def format_timestamp(timestamp):
    return datetime.fromtimestamp(int(timestamp)).strftime("%d-%m-%Y %H:%M:%S")

def show_patient_history(patient_id):
    records = contract.functions.lihatRiwayat(
        int(patient_id)
    ).call({"from": wallet_address})

    if not records:
        st.info("Belum ada riwayat pemeriksaan.")
        return

    rows = []
    for record in records:
        rows.append({
            "Token ID": record[0],
            "ID Pasien": record[1],
            "Nama Pasien": record[2],
            "Rumah Sakit (wallet)": record[3],
            "Diagnosis": record[4],
            "Tanggal Pemeriksaan": format_timestamp(record[5]),
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)

# =========================================================
# 6. NAVIGASI
# =========================================================
st.sidebar.divider()
page = st.sidebar.radio(
    "Navigasi EHR",
    [
        "Dashboard",
        "Patient List",
        "Patient Detail",
        "Medical Record",
        "Add Medical Record",
        "Access Management",
        "Wallet & Transaction",
    ],
)

# =========================================================
# 7. DASHBOARD
# =========================================================
if page == "Dashboard":
    st.header("Dashboard")
    st.write("Ringkasan pengelolaan rekam medis pasien berbasis blockchain.")

    if wallet_ready:
        try:
            patient_ids = get_patient_list()
            total_records = 0
            for patient_id in patient_ids:
                try:
                    records = contract.functions.lihatRiwayat(
                        int(patient_id)
                    ).call({"from": wallet_address})
                    total_records += len(records)
                except Exception:
                    pass

            m1, m2, m3 = st.columns(3)
            m1.metric("Jumlah Pasien di Rumah Sakit Ini", len(patient_ids))
            m2.metric("Jumlah Rekam Medis yang Dapat Diakses", total_records)
            m3.metric("Block Terbaru", latest_block)
        except Exception as e:
            st.warning(f"Ringkasan data belum dapat dimuat: {e}")
    else:
        st.info("Hubungkan wallet untuk melihat ringkasan data pasien.")

    st.subheader("Status Sistem")
    s1, s2 = st.columns(2)
    s1.write("**Blockchain**")
    s1.success("Terhubung ke Hardhat") 
    s2.write("**MetaMask**")
    if wallet_ready:
        s2.success("Terhubung • Jaringan sesuai")
    elif wallet_address:
        s2.warning("Terhubung, tetapi jaringan berbeda")
    else:
        s2.warning("Belum terhubung")

    st.subheader("Informasi Aplikasi")
    st.write(
        "Aplikasi ini menggunakan smart contract untuk menyimpan identitas "
        "pasien, riwayat diagnosis, kepemilikan NFT rekam medis, dan proses rujukan."
    )
    st.caption(
        "Catatan: smart contract saat ini belum menyimpan log aktivitas akses. "
        "Karena itu, halaman ini menampilkan informasi block, bukan jumlah akses dokter."
    )

# =========================================================
# 8. PATIENT LIST / DATA MANAGEMENT
# =========================================================
elif page == "Patient List":
    st.header("Patient List")
    st.write("Daftar pasien yang tercatat pada rumah sakit dari wallet aktif.")

    if require_wallet():
        try:
            patient_ids = get_patient_list()
            if not patient_ids:
                st.info("Belum ada pasien pada daftar rumah sakit ini.")
            else:
                patient_rows = []
                for patient_id in patient_ids:
                    patient_rows.append({
                        "ID Pasien": patient_id,
                        "Nama Pasien": get_patient_name(patient_id),
                    })
                st.dataframe(
                    patient_rows,
                    use_container_width=True,
                    hide_index=True,
                )
                st.caption(f"Total pasien: {len(patient_rows)}")
        except Exception as e:
            st.error(f"Gagal mengambil daftar pasien: {e}")

# =========================================================
# 9. PATIENT DETAIL
# =========================================================
elif page == "Patient Detail":
    st.header("Patient Detail")
    st.write("Cari profil pasien berdasarkan ID pasien.")

    if require_wallet():
        patient_id = st.number_input(
            "ID Pasien",
            min_value=1,
            step=1,
            key="detail_patient_id",
        )
        if st.button("Tampilkan Detail Pasien"):
            try:
                exists = contract.functions.pasienTerdaftar(
                    int(patient_id)
                ).call()
                if not exists:
                    st.warning("Pasien dengan ID tersebut tidak ditemukan.")
                else:
                    name = get_patient_name(int(patient_id))
                    current_hospital = contract.functions.rumahSakitSaatIni(
                        int(patient_id)
                    ).call()
                    st.subheader(name)
                    d1, d2 = st.columns(2)
                    d1.metric("ID Pasien", int(patient_id))
                    d2.write("**Wallet Rumah Sakit Saat Ini**")
                    d2.code(current_hospital)
                    st.divider()
                    st.subheader("Ringkasan Riwayat Pemeriksaan")
                    show_patient_history(int(patient_id))
            except Exception as e:
                st.error(f"Tidak dapat menampilkan detail pasien: {e}")

# =========================================================
# 10. MEDICAL RECORD
# =========================================================
elif page == "Medical Record":
    st.header("Medical Record")
    st.write("Lihat riwayat pemeriksaan pasien sesuai izin akses dari smart contract.")

    if require_wallet():
        patient_id = st.number_input(
            "Masukkan ID Pasien",
            min_value=1,
            step=1,
            key="medical_patient_id",
        )
        if st.button("Lihat Riwayat Rekam Medis"):
            try:
                show_patient_history(int(patient_id))
            except Exception as e:
                st.error(
                    "Riwayat tidak dapat ditampilkan. Pastikan pasien terdaftar "
                    "dan wallet memiliki izin akses."
                )
                st.caption(str(e))

# =========================================================
# 11. ADD MEDICAL RECORD / FORM INPUT
# =========================================================
elif page == "Add Medical Record":
    st.header("Add Medical Record")
    st.write("Gunakan form berikut untuk mendaftarkan pasien atau menambahkan diagnosis.")

    if require_wallet():
        tab_register, tab_update = st.tabs(["Daftarkan Pasien Baru", "Tambah Pemeriksaan"])

        with tab_register:
            with st.form("form_register_patient"):
                new_id = st.number_input(
                    "ID Pasien",
                    min_value=1,
                    step=1,
                    key="new_patient_id",
                )
                new_name = st.text_input("Nama Pasien")
                first_diagnosis = st.text_area("Diagnosis Awal")
                submitted_register = st.form_submit_button("Daftarkan Pasien")

            if submitted_register:
                if not new_name.strip() or not first_diagnosis.strip():
                    st.error("Nama pasien dan diagnosis wajib diisi.")
                else:
                    try:
                        already_registered = contract.functions.pasienTerdaftar(
                            int(new_id)
                        ).call()
                        if already_registered:
                            st.error("ID pasien tersebut sudah terdaftar.")
                        else:
                            send_transaction(
                                contract.functions.daftarkanPasien(
                                    int(new_id),
                                    new_name.strip(),
                                    first_diagnosis.strip(),
                                ),
                                "Pendaftaran pasien dan rekam medis awal",
                            )
                    except Exception as e:
                        st.error(f"Gagal memproses pendaftaran: {e}")

        with tab_update:
            with st.form("form_update_diagnosis"):
                update_id = st.number_input(
                    "ID Pasien",
                    min_value=1,
                    step=1,
                    key="update_patient_id",
                )
                diagnosis = st.text_area("Diagnosis / Hasil Pemeriksaan")
                submitted_update = st.form_submit_button("Simpan Rekam Medis")

            if submitted_update:
                if not diagnosis.strip():
                    st.error("Diagnosis wajib diisi.")
                else:
                    try:
                        exists = contract.functions.pasienTerdaftar(
                            int(update_id)
                        ).call()
                        if not exists:
                            st.error("Pasien belum terdaftar.")
                        else:
                            send_transaction(
                                contract.functions.updateDiagnosa(
                                    int(update_id),
                                    diagnosis.strip(),
                                ),
                                "Penambahan rekam medis",
                            )
                    except Exception as e:
                        st.error(f"Gagal memproses rekam medis: {e}")

# =========================================================
# 12. ACCESS MANAGEMENT
# =========================================================
elif page == "Access Management":
    st.header("Access Management")
    st.write("Pengelolaan status rumah sakit dan proses rujukan pasien.")

    if require_wallet():
        st.subheader("Status Rumah Sakit")
        try:
            current_status = contract.functions.cekStatusRumahSakit(
                wallet_address
            ).call()
            if current_status:
                st.success("Wallet ini terdaftar aktif sebagai rumah sakit.")
            else:
                st.warning("Wallet ini belum diaktifkan sebagai rumah sakit.")

            if st.button(
                "Aktifkan Status Rumah Sakit" if not current_status
                else "Nonaktifkan Status Rumah Sakit"
            ):
                send_transaction(
                    contract.functions.setStatusRumahSakit(not current_status),
                    "Perubahan status rumah sakit",
                )
        except Exception as e:
            st.error(f"Gagal memeriksa status rumah sakit: {e}")

        st.divider()
        tab_request, tab_response, tab_detail = st.tabs([
            "Ajukan Rujukan", "Tanggapi Rujukan", "Detail Rujukan"
        ])

        with tab_request:
            with st.form("form_referral_request"):
                referral_patient_id = st.number_input(
                    "ID Pasien",
                    min_value=1,
                    step=1,
                    key="referral_patient_id",
                )
                destination = st.text_input("Alamat Wallet Rumah Sakit Tujuan")
                reason = st.text_area("Alasan Rujukan")
                submit_referral = st.form_submit_button("Ajukan Rujukan")

            if submit_referral:
                if not Web3.is_address(destination):
                    st.error("Alamat wallet rumah sakit tujuan tidak valid.")
                elif Web3.to_checksum_address(destination) == wallet_address:
                    st.error("Rumah sakit tujuan tidak boleh sama dengan rumah sakit asal.")
                else:
                    try:
                        destination = Web3.to_checksum_address(destination)
                        destination_active = contract.functions.cekStatusRumahSakit(
                            destination
                        ).call()
                        if not destination_active:
                            st.error("Rumah sakit tujuan belum mengaktifkan statusnya.")
                        else:
                            send_transaction(
                                contract.functions.ajukanRujukan(
                                    int(referral_patient_id),
                                    destination,
                                    reason.strip(),
                                ),
                                "Pengajuan rujukan pasien",
                            )
                    except Exception as e:
                        st.error(f"Gagal mengajukan rujukan: {e}")

        with tab_response:
            with st.form("form_referral_response"):
                response_patient_id = st.number_input(
                    "ID Pasien yang Dirujuk",
                    min_value=1,
                    step=1,
                    key="response_patient_id",
                )
                decision = st.radio(
                    "Keputusan",
                    ["Terima", "Tolak"],
                    horizontal=True,
                )
                submit_response = st.form_submit_button("Kirim Keputusan")

            if submit_response:
                try:
                    send_transaction(
                        contract.functions.tanggapiRujukan(
                            int(response_patient_id),
                            decision == "Terima",
                        ),
                        f"{decision} rujukan pasien",
                    )
                except Exception as e:
                    st.error(f"Gagal menanggapi rujukan: {e}")

        with tab_detail:
            with st.form("form_referral_detail"):
                detail_referral_id = st.number_input(
                    "ID Pasien",
                    min_value=1,
                    step=1,
                    key="detail_referral_id",
                )
                submit_detail = st.form_submit_button("Lihat Detail Rujukan")

            if submit_detail:
                try:
                    referral = contract.functions.lihatDetailRujukan(
                        int(detail_referral_id)
                    ).call({"from": wallet_address})
                    st.write("**Rumah Sakit Asal**")
                    st.code(referral[0])
                    st.write("**Rumah Sakit Tujuan**")
                    st.code(referral[1])
                    st.write("**Alasan**")
                    st.write(referral[2] or "-")
                    st.write("**Status**")
                    st.info(STATUS_RUJUKAN.get(int(referral[3]), "Tidak diketahui"))
                    st.write("**Waktu Pengajuan**")
                    st.write(format_timestamp(referral[4]) if referral[4] else "-")
                    st.write("**Waktu Keputusan**")
                    st.write(format_timestamp(referral[5]) if referral[5] else "Belum diputuskan")
                except Exception as e:
                    st.error(f"Detail rujukan tidak dapat diakses: {e}")

# =========================================================
# 13. WALLET & TRANSACTION
# =========================================================
elif page == "Wallet & Transaction":
    st.header("Wallet & Transaction")
    st.write("Informasi wallet aktif dan ringkasan transaksi terakhir.")

    if wallet_address:
        st.success("Wallet terhubung.")
        st.write("**Alamat Wallet**")
        st.code(wallet_address)
        st.write(f"**Chain ID MetaMask:** {wallet_chain_id}")
        st.write(f"**Chain ID RPC:** {chain_id}")
        st.write(
            "**Kesesuaian jaringan:** "
            + ("Sesuai" if wallet_ready else "Tidak sesuai")
        )
    else:
        st.warning("Belum ada wallet yang terhubung.")

    st.divider()
    st.subheader("Transaksi Terakhir")
    last_tx = st.session_state.get("last_tx")
    if last_tx:
        st.write(f"**Fungsi:** {last_tx['label']}")
        st.write(f"**Status:** {last_tx['status']}")
        st.write(f"**Transaction Hash:** {last_tx['hash']}")
        st.write(f"**Block:** {last_tx['block']}")
    else:
        st.info("Belum ada transaksi yang dikirim dari aplikasi ini.")

    st.caption(
        "Status transaksi diperbarui setelah node mengembalikan transaction receipt. "
        "Transaksi yang sedang menunggu konfirmasi akan terlihat saat proses pengiriman berlangsung."
    )

# =========================================================
# 14. CATATAN
# =========================================================
st.sidebar.divider()
st.sidebar.caption("EHR Blockchain • Demo jaringan lokal")
st.caption(
    "Gunakan data pasien fiktif untuk demonstrasi. Jangan masukkan data kesehatan "
    "atau identitas pasien yang sebenarnya."
)
