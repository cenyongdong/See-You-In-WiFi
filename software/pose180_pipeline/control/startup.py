"""Manual release launcher. One SDK owner; reuse the bounded, graceful supervisor.

No startup hook, BOOT write, reboot, router login or automatic SDK retry.
"""
import argparse
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from service import atomic, live, process_identity, supervise
from process_guard import request_stop, StopRequest
from run_hdmi_trial import owners
from boot_audit import fat_files
import startup_network
from input_config import select_input, input_arguments, selection_arguments

LOCK = Path('/run/pose180-resident.lock')
ACTIVE = Path('/run/pose180-resident.active.json')


def read(path):
	return json.loads(path.read_text())


def sha(path):
	value = hashlib.sha256()
	with path.open('rb') as stream:
		for block in iter(lambda: stream.read(1048576), b''):
			value.update(block)
	return value.hexdigest()


def boot_id():
	return Path('/proc/sys/kernel/random/boot_id').read_text().strip()


def verify_files(root, identity):
	for name, expected in identity['files'].items():
		if sha(root/name) != expected:
			raise ValueError('Release file changed: '+name)
	if not os.access(root/'pose180_demo', os.X_OK):
		raise ValueError('Native executable permission missing')


def verify_boot(identity):
	if Path('/sys/class/fpga_manager/fpga0/state').read_text().strip() != 'operating':
		raise ValueError('FPGA is not operating')
	actual = {entry['name']: entry['sha256'] for entry in fat_files()}
	for name, expected in identity['boot_files'].items():
		if actual.get(name) != expected:
			raise ValueError('Qualified startup file differs: '+name)
	return actual['BOOT.BIN']


def authorize_boot(root, identity):
	current = boot_id()
	verify_boot(identity)
	if current in identity['verified_boot_ids']:
		return current
	receipt = root/'next-boot.json'
	prepared = read(receipt) if receipt.exists() else {}
	if (prepared.get('BOOT_sha256') != identity['BOOT_sha256'] or
			not prepared.get('previous_boot_id') or prepared['previous_boot_id'] == current):
		raise ValueError('Unknown running BOOT. Run prepare-boot, then explicitly reboot before starting')
	# Read-only before/after startup-file identity plus a changed Linux boot ID.
	# The native functional ABI/idle/drain checks remain the final device gate.
	return current


def previous_run(root):
	latest = root/'latest.json'
	if not latest.exists():
		return None
	name = read(latest)['run']
	if Path(name).name != name:
		raise ValueError('Invalid run directory')
	return root/'runs'/name


def optional_json(path):
	try:
		value=read(path)
		return value if isinstance(value,dict) else {}
	except (OSError, ValueError):
		return {}


def native_identity(run):
	return optional_json(run/'metadata/process.json').get('identity')


def cleanup_network(run, receipt):
	if receipt is None:
		return
	complete = optional_json(run/'run/completion.json')
	outcome = optional_json(run/'outcome.json')
	safe = (not (run/'sdk-attempt.json').exists() or outcome.get('native_started') is False
			or complete.get('native_shutdown_complete') is True)
	if not safe or live(native_identity(run)) or owners():
		atomic(run/'network-cleanup-pending.json', dict(pending=True, reason='Native release not proved'))
		return
	startup_network.remove(receipt)
	atomic(run/'network-closed.json', dict(removed_owned_alias=receipt['added']))


def check_previous(root, current_boot):
	previous = previous_run(root)
	if previous is None:
		return
	check_run(previous, current_boot)


def check_global(current_boot):
	if not ACTIVE.exists():
		return
	active = read(ACTIVE)
	if not isinstance(active, dict) or not active.get('boot_id') or not active.get('run'):
		raise ValueError('Global ownership receipt is invalid; inspect before starting')
	if active['boot_id'] == current_boot:
		previous = Path(active['run'])
		if not previous.is_absolute() or not (previous/'request.json').exists():
			raise ValueError('Prior global run evidence is unavailable: '+str(previous))
		check_run(previous, current_boot)


