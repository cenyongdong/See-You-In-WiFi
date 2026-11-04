"""Optional PyTorch export. An explicit compatible checkpoint is mandatory."""
import argparse
from pathlib import Path
import sys

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checkpoint', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if not args.checkpoint.is_file() or args.output.exists():
        parser.error('Provide an existing checkpoint and a new output path')
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / 'model/adaptation'))
    import numpy as np
    np.__dict__.setdefault('object', object)
    import torch
    import onnx
    from mmcv import Config
    from opera.models import build_model
    torch.set_num_threads(2)
    torch.manual_seed(0)
    cfg = Config.fromfile(str(root / 'model/adaptation/model_config.py'))
    cfg.model.backbone.init_cfg = None
    model = build_model(cfg.model)
    model.init_weights()
    checkpoint = torch.load(args.checkpoint, map_location='cpu')
    state = checkpoint.get('state_dict', checkpoint)
    state = {k[7:] if k.startswith('module.') else k: v for k, v in state.items()}
    model.load_state_dict(state, strict=True)
    model.eval()

    class FullGraph(torch.nn.Module):
        def __init__(self, detector):
            super().__init__()
            self.detector = detector

        def forward(self, csi_tokens):
            return self.detector.predict_tokens(csi_tokens)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with torch.no_grad():
        torch.onnx.export(FullGraph(model).eval(), (torch.zeros(1, 180, 60),), str(args.output),
            opset_version=11, input_names=['csi_tokens'], output_names=['scores', 'poses'],
            do_constant_folding=True)
    graph = onnx.load(str(args.output))
    onnx.checker.check_model(graph)
    shapes = [[d.dim_value for d in v.type.tensor_type.shape.dim] for v in graph.graph.output]
    if shapes != [[1, 180], [1, 180, 14, 3]]:
        raise ValueError('Unexpected output shapes: ' + repr(shapes))
    if any(node.op_type in ('TopK', 'ScatterND', 'GatherElements') for node in graph.graph.node):
        raise ValueError('Candidate selection or slice-write remains in export')
    print('Exported all 180 candidates:', args.output)

if __name__ == '__main__':
    main()
