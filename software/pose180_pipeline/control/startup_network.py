"""Temporary board CSI address; preserve every pre-existing network setting."""
import json
import os
from pathlib import Path
import socket
import struct
import subprocess
import time

ADDRESS = '192.168.50.49'
INTERFACE = 'eth0'

def add(persist, stopping):
	"""Persist ownership intent before mutation; unique label disambiguates rollback."""
	before = json.loads(subprocess.check_output(['ip', '-j', 'addr', 'show', 'dev', INTERFACE], timeout=3))
	if any(item['local'] == ADDRESS for interface in before for item in interface['addr_info']):
		receipt = dict(added=False, address=ADDRESS + '/24', interface=INTERFACE)
		persist(receipt)
		return receipt
	mac = bytes.fromhex(Path('/sys/class/net/' + INTERFACE + '/address').read_text().strip().replace(':',
		''))
	request = (b'\xff' * 6 + mac + b'\x08\x06' + struct.pack('!HHBBH', 1, 0x0800, 6, 4, 1)
		+mac + b'\0' * 4 + b'\0' * 6 + socket.inet_aton(ADDRESS))
	with socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0806)) as channel:
		channel.bind((INTERFACE, 0))
		channel.settimeout(.1)
		for _ in range(3):
			if stopping.requested:
				return None
			channel.send(request)
			end = time.monotonic() + .4
			while time.monotonic() < end:
				try:
					data = channel.recv(2048)
				except socket.timeout:
					continue
				if (len(data) >= 42 and data[12: 14] == b'\x08\x06' and data[22: 28] != mac
					and data[28: 32] == socket.inet_aton(ADDRESS)):
					raise ValueError('CSI address already owned by another device')
	if stopping.requested:
		return None
	receipt = dict(added=True, address=ADDRESS + '/24', interface=INTERFACE,
		label=INTERFACE + ':p' + os.urandom(3).hex())
	persist(receipt)  # If this fails, no address has been changed.
	if stopping.requested:
		return receipt
	subprocess.run(['ip', 'addr', 'add', receipt['address'], 'dev', INTERFACE,
		'label', receipt['label']], check=True, timeout=3)
	return receipt

def remove(receipt):
	if receipt.get('added'):
		if receipt['address'] != ADDRESS + '/24' or receipt['interface'] != INTERFACE:
			raise ValueError('Temporary CSI address receipt differs')
		current = json.loads(subprocess.check_output(['ip', '-j', 'addr', 'show', 'dev', INTERFACE], timeout=3))
		matches = [item for interface in current for item in interface['addr_info'] if item['local'] == ADDRESS]
		if not matches:
			return  # Already removed; preserve every other address.
		if any(item.get('prefixlen') != 24 or
			('label' in receipt and item.get('label') != receipt['label']) for item in matches):
			raise ValueError('CSI address ownership changed; preserve the current address')
		subprocess.run(['ip', 'addr', 'del', receipt['address'], 'dev', receipt['interface']], check=True,
			timeout=3)
