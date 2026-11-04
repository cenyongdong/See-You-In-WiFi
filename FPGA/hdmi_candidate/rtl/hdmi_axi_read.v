// One outstanding, 64-bit, INCR AXI read burst. No write channel ownership.
// Stop never withdraws an asserted ARVALID. Accepted reads are drained even
// when the pixel clock stops or the consumer FIFO is full.
module hdmi_axi_read
    (input wire clk,
        input wire resetn,
        input wire request_valid,
        output wire request_ready,
        input wire [31 : 0] request_addr,
        input wire [7 : 0] request_beats,
        input wire stop,
        input wire clear_error,
        output wire busy,
        output reg done,
        output reg error,
        output wire fifo_push,
        output wire [63 : 0] fifo_data,
        input wire fifo_ready,
        output reg [31 : 0] araddr,
        output reg [7 : 0] arlen,
        output wire [2 : 0] arsize,
        output wire [1 : 0] arburst,
        output wire arvalid,
        input wire arready,
        input wire [63 : 0] rdata,
        input wire [1 : 0] rresp,
        input wire rlast,
        input wire rvalid,
        output wire rready);
    localparam IDLE = 2'd0, ADDRESS = 2'd1, DATA = 2'd2;
    reg [1 : 0] state;
    reg [8 : 0] received, expected;
    reg discard;
    wire drop_data = stop || discard || error;
    // Valid aligned bursts are at most 128 bytes. Only the last 128-byte
    // block of a 4KiB page can cross its end; compare in beats there.
    wire [4 : 0] last_block_end = {1'b0, request_addr[6 : 3]} + request_beats[4 : 0];
    wire crosses_4k = (&request_addr[11 : 7]) && (last_block_end > 5'd16);
    wire invalid_request = request_beats == 0 || request_beats > 16 || request_addr[2 : 0] != 0 || crosses_4k;
    assign request_ready = state == IDLE && !stop && !error;
    assign busy = state != IDLE;
    assign arvalid = state == ADDRESS;
    assign arsize = 3'd3;
    assign arburst = 2'b01;
    assign rready = state == DATA && (drop_data || fifo_ready);
    // FIFO commits and transaction completion use the same AXI handshake.
    assign fifo_push = state == DATA && rvalid && rready && !drop_data && rresp == 2'b00;
    assign fifo_data = rdata;
    always @(posedge clk or negedge resetn) begin
        if (!resetn) begin
            state <= IDLE;
            received <= 0;
            expected <= 0;
            araddr <= 0;
            arlen <= 0;
            done <= 0;
            error <= 0;
            discard <= 0;
        end else begin
            done <= 0;
            if (clear_error && state == IDLE)
                error <= 0;
            if (stop && state != IDLE)
                discard <= 1;
            case (state)
                IDLE: begin
                    received <= 0;
                    discard <= 0;
                    if (request_valid && request_ready) begin
                        // This candidate restricts bursts to 1..16 aligned beats,
                        // and never permits an address crossing a 4KiB boundary.
                        if (invalid_request) begin
                            error <= 1;
                        end else begin
                            araddr <= request_addr;
                            arlen <= request_beats - 1'b1;
                            expected <= {1'b0, request_beats};
                            state <= ADDRESS;
                        end
                    end
                end
                ADDRESS:
                    if (arready)
                        state <= DATA;
                DATA:
                    if (rvalid && rready) begin
                        if (received != 9'h1ff)
                            received <= received + 1'b1;
                        if (rresp != 2'b00) begin
                            error <= 1;
                            discard <= 1;
                        end
                        if (rlast) begin
                            if (received + 1'b1 != expected)
                                error <= 1;
                            state <= IDLE;
                            done <= 1;
                        end else if (received + 1'b1 >= expected) begin
                            // A malformed slave may omit RLAST. Keep ownership busy
                            // until an actual last-beat handshake, never fake idle.
                            error <= 1;
                            discard <= 1;
                        end
                    end
                default: begin
                    state <= IDLE;
                    error <= 1;
                end
            endcase
        end
    end
endmodule
