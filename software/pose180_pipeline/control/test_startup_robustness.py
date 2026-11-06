"""Local Linux lifecycle races. Real mock processes/signals; all network mutations mocked."""
import argparse
import ctypes
import fcntl
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import threading
import time
from unittest.mock import patch

import bounded_log
import process_guard
import service
import startup
import startup_network
from test_exit_cleanup import mock_command, ports_released, read, wait_for, reap, fd_snapshot

def reject(call):
	try:
		call()
	except ValueError:
		return
	raise AssertionError('Unsafe state was accepted')

def lock_held(path):
	with path.open('a') as contender:
		try:
			fcntl.flock(contender, fcntl.LOCK_EX | fcntl.LOCK_NB)
		except BlockingIOError:
			return
	raise AssertionError('Cleanup lost the exclusive lease')

def startup_cases(root):
	root.mkdir()
	current = startup.boot_id()
	lock, active = root / 'lease.lock', root / 'active.json'
	for index, sig in enumerate((signal.SIGTERM, signal.SIGINT, signal.SIGHUP)):
		case = root / str(index)
		run = case / 'runs/one'
		(run / 'metadata').mkdir(parents=True)
		service.atomic(run / 'request.json', dict(boot_id=current, seconds=0))
		service.atomic(case / 'latest.json', dict(run='one'))
		service.atomic(active, dict(boot_id=current, run=str(run.resolve())))
		receipt = dict(added=True, interface='eth0', address='192.168.50.49/24', label='eth0:ptest')
		def add(persist, stopping):
			persist(receipt)
			os.kill(os.getpid(), sig)  # Stop during pre-SDK initialization.
			if index == 1:
				raise OSError('Injected error after address mutation')
			return receipt
		def remove(value):
			assert value == receipt
			lock_held(lock)
			os.kill(os.getpid(), sig)  # Repeated signal must not interrupt rollback.
		with patch.object(startup, 'LOCK', lock), patch.object(startup, 'ACTIVE', active), patch.object(startup,
			'owners', return_value=[]), patch.object(startup_network, 'add', side_effect=add), patch.object(startup_network,
			'remove', side_effect=remove) as rollback, patch.object(startup, 'supervise') as native, process_guard.StopRequest() as stopping:
			try:
				startup.serve_run(case, run, stopping)
			except OSError:
				assert index == 1
			assert stopping.requested and rollback.call_count == 1 and not native.called
			assert not (run / 'sdk-attempt.json').exists()
			assert read(run / 'network-closed.json')['removed_owned_alias']
			startup.check_global(current)
			# Another package must see the prior cleanup/SDK state, even though
			# it has no local latest.json of its own.
			(run / 'network-closed.json').unlink()
			reject(lambda: startup.check_global(current))
			with lock.open('a') as lease:
				fcntl.flock(lease, fcntl.LOCK_EX | fcntl.LOCK_NB)
				startup.recover_previous(case)
			service.atomic(run / 'sdk-attempt.json', dict(boot_id=current))
			(run / 'recovery.json').unlink()
			reject(lambda: startup.check_global(current))
			service.atomic(run / 'run-placeholder.json', {})
			(run / 'run').mkdir()
			service.atomic(run / 'run/completion.json', dict(failure_before_hardware=True, native_shutdown_complete=False))
			reject(lambda: startup.check_global(current))
			reject(lambda: startup.recover_previous(case))
			# Stale serve for an overwritten reservation may not touch the IP/SDK.
			service.atomic(active, dict(boot_id=current, run=str(root / 'different')))
			with patch.object(startup_network, 'add') as late_add:
				reject(lambda: startup.serve_run(case, run, process_guard.StopRequest()))
				assert not late_add.called
		with lock.open('a') as contender:
			fcntl.flock(contender, fcntl.LOCK_EX | fcntl.LOCK_NB)
	return dict(initialization_signals=3, repeated_cleanup_signals=3, cleanup_lease=True,
		cross_package_guard=True, stale_launch_blocked=True, false_proof_rejected=True)

