if {[catch {
open_checkpoint {D:/FPGACompetitionProject/.local/fpga-package-r4-check/.local/csi-preprocess-20261031-r3/pipeline-opt-banked.dcp}
set checks [get_drc_checks INBB*]
puts "NATIVE_RULES $checks"
report_drc -checks $checks -file {D:/FPGACompetitionProject/.local/fpga-package-r4-check/rebuild-logs/native-blackbox-drc.rpt}
foreach v [get_drc_violations -quiet] {report_property $v}
foreach c [get_cells -hier -filter {IS_BLACKBOX == 1}] {
 puts "FLAGGED_CELL $c"
 set children [get_cells -hier -filter "NAME =~ $c/*"]
 puts "DESCENDANTS [llength $children] $children"
 foreach child $children {report_property $child}
}
read_checkpoint -incremental {D:/FPGACompetitionProject/.local/fpga-package-r4-check/.local/csi-preprocess-20261031-r2/pipeline-routed-csi-incremental.dcp}
puts "INCREMENTAL_BASELINE_READ_COMPLETED"
} result]} {puts $result; puts $::errorInfo; exit 1}
exit
