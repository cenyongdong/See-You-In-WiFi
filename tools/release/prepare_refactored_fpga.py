"""Build maintained FPGA sources with a qualified dependency package, without device access."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('qualified_fpga_flow', Path(__file__).parent / 'source_r5/build_fpga.py')
FLOW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FLOW)

def restore_vendor_headers(output):
# 仅补齐可证明来源一致的原厂头文件；不改写厂商逻辑或运行工具。
    from fpga_dependencies import REF
    vendor_root = ROOT / REF / 'rtl'
    restored = []
    for consumer in (output / 'factory/rtl').rglob('*'):
        if consumer.suffix.lower() not in ('.v', '.sv', '.vh') or not consumer.is_file():
            continue
        for include in re.findall(r'^\s*`include\s+"([^"]+)"', consumer.read_text(errors='replace'), re.M):
            target = consumer.parent / include
            if target.exists():
                continue
            original = vendor_root / consumer.relative_to(output / 'factory/rtl')
            if not original.is_file() or original.read_bytes() != consumer.read_bytes():
                raise RuntimeError('Cannot verify vendor include owner: ' + str(consumer))
            source = (original.parent / include).resolve(strict=True)
            source.relative_to(vendor_root.resolve())
            shutil.copyfile(source, target)
            restored.append(dict(source=source.relative_to(ROOT).as_posix(),
                input=target.relative_to(output).as_posix(),
                sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
    if restored:
        script = output / 'synthesis-banked.tcl'
        text = script.read_text(encoding='utf-8-sig')
        parents = sorted({(output / item['input']).parent.as_posix() for item in restored})
        directories = ' '.join('{' + parent + '}' for parent in parents)
        anchor = 'synth_design -top ai7030_edif_top'
        text = text.replace(anchor, 'set_property include_dirs [concat [get_property include_dirs [current_fileset]] [list ' + directories + ']] [current_fileset]\n' + anchor,
            1)
        script.write_text(text, encoding='utf-8')
    return restored

def prepare(reference, output, procise):
    mapping = json.loads((ROOT / 'FPGA/current_sources.json').read_text(encoding='utf-8'))['files']
    # Resolve the entire maintained input set before copying the dependency package.
    sources = {}
    for destination, relative in mapping.items():
        source = (ROOT / relative).resolve(strict=True)
        target = (output / destination).resolve()
        source.relative_to(ROOT)
        target.relative_to(output)
        sources[destination] = source
    FLOW.prepare(reference, output, procise)
    records = []
    for destination, source in sources.items():
        target = output / destination
        if not target.is_file():
            raise FileNotFoundError('Dependency package has no mapped source: ' + str(target))
        baseline = hashlib.sha256(target.read_bytes()).hexdigest()
        shutil.copyfile(source, target)
        records.append(dict(source=source.relative_to(ROOT).as_posix(), input=destination,
            baseline_sha256=baseline, sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
    # Older compact packages omitted headers referenced by unselected vendor modules.
    # Restore only verified dependencies from the qualified local vendor reference.
    restored = restore_vendor_headers(output)
    records.extend(restored)
    manifest = dict(sources=records, hardware_profile='probe-free-drain-overlay-csi-v3',
        board_tested=False, deployment_qualified=False, reference_package=str(reference))
    (output / 'current-source-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print('Prepared maintained source inputs:', len(records), flush=True)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'run'))
    parser.add_argument('--reference-package', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--stage', choices=(*FLOW.STAGES, 'all'), default='all')
    parser.add_argument('--vivado', type=Path, default=Path('D:/vivado18.3/Vivado/2018.3/bin/vivado.bat'))
    parser.add_argument('--procise', type=Path, default=Path('C:/FudanMicro/Procise'))
    args = parser.parse_args()
    output = args.output.resolve()
    if args.action == 'prepare':
        if not args.reference_package:
            parser.error('--reference-package is required for prepare')
        prepare(args.reference_package.resolve(strict=True), output, args.procise.resolve(strict=True))
    else:
        manifest = json.loads((output / 'current-source-manifest.json').read_text())
        for item in manifest['sources']:
            actual = hashlib.sha256((output / item['input']).read_bytes()).hexdigest()
            if actual != item['sha256']:
                raise RuntimeError('Staged input changed after preparation: ' + item['input'])
        for stage in FLOW.STAGES if args.stage == 'all' else(args.stage,):
            FLOW.run_stage(output, stage, args.vivado)

if __name__ == '__main__':
    main()
