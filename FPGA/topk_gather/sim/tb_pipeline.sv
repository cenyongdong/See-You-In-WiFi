`timescale 1ns/1ps
module tb_pipeline #(parameter integer MEMORY_OUTPUT = 0);
    logic clk = 0, rst_n = 0;
    always #5 clk = ~clk;
    logic start_valid = 0, start_ready;
    logic [31:0] source_base = 64, source_bytes, input_count, keep_count;
    logic [63:0] index_base;
    logic [2:0] element_bytes;
    logic [31:0] read_address, out_score;
    logic [63:0] out_index;
    logic read_valid, read_ready, read_response_valid = 0, read_response_ready, read_error = 0;
    logic [511:0] read_data = 0;
    logic out_valid, out_ready = 0, out_last, done_valid, done_ready = 0;
    logic [3:0] error_code;
    integer output_fault = 0, number;
    logic [31:0] destination_base, destination_bytes, write_address;
    logic [511:0] write_data;
    logic [63:0] write_enable, fence_job_id, fence_response_job_id, done_job_id;
    logic write_valid, write_ready, fence_valid, fence_ready, fence_response_valid = 0, fence_response_ready;
    logic fence_error = 0;
    wire [63:0] job_id = number + 1;
    assign destination_base = output_fault == 2 ? 64 : 4096;
    assign destination_bytes = output_fault == 1 ? 64 : (keep_count*16+63)/64*64;
    generate if (!MEMORY_OUTPUT) begin : stream_output
        score_topk dut(.*);
        assign write_valid = 0; assign fence_valid = 0;
    end else begin : packed_output
        assign out_valid = 0;
        memory_tile dut(
            .clk(clk), .rst_n(rst_n), .start_valid(start_valid), .start_ready(start_ready),
            .job_id(job_id), .index_base(index_base), .score_base(source_base), .score_bytes(source_bytes),
            .input_count(input_count), .keep_count(keep_count), .score_element_bytes(element_bytes),
            .destination_base(destination_base), .destination_bytes(destination_bytes),
            .read_address(read_address), .read_valid(read_valid), .read_ready(read_ready), .read_data(read_data),
            .read_response_valid(read_response_valid), .read_response_ready(read_response_ready), .read_error(read_error),
            .write_address(write_address), .write_data(write_data), .write_enable(write_enable), .write_valid(write_valid), .write_ready(write_ready),
            .fence_valid(fence_valid), .fence_ready(fence_ready), .fence_job_id(fence_job_id),
            .fence_response_valid(fence_response_valid), .fence_response_ready(fence_response_ready),
            .fence_response_job_id(fence_response_job_id), .fence_error(fence_error),
            .done_valid(done_valid), .done_ready(done_ready), .done_job_id(done_job_id), .error_code(error_code));
    end endgenerate
    logic [511:0] lines [0:31];
    logic [31:0] expected_score [0:255];
    logic [63:0] expected_index [0:255];
    logic [31:0] rng = 32'h3301718;
    logic pending = 0;
    integer held_line, delay_count, reads, expected_error;
    byte output_memory [0:4223]; // Includes a full guard line on both sides.
    logic write_pending = 0, fence_pending = 0, visibility_ack = 0, stale_sent = 0, write_stalled = 0;
    logic [31:0] held_write_address;
    logic [511:0] held_write_data;
    logic [63:0] held_write_enable;
    logic [607:0] prior_write;
    integer write_delay = 0, writes = 0;
    assign read_ready = !pending && rng[0];
    assign write_ready = !write_pending && rng[6];
    assign fence_ready = !fence_pending;
    always @(posedge clk) if (rst_n) begin
        rng <= {rng[30:0], rng[31] ^ rng[21] ^ rng[1] ^ rng[0]};
        if (read_valid && read_ready) begin
            if (read_address[5:0] != 0 || read_address < 64 || read_address + 64 > 64 + source_bytes)
                $fatal(1, "pipeline read escaped allocation");
            held_line <= (read_address - 64) / 64;
            pending <= 1; delay_count <= rng[5:1] + 1; reads <= reads + 1;
        end
        if (pending && !read_response_valid) begin
            if (delay_count > 0) delay_count <= delay_count - 1;
            else begin
                read_data <= lines[held_line]; read_response_valid <= 1;
                read_error <= expected_error == 5 && reads == 2;
            end
        end
        if (read_response_valid && read_response_ready) begin
            read_response_valid <= 0; pending <= 0; read_error <= 0;
        end
        if (done_valid && pending) $fatal(1, "pipeline DONE with read outstanding");
        if (MEMORY_OUTPUT) begin
            if (write_stalled && (!write_valid || {write_address, write_enable, write_data} !== prior_write))
                $fatal(1, "memory tile changed a presented write");
            write_stalled <= write_valid && !write_ready;
            prior_write <= {write_address, write_enable, write_data};
            if (write_valid && write_ready) begin
                if (write_address[5:0] || write_address < 4096 || write_address+64 > 4096+destination_bytes)
                    $fatal(1, "memory tile write escaped allocation");
                write_pending <= 1; held_write_address <= write_address;
                held_write_data <= write_data; held_write_enable <= write_enable;
                write_delay <= 5+rng[12:8]; writes <= writes+1;
            end
            if (write_pending) begin
                if (write_delay != 0) write_delay <= write_delay-1;
                else begin
                    for (integer byte_id = 0; byte_id < 64; byte_id = byte_id+1)
                        if (held_write_enable[byte_id]) output_memory[held_write_address-4096+64+byte_id] <= held_write_data[byte_id*8 +: 8];
                    write_pending <= 0;
                end
            end
            if (fence_valid && fence_ready) begin
                if (fence_job_id != job_id || pending) $fatal(1, "memory tile premature fence");
                fence_pending <= 1;
            end
            if (fence_pending && !fence_response_valid) begin
                if (output_fault == 3 && !stale_sent) begin
                    fence_response_valid <= 1; fence_response_job_id <= job_id-1; stale_sent <= 1;
                end else if (!write_pending) begin
                    fence_response_valid <= 1; fence_response_job_id <= job_id; fence_error <= output_fault == 4;
                end
            end
            if (fence_response_valid && fence_response_ready) begin
                fence_response_valid <= 0;
                if (fence_response_job_id == job_id) begin fence_pending <= 0; visibility_ack <= 1; end
            end
            if (done_valid && (write_pending || fence_pending || (writes != 0 && !visibility_ack)))
                $fatal(1, "memory tile DONE before writes drained");
        end
    end
    integer fd, count, scanned, size_value, i, received, cycles, actual_fd;
    logic stalled;
    logic [96:0] held_output;
    initial begin
        repeat (5) @(posedge clk); @(negedge clk); rst_n = 1;
        fd = $fopen("pipeline_vectors.txt", "r");
        if (!fd) $fatal(1, "missing pipeline vectors");
        scanned = $fscanf(fd, "%d\n", count);
        for (number = 0; number < count; number = number + 1) begin
            if (MEMORY_OUTPUT)
                scanned = $fscanf(fd, "%d %d %h %d %d %d %d\n", input_count, keep_count, index_base,
                                  expected_error, size_value, source_bytes, output_fault);
            else scanned = $fscanf(fd, "%d %d %h %d %d %d\n", input_count, keep_count, index_base,
                                  expected_error, size_value, source_bytes);
            if (scanned != (MEMORY_OUTPUT ? 7 : 6) || source_bytes > 2048) $fatal(1, "bad pipeline fixture");
            element_bytes = size_value;
            for (i = 0; i < source_bytes / 64; i = i + 1) scanned = $fscanf(fd, "%h\n", lines[i]);
            if (expected_error == 0)
                for (i = 0; i < keep_count; i = i + 1)
                    scanned = $fscanf(fd, "%h %h\n", expected_score[i], expected_index[i]);
            if (!start_ready) $fatal(1, "pipeline not idle");
            reads = 0; received = 0; cycles = 0; stalled = 0;
            writes = 0; visibility_ack = 0; stale_sent = 0; fence_error = 0;
            for (i = 0; i < 4224; i = i+1) output_memory[i] = 8'ha5;
            start_valid = 1; @(posedge clk); @(negedge clk); start_valid = 0;
            while (!done_valid) begin
                out_ready = rng[7];
                @(posedge clk);
                if (stalled && (!out_valid || {out_last, out_score, out_index} !== held_output))
                    $fatal(1, "pipeline output changed under backpressure");
                stalled = out_valid && !out_ready; held_output = {out_last, out_score, out_index};
                if (out_valid && out_ready) begin
                    if (expected_error != 0 || received >= keep_count ||
                        out_score !== expected_score[received] || out_index !== expected_index[received] ||
                        out_last != (received + 1 == keep_count))
                        $fatal(1, "pipeline mismatch case=%0d rank=%0d", number, received);
                    received = received + 1;
                end
                cycles = cycles + 1;
                if (cycles > 200000) $fatal(1, "pipeline stuck after read/sort failure");
                @(negedge clk);
            end
            out_ready = 0;
            if ((!MEMORY_OUTPUT && received != (expected_error == 0 ? keep_count : 0)) || error_code != expected_error)
                $fatal(1, "pipeline completion mismatch case=%0d error=%0d", number, error_code);
            if (expected_error == 1 && output_fault != 1 && reads != 0) $fatal(1, "invalid tile issued a read");
            if (MEMORY_OUTPUT) begin
                actual_fd = $fopen($sformatf("actual_tile_%0d.bin", number), "wb");
                if (!actual_fd) $fatal(1, "cannot save packed tile");
                for (i = 0; i < destination_bytes; i = i+1) $fwrite(actual_fd, "%c", output_memory[64+i]);
                $fclose(actual_fd);
                if (done_job_id != job_id) $fatal(1, "memory tile identity mismatch");
                if (expected_error == 0)
                    for (i = 0; i < keep_count; i = i+1) begin
                        for (integer byte_id = 0; byte_id < 4; byte_id = byte_id+1)
                            if (output_memory[64+i*16+byte_id] !== expected_score[i][byte_id*8 +: 8] || output_memory[64+i*16+4+byte_id] !== 0)
                                $fatal(1, "memory tile packed score mismatch");
                        for (integer byte_id = 0; byte_id < 8; byte_id = byte_id+1)
                            if (output_memory[64+i*16+8+byte_id] !== expected_index[i][byte_id*8 +: 8])
                                $fatal(1, "memory tile packed index mismatch");
                    end
                for (i = 0; i < 4224; i = i+1)
                    if ((i < 64 || i >= 64+keep_count*16) && output_memory[i] !== 8'ha5)
                        $fatal(1, "memory tile overwrote tail/guard");
            end
            done_ready = 1; @(posedge clk); @(negedge clk); done_ready = 0;
        end
        $fclose(fd);
        if (MEMORY_OUTPUT) $display("TOPK_MEMORY_TILE_PASS cases=%0d", count);
        else $display("TOPK_PIPELINE_PASS cases=%0d", count);
        $finish;
    end
    initial begin #100000000; $fatal(1, "pipeline suite watchdog"); end
endmodule
