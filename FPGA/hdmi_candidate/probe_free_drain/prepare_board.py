"""Prepare three fresh 300-second full-chain rounds with functional consumption."""
from pathlib import Path
import importlib.util
import json
import py_compile
from prepare import ROOT, HERE, WORK, EVIDENCE, PREV, put

source = (PREV / 'prepare_board.py').read_text()
source = source.replace('hdmi-probe-free-20261025-r1', WORK.name)
source = source.replace('BOOT-probe-free-r1.bin', 'BOOT-probe-free-drain-r1.bin')
source = source.replace('enumerate((120, 120, 1800), 1)', 'enumerate((300, 300, 300), 1)')
source = source.replace('session=20261025100000+index', 'session=20261026180000+index')
source = source.replace("mode='probe_free', hardware_profile='probe_free'", "mode='functional_startup_pending', hardware_profile='probe-free-drain-v1'")
source = source.replace("hardware_profile='probe_free'", "hardware_profile='probe-free-drain-v1'")
source = source.replace('SDK=0, diagnostic_MMIO=0', 'SDK=0, passive_diagnostic_MMIO=0')
source = source.replace('diagnostic_MMIO=0,\n', 'passive_diagnostic_MMIO=0, functional_startup_ABI=0x48444302,\n')
source = source.replace("write_text('probe_free\\\\n')", "write_text('functional_startup_pending\\\\n')")
source = source.replace('no protocol health assertion', 'native functional consumer checks/one-shot mitigation still pending before SDK; no protocol checker')
source = source.replace("2026-10-25 user explicitly requested removing all bitstream probes/protocol checkers, booting that design, and reliability verification. This fresh bounded round is within the standing autonomous board-test authorization; no failed SDK retry.",
    "2026-10-26 user explicitly requested removal of diagnostic probes/protocol checkers while retaining abnormal-return consumption, followed by multiple 5-minute full-chain stability tests. Three fresh independent rounds, each at most one candidate and SDK attempt, 300 seconds runtime, one original-BOOT fallback reserved. No blind retry after device failure.")
source = source.replace('runtime_seconds=[120,120,1800]', 'runtime_seconds=[300,300,300]')
# Run the adapted existing packaging code with this module's own path, preserving
# the historical generator and its closed board packages unchanged.
scope = {'__file__': str(HERE / 'prepare_board.py'), '__name__': '_new_bounded_board_package'}
exec(compile(source, str(HERE / 'prepare_board.py'), 'exec'), scope)
scope['main']()

for name in ('board_host.py',):
    text = (PREV / name).read_text().replace('hdmi-probe-free-20261025-r1', WORK.name).replace('HDMI_PROBE_FREE_R1_',
        'HDMI_PROBE_FREE_DRAIN_R1_')
    put(HERE / name, text)
old = ROOT / '.local/hdmi-probe-free-20261025-r1'
for index in range(1, 4):
    text = (old / 'round-1-network.py').read_text().replace(old.name, WORK.name).replace('/round-1/network',
        f'/round-{index}/network')
    put(WORK / f'round-{index}-network.py', text)
for name in ('capture_uart.py', 'capture_hdmi_startup.ps1'):
    text = (old / name).read_text(encoding='utf-8-sig').replace(old.name, WORK.name)
    if name.endswith('.ps1'):
        text = text.replace('seconds_budget=300', 'seconds_budget=90').replace('-lt 300 ', '-lt 90 ')
    else:
        text = text.replace('seconds_budget=300', 'seconds_budget=90')
    put(WORK / name, text)
print(json.dumps({'new_package': WORK.name, 'rounds': 3, 'seconds_per_round': 300, 'active_consumer_retained': True}))
