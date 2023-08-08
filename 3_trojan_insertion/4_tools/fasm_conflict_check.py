#!/usr/bin/env python3
"""Usage: fasm_conflict_check.py destination.fasm source.fasm

Checks whether any elements in source.fasm will have collisions with the
"don't touch" design inside destination.fasm
"""
import sys
from fasm_canonicalize import fasm_canonicalize_line

"""from anytree import Node, RenderTree
from anytree.search import findall, findall_by_attr

def parse_fasm(fasm):
    root = {}
    for entry in fasm:
        stripped = entry.strip()
        if not stripped:
            continue
        parts = stripped.split('.')
        parent = root
        for part in parts:
            for node in parent.descendants:
                if node.name == part:
                    parent = node
                    break
            else:
                node = Node(part, parent=parent)
                parent = node
    return root

def fasm_compare(dest, src):
    for node in findall(src, maxlevel=2):
        node_in_dest = findall_by_attr(dest, node.name, maxlevel=2)
        if node_in_dest:
            node_in_dest = node_in_dest[0]
            print(node, "found, but does it have matching children?")
            for node_child in findall(node, maxlevel=2):
                node_child_in_dest = findall_by_attr(node_in_dest, node_child.name, maxlevel=2)
                if node_child_in_dest:
                    print("  YES, conflicting nodes src:",node_child,"dest:",node_child_in_dest)
"""

def parse_fasm(fasm):
    return [line.strip().split('.', 2) for line in fasm if line.strip()]

#TODO automatically remove the pseudo "input" gates here (i_0 - i_8)
DISABLED_GATES = []
"""
    ['i_0', 'SLICEX140Y94',  'AFF',      'CLBLM_R_X89Y94', 'SLICE'], #M_X0
    ['i_1', 'SLICEX137Y94',  'AFF',      'CLBLM_L_X86Y94', 'SLICE'], #L_X1
    ['i_2', 'SLICEX147Y85',  'AFF',      'CLBLM_R_X93Y85', 'SLICE'], #L_X1
    ['i_3', 'SLICEX146Y84',  'B5FF',     'CLBLM_R_X93Y84', 'SLICE'], #M_X0
    #['i_4', 'SLICEX147Y85',  'BFF',      'CLBLM_R_X93Y85', 'SLICEL_X1'],
    #['i_5', 'SLICEX147Y85',  'CFF',      'CLBLM_R_X93Y85', 'SLICEL_X1'],
    ['i_6', 'SLICEX138Y92',  'BFF',      'CLBLL_R_X87Y92', 'SLICE'], #M_X0
    ['i_7', 'SLICEX141Y92',  'AFF',      'CLBLM_R_X89Y92', 'SLICE'], #L_X1
    #['i_7', '',              '',         'INT_R_X89Y92',   ''], # manually resolved
    ['i_8', 'BUFGCTRL_X0Y4', 'BUFGCTRL', 'CLK_BUFG_BOT_R_X139Y152', ''], # manually resolved
    ['',    '',              '',         'LIOB33_X0Y143',  'IOB_Y0'],
    ['',    '',              '',         'LIOB33_X0Y143',  'IOB_Y1']
]"""
DISABLED_TILES = [".".join(x) for x in zip(*list(zip(*DISABLED_GATES))[3:5])]
DONTSHOW_TILES = [] #"CLBLM_L_X30Y247", "CLK_BUFG_REBUF_X139Y142", "CLK_BUFG_REBUF_X139Y169", 'CLK_HROW_TOP_R_X139Y234'] # all reviewed

