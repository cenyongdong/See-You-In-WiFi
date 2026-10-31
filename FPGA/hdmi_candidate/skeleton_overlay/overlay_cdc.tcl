# Real toggle/single-bit synchronizers only. No global clock cut and no new
# false path. Bound first-stage data arrival; time all following stages normally.
set ov U0_ps_ai_peripheral/hdmi_display/overlay
foreach spec {{request_reg {req_sync_reg\[0\]} 6.734} {ack_reg {ack_sync_reg\[0\]} 10.0} {underflow_any_reg {underflow_sync_reg\[0\]} 10.0}} {
 lassign $spec source target period
 set a [hdmi_cdc_cells overlay/$source 1]
 set b [hdmi_cdc_cells overlay/$target 1]
 if {[llength $a]!=1 || [llength $b]!=1} {error "Overlay handshake missing: $spec"}
 set_max_delay -datapath_only $period -from [get_pins -of_objects $a -filter {REF_PIN_NAME == C}] -to [get_pins -of_objects $b -filter {REF_PIN_NAME == D}]
}
set hide [hdmi_cdc_cells {overlay/hide_sync_reg\[0\]} 1]
if {[llength $hide]!=1} {error "Overlay hide synchronizer missing"}
set hide_d [get_pins -of_objects $hide -filter {REF_PIN_NAME == D}]
set hide_sources [all_fanin -flat -startpoints_only -to $hide_d]
if {![llength $hide_sources]} {error "Overlay hide launch path missing"}
set_max_delay -datapath_only 6.734 -from $hide_sources -to $hide_d
set vstage [hdmi_cdc_cells {overlay/vs_sync_reg\[0\]} 1]
set vd [get_pins -of_objects $vstage -filter {REF_PIN_NAME == D}]
set_max_delay -datapath_only 10.0 -from [all_fanin -flat -startpoints_only -to $vd] -to $vd
hdmi_gray_bound {overlay/fifo/wgray_reg\[[0-9]+\]} {overlay/fifo/ws1_reg\[[0-9]+\]} 10
hdmi_gray_bound {overlay/fifo/rgray_reg\[[0-9]+\]} {overlay/fifo/rs1_reg\[[0-9]+\]} 10
# FIFO payload is written before its Gray write pointer crosses two pixel
# registers. A location cannot be reused until the Gray read pointer returns.
# Bound the stable RAM payload to less than one pixel period; do not cut the
# same-clock read-address/mux paths or synchronization stages.
set fifo_ram [get_cells -quiet -hier -filter {NAME =~ U0_ps_ai_peripheral/hdmi_display/overlay/fifo/* && REF_NAME =~ RAM*}]
set ram_clocks [get_pins -of_objects $fifo_ram -filter {REF_PIN_NAME == CLK || REF_PIN_NAME == WCLK}]
set captures [hdmi_cdc_cells {overlay/(ink_stage|held_ink)_reg\[[0-9]+\]} 1]
if {![llength $ram_clocks]} {error "Overlay FIFO storage clock missing"}
set_max_delay -datapath_only 6.734 -from $ram_clocks -to [get_pins -of_objects $captures -filter {REF_PIN_NAME == D}]
