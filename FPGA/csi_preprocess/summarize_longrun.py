"""Report the actual finite run, cumulative checks, and sampled resource trends."""
from pathlib import Path
import json, statistics
from longrun import ROOT, WORK, NAME, save
r = WORK / 'reports'
e = r / 'board-evidence'
run = next((e / 'board/runs').iterdir())
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
rows = lambda p: [json.loads(s) for s in p.read_text(encoding='utf-8').splitlines() if s.strip()]
outcome = read(run / 'outcome.json')
complete = read(run / 'run/completion.json')
identity = read(e / 'board/identity.json')
status = outcome['final_status']
board = rows(e / 'monitor/samples.jsonl')
pc = rows(r / 'pc/samples.jsonl')
active = [v for v in board if (v.get('status') or {}).get('inferred', 0) > 0]
pc_active = [v for v in pc if v.get('raw', {}).get('connected') and v.get('raw', {}).get('received', 0) > 0]
view_fixed = (r / 'pc/view-fixed-exit.json').exists()
pc_end = {mode: next(json.loads(line) for line in reversed((r / 'pc' / ('view-fixed.stdout.log' if mode == 'view' and view_fixed else mode + '.stdout.log')).read_text().splitlines()) if line.startswith('{')) for mode in ('raw',
    'view')}
view_before = read(r / 'pc/view-restart-before.json') if view_fixed else None
pc_exits = read(r / 'pc/exit.json')
view_total = pc_end['view']['received'] + (view_before['received'] if view_before else 0)
csi = max((v['csi'] for v in board if 'csi' in v), key=lambda v: v['calls'])
for f in (run / 'run').glob('recent-*.jsonl'):
    for line in f.read_text(errors='replace').splitlines():
        try:
            v = json.loads(line)
        except ValueError:
            continue
        if v.get('event') == 'csi_pl' and v['calls'] > csi['calls']:
            csi = v
resource = [v['service-status.json'] for v in active if v.get('service-status.json', {}).get('RSS_KiB')]
warm = [v['service-status.json'] for v in active if v['monotonic'] - active[0]['monotonic'] >= 60 and v.get('service-status.json',
    {}).get('RSS_KiB')]
checks = dict(active_runtime_at_least_1800_seconds=complete.get('active_elapsed_ns', 0) >= 1800 * 10 ** 9,
    native_exit_zero=outcome['native_exit'] == 0, safe_shutdown=outcome['native_shutdown_complete'],
    no_device_owners=not outcome['device_owners'], not_isolated=not status['release_blocked'] and status['state'] != 'isolated',
    hdmi_caught_up=status['adopted'] == status['inferred'], raw_PC_matches_board_sent=pc_end['raw']['received'] == status['pc_sent'],
    view_final_result_matches_raw=all(pc_end['view']['frame'][k] == pc_end['raw']['frame'][k] for k in ('session',
    'sequence')), CSI_no_hardware_fault=csi['faults'] == 0,
    CSI_no_backend_degradation=csi['fallbacks'] == 0, PC_invalid_zero=pc_end['raw']['invalid'] == pc_end['view']['invalid'] == 0,
    PC_observers_ended=(pc_exits[0]['native_exit'] == 0 and read(r / 'pc/view-fixed-exit.json')['native_exit'] == 0) if view_fixed else all(v['native_exit'] == 0 for v in pc_exits))
def stats(values):
    return dict(min=min(values), max=max(values), mean=statistics.mean(values)) if values else None
summary = dict(status='completed_with_observed_gaps_and_controlled_PC_view_restart' if all(checks.values()) and view_fixed else('completed' if all(checks.values()) else 'completed_with_findings'),
    checks=checks,
    active_seconds=complete.get('active_elapsed_ns', 0) / 1e9, total_process_seconds=outcome['seconds'],
    BOOT_sha256=identity['BOOT_sha256'], software_sha256=identity['files']['pose180_demo'], boot_id=read(run / 'request.json')['boot_id'],
    operations=dict(BOOT_writes=0, normal_reboots=1, SDK_attempts=outcome['SDK_attempts'], automatic_retry=False),
    package_closed=True, remaining_operations=0, input=read(WORK / 'selection.json'), final_status=status,
    csi=csi,
    pc={mode: {k: pc_end[mode][k] for k in ('received', 'invalid', 'duplicates', 'reconnects', 'recorded',
    'recordDrops', 'archiveError')} for mode in ('raw', 'view')},
    PC_original_exit_records=pc_exits, PC_intentional_view_restart=view_fixed,
    PC_view_received_before_restart=view_before['received'] if view_before else 0,
    PC_view_combined_observed_received=view_total, PC_view_accounting_gap=status['view_sent'] - view_total,
    PC_view_gap_scope='Includes intentional local view restart; before count is a pre-stop snapshot, not an exact disconnect count. Raw observation and board SDK stayed uninterrupted.' if view_fixed else None,
    retained_full_records=sum(p.stat().st_size // 74544 for p in (r / 'pc/actual.full').glob('*.full')),
    samples=dict(board=len(board), PC=len(pc)), resources=dict(peak_RSS_KiB=outcome['peak_RSS_KiB'],
    warm_RSS_KiB=stats([v['RSS_KiB'] for v in warm]), warm_first_RSS_KiB=warm[0]['RSS_KiB'] if warm else None,
    warm_last_RSS_KiB=warm[-1]['RSS_KiB'] if warm else None, fds=stats([v['fds'] for v in resource]),
    threads=stats([v['threads'] for v in resource]), minimum_MemAvailable_KiB=outcome['minimum_MemAvailable_KiB']),
    overlay_underflow_seen=max(v.get('overlay_underflow_seen', 0) for v in board),
    physical_screen=read(r / 'visual-confirmations.json') if (r / 'visual-confirmations.json').exists() else [],
    PC_UI_automation='Stopped: Windows Computer Use could not determine current browser URL; no automated rendered-screen claim',
    scope='30-minute official train input stability; generated 15Hz timelines, repeated new inference; not live CSI, accuracy or unlimited endurance',
    evidence_archive_sha256=(r / 'board-evidence.sha256').read_text().strip(), device_owners=outcome['device_owners'],
    SDK_autostart=False)
save(r / 'summary.json', summary)
print(json.dumps({k: summary[k] for k in ('status', 'checks', 'active_seconds', 'pc', 'resources', 'csi')},
    indent=2))
# The single maintained running identity points to the tested software/package.
default = ROOT / 'FPGA/hdmi_candidate/default_boot.json'
v = read(default)
v.update(runtime_boot_id=summary['boot_id'], software_path=str((WORK / NAME / 'board/pose180_demo').relative_to(ROOT)).replace('\\',
    '/'),
    software_sha256=summary['software_sha256'], release_state='30_minute_dataset_validated_idle' if all(checks.values()) else '30_minute_dataset_finished_with_findings',
    release_evidence=str((r / 'summary.json').relative_to(ROOT)).replace('\\', '/'), last_validated_input='official_dataset/train/30 clips, 8700 unique windows, 1800 active seconds',
    device_connection_state='connected_idle_after_30_minute_dataset_test', startup_consumed_this_boot=True,
    runtime_identity_scope='Same CSI r3 BOOT; one bounded SDK run, native close and device owners recorded in longrun evidence')
save(default, v)
