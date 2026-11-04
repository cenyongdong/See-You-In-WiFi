// Project-owned command rasterizer. Two BRAM banks; no new DMA master.
module skeleton_overlay
    #(parameter integer W = 960, H = 540)
    (input wire clk, resetn,
        input wire wr_valid,
        input wire [7 : 0] wr_addr,
        input wire [31 : 0] wr_data,
        output wire wr_ready,
        input wire rd_valid,
        input wire [7 : 0] rd_addr,
        output wire rd_ready,
        output reg rsp_valid,
        output reg [31 : 0] rsp_data,
        input wire rsp_ready,
        input wire pclk, presetn,
        input wire hs, vs, de,
        input wire [23 : 0] rgb,
        input wire hide,
        output reg out_hs, out_vs, out_de,
        output reg [23 : 0] out_rgb);
    localparam integer N = W * H, AW = $clog2(2 * N);
    (* ram_style = "block" *) reg [3 : 0] pixels[0 : 2 * N - 1];
    (* ram_style = "block" *) reg [31 : 0] commands[0 : 511];
    reg [9 : 0] words, total, index;
    reg [31 : 0] tag, pending_tag, done_tag, cycles, draw_cycles, completed;
    reg error, back_bank, request;
    reg [3 : 0] state;
    localparam IDLE = 0, CLEAR = 1, FETCH0 = 2, FETCH1 = 3, SETUP = 4, LINE = 5, SHAPE = 6, NEXT = 7,
               WAIT = 8;
    localparam FETCH0_CAPTURE = 9, FETCH1_CAPTURE = 10;
    // 命令 RAM 为同步读；地址、采样分别占一拍，保留原 9/10 状态。
    reg [31 : 0] c0, c1;
    reg [31 : 0] command_q;
    reg [AW - 1 : 0] clear_addr, write_addr;
    reg write_en;
    reg [3 : 0] write_ink, ink, kind;
    reg signed [12 : 0] x, y, xe, ye, xstart, ystart, dx, dy, sx, sy, err;
    wire signed [13 : 0] twice = $signed(err) * 2;
    reg [3 : 0] gx, gy;
    reg [6 : 0] character;
    wire busy = state != IDLE;
    reg ack, front_bank, front_valid;
    reg underflow_any;
    // CDC 寄存器名称被约束引用，保留名称、级数和属性。
    (* ASYNC_REG = "TRUE" *) reg [1 : 0] ack_sync, req_sync, hide_sync;
    (* ASYNC_REG = "TRUE" *) reg [1 : 0] vs_sync;
    (* ASYNC_REG = "TRUE" *) reg [1 : 0] underflow_sync;
    assign wr_ready = 1'b1;
    assign rd_ready = !rsp_valid || rsp_ready;
    always @(posedge clk)
        if (write_en)
            pixels[write_addr] <= write_ink;
    always @(posedge clk) begin
        if (wr_valid && !busy && wr_addr == 32 && words < 512)
            commands[words[8 : 0]] <= wr_data;
        command_q <= commands[index[8 : 0] + (state == FETCH1 ? 9'd1 : 9'd0)];
    end

