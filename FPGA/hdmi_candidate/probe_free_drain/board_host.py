"""Explicit finite board stages; SSH polling never restarts or kills an SDK call."""
from pathlib import Path
import argparse
import json
import shlex
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / '.local/hdmi-probe-free-drain-20261026-r1'
REMOTE = '/root/demo-v1-20261022-r1/' + WORK.name

def call(label, mode, source, destination=None, timeout=90):
    argv = [sys.executable, str(WORK / 'board_call.py'), label, mode, str(source)]
    if destination is not None:
        argv.append(str(destination))
    argv += ['--timeout', str(timeout)]
    result = subprocess.run(argv, capture_output=True, text=True)
    print(result.stdout, flush=True)
    if result.returncode:
        print(result.stderr, flush=True)
        raise RuntimeError('Transport/native stage failed; inspect ' + label + '.log before next action')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stage')
    parser.add_argument('--round', type=int, choices=(1, 2, 3), default=1)
    parser.add_argument('--label')
    args = parser.parse_args()
    name = 'round-' + str(args.round)
    base = REMOTE + '/' + name
    label = name + '-' + (args.label or args.stage)
    def ssh(command, timeout=90):
        call(label, 'ssh', command, timeout=timeout)
    if args.stage == 'deploy':
        ssh('test ! -e ' + REMOTE + ' && mkdir -m 700 ' + REMOTE)
        call('board-upload', 'put', WORK / 'board-package.tar.gz', REMOTE + '/board-package.tar.gz', timeout=150)
        call('board-extract', 'ssh', 'tar xzf ' + REMOTE + '/board-package.tar.gz -C ' + REMOTE, timeout=90)
    elif args.stage == 'start':
        tag = 'candidate-' + str(args.round)
        marker = ('HDMI_PROBE_FREE_DRAIN_R1_' + tag + '_UART_VERIFIED\n').encode()
        code = "import os;f=os.open('/dev/console',os.O_WRONLY|os.O_NOCTTY);print(os.write(f," + repr(marker) + "));os.close(f)"
        call(name + '-uart-marker', 'ssh', 'python3 -c ' + shlex.quote(code), timeout=20)
        capture = WORK / ('uart-' + tag)
        received = False
        for _ in range(30):
            if marker.strip() in (capture / 'rx.bin').read_bytes():
                received = True
                break
            time.sleep(.1)
        (capture / 'review.json').write_text(json.dumps(dict(marker_received=received, host_TX_bytes=0,
            physical_key=0, reboot_before_proof=0)))
        if not received:
            raise RuntimeError('UART receive proof absent; no BOOT change')
        call(name + '-install', 'ssh', 'python3 ' + base + '/controller.py install', timeout=150)
        call(name + '-candidate-reboot', 'ssh', 'python3 ' + base + '/controller.py candidate-reboot',
            timeout=45)
    elif args.stage == 'network':
        call(name + '-network-upload', 'put', WORK / (name + '-network.py'), base + '/network.py')
        ssh('python3 ' + base + '/network.py')
    elif args.stage == 'collect':
        # Keep one raw archive per round; unchanged model files are symlinks.
        ssh('tar czf ' + base + '/result-evidence.tar.gz -C ' + base + ' boot-control pipeline network',
            timeout=120)
        call(name + '-download', 'get', base + '/result-evidence.tar.gz', WORK / (name + '-result-evidence.tar.gz'),
            timeout=150)
    elif args.stage in ('prepare', 'restore', 'startup', 'run', 'status', 'stop', 'result', 'finish',
        'promote', 'fallback-reboot', 'close', 'audit'):
        ssh('python3 ' + base + '/controller.py ' + args.stage, timeout=150 if args.stage in ('restore',
            'promote') else 90)
    else:
        raise ValueError('Unknown stage')

if __name__ == '__main__':
    main()
