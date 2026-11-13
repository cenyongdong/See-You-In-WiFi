`timescale 1ns/1ps
module tb_records;
    localparam integer MEMORY_BYTES = 32768;
    logic clk = 0, rst_n = 0;
    always #5 clk = ~clk;
    logic writer_start = 0, writer_start_ready, writer_abort = 0;
    logic writer_done, writer_done_ready = 0;
    logic [3:0] writer_error;
    logic [31:0] count, allocation, writer_allocation, reader_allocation;
    logic [63:0] job_id, index_limit;
    logic [31:0] in_score;
    logic [63:0] in_index;
    logic in_valid = 0, in_ready;
    logic [31:0] write_address;
    logic [511:0] write_data;
    logic [63:0] write_enable;
    logic write_valid, write_ready;
    logic fence_valid, fence_ready, fence_response_valid = 0, fence_response_ready, fence_error = 0;
    logic [63:0] fence_job_id, fence_response_job_id;
    logic reader_start = 0, reader_start_ready, reader_abort = 0;
    logic reader_done, reader_done_ready = 0;
    logic [3:0] reader_error;
    logic [31:0] out_score, read_address;
    logic [63:0] out_index;
    logic out_valid, out_ready = 0, read_valid, read_ready;
    logic [511:0] read_data;
    logic read_response_valid = 0, read_response_ready, read_error = 0;
    integer fault = 0, case_number = 0, fd, output_fd;
    assign allocation = (count*16+63)/64*64;
    assign writer_allocation = fault == 13 ? 64 : allocation;
    assign reader_allocation = fault == 12 ? 64 : allocation;
    assign index_limit = 64'h100000000 + count*17 + 1;

    run_writer writer(
        .clk(clk), .rst_n(rst_n), .abort_job(writer_abort), .start_valid(writer_start), .start_ready(writer_start_ready),
        .job_id(job_id), .destination_base(32'd64), .destination_bytes(writer_allocation), .record_count(count),
        .record_score(in_score), .record_index(in_index), .record_valid(in_valid), .record_ready(in_ready),
        .write_address(write_address), .write_data(write_data), .write_enable(write_enable),
        .write_valid(write_valid), .write_ready(write_ready), .fence_valid(fence_valid), .fence_ready(fence_ready),
        .fence_job_id(fence_job_id), .fence_response_valid(fence_response_valid), .fence_response_ready(fence_response_ready),
        .fence_response_job_id(fence_response_job_id), .fence_error(fence_error),
        .done_valid(writer_done), .done_ready(writer_done_ready), .error_code(writer_error));
    run_reader reader(
        .clk(clk), .rst_n(rst_n), .abort_job(reader_abort), .start_valid(reader_start), .start_ready(reader_start_ready),
        .source_base(32'd64), .source_bytes(reader_allocation), .record_count(count), .index_limit(index_limit),
        .record_score(out_score), .record_index(out_index), .record_valid(out_valid), .record_ready(out_ready),
        .read_address(read_address), .read_valid(read_valid), .read_ready(read_ready), .read_data(read_data),
        .read_response_valid(read_response_valid), .read_response_ready(read_response_ready), .read_error(read_error),
        .done_valid(reader_done), .done_ready(reader_done_ready), .error_code(reader_error));

    byte memory [0:MEMORY_BYTES-1];
    logic [31:0] rng = 32'h3301313;
    logic write_pending = 0, read_pending = 0, fence_pending = 0, stale_sent = 0, visibility_ack = 0;
    logic hold_write = 0, hold_read = 0;
    logic [31:0] held_write_address, held_read_address;
    logic [511:0] held_write_data;
    logic [63:0] held_write_enable;
    integer write_delay = 0, read_delay = 0, fence_delay = 0, writes = 0, reads = 0, p;
    logic stalled_write = 0, stalled_read = 0;
    logic [31:0] old_write_address, old_read_address;
    logic [511:0] old_write_data;
    logic [63:0] old_write_enable;
    assign write_ready = !write_pending && !hold_write && rng[0];
    assign read_ready = !read_pending && !hold_read && rng[1];
    assign fence_ready = !fence_pending;
    always @(posedge clk) if (rst_n) begin
        rng <= {rng[30:0], rng[31] ^ rng[21] ^ rng[1] ^ rng[0]};
        if (stalled_write && (!write_valid || write_address != old_write_address ||
            write_data !== old_write_data || write_enable !== old_write_enable))
            $fatal(1, "packed write withdrawn or changed while stalled");
        if (stalled_read && (!read_valid || read_address != old_read_address))
            $fatal(1, "packed read withdrawn or changed while stalled");
        stalled_write <= write_valid && !write_ready; stalled_read <= read_valid && !read_ready;
        old_write_address <= write_address; old_write_data <= write_data; old_write_enable <= write_enable;
        old_read_address <= read_address;
        if (write_valid && write_ready) begin
            if (write_address[5:0] || write_address < 64 || write_address+64 > 64+allocation || !write_enable)
                $fatal(1, "packed write outside allocation");
            write_pending <= 1; held_write_address <= write_address;
            held_write_data <= write_data; held_write_enable <= write_enable;
            write_delay <= 10 + rng[7:4]; writes <= writes + 1;
        end
        if (write_pending) begin
            if (write_delay != 0) write_delay <= write_delay - 1;
            else begin
                for (p = 0; p < 64; p = p + 1)
                    if (held_write_enable[p]) memory[held_write_address+p] <= held_write_data[p*8 +: 8];
                write_pending <= 0;
            end
        end
        if (fence_valid && fence_ready) begin
            if (fence_job_id != job_id) $fatal(1, "packed writer fence identity changed");
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
        if (writer_done && writer_error != 1 && (!visibility_ack || write_pending))
            $fatal(1, "packed writer done before visibility");
        if (read_valid && read_ready) begin
            if (read_address[5:0] || read_address < 64 || read_address+64 > 64+allocation)
                $fatal(1, "packed read outside allocation");
            read_pending <= 1; held_read_address <= read_address; read_delay <= 20 + rng[11:8]; reads <= reads + 1;
        end
        if (read_pending && !read_response_valid) begin
            if (read_delay != 0) read_delay <= read_delay - 1;
            else begin
                for (p = 0; p < 64; p = p + 1) read_data[p*8 +: 8] <= memory[held_read_address+p];
                read_error <= fault == 5 && reads == 3; read_response_valid <= 1;
            end
        end
        if (read_response_valid && read_response_ready) begin
            read_response_valid <= 0; read_pending <= 0; read_error <= 0;
        end
        if (reader_done && read_pending) $fatal(1, "packed reader completed with owned read pending");
    end

    function automatic logic [31:0] score(input integer i);
        score = i % 7 == 0 ? (i % 2 ? 32'h80000000 : 0) : 32'h3f000000 + i*17;
    endfunction
    function automatic logic [127:0] record(input integer i);
        record = {64'h100000000 + i*17, 32'd0, score(i)};
    endfunction
    task automatic tick;
        @(posedge clk); @(negedge clk);
    endtask

    integer sent, received, cycles, expected_writer_error, expected_reader_error, valid_records, i, j;
    logic accepted;
    logic [127:0] expected_record;
    initial begin
        repeat (5) tick(); rst_n = 1;
        for (case_number = 0; case_number < 20; case_number = case_number + 1) begin
            case (case_number)
                0: count = 1;
                1: count = 3;
                2: count = 4;
                3: count = 5;
                4: count = 100;
                5: count = 257;
                6: count = 513;
                7: count = 1025;
                default: count = 17;
            endcase
            fault = case_number < 8 ? 0 : case_number - 6; // Faults 2..13.
            expected_writer_error = fault == 6 ? 6 : fault == 7 ? 7 : (fault == 8 || fault == 9) ? 8 : fault == 13 ? 1 : 0;
            expected_reader_error = fault == 2 ? 2 : (fault == 3 || fault == 4) ? 4 : fault == 5 ? 5 :
                                    (fault == 10 || fault == 11) ? 8 : fault == 12 ? 1 : 0;
            job_id = 100 + case_number; writes = 0; reads = 0; stale_sent = 0; visibility_ack = 0;
            fence_error = 0; writer_abort = 0; reader_abort = 0; hold_write = fault == 9; hold_read = fault == 10;
            for (i = 0; i < MEMORY_BYTES; i = i + 1) memory[i] = 'ha5;
            writer_start = 1; tick(); writer_start = 0;
            sent = 0; cycles = 0; accepted = 0;
            while (!writer_done) begin
                if (!in_valid || accepted) begin
                    in_valid = sent < count && rng[2] && !writer_abort;
                    in_score = score(sent); in_index = 64'h100000000 + sent*17;
                end
                if (fault == 8 && sent == 2) begin writer_abort = 1; in_valid = 0; end
                if (fault == 9 && write_valid) begin writer_abort = 1; in_valid = 0; end
                if (fault == 9 && cycles > 50) hold_write = 0;
                @(posedge clk); accepted = in_valid && in_ready;
                if (accepted) sent = sent + 1;
                @(negedge clk); cycles = cycles + 1;
                if (cycles > 100000) $fatal(1, "packed writer watchdog");
            end
            in_valid = 0; writer_abort = 0;
            output_fd = $fopen($sformatf("actual_%0d_records.bin", case_number), "wb");
            for (i = 0; i < allocation; i = i + 1) $fwrite(output_fd, "%c", memory[64+i]);
            $fclose(output_fd);
            if (writer_error != expected_writer_error) $fatal(1, "packed writer error=%0d expected=%0d", writer_error, expected_writer_error);
            valid_records = fault == 8 || fault == 13 ? 0 : fault == 9 ? 4 : count;
            for (i = 0; i < MEMORY_BYTES; i = i + 1) begin
                if (i >= 64 && i < 64+valid_records*16) begin
                    expected_record = record((i-64)/16);
                    if (memory[i] !== expected_record[((i-64)%16)*8 +: 8]) $fatal(1, "packed wire format mismatch");
                end else if (memory[i] !== 8'ha5) $fatal(1, "packed writer changed guard/tail");
            end
            writer_done_ready = 1; tick(); writer_done_ready = 0;
            if (fault == 8 || fault == 9 || fault == 13) begin
                $display("RECORDS case=%0d count=%0d writer_abort_or_reject PASS", case_number, count);
            end else begin
                if (fault == 2) begin memory[64+2] = 'hc0; memory[64+3] = 'h7f; end
                if (fault == 3) memory[64+4] = 1;
                if (fault == 4) for (j = 8; j < 16; j = j + 1) memory[64+j] = 'hff;
                fd = $fopen($sformatf("actual_%0d_stream.txt", case_number), "w");
                reader_start = 1; tick(); reader_start = 0;
                received = 0; cycles = 0;
                while (!reader_done) begin
                    out_ready = rng[3];
                    if (fault == 10 && read_valid) reader_abort = 1;
                    if (fault == 10 && cycles > 40) hold_read = 0;
                    if (fault == 11 && read_pending) reader_abort = 1;
                    @(posedge clk);
                    if (out_valid && out_ready) begin
                        $fwrite(fd, "%h %h\n", out_score, out_index); $fflush(fd);
                        if (out_score !== score(received) || out_index !== 64'h100000000 + received*17)
                            $fatal(1, "packed round trip differs");
                        received = received + 1;
                    end
                    @(negedge clk); cycles = cycles + 1;
                    if (cycles > 100000) $fatal(1, "packed reader watchdog");
                end
                $fclose(fd); reader_abort = 0; out_ready = 0;
                if (reader_error != expected_reader_error || (!expected_reader_error && received != count))
                    $fatal(1, "packed reader result error=%0d expected=%0d received=%0d", reader_error, expected_reader_error, received);
                reader_done_ready = 1; tick(); reader_done_ready = 0;
                $display("RECORDS case=%0d count=%0d emitted=%0d writer_error=%0d reader_error=%0d PASS",
                         case_number, count, received, expected_writer_error, expected_reader_error);
            end
        end
        $display("TOPK_RECORDS_PASS cases=20"); $finish;
    end
    initial begin #100000000; $fatal(1, "record DMA suite watchdog"); end
endmodule
