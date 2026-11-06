"""Assemble a relocatable demonstration release with a verified model pair.

All operations are local. Does not deploy, install autostart or consume a board test.
"""
import argparse
import hashlib
import math
import json
from pathlib import Path
import re
import shutil
import tarfile
import sys
import io
import subprocess

ROOT = Path(__file__).resolve().parents[3]
CONTROL = ROOT / 'software/pose180_pipeline/control'
DOCS = ROOT / 'software/pose180_pipeline/resident'
sys.path.insert(0, str(CONTROL))
from dataset_input import validate_dataset

RUNTIME = ('startup.py', 'startup_network.py', 'boot_audit.py', 'service.py', 'process_guard.py',
	'run_hdmi_trial.py', 'bounded_log.py', 'input_config.py', 'dataset_input.py', 'csi_mat.py')

def sha(path):
	digest = hashlib.sha256()
	with path.open('rb') as stream:
		for block in iter(lambda: stream.read(1048576), b''):
			digest.update(block)
	return digest.hexdigest()

def write(path, value):
	path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

def copy(source, destination):
	destination.parent.mkdir(parents=True, exist_ok=True)
	shutil.copyfile(source, destination)

def model_selection(directory, original):
	if directory is None:
		folder = ROOT / 'model/piw24_pose180_shared-20261024-r1'
		names = {name: expected for name, expected in original['files'].items() if name.startswith('models/')}
		for name, expected in names.items():
			if sha(folder / Path(name).name) != expected:
				raise ValueError('Original epoch99 model differs: ' + name)
		return folder, original['model'], names, None
	folder = directory.resolve()
	candidate = json.loads((folder / 'candidate.json').read_text(encoding='utf-8'))
	graph = json.loads((folder / 'piw24_pose180_ZG.json').read_text())
	raw = (folder / 'piw24_pose180_ZG.raw').read_bytes()
	if (graph.get('ai_target') != '@zhuget(330)' or graph.get('icraft_version') != 'v3.39.0'
		or graph.get('swap_mode') or graph.get('params_bytes') != len(raw)
		or graph.get('params_md5') != hashlib.md5(raw).hexdigest()):
		raise ValueError('Candidate target, version or JSON/RAW pairing differs')
	if any(op['_type_key'] not in {'icraft::xir::Input', 'icraft::xir::Output', 'icraft::xir::HardOp'}
		for op in graph['ops']):
		raise ValueError('Candidate contains unsupported Host operations')
	inputs = [op for op in graph['ops'] if op['_type_key'] == 'icraft::xir::Input']
	outputs = [op for op in graph['ops'] if op['_type_key'] == 'icraft::xir::Output']
	if len(inputs) != 1 or len(outputs) != 1:
		raise ValueError('Candidate port count differs')
	ports = inputs[0]['outputs'] + outputs[0]['inputs']
	if ([p['dtype']['shape'] for p in ports] != [[1, 180, 60], [1, 180], [1, 180, 14, 3]]
		or any(p['dtype']['element_dtype'] != '@fp(32)' for p in ports)):
		raise ValueError('Candidate public ports differ')
	names = {}
	for name in ('piw24_pose180_ZG.json', 'piw24_pose180_ZG.raw'):
		actual = sha(folder / name)
		if candidate['model_files'][name]['sha256'] != actual:
			raise ValueError('Candidate identity differs: ' + name)
		names['models/' + name] = actual
	return folder, candidate['candidate'], names, candidate

def archive(folder, output, prefix=''):
	with tarfile.open(output, 'x:gz') as result:
		for path in sorted(folder.rglob('*')):
			if not path.is_file():
				continue
			name = path.relative_to(folder).as_posix()
			info = result.gettarinfo(str(path), arcname=prefix + name)
			info.mode = 0o755 if path.name == 'pose180_demo' or path.suffix == '.sh' else 0o644
			with path.open('rb') as stream:
				result.addfile(info, stream)

