// A bounded sorting tile. Arbitrary external N/K use sorted runs and merge jobs.
// One comparison and at most one record move per clock; no payload sorting.
module topk_tile #(
    parameter integer CAPACITY = 256
) (
    input  logic        clk,
    input  logic        rst_n,
    input  logic        abort_job,
    input  logic        start_valid,
    output logic        start_ready,
    input  logic [31:0] input_count,
    input  logic [31:0] keep_count,
    input  logic [63:0] index_base,
    input  logic [31:0] in_score,
    input  logic        in_valid,
    output logic        in_ready,
    output logic [31:0] out_score,
    output logic [63:0] out_index,
    output logic        out_valid,
    input  logic        out_ready,
    output logic        out_last,
    output logic        done_valid,
    input  logic        done_ready,
    output logic [ 3:0] error_code
);
    import topk_order_pkg::*;
    typedef enum logic [2:0] {IDLE, LOAD, INSERT, EMIT, DRAIN, DONE} state_t;
    state_t state;
    localparam integer INDEX_BITS = CAPACITY > 1 ? $clog2(CAPACITY) : 1;
    // A single addressed read and a reset-free write port infer small LUT RAM.
    // Storing local indices avoids a 64-bit index in every entry. The common
    // base is added only at the output; relative order is unchanged.
    (* ram_style = "distributed" *) logic [31+INDEX_BITS:0] records [0:CAPACITY-1];
    logic [INDEX_BITS-1:0] read_slot, write_slot;
    logic [31+INDEX_BITS:0] read_record, write_record;
    logic write_record_valid;
    logic [31:0] read_score;
    logic [INDEX_BITS-1:0] read_index, pending_index;
    logic [31:0] count, keep, loaded, used, position, emitted;
    logic [63:0] base;
    logic [31:0] pending_score;
    wire [64:0] last_index = {1'b0, index_base} + {33'b0, input_count} - 65'd1;

    assign start_ready = state == IDLE;
    assign in_ready = state == LOAD || state == DRAIN;
    assign out_valid = state == EMIT;
    assign out_score = state == EMIT ? read_score : 32'd0;
    assign out_index = state == EMIT ? base + read_index : 64'd0;
    assign out_last = state == EMIT && emitted + 1 == keep;
    assign done_valid = state == DONE;

    always_comb begin
        if (state == LOAD) read_slot = INDEX_BITS'(keep - 1);
        else if (state == INSERT) read_slot = INDEX_BITS'(position - 1);
        else read_slot = INDEX_BITS'(emitted);
        read_record = records[read_slot];
        {read_score, read_index} = read_record;
        write_slot = INDEX_BITS'(position);
        write_record_valid = state == INSERT && !abort_job;
        if (position > 0 && precedes(pending_score, 64'(pending_index), read_score, 64'(read_index)))
            write_record = read_record;
        else write_record = {pending_score, pending_index};
    end

    always_ff @(posedge clk) begin
        if (write_record_valid) records[write_slot] <= write_record;
    end

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            error_code <= 0;
            count <= 0; keep <= 0; loaded <= 0; used <= 0;
            position <= 0; emitted <= 0; base <= 0;
            pending_score <= 0; pending_index <= 0;
        end else if (abort_job && state != IDLE && state != DONE) begin
            // Local compute abort only: the owner must drain external reads
            // separately and discard any previously accepted output records.
            error_code <= 3;
            state <= DONE;
        end else begin
            case (state)
                IDLE: if (start_valid) begin
                    count <= input_count;
                    keep <= keep_count;
                    base <= index_base;
                    loaded <= 0; used <= 0; emitted <= 0;
                    error_code <= 0;
                    if (input_count == 0 || input_count > CAPACITY ||
                        keep_count == 0 || keep_count > input_count || last_index[64]) begin
                        error_code <= 1;
                        state <= DONE;
                    end else state <= LOAD;
                end
                LOAD: if (in_valid) begin
                    loaded <= loaded + 1;
                    if (!finite_score(in_score)) begin
                        error_code <= 2;
                        state <= loaded + 1 == count ? DONE : DRAIN;
                    end else if (used == keep &&
                                 !precedes(in_score, {32'd0, loaded}, read_score, 64'(read_index))) begin
                        if (loaded + 1 == count) state <= EMIT;
                    end else begin
                        pending_score <= in_score;
                        pending_index <= INDEX_BITS'(loaded);
                        position <= used < keep ? used : keep - 1;
                        state <= INSERT;
                    end
                end
                INSERT: begin
                    if (position > 0 && precedes(pending_score, 64'(pending_index), read_score, 64'(read_index))) begin
                        position <= position - 1;
                    end else begin
                        if (used < keep) used <= used + 1;
                        state <= loaded == count ? EMIT : LOAD;
                    end
                end
                EMIT: if (out_ready) begin
                    if (emitted + 1 == keep) state <= DONE;
                    else emitted <= emitted + 1;
                end
                DRAIN: if (in_valid) begin
                    loaded <= loaded + 1;
                    if (loaded + 1 == count) state <= DONE;
                end
                DONE: if (done_ready) state <= IDLE;
                default: state <= IDLE;
            endcase
        end
    end
endmodule