// The ROM is generated from the existing project 5x7 font, no vendor glyphs.
`include "font_rom.vh"
    function [23 : 0] palette
        (input [3 : 0] c);
        begin
            case (c)
                1:
                    palette = 24'h399eff;
                2:
                    palette = 24'heff3f7;
                3:
                    palette = 24'h103c31;
                4:
                    palette = 24'hb5f7de;
                5:
                    palette = 24'h4a3c21;
                6:
                    palette = 24'hffe3a5;
                default:
                    palette = 24'hffffff;
            endcase
        end
    endfunction
    wire [4 : 0] glyph_row = font_row(character, gy);
    wire shape_pixel = kind == 3 ||
             (kind == 2 &&
                 ((gx == 2 && gy <= 4) || (gy == 2 && gx <= 4) ||
                     (gx >= 1 && gx <= 3 && gy >= 1 && gy <= 3))) ||
             (kind == 4 && glyph_row[4 - gx]);

    always @(posedge clk or negedge resetn) begin
        if (!resetn) begin
            state <= IDLE;
            words <= 0;
            total <= 0;
            index <= 0;
            tag <= 0;
            pending_tag <= 0;
            done_tag <= 0;
            underflow_sync <= 0;
            cycles <= 0;
            draw_cycles <= 0;
            completed <= 0;
            error <= 0;
            back_bank <= 1;
            request <= 0;
            ack_sync <= 0;
            write_en <= 0;
            write_addr <= 0;
            write_ink <= 0;
            clear_addr <= 0;
            rsp_valid <= 0;
            rsp_data <= 0;
            c0 <= 0;
            c1 <= 0;
            ink <= 0;
            kind <= 0;
            x <= 0;
            y <= 0;
            xe <= 0;
            ye <= 0;
            xstart <= 0;
            ystart <= 0;
            dx <= 0;
            dy <= 0;
            sx <= 0;
            sy <= 0;
            err <= 0;
            gx <= 0;
            gy <= 0;
            character <= 0;
        end else begin
            ack_sync <= {ack_sync[0], ack};
            underflow_sync <= {underflow_sync[0], underflow_any};
            write_en <= 0;
            if (busy && state != WAIT)
                cycles <= cycles + 1'b1;
            if (rd_valid && rd_ready) begin
                rsp_valid <= 1;
                case (rd_addr)
                    0:
                        rsp_data <= 32'h534b4c01;
                    4:
                        rsp_data <= {28'd0, underflow_sync[1], (completed != 0), error, busy};
                    8:
                        rsp_data <= words;
                    12:
                        rsp_data <= tag;
                    20:
                        rsp_data <= done_tag;
                    24:
                        rsp_data <= draw_cycles;
                    28:
                        rsp_data <= total;
                    36:
                        rsp_data <= completed;
                    default:
                        rsp_data <= 0;
                endcase
            end else if (rsp_ready)
                rsp_valid <= 0;
            if (wr_valid) begin
                if (busy || wr_addr[1 : 0] != 0)
                    error <= 1;
                else
                    case (wr_addr)
                        12:
                            tag <= wr_data;
                        32:
                            if (words < 512)
                                words <= words + 1'b1;
                            else
                                error <= 1;
                        16:
                            case (wr_data)
                                1:
                                    if (!words[0] && !error) begin
                                        total <= words;
                                        index <= 0;
                                        pending_tag <= tag;
                                        cycles <= 0;
                                        clear_addr <= back_bank ? N : 0;
                                        state <= CLEAR;
                                    end else
                                        error <= 1;
                                2:
                                    error <= 0;
                                4:
                                    words <= 0;
                                default:
                                    error <= 1;
                            endcase
                        default:
                            error <= 1;
                    endcase
            end
            case (state)
                CLEAR: begin
                    write_en <= 1;
                    write_addr <= clear_addr;
                    write_ink <= 0;
                    if (clear_addr == (back_bank ? 2 * N - 1 : N - 1))
                        state <= FETCH0;
                    else
                        clear_addr <= clear_addr + 1'b1;
                end
                FETCH0:
                    if (index == total) begin
                        draw_cycles <= cycles;
                        request <= ~request;
                        state <= WAIT;
                    end else
                        state <= FETCH0_CAPTURE;
                FETCH0_CAPTURE: begin
                    c0 <= command_q;
                    state <= FETCH1;
                end
                FETCH1:
                    state <= FETCH1_CAPTURE;
                FETCH1_CAPTURE: begin
                    c1 <= command_q;
                    state <= SETUP;
                end
                SETUP: begin
                    x <= $signed({3'b0, c0[9 : 0]});
                    y <= $signed({3'b0, c0[19 : 10]});
                    xe <= $signed({3'b0, c1[9 : 0]});
                    ye <= $signed({3'b0, c1[19 : 10]});
                    xstart <= $signed({3'b0, c0[9 : 0]});
                    ystart <= $signed({3'b0, c0[19 : 10]});
                    dx <= c1[9 : 0] >= c0[9 : 0] ? c1[9 : 0] - c0[9 : 0] : c0[9 : 0] - c1[9 : 0];
                    dy <= c1[19 : 10] >= c0[19 : 10] ? -$signed({3'b0, c1[19 : 10] - c0[19 : 10]})
                                                     : -$signed({3'b0, c0[19 : 10] - c1[19 : 10]});
                    sx <= c1[9 : 0] >= c0[9 : 0] ? 1 : -1;
                    sy <= c1[19 : 10] >= c0[19 : 10] ? 1 : -1;
                    err <= $signed({3'b0,
                               (c1[9 : 0] >= c0[9 : 0] ? c1[9 : 0] - c0[9 : 0] : c0[9 : 0] - c1[9 : 0])}) -
                        $signed({3'b0,
                            (c1[19 : 10] >= c0[19 : 10] ? c1[19 : 10] - c0[19 : 10]
                                                        : c0[19 : 10] - c1[19 : 10])});
                    kind <= c0[27 : 24];
                    ink <= c0[31 : 28];
                    gx <= 0;
                    gy <= 0;
                    character <= c1[6 : 0];
                    if (c0[27 : 24] < 1 || c0[27 : 24] > 4 || c0[9 : 0] >= W || c0[19 : 10] >= H ||
                        ((c0[27 : 24] == 1 || c0[27 : 24] == 3) && (c1[9 : 0] >= W || c1[19 : 10] >= H)) ||
                        (c0[27 : 24] == 3 && (c1[9 : 0] < c0[9 : 0] || c1[19 : 10] < c0[19 : 10]))) begin
                        error <= 1;
                        state <= NEXT;
                    end else
                        state <= c0[27 : 24] == 1 ? LINE : SHAPE;
                end
                LINE: begin
                    // Bresenham 两个方向均读取旧误差；保持非阻塞赋值优先级。
                    write_en <= 1;
                    write_addr <= (back_bank ? N : 0) + y * W + x;
                    write_ink <= ink;
                    if (x == xe && y == ye)
                        state <= NEXT;
                    else begin
                        if (twice >= dy)
                            x <= x + sx;
                        if (twice <= dx)
                            y <= y + sy;
                        err <= err + (twice >= dy ? dy : 13'sd0) + (twice <= dx ? dx : 13'sd0);
                    end
                end
                SHAPE: begin
                    if (kind == 3) begin
                        write_en <= 1;
                        write_addr <= (back_bank ? N : 0) + y * W + x;
                        write_ink <= ink;
                        if (x == xe) begin
                            x <= xstart;
                            if (y == ye)
                                state <= NEXT;
                            else
                                y <= y + 1'b1;
                        end else
                            x <= x + 1'b1;
                    end else begin
                        if (shape_pixel && $signed(xstart) + $signed({1'b0, gx}) - (kind == 2 ? 2 : 0) >= 0 &&
                            $signed(ystart) + $signed({1'b0, gy}) - (kind == 2 ? 2 : 0) >= 0 &&
                            $signed(xstart) + $signed({1'b0, gx}) - (kind == 2 ? 2 : 0) < W &&
                            $signed(ystart) + $signed({1'b0, gy}) - (kind == 2 ? 2 : 0) < H) begin
                            write_en <= 1;
                            write_ink <= ink;
                            write_addr <= (back_bank ? N : 0) + (ystart + gy - (kind == 2 ? 2 : 0)) * W +
                                xstart + gx - (kind == 2 ? 2 : 0);
                        end
                        if (gx == 4) begin
                            gx <= 0;
                            if (gy == (kind == 2 ? 4 : 6))
                                state <= NEXT;
                            else
                                gy <= gy + 1'b1;
                        end else
                            gx <= gx + 1'b1;
                    end
                end
                NEXT: begin
                    index <= index + 2;
                    state <= FETCH0;
                end
                WAIT:
                    if (ack_sync[1] == request) begin
                        done_tag <= pending_tag;
                        completed <= completed + 1'b1;
                        back_bank <= ~back_bank;
                        words <= 0;
                        state <= IDLE;
                    end
                default:
                    ;
            endcase
        end
    end

    // Stable-bank handshake: the writer never modifies the visible bank or
    // outstanding commands. Ack returns only after vertical-blank adoption.
    reg old_vs, old_de;
    reg [11 : 0] px, py;
    reg [3 : 0] pixel_ink, ink_stage, held_ink;
    reg frame_bad;
    wire fifo_full, fifo_empty;
    wire [3 : 0] fifo_head;
    reg [3 : 0] fetch_ink;
    reg fetch_valid;
    reg [19 : 0] fetch_count;
    reg [AW - 1 : 0] fetch_addr;
    reg [10 : 0] fetch_x, fetch_y;
    wire feed_clear = vs_sync[1];
    wire feed_enabled = completed != 0 && !feed_clear;
    wire fetch_read = feed_enabled && !fifo_full && fetch_count < 2 * N;
    // Both large RAM ports use the existing global GP clock.
    always @(posedge clk)
        if (fetch_read)
            fetch_ink <= pixels[fetch_addr];
    always @(posedge clk or negedge resetn) begin
        if (!resetn) begin
            vs_sync <= 0;
            fetch_valid <= 0;
            fetch_count <= 0;
            fetch_addr <= 0;
            fetch_x <= 0;
            fetch_y <= 0;
        end else begin
            vs_sync <= {vs_sync[0], vs};
            if (!feed_enabled) begin
                fetch_valid <= 0;
                fetch_count <= 0;
                fetch_addr <= back_bank ? 0 : N;
                fetch_x <= 0;
                fetch_y <= 0;
            end else if (!fifo_full) begin
                fetch_valid <= fetch_read;
                if (fetch_read) begin
                    fetch_count <= fetch_count + 1'b1;
                    if (fetch_x == W - 1) begin
                        fetch_x <= 0;
                        fetch_y <= fetch_y + 1'b1;
                        fetch_addr <= fetch_y[0] ? fetch_addr + 1'b1 : fetch_addr - (W - 1);
                    end else begin
                        fetch_x <= fetch_x + 1'b1;
                        fetch_addr <= fetch_addr + 1'b1;
                    end
                end
            end
        end
    end
    wire fifo_pop = de && !px[0] && front_valid && !hide_sync[1] && !frame_bad && !fifo_empty;
    palette_fifo fifo(.wclk(clk),
                     .wresetn(resetn),
                     .wclear(feed_clear),
                     .push(fetch_valid && feed_enabled),
                     .data(fetch_ink),
                     .full(fifo_full),
                     .rclk(pclk),
                     .rresetn(presetn),
                     .rclear(vs),
                     .pop(fifo_pop),
                     .head(fifo_head),
                     .empty(fifo_empty));
    reg [1 : 0] hpipe, vpipe, dpipe, enable_pipe;
    reg [23 : 0] bg0, bg1;
    always @(posedge pclk or negedge presetn) begin
        if (!presetn) begin
            req_sync <= 0;
            hide_sync <= 3;
            ack <= 0;
            front_bank <= 0;
            front_valid <= 0;
            old_vs <= 0;
            old_de <= 0;
            px <= 0;
            py <= 0;
            hpipe <= 0;
            vpipe <= 0;
            dpipe <= 0;
            enable_pipe <= 0;
            pixel_ink <= 0;
            ink_stage <= 0;
            held_ink <= 0;
            frame_bad <= 0;
            underflow_any <= 0;
            bg0 <= 0;
            bg1 <= 0;
            out_hs <= 0;
            out_vs <= 0;
            out_de <= 0;
            out_rgb <= 0;
        end else begin
            req_sync <= {req_sync[0], request};
            hide_sync <= {hide_sync[0], hide};
            old_vs <= vs;
            old_de <= de;
            if (vs && !old_vs) begin
                py <= 0;
                frame_bad <= 0;
                if (req_sync[1] != ack) begin
                    front_bank <= ~front_bank;
                    front_valid <= 1;
                    ack <= req_sync[1];
                end
            end else if (old_de && !de)
                py <= py + 1'b1;
            if (de)
                px <= px + 1'b1;
            else
                px <= 0;
            ink_stage <= 0;
            if (de && front_valid && !hide_sync[1] && !frame_bad) begin
                if (!px[0]) begin
                    if (fifo_empty) begin
                        frame_bad <= 1;
                        underflow_any <= 1;
                        held_ink <= 0;
                    end else begin
                        ink_stage <= fifo_head;
                        held_ink <= fifo_head;
                    end
                end else
                    ink_stage <= held_ink;
            end
            pixel_ink <= ink_stage;
            hpipe <= {hpipe[0], hs};
            vpipe <= {vpipe[0], vs};
            dpipe <= {dpipe[0], de};
            enable_pipe <= {enable_pipe[0], front_valid && !hide_sync[1]};
            bg0 <= rgb;
            bg1 <= bg0;
            out_hs <= hpipe[1];
            out_vs <= vpipe[1];
            out_de <= dpipe[1];
            out_rgb <= dpipe[1] && enable_pipe[1] && pixel_ink != 0 ? palette(pixel_ink) : bg1;
        end
    end
endmodule
