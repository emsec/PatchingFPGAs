#!/usr/bin/env python3
"""Usage: rapidwright clean_fasm.py output.dcp output.fasm part2.fasm

This script is step 4 of the how-to in the "reroute_fasm_base_to_mod" script.
Thus, after "reroute_fasm_base_to_mod" the "output.dcp" needs to be converted
to a bitstream (with Vivado) and then to a .fasm (with prjxray) "output.fasm".
Then, this script is run with all the files. Result is a "part2.fasm" which
then should be again checked for any conflicts and then be applied using
Julian's script BUT after the part1! (Step 5 of the How-to).

ATTENTION: This script is quite dumb and expects inserted circuit to be in
completely free CLBs (except the i_ and o_ connecting dummy cells!) Otherwise
some unrelated slice settings might get overridden, as the bit2fasm tends to
add these to the fasm!!!
"""
import re
import sys
from com.xilinx.rapidwright.design import Design

def getDummyClbs(design):
    dummyClbs = set()
    for cell in design.getCells():
        if re.match(r"^(i_[0-9]+(_lutmod_[0-9A-F]+)?(/LUT[56])?|o_[0-9]+(_inferred_SLICE_X[0-9]+Y[0-9]+_[ABCD][1-6X])?(/LUT[56])?)$", cell.getName()):
            dummyClbs.add(cell.getTile().getName())
    return dummyClbs

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)

    # Take routed design for dummy-cell identification
    design = Design.readCheckpoint(sys.argv[1])
    dummyClbs = getDummyClbs(design)
    print("dummyClbs:", dummyClbs)

    # Filter out the fasm for dummy-cells
    emptyLine = True
    with open(sys.argv[3], 'w') as output:
        for line in open(sys.argv[2], 'r'):
            if not line.strip():
                if not emptyLine:
                    emptyLine = True
                    output.write(line)
                continue
            tile = line.split(".", 1)[0]
            if tile in dummyClbs:
                print("removing {}".format(line.strip()))
                continue
            emptyLine = False
            output.write(line)
        if not emptyLine:
            output.write("\n")