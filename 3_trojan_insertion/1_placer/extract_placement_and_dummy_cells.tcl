set requested_data {
    { method fdreout          signal instr_addr_i          cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_addr_q_reg[%31..1%]" }
    { method net/lutout       signal instr_rdata_i         cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/instr_out[%31..0%]" }
    { method bufgctrlout      signal clk_i                 cell "top_earlgrey/u_clkmgr/u_main_cg/i_cg/gen_xilinx.u_impl_xilinx/u_bufgce" }
    { method emptysliceparts }
}

set output_file "extracted-tinylogicanalyzer-data"

#set requested_data {
#    { method lutout           signal ctrl_we_i             cell "top_earlgrey/u_xbar_main/u_sm1_27/u_devicefifo/reqfifo/ctrl_we_q_i_1" }
#    { method fdreout          signal state_init_i          cell "top_earlgrey/u_aes/u_reg/u_data_in_%1%3..0%/q_reg[%2%31..0%]" }
#    { method fdreout/lutin    signal state_init_o          cell "top_earlgrey/u_aes/u_reg/u_data_in_%1%3..0%/q_reg[%2%31..0%]"                                                        input_regex "top_earlgrey/u_aes/u_aes_core/u_aes_cipher_core/u_aes_cipher_control/state_q\\\[.*" }
#    { method fdreout          signal key_init_i            cell "top_earlgrey/u_aes/u_aes_core/key_init_q_reg[0][%1%3..0%][%2%31..0%]" }
#    { method fdreout/lutin    signal key_init_o            cell "top_earlgrey/u_aes/u_aes_core/key_init_q_reg[0][%1%3..0%][%2%31..0%]"                                                input_regex "top_earlgrey/u_aes/u_aes_core/u_aes_cipher_core/u_aes_cipher_control/key_full_q\\\[.*" }
#    { method fdreout          signal aes_cipher_ctrl_cs_i  cell "top_earlgrey/u_aes/u_aes_core/u_aes_cipher_core/u_aes_cipher_control/FSM_sequential_aes_cipher_ctrl_cs_reg[%2..0%]" }
#    { method bufgctrlout      signal aes_clk_i             cell "top_earlgrey/u_clkmgr/u_clk_main_aes_cg/gen_xilinx.u_impl_xilinx/u_bufgce" }
#    { method emptysliceparts }
#}

#set output_file "extracted-aesregistertrojan-data"

#set requested_data {
#    { method lutout           signal instr_rdata_i[25]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[31]_i_6" }
#    { method lutout           signal instr_rdata_i[24]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[30]_i_3" }
#    { method lutout           signal instr_rdata_i[23]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[29]_i_4" }
#    { method lutout           signal instr_rdata_i[22]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[28]_i_6" }
#    { method lutout           signal instr_rdata_i[21]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[27]_i_3" }
#    { method lutout           signal instr_rdata_i[20]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[26]_i_4" }
#    { method lutout           signal instr_rdata_i[19]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[25]_i_7" }
#    { method lutout           signal instr_rdata_i[18]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[24]_i_7" }
#    { method lutout           signal instr_rdata_i[17]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[23]_i_6" }
#    { method lutout           signal instr_rdata_i[16]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[22]_i_3" }
#    { method lutout           signal instr_rdata_i[15]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[21]_i_4" }
#    { method lutout           signal instr_rdata_i[14]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[20]_i_2" }
#    { method lutout           signal instr_rdata_i[13]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[19]_i_3" }
#    { method lutout           signal instr_rdata_i[12]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[18]_i_5" }
#    { method lutout           signal instr_rdata_i[11]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[17]_i_3" }
#    { method lutout           signal instr_rdata_i[10]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[16]_i_3" }
#    { method lutout           signal instr_rdata_i[9]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[15]_i_1" }
#    { method lutout           signal instr_rdata_i[8]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[14]_i_1" }
#    { method lutout           signal instr_rdata_i[7]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[13]_i_1" }
#    { method lutout           signal instr_rdata_i[6]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[12]_i_1" }
#    { method lutout           signal instr_rdata_i[5]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[7]_i_1" }
#    { method lutout           signal instr_rdata_i[4]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[6]_i_1" }
#    { method lutout           signal instr_rdata_i[3]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[5]_i_1" }
#    { method lutout           signal instr_rdata_i[2]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[4]_i_1" }
#    { method lutout           signal instr_rdata_i[1]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[3]_i_1" }
#    { method lutout           signal instr_rdata_i[0]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[2]_i_1" }
#    { method lutout/lutin     signal instr_rdata_o[19]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[31]_i_6" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[18]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[30]_i_3" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[17]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[29]_i_4" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[16]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[28]_i_6" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[15]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[27]_i_3" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[14]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[26]_i_4" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[13]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[25]_i_7" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[12]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[24]_i_7" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[11]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[23]_i_6" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[10]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[22]_i_3" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[9]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[21]_i_4" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[8]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[20]_i_2" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[7]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[19]_i_3" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[6]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[18]_i_5" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[5]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[17]_i_3" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[4]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[16]_i_3" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[3]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[15]_i_1" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[2]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[14]_i_1" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[1]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[13]_i_1" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[0]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[12]_i_1" input_regex ".*" }
#    { method bufgctrlout      signal clk_i                 cell "top_earlgrey/u_clkmgr/u_main_cg/i_cg/gen_xilinx.u_impl_xilinx/u_bufgce" }
#    { method emptysliceparts }
#}

#set output_file "extracted-instructionreplacementtrojan-data"

#set requested_data {
#    { method fdreout          signal instr_addr_i          cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_addr_q_reg[%31..1%]" }
#    { method lutout           signal instr_rdata_i[31]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[31]_i_6" }
#    { method lutout           signal instr_rdata_i[30]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[30]_i_3" }
#    { method lutout           signal instr_rdata_i[29]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[29]_i_4" }
#    { method lutout           signal instr_rdata_i[28]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[28]_i_6" }
#    { method lutout           signal instr_rdata_i[27]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[27]_i_3" }
#    { method lutout           signal instr_rdata_i[26]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[26]_i_4" }
#    { method lutout           signal instr_rdata_i[25]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[25]_i_7" }
#    { method lutout           signal instr_rdata_i[24]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[24]_i_7" }
#    { method lutout           signal instr_rdata_i[23]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[23]_i_6" }
#    { method lutout           signal instr_rdata_i[22]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[22]_i_3" }
#    { method lutout           signal instr_rdata_i[21]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[21]_i_4" }
#    { method lutout           signal instr_rdata_i[20]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[20]_i_2" }
#    { method lutout           signal instr_rdata_i[19]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[19]_i_3" }
#    { method lutout           signal instr_rdata_i[18]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[18]_i_5" }
#    { method lutout           signal instr_rdata_i[17]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[17]_i_3" }
#    { method lutout           signal instr_rdata_i[16]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[16]_i_3" }
#    { method lutout           signal instr_rdata_i[15]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[15]_i_1" }
#    { method lutout           signal instr_rdata_i[14]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[14]_i_1" }
#    { method lutout           signal instr_rdata_i[13]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[13]_i_1" }
#    { method lutout           signal instr_rdata_i[12]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[12]_i_1" }
#    { method lutout           signal instr_rdata_i[11]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[11]_i_1" }
#    { method lutout           signal instr_rdata_i[10]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[10]_i_1" }
#    { method lutout           signal instr_rdata_i[9]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[9]_i_1" }
#    { method lutout           signal instr_rdata_i[8]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[8]_i_1" }
#    { method lutout           signal instr_rdata_i[7]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[7]_i_1" }
#    { method lutout           signal instr_rdata_i[6]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[6]_i_1" }
#    { method lutout           signal instr_rdata_i[5]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[5]_i_1" }
#    { method lutout           signal instr_rdata_i[4]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[4]_i_1" }
#    { method lutout           signal instr_rdata_i[3]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[3]_i_1" }
#    { method lutout           signal instr_rdata_i[2]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[2]_i_1" }
#    { method lutout           signal instr_rdata_i[1]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[1]_i_1" }
#    { method lutout           signal instr_rdata_i[0]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[0]_i_1" }
#    { method lutout           signal instr_rdata_id_o6_i_3_n_0  cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[6]_i_3"}
#    { method lutout           signal instr_rdata_id_o21_i_7_n_0 cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[21]_i_7"}
#    { method bufgctrlout      signal clk_i                 cell "top_earlgrey/u_clkmgr/u_main_cg/i_cg/gen_xilinx.u_impl_xilinx/u_bufgce" }
#    { method lutout/lutin     signal instr_rdata_o[31]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[31]_i_6" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[30]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[30]_i_3" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[29]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[29]_i_4" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[28]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[28]_i_6" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[27]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[27]_i_3" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[26]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[26]_i_4" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[25]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[25]_i_7" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[24]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[24]_i_7" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[23]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[23]_i_6" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[22]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[22]_i_3" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[21]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[21]_i_4" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[20]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[20]_i_2" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[19]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[19]_i_3" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[18]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[18]_i_5" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[17]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[17]_i_3" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[16]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[16]_i_3" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[15]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[15]_i_1" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[14]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[14]_i_1" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[13]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[13]_i_1" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[12]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[12]_i_1" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[11]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[11]_i_1" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[10]     cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[10]_i_1" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[9]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[9]_i_1" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[8]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[8]_i_1" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[7]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[7]_i_1" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[6]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[6]_i_1" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[5]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[5]_i_1" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[4]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[4]_i_1" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[3]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[3]_i_1" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[2]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[2]_i_1" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[1]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[1]_i_1" input_regex ".*" }
#    { method lutout/lutin     signal instr_rdata_o[0]      cell "top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_c_id_o[0]_i_1" input_regex ".*" }
#    { method emptysliceparts }
#}

#set output_file "extracted-instructionmodtrojan-data"

# lutout:
# - connect the input to the net that is connected with the output net of the respective O pin
# - place dummy luts at the same positions as by the supplied cell iteration
# - cell name allows regex
# prints: lutout id signalname[i] bel loc belpin

# fdreout:
# - connect the input to the net that is connected with the output net of the respective Q pin
# - place dummy fdres at the same positions as by the supplied cell iteration
# prints: fdreout id signalname[i] bel loc

# net/lutout:
# - same as lutout, but start with a net name instead and take the output pin of that net (must be on the first hierarchy level!)

# fdreout/lutin:
# - traverse from a fdreout net (see above) to the input pin that can be evaluated with the additional argument regex
# - connect the output to the net that is connected with the respective input pin
# - place dummy luts at the same positions as by the supplied cell iteration
# prints: lutin id signalname[i] bel loc lutpin

# lutout/lutin:
# - same as fdreout/lutin but with lut instead of fdre

# fdrein:
# - connect the output to the net that is connected with the respective input pin
# - place dummy fdres at the same positions as by the supplied cell iteration
# prints: fdrein id signalname[i] bel loc D

# bufgctrlout:
# - considers difficult clktree routing and thus prepares this by also returning the current routes of this clock signal
# - connect the input to the net that is connected with the output net of the respective Q pin
# - place dummy bufgctrl at the same positions as by the supplied cell iteration
# prints: bufgctrlout id signalname loc route

# emptysliceparts:
# WARNING: this method depending on target size and utilization takes a long time to finish (most likely because of a poorly optimized vivado tcl implementation, schedule ~5-10 minutes) and might return a very long line of text in the output file
# - returns a list of all vacant slicerows SLICE_X..Y../A-D
# - append a float score of used pins of the whole slice (if there are 23 nets connected to the slice, return approx 0.51, as there are totally 45 pins in each slice)
# prints: slice/a score slice/b score ...

proc iterate_indices {formatstr} {
    set regex_results [regexp -inline -all {(?:%(\d+))?%(\d+)\.\.(\d+)%} $formatstr]
    if {[llength $regex_results] == 0} {
        # no iterators detected, return single result
        return $formatstr
    } elseif {[llength $regex_results] == 4} {
        # single level iterator detected, return list based on iterator
        set l {}
        if {[lindex $regex_results 2] > [lindex $regex_results 3]} {
            for {set i [lindex $regex_results 2]} {$i >= [lindex $regex_results 3]} {set i [expr {$i - 1}]} {
                lappend l [string map [list [lindex $regex_results 0] $i] $formatstr]
            }
        } else {
            for {set i [lindex $regex_results 2]} {$i <= [lindex $regex_results 3]} {incr i} {
                lappend l [string map [list [lindex $regex_results 0] $i] $formatstr]
            }
        }
        return $l
    } elseif {[llength $regex_results] % 4 == 0} {
        # multi-level iterator detected, return list replacing first iterator and then recurse

        # first, find the lowest index of iterators
        set lowest_result [lrange $regex_results 0 3]
        for {set j 4} {$j < [llength $regex_results]} {incr j 4} {
            set single_result [lrange $regex_results $j [expr {$j + 3}]]
            if {[lindex $single_result 1] < [lindex $lowest_result 1]} {
                set lowest_result $single_result
            }
        }

        # iterate this level and recurse
        set l {}
        if {[lindex $lowest_result 2] > [lindex $lowest_result 3]} {
            for {set i [lindex $lowest_result 2]} {$i >= [lindex $lowest_result 3]} {set i [expr {$i - 1}]} {
                set l [concat $l [iterate_indices [string map [list [lindex $lowest_result 0] $i] $formatstr]]]
            }
        } else {
            for {set i [lindex $lowest_result 2]} {$i <= [lindex $lowest_result 3]} {incr i} {
                set l [concat $l [iterate_indices [string map [list [lindex $lowest_result 0] $i] $formatstr]]]
            }
        }
        return $l
    } else {
        puts "ERROR: wrong format of iterate_indices"
        return {}
    }
}

set id_in 0
set id_out 0

set fo [open $output_file "w"]

foreach d $requested_data {
    if {[dict get $d method] == "emptysliceparts"} {
        set all_slices [lsearch -all -inline [get_sites] "SLICE_*"]
        set total_slice_pins [llength [get_site_pins -of_objects [lindex $all_slices 0]]]
        puts -nonewline $fo "emptysliceparts"
        foreach slice $all_slices {
            # evaluate critical elements of the slice
            set bels_of_interest [get_bels -quiet -filter {(NAME =~ "*FF" || NAME =~ "*LUT") && IS_USED} -of_objects $slice]

            if {![llength $bels_of_interest]} {
                # completely vacant slice, so this is a special case where we can safely assume there are enough routing resources available, thus score 0.0
                puts -nonewline $fo " $slice/A 0.0 $slice/B 0.0 $slice/C 0.0 $slice/D 0.0"
            } else {
                # go through each part (A, B, C, D) individually
                set slice_score -1
                foreach part {A B C D} {
                    if {[llength [lsearch -all $bels_of_interest "*/$part*"]]} {
                        continue
                    }
                    # row is empty
                    if {$slice_score == -1} {
                        # score the slice
                        set slice_score [expr {[expr [join [get_property IS_USED [get_site_pins -of_objects $slice]] +]] * 1.0 / $total_slice_pins}]
                    }
                    puts -nonewline $fo " $slice/$part $slice_score"
                }
            }
        }
        puts $fo ""
        continue
    }

    set indices [iterate_indices [dict get $d cell]]
    set c [expr {[llength $indices] - 1}]
    foreach cellname $indices {
        if {[dict get $d method] == "net/lutout"} {
            if {[dict exists $d cellregex]} {
                set net [get_nets -regex $cellname]
            } else {
                set net [get_nets $cellname]
            }
            set cell [get_property PARENT_CELL [get_pins -leaf -filter {DIRECTION == "out" && IS_LEAF} -of $net]]
        } else {
            if {[dict exists $d cellregex]} {
                set cell [get_cells -regex $cellname]
            } else {
                set cell [get_cells $cellname]
            }
        }
        set bel [get_property BEL $cell]
        set loc [get_property LOC $cell]
        set signal [dict get $d signal]
        if {[llength $indices] > 1} {
            set signal "$signal\[$c\]"
        }
        switch [dict get $d method] {
            net/lutout -
            lutout {
                set tmp [lindex [get_bel_pins -filter {DIRECTION == OUT} -of_objects [get_pins -of_objects $cell]] 0]
                set belpin [string range $tmp [expr {[string last / $tmp] + 1}] end]
                puts $fo "lutout i_$id_in $signal $bel $loc $belpin"
                incr id_in
            }
            fdreout {
                puts $fo "fdreout i_$id_in $signal $bel $loc"
                incr id_in
            }
            fdreout/lutin {
                set outpin [lindex [get_pins -filter {DIRECTION == OUT} -of_objects $cell] 0]
                set inpin [lindex [get_pins -regexp -filter "NAME =~ [dict get $d input_regex] && DIRECTION == IN" -of_objects [get_nets -segment -of_objects $outpin]] 0]
                set cell [get_cells -of_objects $inpin]
                set bel [get_property BEL $cell]
                set loc [get_property LOC $cell]
                set bel_inpin [get_bel_pins -of_objects $inpin]
                set belpin [string range $bel_inpin [expr {[string last / $bel_inpin] + 1}] end]
                set pin [string range $inpin [expr {[string last / $inpin] + 1}] end]
                puts $fo "lutin o_$id_out $signal $bel $loc $pin:$belpin"
                incr id_out
            }
            lutout/lutin {
                set outpin [lindex [get_pins -filter {DIRECTION == OUT} -of_objects $cell] 0]
                set inpin [lindex [get_pins -regexp -filter "NAME =~ [dict get $d input_regex] && DIRECTION == IN" -of_objects [get_nets -segment -of_objects $outpin]] 0]
                set cell [get_cells -of_objects $inpin]
                set bel [get_property BEL $cell]
                set loc [get_property LOC $cell]
                set bel_inpin [get_bel_pins -of_objects $inpin]
                set belpin [string range $bel_inpin [expr {[string last / $bel_inpin] + 1}] end]
                set pin [string range $inpin [expr {[string last / $inpin] + 1}] end]
                puts $fo "lutin o_$id_out $signal $bel $loc $pin:$belpin"
                incr id_out
            }
            fdrein {
                puts $fo "fdrein o_$id_out $signal $bel $loc D"
                incr id_out
            }
            bufgctrlout {
                set outpin [lindex [get_pins -filter {DIRECTION == OUT} -of_objects $cell] 0]
                set nodes [get_nodes -of_objects [get_nets -of_objects $outpin]]
                puts -nonewline $fo "bufgctrlout i_$id_in $signal $loc"
                foreach node $nodes {
                    puts -nonewline $fo " $node"
                }
                puts $fo ""
                incr id_in
            }
            default {
                puts "ERROR: unimplemented method [dict get $d method]"
            }
        }
        set c [expr {$c - 1}]
    }
}

close $fo