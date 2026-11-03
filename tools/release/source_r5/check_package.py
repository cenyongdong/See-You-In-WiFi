"""Read-only package manifest verification; no tools, SDK or device access."""
from pathlib import Path
import hashlib
import json


def main():
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / 'metadata/source-manifest.json').read_text(encoding='utf-8'))
    count = 0
    for record in manifest['files']:
        path = root / record['path']
        if not path.is_file():
            raise FileNotFoundError(record['path'])
        if path.stat().st_size != record['bytes'] or hashlib.sha256(path.read_bytes()).hexdigest() != record['sha256']:
            raise ValueError('Package input changed: ' + record['path'])
        count += 1
    print('Verified', count, 'manifest files; no device operations')


if __name__ == '__main__':
    main()
