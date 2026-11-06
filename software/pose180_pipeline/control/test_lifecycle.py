"""Linux integration: detached RX reconnect, local stop, capped logs and stalled logger.

Uses loopback packets and mock children only; never loads radio firmware or SDK.
"""
import argparse
import base64
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import struct
import subprocess
import sys
import threading
import time
from bounded_log import RingLog

def await_file(path, timeout=10):
	end = time.monotonic() + timeout
	while time.monotonic() < end:
		try:
			return json.loads(path.read_text())
		except (OSError, ValueError):
			time.sleep(.05)
	raise AssertionError('Missing ' + str(path))

def router(root, guard, capture):
	folder = root / 'router'
	folder.mkdir()
	shutil.copyfile(capture, folder / 'capture-metadata-stream')
	(folder / 'capture-metadata-stream').chmod(0o755)
	(folder / 'restore.sh').write_text('#!/bin/sh\ntouch restored\nrm -f armed\n')
	(folder / 'armed').touch()
	listener = socket.socket()
	listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	listener.bind(('127.0.0.1', 0))
	listener.listen()
	listener.settimeout(12)
	sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	done = threading.Event()
	def send():
		while not done.is_set():
			sender.sendto(b'owned loopback CSI capture test' * 10, ('127.0.0.1', 5500))
			time.sleep(.005)
	worker = threading.Thread(target=send)
	worker.start()
	launch = subprocess.run([guard, 'rx', str(folder), '35', '127.0.0.1', str(listener.getsockname()[1]),
		'lo'], capture_output=True, text=True, check=True)
	pid = json.loads(launch.stdout)['guard_pid']
	headers = []
	try:
		for round in range(3):
			peer, _ = listener.accept()
			peer.settimeout(2)
			data = b''
			while len(data) < 24:
				data += peer.recv(24 - len(data))
			assert data[: 4] == b'\xd4\xc3\xb2\xa1'
			headers.append(data.hex())
			if round == 1:
				(folder / 'pause.seconds').write_text('2\n')
			if round == 2:
				(folder / 'stop.request').touch()
			else:
				time.sleep(.3)
			peer.close()
		final = await_file(folder / 'guard-final.json')
		assert final['generations'] >= 3 and final['restore_exit'] == 0 and final['guard_fault'] == 0, final
		assert (folder / 'restored').exists() and not (folder / 'armed').exists()
		assert len(list(folder.glob('capture-*.json'))) <= 4
		return dict(detached_launcher_exit=launch.returncode, fresh_headers=len(headers), **final)
	finally:
		(folder / 'stop.request').touch()
		done.set()
		worker.join()
		sender.close()
		listener.close()
		try:
			os.kill(pid, signal.SIGTERM)
		except ProcessLookupError:
			pass

