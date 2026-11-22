// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";

contract RekamMedis is ERC721URIStorage {

    uint256 private nextTokenId = 1;

    // Status rujukan
    enum StatusRujukan {
        BELUM_ADA,
        MENUNGGU,
        DITERIMA,
        DITOLAK,
        SELESAI
    }
    // Data rekam medis
    struct RekamMedisData {
        uint256 tokenId;
        uint256 idPasien;
        string namaPasien;
        address rumahSakit;
        string diagnosa;
        uint256 timestamp;
    }
    // Data rujukan
    struct DataRujukan {
        address rumahSakitAsal;
        address rumahSakitTujuan;
        string alasan;
        StatusRujukan status;
        uint256 waktuPengajuan;
        uint256 waktuKeputusan;
    }
    // Mapping
    mapping(uint256 => bool) public pasienTerdaftar;
    mapping(uint256 => string) public namaPasienTerdaftar;
    mapping(uint256 => address) public rumahSakitSaatIni;
    mapping(uint256 => RekamMedisData[]) private riwayatPemeriksaan;
    mapping(uint256 => DataRujukan) public rujukan;
    // Event
    event PasienTerdaftarkan(uint256 idPasien, address rumahSakit);
    event RujukanDiajukan(uint256 idPasien, address rumahSakitTujuan);
    event RujukanDitanggapi(uint256 idPasien, StatusRujukan status);
    event DiagnosaDiperbarui(uint256 idPasien, uint256 tokenId);

    constructor() ERC721("RekamMedisNFT", "RMNFT") {}

    // Membuat NFT rekam medis
    function _buatRekamMedis(
        uint256 idPasien,
        string memory diagnosa
    ) internal {
        uint256 tokenId = nextTokenId++;

        RekamMedisData memory data = RekamMedisData(
            tokenId,
            idPasien,
            namaPasienTerdaftar[idPasien],
            msg.sender,
            diagnosa,
            block.timestamp
        );
        riwayatPemeriksaan[idPasien].push(data);
        _safeMint(msg.sender, tokenId);
    }
    // 1. Mendaftarkan pasien dan rekam medis awal
    function daftarkanPasien(
        uint256 idPasien,
        string memory namaPasien,
        string memory diagnosa
    ) public {
        require(!pasienTerdaftar[idPasien], "Pasien sudah terdaftar");
        require(idPasien > 0, "ID pasien tidak boleh kosong");
        require(bytes(namaPasien).length > 0, "Nama pasien wajib diisi");
        require(bytes(diagnosa).length > 0, "Diagnosa wajib diisi");

        pasienTerdaftar[idPasien] = true;
        namaPasienTerdaftar[idPasien] = namaPasien;
        rumahSakitSaatIni[idPasien] = msg.sender;

        _buatRekamMedis(idPasien, diagnosa);

        emit PasienTerdaftarkan(idPasien, msg.sender);
    }
    // 2. Mengajukan rujukan ke rumah sakit lain
    function ajukanRujukan(
        uint256 idPasien,
        address rumahSakitTujuan,
        string memory alasan
    ) public {
        require(pasienTerdaftar[idPasien], "Pasien tidak ditemukan");
        require(
            msg.sender == rumahSakitSaatIni[idPasien], "Bukan rumah sakit saat ini");
        require(rumahSakitTujuan != address(0), "Alamat tidak valid");
        require(rumahSakitTujuan != msg.sender, "Tujuan tidak boleh sama");

        StatusRujukan status = rujukan[idPasien].status;

        require(
            status == StatusRujukan.BELUM_ADA ||
            status == StatusRujukan.DITOLAK ||
            status == StatusRujukan.SELESAI,"Masih ada rujukan aktif");

        rujukan[idPasien] = DataRujukan(
            msg.sender,
            rumahSakitTujuan,
            alasan,
            StatusRujukan.MENUNGGU,
            block.timestamp,
            0 );
        emit RujukanDiajukan(idPasien, rumahSakitTujuan);
    }
    // 3. Menerima atau menolak rujukan
    function tanggapiRujukan(
        uint256 idPasien,
        bool diterima
    ) public {
        require(
            rujukan[idPasien].status == StatusRujukan.MENUNGGU, "Tidak ada rujukan yang menunggu");
        require(
            msg.sender == rujukan[idPasien].rumahSakitTujuan,"Bukan rumah sakit tujuan");

        if (diterima) {
            rujukan[idPasien].status = StatusRujukan.DITERIMA;
            rumahSakitSaatIni[idPasien] = msg.sender;
        } else {
            rujukan[idPasien].status = StatusRujukan.DITOLAK;}

        rujukan[idPasien].waktuKeputusan = block.timestamp;

        emit RujukanDitanggapi(
            idPasien,
            rujukan[idPasien].status);
    }
    // 4. Memperbarui atau menambahkan diagnosa
    function updateDiagnosa(
        uint256 idPasien,
        string memory diagnosa
    ) public {
        require(pasienTerdaftar[idPasien], "Pasien tidak ditemukan");
        require(
            msg.sender == rumahSakitSaatIni[idPasien],"Bukan rumah sakit saat ini"
        );

        _buatRekamMedis(idPasien, diagnosa);

        if (rujukan[idPasien].status == StatusRujukan.DITERIMA) {
            rujukan[idPasien].status = StatusRujukan.SELESAI;
        }

        emit DiagnosaDiperbarui(
            idPasien,
            nextTokenId - 1
        );
    }
    // 5. Melihat seluruh riwayat pemeriksaan
    function lihatRiwayat(
        uint256 idPasien
    ) public view returns (RekamMedisData[] memory) {
        require(pasienTerdaftar[idPasien], "Pasien tidak ditemukan");

        bool bolehMelihat =
            msg.sender == rumahSakitSaatIni[idPasien] ||
            (
                msg.sender == rujukan[idPasien].rumahSakitTujuan &&
                (
                    rujukan[idPasien].status == StatusRujukan.DITERIMA ||
                    rujukan[idPasien].status == StatusRujukan.SELESAI
                )
            );

        require(bolehMelihat, "Tidak memiliki izin akses");

        return riwayatPemeriksaan[idPasien];
    }
    // 6. Melihat detail transaksi rujukan
    function lihatDetailRujukan(
        uint256 idPasien
    ) public view returns (DataRujukan memory) {
        require(
            msg.sender == rujukan[idPasien].rumahSakitAsal ||
            msg.sender == rujukan[idPasien].rumahSakitTujuan,"Tidak memiliki izin akses"
        );

        return rujukan[idPasien];
    }
    // 7. Melihat pemilik NFT rekam medis
    function getRecordOwner(
        uint256 tokenId
    ) public view returns (address) {
        return ownerOf(tokenId);
    }
}