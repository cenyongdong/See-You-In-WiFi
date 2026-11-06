"""Assemble r7 from maintained sources and qualified dependencies. No device access."""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import re
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fpga_dependencies as fd

ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = Path(__file__).resolve().parent / 'source_r5'
UPSTREAM = Path('D:/Person-in-WIFI-3D/Person-in-WiFi-3D-repo')
NAME = 'pose180-current-sources-20261104-r7'
SOURCE_DATE = '2026-11-04'
CURRENT_INPUTS = json.loads((ROOT / 'FPGA/current_sources.json').read_text(encoding='utf-8'))['files']
DEVELOPMENT = json.loads((ROOT / 'FPGA/development_sources.json').read_text(encoding='utf-8'))
PIPE = 'software/pose180_pipeline/'
NATIVE = ('buffer', 'renderer', 'overlay', 'postprocess', 'single_person',
    'release_guard', 'hdmi_resource', 'journal')
PRODUCTION = '''app/main.cpp io/io.cpp diagnostics/journal.cpp input/csi.cpp
input/dataset.cpp input/nexmon/ingress.cpp input/nexmon/adaptive_ingress.cpp
input/nexmon/pcap_stream.cpp preprocess/preprocess.cpp inference/runtime.cpp
display/hdmi_renderer.cpp display/projection.cpp display/hdmi_output.cpp
preprocess/pl_preprocess.cpp preprocess/polar_finish.cpp pose/postprocess.cpp
pose/single_person.cpp'''.split()

def sha(data):
    return hashlib.sha256(data).hexdigest()

class Package:
    def __init__(self, output):
        self.output = output
        if output.exists():
            raise FileExistsError('Preserve existing package: ' + str(output))
        output.mkdir(parents=True)
        self.records = {}

    def write(self, rel, data, source='generated', reason='current build support'):
        if isinstance(data, str):
            data = data.encode('utf-8')
        dest = self.output / rel
        if rel in self.records:
            if dest.read_bytes() != data:
                raise ValueError('Conflicting destination: ' + rel)
            return
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        self.records[rel] = dict(path=rel, bytes=len(data), sha256=sha(data), source=source, reason=reason)

    def copy(self, path, rel, reason):
        path = Path(path)
        if path.is_symlink():
            raise ValueError('Do not follow source links: ' + str(path))
        try:
            source = path.relative_to(ROOT).as_posix()
        except ValueError:
            source = 'Person-in-WiFi-3D/' + path.relative_to(UPSTREAM).as_posix()
        self.write(rel, path.read_bytes(), source, reason)

    def json(self, rel, value, reason='package metadata'):
        self.write(rel, json.dumps(value, ensure_ascii=False, indent=2) + '\n', reason=reason)

def quoted_closure(seeds, search):
    pending, seen = list(seeds), set()
    while pending:
        path = pending.pop().resolve()
        if path in seen:
            continue
        seen.add(path)
        data = path.read_text(encoding='utf-8-sig')
        for name in re.findall(r'^\s*#\s*include\s*"([^"]+)"', data, re.M):
            found = next((p for base in [path.parent, *search] if (p := base / name).is_file()), None)
            if found is None:
                raise FileNotFoundError(f'{path}: {name}')
            pending.append(found)
    return seen

