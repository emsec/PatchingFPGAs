import sys

with open(sys.argv[1], "rb") as f:
    while True:
        data = f.read(8)
        if not data:
            break
        diadi = data[3::-1]
        dibdi = data[7:3:-1]
        instr_rdata_i = hex(int.from_bytes(diadi, "big"))[2:].zfill(8)
        #assert int.from_bytes(dibdi, "big") & 1 == 0
        reserved = int.from_bytes(dibdi, "big") & 1
        instr_addr_i = hex(int.from_bytes(dibdi, "big") & 0xfffffffe)[2:].zfill(8)
        print(f"instr_addr_i: {instr_addr_i}, reserved: {reserved}, instr_rdata_i: {instr_rdata_i}")
