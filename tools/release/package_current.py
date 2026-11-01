"""Source-focused current delivery. No device access or model conversion; superseded delivery BOOT removed only by explicit request."""
from pathlib import Path
import argparse,hashlib,json,os,shutil,subprocess,importlib.util
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Deliverables';WORK=ROOT/'.local/release-20261031-r4'
NAME='pose180-csi-release-20261031-r4';SOURCE='pose180-complete-sources-20261031-r4'
RELEASE=OUT/NAME;PREVIOUS=OUT/'pose180-csi-release-20261031-r3'
UPSTREAM=ROOT/'third_party/Person-in-WiFi-3D-repo'
if not UPSTREAM.exists():UPSTREAM=Path('D:/Person-in-WIFI-3D/Person-in-WiFi-3D-repo')
SKIP={'.git','__pycache__','node_modules','.Xil','.cache','.idea','.pnpm-store','build','dist','runs','pc-logs','xsim.dir','obj_dir','.mim'}
CODE={'.c','.cc','.cpp','.h','.hpp','.cu','.cuh','.sv','.v','.vh','.svh','.vhd','.vhdl','.xdc','.tcl','.xci','.bd','.xpr','.py','.sh','.ps1','.bat','.cmd','.cmake','.toml','.yaml','.yml','.mjs','.js','.ts','.tsx','.jsx','.html','.css','.cfg','.ini','.conf','.coe','.mem','.hex','.sdc','.qsf','.prj','.bif'}
JSON_NAMES={'CMakePresets.json','package.json','package-lock.json','tsconfig.json','default_boot.json','dependencies.lock.json','current-bit.json','rebuild-inputs.json'}
PC_ASSETS=('build/three.module.js','build/three.core.js','examples/jsm/controls/OrbitControls.js','LICENSE')
def deployment_files(release=RELEASE):
 # Source pruning excludes node_modules/build, but these four offline runtime
 # assets are required by the browser and must also appear in the manifest.
 files={p.relative_to(release).as_posix():p for p in walk(release) if p.is_file()}
 for name in PC_ASSETS:
  relative='pc/software/pc_viewer/node_modules/three/'+name
  p=release/relative
  if not p.is_file():raise FileNotFoundError('Required PC viewer asset: '+str(p))
  files[relative]=p
 return files
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def save(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def walk(p):
 for base,dirs,names in os.walk(p):
  dirs[:]=[n for n in dirs if n not in SKIP]
  for n in names:yield Path(base)/n
def is_source(p):
 name=p.name.lower()
 if any(s in name for s in ('netlist','funcsim','timesim','.private.')):return False
 if name in {'inspect-ai7030_edif_top_late.xdc','scoped-actual.xdc'}:return False
 return p.suffix.lower() in CODE or p.name in JSON_NAMES or p.name in {'CMakeLists.txt','Makefile','LICENSE','NOTICE','.editorconfig','.clang-format'} or p.suffix.lower()=='.md' or (p.suffix.lower()=='.txt' and (p.name.startswith(('requirements','LICENSE','NOTICE'))))
def refresh():
 WORK.mkdir(exist_ok=True)
 if not RELEASE.exists():
  if not PREVIOUS.exists():raise FileNotFoundError('Provide the current verified deployment payload before refreshing documents')
  shutil.copytree(PREVIOUS,RELEASE,ignore=lambda d,ns:[n for n in ns if n in SKIP or n in {'next-boot.json','verified-boot.json'}])
 ident=json.loads((RELEASE/'board/identity.json').read_text());ident.update(package=NAME,validation_scope='Same validated runtime; source-only delivery and evidence refresh, no new board run')
 for n,h in ident['files'].items():
  if sha(RELEASE/'board'/n)!=h:raise ValueError('Runtime changed: '+n)
 save(RELEASE/'board/identity.json',ident)
 for n in ('README.md','SOURCE.md','PERFORMANCE.md'):
  src=OUT/({ 'README.md':NAME+'-DEPLOY.md','SOURCE.md':'SOURCE-20261031.md','PERFORMANCE.md':'PERFORMANCE.md'}[n]);shutil.copyfile(src,RELEASE/n)
  if n in ('PERFORMANCE.md','SOURCE.md'):
   page=RELEASE/n;page.write_text(page.read_text(encoding='utf-8').replace('(evidence/','(evidence/current/'),encoding='utf-8')
 shutil.copytree(OUT/'evidence',RELEASE/'evidence/current',dirs_exist_ok=True)
 files=json.loads((RELEASE/'release-files.json').read_text())
 for p in (RELEASE/'evidence/current').rglob('*'):
  if p.is_file():files[p.relative_to(RELEASE).as_posix()]=sha(p)
 files['PERFORMANCE.md']=sha(RELEASE/'PERFORMANCE.md')
 for n in ('LICENSE','THIRD_PARTY_NOTICES.md'):
  shutil.copyfile(ROOT/n,RELEASE/n);files[n]=sha(RELEASE/n)
 for n in files:files[n]=sha(RELEASE/n)
 save(RELEASE/'release-files.json',files)
 prepare_live_assets()
 print('Prepared current deployment; validated binary/data/model unchanged',flush=True)
def prepare_live_assets():
 # Only the current delivery payload is refreshed; historical firmware evidence stays intact.
 router=RELEASE/'router-service';router.mkdir(exist_ok=True)
 original=ROOT/'.local/router-autostart-20261025-r1'
 catalog=original/'package-final.json'
 if not catalog.exists():catalog=router/'package.json'
 roles=json.loads(catalog.read_text())
 for role,meta in roles.items():
  src=original/meta['archive']
  if not src.exists():src=router/meta['archive']
  if sha(src)!=meta['sha256']:raise ValueError('Router package identity differs: '+role)
  dst=router/meta['archive']
  if src.resolve()!=dst.resolve():shutil.copyfile(src,dst)
 save(router/'package.json',roles)
 shutil.copyfile(ROOT/'software/pose180_pipeline/control/autostart/install.sh',router/'install.sh')
 shutil.copyfile(ROOT/'tools/release/current_boot_control.py',RELEASE/'boot_control.py')
 shutil.copyfile(ROOT/'tools/release/current_boot_control.py',RELEASE/'build-config/current_boot_control.py')
 old=RELEASE/'boot/BOOT-baseline-csi-v2.bin'
 if old.exists():
  if old.is_symlink() or old.parent.resolve()!=(RELEASE/'boot').resolve():raise ValueError('Unexpected superseded BOOT path')
  expected=json.loads((RELEASE/'boot/package-review.json').read_text())['baseline_BOOT_sha256']
  if sha(old)!=expected:raise ValueError('Preserve unidentified old BOOT instead of removing it')
  old.unlink()
 for name in ['README.md','SOURCE.md','PERFORMANCE.md']:
  p=RELEASE/name
  p.write_text(p.read_text(encoding='utf-8').replace('(FPGA-REBUILD-20261101-r1.md)','(evidence/current/fpga-full-rebuild-20261101-r1/result.json)'),encoding='utf-8')
 router.joinpath('README.md').write_text('Router assets for the four previously validated RT-AC86U devices only. Roles and SHA256 are in package.json. First-install, wiring, live capture, status and shutdown instructions are in ../README.md. install.sh preserves original hooks and checks role, firmware platform and package digest. Do not reinstall over an existing /jffs/pose180-csi service. No board SDK or BOOT is started by these assets.\n',encoding='utf-8')
 files={name:sha(p) for name,p in deployment_files().items() if name!='release-files.json'}
 save(RELEASE/'release-files.json',files)

def dependency_files():
 spec=importlib.util.spec_from_file_location('pose180_fpga_dependencies',ROOT/'tools/release/fpga_dependencies.py')
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 return module.collect(ROOT)

def source_files():
 selected={};vendor_dependencies=dependency_files()
 def add(p,arc=None):
  if p.is_file():selected[arc or p.relative_to(ROOT).as_posix()]=p
 for name in ('software','tools','FPGA','demo_v1','ADR','LICENSES'):
  for p in walk(ROOT/name):
   if is_source(p):add(p)
 for p in ROOT.glob('*.md'):add(p)
 add(ROOT/'LICENSE');add(ROOT/'.gitignore')
 for name in ('Deliverables/README.txt','Deliverables/SOURCE-20261031.md','Deliverables/PERFORMANCE.md','Deliverables/'+NAME+'-DEPLOY.md'):add(ROOT/name)
 for p in walk(OUT/'evidence'):add(p)
 for p in (ROOT/'.local/csi-preprocess-20261031-r3').iterdir():
  if p.is_file() and (is_source(p) or p.name=='manifest.json'):add(p)
 for p in (ROOT/'.local/csi-preprocess-20261031-r3/sources').iterdir():
  if is_source(p):add(p)
 for p in (ROOT/'.local/csi-preprocess-20261031-r3/reports').glob('*.tcl'):add(p)
 # Vendor original RTL and parameter/configuration files; generated IP HDL can be
 # regenerated from XCI/BD with the matching adapted vendor toolchain.
 ref=ROOT/'.local/hdmi-boot-witness-20261019-r23/reference'
 for p in walk(ref):
  rel=p.relative_to(ref);parts=rel.parts
  if any(x.endswith(('.runs','.cache','.hw','.ip_user_files')) for x in parts):continue
  if not is_source(p) and p.name!='component.xml':continue
  if 'ip_patch' in parts:
   if p.relative_to(ROOT).as_posix() not in vendor_dependencies:continue
  if 'ipshared' in parts or 'hdl' in parts or 'sim' in parts or 'simulation' in parts or 'synth' in parts:continue
  if 'ip' in parts and p.suffix.lower() in {'.v','.sv','.vh','.vhd','.vhdl'}:continue
  add(p)
 # Preserve local upstream model architecture/training/export code, not datasets,
 # checkpoints, ONNX outputs or build products from the upstream checkout.
 for name in ('opera','configs','tools','exportONNX','third_party','requirements'):
  for p in walk(UPSTREAM/name):
   if is_source(p):add(p,'third_party/Person-in-WiFi-3D-repo/'+p.relative_to(UPSTREAM).as_posix())
 for name in ('LICENSE','README.md','requirements.txt','setup.py','setup.cfg','reproduce.md'):add(UPSTREAM/name,'third_party/Person-in-WiFi-3D-repo/'+name)
 for name in ('build/three.module.js','build/three.core.js','examples/jsm/controls/OrbitControls.js','LICENSE','package.json'):add(ROOT/'software/pc_viewer/node_modules/three'/name)
 model=ROOT/'model/piw24_pose180_shared-20261024-r1'
 for name in ('piw24_pose180_ZG.json','piw24_pose180_ZG.raw','source/pose180_shared.onnx','piw24_pose180.toml','source/identities.json','README.md'):add(model/name)
 add(ROOT/'model/README.md')
 bit=ROOT/'hardware/current/pose180-csi-v3.bit'
 if not bit.exists():bit=ROOT/'.local/csi-preprocess-20261031-r3/boot-package/ai7030_top_disable_icap.bit'
 add(bit,'hardware/current/pose180-csi-v3.bit')
 selected.update(vendor_dependencies)
 return selected

def archive(path,pairs):
 if path.exists():raise FileExistsError(path)
 stage=WORK/('source' if path.stem==SOURCE else 'staging-'+path.stem)
 stage.mkdir(parents=True,exist_ok=True)
 for name,p in pairs.items():
  if p.is_symlink():raise ValueError('Unexpected archive link: '+name)
  target=Path('\\\\?\\'+str((stage/name).resolve()));target.parent.mkdir(parents=True,exist_ok=True)
  if path.stem==SOURCE:
   try:os.link(p,target)
   except OSError:shutil.copyfile(p,target)
  else:shutil.copyfile(p,target)
 rar=Path(os.environ.get('POSE180_RAR',str(ROOT/'.local/release-20261031-r3/rar-tool/Rar.exe')))
 if not rar.is_file():raise FileNotFoundError('Set POSE180_RAR to an official RAR command-line executable')
 log=WORK/(path.stem+'-rar.log')
 with log.open('w',encoding='utf-8') as f:
  subprocess.run([str(rar),'a','-ma5','-m5','-md256m','-mt4','-s','-r','-idq','-y',str(path.resolve()),'*'],cwd=stage,stdout=f,stderr=subprocess.STDOUT,check=True)
  subprocess.run([str(rar),'t','-idq',str(path.resolve())],stdout=f,stderr=subprocess.STDOUT,check=True)
 with path.open('rb') as f:
  if f.read(8)!=b'Rar!\x1a\x07\x01\x00':raise ValueError('Not native RAR5')
 h=sha(path);path.with_suffix(path.suffix+'.sha256').write_text(h+'  '+path.name+'\n')
 v=dict(path=path.name,format='RAR5',bytes=path.stat().st_size,sha256=h,rar_test_pass=True);print(json.dumps(v),flush=True);return v

def source():
 WORK.mkdir(exist_ok=True);files=source_files();vendor_dependencies=dependency_files()
 for name,p in files.items():
  if p.suffix.lower() in {'.dcp','.edf','.edif','.ngc','.ncd','.bit','.bin','.pth','.pt','.onnx','.raw'} and not name.startswith('model/piw24_pose180_shared-20261024-r1/') and name!='hardware/current/pose180-csi-v3.bit' and name not in vendor_dependencies:
   raise ValueError('Unexpected binary '+name)
 # Check only the selected plaintext files against known local secrets. Values
 # never enter process arguments, environment, reports or console output.
 private=ROOT/'.local/device-access.private.json'
 if private.exists():
  values=json.loads(private.read_text());secrets=[v['password'].encode() for v in values.values() if isinstance(v,dict) and isinstance(v.get('password'),str) and len(v['password'])>=8]
  for name,p in files.items():
   if p.stat().st_size<2000000 and p.suffix.lower() not in {'.png','.raw','.onnx'}:
    data=p.read_bytes()
    if any(secret in data for secret in secrets):raise ValueError('Credential appears in selected file: '+name)
 index=dict(source_root=SOURCE,files=len(files),uncompressed_bytes=sum(p.stat().st_size for p in files.values()),model_assets=['piw24_pose180_ZG.json','piw24_pose180_ZG.raw','source/pose180_shared.onnx'],excluded=['Unrelated device checkpoints and build caches','BOOT binaries (current qualified adapted BIT included)' ,'Unrelated generated HDL and build cache','raw CSI datasets','training checkpoint with optimizer','SDK installers'],upstream_source=str(UPSTREAM),paths=sorted(files))
 save(WORK/'source-index.json',index)
 files['SOURCE-INDEX.json']=WORK/'source-index.json'
 result=archive(OUT/(SOURCE+'.rar'),{SOURCE+'/'+n:p for n,p in files.items()})
 if result['bytes']>200000000:raise ValueError('Archive exceeds requested 200 MB budget')
 save(WORK/'source-archive.json',result)
def deploy():
 result=archive(OUT/(NAME+'.rar'),{NAME+'/'+name:p for name,p in deployment_files().items()})
 save(WORK/'deploy-archive.json',result)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['refresh','source','deploy','inventory']);a=parser.parse_args()
 if a.stage=='inventory':
  f=source_files();print(json.dumps(dict(files=len(f),MB=sum(p.stat().st_size for p in f.values())/1e6,largest=sorted([(n,p.stat().st_size) for n,p in f.items()],key=lambda x:-x[1])[:8])))
 else:{'refresh':refresh,'source':source,'deploy':deploy}[a.stage]()