def source_snapshot(work, destination):
	files = set()
	# CMake source targets plus the actual project header dependency closure.
	for folder in ('software/pose180_pipeline/src', 'software/pose180_pipeline/tests',
		'software/pose180_pipeline/tools/native', 'software/core/input', 'tools/pose180'):
		files.update(p for p in (ROOT / folder).rglob('*') if p.suffix in ('.h', '.hpp', '.cpp'))
	files.add(ROOT / 'software/pose180_pipeline/CMakeLists.txt')
	files.add(ROOT / 'software/pose180_pipeline/CMakePresets.json')
	files.add(ROOT / 'software/pose180_pipeline/.clang-format')
	files.add(ROOT / 'software/pose180_pipeline/.editorconfig')
	files.add(ROOT / 'software/core/README.md')
	for dependency in work.glob('*/CMakeFiles/**/*.o.d'):
		for path in re.findall(r'/workspace/[^\s\\]+', dependency.read_text()):
			source = (ROOT / path[len('/workspace/'):]).resolve()
			if source.is_file() and not source.is_relative_to(ROOT / '.local'):
				files.add(source)
	for name in RUNTIME:
		files.add(CONTROL / name)
	files.update(CONTROL.glob('test_*.py'))
	# Support files used by the retained offline input/lease tests.
	for name in ('witness.py', 'router_guard.c', 'router_watchdog.sh', 'router_ctl.sh'):
		files.add(CONTROL / name)
	files.update((ROOT / 'software/pose180_pipeline/host').rglob('*.mjs'))
	files.add(ROOT / 'software/pose180_pipeline/host/web/scene.js')
	files.add(ROOT / 'software/pose180_pipeline/host/start-pc.ps1')
	for name in ('build/three.module.js', 'build/three.core.js', 'examples/jsm/controls/OrbitControls.js',
		'LICENSE'):
		files.add(ROOT / 'software/pc_viewer/node_modules/three' / name)
	files.add(CONTROL / 'startup-csi.conf')
	files.add(DOCS / 'STARTUP-PACKAGE.md')
	for name in ('README.md', 'CODING-STANDARDS.md', '.clang-format', '.editorconfig', 'src/README.md', 'control/README.md', 'host/README.md', 'tests/README.md'):
		files.add(ROOT / 'software/pose180_pipeline' / name)
	for name in ('FINAL-REVIEW.md', 'DEMO-INPUTS.md', 'DATASET-PLAYLIST.md'):
		if (DOCS / name).is_file():
			files.add(DOCS / name)
	files.add(ROOT / 'FPGA/hdmi_candidate/default_boot.json')
	if (DOCS / 'KINECT-BOARD-TEST-20261028.md').is_file():
		files.add(DOCS / 'KINECT-BOARD-TEST-20261028.md')
	files.add(Path(__file__))
	files.add(Path(__file__).with_name('build_startup.py'))
	with tarfile.open(destination, 'x:gz') as result:
		guide = ('# 核心源码归档\n\n'
			'从 software/pose180_pipeline/src/README.md 开始阅读；'
			'输入说明与审查记录在 software/pose180_pipeline/resident/。\n\n'
			'保留原仓库相对路径，CMake 目标为 pose180_demo（ARM64）和 pose180_demo_mock（本地）。'
			'含两种输入、SDK 所有权、HDMI／PC、构建配置和离线检查。'
			'不含模型权重、SDK 安装文件、运行日志、凭据或新 PL 开发。'
			'正式硬件继续使用 default_boot.json 对应的既有合格版本；完整演示包含其 BOOT 备份。\n').encode('utf-8')
		info = tarfile.TarInfo('SOURCE-README.md')
		info.size = len(guide)
		info.mode = 0o644
		result.addfile(info, io.BytesIO(guide))
		for path in sorted(files):
			result.add(path, arcname=path.relative_to(ROOT).as_posix())
	return len(files)

