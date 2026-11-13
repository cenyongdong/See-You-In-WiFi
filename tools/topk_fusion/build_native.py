"""Build rank/selection candidates using public XIR operations.

This is a ZG330 instruction experiment, not a replacement for the deployed model.
Scores must be finite FP16 values promoted to FP32. Rank comparison scaling and
the repeated-Argmax penalty are valid only in that domain. The latter is a
preserved failed large-shape experiment. Matmul Gather is numeric, not a
bit-preserving copy: it canonicalizes signed zero.
"""

import argparse
from pathlib import Path

from runtime import load_xir, save_json


def build(directory, n, k, channels, algorithm="argmax"):
    if not 1 <= k <= n <= 2048 or channels < 1:
        raise ValueError("Require 1 <= K <= N <= 2048 and positive channels")
    xir, dll_handles = load_xir()
    target = xir.ZhugeTarget(xir.ZhugeTarget_Chips.ZG330)
    graph = xir.Network("topk_native", xir.Framework.ONNX, "opset11", target)
    fp32 = xir.FloatType.FP32()

    def dtype(shape):
        return xir.TensorType(fp32, shape, xir.Layout("*" * (len(shape) - 1) + "C"))

    def const(shape, function):
        return xir.Params(dtype(shape)).fill(function)

    def add(op, name):
        op.setName(name)
        graph.addOp(op)
        return op[0]

    def linear(lhs, rhs, alpha, beta, name):
        return add(xir.Add(lhs, rhs, xir.ScalarImm(float(alpha)),
                           xir.ScalarImm(float(beta))), name)

    def concat(values, axis, name):
        # Keep each concat within the conservative documented fan-in limit.
        level = 0
        while len(values) > 16:
            values = [add(xir.Concat(values[i:i + 16], axis), name + "_{}_{}".format(level, i))
                      for i in range(0, len(values), 16)]
            level += 1
        return values[0] if len(values) == 1 else add(xir.Concat(values, axis), name)

    dynamic = algorithm == "rank_dynamic"
    input_types = [dtype([1, n]), dtype([n, channels])]
    if dynamic:
        # Masks are runtime descriptor data, not weights. Scalar broadcast of
        # shared constants across N/K axes corrupts shapes in SDK 3.39.0's
        # optimizer; explicit mask shapes avoid that lowering defect.
        input_types.extend([dtype([1, n]), dtype([k, 1])])
    inputs = xir.Input(*input_types)
    graph.addOp(inputs)
    scores, payload = inputs[0], inputs[1]
    if algorithm == "argmax":
        result = add(xir.Argmax(scores, 1, True), "winner")
        outputs = [result]
    elif algorithm in ("rank", "rank_dynamic"):
        ranking_scores = scores
        if dynamic:
            valid_candidates = inputs[2]
            ones = const([1, n], lambda _: 1.0)
            invalid_candidates = linear(ones, valid_candidates, 1, -1, "invalid_candidates")
            # N/K satisfy K <= Nvalid. Move invalid candidates below every
            # finite FP16 score before pairwise comparisons. Multiplying the
            # zero/one mask first preserves tiny valid scores; adding and then
            # subtracting a large constant would lose them through rounding.
            ranking_scores = linear(scores, invalid_candidates, 1, -262144, "masked_scores")
        # Any two distinct finite binary16 values differ by at least 2**-24.
        # Scaling their difference before clamping makes an exact predicate in
        # this restricted domain. It does NOT implement arbitrary FP32 Greater.
        column = add(xir.Reshape(ranking_scores, [n, 1], xir.Layout("*C")), "score_column")
        delta = linear(ranking_scores, column, 16777216, -16777216, "scaled_pair_difference")
        greater = add(xir.ClampScalar(delta, 0, 1), "strict_greater")
        zero = const([1, 1], lambda _: 0.0)
        negated = linear(zero, delta, 0, -1, "negative_difference")
        less = add(xir.ClampScalar(negated, 0, 1), "strict_less")
        unequal = linear(greater, less, 1, 1, "unequal")
        one = const([1, 1], lambda _: 1.0)
        equal = linear(one, unequal, 1, -1, "equal")
        lower_index = const([n, n], lambda j: float(j % n < j // n))
        tie_winner = add(xir.Multiply(equal, lower_index), "lower_index_wins_ties")
        outranks = linear(greater, tie_winner, 1, 1, "outranking_candidates")
        rank_column = add(xir.Sum(outranks, 1, True), "stable_ranks")
        rank_row = add(xir.Reshape(rank_column, [1, n], xir.Layout("*C")), "rank_row")
        wanted_rank = const([k, 1], lambda j: float(j))
        distance = linear(rank_row, wanted_rank, 1, -1, "rank_distance")
        squared = add(xir.Multiply(distance, distance), "rank_distance_squared")
        match = linear(one, squared, 1, -1, "rank_match")
        selection = add(xir.ClampScalar(match, 0, 1), "selection_matrix")
        if dynamic:
            valid_outputs = inputs[3]
            selection = add(xir.Multiply(selection, valid_outputs), "valid_selection_rows")
        indices = const([n, 1], lambda j: float(j))
        ids = add(xir.Matmul(selection, indices, None), "gather_indices")
        if dynamic:
            all_outputs = const([k, 1], lambda _: 1.0)
            invalid_outputs = linear(all_outputs, valid_outputs, 1, -1, "invalid_outputs")
            ids = linear(ids, invalid_outputs, 1, -1, "invalid_index_sentinel")
        winner_ids = add(xir.Reshape(ids, [1, k], xir.Layout("*C")), "winner_indices")
        selected_payload = add(xir.Matmul(selection, payload, None), "gather_payload")
        selected_scores = add(xir.Matmul(selection, column, None), "gather_scores")
        outputs = [winner_ids, selected_scores, selected_payload]
    else:
        indices = const([1, n], lambda j: float(j))
        one = const([1, 1], lambda _: 1.0)
        state = scores
        winners, masks = [], []
        for rank in range(k):
            winner = add(xir.Argmax(state, 1, True), "winner_{}".format(rank))
            delta = linear(indices, winner, 1, -1, "index_delta_{}".format(rank))
            squared = add(xir.Multiply(delta, delta), "delta_squared_{}".format(rank))
            distance = linear(one, squared, 1, -1, "one_minus_squared_{}".format(rank))
            mask = add(xir.ClampScalar(distance, 0, 1), "one_hot_{}".format(rank))
            winners.append(winner)
            masks.append(mask)
            if rank + 1 < k:
                state = linear(state, mask, 1, -262144, "remove_winner_{}".format(rank))
        selection = concat(masks, 0, "selection_matrix")
        winner_ids = concat(winners, 1, "winner_indices")
        selected_payload = add(xir.Matmul(selection, payload, None), "gather_payload")
        score_column = add(xir.Reshape(scores, [n, 1], xir.Layout("*C")), "score_column")
        selected_scores = add(xir.Matmul(selection, score_column, None), "gather_scores")
        outputs = [winner_ids, selected_scores, selected_payload]
    graph.addOp(xir.Output(*outputs))
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    graph.dumpJsonAndParams(str(directory / "topk_native_parsed.json"),
                            str(directory / "topk_native_parsed.raw"))
    save_json(directory / "contract.json", dict(n=n, k=k, channels=channels,
              algorithm=algorithm, score_domain="finite_fp16_promoted_to_fp32",
              runtime_counts=dynamic, output_policy="valid_prefix_then_zero_and_index_minus_one" if dynamic else "fixed_shape",
              ties="lower_original_index", target="ZG330", board_tested=False))
    print("Built {} N={} K={} C={} in {}".format(algorithm, n, k, channels, directory), flush=True)
    return dll_handles


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--n", type=int, default=8)
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--channels", type=int, default=3)
    parser.add_argument("--algorithm", choices=("argmax", "selection", "rank", "rank_dynamic"), default="argmax")
    args = parser.parse_args()
    build(args.directory, args.n, args.k, args.channels, args.algorithm)
