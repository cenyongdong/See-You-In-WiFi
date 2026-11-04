// Dual-clock 64-bit -> four little-endian RGB565 pixels. A word is released
// only after its fourth pixel. Gray pointers cross through two registers;
// implementation constraints must bound pointer-bus skew and synchronizer delay.
// Memory has a synchronous read port with last-lane lookahead, so no bubble is
// inserted between words. Reads while empty are ignored. AW must be >= 2.
module hdmi_stream_fifo
    #(parameter integer AW = 9)
    (input wire resetn,
        input wire wr_clk,
        input wire push,
        input wire [63 : 0] data,
        output wire ready,
        input wire rd_clk,
        input wire pop,
        output wire [15 : 0] pixel,
        output wire empty);
    reg [63 : 0] storage[0 : (1 << AW) - 1];
    reg [AW : 0] wr_bin, wr_gray, rd_bin, rd_gray;
    (* ASYNC_REG = "TRUE" *) reg [AW : 0] rd_sync1, rd_sync2, wr_sync1, wr_sync2;
    (* ASYNC_REG = "TRUE" *) reg [2 : 0] wr_release, rd_release;
    reg [1 : 0] lane;
    reg [63 : 0] word_data;
    wire full = wr_gray == {~rd_sync2[AW : AW - 1], rd_sync2[AW - 2 : 0]};
    assign ready = wr_release[2] && !full;
    assign empty = !rd_release[2] || rd_gray == wr_sync2;
    assign pixel = word_data >> (lane * 16);
    wire advance = pop && !empty && lane == 3;
    wire [AW : 0] next_rd = rd_bin + advance;
    wire [AW : 0] next_wr = wr_bin + 1'b1;
    // Only these release chains receive the cross-domain asynchronous reset.
    // State registers assert asynchronously but release on their OWN clock.
    // Gating ready/empty alone does not synchronize state reset deassertion.
    always @(posedge wr_clk or negedge resetn)
        if (!resetn)
            wr_release <= 0;
        else
            wr_release <= {wr_release[1 : 0], 1'b1};
    always @(posedge rd_clk or negedge resetn)
        if (!resetn)
            rd_release <= 0;
        else
            rd_release <= {rd_release[1 : 0], 1'b1};
    wire wr_resetn = wr_release[2], rd_resetn = rd_release[2];
    // Reading the next word on the final lane makes it available for lane zero.
    always @(posedge rd_clk)
        word_data <= storage[next_rd[AW - 1 : 0]];
    always @(posedge wr_clk)
        if (push && ready)
            storage[wr_bin[AW - 1 : 0]] <= data;
    always @(posedge wr_clk or negedge wr_resetn) begin
        if (!wr_resetn) begin
            wr_bin <= 0;
            wr_gray <= 0;
            rd_sync1 <= 0;
            rd_sync2 <= 0;
        end else begin
            rd_sync1 <= rd_gray;
            rd_sync2 <= rd_sync1;
            if (push && ready) begin
                wr_bin <= next_wr;
                wr_gray <= (next_wr >> 1) ^ next_wr;
            end
        end
    end
    always @(posedge rd_clk or negedge rd_resetn) begin
        if (!rd_resetn) begin
            rd_bin <= 0;
            rd_gray <= 0;
            wr_sync1 <= 0;
            wr_sync2 <= 0;
            lane <= 0;
        end else begin
            wr_sync1 <= wr_gray;
            wr_sync2 <= wr_sync1;
            if (pop && !empty) begin
                lane <= lane + 1'b1;
                if (advance) begin
                    rd_bin <= next_rd;
                    rd_gray <= (next_rd >> 1) ^ next_rd;
                end
            end
        end
    end
endmodule
