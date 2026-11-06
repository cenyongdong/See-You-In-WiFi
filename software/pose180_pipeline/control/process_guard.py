"""Linux process identity and parent-death binding; no device or SDK access."""
import ctypes
import os
from pathlib import Path
import signal

def process_identity(pid):
	try:
		fields = Path('/proc/%d/stat' % pid).read_text().rsplit(')', 1)[1].split()
		if fields[0] in ('Z', 'X'):
			return None
		return dict(pid=pid, start_ticks=fields[19],
			boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip())
	except (OSError, IndexError):
		return None

def live(identity):
	return (isinstance(identity, dict) and type(identity.get('pid')) is int
		and identity['pid'] > 1 and process_identity(identity['pid']) == identity)

class StopRequest:
	"""Defer termination through initialization, in-flight work and cleanup."""
	def __init__(self):
		self.requested = False
		self.previous = {}

	def __enter__(self):
		for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
			self.previous[sig] = signal.signal(sig, self._request)
		return self

	def _request(self, *_):
		self.requested = True

	def __exit__(self, *_):
		for sig, handler in self.previous.items():
			signal.signal(sig, handler)

def bind_parent(expected):
	"""Logger processes only: terminate even if their IO is stalled/stopped."""
	libc = ctypes.CDLL(None, use_errno=True)
	if libc.prctl(1, int(signal.SIGKILL), 0, 0, 0):
		# PR_SET_PDEATHSIG
		raise OSError(ctypes.get_errno(), 'Cannot bind logger lifetime')
	return os.getppid() == expected

def request_stop(identity):
	if not live(identity):
		return False
	# Pin the process when the kernel/Python support pidfds. Recheck identity
	# after opening, so PID reuse cannot redirect a stop to an unrelated owner.
	if hasattr(os, 'pidfd_open') and hasattr(signal, 'pidfd_send_signal'):
		try:
			fd = os.pidfd_open(identity['pid'])
		except ProcessLookupError:
			return False
		except OSError:
			fd = None  # Older board kernels can lack this syscall.
		if fd is not None:
			try:
				if not live(identity):
					return False
				signal.pidfd_send_signal(fd, signal.SIGTERM)
				return True
			except ProcessLookupError:
				return False
			finally:
				os.close(fd)
	try:
		if not live(identity):
			return False
		os.kill(identity['pid'], signal.SIGTERM)
		return True
	except ProcessLookupError:
		return False
