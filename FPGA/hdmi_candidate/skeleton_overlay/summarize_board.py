"""Summarize retained native display events; never extrapolate a bounded ring."""
import argparse
import json
import math
import statistics
from pathlib import Path

def stats(values):
    values = sorted(values)
    if not values:
        return {"samples": 0}
    return dict(samples=len(values), p95_method='nearest rank: ceil(0.95*N)', mean=statistics.mean(values),
        median=statistics.median(values), p95=values[math.ceil(.95 * len(values)) - 1],
        min=values[0], max=values[-1])

def summarize(run):
    rows = []
    bad = []
    for path in sorted(run.glob('recent-*.jsonl')):
        for number, line in enumerate(path.read_text().splitlines(), 1):
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                bad.append(dict(file=path.name, line=number))
    completion = json.loads((run / 'completion.json').read_text())
    status = completion['status']
    result = dict(run=str(run.resolve()), native_shutdown_complete=completion['native_shutdown_complete'],
        counters={k: status.get(k) for k in ('received', 'inferred', 'adopted', 'display_updates',
        'pc_sent', 'pc_dropped', 'view_sent', 'view_dropped', 'replaced', 'release_blocked')},
        malformed_log_lines=bad,
        timing_scope='Retained bounded-ring events only; not necessarily every inference.')
    pl = [r for r in rows if r.get('event') == 'overlay_adopted']
    if pl:
        result['renderer'] = 'pl'
        result['overlay'] = {key: stats([r[key] for r in pl]) for key in
            ('command_bytes', 'prepare_ms', 'submit_ms', 'submit_and_adopt_ms', 'draw_cycles')}
        result['overlay']['draw_ms_at_100MHz'] = stats([r['draw_cycles'] / 100000 for r in pl])
        result['overlay']['underflow_seen_events'] = sum(bool(r['overlay_underflow_seen']) for r in pl)
        result['overlay']['tag_mismatch_events'] = sum(r['hardware_done_tag'] != r['tag'] for r in pl)
        result['overlay']['hardware_completion_range'] = [min(r['hardware_completed'] for r in pl),
            max(r['hardware_completed'] for r in pl)]
        result['overlay']['unique_hardware_completions'] = len({r['hardware_completed'] for r in pl})
        result['scope'] = 'PL submit_and_adopt includes register submission, rasterization and vblank confirmation; prepare_ms is separate. Initial background upload is excluded.'
    else:
        result['renderer'] = 'ps'
        adopted = [r for r in rows if r.get('event') == 'adopted' and 'write_and_adopt_ms' in r]
        result['write_and_adopt_ms'] = stats([r['write_and_adopt_ms'] for r in adopted])
        submitted = {r['id']: r for r in rows if r.get('event') == 'submitted'}
        flip = {r['argument_id']: r for r in rows if r.get('event') == 'command' and r.get('op') == 2}
        result['frame_upload_and_flip_issue_ms'] = stats([
            (flip[tag]['request_sent_ns'] - r['begin_ns']) / 1e6
            for tag, r in submitted.items() if tag in flip])
        result['scope'] = 'PS write_and_adopt includes full framebuffer upload and display confirmation; excludes CPU drawing. Upload_and_flip_issue excludes vblank wait.'
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('run', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    result = summarize(args.run)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
