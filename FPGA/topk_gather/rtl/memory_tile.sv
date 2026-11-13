// Read one bounded score tile and store its selected records in scratch DDR.
// The shared plan owns all allocations. A subsequent merge starts only after
// this job's tagged fence and DONE; DDR write acceptance alone is insufficient.
module memory_tile #(parameter integer FP16_FLUSH_TO_POSITIVE_ZERO = 0) (
    input logic clk, rst_n,
    input logic start_valid,
    output logic start_ready,
    input logic [63:0] job_id, index_base,
    input logic [31:0] score_base, score_bytes, input_count, keep_count,
    input logic [2:0] score_element_bytes,
    input logic [31:0] destination_base, destination_bytes,
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
    logic sorter_ready, writer_ready, sorter_done, writer_done, active;
    logic accept_start, accept_done, buffers_alias, abort_writer;
    logic [3:0] sorter_error, writer_error;
    logic [31:0] score;
    logic [63:0] index;
    logic record_valid, record_ready, writer_record_ready;
    logic writer_fence_valid, writer_fence_ready;
    assign buffers_alias = {1'b0, score_base} < {1'b0, destination_base}+{1'b0, destination_bytes} &&
                           {1'b0, destination_base} < {1'b0, score_base}+{1'b0, score_bytes};
    assign start_ready = sorter_ready && writer_ready;
    assign accept_start = start_valid && start_ready;
    assign done_valid = sorter_done && writer_done;
    assign accept_done = done_valid && done_ready;
    assign abort_writer = active && sorter_error != 0;
    assign error_code = sorter_error != 0 ? sorter_error : writer_error;
    assign record_ready = writer_record_ready || writer_done || abort_writer;
    assign fence_valid = writer_fence_valid && sorter_done;
    assign writer_fence_ready = fence_ready && sorter_done;
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin active <= 0; done_job_id <= 0; end
        else begin
            if (accept_start) begin active <= 1; done_job_id <= job_id; end
            if (accept_done) active <= 0;
        end
    end
    score_topk #(.FP16_FLUSH_TO_POSITIVE_ZERO(FP16_FLUSH_TO_POSITIVE_ZERO)) sorter(
        .clk(clk), .rst_n(rst_n), .start_valid(accept_start), .start_ready(sorter_ready),
        .source_base(score_base), .source_bytes(score_bytes),
        .input_count(buffers_alias ? 32'd0 : input_count), .keep_count(keep_count),
        .index_base(index_base), .element_bytes(score_element_bytes),
        .read_address(read_address), .read_valid(read_valid), .read_ready(read_ready),
        .read_data(read_data), .read_response_valid(read_response_valid), .read_response_ready(read_response_ready), .read_error(read_error),
        .out_score(score), .out_index(index), .out_valid(record_valid), .out_ready(record_ready), .out_last(),
        .done_valid(sorter_done), .done_ready(accept_done), .error_code(sorter_error));
    run_writer writer(
        .clk(clk), .rst_n(rst_n), .abort_job(abort_writer), .start_valid(accept_start), .start_ready(writer_ready),
        .job_id(job_id), .destination_base(destination_base), .destination_bytes(destination_bytes),
        .record_count(buffers_alias ? 32'd0 : keep_count), .record_score(score), .record_index(index),
        .record_valid(record_valid && !abort_writer), .record_ready(writer_record_ready),
        .write_address(write_address), .write_data(write_data), .write_enable(write_enable), .write_valid(write_valid), .write_ready(write_ready),
        .fence_valid(writer_fence_valid), .fence_ready(writer_fence_ready), .fence_job_id(fence_job_id),
        .fence_response_valid(fence_response_valid), .fence_response_ready(fence_response_ready),
        .fence_response_job_id(fence_response_job_id), .fence_error(fence_error),
        .done_valid(writer_done), .done_ready(accept_done), .error_code(writer_error));
endmodule
