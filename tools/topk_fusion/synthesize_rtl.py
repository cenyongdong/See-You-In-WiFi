"""Measure standalone RTL cost using the project's Vivado 2018.3 synthesis flow.

The proxy part matches the established JFMQL30TAI676H adaptation. This does not
run JFM implementation, generate a BIT, or certify integrated board timing.
"""

import argparse
from pathlib import Path
import shutil

from runtime import ROOT, VIVADO_BIN, run_native, save_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--top", choices=("topk_tile", "topk_merge", "gather_engine",
                                        "axi_line_port", "write_coalescer", "score_reader", "score_topk",
                                        "topk_gather_tile", "record_writer", "topk_gather_kernel",
                                        "topk_gather_device", "memory_merge", "memory_tile", "memory_stage"), required=True)
    parser.add_argument("--sorted-run", action="store_true", help="Synthesize final packed-run Gather mode")
    parser.add_argument("--generic-shapes", action="store_true", help="Synthesize the ABI 2.0 multi-command peripheral")
    parser.add_argument("--flush-half-zero", action="store_true", help="Synthesize the explicit FP16 compatibility variant")
    args = parser.parse_args()
    if args.sorted_run and args.top not in ("topk_gather_tile", "topk_gather_kernel"):
        parser.error("--sorted-run requires topk_gather_tile or topk_gather_kernel")
    if args.generic_shapes and args.top != "topk_gather_device":
        parser.error("--generic-shapes requires topk_gather_device")
    if args.flush_half_zero and args.top not in ("score_reader", "score_topk", "memory_tile", "memory_stage",
                                                "gather_engine", "topk_gather_tile", "topk_gather_kernel", "topk_gather_device"):
        parser.error("selected top has no FP16 format policy")
    directory = args.directory.resolve()
    directory.mkdir(parents=True, exist_ok=False)
    rtl = ROOT / "FPGA/topk_gather/rtl"
    sources = [rtl / (args.top + ".sv")]
    if args.top.startswith("topk_"):
        sources.insert(0, rtl / "topk_order_pkg.sv")
    if args.top == "score_topk":
        sources = [rtl / (name + ".sv") for name in
                   ("topk_order_pkg", "topk_tile", "score_reader", "score_topk")]
    if args.top == "memory_merge":
        sources = [rtl / (name + ".sv") for name in
                   ("topk_order_pkg", "topk_merge", "run_reader", "run_writer", "line_read_arbiter", "memory_merge")]
    if args.top in ("memory_tile", "memory_stage"):
        sources = [rtl / (name + ".sv") for name in
                   ("topk_order_pkg", "topk_tile", "score_reader", "score_topk", "run_writer", "memory_tile")]
        if args.top == "memory_stage":
            sources.extend(rtl / (name + ".sv") for name in
                           ("topk_merge", "run_reader", "line_read_arbiter", "memory_merge", "memory_stage"))
    if args.top in ("topk_gather_tile", "topk_gather_kernel", "topk_gather_device"):
        sources = [rtl / (name + ".sv") for name in
                   ("topk_order_pkg", "topk_tile", "score_reader", "score_topk", "run_reader",
                    "gather_engine", "topk_gather_tile")]
        if args.top in ("topk_gather_kernel", "topk_gather_device"):
            sources.extend([rtl / "record_writer.sv", rtl / "topk_gather_kernel.sv"])
        if args.top == "topk_gather_device":
            sources.extend([rtl / "axi_line_port.sv", rtl / "kernel_control.sv", rtl / "topk_gather_device.sv"])
            if args.generic_shapes:
                sources.extend(rtl / (name + ".sv") for name in
                               ("topk_merge", "run_writer", "line_read_arbiter", "memory_tile", "memory_merge", "memory_stage", "command_kernel"))
    for source in sources:
        shutil.copyfile(source, directory / source.name)
    sources = [directory / source.name for source in sources]
    generics = (["INPUT_IS_SORTED_RUN=1"] if args.sorted_run else []) + (["GENERIC_SHAPES=1"] if args.generic_shapes else [])
    if args.flush_half_zero:
        generics.append("FP16_FLUSH_TO_POSITIVE_ZERO=1")
    script = """if {[catch {
set_param general.maxThreads 2
create_project -in_memory -part xc7z030ffg676-2
read_verilog -sv [list SOURCE_LIST]
synth_design -mode out_of_context -top TOP_NAME -part xc7z030ffg676-2 GENERICS
create_clock -name estimate_clk -period 10.000 [get_ports clk]
report_utilization -file utilization.rpt
report_timing_summary -file timing_estimate.rpt
write_checkpoint synthesized.dcp
} result]} {puts stderr $result; exit 1}
exit 0
""".replace("SOURCE_LIST", " ".join("{" + p.as_posix() + "}" for p in sources)).replace("TOP_NAME", args.top).replace(
        "GENERICS", "-generic {" + " ".join(generics) + "}" if generics else "")
    (directory / "synthesize.tcl").write_text(script, encoding="ascii")
    run_native("synthesize", [VIVADO_BIN / "vivado.bat", "-mode", "batch", "-notrace",
               "-source", directory / "synthesize.tcl"], directory)
    required = ("utilization.rpt", "timing_estimate.rpt", "synthesized.dcp")
    if not all((directory / p).is_file() for p in required):
        raise RuntimeError("Native synthesis did not produce the required reports")
    save_json(directory / "result.json", dict(top=args.top, synthesis_passed=True,
              proxy_part="xc7z030ffg676-2", physical_target="JFMQL30TAI676H",
              timing_budget_ns=10, sorted_run=args.sorted_run, generic_shapes=args.generic_shapes,
              fp16_policy="flush-half-zero" if args.flush_half_zero else "preserve",
              integrated_timing_passed=False, board_tested=False))


if __name__ == "__main__":
    main()
