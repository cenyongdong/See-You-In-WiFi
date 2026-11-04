"""Integrate the GP-only CSI core into a copy of the qualified overlay source.
Reuses factory IP and existing CDC constraints; no incremental/greedy routing.
"""
from pathlib import Path
import shutil, json
from run import ROOT, SRC, WORK
BASE = ROOT / '.local/skeleton-overlay-20261031-r2'
s = WORK / 'sources'
s.mkdir(exist_ok=True)
(WORK / 'ip_patch').mkdir(exist_ok=True)
r = WORK / 'reports'
for d in ('physical', 'pipeline-physical', 'physical-final-closure'):
    (r / d).mkdir(exist_ok=True)
for p in (BASE / 'sources').iterdir():
    if p.is_file():
        shutil.copyfile(p, s / p.name)
for name in ('polar.sv', 'batch.sv', 'atan_table.vh'):
    shutil.copyfile(SRC / name, s / name)
v = (s / 'ps_ai_peripheral.sv').read_text()
anchor = "hdmi_cam_router #(.HDMI_BASE(32'h400b0000)) hdmi_router"
assert v.count(anchor) == 1
v = v.replace('.upstream(overlay_passthrough.slave),.camera(cam_legacy.master)',
    '.upstream(csi_passthrough.slave),.camera(cam_legacy.master)')
v = v.replace(anchor, '''mna_gp_ww_itf csi_csr(),csi_passthrough();
hdmi_cam_router #(.HDMI_BASE(32'h400b3000)) csi_router(
 .clk(gp_clk),.resetn(~gp_clk_rst),.upstream(overlay_passthrough.slave),
 .camera(csi_passthrough.master),.hdmi(csi_csr.master));
csi_batch csi_preprocessor(
 .clk(gp_clk),.resetn(~gp_clk_rst),
 .wr_valid(csi_csr.awwvalid),.wr_addr(csi_csr.awwaddr[7:0]),.wr_data(csi_csr.awwdata),.wr_ready(csi_csr.awwready),
 .rd_valid(csi_csr.arvalid),.rd_addr(csi_csr.araddr[7:0]),.rd_ready(csi_csr.arready),
 .rsp_valid(csi_csr.rvalid),.rsp_data(csi_csr.rdata),.rsp_ready(csi_csr.rready));
''' + anchor)
(s / 'ps_ai_peripheral.sv').write_text(v)
for stage in ('synthesis', 'opt', 'place-nonincremental', 'route-direct', 'physopt-direct', 'report-closure',
    'bit-closure'):
    v = (BASE / 'reports' / (stage + '.tcl')).read_text().replace(BASE.as_posix(), WORK.as_posix())
    # Existing patched factory IP is an input, not an output of this candidate.
    if stage != 'bit-closure':
        v = v.replace((WORK / 'ip_patch').as_posix(), (BASE / 'ip_patch').as_posix())
    if stage == 'synthesis':
        v = v.replace('synth_design -top', f'read_verilog -sv [list {{{(s/"polar.sv").as_posix()}}} {{{(s/"batch.sv").as_posix()}}}]\nsynth_design -top')
    if stage == 'report-closure':
        v = v.replace('close $f', '''report_utilization -cells [get_cells U0_ps_ai_peripheral/csi_preprocessor] -file $out/csi-utilization.rpt
set csi_regs [get_cells -hier -filter {NAME =~ U0_ps_ai_peripheral/csi_preprocessor/* && IS_SEQUENTIAL == 1}]
set csi_clocks [get_clocks -of_objects [get_pins -of_objects $csi_regs -filter {IS_CLOCK == 1}]]
if {![llength $csi_clocks]} {error "CSI clock missing"}
foreach c $csi_clocks {if {abs([get_property PERIOD $c]-10)>0.001} {error "CSI changed GP clock"}}
foreach mode {max min} {
 set p [get_timing_paths -delay_type $mode -to $csi_regs -max_paths 1]
 if {![llength $p]} {error "CSI timing coverage missing"}
 puts $f "CSI_TIMING\\t$mode\\t[get_property SLACK $p]"
}
close $f''')
    (r / (stage + '.tcl')).write_text(v)
shutil.copyfile(BASE / 'run_stage.py', WORK / 'run_stage.py')
for name in ('call_procise_disable_icap.bat', 'procise_run_disable_icap.tcl'):
    (WORK / name).write_text((BASE / name).read_text().replace(BASE.as_posix(), WORK.as_posix()))
manifest = json.loads((BASE / 'manifest.json').read_text())
manifest.update(profile='probe-free-drain-overlay-csi-v2', baseline=str(BASE),
    baseline_BOOT_sha256=json.loads((BASE / 'reports/package-review.json').read_text())['BOOT_sha256'],
    csi_CSR='0x400b3000', csi_ABI='0x43534902', samples=5400, GP_MHz=100,
    new_DMA_master=False, deployment_qualified=False, board_tested=False)
(WORK / 'manifest.json').write_text(json.dumps(manifest, indent=2))
v = (BASE / 'qualify_closure.py').read_text()
v = v.replace("overlay_resources=resources(R/'overlay-utilization.rpt')", "csi_resources=resources(R/'csi-utilization.rpt')\n    overlay_resources=resources(R/'overlay-utilization.rpt')")
v = v.replace('overlay_resources=overlay_resources,', 'overlay_resources=overlay_resources, csi_resources=csi_resources,')
v = v.replace("filter_timing = [row for row in facts if row[0]=='FILTER_TIMING']", "csi_timing = [row for row in facts if row[0]=='CSI_TIMING']\n    need({row[1] for row in csi_timing}=={'max','min'} and all(float(row[-1])>=0 for row in csi_timing), 'CSI setup/hold missing/failing')\n    filter_timing = [row for row in facts if row[0]=='FILTER_TIMING']")
v = v.replace("source_snapshot_note='After synthesis read, underflow_any declaration moved before its use for xvlog compatibility; no logic/expression/constraint changed. Source hashes describe the retained equivalent source, not the original declaration-order bytes.'",
    "source_snapshot_note='Retained CSI and overlay source snapshot used by synthesis; GP clock unchanged.'")
(WORK / 'qualify_closure.py').write_text(v)
print('Prepared CSI + retained overlay integration:', WORK)
