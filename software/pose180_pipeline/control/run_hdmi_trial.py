"""One admitted CSI/HDMI trial; a deadline requests stop, never kills the SDK."""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

def sha(path):
	h = hashlib.sha256()
	with Path(path).open('rb') as source:
		for block in iter(lambda: source.read(1048576), b''):
			h.update(block)
	return h.hexdigest()

def owners():
	result = []
	for fd in Path('/proc').glob('[0-9]*/fd/*'):
		try:
			target = os.readlink(fd)
			if target.startswith(('/dev/axi', '/dev/udmabuf', '/dev/u-dma', '/dev/video')):
				result.append([str(fd), target])
		except OSError:
			pass
	return result

def preflight(root):
	identity = json.loads((root / 'identity.json').read_text())
	model = Path(identity['model_package'])
	if (root / 'models').resolve() != (model / 'models').resolve():
		raise ValueError('Model directory differs')
	boot = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
	admission = json.loads((root / 'startup-admission.json').read_text())
	if not admission['passed'] or admission['boot_id'] != boot:
		raise ValueError('Fresh same-boot admission absent')
	if identity.get('hardware_profile') == 'probe-free-drain-v1':
		if (admission.get('hardware_profile') != 'probe-free-drain-v1' or admission.get('mode') != 'functional_startup_pending'
			or admission.get('candidate_boot_sha256') != identity.get('candidate_boot_sha256')
			or not identity.get('candidate_boot_sha256') or admission.get('passive_diagnostic_MMIO') != 0
			or admission.get('functional_startup_ABI') != 0x48444302):
			raise ValueError('Functional-consumer BOOT/profile binding differs')
	elif identity.get('hardware_profile') == 'probe_free':
		if (admission.get('hardware_profile') != 'probe_free' or admission.get('mode') != 'probe_free'
			or admission.get('candidate_boot_sha256') != identity.get('candidate_boot_sha256')
			or not identity.get('candidate_boot_sha256') or admission.get('diagnostic_MMIO') != 0):
			raise ValueError('Uninstrumented BOOT/profile binding differs')
	elif admission.get('observer_generation') != 4:
		raise ValueError('Instrumented startup observation absent')
	if (root / 'startup-mode.txt').read_text().strip() != admission['mode']:
		raise ValueError('Admission mode differs')
	if not os.access(root / 'pose180_demo', os.X_OK):
		raise ValueError('Native executable permission missing; SDK not started')
	metadata = root / 'metadata'
	metadata.mkdir()
	# Package preparation and the same-boot restore already checked files.
	# Reuse those receipts; only inspect live state before the sole SDK call.
	restored = json.loads((root.parent / 'boot-control/metadata/restore.json').read_text())
	if not restored['passed'] or restored['boot_id'] != boot or not restored['boot_partition_unmounted']:
		raise ValueError('Same-boot original restoration absent')
	before = dict(file_checks='reused package preparation and same-boot restore',
		fpga_state=Path('/sys/class/fpga_manager/fpga0/state').read_text().strip(),
		SDK_packages=subprocess.check_output(['dpkg-query', '-W', '-f=${Package} ${Architecture} ${Version}\n',
		'icraft:arm64', 'customop:arm64'], universal_newlines=True).splitlines())
	(metadata / 'before.json').write_text(json.dumps(before, indent=2))
	if before['fpga_state'] != 'operating' or before['SDK_packages'] != ['customop arm64 3.39.0', 'icraft arm64 3.39.0']:
		raise ValueError('FPGA/SDK differs')
	if owners():
		raise ValueError('Existing device owner')
	return identity, boot, metadata

def main():
	root = Path(__file__).resolve().parent
	identity, boot, metadata = preflight(root)
	with (root / 'sdk-attempt.json').open('x') as file:
		json.dump(dict(boot_id=boot, SDK_attempts=1, hdmi=True, CSI_live=True, runtime_seconds=180), file)
	command = [str(root / 'pose180_demo'), '--package', str(root), '--output', str(root / 'run'),
		'--bind', '0.0.0.0', '--session', str(identity['session']), '--seconds', '180', '--hdmi', '1',
		'--csi', str(root / 'csi.conf')]
	(metadata / 'before.dmesg').write_bytes(subprocess.check_output(['dmesg']))
	started = time.monotonic()
	reason = None
	stop_sent = False
	with (metadata / 'native.stdout.log').open('xb') as out, (metadata / 'native.stderr.log').open('xb') as err:
		child = subprocess.Popen(command, stdout=out, stderr=err)
		(metadata / 'process.json').write_text(json.dumps(dict(pid=child.pid,
			start_ticks=Path('/proc/%d/stat' % child.pid).read_text().split()[21], argv=command)))
		print('RESIDENT_HDMI_LAUNCHED pid=%d' % child.pid, flush=True)
		with (metadata / 'resources.jsonl').open('x') as log:
			while child.poll() is None:
				memory = Path('/proc/meminfo').read_text()
				try:
					status = Path('/proc/%d/status' % child.pid).read_text()
				except FileNotFoundError:
					break
				log.write(json.dumps(dict(elapsed=time.monotonic() - started, status=status, meminfo=memory)) + '\n')
				log.flush()
				available = next(int(line.split()[1]) for line in memory.splitlines() if line.startswith('MemAvailable:'))
				if available < 131072:
					reason = 'MemAvailable below 128 MiB'
				if time.monotonic() - started > 240:
					reason = reason or 'Stop requested after 240 seconds; observing original SDK call'
				if reason and not stop_sent:
					child.send_signal(signal.SIGTERM)
					stop_sent = True
					print(reason, flush=True)
				time.sleep(1)
	native = child.wait()
	(metadata / 'after.dmesg').write_bytes(subprocess.check_output(['dmesg']))
	final = {}
	for line in (metadata / 'native.stdout.log').read_text(errors='replace').splitlines():
		offset = line.find('{"state"')
		if offset >= 0:
			try:
				final = json.loads(line[offset:])
			except ValueError:
				pass
	outcome = dict(native_exit=native, seconds=time.monotonic() - started, stop_reason=reason, final_status=final,
		device_owners=owners(), boot_id=boot, final_boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
		SDK_attempts=1, hdmi=True, CSI_live=True, physical_screen_verified=False, automatic_retry=False)
	(root / 'outcome.json').write_text(json.dumps(outcome, indent=2))
	print(json.dumps(outcome), flush=True)
	return native

if __name__ == '__main__':
	raise SystemExit(main())
