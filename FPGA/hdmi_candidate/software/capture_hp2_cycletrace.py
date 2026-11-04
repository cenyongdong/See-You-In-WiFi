"""Read immutable HP2 cycle buffers through aligned, read-only MMIO. No SDK."""
import argparse
import json
import mmap
import os
from pathlib import Path
import stat
import struct
import time
from decode_hp2_cycletrace import decode

def need(ok, message):
    if not ok:
        raise RuntimeError(message)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('output', type=Path)
    p.add_argument('boot_id')
    a = p.parse_args()
    runtime = lambda: Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    need(a.output.is_absolute() and runtime() == a.boot_id, 'Fresh absolute output / same runtime required')
    def save(path, value):
        fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'w') as f:
            json.dump(value, f, indent=2)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
    memory = os.open('/dev/mem', os.O_RDONLY | os.O_SYNC | os.O_CLOEXEC)
    try:
        need(stat.S_ISCHR(os.fstat(memory).st_mode), 'Physical CSR character device required')
        with mmap.mmap(memory, 32768, flags=mmap.MAP_SHARED, prot=mmap.PROT_READ, offset=0x400b8000) as page:
            # One naturally aligned 32-bit load per CSR; never memcpy/SIMD Device memory.
            read = lambda offset: struct.unpack_from('<I', page, offset)[0]
            header = {str(offset): read(offset) for offset in range(0, 0x48, 4)}
            save(a.output.with_suffix('.header.json'), dict(header=header, boot_id=runtime()))
            need(header['0'] == 0x48505401 and header['4'] == 0x01028010, 'Unknown trace aperture; header retained')
            status = header['8']
            snapshot = dict(abi=header['0'], format=header['4'], status=status, nominal_HP_Hz=header['12'],
                boot_id=a.boot_id, read_started_Linux_monotonic_seconds=time.monotonic(), MMIO_writes=0,
                SDK=0, banks=[])
            for bank, base in [(0, 0x10), (1, 0x30)]:
                published = bool(status & (2 << (2 * bank)))
                row = dict(bank=bank, published=published)
                if published:
                    row.update(count=read(base), physical_start=read(base + 4), trigger_index=read(base + 8),
                        trigger_cycle=read(base + 16) | (read(base + 20) << 32))
                    # Keep all physical capacity, including unused tail, out of raw analysis:
                    # count is checked before addresses are used, avoiding unrelated CSR access.
                    need(0 < row['count'] <= 128, 'Invalid trace count; header retained')
                    offset = 0x1000 + 0x2000 * bank
                    row['samples'] = [[read(offset + 64 * i + 4 * j) for j in range(16)] for i in range(row['count'])]
                snapshot['banks'].append(row)
            snapshot.update(status_after=read(8), boot_id_after=runtime(), read_completed_Linux_monotonic_seconds=time.monotonic())
            save(a.output, snapshot)  # Full actual output survives any subsequent validation failure.
            need(snapshot['status_after'] == status and snapshot['boot_id_after'] == a.boot_id, 'Runtime/publication changed; raw retained')
            need(bool(status & 10), 'Neither window published; raw retained')
            for bank in snapshot['banks']:
                if bank['published']:
                    offset = 0x1000 + 0x2000 * bank['bank']
                    for i, words in enumerate(bank['samples']):
                        need(words == [read(offset + 64 * i + 4 * j) for j in range(16)], 'Frozen buffer changed; raw retained')
            result = decode(snapshot)
            save(a.output.with_suffix('.decoded.json'), result)
    finally:
        os.close(memory)
    print(json.dumps(dict(valid=True, published_banks=sum(b['published'] for b in result['banks']), MMIO_writes=0,
        SDK=0, boot_id=a.boot_id)))

if __name__ == '__main__':
    main()
