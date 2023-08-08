#!/usr/bin/env python3
"""Usage: rapidwright reroute_fasm_base_to_mod.py unrouted.dcp
       base.fasm output.dcp output2.fasm [netpriority.txt]

Loads unrouted.dcp into rapidwright, tries to route any unrouted nets inside
while restricting to free resources not used in the base.fasm (except for
special cases), leading to a design saved as output.dcp. Uses global signals
"i_" of unrouted.dcp as dummy input pins (remove related inputs from mod, as
already present in the target) and global signals "o_" of unrouted.dcp as
dummy output pins. These have to be connected only to one destination existing
in base.fasm. The respective nets will be found, unrouted (set the respective
bits to zero!) and then rerouted together with the new source. The zero-set
bits will be stored in output2.fasm. A fasm patch then consists out of
output2.fasm concatenated with output.dcp -> .bit -> .fasm, as output.dcp might
reuse zeroed-out bits again.

Howto:
1. Look for o_* elements
    1.1. unroll the net from this one target pip (leading to all destinations)
    1.2. remember all the destinations of this element, form a net out of them
         (source is the source of the o_* net)
    1.3. remove all the PIPs (unset! -> print out the "0" bits)
2. Route all the nets the same way as in "route_with_forbidden_pips_from_fasm"
3. generate a bitstream from the resulting dcp using vivado
4. take the resulting fasm and add the fasm of the bitstream
5. apply the fasm to the bitstream from which the base.fasm originates

BEWARE: The checkpoint loaded here should only include the top module
(= 1 VHDL file) because every submodule f***s RapidWright up.

BEWARE: Clock nets have to be routed manually beforehand and will not be
touched by this script in case they have "_CLK" in their names. Vice versa all
normal nets with "_CLK" in their names will be left untouched.
"""
import re
import math
import sys
from com.xilinx.rapidwright.design import Design
from com.xilinx.rapidwright.design import Net
from com.xilinx.rapidwright.design import NetType
from com.xilinx.rapidwright.design import Unisim
from com.xilinx.rapidwright.design.tools import LUTTools
from com.xilinx.rapidwright.device import IntentCode
from com.xilinx.rapidwright.device import PIP
from com.xilinx.rapidwright.router import RouteNode
from java.util import HashSet

def fasmFindPIPsAndSinksFromSource(sourceWire, fasmPIPDict, verbose=False):
    # now using a queue, find all PIPs that form this net downwards (DFS/BFS)
    # - note all of these PIPs in the FASM as "zeroed out" PIPs
    # - remove all of these PIPs from the fasmPIPDict
    # - note all of the sinks to form the new net / add to "net"
    q = set([sourceWire])
    qVisited = set()
    pips = set()
    sinks = set()
    while len(q):
        if verbose: print("q: {}".format(q))
        if verbose: print("qVisited: {}".format(qVisited))
        if len(q) > 100:
            raise Exception("ERROR! Queue length exceeded, exiting now.")
        wire = q.pop()
        qVisited.add(wire)
        if verbose: print("wire: {}".format(wire))
        routeNode = RouteNode(wire.getTile(), wire.getWireIndex())
        fasmPIPs = fasm_find_pip(fasmPIPDict, wire)
        for nextWire in routeNode.getConnections():
            if verbose: print("nextWire: {}".format(nextWire))
            if nextWire in qVisited:
                continue
            if re.match(r"^CLB.*_IMUX[0-9]+$", nextWire.getWireName()):
                sitePin = RouteNode(nextWire.getTile(), nextWire.getWireIndex()).getConnections()[0].getSitePin() #TODO evaluate if directly .getSitePin() now works
                print("Found a destination: {}, Pin: {}".format(nextWire, sitePin))
                sinks.add(sitePin)
            elif re.match(r"^CLB.*_[A-D]X$", nextWire.getWireName()):
                # the *X pins originate from PIPs that have only one source (e.g. BYP_L11), thus we need to decide here whether the FF is actually enabled to be able to call it a sink
                global nextWire_
                nextWire_ = nextWire
                slicerow = nextWire.getWireName()[-2]
                fasmtile = nextWire.getTile()
                m_l_slice = nextWire.getWireName()[6]
                xpos = str(nextWire.getSitePin().getSite().getInstanceX() % 2)
                fasmsink = "SLICE" + m_l_slice + "_X" + xpos
                fasmsrc = slicerow + "FFMUX." + slicerow + "X"
                if fasmtile in fasmPIPDict and fasmsrc in fasmPIPDict[fasmtile] and fasmsink in fasmPIPDict[fasmtile][fasmsrc]:
                    sitePin = nextWire.getSitePin()
                    print("Found a destination: {}, Pin: {}".format(nextWire, sitePin))
                    sinks.add(sitePin)
                else:
                    print("Discard destination: {} because of missing slice configuration".format(nextWire))

            else:
                for pip in fasmPIPs:
                    if pip.getEndWire() == nextWire or (pip.getStartWire() == nextWire and pip.isBidirectional()):
                        if verbose: print("add {} to queue because it is in the fasm".format(nextWire))
                        q.add(nextWire)
                        pips.add(pip)
                        break
                else:
                    if len(RouteNode(nextWire.getTile(), nextWire.getWireIndex()).getBackwardConnections()) == 1 and not re.match(r"^CLB.*_(?:[LM]|LL)_[A-D](?:MUX)?$", nextWire.getWireName()):
                        if verbose: print("add {} to queue because it has only one source".format(nextWire))
                        q.add(nextWire)
    return pips, sinks

def fasmFindPIPsAndSinksFromSinkPinInst(sitePinInst, fasmPIPDict, verbose=False):
    routeNode = sitePinInst.getRouteNode()
    backPIPs = routeNode.getBackwardPIPs()
    if len(backPIPs) > 1:
        print("Warning! This net has multiple sources, unusual for LUTs")
    pip = backPIPs[0]
    # traverse up to the net's source, there is only one
    while True:
        if verbose: print("pip: {}".format(pip))
        wire = pip.getStartWire()
        nextWire = None
        while True:
            if verbose: print("wire: {}".format(wire))
            nextWire = wire.getStartWire()
            if wire == nextWire:
                break
            wire = nextWire
        fasmPIPs = fasm_find_pip_reverse(fasmPIPDict, wire)
        if verbose: print("fasmPIPs: {}".format(fasmPIPs))
        if not fasmPIPs:
            fasmPIPs = wire.getBackwardPIPs()
            if verbose: print("fasmPIPs: {}".format(fasmPIPs))
            if "LOGIC_OUT" in wire.getWireName() or not fasmPIPs:
                # TODO check, if we need to take route throughs into consideration here, then we need to continue at LOGIC_OUTs
                print("Start found, we start at {}".format(wire))
                if fasmPIPs:
                    pip = fasmPIPs[0] #CHECK
                break
        if len(fasmPIPs) > 1:
            raise Exception("Warning! In sitePin {} found more than one source for PIP starting at wire {}, please review!\n{}".format(sitePinInst, wire, fasmPIPs))
        pip = fasmPIPs[0]
    return fasmFindPIPsAndSinksFromSource(pip.getEndWire(), fasmPIPDict, verbose)

