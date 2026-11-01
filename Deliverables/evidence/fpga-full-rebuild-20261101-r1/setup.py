from pathlib import Path
import hashlib,json,subprocess,sys,time
root=Path('D:/FPGACompetitionProject');work=root/'.local/frb1101-r1';archive=root/'Deliverables/pose180-complete-sources-20261031-r4.rar'
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
expected=json.loads((root/'Deliverables/release-20261031-r4-validation.json').read_text(encoding='utf-8-sig'))['source']
assert digest(archive)==expected['sha256']
start=time.time();dest=work/'unpack';dest.mkdir()
with (work/'extract.log').open('w') as log:subprocess.run(['D:/7-zip/7z.exe','x',str(archive),'-o'+str(dest),'-y','-bso0','-bsp0'],stdout=log,stderr=subprocess.STDOUT,check=True)
source=work/'source';old=dest/archive.stem
assert source.parent.resolve()==work.resolve() and old.parent.resolve()==dest.resolve() and not source.exists()
old.rename(source)
manifest=json.loads((source/'FPGA/hdmi_candidate/rebuild-inputs.json').read_text())
for n,h in manifest['critical_sha256'].items():assert digest(source/n)==h,n
with (work/'prepare.log').open('w') as log:subprocess.run([sys.executable,str(source/'tools/release/rebuild_fpga.py'),'prepare','--output',str(work/'build')],stdout=log,stderr=subprocess.STDOUT,check=True)
identity=dict(archive=str(archive),sha256=expected['sha256'],bytes=archive.stat().st_size,extracted_source=str(source),build_output=str(work/'build'),critical_dependency_hashes_checked=len(manifest['critical_sha256']),vendor_dependency_files=manifest['files'],prepare_exit_code=0,extraction_seconds=time.time()-start,board_operations=0,scope='New independent extraction of delivered r4 RAR; packaged incremental r2 reference permitted; do not reuse prior r3 optimized/placed/routed outputs')
(work/'identity.json').write_text(json.dumps(identity,indent=2)+'\n');print(json.dumps(identity),flush=True)
