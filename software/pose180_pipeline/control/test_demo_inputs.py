"""Exercise both release input commands, provenance and pre-hardware guards.

Native execution uses the mock only; network/device preflight is not invoked.
The official clip contains real recorded CSI, never prerecorded model outputs.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
from unittest.mock import patch

import startup
from dataset_input import validate_dataset
from input_config import select_input
from test_dataset import free_port

def rejected(call):
	try:
		call()
	except (ValueError, FileNotFoundError):
		return
	raise AssertionError('Invalid input/unsafe restart was accepted')

def main():
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument('binary', type=Path)
	parser.add_argument('dataset', type=Path)
	parser.add_argument('output', type=Path)
	args = parser.parse_args()
	root = args.output.resolve()
	root.mkdir()
	for name in ('dataset.json', 'dataset.piwcsi2'):
		shutil.copyfile(args.dataset / name, root / name)
	(root / 'csi.conf').write_text('# configuration placeholder; no live router access\n')
	identity = dict(input_source='live_csi', input_sources=['live_csi', 'official_dataset'])
	manifest = validate_dataset(root)
	live = select_input(root, identity)
	recorded = select_input(root, identity, 'official_dataset', 1)
	assert recorded['split'] == manifest['split'] and recorded['dataset_sha256'] == manifest['sha256']
	commands = [startup.command(root, root, 9001, 0, choice) for choice in (live, recorded)]
	options = [dict(zip(argv[1:: 2], argv[2:: 2])) for argv in commands]
	assert '--csi' in options[0] and '--dataset' not in options[0]
	assert '--dataset' in options[1] and '--csi' not in options[1]
	for option in options:
		assert option['--input-port'] == '0' and option['--score-threshold'] == 'none'
		assert option['--top-k'] == option['--single-person-stability'] == '1'
	rejected(lambda: select_input(root, identity, 'unknown'))
	rejected(lambda: select_input(root, identity, 'live_csi', 2))
	for passes in (0, -1, 31, 1.5, True):
		rejected(lambda: select_input(root, identity, 'official_dataset', passes))
	rejected(lambda: select_input(root, dict(input_source='live_csi'), 'official_dataset'))
	(root / 'dataset.piwcsi2').rename(root / 'saved.piwcsi2')
	rejected(lambda: select_input(root, identity, 'official_dataset'))
	assert select_input(root, identity) == live  # Explicit live input remains independent.
	(root / 'saved.piwcsi2').rename(root / 'dataset.piwcsi2')

	# Use the real release command; replace only hardware/ports and a short
	# prefix of the official recording to keep this integration test bounded.
	option = options[1]
	short = root / 'short.piwcsi2'
	with (root / 'dataset.piwcsi2').open('rb') as stream:
		short.write_bytes(stream.read(12 * 86432))
	option.update({'--dataset': str(short), '--hdmi': '0', '--hardware-profile': 'r45',
		'--result-port': str(free_port()), '--status-port': str(free_port()),
		'--view-port': str(free_port()), '--mock-delay-ms': '1'})
	argv = [str(args.binary.resolve())] + [word for pair in option.items() for word in pair]
	result = subprocess.run(argv, capture_output=True, text=True, timeout=10)
	assert result.returncode == 0, result.stdout + result.stderr
	complete = json.loads((root / 'run/completion.json').read_text())
	status = complete['status']
	assert complete['native_shutdown_complete'] and status['dataset_done']
	assert status['received'] == status['inferred'] == 12 and status['dataset_passes'] == 1
	assert status['input_source'] == 'official_dataset' and status['single_person_stability']

	prior = root / 'prior'
	prior.mkdir()
	def write(name, value):
		(prior / name).write_text(json.dumps(value))
	write('request.json', dict(boot_id='current', functional_startup_once=True))
	write('sdk-attempt.json', dict(boot_id='current'))
	write('outcome.json', dict(native_exit=0, native_shutdown_complete=True, device_owners=[]))
	with patch.object(startup, 'live', return_value=False):
		rejected(lambda: startup.check_run(prior, 'current'))
		startup.check_run(prior, 'new-boot')
		(prior / 'run').mkdir()
		write('run/completion.json', dict(failure_before_hardware=True, native_shutdown_complete=True))
		startup.check_run(prior, 'current')

	invalid = [('--seconds', '-1'), ('--seconds', '2bad'), ('--seconds', '18446744074'),
		('--max-input-age-ms', '18446744073709551615'), ('--max-input-age-ms', '60001'),
		('--min-cutoff', '0.5bad'), ('--beta', 'nan'), ('--top-k', '1junk'),
		('--result-port', '65536'), ('--dataset-repetitions', '-1')]
	for index, (name, value) in enumerate(invalid):
		destination = root / ('invalid-' + str(index))
		result = subprocess.run([str(args.binary.resolve()), '--output', str(destination),
			'--session', '99', name, value], capture_output=True, text=True, timeout=5)
		assert result.returncode != 0 and not destination.exists(), (name, value, result.stdout)
	report = dict(passed=True, mock=True, SDK_used=False, board_access=False,
		input_sources=['live_csi', 'official_dataset'], official_samples=12,
		release_command_EOF=True, same_boot_restart_rejected=True,
		missing_input_no_fallback=True, invalid_native_options=len(invalid))
	(root / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
	print(json.dumps(report))

if __name__ == '__main__':
	main()
