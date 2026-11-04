from pathlib import Path
import subprocess,json,time
R=Path.cwd();W=R/'.local/fpga-refactor-20261104-r1';O=W/'numeric-equivalence';O.mkdir(exist_ok=True)
def mapped(p):return '/workspace/'+p.relative_to(R).as_posix()
def run(name,args):
 t=time.time()
 with (O/(name+'.log')).open('w') as f:p=subprocess.run(['docker','exec','FPAI',*args],stdout=f,stderr=subprocess.STDOUT)
 (O/(name+'.execution.json')).write_text(json.dumps(dict(command=args,seconds=time.time()-t,native_exit=p.returncode),indent=2))
 if p.returncode:raise RuntimeError((O/(name+'.log')).read_text())
 print(name,'PASS',flush=True)
run('baseline-build',['g++','-O2','-std=c++17','-ffp-contract=off','-Dcsi_pl=csi_pl_baseline','-c',mapped(W/'before/FPGA/csi_preprocess/polar_model.cpp'),'-o',mapped(O/'baseline.o')])
run('comparison-build',['g++','-O2','-std=c++17','-ffp-contract=off','-I/workspace/FPGA/csi_preprocess',mapped(W/'polar_differential.cpp'),'/workspace/FPGA/csi_preprocess/polar_model.cpp',mapped(O/'baseline.o'),'-o',mapped(O/'compare')])
run('comparison',[mapped(O/'compare'),'/workspace/.local/skeleton-overlay-20261031-r2/pose180-skeleton-overlay-20261031-r2/board/dataset.piwcsi2',mapped(O)])
print((O/'comparison.log').read_text())
