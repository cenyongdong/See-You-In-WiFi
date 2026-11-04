"""Remove passive r45 diagnostics while retaining its bounded startup consumer."""
from pathlib import Path
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'sources'
BASE = ROOT / 'FPGA/hdmi_candidate/diagnostics/deferred_consume_r45/sources'
PREV = ROOT / 'FPGA/hdmi_candidate/probe_free'
ID = 'hdmi-probe-free-drain-20261026-r1'
WORK = ROOT / '.local' / ID
EVIDENCE = ROOT / 'tools/pose-v1/evidence' / ID
OLD_WORK = ROOT / '.local/hdmi-probe-free-20261025-r1'
OLD_E = ROOT / 'tools/pose-v1/evidence/hdmi-probe-free-20261025-r1'

def put(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')

def remap(text):
    return text.replace(OLD_WORK.as_posix(), WORK.as_posix()).replace(OLD_E.as_posix(), EVIDENCE.as_posix()).replace(PREV.as_posix(),
        HERE.as_posix())

def main():
    if (EVIDENCE / 'synthesis-process.json').exists():
        raise RuntimeError('Build already started; preserve its source and logs')
    WORK.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / 'physical').mkdir(parents=True, exist_ok=True)
    (EVIDENCE / 'pipeline-physical').mkdir(exist_ok=True)
    # Keep only reset outputs needed by the active consumer; remove bus probes.
    names = re.findall(r'\bdiagnostic_\w+', (BASE / 'ps_ai.v').read_text())
    removed = set(names) - {'diagnostic_ps_resetn', 'diagnostic_hp2_resetn'}
    renames = {'diagnostic_ps_resetn': 'drain_ps_resetn', 'diagnostic_hp2_resetn': 'drain_pl_resetn'}
    for name in ('ps_ai.v', 'ps_ai_wrapper.sv', 'ps_ai_peripheral.sv'):
        text = (BASE / name).read_text()
        if name == 'ps_ai_peripheral.sv':
            start = text.index('// r37: S01 HDMI')
            end = text.index("hdmi_cam_router #(.HDMI_BASE(32'h400b0000)) hdmi_router", start)
            original = text[start: end]
            consumer = original[original.index('// r38: bounded S01'):]
            consumer = consumer.replace('wire drain_request_activity = ', 'wire drain_request_activity = drain_ps_request | ')
            control = '''// One functional CSR aperture; no passive diagnostic routers or IP.
mna_gp_ww_itf drain_control_csr(),drain_control_passthrough();
wire drain_arm;
hdmi_cam_router #(.HDMI_BASE(32'h400b0800)) drain_control_router(
 .clk(gp_clk),.resetn(~gp_clk_rst),.upstream(cam.slave),
 .camera(drain_control_passthrough.master),.hdmi(drain_control_csr.master));
hp2_deferred_control deferred_control(
 .source_clk(hp_clk),.csr_clk(gp_clk),.csr_resetn(~gp_clk_rst),.csr(drain_control_csr.slave),
 .ps_resetn(drain_ps_resetn),.pl_resetn(drain_pl_resetn),.hp_reset(hp_clk_rst),
 .any_request(drain_request_activity),.reader_ready(hdmi_reader_rready),
 .rvalid(S_AXI_HP2_RVALID),.rid(S_AXI_HP2_RID),.rresp(S_AXI_HP2_RRESP),
 .rlast(S_AXI_HP2_RLAST),.ps_rvalid(drain_ps_rvalid),
 .drain_status(startup_drain_status),.arm(drain_arm));
'''
            text = text[: start] + control + consumer + text[end:]
            text = text.replace('.upstream(diag_passthrough.slave)', '.upstream(drain_control_passthrough.slave)')
            text = '\n'.join(line for line in text.splitlines() if not re.search(r'ai_read_channels|mna_gp_ww_itf (?:diag_passthrough|ai_diag_csr|read_diag_passthrough|ai_read_csr)',
                line)) + '\n'
            text = text.replace('  wire diagnostic_ps_resetn;', '  wire diagnostic_ps_resetn;\nwire drain_ps_rvalid,drain_ps_request,drain_pl_resetn;')
            text = text.replace('    .diagnostic_ps_resetn(diagnostic_ps_resetn),', '    .diagnostic_ps_resetn(diagnostic_ps_resetn),\n    .drain_ps_rvalid(drain_ps_rvalid),.drain_ps_request(drain_ps_request),')
        elif name == 'ps_ai.v':
            start = text.index('  assign diagnostic_hp2_write[31:0]')
            end = text.index('endmodule', start)
            text = text[: start] + '''  assign diagnostic_hp2_resetn = proc_sys_reset_1_peripheral_aresetn;
  assign drain_ps_rvalid = axi_interconnect_4_M00_AXI_RVALID;
  assign drain_ps_request = axi_interconnect_4_M00_AXI_ARVALID |
      axi_interconnect_4_M00_AXI_AWVALID | axi_interconnect_4_M00_AXI_WVALID;
''' + text[end:]
            start = text.index('module ps_ai\n')
            end = text.index(');', start)
            header = re.sub(r'\s*diagnostic_\w+\s*,?', '', text[start: end]).rstrip().rstrip(',')
            header += ',\n    drain_ps_resetn,drain_pl_resetn,drain_ps_rvalid,drain_ps_request\n'
            body = text[end + 2:]
            body = re.sub(r'^\s*output[^;\n]*diagnostic_[^;\n]*;\n', '', body, flags=re.M)
            text = text[: start] + header + ');\n  output drain_ps_resetn,drain_pl_resetn,drain_ps_rvalid,drain_ps_request;\n' + body
        else:
            text = text.replace('    output diagnostic_ps_resetn,', '    output diagnostic_ps_resetn,\n    output drain_ps_rvalid,drain_ps_request,')
            text = text.replace('  .diagnostic_ps_resetn(diagnostic_ps_resetn),', '  .diagnostic_ps_resetn(diagnostic_ps_resetn),\n  .drain_ps_rvalid(drain_ps_rvalid),.drain_ps_request(drain_ps_request),')
        text = '\n'.join(line for line in text.splitlines() if not any(re.search(r'\b' + field + r'\b',
            line) for field in removed)) + '\n'
        for before, after in renames.items():
            text = text.replace(before, after)
        text = re.sub(r',\s*\);', '\n);', text)
        text = re.sub(r'\(\*\s*(?:DEBUG\s*=\s*"true"|MARK_DEBUG(?:\s*=\s*"true")?)\s*\*\)\s*', '', text)
        put(SOURCE / name, text)
    shutil.copyfile(BASE / 'hp2_startup_drain.sv', SOURCE / 'hp2_startup_drain.sv')
    for name in ('hdmi_cdc.tcl', 'ps_release_factory_clocks.tcl'):
        text = (PREV / 'sources' / name).read_text()
        text = text.replace('NAME !~ U0_ps_ai_peripheral/hdmi_display/*', 'NAME !~ U0_ps_ai_peripheral/hdmi_display/* && NAME !~ U0_ps_ai_peripheral/deferred_control/* && NAME !~ U0_ps_ai_peripheral/startup_drain/*')
        text = text.replace('NAME =~ U0_ps_ai_peripheral/hdmi_display/*', 'NAME =~ U0_ps_ai_peripheral/hdmi_display/* || NAME =~ U0_ps_ai_peripheral/deferred_control/* || NAME =~ U0_ps_ai_peripheral/startup_drain/*')
        put(SOURCE / name, text)
    for name in ('deferred_control_cdc.tcl', 'deferred_control_validate.tcl', 'startup_drain_bounds.tcl'):
        shutil.copyfile(BASE / name, SOURCE / name)
    shutil.copyfile(PREV / 'strip_probe_attributes.tcl', HERE / 'strip_probe_attributes.tcl')
    for stage in ('synthesis', 'opt', 'place', 'route'):
        text = remap((OLD_E / (stage + '.tcl')).read_text())
        if stage == 'synthesis':
            pos = text.index('synth_design ')
            text = text[: pos] + 'read_verilog -sv {' + (SOURCE / 'hp2_startup_drain.sv').as_posix() + '}\nread_verilog -sv {' + (SOURCE / 'hp2_deferred_control.sv').as_posix() + '}\n' + text[pos:]
        if stage == 'opt':
            addition = '\n'.join('source {' + (SOURCE / name).as_posix() + '}' for name in ('consumer_capture_scope.tcl',
                'deferred_control_cdc.tcl', 'startup_drain_bounds.tcl'))
            text = text.replace('\nopt_design\n', '\n' + addition + '\nopt_design\n')
        if stage == 'place':
            text = text.replace((ROOT / '.local/hp2-deferred-consume-20261024-r45/pipeline-routed.dcp').as_posix(),
                (OLD_WORK / 'pipeline-routed.dcp').as_posix())
        put(EVIDENCE / (stage + '.tcl'), text)
    for name in ('run_stage.py', 'prepare_bit.py'):
        text = (PREV / name).read_text().replace('hdmi-probe-free-20261025-r1', ID).replace('BOOT-probe-free-r1.bin',
            'BOOT-probe-free-drain-r1.bin')
        put(HERE / name, text)
    state = dict(status='prepared', source_baseline='qualified r45', removed=['event/read monitors', 'startup witness',
        'cycle/protocol trace', 'AXI protocol checker', 'MARK_DEBUG'], retained=['unchanged hp2_startup_drain',
        'one-shot control with bounded CDC', 'functional HDMI error/STOP/drain', 'AI four ports'], scope='3 independent candidate starts, each 300 seconds real CSI -> PS/NPU -> HDMI; optional PC observer',
        candidate_starts=0, SDK_Open=0, original_fallbacks=0)
    put(EVIDENCE / 'state.json', json.dumps(state, indent=2) + '\n')
    print(json.dumps(state))

if __name__ == '__main__':
    main()
