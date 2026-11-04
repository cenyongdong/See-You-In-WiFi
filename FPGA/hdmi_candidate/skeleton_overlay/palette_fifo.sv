// Small FWFT distributed FIFO: the regional pixel clock drives only this
// bounded line elasticity, not the full-frame BRAM array. Local synchronous
// vblank clear lasts many clocks in both domains; traffic resumes afterwards.
module palette_fifo
    #(parameter AW = 9)
    (input wire wclk, wresetn, wclear,
        input wire push,
        input wire [3 : 0] data,
        output wire full,
        input wire rclk, rresetn, rclear,
        input wire pop,
        output wire [3 : 0] head,
        output wire empty);
    (* ram_style = "distributed" *) reg [3 : 0] mem[0 : (1 << AW) - 1];
    reg [AW : 0] wbin, wgray, rbin, rgray;
    (* ASYNC_REG = "TRUE" *) reg [AW : 0] rs1, rs2, ws1, ws2;
    wire [AW : 0] wn = wbin + 1'b1, rn = rbin + 1'b1;
    assign full = wgray == {~rs2[AW : AW - 1], rs2[AW - 2 : 0]};
    assign empty = rgray == ws2;
    assign head = mem[rbin[AW - 1 : 0]];
    always @(posedge wclk)
        if (push && !full && !wclear)
            mem[wbin[AW - 1 : 0]] <= data;
    always @(posedge wclk or negedge wresetn) begin
        if (!wresetn) begin
            wbin <= 0;
            wgray <= 0;
            rs1 <= 0;
            rs2 <= 0;
        end else begin
            rs1 <= rgray;
            rs2 <= rs1;
            if (wclear) begin
                wbin <= 0;
                wgray <= 0;
            end else if (push && !full) begin
                wbin <= wn;
                wgray <= (wn >> 1) ^ wn;
            end
        end
    end
    always @(posedge rclk or negedge rresetn) begin
        if (!rresetn) begin
            rbin <= 0;
            rgray <= 0;
            ws1 <= 0;
            ws2 <= 0;
        end else begin
            ws1 <= wgray;
            ws2 <= ws1;
            if (rclear) begin
                rbin <= 0;
                rgray <= 0;
            end else if (pop && !empty) begin
                rbin <= rn;
                rgray <= (rn >> 1) ^ rn;
            end
        end
    end
endmodule
