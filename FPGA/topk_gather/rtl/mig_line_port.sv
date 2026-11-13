// Candidate native-MIG transport, not yet connected to the qualified SoC.
// One rank, eight banks, ROW_BANK_COLUMN, 64-bit DDR words, BL8, 4:1 UI.
// A write handshake only transfers ownership of the buffered line. Completion
// requires a read response after the last write in EVERY modified bank. This
// relies on the controller's per-rank/bank request ordering (UG586 Reordering),
// not app_rdy/app_wdf_rdy. No global cross-bank ordering is assumed.
// Reset/ownership removal requires an externally proven STOP and drain.
module mig_line_port (
    input logic clk, rst_n, exclusive, init_calib_complete,
    input logic [31:0] read_address,
    input logic read_valid,
    output logic read_ready,
    output logic [511:0] read_data,
    output logic read_response_valid,
    input logic read_response_ready,
    output logic read_error,
    input logic [31:0] write_address,
    input logic [511:0] write_data,
    input logic [63:0] write_enable,
    input logic write_valid,
    output logic write_ready,
    input logic fence_valid,
    output logic fence_ready,
    input logic [63:0] fence_job_id,
    output logic fence_response_valid,
    input logic fence_response_ready,
    output logic [63:0] fence_response_job_id,
    output logic fence_error,
    output logic quiescent, fatal,
    output logic [28:0] app_addr,
    output logic [2:0] app_cmd,
    output logic app_en,
    input logic app_rdy,
    output logic [511:0] app_wdf_data,
    output logic [63:0] app_wdf_mask,
    output logic app_wdf_end, app_wdf_wren,
    input logic app_wdf_rdy,
    input logic [511:0] app_rd_data,
    input logic app_rd_data_valid, app_rd_data_end
);
    typedef enum logic [3:0] {IDLE, READ_COMMAND, READ_WAIT, READ_OUTPUT,
        WRITE_DATA, WRITE_COMMAND, FENCE_SELECT, FENCE_COMMAND, FENCE_WAIT, FENCE_OUTPUT} state_t;
    state_t state;
    logic [7:0] dirty_banks;
    logic [28:0] last_write [0:7];
    logic [2:0] active_bank, first_dirty;
    logic write_fault, enabled, unexpected_response;
    integer bank;

    function automatic logic valid_address(input logic [31:0] address);
        // The single-rank geometry has 2 GiB; bit31 must not alias rank zero.
        valid_address = !address[31] && address[5:0] == 0;
    endfunction
    always_comb begin
        first_dirty = 0;
        for (integer i = 7; i >= 0; i = i - 1)
            if (dirty_banks[i]) first_dirty = i[2:0];
    end
    assign unexpected_response = app_rd_data_valid && state != READ_WAIT && state != FENCE_WAIT;
    assign enabled = exclusive && init_calib_complete && !fatal && !unexpected_response;
    assign read_ready = enabled && state == IDLE && !fence_valid;
    assign write_ready = read_ready && !read_valid;
    assign fence_ready = enabled && state == IDLE;
    assign read_response_valid = enabled && state == READ_OUTPUT;
    assign fence_response_valid = enabled && state == FENCE_OUTPUT;
    assign quiescent = state == IDLE && dirty_banks == 0 && !write_fault && !fatal && !unexpected_response;
    assign app_cmd = state == WRITE_COMMAND ? 3'b000 : 3'b001;
    assign app_en = enabled && (state == READ_COMMAND || state == WRITE_COMMAND || state == FENCE_COMMAND);
    assign app_wdf_wren = enabled && state == WRITE_DATA;
    assign app_wdf_end = 1'b1; // One complete 512-bit UI beat per BL8 write.

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE; dirty_banks <= 0; fatal <= 0; write_fault <= 0;
            active_bank <= 0; app_addr <= 0; app_wdf_data <= 0; app_wdf_mask <= 0;
            read_data <= 0; read_error <= 0; fence_error <= 0; fence_response_job_id <= 0;
            for (bank = 0; bank < 8; bank = bank + 1) last_write[bank] <= 0;
        end else begin
            // A foreign response or ownership/calibration loss cannot be
            // converted into successful completion. Retain all outstanding work.
            if (unexpected_response ||
                ((!exclusive || !init_calib_complete) && !quiescent)) fatal <= 1;
            if (enabled) case (state)
                IDLE: begin
                    if (fence_valid) begin
                        fence_response_job_id <= fence_job_id;
                        fence_error <= write_fault;
                        state <= FENCE_SELECT;
                    end else if (read_valid) begin
                        app_addr <= read_address[31:3];
                        read_data <= 0;
                        read_error <= !valid_address(read_address);
                        state <= valid_address(read_address) ? READ_COMMAND : READ_OUTPUT;
                    end else if (write_valid) begin
                        if (!valid_address(write_address)) write_fault <= 1;
                        else if (write_enable != 0) begin
                            app_addr <= write_address[31:3];
                            active_bank <= write_address[15:13];
                            app_wdf_data <= write_data;
                            app_wdf_mask <= ~write_enable;
                            state <= WRITE_DATA;
                        end
                    end
                end
                READ_COMMAND: if (app_rdy) state <= READ_WAIT;
                READ_WAIT: if (app_rd_data_valid) begin
                    read_data <= app_rd_data;
                    read_error <= read_error || !app_rd_data_end;
                    if (app_rd_data_end) state <= READ_OUTPUT;
                end
                READ_OUTPUT: if (read_response_ready) state <= IDLE;
                // Queue data before its command, avoiding any late-data window.
                WRITE_DATA: if (app_wdf_rdy) state <= WRITE_COMMAND;
                WRITE_COMMAND: if (app_rdy) begin
                    last_write[active_bank] <= app_addr;
                    dirty_banks[active_bank] <= 1;
                    state <= IDLE;
                end
                FENCE_SELECT: begin
                    if (dirty_banks == 0) state <= FENCE_OUTPUT;
                    else begin
                        active_bank <= first_dirty;
                        app_addr <= last_write[first_dirty];
                        state <= FENCE_COMMAND;
                    end
                end
                FENCE_COMMAND: if (app_rdy) state <= FENCE_WAIT;
                FENCE_WAIT: if (app_rd_data_valid) begin
                    fence_error <= fence_error || !app_rd_data_end;
                    if (app_rd_data_end) begin
                        dirty_banks[active_bank] <= 0;
                        state <= FENCE_SELECT;
                    end
                end
                FENCE_OUTPUT: if (fence_response_ready) begin
                    write_fault <= 0;
                    state <= IDLE;
                end
                default: fatal <= 1;
            endcase
        end
    end
endmodule