def network_cases(root):
	root.mkdir()
	events = []
	receipt = None
	def persist(value):
		nonlocal receipt
		receipt = value
		events.append('persist')
	def change(*args, **kwargs):
		events.append('ip-add')
		assert receipt and receipt.get('label') and events.index('persist') < events.index('ip-add')
		raise OSError('Injected interruption after address add')
	raw_read = Path.read_text
	def read_path(path, *args, **kwargs):
		if str(path) == '/sys/class/net/eth0/address':
			return '02:00:00:00:00:01'
		return raw_read(path, *args, **kwargs)
	# No actual AF_PACKET socket or IP commands are used.
	with patch.object(Path, 'read_text', read_path), patch.object(startup_network.subprocess, 'check_output',
		return_value=b'[{"addr_info":[]}]'), patch.object(startup_network.subprocess, 'run', side_effect=change) as mutate, patch.object(startup_network.socket,
		'socket') as channel:
		channel.return_value.__enter__.return_value.recv.side_effect = socket.timeout
		try:
			startup_network.add(persist, process_guard.StopRequest())
		except OSError:
			pass
		assert events == ['persist', 'ip-add'] and mutate.call_count == 1
		mutate.reset_mock()
		def failed_persist(_):
			raise OSError(28, 'No space for ownership receipt')
		try:
			startup_network.add(failed_persist, process_guard.StopRequest())
		except OSError:
			pass
		assert not mutate.called
	for label, prefix, allowed in ((receipt['label'], 24, True), ('eth0:someone', 24, False), (receipt['label'],
		25, False)):
		current = json.dumps([dict(addr_info=[dict(local=startup_network.ADDRESS, prefixlen=prefix, label=label)])]).encode()
		with patch.object(startup_network.subprocess, 'check_output', return_value=current), patch.object(startup_network.subprocess,
			'run') as mutate:
			if allowed:
				startup_network.remove(receipt)
				assert mutate.call_count == 1
			else:
				reject(lambda: startup_network.remove(receipt))
				assert not mutate.called
	return dict(write_before_mutation=True, failed_receipt_no_mutation=True, foreign_alias_preserved=True)