def check_run(previous, current_boot):
	process = previous/'supervisor.json'
	if process.exists() and live(read(process)):
		raise ValueError('Release supervisor already running')
	if live(native_identity(previous)):
		raise ValueError('Previous native process is still running without its supervisor')
	# A finished native may still need its own network cleanup. Do not lose
	# ownership by overwriting latest.json or starting another release directory.
	same_boot = optional_json(previous/'request.json').get('boot_id', current_boot) == current_boot
	if same_boot and (previous/'network.json').exists() and not (previous/'network-closed.json').exists():
		raise ValueError('Previous network cleanup pending; run recover in '+str(previous.parent.parent))
	attempted = previous/'sdk-attempt.json'
	if not attempted.exists():
		return
	outcome = optional_json(previous/'outcome.json')
	safe = (outcome.get('native_exit') == 0 and outcome.get('native_shutdown_complete') is True
			and outcome.get('device_owners') == [])
	complete=optional_json(previous/'run/completion.json')
	safe = safe or (complete.get('failure_before_hardware') is True
					and complete.get('native_shutdown_complete') is True)
	recovered = optional_json(previous/'recovery.json')
	safe = safe or (recovered.get('boot_id')==current_boot and recovered.get('release_proven') is True)
	attempt = read(attempted)
	if not isinstance(attempt,dict) or not attempt.get('boot_id'):
		raise ValueError('Prior SDK attempt receipt is invalid; release unproved')
	if not safe and attempt.get('boot_id') == current_boot:
		raise ValueError('Previous SDK attempt lacks a safe completion; no same-boot retry')
	# A clean SDK shutdown does not reset the functional startup consumer.
	# New launchers reserve it explicitly; older runs expose its native log.
	request = optional_json(previous/'request.json')
	once = request.get('functional_startup_once') or (previous/'run/startup-consumer.jsonl').exists()
	never_entered = outcome.get('native_started') is False or (
		complete.get('failure_before_hardware') is True and complete.get('native_shutdown_complete') is True)
	if once and not never_entered and attempt['boot_id'] == current_boot:
		raise ValueError('Functional startup already used/reserved in this boot; safely stop, prepare-boot and reboot before another run')


def recover_previous(root):
	"""Manual metadata/network cleanup only. Never initializes/retries an SDK."""
	previous=previous_run(root)
	if previous is None:
		return dict(recovered=False, SDK_started=False)
	if live(optional_json(previous/'supervisor.json')) or live(native_identity(previous)) or owners():
		raise ValueError('Prior load is still alive or owns a device')
	attempted=optional_json(previous/'sdk-attempt.json')
	if ((previous/'sdk-attempt.json').exists() and attempted.get('boot_id')!=boot_id()
			or optional_json(previous/'request.json').get('boot_id',boot_id())!=boot_id()):
		raise ValueError('Recovery applies only to this boot and this run')
	outcome=optional_json(previous/'outcome.json')
	complete=optional_json(previous/'run/completion.json')
	never_started=(not (previous/'sdk-attempt.json').exists() or outcome.get('native_started') is False
				   or (complete.get('failure_before_hardware') is True and complete.get('native_shutdown_complete') is True))
	status = complete.get('status')
	proved=(complete.get('native_shutdown_complete') is True and isinstance(status,dict)
			and status.get('state') not in (None,'isolated','release_blocked')
			and status.get('release_blocked') is not True
			and outcome.get('native_exit') in (None,0))
	if not (never_started or proved):
		raise ValueError('Hardware release unproved or failed SDK; keep the run blocked')
	network=optional_json(previous/'network.json')
	if (previous/'network.json').exists() and not network:
		raise ValueError('Network ownership receipt is invalid; preserve the current address')
	if network:
		cleanup_network(previous,network)
		if not (previous/'network-closed.json').exists():
			raise ValueError('Network cleanup remains pending')
	result=dict(boot_id=boot_id(),release_proven=True,SDK_started=False,
				original_outcome_preserved=True,automatic_retry=False)
	atomic(previous/'recovery.json',result)
	return result


def preflight(root, identity):
	if os.geteuid() != 0:
		raise ValueError('Board root is required')
	verify_files(root, identity)
	current = authorize_boot(root, identity)
	packages = subprocess.check_output(['dpkg-query', '-W', '-f=${Package} ${Architecture} ${Version}\n',
										'icraft:arm64', 'customop:arm64'], universal_newlines=True).splitlines()
	if sorted(packages) != ['customop arm64 3.39.0', 'icraft arm64 3.39.0']:
		raise ValueError('Requires the existing ARM64 Icraft/customop 3.39.0 SDK')
	for name, expected in identity['libraries'].items():
		if sha(Path('/usr/lib/aarch64-linux-gnu')/name) != expected:
			raise ValueError('SDK library identity differs: '+name)
	if owners():
		raise ValueError('Device already owned')
	check_previous(root, current)
	check_global(current)
	return current


