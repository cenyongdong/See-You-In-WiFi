from pathlib import Path
import re,json,subprocess,time,shutil
R=Path.cwd();W=R/'.local/fpga-refactor-20261104-r1';V=Path('D:/vivado18.3/Vivado/2018.3/bin')
O=W/'cycle-equivalence';O.mkdir(exist_ok=True)
def run(name,args,d):
 t=time.time()
 with (d/(name+'.log')).open('w') as f:
  p=subprocess.Popen(list(map(str,args)),cwd=d,stdout=f,stderr=subprocess.STDOUT)
  (d/(name+'.execution.json')).write_text(json.dumps(dict(pid=p.pid,command=list(map(str,args)),started=t,state='running')))
  rc=p.wait()
 (d/(name+'.execution.json')).write_text(json.dumps(dict(pid=p.pid,command=list(map(str,args)),seconds=time.time()-t,native_exit=rc,state='completed'),indent=2))
 if rc:raise RuntimeError((d/(name+'.log')).read_text(errors='replace')[-3000:])
def endparen(s,pos):
 depth=0
 for i in range(pos,len(s)):
  if s[i]=='(':depth+=1
  elif s[i]==')':
   depth-=1
   if depth==0:return i
cases=[('polar','FPGA/csi_preprocess','csi_polar',['polar.sv'],{'busy':('','busy'),'done':('','done'),'error':('','error'),'magnitude':('[31:0]','magnitude'),'angle':('[31:0]','angle')},''),
 ('batch','FPGA/csi_preprocess','csi_batch',['polar.sv','batch.sv'],{'wr_ready':('','wr'),'rd_ready':('','ar'),'rsp_valid':('','rvalid'),'rsp_data':('[31:0]','rd')},'#(.SAMPLES(N))'),
 ('overlay','FPGA/hdmi_candidate/skeleton_overlay','skeleton_overlay',['palette_fifo.sv','overlay.sv'],{'wr_ready':('','ready'),'rd_ready':('','rr'),'rsp_valid':('','rv'),'rsp_data':('[31:0]','rd'),'out_hs':('','oh'),'out_vs':('','ov'),'out_de':('','od'),'out_rgb':('[23:0]','rgb')},'#(.W(32),.H(24))')]
for name,folder,module,files,outputs,params in cases:
 d=O/name;d.mkdir(exist_ok=True)
 modules={'csi_polar':'gold_csi_polar','csi_batch':'gold_csi_batch','palette_fifo':'gold_palette_fifo','skeleton_overlay':'gold_skeleton_overlay'}
 gold=[]
 for file in files:
  s=(W/'before'/folder/file).read_text()
  for old,new in modules.items():s=re.sub(r'\b'+old+r'\b',new,s)
  p=d/('gold_'+file);p.write_text(s);gold.append(p)
 tb=(W/'before'/folder/('tb_'+name+'.sv')).read_text();pos=tb.index('dut(')+3;end=endparen(tb,pos);args=tb[pos+1:end].split(',')
 # Port ordering is taken from the baseline declaration, including shared ANSI types.
 source=(W/'before'/folder/files[-1]).read_text();mat=re.search(r'\bmodule\s+'+module+r'\s*',source);p=mat.end()
 if source[p]=='#':p=endparen(source,source.index('(',p))+1
 p=source.index('(',p);e=endparen(source,p);ports=[re.findall(r'\b\w+\b',x)[-1] for x in source[p+1:e].split(',')]
 assert len(args)==len(ports),(name,len(args),len(ports))
 connections=[]
 for port,arg in zip(ports,args):connections.append('.'+port+'('+('gold_'+port if port in outputs else arg.strip())+')')
 extra='\n'+''.join(f'wire {width} gold_{port};\n' for port,(width,_) in outputs.items())
 extra+=modules[module]+' '+params+' reference_dut('+','.join(connections)+');\n'
 extra+='integer compared_cycles=0;\nalways @(negedge clk'+(' or negedge pclk' if name=='overlay' else '')+') begin\n #0.001;\n if(resetn'+(' && presetn' if name=='overlay' else '')+') begin\n compared_cycles=compared_cycles+1;\n'
 for port,(_,actual) in outputs.items():extra+=f' if({actual} !== gold_{port}) $fatal(1,"cycle mismatch {port}");\n'
 extra+='end\nend\n';tb=tb[:end+2]+extra+tb[end+2:]
 tb=tb.replace('$finish;', '$display("CYCLE_EQUIVALENCE_PASS cycles=%0d",compared_cycles);$finish;')
 (d/'test.sv').write_text(tb)
 if name in ('polar','batch'):shutil.copyfile(W/'after/vectors.hex',d/'vectors.hex')
 (d/'run.tcl').write_text('run all\nquit\n')
 run('compile',[V/'xvlog.bat','-sv','-i',R/folder,*[R/folder/f for f in files],*gold,d/'test.sv'],d)
 run('elaborate',[V/'xelab.bat','tb_'+name,'-s','comparison','-timescale','1ns/1ps','-mt','2'],d)
 run('simulate',[V/'xsim.bat','comparison','-tclbatch','run.tcl'],d)
 text=(d/'simulate.log').read_text(errors='replace');assert 'CYCLE_EQUIVALENCE_PASS' in text and 'Fatal:' not in text
 print(name,re.findall(r'CYCLE_EQUIVALENCE_PASS[^\n]*',text),flush=True)
