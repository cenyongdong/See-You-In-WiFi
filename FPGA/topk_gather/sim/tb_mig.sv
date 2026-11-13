`timescale 1ns/1ps
module mig_test_case #(parameter integer FINAL_FAULT = 0)(output logic done);
    logic clk = 0;
    always #5 clk = ~clk;
    logic rst_n = 0, exclusive = 1, init_calib_complete = 0;
    logic [31:0] read_address = 0, write_address = 0;
    logic read_valid = 0, read_ready, read_response_valid, read_response_ready = 0, read_error;
    logic [511:0] read_data, write_data = 0;
    logic [63:0] write_enable = 0;
    logic write_valid = 0, write_ready, fence_valid = 0, fence_ready;
    logic [63:0] fence_job_id = 0, fence_response_job_id;
    logic fence_response_valid, fence_response_ready = 0, fence_error, quiescent, fatal;
    logic [28:0] app_addr;
    logic [2:0] app_cmd;
    logic app_en, app_rdy, app_wdf_end, app_wdf_wren, app_wdf_rdy;
    logic [511:0] app_wdf_data, app_rd_data = 0;
    logic [63:0] app_wdf_mask;
    logic app_rd_data_valid = 0, app_rd_data_end = 0;
    mig_line_port dut(.*);

    logic [31:0] random_state = 32'h26371289 + FINAL_FAULT;
    logic [511:0] memory [0:1023], expected [0:1023];
    logic [511:0] staged_data, queued_data [0:63];
    logic [63:0] staged_mask, queued_mask [0:63];
    integer queued_line [0:63];
    logic queued_valid [0:63];
    logic staged = 0, read_pending = 0, hold_responses = 0, inject_foreign = 0;
    integer write_count = 0, read_count = 0, queue_count = 0;
    integer response_line, delay_count, response_bank;
    integer i, byte_index, active, previous_reads, previous_writes;

    assign app_rdy = init_calib_complete && random_state[0];
    assign app_wdf_rdy = init_calib_complete && random_state[4];
    always @(posedge clk) begin
        random_state <= {random_state[30:0], random_state[31]^random_state[21]^random_state[1]^random_state[0]};
        app_rd_data_valid <= 0;
        app_rd_data_end <= 0;
        if (rst_n) begin
            if (app_wdf_wren && app_wdf_rdy) begin
                if (staged || !app_wdf_end) $fatal(1, "Invalid write-data sequencing");
                staged_data = app_wdf_data; staged_mask = app_wdf_mask; staged = 1;
            end
            if (app_en && app_rdy) begin
                if (app_addr[2:0] != 0 || app_addr[28]) $fatal(1, "Invalid word/rank address");
                if (app_cmd == 0) begin
                    if (!staged || queue_count >= 64) $fatal(1, "Write command without data");
                    queued_data[queue_count] = staged_data;
                    queued_mask[queue_count] = staged_mask;
                    queued_line[queue_count] = app_addr >> 3;
                    queued_valid[queue_count] = 1;
                    queue_count = queue_count + 1; write_count = write_count + 1; staged = 0;
                end else if (app_cmd == 1) begin
                    if (read_pending) $fatal(1, "Multiple outstanding reads");
                    response_line = app_addr >> 3;
                    response_bank = app_addr[12:10];
                    delay_count = 7;
                    read_pending = 1; read_count = read_count + 1;
                end else $fatal(1, "Unexpected MIG command");
            end
            if (read_pending && !hold_responses) begin
                if (delay_count != 0) delay_count = delay_count - 1;
                else begin
                    // Adversarial legal ordering: other banks retain ALL their
                    // writes. Reading one final address cannot drain those banks.
                    for (integer q = 0; q < queue_count; q = q + 1)
                        if (queued_valid[q] && ((queued_line[q] >> 7) & 7) == response_bank) begin
                            for (integer b = 0; b < 64; b = b + 1)
                                if (!queued_mask[q][b]) memory[queued_line[q]][b*8+:8] = queued_data[q][b*8+:8];
                            queued_valid[q] = 0;
                        end
                    app_rd_data <= memory[response_line];
                    app_rd_data_valid <= 1; app_rd_data_end <= 1; read_pending = 0;
                end
            end
            if (inject_foreign) begin app_rd_data_valid <= 1; app_rd_data_end <= 1; end
        end
    end

    task automatic send_write(input logic [31:0] address, input logic [7:0] value, input logic [63:0] mask);
        begin
            @(negedge clk); write_address = address; write_data = {64{value}}; write_enable = mask; write_valid = 1;
            do @(posedge clk); while (!write_ready);
            @(negedge clk); write_valid = 0;
            if (!address[31] && address[5:0] == 0)
                for (integer b = 0; b < 64; b = b + 1)
                    if (mask[b]) expected[address >> 6][b*8+:8] = value;
        end
    endtask
    task automatic start_fence(input logic [63:0] tag);
        begin
            @(negedge clk); fence_job_id = tag; fence_valid = 1;
            do @(posedge clk); while (!fence_ready);
            @(negedge clk); fence_valid = 0;
        end
    endtask
    task automatic finish_fence(input logic [63:0] tag, input logic expected_error);
        begin
            do @(posedge clk); while (!fence_response_valid);
            if (fence_response_job_id !== tag || fence_error !== expected_error) $fatal(1, "Fence identity/error differs");
            for (integer q = 0; q < queue_count; q = q + 1)
                if (queued_valid[q]) $fatal(1, "Fence completed before another bank's write");
            repeat (4) begin
                @(posedge clk);
                if (!fence_response_valid || fence_response_job_id !== tag || read_ready || write_ready)
                    $fatal(1, "Completion was not retained under backpressure");
            end
            @(negedge clk); fence_response_ready = 1;
            @(negedge clk); fence_response_ready = 0;
        end
    endtask
    task automatic check_read(input logic [31:0] address, input logic expected_error);
        logic [511:0] captured;
        begin
            @(negedge clk); read_address = address; read_valid = 1;
            do @(posedge clk); while (!read_ready);
            @(negedge clk); read_valid = 0;
            do @(posedge clk); while (!read_response_valid);
            if (read_error !== expected_error) $fatal(1, "Read error differs");
            captured = read_data;
            if (!expected_error && captured !== expected[address >> 6]) $fatal(1, "Masked data readback differs");
            repeat (3) begin
                @(posedge clk);
                if (!read_response_valid || read_data !== captured) $fatal(1, "Read result was not retained");
            end
            @(negedge clk); read_response_ready = 1;
            @(negedge clk); read_response_ready = 0;
        end
    endtask

    initial begin
        done = 0;
        for (i = 0; i < 1024; i = i + 1) begin memory[i] = 0; expected[i] = 0; end
        for (i = 0; i < 64; i = i + 1) queued_valid[i] = 0;
        repeat (5) @(negedge clk);
        rst_n = 1;
        repeat (5) begin
            @(posedge clk);
            if (read_ready || write_ready || fence_ready || app_en || app_wdf_wren) $fatal(1, "Activity before calibration");
        end
        @(negedge clk); init_calib_complete = 1;
        for (i = 0; i < 8; i = i + 1) begin
            send_write(i * 8192, 8'h30+i, 64'hffffffffffffffff);
            send_write(i * 8192, 8'ha0+i, 64'h5555555555555555);
        end
        previous_reads = read_count;
        hold_responses = 1;
        start_fence(64'h100000001);
        repeat (40) begin
            @(posedge clk);
            if (fence_response_valid || quiescent) $fatal(1, "Missing response was treated as completion");
        end
        @(negedge clk); hold_responses = 0;
        finish_fence(64'h100000001, 0);
        if (read_count - previous_reads != 8) $fatal(1, "Expected one barrier per modified bank");
        for (i = 0; i < 8; i = i + 1) check_read(i * 8192, 0);
        previous_reads = read_count;
        start_fence(2); finish_fence(2, 0);
        if (read_count != previous_reads || !quiescent) $fatal(1, "Clean fence should need no DDR traffic");
        previous_writes = write_count;
        send_write(3, 8'hff, 64'hffffffffffffffff);
        send_write(32'h80000000, 8'hff, 64'hffffffffffffffff);
        send_write(0, 8'hff, 0);
        start_fence(3); finish_fence(3, 1);
        if (write_count != previous_writes) $fatal(1, "Invalid/empty write reached DDR");
        check_read(3, 1); check_read(32'h80000000, 1);
        if (FINAL_FAULT == 0) begin
            start_fence(4);
            do @(posedge clk); while (!fence_response_valid);
            @(negedge clk); inject_foreign = 1;
            @(negedge clk); inject_foreign = 0; fence_response_ready = 1;
            @(negedge clk); fence_response_ready = 0;
            repeat (3) @(negedge clk);
        end else begin
            send_write(64, 8'h55, 64'hffffffffffffffff);
            do @(negedge clk); while (write_count == previous_writes);
            exclusive = 0;
            repeat (3) @(negedge clk);
        end
        if (!fatal || quiescent || read_ready || write_ready || fence_response_valid)
            $fatal(1, "Ownership/protocol fault did not retain resources");
        done = 1;
    end
    initial begin #500000; $fatal(1, "Testbench deadline"); end
endmodule

module tb_mig;
    wire done0, done1;
    mig_test_case #(.FINAL_FAULT(0)) unexpected_response(done0);
    mig_test_case #(.FINAL_FAULT(1)) ownership_loss(done1);
    initial begin
        wait(done0 && done1);
        $display("TOPK_MIG_PASS banks=8 variants=2 masked_writes=32");
        $finish;
    end
endmodule
