if {[catch {
set_param general.maxThreads 2
  create_project -in_memory -part xc7z030ffg676-2
  set_property design_mode GateLvl [current_fileset]
  set_param project.singleFileAddWarning.threshold 0
  set_property webtalk.parent_dir D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/fpai_demo_vivado.cache/wt [current_project]
  set_property parent.project_path D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/fpai_demo_vivado.xpr [current_project]
  set_property ip_repo_paths {{D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/PS_AI IP}} [current_project]
  update_ip_catalog
  set_property ip_output_repo D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/fpai_demo_vivado.cache/ip [current_project]
  set_property ip_cache_permissions disable [current_project]
  set_property XPM_LIBRARIES {XPM_CDC XPM_MEMORY} [current_project]
  add_files -quiet D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/pipeline-synth-banked.dcp
  set_msg_config -source 4 -id {BD 41-1661} -limit 0
  set_param project.isImplRun true
  read_ip -quiet {D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/fpai_demo_vivado.srcs/sources_1/bd/ps_ai/ip/ps_ai_axi_interconnect_0_0/ps_ai_axi_interconnect_0_0.xci}
  read_ip -quiet {D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/fpai_demo_vivado.srcs/sources_1/bd/ps_ai/ip/ps_ai_axi_interconnect_1_0/ps_ai_axi_interconnect_1_0.xci}
  read_ip -quiet {D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/fpai_demo_vivado.srcs/sources_1/bd/ps_ai/ip/ps_ai_axi_interconnect_3_0/ps_ai_axi_interconnect_3_0.xci}
  read_ip -quiet {D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/fpai_demo_vivado.srcs/sources_1/bd/ps_ai/ip/ps_ai_m00_regslice_0/ps_ai_m00_regslice_0.xci}
  read_ip -quiet {D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/fpai_demo_vivado.srcs/sources_1/bd/ps_ai/ip/ps_ai_proc_sys_reset_0_0/ps_ai_proc_sys_reset_0_0.xci}
  read_ip -quiet {D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/fpai_demo_vivado.srcs/sources_1/bd/ps_ai/ip/ps_ai_proc_sys_reset_0_1/ps_ai_proc_sys_reset_0_1.xci}
  read_ip -quiet {D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/fpai_demo_vivado.srcs/sources_1/bd/ps_ai/ip/ps_ai_s00_regslice_0/ps_ai_s00_regslice_0.xci}
  read_ip -quiet {D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/fpai_demo_vivado.srcs/sources_1/bd/ps_ai/ip/ps_ai_s00_regslice_1/ps_ai_s00_regslice_1.xci}
  read_ip -quiet {D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/fpai_demo_vivado.srcs/sources_1/bd/ps_ai/ip/ps_ai_s01_regslice_0/ps_ai_s01_regslice_0.xci}
  read_ip -quiet {D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/fpai_demo_vivado.srcs/sources_1/bd/ps_ai/ip/ps_ai_util_vector_logic_0_0/ps_ai_util_vector_logic_0_0.xci}
  read_ip -quiet {D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/fpai_demo_vivado.srcs/sources_1/bd/ps_ai/ip/ps_ai_xbar_0/ps_ai_xbar_0.xci}
  read_ip -quiet {D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/fpai_demo_vivado.srcs/sources_1/bd/ps_ai/ip/ps_ai_xbar_1/ps_ai_xbar_1.xci}
  read_ip -quiet {D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/fpai_demo_vivado.srcs/sources_1/bd/ps_ai/ip/ps_ai_xbar_4/ps_ai_xbar_4.xci}
  read_ip -quiet {D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/fpai_demo_vivado.srcs/sources_1/bd/ps_ai/ip/ps_ai_xlconcat_0_0/ps_ai_xlconcat_0_0.xci}
  read_ip -quiet D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/rtl/ip/mig_7series_0/mig_7series_0.xci
  read_ip -quiet D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/rtl/sdi/ip/smpte_sdi/smpte_sdi.xci
  read_ip -quiet D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/rtl/sdi/ip/mgtclk/mgtclk.xci
  read_ip -quiet D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/rtl/sdi/ip/sys_clk/sys_clk.xci
  read_ip -quiet D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/rtl/ip/clk_wiz_0/clk_wiz_0.xci
  read_ip -quiet D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/rtl/ip/afifo_24w_4096d/afifo_24w_4096d.xci
  read_ip -quiet D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/rtl/ip/rindex_buf_2b_16w/rindex_buf_2b_16w.xci
  read_ip -quiet D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/rtl/ip/windex_buf_2b_16w/windex_buf_2b_16w.xci
  read_ip -quiet D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/rtl/ip/afifo_64i_16o_128/afifo_64i_16o_128.xci
  read_ip -quiet D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/rtl/ip/fifo_1/fifo_1.xci
  read_ip -quiet D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/rtl/ip/afifo_16i_64o_largebuf/afifo_16i_64o_largebuf.xci
  read_ip -quiet D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/rtl/ip/cmos_clkgen_742_5/cmos_clkgen_742_5.xci
  read_ip -quiet D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/rtl/ip/mna_idfifo_w12/mna_idfifo_w12.xci
  set_param project.isImplRun false
  read_edif D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/rtl/sdi/dru.edf
  read_edif D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/rtl/edif/AI_Mate.edif
  read_xdc D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/constrs_1/ai7030.xdc
  read_xdc D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/constrs_1/impl_constraints.xdc
  read_xdc D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/factory/constrs_1/hdmi_input.xdc
  set_param project.isImplRun true
  link_design -top ai7030_edif_top -part xc7z030ffg676-2
  set_param project.isImplRun false
read_checkpoint -cell U0_ps_ai_peripheral/ps_ai_wrapper_u0/ps_ai_i/processing_system7_0 {D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/inputs/FPGA/reference/ps-export.dcp}
write_checkpoint -force {D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/pipeline-linked-banked-unclocked.dcp}
set ps_primitive [get_cells -hier -filter {REF_NAME == PS7}]
if {[llength $ps_primitive]!=1} {error "Adapted PS7 primitive missing"}
set fclk [get_pins -of_objects $ps_primitive -filter {REF_PIN_NAME == "FCLKCLK[0]"}]
puts "PS_RELEASE_FCLK_BIND primitive=$ps_primitive pin=$fclk"
if {[llength $fclk]!=1} {error "Real PS FCLKCLK0 output is not unique"}
if {![llength [get_clocks -quiet clk_fpga_0]]} {create_clock -name clk_fpga_0 -period 20.000 $fclk}
if {abs([get_property PERIOD [get_clocks clk_fpga_0]]-20)>0.001} {error "Original PS frequency changed"}
set_input_jitter [get_clocks clk_fpga_0] 0.600
source {D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/inputs/FPGA/constraints/ps_release_factory_clocks.tcl}
report_clocks -file {D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/reports/pipeline-physical/linked-clocks.rpt}
write_checkpoint -force {D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/pipeline-linked-banked.dcp}
# Verify the formerly isolated master is connected in this actual linked netlist.
set x U0_ps_ai_peripheral/ps_ai_wrapper_u0/ps_ai_i/axi_interconnect_4
foreach field {ARVALID ARADDR RREADY} {
 set p [get_pins -quiet $x/S01_AXI_[string tolower $field]*]
 if {![llength $p]} {error "Connected S01 input missing: $field"}
 set src [get_cells -of_objects [get_pins -leaf -of_objects [get_nets -segments -of_objects $p] -filter {DIRECTION == OUT}]]
 set refs [lsort -unique [get_property REF_NAME $src]]
 puts "S01_CONNECTED $field $refs"
 if {$refs eq "GND" || ![llength $refs]} {error "S01 unexpectedly isolated: $field"}
}
source {D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/inputs/FPGA/constraints/implementation_opt_pre.tcl}
source {D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/inputs/FPGA/constraints/hdmi_cdc.tcl}
source {D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/inputs/FPGA/constraints/deferred_control_cdc.tcl}
source {D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/inputs/FPGA/constraints/startup_drain_bounds.tcl}
source {D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/inputs/FPGA/constraints/consumer_capture_scope.tcl}
source {D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/inputs/FPGA/constraints/overlay_cdc.tcl}
opt_design
source {D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/inputs/FPGA/constraints/implementation_opt_post.tcl}
write_checkpoint -force {D:/FPGACompetitionProject/.local/fpga-refactor-20261104-r1/hardware-r2/pipeline-opt-banked.dcp}

} result]} {puts $result;puts $::errorInfo;exit 1}
exit
