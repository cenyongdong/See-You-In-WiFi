if {[catch {
set_device JFMQL30TAI676H
create_boot_image {D:/FPGACompetitionProject/.local/r7-board-20261104-r1/boot/candidate.bif} {D:/FPGACompetitionProject/.local/r7-board-20261104-r1/boot/BOOT.BIN} -fmql
} message]} {puts $message; exit 1}
exit
