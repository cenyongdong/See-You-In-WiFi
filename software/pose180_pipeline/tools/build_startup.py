"""Build the shared live-CSI/HDMI core and its offline checks; no board access."""
import argparse
import json
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
DOCKER = 'C:/Program Files/Docker/Docker/resources/bin/docker.exe'

def main():
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument('--work', type=Path, required=True)
	parser.add_argument('--resume', action='store_true', help='Reuse successful stages from this unchanged build')
	args = parser.parse_args()
	work = args.work.resolve()
	work.mkdir(parents=True, exist_ok=True)
	relative = work.relative_to(ROOT).as_posix()
	source = '/workspace/software/pose180_pipeline'
	base = '/workspace/' + relative
	steps = json.loads((work / 'build.json').read_text()) if args.resume else []

	resume_reusable = args.resume

	def run(name, *command):
		nonlocal resume_reusable
		if resume_reusable and any(step['stage'] == name and step['native_exit'] == 0
			and step['argv'] == list(command) for step in steps):
			return
		# A changed configure command invalidates all following cached stages.
		resume_reusable = False
		started = time.monotonic()
		log_path = work / (str(len(steps)).zfill(2) + '-' + name + '.log')
		with log_path.open('xb') as log:
			result = subprocess.run([DOCKER, *command], stdout=log, stderr=subprocess.STDOUT)
		steps.append(dict(stage=name, argv=command, native_exit=result.returncode,
			seconds=time.monotonic() - started, log=log_path.name))
		(work / 'build.json').write_text(json.dumps(steps, indent=2) + '\n')
		print(json.dumps(steps[-1]), flush=True)
		if result.returncode:
			raise RuntimeError(name + ': ' + log_path.read_text(errors='replace')[-4000:])

	state = subprocess.check_output([DOCKER, 'inspect', '--format', '{{.State.Status}}', 'FPAI']).strip()
	started_here = state == b'exited'
	if started_here:
		run('container-start', 'start', 'FPAI')
	try:
		run('native-configure', 'exec', '-w', source, 'FPAI', 'cmake', '--preset', 'native-offline', '-B',
			base + '/native')
		targets = ['postprocess_tests', 'single_person_tests', 'renderer_tests', 'display_state_tests',
			'buffer_tests', 'journal_tests', 'release_guard_tests', 'hdmi_resource_tests', 'pose180_demo_mock']
		run('native-build', 'exec', 'FPAI', 'cmake', '--build', base + '/native', '--parallel', '2', '--target',
			*targets)
		for name in targets[: -1]:
			extra = [base + '/journal-test'] if name == 'journal_tests' else []
			run(name, 'exec', 'FPAI', base + '/native/' + name, *extra)
		run('arm64-configure', 'exec', '-w', source, 'FPAI', 'cmake', '--preset', 'csi-v3-arm64', '-B',
			base + '/arm64')
		run('arm64-build', 'exec', 'FPAI', 'cmake', '--build', base + '/arm64', '--target', 'pose180_demo',
			'pose180_pipeline', '--parallel', '2')
	finally:
		if started_here:
			run('container-stop', 'stop', 'FPAI')

if __name__ == '__main__':
	main()
