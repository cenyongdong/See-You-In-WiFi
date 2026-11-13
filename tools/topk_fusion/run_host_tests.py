"""Compile and test the SDK-independent C++ planner and ownership guard."""

import argparse
import hashlib
from pathlib import Path
import shutil

from runtime import ROOT, run_native, save_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    directory = args.directory.resolve()
    directory.mkdir(parents=True, exist_ok=False)
    source = ROOT / "FPGA/topk_gather/host"
    snapshots = directory / "sources"
    snapshots.mkdir()
    identities = []
    for name in ("topk_plan.hpp", "topk_plan.cpp", "test_topk_plan.cpp",
                 "topk_scratch.hpp", "topk_scratch.cpp", "test_topk_scratch.cpp",
                 "topk_registers.hpp", "generate_device_vectors.cpp", "generate_command_vectors.cpp"):
        copied = snapshots / name
        shutil.copyfile(source / name, copied)
        identities.append(dict(path=str(source / name), sha256=hashlib.sha256(copied.read_bytes()).hexdigest()))
    save_json(directory / "sources.json", identities)
    executable = directory / "test_topk_plan.exe"
    run_native("compile", ["g++", "-std=c++17", "-O2", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
               snapshots / "topk_plan.cpp", snapshots / "topk_scratch.cpp",
               snapshots / "test_topk_plan.cpp", "-o", executable], directory)
    run_native("test", [executable, directory / "plan_vectors.txt"], directory)
    scratch_executable = directory / "test_topk_scratch.exe"
    run_native("compile_scratch", ["g++", "-std=c++17", "-O2", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
               snapshots / "topk_plan.cpp", snapshots / "topk_scratch.cpp", snapshots / "test_topk_scratch.cpp",
               "-o", scratch_executable], directory)
    run_native("test_scratch", [scratch_executable], directory)
    vector_executable = directory / "generate_device_vectors.exe"
    run_native("compile_registers", ["g++", "-std=c++17", "-O2", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
               snapshots / "topk_plan.cpp", snapshots / "generate_device_vectors.cpp", "-o", vector_executable], directory)
    run_native("device_vectors", [vector_executable, directory / "device_vectors.txt"], directory)
    command_executable = directory / "generate_command_vectors.exe"
    run_native("compile_commands", ["g++", "-std=c++17", "-O2", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
               snapshots / "topk_plan.cpp", snapshots / "topk_scratch.cpp", snapshots / "generate_command_vectors.cpp",
               "-o", command_executable], directory)
    run_native("command_vectors", [command_executable, directory / "command_vectors.txt"], directory)
    run_native("command_vectors_ftz", [command_executable, directory / "command_vectors_ftz.txt", "--flush-half-zero"], directory)
    save_json(directory / "result.json", dict(host_tests_passed=True, physical_scratch_tests_passed=True, board_tested=False))


if __name__ == "__main__":
    main()
