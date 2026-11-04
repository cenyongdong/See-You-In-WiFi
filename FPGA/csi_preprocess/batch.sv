// Independent simple-dual-port input/output buffers. Avoid read/write sharing
// across both physical ports; retain bounded readback for device verification.
// GP slave only. No DMA, external memory addresses, or asynchronous clocks.
module csi_batch
    #(parameter SAMPLES = 5400)
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
        input wire rsp_ready);

    // GP 字节偏移和错误码是软件可见 ABI，重命名不改变数值。
    localparam [7 : 0] CSR_ABI = 8'h00;
    localparam [7 : 0] CSR_STATUS = 8'h04;
    localparam [7 : 0] CSR_LOADED = 8'h08;
    localparam [7 : 0] CSR_TAG = 8'h0c;
    localparam [7 : 0] CSR_COMMAND = 8'h10;
    localparam [7 : 0] CSR_COMPLETED_TAG = 8'h14;
    localparam [7 : 0] CSR_ELAPSED = 8'h18;
    localparam [7 : 0] CSR_COMPLETION_COUNT = 8'h1c;
    localparam [7 : 0] CSR_INPUT = 8'h20;
    localparam [7 : 0] CSR_OUTPUT = 8'h24;
    localparam [7 : 0] CSR_READ_POINTER = 8'h28;
    localparam [7 : 0] CSR_INSPECT_POINTER = 8'h2c;
    localparam [7 : 0] CSR_INSPECT_DATA = 8'h30;
    localparam [7 : 0] CSR_INDEX = 8'h34;
    localparam [7 : 0] CSR_REAL = 8'h38;
    localparam [7 : 0] CSR_IMAG = 8'h3c;
    localparam [7 : 0] CSR_FAULT = 8'h40;
    localparam [7 : 0] CSR_PUBLISHED_WORDS = 8'h44;
    localparam [7 : 0] FAULT_NONE = 8'd0;
    localparam [7 : 0] FAULT_BUSY_WRITE = 8'd1;
    localparam [7 : 0] FAULT_COMMAND = 8'd2;
    localparam [7 : 0] FAULT_INPUT_OVERFLOW = 8'd3;
    localparam [7 : 0] FAULT_OUTPUT_UNAVAILABLE = 8'd4;
    localparam [7 : 0] FAULT_POLAR = 8'd5;
    localparam [7 : 0] FAULT_INSPECT_RANGE = 8'd6;
    localparam [7 : 0] FAULT_WRITE_ADDRESS = 8'd7;

    localparam WORDS = 2 * SAMPLES;
    // Explicit power-of-two banks avoid rounding each 10800-word buffer up to
    // 16384 words (32 BRAM36 total would exceed the remaining device capacity).
    (* ram_style = "block" *) reg [31 : 0] input_low[0 : 8191], input_high[0 : 4095];
    (* ram_style = "block" *) reg [31 : 0] output_low[0 : 8191], output_high[0 : 4095];

    // 状态编码与原实现一致；等待状态对应同步 RAM 延迟，不能合并。
    localparam [3 : 0] ST_IDLE = 4'd0;
    localparam [3 : 0] ST_REAL_ADDRESS = 4'd1;
    localparam [3 : 0] ST_REAL_WAIT = 4'd9;
    localparam [3 : 0] ST_REAL_CAPTURE = 4'd2;
    localparam [3 : 0] ST_IMAG_ADDRESS = 4'd3;
    localparam [3 : 0] ST_IMAG_WAIT = 4'd10;
    localparam [3 : 0] ST_IMAG_CAPTURE = 4'd4;
    localparam [3 : 0] ST_START_POLAR = 4'd5;
    localparam [3 : 0] ST_WAIT_POLAR = 4'd6;
    localparam [3 : 0] ST_WRITE_MAGNITUDE = 4'd7;
    localparam [3 : 0] ST_WRITE_ANGLE = 4'd8;

    reg [13 : 0] loaded, read_pointer, index, published_words;
    reg [7 : 0] group_word;
    reg [31 : 0] tag, completed, cycles, elapsed, completion_count;
    reg fault, finished;
    reg [3 : 0] state;
    reg [13 : 0] inspect_pointer;
    reg [7 : 0] fault_reason;
    wire busy = state != ST_IDLE;
    reg [31 : 0] re, im, input_low_q, input_high_q, output_low_q, output_high_q;
    reg input_bank, output_bank;
    wire [31 : 0] port_a = output_bank ? output_high_q : output_low_q;
    wire [31 : 0] port_b = input_bank ? input_high_q : input_low_q;
    wire data_write = wr_valid && wr_addr == CSR_INPUT && !busy && !finished && loaded < WORDS;
    wire [13 : 0] addr_b = !busy ? inspect_pointer
                                 : ((state == ST_IMAG_ADDRESS || state == ST_IMAG_CAPTURE ||
                                        state == ST_IMAG_WAIT || state == ST_WRITE_ANGLE)
                                           ? index + 1'b1
                                           : index);
    wire [13 : 0] result_address = state == ST_WRITE_ANGLE ? index + 1'b1 : index;
    wire result_write = state == ST_WRITE_MAGNITUDE || state == ST_WRITE_ANGLE;
    wire [31 : 0] polar_magnitude;
    wire signed [31 : 0] polar_angle;
    wire polar_busy, polar_done, polar_error;
    reg polar_start;
    reg [31 : 0] saved_m, saved_a;
    csi_polar polar(.clk(clk),
                  .resetn(resetn),
                  .start(polar_start),
                  .re(re),
                  .im(im),
                  .busy(polar_busy),
                  .done(polar_done),
                  .error(polar_error),
                  .magnitude(polar_magnitude),
                  .angle(polar_angle));
    // Match the qualified overlay's separate write/read-port coding style.
    always @(posedge clk) begin
        if (data_write && !loaded[13])
            input_low[loaded[12 : 0]] <= wr_data;
        if (data_write && loaded[13])
            input_high[loaded[11 : 0]] <= wr_data;
        input_low_q <= input_low[addr_b[12 : 0]];
        input_high_q <= input_high[addr_b[11 : 0]];
        input_bank <= addr_b[13];
    end
    always @(posedge clk) begin
        if (result_write && !result_address[13])
            output_low[result_address[12 : 0]] <= state == ST_WRITE_MAGNITUDE ? saved_m : saved_a;
        if (result_write && result_address[13])
            output_high[result_address[11 : 0]] <= state == ST_WRITE_MAGNITUDE ? saved_m : saved_a;
        output_low_q <= output_low[read_pointer[12 : 0]];
        output_high_q <= output_high[read_pointer[11 : 0]];
        output_bank <= read_pointer[13];
    end
    reg pending;
    reg [7 : 0] pending_addr;
    assign wr_ready = 1;
    assign rd_ready = !pending && !rsp_valid;
    always @(posedge clk) begin
        if (!resetn) begin
            loaded <= 0;
            read_pointer <= 0;
            index <= 0;
            published_words <= 0;
            group_word <= 0;
            tag <= 0;
            completed <= 0;
            cycles <= 0;
            elapsed <= 0;
            completion_count <= 0;
            fault <= 0;
            finished <= 0;
            state <= ST_IDLE;
            re <= 0;
            im <= 0;
            // 默认撤销请求；ST_START_POLAR 仅置位一拍。
            polar_start <= 0;
            saved_m <= 0;
            saved_a <= 0;
            pending <= 0;
            pending_addr <= 0;
            rsp_valid <= 0;
            rsp_data <= 0;
            inspect_pointer <= 0;
            fault_reason <= FAULT_NONE;
        end else begin
            polar_start <= 0;
            if (rsp_valid && rsp_ready)
                rsp_valid <= 0;
            if (rd_valid && rd_ready) begin
                pending <= 1;
                pending_addr <= rd_addr;
            end
            if (pending) begin
                pending <= 0;
                rsp_valid <= 1;
                case (pending_addr)
                    CSR_ABI:
                        rsp_data <= 32'h43534903;
                    CSR_STATUS:
                        rsp_data <= {29'd0, fault, finished, busy};
                    CSR_LOADED:
                        rsp_data <= loaded;
                    CSR_TAG:
                        rsp_data <= tag;
                    CSR_COMPLETED_TAG:
                        rsp_data <= completed;
                    CSR_ELAPSED:
                        rsp_data <= elapsed;
                    CSR_COMPLETION_COUNT:
                        rsp_data <= completion_count;
                    CSR_OUTPUT: begin
                        // Publish only complete 90-complex groups. Port A writes later samples
                        // while port B drains already committed words; never read a live write.
                        if (!fault && read_pointer < published_words) begin
                            rsp_data <= port_a;
                            read_pointer <= read_pointer + 1;
                        end else begin
                            rsp_data <= 0;
                            fault <= 1;
                            fault_reason <= FAULT_OUTPUT_UNAVAILABLE;
                        end
                    end
                    CSR_READ_POINTER:
                        rsp_data <= read_pointer;
                    CSR_INSPECT_POINTER:
                        rsp_data <= inspect_pointer;
                    CSR_INSPECT_DATA:
                        rsp_data <= busy ? 32'd0 : port_b;
                    CSR_INDEX:
                        rsp_data <= index;
                    CSR_REAL:
                        rsp_data <= re;
                    CSR_IMAG:
                        rsp_data <= im;
                    CSR_FAULT:
                        rsp_data <= fault_reason;
                    CSR_PUBLISHED_WORDS:
                        rsp_data <= published_words;
                    default:
                        rsp_data <= 0;
                endcase
            end
            if (busy)
                cycles <= cycles + 1;
            case (state)
                ST_REAL_ADDRESS:
                    state <= ST_REAL_WAIT;
                ST_REAL_WAIT:
                    state <= ST_REAL_CAPTURE;
                ST_REAL_CAPTURE: begin
                    re <= port_b;
                    state <= ST_IMAG_ADDRESS;
                end
                ST_IMAG_ADDRESS:
                    state <= ST_IMAG_WAIT;
                ST_IMAG_WAIT:
                    state <= ST_IMAG_CAPTURE;
                ST_IMAG_CAPTURE: begin
                    im <= port_b;
                    state <= ST_START_POLAR;
                end
                ST_START_POLAR: begin
                    polar_start <= 1;
                    state <= ST_WAIT_POLAR;
                end
                ST_WAIT_POLAR:
                    if (polar_done) begin
                        if (polar_error) begin
                            fault <= 1;
                            fault_reason <= FAULT_POLAR;
                            state <= ST_IDLE;
                            finished <= 0;
                        end else begin
                            saved_m <= polar_magnitude;
                            saved_a <= polar_angle;
                            state <= ST_WRITE_MAGNITUDE;
                        end
                    end
                ST_WRITE_MAGNITUDE:
                    state <= ST_WRITE_ANGLE;
                ST_WRITE_ANGLE: begin
                    // RAM 本拍写入相位后，才发布完整 90 复数组的边界。
                    if (group_word == 178 || index == WORDS - 2) begin
                        published_words <= index + 2;
                        group_word <= 0;
                    end else
                        group_word <= group_word + 2;
                    if (index == WORDS - 2) begin
                        state <= ST_IDLE;
                        finished <= 1;
                        elapsed <= cycles + 1;
                        completed <= tag;
                        completion_count <= completion_count + 1;
                    end else begin
                        index <= index + 2;
                        state <= ST_REAL_ADDRESS;
                    end
                end
            endcase
            if (wr_valid) begin
                if (busy) begin
                    fault <= 1;
                    fault_reason <= FAULT_BUSY_WRITE;
                end else
                    case (wr_addr)
                        CSR_TAG:
                            tag <= wr_data;
                        CSR_COMMAND: begin
                            if (wr_data == 2) begin
                                loaded <= 0;
                                read_pointer <= 0;
                                published_words <= 0;
                                group_word <= 0;
                                finished <= 0;
                                fault <= 0;
                                fault_reason <= FAULT_NONE;
                            end else if (wr_data == 1 && loaded == WORDS && !fault) begin
                                state <= ST_REAL_ADDRESS;
                                index <= 0;
                                cycles <= 0;
                                finished <= 0;
                                published_words <= 0;
                                group_word <= 0;
                            end else begin
                                fault <= 1;
                                fault_reason <= FAULT_COMMAND;
                            end
                        end
                        CSR_INPUT: begin
                            if (loaded < WORDS && !finished)
                                loaded <= loaded + 1;
                            else begin
                                fault <= 1;
                                fault_reason <= FAULT_INPUT_OVERFLOW;
                            end
                        end
                        CSR_INSPECT_POINTER: begin
                            if (wr_data < WORDS)
                                inspect_pointer <= wr_data[13 : 0];
                            else begin
                                fault <= 1;
                                fault_reason <= FAULT_INSPECT_RANGE;
                            end
                        end
                        default: begin
                            fault <= 1;
                            fault_reason <= FAULT_WRITE_ADDRESS;
                        end
                    endcase
            end
        end
    end
endmodule
