# This script could be run on synthesized designs to extract information for each cells.
# This information helps custom placers to place the design in respect to other designs.

# for each cell that is not named i_X or o_X, return the following:
# - type: LUT6, FDRE, ...
# - name: name of the cell
# - signals: all input and output pins and connected signal names of the cell, e.g. "IN C SLICE_X..Y../AFF/C clk OUT Q SLICE_X..Y../AFF/Q ff_out_signal"

set output_file "extracted-tinylogicanalyzer-design-data"
#set output_file "extracted-aesregistertrojan-design-data"
#set output_file "extracted-instructionreplacementtrojan-design-data"
#set output_file "extracted-instructionmodtrojan-design-data"

set fo [open $output_file "w"]

set mod_cells [get_cells -regexp -filter { REF_NAME != "IBUF" && REF_NAME != "BUFG" && NAME !~ "(.*/)?[io]_[0-9]+(_lutmod_[0-9A-F]+)?(/LUT[56])?" && NAME !~ "GND.*" && NAME !~ "VCC.*" }]
foreach mod_cell $mod_cells {
    set type [get_property REF_NAME $mod_cell]
    set signals {}
    foreach pin [get_pins -of_objects $mod_cell -filter { IS_CONNECTED } ] {
        set dir [get_property DIRECTION $pin]
        set pinname [get_property REF_PIN_NAME $pin]
        set belpin [lindex [get_bel_pins -of_objects $pin] 0]
        set signalname [get_nets -of_objects $pin]
        lappend signals "$dir $pinname $belpin $signalname"
    }
    puts $fo "$type $mod_cell [join $signals " "]"
}

close $fo