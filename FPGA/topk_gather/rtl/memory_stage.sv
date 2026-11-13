// One tile-or-merge command on one shared memory port. Engine selection is
// captured at START and cannot change until the tagged DONE is acknowledged.
// For a tile, left_* names the score allocation/count; right_* is unused.
module memory_stage #(parameter integer FP16_FLUSH_TO_POSITIVE_ZERO = 0) (
    input logic clk, rst_n, operation_merge,
    input logic start_valid,
    output logic start_ready,
    input logic [63:0] job_id, index_limit, index_base,
    input logic [2:0] score_element_bytes,
    input logic [31:0] left_base, left_bytes, left_count, right_base, right_bytes, right_count,
    input logic [31:0] destination_base, destination_bytes, keep_count,
    output logic [31:0] read_address,
    output logic read_valid,
    input logic read_ready,
    input logic [511:0] read_data,
    input logic read_response_valid,
    output logic read_response_ready,
    input logic read_error,
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
    output logic [63:0] done_job_id,
    output logic [3:0] error_code
);
    logic active, selected;
    wire accept_start = start_valid && start_ready;
    wire accept_done = done_valid && done_ready;
    wire [1:0] ready, done, rd_valid, rd_response_ready, wr_valid, fn_valid, fn_response_ready;
    wire [1:0][31:0] rd_address, wr_address;
    wire [1:0][511:0] wr_data;
    wire [1:0][63:0] wr_enable, fn_job, completed_job;
    wire [1:0][3:0] error;
    wire [1:0] running = active ? (selected ? 2'b10 : 2'b01) : 2'b00;
    assign start_ready = !active && (&ready);
    assign done_valid = active && done[selected];
    assign done_job_id = completed_job[selected];
    assign error_code = error[selected];
    assign read_address = rd_address[selected];
    assign read_valid = active && rd_valid[selected];
    assign read_response_ready = active && rd_response_ready[selected];
    assign write_address = wr_address[selected];
    assign write_data = wr_data[selected];
    assign write_enable = wr_enable[selected];
    assign write_valid = active && wr_valid[selected];
    assign fence_valid = active && fn_valid[selected];
    assign fence_job_id = fn_job[selected];
    assign fence_response_ready = active && fn_response_ready[selected];
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin active <= 0; selected <= 0; end
        else begin
            if (accept_start) begin active <= 1; selected <= operation_merge; end
            if (accept_done) active <= 0;
        end
    end
    memory_tile #(.FP16_FLUSH_TO_POSITIVE_ZERO(FP16_FLUSH_TO_POSITIVE_ZERO)) tile_engine(
        .clk(clk), .rst_n(rst_n), .start_valid(accept_start && !operation_merge), .start_ready(ready[0]),
        .job_id(job_id), .index_base(index_base), .score_base(left_base), .score_bytes(left_bytes),
        .input_count(left_count), .keep_count(keep_count), .score_element_bytes(score_element_bytes),
        .destination_base(destination_base), .destination_bytes(destination_bytes),
        .read_address(rd_address[0]), .read_valid(rd_valid[0]), .read_ready(running[0] && read_ready), .read_data(read_data),
        .read_response_valid(running[0] && read_response_valid), .read_response_ready(rd_response_ready[0]), .read_error(read_error),
        .write_address(wr_address[0]), .write_data(wr_data[0]), .write_enable(wr_enable[0]),
        .write_valid(wr_valid[0]), .write_ready(running[0] && write_ready),
        .fence_valid(fn_valid[0]), .fence_ready(running[0] && fence_ready), .fence_job_id(fn_job[0]),
        .fence_response_valid(running[0] && fence_response_valid), .fence_response_ready(fn_response_ready[0]),
        .fence_response_job_id(fence_response_job_id), .fence_error(fence_error),
        .done_valid(done[0]), .done_ready(accept_done && !selected), .done_job_id(completed_job[0]), .error_code(error[0]));
    memory_merge merge_engine(
        .clk(clk), .rst_n(rst_n), .abort_job(1'b0), .start_valid(accept_start && operation_merge), .start_ready(ready[1]),
        .job_id(job_id), .index_limit(index_limit), .left_base(left_base), .left_bytes(left_bytes), .left_count(left_count),
        .right_base(right_base), .right_bytes(right_bytes), .right_count(right_count),
        .destination_base(destination_base), .destination_bytes(destination_bytes), .keep_count(keep_count),
        .read_address(rd_address[1]), .read_valid(rd_valid[1]), .read_ready(running[1] && read_ready), .read_data(read_data),
        .read_response_valid(running[1] && read_response_valid), .read_response_ready(rd_response_ready[1]), .read_error(read_error),
        .write_address(wr_address[1]), .write_data(wr_data[1]), .write_enable(wr_enable[1]),
        .write_valid(wr_valid[1]), .write_ready(running[1] && write_ready),
        .fence_valid(fn_valid[1]), .fence_ready(running[1] && fence_ready), .fence_job_id(fn_job[1]),
        .fence_response_valid(running[1] && fence_response_valid), .fence_response_ready(fn_response_ready[1]),
        .fence_response_job_id(fence_response_job_id), .fence_error(fence_error),
        .done_valid(done[1]), .done_ready(accept_done && selected), .done_job_id(completed_job[1]), .error_code(error[1]));
endmodule