def elaborateRerouteNets(design, fasmPIPDict, usedNodes, intraSiteRoutes):
    parent = design.getTopEDIFCell() #[cell for cell in design.getNetlist().getLibrary("work").getValidCellExportOrder() if cell.getName() != "top"][0] # FIXME this works only if the "trojan" or "logic analyzer" module is the first cell, design.getTopEDIFCell() doesn't work
    fasmOutput = ""
    #cellsToRemove = []
    cellsToCreate = []
    for cell in design.getCells():
        if not re.match(r"^o_[0-9]+(_lutmod_[0-9A-F]+)?(/LUT[56])?$", cell.getName()):
            print("Skipping " + cell.getName())
            continue
        verbose = False #(cell.getName() == "o_14" or cell.getName() == "o_19")
        outputPorts = []
        for portInst in cell.getEDIFCellInst().getPortInsts():
            if any(source.isPrimitiveStaticSource() for source in portInst.getNet().getSourcePortInsts(True)):
                continue
            outputPorts.append(portInst)
        if not outputPorts:
            print("Error! Cell {} has no net to be rerouted, ensure that other cells might not be called o_*".format(cell))
            continue
        for outputPort in outputPorts:
            edifNet = outputPort.getNet()
            net = design.getNet(edifNet.getName())
            if not net:
                for portInst in edifNet.getPortInsts():
                    if portInst.isOutput():
                        net = design.getNet(repr(portInst))
                        if net:
                            break
                else:
                    print("Error! EDIF Net {} not found in the design! Required later to reconnect logically".format(edifNet))
                    continue
            #net.setPIPs([])
            print("Elaborating net {} ({})...".format(edifNet.getName(), cell.getName()))
            print("New net source {}, sinks: {}".format(net.getSource(), net.getSinkPins()))
            initialSitePin = cell.getSitePinFromPortInst(outputPort, [])
            pipsToRemove, sinks = fasmFindPIPsAndSinksFromSinkPinInst(initialSitePin, fasmPIPDict, verbose)
            for sitePin in sinks:
                #if sitePin.getSite() == initialSitePin.getSite() and sitePin.getPinName() == initialSitePin.getName():
                #    print("Skip pin {}, already in the net".format(sitePin))
                #else:
                if repr(sitePin).endswith("X"):
                    cellsToCreate.append(((cell.getName() + "_inferred_" + repr(sitePin).replace("/", "_"), Unisim.FDRE, sitePin.getSite(), sitePin.getSite().getBEL(repr(sitePin).split("/")[-1][:-1] + "FF")), net, sitePin.getPinName()))
                else:
                    cellsToCreate.append(((cell.getName() + "_inferred_" + repr(sitePin).replace("/", "_"), Unisim.LUT6, sitePin.getSite(), sitePin.getSite().getBEL(repr(sitePin).split("/")[-1][:-1] + "6LUT")), net, sitePin.getPinName()))

            for pip in pipsToRemove:
                # remove from fasmPIPDict and the usedNodes, to make the resources reusable
                tile = pip.getTile()
                fasmsrc = pip.getStartWireName()
                fasmsink = pip.getEndWireName()
                #if tile.getName() == "INT_R_X85Y85" and fasmsink == "GFAN1":
                #    print("### removing right here!!! (sink)")
                #if tile.getName() == "INT_R_X85Y85" and fasmsrc == "GFAN1":
                #    print("### removing right here!!! (src)")
                if fasmsrc in fasmPIPDict[tile]:
                    # zero out all of these PIPs, we want to reroute the whole net
                    fasmOutput += fasm_set_pip(pip, 0)
                    fasmPIPDict[tile][fasmsrc].remove(fasmsink)
                usedNodes.discard(RouteNode(tile, tile.getWireIndex(fasmsink)))
                usedNodes.discard(RouteNode(tile, tile.getWireIndex(fasmsrc)))
            #cellsToRemove.append((cell, net))
    # deleting and creating again is somehow unintuitively as it also leaves still some traces in the EDIF...
    #for cellToRemove, netFromCellToRemove in cellsToRemove:
    #    for sitePinInst in net.getPins():
    #        if sitePinInst.getSiteInst() == cellToRemove.getSiteInst():
    #            netFromCellToRemove.removePin(sitePinInst)
    #            break
    #    else:
    #        print("WARNING: net could not be disconnected")
    #    design.removeCell(cellToRemove)
    global cellsToCreate_
    cellsToCreate_ = cellsToCreate
    for cellToCreateArgs, cellToCreateNet, cellToCreatePinName in cellsToCreate:
        cellToCreateParent = cellToCreateNet.getLogicalNet().getParentCell()
        print("create cell {}, placed in site {} on bel {}, connected with net {} on pin {}".format(cellToCreateArgs[0], cellToCreateArgs[2], cellToCreateArgs[3], cellToCreateNet, cellToCreatePinName))
        isLUT = (cellToCreateArgs[1] != Unisim.FDRE)
        for designCell in design.getCells():
            if designCell.getSite() == cellToCreateArgs[2]:
                if designCell.getBEL() == cellToCreateArgs[3]:
                    print("cell already found, named {}, do not recreate".format(designCell.getName()))
                    cell = designCell
                    if isLUT:
                        lutEquation = LUTTools.getLUTEquation(cell)
                    break
                elif isLUT:
                    # if we have a LUT6, is there a LUT5 aswell or other way around?
                    belName = designCell.getBEL().getName()
                    if belName[0] == cellToCreateArgs[3].getName()[0] and \
                       belName[2:] == cellToCreateArgs[3].getName()[2:]:
                        print("equivalent cell already found, named {}, do not recreate".format(designCell.getName()))
                        cell = designCell
                        lutEquation = LUTTools.getLUTEquation(cell)
                        if belName[1] == "5" and cellToCreatePinName[1] == "6":
                            print("ERROR: this does not fit, we have to intervene (e.g. by changing the existing cell {} to a larger LUT6)".format(cell))
                            quit()
                        break
        else:
            cell = design.createAndPlaceCell(*((cellToCreateParent,) + cellToCreateArgs))
            if isLUT:
                lutEquation = "O=0"
        # TODO how to handle other BELs than LUTs and [ABCD]X inputs?
        if isLUT:
            pinName = "A" + str(int(cellToCreatePinName[1]))
            if pinName in cell.getPinMappingsP2L():
                lutInput = cell.getPinMappingsP2L()[pinName]
            else:
                lutInput = "I" + str(int(pinName[1])-1)
                cell.addPinMapping(pinName, lutInput)
            if lutInput not in lutEquation:
                if lutEquation == "O=0":
                    lutEquation = " " # "O =" can be omitted here
                else:
                    lutEquation += " + "
                LUTTools.configureLUT(cell, lutEquation + lutInput)
        else:
            lutInput = "D"
        # look at the destination cell in case it is already connected to <const1> or similar
        netlist = design.getNetlist()
        edifCell = netlist.getCellInstFromHierName(cell.getName())
        if not edifCell:
            for edifCell in netlist.getAllLeafCellInstances():
                if edifCell.getName() == cell.getName():
                    break
            else:
                print("WARNING: EDIF cell not found")
        else:
            edifPortInst = edifCell.getPortInst(lutInput)
            if edifPortInst:
                edifNet = edifPortInst.getNet()
                print("lets remove the portInst {} first (net {})".format(edifPortInst, edifNet))
                edifNet.removePortInst(edifPortInst)
        if(edifCell.getName() == "LUT6"):
            print("XXXX:",edifCell,cell,cellToCreateArgs,cellToCreateNet,cellToCreatePinName)
            print("REVIEW HERE! Unsupported hierarchy of LUT6_2 elements, we need to take care of unassoc. LUT[56] instances!")
            quit()

            #for edifNet in edifCell.getNets():
            #    for edifPortInst in edifNet.getPortInsts():
            #        if edifPortInst.isInput() and edifPortInst.getCellInst() == edifCell:
            #            print("lets remove the portInst {} first (net {})".format(edifPortInst, edifNet))
            #            edifNet.removePortInst(edifPortInst)
        siteInst = cell.getSiteInst()
        for sitePinInst in siteInst.getSitePinInsts():
            if sitePinInst.getName() == cellToCreatePinName:
                break
        else:
            global net_, cell_
            net_ = cellToCreateNet
            cell_ = cell
            print("net.connect({}, {})".format(cell, lutInput))
            cellToCreateNet.connect(cell, lutInput)
            sitePinInst = siteInst.getSitePinInst(cellToCreatePinName)      
        cellToCreateNet.addPin(sitePinInst)
        sitePinInst.setNet(cellToCreateNet)  
        belPin1 = sitePinInst.getBELPin()
        if isLUT:
            pinName = "A" + cellToCreatePinName[1]
        else:
            pinName = "D"
        belPin2 = cell.getSite().getBELPin(cellToCreateArgs[3].getName(), pinName)
        print("route intra-site {} from {} to {}".format(siteInst, belPin1, belPin2))
        # store this now because we will unroute every net during routing step, so intra-site routings will be the last step
        intraSiteRoutes.append((siteInst, (cellToCreateNet, belPin1, belPin2)))
        edifNet = netlist.getNetFromHierName(cellToCreateNet.getName())
        print("EDIFCell: {}, EDIFNet: {}".format(edifCell, edifNet))
        edifPortInstMap = edifCell.getPortInstMap()
        if lutInput in edifPortInstMap:
            edifNet.addPortInst(edifPortInstMap[lutInput])
        else:
            edifNet.createPortInst(lutInput, edifCell)
    return fasmOutput

