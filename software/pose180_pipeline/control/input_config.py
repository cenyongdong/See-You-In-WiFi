"""Resolve one input adapter before networking or SDK initialization.

The selected source is recorded per run. An unavailable dataset never falls
back to live collection. Older single-source packages keep their own default.
"""
from pathlib import Path
import math


def selection_arguments(identity):
	# 旧包无 selection 时保留其 Top1 入口，新包显式声明展示策略。
	selection = identity.get('selection', dict(top_k=1, strict_score_threshold=None, single_person_stability=True))
	top = selection.get('top_k')
	threshold = selection.get('strict_score_threshold')
	single = selection.get('single_person_stability')
	if (type(top) is not int or not 1 <= top <= 3 or type(single) is not bool
		or (single and top != 1) or (threshold is not None and
		(type(threshold) not in (float, int) or not math.isfinite(threshold) or not 0 <= threshold <= 1))):
		raise ValueError('Invalid presentation selection')
	return ['--top-k', str(top), '--score-threshold', 'none' if threshold is None else str(threshold),
		'--single-person-stability', str(int(single))]


def select_input(root, identity, source=None, repetitions=None):
	source = source or identity.get('input_source')
	available = identity.get('input_sources', [identity.get('input_source')])
	if source not in ('live_csi', 'official_dataset') or source not in available:
		raise ValueError('Requested input is not included in this package')
	selected = dict(input_source=source)
	if 'selection' in identity:
		selection_arguments(identity)
		selected['selection'] = identity['selection'].copy()
	if source == 'official_dataset':
		from dataset_input import validate_dataset
		manifest = validate_dataset(root)
		passes = repetitions if repetitions is not None else identity.get('dataset_repetitions', 1)
		# Keep the per-file bound (9000), but permit a bounded 30-minute run
		# at 15 Hz without restarting the SDK between playlist passes.
		if type(passes) is not int or not 1 <= passes <= 30 or manifest['count'] * passes > 36000:
			raise ValueError('Dataset requires 1..30 passes and at most 36000 total inputs')
		selected.update(dataset_repetitions=passes, dataset_sha256=manifest['sha256'],
						split=manifest['split'], sequence=manifest['sequence'], count=manifest['count'])
		if manifest['schema'] == 'PIWPLAYLIST1':
			selected['dataset_segment_frames'] = [clip['count'] for clip in manifest['clips']]
	else:
		if repetitions is not None:
			raise ValueError('Dataset repetitions require official_dataset input')
		if not (Path(root)/'csi.conf').is_file():
			raise ValueError('Live CSI configuration is missing')
	return selected


def input_arguments(root, identity):
	source = identity.get('input_source')
	if source == 'official_dataset':
		if not (Path(root)/'dataset.piwcsi2').is_file():
			raise ValueError('Prepared dataset is missing')
		arguments = ['--dataset', str(Path(root)/'dataset.piwcsi2'), '--input-port', '0',
			'--dataset-repetitions', str(identity.get('dataset_repetitions',1))]
		if 'dataset_segment_frames' in identity:
			arguments += ['--dataset-segment-frames', ','.join(map(str, identity['dataset_segment_frames']))]
		return arguments
	if source == 'live_csi':
		return ['--csi', str(Path(root)/'csi.conf'), '--input-port', '0']
	raise ValueError('New package must explicitly select official_dataset or live_csi')
