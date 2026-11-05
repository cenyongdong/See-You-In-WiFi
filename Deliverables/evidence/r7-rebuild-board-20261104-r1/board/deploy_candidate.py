from pathlib import Path
import json,hashlib,tarfile,shutil,os
root=Path('/root/pose180-r7-rebuild-20261104-r1')
archive=Path('/tmp/pose180-r7-rebuild-20261104-r1.tar.gz')
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda:stream.read(1048576),b''):h.update(data)
    return h.hexdigest()
assert sha(archive)=='aa2961fceb914c759f8fb2cdbaff20686de374a89f01a361f0ee8c997d1c7f4b'
with tarfile.open(archive) as tar:
    members=tar.getmembers()
    for member in members:
        path=Path('/root')/member.name
        assert member.isfile() and root in path.parents and '..' not in path.parts
        assert not path.is_symlink()
        if path.exists():
            assert hashlib.sha256(tar.extractfile(member).read()).hexdigest()==sha(path),'Existing file differs: '+str(path)
    tar.extractall('/root',members=members)
identity=json.loads((root/'board/identity.json').read_text())
fixture=Path('/root/pose180-csi-release-20261031-r4/board/dataset.piwcsi2')
assert fixture.is_file() and sha(fixture)==identity['files']['dataset.piwcsi2']
target=root/'board/dataset.piwcsi2'
assert not target.exists()
shutil.copyfile(str(fixture),str(target))
for name,expected in identity['files'].items():assert sha(root/'board'/name)==expected,name
assert os.access(root/'board/pose180_demo',os.X_OK)
assert sha(root/'boot/BOOT.BIN')==identity['BOOT_sha256']
receipt=dict(package=identity['package'],verified_files=len(identity['files']),BOOT_sha256=identity['BOOT_sha256'],dataset_fixture=str(fixture),SDK_started=False,boot_written=False)
(root/'transfer-verified.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
