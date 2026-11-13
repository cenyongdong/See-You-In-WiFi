// Bounded memory-to-memory kernel: all three outputs are fenced together.
// The caller owns allocations and establishes producer completion before START.
// A CSR/SDK binding is deliberately separate from this memory-port contract.
module topk_gather_kernel #(
    parameter integer INPUT_IS_SORTED_RUN = 0,
    parameter integer FP16_FLUSH_TO_POSITIVE_ZERO = 0
) (
    input logic clk, rst_n,
    input logic start_valid,
    output logic start_ready,
    input logic [63:0] job_id,
    input logic [31:0] input_count, keep_count, channels,
    input logic [31:0] score_base, score_bytes,
    input logic [2:0] score_element_bytes, element_bytes,
    input logic source_blocked16, destination_blocked16,
    input logic [31:0] source_base, source_bytes, source_row_stride, source_block_stride,
    input logic [31:0] destination_base, destination_bytes, destination_row_stride, destination_block_stride,
    input logic [31:0] selected_score_base, selected_score_bytes, selected_index_base, selected_index_bytes,
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
    output logic [3:0] error_code,
    output logic [31:0] read_transactions, write_transactions
);
    logic core_ready, writer_ready, core_done, writer_done, accept_start, accept_done;
    logic [3:0] core_error, writer_error;
    logic [31:0] record_score;
    logic [63:0] record_index;
    logic record_valid, record_ready, writer_record_ready;
    logic [31:0] core_write_address, writer_write_address;
    logic [511:0] core_write_data, writer_write_data;
    logic [63:0] core_write_enable, writer_write_enable;
    logic core_write_valid, core_write_ready, writer_write_valid, writer_write_ready;
    logic core_fence_valid, writer_fence_valid, core_fence_ready, writer_fence_ready;
    logic core_response_ready, writer_response_ready, all_writers_finished;
    logic grant_valid, grant_writer, prefer_writer, buffers_alias;
    logic [63:0] active_job;
    logic [31:0] checked_count, checked_keep;

    function automatic logic overlap(input logic [31:0] a, a_bytes, b, b_bytes);
        overlap = {1'b0, a} < {1'b0, b} + {1'b0, b_bytes} &&
                  {1'b0, b} < {1'b0, a} + {1'b0, a_bytes};
    endfunction
    always_comb begin
        buffers_alias =
            overlap(selected_score_base, selected_score_bytes, score_base, score_bytes) ||
            overlap(selected_score_base, selected_score_bytes, source_base, source_bytes) ||
            overlap(selected_score_base, selected_score_bytes, destination_base, destination_bytes) ||
            overlap(selected_index_base, selected_index_bytes, score_base, score_bytes) ||
            overlap(selected_index_base, selected_index_bytes, source_base, source_bytes) ||
            overlap(selected_index_base, selected_index_bytes, destination_base, destination_bytes) ||
            overlap(selected_score_base, selected_score_bytes, selected_index_base, selected_index_bytes);
    end
    assign checked_count = buffers_alias ? 32'd0 : input_count;
    assign checked_keep = buffers_alias ? 32'd0 : keep_count;
    assign start_ready = core_ready && writer_ready && !grant_valid;
    assign accept_start = start_valid && start_ready;
    assign done_valid = core_done && writer_done && !grant_valid;
    assign accept_done = done_valid && done_ready;
    assign error_code = core_error != 0 ? core_error : writer_error;
    assign done_job_id = active_job;
    // On a failed core job the writer safely drains its accepted writes, while
    // the fork continues consuming provisional records to avoid a cyclic wait.
    assign record_ready = writer_record_ready || writer_done || core_error != 0;

    // Register the grant, never a transient combinational selection. Each
    // producer holds its address/data until its own handshake.
    assign write_valid = grant_valid;
    assign write_address = grant_writer ? writer_write_address : core_write_address;
    assign write_data = grant_writer ? writer_write_data : core_write_data;
    assign write_enable = grant_writer ? writer_write_enable : core_write_enable;
    assign core_write_ready = grant_valid && !grant_writer && write_ready;
    assign writer_write_ready = grant_valid && grant_writer && write_ready;
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            grant_valid <= 0; grant_writer <= 0; prefer_writer <= 0;
            active_job <= 0; write_transactions <= 0;
        end else begin
            if (accept_start) begin active_job <= job_id; write_transactions <= 0; end
            if (!grant_valid && (core_write_valid || writer_write_valid)) begin
                grant_valid <= 1;
                grant_writer <= writer_write_valid && (!core_write_valid || prefer_writer);
            end
            if (write_valid && write_ready) begin
                grant_valid <= 0; prefer_writer <= !grant_writer;
                write_transactions <= write_transactions + 1;
            end
        end
    end

    // One common fence starts only when BOTH producers have stopped writing.
    // An invalid descriptor may finish without issuing any memory request.
    assign all_writers_finished = (core_fence_valid || core_done) &&
                                  (writer_fence_valid || writer_done) && !grant_valid;
    assign fence_valid = all_writers_finished && (core_fence_valid || writer_fence_valid);
    assign fence_job_id = active_job;
    assign core_fence_ready = all_writers_finished && fence_ready;
    assign writer_fence_ready = all_writers_finished && fence_ready;
    assign fence_response_ready = core_response_ready || writer_response_ready;

    topk_gather_tile #(.INPUT_IS_SORTED_RUN(INPUT_IS_SORTED_RUN),
                     .FP16_FLUSH_TO_POSITIVE_ZERO(FP16_FLUSH_TO_POSITIVE_ZERO)) core(
        .clk(clk), .rst_n(rst_n), .start_valid(accept_start), .start_ready(core_ready), .job_id(job_id),
        .input_count(checked_count), .keep_count(checked_keep), .channels(channels),
        .score_base(score_base), .score_bytes(score_bytes), .score_element_bytes(score_element_bytes),
        .element_bytes(element_bytes), .source_blocked16(source_blocked16),
        .destination_blocked16(destination_blocked16), .source_base(source_base), .source_bytes(source_bytes),
        .source_row_stride(source_row_stride), .source_block_stride(source_block_stride),
        .destination_base(destination_base), .destination_bytes(destination_bytes),
        .destination_row_stride(destination_row_stride), .destination_block_stride(destination_block_stride),
        .record_score(record_score), .record_index(record_index), .record_valid(record_valid),
        .record_ready(record_ready), .record_last(),
        .read_address(read_address), .read_valid(read_valid), .read_ready(read_ready), .read_data(read_data),
        .read_response_valid(read_response_valid), .read_response_ready(read_response_ready), .read_error(read_error),
        .write_address(core_write_address), .write_data(core_write_data), .write_enable(core_write_enable),
        .write_valid(core_write_valid), .write_ready(core_write_ready),
        .fence_valid(core_fence_valid), .fence_ready(core_fence_ready), .fence_job_id(),
        .fence_response_valid(fence_response_valid), .fence_response_ready(core_response_ready),
        .fence_response_job_id(fence_response_job_id), .fence_error(fence_error),
        .done_valid(core_done), .done_ready(accept_done), .done_job_id(), .error_code(core_error),
        .read_transactions(read_transactions), .write_transactions());
    record_writer writer(
        .clk(clk), .rst_n(rst_n), .abort_job(core_error != 0 && !writer_done),
        .start_valid(accept_start), .start_ready(writer_ready), .job_id(job_id), .record_count(checked_keep),
        .score_base(selected_score_base), .score_bytes(selected_score_bytes),
        .index_base(selected_index_base), .index_bytes(selected_index_bytes),
        .record_score(record_score), .record_index(record_index),
        .record_valid(record_valid && core_error == 0), .record_ready(writer_record_ready),
        .write_address(writer_write_address), .write_data(writer_write_data), .write_enable(writer_write_enable),
        .write_valid(writer_write_valid), .write_ready(writer_write_ready),
        .fence_valid(writer_fence_valid), .fence_ready(writer_fence_ready), .fence_job_id(),
        .fence_response_valid(fence_response_valid), .fence_response_ready(writer_response_ready),
        .fence_response_job_id(fence_response_job_id), .fence_error(fence_error),
        .done_valid(writer_done), .done_ready(accept_done), .error_code(writer_error));
endmodule
