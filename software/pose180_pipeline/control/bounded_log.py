"""Bounded byte logs. The native writer uses a nonblocking pipe, never disk IO."""
import argparse
import json
import os
from pathlib import Path
import time
from process_guard import bind_parent

class RingLog:
	def __init__(self, root, name, limit=524288, segments=4):
		self.root, self.name = Path(root), name
		self.limit, self.segments = limit, segments
		self.index, self.size, self.file = -1, 0, None
		self.retry = 0
		self.received = self.written = self.dropped = 0

	def write(self, data):
		self.received += len(data)
		if time.monotonic() < self.retry:
			self.dropped += len(data)
			return
		offset = 0
		try:
			while offset < len(data):
				if self.file is None or self.size == self.limit:
					self.close()
					self.index = (self.index + 1) % self.segments
					self.file = (self.root / ('%s-%d.log' % (self.name, self.index))).open('wb', buffering=0)
					self.size = 0
				part = data[offset: offset + self.limit - self.size]
				count = self.file.write(part)
				if not count:
					raise OSError('Short log write')
				offset += count
				self.size += count
				self.written += count
		except OSError:
			self.dropped += len(data) - offset
			self.close()
			self.retry = time.monotonic() + 5

	def close(self):
		stream, self.file = self.file, None
		if stream is not None:
			try:
				stream.close()
			except OSError:
				pass  # Diagnostic close errors cannot skip process cleanup.

def pump(fd, folder):
	log = RingLog(folder, 'native')
	try:
		while True:
			data = os.read(fd, 65536)
			if not data:
				break
			log.write(data)
	finally:
		os.close(fd)
		log.close()
		# EAGAIN at the SDK's stdout cannot be counted by the receiving end.
		try:
			(Path(folder) / 'native-log-summary.json').write_text(json.dumps(dict(
				received_bytes=log.received, written_bytes=log.written,
				disk_dropped_bytes=log.dropped, pipe_dropped_bytes=None,
				maximum_log_bytes=log.limit * log.segments)))
		except OSError:
			pass

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('fd', type=int)
	parser.add_argument('folder')
	parser.add_argument('--parent-pid', type=int)
	args = parser.parse_args()
	if args.parent_pid is not None and not bind_parent(args.parent_pid):
		raise SystemExit(0)
	pump(args.fd, args.folder)