def monitor_cases(binary, root):
	root.mkdir()
	before = fd_snapshot()
	# Pending stop must prevent even exec, including a signal between logger
	# creation and native launch.
	for phase in ('before', 'logger'):
		case = root / phase
		(case / 'metadata').mkdir(parents=True)
		command, ports = mock_command(binary, case)
		atomic = service.atomic
		def publish(path, value):
			atomic(path, value)
			if path.name == 'logger-process.json':
				os.kill(os.getpid(), signal.SIGTERM)
		with process_guard.StopRequest() as stopping, patch.object(service, 'atomic', side_effect=publish):
			if phase == 'before':
				stopping.requested = True
			outcome = service.supervise(case, command, 1, ports[2], stop_request=stopping)
			assert outcome['native_started'] is False and not (case / 'run').exists()
		ports_released(ports)
	case = root / 'monitor-error'
	(case / 'metadata').mkdir(parents=True)
	command, ports = mock_command(binary, case)
	original_status = service.read_status
	def fail_after_ready(port):
		wait_for(lambda: original_status(port))
		raise RuntimeError('Injected monitor failure')
	with patch.object(service, 'read_status', side_effect=fail_after_ready):
		try:
			service.supervise(case, command, 2, ports[2], bind_native_parent=True)
		except RuntimeError:
			pass
		else:
			raise AssertionError('Monitor failure not exercised')
	outcome = read(case / 'outcome.json')
	assert outcome['native_exit'] == 0 and outcome['native_shutdown_complete'] and outcome['monitor_error']
	assert not service.live(read(case / 'metadata/logger-process.json'))
	ports_released(ports)
	case = root / 'memory-sample-unavailable'
	(case / 'metadata').mkdir(parents=True)
	command, ports = mock_command(binary, case)
	original_read = Path.read_text
	def read_path(path, *args, **kwargs):
		if str(path) == '/proc/meminfo':
			raise OSError('Injected proc read failure')
		return original_read(path, *args, **kwargs)
	with patch.object(Path, 'read_text', read_path):
		outcome = service.supervise(case, command, .4, ports[2], bind_native_parent=True)
	assert outcome['native_exit'] == 0 and outcome['native_shutdown_complete']
	assert outcome['minimum_MemAvailable_KiB'] is None and outcome['samples'] > 0
	ports_released(ports)
	# Direct native HUP also follows the real graceful path.
	case = root / 'native-hup'
	case.mkdir()
	command, ports = mock_command(binary, case)
	process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	try:
		wait_for(lambda: service.read_status(ports[2]))
		process.send_signal(signal.SIGHUP)
		assert process.wait(timeout=5) == 0
		assert read(case / 'run/completion.json')['native_shutdown_complete']
	finally:
		if process.poll() is None:
			process.terminate()
			process.wait(timeout=5)
	ports_released(ports)
	class BrokenClose:
		def close(self):
			raise OSError('Injected close failure')
	log = bounded_log.RingLog(root, 'close-test')
	log.file = BrokenClose()
	log.close()
	log.close()
	assert log.file is None
	# A status peer trickling bytes must not postpone stop checks indefinitely.
	done = threading.Event()
	with socket.socket() as listener:
		listener.bind(('127.0.0.1', 0))
		listener.listen()
		listener.settimeout(1)
		def trickle():
			with listener.accept()[0] as client:
				while not done.wait(.06):
					try:
						client.sendall(b' ')
					except OSError:
						return
		worker = threading.Thread(target=trickle)
		worker.start()
		started = time.monotonic()
		try:
			assert service.read_status(listener.getsockname()[1]) is None
			assert time.monotonic() - started < .5
		finally:
			done.set()
			worker.join(timeout=2)
		assert not worker.is_alive()
		# join() observes Python's sentinel, before libc finishes pthread_exit.
		# Its first unwind can briefly open libgcc_s.so.1. Wait for this exact
		# native thread to leave /proc before checking process-wide resources.
		wait_for(lambda: not Path('/proc/self/task/%d' % worker.native_id).exists(), timeout=2)
	for malformed in (None, {}, [], True, {'pid': 0}, {'pid': -1}, {'pid': 'bad'}):
		assert not process_guard.live(malformed) and not process_guard.request_stop(malformed)
	after = fd_snapshot()
	assert after == before, dict(FDs_before=before, FDs_after=after)
	return dict(prelaunch_stop_phases=2, monitor_exception_reaped=True, missing_memory_sample_tolerated=True,
		native_hup_graceful=True, log_close_error_tolerated=True, status_read_bounded=True,
		native_thread_exit_proved=True, FDs_before=len(before), FDs_after=len(after))

