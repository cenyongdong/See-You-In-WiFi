// Shared vectoring CORDIC. One FP32 complex sample per request; no vendor IP.
// Angle output is signed pi*2^-30. FP32 subnormal/nonfinite inputs are rejected.
module csi_polar
    (input wire clk, resetn, start,
        input wire [31 : 0] re, im,
        output wire busy,
        output reg done, error,
        output reg [31 : 0] magnitude,
        output reg signed [31 : 0] angle);

    // 状态编码与原实现一致；等待状态对应同步 RAM 延迟，不能合并。
    localparam [2 : 0] ST_IDLE = 3'd0;
    localparam [2 : 0] ST_VECTOR = 3'd1;
    localparam [2 : 0] ST_GAIN_PRODUCT = 3'd2;
    localparam [2 : 0] ST_GAIN_SCALE = 3'd3;
    localparam [2 : 0] ST_PUBLISH = 3'd4;

    reg [2 : 0] state;
    reg [4 : 0] iteration;
    reg signed [42 : 0] x, y;
    reg signed [31 : 0] z;
    reg [7 : 0] exponent;
    reg [74 : 0] product;
    reg [43 : 0] mag;
    wire [7 : 0] real_exponent = re[30 : 23], imag_exponent = im[30 : 23];
    wire [7 : 0] shared_exponent = real_exponent > imag_exponent ? real_exponent : imag_exponent;
    wire [7 : 0] real_shift = shared_exponent - real_exponent, imag_shift = shared_exponent - imag_exponent;
    wire [42 : 0] aligned_real = real_shift >= 40 ? 43'd0 : ({3'd0, 1'b1, re[22 : 0], 16'd0} >> real_shift);
    wire [42 : 0] aligned_imag = imag_shift >= 40 ? 43'd0 : ({3'd0, 1'b1, im[22 : 0], 16'd0} >> imag_shift);
    wire signed [42 : 0] signed_real = re[31] ? -$signed(aligned_real) : $signed(aligned_real);
    wire signed [42 : 0] signed_imag = im[31] ? -$signed(aligned_imag) : $signed(aligned_imag);
`include "atan_table.vh"
    assign busy = state != ST_IDLE;
    integer b;
    reg [5 : 0] lead, shift;
    reg [43 : 0] significand, remainder_bits, half;
    reg [8 : 0] out_exp;
    // 幅度回封为 FP32：保留原位宽和 ties-to-even 舍入顺序。
    always @* begin
        lead = 0;
        for (b = 0; b < 44; b = b + 1)
            if (mag[b])
                lead = b;
        shift = lead >= 23 ? lead - 23 : 0;
        significand = mag >> shift;
        remainder_bits = mag & ((44'd1 << shift) - 1);
        half = shift ? 44'd1 << (shift - 1) : 0;
        if (shift && (remainder_bits > half || (remainder_bits == half && significand[0])))
            significand = significand + 1;
        out_exp = {1'b0, exponent} + lead - 39;
        if (significand[24]) begin
            significand = significand >> 1;
            out_exp = out_exp + 1;
        end
    end
    always @(posedge clk) begin
        if (!resetn) begin
            state <= ST_IDLE;
            done <= 0;
            error <= 0;
            magnitude <= 0;
            angle <= 0;
            x <= 0;
            y <= 0;
            z <= 0;
            exponent <= 0;
            iteration <= 0;
            product <= 0;
            mag <= 0;
        end else begin
            done <= 0;
            case (state)
                ST_IDLE:
                    if (start) begin
                        error <= 0;
                        if (real_exponent == 255 || imag_exponent == 255 ||
                            (real_exponent == 0 && re[22 : 0] != 0) ||
                            (imag_exponent == 0 && im[22 : 0] != 0)) begin
                            error <= 1;
                            done <= 1;
                        end else if (im[30 : 0] == 0) begin
                            magnitude <= {1'b0, re[30 : 0]};
                            angle <= re[31] ? (im[31] ? -32'sd1073741824 : 32'sd1073741824) : 0;
                            done <= 1;
                        end else if (re[30 : 0] == 0) begin
                            magnitude <= {1'b0, im[30 : 0]};
                            angle <= im[31] ? -32'sd536870912 : 32'sd536870912;
                            done <= 1;
                        end else begin
                            exponent <= shared_exponent;
                            iteration <= 0;
                            if (re[31]) begin
                                x <= -signed_real;
                                y <= -signed_imag;
                                z <= im[31] ? -32'sd1073741824 : 32'sd1073741824;
                            end else begin
                                x <= signed_real;
                                y <= signed_imag;
                                z <= 0;
                            end
                            state <= ST_VECTOR;
                        end
                    end
                ST_VECTOR: begin
                    // 非阻塞赋值同时使用本拍旧 x/y；不得改为顺序更新。
                    if (y >= 0) begin
                        x <= x + (y >>> iteration);
                        y <= y - (x >>> iteration);
                        z <= z + atan_step(iteration);
                    end else begin
                        x <= x - (y >>> iteration);
                        y <= y + (x >>> iteration);
                        z <= z - atan_step(iteration);
                    end
                    if (iteration == 30)
                        state <= ST_GAIN_PRODUCT;
                    else
                        iteration <= iteration + 1;
                end
                ST_GAIN_PRODUCT: begin
                    product <= $unsigned(x) * 32'd1304065748;
                    state <= ST_GAIN_SCALE;
                end
                ST_GAIN_SCALE: begin
                    mag <= product >> 31;
                    state <= ST_PUBLISH;
                end
                ST_PUBLISH: begin
                    magnitude <= {1'b0, out_exp[7 : 0], significand[22 : 0]};
                    angle <= z;
                    if (out_exp == 0 || out_exp >= 255)
                        error <= 1;
                    done <= 1;
                    state <= ST_IDLE;
                end
            endcase
        end
    end
endmodule
