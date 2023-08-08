# Copyright lowRISC contributors.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0


foreach device_name, device_lib : sw_lib_arch_core_devices
  hsm_demo_elf = executable(
    'hsm_demo_' + device_name,
    sources: ['hsm_demo.c'],
    name_suffix: 'elf',
    dependencies: [
      device_lib,
      riscv_crt,
      sw_lib_aes,
      sw_lib_mmio,
      sw_lib_runtime_hart,
      sw_lib_runtime_print,
      sw_lib_runtime_log,
      sw_lib_pinmux,
      sw_lib_dif_uart,
      sw_lib_irq_handlers,
      sw_lib_testing_test_status,
    ],
    #c_args : ['-Os']
  )

  target_name = 'hsm_demo_@0@_' + device_name

  hsm_demo = custom_target(
    target_name,
    command: make_embedded_target,
    input: hsm_demo_elf,
    output: make_embedded_target_outputs,
    build_by_default: true,
  )

#  hsm_demo_dis = custom_target(
#    target_name.format('dis'),
#    input: hsm_demo_elf,
#    kwargs: elf_to_dis_custom_target_args,
#  )
#
#  hsm_demo_bin = custom_target(
#    target_name.format('bin'),
#    input: hsm_demo_elf,
#    kwargs: elf_to_bin_custom_target_args,
#  )
#
#  hsm_demo_vmem32 = custom_target(
#    target_name.format('vmem32'),
#    input: hsm_demo_bin,
#    kwargs: bin_to_vmem32_custom_target_args,
#  )
#
#  hsm_demo_vmem64 = custom_target(
#    target_name.format('vmem64'),
#    input: hsm_demo_bin,
#    kwargs: bin_to_vmem64_custom_target_args,
#  )

  custom_target(
    target_name.format('export'),
    command: export_embedded_target,
    input: [
      hsm_demo_elf,
      hsm_demo,
    ],
    output: target_name.format('export'),
    build_always_stale: true,
    build_by_default: true
  )
endforeach