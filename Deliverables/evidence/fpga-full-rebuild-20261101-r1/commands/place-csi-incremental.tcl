if {[catch {
set_param general.maxThreads 2
open_checkpoint {D:/FPGACompetitionProject/.local/frb1101-r1/build/.local/csi-preprocess-20261031-r3/pipeline-opt-banked.dcp}
read_checkpoint -incremental {D:/FPGACompetitionProject/.local/frb1101-r1/build/.local/csi-preprocess-20261031-r2/pipeline-routed-csi-incremental.dcp}
# Reapply the existing 030ai placement-only GT adaptation after reopening DCP.
# Final DRC is run with these checks restored; no new exception is added.
if {[get_property PART [current_project]] ne "xc7z030ffg676-2"} {error "Unexpected target"}
foreach spec {{rx_sdi_inst/SDI0/SDI/GTX_i/gtxe2_i GTXE2_CHANNEL} {rx_sdi_inst/gtxe2_common_0/gtxe2_common_i GTXE2_COMMON}} {
 lassign $spec name ref
 set c [get_cells -quiet $name]
 if {[llength $c]!=1 || [get_property REF_NAME $c] ne $ref} {error "Approved GT target changed: $name"}
}
set approved_gt_drc [get_drc_checks {REQP-52 REQP-56}]
if {[llength $approved_gt_drc]!=2} {error "Existing GT adaptation checks missing"}
set_property IS_ENABLED 0 $approved_gt_drc
puts "EXISTING_030AI_GT_PLACEMENT_ADAPTATION REQP-52 REQP-56"
place_design -directive Explore
write_checkpoint -force {D:/FPGACompetitionProject/.local/frb1101-r1/build/.local/csi-preprocess-20261031-r3/pipeline-placed-csi-incremental.dcp}
phys_opt_design -directive AggressiveExplore
set_property IS_ENABLED 1 $approved_gt_drc
puts "GT_DRC_RESTORED [get_property IS_ENABLED $approved_gt_drc]"
write_checkpoint -force {D:/FPGACompetitionProject/.local/frb1101-r1/build/.local/csi-preprocess-20261031-r3/pipeline-physopt-csi-incremental.dcp}
report_timing_summary -max_paths 10 -report_unconstrained -file {D:/FPGACompetitionProject/.local/frb1101-r1/build/.local/csi-preprocess-20261031-r3/reports/physical/physopt-csi-incremental-timing.rpt}
} result]} {puts $result; puts $::errorInfo; exit 1}
exit
