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

def pins(line_tokens):
    return [line_tokens[i:i+4] for i in range(2, len(line_tokens), 4)]

def find_cell_by_net(cells, net, direction=None, pinname=None, cellfilter=None):
    for i, line_tokens in enumerate(cells):
        if cellfilter is None or line_tokens[0] in cellfilter:
            for pin in pins(line_tokens):
                if (direction is None or pin[0] == direction) and (pinname is None or pin[1] == pinname):
                    if pin[3] == net:
                        return i, line_tokens, pin
    return None, None, None

def get_connected_slices(line_tokens, net_locs, clock_signals):
    connected_slices = []
    ff_in_signal = None
    lut_out_signal = None
    for pin in pins(line_tokens):
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
    return connected_slices, ff_in_signal, lut_out_signal

# algo is as follows:
# - go through inputs/outputs
#   - remember all input luts (i_*)
#   - place input ffs (i_*) at respective locations
#   - place output ffs (o_*) at respective locations
#   - remember all output luts (o_*) in buffered_luts, also completing all I* pins from other outputs in the same lut
#   - place input clocks (i_*) at respective locations
#   - remember empty slices
#   - with input ffs, and input / output luts, remember used SLICE as net_locs
# - place input luts combined with all pins as remembered
# - place output luts (buffered_luts) combined with all pins as remembered
# - place the input design file

