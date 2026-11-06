"""Prepare a finite official CSI clip. No devices, labels, inference or UI changes."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct

RECORD_BYTES = 86432

def sha(path):
	h = hashlib.sha256()
	with Path(path).open('rb') as stream:
		for block in iter(lambda: stream.read(1048576), b''):
			h.update(block)
	return h.hexdigest()

def validate_dataset(directory):
	directory = Path(directory)
	manifest = json.loads((directory / 'dataset.json').read_text(encoding='utf-8'))

	# 先检查来源和片段边界，再核对实际数据文件，避免混用训练／测试或不同片段。
	if (
		not isinstance(manifest, dict)
		or manifest.get('schema') not in ('PIWDATASET1', 'PIWPLAYLIST1')
		or manifest.get('input_source') != 'official_dataset'
		or manifest.get('file') != 'dataset.piwcsi2'
		or manifest.get('split') not in ('train', 'test')
		or not isinstance(manifest.get('sequence'), str) or not manifest['sequence']
		or type(manifest.get('count')) is not int
		or not 1 <= manifest.get('count', 0) <= 9000
		or (manifest['schema'] == 'PIWDATASET1' and len(manifest.get('samples', [])) != manifest['count'])
		):
		raise ValueError('Invalid dataset manifest')
	if manifest['schema'] == 'PIWPLAYLIST1':
		clips = manifest.get('clips')
		if not isinstance(clips, list) or not 1 <= len(clips) <= 30:
			raise ValueError('Invalid playlist clips')
		total = 0
		for clip in clips:
			if (not isinstance(clip, dict) or type(clip.get('count')) is not int
				or not 1 <= clip['count'] <= 9000 or clip.get('split') != manifest['split']
				or not isinstance(clip.get('sequence'), str) or not clip['sequence']
				or len(clip.get('samples', [])) != clip['count']
				or type(clip.get('people')) is not int or not 1 <= clip['people'] <= 3
				or clip.get('offset_frames') != total):
				raise ValueError('Invalid playlist segment or provenance')
			total += clip['count']
		if total != manifest['count']:
			raise ValueError('Playlist counts differ')

	data = directory / manifest['file']
	if data.stat().st_size != manifest['count'] * RECORD_BYTES or sha(data) != manifest['sha256']:
		raise ValueError('Dataset bytes differ from prepared source')
	return manifest

def prepare_playlist(directories, people, output):
	# 各片段保留自身帧号／时间线；边界由清单显式交给板端，不拼接跟踪历史。
	if not 1 <= len(directories) <= 30 or len(directories) != len(people):
		raise ValueError('Playlist requires matching clips and person counts')
	manifests = [validate_dataset(path) for path in directories]
	if (any(m['schema'] != 'PIWDATASET1' for m in manifests)
		or len({m['split'] for m in manifests}) != 1
		or len({m['playback_hz'] for m in manifests}) != 1
		or sum(m['count'] for m in manifests) > 9000
		or any(type(n) is not int or not 1 <= n <= 3 for n in people)):
		raise ValueError('Playlist requires bounded clips from one split and playback rate')
	output = Path(output)
	output.mkdir(parents=True, exist_ok=False)
	data = output / 'dataset.piwcsi2'
	clips = []
	total = 0
	with data.open('xb') as target:
		for directory, manifest, count in zip(directories, manifests, people):
			with (Path(directory) / manifest['file']).open('rb') as source:
				for block in iter(lambda: source.read(1048576), b''):
					target.write(block)
			clips.append(dict(manifest, people=count, offset_frames=total))
			total += manifest['count']
	manifest = dict(schema='PIWPLAYLIST1', input_source='official_dataset', CSI_live=False,
		dataset='Person-in-WiFi 3D', split=manifests[0]['split'],
		sequence=' -> '.join(m['sequence'] for m in manifests), count=total,
		playback_hz=manifests[0]['playback_hz'], file=data.name, bytes=data.stat().st_size,
		sha256=sha(data), clips=clips, ground_truth_used_as_input=False,
		source_time='Independent synthetic clip timelines; tracking resets at every boundary')
	(output / 'dataset.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
	return validate_dataset(output)

def prepare_dataset(dataset_root, split, sequence, start, count, hz, output):
	# 按官方索引选择同一段连续采样，不跨录制拼接，也不使用标签作为输入。
	if (
		split not in ('test', 'train')
		or (count is not None and not 1 <= count <= 9000)
		or not math.isfinite(hz)
		or not 1 <= hz <= 60
		):
		raise ValueError('Finite clip (1..9000) and playback rate (1..60 Hz) required')

	folder = Path(dataset_root) / (split + '_data')
	names = (folder / (split + '_data_list.txt')).read_text(encoding='utf-8-sig').splitlines()
	selected = {}
	for value in names:
		name = value.strip()
		if not name:
			continue
		if Path(name).name != name or '/' in name or '\\' in name:
			raise ValueError('Unexpected dataset list entry')
		stem = name[: -4] if name.endswith('.mat') else name
		prefix, number = stem.rsplit('_', 1)
		if prefix == sequence:
			index = int(number)
			if index in selected:
				raise ValueError('Duplicate sample in official list')
			selected[index] = stem
	if not selected:
		raise ValueError('Sequence not found in official split list')

	first = min(selected) if start is None else start
	if count is None:
		count = 1
		while first + count in selected and count < 9000:
			count += 1
	indices = list(range(first, first + count))
	if any(i not in selected for i in indices):
		raise ValueError('Clip crosses a missing sample or recording boundary; choose a shorter contiguous clip')
	sources = [folder / 'csi' / (selected[i] + '.mat') for i in indices]
	if any(not p.is_file() for p in sources):
		raise ValueError('CSI MAT file missing')
	from csi_mat import aligned_payload

	output = Path(output)
	output.mkdir(parents=True, exist_ok=False)
	data = output / 'dataset.piwcsi2'
	with data.open('xb') as stream:
		for i, source in enumerate(sources):
			# 只转换原始 CSI 的存储布局；预处理与推理仍由板端执行。
			payload = aligned_payload(source)
			stamp = 1000000000 + round(i * 1000000000 / hz)
			stream.write(struct.pack('<8sIIQQ', b'PIWCSI2\0', 2, 86400, i + 1, stamp))
			stream.write(payload)

	# 播放时间线属于演示节奏，显式记录其来源，不冒充真实射频采样时间。
	manifest = dict(
		schema='PIWDATASET1', input_source='official_dataset', CSI_live=False,
		dataset='Person-in-WiFi 3D', dataset_root=str(Path(dataset_root).resolve()),
		split=split, sequence=sequence, first_sample=first, count=count, playback_hz=hz,
		source_time='synthetic clip timeline at playback_hz; not measured RF time',
		layout='RX,antenna,time,carrier,real-imag / float64 little-endian',
		file=data.name, bytes=data.stat().st_size, sha256=sha(data), ground_truth_used_as_input=False,
		samples=[dict(frame=i + 1, name=selected[index]) for i, index in enumerate(indices)]
		)
	(output / 'dataset.json').write_text(
		json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8'
		)
	return manifest

def main():
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument('--dataset-root', type=Path, required=True, help='Official data/wifipose directory')
	parser.add_argument('--split', choices=('test', 'train'), default='test')
	parser.add_argument('--sequence', required=True, help='One recording prefix, e.g. S11_01')
	parser.add_argument('--start', type=int)
	parser.add_argument('--count', type=int, help='Default: continuous run from --start, capped at 9000')
	parser.add_argument('--hz', type=float, default=15)
	parser.add_argument('--output', type=Path, required=True)
	args = parser.parse_args()
	result = prepare_dataset(args.dataset_root, args.split, args.sequence, args.start, args.count, args.hz,
		args.output)
	print(json.dumps({k: v for k, v in result.items() if k != 'samples'}, ensure_ascii=False))

if __name__ == '__main__':
	main()
