"""Native catch-all and retained SDK-owner boundary, using the mock binary only."""
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
import time
from unittest.mock import patch
import service
import startup
from process_guard import request_stop
from test_exit_cleanup import mock_command, read, wait_for, reap, ports_released
from test_resident import frame

def blocked_lease(root):
	with (root / 'lease.lock').open('a') as contender:
		try:
			fcntl.flock(contender, fcntl.LOCK_EX | fcntl.LOCK_NB)
		except BlockingIOError:
			return
	raise AssertionError('Live unproved owner lost its lease')

def blocked_case(binary, root):
	run = root / 'runs/blocked'
	(run / 'metadata').mkdir(parents=True)
	service.atomic(root / 'latest.json', dict(run='blocked'))
	service.atomic(run / 'request.json', dict(boot_id=startup.boot_id(), seconds=0))
	service.atomic(run / 'sdk-attempt.json', dict(boot_id=startup.boot_id(), mock=True))
	command, ports = mock_command(binary, run)
	command += ['--mock-unproved-at', '1']
	service.atomic(run / 'setup.json', dict(command=command, ports=ports))
	supervisor = subprocess.Popen([sys.executable, str(Path(__file__).with_name('test_exit_cleanup.py')),
		str(binary), str(run), '--helper'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	native = logger = None
	try:
		native = wait_for(lambda: read(run / 'metadata/process.json').get('identity'))
		logger = wait_for(lambda: read(run / 'metadata/logger-process.json'))
		wait_for(lambda: service.read_status(ports[2]))
		with socket.create_connection(('127.0.0.1', ports[0]), 1) as channel:
			channel.sendall(frame(1))
			wait_for(lambda: (service.read_status(ports[2]) or {}).get('release_blocked'))
			channel.sendall(frame(2))
		supervisor.terminate()
		time.sleep(.7)
		assert supervisor.poll() is None and service.live(native)
		state = service.read_status(ports[2])
		assert state['state'] == 'release_blocked' and state['inferred'] == 0
		assert not (run / 'run/completion.json').exists()
		blocked_lease(run)
		with patch.object(startup, 'owners', return_value=[]):
			try:
				startup.recover_previous(root)
			except ValueError:
				pass
			else:
				raise AssertionError('Recovery accepted a retained native owner')
		supervisor.kill()
		supervisor.wait(timeout=3)  # Local test supervisor only.
		assert request_stop(native)
		time.sleep(.2)
		assert service.live(native) and service.read_status(ports[2])['release_blocked']
		blocked_lease(run)
		assert not (run / 'outcome.json').exists() and not (run / 'run/completion.json').exists()
		return dict(retained_after_TERM=True, retained_after_supervisor_death=True,
			lease_retained=True, status_responsive=True, no_false_completion=True, recovery_refused=True)
	finally:
		# Intentional quarantine has no software unlock. This is a no-SDK mock;
		# kill only this recorded test PID to release the disposable fixture.
		if service.live(native):
			os.kill(native['pid'], signal.SIGKILL)
			wait_for(lambda: not service.live(native))
		if supervisor.poll() is None:
			supervisor.wait(timeout=5)
		if logger:
			wait_for(lambda: not service.live(logger))
		if native:
			# A zombie group leader is not live(), but its other threads can
			# still be dropping shared socket FDs. Reap our adopted mock only
			# after the kernel has finished the whole thread group.
			def native_reaped():
				try:
					return os.waitpid(native['pid'], os.WNOHANG)[0] == native['pid']
				except ChildProcessError:
					return not Path('/proc/%d' % native['pid']).exists()
			wait_for(native_reaped)
		reap()
		ports_released(ports)

def nonstandard_case(binary, root):
	root.mkdir()
	command, ports = mock_command(binary, root)
	command += ['--mock-nonstandard-at', '1']
	process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	try:
		wait_for(lambda: service.read_status(ports[2]))
		with socket.create_connection(('127.0.0.1', ports[0]), 1) as channel:
			channel.sendall(frame(1))
			wait_for(lambda: (service.read_status(ports[2]) or {}).get('state') == 'isolated')
		assert process.poll() is None
		process.terminate()
		assert process.wait(timeout=5) == 3
		complete = read(root / 'run/completion.json')
		assert complete['native_shutdown_complete'] and not complete['status']['release_blocked']
		ports_released(ports)
		return dict(nonstandard_caught=True, control_plane_alive=True, graceful_exit=3, resources_released=True)
	finally:
		if process.poll() is None:
			process.terminate()
			process.wait(timeout=5)

def main():
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument('binary', type=Path)
	parser.add_argument('output', type=Path)
	args = parser.parse_args()
	args.output.mkdir()
	assert ctypes.CDLL(None).prctl(36, 1, 0, 0, 0) == 0
	result = dict(mock=True, SDK=False, board_access=False,
		nonstandard=nonstandard_case(args.binary, args.output / 'nonstandard'),
		unproved=blocked_case(args.binary, args.output / 'unproved'))
	(args.output / 'result.json').write_text(json.dumps(result, indent=2))
	print(json.dumps(result))

if __name__ == '__main__':
	main()