def checkForClockNet(n):
    return n.isClockNet() or "_CLK" in n.name.upper() or "CLK_" in n.name.upper() # FIXME better detection of Clock nets than "_CLK" in the name

def routeDesign(design, usedNodes=None, fasm=None, netPriorityList=[]):
    fasmOutput = ""
    if usedNodes is None:
        usedNodes = HashSet()
    # TODO implement a better solution as manually to reorder the nets
    # - give any net a priority value of 0
    # - in case the net fails to route, increase the priority value by one
    # - retry routing with the new priority order
    # - but only if the order has changed after changed values
    primaryNets = [net for net in [design.getNet(net) for net in ["GLOBAL_LOGIC0", "GLOBAL_LOGIC1"] + netPriorityList] if net]
        #design.getNet("TRJ_RDATA_O[9]"), design.getNet("TRJ_RDATA_O[3]"), design.getNet("TRJ_RDATA_O[6]"), design.getNet("TRJ_RDATA_O[8]"), design.getNet("TRJ_RDATA_O[7]"), design.getNet("TRJ_RDATA_O[5]"), design.getNet("TRJ_RDATA_O[4]"), design.getNet("TRJ_RDATA_O[10]"), design.getNet("TRJ_RDATA_O[0]"), design.getNet("TRJ_RDATA_O[15]"), design.getNet("TRJ_RDATA_O[2]"), design.getNet("TRJ_RDATA_O[17]"), design.getNet("TRJ_RDATA_O[19]"), design.getNet("TRJ_RDATA_O[11]")] if net]
        #design.getNet("TRJ_AES_Key_Filter_inst/in0[5]"), design.getNet("TRJ_AES_Key_Filter_inst/in0[4]"), design.getNet("TRJ_AES_Key_Filter_inst/in0[10]"), design.getNet("TRJ_AES_Key_Filter_inst/in0[3]"), design.getNet("TRJ_AES_Key_Filter_inst/in0[11]"), design.getNet("TRJ_AES_Key_Filter_inst/in0[15]")] if net]
    disabledTiles = []
    for cell in design.getCells():
        if not re.match(r"^[io]_[0-9]+(_lutmod_[0-9A-F]+)?(/LUT[56])?$", cell.getName()):
            continue
        disabledTiles.append(cell.getTile())

        # here we can already do LUT magic in case we want to modify the LUT INIT strings    
        if "LUT" in cell.getType() and "_lutmod" in cell.getName():
            # take the INIT value and modify. This must be done here, as the saved checkpoint won't contain any modified INIT strings otherwise unfortunately
            # also, we can take care here to export it directly to the FASM update
            init_hex = re.match(r"^[io]_[0-9]+_lutmod_([0-9A-F]+)(?:/LUT[56])?$", cell.getName()).group(1)
            init_length = len(init_hex) * 4
            lut_length = 2 ** int(cell.getType()[3:])
            if lut_length >= init_length:
                # if the INIT string can hold the value, then override
                new_init = str(init_length) + "'h" + init_hex
                #cell.setProperty("INIT", new_init) # if it was that simple...
                #LUTTools.configureLUT(cell, LUTTools.getLUTEquation(new_init))
                # unfortunately when the design is saved, the LUT again is discarded because of missing inputs. They can also be added again later on by:
                # foreach cell [get_cells *lutmod*] {
                #     set init [string range $cell [expr {[string last _ $cell] + 1}] end]
                #     set_property INIT "64'h${init}" $cell
                # }
                # however to make it more simple anyway, we add it to the output2.fasm (set to all zero) or another output3.fasm (set single bits)
                global cell_
                cell_ = cell

                # ATTENTION! If that feature is used, the LUT String MUST be converted to BEL related
                # This can be done in RapidWright using the conversion table ("Pin 2 BEL") but unfortunately not within this script because this information is missing (only in original design or by RE means)
                # eq = LUTTools.getLUTEquation("64'hFCFCCCCCFFCCCCCC")
                # t = {"I0":"I2","I1":"I3","I2":"I1","I3":"I0","I4":"I5","I5":"I4"}
                # print(LUTTools.getLUTInitFromEquation("".join([t[x] if x in t else x for x in re.split(r'(I[0-5])', eq)]),6))

                fasm_line = cell.getTile().getName() + "." + str(cell.getSite().getSiteTypeEnum()) + "_X" + str(cell.getSite().getInstanceX() % 2) + "." + cell.getBEL().getName()[0] + "LUT.INIT[" + str(lut_length - 1) + ":0] = " + str(lut_length) + "'b" + bin(int(init_hex, 16))[2:].zfill(lut_length) + "\n"
                fasmOutput += fasm_line

    # Block BYP PIPs for routing of other nets in case they are the only ones that can be used to reach certain sinks.
    # We find these by going through each sink of each non-static net and checking if the last PIP is a "BYP". Then restrict usage to routing of the net (not specifically that sink required, worst case the sink won't get routed when the pip was used for another sink in the same net)
    blockedWiresForNet = {}
    for n in design.getNets():
        if checkForClockNet(n) or n.isStaticNet() or n.getSource() == None: continue
        for sink in n.getPins():
            rn = sink.getRouteNode()
            backPIPs = rn.getBackwardPIPs()
            if len(backPIPs) != 1: continue
            rn = backPIPs[0].getStartRouteNode()
            backConns = rn.getBackwardConnections()
            if len(backConns) != 1 or not backConns[0].getWireName().startswith("BYP"): continue
            wire = backConns[0]
            backPIPs = wire.getBackwardPIPs()
            if len(backPIPs) != 1: continue
            wire = backPIPs[0].getStartWire()
            blockedWiresForNet[wire] = n.getName()
    global blockedWiresForNet_
    blockedWiresForNet_ = blockedWiresForNet
    for k, v in blockedWiresForNet.items():
        print(str(v)+"\t"+str(k))

    #TODO check whether disabledTiles also need IOBs that had been implicitely added by vivado beforehand (min. with TinyLogicAnalyzer)
    for n in primaryNets + [n for n in design.getNets() if n not in primaryNets]:
        if checkForClockNet(n): continue
        n.unroute() # unroute first because somehow we couldn't use "just placed" checkpoints here. so we had to dummy route in vivado before
        if n.isStaticNet():
            routeStaticNet(n, usedNodes, design, disabledTiles)
        else:
            if n.getSource() == None: continue
            routeNet(n, usedNodes, fasm, design, blockedWiresForNet)
    
    return fasmOutput

