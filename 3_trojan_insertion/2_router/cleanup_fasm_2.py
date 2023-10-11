#!/usr/bin/env python3
"""Usage: rapidwright clean_fasm.py output.dcp output.fasm part2.fasm

This script is step 4 of the how-to in the "reroute_fasm_base_to_mod" script.
Thus, after "reroute_fasm_base_to_mod" the "output.dcp" needs to be converted
to a bitstream (with Vivado) and then to a .fasm (with prjxray) "output.fasm".
Then, this script is run with all the files. Result is a "part2.fasm" which
then should be again checked for any conflicts and then be applied using the
bitstream tool BUT after the part1! (Step 5 of the How-to).
"""
import re
import sys
from com.xilinx.rapidwright.design import Design

def getDummyClbs(design):
    dummyClbs = set()
    for cell in design.getCells():
        if re.match(r"^(i_[0-9]+(_lutmod_[0-9A-F]+)?(/LUT[56])?|o_[0-9]+(_inferred_SLICE_X[0-9]+Y[0-9]+_[ABCD][1-6X])?(/LUT[56])?)$", cell.getName()):
            dummyClbs.add((cell.getTile().getName(), cell.getBEL().getName()))
    return dummyClbs

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)

    # Take routed design for dummy-cell identification
    design = Design.readCheckpoint(sys.argv[1])
    dummyClbs = getDummyClbs(design)
    selectedDummyClbs = set()

    # Filter out the fasm for dummy-cells
    emptyLine = True
    with open(sys.argv[3], 'w') as output:
        for line in open(sys.argv[2], 'r'):
            if not line.strip():
                if not emptyLine:
                    emptyLine = True
                    output.write(line)
                continue
            tile, bel = line.split(".", 1)
            for clb in dummyClbs:
                if tile in clb[0] and (clb[1] in bel or (("." + clb[1][0] + "LUT" in bel or "." + clb[1][0] + "FF" in bel) and ("LUT" in clb[1] or "FF" in clb[1]))):
                    selectedDummyClbs.add(clb)
                    print("removing {}".format(line.strip()))
                    break
            else:
                # not to remove
                emptyLine = False
                output.write(line)
        if not emptyLine:
            output.write("\n")
    
    print("missed dummy clbs:", dummyClbs - selectedDummyClbs)
