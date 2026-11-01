if {[catch {
set_param general.maxThreads 2
open_checkpoint {D:/FPGACompetitionProject/.local/frb1101-r1/build/.local/csi-preprocess-20261031-r3/pipeline-physopt-csi-incremental.dcp}
source {D:/FPGACompetitionProject/.local/frb1101-r1/build/FPGA/hdmi_candidate/probe_free_drain/strip_probe_attributes.tcl}
if {[catch {route_design -directive Explore} route_error]} {
 catch {report_route_status -file {D:/FPGACompetitionProject/.local/frb1101-r1/build/.local/csi-preprocess-20261031-r3/reports/physical/failed-route-csi-incremental-status.rpt}}
 catch {report_timing_summary -max_paths 10 -report_unconstrained -file {D:/FPGACompetitionProject/.local/frb1101-r1/build/.local/csi-preprocess-20261031-r3/reports/physical/failed-route-csi-incremental-timing.rpt}}
 catch {write_checkpoint -force {D:/FPGACompetitionProject/.local/frb1101-r1/build/.local/csi-preprocess-20261031-r3/pipeline-route-csi-incremental-failed.dcp}}
 catch {report_route_status -route_type CONFLICTS -list_all_nets -show_all -file {D:/FPGACompetitionProject/.local/frb1101-r1/build/.local/csi-preprocess-20261031-r3/reports/direct-conflicts.rpt}}
 error $route_error
}
source {D:/FPGACompetitionProject/.local/frb1101-r1/build/FPGA/hdmi_candidate/baselines/ps_release_r26/sources/implementation_route_post.tcl}
write_checkpoint -force {D:/FPGACompetitionProject/.local/frb1101-r1/build/.local/csi-preprocess-20261031-r3/pipeline-routed-csi-incremental.dcp}
} result]} {puts $result; puts $::errorInfo; exit 1}
exit