def command(root, run, session, seconds, selected=None):
	# Legacy callers select live CSI; the CLI always supplies a validated choice.
	selected = selected or dict(input_source='live_csi')
	display = optional_json(root/'identity.json')
	profile = display.get('hardware_profile', 'probe-free-drain-filter-v1')
	renderer = display.get('renderer_backend', 'ps')
	if renderer not in ('ps','pl') or (renderer=='pl' and profile not in ('probe-free-drain-overlay-v1','probe-free-drain-overlay-csi-v2','probe-free-drain-overlay-csi-v3')):
		raise ValueError('Renderer/profile mismatch')
	preprocess = display.get('preprocess_backend', 'ps')
	if preprocess not in ('ps','pl') or (preprocess=='pl' and profile not in ('probe-free-drain-overlay-csi-v2','probe-free-drain-overlay-csi-v3')):
		raise ValueError('CSI backend/profile mismatch')
	preprocess_args = ['--preprocess-backend', preprocess] if profile in ('probe-free-drain-overlay-csi-v2','probe-free-drain-overlay-csi-v3') else []
	return [str(root/'pose180_demo'), '--package', str(root), '--output', str(run/'run'),
			'--bind', '0.0.0.0', '--session', str(session), '--seconds', str(seconds),
			'--hardware-profile', profile, '--filter-backend', 'cpu', '--renderer-backend', renderer,
			'--min-cutoff', '0.5', '--beta', '0.3', '--d-cutoff', '1',
			'--hdmi', '1',
			'--result-port', '39383', '--status-port', '39384', '--view-port', '39385'] + preprocess_args + selection_arguments(selected) + input_arguments(root, selected)


def serve_run(root, run, stopping):
	# 独占锁覆盖预检、SDK 运行和网络回滚，避免其他部署包抢在清理完成前启动。
	with LOCK.open('a') as lock:
		deadline = time.monotonic()+5
		while True:
			try:
				fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
				break
			except BlockingIOError:
				if stopping.requested:
					return
				if time.monotonic() >= deadline:
					raise
				time.sleep(.02)  # Parent still publishing; never starts a second SDK.
		network = None
		try:
			active = read(ACTIVE)
			if active != dict(boot_id=boot_id(), run=str(run.resolve())):
				raise ValueError('Superseded or invalid global launch reservation')
			request = read(run/'request.json')
			if request['boot_id'] != boot_id() or owners():
				raise ValueError('Boot or device ownership changed before launch')
			if stopping.requested or (run/'stop.request').exists():
				return

			selected = request.get('input')
			if selected is not None:
				# Recheck the prepared input before any network mutation. Keep
				# provenance fixed across the detached launch handoff.
				actual = select_input(root, read(root/'identity.json'), selected['input_source'],
									  selected.get('dataset_repetitions'))
				if actual != selected:
					raise ValueError('Input identity changed after launch reservation')

			# 两种输入共用面向 PC 的网络别名；仅实时适配器监听 CSI，不改动路由器。
			network = startup_network.add(lambda receipt: atomic(run/'network.json',receipt), stopping)
			if stopping.requested or (run/'stop.request').exists():
				return
			with (run/'sdk-attempt.json').open('x') as stream:
				json.dump(dict(boot_id=boot_id(), automatic_retry=False), stream)
			session = time.time_ns() // 1000
			seconds = request['seconds']
			return supervise(
				run, command(root, run, session, seconds, selected),
				seconds + 120 if seconds else float('inf'),
				bind_native_parent=True, lease_fd=lock.fileno(), stop_request=stopping
			)
		except Exception as error:
			try:
				atomic(run/'error.json', dict(error=str(error), automatic_retry=False))
			except OSError:
				pass
			raise
		finally:
			try:
				# add() 可能在修改接口后抛错，因此也从落盘回执恢复待清理的网络资源。
				receipt = network if network is not None else optional_json(run/'network.json')
				if (run/'network.json').exists() and not receipt:
					raise ValueError('Network ownership receipt is invalid')
				cleanup_network(run, receipt or None)
			except Exception as error:
				try:
					atomic(run/'network-cleanup-pending.json', dict(pending=True, error=str(error)))
				except OSError:
					pass


