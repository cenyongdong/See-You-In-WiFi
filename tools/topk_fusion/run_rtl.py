"""Run native Vivado 2018.3 RTL simulation without board access."""

import argparse
import hashlib
from pathlib import Path
import shutil

from pl_vectors import make_vectors, make_gather_vectors, make_score_vectors, make_pipeline_vectors
from runtime import ROOT, VIVADO_BIN, run_native, save_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--suite", choices=("sort", "gather", "fusion", "kernel", "run_gather", "device", "command_device", "records", "memory_tile", "memory_merge", "plan", "axi", "mig", "scores", "pipeline"), default="sort")
    parser.add_argument("--vectors", type=Path)
    parser.add_argument("--write-buffer", action="store_true")
    parser.add_argument("--memory-merge", action="store_true", help="Execute both plan tile and merge commands through DDR")
    parser.add_argument("--flush-half-zero", action="store_true", help="Explicit old-model FP16 compatibility variant")
    args = parser.parse_args()
    if args.flush_half_zero and args.suite not in ("device", "command_device", "scores"):
        raise ValueError("FP16 policy option is supported by the device and score suites")
    directory = args.directory.resolve()
    directory.mkdir(parents=True, exist_ok=False)
    if args.suite in ("device", "command_device"):
        if args.vectors is None:
            raise ValueError("The device suite requires C++-generated --vectors")
        shutil.copyfile(args.vectors, directory / "device_vectors.txt")
        counts = dict(device_cases=int(args.vectors.read_text().splitlines()[0]))
    elif args.suite == "plan":
        if args.vectors is None:
            raise ValueError("The plan suite requires C++-generated --vectors")
        shutil.copyfile(args.vectors, directory / "plan_vectors.txt")
        shutil.copyfile(Path(str(args.vectors) + ".scratch"), directory / "plan_scratch.txt")
        counts = dict(planned_shapes=6, batches_per_shape=2)
        counts["memory_merge"] = args.memory_merge
    elif args.suite == "axi":
        counts = dict(axi_cases=97)
    elif args.suite == "mig":
        counts = dict(bank_fences=8, fault_variants=2)
    elif args.suite == "records":
        counts = dict(record_dma_cases=20)
    elif args.suite == "memory_merge":
        counts = dict(memory_merge_cases=30)
    elif args.suite == "scores":
        counts = make_score_vectors(directory, flush_half_zero=args.flush_half_zero)
    elif args.suite in ("pipeline", "memory_tile"):
        counts = make_pipeline_vectors(directory, memory_output=args.suite == "memory_tile")
    elif args.suite in ("fusion", "kernel", "run_gather"):
        if args.suite == "run_gather" and args.vectors is not None:
            shutil.copyfile(args.vectors, directory / "gather_vectors.txt")
            shutil.copyfile(Path(str(args.vectors) + ".records"), directory / "run_records.txt")
            counts = dict(gather_cases=int(args.vectors.read_text().splitlines()[0]), actual_run_records=True)
        else:
            counts = make_gather_vectors(directory, fused=True, memory_output=args.suite != "fusion",
                                         sorted_run=args.suite == "run_gather")
    else:
        if args.suite == "gather" and args.vectors is not None:
            shutil.copyfile(args.vectors, directory / "gather_vectors.txt")
            counts = dict(gather_cases=int(args.vectors.read_text().splitlines()[0]),
                          supplied_vectors=str(args.vectors.resolve()))
        else:
            counts = make_vectors(directory) if args.suite == "sort" else make_gather_vectors(directory)
    source = ROOT / "FPGA/topk_gather"
    files = ([source / "rtl/topk_order_pkg.sv", source / "rtl/topk_tile.sv",
              source / "rtl/topk_merge.sv", source / ("sim/tb_" + args.suite + ".sv")] if args.suite in ("sort", "plan")
             else [source / ("rtl/axi_line_port.sv" if args.suite == "axi" else "rtl/gather_engine.sv"),
                   source / ("sim/tb_" + args.suite + ".sv")])
    top = "tb_" + args.suite
    if args.suite == "mig":
        files = [source / "rtl/mig_line_port.sv", source / "sim/tb_mig.sv"]
    if args.suite == "scores":
        files = [source / "rtl/score_reader.sv", source / "sim/tb_scores.sv"]
        if args.flush_half_zero:
            top = "tb_scores_configured"
            wrapper = directory / (top + ".sv")
            wrapper.write_text("module tb_scores_configured; tb_scores #(.FP16_FLUSH_TO_POSITIVE_ZERO(1)) test(); endmodule\n")
            files.append(wrapper)
    if args.suite == "records":
        files = [source / "rtl/run_reader.sv", source / "rtl/run_writer.sv", source / "sim/tb_records.sv"]
    if args.suite == "memory_merge":
        files = [source / ("rtl/" + name + ".sv") for name in
                 ("topk_order_pkg", "topk_merge", "run_reader", "run_writer", "line_read_arbiter", "memory_merge")]
        files.append(source / "sim/tb_memory_merge.sv")
    if args.suite == "plan" and args.memory_merge:
        files[3:3] = [source / ("rtl/" + name + ".sv") for name in
                      ("score_reader", "score_topk", "run_reader", "run_writer", "line_read_arbiter", "memory_tile", "memory_merge", "memory_stage")]
        top = "tb_plan_configured"
        wrapper = directory / (top + ".sv")
        wrapper.write_text("module tb_plan_configured; tb_plan #(.USE_MEMORY_MERGE(1)) test(); endmodule\n")
        files.append(wrapper)
    if args.suite in ("pipeline", "memory_tile"):
        files = [source / ("rtl/" + name + ".sv") for name in
                 ("topk_order_pkg", "topk_tile", "score_reader", "score_topk")]
        files.append(source / "sim/tb_pipeline.sv")
        if args.suite == "memory_tile":
            files[4:4] = [source / "rtl/run_writer.sv", source / "rtl/memory_tile.sv"]
            top = "tb_pipeline_configured"
            wrapper = directory / (top + ".sv")
            wrapper.write_text("module tb_pipeline_configured; tb_pipeline #(.MEMORY_OUTPUT(1)) test(); endmodule\n")
            files.append(wrapper)
    if args.suite in ("fusion", "kernel", "run_gather"):
        files = [source / ("rtl/" + name + ".sv") for name in
                 ("topk_order_pkg", "topk_tile", "score_reader", "score_topk", "run_reader", "gather_engine", "topk_gather_tile")]
        files.append(source / "sim/tb_gather.sv")
        if args.suite in ("kernel", "run_gather"):
            files.extend([source / "rtl/record_writer.sv", source / "rtl/topk_gather_kernel.sv"])
    if args.suite in ("device", "command_device"):
        files = [source / ("rtl/" + name + ".sv") for name in
                 ("topk_order_pkg", "topk_tile", "score_reader", "score_topk", "run_reader", "gather_engine",
                  "topk_gather_tile", "record_writer", "topk_gather_kernel", "axi_line_port",
                  "kernel_control", "topk_gather_device")]
        files.append(source / "sim/tb_device.sv")
        if args.suite == "command_device":
            files[-1:-1] = [source / ("rtl/" + name + ".sv") for name in
                            ("topk_merge", "run_writer", "line_read_arbiter", "memory_tile", "memory_merge", "memory_stage", "command_kernel")]
        if args.suite == "command_device" or args.flush_half_zero:
            top = "tb_device_configured"
            wrapper = directory / (top + ".sv")
            wrapper.write_text("module tb_device_configured; tb_device #(.GENERIC_SHAPES({}), .FP16_FLUSH_TO_POSITIVE_ZERO({})) test(); endmodule\n".format(
                               int(args.suite == "command_device"), int(args.flush_half_zero)))
            files.append(wrapper)
    if args.suite in ("gather", "fusion", "kernel", "run_gather"):
        files.insert(0, source / "rtl/write_coalescer.sv")
        counts["write_buffer"] = args.write_buffer
        if args.write_buffer or args.suite in ("fusion", "kernel", "run_gather"):
            top = "tb_gather_configured"
            wrapper = directory / (top + ".sv")
            wrapper.write_text("module tb_gather_configured; tb_gather #(.USE_COALESCER({}), .USE_FUSION({}), .USE_MEMORY_OUTPUT({}), .USE_SORTED_RUN({}), .USE_RECORD_FILE({})) test(); endmodule\n".format(
                               int(args.write_buffer), int(args.suite != "gather"), int(args.suite in ("kernel", "run_gather")),
                               int(args.suite == "run_gather"), int(args.suite == "run_gather" and args.vectors is not None)))
            files.append(wrapper)
    (directory / "run.tcl").write_text("run all\nquit\n", encoding="ascii")
    snapshots = directory / "sources"
    snapshots.mkdir()
    identities = []
    for source_file in files:
        copied = snapshots / source_file.name
        shutil.copyfile(source_file, copied)
        identities.append(dict(path=str(source_file), sha256=hashlib.sha256(copied.read_bytes()).hexdigest()))
    files = [snapshots / source_file.name for source_file in files]
    save_json(directory / "sources.json", identities)
    run_native("compile", [VIVADO_BIN / "xvlog.bat", "-sv", *files], directory)
    run_native("elaborate", [VIVADO_BIN / "xelab.bat", top, "-s", "topk_test",
                             "-timescale", "1ns/1ps", "-mt", "2"], directory)
    run_native("simulate", [VIVADO_BIN / "xsim.bat", "topk_test", "-tclbatch", "run.tcl"], directory)
    output = (directory / "simulate.log").read_text(errors="replace")
    marker = "GATHER" if args.suite in ("fusion", "kernel", "run_gather") else args.suite.upper()
    passed = "TOPK_" + marker + "_PASS" in output and "Fatal:" not in output
    save_json(directory / "result.json", dict(passed=passed, board_tested=False,
              fp16_policy="flush-half-zero" if args.flush_half_zero else "preserve", **counts))
    print(output[-1800:])
    if not passed:
        raise SystemExit("RTL simulation did not pass")


if __name__ == "__main__":
    main()
