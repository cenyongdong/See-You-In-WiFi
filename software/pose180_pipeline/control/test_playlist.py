"""Check one-process playlist boundaries, selection and cleanup using Linux mock."""
import argparse
import copy
import contextlib
import io
import json
from pathlib import Path
import struct
import subprocess
import sys
from unittest.mock import patch

import startup

from dataset_input import prepare_playlist, sha, validate_dataset
from input_config import select_input
from startup import command
from test_dataset import free_port

def main():
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument('binary', type=Path)
	parser.add_argument('output', type=Path)
	args = parser.parse_args()
	root = args.output.resolve()
	root.mkdir()
	clips = []
	for i, count in enumerate((3, 5, 7), 1):
		folder = root / ('clip' + str(i))
		folder.mkdir()
		data = folder / 'dataset.piwcsi2'
		# Explicit synthetic protocol fixture; never packaged as official input.
		data.write_bytes(b''.join(
			struct.pack('<8sIIQQ', b'PIWCSI2\0', 2, 86400, j + 1, 1000000000 + j * 20000000)
			+struct.pack('<dd', float(i), .25) * 5400 for j in range(count)))
		manifest = dict(schema='PIWDATASET1', input_source='official_dataset',
			split='train', sequence='mock-' + str(i), first_sample=1, count=count,
			playback_hz=50, file=data.name, sha256=sha(data),
			samples=[dict(frame=j + 1, name='mock') for j in range(count)])
		(folder / 'dataset.json').write_text(json.dumps(manifest))
		clips.append(folder)
	playlist = root / 'playlist'
	manifest = prepare_playlist(clips, [1, 2, 3], playlist)
	identity = dict(input_source='official_dataset', input_sources=['official_dataset', 'live_csi'],
		selection=dict(top_k=3, strict_score_threshold=.2, single_person_stability=False))
	(playlist / 'csi.conf').write_text('# unused mock configuration\n')
	selected = select_input(playlist, identity)
	assert selected['dataset_segment_frames'] == [3, 5, 7]
	live = select_input(playlist, identity, 'live_csi')
	assert live['selection'] == identity['selection'] and 'dataset_segment_frames' not in live
	# 预检回显必须与真正传入原生进程的展示策略一致。
	(playlist / 'identity.json').write_text(json.dumps(identity))
	text = io.StringIO()
	with patch.object(startup, '__file__', str(playlist / 'startup.py')), patch.object(startup, 'preflight',
		return_value='mock-boot'), patch.object(sys, 'argv', ['startup.py', 'check']), contextlib.redirect_stdout(text):
		startup.main(None)
	check = json.loads(text.getvalue())
	assert check['top_k'] == 3 and check['score_threshold'] == .2
	assert check['single_person_stability'] is False and check['SDK_started'] is False

	def launch(name, passes=1, extra=None):
		choice = select_input(playlist, identity, repetitions=passes)
		argv = command(playlist, root / name, 12000, 0, choice)
		options = dict(zip(argv[1:: 2], argv[2:: 2]))
		assert options['--top-k'] == '3' and options['--score-threshold'] == '0.2'
		assert options['--single-person-stability'] == '0'
		options.update({'--hdmi': '0', '--hardware-profile': 'r45', '--mock-delay-ms': '1',
			'--result-port': str(free_port()), '--status-port': str(free_port()), '--view-port': '0'})
		if extra:
			options.update(extra)
		(root / name).mkdir()
		return subprocess.run([str(args.binary.resolve())] +
			[word for pair in options.items() for word in pair], capture_output=True, text=True, timeout=10)

	for name, passes in [('once', 1), ('twice', 2)]:
		result = launch(name, passes)
		assert result.returncode == 0, result.stdout + result.stderr
		done = json.loads((root / name / 'run/completion.json').read_text())
		status = done['status']
		assert done['native_shutdown_complete'] and status['dataset_done']
		assert status['received'] == status['inferred'] == 15 * passes
		assert status['dataset_passes'] == passes and status['post_resets'] == 3 * passes - 1
		assert status['top_k'] == 3 and abs(status['score_threshold'] - .2) < 1e-6
		observed = []
		for path in (root / name).rglob('*.full'):
			data = path.read_bytes()
			for offset in range(0, len(data), 74544):
				epoch, frame, sequence, stamp = struct.unpack_from('<QQQQ', data, offset + 16)
				observed.append((sequence, epoch, frame, stamp))
		observed.sort()
		expected = [(12000 + p * 3 + c, f + 1, 1000000000 + f * 20000000)
			for p in range(passes) for c, count in enumerate((3, 5, 7)) for f in range(count)]
		assert [row[1:] for row in observed] == expected

	for i, sizes in enumerate(('3,5,6', '0,5,10', '3,,12', '3,5,7,', '9001')):
		assert launch('invalid' + str(i), extra={'--dataset-segment-frames': sizes}).returncode != 0
	broken = copy.deepcopy(manifest)
	broken['clips'][1]['offset_frames'] = 1
	(playlist / 'dataset.json').write_text(json.dumps(broken))
	try:
		validate_dataset(playlist)
	except ValueError:
		pass
	else:
		raise AssertionError('Bad boundary accepted')
	(playlist / 'dataset.json').write_text(json.dumps(manifest))
	result = dict(passed=True, mock=True, SDK_used=False, board_access=False,
		one_process_sequence=True, per_clip_epoch_and_tracking_reset=True,
		playlist_repetition=True, invalid_boundaries_rejected=6,
		check_output_matches_launch=True,
		top_k=3, strict_score_threshold=.2, single_person_stability=False)
	(root / 'result.json').write_text(json.dumps(result, indent=2))
	print(json.dumps(result))

if __name__ == '__main__':
	main()
