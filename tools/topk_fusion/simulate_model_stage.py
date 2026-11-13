"""Run one exported compiled stage with Host instruction simulation only."""

import json
from pathlib import Path
import shutil

from runtime import ICRAFT_BIN, icraft_environment, run_native, save_json


def simulate_stage(exported, name, inputs, directory):
    exported, directory = Path(exported).resolve(), Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=False)
    manifest = json.loads((exported / "manifest.json").read_text())
    stage, = [item for item in manifest["stages"] if item["name"] == name]
    paths = []
    for port in stage["inputs"]:
        path = Path(inputs[port["value_id"]]).resolve()
        if path.stat().st_size != port["bytes"]:
            raise ValueError("Input storage length differs at value {}".format(port["value_id"]))
        # The CLI dispatches by suffix; .f32 would be interpreted as an image.
        fixture = directory / ("input_{}.ftmp".format(port["value_id"]))
        shutil.copyfile(path, fixture)
        paths.append(fixture.as_posix())
    config = directory / "run.toml"
    config.write_text('[run]\njson = "' + (exported / (name + ".json")).as_posix() + '"\n'
                      'raw = "' + (exported / (name + ".raw")).as_posix() + '"\n'
                      'input = "' + ";".join(paths) + '"\n'
                      'backends = "Host"\nuse_fireby = false\n'
                      'dump_format = "HQB"\ndump_ftmp = "' +
                      ",".join(str(p["value_id"]) for p in stage["outputs"]) + '"\n'
                      'log_path = "' + (directory / "native").as_posix() + '"\n', encoding="utf-8")
    temporary = directory / "tmp"
    temporary.mkdir()
    environment = icraft_environment()
    environment.update(TEMP=str(temporary), TMP=str(temporary))
    run_native("simulate", [ICRAFT_BIN / "icraft.exe", "run", config], directory, environment)
    outputs = {}
    for port in stage["outputs"]:
        files = list((directory / "native").glob("*/ftmpHQB/{}.ftmp".format(port["value_id"])))
        if len(files) != 1 or files[0].stat().st_size != port["bytes"]:
            raise RuntimeError("Missing or malformed complete actual output {}".format(port["value_id"]))
        outputs[port["value_id"]] = files[0]
    save_json(directory / "result.json", dict(board_tested=False, backend="Host",
              stage=name, dump_format="HQB",
              actual_outputs={str(k): str(v) for k, v in outputs.items()}))
    return outputs
