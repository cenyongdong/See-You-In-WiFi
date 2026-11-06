"""Collect the qualified CSI v3 inputs; do not build or access a device."""
from pathlib import Path

REF = '.local/hdmi-boot-witness-20261019-r23/reference'
HW = '.local/csi-preprocess-20261031-r3'
INCREMENTAL = '.local/csi-preprocess-20261031-r2/pipeline-routed-csi-incremental.dcp'

EXCLUDED_SUFFIXES = {'.log', '.jou', '.bak', '.wdb', '.rpt', '.pb', '.html', '.pdf'}
SIMULATION_MARKERS = ('_sim_netlist', '_funcsim', '_timesim')

def is_build_input(path):
# 保留必要网表；排除工具缓存、报告和可再生仿真副本，不改变厂商文件内容。
    return (
        path.is_file()
        and path.name != 'AI_Mate_no_detpost.edif'
        and not any(marker in path.name for marker in SIMULATION_MARKERS)
        and path.suffix.lower() not in EXCLUDED_SUFFIXES
        and '__pycache__' not in path.parts
        )

def collect(root):
    root = Path(root)
    files = {}

    def add(path):
        if not path.is_file():
            raise FileNotFoundError(path)
        if path.is_symlink():
            raise ValueError('Dependency link: ' + str(path))
        files[path.relative_to(root).as_posix()] = path

    def add_tree(relative):
        for path in (root / relative).rglob('*'):
            if is_build_input(path):
                add(path)

    for suffix in ('rtl', 'fpai_demo_vivado.srcs', 'constrs_1', 'PS_AI IP'):
        add_tree(REF + '/' + suffix)
    for suffix in ('030ai', 'edif', 'edif_transform', 'process_control', 'xadc_filter', 'paspd/fmsh/030ai'):
        add_tree(REF + '/ip_patch/' + suffix)

    # 顶层适配脚本与显式引用按原清单收录，不套用递归树的过滤条件。
    for path in (root / REF / 'ip_patch').iterdir():
        if path.is_file() and path.suffix.lower() != '.bak':
            add(path)
    for suffix in (
        'paspd/fmsh/xc7z030.paspd', 'paspd/xilinx/xc7z030.paspd',
        'tools/bitfile_replace.tcl', 'tools/mig_auto_winCheck.tcl',
        'tools/iostandard_check.tcl', 'tools/netdelay_check.tcl',
        ):
        add(root / REF / 'ip_patch' / suffix)
    for relative in (
        REF + '/fpai_demo_vivado.xpr',
        REF + '/fpai_demo_vivado.runs/synth_hp2ready_r24/dont_touch.xdc',
        '.local/hdmi-ps-release-20261020-r26/ps-export.dcp', INCREMENTAL,
        ):
        add(root / relative)
    for name in ('candidate.bif', 'FSBL251210_ddr400_demo.out', 'bl31.elf', 'u-boot'):
        add(root / HW / 'boot-package' / name)
    return files
