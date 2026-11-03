"""Run installed Icraft CLI stages in a fresh output folder, without a board."""
import argparse
from pathlib import Path
import shutil
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--icraft', required=True, type=Path, help='Installed Icraft 3.39 CLI executable')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Choose a fresh output directory; delivered JSON/RAW are never overwritten')
    model = Path(__file__).resolve().parents[1] / 'model/pose180'
    args.output.mkdir(parents=True)
    shutil.copytree(model / 'source', args.output / 'source')
    shutil.copyfile(model / 'piw24_pose180.toml', args.output / 'piw24_pose180.toml')
    for stage in ('parse', 'optimize', 'quantize', 'adapt', 'generate'):
        with (args.output / (stage + '.log')).open('xb') as log:
            subprocess.run([str(args.icraft.resolve()), stage, 'piw24_pose180.toml'], cwd=args.output,
                           stdout=log, stderr=subprocess.STDOUT, check=True)
        print(stage + ': native exit 0', flush=True)


if __name__ == '__main__':
    main()
