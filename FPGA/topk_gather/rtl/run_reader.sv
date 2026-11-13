// Read packed scratch records: {index[63:0], reserved=0, score_bits[31:0]}.
// A line contains four records. Allocations own complete 64-byte lines.
// Abort cancels the internal record stream; its consumer shares that abort.
// A presented DDR read is never withdrawn, and its response is drained first.
module run_reader (
    input logic clk, rst_n, abort_job,
    input logic start_valid,
    output logic start_ready,
    input logic [31:0] source_base, source_bytes, record_count,
    input logic [63:0] index_limit,
    output logic [31:0] record_score,
    output logic [63:0] record_index,
    output logic record_valid,
    input logic record_ready,
    output logic [31:0] read_address,
    output logic read_valid,
    input logic read_ready,
    input logic [511:0] read_data,
    input logic read_response_valid,
    output logic read_response_ready,
    input logic read_error,
    output logic done_valid,
    input logic done_ready,
    output logic [3:0] error_code
);
    typedef enum logic [2:0] {IDLE, VALIDATE, REQUEST, RESPONSE, EMIT, DONE} state_t;
    state_t state;
    logic [31:0] remaining, allocation_bytes;
    logic [63:0] limit;
    logic [511:0] line_data;
    logic [1:0] lane;
    logic abort_pending, invalid_record, nonfinite;
    logic [31:0] reserved;

    assign start_ready = state == IDLE;
    assign read_valid = state == REQUEST;
    assign read_response_ready = state == RESPONSE;
    assign done_valid = state == DONE;
    assign record_score = line_data[lane*128 +: 32];
    assign reserved = line_data[lane*128+32 +: 32];
    assign record_index = line_data[lane*128+64 +: 64];
    assign nonfinite = record_score[30:23] == 255;
    assign invalid_record = reserved != 0 || record_index >= limit;
    assign record_valid = state == EMIT && !abort_pending && !abort_job && !invalid_record && !nonfinite;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE; remaining <= 0; allocation_bytes <= 0; limit <= 0;
            line_data <= 0; lane <= 0; abort_pending <= 0; error_code <= 0; read_address <= 0;
        end else begin
            if (abort_job && state != IDLE && state != DONE) abort_pending <= 1;
            case (state)
                IDLE: if (start_valid) begin
                    read_address <= source_base; allocation_bytes <= source_bytes;
                    remaining <= record_count; limit <= index_limit; lane <= 0;
                    abort_pending <= abort_job; error_code <= 0; state <= VALIDATE;
                end
                VALIDATE: begin
                    if (!remaining || !limit || read_address[5:0] != 0 || allocation_bytes[5:0] != 0 ||
                        !allocation_bytes || {4'd0, allocation_bytes} < {remaining, 4'd0} ||
                        {1'b0, read_address} + {1'b0, allocation_bytes} > 33'h100000000) begin
                        error_code <= 1; state <= DONE;
                    end else if (abort_pending || abort_job) begin error_code <= 8; state <= DONE; end
                    else state <= REQUEST;
                end
                REQUEST: if (read_ready) state <= RESPONSE;
                RESPONSE: if (read_response_valid) begin
                    if (read_error) begin error_code <= 5; state <= DONE; end
                    else if (abort_pending || abort_job) begin error_code <= 8; state <= DONE; end
                    else begin line_data <= read_data; state <= EMIT; end
                end
                EMIT: begin
                    if (abort_pending || abort_job) begin error_code <= 8; state <= DONE; end
                    else if (nonfinite || invalid_record) begin
                        error_code <= nonfinite ? 2 : 4; state <= DONE;
                    end else if (record_ready) begin
                        remaining <= remaining - 1;
                        if (remaining == 1) state <= DONE;
                        else if (lane == 3) begin lane <= 0; read_address <= read_address + 64; state <= REQUEST; end
                        else lane <= lane + 1;
                    end
                end
                DONE: if (done_ready) state <= IDLE;
                default: state <= IDLE;
            endcase
        end
    end
endmodule
