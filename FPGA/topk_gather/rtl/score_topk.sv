// A complete bounded score-read/sort stage. No CPU score copy is required.
// Read failure aborts only local sorting after the reader has consumed its
// response. DONE waits for both components; resource release is still owned
// by the outer job lifecycle, and output records are provisional until DONE.
module score_topk #(parameter integer FP16_FLUSH_TO_POSITIVE_ZERO = 0) (
    input logic clk, rst_n,
    input logic start_valid,
    output logic start_ready,
    input logic [31:0] source_base, source_bytes, input_count, keep_count,
    input logic [63:0] index_base,
    input logic [2:0] element_bytes,
    output logic [31:0] read_address,
    output logic read_valid,
    input logic read_ready,
    input logic [511:0] read_data,
    input logic read_response_valid,
    output logic read_response_ready,
    input logic read_error,
    output logic [31:0] out_score,
    output logic [63:0] out_index,
    output logic out_valid,
    input logic out_ready,
    output logic out_last,
    output logic done_valid,
    input logic done_ready,
    output logic [3:0] error_code
);
    logic reader_ready, tile_ready, accept_start, accept_done;
    logic reader_done, tile_done, score_valid, score_ready, tile_input_ready;
    logic [31:0] score_data;
    logic [3:0] reader_error, tile_error;
    logic tile_output_valid, abort_tile;
    logic [64:0] last_index;
    logic legal_shape;
    assign last_index = {1'b0, index_base} + {33'd0, input_count} - 65'd1;
    assign legal_shape = input_count > 0 && input_count <= 256 && keep_count > 0 &&
                         keep_count <= input_count && !last_index[64];
    assign start_ready = reader_ready && tile_ready;
    assign accept_start = start_valid && start_ready;
    assign done_valid = reader_done && tile_done;
    assign accept_done = done_valid && done_ready;
    assign abort_tile = reader_done && reader_error != 0 && !tile_done;
    assign score_ready = tile_input_ready || tile_done;
    assign out_valid = tile_output_valid && reader_error == 0;
    assign error_code = reader_error != 0 ? reader_error : tile_error;
    score_reader #(.FP16_FLUSH_TO_POSITIVE_ZERO(FP16_FLUSH_TO_POSITIVE_ZERO)) reader(
        .clk(clk), .rst_n(rst_n), .start_valid(accept_start), .start_ready(reader_ready),
        .source_base(source_base), .source_bytes(source_bytes),
        .input_count(legal_shape ? input_count : 32'd0), .element_bytes(element_bytes),
        .read_address(read_address), .read_valid(read_valid), .read_ready(read_ready),
        .read_data(read_data), .read_response_valid(read_response_valid),
        .read_response_ready(read_response_ready), .read_error(read_error),
        .score_data(score_data), .score_valid(score_valid), .score_ready(score_ready), .score_last(),
        .done_valid(reader_done), .done_ready(accept_done), .error_code(reader_error));
    topk_tile sorter(
        .clk(clk), .rst_n(rst_n), .abort_job(abort_tile), .start_valid(accept_start), .start_ready(tile_ready),
        .input_count(input_count), .keep_count(keep_count), .index_base(index_base),
        .in_score(score_data), .in_valid(score_valid), .in_ready(tile_input_ready),
        .out_score(out_score), .out_index(out_index), .out_valid(tile_output_valid),
        .out_ready(out_ready && reader_error == 0), .out_last(out_last),
        .done_valid(tile_done), .done_ready(accept_done), .error_code(tile_error));
endmodule
