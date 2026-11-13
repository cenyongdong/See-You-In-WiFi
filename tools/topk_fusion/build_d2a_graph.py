"""Wrap generated D2a instructions in a standalone XIR HardOp for host simulation."""

import argparse
import json
from pathlib import Path

from runtime import load_xir, save_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("instructions", type=Path)
    parser.add_argument("--n", type=int, default=8)
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--channels", type=int, default=16)
    parser.add_argument("--quantized-ports", action="store_true")
    args = parser.parse_args()
    data = args.instructions.read_bytes()
    args.directory.mkdir(parents=True, exist_ok=False)

    def value(vid, shape, element, chunk):
        if args.quantized_ports and element != "@uint(64)":
            element = dict(_type_key="icraft::xir::QuantizedType", expressed_dtype="@fp(32)",
                           storage_dtype="@tf(32)" if element == "@fp(32)" else element,
                           scale="@scales([axis=-1])", zero_points=[])
        return dict(_type_key="icraft::xir::Value", v_id=vid, name="", tags={},
                    mtype="@chunk({}@0)".format(chunk), dtype=dict(_type_key="icraft::xir::TensorType",
                    element_dtype=element, layout="@layout(*C)", shape=shape, merged_distrs=[]))

    coordinates = value(0, [args.k, 2], "@fp(16)", 0)
    payload = value(1, [args.n, args.channels], "@fp(32)", 1)
    output = value(2, [args.k, args.channels], "@fp(32)", 2)
    instruction = value(3, [len(data)//8], "@uint(64)", 3)
    instruction.update(_type_key="icraft::xir::Params", _allow_no_data=False)
    instruction["dtype"]["layout"] = "@layout(*)"
    base = dict(device_info={}, tags={}, origin_ops_id=[])
    graph = dict(_type_key="icraft::xir::Network", ai_target="@zhuget(330)", framework_kind="ONNX",
                 framework_version="opset11", icraft_version="v3.39.0", icraft_xir_version="3.39.0.0",
                 llm_mode=False, name="topk_native", params_bytes=0, params_md5="", swap_mode=False, tags={},
                 ops=[dict(base, _type_key="icraft::xir::Input", op_id=0, name="inputs", compile_target="@hostt",
                           inputs=[], outputs=[coordinates, payload]),
                      dict(base, _type_key="icraft::xir::HardOp", op_id=1, name="D2aGather",
                           compile_target="@zhuget(330)", inputs=[coordinates, payload], outputs=[output],
                           instr=[instruction], layer_count=1, params=[], sub_hard_ops=[]),
                      dict(base, _type_key="icraft::xir::Output", op_id=2, name="outputs", compile_target="@hostt",
                           inputs=[output], outputs=[])])
    source = args.directory / "skeleton.json"
    save_json(source, graph)
    xir, handles = load_xir()
    network = xir.Network.CreateFromJsonFile(str(source))
    parameters = network.getOpById(1).paramsAttrs()
    if len(parameters) != 1:
        raise RuntimeError("Unexpected HardOp instruction parameter count")
    parameters[0].setData(data)
    network.dumpJsonAndParams(str(args.directory / "topk_native_ZG.json"),
                             str(args.directory / "topk_native_ZG.raw"))
    print("Wrapped D2a instructions in XIR", flush=True)
    return handles


if __name__ == "__main__":
    main()
