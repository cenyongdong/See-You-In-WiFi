if {[catch {

set ref {D:/FPGACompetitionProject/.local/frb1101-r1/build/.local/hdmi-boot-witness-20261019-r23/reference}
set native {D:/FPGACompetitionProject/.local/frb1101-r1/build/.local/csi-preprocess-20261031-r3/fpai_demo_vivado.runs/impl_pose_filter}
file mkdir {D:/FPGACompetitionProject/.local/frb1101-r1/build/.local/csi-preprocess-20261031-r3/ip_patch}
file mkdir $native
cd $native
open_checkpoint {D:/FPGACompetitionProject/.local/frb1101-r1/build/.local/csi-preprocess-20261031-r3/pipeline-routed-csi-incremental.dcp}
set_param general.maxThreads 2
source $ref/ip_patch/project_execution_guard.tcl
set ::env(JFM_PATH) $ref
set ::boot_allowed_xpr [file normalize $ref/fpai_demo_vivado.xpr]
set ::boot_allowed_launcher [file normalize {D:/FPGACompetitionProject/.local/frb1101-r1/build/.local/csi-preprocess-20261031-r3/call_procise_disable_icap.bat}]
rename open_project boot_original_open_project
proc open_project args {
 if {[llength $args]!=1 || [file normalize [lindex $args 0]] ne $::boot_allowed_xpr} {error "Bit hook selected an unexpected project: $args"}
 return [uplevel 1 [linsert $args 0 boot_original_open_project]]
}
rename exec boot_original_exec
proc exec args {
 if {[llength $args]==3 && [string equal -nocase [lindex $args 0] cmd] && [lindex $args 1] eq "/c" && [file normalize [lindex $args 2]] eq $::boot_allowed_launcher} {
  set f [open {D:/FPGACompetitionProject/.local/frb1101-r1/build/.local/csi-preprocess-20261031-r3/reports/factory-ICAP-deferred.txt} w];puts $f $args;close $f
  puts "BOOT_WITNESS_FACTORY_ICAP_DEFERRED_TO_EXPLICIT_INPUT_STAGE"
  return ""
 }
 return [uplevel 1 [linsert $args 0 boot_original_exec]]
}
# Physical qualification is recorded separately; preserve the routed context.
foreach mode {max min} {
 set path [get_timing_paths -delay_type $mode -max_paths 1]
 if {![llength $path] || [get_property SLACK $path]<0} {error "Physical setup/hold failed"}
}
set expected_design [current_design]
set expected_project [current_project]
source {D:/FPGACompetitionProject/.local/frb1101-r1/build/FPGA/hdmi_candidate/baselines/ps_release_r26/sources/write_bitstream_pre.tcl}
if {[current_design] ne $expected_design || [current_project] ne $expected_project || [get_property PART [current_project]] ne "xc7z030ffg676-2"} {error "Bit pre-hook replaced the routed context"}
if {[file exists ai7030_edif_top.bit]} {error "Preserve existing bit output"}
write_bitstream ai7030_edif_top.bit
source {D:/FPGACompetitionProject/.local/frb1101-r1/build/FPGA/hdmi_candidate/baselines/ps_release_r26/sources/write_bitstream_post.tcl}
if {![file exists ai7030_edif_top.bit] || [file size ai7030_edif_top.bit]<5000000} {error "Native bit missing/incomplete"}
puts "BOOT_WITNESS_RAW_BIT_COMPLETE_NO_BOARD_OPERATION"

} result]} {puts "BOOT_WITNESS_BIT_FAILED $result";puts $::errorInfo;exit 1}
exit
