// DDR -> two packed runs -> stable prefix merge -> packed DDR result.
// Both inputs are completely consumed/validated, even after emitting K records.
// A shared abort cancels local streams; reader/writer owners drain actual I/O.
module memory_merge (
    input logic clk, rst_n, abort_job,
    input logic start_valid,
    output logic start_ready,
    input logic [63:0] job_id, index_limit,
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
    logic [1:0] readers_ready, readers_done;
    logic merge_ready, merge_done, writer_ready, writer_done, port_idle;
    logic accept_start, accept_done, cancel_streams, invalid_buffers, all_reads_finished, active;
    logic [3:0] left_error, right_error, merge_error, writer_error;
    logic [31:0] left_score, right_score, merged_score;
    logic [63:0] left_index, right_index, merged_index;
    wire left_valid, left_ready, right_valid, right_ready, merged_valid, merged_ready;
    logic [1:0][31:0] client_address;
    logic [1:0] client_valid, client_ready, client_response_valid, client_response_ready;
    logic writer_fence_valid, writer_fence_ready;
    logic [31:0] checked_left, checked_right, checked_keep;

    function automatic logic overlap(input logic [31:0] a, a_bytes, b, b_bytes);
        overlap = {1'b0, a} < {1'b0, b}+{1'b0, b_bytes} &&
                  {1'b0, b} < {1'b0, a}+{1'b0, a_bytes};
    endfunction
    assign invalid_buffers = overlap(left_base, left_bytes, right_base, right_bytes) ||
                             overlap(left_base, left_bytes, destination_base, destination_bytes) ||
                             overlap(right_base, right_bytes, destination_base, destination_bytes) ||
                             !left_count || !right_count;
    assign checked_left = invalid_buffers ? 0 : left_count;
    assign checked_right = invalid_buffers ? 0 : right_count;
    assign checked_keep = invalid_buffers ? 0 : keep_count;
    assign start_ready = (&readers_ready) && merge_ready && writer_ready && port_idle;
    assign accept_start = start_valid && start_ready;
    assign done_valid = (&readers_done) && merge_done && writer_done && port_idle;
    assign accept_done = done_valid && done_ready;
    assign cancel_streams = abort_job || (active &&
                           (left_error != 0 || right_error != 0 || merge_error != 0 || writer_error != 0));
    // Preserve the triggering failure rather than an induced peer abort.
    always_comb begin
        if (left_error != 0 && left_error != 8) error_code = left_error;
        else if (right_error != 0 && right_error != 8) error_code = right_error;
        else if (merge_error != 0 && merge_error != 8) error_code = merge_error;
        else if (writer_error != 0 && writer_error != 8) error_code = writer_error;
        else error_code = (left_error != 0 || right_error != 0 || merge_error != 0 || writer_error != 0) ? 8 : 0;
    end
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin done_job_id <= 0; active <= 0; end
        else begin
            if (accept_start) begin done_job_id <= job_id; active <= 1; end
            if (accept_done) active <= 0;
        end
    end
    assign all_reads_finished = (&readers_done) && merge_done && port_idle;
    assign fence_valid = writer_fence_valid && all_reads_finished;
    assign writer_fence_ready = fence_ready && all_reads_finished;

    line_read_arbiter read_port(
        .clk(clk), .rst_n(rst_n), .client_address(client_address), .client_valid(client_valid), .client_ready(client_ready),
        .client_response_valid(client_response_valid), .client_response_ready(client_response_ready),
        .read_address(read_address), .read_valid(read_valid), .read_ready(read_ready),
        .read_response_valid(read_response_valid), .read_response_ready(read_response_ready), .idle(port_idle));
    run_reader left_reader(
        .clk(clk), .rst_n(rst_n), .abort_job(cancel_streams), .start_valid(accept_start), .start_ready(readers_ready[0]),
        .source_base(left_base), .source_bytes(left_bytes), .record_count(checked_left), .index_limit(index_limit),
        .record_score(left_score), .record_index(left_index), .record_valid(left_valid), .record_ready(left_ready),
        .read_address(client_address[0]), .read_valid(client_valid[0]), .read_ready(client_ready[0]),
        .read_data(read_data), .read_response_valid(client_response_valid[0]), .read_response_ready(client_response_ready[0]),
        .read_error(read_error), .done_valid(readers_done[0]), .done_ready(accept_done), .error_code(left_error));
    run_reader right_reader(
        .clk(clk), .rst_n(rst_n), .abort_job(cancel_streams), .start_valid(accept_start), .start_ready(readers_ready[1]),
        .source_base(right_base), .source_bytes(right_bytes), .record_count(checked_right), .index_limit(index_limit),
        .record_score(right_score), .record_index(right_index), .record_valid(right_valid), .record_ready(right_ready),
        .read_address(client_address[1]), .read_valid(client_valid[1]), .read_ready(client_ready[1]),
        .read_data(read_data), .read_response_valid(client_response_valid[1]), .read_response_ready(client_response_ready[1]),
        .read_error(read_error), .done_valid(readers_done[1]), .done_ready(accept_done), .error_code(right_error));
    topk_merge merger(
        .clk(clk), .rst_n(rst_n), .abort_job(cancel_streams), .start_valid(accept_start), .start_ready(merge_ready),
        .left_count(checked_left), .right_count(checked_right), .keep_count(checked_keep),
        .left_score(left_score), .left_index(left_index), .left_valid(left_valid), .left_ready(left_ready),
        .right_score(right_score), .right_index(right_index), .right_valid(right_valid), .right_ready(right_ready),
        .out_score(merged_score), .out_index(merged_index), .out_valid(merged_valid), .out_ready(merged_ready), .out_last(),
        .done_valid(merge_done), .done_ready(accept_done), .error_code(merge_error));
    run_writer writer(
        .clk(clk), .rst_n(rst_n), .abort_job(cancel_streams), .start_valid(accept_start), .start_ready(writer_ready),
        .job_id(job_id), .destination_base(destination_base), .destination_bytes(destination_bytes), .record_count(checked_keep),
        .record_score(merged_score), .record_index(merged_index), .record_valid(merged_valid), .record_ready(merged_ready),
        .write_address(write_address), .write_data(write_data), .write_enable(write_enable), .write_valid(write_valid), .write_ready(write_ready),
        .fence_valid(writer_fence_valid), .fence_ready(writer_fence_ready), .fence_job_id(fence_job_id),
        .fence_response_valid(fence_response_valid), .fence_response_ready(fence_response_ready),
        .fence_response_job_id(fence_response_job_id), .fence_error(fence_error),
        .done_valid(writer_done), .done_ready(accept_done), .error_code(writer_error));
endmodule