def routeStaticNet(net, usedNodes, design, disabledTiles, debug=False):
    netType = net.getType()

    # Assume the net is completely un-routed
    # TODO here again go through all the used Nodes and find out if they do originate from the same static net !! (otherwise errors in TINYLA_BSCAN_SEL 8 times as this is a CE that then cannot find any route anymore...)
    netPIPs = HashSet()
    sinksToRemove = HashSet()
    # For each pin, route backward from the input pin
    for sink in net.getPins():
        # ignore all the sinks inside the 'dummy slices' as well as clock (?)
        if sink.getTile() in disabledTiles:
            # remove sink!
            sinksToRemove.add(sink)
            continue

        if sink.isOutPin():
            continue
        watchdog = 10000

        """
        1st approach: create a wire, then get the RouteNode
        wire = sink.getSiteInst().getSite().getTileWireIndexFromPinName(sink.getName())
        if wire == -1: ERROR...
        debug... t.getWireName(wire)
        n = RouteNode(t, wire)

        2nd approach: directly get the RouteNode
        n = sink.getRouteNode()

        3rd approach: Workaround for RapidWright bug (Issue #635 and #641)
        """
        n = RouteNode(sink.getTile(), sink.getConnectedWireIndex())
        if not n:
            print("ERROR: Problem while trying to route static sink " + str(sink))
            continue
        t = sink.getTile()
        if debug:
            print("SINK: " + t.getName() + " " + (n.getWireName() if n.getWire() != -1 else "?"))
        
        q = RouteNode.getPriorityQueue()
        visitedNodes = HashSet()
        q.add(n)
        success = False
        while(not q.isEmpty()):
            n = q.poll()
            visitedNodes.add(n)
            if debug:
                print("DEQUEUE: " + (str(n) if n.getWire() != -1 else n.getTile().getName()+"/?"))
            usable = isNodeUsableStaticSource(n, netType, design)
            if usable:
                currPathNode = n
                while currPathNode.getParent() is not None:
                    for w in currPathNode.getConnections():
                        if w.getWireIndex() == currPathNode.getParent().getWire() and w.isEndPIPWire():
                            p = PIP(currPathNode.getTile(), currPathNode.getWire(), currPathNode.getParent().getWire(), w.getPIPType())
                            if debug:
                                print(" " + str(p))
                            netPIPs.add(p)
                            break
                    currPathNode = currPathNode.getParent()
                success = True
                break
            try:
                for w in n.getBackwardConnections():
                    if w.isRouteThru():
                        continue
                    nParent = RouteNode(w, n)
                    nParent.setCost(n.getLevel()+1)
                    if nParent.getIntentCode() in (IntentCode.NODE_GLOBAL_VDISTR,
                        IntentCode.NODE_GLOBAL_HROUTE, IntentCode.NODE_GLOBAL_HDISTR,
                        IntentCode.NODE_HLONG, IntentCode.NODE_VLONG,
                        IntentCode.NODE_GLOBAL_VROUTE, IntentCode.NODE_GLOBAL_LEAF,
                        IntentCode.NODE_GLOBAL_BUFG):
                        continue
                    if usedNodes.contains(nParent): continue
                    if visitedNodes.contains(nParent): continue
                    q.add(nParent)
            except:
                print("FAIL! Probably could not enumerate any Backwad Connections because of BRAM...")
            watchdog = watchdog - 1
            if(watchdog < 0): break
        if not success:
            print("FAILED to route " + str(netType) + " pin " + str(sink))
        else:
            sink.setRouted(True)
    
    for pin in sinksToRemove:
        net.removePin(pin)

    net.setPIPs(netPIPs)
    for pip in netPIPs:
        usedNodes.add(RouteNode(pip.getTile(),pip.getStartWireIndex()))
        usedNodes.add(RouteNode(pip.getTile(),pip.getEndWireIndex()))

