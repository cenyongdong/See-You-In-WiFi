"""Read-only, naturally aligned MMIO; retain full raw data before validation."""
import argparse, json, mmap, os, stat, struct, time
from pathlib import Path
from decode_hp2_protocol import decode, TRIGGER_MASK

def need(ok, message):
    if not ok:
        raise RuntimeError(message)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('output', type=Path)
    p.add_argument('boot_id')
    a = p.parse_args()
    runtime = lambda: Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    need(a.output.is_absolute() and runtime() == a.boot_id, 'Absolute fresh output / same runtime required')
    def save(path, value):
        fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'w') as f:
            json.dump(value, f, indent=2)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
    memory = os.open('/dev/mem', os.O_RDONLY | os.O_SYNC | os.O_CLOEXEC)
    try:
        need(stat.S_ISCHR(os.fstat(memory).st_mode), 'CSR character device required')
        with mmap.mmap(memory, 16384, flags=mmap.MAP_SHARED, prot=mmap.PROT_READ, offset=0x400b4000) as page:
            read = lambda offset: struct.unpack_from('<I', page, offset)[0]
            header = {str(offset): read(offset) for offset in range(0, 0x84, 4)}
            save(a.output.with_suffix('.header.json'), dict(header=header, boot_id=runtime()))
            need((header['0'], header['4']) in ((0x48505001, 0x01018012), (0x48505002, 0x02018012)), 'Unknown protocol aperture; header retained')
            status = header['8']
            snapshot = dict(abi=header['0'], format=header['4'], status=status,
                boot_id=a.boot_id, nominal_HP_Hz=header['12'], MMIO_writes=0, SDK=0,
                read_started_Linux_monotonic_seconds=time.monotonic())
            if header['0'] == 0x48505002:
                snapshot['trigger_mask'] = sum(header[str(0x70 + 4 * j)] << (32 * j) for j in range(5))
                words = [header[str(0x50 + 4 * j)] for j in range(5)]
                snapshot['first_indication'] = dict(published=bool(header['108'] & 1), HP_cycle=header['100'] | (header['104'] << 32),
                    status_words=words, status=sum(w << (32 * j) for j, w in enumerate(words)))
            def sample(i):
                return [read(0x1000 + 64 * i + 4 * j) for j in range(16)] + [read(0x3000 + 8 * i + 4 * j) for j in range(2)]
            if status & 2:
                count = header['16']
                need(0 < count <= 128, 'Invalid protocol sample count; header retained')
                snapshot['capture'] = dict(count=count, physical_start=header['20'], trigger_index=header['24'],
                    trigger_cycle=header['32'] | (header['36'] << 32),
                    first_status_words=[header[str(0x30 + 4 * j)] for j in range(5)],
                    first_status=sum(header[str(0x30 + 4 * j)] << (32 * j) for j in range(5)),
                    samples=[sample(i) for i in range(count)])
            snapshot.update(status_after=read(8), boot_id_after=runtime(), read_completed_Linux_monotonic_seconds=time.monotonic())
            save(a.output, snapshot)
            need(runtime() == a.boot_id and not ((snapshot['status_after'] ^ status) & 3), 'Publication/runtime changed; raw retained')
            if status & 2:
                for i, words in enumerate(snapshot['capture']['samples']):
                    need(words == sample(i), 'Frozen protocol buffer changed; raw retained')
            result = decode(snapshot)
            save(a.output.with_suffix('.decoded.json'), result)
    finally:
        os.close(memory)
    print(json.dumps(dict(valid=True, published=result['published'], fired=result['fired'],
        first_checks=result.get('first_checks', []), MMIO_writes=0, SDK=0, boot_id=a.boot_id)))

if __name__ == '__main__':
    main()
