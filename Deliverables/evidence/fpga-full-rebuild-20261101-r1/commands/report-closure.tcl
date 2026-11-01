# Read-only physical qualification of the new uninstrumented design.
if {[catch {
set_param general.maxThreads 2
set work {D:/FPGACompetitionProject/.local/frb1101-r1/build/.local/csi-preprocess-20261031-r3}
set out {D:/FPGACompetitionProject/.local/frb1101-r1/build/.local/csi-preprocess-20261031-r3/reports/physical-final-closure}
open_checkpoint $work/pipeline-routed-csi-incremental.dcp
report_timing_summary -file $out/timing-final.rpt -max_paths 10 -report_unconstrained
report_pulse_width -file $out/pulse-width.rpt
report_bus_skew -file $out/bus-skew-final.rpt
report_route_status -file $out/route-status-final.rpt
report_drc -file $out/drc-final.rpt
report_utilization -hierarchical -file $out/utilization.rpt
report_cdc -details -cells [get_cells U0_ps_ai_peripheral/hdmi_display] -file $out/hdmi-cdc.rpt
report_clocks -file $out/clocks.rpt
set f [open $out/final-native-facts.tsv w]
puts $f "PART\t[get_property PART [current_project]]"
foreach mode {max min} {
 set p [get_timing_paths -delay_type $mode -max_paths 1]
 if {![llength $p]} {error "No $mode timing path"}
 puts $f "$mode\t[get_property SLACK $p]\t[get_property STARTPOINT_PIN $p]\t[get_property ENDPOINT_PIN $p]"
}
foreach instance {ai_path_monitor ai_read_path_monitor hp2_cycle_recorder hp2_protocol_recorder hp2_protocol_observer} {
 set cells [get_cells -quiet -hier -filter "NAME =~ U0_ps_ai_peripheral/$instance || NAME =~ U0_ps_ai_peripheral/$instance/*"]
 puts $f "REMOVED\t$instance\t[llength $cells]"
 if {[llength $cells]} {error "Diagnostic hierarchy remains: $instance"}
}
set cores [get_debug_cores -quiet]
puts $f "DEBUG_CORES\t[llength $cores]"
if {[llength $cores]} {error "Debug core remains"}
set marked [get_nets -quiet -hier -filter {MARK_DEBUG == 1}]
puts $f "MARK_DEBUG\t[llength $marked]"
foreach net $marked {puts $f "DEBUG_NET\t$net"}
if {[llength $marked]} {error "Marked probe nets remain"}
foreach clock {clk_fpga_0 clk_out1_clk_wiz_0 clk_pll_i} period {20 10 5} {
 set c [get_clocks -quiet $clock]
 if {[llength $c]!=1 || abs([get_property PERIOD $c]-$period)>0.001} {error "Functional clock changed: $clock"}
 puts $f "CLOCK\t$clock\t[get_property PERIOD $c]"
}
set ready [get_pins -hier -quiet -filter {NAME =~ */proc_sys_reset_1/dcm_locked}]
set paths [get_timing_paths -through $ready -max_paths 4]
if {[llength $ready]!=1 || ![llength $paths]} {error "Functional HP2 readiness path absent/cut"}
foreach p $paths {puts $f "READY\t[get_property STARTPOINT_PIN $p]\t[get_property ENDPOINT_PIN $p]\t[get_property REQUIREMENT $p]\t[get_property SLACK $p]"}
set x U0_ps_ai_peripheral/ps_ai_wrapper_u0/ps_ai_i/axi_interconnect_4
foreach field {ARVALID ARADDR RREADY} {
 set pins [get_pins -quiet $x/S01_AXI_[string tolower $field]*]
 set src [get_cells -of_objects [get_pins -leaf -of_objects [get_nets -segments -of_objects $pins] -filter {DIRECTION == OUT}]]
 set refs [lsort -unique [get_property REF_NAME $src]]
 puts $f "S01_CONNECTED\t$field\t$refs"
 if {![llength $pins] || ![llength $refs] || $refs eq "GND"} {error "Functional S01 disconnected: $field"}
}

foreach instance {deferred_control startup_drain} {
 set cells [get_cells -quiet -hier -filter "NAME =~ U0_ps_ai_peripheral/$instance || NAME =~ U0_ps_ai_peripheral/$instance/*"]
 puts $f "RETAINED	$instance	[llength $cells]"
 if {![llength $cells]} {error "Functional consumer/control removed: $instance"}
}
set checker [get_cells -quiet -hier -filter {REF_NAME =~ *protocol_checker* || REF_NAME =~ *hp2_protocol* || REF_NAME =~ *cycle_trace* || REF_NAME =~ *boot_witness* || REF_NAME =~ *event_monitor* || REF_NAME =~ *read_monitor*}]
puts $f "FORBIDDEN_MODULES	[llength $checker]"
if {[llength $checker]} {error "Passive diagnostic module remains: $checker"}
source {D:/FPGACompetitionProject/.local/frb1101-r1/build/FPGA/hdmi_candidate/probe_free_drain/sources/consumer_paths_validate.tcl}
set deferred_validation_file {D:/FPGACompetitionProject/.local/frb1101-r1/build/.local/csi-preprocess-20261031-r3/reports/physical-final-closure/control-cdc.tsv}
source {D:/FPGACompetitionProject/.local/frb1101-r1/build/FPGA/hdmi_candidate/probe_free_drain/sources/deferred_control_validate.tcl}
set raw_ps [get_pins -hier -filter {REF_PIN_NAME == SAXIHP2ARESETN}]
set raw_ends [filter [all_fanout -flat -endpoints_only -from $raw_ps] {REF_PIN_NAME == D || REF_PIN_NAME == CE}]
if {[llength $raw_ps]!=1 || ![llength $raw_ends]} {error "Consumer reset path missing"}
foreach endpoint $raw_ends {
 set p [get_timing_paths -from $raw_ps -to $endpoint -max_paths 1]
 if {![llength $p]} {error "Consumer reset path is cut: $endpoint"}
 set r [get_property REQUIREMENT $p];set slack [get_property SLACK $p]
 puts $f "CONSUMER_RESET	$endpoint	$r	$slack"
 if {abs($r-5)>0.001 || $slack<0} {error "Consumer reset path failed: $endpoint"}
}


set filter_cells [get_cells -quiet -hier -filter {NAME =~ U0_ps_ai_peripheral/presentation_filter/*}]
if {![llength $filter_cells]} {error "Filter hierarchy missing"}
set filter_regs [filter $filter_cells {IS_SEQUENTIAL == 1}]
set filter_clocks [get_clocks -of_objects [get_pins -of_objects $filter_regs -filter {IS_CLOCK == 1}]]
foreach c $filter_clocks {if {abs([get_property PERIOD $c]-10)>0.001} {error "Filter clock differs from the existing GP source: $c"}}
if {![llength $filter_clocks]} {error "Filter clock missing"}
foreach mode {max min} {
 set p [get_timing_paths -delay_type $mode -to $filter_regs -max_paths 1]
 if {![llength $p] || [get_property SLACK $p]<0} {error "Filter $mode timing failed/missing"}
 puts $f "FILTER_TIMING\t$mode\t[get_property SLACK $p]"
}
report_utilization -cells [get_cells U0_ps_ai_peripheral/presentation_filter] -file $out/filter-utilization.rpt
report_utilization -file $out/total-utilization.rpt
report_cdc -details -cells [get_cells U0_ps_ai_peripheral/presentation_filter] -file $out/filter-cdc.rpt

report_utilization -cells [get_cells U0_ps_ai_peripheral/hdmi_display/overlay] -file $out/overlay-utilization.rpt
report_cdc -details -cells [get_cells U0_ps_ai_peripheral/hdmi_display/overlay] -file $out/overlay-cdc.rpt
report_utilization -cells [get_cells U0_ps_ai_peripheral/csi_preprocessor] -file $out/csi-utilization.rpt
set csi_regs [get_cells -hier -filter {NAME =~ U0_ps_ai_peripheral/csi_preprocessor/* && IS_SEQUENTIAL == 1}]
set csi_clocks [get_clocks -of_objects [get_pins -of_objects $csi_regs -filter {IS_CLOCK == 1}]]
if {![llength $csi_clocks]} {error "CSI clock missing"}
foreach c $csi_clocks {if {abs([get_property PERIOD $c]-10)>0.001} {error "CSI changed GP clock"}}
foreach mode {max min} {
 set p [get_timing_paths -delay_type $mode -to $csi_regs -max_paths 1]
 if {![llength $p]} {error "CSI timing coverage missing"}
 puts $f "CSI_TIMING\t$mode\t[get_property SLACK $p]"
}
close $f
} result]} {puts $result; puts $::errorInfo; exit 1}
exit
