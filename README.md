This repository contains case studies and scripts for our research publication about senseful FPGA bitstream modifications.
The scripts work in cooperation with RapidWright, the scripting framework for Xilinx FPGAs.
Also, it has dependencies to the ProjectXray database for actual bitstream fiddling.
The scripts are written in Python and Tcl whilst the FPGA designs are written in SystemVerilog, like OpenTitan, the base for the case studies is written in.

The OpenTitan version we used for our case studies is commit [24baa88](https://github.com/lowRISC/opentitan/tree/24baa88a432a1822ae7d1065bbd244538f38d030). There is no specific reason for the choice, however at this development stage, the OpenTitan still runs fine on the NexysVideo FPGA Board and we chose to not update the OpenTitan as this would have involved extra work during our experiments. However the current version of the OpenTitan in combination with the ChipWhisperer CW310 board should also work. It just would need the ProjectXray database generated for the Kintex 7 410T FPGA and probably some additional tweaks which were not yet evaluated.
The NexysVideo board is based on the smaller Artix 7 200T FPGA.
Beneficial is that there is no need for a costly full Xilinx Vivado license to work with the Artix 7 on the NexysVideo. 

This repository is work in progress.

How To
======

Information: To save work during creation of the placement and clock routing constraints, it is possible to skip steps 2-13 by using the prepared working constraints file supplied in the respective trojan design folder.

Information: Data collected from steps 2-4 could also originate from reverse engineering means out of the target bitstream instead. This is however not covered in this research work. If data is collected by other means, no information from the original design is required for modding bitstreams.

1. Create a Vivado project with the trojan design out of the respective folder (.sv file)
2. Open the base design checkpoint `1_opentitan_base/top_earlgrey_nexysvideo_routed.dcp` in Vivado
3. Uncomment the respective `output_file` and `request_data` lines of the trojan in the `3_trojan_insertion/1_placer/extract_placement_and_dummy_cells.tcl` script
4. In the Tcl Console of the base design checkpoint, with `cd <git path>/3_trojan_insertion/1_placer` change to the folder containing the script and run `source ./extract_placement_and_dummy_cells.tcl`
5. In a terminal, change to the folder `3_trojan_insertion/1_placer` and run `python generate_dummy_cells_and_constraints.py extracted-<trojan>-data <trojan>-dummies.sv <trojan>.xdc`
6. Append contents of the `-dummies.sv` file in the opened vivado project into the top module
7. Add the `.xdc` file to the vivado project as constraints
8. Synthesize and Place & Route (Click on ``Run Implementation'')
9. Uncomment the respective `set output_file` line in the `3_trojan_insertion/1_placer/extract_design_cells.tcl` script
10. In the Tcl Console of Vivado, run `source ./extract_design_cells.tcl`
11. In the terminal, re-run the generate script with additional parameters `python generate_dummy_cells_and_constraints.py extracted-<trojan>-data <trojan>-dummies.sv <trojan>.xdc extracted-<trojan>-design-data SLICE_X105Y81` where `SLICE_X105Y81` denotes the center of the region of interest, so cells that have no placement details will be placed in the near of the center
12. Replace the constraints with the new generated ones
13. Add / replace extra constraints out of the respective section `Custom Constraints` below in the constraints file and reorder such that vivado doesn't return any critical warnings due to placement conflicts and all cells are placed (useful Tcl command `get_cells -filter { IS_BEL_FIXED == 0 && NAME !~ GND* && NAME !~ VCC* }`)
14. Click on ``Run Implementation''
15. Change to the trojan design directory in the Tcl Console of Vivado `cd ../../2_trojan_designs/<trojan>`
16. Write checkpoint and EDIF netlist by entering `write_checkpoint trojan.dcp; write_edif trojan.edf`
17. Run the custom routing and merging script in a shell in the trojan design's directory with `../../3_trojan_insertion/route_and_merge_trojan.sh .`

Custom Constraints
------------------

Constraints from this section should be appended to the generated constraints file after step 12 to take care of non implemented placement of some elements (such as CARRY4) and clock routing.

### Tiny Logic Analyzer

```
set_property BEL C6LUT [get_cells "FSM_onehot_tinyla_state[0]_i_1"];
set_property LOC SLICE_X101Y76 [get_cells "FSM_onehot_tinyla_state[0]_i_1"];
set_property IS_LOC_FIXED yes [get_cells "FSM_onehot_tinyla_state[0]_i_1"];
set_property IS_BEL_FIXED yes [get_cells "FSM_onehot_tinyla_state[0]_i_1"];

set_property BEL CFF [get_cells "FSM_onehot_tinyla_state_reg[0]"];
set_property LOC SLICE_X101Y76 [get_cells "FSM_onehot_tinyla_state_reg[0]"];
set_property IS_LOC_FIXED yes [get_cells "FSM_onehot_tinyla_state_reg[0]"];
set_property IS_BEL_FIXED yes [get_cells "FSM_onehot_tinyla_state_reg[0]"];

set_property BEL AFF [get_cells "tinyla_buffer_read_addr_reg[0]"];
set_property LOC SLICE_X93Y69 [get_cells "tinyla_buffer_read_addr_reg[0]"];
set_property IS_LOC_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[0]"];
set_property IS_BEL_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[0]"];

set_property BEL BFF [get_cells "tinyla_buffer_read_addr_reg[1]"];
set_property LOC SLICE_X93Y69 [get_cells "tinyla_buffer_read_addr_reg[1]"];
set_property IS_LOC_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[1]"];
set_property IS_BEL_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[1]"];

set_property BEL CFF [get_cells "tinyla_buffer_read_addr_reg[2]"];
set_property LOC SLICE_X93Y69 [get_cells "tinyla_buffer_read_addr_reg[2]"];
set_property IS_LOC_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[2]"];
set_property IS_BEL_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[2]"];

set_property BEL DFF [get_cells "tinyla_buffer_read_addr_reg[3]"];
set_property LOC SLICE_X93Y69 [get_cells "tinyla_buffer_read_addr_reg[3]"];
set_property IS_LOC_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[3]"];
set_property IS_BEL_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[3]"];

set_property BEL AFF [get_cells "tinyla_buffer_read_addr_reg[4]"];
set_property LOC SLICE_X93Y70 [get_cells "tinyla_buffer_read_addr_reg[4]"];
set_property IS_LOC_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[4]"];
set_property IS_BEL_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[4]"];

set_property BEL BFF [get_cells "tinyla_buffer_read_addr_reg[5]"];
set_property LOC SLICE_X93Y70 [get_cells "tinyla_buffer_read_addr_reg[5]"];
set_property IS_LOC_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[5]"];
set_property IS_BEL_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[5]"];

set_property BEL CFF [get_cells "tinyla_buffer_read_addr_reg[6]"];
set_property LOC SLICE_X93Y70 [get_cells "tinyla_buffer_read_addr_reg[6]"];
set_property IS_LOC_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[6]"];
set_property IS_BEL_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[6]"];

set_property BEL DFF [get_cells "tinyla_buffer_read_addr_reg[7]"];
set_property LOC SLICE_X93Y70 [get_cells "tinyla_buffer_read_addr_reg[7]"];
set_property IS_LOC_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[7]"];
set_property IS_BEL_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[7]"];

set_property BEL AFF [get_cells "tinyla_buffer_read_addr_reg[8]"];
set_property LOC SLICE_X93Y71 [get_cells "tinyla_buffer_read_addr_reg[8]"];
set_property IS_LOC_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[8]"];
set_property IS_BEL_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[8]"];

set_property BEL BFF [get_cells "tinyla_buffer_read_addr_reg[9]"];
set_property LOC SLICE_X93Y71 [get_cells "tinyla_buffer_read_addr_reg[9]"];
set_property IS_LOC_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[9]"];
set_property IS_BEL_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[9]"];

set_property BEL CFF [get_cells "tinyla_buffer_read_addr_reg[10]"];
set_property LOC SLICE_X93Y71 [get_cells "tinyla_buffer_read_addr_reg[10]"];
set_property IS_LOC_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[10]"];
set_property IS_BEL_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[10]"];

set_property BEL DFF [get_cells "tinyla_buffer_read_addr_reg[11]"];
set_property LOC SLICE_X93Y71 [get_cells "tinyla_buffer_read_addr_reg[11]"];
set_property IS_LOC_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[11]"];
set_property IS_BEL_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[11]"];

set_property BEL AFF [get_cells "tinyla_buffer_read_addr_reg[12]"];
set_property LOC SLICE_X93Y72 [get_cells "tinyla_buffer_read_addr_reg[12]"];
set_property IS_LOC_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[12]"];
set_property IS_BEL_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[12]"];

set_property BEL BFF [get_cells "tinyla_buffer_read_addr_reg[13]"];
set_property LOC SLICE_X93Y72 [get_cells "tinyla_buffer_read_addr_reg[13]"];
set_property IS_LOC_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[13]"];
set_property IS_BEL_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[13]"];

set_property BEL CFF [get_cells "tinyla_buffer_read_addr_reg[14]"];
set_property LOC SLICE_X93Y72 [get_cells "tinyla_buffer_read_addr_reg[14]"];
set_property IS_LOC_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[14]"];
set_property IS_BEL_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[14]"];

set_property BEL A6LUT [get_cells "tinyla_buffer_read_addr[0]_i_2"];
set_property LOC SLICE_X93Y69 [get_cells "tinyla_buffer_read_addr[0]_i_2"];
set_property IS_LOC_FIXED yes [get_cells "tinyla_buffer_read_addr[0]_i_2"];
set_property IS_BEL_FIXED yes [get_cells "tinyla_buffer_read_addr[0]_i_2"];

set_property BEL CARRY4 [get_cells "tinyla_buffer_read_addr_reg[12]_i_1"];
set_property LOC SLICE_X93Y72 [get_cells "tinyla_buffer_read_addr_reg[0]_i_1"];
set_property IS_LOC_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[0]_i_1"];
set_property IS_BEL_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[0]_i_1"];

set_property BEL CARRY4 [get_cells "tinyla_buffer_read_addr_reg[8]_i_1"];
set_property LOC SLICE_X93Y71 [get_cells "tinyla_buffer_read_addr_reg[0]_i_1"];
set_property IS_LOC_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[0]_i_1"];
set_property IS_BEL_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[0]_i_1"];

set_property BEL CARRY4 [get_cells "tinyla_buffer_read_addr_reg[4]_i_1"];
set_property LOC SLICE_X93Y70 [get_cells "tinyla_buffer_read_addr_reg[0]_i_1"];
set_property IS_LOC_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[0]_i_1"];
set_property IS_BEL_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[0]_i_1"];

set_property BEL CARRY4 [get_cells "tinyla_buffer_read_addr_reg[0]_i_1"];
set_property LOC SLICE_X93Y69 [get_cells "tinyla_buffer_read_addr_reg[0]_i_1"];
set_property IS_LOC_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[0]_i_1"];
set_property IS_BEL_FIXED yes [get_cells "tinyla_buffer_read_addr_reg[0]_i_1"];

set_property BEL RAMB36E1 [get_cells "tinyla_buffer"];
set_property LOC RAMB36_X5Y25 [get_cells "tinyla_buffer"];
set_property IS_LOC_FIXED yes [get_cells "tinyla_buffer"];
set_property IS_BEL_FIXED yes [get_cells "tinyla_buffer"];

set_property FIXED_ROUTE { CLK_BUFG_BUFGCTRL5_O \
 CLK_BUFG_REBUF_X139Y169/CLK_BUFG_REBUF_R_CK_GCLK5_BOT \
 CLK_BUFG_REBUF_X139Y142/CLK_BUFG_REBUF_R_CK_GCLK5_BOT \
 { CLK_HROW_CK_MUX_OUT_R0 CLK_HROW_CK_HCLK_OUT_R0 CLK_HROW_CK_BUFHCLK_R0 HCLK_R_X149Y130/HCLK_LEAF_CLK_B_TOP2 INT_R_X59Y126/GCLK_B2_WEST { CLK_L1 BRAM_FIFO36_CLKBWRCLKU } CLK_L0 BRAM_FIFO36_CLKBWRCLKL } \
 CLK_BUFG_REBUF_X139Y117/CLK_BUFG_REBUF_R_CK_GCLK5_BOT \
 CLK_BUFG_REBUF_X139Y90/CLK_BUFG_REBUF_R_CK_GCLK5_BOT \
 CLK_HROW_CK_MUX_OUT_R9 CLK_HROW_CK_HCLK_OUT_R9 CLK_HROW_CK_BUFHCLK_R9 \
 { HCLK_L_X168Y78/HCLK_LEAF_CLK_B_TOPL4 { INT_L_X66Y75/GCLK_L_B10_EAST CLK1 CLBLM_M_CLK } INT_L_X66Y76/GCLK_L_B10_EAST CLK0 CLBLM_L_CLK } \
 { HCLK_L_X172Y78/HCLK_LEAF_CLK_B_BOTL5 INT_L_X68Y73/GCLK_L_B11_WEST CLK_L0 CLBLM_L_CLK } \
 HCLK_L_X178Y78/HCLK_LEAF_CLK_B_BOTL4 INT_L_X70Y72/GCLK_L_B10_WEST CLK_L1 CLBLM_M_CLK } [get_nets "clk_i"];
```

### Instruction Replacement Trojan

```
set_property FIXED_ROUTE { CLK_BUFG_BUFGCTRL5_O \
 CLK_BUFG_REBUF_X139Y169/CLK_BUFG_REBUF_R_CK_GCLK5_BOT \
 CLK_BUFG_REBUF_X139Y142/CLK_BUFG_REBUF_R_CK_GCLK5_BOT \
 CLK_BUFG_REBUF_X139Y117/CLK_BUFG_REBUF_R_CK_GCLK5_BOT \
 CLK_BUFG_REBUF_X139Y90/CLK_BUFG_REBUF_R_CK_GCLK5_BOT \
 CLK_HROW_CK_MUX_OUT_R9 CLK_HROW_CK_HCLK_OUT_R9 CLK_HROW_CK_BUFHCLK_R9 \
 HCLK_L_X148Y78/HCLK_LEAF_CLK_B_BOTL4 \
 INT_L_X58Y60/GCLK_L_B10_EAST { CLK1 CLBLM_M_CLK } CLK0 CLBLM_L_CLK } [get_nets "clk_i"];
```

### AES Register Trojan

```
set_property FIXED_ROUTE { CLK_BUFG_BUFGCTRL2_O \
 CLK_BUFG_REBUF_X139Y169/CLK_BUFG_REBUF_R_CK_GCLK2_BOT \
 CLK_BUFG_REBUF_X139Y194/CLK_BUFG_REBUF_R_CK_GCLK2_BOT \
 CLK_HROW_CK_MUX_OUT_L10 CLK_HROW_CK_HCLK_OUT_L10 CLK_HROW_CK_BUFHCLK_L10 \
 HCLK_L_X136Y182/HCLK_LEAF_CLK_B_TOPL4 INT_L_X54Y183/GCLK_L_B10_WEST CLK_L1 CLBLL_L_X54Y183/CLBLL_LL_CLK } [get_nets "aes_clk_i"];
```

### Instruction Replacement Trojan

```
set_property FIXED_ROUTE { CLK_BUFG_BUFGCTRL5_O \
 CLK_BUFG_REBUF_X139Y169/CLK_BUFG_REBUF_R_CK_GCLK5_BOT \
 CLK_BUFG_REBUF_X139Y142/CLK_BUFG_REBUF_R_CK_GCLK5_BOT \
 CLK_BUFG_REBUF_X139Y117/CLK_BUFG_REBUF_R_CK_GCLK5_BOT \
 CLK_BUFG_REBUF_X139Y90/CLK_BUFG_REBUF_R_CK_GCLK5_BOT \
 CLK_HROW_CK_MUX_OUT_R9 CLK_HROW_CK_HCLK_OUT_R9 CLK_HROW_CK_BUFHCLK_R9 \
 { HCLK_L_X148Y78/HCLK_LEAF_CLK_B_TOPL4 INT_L_X58Y80/GCLK_L_B10_EAST CLK0 CLBLM_L_CLK } \
 HCLK_L_X142Y78/HCLK_LEAF_CLK_B_TOPL4 INT_L_X56Y84/GCLK_L_B10_EAST CLK0 CLBLL_L_CLK } [get_nets "clk_i"];
```