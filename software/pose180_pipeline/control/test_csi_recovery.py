"""Linux TCP integration: fresh CSI windows after local continuity/transport faults.

Uses synthetic, structurally valid 300 Hz CSI/NMD3 PCAP records and the real
resident CSI adapter. Inference is the mock backend; no hardware is accessed.
"""
import argparse
import json
from pathlib import Path
import select
import signal
import socket
import struct
import subprocess
import threading
import time

MAC = bytes.fromhex('021122334455')
CHANNEL = 0xD0A1
PCAP_HEADER = struct.pack('<IHHIIII', 0xA1B2C3D4, 2, 4, 0, 0, 4096, 1)
FAULT_EVENT = 900
DISCONNECT_EVENT = 1800
RECONNECT_EVENT = 1950
END_EVENT = 3300

def record(payload, port, arrival_us):
	udp = struct.pack('!HHHH', port, port, len(payload) + 8, 0) + payload
	ip = struct.pack('!BBHHHBBH4s4s', 0x45, 0, len(udp) + 20, 0, 0,
		64, 17, 0, b'\x7f\x00\x00\x01', b'\x7f\x00\x00\x01')
	frame = b'\x00' * 12 + b'\x08\x00' + ip + udp
	seconds, micros = divmod(arrival_us, 1000000)
	return struct.pack('<IIII', seconds, micros, len(frame), len(frame)) + frame