def fasm_compare(dest, src):
    for entry in src:
        tile = ".".join(entry[:2])
        if any(tile.startswith(x) for x in DISABLED_TILES):
            prefix = "D"
            continue # no need to check, will remove anyway
        elif any(entry[0] == x for x in DONTSHOW_TILES):
            prefix = "X"
            continue # hide as already reviewed and OK
        elif tile.startswith("INT_"):
            continue # handle INTs seperately
        else:
            prefix = ""
        entryFound = False
        mismatch = []
        for entry_dest in dest:
            if entry_dest[:2] == entry[:2]:
                #if (len(entry_dest) <= 2 and len(entry) <= 2) or entry_dest[2] == entry[2]:
                #    break
                if len(entry_dest) <= 2:
                    mismatch.append("")
                else:
                    mismatch.append(entry_dest[2])
                entryFound = True
            elif entry_dest[0] != entry[0] and entryFound:
                # after a block of a specific tile, the tile usually does not appear anymore in the fasm
                break
        if mismatch:
            print(prefix + "B: Conflicting nodes src:",entry,"dest:",mismatch)

def fasm_diff(f1, f2):
    s1 = set()
    for l1 in f1:
        s1 |= set(fasm_canonicalize_line(l1))
    s2 = set()
    for l2 in f2:
        s2 |= set(fasm_canonicalize_line(l2))
    r = set()
    # in 1 but not in 2
    #for x in s1 - s2:
    #    r.add((x, '-'))
    # in 2 but not in 1
    for x in s2 & s1:
        r.add((x, '&'))
    for x in s2 - s1:
        if any(x.split(".",1)[0] == y.split(".",1)[0] for y, _ in r):
            r.add((x, '+'))
    for x in sorted(r):
        if not x[0].split(".",1)[0] in DONTSHOW_TILES and not any(x[0].startswith(y) for y in DISABLED_TILES):
            print(x[1], x[0])

def fasm_collisions(f1, f2):
    # parse source file first
    src_zero = {}
    src_one = {}
    for line in f2:
        if line.startswith("INT_"):
            if line.strip().endswith("= 0"):
                parts = line.split("=", 1)[0].strip().split(".")
                key = '.'.join(parts[:2])
                value = parts[2]
                if key in src_one and src_one[key] == value:
                    print("{}.{} is set to 1 and 0 at the same time in the source".format(key, value))
                elif key in src_zero:
                    print("{}.{} has a duplicate in src_zero ({})".format(key, value, src_zero[key]))
                src_zero[key] = value
            else:
                parts = line.strip().split(".")
                key = '.'.join(parts[:2])
                value = parts[2]
                if key in src_zero and src_zero[key] == value:
                    print("{}.{} is set to 1 and 0 at the same time in the source".format(key, value))
                elif key in src_one:
                    print("{}.{} has a duplicate in src_one ({})".format(key, value, src_one[key]))
                src_one[key] = value
    dest_one = {}
    for line in f1:
        if line.startswith("INT_"):
            parts = line.strip().split(".")
            key = '.'.join(parts[:2])
            value = parts[2]
            if key in dest_one:
                print("{}.{} has a duplicate in dest_one ({})".format(key, value, dest_one[key]))
            if key in src_zero and src_zero[key] == value:
                # do not add to dict, as we remove this one
                pass
            else:
                dest_one[key] = value
    for key, value in dest_one.items():
        if key in src_one:
            if src_one[key] != value:
                print("{}.{} in dest would collide with the signal from {} in source".format(key, value, src_one[key]))

if __name__ == '__main__':
    if len(sys.argv) == 3:
        fasm_destination = parse_fasm(list(open(sys.argv[1])))
        fasm_source = parse_fasm(list(open(sys.argv[2])))
    else:
        print(__doc__)
        sys.exit(1)
    print("== 1st Method: find diverse features including direct and indirect collisions ==")
    fasm_compare(fasm_destination, fasm_source)
    print("== 2nd Method; completely parse all features to find direct collisions and alternatives ==")
    fasm_diff(open(sys.argv[1]), open(sys.argv[2]))
    print("== 3rd Method; take destination and check if non-zeroed-out PIPs collide with those in source (two source detection) ==")
    fasm_collisions(open(sys.argv[1]), open(sys.argv[2]))