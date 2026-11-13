// Read a contiguous C1 score vector from 64-byte DDR lines. The producer's
// completion and allocation ownership must be established before START.
// Default FP16 expansion is exact. The explicit old-model compatibility
// variant maps exponent-zero FP16 (including -0) to +0 before sorting.
module score_reader #(parameter integer FP16_FLUSH_TO_POSITIVE_ZERO = 0) (
    input logic clk, rst_n,
    input logic start_valid,
    output logic start_ready,
    input logic [31:0] source_base, source_bytes, input_count,
    input logic [2:0] element_bytes,
    output logic [31:0] read_address,
    output logic read_valid,
    input logic read_ready,
    input logic [511:0] read_data,
    input logic read_response_valid,
    output logic read_response_ready,
    input logic read_error,
    output logic [31:0] score_data,
    output logic score_valid,
    input logic score_ready,
    output logic score_last,
    output logic done_valid,
    input logic done_ready,
    output logic [3:0] error_code
);
    typedef enum logic [2:0] {IDLE, VALIDATE, REQUEST, RESPONSE, EMIT, DONE} state_t;
    state_t state;
    logic [511:0] line_data;
    logic [31:0] remaining, allocation_bytes;
    logic [5:0] lane;
    logic [2:0] bytes_per_element;
    logic [63:0] requested_bytes;

    function automatic logic [31:0] expand_half(input logic [15:0] half);
        logic [7:0] exponent;
        logic [22:0] fraction;
        integer leading;
        begin
            exponent = 0; fraction = 0; leading = 0;
            if (half[14:10] == 31) begin
                exponent = 255; fraction = {half[9:0], 13'd0};
            end else if (half[14:10] != 0) begin
                exponent = {3'd0, half[14:10]} + 8'd112;
                fraction = {half[9:0], 13'd0};
            end else if (half[9:0] != 0) begin
                for (integer bit_number = 0; bit_number < 10; bit_number = bit_number + 1)
                    if (half[bit_number]) leading = bit_number;
                exponent = 103 + leading;
                fraction = {13'd0, half[9:0]} << (23 - leading);
            end
            expand_half = {half[15], exponent, fraction};
            if (FP16_FLUSH_TO_POSITIVE_ZERO && half[14:10] == 0) expand_half = 0;
        end
    endfunction

    always_comb begin
        requested_bytes = {32'd0, remaining} << (bytes_per_element == 4 ? 2 : 1);
        score_data = bytes_per_element == 2 ? expand_half(line_data[lane*8 +: 16]) :
                                             line_data[lane*8 +: 32];
    end
    assign start_ready = state == IDLE;
    assign read_valid = state == REQUEST;
    assign read_response_ready = state == RESPONSE;
    assign score_valid = state == EMIT;
    assign score_last = score_valid && remaining == 1;
    assign done_valid = state == DONE;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE; read_address <= 0; line_data <= 0;
            remaining <= 0; allocation_bytes <= 0; lane <= 0; bytes_per_element <= 0; error_code <= 0;
        end else begin
            case (state)
                IDLE: if (start_valid) begin
                    remaining <= input_count; bytes_per_element <= element_bytes;
                    read_address <= source_base; lane <= 0; error_code <= 0;
                    allocation_bytes <= source_bytes;
                    // Break the outer alias/shape-check path before the local
                    // allocation arithmetic. No DDR request precedes VALIDATE.
                    state <= VALIDATE;
                end
                VALIDATE: begin
                    if (!remaining || (bytes_per_element != 2 && bytes_per_element != 4) ||
                        read_address[5:0] != 0 || allocation_bytes[5:0] != 0 || !allocation_bytes ||
                        requested_bytes > {32'd0, allocation_bytes} ||
                        {1'b0, read_address} + {1'b0, allocation_bytes} > 33'h100000000) begin
                        error_code <= 1; state <= DONE;
                    end else state <= REQUEST;
                end
                REQUEST: if (read_ready) state <= RESPONSE;
                RESPONSE: if (read_response_valid) begin
                    if (read_error) begin error_code <= 5; state <= DONE; end
                    else begin line_data <= read_data; state <= EMIT; end
                end
                EMIT: if (score_ready) begin
                    remaining <= remaining - 1;
                    if (remaining == 1) state <= DONE;
                    else if ({1'b0, lane} + bytes_per_element == 64) begin
                        lane <= 0; read_address <= read_address + 64; state <= REQUEST;
                    end else lane <= lane + bytes_per_element;
                end
                DONE: if (done_ready) state <= IDLE;
                default: state <= IDLE;
            endcase
        end
    end
endmodule
