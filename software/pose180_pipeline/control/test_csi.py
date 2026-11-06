"""Paced real-recording replay through three direct TCP inputs, then reconnect."""
import argparse
import json
from pathlib import Path
import signal
import socket
import struct
import subprocess
import threading
import time

def main():
	p = argparse.ArgumentParser()
	p.add_argument('binary')
	p.add_argument('fixtures')
	p.add_argument('output')
	a = p.parse_args()
	root = Path(a.output)
	root.mkdir()
	ports = []
	for _ in range(3):
		with socket.socket() as s:
			s.bind(('127.0.0.1', 0))
			ports.append(s.getsockname()[1])
	cport, rport, sport = ports
	config = root / 'csi.conf'
	config.write_text('bind=127.0.0.1\nport=%d\nsource=f0:2f:74:39:45:6c\nchannel=0xd0a1\nrx1=127.0.0.2\nrx2=127.0.0.3\nrx3=127.0.0.4\ngain1=1\ngain2=2\ngain3=3\n' % cport)
	process = subprocess.Popen([a.binary, '--output', str(root / 'run'), '--session', '890000', '--csi',
		str(config),
		'--result-port', str(rport), '--status-port', str(sport), '--seconds', '70'], stdout=subprocess.PIPE,
		stderr=subprocess.PIPE, text=True)
	samples = []
	errors = []
	def status():
		with socket.create_connection(('127.0.0.1', sport), 2) as s:
			data = b''
			while True:
				b = s.recv(4096)
				if not b:
					break
				data += b
		value = json.loads(data)
		samples.append(value)
		return value
	def send(r, round, start):
		try:
			data = (Path(a.fixtures) / ('rx%d' % (r + 1)) / ('run300-%d.pcap' % round)).read_bytes()
			with socket.socket() as s:
				s.bind(('127.0.0.%d' % (r + 2), 0))
				s.connect(('127.0.0.1', cport))
				s.sendall(data[: 24])
				offset = 24
				first = None
				while offset < len(data):
					sec, usec, size, _ = struct.unpack_from('<IIII', data, offset)
					stamp = sec + usec / 1e6
					if first is None:
						first = stamp
					time.sleep(max(0, start + stamp - first - time.monotonic()))
					s.sendall(data[offset: offset + 16 + size])
					offset += 16 + size
				time.sleep(.3)
		except Exception as e:
			errors.append(repr(e))
	try:
		ready = process.stdout.readline()
		assert 'mock=1' in ready
		# Startup/SDK loading can exceed the ten-second no-valid-window budget.
		# A disconnected source must not spend the next connection's allowance.
		time.sleep(11)
		before = 0
		epoch = 0
		for round in (1, 2):
			start = time.monotonic() + .3
			threads = [threading.Thread(target=send, args=(r, round, start)) for r in range(3)]
			for t in threads:
				t.start()
			while any(t.is_alive() for t in threads):
				status()
				time.sleep(.2)
			for t in threads:
				t.join()
			assert not errors, errors
			after = status()
			assert after['inferred'] > before + 90, after
			assert after['input_epoch'] > epoch, after
			before = after['inferred']
			epoch = after['input_epoch']
			if round == 1:
				time.sleep(12)
		process.send_signal(signal.SIGTERM)
		out, err = process.communicate(timeout=5)
		assert process.returncode == 0, (out, err)
		(root / 'samples.json').write_text(json.dumps(samples, indent=2))
		(root / 'native.stdout.log').write_text(ready + out)
		(root / 'native.stderr.log').write_text(err)
		print(json.dumps({'mock': True, 'CSI_live': False, 'real_pcap_rounds': 2, 'inferred': before,
			'three_RX_reconnect': True}))
	finally:
		if process.poll() is None:
			process.terminate()
			process.wait(timeout=5)

if __name__ == '__main__':
	main()
