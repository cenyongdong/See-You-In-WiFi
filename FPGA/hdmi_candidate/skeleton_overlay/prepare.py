"""Isolated overlay integration, reusing the released filter-v1 build/IP caches."""
from pathlib import Path
import json, shutil
from run import ROOT,SRC,WORK,prepare
BASE=ROOT/'.local/pose-filter-integration-20261026-r2'
REF=ROOT/'.local/hdmi-boot-witness-20261019-r23/reference/rtl/hdmi_candidate'
prepare()
sources=WORK/'sources';sources.mkdir(exist_ok=True)
reports=WORK/'reports'
for name in ('physical','pipeline-physical','physical-final'):(reports/name).mkdir(exist_ok=True)
for p in (BASE/'sources').iterdir():
    if p.is_file():shutil.copyfile(p,sources/p.name)
value=(BASE/'sources/ps_ai_peripheral.sv').read_text()
anchor="hdmi_cam_router #(.HDMI_BASE(32'h400b0000)) hdmi_router"
value=value.replace('.upstream(filter_passthrough.slave),.camera(cam_legacy.master)',
                    '.upstream(overlay_passthrough.slave),.camera(cam_legacy.master)')
block='''mna_gp_ww_itf overlay_csr(),overlay_passthrough();
hdmi_cam_router #(.HDMI_BASE(32'h400b2000)) overlay_router(
 .clk(gp_clk),.resetn(~gp_clk_rst),.upstream(filter_passthrough.slave),
 .camera(overlay_passthrough.master),.hdmi(overlay_csr.master));
'''
assert value.count(anchor)==1
value=value.replace(anchor,block+anchor).replace('.csr(hdmi_csr.slave),','.csr(hdmi_csr.slave),.overlay_csr(overlay_csr.slave),')
(sources/'ps_ai_peripheral.sv').write_text(value)
board=(REF/'hdmi_board.sv').read_text().replace('mna_gp_ww_itf.slave csr,','mna_gp_ww_itf.slave csr,mna_gp_ww_itf.slave overlay_csr,')
anchor='    uihdmitx #(.FAMILY("7FAMILY")) transmitter('
block='''    wire overlay_hs,overlay_vs,overlay_de;wire [23:0] overlay_rgb;
    skeleton_overlay overlay(
     .clk(csr_clk),.resetn(csr_resetn),
     .wr_valid(overlay_csr.awwvalid),.wr_addr(overlay_csr.awwaddr[7:0]),.wr_data(overlay_csr.awwdata),.wr_ready(overlay_csr.awwready),
     .rd_valid(overlay_csr.arvalid),.rd_addr(overlay_csr.araddr[7:0]),.rd_ready(overlay_csr.arready),
     .rsp_valid(overlay_csr.rvalid),.rsp_data(overlay_csr.rdata),.rsp_ready(overlay_csr.rready),
     .pclk(pixel_clk),.presetn(pixel_resetn),.hs(hs),.vs(vs),.de(de),
     .rgb(pattern_pixel[1] ? pattern_rgb : rgb),.hide(safe_idle | pattern_pixel[1]),
     .out_hs(overlay_hs),.out_vs(overlay_vs),.out_de(overlay_de),.out_rgb(overlay_rgb));
'''
board=board.replace(anchor,block+anchor).replace('.HS_i(hs),.VS_i(vs),.VDE_i(de)',
 '.HS_i(overlay_hs),.VS_i(overlay_vs),.VDE_i(overlay_de)').replace('.RGB_i(pattern_pixel[1] ? pattern_rgb : rgb)', '.RGB_i(overlay_rgb)')
(sources/'hdmi_board.sv').write_text(board)
for name in ('overlay.sv','palette_fifo.sv','font_rom.vh'):shutil.copyfile(SRC/name,sources/name)
def remap(v):return v.replace(BASE.as_posix(),WORK.as_posix())
for stage in ('synthesis','opt','place','route','report','bit'):
    v=remap((BASE/'reports'/(stage+'.tcl')).read_text())
    if stage=='synthesis':
        v=v.replace((REF/'hdmi_board.sv').as_posix(),(sources/'hdmi_board.sv').as_posix())
        v=v.replace('synth_design -top',f'read_verilog -sv [list {{{(sources/"palette_fifo.sv").as_posix()}}} {{{(sources/"overlay.sv").as_posix()}}}]\nset_property include_dirs {{{sources.as_posix()}}} [current_fileset]\nsynth_design -top')
    if stage=='place':
        v=v.replace((ROOT/'.local/hdmi-probe-free-drain-20261026-r1/pipeline-scoped.dcp').as_posix(),(BASE/'pipeline-routed.dcp').as_posix())
    if stage=='opt':
        v=v.replace('opt_design\n',f'source {{{(SRC/"overlay_cdc.tcl").as_posix()}}}\nopt_design\n')
    if stage=='report':
        v=v.replace('close $f','''report_utilization -cells [get_cells U0_ps_ai_peripheral/hdmi_display/overlay] -file $out/overlay-utilization.rpt
report_cdc -details -cells [get_cells U0_ps_ai_peripheral/hdmi_display/overlay] -file $out/overlay-cdc.rpt
close $f''')
    (reports/(stage+'.tcl')).write_text(v)
for name in ('run_stage.py','qualify.py','call_procise_disable_icap.bat','procise_run_disable_icap.tcl'):
    v=remap((BASE/name).read_text())
    if name=='qualify.py':
        v=v.replace('new_timing_exceptions=False', 'new_timing_waivers=False')
        v=v.replace("sources += list((WORK/'sources').iterdir())", "sources += list((WORK/'sources').iterdir())\n    sources += [ROOT/'FPGA/hdmi_candidate/skeleton_overlay/overlay_cdc.tcl']")
        v=v.replace("filter_resources=resources(R/'filter-utilization.rpt')", "overlay_resources=resources(R/'overlay-utilization.rpt')\n    filter_resources=resources(R/'filter-utilization.rpt')")
        v=v.replace("filter_budget_pass=within_budget)", "filter_budget_pass=within_budget, overlay_resources=overlay_resources, new_CDC_max_delay_bounds=True, new_false_paths=False)")
    (WORK/name).write_text(v)
manifest=json.loads((BASE/'manifest.json').read_text())
manifest.update(profile='probe-free-drain-overlay-v1',deployment_qualified=False,overlay_ABI='0x534b4c01',overlay_CSR='0x400b2000',overlay_resolution=[960,540],baseline=str(BASE),board_tested=False)
(WORK/'manifest.json').write_text(json.dumps(manifest,indent=2))
print('Prepared',WORK,'No board operation')
