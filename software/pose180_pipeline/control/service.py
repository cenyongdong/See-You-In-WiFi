"""One detached board supervisor; stop requests never kill/retry an SDK call."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time
from bounded_log import RingLog
from run_hdmi_trial import preflight, owners
from process_guard import process_identity, live, StopRequest

def atomic(path, value):
	temporary = path.with_suffix(path.suffix + '.tmp')
	temporary.write_text(json.dumps(value, ensure_ascii=False))
	os.replace(temporary, path)

def read_status(port):
	try:
		deadline = time.monotonic() + .2
		with socket.create_connection(('127.0.0.1', port), .2) as connection:
			data = b''
			while b'\n' not in data and len(data) < 8192:
				remaining = deadline - time.monotonic()
				if remaining <= 0:
					return None
				connection.settimeout(remaining)
				chunk = connection.recv(8192 - len(data))
				if not chunk:
					break
				data += chunk
		value = json.loads(data)
		return value if isinstance(value, dict) else None
	except (OSError, ValueError):
		return None

def supervise(root, command, budget, status_port=39384, bind_native_parent=False, lease_fd=None,
	stop_request=None):
	"""Also exercised with an explicit mock binary; no hidden process retries."""
	if stop_request is None:
		with StopRequest() as request:
			return _supervise(root, command, budget, status_port, bind_native_parent, lease_fd, request)
	return _supervise(root, command, budget, status_port, bind_native_parent, lease_fd, stop_request)

def _supervise(root, command, budget, status_port, bind_native_parent, lease_fd, stopping):
	metadata = root / 'metadata'
	samples = RingLog(metadata, 'resources', 262144, 2)
	read_fd = write_fd = -1
	pump = None
	started = time.monotonic()
	child = None
	reason = None
	sent = False
	final = {}
	count = 0
	peak_rss = peak_fds = peak_threads = 0
	minimum_available = None

	# 诊断写入失败只丢弃本条记录，不能打断 SDK 生命周期。
	def diagnostic(path, value):
		try:
			atomic(path, value)
		except OSError:
			pass

	def stop_child():
		if child is not None and child.poll() is None:
			child.send_signal(signal.SIGTERM)
			# No timeout escalation: SDK work must return before freeing buffers.
			while child.poll() is None:
				time.sleep(.1)

	def finish(monitor_error=None):
		complete = {}
		try:
			complete = json.loads((root / 'run/completion.json').read_text())
			if not isinstance(complete, dict):
				complete = {}
		except (OSError, ValueError):
			pass
		outcome = dict(
			native_exit=child.wait(), seconds=time.monotonic() - started,
			stop_reason=reason, stop_sent=sent, final_status=complete.get('status', final),
			native_shutdown_complete=complete.get('native_shutdown_complete') is True,
			device_owners=owners(), SDK_attempts=1, automatic_retry=False,
			samples=count, peak_RSS_KiB=peak_rss, peak_fds=peak_fds,
			peak_threads=peak_threads, minimum_MemAvailable_KiB=minimum_available
			)
		if monitor_error is not None:
			outcome['monitor_error'] = str(monitor_error)
		diagnostic(root / 'outcome.json', outcome)
		diagnostic(root / 'service-status.json', dict(running=False, **outcome))
		return outcome

	try:
		if stopping.requested or (root / 'stop.request').exists():
			result = dict(native_started=False, native_shutdown_complete=False,
				stop_reason='Stopped before native launch', automatic_retry=False)
			diagnostic(root / 'outcome.json', result)
			return result

		# 先建立日志管道和日志子进程，原生进程只继承写端及独占租约。
		read_fd, write_fd = os.pipe()
		os.set_blocking(write_fd, False)
		pump = subprocess.Popen(
			[sys.executable, str(Path(__file__).with_name('bounded_log.py')),
			str(read_fd), str(metadata), '--parent-pid', str(os.getpid())],
			pass_fds=(read_fd,), stdin=subprocess.DEVNULL,
			stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
			)
		os.close(read_fd)
		read_fd = -1
		diagnostic(metadata / 'logger-process.json', process_identity(pump.pid))
		if stopping.requested or (root / 'stop.request').exists():
			result = dict(native_started=False, native_shutdown_complete=False,
				stop_reason='Stopped before native launch', automatic_retry=False)
			diagnostic(root / 'outcome.json', result)
			return result

		argv = command + (['--supervisor-pid', str(os.getpid())] if bind_native_parent else [])
		child = subprocess.Popen(
			argv, stdin=subprocess.DEVNULL, stdout=write_fd, stderr=write_fd,
			pass_fds=() if lease_fd is None else(lease_fd,)
			)
		os.close(write_fd)
		write_fd = -1
		native_identity = process_identity(child.pid)
		diagnostic(metadata / 'process.json', dict(identity=native_identity, argv=argv))
		# 监督循环只提出停止请求，不强杀仍可能持有在途设备资源的原生进程。
		while child.poll() is None:
			now = time.monotonic()
			state = read_status(status_port)
			if state:
				final = state
			try:
				mem = Path('/proc/meminfo').read_text()
				available = next(int(line.split()[1]) for line in mem.splitlines() if line.startswith('MemAvailable:'))
			except (OSError, ValueError, StopIteration):
				available = None  # An unavailable sample is not zero free memory.
			if available is not None:
				minimum_available = available if minimum_available is None else min(minimum_available,
					available)
			try:
				status = Path('/proc/%d/status' % child.pid).read_text()
				fields = dict(line.split(':', 1) for line in status.splitlines() if ':' in line)
				rss = int(fields.get('VmRSS', '0').split()[0])
				threads = int(fields.get('Threads', '0').split()[0])
				fds = len(list(Path('/proc/%d/fd' % child.pid).iterdir()))
			except (OSError, ValueError):
				rss = threads = fds = 0
			peak_rss, peak_fds, peak_threads = max(peak_rss, rss), max(peak_fds, fds), max(peak_threads,
				threads)
			if available is not None and available < 131072:
				reason = reason or 'MemAvailable below 128 MiB'
			if state and state.get('state') in ('isolated', 'release_blocked'):
				reason = reason or 'Native isolated; no SDK restart'
			if stopping.requested or (root / 'stop.request').exists():
				reason = reason or 'Explicit local stop request'
			if now - started > budget:
				reason = reason or 'Finite stop-request budget reached; observing original SDK'
			if reason and not sent:
				child.send_signal(signal.SIGTERM)
				sent = True
			row = dict(elapsed=now - started, status=final, RSS_KiB=rss, fds=fds, threads=threads,
				MemAvailable_KiB=available, stop_reason=reason, stop_sent=sent)
			samples.write((json.dumps(row) + '\n').encode())
			try:
				atomic(root / 'service-status.json', dict(supervisor=process_identity(os.getpid()),
					native=native_identity, running=True, **row))
			except OSError:
				pass  # A diagnostic write failure must not terminate the SDK.
			count += 1
			time.sleep(.5)
		return finish()
	except BaseException as error:
		if child is None:
			diagnostic(root / 'outcome.json', dict(native_started=False, native_shutdown_complete=False,
				error=str(error), automatic_retry=False))
		else:
			stop_child()
			finish(error)  # Preserve real cleanup evidence even if monitoring failed.
		raise
	finally:
		if write_fd >= 0:
			os.close(write_fd)
		if read_fd >= 0:
			os.close(read_fd)

		# 先等原生进程安全退出，再收尾日志；监控异常也遵循这一顺序。
		stop_child()
		samples.close()
		try:
			if pump is not None:
				pump.wait(timeout=2)
		except subprocess.TimeoutExpired:
			pump.terminate()
			try:
				pump.wait(timeout=1)
			except subprocess.TimeoutExpired:
				pump.kill()  # Logger created before SDK; owns no device handles.
				try:
					pump.wait(timeout=1)
				except subprocess.TimeoutExpired:
					diagnostic(metadata / 'logger-cleanup-pending.json', dict(identity=process_identity(pump.pid),
						SDK_handles=False))

def authorize(root):
	auth = json.loads((root.parent / 'authorization.json').read_text())
	manifest = json.loads((root.parent / 'manifest.json').read_text())
	if (not auth.get('active') or not auth.get('user_confirmation') or
		auth['package_id'] != manifest['package_id'] or auth['caps'] != manifest['caps'] or
		(root.parent / 'boot-control/metadata/closed.json').exists()):
		raise ValueError('This new package lacks active authorization or is closed')
	return auth['caps']

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('action', choices=('start', 'serve', 'status', 'stop'))
	args = parser.parse_args()
	root = Path(__file__).resolve().parent
	if args.action == 'status':
		status = json.loads((root / 'service-status.json').read_text()) if (root / 'service-status.json').exists() else {}
		if (root / 'service-error.json').exists():
			status['supervisor_error'] = json.loads((root / 'service-error.json').read_text())
		if not status and (root / 'service-process.json').exists():
			status = json.loads((root / 'service-process.json').read_text())
			status['supervisor_alive'] = live(status.get('supervisor'))
		if status.get('running'):
			status['supervisor_alive'] = live(status.get('supervisor'))
			status['native_alive'] = live(status.get('native'))
		print(json.dumps(status))
		return
	if args.action == 'stop':
		(root / 'stop.request').touch(exist_ok=True)
		print(json.dumps(dict(stop_requested=True, forced_SDK_kill=False)))
		return
	caps = authorize(root)
	if args.action == 'start':
		# An exclusive marker prevents two starts even while preflight is running.
		with (root / 'service-start.attempt.json').open('x') as file:
			json.dump(dict(caps=caps, automatic_retry=False), file)
		child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), 'serve'],
			stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
			stderr=subprocess.DEVNULL, start_new_session=True)
		result = dict(supervisor=process_identity(child.pid), detached=True)
		atomic(root / 'service-process.json', result)
		print(json.dumps(result))
		return
	with Path('/run/pose180-resident.lock').open('a') as lock:
		fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
		try:
			identity, boot, metadata = preflight(root)
			with (root / 'sdk-attempt.json').open('x') as file:
				json.dump(dict(boot_id=boot, SDK_attempts=1, caps=caps), file)
			(metadata / 'before.dmesg').write_bytes(subprocess.check_output(['dmesg']))
			command = [str(root / 'pose180_demo'), '--package', str(root), '--output', str(root / 'run'),
				'--bind', '0.0.0.0', '--session', str(identity['session']),
				'--seconds', str(caps['runtime_seconds']), '--hdmi', '1', '--csi', str(root / 'csi.conf')]
			supervise(root, command, caps['stop_request_seconds'], bind_native_parent=True, lease_fd=lock.fileno())
			(metadata / 'after.dmesg').write_bytes(subprocess.check_output(['dmesg']))
		except Exception as error:
			atomic(root / 'service-error.json', dict(error=str(error), automatic_retry=False))
			raise

if __name__ == '__main__':
	main()
