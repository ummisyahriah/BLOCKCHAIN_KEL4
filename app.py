from pathlib import Path

import streamlit as st
import streamlit.components.v2 as components
from web3 import Web3
import json
# =========================================================
# KONFIGURASI HALAMAN
# =========================================================
st.set_page_config(
    page_title="Rekam Medis Blockchain",
    page_icon="🏥",
    layout="wide",
)
# =========================================================
# KONFIGURASI DASAR
# =========================================================
RPC_URL = "http://127.0.0.1:8545"
PROJECT_DIR = Path(__file__).parent
DEPLOYMENT_PATH = PROJECT_DIR / "deployment.json"
ARTIFACTS_PATH = (
    PROJECT_DIR
    / "artifacts"
    / "contracts"
    / "RekamMedis.sol"
    / "RekamMedis.json"
)

# =========================================================
# LOAD CONTRACT ADDRESS
# =========================================================

if not DEPLOYMENT_PATH.exists():
    st.error(
        "File deployment.json tidak ditemukan. "
        "Silakan deploy smart contract terlebih dahulu."
    )
    st.stop()

with open(DEPLOYMENT_PATH, "r") as file:
    deployment_data = json.load(file)

CONTRACT_ADDRESS = Web3.to_checksum_address(
    deployment_data["address"]
)

# =========================================================
# LOAD CONTRACT ABI
# =========================================================

if not ARTIFACTS_PATH.exists():
    st.error(
        "Artifact smart contract tidak ditemukan. "
        "Silakan compile smart contract terlebih dahulu."
    )
    st.stop()

with open(ARTIFACTS_PATH, "r") as file:
    contract_artifact = json.load(file)

CONTRACT_ABI = contract_artifact["abi"]

# =========================================================
# SIDEBAR & PENGATURAN BLOCKCHAIN
# =========================================================

st.sidebar.header("Pengaturan Blockchain")

rpc_url = st.sidebar.text_input(
    "RPC URL",
    value=RPC_URL,
)

contract_address_input = st.sidebar.text_input(
    "Alamat Smart Contract",
    value=CONTRACT_ADDRESS,
)

# =========================================================
# KONEKSI WEB3
# =========================================================

w3 = Web3(
    Web3.HTTPProvider(
        rpc_url,
        request_kwargs={"timeout": 5}
    )
)

if not w3.is_connected():
    st.error(
        "Tidak dapat terhubung ke Hardhat Network. "
        "Pastikan Hardhat node sedang berjalan."
    )
    st.stop()

# =========================================================
# VALIDASI ALAMAT SMART CONTRACT
# =========================================================

if not Web3.is_address(contract_address_input):
    st.error("Alamat smart contract tidak valid.")
    st.stop()

CONTRACT_ADDRESS = Web3.to_checksum_address(
    contract_address_input
)
# =========================================================
# INISIALISASI SMART CONTRACT
# =========================================================

RekamMedis_Contract = w3.eth.contract(
    address=CONTRACT_ADDRESS,
    abi=CONTRACT_ABI,
)

# =========================================================
# JUDUL APLIKASI
# =========================================================

st.title("🏥 Rekam Medis Pasien Berbasis Blockchain")

st.caption(
    "EHR menggunakan Smart Contract Solidity, "
    "Hardhat, MetaMask, Streamlit, dan Web3.py"
)

# =========================================================
# KOMPONEN JAVASCRIPT METAMASK
# =========================================================

WALLET_HTML = """
<div>
  <button id="connect-wallet" type="button">Connect Wallet</button>
  <p id="wallet-status">Wallet belum terhubung.</p>
</div>
"""

WALLET_CSS = """
button {
    padding: 0.7rem 1rem;
    border: none;
    border-radius: 8px;
    background: var(--st-primary-color);
    color: white;
    font-weight: 600;
    cursor: pointer;
}
p {
    color: var(--st-text-color);
    overflow-wrap: anywhere;
}
"""

