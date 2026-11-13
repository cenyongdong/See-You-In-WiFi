// Four recent destination lines combine byte enables before external writes.
// This halves C16/FP16 writes for the common 42-channel, even-K layout. A fence
// first drains every dirty line, then waits for the downstream visibility ACK.
module write_coalescer #(
    parameter integer LINES = 4
) (
    input logic clk, rst_n,
    input logic [31:0] write_address,
    input logic [511:0] write_data,
    input logic [63:0] write_enable,
    input logic write_valid,
    output logic write_ready,
    input logic fence_valid,
    output logic fence_ready,
    input logic [63:0] fence_job_id,
    output logic fence_response_valid,
    input logic fence_response_ready,
    output logic [63:0] fence_response_job_id,
    output logic fence_error,
    output logic [31:0] downstream_write_address,
    output logic [511:0] downstream_write_data,
    output logic [63:0] downstream_write_enable,
    output logic downstream_write_valid,
    input logic downstream_write_ready,
    output logic downstream_fence_valid,
    input logic downstream_fence_ready,
    output logic [63:0] downstream_fence_job_id,
    input logic downstream_fence_response_valid,
    output logic downstream_fence_response_ready,
    input logic [63:0] downstream_fence_response_job_id,
    input logic downstream_fence_error
);
    localparam integer SLOT_BITS = LINES > 1 ? $clog2(LINES) : 1;
    typedef enum logic [2:0] {ACCEPT, EVICT, FLUSH_PICK, FLUSH_SEND, FENCE_SEND, FENCE_WAIT} state_t;
    state_t state;
    logic [31:0] addresses [0:LINES-1];
    logic [511:0] data [0:LINES-1];
    logic [63:0] enables [0:LINES-1];
    logic [SLOT_BITS-1:0] victim, sending;
    logic [63:0] active_job;
    integer slot, first_dirty, first_full, i;
    logic found_hit;

    always_comb begin
        slot = -1; first_dirty = -1; first_full = -1; found_hit = 0;
        for (integer line = 0; line < LINES; line = line + 1) begin
            if (enables[line] != 0 && addresses[line] == write_address) begin
                slot = line; found_hit = 1;
            end
            if (first_dirty < 0 && enables[line] != 0) first_dirty = line;
            if (first_full < 0 && enables[line] == 64'hffffffffffffffff) first_full = line;
        end
        if (!found_hit)
            for (integer line = 0; line < LINES; line = line + 1)
                if (slot < 0 && enables[line] == 0) slot = line;
    end
    assign write_ready = state == ACCEPT && slot >= 0 && !fence_valid;
    assign fence_ready = state == ACCEPT;
    assign downstream_write_valid = state == EVICT || state == FLUSH_SEND;
    assign downstream_write_address = addresses[sending];
    assign downstream_write_data = data[sending];
    assign downstream_write_enable = enables[sending];
    assign downstream_fence_valid = state == FENCE_SEND;
    assign downstream_fence_job_id = active_job;
    assign fence_response_valid = state == FENCE_WAIT && downstream_fence_response_valid;
    assign downstream_fence_response_ready = state == FENCE_WAIT && fence_response_ready;
    assign fence_response_job_id = downstream_fence_response_job_id;
    assign fence_error = downstream_fence_error;

    // Payload RAM has no reset; only byte-valid masks control its visibility.
    always_ff @(posedge clk) begin
        if (rst_n && write_valid && write_ready) begin
            addresses[slot] <= write_address;
            for (integer lane = 0; lane < 64; lane = lane + 1)
                if (write_enable[lane]) data[slot][lane*8 +: 8] <= write_data[lane*8 +: 8];
        end
    end
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= ACCEPT; victim <= 0; sending <= 0; active_job <= 0;
            for (i = 0; i < LINES; i = i + 1) enables[i] <= 0;
        end else begin
            case (state)
                ACCEPT: begin
                    if (fence_valid) begin
                        active_job <= fence_job_id;
                        state <= FLUSH_PICK;
                    end else if (write_valid) begin
                        if (slot >= 0) enables[slot] <= enables[slot] | write_enable;
                        else begin
                            sending <= first_full >= 0 ? first_full : victim;
                            state <= EVICT;
                        end
                    end
                end
                EVICT: if (downstream_write_ready) begin
                    enables[sending] <= 0;
                    victim <= victim == LINES - 1 ? 0 : victim + 1;
                    state <= ACCEPT;
                end
                FLUSH_PICK: begin
                    if (first_dirty < 0) state <= FENCE_SEND;
                    else begin sending <= first_dirty; state <= FLUSH_SEND; end
                end
                FLUSH_SEND: if (downstream_write_ready) begin
                    enables[sending] <= 0;
                    state <= FLUSH_PICK;
                end
                FENCE_SEND: if (downstream_fence_ready) state <= FENCE_WAIT;
                FENCE_WAIT: if (fence_response_valid && fence_response_ready &&
                               fence_response_job_id == active_job) state <= ACCEPT;
                default: state <= ACCEPT;
            endcase
        end
    end
endmodule
