@echo off
set "PROCISE_DIR=C:/FudanMicro/Procise"
set "TCL_LIBRARY=%PROCISE_DIR%/tcl8.4"
set "PATH=%PROCISE_DIR%/dll;%PROCISE_DIR%/bin;%PATH%"
set "ICTIME_HOME=%PROCISE_DIR%"
set "APP_DIR=%PROCISE_DIR%"
set "FMSH_DB=%PROCISE_DIR%/db"
"%PROCISE_DIR%/bin/procise.exe" "D:/FPGACompetitionProject/.local/r7-board-20261104-r1/boot/generate.tcl"