def main(stopping):
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument('action', choices=('start', 'serve', 'status', 'stop', 'check', 'recover', 'prepare-boot'))
	parser.add_argument('--seconds', type=int, default=0, help='0: run until a manual stop; no automatic restart')
	parser.add_argument('--input-source', choices=('live_csi', 'official_dataset'),
						help='Default comes from package identity; applies to start/check')
	parser.add_argument('--dataset-repetitions', type=int, help='1..30 finite passes, official_dataset only')
	parser.add_argument('--run', help=argparse.SUPPRESS)
	args = parser.parse_args()
	if args.seconds < 0:
		parser.error('Runtime must be nonnegative')
	if args.seconds > (2**64-1)//1000000000:
		parser.error('Runtime exceeds the native monotonic duration range')
	if args.action not in ('start', 'check') and (args.input_source or args.dataset_repetitions is not None):
		parser.error('Input options apply only to start/check')
	root = Path(__file__).resolve().parent
	previous = previous_run(root)
	if args.action in ('status', 'stop'):
		if previous is None:
			print(json.dumps(dict(running=False, started=False)))
			return
		supervisor = optional_json(previous/'supervisor.json')
		running = live(supervisor)
		native = native_identity(previous)
		native_alive = live(native)
		if args.action == 'stop':
			try:
				(previous/'stop.request').touch(exist_ok=True)
			except OSError:
				pass  # Disk-full cannot disable the identity-checked signal path.
			supervisor_requested = request_stop(supervisor) if running else False
			orphan_requested = request_stop(native) if not running else False
			print(json.dumps(dict(stop_requested=supervisor_requested or orphan_requested, orphan_SIGTERM=orphan_requested,
								  forced_SDK_kill=False, run=str(previous))))
		else:
			state = optional_json(previous/'service-status.json')
			state.update(running=running or native_alive, supervisor_alive=running, native_alive=native_alive,
						 supervisor_lost=native_alive and not running, run=str(previous))
			if not running and not (previous/'outcome.json').exists():
				state['release_proven']=False
			state['network_cleanup_pending']=(previous/'network.json').exists() and not (previous/'network-closed.json').exists()
			if (previous/'error.json').exists():
				state['error'] = optional_json(previous/'error.json')
			print(json.dumps(state))
		return
	if args.action == 'recover':
		with LOCK.open('a') as lock:
			fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
			print(json.dumps(recover_previous(root)))
		return
	identity = read(root/'identity.json')
	if args.action == 'prepare-boot':
		verify_files(root, identity)
		if owners():
			raise ValueError('Stop all device owners before boot preparation')
		actual = verify_boot(identity)
		atomic(root/'next-boot.json', dict(previous_boot_id=boot_id(), BOOT_sha256=actual))
		print(json.dumps(dict(prepared=True, reboot_performed=False, next_step='Explicit operator reboot, then start')))
		return
	if args.action == 'check':
		selected = select_input(root, identity, args.input_source, args.dataset_repetitions)
		current = preflight(root, identity)
		arguments = selection_arguments(selected)
		policy = dict(zip(arguments[::2], arguments[1::2]))
		print(json.dumps(dict(ready=True, boot_id=current, SDK_started=False,
			top_k=int(policy['--top-k']),
			score_threshold=None if policy['--score-threshold'] == 'none' else float(policy['--score-threshold']),
			single_person_stability=policy['--single-person-stability'] == '1', input=selected)))
		return
	if args.action == 'start':
		with LOCK.open('a') as lock:
			fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
			selected = select_input(root, identity, args.input_source, args.dataset_repetitions)
			current = preflight(root, identity)
			if stopping.requested:
				return
			name = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+str(time.time_ns())
			run = root/'runs'/name
			(run/'metadata').mkdir(parents=True)
			atomic(run/'request.json', dict(boot_id=current, seconds=args.seconds, input=selected,
										   functional_startup_once=identity.get('hardware_profile') in ('probe-free-drain-filter-v1','probe-free-drain-overlay-v1','probe-free-drain-overlay-csi-v2','probe-free-drain-overlay-csi-v3')))
			atomic(root/'latest.json', dict(run=name))
			atomic(ACTIVE, dict(boot_id=current,run=str(run.resolve())))
			if stopping.requested:
				return
			child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), 'serve', '--run', name],
									 stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
									 stderr=subprocess.DEVNULL, start_new_session=True)
			supervisor = process_identity(child.pid)
			atomic(run/'supervisor.json', supervisor)
			if stopping.requested:
				request_stop(supervisor)
			print(json.dumps(dict(started=True, supervisor=supervisor, run=str(run), automatic_retry=False)))
		return
	if not args.run or Path(args.run).name != args.run:
		raise ValueError('Internal supervisor needs a valid run directory')
	run = root/'runs'/args.run
	# Parent publishes identity while holding the lock; acquiring it below also
	# orders its reservation against this child. Lost publication cannot launch.
	deadline=time.monotonic()+5
	while not (run/'supervisor.json').exists() and time.monotonic()<deadline and not stopping.requested:
		time.sleep(.02)
	if stopping.requested:
		return
	if read(run/'supervisor.json') != process_identity(os.getpid()):
		raise ValueError('Supervisor launch identity was not published')
	serve_run(root, run, stopping)


if __name__ == '__main__':
	with StopRequest() as stopping:
		main(stopping)
