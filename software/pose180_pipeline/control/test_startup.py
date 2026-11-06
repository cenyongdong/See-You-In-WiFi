"""Offline release boot binding, previous-attempt guard and graceful supervision."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import threading
import time
from unittest.mock import patch

import startup
from boot_audit import fat_files
from test_resident import port

def main():
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument('binary', type=Path)
	parser.add_argument('output', type=Path)
	args = parser.parse_args()
	root = args.output.resolve()
	root.mkdir()
	# Exercise the actual read-only FAT reader with a compact synthetic image.
	image = bytearray(2048)
	struct.pack_into('<H', image, 11, 512)
	image[13] = 1
	struct.pack_into('<H', image, 14, 1)
	image[16] = 1
	struct.pack_into('<H', image, 17, 16)
	struct.pack_into('<H', image, 22, 1)
	image[510: 512] = b'\x55\xaa'
	struct.pack_into('<H', image, 512 + 4, 0xfff8)
	image[1024: 1035] = b'BOOT    BIN'
	struct.pack_into('<H', image, 1024 + 26, 2)
	struct.pack_into('<I', image, 1024 + 28, 5)
	image[1536: 1541] = b'hello'
	(root / 'fat16.img').write_bytes(image)
	files = fat_files(str(root / 'fat16.img'))
	assert files == [dict(name='BOOT.BIN', size=5, sha256=hashlib.sha256(b'hello').hexdigest())]
	identity = dict(BOOT_sha256='expected', verified_boot_ids=['qualified'])
	with patch.object(startup, 'verify_boot'), patch.object(startup, 'boot_id', return_value='qualified'):
		assert startup.authorize_boot(root, identity) == 'qualified'
	with patch.object(startup, 'verify_boot'), patch.object(startup, 'boot_id', return_value='new'):
		try:
			startup.authorize_boot(root, identity)
		except ValueError:
			pass
		else:
			raise AssertionError('Unknown running BOOT accepted without preparation')
		(root / 'next-boot.json').write_text(json.dumps(dict(BOOT_sha256='expected', previous_boot_id='qualified')))
		assert startup.authorize_boot(root, identity) == 'new'
	previous = root / 'runs/previous'
	previous.mkdir(parents=True)
	(root / 'latest.json').write_text(json.dumps(dict(run='previous')))
	(previous / 'sdk-attempt.json').write_text(json.dumps(dict(boot_id='same')))
	try:
		startup.check_previous(root, 'same')
	except ValueError:
		pass
	else:
		raise AssertionError('Unproved prior SDK shutdown allowed a same-boot retry')
	(previous / 'outcome.json').write_text(json.dumps(dict(native_exit=0, native_shutdown_complete=True,
		device_owners=[])))
	startup.check_previous(root, 'same')
	run = root / 'supervisor'
	(run / 'metadata').mkdir(parents=True)
	shutil.copyfile(args.binary, root / 'pose180_demo')
	(root / 'pose180_demo').chmod(0o755)
	command = startup.command(root, run, 123456, 0)
	options = dict(zip(command[1:: 2], command[2:: 2]))
	assert options['--top-k'] == '1' and options['--score-threshold'] == 'none' and options['--seconds'] == '0'
	assert options['--single-person-stability'] == '1'
	# Use that same selection/runtime invocation with only the device adapter
	# replaced by an explicit native mock and loopback input for this test.
	options['--hdmi'] = '0'
	del options['--csi']
	del options['--filter-backend']
	del options['--hardware-profile']
	options['--input-port'] = str(port())
	options['--result-port'] = str(port())
	options['--status-port'] = str(port())
	options['--view-port'] = str(port())
	command = [command[0]] + [word for pair in options.items() for word in pair]
	timer = threading.Timer(.8, lambda: (run / 'stop.request').touch())
	timer.start()
	try:
		outcome = startup.supervise(run, command, float('inf'), int(options['--status-port']))
	finally:
		timer.cancel()
	assert outcome['native_exit'] == 0 and outcome['native_shutdown_complete'] and outcome['device_owners'] == []
	assert outcome['stop_sent'] and not outcome['automatic_retry']
	result = dict(mock=True, boot_binding=True, previous_failure_guard=True, graceful_stop=True,
		top_k=1, score_threshold=None, native_exit=0, SDK_used=False, board_access=False)
	(root / 'result.json').write_text(json.dumps(result, indent=2))
	print(json.dumps(result))

if __name__ == '__main__':
	main()
