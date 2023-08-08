#!/usr/bin/env python3
"""Usage: rapidwright cleanup_and_merge_fasm.py output.dcp
       output.fasm output2.fasm to_merge.fasm

This script is step 4 of the how-to in the "reroute_fasm_base_to_mod" script.
Thus, after "reroute_fasm_base_to_mod" the "output.dcp" needs to be converted
to a bitstream (with Vivado) and then to a .fasm (with prjxray) "output.fasm".
Then, this script is run with all the files (also "output2.fasm" from the
reroute script). Result is a "to_merge.fasm" which then should be again checked
for any conflicts and then be applied using Julian's script (Step 5 of the
How-to).
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

def fasm_canonicalize_line(line):
    # e.g. CLBLL_L_X2Y113.SLICEL_X0.BLUT.INIT[36:0] = 37'b1000100000000000000000000000000010001
    if '#' in line:
        line = line.split('#', 1)[0]
    line = line.strip()
    if not line:
        return []
    
    # currently not supported unknown bits
    if line[0] == '{':
        return []
    
    if '=' in line:
        feature_with_address, value = line.split('=', 1)
        feature_with_address = feature_with_address.strip()
        value = value.strip()
        if value == '0':
            return []
    else:
        feature_with_address = line
        value = '1'

    if '[' in feature_with_address:
        feature, feature_address = feature_with_address.split('[', 1)
        feature_address, _ = feature_address.split(']', 1)
        if ':' in feature_address:
            feature_address, feature_range = feature_address.split(':', 1)
            feature_address = int(feature_address)
            feature_range = int(feature_range)
        else:
            feature_address = int(feature_address)
            feature_range = feature_address
    else:
        feature = feature_with_address
        feature_address = 0
        feature_range = 0
    feature_range_length = feature_address - feature_range + 1

    if value == '1':
        assert feature_range_length == 1, "expected a single feature, not a range"
        # nothing to be done with this feature
        if feature_address == 0:
            return [feature]
        else:
            return [feature+'['+str(feature_address)+']']
    else:
        if "'b" in value:
            binlen, binvalue = value.split("'b", 1)
            binlen = int(binlen)
            assert feature_range_length == binlen, "expected a string as long as the range defined"
            binvalue = int(binvalue, 2)
            ret = []
            for i in range(binlen):
                if binvalue & (1 << i):
                    if feature_range+i == 0:
                        ret.append(feature)
                    else:
                        ret.append(feature+'['+str(feature_range+i)+']')
            return ret
        else:
            assert False, "for now could not handle anything else than binary values"

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print(__doc__)
        sys.exit(1)

    # Take routed design for dummy-cell identification
    design = Design.readCheckpoint(sys.argv[1])
    dummyClbs = getDummyClbs(design)

    # Take the zeros
    fasm_zeros = []
    for line in open(sys.argv[3], 'r'):
        if not line.strip():
            continue
        if not line.strip().endswith(" = 0"):
            print("ERROR: untypical zero-bit line found: {}".format(line))
        fasm_zeros.append(line.split("=", 1)[0].strip())

    # Filter out the fasm for dummy-cells
    # Also remove the respecting lines from both zeros and here in case they are included in the zeros
    emptyLine = True
    with open(sys.argv[4], 'w') as output:
        for line in open(sys.argv[2], 'r'):
            if not line.strip():
                if not emptyLine:
                    emptyLine = True
                    output.write(line)
                continue
            canonicalized = fasm_canonicalize_line(line)
            if not canonicalized:
                continue
            canonicalized_output = []
            for singleBit in canonicalized:
                tile = singleBit.split(".", 1)[0]
                if tile in dummyClbs:
                    continue
                if singleBit in fasm_zeros:
                    fasm_zeros.remove(singleBit)
                    continue
                canonicalized_output.append(singleBit)
            emptyLine &= not bool(canonicalized_output)
            if canonicalized_output == canonicalized:
                output.write(line)
            else:
                for singleBit in canonicalized_output:
                    output.write(singleBit + "\n")
        if not emptyLine:
            output.write("\n")
        for line in fasm_zeros:
            output.write(line + " = 0\n")