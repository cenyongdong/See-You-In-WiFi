foreach f {
D:/FPGACompetitionProject/.local/fpga-package-r4-check/.local/csi-preprocess-20261031-r3/pipeline-opt-banked.dcp
D:/FPGACompetitionProject/.local/csi-preprocess-20261031-r3/pipeline-opt-banked.dcp
D:/FPGACompetitionProject/.local/csi-preprocess-20261031-r3/pipeline-routed-csi-incremental.dcp
} {
open_checkpoint $f
puts "CHECKPOINT $f"
set bb [get_cells -hier -filter {IS_BLACKBOX == 1}]
foreach c $bb {puts "BLACKBOX $c";report_property $c}
close_design
}
exit
