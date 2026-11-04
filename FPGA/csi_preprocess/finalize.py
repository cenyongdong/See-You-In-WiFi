"""Summarize retained measurements and the actual installed idle configuration."""
from run import ROOT, WORK
import json
r = WORK / 'reports'
def read(p):
    return json.loads(p.read_text())
run = next((r / 'board-evidence/board/runs').iterdir())
outcome = read(run / 'outcome.json')
state = outcome['final_status']
ident = read(r / 'board-evidence/board/identity.json')
package = read(r / 'package-review.json')
request = read(run / 'request.json')
benchmark = read(r / 'benchmark.json')
comparison = read(r / 'npu-comparison.json')
events = []
for p in (run / 'run').glob('recent-*.jsonl'):
    events.extend(json.loads(line) for line in p.read_text().splitlines() if line.strip())
csi = max((v for v in events if v.get('event') == 'csi_pl'), key=lambda v: v['calls'])
overlays = [v for v in events if v.get('event') == 'overlay_adopted']
pc = {}
for mode in ('raw', 'view'):
    rows = (r / 'pc' / (mode + '.stdout.log')).read_text().splitlines()
    pc[mode] = next(json.loads(line) for line in reversed(rows) if line.startswith('{'))
exit_rows = read(r / 'pc/exit.json')
assert outcome['native_exit'] == 0 and outcome['native_shutdown_complete'] and not outcome['device_owners']
assert csi['calls'] == state['inferred'] and csi['faults'] == csi['fallbacks'] == 0
assert all(v['native_exit'] == 0 for v in exit_rows)
visual = read(r / 'visual-confirmation.json') if (r / 'visual-confirmation.json').exists() else None
summary = dict(status='finite_board_validation_completed_idle', boot_id=request['boot_id'],
    hardware_profile=ident['hardware_profile'], BOOT_sha256=ident['BOOT_sha256'], software_sha256=ident['files']['pose180_demo'],
    candidate_operations=dict(BOOT_installs=1, normal_reboots=1, GP_benchmark_invocations=1, SDK_attempts=1,
    fallbacks=0),
    package_closed=True, remaining_operations=0, native_exit=outcome['native_exit'], seconds=outcome['seconds'],
    native_shutdown_complete=True, device_owners=[], input_frames=state['received'], inferred=state['inferred'],
    hdmi_adopted=state['adopted'], replaced=state['replaced'], csi_cumulative=csi,
    board_record_dropped=state['record_dropped'],
    overlay_retained_events=len(overlays), overlay_underflow_seen=max(v['overlay_underflow_seen'] for v in overlays),
    pc_raw_received=pc['raw']['received'], pc_view_received=pc['view']['received'], pc_raw_recorded=pc['raw']['recorded'],
    pc_raw_record_drops=pc['raw']['recordDrops'], pc_retained_full_records=comparison['pl_records'], pc_observers_ended=True,
    physical_screen=visual if visual else 'No onsite confirmation recorded for this run; previous confirmations are not reused.',
    CPU_time_reduction_percent=100 * (1 - benchmark['PL_CPU_ms_per_window'] / benchmark['PS_CPU_ms_per_window']),
    latency_change_percent=100 * (benchmark['PL_wall_ms_per_window'] / benchmark['PS_wall_ms_per_window'] - 1),
    SDK_autostart=False, live_CSI_tested_this_round=False, long_duration_tested=False, power_measured=False,
    post_test_state='CSI r3 streaming BOOT installed and running, SDK closed. Startup consumed; prepare a normal reboot and preflight before another demonstration.',
    evidence=dict(qualification='qualification-closure.json', benchmark='benchmark.json', NPU_comparison='npu-comparison.json',
    board_archive='board-evidence.tar.gz', board_archive_sha256=(r / 'board-evidence.sha256').read_text().split()[0],
    performance_figure='optimization-comparison.png', PC='pc/', prior_failed_revision='../../csi-preprocess-20261031-r1/reports/board-failure-summary.json',
    software_optimization='../../csi-optimization-20261031-r1/reports/board-results.tar.gz'))
(r / 'final-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
default = ROOT / 'FPGA/hdmi_candidate/default_boot.json'
v = read(default)
v.update(hardware_profile=ident['hardware_profile'], hardware_work=str(WORK.relative_to(ROOT)).replace('\\',
    '/'),
    BOOT_path=str(WORK / 'boot-package/BOOT-csi-preprocess.bin'), BOOT_sha256=ident['BOOT_sha256'], runtime_boot_id=summary['boot_id'],
    release_state='finite_onsite_validated_installed_manual_start_only' if visual else 'finite_remote_validated_candidate_installed_manual_start_only',
    release_evidence=str((r / 'final-summary.json').relative_to(ROOT)).replace('\\', '/'),
    software_path=str((WORK / ident['package'] / 'board/pose180_demo').relative_to(ROOT)).replace('\\',
    '/'), software_sha256=ident['files']['pose180_demo'],
    last_validated_input='official_dataset/' + request['input']['split'] + '/' + str(state['received']) + ' input windows, ' + str(state['dataset_passes']) + ' pass; ' + request['input']['sequence'],
    device_connection_state='connected_idle_after_CSI_streaming_validation', startup_consumed_this_boot=True,
    runtime_identity_scope='CSI streaming finite GP comparison and one real SDK run completed; no current owners. Visual scope is recorded in the release evidence.',
    previous_qualified_BOOT_path='.local/csi-preprocess-20261031-r2/boot-package/BOOT-csi-preprocess.bin',
    previous_qualified_BOOT_sha256=package['baseline_BOOT_sha256'])
default.write_text(json.dumps(v, indent=2) + '\n')
print(json.dumps({k: summary[k] for k in ('status', 'inferred', 'hdmi_adopted', 'CPU_time_reduction_percent',
    'latency_change_percent', 'csi_cumulative', 'pc_raw_received', 'pc_retained_full_records')}))
