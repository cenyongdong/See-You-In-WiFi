"""Reproducible simulation/OOC; records native exit, never kills on timeout."""
from pathlib import Path
import subprocess, sys, json, re, time
ROOT = Path(__file__).resolve().parents[3]
SRC = Path(__file__).resolve().parent
WORK = ROOT / '.local/skeleton-overlay-20261031-r2'
V = Path('D:/vivado18.3/Vivado/2018.3/bin')
def prepare():
    WORK.mkdir(exist_ok=True)
    (WORK / 'reports').mkdir(exist_ok=True)
    font = (ROOT / 'software/pose180_pipeline/src/display/font5x7.hpp').read_text()
    rows = []
    for ch, values in re.findall(r"\{'(.)', \{\{([0-9, ]+)\}\}\}", font):
        for y, value in enumerate(map(int, values.split(','))):
            rows.append(f"10'd{ord(ch)*8+y}:font_row=5'd{value};")
    (SRC / 'font_rom.vh').write_text('function [4:0] font_row(input [6:0] ch,input [3:0] row);\nbegin case ({ch,row[2:0]})\n' + '\n'.join(rows) + '\ndefault:font_row=0;\nendcase end\nendfunction\n')
def run(name, argv, cwd, env=None):
    log = cwd / (name + '.log')
    with log.open('w') as f:
        p = subprocess.Popen(list(map(str, argv)), cwd=cwd, env=env, stdout=f, stderr=subprocess.STDOUT)
        (cwd / (name + '-process.json')).write_text(json.dumps(dict(pid=p.pid, command=list(map(str, argv)),
            started=time.time(), automatic_kill=False), indent=2))
        rc = p.wait()
    (cwd / (name + '-exit.json')).write_text(json.dumps(dict(native_exit=rc)))
    print(name, rc, str(log), flush=True)
    if rc:
        print(log.read_text(errors='replace')[-4000:])
        sys.exit(rc)
def main():
    prepare()
    mode = sys.argv[1]
    d = WORK / 'reports' / (mode + '-' + time.strftime('%H%M%S'))
    d.mkdir(exist_ok=False)
    (WORK / 'reports' / (mode + '-latest.json')).write_text(json.dumps(dict(directory=str(d))))
    if mode in ('sim', 'frame'):
        top = 'tb_overlay' if mode == 'sim' else 'tb_frame'
        if mode == 'frame':
            fixture = (WORK / 'software/fixture-3.hex').read_text()
            (d / 'fixture.hex').write_text(fixture)
            (d / 'fixture_count.vh').write_text(f'localparam WORDS={len(fixture.splitlines())};\n')
        (d / 'run.tcl').write_text('run all\nquit\n')
        run('compile', [V / 'xvlog.bat', '-sv', '-i', SRC, '-i', d, SRC / 'palette_fifo.sv', SRC / 'overlay.sv',
            SRC / (top + '.sv')], d)
        run('elaborate', [V / 'xelab.bat', top, '-s', 'overlay_sim', '-timescale', '1ns/1ps', '-mt', '2'],
            d)
        run('simulate', [V / 'xsim.bat', 'overlay_sim', '-tclbatch', 'run.tcl'], d)
        t = (d / 'simulate.log').read_text(errors='replace')
        print(t[-1500:])
        if 'OVERLAY_PASS' not in t or 'Fatal' in t:
            sys.exit(1)
    elif mode == 'ooc':
        (d / 'synth.tcl').write_text(f'''set_param general.maxThreads 2
read_verilog -sv [list {{{(SRC/'palette_fifo.sv').as_posix()}}} {{{(SRC/'overlay.sv').as_posix()}}}]
set_property include_dirs {{{SRC.as_posix()}}} [current_fileset]
synth_design -top skeleton_overlay -part xc7z030ffg676-2 -mode out_of_context
create_clock -name GP -period 10 [get_ports clk]
create_clock -name PIXEL -period 6.734 [get_ports pclk]
report_utilization -file utilization.rpt
report_timing_summary -report_unconstrained -file timing.rpt
write_checkpoint -force overlay.dcp
exit
''')
        run('synthesis', [V / 'vivado.bat', '-mode', 'batch', '-nojournal', '-source', 'synth.tcl'], d)
    else:
        raise ValueError(mode)
if __name__ == '__main__':
    main()
