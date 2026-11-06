"""Linux-only fault injection against mock processes; no SDK, BOOT, routers or IP changes."""
import argparse
import ctypes
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time
from unittest.mock import patch

import service
import startup
from test_resident import frame, port

def wait_for(test, timeout=8):
	end = time.monotonic() + timeout
	while time.monotonic() < end:
		result = test()
		if result:
			return result
		time.sleep(.02)
	raise AssertionError('Fault-injection deadline expired')

def read(path):
	try:
		return json.loads(path.read_text())
	except (OSError, ValueError):
		return {}

def reap():
	while True:
		try:
			pid, _ = os.waitpid(-1, os.WNOHANG)
		except ChildProcessError:
			return
		if not pid:
			return

def mock_command(binary, root, slow=False):
	ports = [port() for _ in range(4)]
	return [str(binary), '--output', str(root / 'run'), '--session', '123456', '--seconds', '0',
		'--input-port', str(ports[0]), '--result-port', str(ports[1]), '--status-port', str(ports[2]),
		'--view-port', str(ports[3]), '--top-k', '1', '--score-threshold', 'none',
		'--single-person-stability', '1', '--mock-slow-at', '1' if slow else '0'], ports

def ports_released(ports):
	for number in ports:
		with socket.socket() as channel:
			channel.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			channel.bind(('127.0.0.1', number))

def fd_snapshot():
	"""Capture live descriptor identities after the directory reader has closed."""
	result = {}
	for name in os.listdir('/proc/self/fd'):
		try:
			result[int(name)] = os.readlink('/proc/self/fd/' + name)
		except FileNotFoundError:
			# listdir briefly opens this directory itself. Its descriptor is
			# already closed here; do not count that observer as a resource.
			pass
	return result

def helper(binary, root, legacy):
	module = service
	if legacy:
		spec = importlib.util.spec_from_file_location('legacy_service', legacy / 'service.py')
		module = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(module)
	setup = read(root / 'setup.json')
	with (root / 'lease.lock').open('a') as lease:
		fcntl.flock(lease, fcntl.LOCK_EX | fcntl.LOCK_NB)
		command = setup['command']
		if legacy:
			outcome = module.supervise(root, command, 30, setup['ports'][2])
		else:
			outcome = module.supervise(root, command, 30, setup['ports'][2], bind_native_parent=True,
				lease_fd=lease.fileno())
		(root / 'helper-result.json').write_text(json.dumps(outcome))

