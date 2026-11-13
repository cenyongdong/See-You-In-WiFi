// Default: fused fast path for 1 <= K <= N <= 256.
// INPUT_IS_SORTED_RUN: consume K packed records from a completed tiled plan;
// score_base/score_bytes then describe that run, and input_count is the original
// N used to validate indices. No local sorting capacity limit applies here.
// Records are a provisional stream; publish only after successful tagged DONE.
module topk_gather_tile #(
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
    output logic [31:0] record_score,
    output logic [63:0] record_index,
    output logic record_valid, record_last,
    input logic record_ready,
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
    logic sort_start_ready, gather_start_ready, accept_start, accept_done;
    logic sort_done, gather_done;
    logic [3:0] sort_error, gather_error;
    logic [31:0] sort_score;
    logic [63:0] sort_index;
    logic sort_valid, sort_ready, sort_last;
    logic gather_index_ready, gather_index_valid;
    logic held_valid, record_sent, index_sent;
    logic [31:0] sort_read_address, gather_read_address;
    logic sort_read_valid, sort_read_ready, sort_response_valid, sort_response_ready;
    logic gather_read_valid, gather_read_ready, gather_response_valid, gather_response_ready;
    logic read_pending, read_owner_sort, grant_valid, grant_owner_sort;
    logic [31:0] grant_address;
    logic score_aliases_destination;
    logic [31:0] checked_count;

    assign score_aliases_destination =
        {1'b0, score_base} < ({1'b0, destination_base} + {1'b0, destination_bytes}) &&
        {1'b0, destination_base} < ({1'b0, score_base} + {1'b0, score_bytes});
    assign checked_count = score_aliases_destination ? 32'd0 : input_count;
    assign start_ready = sort_start_ready && gather_start_ready && !held_valid && !read_pending && !grant_valid;
    assign accept_start = start_valid && start_ready;
    assign done_valid = sort_done && gather_done && !held_valid && !read_pending && !grant_valid;
    assign accept_done = done_valid && done_ready;
    assign error_code = sort_error != 0 ? sort_error : gather_error;

    // One stored record forks to Gather and the selected score/index consumer.
    // Independent acknowledgements avoid coupled READY/VALID deadlocks.
    assign sort_ready = !held_valid;
    assign record_valid = held_valid && !record_sent;
    assign gather_index_valid = held_valid && !index_sent && !gather_done;
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            held_valid <= 0; record_sent <= 0; index_sent <= 0;
            record_score <= 0; record_index <= 0; record_last <= 0;
        end else begin
            if (held_valid) begin
                if (record_ready) record_sent <= 1;
                if (gather_index_ready || gather_done) index_sent <= 1;
                if ((record_sent || record_ready) &&
                    (index_sent || gather_index_ready || gather_done)) held_valid <= 0;
            end
            if (sort_valid && sort_ready) begin
                held_valid <= 1; record_sent <= 0; index_sent <= 0;
                record_score <= sort_score; record_index <= sort_index; record_last <= sort_last;
            end
        end
    end

    // At most one accepted read is in flight. Capture the owner at acceptance
    // and route the response to that owner, regardless of later requests.
    assign read_valid = grant_valid;
    assign read_address = grant_address;
    assign sort_read_ready = grant_valid && grant_owner_sort && read_ready;
    assign gather_read_ready = grant_valid && !grant_owner_sort && read_ready;
    assign sort_response_valid = read_pending && read_owner_sort && read_response_valid;
    assign gather_response_valid = read_pending && !read_owner_sort && read_response_valid;
    assign read_response_ready = read_pending && (read_owner_sort ? sort_response_ready : gather_response_ready);
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            read_pending <= 0; read_owner_sort <= 0;
            grant_valid <= 0; grant_owner_sort <= 0; grant_address <= 0;
            read_transactions <= 0; write_transactions <= 0;
        end else begin
            if (accept_start) begin read_transactions <= 0; write_transactions <= 0; end
            if (!grant_valid && !read_pending && (sort_read_valid || gather_read_valid)) begin
                grant_valid <= 1; grant_owner_sort <= sort_read_valid;
                grant_address <= sort_read_valid ? sort_read_address : gather_read_address;
            end
            if (read_valid && read_ready) begin
                grant_valid <= 0;
                read_pending <= 1; read_owner_sort <= grant_owner_sort;
                read_transactions <= read_transactions + 1;
            end
            if (read_response_valid && read_response_ready) read_pending <= 0;
            if (write_valid && write_ready) write_transactions <= write_transactions + 1;
        end
    end

    generate if (!INPUT_IS_SORTED_RUN) begin : local_sort
    score_topk #(.FP16_FLUSH_TO_POSITIVE_ZERO(FP16_FLUSH_TO_POSITIVE_ZERO)) sorter(
        .clk(clk), .rst_n(rst_n), .start_valid(accept_start), .start_ready(sort_start_ready),
        .source_base(score_base), .source_bytes(score_bytes), .input_count(checked_count),
        .keep_count(keep_count), .index_base(64'd0), .element_bytes(score_element_bytes),
        .read_address(sort_read_address), .read_valid(sort_read_valid), .read_ready(sort_read_ready),
        .read_data(read_data), .read_response_valid(sort_response_valid),
        .read_response_ready(sort_response_ready), .read_error(read_error),
        .out_score(sort_score), .out_index(sort_index), .out_valid(sort_valid), .out_ready(sort_ready),
        .out_last(sort_last), .done_valid(sort_done), .done_ready(accept_done), .error_code(sort_error));
    end else begin : completed_run
        logic [31:0] remaining;
        wire legal_shape = checked_count > 0 && keep_count > 0 && keep_count <= checked_count;
        assign sort_last = remaining == 1;
        always_ff @(posedge clk or negedge rst_n) begin
            if (!rst_n) remaining <= 0;
            else if (accept_start) remaining <= keep_count;
            else if (sort_valid && sort_ready) remaining <= remaining - 1;
        end
        run_reader reader(
            .clk(clk), .rst_n(rst_n), .abort_job(1'b0),
            .start_valid(accept_start), .start_ready(sort_start_ready),
            .source_base(score_base), .source_bytes(score_bytes),
            .record_count(legal_shape ? keep_count : 32'd0), .index_limit({32'd0, checked_count}),
            .record_score(sort_score), .record_index(sort_index), .record_valid(sort_valid), .record_ready(sort_ready),
            .read_address(sort_read_address), .read_valid(sort_read_valid), .read_ready(sort_read_ready),
            .read_data(read_data), .read_response_valid(sort_response_valid),
            .read_response_ready(sort_response_ready), .read_error(read_error),
            .done_valid(sort_done), .done_ready(accept_done), .error_code(sort_error));
    end endgenerate
    gather_engine #(.FP16_FLUSH_TO_POSITIVE_ZERO(FP16_FLUSH_TO_POSITIVE_ZERO)) gatherer(
        .clk(clk), .rst_n(rst_n), .abort_job(sort_done && sort_error != 0 && !gather_done),
        .start_valid(accept_start), .start_ready(gather_start_ready), .job_id(job_id),
        .input_count(checked_count), .keep_count(keep_count), .channels(channels), .element_bytes(element_bytes),
        .source_blocked16(source_blocked16), .destination_blocked16(destination_blocked16),
        .source_base(source_base), .source_bytes(source_bytes), .source_row_stride(source_row_stride),
        .source_block_stride(source_block_stride), .destination_base(destination_base),
        .destination_bytes(destination_bytes), .destination_row_stride(destination_row_stride),
        .destination_block_stride(destination_block_stride), .index_data(record_index),
        .index_valid(gather_index_valid), .index_ready(gather_index_ready),
        .read_address(gather_read_address), .read_valid(gather_read_valid), .read_ready(gather_read_ready),
        .read_data(read_data), .read_response_valid(gather_response_valid),
        .read_response_ready(gather_response_ready), .read_error(read_error),
        .write_address(write_address), .write_data(write_data), .write_enable(write_enable),
        .write_valid(write_valid), .write_ready(write_ready), .fence_valid(fence_valid), .fence_ready(fence_ready),
        .fence_job_id(fence_job_id), .fence_response_valid(fence_response_valid),
        .fence_response_ready(fence_response_ready), .fence_response_job_id(fence_response_job_id),
        .fence_error(fence_error), .done_valid(gather_done), .done_ready(accept_done), .done_job_id(done_job_id),
        .error_code(gather_error), .read_transactions(), .write_transactions());
endmodule