WALLET_JS = """
export default function(component) {
    const { parentElement, setStateValue } = component;
    const button = parentElement.querySelector("#connect-wallet");
    const status = parentElement.querySelector("#wallet-status");
    let mounted = true;

    async function readWallet() {
        if (!window.ethereum) return;

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
            status.textContent =
                "MetaMask tidak ditemukan. Silakan pasang MetaMask.";
            return;
        }

        try {
            status.textContent =
                "Menunggu persetujuan MetaMask...";

            await window.ethereum.request({
                method: "eth_requestAccounts"
            });

            await readWallet();

        } catch (error) {
            status.textContent =
                "Koneksi gagal: " + (error.message || "Kesalahan");
        }
    }

    function onAccountsChanged() {
        readWallet().catch(() => {});
    }

    function onChainChanged() {
        readWallet().catch(() => {});
    }

    button.addEventListener("click", connectWallet);

    if (window.ethereum) {
        window.ethereum.on("accountsChanged", onAccountsChanged);
        window.ethereum.on("chainChanged", onChainChanged);

        readWallet().catch(() => {});
    }

    return () => {
        mounted = false;

        button.removeEventListener("click", connectWallet);

        if (window.ethereum && window.ethereum.removeListener) {
            window.ethereum.removeListener(
                "accountsChanged",
                onAccountsChanged
            );

            window.ethereum.removeListener(
                "chainChanged",
                onChainChanged
            );
        }
    };
}
"""
wallet_component = components.component(
    name="ehr_metamask_mod9",
    html=WALLET_HTML,
    css=WALLET_CSS,
    js=WALLET_JS,
)
# =========================================================
# STATUS BLOCKCHAIN LOKAL
# =========================================================

st.subheader("1. Status Blockchain Lokal")

col1, col2 = st.columns(2)

col1.metric(
    "Chain ID",
    w3.eth.chain_id
)

col2.metric(
    "Block Terbaru",
    w3.eth.block_number
)

st.success("Terhubung ke blockchain.")

# =========================================================
# KONEKSI METAMASK & INFORMASI WALLET
# =========================================================

st.divider()

st.subheader("2. Hubungkan MetaMask")

wallet_result = wallet_component(
    key="wallet_mod9",
    default={},
)

wallet = wallet_result.wallet

wallet_address = None
wallet_ready = False

if wallet and wallet.get("connected") and wallet.get("address"):

    try:
        wallet_address = Web3.to_checksum_address(
            wallet["address"]
        )

        wallet_chain_id = int(
            wallet["chainId"],
            16
        )

        st.success("Wallet terhubung.")
        st.code(wallet_address)

        st.write(
            f"Chain ID MetaMask: **{wallet_chain_id}**"
        )

        if wallet_chain_id == w3.eth.chain_id:
            wallet_ready = True
            st.success("Jaringan MetaMask sesuai dengan RPC.")

        else:
            st.warning(
                "Jaringan MetaMask berbeda dengan RPC Hardhat."
            )

    except (ValueError, TypeError):
        st.error("Informasi wallet tidak valid.")

else:
    st.info(
        "Hubungkan MetaMask untuk menggunakan fitur aplikasi."
    )
# =========================================================
# MENU UTAMA
# =========================================================

st.divider()
menu = st.sidebar.radio(
    "Menu Utama",
    [
        "Dashboard",
        "Data Pasien",
        "Rujukan Pasien",
        "Rekam Medis",
        "Rumah Sakit",
        "Informasi NFT",
    ]
)

# =========================================================
# DATA PASIEN
# =========================================================

if menu == "Data Pasien":

    st.header("Data Pasien")

    if not wallet_ready:
        st.warning("Hubungkan MetaMask terlebih dahulu.")

    else:
        st.subheader("Daftar Pasien Rumah Sakit")

        if st.button("Tampilkan Daftar Pasien"):

            try:
                daftar_id = (
                    RekamMedis_Contract
                    .functions
                    .lihatDaftarPasien()
                    .call({"from": wallet_address})
                )

                if len(daftar_id) == 0:
                    st.info("Belum ada pasien terdaftar.")

                else:
                    data_pasien = []

                    for id_pasien in daftar_id:

                        nama = (
                            RekamMedis_Contract
                            .functions
                            .namaPasienTerdaftar(id_pasien)
                            .call()
                        )

                        data_pasien.append({
                            "ID Pasien": id_pasien,
                            "Nama Pasien": nama
                        })

                    st.dataframe(
                        data_pasien,
                        use_container_width=True
                    )

            except Exception as e:
                st.error(f"Gagal mengambil data: {e}")
