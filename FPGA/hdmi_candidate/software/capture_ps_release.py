"""Read already-held r26 CSR banks. Never writes MMIO or loads an SDK."""
import argparse
import json
import mmap
import os
from pathlib import Path
import stat
import struct

def need(ok, message):
    if not ok:
        raise RuntimeError(message)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('output', type=Path)
    p.add_argument('boot_id')
    a = p.parse_args()
    need(a.output.is_absolute(), 'Fresh absolute evidence output required')
    runtime = lambda: Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    need(runtime() == a.boot_id, 'Runtime changed before mapping')
    fd = os.open(str(a.output), os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'w') as log:
        def save(row):
            log.write(json.dumps(row) + '\n')
            log.flush()
            os.fsync(log.fileno())
        memory = os.open('/dev/mem', os.O_RDONLY | os.O_SYNC | os.O_CLOEXEC)
        try:
            need(stat.S_ISCHR(os.fstat(memory).st_mode), 'Physical CSR character device required')
            with mmap.mmap(memory, 4096, flags=mmap.MAP_SHARED, prot=mmap.PROT_READ, offset=0x400b0000) as page:
            # The C++ ARM/FREEZE probe has already completed its fenced
            # handshake. Both banks remain static throughout these reads.
                read = lambda offset: struct.unpack_from('<I', page, 0x400 + offset)[0]
                header = dict(abi=read(4), count=read(0x10), status=read(0), request=read(8), response=read(12))
                save(dict(header, event='ps_release_initial', boot_id=a.boot_id))
                need(header == dict(abi=0x41495201, count=104, status=0, request=2, response=2), 'Expected first completed FREEZE missing')
                identity = [read(0x200), read(0x204)]
                save(dict(event='ps_release_header', abi=identity[0], flags=identity[1]))
                need(identity[0] == 0x50534c01 and identity[1] & 3 == 3, 'Release bank is not published')
                words = [read(0x200 + 4 * i) for i in range(128)]
                boot_words = [read(0x14 + 4 * i if i < 11 else 0x1e0 + 4 * (i - 11)) for i in range(19)]
                after = dict(status=read(0), request=read(8), response=read(12))
                save(dict(event='ps_release_snapshot', words=words, boot_words=boot_words, after=after,
                    boot_id=runtime()))
                need(runtime() == a.boot_id and after == dict(status=0, request=2, response=2) and
                    words[: 2] == identity and words[7] == 1 and boot_words[0] == 0x42545201 and boot_words[18] & 128,
                    'Complete raw retained; snapshot identity/generation invalid')
        finally:
            os.close(memory)
    print(json.dumps(dict(valid=True, boot_id=a.boot_id, event_overflow=bool(words[1] & 4), MMIO_writes=0,
        SDK=0)))

if __name__ == '__main__':
    main()
