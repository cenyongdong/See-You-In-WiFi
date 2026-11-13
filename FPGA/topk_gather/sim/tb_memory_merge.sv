`timescale 1ns/1ps
// Exercise the complete memory merge, including errors after K is retained.
module tb_memory_merge;
    localparam integer MEMORY_BYTES = 196608, LEFT_BASE = 64, RIGHT_BASE = 65536, OUTPUT_BASE = 131072;
    logic clk = 0, rst_n = 0;
    always #5 clk = ~clk;
    logic start_valid = 0, start_ready, abort_job = 0, done_valid, done_ready = 0;
    logic [63:0] job_id, index_limit, done_job_id;
    logic [31:0] left_base, left_bytes, left_count, right_base, right_bytes, right_count;
    logic [31:0] destination_base, destination_bytes, keep_count;
    logic [31:0] read_address, write_address;
    logic [511:0] read_data, write_data;
    logic [63:0] write_enable;
    logic read_valid, read_ready, read_response_valid = 0, read_response_ready, read_error = 0;
    logic write_valid, write_ready, fence_valid, fence_ready;
    logic [63:0] fence_job_id, fence_response_job_id;
    logic fence_response_valid = 0, fence_response_ready, fence_error = 0;
    logic [3:0] error_code;
    memory_merge dut(.*);
    byte memory [0:MEMORY_BYTES-1], before_run [0:MEMORY_BYTES-1];
    logic [127:0] expected [0:4095];
    logic [31:0] rng = 32'h3301314;
    integer fault = 0, case_number, reads = 0, writes = 0, p;
    logic hold_read = 0, hold_write = 0;
    logic read_pending = 0, write_pending = 0, fence_pending = 0, stale_sent = 0, visibility_ack = 0;
    logic [31:0] held_read, held_write;
    logic [511:0] held_data;
    logic [63:0] held_mask;
    integer read_delay = 0, write_delay = 0, fence_delay = 0;
    logic stalled_read = 0, stalled_write = 0;
    logic [31:0] prior_read, prior_write;
    logic [511:0] prior_data;
    logic [63:0] prior_mask;
    assign read_ready = !read_pending && !hold_read && rng[0];
    assign write_ready = !write_pending && !hold_write && rng[1];
    assign fence_ready = !fence_pending;

    always @(posedge clk) if (rst_n) begin
        rng <= {rng[30:0], rng[31] ^ rng[21] ^ rng[1] ^ rng[0]};
        if (stalled_read && (!read_valid || read_address != prior_read)) $fatal(1, "merge read withdrawn while stalled");
        if (stalled_write && (!write_valid || write_address != prior_write || write_data !== prior_data || write_enable !== prior_mask))
            $fatal(1, "merge write withdrawn while stalled");
        stalled_read <= read_valid && !read_ready; stalled_write <= write_valid && !write_ready;
        prior_read <= read_address; prior_write <= write_address; prior_data <= write_data; prior_mask <= write_enable;
        if (read_valid && read_ready) begin
            if (read_address[5:0] || !((read_address >= LEFT_BASE && read_address+64 <= LEFT_BASE+left_bytes) ||
                (read_address >= RIGHT_BASE && read_address+64 <= RIGHT_BASE+right_bytes))) $fatal(1, "merge read outside allocation");
            read_pending <= 1; held_read <= read_address; read_delay <= 1 + rng[7:4]; reads <= reads + 1;
        end
        if (read_pending && !read_response_valid) begin
            if (read_delay != 0) read_delay <= read_delay - 1;
            else begin
                for (p = 0; p < 64; p = p + 1) read_data[p*8 +: 8] <= memory[held_read+p];
                read_response_valid <= 1; read_error <= fault == 5 && reads == 5;
            end
        end
        if (read_response_valid && read_response_ready) begin read_response_valid <= 0; read_pending <= 0; read_error <= 0; end
        if (write_valid && write_ready) begin
            if (write_address[5:0] || write_address < OUTPUT_BASE || write_address+64 > OUTPUT_BASE+destination_bytes)
                $fatal(1, "merge output outside allocation");
            write_pending <= 1; held_write <= write_address; held_data <= write_data; held_mask <= write_enable;
            write_delay <= 10 + rng[11:8]; writes <= writes + 1;
        end
        if (write_pending) begin
            if (write_delay != 0) write_delay <= write_delay - 1;
            else begin
                for (p = 0; p < 64; p = p + 1) if (held_mask[p]) memory[held_write+p] <= held_data[p*8 +: 8];
                write_pending <= 0;
            end
        end
        if (fence_valid && fence_ready) begin
            if (fence_job_id != job_id || read_pending || read_valid) $fatal(1, "merge fenced before read drain");
            fence_pending <= 1; fence_delay <= 30;
        end
        if (fence_pending && !fence_response_valid) begin
            if (fault == 6 && !stale_sent) begin
                fence_response_valid <= 1; fence_response_job_id <= job_id-1; stale_sent <= 1;
            end else if (fence_delay != 0) fence_delay <= fence_delay - 1;
            else if (!write_pending) begin
                fence_response_valid <= 1; fence_response_job_id <= job_id; fence_error <= fault == 7;
            end
        end
        if (fence_response_valid && fence_response_ready) begin
            fence_response_valid <= 0;
            if (fence_response_job_id == job_id) begin fence_pending <= 0; visibility_ack <= 1; end
        end
        if (done_valid && (read_pending || write_pending || (writes != 0 && !visibility_ack)))
            $fatal(1, "merge DONE before owned I/O drained");
    end

    logic all_zero_scores;
    function automatic logic [127:0] make_record(input integer index);
        logic [31:0] bits;
        begin
            bits = all_zero_scores ? (index % 2 ? 32'h80000000 : 0) : 32'h4b000000 + (4096-index)/3;
            make_record = {64'h100000000 + index, 32'd0, bits};
        end
    endfunction
    task automatic put_record(input integer address, input logic [127:0] value);
        for (integer j = 0; j < 16; j = j + 1) memory[address+j] = value[j*8 +: 8];
    endtask
    task automatic tick;
        @(posedge clk); @(negedge clk);
    endtask

    integer i, j, rank, cycles, expected_error, actual_fd;
    logic [127:0] actual_record;
    initial begin
        repeat (5) tick(); rst_n = 1;
        for (case_number = 0; case_number < 30; case_number = case_number + 1) begin
            fault = case_number < 8 || case_number % 2 ? 0 : (case_number-8)/2+1;
            left_count = 67; right_count = 65; keep_count = 17;
            case (case_number)
                0: begin left_count = 1; right_count = 1; keep_count = 1; end
                1: begin left_count = 90; right_count = 90; keep_count = 100; end
                2: begin left_count = 50; right_count = 50; keep_count = 50; end
                3: begin left_count = 256; right_count = 257; keep_count = 400; end
                4: begin left_count = 512; right_count = 513; keep_count = 513; end
                5: begin left_count = 512; right_count = 513; keep_count = 1025; end
                6: begin left_count = 1024; right_count = 1024; keep_count = 2048; end
                7: begin left_count = 1; right_count = 513; keep_count = 500; end
            endcase
            if (fault == 2 || fault == 3) keep_count = 2; // Bad tail must still fail.
            all_zero_scores = case_number == 7;
            left_base = LEFT_BASE; right_base = RIGHT_BASE; destination_base = OUTPUT_BASE;
            left_bytes = (left_count*16+63)/64*64; right_bytes = (right_count*16+63)/64*64;
            destination_bytes = (keep_count*16+63)/64*64; index_limit = 64'h100001000;
            job_id = 1000 + case_number; reads = 0; writes = 0; stale_sent = 0; visibility_ack = 0; fence_error = 0;
            hold_write = fault == 8; hold_read = fault == 9;
            for (i = 0; i < MEMORY_BYTES; i = i + 1) memory[i] = 'ha5;
            for (i = 0; i < left_count; i = i + 1) put_record(LEFT_BASE+i*16, make_record(i*2));
            for (i = 0; i < right_count; i = i + 1) put_record(RIGHT_BASE+i*16, make_record(i*2+1));
            // Ascending global indices are the independent oracle for this
            // monotonic score family (including all-zero score ties).
            rank = 0;
            for (i = 0; i < 4096; i = i + 1)
                if ((i % 2 == 0 && i/2 < left_count) || (i % 2 != 0 && i/2 < right_count)) begin
                    expected[rank] = make_record(i); rank = rank + 1;
                end
            if (rank != left_count+right_count) $fatal(1, "invalid independent merge fixture");
            expected_error = fault == 1 || fault == 10 || fault == 11 ? 1 : fault == 2 || fault == 4 ? 4 :
                             fault == 3 ? 2 : fault == 5 ? 5 : fault == 6 ? 6 : fault == 7 ? 7 : fault ? 8 : 0;
            if (fault == 1) destination_bytes = 64;
            if (fault == 2) memory[LEFT_BASE+(left_count-1)*16+4] = 1;
            if (fault == 3) begin memory[RIGHT_BASE+(right_count-1)*16+2] = 'hc0; memory[RIGHT_BASE+(right_count-1)*16+3] = 'h7f; end
            if (fault == 4) for (j = 8; j < 16; j = j + 1) memory[LEFT_BASE+j] = 'hff;
            if (fault == 10) left_count = 0;
            if (fault == 11) right_base = LEFT_BASE;
            for (i = 0; i < MEMORY_BYTES; i = i + 1) before_run[i] = memory[i];
            if (!start_ready) $fatal(1, "merge not reusable after prior result");
            start_valid = 1; tick(); start_valid = 0;
            cycles = 0;
            while (!done_valid) begin
                if (fault == 8 && write_valid) abort_job = 1;
                if (fault == 9 && read_valid) abort_job = 1;
                if (cycles > 150) begin hold_read = 0; hold_write = 0; end
                tick(); cycles = cycles + 1;
                if (cycles > 100000) $fatal(1, "memory merge watchdog case=%0d", case_number);
            end
            actual_fd = $fopen($sformatf("actual_%0d_merge.bin", case_number), "wb");
            for (i = 0; i < destination_bytes; i = i + 1) $fwrite(actual_fd, "%c", memory[OUTPUT_BASE+i]);
            $fclose(actual_fd);
            if (error_code != expected_error || done_job_id != job_id)
                $fatal(1, "memory merge result error=%0d expected=%0d case=%0d", error_code, expected_error, case_number);
            if (!expected_error) begin
                for (i = 0; i < keep_count; i = i + 1) begin
                    for (j = 0; j < 16; j = j + 1) actual_record[j*8 +: 8] = memory[OUTPUT_BASE+i*16+j];
                    if (actual_record !== expected[i]) $fatal(1, "memory merge rank mismatch case=%0d rank=%0d", case_number, i);
                end
                if (reads != (left_count+3)/4+(right_count+3)/4) $fatal(1, "input tail not fully read");
            end
            for (i = 0; i < MEMORY_BYTES; i = i + 1)
                if (!(i >= OUTPUT_BASE && i < OUTPUT_BASE+(expected_error ? destination_bytes : keep_count*16)) && memory[i] !== before_run[i])
                    $fatal(1, "merge changed input/guard bytes");
            if ((fault == 10 || fault == 11) && (reads || writes)) $fatal(1, "invalid merge accessed memory");
            abort_job = 0; done_ready = 1; tick(); done_ready = 0;
            $display("MEMORY_MERGE case=%0d left=%0d right=%0d k=%0d reads=%0d writes=%0d error=%0d PASS",
                     case_number, left_count, right_count, keep_count, reads, writes, expected_error);
        end
        $display("TOPK_MEMORY_MERGE_PASS cases=30"); $finish;
    end
    initial begin #100000000; $fatal(1, "memory merge suite watchdog"); end
endmodule