# =========================================================
# REKAM MEDIS
# =========================================================

elif menu == "Rekam Medis":

    st.header("Riwayat Rekam Medis")

    if not wallet_ready:
        st.warning("Hubungkan MetaMask terlebih dahulu.")

    else:
        id_pasien = st.number_input(
            "Masukkan ID Pasien",
            min_value=1,
            step=1
        )

        if st.button("Lihat Riwayat"):

            try:
                riwayat = (
                    RekamMedis_Contract
                    .functions
                    .lihatRiwayat(int(id_pasien))
                    .call({"from": wallet_address})
                )

                if len(riwayat) == 0:
                    st.info("Riwayat pemeriksaan belum tersedia.")

                else:
                    data_riwayat = []

                    for record in riwayat:
                        data_riwayat.append({
                            "Token ID": record[0],
                            "ID Pasien": record[1],
                            "Nama Pasien": record[2],
                            "Rumah Sakit": record[3],
                            "Diagnosis": record[4],
                            "Waktu Pemeriksaan": record[5],
                        })

                    st.dataframe(
                        data_riwayat,
                        use_container_width=True
                    )

            except Exception as e:
                st.error(
                    "Tidak dapat melihat riwayat. "
                    "Pastikan pasien terdaftar dan wallet memiliki izin."
                )
                st.caption(str(e))

# =========================================================
# INFORMASI RUMAH SAKIT
# =========================================================

elif menu == "Rumah Sakit":

    st.header("Informasi Rumah Sakit")

    if not wallet_ready:
        st.warning("Hubungkan MetaMask terlebih dahulu.")

    else:
        st.subheader("Status Rumah Sakit")

        if st.button("Cek Status Rumah Sakit Saya"):

            try:
                status = (
                    RekamMedis_Contract
                    .functions
                    .cekStatusRumahSakit(wallet_address)
                    .call()
                )

                if status:
                    st.success("Rumah sakit berstatus aktif.")
                else:
                    st.warning("Rumah sakit belum aktif.")

            except Exception as e:
                st.error(f"Gagal mengecek status: {e}")

        st.divider()

        st.subheader("Cek Rumah Sakit Tujuan")

        alamat_rs = st.text_input(
            "Alamat Wallet Rumah Sakit"
        )

        if st.button("Cek Rumah Sakit"):

            if not Web3.is_address(alamat_rs):
                st.error("Alamat wallet tidak valid.")

            else:
                try:
                    status = (
                        RekamMedis_Contract
                        .functions
                        .cekStatusRumahSakit(
                            Web3.to_checksum_address(alamat_rs)
                        )
                        .call()
                    )

                    if status:
                        st.success("Rumah sakit tujuan aktif.")
                    else:
                        st.warning("Rumah sakit tujuan belum aktif.")

                except Exception as e:
                    st.error(f"Gagal mengecek status: {e}")

# =========================================================
# INFORMASI NFT
# =========================================================

elif menu == "Informasi NFT":

    st.header("Informasi NFT Rekam Medis")

    if not wallet_ready:
        st.warning("Hubungkan MetaMask terlebih dahulu.")

    else:
        token_id = st.number_input(
            "Masukkan Token ID",
            min_value=1,
            step=1
        )

        if st.button("Lihat Pemilik NFT"):

            try:
                pemilik = (
                    RekamMedis_Contract
                    .functions
                    .getRecordOwner(int(token_id))
                    .call()
                )

                st.success("Data NFT ditemukan.")

                st.write("Token ID:")
                st.code(str(token_id))

                st.write("Pemilik NFT:")
                st.code(pemilik)

            except Exception as e:
                st.error(
                    "Token tidak ditemukan atau belum tersedia."
                )
                st.caption(str(e))   
# =========================================================
# CATATAN
# =========================================================

st.divider()
st.markdown(
    """
    **Catatan:**
    1. Pastikan node Hardhat aktif (`npx hardhat node`).
    2. Pastikan MetaMask terhubung ke jaringan lokal Hardhat.
    3. Pastikan alamat smart contract sesuai dengan hasil deploy.
    4. Pastikan ABI berasal dari hasil compile terbaru.
    """
)
