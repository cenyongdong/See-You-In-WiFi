// Indexed FP16/FP32 payload copy through a 64-byte memory port. The default
// preserves bits; the explicit FP16 compatibility variant normalizes zeros.
// WRITE ready means acceptance only. DONE requires a matching visibility fence.
// The board adapter must implement that fence; a ready bit or delay is invalid.
module gather_engine #(parameter integer FP16_FLUSH_TO_POSITIVE_ZERO = 0) (
    input logic clk, rst_n,
    input logic abort_job,
    input logic start_valid,
    output logic start_ready,
    input logic [63:0] job_id,
    input logic [31:0] input_count, keep_count, channels,
    input logic [2:0] element_bytes,
    input logic source_blocked16, destination_blocked16,
    input logic [31:0] source_base, source_bytes, source_row_stride, source_block_stride,
    input logic [31:0] destination_base, destination_bytes, destination_row_stride, destination_block_stride,
    input logic [63:0] index_data,
    input logic index_valid,
    output logic index_ready,

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
    typedef enum logic [3:0] {
        IDLE, GET_INDEX, ELEMENT, READ_REQUEST, READ_WAIT, WRITE_REQUEST,
        DRAIN_INDICES, FENCE_REQUEST, FENCE_WAIT, DONE, ROW_ADDRESS
    } state_t;
    state_t state, after_write;
    logic [63:0] active_job;
    logic [31:0] n, k, c, column_limit, accepted_indices, column;
    logic [2:0] bytes_per_element;
    logic src_blocked, dst_blocked;
    logic [31:0] src_base, src_size, src_row, src_block;
    logic [31:0] dst_base, dst_size, dst_row, dst_block;
    logic [511:0] cached_read, pending_write;
    logic cache_valid;
    logic abort_pending;
    logic [31:0] cached_address, pending_read_address, pending_write_address;
    logic [63:0] pending_enable;

    // Compute one source row product per selected row. Channel addresses then
    // advance by addition; no wide multiplier sits in the per-element path.
    logic [63:0] src_position, dst_position, src_row_product;
    logic [63:0] src_group_start, dst_group_start, next_destination_row;
    logic [63:0] src_end, dst_end;
    logic [63:0] required_src_row, required_dst_row, required_src_block, required_dst_block;
    logic [5:0] src_lane, dst_lane;
    logic [31:0] element;
    logic padding;
    always_comb begin
        src_end = {32'd0, src_base} + {32'd0, src_size};
        dst_end = {32'd0, dst_base} + {32'd0, dst_size};
        // Canonical dense and C16 layouts cover the original graph. Arbitrary
        // strides are rejected, preventing overlapping rows/channel groups.
        required_src_row = source_blocked16 ? 64'd16 : {32'd0, channels};
        required_dst_row = destination_blocked16 ? 64'd16 : {32'd0, channels};
        required_src_row = required_src_row << (element_bytes == 4 ? 2 : 1);
        required_dst_row = required_dst_row << (element_bytes == 4 ? 2 : 1);
        required_src_block = {32'd0, input_count} << (element_bytes == 4 ? 6 : 5);
        required_dst_block = {32'd0, keep_count} << (element_bytes == 4 ? 6 : 5);
        src_lane = src_position[5:0];
        dst_lane = dst_position[5:0];
        padding = column >= c;
        element = 0;
        if (!padding) begin
            if (bytes_per_element == 2) element[15:0] = cached_read[src_lane * 8 +: 16];
            else element = cached_read[src_lane * 8 +: 32];
        end
        // Only logical FP16 payload elements use this opt-in format policy.
        // Packed run records, indices and FP32 data must remain bit-preserving.
        if (FP16_FLUSH_TO_POSITIVE_ZERO && bytes_per_element == 2 && element[14:10] == 0)
            element = 0;
    end

    assign start_ready = state == IDLE;
    assign index_ready = state == GET_INDEX || (state == DRAIN_INDICES && accepted_indices < k);
    assign read_address = pending_read_address;
    assign read_valid = state == READ_REQUEST;
    assign read_response_ready = state == READ_WAIT;
    assign write_address = pending_write_address;
    assign write_data = pending_write;
    assign write_enable = pending_enable;
    assign write_valid = state == WRITE_REQUEST;
    assign fence_valid = state == FENCE_REQUEST;
    assign fence_job_id = active_job;
    assign fence_response_ready = state == FENCE_WAIT;
    assign done_valid = state == DONE;
    assign done_job_id = active_job;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE; after_write <= ELEMENT;
            active_job <= 0;
            n <= 0; k <= 0; c <= 0; column_limit <= 0;
            accepted_indices <= 0; column <= 0; bytes_per_element <= 0;
            src_blocked <= 0; dst_blocked <= 0;
            src_base <= 0; src_size <= 0; src_row <= 0; src_block <= 0;
            dst_base <= 0; dst_size <= 0; dst_row <= 0; dst_block <= 0;
            cache_valid <= 0; cached_read <= 0; cached_address <= 0;
            abort_pending <= 0;
            pending_read_address <= 0; pending_write_address <= 0;
            pending_write <= 0; pending_enable <= 0;
            src_position <= 0; dst_position <= 0; src_row_product <= 0;
            src_group_start <= 0; dst_group_start <= 0; next_destination_row <= 0;
            error_code <= 0; read_transactions <= 0; write_transactions <= 0;
        end else begin
            // Abort never withdraws an accepted/presented memory request. A
            // read response or write handshake is drained before fencing.
            if (abort_job && state != IDLE && state != DONE) begin
                abort_pending <= 1;
                if (error_code == 0) error_code <= 8;
            end
            case (state)
                IDLE: if (start_valid) begin
                    active_job <= job_id; n <= input_count; k <= keep_count; c <= channels;
                    column_limit <= destination_blocked16 ? (channels + 15) & 32'hfffffff0 : channels;
                    bytes_per_element <= element_bytes;
                    src_blocked <= source_blocked16; dst_blocked <= destination_blocked16;
                    src_base <= source_base; src_size <= source_bytes;
                    src_row <= source_row_stride; src_block <= source_block_stride;
                    dst_base <= destination_base; dst_size <= destination_bytes;
                    dst_row <= destination_row_stride; dst_block <= destination_block_stride;
                    next_destination_row <= {32'd0, destination_base};
                    accepted_indices <= 0; column <= 0; cache_valid <= 0;
                    pending_enable <= 0; pending_write <= 0;
                    error_code <= 0; read_transactions <= 0; write_transactions <= 0;
                    abort_pending <= 0;
                    // Allocations include full cache lines; subword writes use enables.
                    if (input_count == 0 || keep_count == 0 || keep_count > input_count ||
                        channels == 0 || channels > 32'hfffffff0 ||
                        (element_bytes != 2 && element_bytes != 4) ||
                        source_base[5:0] != 0 || destination_base[5:0] != 0 ||
                        source_bytes == 0 || destination_bytes == 0 ||
                        source_bytes[5:0] != 0 || destination_bytes[5:0] != 0 ||
                        {32'd0, source_row_stride} != required_src_row ||
                        {32'd0, destination_row_stride} != required_dst_row ||
                        (source_blocked16 && {32'd0, source_block_stride} != required_src_block) ||
                        (destination_blocked16 && {32'd0, destination_block_stride} != required_dst_block) ||
                        ({1'b0, source_base} + {1'b0, source_bytes}) > 33'h100000000 ||
                        ({1'b0, destination_base} + {1'b0, destination_bytes}) > 33'h100000000 ||
                        (({1'b0, source_base} < ({1'b0, destination_base} + {1'b0, destination_bytes})) &&
                         ({1'b0, destination_base} < ({1'b0, source_base} + {1'b0, source_bytes})))) begin
                        error_code <= 1;
                        state <= DONE; // No memory request was issued for invalid configuration.
                    end else state <= GET_INDEX;
                end
                GET_INDEX: if (abort_pending || abort_job) begin
                    accepted_indices <= k; pending_enable <= 0; state <= FENCE_REQUEST;
                end else if (index_valid) begin
                    accepted_indices <= accepted_indices + 1;
                    src_row_product <= {32'd0, index_data[31:0]} * {32'd0, src_row};
                    column <= 0;
                    if (index_data >= {32'd0, n}) begin
                        error_code <= 3;
                        pending_enable <= 0;
                        state <= DRAIN_INDICES;
                    end else state <= ROW_ADDRESS;
                end
                ROW_ADDRESS: begin
                    src_position <= {32'd0, src_base} + src_row_product;
                    src_group_start <= {32'd0, src_base} + src_row_product;
                    dst_position <= next_destination_row;
                    dst_group_start <= next_destination_row;
                    next_destination_row <= next_destination_row + {32'd0, dst_row};
                    state <= ELEMENT;
                end
                ELEMENT: begin
                    if (abort_pending || abort_job) begin
                        accepted_indices <= k; pending_enable <= 0; state <= FENCE_REQUEST;
                    end else if (dst_position[63:32] != 0 || dst_position + bytes_per_element > dst_end ||
                        (dst_lane & (bytes_per_element - 1)) != 0 ||
                        (!padding && (src_position[63:32] != 0 ||
                         src_position + bytes_per_element > src_end ||
                         (src_lane & (bytes_per_element - 1)) != 0))) begin
                        error_code <= 4;
                        pending_enable <= 0;
                        state <= DRAIN_INDICES;
                    end else if (pending_enable != 0 &&
                                 pending_write_address != {dst_position[31:6], 6'd0}) begin
                        after_write <= ELEMENT;
                        state <= WRITE_REQUEST;
                    end else if (!padding && (!cache_valid || cached_address != {src_position[31:6], 6'd0})) begin
                        pending_read_address <= {src_position[31:6], 6'd0};
                        state <= READ_REQUEST;
                    end else begin
                        pending_write_address <= {dst_position[31:6], 6'd0};
                        if (bytes_per_element == 2) begin
                            pending_write[dst_lane * 8 +: 16] <= element[15:0];
                            pending_enable <= pending_enable | (64'h3 << dst_lane);
                        end else begin
                            pending_write[dst_lane * 8 +: 32] <= element;
                            pending_enable <= pending_enable | (64'hf << dst_lane);
                        end
                        column <= column + 1;
                        if (src_blocked && column[3:0] == 15) begin
                            src_position <= src_group_start + {32'd0, src_block};
                            src_group_start <= src_group_start + {32'd0, src_block};
                        end else src_position <= src_position + bytes_per_element;
                        if (dst_blocked && column[3:0] == 15) begin
                            dst_position <= dst_group_start + {32'd0, dst_block};
                            dst_group_start <= dst_group_start + {32'd0, dst_block};
                        end else dst_position <= dst_position + bytes_per_element;
                        if (column + 1 == column_limit) begin
                            if (accepted_indices == k) begin
                                after_write <= FENCE_REQUEST;
                                state <= WRITE_REQUEST;
                            end else state <= GET_INDEX;
                        end
                    end
                end
                READ_REQUEST: if (read_ready) begin
                    read_transactions <= read_transactions + 1;
                    state <= READ_WAIT;
                end
                READ_WAIT: if (read_response_valid) begin
                    if (read_error) begin
                        error_code <= 5;
                        pending_enable <= 0;
                        state <= DRAIN_INDICES;
                    end else begin
                        cached_read <= read_data;
                        cached_address <= pending_read_address;
                        cache_valid <= 1;
                        state <= ELEMENT;
                    end
                end
                WRITE_REQUEST: if (write_ready) begin
                    write_transactions <= write_transactions + 1;
                    pending_enable <= 0;
                    state <= after_write;
                end
                DRAIN_INDICES: begin
                    if (abort_pending || abort_job) begin accepted_indices <= k; state <= FENCE_REQUEST; end
                    else begin
                        if (index_valid && index_ready) accepted_indices <= accepted_indices + 1;
                        if (accepted_indices == k) state <= FENCE_REQUEST;
                    end
                end
                FENCE_REQUEST: if (fence_ready) state <= FENCE_WAIT;
                FENCE_WAIT: if (fence_response_valid) begin
                    if (fence_response_job_id != active_job) begin
                        if (error_code == 0) error_code <= 6;
                        // Consume a stale response without releasing this job's buffers.
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