LUT_OUTPUT_PIN_NAMES = ["CLE_CLE_"+cle+"_SITE_0_"+pin+"_O" for cle in "LM" for pin in "ABCDEFGH"]

def isNodeUsableStaticSource(n, type, design):
    # RapidWright Bug, some valid RouteNodes seem to have an invalid wireIndex (-1)
    if n.getWire() == -1:
        return False

    # We should look for 3 different potential sources before we stop:
    # (1) GND_WIRE 
    # (2) VCC_WIRE 
    # (3) Unused LUT Outputs (A_0, B_0,...,H_0)
    pinName = Net.VCC_WIRE_NAME if type == NetType.VCC else Net.GND_WIRE_NAME
    if n.getWireName().startswith(pinName):
        return True
    elif n.getWireName() in LUT_OUTPUT_PIN_NAMES:
        # If lut is unused, we can re-purpose it for a static source
        slice = n.getTile().getSites()[0]
        i = design.getSiteInstFromSite(slice)
        if i is None:
            return True # Site is not used
        uniqueId = n.getWireName()[len(n.getWireName())-3]
        currNet = i.getNetFromSiteWire(uniqueId + "_O")
        if currNet is None:
            return True
        if currNet.getType() == type:
            return True
        return False
        # TODO howto find out if static LUTs of the FASM might be used?
        """proposedLutName = uniqueId + "6LUT"
        for c in i.getCells():
            if proposedLutName == c.getBel().getName():
                return False
        return True"""
    return False

class RoutingFailedError(Exception):
    def __init__(self, problematicNet, problematicSink):
        self.net = problematicNet
        self.sink = problematicSink
        self.message = "Failed to route: {} ({}/{})".format(self.net.getName(), self.sink.getSite().getName(), self.sink.getName())
        super(Exception, self).__init__(self.message)

