// One-shot diagnostic only. Never declares the AXI subsystem recovered.
// No request, reset, DDR write, FIFO push or automatic HDMI START output.
module hp2_startup_drain
    #(parameter integer MAX_BEATS = 256, MAX_CYCLES = 4096, QUIET_CYCLES = 64)
    (input wire clk, ps_resetn, pl_resetn, hp_reset, arm,
        input wire any_request, reader_ready,
        input wire rvalid,
        input wire [4 : 0] rid,
        input wire [1 : 0] rresp,
        input wire rlast,
        output wire drain_ready,
        output wire [31 : 0] status);
    localparam [2 : 0] WAIT = 0, RUN = 1, QUIET = 2, BEAT_LIMIT = 3, TIME_LIMIT = 4, ABORT = 5;
    reg [2 : 0] state = WAIT;
    reg [8 : 0] beats = 0;
    reg [12 : 0] cycles = 0;
    reg [6 : 0] quiet = 0;
    reg saw_last = 0, saw_error = 0, bad_id = 0, late_valid = 0;
    wire released = ps_resetn && pl_resetn && !hp_reset;
    wire collision = any_request || reader_ready;
    wire wrong_id = rvalid && rid != 0;
    assign drain_ready = state == RUN && released && !collision && !wrong_id;
    assign status = {late_valid, 3'd0, bad_id, saw_error, saw_last, cycles, beats, state};
    always @(posedge clk) begin
        // Terminal state persists through subsequent resets; only reconfiguration
        // can arm another experiment. A quiet interval is merely an observation.
        if (state == QUIET && rvalid)
            late_valid <= 1;
        case (state)
            WAIT: begin
                if (collision)
                    state <= ABORT;
                else if (released && arm)
                    state <= RUN;
            end
            RUN: begin
                if (!released || collision || wrong_id) begin
                    state <= ABORT;
                    if (wrong_id)
                        bad_id <= 1;
                end else begin
                    cycles <= cycles + 1'b1;
                    if (rvalid && drain_ready) begin
                        beats <= beats + 1'b1;
                        quiet <= 0;
                        if (rlast)
                            saw_last <= 1;
                        if (rresp != 0)
                            saw_error <= 1;
                        if (beats == MAX_BEATS - 1)
                            state <= BEAT_LIMIT;
                    end else begin
                        quiet <= quiet + 1'b1;
                        if (quiet == QUIET_CYCLES - 1)
                            state <= QUIET;
                    end
                    // Priority after count/quiet handling ensures a finite time budget.
                    if (cycles == MAX_CYCLES - 1)
                        state <= TIME_LIMIT;
                end
            end
            default: begin
            end
        endcase
    end
endmodule