def software(package):
    for name in ('CODING-STANDARDS.md', '.clang-format', '.editorconfig'):
        package.copy(ROOT / PIPE / name, PIPE + name, 'software coding rules and local configuration')
    src = ROOT / PIPE / 'src'
    dirs = [src / x for x in ('app', 'common', 'input', 'input/nexmon', 'inference',
        'pose', 'display', 'io', 'diagnostics', 'compat', 'preprocess')]
    test = ROOT / PIPE / 'tests'
    seeds = [src / x for x in PRODUCTION]
    seeds += [test / 'native' / (x + '_tests.cpp') for x in NATIVE]
    seeds += [ROOT / 'FPGA/csi_preprocess' / x for x in ('numeric_test.cpp', 'polar_model.cpp')]
    for path in sorted(quoted_closure(seeds, [*dirs, test / 'sdk_stub', ROOT / 'FPGA/csi_preprocess',
        ROOT])):
        if path.is_relative_to(src):
            rel = PIPE + 'src/' + path.relative_to(src).as_posix()
        elif path.is_relative_to(test):
            rel = 'tests/' + path.relative_to(test).as_posix()
        elif path.is_relative_to(ROOT / 'FPGA/csi_preprocess'):
            rel = path.relative_to(ROOT).as_posix()
        else:
            raise ValueError('Unexpected production source dependency: ' + str(path))
        package.copy(path, rel, 'formal pose180_demo or selected native check include closure')
    stub = 'icraft-xrt/core/device.h'
    package.copy(test / 'sdk_stub' / stub, 'tests/native/sdk_stub/' + stub,
        'angle-bracket SDK substitute used only by native HDMI resource checks')
    package.copy(TEMPLATES / 'CMakeLists.txt.in', 'CMakeLists.txt', 'root CMake entry')
    package.copy(TEMPLATES / 'pipeline.cmake.in', PIPE + 'CMakeLists.txt', 'pruned formal target and native checks')
    package.copy(TEMPLATES / 'aarch64-icraft.cmake.in', 'cmake/aarch64-icraft.cmake', 'ARM64 toolchain')
    package.copy(TEMPLATES / 'run_journal_test.cmake.in', 'cmake/run_journal_test.cmake', 'fresh Linux output for journal isolation test')
    presets = {
        'version': 5, 'cmakeMinimumRequired': {'major': 3, 'minor': 24, 'patch': 0},
        'configurePresets': [
        dict(name='csi-v3-arm64', generator='Unix Makefiles', binaryDir='${sourceDir}/build/arm64',
        toolchainFile='${sourceDir}/cmake/aarch64-icraft.cmake',
        cacheVariables={'CMAKE_BUILD_TYPE': 'Release', 'POSE180_BUILD_SDK': 'ON'}),
        dict(name='native-offline', generator='Unix Makefiles', binaryDir='${sourceDir}/build/native',
        cacheVariables={'CMAKE_BUILD_TYPE': 'Release', 'POSE180_BUILD_SDK': 'OFF', 'BUILD_TESTING': 'ON'})],
        'buildPresets': [dict(name='csi-v3-arm64', configurePreset='csi-v3-arm64', targets=['pose180_demo'],
        jobs=2),
        dict(name='native-offline', configurePreset='native-offline', jobs=2)],
        'testPresets': [dict(name='native-offline', configurePreset='native-offline', output={'outputOnFailure': True})]}
    package.json('CMakePresets.json', presets)

def development_cpp(package):
    """Keep offline probes reviewable; copying does not authorize their execution."""
    seeds = [ROOT / relative for relative in DEVELOPMENT['cpp']]
    search = [ROOT / relative for relative in (
        'FPGA/hdmi_candidate/software',
        'FPGA/csi_preprocess', 'software/pose180_pipeline/src/preprocess',
        'software/core/display', 'software/core/inference', 'software/core/contracts',
        'software/pose_v1/include',
        )] + [ROOT]
    for path in sorted(quoted_closure(seeds, search)):
        package.copy(path, path.relative_to(ROOT).as_posix(), 'FPGA offline development source/header dependency')

def python_closure(seeds, directory):
    pending, seen = list(seeds), set()
    while pending:
        path = pending.pop().resolve()
        if path in seen:
            continue
        seen.add(path)
        tree = ast.parse(path.read_text(encoding='utf-8-sig'))
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [n.name.split('.')[0] for n in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module.split('.')[0]]
            for name in names:
                local = directory / (name + '.py')
                if local.is_file():
                    pending.append(local)
    return seen

