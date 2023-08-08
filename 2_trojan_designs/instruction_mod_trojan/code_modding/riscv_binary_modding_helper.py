#!/usr/bin/env python3
"""Usage: python riscv_binary_modding_helper.py <start address> <mod.bin>
       <original.bin>

Example: python riscv_binary_modding_helper.py 3e0 trojan.bin
         hsm_demo_fpga_nexysvideo_nomod.bin

This script generates a binary that can be used to mod a RISCV program in
special cases, namely when instructions will be replaced in the hardware
implementation of the CPU. We assume that we are in control of the instructions
but also assume the instruction counter (PC) will perform according to the
original program. Thus we need to take into account that compressed
instructions increment the PC by 2 while full instructions increment the PC by
4. To make this work, we output 32-bit data for every mod instruction, starting
at address "start address". Keep in mind, that addressing in fact is 2 byte
aligned, not 32-bit aligned. So every addressed 2-byte word is yielding a
32-bit double word, which is not how software modding / patching can work. In
normal scenarios, the upper 2 byte of the 32-bit word will be the previous
address, this is NOT the case here, the upper 2 bytes can be different.

To make again clear: The resulting program needs to be injected into the ID
stage while the PC is still according to the original fetched instructions
output by the IF stage. Especially relative branch instructions need to take
this specialty into account.

What is missing: Any other actions with the PC except branch instructions will
probably not work as designed. Branch instructions are updated so they can jump
to the correct modded addresses.

Byteorder: Litle Endian
"""

import sys

METHOD = 1 # 1 is BRAM INIT, 2 is as verilog case statement

