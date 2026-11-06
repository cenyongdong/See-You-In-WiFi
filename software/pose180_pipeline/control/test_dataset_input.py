"""Check official clip selection, raw coordinate layout and launch isolation."""
import argparse
import json
from pathlib import Path
import struct
import tempfile
from dataset_input import prepare_dataset, validate_dataset
from input_config import input_arguments

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('clip', type=Path)
	args = parser.parse_args()
	manifest = validate_dataset(args.clip)
	import h5py
	data = (args.clip / 'dataset.piwcsi2').read_bytes()
	for i, row in enumerate(manifest['samples']):
		record = data[i * 86432: (i + 1) * 86432]
		magic, version, size, frame, stamp = struct.unpack_from('<8sIIQQ', record)
		assert (magic, version, size, frame) == (b'PIWCSI2\0', 2, 86400, i + 1)
		assert stamp == 1000000000 + round(i * 1e9 / manifest['playback_hz'])
		with h5py.File(Path(manifest['dataset_root']) / (manifest['split'] + '_data') / 'csi' / (row['name'] + '.mat')) as file:
			raw = file['csi_out'][()]
		for rx, ant, t, carrier in [(0, 0, 0, 0), (2, 1, 17, 28), (1, 2, 19, 29)]:
			re, im = struct.unpack_from('<dd', record, 32 + (((rx * 3 + ant) * 20 + t) * 30 + carrier) * 16)
			assert re == raw['real'][t, carrier, ant, rx] and im == raw['imag'][t, carrier, ant, rx]
	native = input_arguments(args.clip, dict(input_source='official_dataset'))
	options = dict(zip(native[:: 2], native[1:: 2]))
	assert '--csi' not in options and options['--input-port'] == '0' and options['--dataset-repetitions'] == '1'
	repeated = input_arguments(args.clip, dict(input_source='official_dataset', dataset_repetitions=15))
	assert dict(zip(repeated[:: 2], repeated[1:: 2]))['--dataset-repetitions'] == '15'
	try:
		input_arguments(args.clip, {})
	except ValueError:
		pass
	else:
		raise AssertionError('Missing source must not enable live CSI')
	with tempfile.TemporaryDirectory() as temp:
		output = Path(temp) / 'invalid'
		try:
			prepare_dataset(manifest['dataset_root'], manifest['split'], manifest['sequence'],
				manifest['first_sample'], 9000, 15, output)
		except ValueError:
			pass
		else:
			raise AssertionError('Cross-recording clip was accepted')
		assert not output.exists()
	print(json.dumps(dict(passed=True, official_samples=manifest['count'],
		checks=['raw complex coordinate layout', 'record identity and synthetic cadence',
		'no cross-recording smoothing', 'explicit source selection'], SDK_calls=0)))

if __name__ == '__main__':
	main()
