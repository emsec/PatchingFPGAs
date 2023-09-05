#!/usr/bin/env python3

# helper script for finding good filter values

from riscv_binary_modding_helper import Instruction

from more_itertools import distinct_permutations
import re
import sys

instrs = {}

with open(sys.argv[1], "r") as f:
    for line in f:
        m = re.match(r"^\s*([0-9a-f]+):\s+([0-9a-f]+)\s+", line)
        if m:
            addr_s, rdata_s = m.groups()
            addr_i = int(addr_s, 16)
            rdata_b = int.to_bytes(int(rdata_s, 16), 4, "little")
            instr = Instruction(addr_i, rdata_b)
            #instr.decompress(True)
            if instr.illegal:
                continue
            #if addr_i == 0x83ba:
            #    print(f"{line} -> {hex(addr_i)}: {rdata_s} uncompressed: {hex(instr.rdata)}")
            while addr_i in instrs.keys():
                addr_i += 0x100000000 
            instrs[addr_i] = instr.rdata

print("START")

ALLOWED_ADDRS = [0x20000b2e, 0x20000b4c, 0x200002d8]

#value = 0x04812423
#full_mask = 0xfffff07c
value = 0xc4a2
full_mask = 0xfffff0fc

bitwidth = bin(full_mask).count('1')
print(f"full mask contains {bitwidth} bits")

def fill_into_mask(value, mask):
    # go from right to left, replace every 1 with the next bit
    o = 0
    i = 0
    for b in bin(mask)[2:][::-1]:
        if b == '1':
            o = o | ((value & 1) << i)
            value = value >> 1
        i += 1
    return o

for fixed_bits in range(bitwidth, 0, -1):
    base_value = "0" * (bitwidth - fixed_bits) + "1" * fixed_bits
    for perm_value in distinct_permutations(base_value):
        mask = fill_into_mask(int("".join(perm_value), 2), full_mask)
        looking_for = value & mask

        # now that we have a mask, check all instructions against this
        for addr, instr in instrs.items():
            if instr & mask == looking_for and addr not in ALLOWED_ADDRS:
                #print(f"failed for {hex(addr)}: {hex(instr)}")
                break
        else:
            print(f"found a valid permutation for {fixed_bits} bits: {hex(mask)}")
            break
    else:
        print("found no more permutations for bitwidth {fixed_bits}, we are done.")
        break
print("done.")