def runtime(package):
    control = ROOT / PIPE / 'control'
    names = ('startup.py', 'startup_network.py', 'boot_audit.py', 'service.py', 'process_guard.py',
        'run_hdmi_trial.py', 'bounded_log.py', 'input_config.py', 'dataset_input.py', 'csi_mat.py')
    for path in sorted(python_closure([control / n for n in names], control)):
        package.copy(path, PIPE + 'control/' + path.name, 'current startup/control local import closure')
    package.copy(control / 'startup-csi.conf', PIPE + 'control/startup-csi.conf', 'current CSI runtime configuration')
    for name in ('service.sh', 'watchdog.sh', 'install.sh'):
        package.copy(control / 'autostart' / name, PIPE + 'control/autostart/' + name, 'current router service source')
    # Preparation scripts reading old local radio packages are not runtime inputs.
    package.copy(control / 'router_guard.c', PIPE + 'control/router_guard.c', 'current router TX/RX resource guard')
    credential = ROOT / 'tools/device_credentials.py'
    texts = '\n'.join((package.output / p).read_text(encoding='utf-8') for p in package.records if p.endswith('.py'))
    if 'device_credentials' in texts:
        package.copy(credential, 'tools/device_credentials.py', 'credential loader only; no private credential files')
    host = ROOT / PIPE / 'host'
    for name in ('viewer_page.mjs', 'resident.mjs', 'resident_archive.mjs', 'full_record.mjs', 'presentation.mjs',
        'web/scene.js',
        'start-pc.ps1'):
        data = (host / name).read_text(encoding='utf-8-sig')
        if name == 'resident.mjs':
            data = data.replace('software/pc_viewer/node_modules/three/', 'third_party/three/')
        elif name == 'start-pc.ps1':
            data = data.replace('# Deployment-root launcher.', '# Source-package PC launcher.')
            data = data.replace('Join-Path $PSScriptRoot "pc/software/pose180_pipeline/host/resident.mjs"',
                'Join-Path $PSScriptRoot "resident.mjs"')
            data = data.replace('"pc/software/pose180_pipeline/host/web/scene.js"', '"web/scene.js"')
            data = data.replace('"pc/software/pc_viewer/node_modules/three/', '"../../../third_party/three/')
            data = data.replace('Run this launcher from the extracted deployment package.', 'Use the launcher in the extracted source package.')
            data = data.replace('Extract the complete deployment package or the PC asset repair patch into this folder.',
                'Verify the extracted source package and its third_party/three directory.')
        package.write(PIPE + 'host/' + name, data, PIPE + 'host/' + name, 'current PC resident service and offline web assets')
    three = ROOT / 'software/pc_viewer/node_modules/three'
    for name in ('build/three.module.js', 'build/three.core.js', 'examples/jsm/controls/OrbitControls.js',
        'LICENSE', 'package.json'):
        package.copy(three / name, 'third_party/three/' + name, 'Three.js offline viewer dependency or license/version')

