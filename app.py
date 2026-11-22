from pathlib import Path

import streamlit as st
import streamlit.components.v2 as components
from web3 import Web3
import json

# =========================================================
# KONFIGURASI DASAR 
# =========================================================

RPC_URL = "http://127.0.0.1:8545"

PROJECT_DIR = Path(__file__) .parent 

DEPLOYMENT_PATH = PROJECT_DIR / "deployment.json"

ARTIFACTS_PATH =  (
    PROJECT_DIR 
    / "artifacts"
    / "contracts"
    / "RekamMedis.sol"
    / "RekamMedis.json"

)

# =========================================================
# KONEKSI WEB 3
# =========================================================

w3 = Web3(
    Web3.HTTPProvider(
     RPC_URL, 
     request_kwargs={"timeout": 5}
    )
)

# =========================================================
# CEK KONEKSI BLOCKCHAIN
# =========================================================

if not w3.is_connected():
    st.error(
        "Tidak dapat terhubung ke hardhat Network. "
        "Pastikan Hardhat node sedang berjalan." 
    )
    st.stop()


# =========================================================
# LOAD CONTRACT ADDRESS 
# =========================================================    

if not DEPLOYMENT_PATH.exists():
    st.error(
        "File deployment.json tidak ditemukan. "
        "Silakan deploy smart contract terlebih dahulu "
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
        "artifacts smart contract tidak ditemukan. "
        "silakan compile smart contract terlebih dahulu."
    )
    st.stop()

with open(ARTIFACTS_PATH, "r") as file:
    contract_artifact = json.load(file)

CONTRACT_ABI = contract_artifact["abi"]


# =========================================================
# INISIALISASI SMART CONTRACT
# =========================================================

RekamMedis_Contract = w3.eth.contract(
    address=CONTRACT_ADDRESS,
    abi=CONTRACT_ABI,
)
st.set_page_config(
    page_title="Rekam Medis Blockchain",
    page_icon="🏥",
    layout="wide",
)

st.title("🏥 Rekam Medis Pasien Berbasis Blockchain")
st.caption("EHR menggunakan Smart Contract Solidity, Hardhat, MetaMask, Streamlit, dan Web3.py")

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
        const accounts = await window.ethereum.request({ method: "eth_accounts" });
        const chainId = await window.ethereum.request({ method: "eth_chainId" });

        if (!mounted) return;
        if (accounts && accounts.length > 0) {
            setStateValue("wallet", {
                address: accounts[0], chainId: chainId, connected: true
            });
            status.textContent = "Wallet terhubung: " + accounts[0];
        } else {
            setStateValue("wallet", {
                address: "", chainId: chainId, connected: false
            });
            status.textContent = "Wallet belum terhubung.";
        }
    }

    async function connectWallet() {
        if (!window.ethereum) {
            status.textContent = "MetaMask tidak ditemukan. Silakan pasang MetaMask.";
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

    function onAccountsChanged() { readWallet().catch(() => {}); }
    function onChainChanged() { readWallet().catch(() => {}); }

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
            window.ethereum.removeListener("accountsChanged", onAccountsChanged);
            window.ethereum.removeListener("chainChanged", onChainChanged);
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
# SIDEBAR & STATUS BLOCKCHAIN LOKAL 
# =========================================================

st.sidebar.header("Pengaturan Blockchain")
rpc_url = st.sidebar.text_input("RPC URL", value=RPC_URL)
contract_address_input = st.sidebar.text_input(
    "Alamat Smart Contract",
    placeholder="Masukkan alamat hasil deploy kontrak",
)

w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 5}))
rpc_connected = w3.is_connected()

st.subheader("1. Status Blockchain Lokal")
if rpc_connected:
    col1, col2 = st.columns(2)
    col1.metric("Chain ID", w3.eth.chain_id)
    col2.metric("Block Terbaru", w3.eth.block_number)
    st.success("Terhubung ke blockchain.")
else:
    st.error("RPC tidak terhubung. Jalankan node Hardhat terlebih dahulu.")

# =========================================================
# BAGIAN Koneksi MetaMask & Informasi Wallet
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
        wallet_address = Web3.to_checksum_address(wallet["address"])
        wallet_chain_id = int(wallet["chainId"], 16)
        st.success("Wallet terhubung.")
        st.code(wallet_address)
        st.write(f"Chain ID MetaMask: **{wallet_chain_id}**")

        if rpc_connected and wallet_chain_id == w3.eth.chain_id:
            wallet_ready = True
            st.success("Jaringan MetaMask sesuai dengan RPC.")
        elif rpc_connected:
            st.warning("Jaringan MetaMask berbeda dengan RPC Hardhat.")
    except (ValueError, TypeError):
        st.error("Informasi wallet tidak valid.")
else:
    st.info("Hubungkan MetaMask untuk menggunakan fitur aplikasi.")

# =========================================================
# CATATAN
# =========================================================
st.divider()
st.markdown(
    """
    **Catatan Pertemuan 9:**
    1. Pastikan node Hardhat aktif (`npx hardhat node`)[cite: 5].
    2. Pastikan ekstensi MetaMask terhubung ke jaringan lokal (`127.0.0.1:8545`)[cite: 6].
    """
)