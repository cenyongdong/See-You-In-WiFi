// Write packed scratch records and wait for a tagged visibility fence.
// Partial-line writes use byte enables; bytes outside record_count are untouched.
// Abort discards only an unsubmitted partial line. A presented write is held
// through its handshake, and fence completion still drains accepted writes.
module run_writer (
    input logic clk, rst_n, abort_job,
    input logic start_valid,
    output logic start_ready,
    input logic [63:0] job_id,
    input logic [31:0] destination_base, destination_bytes, record_count,
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
    typedef enum logic [2:0] {IDLE, VALIDATE, FILL, WRITE_LINE, FENCE, RESPONSE, DONE} state_t;
    state_t state;
    logic [31:0] remaining, allocation_bytes;
    logic [1:0] lane;
    logic abort_pending;
    assign start_ready = state == IDLE;
    assign record_ready = state == FILL && !abort_pending && !abort_job;
    assign write_valid = state == WRITE_LINE;
    assign fence_valid = state == FENCE;
    assign fence_response_ready = state == RESPONSE;
    assign done_valid = state == DONE;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE; remaining <= 0; allocation_bytes <= 0; lane <= 0;
            write_address <= 0; write_data <= 0; write_enable <= 0;
            fence_job_id <= 0; error_code <= 0; abort_pending <= 0;
        end else begin
            if (abort_job && state != IDLE && state != DONE) begin
                abort_pending <= 1;
                if (error_code == 0) error_code <= 8;
            end
            case (state)
                IDLE: if (start_valid) begin
                    remaining <= record_count; allocation_bytes <= destination_bytes;
                    write_address <= destination_base; write_enable <= 0; lane <= 0;
                    fence_job_id <= job_id; error_code <= 0; abort_pending <= abort_job; state <= VALIDATE;
                end
                VALIDATE: begin
                    if (!remaining || write_address[5:0] != 0 || allocation_bytes[5:0] != 0 || !allocation_bytes ||
                        {4'd0, allocation_bytes} < {remaining, 4'd0} ||
                        {1'b0, write_address} + {1'b0, allocation_bytes} > 33'h100000000) begin
                        error_code <= 1; state <= DONE;
                    end else if (abort_pending || abort_job) begin error_code <= 8; state <= FENCE; end
                    else state <= FILL;
                end
                FILL: begin
                    if (abort_pending || abort_job) begin error_code <= 8; write_enable <= 0; state <= FENCE; end
                    else if (record_valid) begin
                        write_data[lane*128 +: 128] <= {record_index, 32'd0, record_score};
                        write_enable[lane*16 +: 16] <= 16'hffff;
                        remaining <= remaining - 1;
                        if (lane == 3 || remaining == 1) state <= WRITE_LINE;
                        else lane <= lane + 1;
                    end
                end
                WRITE_LINE: if (write_ready) begin
                    write_enable <= 0; lane <= 0; write_address <= write_address + 64;
                    if (!remaining || abort_pending || abort_job) state <= FENCE;
                    else state <= FILL;
                end
                FENCE: if (fence_ready) state <= RESPONSE;
                RESPONSE: if (fence_response_valid) begin
                    if (fence_response_job_id != fence_job_id) begin
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