def fixture_main(entry):
	"""Actual start/serve/stop CLI with only device/network adapters replaced."""
	entry = Path(entry).resolve()
	root = entry.parent
	setup = read(root / 'fixture.json')
	startup.__file__ = str(entry)
	def preflight(folder, identity):
		current = startup.boot_id()
		startup.check_previous(folder, current)
		startup.check_global(current)
		return current
	def command(folder, run, session, seconds, selected=None):
		argv, unused = mock_command(Path(setup['binary']), run)
		for option, number in zip(('--input-port', '--result-port', '--status-port', '--view-port'), setup['ports']):
			argv[argv.index(option) + 1] = str(number)
		return argv
	def supervise(run, argv, budget, **kwargs):
		return service.supervise(run, argv, budget, setup['ports'][2], **kwargs)
	def add(persist, stopping):
		receipt = dict(added=False, address=startup_network.ADDRESS + '/24', interface='eth0')
		persist(receipt)
		return receipt
	original_touch = Path.touch
	def touch(path, *args, **kwargs):
		if path.name == 'stop.request' and (root / 'deny-stop-file').exists():
			raise OSError(28, 'Injected stop file disk full')
		return original_touch(path, *args, **kwargs)
	with patch.object(startup, 'LOCK', Path(setup['lock'])), patch.object(startup, 'ACTIVE', Path(setup['active'])), patch.object(startup,
		'preflight', side_effect=preflight), patch.object(startup, 'command', side_effect=command), patch.object(startup,
		'supervise', side_effect=supervise), patch.object(startup_network, 'add', side_effect=add), patch.object(startup_network,
		'remove'), patch.object(Path, 'touch', touch), process_guard.StopRequest() as stopping:
		startup.main(stopping)

def cli_cases(binary, root):
	root.mkdir()
	assert ctypes.CDLL(None).prctl(36, 1, 0, 0, 0) == 0
	fixture = 'import sys\nsys.path.insert(0, ' + repr(str(Path(__file__).parent)) + ')\nfrom test_startup_robustness import fixture_main\nfixture_main(__file__)\n'
	entries = []
	ports = None
	for name in ('first', 'second'):
		folder = root / name
		folder.mkdir()
		unused, ports = mock_command(binary, folder)
		service.atomic(folder / 'identity.json', dict(input_source='live_csi'))
		(folder / 'csi.conf').write_text('# mock only: no router or network changes\n')
		service.atomic(folder / 'fixture.json', dict(binary=str(binary), ports=ports, lock=str(root / 'lease.lock'),
			active=str(root / 'active.json')))
		entry = folder / 'startup-fixture.py'
		entry.write_text(fixture)
		entries.append(entry)
	def invoke(entry, action):
		return subprocess.run([sys.executable, str(entry), action], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
			text=True, timeout=10)
	for cycle in range(3):
		started = invoke(entries[0], 'start')
		assert started.returncode == 0, started.stderr
		launch = json.loads(started.stdout)
		run = Path(launch['run'])
		identity = launch['supervisor']
		try:
			native = wait_for(lambda: read(run / 'metadata/process.json').get('identity'))
			wait_for(lambda: (service.read_status(read(entries[0].parent / 'fixture.json')['ports'][2]) or {}).get('state') == 'waiting_input')
			rejected = invoke(entries[1], 'start')
			assert rejected.returncode != 0, 'Second package overtook a live load'
			(entries[0].parent / 'deny-stop-file').touch()
			stopped = invoke(entries[0], 'stop')
			assert stopped.returncode == 0 and json.loads(stopped.stdout)['stop_requested'], stopped.stderr
			wait_for(lambda: not service.live(identity))
			assert not service.live(native)
			outcome = read(run / 'outcome.json')
			assert outcome['native_exit'] == 0 and outcome['native_shutdown_complete'], outcome
			assert (run / 'network-closed.json').exists()
		finally:
			if service.live(identity):
				process_guard.request_stop(identity)
				wait_for(lambda: not service.live(identity))
			reap()
	return dict(cli_cycles=3, concurrent_package_rejected=3, stop_with_full_disk=3, all_native_shutdown_proved=True)

def main():
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument('binary', type=Path)
	parser.add_argument('output', type=Path)
	args = parser.parse_args()
	args.output.mkdir()
	result = dict(mock=True, SDK=False, board_access=False, network_mutated=False,
		startup=startup_cases(args.output / 'startup'), network=network_cases(args.output / 'network'),
		monitor=monitor_cases(args.binary, args.output / 'monitor'), cli=cli_cases(args.binary, args.output / 'cli'))
	(args.output / 'result.json').write_text(json.dumps(result, indent=2))
	print(json.dumps(result))

if __name__ == '__main__':
	main()