class Instruction:
    def __init__(self, addr, bdata):
        self.addr = addr

        # is the instruction compressed? the low byte (LE: first) will reveal to us
        self.is_compressed = bdata[0] & 0x3 != 0x3

        if self.is_compressed:
            self.rdata = int.from_bytes(bdata[:2], "little")
        else:
            self.rdata = int.from_bytes(bdata[:4], "little")

        self.bitwidth = ((not self.is_compressed)+1)*16

        self.instr = None
        self.instr_offset = None

    def decompress(self):
        # rewrite of https://github.com/lowRISC/ibex/blob/master/rtl/ibex_compressed_decoder.sv
        if not self.is_compressed:
            # already decompressed
            return
        
        illegal_instr = False
        instr = self.rdata
        # C0
        if self.rdata & 0x3 == 0x0:
            if self.rdata >> 13 & 0x7 == 0x0:
                # c.addi4spn -> addi rd', x2, imm
                instr = self.rdata >> 7 << 26 & 0x3c000000 | self.rdata >> 11 << 24 & 0x3000000 | self.rdata >> 5 << 23 & 0x800000 | self.rdata >> 6 << 22 & 0x400000 | 0x10000 | 0x400 | self.rdata >> 2 << 7 & 0x380 | 0x13
                if self.rdata >> 5 & 0xff == 0x0:
                    illegal_instr = True
            elif self.rdata >> 13 & 0x7 == 0x2:
                # c.lw -> lw rd', imm(rs1')
                instr = self.rdata >> 5 << 26 & 0x4000000 | self.rdata >> 10 << 23 & 0x3800000 | self.rdata >> 6 << 22 & 0x400000 | 0x40000 | self.rdata >> 7 << 15 & 0x38000 | 0x2000 | 0x400 | self.rdata >> 2 << 7 & 0x380 | 0x3
            elif self.rdata >> 13 & 0x7 == 0x6:
                # c.sw -> sw rs2', imm(rs1')
                instr = self.rdata >> 5 << 26 & 0x4000000 | self.rdata >> 12 << 25 & 0x2000000 | 0x800000 | self.rdata >> 2 << 20 & 0x700000 | 0x40000 | self.rdata >> 7 << 15 & 0x38000 | 0x2000 | self.rdata >> 10 << 10 & 0xc00 | self.rdata >> 6 << 9 & 0x200 | 0x23
            else:
                illegal_instr = True
        # C1
        #
        # Register address checks for RV32E are performed in the regular instruction decoder.
        # If this check fails, an illegal instruction exception is triggered and the controller
        # writes the actual faulting instruction to mtval.
        elif self.rdata & 0x3 == 0x1:
            if self.rdata >> 13 & 0x7 == 0x0:
                # c.addi -> addi rd, rd, nzimm
                # c.nop
                instr = self.rdata >> 12 << 31 & 0x80000000 | self.rdata >> 12 << 30 & 0x40000000 | self.rdata >> 12 << 29 & 0x20000000 | self.rdata >> 12 << 28 & 0x10000000 | self.rdata >> 12 << 27 & 0x8000000 | self.rdata >> 12 << 26 & 0x4000000 | self.rdata >> 12 << 25 & 0x2000000 | self.rdata >> 2 << 20 & 0x1f00000 | self.rdata >> 7 << 15 & 0xf8000 | self.rdata >> 7 << 7 & 0xf80 | 0x13
            elif self.rdata >> 13 & 0x7 == 0x1 or self.rdata >> 13 & 0x7 == 0x5:
                # 001: c.jal -> jal x1, imm
                # 101: c.j   -> jal x0, imm
                instr = self.rdata >> 12 << 31 & 0x80000000 | self.rdata >> 8 << 30 & 0x40000000 | self.rdata >> 9 << 28 & 0x30000000 | self.rdata >> 6 << 27 & 0x8000000 | self.rdata >> 7 << 26 & 0x4000000 | self.rdata >> 2 << 25 & 0x2000000 | self.rdata >> 11 << 24 & 0x1000000 | self.rdata >> 3 << 21 & 0xe00000 | self.rdata >> 12 << 20 & 0x100000 | self.rdata >> 12 << 19 & 0x80000 | self.rdata >> 12 << 18 & 0x40000 | self.rdata >> 12 << 17 & 0x20000 | self.rdata >> 12 << 16 & 0x10000 | self.rdata >> 12 << 15 & 0x8000 | self.rdata >> 12 << 14 & 0x4000 | self.rdata >> 12 << 13 & 0x2000 | self.rdata >> 12 << 12 & 0x1000 | ~self.rdata >> 15 << 7 & 0x80 | 0x6f
            elif self.rdata >> 13 & 0x7 == 0x2:
                # c.li -> addi rd, x0, nzimm
                # (c.li hints are translated into an addi hint)
                instr = self.rdata >> 12 << 31 & 0x80000000 | self.rdata >> 12 << 30 & 0x40000000 | self.rdata >> 12 << 29 & 0x20000000 | self.rdata >> 12 << 28 & 0x10000000 | self.rdata >> 12 << 27 & 0x8000000 | self.rdata >> 12 << 26 & 0x4000000 | self.rdata >> 12 << 25 & 0x2000000 | self.rdata >> 2 << 20 & 0x1f00000 | self.rdata >> 7 << 7 & 0xf80 | 0x13
            elif self.rdata >> 13 & 0x7 == 0x3:
                # c.lui -> lui rd, imm
                # (c.lui hints are translated into a lui hint)
                instr = self.rdata >> 12 << 31 & 0x80000000 | self.rdata >> 12 << 30 & 0x40000000 | self.rdata >> 12 << 29 & 0x20000000 | self.rdata >> 12 << 28 & 0x10000000 | self.rdata >> 12 << 27 & 0x8000000 | self.rdata >> 12 << 26 & 0x4000000 | self.rdata >> 12 << 25 & 0x2000000 | self.rdata >> 12 << 24 & 0x1000000 | self.rdata >> 12 << 23 & 0x800000 | self.rdata >> 12 << 22 & 0x400000 | self.rdata >> 12 << 21 & 0x200000 | self.rdata >> 12 << 20 & 0x100000 | self.rdata >> 12 << 19 & 0x80000 | self.rdata >> 12 << 18 & 0x40000 | self.rdata >> 12 << 17 & 0x20000 | self.rdata >> 2 << 12 & 0x1f000 | self.rdata >> 7 << 7 & 0xf80 | 0x37
                if self.rdata >> 7 & 0x1f == 0x2:
                    # c.addi16sp -> addi x2, x2, nzimm
                    instr = self.rdata >> 12 << 31 & 0x80000000 | self.rdata >> 12 << 30 & 0x40000000 | self.rdata >> 12 << 29 & 0x20000000 | self.rdata >> 3 << 27 & 0x18000000 | self.rdata >> 5 << 26 & 0x4000000 | self.rdata >> 2 << 25 & 0x2000000 | self.rdata >> 6 << 24 & 0x1000000 | 0x10000 | 0x100 | 0x13
                if self.rdata >> 12 & 0x1 == 0x0 and self.rdata >> 2 & 0x1f == 0x0:
                    illegal_instr = True
            elif self.rdata >> 13 & 0x7 == 0x4:
                if self.rdata >> 11 & 0x1 == 0x0:
                    # 00: c.srli -> srli rd, rd, shamt
                    # 01: c.srai -> srai rd, rd, shamt
                    # (c.srli/c.srai hints are translated into a srli/srai hint)
                    instr = self.rdata >> 10 << 30 & 0x40000000 | self.rdata >> 2 << 20 & 0x1f00000 | 0x40000 | self.rdata >> 7 << 15 & 0x38000 | 0x5000 | 0x400 | self.rdata >> 7 << 7 & 0x380 | 0x13
                    if self.rdata >> 12 & 0x1 == 0x1:
                        illegal_instr = True
                elif self.rdata >> 10 & 0x3 == 0x2:
                    # c.andi -> andi rd, rd, imm
                    instr = self.rdata >> 12 << 31 & 0x80000000 | self.rdata >> 12 << 30 & 0x40000000 | self.rdata >> 12 << 29 & 0x20000000 | self.rdata >> 12 << 28 & 0x10000000 | self.rdata >> 12 << 27 & 0x8000000 | self.rdata >> 12 << 26 & 0x4000000 | self.rdata >> 12 << 25 & 0x2000000 | self.rdata >> 2 << 20 & 0x1f00000 | 0x40000 | self.rdata >> 7 << 15 & 0x38000 | 0x7000 | 0x400 | self.rdata >> 7 << 7 & 0x380 | 0x13
                elif self.rdata >> 10 & 0x3 == 0x3:
                    if self.rdata >> 12 & 0x1 == 0x1:
                        illegal_instr = True
                    elif self.rdata >> 5 & 0x3 == 0x0:
                        # c.sub -> sub rd', rd', rs2'
                        instr = 0x40000000 | 0x800000 | self.rdata >> 2 << 20 & 0x700000 | 0x40000 | self.rdata >> 7 << 15 & 0x38000 | 0x400 | self.rdata << 7 >> 7 & 0x380 | 0x33
                    elif self.rdata >> 5 & 0x3 == 0x1:
                        # c.xor -> xor rd', rd', rs2'
                        instr = 0x800000 | self.rdata >> 2 << 20 & 0x700000 | 0x40000 | self.rdata >> 7 << 15 & 0x38000 | 0x4000 | 0x400 | self.rdata << 7 >> 7 & 0x380 | 0x33
                    elif self.rdata >> 5 & 0x3 == 0x2:
                        # c.or -> or rd', rd', rs2'
                        instr = 0x800000 | self.rdata >> 2 << 20 & 0x700000 | 0x40000 | self.rdata >> 7 << 15 & 0x38000 | 0x6000 | 0x400 | self.rdata << 7 >> 7 & 0x380 | 0x33
                    elif self.rdata >> 5 & 0x3 == 0x3:
                        # c.and -> and rd', rd', rs2'
                        instr = 0x800000 | self.rdata >> 2 << 20 & 0x700000 | 0x40000 | self.rdata >> 7 << 15 & 0x38000 | 0x7000 | 0x400 | self.rdata << 7 >> 7 & 0x380 | 0x33
            elif self.rdata >> 13 & 0x7 == 0x6 or self.rdata >> 13 & 0x7 == 0x7:
                # 0: c.beqz -> beq rs1', x0, imm
                # 1: c.bnez -> bne rs1', x0, imm
                instr = self.rdata >> 12 << 31 & 0x80000000 | self.rdata >> 12 << 30 & 0x40000000 | self.rdata >> 12 << 29 & 0x20000000 | self.rdata >> 12 << 28 & 0x10000000 | self.rdata >> 5 << 26 & 0xc000000 | self.rdata >> 2 << 25 & 0x2000000 | 0x40000 | self.rdata >> 7 << 15 & 0x38000 | self.rdata >> 13 << 12 & 0x1000 | self.rdata >> 10 << 10 & 0xc00 | self.rdata >> 3 << 8 & 0x300 | self.rdata >> 12 << 7 & 0x80 | 0x63
            else:
                illegal_instr = True
        # C2
        #
        # Register address checks for RV32E are performed in the regular instruction decoder.
        # If this check fails, an illegal instruction exception is triggered and the controller
        # writes the actual faulting instruction to mtval.
        elif self.rdata & 0x3 == 0x2:
            if self.rdata >> 13 & 0x7 == 0x0:
                # c.slli -> slli rd, rd, shamt
                # (c.ssli hints are translated into a slli hint)
                instr = self.rdata >> 2 << 20 & 0x1f00000 | self.rdata >> 7 << 15 & 0xf8000 | 0x1000 | self.rdata >> 7 << 7 & 0xf80 | 0x13
                if self.rdata >> 12 & 0x1 == 0x1:
                    illegal_instr = True # reserved for custom extensions
            elif self.rdata >> 13 & 0x7 == 0x2:
                # c.lwsp -> lw rd, imm(x2)
                instr = self.rdata >> 2 << 26 & 0xc000000 | self.rdata >> 12 << 25 & 0x2000000 | self.rdata >> 4 << 22 & 0x1c00000 | 0x10000 | 0x2000 | self.rdata >> 7 << 7 & 0xf80 | 0x3
                if self.rdata >> 7 & 0x1f == 0x0:
                    illegal_instr = True
            elif self.rdata >> 13 & 0x7 == 0x4:
                if self.rdata >> 12 & 0x1 == 0x0:
                    if self.rdata >> 2 & 0x1f != 0x0:
                        # c.mv -> add rd/rs1, x0, rs2
                        # (c.mv hints are translated into an add hint)
                        instr = self.rdata >> 2 << 20 & 0x1f00000 | self.rdata >> 7 << 7 & 0xf80 | 0x33
                    else:
                        # c.jr -> jalr x0, rd/rs1, 0
                        instr = self.rdata >> 7 << 15 & 0xf8000 | 0x67
                        if self.rdata >> 7 & 0x1f == 0x0:
                            illegal_instr = True
                else:
                    if self.rdata >> 2 & 0x1f != 0x0:
                        # c.add -> add rd, rd, rs2
                        # (c.add hints are translated into an add hint)
                        instr = self.rdata >> 2 << 20 & 0x1f00000 | self.rdata >> 7 << 15 & 0xf8000 | self.rdata >> 7 << 7 & 0xf80 | 0x33
                    else:
                        if self.rdata >> 7 & 0x1f == 0x0:
                            # c.ebreak -> ebreak
                            instr = 0x100073
                        else:
                            # c.jalr -> jalr x1, rs1, 0
                            instr = self.rdata >> 7 << 15 & 0xf8000 | 0x80 | 0x67
            elif self.rdata >> 13 & 0x7 == 0x6:
                # c.swsp -> sw rs2, imm(x2)
                instr = self.rdata >> 7 << 26 & 0xc000000 | self.rdata >> 12 << 25 & 0x2000000 | self.rdata >> 2 << 20 & 0x1f00000 | 0x10000 | 0x2000 | self.rdata >> 9 << 9 & 0xe00 | 0x23
            else:
                illegal_instr = True
        # Incoming instruction is not compressed.
        else:
            pass
        if illegal_instr:
            print("ILLEGAL INSTR, MTVAL=" + hex(self.rdata))
        else:
            self.rdata = instr
        
    def parse(self):
        # this routine for now only parses parts of branch / jump instructions for now 

        # do we have a branch / jump instruction here?
        if self.is_compressed:
            if self.rdata >> 13 & 0x7 == 0x1 and self.rdata & 0x3 == 0x1:
                self.instr = "C.JAL"
            elif self.rdata >> 13 & 0x7 == 0x5 and self.rdata & 0x3 == 0x1:
                self.instr = "C.J"
            elif self.rdata >> 13 & 0x7 == 0x6 and self.rdata & 0x3 == 0x1:
                self.instr = "C.BEQZ"
            elif self.rdata >> 13 & 0x7 == 0x7 and self.rdata & 0x3 == 0x1:
                self.instr = "C.BNEZ"
            else:
                self.instr = ""

            if self.instr.startswith("C.J"):
                # 12|11|10:9| 8|7|6|5:3|2 to
                # 11| 4| 9:8|10|6|7|3:1|5
                self.instr_offset = self.rdata >> 1 & 0x800 | self.rdata << 2 & 0x400 | \
                    self.rdata >> 1 & 0x300 | self.rdata << 1 & 0x80 | self.rdata >> 1 & 0x40 | \
                    self.rdata << 3 & 0x20 | self.rdata >> 7 & 0x10 | self.rdata >> 2 & 0xe
                if self.instr_offset & 0x800:
                    self.instr_offset = -((~self.instr_offset & 0x7ff) + 1)
            elif self.instr.startswith("C.B"):
                # 12|11:10|6:5|4:3|2 to
                #  8|  4:3|7:6|2:1|5
                self.instr_offset = self.rdata >> 4 & 0x100 | self.rdata << 1 & 0xc0 | \
                    self.rdata << 3 & 0x20 | self.rdata >> 7 & 0x18 | self.rdata >> 2 & 0x6
                if self.instr_offset & 0x100:
                    self.instr_offset = -((~self.instr_offset & 0xff) + 1)
            else:
                self.instr_offset = 0
        else:
            if self.rdata & 0x7f == 0x6f:
                self.instr = "JAL"
            elif self.rdata & 0x7f == 0x63 and self.rdata >> 12 & 0x7 == 0x0:
                self.instr = "BEQ"
            elif self.rdata & 0x7f == 0x63 and self.rdata >> 12 & 0x7 == 0x1:
                self.instr = "BNE"
            elif self.rdata & 0x7f == 0x63 and self.rdata >> 12 & 0x7 == 0x4:
                self.instr = "BLT"
            elif self.rdata & 0x7f == 0x63 and self.rdata >> 12 & 0x7 == 0x5:
                self.instr = "BGE"
            elif self.rdata & 0x7f == 0x63 and self.rdata >> 12 & 0x7 == 0x6:
                self.instr = "BLTU"
            elif self.rdata & 0x7f == 0x63 and self.rdata >> 12 & 0x7 == 0x7:
                self.instr = "BGEU"
            else:
                self.instr = ""

            if self.instr == "JAL":
                # 31|30:21|20|19:12 to
                # 20| 10:1|11|19:12
                self.instr_offset = self.rdata >> 11 & 0x100000 | self.rdata & 0xff000 | \
                    self.rdata >> 9 & 0x800 | self.rdata >> 20 & 0x7fe
                if self.instr_offset & 0x100000:
                    self.instr_offset = -((~self.instr_offset & 0x1fffff) + 1)
            elif self.instr == "BEQ" or self.instr == "BNE" or self.instr == "BLT" or \
                self.instr == "BLTU" or self.instr == "BGE" or self.instr == "BGEU":
                # 31|30:25|11:8| 7 to
                # 12| 10:5| 4:1|11
                self.instr_offset = self.rdata >> 19 & 0x1000 | self.rdata << 4 & 0x800 | \
                    self.rdata >> 20 & 0x7e0 | self.rdata >> 7 & 0x1e
                if self.instr_offset & 0x1000:
                    self.instr_offset = -((~self.instr_offset & 0x1fff) + 1)
    
    def assemble(self):
        assert self.instr, "No instruction to assemble"

        #if self.instr.startswith("C."):
        #    self.is_compressed = True

        # we already have our instructions assembled in this case, so we do not need to fully assemble
        # the only thing we actually do here is to fill the branch / jump offset again

        if self.instr.startswith("C.J"):
            # 11| 4| 9:8|10|6|7|3:1|5 to
            # 12|11|10:9| 8|7|6|5:3|2
            self.rdata = (self.rdata & ~(0x1ffc)) | self.instr_offset << 1 & 0x1000 | \
                self.instr_offset << 7 & 0x800 | self.instr_offset << 1 & 0x600 | \
                self.instr_offset >> 2 & 0x100 | self.instr_offset << 1 & 0x80 | \
                self.instr_offset >> 1 & 0x40 | self.instr_offset << 2 & 0x38 | \
                self.instr_offset >> 3 & 0x4
        elif self.instr.startswith("C.B"):
            #  8|  4:3|7:6|2:1|5 to
            # 12|11:10|6:5|4:3|2
            self.rdata = (self.rdata & ~(0x1c7c)) | self.instr_offset << 4 & 0x1000 | \
                self.instr_offset << 7 & 0xc00 | self.instr_offset >> 1 & 0x60 | \
                self.instr_offset << 2 & 0x18 | self.instr_offset >> 3 & 0x4
        elif self.instr == "JAL":
            # 20| 10:1|11|19:12 to
            # 31|30:21|20|19:12
            self.rdata = (self.rdata & ~(0xfffff000)) | \
                self.instr_offset << 11 & 0x80000000 | \
                self.instr_offset << 20 & 0x7fe00000 | \
                self.instr_offset << 9 & 0x100000 | \
                self.instr_offset & 0xff000
        elif self.instr == "BEQ" or self.instr == "BNE" or self.instr == "BLT" or \
            self.instr == "BLTU" or self.instr == "BGE" or self.instr == "BGEU":
            # 12| 10:5| 4:1|11 to
            # 31|30:25|11:8| 7
            self.rdata = (self.rdata & ~(0xfe000f80)) | \
                self.instr_offset << 19 & 0x80000000 | \
                self.instr_offset << 20 & 0x7e000000 | \
                self.instr_offset << 7 & 0xf00 | \
                self.instr_offset >> 4 & 0x80
            
    def __repr__(self):
        return (hex(self.addr) + ": " + hex(self.rdata)[2:].zfill(self.bitwidth//4)) + (f"\t {self.instr} {self.instr_offset}" if self.instr else "")

start_addr = int(sys.argv[1], 16)

with open(sys.argv[2], "rb") as f:
    mod_data = f.read()

i = 0
mod_instructions = []
while i < len(mod_data):
    # fetch an instruction
    instruction = Instruction(i + start_addr, mod_data[i:i+4])

    # parse the instruction
    instruction.parse()

    # store
    mod_instructions.append(instruction)

    # increment PC
    i += 2 if instruction.is_compressed else 4

with open(sys.argv[3], "rb") as f:
    f.seek(start_addr)
    orig_data = f.read()

i = 0
addr = 0
orig_instructions = []
while i < len(mod_instructions):
    # fetch an instruction
    instruction = Instruction(addr + start_addr, orig_data[addr:addr+4])

    # store
    orig_instructions.append(instruction)

    # increment PC
    addr += 2 if instruction.is_compressed else 4
    i += 1

# go through the list of both instructions, build an address map
address_map_m2o = {}
for i, mod_instr in enumerate(mod_instructions):
    orig_instr = orig_instructions[i]
    address_map_m2o[mod_instr.addr] = orig_instr.addr

# go through the list of modded instructions, apply address translations
new_instructions = {}
for i, mod_instr in enumerate(mod_instructions):
    orig_instr = orig_instructions[i]
    print(f"{orig_instr}\t -> {mod_instr}")
    current = address_map_m2o[mod_instr.addr]
    if mod_instr.instr_offset:
        # we have a branch / jump here
        target = address_map_m2o[mod_instr.addr + mod_instr.instr_offset]
        new_offset = target - current
        print(f"MOD OFFSET TO {new_offset}")
        mod_instr.instr_offset = new_offset
        mod_instr.assemble()
    # decompress the instruction (extra requirement)
    mod_instr.decompress()
    new_instructions[current] = mod_instr.rdata

if METHOD == 1:
    data_array = []
    init = start_addr >> 4
elif METHOD == 2:
    from pyriscv_disas import rv_disas
    addr = start_addr
    print("""always @(instr_addr_i) begin
case (instr_addr_i)""")

for i in range(start_addr, orig_instructions[len(mod_instructions)-1].addr + 2, 2):
    if i in new_instructions:
        rdata = new_instructions[i]
    else:
        rdata = 0
    rdata_bytes = int.to_bytes(rdata, 4, byteorder="big")
    # output_file.write(rdata_bytes)
    if METHOD == 1:
        data_array.append(rdata_bytes)
        if i == orig_instructions[len(mod_instructions)-1].addr:
            data_array += [b"\x00\x00\x00\x00"] * (8 - len(data_array) % 8)
        if len(data_array) == 8:
            print(f"   .INIT_{hex(init)[2:].upper()}(256'h", end="")
            for d in data_array[::-1]:
                print("".join(hex(j)[2:].zfill(2) for j in d), end="")
            print("),")
            data_array = []
            init += 1
    elif METHOD == 2:
        if rdata != 0:
            addr_rshift = hex((addr >> 1)+0x10000000)[2:].zfill(8)
            data = "".join(hex(i)[2:].zfill(2) for i in rdata_bytes)
            machine = rv_disas(PC = addr)
            disas = " // " + machine.disassemble(int(data,16)).format().strip("\x00")
            print(f"    31'h{addr_rshift} : instr_mod = 32'h{data};{disas}")
        addr += 2

if METHOD == 2:
    print("""    default      : instr_mod = 32'h00000000;
endcase
end""")