def routeNet(net, usedNodes, fasm, design=None, blockedWiresForNet={}):
    # Keep track of all PIPs used
    allUsedPIPs = HashSet()
    initiallyUsedPIPs = HashSet()
    allUsedPIPsOutput = HashSet()
    """
    # in case something similar happens for structures not supported completely by RapidWright, use this hack:
    if "DOADO[0]" in net.name: # HACK, see RapidWright Issue #214
        device = design.getDevice()
        tile = device.getTile('BRAM_L_X28Y245')
        allUsedPIPs.add(tile.getPIP(tile.getWireIndex('BRAM_RAMB18_DOADO0'), tile.getWireIndex('BRAM_LOGIC_OUTS_B15_2')))
        tile = device.getTile('BRAM_INT_INTERFACE_L_X28Y247')
        allUsedPIPs.add(tile.getPIP(tile.getWireIndex('INT_INTERFACE_LOGIC_OUTS_L_B15'), tile.getWireIndex('INT_INTERFACE_LOGIC_OUTS_L15')))
        tile = device.getTile('INT_L_X28Y247')
        allUsedPIPs.add(tile.getPIP(tile.getWireIndex('LOGIC_OUTS_L15'), tile.getWireIndex('NW6BEG3')))
    """

    # compare with the FASM to make routing most convenient
    print("--- Signal: "+str(net)+" ---")
    usedNodesCopy = usedNodes.copy()
    spi = net.getSource()
    srcNode = spi.getRouteNode()
    if spi.getName() in "ABCD":
        # could be *MUX as well, when having O6 routed to the A/B/C/D pin!
        # check if following PIP is set: CLBLM_R_X53Y82.SLICEL_X1.DOUTMUX.O6
        s = spi.getSite()
        fasmtile = spi.getTile()
        xpos = str(s.getInstanceX() % 2)
        fasmsink = str(s.getSiteTypeEnum()) + "_X" + xpos
        fasmsrc = spi.getName() + "OUTMUX.O6"
        if fasmtile in fasmPIPDict and fasmsrc in fasmPIPDict[fasmtile] and fasmsink in fasmPIPDict[fasmtile][fasmsrc]:
            # as we have the OUTMUX set to O6, we will take this output as precedence to the normal pin
            # (if XOUTMUX is not used, then the XOUTMUX BEL won't be configured, if it is used, we can use it)
            srcNode = RouteNode(s.getTile(), s.getTileWireIndexFromPinName(spi.getName() + "MUX"))
            # also set the respective OUTMUX in our checkpoint
            si = spi.getSiteInst()
            si.addSitePIP(si.getSitePIP(spi.getName() + "OUTMUX", "O6"))

    if len(srcNode.getConnections()) > 0:
        clbWire = srcNode.getConnections()[0]
        clbNode = RouteNode(clbWire, srcNode)
        if len(clbNode.getConnections()) > 0:
            intWire = clbNode.getConnections()[0]
            fasmUsedPIPs = fasm_find_pip(fasm, intWire)
            if fasmUsedPIPs:
                intNode = RouteNode(intWire, clbNode)
                initiallyUsedPIPs.update(intNode.getPIPsBackToSource())
                # follow this pip
                while True:
                    print(fasmUsedPIPs)
                    #TODO verify how it works with multiple PIPs in the list here
                    initiallyUsedPIPs.add(fasmUsedPIPs[0])
                    usedNodesCopy.remove(RouteNode(fasmUsedPIPs[0].getTile(), fasmUsedPIPs[0].getStartWireIndex()))
                    usedNodesCopy.remove(RouteNode(fasmUsedPIPs[0].getTile(), fasmUsedPIPs[0].getEndWireIndex()))
                    newNode = fasmUsedPIPs[0].getEndRouteNode() # TODO could add level and parent here and store all the routenodes for the path[-1] step later on
                    for newWire in newNode.getConnections():
                        fasmUsedPIPs = fasm_find_pip(fasm, newWire)
                        if fasmUsedPIPs:
                            #TODO: if more than one (yes, this can happen of course, signals DO split!), follow each one.
                            break
                    else:
                        # no PIP set from this one
                        break
                    intNode = RouteNode(newWire, newNode)

    # We will use a priority queue to sort through the nodes we encounter, 
    # those with the least cost will fall to the bottom
    allUsedPIPs.update(initiallyUsedPIPs)
    q = RouteNode.getPriorityQueue()
    if allUsedPIPs.isEmpty():
        q.add(srcNode)
    
    # For each sink, run findRoute()
    global net_
    net_ = net
    routedSinks = set()
    for sink in net.getPins():
        if sink.equals(net.getSource()) or sink in routedSinks: 
            continue
        # If we already have some PIPs dedicated to the route, let's 
        # add them to the queue to be used for future routes
        if allUsedPIPs.size() > 0:
            q.clear()
            for pip in allUsedPIPs:
                # TODO take costs (=level/4) and level into consideration here
                q.add(RouteNode(pip.getTile(),pip.getStartWireIndex()))
                q.add(RouteNode(pip.getTile(),pip.getEndWireIndex()))
        #if net.name == "instr_rdata_o[15]": print("=== route sink {} ===".format(sink))
        print("find Route to {}".format(sink.getRouteNode()))
        path, level = findRoute(q,sink.getRouteNode(), usedNodesCopy, routeThroughs=False, verbose=False, blockedWiresForNet=blockedWiresForNet, netName=net.name) #(net.name == "instr_rdata_o[15]")) # verbose=(sink.getSite().getName() == "SLICE_X149Y96" and sink.getName() == "A5"))
        if path == None:
            raise RoutingFailedError(net, sink)
        elif path: # if path is empty, nothing seems to be required!
            # save longest route in the design
            global maxLevel
            if maxLevel < level:
                global maxLevelNetSink
                maxLevel = level
                maxLevelNetSink = (net, sink)

            # find start of path (path[-1]) and all of it's possible predecessors in initiallyUsedPIPs
            # this is done so the complete net is put into the dcp which allows to generate the bitstream in vivado
            if initiallyUsedPIPs.size() > 0:
                pip = path[-1]
                while pip.getStartRouteNode() != srcNode:
                    back = pip.getStartRouteNode().getBackwardConnections()
                    if len(back):
                        for pip in initiallyUsedPIPs:
                            # TODO route back using the strategy used in fasmFindPIPsAndSinksFromSinkPinInst, also what happens with "always-taken" connections? -> low prio as there was never an error here
                            if pip.getEndWire() in back or pip.getStartWire() in back:
                                # add this pip, recurse until the srcNode
                                allUsedPIPsOutput.add(pip)
                                break
                        else:
                            break
                    else:
                        break
            allUsedPIPs.addAll(path)
            # Keep track of used nodes for future nets and other sinks (leaf-trees can never join the same nodes again or there will be two parallel routes to the same nodes)
            for pip in path:
                usedNodes.add(RouteNode(pip.getTile(), pip.getStartWireIndex()))
                usedNodes.add(RouteNode(pip.getTile(), pip.getEndWireIndex()))
                usedNodesCopy.add(RouteNode(pip.getTile(), pip.getStartWireIndex()))
                usedNodesCopy.add(RouteNode(pip.getTile(), pip.getEndWireIndex()))
            allUsedPIPsOutput.addAll(path)
            routedSinks.add(sink)

    # Attach our final set of PIPs to the route
    net.setPIPs(allUsedPIPsOutput)

# We've augmented our cost function to model both distance to the sink
# but also include the depth (level) of the route we are following
def costFunction(curr, snk):

    return curr.getManhattanDistance(snk) + curr.getLevel() / 4