def killed_supervisor(binary, root, legacy=None):
	root.mkdir()
	(root / 'metadata').mkdir()
	command, ports = mock_command(binary, root, slow=not bool(legacy))
	(root / 'setup.json').write_text(json.dumps(dict(command=command, ports=ports)))
	argv = [sys.executable, str(Path(__file__).resolve()), str(binary), str(root), '--helper']
	if legacy:
		argv += ['--legacy', str(legacy)]
	supervisor = subprocess.Popen(argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	native = logger = None
	try:
		native = wait_for(lambda: read(root / 'metadata/process.json').get('identity'))
		logger = wait_for(lambda: read(root / 'metadata/logger-process.json'))
		wait_for(lambda: connection_ready(ports[0]))
		time.sleep(.06)
		if not legacy:
			with socket.create_connection(('127.0.0.1', ports[0]), 1) as channel:
				channel.sendall(frame(1))
				wait_for(lambda: ((service.read_status(ports[2]) or {}).get('forward_age_ms') or 0) > 50)
		os.kill(supervisor.pid, signal.SIGKILL)
		supervisor.wait(timeout=3)
		if legacy:
			time.sleep(.4)
			assert service.live(native), 'Baseline orphan condition was not reproduced'
			service_request = signal.SIGTERM
			os.kill(native['pid'], service_request)  # Explicitly this test's mock only.
		else:
			assert service.live(native), 'Slow in-flight mock was unexpectedly killed'
			with (root / 'lease.lock').open('a') as contender:
				try:
					fcntl.flock(contender, fcntl.LOCK_EX | fcntl.LOCK_NB)
				except BlockingIOError:
					pass
				else:
					raise AssertionError('Resource lease disappeared while native work was in flight')
		wait_for(lambda: not service.live(native))
		wait_for(lambda: not service.live(logger))
		assert read(root / 'run/completion.json').get('native_shutdown_complete') is True
		with (root / 'lease.lock').open('a') as contender:
			fcntl.flock(contender, fcntl.LOCK_EX | fcntl.LOCK_NB)
		ports_released(ports)
		return dict(baseline_orphan_reproduced=bool(legacy), graceful_parent_death=not bool(legacy), lease_released=True)
	finally:
		if supervisor.poll() is None:
			supervisor.terminate()
			supervisor.wait(timeout=5)
		if service.live(native):
			os.kill(native['pid'], signal.SIGTERM)
			wait_for(lambda: not service.live(native))
		if service.live(logger):
			os.kill(logger['pid'], signal.SIGKILL)
		reap()

def connection_ready(port):
	try:
		with socket.create_connection(('127.0.0.1', port), .1):
			return True
	except OSError:
		return False

def killed_native(binary, root):
	root.mkdir()
	(root / 'metadata').mkdir()
	command, ports = mock_command(binary, root)
	(root / 'setup.json').write_text(json.dumps(dict(command=command, ports=ports)))
	supervisor = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), str(binary), str(root),
		'--helper'],
		stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	native = recorder = None
	try:
		native = wait_for(lambda: read(root / 'metadata/process.json').get('identity'))
		wait_for(lambda: connection_ready(ports[0]))
		def recorder_id():
			try:
				children = Path('/proc/%d/task/%d/children' % (native['pid'], native['pid'])).read_text().split()
				return service.process_identity(int(children[0])) if children else None
			except OSError:
				return None
		recorder = wait_for(recorder_id)
		os.kill(recorder['pid'], signal.SIGSTOP)  # A stuck diagnostic logger owns no devices.
		os.kill(native['pid'], signal.SIGKILL)  # Mock binary only; never do this to a board SDK.
		supervisor.wait(timeout=8)
		outcome = read(root / 'outcome.json')
		assert outcome['native_exit'] == - 9 and outcome['native_shutdown_complete'] is False, outcome
		wait_for(lambda: not service.live(recorder))
		ports_released(ports)
		return dict(mock_exit=-9, release_proven=False, stopped_recorder_reaped=True, ports_released=True)
	finally:
		if service.live(recorder):
			os.kill(recorder['pid'], signal.SIGKILL)
		if supervisor.poll() is None:
			supervisor.terminate()
			supervisor.wait(timeout=5)
		reap()

