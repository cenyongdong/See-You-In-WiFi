// ABI 2.0 command execution. Opcode 0/1 runs a score tile / packed merge;
// opcode 2 consumes the completed run and writes scores, indices and features.
// The command sequencer retains ownership until the selected engine drains.
module command_kernel #(parameter integer FP16_FLUSH_TO_POSITIVE_ZERO = 0) (
    input logic clk, rst_n,
    input logic [31:0] descriptor [0:31],
    input logic start_valid,
    output logic start_ready,
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
    logic active, selected, invalid;
    logic [63:0] active_job;
    wire accept_start = start_valid && start_ready;
    wire accept_done = done_valid && done_ready;
    wire [1:0] ready, done, rd_valid, rd_response_ready, wr_valid, fn_valid, fn_response_ready;
    wire [1:0][31:0] rd_address, wr_address;
    wire [1:0][511:0] wr_data;
    wire [1:0][63:0] wr_enable, fn_job, completed_job;
    wire [1:0][3:0] error;
    wire [1:0] running = active && !invalid ? (selected ? 2'b10 : 2'b01) : 2'b00;
    assign start_ready = !active && (&ready);
    assign done_valid = active && (invalid || done[selected]);
    assign done_job_id = invalid ? active_job : completed_job[selected];
    assign error_code = invalid ? 4'd1 : error[selected];
    assign read_address = rd_address[selected];
    assign read_valid = (|running) && rd_valid[selected];
    assign read_response_ready = (|running) && rd_response_ready[selected];
    assign write_address = wr_address[selected];
    assign write_data = wr_data[selected];
    assign write_enable = wr_enable[selected];
    assign write_valid = (|running) && wr_valid[selected];
    assign fence_valid = (|running) && fn_valid[selected];
    assign fence_job_id = fn_job[selected];
    assign fence_response_ready = (|running) && fn_response_ready[selected];
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            active <= 0; selected <= 0; invalid <= 0; active_job <= 0;
            read_transactions <= 0; write_transactions <= 0;
        end else begin
            if (accept_start) begin
                active <= 1; selected <= descriptor[22] == 2; invalid <= descriptor[22] > 2;
                active_job <= {descriptor[1], descriptor[0]};
                read_transactions <= 0; write_transactions <= 0;
            end
            if (accept_done) active <= 0;
            if (read_valid && read_ready) read_transactions <= read_transactions + 1;
            if (write_valid && write_ready) write_transactions <= write_transactions + 1;
        end
    end
    memory_stage #(.FP16_FLUSH_TO_POSITIVE_ZERO(FP16_FLUSH_TO_POSITIVE_ZERO)) records(
        .clk(clk), .rst_n(rst_n), .operation_merge(descriptor[22] == 1),
        .start_valid(accept_start && descriptor[22] < 2), .start_ready(ready[0]),
        .job_id({descriptor[1], descriptor[0]}), .index_limit({descriptor[29], descriptor[28]}),
        .index_base({descriptor[27], descriptor[26]}), .score_element_bytes(descriptor[7][2:0]),
        .left_base(descriptor[5]), .left_bytes(descriptor[6]), .left_count(descriptor[2]),
        .right_base(descriptor[23]), .right_bytes(descriptor[24]), .right_count(descriptor[25]),
        .destination_base(descriptor[14]), .destination_bytes(descriptor[15]), .keep_count(descriptor[3]),
        .read_address(rd_address[0]), .read_valid(rd_valid[0]), .read_ready(running[0] && read_ready), .read_data(read_data),
        .read_response_valid(running[0] && read_response_valid), .read_response_ready(rd_response_ready[0]), .read_error(read_error),
        .write_address(wr_address[0]), .write_data(wr_data[0]), .write_enable(wr_enable[0]),
        .write_valid(wr_valid[0]), .write_ready(running[0] && write_ready),
        .fence_valid(fn_valid[0]), .fence_ready(running[0] && fence_ready), .fence_job_id(fn_job[0]),
        .fence_response_valid(running[0] && fence_response_valid), .fence_response_ready(fn_response_ready[0]),
        .fence_response_job_id(fence_response_job_id), .fence_error(fence_error),
        .done_valid(done[0]), .done_ready(accept_done && !selected && !invalid), .done_job_id(completed_job[0]), .error_code(error[0]));
    topk_gather_kernel #(.INPUT_IS_SORTED_RUN(1),
                        .FP16_FLUSH_TO_POSITIVE_ZERO(FP16_FLUSH_TO_POSITIVE_ZERO)) final_gather(
        .clk(clk), .rst_n(rst_n), .start_valid(accept_start && descriptor[22] == 2), .start_ready(ready[1]),
        .job_id({descriptor[1], descriptor[0]}), .input_count(descriptor[2]), .keep_count(descriptor[3]),
        .channels(descriptor[4]), .score_base(descriptor[5]), .score_bytes(descriptor[6]), .score_element_bytes(3'd0),
        .element_bytes(descriptor[8][2:0]), .source_blocked16(descriptor[9][0]), .destination_blocked16(descriptor[9][1]),
        .source_base(descriptor[10]), .source_bytes(descriptor[11]),
        .source_row_stride(descriptor[12]), .source_block_stride(descriptor[13]),
        .destination_base(descriptor[14]), .destination_bytes(descriptor[15]),
        .destination_row_stride(descriptor[16]), .destination_block_stride(descriptor[17]),
        .selected_score_base(descriptor[18]), .selected_score_bytes(descriptor[19]),
        .selected_index_base(descriptor[20]), .selected_index_bytes(descriptor[21]),
        .read_address(rd_address[1]), .read_valid(rd_valid[1]), .read_ready(running[1] && read_ready), .read_data(read_data),
        .read_response_valid(running[1] && read_response_valid), .read_response_ready(rd_response_ready[1]), .read_error(read_error),
        .write_address(wr_address[1]), .write_data(wr_data[1]), .write_enable(wr_enable[1]),
        .write_valid(wr_valid[1]), .write_ready(running[1] && write_ready),
        .fence_valid(fn_valid[1]), .fence_ready(running[1] && fence_ready), .fence_job_id(fn_job[1]),
        .fence_response_valid(running[1] && fence_response_valid), .fence_response_ready(fn_response_ready[1]),
        .fence_response_job_id(fence_response_job_id), .fence_error(fence_error),
        .done_valid(done[1]), .done_ready(accept_done && selected && !invalid), .done_job_id(completed_job[1]), .error_code(error[1]),
        .read_transactions(), .write_transactions());
endmodule
