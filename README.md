This repository contains case studies and scripts for our research publication about senseful FPGA bitstream modifications.
The scripts work in cooperation with RapidWright, the scripting framework for Xilinx FPGAs.
Also, it has dependencies to the ProjectXray database for actual bitstream fiddling.
The scripts are written in Python and Tcl whilst the FPGA designs are written in SystemVerilog, like OpenTitan, the base for the case studies is written in.

The OpenTitan version we used for our case studies is commit [24baa88](https://github.com/lowRISC/opentitan/tree/24baa88a432a1822ae7d1065bbd244538f38d030). There is no specific reason for the choice, however at this development stage, the OpenTitan still runs fine on the NexysVideo FPGA Board and we chose to not update the OpenTitan as this would have involved extra work during our experiments. However the current version of the OpenTitan in combination with the ChipWhisperer CW310 board should also work. It just would need the ProjectXray database generated for the Kintex 7 410T FPGA and probably some additional tweaks which were not yet evaluated.
The NexysVideo board is based on the smaller Artix 7 200T FPGA.

This repository is work in progress.
