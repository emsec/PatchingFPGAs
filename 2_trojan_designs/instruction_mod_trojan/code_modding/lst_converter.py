#!/usr/bin/env python3

# helper script for understanding listing files, call with filename.dis, writes fo filename.dis.dec

from riscv_binary_modding_helper import Instruction

import re
import sys

with open(sys.argv[1], "r") as f:
    with open(sys.argv[1] + ".dec", "w") as f2:
        for line in f:
            m = re.match(r"^\s*([0-9a-f]+):\s+([0-9a-f]+)\s+", line)
            if m:
                addr_s, rdata_s = m.groups()
                addr_i = int(addr_s, 16)
                rdata_b = int.to_bytes(int(rdata_s, 16), 4, "little")
                instr = Instruction(addr_i, rdata_b)
                instr.decompress()
                line = line.rstrip() + "\t" + hex(instr.rdata)[2:].zfill(8) + "\n"
            f2.write(line)