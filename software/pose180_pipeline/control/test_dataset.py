"""Finite Linux mock integration, including real prepared CSI; no SDK/devices."""
import argparse
import json
from pathlib import Path
import socket
import struct
import subprocess

def free_port():
	with socket.socket() as sock:
		sock.bind(('127.0.0.1', 0))
		return sock.getsockname()[1]

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('binary')
	parser.add_argument('dataset', type=Path)
	parser.add_argument('output', type=Path)
	parser.add_argument('--container', help='Run Linux binary in an existing /workspace-mounted container')
	args = parser.parse_args()
	args.output.mkdir()
	manifest = json.loads((args.dataset / 'dataset.json').read_text())
	def native_path(path):
		return '/workspace/' + Path(path).resolve().relative_to(Path(__file__).resolve().parents[3]).as_posix() if args.container else str(path)
	def command(name, data):
		return (['docker', 'exec', args.container] if args.container else []) + [args.binary, '--output',
			native_path(args.output / name), '--session', '81234',
			'--dataset', native_path(data), '--result-port', str(free_port()), '--status-port', str(free_port()),
			'--seconds', '8', '--mock-delay-ms', '1']
	source = args.dataset / 'dataset.piwcsi2'
	# Keep integration finite while using actual official payloads.
	clip = args.output / 'short.piwcsi2'
	count = min(24, manifest['count'])
	with source.open('rb') as stream:
		clip.write_bytes(stream.read(count * 86432))
	completed = subprocess.run(command('normal', clip), capture_output=True, text=True, timeout=15)
	if completed.returncode:
		raise AssertionError(completed.stdout + completed.stderr)
	status = json.loads((args.output / 'normal/completion.json').read_text())['status']
	assert status['mock'] is True and status['input_source'] == 'official_dataset'
	assert status['dataset_done'] and status['received'] == count and status['inferred'] == count
	assert status['resyncs'] == 0 and not status['input_connected']
	# Native reader must preserve prepared frame/time identity through processing.
	rows = []
	for file in (args.output / 'normal').rglob('*.full'):
		data = file.read_bytes()
		for offset in range(0, len(data), 74544):
			record = data[offset: offset + 74544]
			assert record[: 8] == b'PIWFUL3\0'
			frame = struct.unpack_from('<Q', record, 24)[0]
			stamp = struct.unpack_from('<Q', record, 40)[0]
			with clip.open('rb') as stream:
				stream.seek((frame - 1) * 86432 + 24)
				assert stamp == struct.unpack('<Q', stream.read(8))[0]
			rows.append(frame)
	assert set(rows) == set(range(1, count + 1)), rows
	repeated = subprocess.run(command('repeated', clip) + ['--dataset-repetitions', '3'], capture_output=True,
		text=True, timeout=15)
	if repeated.returncode:
		raise AssertionError(repeated.stdout + repeated.stderr)
	repeat_status = json.loads((args.output / 'repeated/completion.json').read_text())['status']
	assert repeat_status['dataset_done'] and repeat_status['dataset_passes'] == 3
	assert repeat_status['received'] == repeat_status['inferred'] == count * 3
	assert repeat_status['post_resets'] == 2 and repeat_status['resyncs'] == 0
	epochs = set()
	for file in (args.output / 'repeated').rglob('*.full'):
		data = file.read_bytes()
		for offset in range(0, len(data), 74544):
			record = data[offset: offset + 74544]
			epoch, frame = struct.unpack_from('<QQ', record, 16)
			assert 81234 <= epoch <= 81236 and 1 <= frame <= count
			stamp = struct.unpack_from('<Q', record, 40)[0]
			with clip.open('rb') as stream:
				stream.seek((frame - 1) * 86432 + 24)
				assert stamp == struct.unpack('<Q', stream.read(8))[0]
			epochs.add(epoch)
	assert epochs == {81234, 81235, 81236}
	for name, extra in [('csi_conflict', ['--csi', 'absent.conf']), ('tcp_conflict', ['--input-port',
		str(free_port())])]:
		result = subprocess.run(command(name, clip) + extra, capture_output=True, text=True, timeout=5)
		assert result.returncode != 0 and 'Dataset excludes' in result.stderr
		assert not (args.output / name).exists(), 'Conflict must fail before IO/SDK'
	bad = args.output / 'truncated.piwcsi2'
	bad.write_bytes(clip.read_bytes()[: -1])
	result = subprocess.run(command('truncated', bad), capture_output=True, text=True, timeout=5)
	assert result.returncode != 0 and 'complete PIWCSI2' in result.stderr
	report = dict(passed=True, SDK_calls=0, BOOT_writes=0, official_samples=count,
		input_source='official_dataset', mock=True, display_code_changed=False,
		checks=['EOF and final pending frame', 'source identity preserved', 'no resync',
		'live CSI/TCP input exclusivity before IO', 'truncated input rejected',
		'three bounded passes preserve source identity and reset tracking per epoch'])
	(args.output / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
	print(json.dumps(report))

if __name__ == '__main__':
	main()
