// Full-system adapter: owns only HP2 reads and its dedicated CSR endpoint.
// Defaults to black raster without DMA. Static color bars require safe idle.
module hdmi_board
    (input wire ref_100m,
        input wire clock_reset,
        input wire csr_clk,
        input wire csr_resetn,
        mna_gp_ww_itf.slave csr,
        mna_gp_ww_itf.slave overlay_csr,
        input wire mem_clk,
        input wire mem_resetn,
        output wire [31 : 0] araddr,
        output wire [3 : 0] arlen,
        output wire [2 : 0] arsize,
        output wire [1 : 0] arburst,
        output wire arvalid,
        input wire arready,
        input wire [63 : 0] rdata,
        input wire [1 : 0] rresp,
        input wire [4 : 0] rid,
        input wire rlast,
        input wire rvalid,
        output wire rready,
        output wire tmds_clk_p,
        output wire tmds_clk_n,
        output wire [2 : 0] tmds_p,
        output wire [2 : 0] tmds_n);
    wire pixel_clk, serial_clk, locked, safe_idle;
    wire pixel_reset = !locked || !csr_resetn || !mem_resetn;
    (* ASYNC_REG = "TRUE" *) reg [2 : 0] pixel_release;
    always @(posedge pixel_clk or posedge pixel_reset)
        if (pixel_reset)
            pixel_release <= 0;
        else
            pixel_release <= {pixel_release[1 : 0], 1'b1};
    wire pixel_resetn = pixel_release[2];
    hdmi_clock_jfm clock_generator(.ref_100m(ref_100m),
                       .reset(clock_reset),
                       .pixel_clk(pixel_clk),
                       .serial_clk(serial_clk),
                       .locked(locked));
    wire [7 : 0] core_arlen;
    assign arlen = core_arlen[3 : 0]; // core restricts every burst to 1..16 beats.
    wire write_ready;
    wire [31 : 0] core_read_data;
    wire [7 : 0] offset = csr.awwaddr[7 : 0];
    wire core_write = offset <= 8'h2c;
    wire aligned_write = csr.awwaddr[1 : 0] == 0;
    reg pattern_enable, diagnostic_error, dma_started;
    (* ASYNC_REG = "TRUE" *) reg [1 : 0] locked_csr, idle_csr, pattern_pixel;
    reg response_valid;
    reg [31 : 0] response_data, csr_ticks;
    reg [31 : 0] pixel_count, pixel_gray;
    (* ASYNC_REG = "TRUE" *) reg [31 : 0] pixel_gray_csr1, pixel_gray_csr2;
    wire [31 : 0] next_pixel_count = pixel_count + 1'b1;
    always @(posedge pixel_clk or negedge pixel_resetn) begin
        if (!pixel_resetn) begin
            pixel_count <= 0;
            pixel_gray <= 0;
            pattern_pixel <= 0;
        end else begin
            pixel_count <= next_pixel_count;
            pixel_gray <= (next_pixel_count >> 1) ^ next_pixel_count;
            pattern_pixel <= {pattern_pixel[0], pattern_enable};
        end
    end
    function [31 : 0] ungray
        (input [31 : 0] value);
        integer i;
        begin
            ungray[31] = value[31];
            for (i = 30; i >= 0; i = i - 1)
                ungray[i] = ungray[i + 1] ^ value[i];
        end
    endfunction
    wire reject_pattern_start = offset == 8'h0c && csr.awwdata == 1 && pattern_enable;
    assign csr.awwready = !aligned_write || !core_write || reject_pattern_start || write_ready;
    assign csr.arready = !response_valid || csr.rready;
    assign csr.rvalid = response_valid;
    assign csr.rdata = response_data;
    wire write_fire = csr.awwvalid && csr.awwready;
    reg [31 : 0] selected_read;
    always @* begin
        selected_read = core_read_data;
        if (csr.araddr[1 : 0] != 0)
            selected_read = 32'hbad00001;
        else
            case (csr.araddr[7 : 0])
                8'h30:
                    selected_read = {28'd0, diagnostic_error, pattern_enable, idle_csr[1], locked_csr[1]};
                8'h34:
                    selected_read = {31'd0, pattern_enable};
                8'h38:
                    selected_read = ungray(pixel_gray_csr2);
                8'h3c:
                    selected_read = csr_ticks;
                8'h40:
                    selected_read = 32'h48445301;
                8'h44:
                    selected_read = 32'd148500000;
                8'h48:
                    selected_read = 32'd742500000;
                default:
                    if (csr.araddr[7 : 0] > 8'h2c)
                        selected_read = 0;
            endcase
    end
    always @(posedge csr_clk or negedge csr_resetn) begin
        if (!csr_resetn) begin
            response_valid <= 0;
            response_data <= 0;
            pattern_enable <= 0;
            diagnostic_error <= 0;
            dma_started <= 0;
            locked_csr <= 0;
            idle_csr <= 0;
            pixel_gray_csr1 <= 0;
            pixel_gray_csr2 <= 0;
            csr_ticks <= 0;
        end else begin
            locked_csr <= {locked_csr[0], locked};
            idle_csr <= {idle_csr[0], safe_idle};
            pixel_gray_csr1 <= pixel_gray;
            pixel_gray_csr2 <= pixel_gray_csr1;
            csr_ticks <= csr_ticks + 1'b1;
            if (csr.arvalid && csr.arready) begin
                response_valid <= 1;
                response_data <= selected_read;
            end else if (csr.rready)
                response_valid <= 0;
            if (write_fire) begin
                if (aligned_write && core_write && offset == 8'h0c && csr.awwdata == 1 &&
                    !reject_pattern_start)
                    dma_started <= 1;
                if (!aligned_write || reject_pattern_start)
                    diagnostic_error <= 1;
                else if (!core_write) begin
                    // Static bars are a pre-DMA bring-up mode. After the first
                    // START, they cannot be re-enabled until a system reset.
                    if (offset == 8'h34 && csr.awwdata <= 1 && idle_csr[1] &&
                        (!dma_started || csr.awwdata == 0))
                        pattern_enable <= csr.awwdata[0];
                    else if (offset == 8'h30 && csr.awwdata == 8)
                        diagnostic_error <= 0;
                    else
                        diagnostic_error <= 1;
                end
            end
        end
    end
    wire hs, vs, de;
    wire [23 : 0] rgb;
    hdmi_scanout scanout(.csr_clk(csr_clk),
                     .csr_resetn(csr_resetn),
                     .write_valid(write_fire && aligned_write && core_write && !reject_pattern_start),
                     .write_ready(write_ready),
                     .write_offset(offset),
                     .write_data(csr.awwdata),
                     .write_strobe(4'hf),
                     .read_offset(csr.araddr[7 : 0]),
                     .read_data(core_read_data),
                     .mem_clk(mem_clk),
                     .mem_resetn(mem_resetn),
                     .pixel_clk(pixel_clk),
                     .pixel_resetn(pixel_resetn),
                     .clock_locked(locked),
                     .araddr(araddr),
                     .arlen(core_arlen),
                     .arsize(arsize),
                     .arburst(arburst),
                     .arvalid(arvalid),
                     .arready(arready),
                     .rdata(rdata),
                     .rresp(rid != 0 ? 2'b10 : rresp),
                     .rlast(rlast),
                     .rvalid(rvalid),
                     .rready(rready),
                     .safe_idle(safe_idle),
                     .hs(hs),
                     .vs(vs),
                     .de(de),
                     .rgb(rgb));
    reg [10 : 0] pattern_x;
    always @(posedge pixel_clk or negedge pixel_resetn)
        if (!pixel_resetn)
            pattern_x <= 0;
        else if (!de)
            pattern_x <= 0;
        else
            pattern_x <= pattern_x + 1'b1;
    wire [2 : 0] bar = pattern_x < 240  ? 3'd7
                     : pattern_x < 480  ? 3'd6
                     : pattern_x < 720  ? 3'd5
                     : pattern_x < 960  ? 3'd4
                     : pattern_x < 1200 ? 3'd3
                     : pattern_x < 1440 ? 3'd2
                     : pattern_x < 1680 ? 3'd1
                                        : 3'd0;
    wire [23 : 0] pattern_rgb = {{8{bar[2]}}, {8{bar[1]}}, {8{bar[0]}}};
    wire overlay_hs, overlay_vs, overlay_de;
    wire [23 : 0] overlay_rgb;
    skeleton_overlay overlay(.clk(csr_clk),
                         .resetn(csr_resetn),
                         .wr_valid(overlay_csr.awwvalid),
                         .wr_addr(overlay_csr.awwaddr[7 : 0]),
                         .wr_data(overlay_csr.awwdata),
                         .wr_ready(overlay_csr.awwready),
                         .rd_valid(overlay_csr.arvalid),
                         .rd_addr(overlay_csr.araddr[7 : 0]),
                         .rd_ready(overlay_csr.arready),
                         .rsp_valid(overlay_csr.rvalid),
                         .rsp_data(overlay_csr.rdata),
                         .rsp_ready(overlay_csr.rready),
                         .pclk(pixel_clk),
                         .presetn(pixel_resetn),
                         .hs(hs),
                         .vs(vs),
                         .de(de),
                         .rgb(pattern_pixel[1] ? pattern_rgb : rgb),
                         .hide(safe_idle | pattern_pixel[1]),
                         .out_hs(overlay_hs),
                         .out_vs(overlay_vs),
                         .out_de(overlay_de),
                         .out_rgb(overlay_rgb));
    uihdmitx #(.FAMILY("7FAMILY"))
        transmitter(.RSTn_i(pixel_resetn),
            .HS_i(overlay_hs),
            .VS_i(overlay_vs),
            .VDE_i(overlay_de),
            .RGB_i(overlay_rgb),
            .PCLKX1_i(pixel_clk),
            .PCLKX2_5_i(1'b0),
            .PCLKX5_i(serial_clk),
            .TMDS_TX_CLK_P(tmds_clk_p),
            .TMDS_TX_CLK_N(tmds_clk_n),
            .TMDS_TX_P(tmds_p),
            .TMDS_TX_N(tmds_n));
endmodule
