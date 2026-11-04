from run import WORK
r = WORK / 'reports'
source = (r / 'opt.tcl').read_text()
tail = source[source.index('set ps_primitive'):]
(r / 'opt-linked.tcl').write_text('if {[catch {\nset_param general.maxThreads 2\nopen_checkpoint {' + (WORK / 'pipeline-linked-unclocked.dcp').as_posix() + '}\n' + tail)
print('Prepared recovery from completed unclocked linked checkpoint')
