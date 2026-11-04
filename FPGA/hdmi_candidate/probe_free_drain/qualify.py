"""Qualify actual routed hardware, retaining only the established AI/GT scope."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
WORK = ROOT / '.local/hdmi-probe-free-drain-20261026-r1'
E = ROOT / 'tools/pose-v1/evidence/hdmi-probe-free-drain-20261026-r1'
R = E / 'physical-final'

def need(value, message):
    if not value:
        raise RuntimeError(message)

def main():
    for stage in ('synthesis', 'opt', 'place', 'route', 'scope_fix', 'report_final'):
        row = json.loads((E / (stage + '-execution.json')).read_text())
        need(row['native_exit'] == 0, 'Native stage failed: ' + stage)
    timing = (R / 'timing-final.rpt').read_text()
    lines = timing.splitlines()
    header = next(i for i, line in enumerate(lines) if 'WNS(ns)' in line and 'TNS(ns)' in line)
    values = next(line.split() for line in lines[header + 1:] if re.match(r'^\s*-?\d+\.\d+\s', line))
    need(len(values) == 12, 'Timing summary format requires inspection')
    wns, tns, whs, ths = [float(values[i]) for i in (0, 1, 4, 5)]
    need(wns >= 0 and whs >= 0 and tns == ths == 0 and values[2] == values[6] == '0', 'Setup/hold failed')
    for pattern in (r'There are\s+0\s+pins that are not constrained for maximum delay\.', r'There are\s+0\s+register/latch pins with no clock\.'):
        need(re.search(pattern, timing), 'Internal timing/clock coverage incomplete')
    prefix = 'U0_ps_ai_peripheral/ZGolo/u_AI_Mate_top/clkrst_wrapper_u0/AI_CORE_CLK/inst/'
    allowed = {prefix + 'clkout1_buf/I': (1.409, 1.0, -0.409), prefix + 'plle2_adv_inst/CLKOUT0': (1.071,
        1.0, -0.071)}
    exceptions = []
    for line in lines:
        match = re.search(r'\s(-\d+\.\d+)\s+\S+\s+(\S+)\s*$', line)
        if not match or not re.match(r'^(Min Period|Max Period|Low Pulse Width|High Pulse Width)\s', line):
            continue
        actual = tuple(float(x) for x in line.split() if re.fullmatch(r'-?\d+\.\d+', x))
        need(line.startswith('Min Period') and match[2] in allowed and actual == allowed[match[2]], 'New/changed pulse failure: ' + line)
        exceptions.append(line)
    need(len(exceptions) == 2 and int(values[10]) == 2, 'Only the two original AI exceptions are permitted')
    need('VIOLATED' not in (R / 'bus-skew-final.rpt').read_text(), 'Bus skew failed')
    route = (R / 'route-status-final.rpt').read_text()
    def count(label):
        match = re.search(r'# of ' + re.escape(label) + r'\.+\s*:\s*(\d+)\s*:', route)
        need(match, 'Missing native route field: ' + label)
        return int(match[1])
    routable = count('routable nets')
    need(routable > 0 and count('fully routed nets') == routable and count('nets with routing errors') == 0,
        'Routing incomplete')
    drc = (R / 'drc-final.rpt').read_text()
    errors = re.findall(r'^(\S+#\d+)\s+Error\s*\n(.*?)(?=^\S+#\d+\s|\Z)', drc, re.M | re.S)
    legacy = {'REQP-52': 'rx_sdi_inst/SDI0/SDI/GTX_i/gtxe2_i', 'REQP-56': 'rx_sdi_inst/gtxe2_common_0/gtxe2_common_i'}
    for name, body in errors:
        need(name.split('#')[0] in legacy and re.findall(r'\bcell\s+(\S+?):', body) == [legacy[name.split('#')[0]]],
            'New DRC error: ' + name)
    facts = [line.split('\t') for line in (R / 'final-native-facts.tsv').read_text().splitlines()]
    need(['PART', 'xc7z030ffg676-2'] in facts, 'Wrong actual target')
    removed = [row for row in facts if row[0] == 'REMOVED']
    need(len(removed) == 5 and all(row[-1] == '0' for row in removed), 'Instrumentation remains')
    need(['DEBUG_CORES', '0'] in facts and ['MARK_DEBUG', '0'] in facts, 'Debug core/probe marks remain')
    retained = [row for row in facts if row[0] == 'RETAINED']
    need({row[1] for row in retained} == {'deferred_control', 'startup_drain'} and all(int(row[2]) > 0 for row in retained),
        'Active consumer missing')
    need(['FORBIDDEN_MODULES', '0'] in facts, 'Diagnostic/protocol modules remain')
    control = [line.split('\t') for line in (R / 'control-cdc.tsv').read_text().splitlines()]
    need({row[0] for row in control if not row[0].endswith('_ENDPOINT')} == {'TOGGLE', 'REPLY', 'COMMAND'},
        'Control CDC checks incomplete')
    need(all(float(row[-1]) >= 0 for row in control), 'Functional control timing failed')
    reset = [row for row in facts if row[0] == 'CONSUMER_RESET']
    need(reset and all(float(row[-2]) == 5 and float(row[-1]) >= 0 for row in reset), 'Consumer reset bound missing/failing')
    ready = [row for row in facts if row[0] == 'READY']
    need(ready and all(abs(float(row[-2]) - 5) < .001 and float(row[-1]) >= 0 for row in ready), 'HP2 readiness absent/cut/failing')
    connected = [row for row in facts if row[0] == 'S01_CONNECTED']
    need({row[1] for row in connected} == {'ARVALID', 'ARADDR', 'RREADY'} and all(row[2] and row[2] != 'GND' for row in connected),
        'HDMI S01 not connected')
    sources = list((HERE / 'sources').iterdir()) + [HERE / 'strip_probe_attributes.tcl'] + [E / (name + '.tcl') for name in ('synthesis',
        'opt', 'place', 'route', 'scope_fix', 'report_final')]
    result = dict(bit_generation_prerequisite_pass=True, raw_timing_pass=False, WNS_ns=wns, WHS_ns=whs,
        TNS_ns=tns, THS_ns=ths,
        approved_AI_period_exceptions=exceptions, new_timing_exceptions=False, new_DRC_waivers=False,
        unconstrained_internal_endpoints=0, routable_nets=routable, fully_routed_nets=routable,
        removed_diagnostic_hierarchies=[row[1] for row in removed], retained_active_hierarchies=[row[1] for row in retained],
        checkpoint=str(WORK / 'pipeline-scoped.dcp'),
        reused_factory_inputs='r45 synthesis/opt input list; original PS export and OOC IP checkpoints',
        source_sha256={str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in sources},
        board_tested=False)
    (E / 'qualification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: result[key] for key in ('bit_generation_prerequisite_pass', 'WNS_ns', 'WHS_ns',
        'raw_timing_pass')}))

if __name__ == '__main__':
    main()
