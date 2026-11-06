"""Loopback TCP/real CSI parser plus mock inference. Never accesses devices."""
import argparse
import json
from pathlib import Path
import select
import signal
import socket
import subprocess
import time
from test_csi_recovery import PCAP_HEADER, event

def run(binary, output):
	output.mkdir()
	holders = [socket.socket() for _ in range(3)]
	for channel in holders:
		channel.bind(('127.0.0.1', 0))
	csi_port, result_port, status_port = [s.getsockname()[1] for s in holders]
	for channel in holders:
		channel.close()
	config = output / 'csi.conf'
	config.write_text('bind=127.0.0.1\nport=%d\nsource=02:11:22:33:44:55\n'
		'channel=0xd0a1\nrx1=127.0.0.2\nrx2=127.0.0.3\nrx3=127.0.0.4\n'
		'gain1=1\ngain2=2\ngain3=3\nalignment=adaptive\n' % csi_port)
	process = subprocess.Popen([binary, '--output', str(output / 'run'), '--session', '980000',
		'--csi', str(config), '--result-port', str(result_port),
		'--status-port', str(status_port), '--seconds', '15',
		'--mock-delay-ms', '10'], stdout=subprocess.PIPE,
		stderr=subprocess.PIPE, text=True)
	clients, samples = [], []
	ready = ''
	def status():
		with socket.create_connection(('127.0.0.1', status_port), 1) as channel:
			data = b''
			while True:
				part = channel.recv(4096)
				if not part:
					break
				data += part
		value = json.loads(data)
		samples.append(value)
		return value
	try:
		assert select.select([process.stdout], [], [], 5)[0], 'Mock did not announce readiness'
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
		for ordinal in range(2100):
			time.sleep(max(0, start + ordinal / 300 - time.monotonic()))
			for receiver, channel in enumerate(clients):
				packet = event(receiver, ordinal,
					clock_shift_us=1200 if receiver == 1 and ordinal >= 400 else 0,
					invalid_payload=receiver == 2 and ordinal >= 700 and ordinal % 97 == 0,
					counter_fault=True)
				if receiver == 1 and ordinal == 500:
					packet = bytearray(packet)
					packet[16 + 14] = 0x44  # trusted PCAP record, malformed IPv4 IHL
				channel.sendall(packet)
			if ordinal % 30 == 0:
				status()
		time.sleep(.1)
		final = status()
		assert final['inferred'] >= 80, final
		assert final['resyncs'] == final['transport_resets'] == final['alignment_resets'] == 0, final
		assert final['reconnects'] == 3 and final['state'] == 'running', final
		assert final['longest_result_gap_ms'] < 700, final
		assert final['csi_alignment'] == 'adaptive', final
		# Status reads independent atomics while a window may be handed over.
		assert abs(final['csi_exact_windows'] + final['csi_approximate_windows'] - final['received']) <= 1, final
		assert final['csi_approximate_points'] > 0 and final['csi_mapping_switches'] > 0, final
		assert final['csi_decoder_resets'] >= 1 and final['csi_max_skew_us'] <= 5000, final
		assert final['csi_rejected_records'] == 1, final
		epochs = {s['input_epoch'] for s in samples if s['inferred']}
		assert len(epochs) == 1, epochs
		process.send_signal(signal.SIGTERM)
		stdout, stderr = process.communicate(timeout=5)
		(output / 'native.stdout.log').write_text(ready + stdout)
		(output / 'native.stderr.log').write_text(stderr)
		assert process.returncode == 0, (process.returncode, stderr)
		rows = []
		for path in (output / 'run').glob('diagnostic-*.jsonl'):
			for line in path.read_text().splitlines():
				assert len(line.encode()) + 1 <= 1024, 'Diagnostic exceeded bounded item'
				rows.append(json.loads(line))
		windows = [r for r in rows if r.get('event') == 'csi_adaptive_window']
		faults = [r for r in rows if r.get('phase') == 'decoder_reset']
		assert any(r['rx'] == 2 and r['reason'] == 'counter_step'
			and r['counter_step'] == 3 and r['have_previous'] for r in faults), faults
		assert len(windows) >= 80 and any(r['approximate_points'] for r in windows), windows[-3:]
		assert max(r['alignment_version'] for r in windows) > 0
		assert all(r['strict_grid_verified'] is False for r in windows)
		assert all(r['max_skew_us'] <= 5000 and r['span_us'] <= 100000 for r in windows)
		complete = json.loads((output / 'run/completion.json').read_text())
		assert complete['native_shutdown_complete']
		stopped = complete['status']
		assert stopped['csi_exact_windows'] + stopped['csi_approximate_windows'] == stopped['received'], stopped
		result = dict(passed=True, CSI_live=False, SDK=False, generated_seconds=7,
			final=final, input_epochs=sorted(epochs), recorded_windows=len(windows),
			recorded_approximate_windows=sum(bool(r['approximate_points']) for r in windows),
			max_alignment_version=max(r['alignment_version'] for r in windows))
		(output / 'result.json').write_text(json.dumps(result, indent=2))
		(output / 'samples.json').write_text(json.dumps(samples, indent=2))
		print(json.dumps(result))
	finally:
		for channel in clients:
			channel.close()
		if process.poll() is None:
			process.send_signal(signal.SIGTERM)
			process.communicate(timeout=5)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument('binary')
	parser.add_argument('output', type=Path)
	args = parser.parse_args()
	run(args.binary, args.output)
