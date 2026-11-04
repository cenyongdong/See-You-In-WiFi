"""Prepare native physical checks and unchanged factory bit packaging hooks."""
from prepare import ROOT, HERE, SOURCE, WORK, EVIDENCE, PREV, OLD_WORK, OLD_E, remap, put

text = remap((PREV / 'report.tcl').read_text())
text = text.replace('hp2_protocol_observer deferred_control startup_drain}', 'hp2_protocol_observer}')
addition = '''
foreach instance {deferred_control startup_drain} {
 set cells [get_cells -quiet -hier -filter "NAME =~ U0_ps_ai_peripheral/$instance || NAME =~ U0_ps_ai_peripheral/$instance/*"]
 puts $f "RETAINED\t$instance\t[llength $cells]"
 if {![llength $cells]} {error "Functional consumer/control removed: $instance"}
}
set checker [get_cells -quiet -hier -filter {REF_NAME =~ *protocol_checker* || REF_NAME =~ *hp2_protocol* || REF_NAME =~ *cycle_trace* || REF_NAME =~ *boot_witness* || REF_NAME =~ *event_monitor* || REF_NAME =~ *read_monitor*}]
puts $f "FORBIDDEN_MODULES\t[llength $checker]"
if {[llength $checker]} {error "Passive diagnostic module remains: $checker"}
source {CONSUMER_VALIDATE}
set deferred_validation_file {CONTROL_REPORT}
source {CONTROL_VALIDATE}
set raw_ps [get_pins -hier -filter {REF_PIN_NAME == SAXIHP2ARESETN}]
set raw_ends [filter [all_fanout -flat -endpoints_only -from $raw_ps] {REF_PIN_NAME == D || REF_PIN_NAME == CE}]
if {[llength $raw_ps]!=1 || ![llength $raw_ends]} {error "Consumer reset path missing"}
foreach endpoint $raw_ends {
 set p [get_timing_paths -from $raw_ps -to $endpoint -max_paths 1]
 if {![llength $p]} {error "Consumer reset path is cut: $endpoint"}
 set r [get_property REQUIREMENT $p];set slack [get_property SLACK $p]
 puts $f "CONSUMER_RESET\t$endpoint\t$r\t$slack"
 if {abs($r-5)>0.001 || $slack<0} {error "Consumer reset path failed: $endpoint"}
}
'''.replace('CONSUMER_VALIDATE',
    (SOURCE / 'consumer_paths_validate.tcl').as_posix()).replace('CONTROL_REPORT', (EVIDENCE / 'physical/control-cdc.tsv').as_posix()).replace('CONTROL_VALIDATE',
    (SOURCE / 'deferred_control_validate.tcl').as_posix())
text = text.replace('close $f', addition + '\nclose $f')
put(EVIDENCE / 'report.tcl', text)
text = (PREV / 'qualify.py').read_text().replace('hdmi-probe-free-20261025-r1', WORK.name)
text = text.replace('len(removed) == 7', 'len(removed) == 5')
anchor = "    ready = [row for row in facts if row[0] == 'READY']"
addition = '''    retained = [row for row in facts if row[0] == 'RETAINED']
    need({row[1] for row in retained} == {'deferred_control','startup_drain'} and all(int(row[2])>0 for row in retained), 'Active consumer missing')
    need(['FORBIDDEN_MODULES','0'] in facts, 'Diagnostic/protocol modules remain')
    control = [line.split('\\t') for line in (R/'control-cdc.tsv').read_text().splitlines()]
    need({row[0] for row in control if not row[0].endswith('_ENDPOINT')} == {'TOGGLE','REPLY','COMMAND'}, 'Control CDC checks incomplete')
    need(all(float(row[-1])>=0 for row in control), 'Functional control timing failed')
    reset = [row for row in facts if row[0] == 'CONSUMER_RESET']
    need(reset and all(float(row[-2])==5 and float(row[-1])>=0 for row in reset), 'Consumer reset bound missing/failing')
'''
text = text.replace(anchor, addition + anchor)
text = text.replace('removed_diagnostic_hierarchies=[row[1] for row in removed],', "removed_diagnostic_hierarchies=[row[1] for row in removed], retained_active_hierarchies=[row[1] for row in retained],")
put(HERE / 'qualify.py', text)
put(EVIDENCE / 'bit.tcl', remap((OLD_E / 'bit.tcl').read_text()).replace('impl_probe_free_r1', 'impl_probe_free_drain_r1'))
for name in ('call_procise_disable_icap.bat', 'procise_run_disable_icap.tcl'):
    put(WORK / name, remap((OLD_WORK / name).read_text()).replace('impl_probe_free_r1', 'impl_probe_free_drain_r1'))
put(HERE / 'prepare_bit.py', '"""Factory bit hooks are prepared together with physical qualification."""\nimport prepare_finish\n')
print('Physical checks, active-consumer timing coverage and factory bit hooks prepared')