# Let's put our route routine into a function
def findRoute(q, snk, usedNodes, verbose=False, routeThroughs=True, blockedWiresForNet={}, netName=""):
    # We'll keep track of where we have visited and a watchdog timer
    visited = HashSet()
    watchdog = 50000000 # last three 0
    
    # While we still have nodes to look at, keep expanding
    while(not q.isEmpty()):
        curr = q.poll()
        if verbose:
            print("Queue:", curr, "Connections:", curr.getConnections(), "Sink:", snk)
        if(curr.equals(snk)):
            # print "Visited Wire Count: " + str(visited.size())
            # We've found the sink, recover our trail of PIPs 
            if verbose:
                global pips
                pips = curr.getPIPsBackToSource()
                print(pips)
            return curr.getPIPsBackToSource(), curr.getLevel()
        
        visited.add(curr)
        watchdog = watchdog - 1
        if verbose:
            print("Watchdog:", watchdog)
        if(watchdog < 0): break
        # Print our search path to help debugging easier
        # print MessageGenerator.makeWhiteSpace(curr.getLevel()) + str(curr)
        # Expand the current node to look for more nodes/paths
        for wire in curr.getConnections():
            nextNode = RouteNode(wire, curr)
            if verbose:
                print("Next Node:", nextNode)
            if visited.contains(nextNode): continue
            if usedNodes.contains(nextNode): continue
            # TODO: Evaluate before actual routing which targets will end up after a BYP (i.e. AX,BX,CX,DX) and block these for all *other* nets.
            # The following is just a hotfix to get things done in the first place. Normally this is catched by net priorities, but this can lead to loops and thus unroutable situations.
            # There is a AX/BX/CX/DX used check in lines 83-97, however this "used" check is not used for keeping the BYP free, only to detect where to route to - this seems not to be a problem for the mux control inputs, but for routing it certainly is an issue that was catched only by completely failing and retrying with different priorities leading to aforementioned loops - we can do better!
            skipWire = False
            if "BYP_" in nextNode.getName():
                for blockWire, blockNet in blockedWiresForNet.items():
                    if blockWire in nextNode.getWiresInNode():
                        if blockNet != netName:
                            print("changed route due to conflicting BYP to X-pin of slice (node: {}, net: {}).".format(nextNode.getName(), netName))
                            skipWire = True
                            break
            if skipWire:
                continue
            """if (nextNode.getName() == "INT_R_X71Y61/BYP_ALT0" and snk.getName() == "CLBLL_R_X71Y61/CLBLL_LL_AX") or \
                (nextNode.getName() == "INT_R_X63Y71/BYP_ALT1" and snk.getName() == "CLBLM_R_X63Y71/CLBLM_M_C3") or \
                (nextNode.getName() == "INT_L_X74Y59/BYP_ALT2" and snk.getName() == "CLBLM_L_X74Y59/CLBLM_M_CX") or \
                (nextNode.getName() == "INT_L_X70Y68/BYP_ALT3" and netName != "instr_addr_i[0]") or \
                (nextNode.getName() == "INT_L_X68Y70/BYP_ALT2" and netName != "instr_addr_i[1]") or \
                (nextNode.getName() == "INT_L_X68Y71/BYP_ALT1" and netName != "instr_addr_i[1]") or \
                (nextNode.getName() == "INT_L_X68Y71/BYP_ALT2" and netName != "instr_addr_i[1]") or \
                (nextNode.getName() == "INT_L_X70Y68/BYP_ALT2" and netName != "instr_addr_i[3]") or \
                (nextNode.getName() == "INT_R_X65Y73/BYP_ALT2" and netName != "instr_addr_i[0]") or \
                (nextNode.getName() == "INT_L_X72Y58/BYP_ALT5" and netName != "instr_addr_i[4]") or \
                (nextNode.getName() == "INT_R_X71Y61/BYP_ALT5" and netName != "trj_instr_mux_intercept[2]_i_4_n_66") or \
                (nextNode.getName() == "INT_R_X63Y71/BYP_ALT3" and netName != "instr_addr_i[1]") or \
                (nextNode.getName() == "INT_R_X71Y61/BYP_ALT3" and netName != "instr_addr_i[5]") or \
                (nextNode.getName() == "INT_R_X65Y73/BYP_ALT0" and netName != "instr_addr_i[8]") or \
                (nextNode.getName() == "INT_R_X71Y58/BYP_ALT1" and netName != "instr_addr_i[4]") or \
                (nextNode.getName() == "INT_R_X71Y61/BYP_ALT2" and netName != "instr_addr_i[2]") or \
                (nextNode.getName() == "INT_R_X63Y71/BYP_ALT2" and netName != "instr_addr_i[1]") or \
                (nextNode.getName() == "INT_R_X65Y73/BYP_ALT1" and netName != "instr_addr_i[2]"):
                #(nextNode.getName() == "INT_R_X71Y61/BYP_ALT4" and netName != "trj_instr_mux_intercept[2]_i_4_n_66") or \
                #(nextNode.getName() == "INT_R_X73Y59/BYP_ALT0" and netName != "instr_addr_i[1]") or \
                print("changed route due to conflicting BYP to X-pin of slice (node: {}, net: {}).".format(nextNode.getName(), netName))
                continue"""
            # BUG: BYP/FAN wires are routed without a PIP for instance to [A-D]X pins in CLBs.
            # Whenever a BYP/FAN pin is not configured, it defaults to VCC.
            # When the respective pin is used within the CLB (= as VCC) then there is no
            # indication in the fasm that the BYP/FAN pin is used. To resolve this issue
            # (and not statically blocking these nodes) it is required to check which of these
            # pins inside each CLB are used and if they are used and set to VCC, block the
            # usage of these for routing. (probably already fixed with the above)
            if nextNode.getName() == "INT_L_X60Y80/BYP_ALT1": continue
            # BUG: somewhat related issue here with [A-D]X pins. If we route a signal to a
            # [A-D]X pin in a different net later on, the resp. BYP/FAN pin needs to keep free
            # to accomodate for routing. In case they can be detected as used CLB pins (maybe
            # also only in the mod design, not only the original design!!!) they are required
            # to be blocked for ANY OTHER nets. (probably already fixed with the above)
            if snk.getName() == "CLBLL_R_X57Y77/CLBLL_L_AX":
                if nextNode.getName() == "INT_R_X57Y77/BYP_ALT5": continue
            # BUG: we sometimes route through BUFR cells in the IOIs, it is unsure if we can
            # successfully merge these, so better keep them out.
            if "IOI" in nextNode.getName():
                print("SKIP IOI: " + nextNode.getName())
                continue
            # also check if the any of the wire's connections connect back to the wire. This could happen for instance with LH/LV wires as they can be driven from multiple locations (displayed in pink in vivado)
            wireNode = RouteNode(wire.getTile(), wire.getWireIndex()) # we need to build a clean RouteNode for checking the PIPs required
            for nextWire in wireNode.getConnections():
                nextRouteNode = RouteNode(nextWire, wireNode)
                if not nextRouteNode.getPIPsBackToSource(): # do this only if there are no PIPs required for this connection, otherwise we are somewhat safe now
                    # so if there are no PIPs required, this connection must be active anytime
                    if usedNodes.contains(nextRouteNode): # if then this selected destination is already under the used nodes, do not use this wire
                        skipWire = True
                        break
            if skipWire:
                continue
            # Fixing a Routing Error (2x LH12)
            if curr.getParent() and curr.getParent().getWireName() == "LH12" and wire.getWireName() == "LH12": continue
            # do not use Routethroughs
            if not routeThroughs and re.match(r"^CLB.*_(?:[LM]|LL)_[A-D](?:MUX)?$", nextNode.getName()): continue
            # Now we've modified our cost function to include levels or hops from source
            # along with Manhattan distance
            cost = costFunction(nextNode, snk)
            if verbose:
                print("Use it, cost:", cost)
            nextNode.setCost(cost)
            q.add(nextNode)
    
    if verbose:
        global pips
        pips = curr.getPIPsBackToSource()
        print(pips)
                
    # Unroutable situation
    return None, None

