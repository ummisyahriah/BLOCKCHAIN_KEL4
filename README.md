# Sample Hardhat Project

This project demonstrates a basic Hardhat use case. It comes with a sample contract, a test for that contract, and a Hardhat Ignition module that deploys that contract.

Try running some of the following tasks:

```shell
npx hardhat help
npx hardhat test
REPORT_GAS=true npx hardhat test
npx hardhat node
npx hardhat ignition deploy ./ignition/modules/Lock.js
```

## Deskripsi
Aplikasi Rekam Medis Berbasis Blockchain merupakan aplikasi untuk mengelola data pasien, riwayat pemeriksaan, dan proses rujukan antar rumah sakit dengan memanfaatkan teknologi blockchain.

Aplikasi ini menggunakan smart contract untuk mengatur penyimpanan dan pengelolaan data, sehingga setiap perubahan data dapat tercatat melalui transaksi blockchain.

## Teknologi yang Digunakan
- **Python** – Bahasa pemrograman untuk membangun aplikasi.
- **Streamlit** – Framework untuk membuat antarmuka aplikasi.
- **Web3.py** – Menghubungkan aplikasi Python dengan blockchain.
- **Solidity** – Bahasa pemrograman untuk membuat smart contract.
- **Hardhat** – Menjalankan blockchain lokal dan melakukan deployment smart contract.
- **MetaMask** – Wallet untuk menghubungkan akun dengan aplikasi.

## Persyaratan
Sebelum menjalankan aplikasi, pastikan sudah menginstal:
- Python
- Node.js dan npm
- MetaMask pada browser
- Git (opsional, jika mengunduh melalui GitHub)

## Instalasi

### 1. Clone Repository
Unduh project dari GitHub menggunakan perintah:

```bash
git clone URL_REPOSITORY
```

Masuk ke folder project:

```bash
cd rekam_medis_bc
```

### 2. Membuat Virtual Environment

```bash
python -m venv .venv
```

Aktifkan virtual environment pada Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Instalasi Library Python

```bash
pip install streamlit web3
```

### 4. Instalasi Dependency Node.js

```bash
npm install
```
Pastikan package OpenZeppelin sudah tersedia:

```bash
npm install @openzeppelin/contracts
```

## Menjalankan Aplikasi

### 1. Menjalankan Hardhat Node

Buka terminal pertama, kemudian jalankan:

```bash
npx hardhat node
```
Hardhat Node berfungsi sebagai jaringan blockchain lokal untuk menjalankan dan menguji smart contract.

Biarkan terminal tetap berjalan.

### 2. Compile Smart Contract

Buka terminal kedua pada folder project, kemudian jalankan:

```bash
npx hardhat compile
```

Perintah ini digunakan untuk mengompilasi file smart contract Solidity.

### 3. Deploy Smart Contract

Jalankan perintah berikut:

```bash
npx hardhat run scripts/deploy.js --network localhost
```

Setelah deployment berhasil, salin alamat smart contract yang dihasilkan dan pastikan alamat tersebut sudah dimasukkan ke dalam file `deployment.json`.

Contoh isi `deployment.json`:

```json
{
    "address": "ALAMAT_SMART_CONTRACT"
}
```

### 4. Konfigurasi MetaMask

Tambahkan jaringan Hardhat lokal pada MetaMask dengan konfigurasi berikut:

- Network Name: Hardhat Local
- RPC URL: `http://127.0.0.1:8545`
- Chain ID: `31337`
- Currency Symbol: ETH

Gunakan akun pengujian dari Hardhat untuk melakukan transaksi pada aplikasi.

### 5. Menjalankan Streamlit

Setelah blockchain dan smart contract siap, jalankan aplikasi dengan perintah:

```bash
streamlit run app.py
```

Aplikasi akan terbuka melalui browser pada alamat lokal yang ditampilkan oleh Streamlit, biasanya:

```text
http://localhost:8501
```

## Catatan
- Hardhat Node harus tetap berjalan selama aplikasi digunakan.
- Pastikan alamat smart contract pada `deployment.json` sesuai dengan hasil deployment terbaru.
- Jika Hardhat Node dihentikan dan dijalankan kembali, jaringan lokal akan dimulai ulang sehingga smart contract perlu di-deploy kembali.
- Pastikan MetaMask terhubung ke jaringan Hardhat lokal.
- Gunakan akun pengujian dan data pasien fiktif selama demonstrasi.

