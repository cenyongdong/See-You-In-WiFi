"""Exercise consumer safety bounds and the reduced functional CSR control."""
from pathlib import Path
import json
import subprocess
from prepare import ROOT, HERE, SOURCE, WORK, EVIDENCE

old = ROOT / 'FPGA/hdmi_candidate/diagnostics/deferred_consume_r45'
text = (old / 'tb_deferred_control.sv').read_text()
text = text.replace('wire ready,arm,rearm;', 'wire ready,arm;')
text = text.replace(',clears=0;', ';')
text = text.replace('.drain_status(status),.pc_status(160\'h0c00000000000000),\n  .pc_ready(1\'b1),.pc_system_resetn(1\'b1),.arm(arm),.checker_rearm(rearm),.csr(csr)',
    '.drain_status(status),.rlast(last),.ps_rvalid(rv),.arm(arm),.csr(csr)')
text = text.replace('  if(rearm)clears<=clears+1;\n', '')
text = text.replace('c.csr_flags[7]', 'c.csr_flags[1]')
text = text.replace("    write(32'h43484b52);settled();write(32'h534e4150);settled();\n    if(clears!=1 || !c.csr_flags[1])$fatal(1,\"post-quiet checker rearm not acknowledged\");\n",
    '')
text = text.replace('if(clears || !c.command_error)', 'if(!c.command_error)')
text = text.replace('checker_rearm=%0d",N,accepted,arms,clears', 'control_error=%0d",N,accepted,arms,c.command_error')
text = text.replace('if(c.csr_status!=0 || c.csr_flags[1:0]!=0)', 'if(c.csr_status!=0 || c.csr_flags[1:0]!=0 || !c.csr_flags[16] || !c.csr_flags[7])')
(HERE / 'tb_control.sv').write_text(text, newline='\n')
interface = ROOT / '.local/hdmi-boot-witness-20261019-r23/reference/rtl/utils/mna_itf.sv'
V = Path('D:/vivado18.3/Vivado/2018.3/bin')
results = []
for name, top, test, marker in (
    ('control', 'tb_deferred_control', HERE / 'tb_control.sv', 'DEFERRED_CONTROL_PASS'),
    ('bounds', 'tb_startup_drain', old / 'tb_bounds.sv', 'BOUNDED_DRAIN_UNIT_PASS')):
    cwd = WORK / ('simulation-' + name)
    cwd.mkdir()
    (cwd / 'run.tcl').write_text('run all\nquit\n')
    files = [interface, SOURCE / 'hp2_startup_drain.sv', SOURCE / 'hp2_deferred_control.sv', test]
    commands = [('compile', [str(V / 'xvlog.bat'), '-sv', *map(str, files)]),
        ('elaborate', [str(V / 'xelab.bat'), top, '-s', name, '-timescale', '1ns/1ps', '-mt', '2']),
        ('simulate', [str(V / 'xsim.bat'), name, '-tclbatch', 'run.tcl'])]
    for stage, command in commands:
        log = EVIDENCE / ('simulation-' + name + '-' + stage + '.log')
        with log.open('xb') as output:
            child = subprocess.run(command, cwd=cwd, stdout=output, stderr=subprocess.STDOUT)
        results.append(dict(test=name, stage=stage, command=command, native_exit=child.returncode))
        (EVIDENCE / 'simulation.json').write_text(json.dumps(results, indent=2) + '\n')
        if child.returncode:
            raise RuntimeError(log.read_text(errors='replace')[-3000:])
    if marker not in log.read_text(errors='replace'):
        raise RuntimeError('Simulation assertion did not finish: ' + str(log))
    print(json.dumps(dict(test=name, passed=True)), flush=True)
