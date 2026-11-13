package topk_order_pkg;
    // Payload bits are copied, never recomputed. Only finite scores are ordered.
    function automatic logic finite_score(input logic [31:0] score);
        finite_score = score[30:23] != 8'hff;
    endfunction

    function automatic logic [31:0] order_key(input logic [31:0] score);
        // IEEE +0 and -0 compare equal; preserve their original payload bits.
        if (score[30:0] == 0)
            order_key = 32'h80000000;
        else
            order_key = score[31] ? ~score : (score ^ 32'h80000000);
    endfunction

    function automatic logic precedes(
        input logic [31:0] a_score,
        input logic [63:0] a_index,
        input logic [31:0] b_score,
        input logic [63:0] b_index
    );
        precedes = (order_key(a_score) > order_key(b_score)) ||
                   ((order_key(a_score) == order_key(b_score)) && (a_index < b_index));
    endfunction
endpackage
