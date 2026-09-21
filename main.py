from block import Block
from pow import proof_of_work
from pos import proof_of_stake

print("PROOF-OF-WORK")

block = Block (
    index=1,
    data = {"id_pasien":"P-001",
            "nama_pasien":"init",
            "diagnosa":"Flu",
            "dokter":"Dr. Smith"},
    previous_hash = "0"
)
difficulty = 2

print("\nData Block :", block.data)
print("Difficulty   :", difficulty)

proof_of_work(block, difficulty)
print("Nonce       :", block.nonce)
print("Hash        :", block.hash)

print("\nPROOF-OF-STAKE")

validators = {
    "Rumah Sakit A": 70,
    "Dokter": 10,
    "Pasien": 10,
    "Rumah Sakit B": 10
}

print("\nValidator:")
for validator, stake in validators.items():
    print(f"{validator}: {stake} stake")

selected = proof_of_stake(validators)
print("\nValidator terpilih:", selected)