def generate_dummies_and_constraints(input_target_file, output_verilog, output_xdc, input_design_file, center_slice):
    verilog_file = open(output_verilog, "w")
    xdc_file = open(output_xdc, "w")

    fixed_output = []

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
            # TODO: what if a LUT is output / input at the same time? (usually doesn't happen)
            slicerow = f"{line_tokens[4]}/{line_tokens[3][7]}"
            if slicerow not in luts:
                luts[slicerow] = {}
            luts[slicerow][line_tokens[5]] = (line_tokens[1], line_tokens[2])
        elif method == "fdreout":
            bel = line_tokens[3].split(".")[1]
            fixed_output.append({
                "type": "FDRE",
                "properties": {"INIT": "1'b0"},
                "name": line_tokens[1],
                "pins": {"Q": line_tokens[2]},
                "loc": line_tokens[4],
                "bel": bel
            })
        elif method == "fdrein":
            bel = line_tokens[3].split(".")[1]
            fixed_output.append({
                "type": "FDRE",
                "properties": {"INIT": "1'b0"},
                "name": line_tokens[1],
                "pins": {"D": line_tokens[2]},
                "loc": line_tokens[4],
                "bel": bel
            })
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
            else:
                buffered_luts.append(this_lut)
        elif method == "bufgctrlout":
            clock_signals[line_tokens[2]] = line_tokens[4:]
            fixed_output.append({
                "type": "BUFGCTRL",
                "properties": {
                    "INIT_OUT": "0",
                    "PRESELECT_I0": '"FALSE"',
                    "PRESELECT_I1": '"FALSE"',
                    "SIM_DEVICE": '"7SERIES"'
                },
                "name": line_tokens[1],
                "pins": {"O": line_tokens[2]},
                "loc": line_tokens[3],
                "bel": "BUFGCTRL"
            })
        elif method == "emptysliceparts":
            empty_slices |= {x[0]: float(x[1]) for x in zip(line_tokens[1::2], line_tokens[2::2]) if float(x[1]) == 0.0} # HACK if clause see below's hack
        else:
            print(f"ERROR: unsupported method {method}")
            continue
        if method == "lutout" or method == "fdreout" or method == "lutin":
            net_locs[line_tokens[2]] = line_tokens[4]
    
    # first go through all input luts
    for slicerow, lut in luts.items():
        loc, bel = slicerow.split("/")
        if len(lut) > 1:
            pindict = {}
            name = None
            for pin, data in lut.items():
                if not name:
                    name = data[0]
                pindict[pin] = data[1]
            bel += "6"
            fixed_output.append({
                "type": "LUT6_2",
                "properties": {"INIT": "64'h0000000000000000"},
                "name": name,
                "pins": pindict,
                "loc": loc,
                "bel": bel
            })
        else:
            pin = list(lut.keys())[0]
            bel += pin[1] + "LUT"
            fixed_output.append({
                "type": f"LUT{pin[1]}",
                "properties": {"INIT": "64'h0000000000000000"},
                "name": lut[pin][0],
                "pins": {"O": lut[pin][1]},
                "loc": loc,
                "bel": bel
            })

    # now go through all buffered luts
    for lut in buffered_luts:
        fixed_output.append({
            "type": lut["lut_type"],
            "properties": {"INIT": "64'h0000000000000000"},
            "name": lut["id"],
            "pins": {pin[0]: pin[2] for pin in lut["pins"]},
            "loc": lut["loc"],
            "bel": lut["bel"],
            "lock_pins": {pin[0]: pin[1] for pin in lut["pins"]}
        })

    if input_design_file:
        # HACK first sort out slices of clbs where not both slices are free, as during bitstream merging it wouldn't work otherwise
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

        # #### Place new cells ####

        # placement is as follows
        # - All placement takes place in only fully empty slices, as later it is only possible to merge when the slice was empty
        # 1. (optional: place other constrained BELs, like inputs / outputs (?))
        # 2. for each MUXF8, place MUXF8 in empty slice and the two MUXF7 in front there aswell
        # 3. for each MUXF7, place them in a vacant half-slice
        # 4. for each FF, check whether input matches to already placed output, if yes, place there, if no, place at vacant slicerow
        # 5. for each LUT, check whether output matches to already placed inputs, if yes, place there, if no, place at vacant slicerow

        # TODO: handle CARRY4 (evaluate the whole carry chain and find as many slices in a column as necessary)
        # TODO: handle LUT5_6 combos (consisting of two LUTs (but not both are LUT6) placed in the same slicerow, sharing some of their inputs, having at most 1 differing input)

        # read the full file first as we need roughly this order
        # MUXF8, MUXF7, (CARRY4), FF_TYPES, LUT1,2,3,4,5,6
        design_lines = [line.strip().split(" ") for line in open(input_design_file) if line.strip()]

        # group lines by type
        all_muxf8 = []
        all_muxf7 = []
        global all_others
        all_others = []
        for line_tokens in design_lines:
            if line_tokens[0] == "MUXF8":
                all_muxf8.append(line_tokens)
            elif line_tokens[0] == "MUXF7":
                all_muxf7.append(line_tokens)
            else:
                all_others.append(line_tokens)
        
        # start with MUXF8, evaluate the whole tree and block a slice for all elements
        for line_tokens in all_muxf8:
            print(f"place {line_tokens[1]}, evaluate...")
            connected_slices, _, _ = get_connected_slices(line_tokens, net_locs, clock_signals)
            for pin in pins(line_tokens):
                # OUT O: check if there are FFs that have this net as IN D, place it in the same SLICE as BFF
                # IN I0: find the MUXF7 that has this net as OUT O, place it in the same SLICE as F7BMUX
                #   OUT O: check if there are FFs that have this net as IN D, place it in the same SLICE as CFF
                #   IN I0: find the LUTn that has this net as OUT O, place it in the same SLICE as DnLUT
                #   IN I1: find the LUTn that has this net as OUT O, place it in the same SLICE as CnLUT
                # IN I1: find the MUXF7 that has this net as OUT O, place it in the same SLICE as F7AMUX
                #   OUT O: check if there are FFs that have this net as IN D, place it in the same SLICE as AFF
                #   IN I0: find the LUTn that has this net as OUT O, place it in the same SLICE as BnLUT
                #   IN I1: find the LUTn that has this net as OUT O, place it in the same SLICE as AnLUT
                print(pin)
                if pin[:2] == ["OUT", "O"]:
                    i, ffb, _ = find_cell_by_net(all_others, pin[3], "IN", "D", FF_TYPES)
                    if ffb is not None:
                        print("FOUND BFF that connects to the MUXF8! It is "+ffb[1])
                        connected_slices += get_connected_slices(ffb, net_locs, clock_signals)[0]
                elif pin[:2] == ["IN", "I0"]:
                    i, f7bmux, _ = find_cell_by_net(all_muxf7, pin[3], "OUT", "O")
                    if f7bmux is not None:
                        print("FOUND F7BMUX that connects to the MUXF8 (I0 part)! It is "+f7bmux[1])
                        connected_slices += get_connected_slices(f7bmux, net_locs, clock_signals)[0]
                        for f7bmux_pin in pins(f7bmux):
                            if f7bmux_pin[:2] == ["OUT", "O"]:
                                i, ffc, _ = find_cell_by_net(all_others, f7bmux_pin[3], "IN", "D", FF_TYPES)
                                if ffc is not None:
                                    print("FOUND CFF that connects to the MUXF7! It is "+ffc[1])
                                    connected_slices += get_connected_slices(ffc, net_locs, clock_signals)[0]
                            if f7bmux_pin[:2] == ["IN", "I0"]:
                                i, lutd, _ = find_cell_by_net(all_others, f7bmux_pin[3], "OUT", "O")
                                if lutd is not None:
                                    print("FOUND DLUT that connects to the MUXF7! It is "+lutd[1])
                                    connected_slices += get_connected_slices(lutd, net_locs, clock_signals)[0]
                            if f7bmux_pin[:2] == ["IN", "I1"]:
                                i, lutc, _ = find_cell_by_net(all_others, f7bmux_pin[3], "OUT", "O")
                                if lutc is not None:
                                    print("FOUND CLUT that connects to the MUXF7! It is "+lutc[1])
                                    connected_slices += get_connected_slices(lutc, net_locs, clock_signals)[0]
                elif pin[:2] == ["IN", "I1"]:
                    i, f7amux, _ = find_cell_by_net(all_muxf7, pin[3], "OUT", "O")
                    if f7amux is not None:
                        print("FOUND F7AMUX that connects to the MUXF8 (I1 part)! It is "+f7amux[1])
                        connected_slices += get_connected_slices(f7amux, net_locs, clock_signals)[0]
                        for f7amux_pin in pins(f7amux):
                            if f7amux_pin[:2] == ["OUT", "O"]:
                                i, ffa, _ = find_cell_by_net(all_others, f7amux_pin[3], "IN", "D", FF_TYPES)
                                if ffa is not None:
                                    print("FOUND AFF that connects to the MUXF7! It is "+ffa[1])
                                    connected_slices += get_connected_slices(ffa, net_locs, clock_signals)[0]
                            if f7amux_pin[:2] == ["IN", "I0"]:
                                i, lutb, _ = find_cell_by_net(all_others, f7amux_pin[3], "OUT", "O")
                                if lutb is not None:
                                    print("FOUND BLUT that connects to the MUXF7! It is "+lutb[1])
                                    connected_slices += get_connected_slices(lutb, net_locs, clock_signals)[0]
                            if f7amux_pin[:2] == ["IN", "I1"]:
                                i, luta, _ = find_cell_by_net(all_others, f7amux_pin[3], "OUT", "O")
                                if luta is not None:
                                    print("FOUND ALUT that connects to the MUXF7! It is "+luta[1])
                                    connected_slices += get_connected_slices(luta, net_locs, clock_signals)[0]
            if not connected_slices:
                # TODO: implement a better approach not requiring additional information
                # probably something like route add this cell again to the end of the queue and route all the others first, so the others nets positions can get estimated
                connected_slices.append(center_slice)
            # now calculate the score of all empty slices
            min_score = math.inf
            min_slicepart = None
            for empty_slicepart in new_empty_slices:
                # omit the check for whole empty slices here, as there are only completely empty slices currently used
                # in case the MUXF8 placement will take place at a later stage, we have to ensure that A-D are empty!

                # the score will simply be the mean average over all distance scores we get by considering the connected slices we evaluated above
                score_count = 0
                score = 0
                score_accs = []
                for slice in connected_slices:
                    score_acc = slice_distance_score(slice, empty_slicepart)
                    score_accs.append(score_acc)
                    score += score_acc
                    score_count += 1
                score /= score_count

                if score < min_score:
                    min_score = score
                    min_slicepart = empty_slicepart
            # luckily we can easily take min_slicepart and remove A-D
            slice = min_slicepart.split("/")[0]
            new_empty_slices.remove(slice+"/A")
            new_empty_slices.remove(slice+"/B")
            new_empty_slices.remove(slice+"/C")
            new_empty_slices.remove(slice+"/D")
            print(f" -> slice: {slice} score = {min_score}")
            
            # now place all the elements in min_slice A-D resp.
            fixed_output.append({
                "name": luta[1],
                "loc": slice,
                "bel": "A6LUT",
            })
            all_others.remove(luta)
            fixed_output.append({
                "name": lutb[1],
                "loc": slice,
                "bel": "B6LUT",
            })
            all_others.remove(lutb)
            fixed_output.append({
                "name": lutc[1],
                "loc": slice,
                "bel": "C6LUT",
            })
            all_others.remove(lutc)
            fixed_output.append({
                "name": lutd[1],
                "loc": slice,
                "bel": "D6LUT",
            })
            all_others.remove(lutd)
            if ffa:
                fixed_output.append({
                    "name": ffa[1],
                    "loc": slice,
                    "bel": "AFF",
                })
                all_others.remove(ffa)
            if ffb:
                fixed_output.append({
                    "name": ffb[1],
                    "loc": slice,
                    "bel": "BFF",
                })
                all_others.remove(ffb)
            if ffc:
                fixed_output.append({
                    "name": ffc[1],
                    "loc": slice,
                    "bel": "CFF",
                })
                all_others.remove(ffc)
            fixed_output.append({
                "name": f7amux[1],
                "loc": slice,
                "bel": "F7AMUX",
            })
            all_muxf7.remove(f7amux)
            fixed_output.append({
                "name": f7bmux[1],
                "loc": slice,
                "bel": "F7BMUX",
            })
            all_muxf7.remove(f7bmux)
            fixed_output.append({
                "name": line_tokens[1],
                "loc": slice,
                "bel": "F8MUX",
            })

        # similarly place MUXF7, block half a slice for all elements
        for line_tokens in all_muxf7:
            print(f"place {line_tokens[1]}, evaluate...")
            connected_slices, _, _ = get_connected_slices(line_tokens, net_locs, clock_signals)
            for pin in pins(line_tokens):
                # OUT O: check if there are FFs that have this net as IN D, place it in the same SLICE as C/AFF
                # IN I0: find the LUTn that has this net as OUT O, place it in the same SLICE as D/BnLUT
                # IN I1: find the LUTn that has this net as OUT O, place it in the same SLICE as C/AnLUT
                print(pin)
                if pin[:2] == ["OUT", "O"]:
                    i, ffca, _ = find_cell_by_net(all_others, pin[3], "IN", "D", FF_TYPES)
                    if ffca is not None:
                        print("FOUND C/AFF that connects to the MUXF7! It is "+ffca[1])
                        connected_slices += get_connected_slices(ffca, net_locs, clock_signals)[0]
                if pin[:2] == ["IN", "I0"]:
                    i, lutdb, _ = find_cell_by_net(all_others, pin[3], "OUT", "O")
                    if lutdb is not None:
                        print("FOUND D/BLUT that connects to the MUXF7! It is "+lutdb[1])
                        connected_slices += get_connected_slices(lutdb, net_locs, clock_signals)[0]
                if pin[:2] == ["IN", "I1"]:
                    i, lutca, _ = find_cell_by_net(all_others, pin[3], "OUT", "O")
                    if lutca is not None:
                        print("FOUND C/ALUT that connects to the MUXF7! It is "+lutca[1])
                        connected_slices += get_connected_slices(lutca, net_locs, clock_signals)[0]
            if not connected_slices:
                # TODO: implement a better approach not requiring additional information
                # probably something like route add this cell again to the end of the queue and route all the others first, so the others nets positions can get estimated
                connected_slices.append(center_slice)
            # now calculate the score of all empty slices
            min_score = math.inf
            min_slicepart = None
            for empty_slicepart in new_empty_slices:
                # omit the check for half empty slices here, as there are only completely empty slices currently used (MUXF8 placement did take whole slices)
                # in case the MUXF7/F8 placement will take place at a later stage, we have to ensure that the siblings AB or CD are empty!
                ## first check that the sibling of the half of the slice is still free
                #empty_slice, part = empty_slicepart.split("/")
                #if not empty_slice + "/" + chr(ord(part)+1+2*(ord(part)%2-1)) in new_empty_slices:
                #    # if not, skip this, we need either A and B or C and D here
                #    continue

                # the score will simply be the mean average over all distance scores we get by considering the connected slices we evaluated above
                score_count = 0
                score = 0
                score_accs = []
                for slice in connected_slices:
                    score_acc = slice_distance_score(slice, empty_slicepart)
                    score_accs.append(score_acc)
                    score += score_acc
                    score_count += 1
                score /= score_count

                if score < min_score:
                    min_score = score
                    min_slicepart = empty_slicepart
            # now we have one of A+B or C+D
            min_slice, min_part = min_slicepart.split("/")
            if min_part in ("A", "B"):
                new_empty_slices.remove(min_slice+"/A")
                new_empty_slices.remove(min_slice+"/B")
                half = "AB"
                bel = "F7AMUX"
            elif min_part in ("C", "D"):
                new_empty_slices.remove(min_slice+"/C")
                new_empty_slices.remove(min_slice+"/D")
                half = "CD"
                bel = "F7BMUX"
            print(f" -> slice: {min_slice}/{half} score = {min_score}")
            
            # now place all the elements in the half of min_slice resp.
            fixed_output.append({
                "name": lutca[1],
                "loc": min_slice,
                "bel": half[0]+"6LUT",
            })
            all_others.remove(lutca)
            fixed_output.append({
                "name": lutdb[1],
                "loc": min_slice,
                "bel": half[1]+"6LUT",
            })
            all_others.remove(lutdb)
            if ffca:
                fixed_output.append({
                    "name": ffca[1],
                    "loc": min_slice,
                    "bel": half[0]+"FF",
                })
                all_others.remove(ffca)
            fixed_output.append({
                "name": line_tokens[1],
                "loc": min_slice,
                "bel": bel,
            })

        # now go through all other mod cells, also check if they require a clock signal
        # a trick here is to route FFs first, thus we sort by alphabet (FF < LUT)
        ff_signal_slices = {}
        for line_tokens in sorted(all_others):

            # we get entries like "FDRE ff_test OUT Q SLICE_X67Y153/AFF/Q ffout IN C SLICE_X67Y153/AFF/CK clkin"
            # first get the slices, nets of pins in this cell connect to
            # here we need to evaluate all the nets the cell is connected to and see where the respective slices they connect to are.
            # that could be other already placed cells, however to keep it simple we assume it is enough to take the i_/o_ cells we set above into consideration.
            connected_slices, ff_in_signal, lut_out_signal = get_connected_slices(line_tokens, net_locs, clock_signals)
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
                fixed_output.append({
                    "name": line_tokens[1],
                    "loc": slice,
                    "bel": bel,
                })
            else:
                print(f"ERROR: unsupported cell type {line_tokens[0]}, handle {line_tokens[1]} yourself.")

    for x in fixed_output:
        if "type" in x and "properties" in x and "pins" in x:
            verilog = f"""(* DONT_TOUCH = "yes" *) {x["type"]} #(\n"""
            verilog += ",\n".join([f"   .{key}({value})" for key, value in x["properties"].items()])
            verilog += f"""\n) {x["name"]} (\n"""
            verilog += ",\n".join([f"    .{key}({value})" for key, value in x["pins"].items()])
            verilog += "\n);\n\n"
            verilog_file.write(verilog)
        xdc = f"""set_property BEL {x["bel"]} [get_cells "{x["name"]}"];
set_property LOC {x["loc"]} [get_cells "{x["name"]}"];\n"""
        if "lock_pins" in x:
            pin_constraints = " ".join(f"{key}:{value}" for key, value in x["lock_pins"].items()) # format: "I0:A0" or "{I0:A0 I1:A1}" ...
            if len(x["lock_pins"]) > 1:
                pin_constraints = f"{{{pin_constraints}}}"
            xdc += f"""set_property LOCK_PINS {pin_constraints} [get_cells "{x["name"]}"];\n"""
        xdc += f"""set_property IS_LOC_FIXED yes [get_cells "{x["name"]}"];
set_property IS_BEL_FIXED yes [get_cells "{x["name"]}"];\n\n"""
        xdc_file.write(xdc)

    verilog_file.close()
    xdc_file.close()
    print("done.")

if __name__ == '__main__':
    if (len(sys.argv) == 4 or (len(sys.argv) == 6 and os.path.isfile(sys.argv[4]))) and os.path.isfile(sys.argv[1]):
        generate_dummies_and_constraints(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None, sys.argv[5] if len(sys.argv) > 5 else None)
    else:
        print(__doc__)
        sys.exit(1)
