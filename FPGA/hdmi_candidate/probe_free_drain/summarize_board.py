"""Summarize the three preserved raw archives without copying their contents."""
from pathlib import Path
import collections
import json
import re
import tarfile
from prepare import ROOT, WORK, EVIDENCE

def summarize(index):
    archive = WORK / f'round-{index}-result-evidence.tar.gz'
    with tarfile.open(archive) as source:
        def raw(name):
            return source.extractfile(name).read().decode(errors='replace')
        def read(name):
            return json.loads(raw(name))
        result = read('boot-control/metadata/long-test.json')
        closed = read('boot-control/metadata/closed.json')
        installed = read('boot-control/metadata/install.json')
        startup = read('boot-control/metadata/startup.json')
        identity = read('pipeline/identity.json')
        process = read('pipeline/metadata/process.json')
        consumer = raw('pipeline/run/startup-consumer.jsonl')
        snapshots = [json.loads(line) for line in consumer.splitlines() if line.startswith('{')]
        mode = re.search(r'startup_mode=(\w+)', consumer).group(1)
        events = collections.Counter()
        stop = []
        for member in source.getmembers():
            if re.fullmatch(r'pipeline/run/recent-[0-9]+\.jsonl', member.name):
                for line in raw(member.name).splitlines():
                    try:
                        row = json.loads(line)
                    except ValueError:
                        continue
                    event = row.get('event', '')
                    events[event] += 1
                    if event in ('stop_proved', 'frames_released_after_stop'):
                        stop.append(row)
        before = raw('pipeline/metadata/before.dmesg')
        after = raw('pipeline/metadata/after.dmesg')
        old_lines = set(before.splitlines())
        delta = after[len(before):] if after.startswith(before) else '\n'.join(line for line in after.splitlines() if line not in old_lines)
        final = result['final_status']
        native_seconds = int(process['argv'][process['argv'].index('--seconds') + 1])
        pc = json.loads((WORK / f'pc-round-{index}/completed.json').read_text())
        state = pc['last_state']
        # Only execution, identity and resource safety are hard requirements.
        if not (result['passed'] and native_seconds == 300 and closed['closed']
            and not final['mock'] and final['hdmi'] and final['inferred'] > 0
            and result['native_shutdown_complete'] and not result['device_owners']
            and events['stop_proved'] and events['frames_released_after_stop']):
            raise RuntimeError(f'Round {index}: incomplete execution or safe shutdown')
        return dict(round=index, passed=result['passed'], boot_id=startup['boot_id'],
            runtime_seconds=native_seconds, process_seconds=result['seconds'],
            startup_mode=mode, consumer_raw_snapshots=snapshots,
            candidate_BOOT_sha256=installed['BOOT_sha256'],
            native_binary_sha256=identity['files']['pose180_demo'],
            hardware_profile=identity['hardware_profile'],
            final_status=final, native_exit=result['native_exit'],
            native_shutdown_complete=result['native_shutdown_complete'],
            stop_and_release_events=stop, device_owners=result['device_owners'],
            stop_reason=result['stop_reason'], peak_RSS_KiB=result['peak_RSS_KiB'],
            peak_fds=result['peak_fds'], peak_threads=result['peak_threads'],
            minimum_MemAvailable_KiB=result['minimum_MemAvailable_KiB'],
            new_kernel_lines=delta.splitlines(),
            PC=dict(native_exit=pc['native_exit'], received=state['received'],
            invalid=state['invalid'], duplicates=state['duplicates'],
            record_drops=state['recordDrops']), closed=closed,
            physical_screen_verified=False, raw_archive=str(archive))

rows = [summarize(index) for index in range(1, 4)]
if len({row['boot_id'] for row in rows}) != 3 or len({row['candidate_BOOT_sha256'] for row in rows}) != 1:
    raise RuntimeError('Three distinct boots of the same image were not established')
summary = dict(status='three_rounds_completed_original_BOOT_fallback_verified',
    rounds=rows, candidate_starts=3, SDK_attempts=3, original_fallbacks=1,
    running_original_BOOT=not rows[-1]['closed'].get('running_candidate', False),
    final_boot_id=rows[-1]['closed']['boot_id'],
    physical_screen_verified=False,
    limits=['Software reboots; no power-cycle test', 'Three finite 300-second runtime samples',
    'CSI gaps and bounded alignment recoveries are recorded, not zero-stutter acceptance',
    'D45 root cause remains open; no protocol checker diagnostic coverage claimed'])
target = EVIDENCE / 'board-summary.json'
with target.open('x', encoding='utf-8') as stream:
    json.dump(summary, stream, ensure_ascii=False, indent=2)
print(json.dumps(dict(rounds=3, inferred=[row['final_status']['inferred'] for row in rows],
    PC_received=[row['PC']['received'] for row in rows], final_boot_id=summary['final_boot_id'])))
