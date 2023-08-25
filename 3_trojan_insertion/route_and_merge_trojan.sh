#!/bin/bash

# paths that might be adapted to the user's needs
RAPIDWRIGHT_ROOT="../../../../RapidWright"
PRJXRAY_ROOT="../../../../prjxray"
VIVADO_ROOT="/opt/Xilinx/Vivado/2020.1"

# paths that are always relative to the git
ORIGINAL_BIT="../1_opentitan_base/top_earlgrey_nexysvideo.bit"
ORIGINAL_FASM="../1_opentitan_base/top_earlgrey_nexysvideo.fasm"

display_usage() {
    echo "This script can be used to ..."
    echo "It expects RapidWright to be in the folder $RAPIDWRIGHT_ROOT"
    echo -e "\nUsage: $0 <trojan design project>"
}

if [ $# -le 0 ]
then
    display_usage
    exit 1
fi

if [[ ( $@ == "--help") || $@ == "-h" ]]
then
    display_usage
    exit 0
fi

PROJECT_ROOT=$(realpath $1)
SEP="=============================================================================="

# cd to the script path makes things easier
cd "${0%/*}"

# configure ProjectXray
source $PRJXRAY_ROOT/settings/artix7_200t.sh

# check if the original fasm exists. If not, generate with bit2fasm
if [ ! -f $ORIGINAL_FASM ]
then
    echo -e "\n$SEP"
    echo "Starting generation of FASM out of original design (required only once)."
    echo -e "$SEP\n"
    start=$(date +%s)
    $PRJXRAY_ROOT/utils/bit2fasm.py --db-root $PRJXRAY_ROOT/database/artix7 --part xc7a200tsbg484-1 $ORIGINAL_BIT > $ORIGINAL_FASM
    end=$(date +%s)
    echo -e "\n$SEP"
    echo "Generated FASM out of original design in $((end-start)) seconds."
    echo -e "$SEP\n"
fi

# check for the required trojan.dcp and trojan.edf files in the project folder
if [[ ! -f $PROJECT_ROOT/trojan.dcp || ! -f $PROJECT_ROOT/trojan.edf ]]
then
    echo "Error: The required trojan.dcp or trojan.edf are not existing in the project directory."
    exit 1
fi

# configure RapidWright
source $RAPIDWRIGHT_ROOT/rapidwright.sh

echo "(Starting total timer from this point on as all preparation steps have been executed prior.)"
total_start=$(date +%s)

# run the reroute custom router script
echo -e "\n$SEP"
echo "Starting routing process of trojan design into the original design."
echo -e "$SEP\n"
start=$(date +%s)
while :
do
    java com.xilinx.rapidwright.util.RapidWright 2_router/reroute_fasm_base_to_mod.py $PROJECT_ROOT/trojan.dcp $ORIGINAL_FASM $PROJECT_ROOT/trojan_after_rapidwright.dcp $PROJECT_ROOT/trojan_after_rapidwright_part1.fasm $PROJECT_ROOT/trojan_after_rapidwright_priorities.txt
    if [ $? -ne 2 ]
    then
        break
    fi
done
end=$(date +%s)
echo -e "\n$SEP"
echo "Routed trojan design into the original design in $((end-start)) seconds. Finalizing bitstream..."
echo -e "$SEP\n"

# write the bitstream
source $VIVADO_ROOT/settings64.sh
cd $PROJECT_ROOT
vivado -mode batch -source ../../3_trojan_insertion/2_router/write_bitstream.tcl
cd "${0%/*}"

# convert to fasm
$PRJXRAY_ROOT/utils/bit2fasm.py --db-root $PRJXRAY_ROOT/database/artix7 --part xc7a200tsbg484-1 $PROJECT_ROOT/trojan_after_rapidwright.bit > $PROJECT_ROOT/trojan_after_rapidwright.fasm

# cleanup fasm
java com.xilinx.rapidwright.util.RapidWright 2_router/cleanup_fasm.py $PROJECT_ROOT/trojan_after_rapidwright.dcp $PROJECT_ROOT/trojan_after_rapidwright.fasm $PROJECT_ROOT/trojan_after_rapidwright_part2.fasm

# merge the original bitstream with part 1 of the mods
3_bitstream_merging/bitstream $PRJXRAY_ROOT/database xc7a200tsbg484-1 $ORIGINAL_BIT -delta $PROJECT_ROOT/trojan_after_rapidwright_part1.fasm -o_bitstream $PROJECT_ROOT/1.bit

# merge the first intermediate with part 2 of the mods
3_bitstream_merging/bitstream $PRJXRAY_ROOT/database xc7a200tsbg484-1 $PROJECT_ROOT/1.bit -delta $PROJECT_ROOT/trojan_after_rapidwright_part2.fasm -o_bitstream $PROJECT_ROOT/2_THIS.bit

echo "DONE, find the trojanized bitstream at $PROJECT_ROOT/2_THIS.bit"

total_end=$(date +%s)
echo -e "\n$SEP"
echo "Ended routing script in total $((total_end-total_start)) seconds."
echo -e "$SEP"