def fasm_set_pip(pip, value=True):
    # we want to generate something like: INT_L_X14Y243.NN2BEG2.NR1END2 = 0
    tileName = pip.getTile().getName()
    sink = pip.getEndWireName()
    source = pip.getStartWireName()
    return ".".join((tileName, sink, source)) + (" = 0\n" if not value else "\n")

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

# input: iterable containing only canoncialized fasm lines (string), device to get the tiles from (Device)
# output: set of RouteNodes that are presumably inside the fasm
# warning: only intersite routing supported here as we filter for INTs

def fasm_used_routing_resources(fasm, device):
    usedNodes = HashSet()
    fasmPIPs = {}

    for line in fasm:
        if line.startswith('INT_') or line.startswith('CLB'):
            fasmtile, fasmsink, fasmsrc = line.split('.', 2)
            tile = device.getTile(fasmtile)
            if line.startswith('INT_'):
                usedNodes.add(RouteNode(tile, tile.getWireIndex(fasmsink)))
                usedNodes.add(RouteNode(tile, tile.getWireIndex(fasmsrc)))
            if tile not in fasmPIPs:
                fasmPIPs[tile] = {}
            if fasmsrc not in fasmPIPs[tile]:
                fasmPIPs[tile][fasmsrc] = []
            fasmPIPs[tile][fasmsrc].append(fasmsink)

    return fasmPIPs, usedNodes

def fasm_find_pip(fasmPIPs, wire):
    tile = wire.getTile()
    if tile not in fasmPIPDict:
        return []
    wireName = wire.getWireName()
    if wireName not in fasmPIPDict[tile]:
        return []
    fasmsinks = fasmPIPDict[tile][wireName]
    return [tile.getPIP(wire.getWireIndex(), tile.getWireIndex(fasmsink)) for fasmsink in fasmsinks]


def fasm_find_pip_reverse(fasmPIPs, wire):
    tile = wire.getTile()
    if tile not in fasmPIPDict:
        return None
    wireName = wire.getWireName()
    sources = []
    for fasmsource, fasmsinks in fasmPIPDict[tile].items():
        if wireName in fasmsinks:
            sourcePIPs = [x for x in tile.getBackwardPIPs(wire.getWireIndex()) if x.getStartWireIndex() == tile.getWireIndex(fasmsource)]
            if not sourcePIPs:
                print("Error! PIP {}->{} does not exist...".format(fasmsource, wireName))
            sources += sourcePIPs
    if not sources:
        return None
    #TODO sources can only be len=1, or?
    return sources

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    # Route the design
    design = Design.readCheckpoint(sys.argv[1])
    #design.unrouteDesign()

    # Load prohibited routing nodes
    fasm = []
    print("Load FASM...")
    for line in open(sys.argv[2], 'r'):
        fasm += fasm_canonicalize_line(line)
    print("Analyze PIPs from FASM...")
    fasmPIPDict, prohibitedRouteNodes = fasm_used_routing_resources(fasm, design.getDevice())

    if len(sys.argv) < 5 or len(sys.argv) > 6:
        print(__doc__)
        sys.exit(1)

    intraSiteRoutes = []
    print("Analyze nets to be rerouted, remove their PIPs...")
    fasmOutput = elaborateRerouteNets(design, fasmPIPDict, prohibitedRouteNodes, intraSiteRoutes)
    fasmFile = open(sys.argv[4], 'w')
    fasmFile.write(fasmOutput)

    print("Route Design...")
    maxLevel = -1
    maxLevelNetSink = None, None
    #Router(design).routeDesign() # - Use the RapidWright Router instead
    if len(sys.argv) == 5:
        fasmOutput = routeDesign(design, prohibitedRouteNodes, fasmPIPDict)
    else:
        # we have an optional priority file which we can make use of
        netPriorities = []
        try:
            for line in open(sys.argv[5], 'r'):
                if not line.strip():
                    continue
                priority, net = line.strip().split(" ", 1)
                netPriorities.append((net, int(priority)))
        except IOError:
            pass
        netPriorityList = sorted(netPriorities, key=lambda x:-x[1])
        while True:
            usedNodes = prohibitedRouteNodes.copy()
            try:
                print("Priority List: {}".format(netPriorityList))
                if netPriorityList:
                    designPriorities = list(tuple(zip(*netPriorityList))[0])
                else:
                    designPriorities = []
                fasmOutput = routeDesign(design, usedNodes, fasmPIPDict, designPriorities)
                break
            except RoutingFailedError as e:
                print(e.message)
                design.writeCheckpoint("intermediate.dcp")
                print("Retry routing with optimized net priorities")
                try:
                    if netPriorityList:
                        netIndex = tuple(zip(*netPriorityList))[0].index(e.net.getName())
                        if netIndex == 0:
                            raise Exception("Could not prioritize this net any more. Routing failed!")
                        netPriorityList[netIndex] = (netPriorityList[netIndex][0], netPriorityList[netIndex][1] + 1)
                        # additionally swap with the next one to give a better sort probability
                        netPriorityList = netPriorityList[:netIndex-1]+netPriorityList[netIndex:netIndex+1]+netPriorityList[netIndex-1:netIndex]+netPriorityList[netIndex+1:]
                    else:
                        raise ValueError
                except ValueError:
                    netPriorityList.append((e.net.getName(), 0))
                with open(sys.argv[5], 'w') as priorityFile:
                    for net, priority in netPriorityList:
                        priorityFile.write("{} {}\n".format(priority, net))
                design = Design.readCheckpoint(sys.argv[1])
                # need to stop this script as unfortunately just repeating the loop (which is of course preferred) seems not to have all RapidWright resources in a clean state
                print("Please re-run command now, due to non-repeatable things in RapidWright...")
                sys.exit(2)
                # maybe because of fasm_used_routing_resources uses 'design'?
    fasmFile.write(fasmOutput)
    fasmFile.close()

    for siteInst, args in intraSiteRoutes:
        siteInst.routeIntraSiteNet(*args)

    design.writeCheckpoint(sys.argv[3])
    print("Wrote " + sys.argv[3])
    print("Longest Route is of Net " + maxLevelNetSink[0].name + " to Sink " + repr(maxLevelNetSink[1]) + " with level " + str(maxLevel))