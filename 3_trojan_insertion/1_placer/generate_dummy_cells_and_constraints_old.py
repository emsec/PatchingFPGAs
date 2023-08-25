#!/usr/bin/env python3
"""Usage: generate_dummy_cells_and_constraints.py <input target> <output.sv>
       <output.xdc> [<input design> <center slice>]

Takes the extracted information of the extract_placement_and_dummy_cells.tcl
script from vivado and builds meaningful verilog dummy cells connected to the
correct signals, as well as a constraint file containing all the placement
information required to be able to place and route a modification fitting to
the original placed and routed design.

Furthermore, it takes another file with information extracted from the
modification project to be able to already place the mod cells on vacant
spaces of the target design by means of constraints. Also, the clock routing
can get evaluated and prepared already. For that, the output of
extract_design_cells.tcl has to be supplied as well. In case no file is
provided, this step will be skipped. This option requires to also provide the
center slice in the format "SLICE_X1Y1" to be able to place cells in the near
the main area of interest. This could be automated though in a future version.

All information supplied to this script with the first argument could be also
coming from reverse engineering means, skipping the need for the original
vivado project checkpoint and the tcl script
extract_placement_and_dummy_cells.tcl.

Warning: this script overrides the two output files.
"""

import math
import os
import re
import sys

FF_TYPES = {"FDCE", "FDRE", "FDPE", "LDCE", "FDSE", "LDPE"}

RE_SLICE_COORDS = re.compile(r"^SLICE_X(\d+)Y(\d+)")

def slice_distance_score(slice1, slice2):
    x1, y1 = (int(x) for x in RE_SLICE_COORDS.match(slice1).groups())
    x2, y2 = (int(x) for x in RE_SLICE_COORDS.match(slice2).groups())
    return abs(max(x1, x2) - min(x1, x2)) + (max(y1, y2) - min(y1, y2))

