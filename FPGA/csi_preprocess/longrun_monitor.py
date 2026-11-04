"""Read-only, finite on-board sampling. Does not start, stop or retry SDK."""
import json, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'board'))
import startup
from service import read_status
from run_hdmi_trial import owners
out = ROOT / 'monitor'
out.mkdir(exist_ok=False)
latest = startup.read(ROOT / 'board/latest.json')
run = ROOT / 'board/runs' / latest['run']
started = time.monotonic()
with (out / 'samples.jsonl').open('w') as f:
    while time.monotonic() - started < 1920:
        status = read_status(39384)
        record = dict(monotonic=time.monotonic(), boot_id=startup.boot_id(), status=status)
        for name in ('service-status.json', 'outcome.json'):
            if (run / name).exists():
                record[name] = startup.optional_json(run / name)
        # Small cumulative CSI/overlay sample; no MMIO or private SDK memory access.
        newest = sorted((run / 'run').glob('recent-*.jsonl'), key=lambda p: p.stat().st_mtime, reverse=True)
        events = []
        for path in newest[: 2]:
            for line in path.read_text(errors='replace').splitlines():
                if '"event":"csi_pl"' in line or '"event":"overlay_adopted"' in line:
                    try:
                        events.append(json.loads(line))
                    except ValueError:
                        pass
        csi = [v for v in events if v.get('event') == 'csi_pl']
        if csi:
            record['csi'] = max(csi, key=lambda v: v['calls'])
        overlays = [v for v in events if v.get('event') == 'overlay_adopted']
        if overlays:
            record['overlay_underflow_seen'] = max(v.get('overlay_underflow_seen', 0) for v in overlays)
        f.write(json.dumps(record) + '\n')
        f.flush()
        if record.get('outcome.json'):
            (out / 'ended.json').write_text(json.dumps(dict(normal_monitor_end=True, device_owners=owners(),
                elapsed=time.monotonic() - started)))
            break
        time.sleep(10)
    else:
        (out / 'ended.json').write_text(json.dumps(dict(normal_monitor_end=False, reason='finite observation deadline; no process killed')))
