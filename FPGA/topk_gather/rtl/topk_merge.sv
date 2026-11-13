// Merge two sorted runs, emit only the first K records, and drain both inputs.
// Counts refer to stored records, not the original number of candidates.
module topk_merge (
    input  logic        clk,
    input  logic        rst_n,
    // Local stream cancellation. The owner must separately drain memory I/O.
    input  logic        abort_job,
    input  logic        start_valid,
    output logic        start_ready,
    input  logic [31:0] left_count,
    input  logic [31:0] right_count,
    input  logic [31:0] keep_count,
    input  logic [31:0] left_score,
    input  logic [63:0] left_index,
    input  logic        left_valid,
    output logic        left_ready,
    input  logic [31:0] right_score,
    input  logic [63:0] right_index,
    input  logic        right_valid,
    output logic        right_ready,
    output logic [31:0] out_score,
    output logic [63:0] out_index,
    output logic        out_valid,
    input  logic        out_ready,
    output logic        out_last,
    output logic        done_valid,
    input  logic        done_ready,
    output logic [ 3:0] error_code
);
    import topk_order_pkg::*;
    typedef enum logic [1:0] {IDLE, MERGE, DRAIN, DONE} state_t;
    state_t state;
    logic [31:0] left_remaining, right_remaining, keep, emitted;
    logic choose_left, have_choice;
    wire [32:0] total = {1'b0, left_count} + {1'b0, right_count};

    always_comb begin
        have_choice = (left_remaining == 0 || left_valid) &&
                      (right_remaining == 0 || right_valid) &&
                      (left_remaining != 0 || right_remaining != 0);
        choose_left = right_remaining == 0 ||
                      (left_remaining != 0 && precedes(left_score, left_index, right_score, right_index));
        start_ready = state == IDLE;
        out_valid = state == MERGE && !abort_job && have_choice &&
                    (left_remaining == 0 || finite_score(left_score)) &&
                    (right_remaining == 0 || finite_score(right_score));
        out_score = choose_left ? left_score : right_score;
        out_index = choose_left ? left_index : right_index;
        out_last = out_valid && emitted + 1 == keep;
        left_ready = (state == DRAIN && left_remaining != 0) ||
                     (out_valid && out_ready && choose_left);
        right_ready = (state == DRAIN && right_remaining != 0) ||
                      (out_valid && out_ready && !choose_left);
        done_valid = state == DONE;
    end

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            left_remaining <= 0; right_remaining <= 0;
            keep <= 0; emitted <= 0; error_code <= 0;
        end else if (abort_job && (state == MERGE || state == DRAIN)) begin
            state <= DONE;
            if (error_code == 0) error_code <= 8;
        end else begin
            case (state)
                IDLE: if (start_valid) begin
                    left_remaining <= left_count;
                    right_remaining <= right_count;
                    keep <= keep_count; emitted <= 0; error_code <= 0;
                    if (keep_count == 0 || {1'b0, keep_count} > total) begin
                        error_code <= 1;
                        state <= DONE;
                    end else state <= MERGE;
                end
                MERGE: begin
                    if ((left_remaining != 0 && left_valid && !finite_score(left_score)) ||
                        (right_remaining != 0 && right_valid && !finite_score(right_score))) begin
                        error_code <= 2;
                        state <= DRAIN;
                    end else if (out_valid && out_ready) begin
                        if (choose_left) left_remaining <= left_remaining - 1;
                        else right_remaining <= right_remaining - 1;
                        emitted <= emitted + 1;
                        if (emitted + 1 == keep) state <= DRAIN;
                    end
                end
                DRAIN: begin
                    if (left_valid && left_ready) left_remaining <= left_remaining - 1;
                    if (right_valid && right_ready) right_remaining <= right_remaining - 1;
                    if ((left_valid && left_ready && !finite_score(left_score)) ||
                        (right_valid && right_ready && !finite_score(right_score))) error_code <= 2;
                    if (left_remaining == 0 && right_remaining == 0) state <= DONE;
                end
                DONE: if (done_ready) state <= IDLE;
                default: state <= IDLE;
            endcase
        end
    end
endmodule