def generate_dummies_and_constraints(input_target_file, output_verilog, output_xdc, input_design_file, center_slice):
    verilog_file = open(output_verilog, "w")
    xdc_file = open(output_xdc, "w")

    luts = {}
    buffered_luts = []

    empty_slices = {}
    clock_signals = {}
    net_locs = {}

    for line in open(input_target_file):
        stripped_line = line.strip()
        if not stripped_line:
            # ignore empty lines consisting only out of whitespace
            continue
        line_tokens = stripped_line.split()
        method = line_tokens[0]
        if method == "lutout":
            # FIXME: evaluate, whether this also works for other LUTs, as we use this just a single time in our AES trojan where it correctly routes from O6 to the "C" pin of C6LUT and IIRC we need intra-site routing before we route the remaining parts with our own router
            # TODO: what if a LUT is output / input at the same time?
            slicerow = f"{line_tokens[4]}/{line_tokens[3][7]}"
            if slicerow not in luts:
                luts[slicerow] = {}
            luts[slicerow][line_tokens[5]] = (line_tokens[1], line_tokens[2])
        elif method == "fdreout":
            verilog_file.write(f"""(* DONT_TOUCH = "yes" *) FDRE #(
   .INIT(1'b0)
) {line_tokens[1]} (
   .Q({line_tokens[2]})
);

""")
            bel = line_tokens[3].split(".")[1]
            xdc_file.write(f"""set_property BEL {bel} [get_cells "{line_tokens[1]}"];
set_property LOC {line_tokens[4]} [get_cells "{line_tokens[1]}"];
set_property IS_LOC_FIXED yes [get_cells "{line_tokens[1]}"];
set_property IS_BEL_FIXED yes [get_cells "{line_tokens[1]}"];

""")
        elif method == "fdrein":
            verilog_file.write(f"""(* DONT_TOUCH = "yes" *) FDRE #(
   .INIT(1'b0)
) {line_tokens[1]} (
   .D({line_tokens[2]})
);

""")
            bel = line_tokens[3].split(".")[1]
            xdc_file.write(f"""set_property BEL {bel} [get_cells "{line_tokens[1]}"];
set_property LOC {line_tokens[4]} [get_cells "{line_tokens[1]}"];
set_property IS_LOC_FIXED yes [get_cells "{line_tokens[1]}"];
set_property IS_BEL_FIXED yes [get_cells "{line_tokens[1]}"];

""")
        elif method == "lutin":
            # because of the fact that a single slice (one of A-D) might be used two times (especially as output, input for now we don't really case, but would work similar), we basically need to manage the case where both LUT5 and LUT6 are used.
            # the problem actually is in the pins, as all undefined pins will get GLOBAL_LOGIC1 and then the second LUT cannot be placed there as the pin is already defined.
            # so what we do here is we aggregate all output LUTs (TODO: might join input LUTs as well) and merge the pins, so we get a working placement without any warnings. This has to be done also for the constraints probably...

            # 1. whenever a SLICE (A-D) is already defined
            # 2. find a free I* pin in that slice
            # 3. set that free pin to the new pin
            # 4. add a constraint to that SLICE for the pin above and the BEL of this iteration
            # 5. repeat steps 2-4 but the other way around (for the old pin and the routing BEL of the existing SLICE)

            bel = line_tokens[3].split(".")[1][0] + "6LUT" # line_tokens[3].split(".")[1]
            lut_type = bel[2:] + bel[1]

            other_luts = [lut for lut in buffered_luts if lut["loc"] == line_tokens[4] and lut["bel"][0] == bel[0]]
            this_pin = line_tokens[5].split(":") + [line_tokens[2]]
            this_lut = {"lut_type": lut_type, "pins": [this_pin], "id": line_tokens[1], "bel": bel, "loc": line_tokens[4]}
            if other_luts:
                # do the magic noted above
                for other_lut in other_luts:
                    for i in range(6):
                        if not any(pin[0] == f"I{i}" for pin in this_lut["pins"]):
                            break
                    else:
                        raise Exception(f"no free pin found in a LUT of {line_tokens[4]} trying to make it placeable")
                    # add the initial pin of the other lut to the found free pin
                    other_pin = other_lut["pins"][0]
                    this_lut["pins"].append([f"I{i}"] + other_pin[1:])

                    # find a free pin in the other lut to add this lut's pin
                    for i in range(6):
                        if not any(pin[0] == f"I{i}" for pin in other_lut["pins"]):
                            break
                    else:
                        raise Exception(f"no free pin found in a LUT of {line_tokens[4]} trying to make it placeable")
                    other_lut["pins"].append([f"I{i}"] + this_pin[1:])
            buffered_luts.append(this_lut)
        elif method == "bufgctrlout":
            clock_signals[line_tokens[2]] = line_tokens[4:]
            verilog_file.write(f"""(* DONT_TOUCH = "yes" *) BUFGCTRL #(
   .INIT_OUT(0),
   .PRESELECT_I0("FALSE"),
   .PRESELECT_I1("FALSE"),
   .SIM_DEVICE("7SERIES")
)
{line_tokens[1]} (
   .O({line_tokens[2]})
);

""")
            xdc_file.write(f"""set_property BEL BUFGCTRL [get_cells "{line_tokens[1]}"];
set_property LOC {line_tokens[3]} [get_cells "{line_tokens[1]}"];
set_property IS_LOC_FIXED yes [get_cells "{line_tokens[1]}"];
set_property IS_BEL_FIXED yes [get_cells "{line_tokens[1]}"];

""")
        elif method == "emptysliceparts":
            empty_slices |= {x[0]: float(x[1]) for x in zip(line_tokens[1::2], line_tokens[2::2]) if float(x[1]) == 0.0} # HACK if clause see below's hack
        else:
            print(f"ERROR: unsupported method {method}")
            continue
        if method == "lutout" or method == "fdreout" or method == "lutin":
            net_locs[line_tokens[2]] = line_tokens[4]
    
    # first go through all input luts
    for slicerow, lut in luts.items():
        name = None
        loc, bel = slicerow.split("/")
        if len(lut) > 1:
            pins = []
            for pin, data in lut.items():
                if not name:
                    name = data[0]
                pins.append(f"   .{pin}({data[1]})")
            pins_str = ",\n".join(pins)
            verilog_file.write(f"""(* DONT_TOUCH = "yes" *) LUT6_2 #(
.INIT(64'h0000000000000000)
) {name} (
{pins_str}
);

""")
            bel += "6"
        else:
            pin = list(lut.keys())[0]
            name = lut[pin][0]
            verilog_file.write(f"""(* DONT_TOUCH = "yes" *) LUT{pin[1]} #(
.INIT(64'h0000000000000000)
) {name} (
    .O({lut[pin][1]})
);

""")
            bel += pin[1]
        xdc_file.write(f"""set_property BEL {bel}LUT [get_cells "{name}"];
set_property LOC {loc} [get_cells "{name}"];
set_property IS_LOC_FIXED yes [get_cells "{name}"];
set_property IS_BEL_FIXED yes [get_cells "{name}"];

""")

    # now go through all buffered luts
    for lut in buffered_luts:
        pin_defs = ",\n   ".join(f"   .{pin[0]}({pin[2]})" for pin in lut["pins"])
        verilog_file.write(f"""(* DONT_TOUCH = "yes" *) {lut["lut_type"]} #(
   .INIT(64'h0000000000000000)
) {lut["id"]} (
   {pin_defs}
);

""")
        pin_constraints = " ".join(f"{pin[0]}:{pin[1]}" for pin in lut["pins"]) # format: "I0:A0" or "{I0:A0 I1:A1}" ...
        if len(lut["pins"]) > 1:
            pin_constraints = f"{{{pin_constraints}}}"
        xdc_file.write(f"""set_property BEL {lut["bel"]} [get_cells "{lut["id"]}"];
set_property LOC {lut["loc"]} [get_cells "{lut["id"]}"];
set_property LOCK_PINS {pin_constraints} [get_cells "{lut["id"]}"];
set_property IS_LOC_FIXED yes [get_cells "{lut["id"]}"];
set_property IS_BEL_FIXED yes [get_cells "{lut["id"]}"];

""")

    if input_design_file:
        # HACK first sort out slices of clbs where not both slices are free
        # HACK: for our crappy cleanup script, we require fully free CLBs (both slices!!!)
        # so slice_score is required to be 0.0 here and also for the slice above/below
        print("sort out the slices...")
        global new_empty_slices
        new_empty_slices = []
        for empty_slicepart in empty_slices:
            x, y = (int(x) for x in RE_SLICE_COORDS.match(empty_slicepart).groups())
            otherx = (x // 2) * 2 + (1 - x % 2)
            if f"SLICE_X{otherx}Y{y}/A" in empty_slices:
                # add to the new list, as we got fully free slices
                new_empty_slices.append(empty_slicepart)
        print("sort out the slices done...")


        # now go through all mod cells, also check if they require a clock signal
        # a trick here is to route FFs first, thus we sort by alphabet (FF < LUT)
        ff_signal_slices = {}
        for line in sorted(line.strip() for line in open(input_design_file) if line.strip()):
            line_tokens = line.split(" ")

            # we get entries like "FDRE ff_test OUT Q SLICE_X67Y153/AFF/Q ffout IN C SLICE_X67Y153/AFF/CK clkin"
            # first get the slices, nets of pins in this cell connect to
            # here we need to evaluate all the nets the cell is connected to and see where the respective slices they connect to are.
            # that could be other already placed cells, however to keep it simple we assume it is enough to take the i_/o_ cells we set above into consideration.
            # TODO: handle CARRY4
            # TODO: handle LUT5_6 combos (consisting of two LUTs (but not both are LUT6) placed in the same slicerow, sharing some of their inputs, having at most 1 differing input)
            connected_slices = []
            for pin in [line_tokens[i:i+4] for i in range(2, len(line_tokens), 4)]:
                if pin[3] in clock_signals:
                    # TODO handle CLKs!
                    print(f"-> there is a clock signal {pin[3]} getting routed to {pin[2]}")
                    # HACK: this will easily be used for the only flip flop we got clock for
                    #center_slice = pin[2].split("/")[0]
                    continue
                if line_tokens[0] in FF_TYPES:
                    # FF special care
                    if pin[0] == "IN" and pin[1] == "D":
                        ff_in_signal = pin[3]
                elif line_tokens[0].startswith("LUT"):
                    # LUT special care
                    if pin[0] == "OUT" and pin[1] == "O":
                        lut_out_signal = pin[3]
                # evaluate the net
                if pin[3] in net_locs:
                    print(f"place {line_tokens[1]} cell near {net_locs[pin[3]]}")
                    connected_slices.append(net_locs[pin[3]])
            if not connected_slices:
                # TODO: implement a better approach not requiring additional information
                # probably something like route add this cell again to the end of the queue and route all the others first, so the others nets positions can get estimated
                connected_slices.append(center_slice)

            if line_tokens[0] in FF_TYPES or line_tokens[0].startswith("LUT"):
                # other kinds cannot be placed right now
                if line_tokens[0].startswith("LUT") and lut_out_signal in ff_signal_slices:
                    # lucky! we found a LUT that is in front of a FF, take the same row (can be only one, as a FF is supplied only by one signal)
                    min_slicepart = ff_signal_slices[lut_out_signal]
                    min_score = 0.0
                else:
                    # now calculate the score of all empty slices
                    min_score = math.inf
                    min_slicepart = None
                    for empty_slicepart in new_empty_slices:
                        # the score will simply be the mean average over all distance scores we get by considering the connected slices we evaluated above
                        score_count = 0
                        score = 0
                        score_accs = []
                        for slice in connected_slices:
                            score_acc = slice_distance_score(slice, empty_slicepart) #+ ((max(0, slice_score - 0.75)) / 0.25 * 10 if slice_score < 1.0 else math.inf)
                            score_accs.append(score_acc)
                            score += score_acc
                            score_count += 1
                        score /= score_count

                        if score < min_score:
                            min_score = score
                            min_slicepart = empty_slicepart
                            #print(f" -> slice: {empty_slicepart} score += {score_acc} ({score_accs})")
                    del new_empty_slices[new_empty_slices.index(min_slicepart)]
                print(f" -> slice: {min_slicepart} score = {min_score}")

                # add constraint for placement of this cell
                slice, part = min_slicepart.split("/")
                # LUT6 -> 6LUT, LUT5 -> 5LUT, F* -> FF
                if line_tokens[0] in FF_TYPES:
                    bel = f"{part}FF"
                    ff_signal_slices[ff_in_signal] = min_slicepart
                elif line_tokens[0].startswith("LUT"):
                    bel = f"{part}6LUT" #6 equals {line_tokens[0][3]}
                xdc_file.write(f"""set_property BEL {bel} [get_cells "{line_tokens[1]}"];
set_property LOC {slice} [get_cells "{line_tokens[1]}"];
set_property IS_LOC_FIXED yes [get_cells "{line_tokens[1]}"];
set_property IS_BEL_FIXED yes [get_cells "{line_tokens[1]}"];

""")
            else:
                print(f"ERROR: unsupported cell type {line_tokens[0]}, handle {line_tokens[1]} yourself.")
    
    verilog_file.close()
    xdc_file.close()
    print("done.")

if __name__ == '__main__':
    if (len(sys.argv) == 4 or (len(sys.argv) == 6 and os.path.isfile(sys.argv[4]))) and os.path.isfile(sys.argv[1]):
        generate_dummies_and_constraints(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None, sys.argv[5] if len(sys.argv) > 5 else None)
    else:
        print(__doc__)
        sys.exit(1)