def logs(root):
	folder = root / 'ring'
	folder.mkdir()
	ring = RingLog(folder, 'test', 4096, 3)
	for _ in range(100):
		ring.write(b'x' * 1000)
	ring.close()
	assert sum(p.stat().st_size for p in folder.glob('*.log')) <= 3 * 4096
	full = root / 'full'
	full.mkdir()
	(full / 'test-0.log').symlink_to('/dev/full')
	ring = RingLog(full, 'test', 4096, 3)
	ring.write(b'x' * 1000)
	assert ring.dropped == 1000
	ring.close()
	# This mock continuously fills stdout. Its progress file is independent
	# of the logger, matching the SDK's nonblocking stdout contract.
	run = root / 'supervisor'
	run.mkdir()
	(run / 'metadata').mkdir()
	child = run / 'flood.py'
	child.write_text('''import json,os,signal,time
from pathlib import Path
root=Path(__file__).parent
stop=False
def request(*_):
 global stop;stop=True
signal.signal(signal.SIGTERM,request)
n=0
while not stop:
 for _ in range(100):
  try:os.write(1,b'x'*8192)
  except BlockingIOError:pass
 n+=1;(root/'progress').write_text(str(n));time.sleep(.01)
(root/'run').mkdir()
(root/'run/completion.json').write_text(json.dumps(dict(native_shutdown_complete=True,status=dict(mock=True,inferred=n,adopted=0))))
''')
	code = 'from pathlib import Path;from service import supervise;import sys;supervise(Path(sys.argv[1]),[sys.executable,sys.argv[1]+"/flood.py"],20,9)'
	# The launcher exits; the actual supervisor has its own session/stdin.
	parent = subprocess.Popen([sys.executable, '-c', code, str(run)], cwd=Path(__file__).parent,
		stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
	pump = await_file(run / 'metadata/logger-process.json')['pid']
	await_file(run / 'metadata/process.json')
	time.sleep(2)
	os.kill(pump, signal.SIGSTOP)
	before = int((run / 'progress').read_text())
	time.sleep(1)
	after = int((run / 'progress').read_text())
	assert after > before + 20, (before, after)
	os.kill(pump, signal.SIGCONT)
	(run / 'stop.request').touch()
	parent.wait(timeout=8)
	assert parent.returncode == 0
	result = await_file(run / 'outcome.json')
	assert result['native_exit'] == 0 and result['native_shutdown_complete'] and result['stop_sent'], result
	size = sum(p.stat().st_size for p in (run / 'metadata').glob('native-*.log'))
	assert size <= 4 * 524288, size
	return dict(logger_stall_progress=after - before, log_bytes=size, supervisor_native_exit=result['native_exit'],
		stop_proved_by_mock_completion=True)

def transmitter(root, guard):
	folder = root / 'tx'
	folder.mkdir()
	(folder / 'armed').touch()
	(folder / 'run.params').write_text('mock-parameters\n')
	(folder / 'restore.sh').write_text('#!/bin/sh\ntouch restored\nrm -f armed\n')
	# Execute the real decoder/lifecycle against a fake command, including a
	# firmware error on the second finite job. Such an error must not restart TX.
	fake = '''#!/usr/bin/python3
import base64,json,struct,sys
from pathlib import Path
p=Path('fake-state.json');s=json.loads(p.read_text()) if p.exists() else dict(starts=0,queries=0,stops=0,configured=False,configurations=0)
op=sys.argv[2]
if op=='-s429':
 s['configured']=True;s['configurations']+=1
elif op=='-s430':
 assert len(sys.argv)==3 and s['configured'];s['starts']+=1;s['queries']=0
elif op=='-s432':
 assert len(sys.argv)==3;s['stops']+=1;s['configured']=False
elif op=='-g433':
 s['queries']+=1;error=7 if s['starts']==2 else 0
 running=int(s['queries']==1 and not error)
 words=[0x3158544e,running,300,18000 if running else 0,0 if running else 18000,0,error,100,1,2,3,1]
 print(base64.b64encode(struct.pack('<12I',*words)).decode())
p.write_text(json.dumps(s))
'''
	(folder / 'nexutil').write_text(fake)
	(folder / 'nexutil').chmod(0o755)
	subprocess.run([guard, 'tx', str(folder), '20', '127.0.0.1', '39033', 'lo'], check=True, capture_output=True)
	final = await_file(folder / 'guard-final.json')
	state = json.loads((folder / 'fake-state.json').read_text())
	assert final['completed_TX_jobs'] == 1 and final['guard_fault'] == 1 and final['restore_exit'] == 0, (final,
		state)
	assert state['starts'] == 2 and state['stops'] >= 2 and state['configurations'] == 2, state
	return dict(mock_firmware=True, error_stops_without_retry=True, **final)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('guard')
	parser.add_argument('capture')
	parser.add_argument('output')
	parser.add_argument('--export')
	args = parser.parse_args()
	root = Path(args.output).resolve()
	root.mkdir()
	guard = str(Path(args.guard).resolve())
	result = dict(mock=True, RX=router(root, guard, str(Path(args.capture).resolve())), TX=transmitter(root,
		guard), logs=logs(root))
	(root / 'result.json').write_text(json.dumps(result, indent=2))
	print(json.dumps(result))
	if args.export:
		target = Path(args.export)
		target.mkdir()
		for p in root.rglob('*'):
			if p.is_file() and not p.is_symlink():
				destination = target / p.relative_to(root)
				destination.parent.mkdir(parents=True, exist_ok=True)
				shutil.copyfile(p, destination)

if __name__ == '__main__':
	main()