def event(receiver, ordinal, *, clock_shift_us=0, invalid_payload=False, counter_fault=True):
	capture_us = round(ordinal * 1000000 / 300)
	sequence = (ordinal & 4095) << 4
	tsf = (capture_us + receiver * 12345 + clock_shift_us) & 65535
	counter = ordinal + (2 if counter_fault and receiver == 1 and ordinal >= FAULT_EVENT else 0)
	packets = []
	for core in range(3):
		csi = bytearray(274)
		struct.pack_into('<H', csi, 0, 0x1111)
		csi[4: 10] = MAC
		struct.pack_into('<HHHH', csi, 10, sequence, core << 8, CHANNEL, 106)
		for carrier in range(64):
			struct.pack_into('<I', csi, 18 + 4 * carrier, 0 if invalid_payload else(carrier + 1) << 18)
		meta = bytearray(50)
		meta[: 4] = b'NMD3'
		struct.pack_into('<HH', meta, 4, 3, 50)
		meta[8: 14] = MAC
		struct.pack_into('<HHHHHHHHH', meta, 14, sequence, core << 8,
			CHANNEL, 8, 0xAAAA, tsf, counter & 65535, 28, 3)
		for carrier in range(3):
			struct.pack_into('<I', meta, 32 + 4 * carrier, (100 + carrier) << 18)
		struct.pack_into('<HI', meta, 44, 59, capture_us + 80)
		arrival = 100000000 + capture_us + core
		packets.extend((record(csi, 5500, arrival), record(meta, 5501, arrival)))
	return b''.join(packets)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('binary')
	parser.add_argument('output')
	args = parser.parse_args()
	output = Path(args.output)
	output.mkdir()
	# Reserve distinct ports together before handing them to the subprocess.
	reservations = [socket.socket() for _ in range(3)]
	for channel in reservations:
		channel.bind(('127.0.0.1', 0))
	csi_port, result_port, status_port = [s.getsockname()[1] for s in reservations]
	for channel in reservations:
		channel.close()
	config = output / 'csi.conf'
	config.write_text('bind=127.0.0.1\nport=%d\nsource=02:11:22:33:44:55\n'
		'channel=0xd0a1\nrx1=127.0.0.2\nrx2=127.0.0.3\n'
		'rx3=127.0.0.4\ngain1=1\ngain2=2\ngain3=3\n' % csi_port)
	command = [args.binary, '--output', str(output / 'run'), '--session', '950000',
		'--csi', str(config), '--result-port', str(result_port),
		'--status-port', str(status_port), '--seconds', '25',
		'--mock-delay-ms', '1']
	(output / 'command.json').write_text(json.dumps(command, indent=2))
	process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
		text=True)
	clients = [None] * 3
	samples, sampling_errors = [], []
	stop_sampling = threading.Event()
	sampler = None
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
		value['test_monotonic'] = time.monotonic()
		samples.append(value)
		return value

	def sample():
		while not stop_sampling.wait(.1):
			try:
				status()
			except Exception as error:
				sampling_errors.append(repr(error))

	def connect(receiver):
		channel = socket.socket()
		channel.settimeout(1)
		channel.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
		channel.bind(('127.0.0.%d' % (receiver + 2), 0))
		channel.connect(('127.0.0.1', csi_port))
		channel.sendall(PCAP_HEADER)
		clients[receiver] = channel

	checkpoints = {}
	try:
		assert select.select([process.stdout], [], [], 5)[0], 'Mock did not announce readiness'
		ready = process.stdout.readline()
		assert 'mock=1' in ready, ready
		for receiver in range(3):
			connect(receiver)
		sampler = threading.Thread(target=sample, name='csi-recovery-status')
		sampler.start()
		start = time.monotonic() + .1
		for ordinal in range(END_EVENT):
			time.sleep(max(0, start + ordinal / 300 - time.monotonic()))
			if ordinal == FAULT_EVENT:
				checkpoints['before_continuity'] = status()
				assert checkpoints['before_continuity']['inferred'] > 10
			if ordinal == DISCONNECT_EVENT:
				checkpoints['after_continuity'] = status()
				before = checkpoints['before_continuity']
				after = checkpoints['after_continuity']
				assert after['inferred'] > before['inferred'] + 10, after
				assert after['reconnects'] == before['reconnects'] == 3, after
				assert after['transport_resets'] == 0, after
				clients[1].shutdown(socket.SHUT_RDWR)
				clients[1].close()
				clients[1] = None
			if ordinal == RECONNECT_EVENT:
				checkpoints['during_rx2_disconnect'] = status()
				connect(1)
			for receiver, channel in enumerate(clients):
				if channel is not None:
					channel.sendall(event(receiver, ordinal))
		checkpoints['after_rx2_reconnect'] = status()
		final = checkpoints['after_rx2_reconnect']
		assert final['inferred'] > checkpoints['after_continuity']['inferred'] + 10, final
		assert final['reconnects'] == 4 and final['transport_resets'] == 1, final
		assert final['input_connected'] and final['state'] == 'running', final
		assert not sampling_errors, sampling_errors
		stop_sampling.set()
		sampler.join(timeout=2)
		process.send_signal(signal.SIGTERM)
		stdout, stderr = process.communicate(timeout=5)
		(output / 'native.stdout.log').write_text(ready + stdout)
		(output / 'native.stderr.log').write_text(stderr)
		assert process.returncode == 0, (process.returncode, stderr)
		events = []
		for path in sorted([*(output / 'run').glob('recent-*.jsonl'), *(output / 'run').glob('diagnostic-*.jsonl')]):
			for line in path.read_text().splitlines():
				# The shared journal also carries a presentation identity line.
				# Keep JSON parsing strict for actual structured records.
				if not line.lstrip().startswith('{'):
					continue
				item = json.loads(line)
				if item.get('event') == 'csi_recovery':
					events.append(item)
		events.sort(key=lambda item: item['elapsed_ms'])
		fault = next(item for item in events if item['phase'] == 'reset'
			and item['scope'] == 'alignment' and item['reason'] == 'counter_step')
		before_us = round((FAULT_EVENT - 1) * 1000000 / 300)
		after_us = round(FAULT_EVENT * 1000000 / 300)
		assert fault['rx'] == 2 and fault['connected'] == [1, 1, 1], fault
		assert fault['arrival_us'] == 100000000 + after_us, fault
		assert fault['previous_arrival_us'] == 100000000 + before_us, fault
		assert fault['host_delta_us'] == fault['tsf_delta_us'] == after_us - before_us, fault
		assert fault['counter_before'] == FAULT_EVENT - 1, fault
		assert fault['counter_after'] == FAULT_EVENT + 2 and fault['counter_step'] == 3, fault
		assert fault['sequence_before'] == (FAULT_EVENT - 1) << 4, fault
		assert fault['sequence_after'] == FAULT_EVENT << 4, fault
		assert fault['have_previous'] and fault['event_clock_known'], fault
		resets = [item for item in events if item['phase'] == 'reset' and item['scope'] == 'transport']
		assert len(resets) == 1 and resets[0]['rx'] == 2, resets
		assert resets[0]['connected'] == [1, 0, 1], resets
		recoveries = [item for item in events if item['phase'] == 'ready' and item['recovery_ms']]
		assert any(fault['elapsed_ms'] < item['elapsed_ms'] < resets[0]['elapsed_ms']
			for item in recoveries), recoveries
		assert any(item['elapsed_ms'] > resets[0]['elapsed_ms'] for item in recoveries), recoveries
		completion = json.loads((output / 'run' / 'completion.json').read_text())
		assert completion['native_shutdown_complete'], completion
		summary = {'passed': True, 'mock': True, 'CSI_live': False,
			'generated_capture_seconds': END_EVENT / 300,
			'new_inferences': final['inferred'],
			'continuity_recovered_without_reconnect': True,
			'single_rx_reconnect_preserved_healthy_tcp': True,
			'connection_accepts': final['reconnects'],
			'transport_resets': final['transport_resets'],
			'alignment_resets': final['alignment_resets'],
			'recovery_ms': [item['recovery_ms'] for item in recoveries],
			'diagnostic_raw_fields_verified': True,
			'native_shutdown_complete': True}
		(output / 'recovery-events.json').write_text(json.dumps(events, indent=2))
		(output / 'result.json').write_text(json.dumps(summary, indent=2))
		print(json.dumps(summary))
	finally:
		stop_sampling.set()
		if sampler is not None:
			sampler.join(timeout=2)
		for channel in clients:
			if channel is not None:
				channel.close()
		if process.poll() is None:
			process.send_signal(signal.SIGTERM)
			stdout, stderr = process.communicate(timeout=5)
			(output / 'native.stdout.log').write_text(ready + stdout)
			(output / 'native.stderr.log').write_text(stderr)
		(output / 'samples.json').write_text(json.dumps(samples, indent=2))
		(output / 'checkpoints.json').write_text(json.dumps(checkpoints, indent=2))

if __name__ == '__main__':
	main()
