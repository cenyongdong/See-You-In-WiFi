"""Read the Lite FAT16 startup partition without mounts, writes or SDK access."""
import hashlib
import struct

def fat_files(device='/dev/mmcblk0p1'):
	with open(device, 'rb') as stream:
		boot = stream.read(512)
		bps = struct.unpack_from('<H', boot, 11)[0]
		spc, reserved, count = boot[13], struct.unpack_from('<H', boot, 14)[0], boot[16]
		entries, sectors = struct.unpack_from('<H', boot, 17)[0], struct.unpack_from('<H', boot, 22)[0]
		if not (bps == 512 and spc > 0 and count in (1, 2) and sectors > 0 and entries > 0 and boot[510: 512] == b'\x55\xaa'):
			raise ValueError('Unexpected Lite FAT16 startup partition')
		root_sector = reserved + count * sectors
		data_sector = root_sector + (entries * 32 + bps - 1) // bps
		stream.seek(reserved * bps)
		fat = stream.read(sectors * bps)
		stream.seek(root_sector * bps)
		root = stream.read(entries * 32)
		result = []
		for offset in range(0, len(root), 32):
			entry = root[offset: offset + 32]
			if entry[0] == 0:
				break
			if entry[0] == 229 or entry[11] & 0x18 or entry[11] == 15:
				continue
			name = entry[: 8].decode('ascii').rstrip()
			extension = entry[8: 11].decode('ascii').rstrip()
			name += '.' + extension if extension else ''
			size = remaining = struct.unpack_from('<I', entry, 28)[0]
			cluster = struct.unpack_from('<H', entry, 26)[0]
			seen, digest = set(), hashlib.sha256()
			while remaining:
				if not (2 <= cluster < 0xfff0 and cluster not in seen and cluster * 2 + 2 <= len(fat)):
					raise ValueError('Invalid FAT cluster chain')
				seen.add(cluster)
				stream.seek((data_sector + (cluster - 2) * spc) * bps)
				block = stream.read(min(remaining, spc * bps))
				if not block:
					raise ValueError('Truncated startup file')
				digest.update(block)
				remaining -= len(block)
				cluster = struct.unpack_from('<H', fat, cluster * 2)[0]
			result.append(dict(name=name, size=size, sha256=digest.hexdigest()))
		return result