def fpga(package):
    ref = ROOT / fd.REF
    hw = ROOT / fd.HW
    mapping = {}
    project = []
    factory = {}
    def project_file(path, rel):
        # 用维护中的源码覆盖旧快照；旧路径仍用于原始 Tcl 的重定位。
        maintained = ROOT / CURRENT_INPUTS['inputs/' + rel] if 'inputs/' + rel in CURRENT_INPUTS else path
        package.copy(maintained, rel, 'maintained source or unchanged qualified CSI v3 dependency')
        mapping[path.as_posix()] = '@ROOT@/' + rel
        project.append(rel)
    for group, names in {
        'system': ('hdmi_board.sv', 'ps_ai_peripheral.sv'),
        'csi': ('polar.sv', 'batch_banked.sv', 'atan_table.vh'),
        'skeleton_overlay': ('overlay.sv', 'palette_fifo.sv', 'font_rom.vh'),
        'pose_filter': ('pose_filter.sv', 'pose_filter_lane.sv', 'pose_filter_csr.sv')}.items():
        for name in names:
            project_file(hw / 'sources' / name, 'FPGA/rtl/' + group + '/' + name)
    for name in ('hdmi_cdc.tcl', 'ps_release_factory_clocks.tcl', 'consumer_capture_scope.tcl'):
        project_file(hw / 'sources' / name, 'FPGA/constraints/' + name)
    drain = ROOT / 'FPGA/hdmi_candidate/probe_free_drain/sources'
    for name in ('ps_ai_wrapper.sv', 'ps_ai.v', 'hp2_startup_drain.sv', 'hp2_deferred_control.sv',
        'deferred_control_cdc.tcl', 'startup_drain_bounds.tcl', 'consumer_paths_validate.tcl',
        'deferred_control_validate.tcl'):
        group = 'rtl/system' if Path(name).suffix in ('.v', '.sv') else 'constraints'
        project_file(drain / name, 'FPGA/' + group + '/' + name)
    project_file(drain.parent / 'strip_probe_attributes.tcl', 'FPGA/constraints/strip_probe_attributes.tcl')
    base = ROOT / 'FPGA/hdmi_candidate/baselines/ps_release_r26/sources'
    for name in ('ps_release_stub.v', 'ps-managed-io.xdc', 'implementation_opt_pre.tcl',
        'implementation_opt_post.tcl', 'implementation_route_post.tcl',
        'write_bitstream_pre.tcl', 'write_bitstream_post.tcl'):
        group = 'rtl/system' if name.endswith('.v') else 'constraints'
        project_file(base / name, 'FPGA/' + group + '/' + name)
    project_file(ROOT / 'FPGA/hdmi_candidate/skeleton_overlay/overlay_cdc.tcl', 'FPGA/constraints/overlay_cdc.tcl')
    stage_names = ('synthesis-banked', 'opt-banked', 'place-csi-incremental', 'route-csi-incremental',
        'report-closure', 'bit-closure')
    stages = {name: (hw / 'reports' / (name + '.tcl')).read_text(encoding='utf-8-sig') for name in stage_names}
    stages['procise'] = (hw / 'procise_run_disable_icap.tcl').read_text(encoding='utf-8-sig')
    used = '\n'.join(stages.values()).lower()
    dependencies = fd.collect(ROOT)
    factory_rtl = [p for p in dependencies.values() if p.is_relative_to(ref / 'rtl')
        and p.suffix.lower() in ('.v', '.sv', '.vh', '.vhd')]
    selected_rtl = {p for p in factory_rtl if p.as_posix().lower() in used}
    # color_bar 在厂商读取列表中间接使用此头文件，显式保留并设置 include 目录。
    selected_rtl.add(ref / 'rtl/display/video_define.v')
    pending = list(selected_rtl)
    while pending:
        source = pending.pop()
        for name in re.findall(r'^\s*`include\s+"([^"]+)"', source.read_text(encoding='utf-8', errors='replace'),
            re.M):
            header = source.parent / name
            if not header.is_file():
                matches = [p for p in factory_rtl if p.name == name]
                if len(matches) != 1:
                    raise ValueError(f'Cannot resolve RTL include {name} in {source}')
                header = matches[0]
            if header not in selected_rtl:
                selected_rtl.add(header)
                pending.append(header)
    vendor_content = {}
    for _, path in sorted(dependencies.items()):
        if path.is_relative_to(ref):
            original = path.relative_to(ref).as_posix()
            if (set(Path(original).parts) & {'doc', 'docs', 'example_design', '.Xil', 'xsim.dir'}
                or path.suffix.lower() in {'.zip', '.rar', '.log', '.jou', '.bak', '.pdf', '.md'}
                or path.name in {'datasheet.txt', 'tb_smpte_sdi.txt', 'tb_v_smpte_sdi.txt'}):
                continue
            # Root factory RTL snapshots not read by the qualified script are
            # excluded. Required generated IP subtrees keep their own layout.
            is_ip = '/ip/' in '/' + original or original.startswith(('fpai_demo_vivado.srcs/', 'PS_AI IP/'))
            if original.startswith('rtl/') and not is_ip and path.suffix.lower() in ('.v', '.sv', '.vh',
                '.vhd'):
                if path not in selected_rtl:
                    continue
            if original.startswith('ip_patch/'):
                dest = 'FPGA/vendor/adaptation/' + original[len('ip_patch/'):]
            elif path.suffix.lower() in ('.edif', '.edf', '.dcp'):
                dest = 'FPGA/vendor/netlists/' + original
            elif is_ip:
                dest = 'FPGA/vendor/ip/' + original
            elif original.startswith('rtl/'):
                dest = 'FPGA/vendor/rtl/' + original[4:]
            else:
                dest = 'FPGA/vendor/adaptation/project/' + original
            maintained = ROOT / CURRENT_INPUTS['factory/' + original] if 'factory/' + original in CURRENT_INPUTS else path
            data = maintained.read_bytes()
            digest = sha(data)
            if digest not in vendor_content:
                package.write(dest, data, maintained.relative_to(ROOT).as_posix(),
                    'required vendor IP, netlist, constraints or adapted factory flow')
                vendor_content[digest] = dest
            factory[original] = vendor_content[digest]
        elif path.as_posix().endswith(fd.INCREMENTAL):
            project_file(path, 'FPGA/reference/csi-v2-placement-reference.dcp')
        elif path.name == 'ps-export.dcp':
            project_file(path, 'FPGA/reference/ps-export.dcp')
        elif path.name != 'candidate.bif':
            project_file(path, 'FPGA/boot/' + path.name)
    # Generated copies, not packaged sources, receive relocated paths. This
    # also keeps encrypted vendor scripts and legal text byte-exact in the RAR.
    mapping[ref.as_posix()] = '@FACTORY@'
    mapping[hw.as_posix()] = '@BUILD@'
    # All explicit project input paths take precedence over the output prefix.
    for name, text in stages.items():
        for old, new in sorted(mapping.items(), key=lambda x: -len(x[0])):
            text = re.sub(re.escape(old), lambda m, v=new: v, text, flags=re.I)
        text = text.replace('set_property include_dirs {@BUILD@/sources}',
            'set_property include_dirs {@ROOT@/FPGA/rtl/csi @ROOT@/FPGA/rtl/skeleton_overlay}')
        if name == 'synthesis-banked':
            anchor = 'synth_design -top ai7030_edif_top'
            if text.count(anchor) != 1:
                raise ValueError('Unexpected synthesis entry count')
            include = 'set_property include_dirs [concat [get_property include_dirs [current_fileset]] [list {@FACTORY@/rtl/display}]] [current_fileset]\n'
            text = text.replace(anchor, include + anchor, 1)
        if ROOT.as_posix().lower() in text.lower():
            raise ValueError('Unrelocated workspace path in FPGA stage: ' + name)
        package.write('FPGA/scripts/' + name + '.tcl.in', text,
            fd.HW + ('/procise_run_disable_icap.tcl' if name == 'procise' else '/reports/' + name + '.tcl'),
            'qualified stage with path-only substitution')
    bif = '''//arch = fmql; split = false; format = BIN
the_ROM_image:
{
 [bootloader, destination_device = ps]@ROOT@/FPGA/boot/FSBL251210_ddr400_demo.out
 [destination_device = pl]@BUILD@/fpai_demo_vivado.runs/impl_pose_filter/ai7030_edif_top_disable_icap.bit
 [destination_cpu = apu_0, destination_device = ps]@ROOT@/FPGA/boot/bl31.elf
 [destination_cpu = apu_0, destination_device = ps]@ROOT@/FPGA/boot/u-boot
 [fsbl_config]apu_x32
}
'''
    package.write('FPGA/boot/candidate.bif.in', bif, reason='path-relocatable BOOT recipe; does not write BOOT')
    package.json('metadata/fpga-inputs.json', dict(project_files=sorted(project), factory_files=factory,
        legacy_paths=mapping))
    package.copy(TEMPLATES / 'build_fpga.py', 'tools/build_fpga.py', 'staged isolated FPGA rebuild driver')
    for path, rel in [(ROOT / 'FPGA/csi_preprocess/tb_batch.sv', 'FPGA/sim/tb_batch.sv'),
        (ROOT / 'FPGA/hdmi_candidate/skeleton_overlay/tb_overlay.sv', 'FPGA/sim/tb_overlay.sv')]:
        package.copy(path, rel, 'current CSI and overlay testbench')

