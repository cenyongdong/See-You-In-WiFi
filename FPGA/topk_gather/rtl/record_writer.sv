// Write selected FP32 scores and uint64 indices to separate dense allocations.
// Both buffers belong to one job. Presented writes are never withdrawn on
// abort; unsubmitted partial lines may be discarded before the final fence.
module record_writer (
    input logic clk, rst_n, abort_job,
    input logic start_valid,
    output logic start_ready,
    input logic [63:0] job_id,
    input logic [31:0] record_count,
    input logic [31:0] score_base, score_bytes, index_base, index_bytes,
    input logic [31:0] record_score,
    input logic [63:0] record_index,
    input logic record_valid,
    output logic record_ready,
    output logic [31:0] write_address,
    output logic [511:0] write_data,
    output logic [63:0] write_enable,
    output logic write_valid,
    input logic write_ready,
    output logic fence_valid,
    input logic fence_ready,
    output logic [63:0] fence_job_id,
    input logic fence_response_valid,
    output logic fence_response_ready,
    input logic [63:0] fence_response_job_id,
    input logic fence_error,
    output logic done_valid,
    input logic done_ready,
    output logic [3:0] error_code
);
    typedef enum logic [2:0] {IDLE, ACCEPT, SCORE_WRITE, INDEX_WRITE,
                              FENCE_REQUEST, FENCE_WAIT, DONE} state_t;
    state_t state;
    logic [31:0] count, accepted, score_address, index_address;
    logic [3:0] score_lane;
    logic [2:0] index_lane;
    logic [511:0] scores, indices;
    logic [63:0] score_enable, index_enable, active_job;
    logic abort_pending;
    assign start_ready = state == IDLE;
    assign record_ready = state == ACCEPT && !abort_pending && !abort_job;
    assign write_valid = state == SCORE_WRITE || state == INDEX_WRITE;
    assign write_address = state == SCORE_WRITE ? score_address : index_address;
    assign write_data = state == SCORE_WRITE ? scores : indices;
    assign write_enable = state == SCORE_WRITE ? score_enable : index_enable;
    assign fence_valid = state == FENCE_REQUEST;
    assign fence_job_id = active_job;
    assign fence_response_ready = state == FENCE_WAIT;
    assign done_valid = state == DONE;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE; count <= 0; accepted <= 0; active_job <= 0;
            score_address <= 0; index_address <= 0; score_lane <= 0; index_lane <= 0;
            scores <= 0; indices <= 0; score_enable <= 0; index_enable <= 0;
            error_code <= 0; abort_pending <= 0;
        end else begin
            if (abort_job && state != IDLE && state != DONE) begin
                abort_pending <= 1;
                if (error_code == 0) error_code <= 8;
            end
            case (state)
                IDLE: if (start_valid) begin
                    active_job <= job_id; count <= record_count; accepted <= 0;
                    score_address <= score_base; index_address <= index_base;
                    score_lane <= 0; index_lane <= 0;
                    scores <= 0; indices <= 0; score_enable <= 0; index_enable <= 0;
                    error_code <= 0; abort_pending <= 0;
                    if (record_count == 0 || score_bytes == 0 || index_bytes == 0 ||
                        score_base[5:0] != 0 || index_base[5:0] != 0 ||
                        score_bytes[5:0] != 0 || index_bytes[5:0] != 0 ||
                        ({32'd0, record_count} << 2) > {32'd0, score_bytes} ||
                        ({32'd0, record_count} << 3) > {32'd0, index_bytes} ||
                        {1'b0, score_base} + {1'b0, score_bytes} > 33'h100000000 ||
                        {1'b0, index_base} + {1'b0, index_bytes} > 33'h100000000 ||
                        ({1'b0, score_base} < {1'b0, index_base} + {1'b0, index_bytes} &&
                         {1'b0, index_base} < {1'b0, score_base} + {1'b0, score_bytes})) begin
                        error_code <= 1; state <= DONE;
                    end else state <= ACCEPT;
                end
                ACCEPT: if (abort_pending || abort_job) begin
                    score_enable <= 0; index_enable <= 0; state <= FENCE_REQUEST;
                end else if (record_valid) begin
                    scores[score_lane*32 +: 32] <= record_score;
                    indices[index_lane*64 +: 64] <= record_index;
                    score_enable <= score_enable | (64'hf << (score_lane * 4));
                    index_enable <= index_enable | (64'hff << (index_lane * 8));
                    score_lane <= score_lane + 1; index_lane <= index_lane + 1;
                    accepted <= accepted + 1;
                    if (score_lane == 15 || accepted + 1 == count) state <= SCORE_WRITE;
                    else if (index_lane == 7) state <= INDEX_WRITE;
                end
                SCORE_WRITE: if (write_ready) begin
                    score_enable <= 0; score_lane <= 0; score_address <= score_address + 64;
                    if (abort_pending || abort_job) begin index_enable <= 0; state <= FENCE_REQUEST; end
                    else state <= INDEX_WRITE;
                end
                INDEX_WRITE: if (write_ready) begin
                    index_enable <= 0; index_lane <= 0; index_address <= index_address + 64;
                    if (abort_pending || abort_job || accepted == count) begin
                        score_enable <= 0; state <= FENCE_REQUEST;
                    end else state <= ACCEPT;
                end
                FENCE_REQUEST: if (fence_ready) state <= FENCE_WAIT;
                FENCE_WAIT: if (fence_response_valid) begin
                    if (fence_response_job_id != active_job) begin
                        if (error_code == 0) error_code <= 6;
                    end else begin
                        if (fence_error && error_code == 0) error_code <= 7;
                        state <= DONE;
                    end
                end
                DONE: if (done_ready) state <= IDLE;
                default: state <= IDLE;
            endcase
        end
    end
endmodule
