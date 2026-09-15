from blockchain import Blockchain


blockchain = Blockchain()


# Rumah Sakit A membuat rekam medis pasien
blockchain.add_block({
    "record_id": "EHR-001",
    "patient_id": "P001",
    "activity": "Rekam medis dibuat",
    "actor": "Rumah Sakit A",
    "hospital": "Rumah Sakit A"
})


# Pasien memberikan izin akses data
blockchain.add_block({
    "record_id": "EHR-001",
    "patient_id": "P001",
    "activity": "Memberikan izin akses rekam medis",
    "actor": "Pasien",
    "permission": "Disetujui"
})


# Rumah Sakit B meminta akses rekam medis
blockchain.add_block({
    "record_id": "EHR-001",
    "patient_id": "P001",
    "activity": "Mengakses rekam medis pasien",
    "actor": "Rumah Sakit B",
    "permission_status": "Diizinkan oleh pasien"
})


# Dokter mengakses data pasien untuk pelayanan
blockchain.add_block({
    "record_id": "EHR-001",
    "patient_id": "P001",
    "activity": "Melihat rekam medis pasien",
    "actor": "Dokter",
    "purpose": "Pemeriksaan dan pelayanan kesehatan"
})


for block in blockchain.chain:

    print("=" * 50)

    print("INDEX :", block.index)
    print("DATA  :", block.data)
    print("PREV  :", block.previous_hash)
    print("HASH  :", block.hash)


print("\nBlockchain valid:", blockchain.is_valid())