def model(package):
    directory = ROOT / 'model/piw24_pose180_shared-20261024-r1'
    for name in ('piw24_pose180_ZG.json', 'piw24_pose180_ZG.raw', 'piw24_pose180.toml', 'source/pose180_shared.onnx'):
        package.copy(directory / name, 'model/pose180/' + name, 'current deployment model and conversion source/config')
    # Architecture dependency closure. Only module registration entrypoints are
    # reduced; model/algorithm implementations are copied without edits.
    bases = ['opera/models/pose180/head.py', 'opera/models/pose180/transformer.py', 'opera/models/pose180/detector.py',
        'opera/models/dense_heads/petr_head.py', 'opera/models/detectors/petr.py', 'opera/models/builder.py']
    for prefix in ('opera/models/utils', 'opera/models/losses', 'opera/core/bbox', 'opera/core/keypoint'):
        bases += [p.relative_to(UPSTREAM).as_posix() for p in (UPSTREAM / prefix).rglob('*.py')
            if p.name != 'transformer_wit.py']
    entrypoints = {
        'opera/__init__.py': '',
        'opera/models/__init__.py': 'from .builder import *\nfrom .utils import *\nfrom .losses import *\nfrom .dense_heads.petr_head import PETRHead\nfrom .detectors.petr import PETR\nfrom .pose180 import *\n',
        'opera/models/pose180/__init__.py': 'from .transformer import PETR180Transformer\nfrom .head import PETR180Head\nfrom .detector import PETR180\n',
        'opera/models/dense_heads/__init__.py': 'from .petr_head import PETRHead\n',
        'opera/models/detectors/__init__.py': 'from .petr import PETR\n',
        'opera/core/__init__.py': 'from .bbox import *\nfrom .keypoint import *\n'}
    for rel in sorted(set(bases)):
        if rel not in entrypoints:
            package.copy(UPSTREAM / rel, 'model/adaptation/' + rel, 'shared-refinement architecture dependency')
    for rel, data in entrypoints.items():
        package.write('model/adaptation/' + rel, data, reason='minimal model registration, excludes datasets/trainers/hooks')
    config_path = UPSTREAM / 'result/code_faithful/petr_wifi.py'
    tree = ast.parse(config_path.read_text(encoding='utf-8-sig'))
    value = next(n.value for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'model' for t in n.targets))
    # Config uses dict(...) expressions. Evaluate this expression with only dict
    # available, without importing the training project or executing config code.
    config = eval(compile(ast.Expression(value), str(config_path), 'eval'), {'__builtins__': {}, 'dict': dict})
    config['type'] = 'opera.PETR180'
    config['source_checkpoint'] = None
    config['bbox_head']['type'] = 'opera.PETR180Head'
    config['bbox_head']['num_query'] = 180
    config['bbox_head']['transformer']['type'] = 'opera.PETR180Transformer'
    config['bbox_head']['transformer']['two_stage_num_proposals'] = 180
    config['test_cfg'] = dict(max_per_img=180)
    import pprint
    package.write('model/adaptation/model_config.py', 'model = ' + pprint.pformat(config, sort_dicts=False,
        width=100) + '\n',
        'Person-in-WiFi-3D model dictionary + current pose180 overrides', 'self-contained current model configuration')
    for name in ('export_model.py', 'convert_model.py'):
        if (TEMPLATES / name).exists():
            package.copy(TEMPLATES / name, 'tools/' + name, 'optional explicit model export/conversion helper')