def local_failures(binary, root):
	root.mkdir()
	original = service.atomic
	before = fd_snapshot()
	# Complete metadata failure must neither stop inference nor leak pipe FDs.
	def failed_write(*args, **kwargs):
		raise OSError(28, 'Injected disk full')
	# Both failures happen after pipe allocation, before a native process owns
	# any resources. The supervisor must close both ends on either path.
	for name, target in (('pipe-setup-failed', 'set_blocking'), ('logger-exec-failed', 'Popen')):
		case = root / name
		(case / 'metadata').mkdir(parents=True)
		owner = service.os if target == 'set_blocking' else service.subprocess
		with patch.object(owner, target, side_effect=OSError('Injected ' + name)):
			try:
				service.supervise(case, ['/unused-before-native'], 1, 9)
			except OSError:
				pass
			else:
				raise AssertionError('Pre-native setup failure was not exercised')
		assert read(case / 'outcome.json')['native_started'] is False
		assert fd_snapshot() == before, dict(case=name, FDs_before=before, FDs_after=fd_snapshot())
	for index in range(4):
		case = root / str(index)
		case.mkdir()
		(case / 'metadata').mkdir()
		command, ports = mock_command(binary, case)
		with patch.object(service, 'atomic', side_effect=failed_write):
			outcome = service.supervise(case, command, .3, ports[2], bind_native_parent=True)
		assert outcome['native_exit'] == 0 and outcome['native_shutdown_complete'], outcome
		ports_released(ports)
	case = root / 'exec-failed'
	case.mkdir()
	(case / 'metadata').mkdir()
	try:
		service.supervise(case, ['/missing-owned-test-program'], 1, 9)
	except FileNotFoundError:
		pass
	else:
		raise AssertionError('Missing executable succeeded')
	assert read(case / 'outcome.json')['native_started'] is False
	# A bind failure must unwind the partial IO constructor and recorder before
	# reporting that no hardware was touched; it need not strand a network alias.
	case = root / 'port-busy'
	case.mkdir()
	command, ports = mock_command(binary, case)
	with socket.socket() as blocker:
		blocker.bind(('127.0.0.1', ports[2]))
		blocker.listen()
		failed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
		assert failed.returncode == 1
		completion = read(case / 'run/completion.json')
		assert completion.get('failure_before_hardware') is True and completion.get('native_shutdown_complete') is True
	ports_released(ports)
	reap()
	after = fd_snapshot()
	assert after == before, dict(FDs_before=before, FDs_after=after)
	# Network removal is mocked: these tests never alter an actual IP address.
	for index, state in enumerate(('before-SDK', 'proved-close', 'unproved-crash')):
		case = root / ('network-' + state)
		case.mkdir()
		(case / 'run').mkdir()
		if state != 'before-SDK':
			(case / 'sdk-attempt.json').touch()
		if state == 'proved-close':
			original(case / 'run/completion.json', dict(native_shutdown_complete=True))
		with patch.object(startup.startup_network, 'remove') as remove, patch.object(startup, 'owners',
			return_value=[]):
			startup.cleanup_network(case, dict(added=True))
			assert remove.called == (state != 'unproved-crash')
	# A lost supervisor can be recovered manually only after actual completion;
	# preserve the original absence/failure of the supervisor's outcome.
	recovery = root / 'recovery'
	case = recovery / 'runs/one'
	(case / 'run').mkdir(parents=True)
	original(recovery / 'latest.json', dict(run='one'))
	current = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
	original(case / 'sdk-attempt.json', dict(boot_id=current))
	original(case / 'network.json', dict(added=True))
	original(case / 'run/completion.json', dict(native_shutdown_complete=True, status=dict(state='running')))
	with patch.object(startup.startup_network, 'remove') as remove, patch.object(startup, 'owners', return_value=[]):
		try:
			startup.check_previous(recovery, current)
		except ValueError:
			pass
		else:
			raise AssertionError('Unobserved supervisor outcome was bypassed automatically')
		assert startup.recover_previous(recovery)['release_proven'] and remove.called
		startup.check_previous(recovery, current)
		(case / 'recovery.json').unlink()
		original(case / 'run/completion.json', dict(native_shutdown_complete=False))
		try:
			startup.recover_previous(recovery)
		except ValueError:
			pass
		else:
			raise AssertionError('Missing hardware proof allowed recovery')
	# No network command is issued for a pre-existing address or an alias that
	# an operator has already removed.
	with patch.object(startup.startup_network.subprocess, 'check_output', return_value=b'[{"addr_info":[]}]'), patch.object(startup.startup_network.subprocess,
		'run') as mutate:
		startup.startup_network.remove(dict(added=True, address='192.168.50.49/24', interface='eth0'))
		startup.startup_network.remove(dict(added=False))
		assert not mutate.called
	return dict(pre_native_setup_failures=2, disk_full_cycles=4, exec_failure_cleaned=True, port_collision_cleaned=True,
		FDs_before=len(before), FDs_after=len(after),
		network_cases=3, manual_recovery_proof_checked=True, idempotent_network_cleanup=True)

def main():
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument('binary', type=Path)
	parser.add_argument('output', type=Path)
	parser.add_argument('--helper', action='store_true')
	parser.add_argument('--legacy', type=Path)
	args = parser.parse_args()
	if args.helper:
		return helper(args.binary, args.output, args.legacy)
	# Adopt only descendants created by these local mock cases, to reap them.
	assert ctypes.CDLL(None).prctl(36, 1, 0, 0, 0) == 0  # PR_SET_CHILD_SUBREAPER
	args.output.mkdir()
	result = dict(mock=True, SDK=False, board_access=False,
		local=local_failures(args.binary, args.output / 'local'),
		supervisor_killed=killed_supervisor(args.binary, args.output / 'parent-killed'),
		native_killed=killed_native(args.binary, args.output / 'native-killed'))
	if args.legacy:
		result['baseline'] = killed_supervisor(args.binary, args.output / 'baseline', args.legacy)
	(args.output / 'result.json').write_text(json.dumps(result, indent=2))
	print(json.dumps(result))

if __name__ == '__main__':
	main()
