"""Real CSI/TCP adapter with synthetic captures and mock inference, no devices."""
import argparse
import json
from pathlib import Path
import select
import signal
import socket
import subprocess
import time
from test_csi_recovery import PCAP_HEADER, event

def scenario(binary, output, empty_start):
	output.mkdir()
	holders = [socket.socket() for _ in range(3)]
	for channel in holders:
		channel.bind(('127.0.0.1', 0))
	csi_port, result_port, status_port = [s.getsockname()[1] for s in holders]
	for channel in holders:
		channel.close()
	config = output / 'csi.conf'
	config.write_text('bind=127.0.0.1\nport=%d\nsource=02:11:22:33:44:55\nchannel=0xd0a1\n'
		'rx1=127.0.0.2\nrx2=127.0.0.3\nrx3=127.0.0.4\ngain1=1\ngain2=2\ngain3=3\n' % csi_port)
	command = [binary, '--output', str(output / 'run'), '--session', '970000', '--csi', str(config),
		'--result-port', str(result_port), '--status-port', str(status_port), '--seconds', '15', '--mock-delay-ms',
		'1']
	process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
	clients = []
	samples = []
	ready = ''
	def status():
		with socket.create_connection(('127.0.0.1', status_port), 1) as channel:
			data = b''
			while True:
				part = channel.recv(4096)
				if not part:
					break
				data += part
		row = json.loads(data)
		samples.append(row)
		return row
	try:
		assert select.select([process.stdout], [], [], 5)[0]
		ready = process.stdout.readline()
		assert 'mock=1' in ready, ready
		for receiver in range(3):
			channel = socket.socket()
			channel.settimeout(1)
			channel.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
			channel.bind(('127.0.0.%d' % (receiver + 2), 0))
			channel.connect(('127.0.0.1', csi_port))
			channel.sendall(PCAP_HEADER)
			clients.append(channel)
		start = time.monotonic() + .1
		for ordinal in range(2700):
			time.sleep(max(0, start + ordinal / 300 - time.monotonic()))
			if ordinal == 900:
				before = status()
			for receiver, channel in enumerate(clients):
				# Continuous, fully framed stream. A 1.2 ms clock phase step
				# crosses the unchanged 833 us grid tolerance, never loses TCP.
				shift = 1200 if not empty_start and receiver == 1 and ordinal >= 900 else 0
				channel.sendall(event(receiver, ordinal, clock_shift_us=shift,
					invalid_payload=empty_start and ordinal < 1800, counter_fault=False))
			if ordinal % 30 == 0:
				sample = status()
				if empty_start and ordinal < 1800:
					assert sample['inferred'] == 0, 'Invalid CSI published as real input'
		final = status()
		assert final['reconnects'] == 3 and final['transport_resets'] == 0, final
		assert final['inferred'] > before['inferred'] + 10 and final['input_connected'], final
		process.send_signal(signal.SIGTERM)
		stdout, stderr = process.communicate(timeout=5)
		(output / 'native.stdout.log').write_text(ready + stdout)
		(output / 'native.stderr.log').write_text(stderr)
		assert process.returncode == 0, (process.returncode, stderr)
		rows = []
		for path in (output / 'run').glob('diagnostic-*.jsonl'):
			for line in path.read_text().splitlines():
				row = json.loads(line)
				if row.get('event', '').startswith('csi_'):
					assert len(line.encode()) + 1 <= 1024, 'Diagnostic exceeded bounded ring item'
					rows.append(row)
		resets = [r for r in rows if r.get('phase') == 'reset']
		assert len(resets) == 1, resets
		reset = resets[0]
		windows = [r for r in rows if r.get('event') == 'csi_windows' and r['trigger'] == 'before_reset']
		assert len(windows) == 1, windows
		d = windows[0]
		if empty_start:
			assert reset['reason'] == 'Initial joint alignment exceeded five seconds', reset
			assert 5000 <= reset['elapsed_ms'] < 6000, reset
			assert d['accepted'] == d['decided'] == 0, d
			nodes = [r for r in rows if r.get('event') == 'csi_node' and r['epoch'] == d['epoch']]
			assert len(nodes) >= 3 and all(r['invalid'] > 0 and not r['locked'] for r in nodes), nodes
		else:
			assert reset['reason'] == 'No jointly valid windows for two seconds', reset
			assert 2000 <= d['no_window_ms'] < 2500, d
			assert d['point_error'] > 0 and d['point_errors'][1] > 0 and d['point_errors'][0] == d['point_errors'][2] == 0, d
			assert final['longest_result_gap_ms'] < 4000, final
		recoveries = [r for r in rows if r.get('phase') == 'ready' and r['elapsed_ms'] > reset['elapsed_ms']]
		assert recoveries and final['diagnostic_dropped'] == 0, (recoveries, final)
		assert json.loads((output / 'run/completion.json').read_text())['native_shutdown_complete']
		result = dict(passed=True, mock=True, CSI_live=False, empty_start=empty_start,
			final=final, reset=reset, window_diagnostic=d, recovery=recoveries[0])
		(output / 'result.json').write_text(json.dumps(result, indent=2))
		return result
	finally:
		for channel in clients:
			channel.close()
		if process.poll() is None:
			process.send_signal(signal.SIGTERM)
			process.communicate(timeout=5)

if __name__ == '__main__':
	p = argparse.ArgumentParser()
	p.add_argument('binary')
	p.add_argument('output', type=Path)
	a = p.parse_args()
	a.output.mkdir()
	results = [scenario(a.binary, a.output / name, empty) for name, empty in [('phase-step', False), ('empty-start',
		True)]]
	print(json.dumps(dict(passed=True, cases=len(results), max_result_gap_ms=[v['final']['longest_result_gap_ms'] for v in results])))
