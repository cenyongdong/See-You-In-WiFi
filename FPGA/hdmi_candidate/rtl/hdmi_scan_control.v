// Memory-clock owner of frame addresses. CSR uses the mailbox's atomic command
// interface, not direct asynchronous register wires. All reset domains must be
// reset together with the AXI subsystem; a local reset is not a release fence.
module hdmi_scan_control
    #(parameter integer FRAME_WORDS = 518400,
        parameter [31 : 0] DMA_BASE = 32'd0,
        parameter [31 : 0] DMA_LIMIT = 32'd0)
    (input wire clk,
        input wire resetn,
        input wire clock_locked,
        input wire pixel_frame_toggle,
        input wire sink_fault,
        input wire cmd_valid,
        output wire cmd_ready,
        input wire [71 : 0] command,
        output wire [159 : 0] response,
        output wire request_valid,
        input wire request_ready,
        output wire [31 : 0] request_addr,
        output wire [7 : 0] request_beats,
        input wire reader_busy,
        input wire reader_done,
        input wire reader_error,
        output wire reader_stop,
        output wire reader_clear_error,
        output wire safe_idle,
        output wire display_running,
        output reg [31 : 0] accepted_id,
        output reg [31 : 0] accepted_addr,
        output reg [31 : 0] stopped_id,
        output reg [31 : 0] faults);
    localparam [3 : 0] SNAPSHOT = 0, START = 1, FLIP = 2, STOP = 3, CLEAR = 4;
    (* ASYNC_REG = "TRUE" *) reg [1 : 0] locked_sync;
    (* ASYNC_REG = "TRUE" *) reg [2 : 0] frame_sync;
    (* ASYNC_REG = "TRUE" *) reg [1 : 0] sink_sync;
    reg frame_seen, running, stopping, frame_active, waiting, pending_valid, have_current;
    reg [31 : 0] pending_addr, pending_id, next_addr, words_left, stop_tag;
    reg stop_tag_pending;
    wire [3 : 0] op = command[71 : 68];
    wire [31 : 0] id = command[63 : 32], addr = command[31 : 0];
    wire frame_event = frame_sync[2] != frame_seen;
    wire address_ok = addr[5 : 0] == 0 && addr >= DMA_BASE &&
             ({1'b0, addr} + FRAME_WORDS * 8) <= {1'b0, DMA_LIMIT} && DMA_LIMIT > DMA_BASE;
    wire command_ok = command[67 : 64] == 0 &&
             (op == SNAPSHOT || op == STOP || (op == CLEAR && safe_idle) ||
                 (op == START && safe_idle && locked_sync[1] && !sink_sync[1] && faults == 0 && address_ok) ||
                 (op == FLIP && running && !stopping && !pending_valid && address_ok));
    wire [31 : 0] status = {23'd0, have_current, stopping, locked_sync[1], waiting, pending_valid,
                      frame_active, reader_busy, running, safe_idle};
    assign cmd_ready = 1'b1;
    // A command response acknowledges queuing, not frame adoption or safe stop.
    // SNAPSHOT returns an atomic copy, stable on the source side until replaced.
    assign response = {faults, accepted_id, accepted_addr, stopped_id,
               (status | (command_ok ? 32'd0 : 32'h80000000))};
    assign request_valid = running && frame_active && !stopping && !waiting && faults == 0 &&
               words_left != 0 && locked_sync[1];
    assign request_addr = next_addr;
    // Keep the public 64-byte frame alignment contract. A 16-beat burst
    // starting 64 bytes before a page boundary must be split, not rejected.
    wire [9 : 0] words_to_page = 10'd512 - {1'b0, next_addr[11 : 3]};
    wire [7 : 0] page_burst = words_to_page < 16 ? words_to_page[7 : 0] : 8'd16;
    assign request_beats = words_left < page_burst ? words_left[7 : 0] : page_burst;
    assign reader_stop = stopping || !locked_sync[1];
    assign reader_clear_error = cmd_valid && command_ok && op == CLEAR;
    assign safe_idle = stopping && !running && !frame_active && !waiting && !reader_busy;
    assign display_running = running && !stopping;
    always @(posedge clk or negedge resetn) begin
        if (!resetn) begin
            locked_sync <= 0;
            frame_sync <= 0;
            frame_seen <= 0;
            sink_sync <= 0;
            running <= 0;
            stopping <= 1;
            frame_active <= 0;
            waiting <= 0;
            pending_valid <= 0;
            have_current <= 0;
            pending_addr <= 0;
            pending_id <= 0;
            next_addr <= 0;
            words_left <= 0;
            accepted_id <= 0;
            accepted_addr <= 0;
            stopped_id <= 0;
            faults <= 0;
            stop_tag <= 0;
            stop_tag_pending <= 0;
        end else begin
            locked_sync <= {locked_sync[0], clock_locked};
            frame_sync <= {frame_sync[1 : 0], pixel_frame_toggle};
            sink_sync <= {sink_sync[0], sink_fault};
            frame_seen <= frame_sync[2];
            if (request_valid && request_ready) begin
                waiting <= 1;
                words_left <= words_left - request_beats;
                next_addr <= next_addr + ({24'd0, request_beats} << 3);
            end
            if (reader_done) begin
                waiting <= 0;
                if (words_left == 0)
                    frame_active <= 0;
            end
            if (frame_event && running && !stopping) begin
                if (frame_active || reader_busy || waiting) begin
                    // No address replacement while an older frame can still
                    // issue/complete reads. Report overrun and enter safe stop.
                    faults[2] <= 1;
                    stopping <= 1;
                    running <= 0;
                    frame_active <= 0;
                    pending_valid <= 0;
                end else if (pending_valid || have_current) begin
                    if (pending_valid) begin
                        accepted_addr <= pending_addr;
                        accepted_id <= pending_id;
                        next_addr <= pending_addr;
                        pending_valid <= 0;
                        have_current <= 1;
                    end else
                        next_addr <= accepted_addr;
                    words_left <= FRAME_WORDS;
                    frame_active <= 1;
                end
            end
            if (stop_tag_pending && safe_idle) begin
                stopped_id <= stop_tag;
                stop_tag_pending <= 0;
            end
            if (cmd_valid && command_ok) begin
                case (op)
                    START: begin
                        running <= 1;
                        stopping <= 0;
                        pending_valid <= 1;
                        pending_addr <= addr;
                        pending_id <= id;
                    end
                    FLIP: begin
                        pending_addr <= addr;
                        pending_id <= id;
                        pending_valid <= 1;
                    end
                    STOP: begin
                        running <= 0;
                        stopping <= 1;
                        frame_active <= 0;
                        pending_valid <= 0;
                        stop_tag <= id;
                        stop_tag_pending <= 1;
                    end
                    CLEAR:
                        faults <= 0;
                    default: begin
                    end
                endcase
            end
            // Stop is independent of the pixel clock: outstanding accepted AXI
            // responses are discarded by the read master, even if FIFO is full.
            if ((!locked_sync[1] && running) || (reader_error && !(cmd_valid && command_ok && op == CLEAR)) ||
                (sink_sync[1] && running)) begin
                if (!locked_sync[1])
                    faults[0] <= 1;
                if (reader_error)
                    faults[1] <= 1;
                if (sink_sync[1] && running)
                    faults[3] <= 1;
                stopping <= 1;
                running <= 0;
                frame_active <= 0;
                pending_valid <= 0;
                // A locally rejected request never asserted ARVALID. The read
                // master's idle state proves there is no outstanding bus read.
                if (reader_error && !reader_busy)
                    waiting <= 0;
            end
        end
    end
endmodule
