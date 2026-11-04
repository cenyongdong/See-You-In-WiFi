// Free-running positive-polarity 1080p60 raster. STOP changes active RGB to
// black without gating sync or DE. START arms only at the next frame boundary.
// Timing parameters exist for bounded simulation; hardware defaults are fixed.
module hdmi_pixel_scan
    #(parameter integer HS = 44, HB = 148, HA = 1920, HF = 88,
        parameter integer VS = 5, VB = 36, VA = 1080, VF = 4)
    (input wire clk,
        input wire resetn,
        input wire run,
        input wire idle,
        input wire [15 : 0] pixel,
        input wire empty,
        output wire pop,
        output reg frame_toggle,
        output reg underflow,
        output reg hs,
        output reg vs,
        output reg de,
        output reg [23 : 0] rgb);
    localparam integer HT = HS + HB + HA + HF, VT = VS + VB + VA + VF;
    reg [11 : 0] x, y;
    (* ASYNC_REG = "TRUE" *) reg [1 : 0] run_sync, idle_sync;
    reg frame_enabled;
    wire active = x >= HS + HB && x < HS + HB + HA && y >= VS + VB && y < VS + VB + VA;
    assign pop = active && frame_enabled && run_sync[1] && !empty;
    always @(posedge clk or negedge resetn) begin
        if (!resetn) begin
            x <= 0;
            y <= 0;
            run_sync <= 0;
            idle_sync <= 3;
            frame_enabled <= 0;
            frame_toggle <= 0;
            underflow <= 0;
            hs <= 0;
            vs <= 0;
            de <= 0;
            rgb <= 0;
        end else begin
            run_sync <= {run_sync[0], run};
            idle_sync <= {idle_sync[0], idle};
            if (x == HT - 1) begin
                x <= 0;
                if (y == VT - 1)
                    y <= 0;
                else
                    y <= y + 1'b1;
            end else
                x <= x + 1'b1;
            hs <= x < HS;
            vs <= y < VS;
            de <= active;
            rgb <= 0;
            if (idle_sync[1])
                underflow <= 0;
            if (!run_sync[1])
                frame_enabled <= 0;
            if (x == 0 && y == 0) begin
                frame_enabled <= run_sync[1];
                if (run_sync[1])
                    frame_toggle <= ~frame_toggle;
            end
            if (active && frame_enabled && run_sync[1]) begin
                if (empty)
                    underflow <= 1;
                else
                    rgb <= {pixel[15 : 11], pixel[15 : 13], pixel[10 : 5], pixel[10 : 9], pixel[4 : 0],
                        pixel[4 : 2]};
            end
        end
    end
endmodule