def synthetic_fixtures(package):
    import math
    import struct
    fixture = bytearray(86432)
    fixture[: 8] = b'PIWCSI2\0'
    for i in range(5400):
        angle = (i % 30) * .23 + (i // 30 % 20) * .07
        amplitude = 1 + (i * 17 % 101) / 13
        struct.pack_into('<dd', fixture, 32 + i * 16, amplitude * math.cos(angle), amplitude * math.sin(angle))
    package.write('tests/fixtures/synthetic.piwcsi2', fixture, reason='one deterministic synthetic CSI window, not official measurements')
    vectors = ROOT / fd.HW / 'reports/batch-175241/vectors.hex'
    synthetic_vectors = vectors.read_text(encoding='ascii').splitlines()[: 1536]
    if len(synthetic_vectors) != 1536:
        raise ValueError('Missing deterministic CORDIC reference vectors')
    # The existing testbench repeats at 1836 entries. Fill the tail with
    # additional synthetic vectors rather than the official window samples.
    package.write('tests/fixtures/vectors.hex', '\n'.join(synthetic_vectors + synthetic_vectors[: 300]) + '\n',
        vectors.relative_to(ROOT).as_posix(), 'synthetic portion of qualified CORDIC vectors, repeated to match testbench length')

def package_documents(package):
    package.copy(ROOT / 'LICENSE', 'LICENSES/project-MIT.txt', 'project license original')
    package.copy(UPSTREAM / 'LICENSE', 'LICENSES/Person-in-WiFi-3D-Apache-2.0.txt', 'base model license original')
    for source, label in ((ROOT, 'project'), (UPSTREAM, 'Person-in-WiFi-3D')):
        if (source / 'NOTICE').is_file():
            package.copy(source / 'NOTICE', 'LICENSES/' + label + '-NOTICE', 'original notice')
    package.copy(TEMPLATES / 'README.md.in', 'README.md', 'single technical documentation entrypoint')

    package.copy(ROOT / 'Docs/llm_usage.md', 'llm_usage.md', 'original AI-assisted development statement')
    for name in ('.editorconfig', '.clang-format'):
        package.copy(ROOT / 'FPGA' / name, 'FPGA/' + name, 'FPGA local formatting settings')
    standards = (ROOT / 'FPGA/CODING-STANDARDS.md').read_text(encoding='utf-8')
    for old, new in {
        '(development_sources.json)': '(../metadata/development-sources.json)',
        '(current_sources.json)': '(../metadata/refactored-inputs.json)',
        '(README.md)': '(../README.md)',
        '(../AGENTS.md)': '(https://github.com/cenyongdong/See-You-In-WiFi/blob/master/AGENTS.md)',
        '(../REFERENCES.md)': '(https://github.com/cenyongdong/See-You-In-WiFi/blob/master/REFERENCES.md)',
        '(../tools/release/prepare_refactored_fpga.py)': '(../tools/build_fpga.py)',
        }.items():
        standards = standards.replace(old, new)
    standards += '\n本包独立构建入口为 `tools/build_fpga.py`，命令以根 README 为准；仓库开发入口的参数不直接套用。\n'
    package.write('FPGA/CODING-STANDARDS.md', standards, 'FPGA/CODING-STANDARDS.md', 'same rules with package-local navigation')
    package.json('metadata/development-sources.json', dict(cpp=DEVELOPMENT['cpp'], device_programs_executed=False))
    mapped = {row['source']: row['path'] for row in package.records.values()}
    package.json('metadata/refactored-inputs.json', {
        source: mapped[source] for source in CURRENT_INPUTS.values()
        })
    package.copy(ROOT / 'Deliverables/evidence/fpga-refactor-20261104-r1/qualification-closure.json',
        'metadata/fpga-qualification.json', 'existing complete implementation; not a new board test')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    package = Package(args.output.resolve())
    software(package)
    runtime(package)
    development_cpp(package)
    fpga(package)
    model(package)
    for name in ('check_package.py', 'simulate.py'):
        package.copy(TEMPLATES / name, 'tools/' + name, 'offline package check or RTL simulation entry')
    synthetic_fixtures(package)
    package_documents(package)
    package.json('metadata/build-environment.json', dict(
        package=NAME, date=SOURCE_DATE, base_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'],
        cwd=ROOT, text=True).strip(),
        docker=dict(container='FPAI', historical_tag='ubuntu20.04:custom',
        image_id='sha256:397a49458ae85e065c484eaa3a83d4b5cc248f78bdf6a534e2414ce275e591db',
        rootfs='ubuntu20.04_container.tar', rootfs_format='docker import', ubuntu='20.04.6 LTS'),
        software=dict(cmake='3.24.2', native_gcc='9.4.0', aarch64_gcc='9.4.0', icraft_customop='3.39.0',
        prefix='/usr/cmake'),
        fpga=dict(vivado='2018.3 factory-adapted (SW Build 2405991)', procise='2025.1.1 temp / SVN 32494',
        device='JFMQL30TAI676H',
        vivado_logical_part='xc7z030ffg676-2', original_ps_period_ns=20, original_gp_period_ns=10),
        validation=dict(state='see_release_validation_report', device_operations=0,
        note='Final archive validation is reported in the GitHub Release; qualification JSON covers the matched RTL implementation only.')))
    package.json('metadata/source-manifest.json', dict(schema=1, package=NAME,
        note='Provenance paths identify original inputs only; build does not read the original workspace. Manifest excludes itself.',
        files=sorted(package.records.values(), key=lambda r: r['path'])))
    print(json.dumps(dict(output=str(package.output), files=len(package.records),
        bytes=sum(r['bytes'] for r in package.records.values())), ensure_ascii=False))

if __name__ == '__main__':
    main()