def main():
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument('--work', required=True, type=Path)
	parser.add_argument('--build-work', type=Path, help='Reuse an existing verified build without rebuilding or modifying it')
	parser.add_argument('--model-dir', type=Path, help='Independent converted candidate with candidate.json; default is original epoch99')
	parser.add_argument('--default-seconds', type=int, default=0, help='Default manual run duration; 0 runs until manual stop')
	parser.add_argument('--dataset', type=Path, help='Prepared official clip; enables both live CSI and dataset launchers')
	parser.add_argument('--input-source', choices=('live_csi', 'official_dataset'), default='live_csi')
	parser.add_argument('--dataset-repetitions', type=int, default=1)
	parser.add_argument('--top-k', type=int, choices=(1, 2, 3), default=3)
	parser.add_argument('--score-threshold', default='0.2', help='Strict cutoff, or none')
	parser.add_argument('--single-person-stability', action='store_true', help='CPU Top1 only')
	parser.add_argument('--output', type=Path, default=ROOT / 'Deliverables')
	args = parser.parse_args()
	threshold = None if args.score_threshold == 'none' else float(args.score_threshold)
	if (threshold is not None and (not math.isfinite(threshold) or not 0 <= threshold <= 1)) or (args.single_person_stability and args.top_k != 1):
		parser.error('Invalid confidence cutoff or single-person/TopK combination')
	selection = dict(top_k=args.top_k, strict_score_threshold=threshold, single_person_stability=args.single_person_stability)
	selection_text = ('TopK=' + str(args.top_k) + '、' + ('无置信度阈值' if threshold is None else '严格 score > ' + str(threshold)) +
		('、CPU 单人增强滤波' if args.single_person_stability else '、CPU 多人跟踪／滤波'))
	work = args.work.resolve()
	build = args.build_work.resolve() if args.build_work else work
	build_record = json.loads((build / 'build.json').read_text())
	verification = json.loads((build / 'verification.json').read_text())
	if not build_record or any(step.get('native_exit') != 0 for step in build_record) or verification.get('passed') is not True:
		raise ValueError('A deployment package requires successful native build and local verification records')
	checks = build / 'final-checks' if (build / 'final-checks').is_dir() else build
	safety_file = checks / 'native-safety-final/result.json'
	if not safety_file.is_file():
		safety_file = build / 'runtime-checks/test_native_safety/result.json'
	safety_record = json.loads(safety_file.read_text()) if safety_file.is_file() else {}
	safety_verified = (safety_record.get('unproved', {}).get('lease_retained') is True
		and safety_record.get('nonstandard', {}).get('resources_released') is True)
	if not 0 <= args.default_seconds <= (2 ** 64 - 1) // 1000000000:
		parser.error('--default-seconds exceeds native duration range')
	dataset = validate_dataset(args.dataset) if args.dataset else None
	playlist = bool(dataset and dataset['schema'] == 'PIWPLAYLIST1')
	dataset_text = ''
	if dataset:
		if playlist:
			dataset_text = '一次启动，按以下顺序在同一 SDK 进程内播放，片段之间不重启开发板；每段切换重置跟踪状态。\n\n'
			dataset_text += '| 顺序 | 人数 | 官方来源 | 样本范围 | 展示时长 |\n|---|---|---|---|---|\n'
			for i, clip in enumerate(dataset['clips'], 1):
				dataset_text += '| ' + str(i) + ' | ' + str(clip['people']) + ' | ' + clip['split'] + ' / ' + clip['sequence'] + ' | ' + str(clip['first_sample']) + '–' + str(clip['first_sample'] + clip['count'] - 1) + ' | ' + str(clip['count'] / clip['playback_hz']) + ' 秒 |\n'
			dataset_text += '\n每段 15 Hz 播放时长为演示时间线，不作为原始采集时长。片段边界有约 0.1 秒收尾间隔。'
		else:
			dataset_text = dataset['split'] + ' / ' + dataset['sequence'] + '，' + str(dataset['count']) + ' 帧、' + str(dataset['playback_hz']) + ' Hz。'
	if args.input_source == 'official_dataset' and not dataset:
		parser.error('--input-source official_dataset requires --dataset')
	if (not 1 <= args.dataset_repetitions <= 30 or
		(dataset and dataset['count'] * args.dataset_repetitions > 9000) or
		(not dataset and args.dataset_repetitions != 1)):
		parser.error('Dataset playback requires 1..30 passes and at most 9000 total inputs')
	original = json.loads((ROOT / 'software/pose180_pipeline/evidence/20261025/original-boot/software-identity.json').read_text())
	model_dir, model_name, model_files, candidate = model_selection(args.model_dir, original)
	work.mkdir(parents=True, exist_ok=True)
	release = work / 'release'
	release.mkdir()
	board = release / 'board'
	board.mkdir()
	deployed = json.loads((ROOT / 'FPGA/hdmi_candidate/default_boot.json').read_text())
	if deployed['hardware_profile'] != 'probe-free-drain-overlay-csi-v3':
		raise ValueError('Release launcher requires the currently qualified hardware profile')
	cache = {}
	for line in (build / 'arm64/CMakeCache.txt').read_text().splitlines():
		if ':' in line and '=' in line and not line.startswith(('//', '#')):
			key, value = line.split('=', 1)
			cache[key.split(':', 1)[0]] = value
	for key, expected in {'POSE180_BUILD_SDK': 'ON', 'POSE180_DEMO_PROBE_FREE_DRAIN': 'ON',
		'POSE180_DEMO_PL_FILTER': 'ON', 'POSE180_DEMO_PL_OVERLAY': 'ON',
		'POSE180_DEMO_PL_CSI': 'ON', 'POSE180_DEMO_PL_POST': 'OFF'}.items():
		if cache.get(key) != expected:
			raise ValueError('Build does not match CSI v3: ' + key + '; configure with csi-v3-arm64')
	copy(build / 'arm64/pose180_demo', board / 'pose180_demo')
	with (board / 'pose180_demo').open('rb') as stream:
		header = stream.read(20)
	if header[: 6] != b'\x7fELF\x02\x01' or int.from_bytes(header[18: 20], 'little') != 183:
		raise ValueError('Expected a little-endian ARM64 ELF executable')
	for name in RUNTIME:
		copy(CONTROL / name, board / name)
	copy(CONTROL / 'startup-csi.conf', board / 'csi.conf')
	if dataset:
		for name in ('dataset.piwcsi2', 'dataset.json'):
			copy(args.dataset / name, board / name)
	for name in model_files:
		copy(model_dir / Path(name).name, board / name)
	if candidate:
		copy(model_dir / 'candidate.json', release / 'validation/model-candidate.json')
		copy(model_dir / 'host-comparison.json', release / 'validation/model-host-comparison.json')
	boot_files = {entry['name']: entry['sha256'] for entry in original['protected_original_boot_files']
		if entry['name'] in ('BOOT.BIN', 'IMAGE', 'FMQLMP~1.DTB', 'UENV.TXT')}
	boot_files['BOOT.BIN'] = deployed['BOOT_sha256']
	boot = ROOT / deployed['BOOT_path']
	if sha(boot) != deployed['BOOT_sha256']:
		raise ValueError('Qualified BOOT differs')
	copy(boot, release / 'boot/BOOT.BIN')
	for source_name, name in (('qualification-closure.json', 'qualification.json'),
		('package-review.json', 'package-review.json')):
		copy(ROOT / deployed['hardware_work'] / 'reports' / source_name, release / 'boot' / name)
	identity = dict(package=work.name, selection=selection,
		model=model_name, input_source=args.input_source, csi_alignment='adaptive',
		input_sources=['live_csi', 'official_dataset'] if dataset else ['live_csi'],
		dataset_repetitions=args.dataset_repetitions,
		phase_preprocessing='original', hardware_profile=deployed['hardware_profile'],
		preprocess_backend='pl', renderer_backend='pl', csi_ABI='0x43534903', overlay_ABI='0x534b4c01',
		BOOT_sha256=deployed['BOOT_sha256'], boot_files=boot_files,
		verified_boot_ids=[], libraries=original['SDK_libraries'],
		SDK_autostart=False, automatic_retry=False,
		runtime_safety='release-blocked-v1' if safety_verified else 'see-build-record',
		presentation_filter='single-person-continuity-v1' if args.single_person_stability else 'tracked-one-euro-v5: CPU 0.5/0.3/1',
		files={p.relative_to(board).as_posix(): sha(p) for p in board.rglob('*') if p.is_file()})
	write(board / 'identity.json', identity)
	for script, action in [('start', 'start'), ('stop', 'stop'), ('status', 'status'), ('check', 'check'),
		('recover', 'recover'), ('prepare-boot', 'prepare-boot')]:
		defaults = ' --seconds ' + str(args.default_seconds) if action == 'start' else ''
		(release / (script + '.sh')).write_text('#!/bin/sh\nset -eu\nroot=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)\nexec python3 "$root/board/startup.py" ' + action + defaults + ' "$@"\n',
			newline='\n')
	for script, source in [('start-live', 'live_csi')] + ([('start-dataset', 'official_dataset')] if dataset else []):
		(release / (script + '.sh')).write_text(
			'#!/bin/sh\nset -eu\nroot=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)\n'
			'exec python3 "$root/board/startup.py" start --seconds ' + str(args.default_seconds) +
			' --input-source ' + source + ' "$@"\n', newline='\n')
	for name in ('viewer_page.mjs', 'resident.mjs', 'presentation.mjs', 'full_record.mjs', 'resident_archive.mjs'):
		copy(ROOT / 'software/pose180_pipeline/host' / name, release / 'pc/software/pose180_pipeline/host' / name)
	copy(ROOT / 'software/pose180_pipeline/host/web/scene.js', release / 'pc/software/pose180_pipeline/host/web/scene.js')
	three = ROOT / 'software/pc_viewer/node_modules/three'
	for name in ('build/three.module.js', 'build/three.core.js', 'examples/jsm/controls/OrbitControls.js',
		'LICENSE'):
		copy(three / name, release / 'pc/software/pc_viewer/node_modules/three' / name)
	copy(ROOT / 'software/pose180_pipeline/host/start-pc.ps1', release / 'start-pc.ps1')
	count = source_snapshot(build, release / 'core-sources.tar.gz')
	copy(DOCS / 'STARTUP-PACKAGE.md', release / 'STARTUP-GUIDE.md')
	for name in ('DEMO-INPUTS.md', 'FINAL-REVIEW.md', 'DATASET-PLAYLIST.md'):
		if (DOCS / name).is_file():
			copy(DOCS / name, release / name)
	if candidate:
		copy(DOCS / 'KINECT-BOARD-TEST-20261028.md', release / 'KINECT-BOARD-TEST-20261028.md')
	(release / 'README.md').write_text(
		'# ' + work.name + '\n\n'
		'首次部署请先读 [部署与演示步骤](DEPLOY.md)。本包由整理后的 `src/`、`control/`、`host/` 源码构建，源码快照见 `core-sources.tar.gz`。\n\n'
		'模型：`' + model_name + '`。' + selection_text + '。默认输入：`' + args.input_source + '`。\n\n' +
		('双输入：`sh start-live.sh` 接实时CSI；`sh start-dataset.sh` 对包内官方CSI执行新推理，EOF正常退出。'
		'数据来源：' + dataset_text + '\n\n训练集演示不计独立测试精度。\n\n' if dataset else '') +
		'所用构建与本地检查见validation记录；本包尚未部署或实板验证。保留原HDMI和PC性能指标栏。\n\n'
		'以root执行 `sh check.sh` 核对，`sh start.sh` 手动开始，`sh status.sh` 查看，`sh stop.sh` 请求正常停止。'
		'默认处理期为' + str(args.default_seconds) + '秒（0表示手动停止）；可用 `sh start.sh --seconds 300` 显式指定。\n\n'
		'一次只运行一个输入；切换前须安全停止、确认SDK／HDMI关闭，再prepare-boot、正常重启并重新check。每次FPGA配置只使用一次功能启动入口。'
		'`release_blocked`表示完成未证明，必须保留资源与独占，不强杀、不自动重试或切换模型。\n\n'
		'未知boot_id按STARTUP-GUIDE.md处理，不跳过BOOT身份检查。包内BOOT仅为备份，不会自动安装或重启。'
		'PC运行 `start-pc.ps1`；停止PC不影响板端。\n\n'
		'完整操作与边界见 [启动说明](STARTUP-GUIDE.md)；实际构建、故障注入与模型身份在 `validation/`。\n',
		encoding='utf-8', newline='\n')
	(release / 'DEPLOY.md').write_text(
		'# 部署与演示步骤\n\n'
		'适用：ARM64 Lite、板端既有 Icraft/customop 3.39.0、当前合格 `probe-free-drain-overlay-csi-v3` BOOT。'
		'板端需要 Python 3；PC 可选，需要 Node.js 20 或以上。原 epoch99 模型，' + selection_text + '。\n\n'
		'## 解压到独立目录\n\n'
		'先将 `' + work.name + '.tar.gz` 复制到开发板 `/tmp/`。以 root 执行以下解压命令；若目标目录已经存在，先选择另一个独立目录，避免覆盖已有运行记录。\n\n'
		'```sh\ntar -xzf /tmp/' + work.name + '.tar.gz -C /root\ncd /root/' + work.name + '\n```\n\n'
		'推荐部署位置为 `/root/' + work.name + '`；也可整体解压到其它可写位置，脚本按自身目录定位。'
		'模型在 `board/models/`，运行记录在 `board/runs/`。' +
		('官方输入在 `/root/' + work.name + '/board/dataset.piwcsi2`，来源及校验信息在同目录 `dataset.json`。'
		'主机已完成原始 CSI 格式转换，板端仍执行预处理与新推理，不需要安装 NumPy／h5py。\n\n' if dataset else '\n\n') +
		'## 启动前\n\n'
		'若旧包仍在运行，先使用旧包的停止入口，并确认原生进程、监督进程及设备占用结束且关闭证明成立。'
		'本包 `stop.sh` 只管理本包，不能用来结束其它目录的旧任务。\n\n'
		'本硬件每次 FPGA 配置只能消费一次功能启动入口。已使用过、或首次 `check.sh` 报未知 boot_id 时，'
		'在旧任务安全结束后执行下列只读 BOOT 核对，再安排正常重启：\n\n'
		'```sh\nsh prepare-boot.sh\n# 仅当 prepared=true，且已有任务安全结束后：\nreboot\n```\n\n'
		'重连后回到本包目录再执行所选输入的 check。`prepare-boot.sh` 只核对启动文件并保存下一次启动凭据，'
		'不写 BOOT、不自行重启。核对失败或仍有占用时先处理原因；包内 `boot/BOOT.BIN` 仅作备份。\n\n'
		'## 选择一次演示\n\n' +
		('官方预采数据：\n\n```sh\nsh check.sh --input-source official_dataset\nsh start-dataset.sh\nsh status.sh\n```\n\n'
		+dataset_text + '\n\n'
		'默认一轮，EOF 正常退出；需要更长展示时，在首次启动前选择 `sh start-dataset.sh --dataset-repetitions 3`。'
		'训练片段演示不计独立测试精度。\n\n' if dataset else '') +
		'实时采集：\n\n```sh\nsh check.sh --input-source live_csi\nsh start-live.sh\nsh status.sh\n```\n\n'
		'实时入口复用已安装的路由器采集服务；默认处理期为 ' + str(args.default_seconds) + ' 秒（0 表示持续到手动停止），也可在首次启动时指定 `--seconds 300`。'
		'`start.sh` 的默认输入为 `' + args.input_source + '`。\n\n'
		'## 结束、切换与 PC\n\n'
		'`sh stop.sh` 请求正常停止；随后用 `sh status.sh` 核对 `running=false`、`native_shutdown_complete=true`、'
		'`device_owners=[]` 和 `network_cleanup_pending=false`。数据集 EOF 后同样核对。'
		'本包清单内的片段自动顺序切换，无需中途停止或重启。整轮结束后再次启动程序，或切换到实时输入，仍须重新准备 BOOT 凭据、正常重启并 check。'
		'若为 `release_blocked` 或缺少完成证明，保留原资源与独占，按 STARTUP-GUIDE.md 处理，不强杀或重试。\n\n'
		'PC 解压同一个包，在 Windows 包根目录执行 `./start-pc.ps1`，浏览器打开 `http://127.0.0.1:39380/`。'
		'默认板端地址 `192.168.50.49`；可用 `./start-pc.ps1 -Board <实际可达地址>` 指定。'
		'关闭 PC 服务不停止板端推理和 HDMI。\n\n'
		'本包只完成本地构建、mock／接口替身与 PC 验证；本次打包没有连接设备或安装任何服务。\n',
		encoding='utf-8', newline='\n')
	for name in ('build.json', 'verification.json'):
		copy(build / name, release / 'validation' / name)
	for step in build_record:
		copy(build / step['log'], release / 'validation/build-logs' / step['log'])
	for check in verification.get('checks', []):
		for field in ('log', 'result'):
			relative = check.get(field)
			if not isinstance(relative, str):
				continue
			origin = (build / relative).resolve()
			if origin.is_relative_to(build) and origin.is_file():
				copy(origin, release / 'validation' / origin.relative_to(build))
	for relative in verification.get('retained_attempts', []):
		origin = (build / relative).resolve()
		if origin.is_relative_to(build) and origin.is_file():
			copy(origin, release / 'validation' / origin.relative_to(build))
	for name in ('pc-verified.log', 'official-data-verified.log'):
		if (build / name).is_file():
			copy(build / name, release / 'validation' / name)
	if (work / 'clip-selection.json').is_file():
		copy(work / 'clip-selection.json', release / 'validation/clip-selection.json')
	revision = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()
	write(release / 'validation/build-reuse.json', dict(build_work=str(build), native_sha256=identity['files']['pose180_demo'],
		git_base=revision, source_of_truth='core-sources.tar.gz includes final working-tree changes'))
	if (build / 'final-review-tests.json').is_file():
		copy(build / 'final-review-tests.json', release / 'validation/final-review-tests.json')
	manifest = dict(package=work.name, selection=identity['selection'], model=identity['model'],
		runtime_safety=identity['runtime_safety'],
		input_sources=identity['input_sources'], default_input=identity['input_source'],
		input='explicit source selection; PL CSI polar with original PS phase finish', outputs=['HDMI',
		'PC raw:39383', 'PC filtered:39385'],
		runtime_seconds_default=args.default_seconds, SDK_autostart=False, automatic_retry=False,
		board_tested=False, hardware_rebuilt=False, core_source_files=count,
		validation='Local C++/mock/PC checks only; no new board or collection run',
		files={p.relative_to(release).as_posix(): dict(bytes=p.stat().st_size, sha256=sha(p))
		for p in release.rglob('*') if p.is_file()})
	write(release / 'manifest.json', manifest)
	args.output.mkdir(exist_ok=True, parents=True)
	output = args.output / (work.name + '.tar.gz')
	archive(release, output, work.name + '/')
	deployment_guide = args.output / (work.name + '-DEPLOY.md')
	copy(release / 'DEPLOY.md', deployment_guide)
	result = dict(archive=str(output), bytes=output.stat().st_size, sha256=sha(output),
		deployment_guide=str(deployment_guide),
		native_sha256=identity['files']['pose180_demo'], model=identity['model'],
		top_k=args.top_k, score_threshold=threshold, single_person_stability=args.single_person_stability,
		BOOT_sha256=identity['BOOT_sha256'], board_tested=False)
	write(work / 'package.json', result)
	(output.with_suffix(output.suffix + '.sha256')).write_text(result['sha256'] + '  ' + output.name + '\n')
	print(json.dumps(result))

if __name__ == '__main__':
	main()
