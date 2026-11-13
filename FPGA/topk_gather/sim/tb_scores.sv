`timescale 1ns/1ps
module tb_scores #(parameter integer FP16_FLUSH_TO_POSITIVE_ZERO = 0);
    logic clk = 0, rst_n = 0;
    always #5 clk = ~clk;
    logic start_valid = 0, start_ready;
    logic [31:0] source_base = 64, source_bytes, input_count;
    logic [2:0] element_bytes;
    logic [31:0] read_address, score_data;
    logic read_valid, read_ready, read_response_valid = 0, read_response_ready, read_error = 0;
    logic [511:0] read_data = 0;
    logic score_valid, score_ready = 0, score_last, done_valid, done_ready = 0;
    logic [3:0] error_code;
    score_reader #(.FP16_FLUSH_TO_POSITIVE_ZERO(FP16_FLUSH_TO_POSITIVE_ZERO)) dut(.*);
    logic [511:0] lines [0:4095];
    logic [31:0] expected [0:65535];
    logic [31:0] rng = 32'h33016;
    logic pending = 0;
    integer held_line, delay_count, reads, fault;
    assign read_ready = !pending && rng[0];
    always @(posedge clk) if (rst_n) begin
        rng <= {rng[30:0], rng[31] ^ rng[21] ^ rng[1] ^ rng[0]};
        if (read_valid && read_ready) begin
            if (read_address[5:0] != 0 || read_address < 64 || read_address + 64 > 64 + source_bytes)
                $fatal(1, "score read escaped allocation");
            held_line <= (read_address - 64) / 64;
            pending <= 1; delay_count <= rng[5:1] + 1; reads <= reads + 1;
        end
        if (pending && !read_response_valid) begin
            if (delay_count > 0) delay_count <= delay_count - 1;
            else begin
                read_data <= lines[held_line]; read_response_valid <= 1;
                read_error <= fault == 2 && reads == 2;
            end
        end
        if (read_response_valid && read_response_ready) begin
            read_response_valid <= 0; pending <= 0; read_error <= 0;
        end
        if (done_valid && pending) $fatal(1, "score DONE with read outstanding");
    end

    integer fd, count, number, scanned, size_value, i, received, cycles, expected_count;
    logic stalled;
    logic [32:0] held_output;
    initial begin
        repeat (5) @(posedge clk); @(negedge clk); rst_n = 1;
        fd = $fopen("score_vectors.txt", "r");
        if (!fd) $fatal(1, "missing score vectors");
        scanned = $fscanf(fd, "%d\n", count);
        for (number = 0; number < count; number = number + 1) begin
            scanned = $fscanf(fd, "%d %d %d %d\n", input_count, size_value, source_bytes, fault);
            if (scanned != 4 || input_count > 65536 || source_bytes > 262144) $fatal(1, "bad score fixture");
            element_bytes = size_value;
            for (i = 0; i < source_bytes / 64; i = i + 1) scanned = $fscanf(fd, "%h\n", lines[i]);
            for (i = 0; i < input_count; i = i + 1) scanned = $fscanf(fd, "%h\n", expected[i]);
            if (fault == 1) source_bytes = 64;
            if (!start_ready) $fatal(1, "score reader not idle");
            reads = 0; received = 0; cycles = 0; stalled = 0;
            start_valid = 1; @(posedge clk); @(negedge clk); start_valid = 0;
            while (!done_valid) begin
                score_ready = rng[7];
                @(posedge clk);
                if (stalled && (!score_valid || {score_last, score_data} !== held_output))
                    $fatal(1, "score changed under backpressure");
                stalled = score_valid && !score_ready; held_output = {score_last, score_data};
                if (score_valid && score_ready) begin
                    if (received >= input_count || score_data !== expected[received] ||
                        score_last != (received + 1 == input_count))
                        $fatal(1, "score conversion/ordering mismatch case=%0d index=%0d", number, received);
                    received = received + 1;
                end
                cycles = cycles + 1;
                if (cycles > 1000000) $fatal(1, "score watchdog");
                @(negedge clk);
            end
            score_ready = 0;
            expected_count = fault == 1 ? 0 : (fault == 2 ? 64 / size_value : input_count);
            if (received != expected_count || error_code != (fault == 1 ? 1 : (fault == 2 ? 5 : 0)))
                $fatal(1, "score completion mismatch");
            $display("SCORES case=%0d n=%0d bytes=%0d emitted=%0d error=%0d", number, input_count,
                     size_value, received, error_code);
            done_ready = 1; @(posedge clk); @(negedge clk); done_ready = 0;
        end
        $fclose(fd);
        $display("TOPK_SCORES_PASS cases=%0d", count); $finish;
    end
    initial begin #20000000; $fatal(1, "score suite watchdog"); end
endmodule
