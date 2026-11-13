`timescale 1ns/1ps
module tb_sort;
    logic clk = 0;
    always #5 clk = ~clk;
    logic rst_n = 0;
    logic t_start = 0, t_start_ready, t_in_valid = 0, t_in_ready;
    logic t_out_valid, t_out_ready = 0, t_out_last, t_done, t_done_ready = 0;
    logic [31:0] t_count, t_keep, t_in_score, t_out_score;
    logic [63:0] t_base, t_out_index;
    logic [3:0] t_error;
    topk_tile tile_dut(
        .abort_job(1'b0),
        .clk(clk), .rst_n(rst_n), .start_valid(t_start), .start_ready(t_start_ready),
        .input_count(t_count), .keep_count(t_keep), .index_base(t_base),
        .in_score(t_in_score), .in_valid(t_in_valid), .in_ready(t_in_ready),
        .out_score(t_out_score), .out_index(t_out_index), .out_valid(t_out_valid),
        .out_ready(t_out_ready), .out_last(t_out_last), .done_valid(t_done),
        .done_ready(t_done_ready), .error_code(t_error));

    logic m_start = 0, m_start_ready, l_valid = 0, l_ready, r_valid = 0, r_ready;
    logic m_valid, m_ready = 0, m_last, m_done, m_done_ready = 0;
    logic [31:0] l_count, r_count, m_keep, l_score, r_score, m_score;
    logic [63:0] l_index, r_index, m_index;
    logic [3:0] m_error;
    topk_merge merge_dut(
        .abort_job(1'b0),
        .clk(clk), .rst_n(rst_n), .start_valid(m_start), .start_ready(m_start_ready),
        .left_count(l_count), .right_count(r_count), .keep_count(m_keep),
        .left_score(l_score), .left_index(l_index), .left_valid(l_valid), .left_ready(l_ready),
        .right_score(r_score), .right_index(r_index), .right_valid(r_valid), .right_ready(r_ready),
        .out_score(m_score), .out_index(m_index), .out_valid(m_valid), .out_ready(m_ready),
        .out_last(m_last), .done_valid(m_done), .done_ready(m_done_ready), .error_code(m_error));

    logic [31:0] source_score [0:511];
    logic [31:0] right_scores [0:511];
    logic [63:0] source_index [0:511], right_indices [0:511];
    logic [31:0] expected_score [0:511];
    logic [63:0] expected_index [0:511];
    integer fd, cases, case_number, j, scanned, expected_error;
    integer sent, received, cycles, left_sent, right_sent;
    integer total_cycles = 0;
    logic accepted, left_accepted, right_accepted, stalled;
    logic [95:0] held_record;
    logic [31:0] random_state = 32'hbeef3301;

    function automatic logic [31:0] next_random(input logic [31:0] current);
        next_random = {current[30:0], current[31] ^ current[21] ^ current[1] ^ current[0]};
    endfunction

    task automatic run_tile;
        begin
            sent = 0; received = 0; cycles = 0; accepted = 0; stalled = 0;
            @(negedge clk);
            if (!t_start_ready) $fatal(1, "tile not idle");
            t_start = 1;
            @(posedge clk); @(negedge clk); t_start = 0;
            while (!t_done) begin
                random_state = next_random(random_state);
                if (!t_in_valid || accepted) begin
                    t_in_valid = sent < t_count && random_state[0];
                    if (sent < t_count) t_in_score = source_score[sent];
                end
                t_out_ready = random_state[2] || random_state[3];
                @(posedge clk);
                if (stalled && (!t_out_valid || {t_out_score, t_out_index} !== held_record))
                    $fatal(1, "tile changed output during backpressure");
                stalled = t_out_valid && !t_out_ready;
                held_record = {t_out_score, t_out_index};
                accepted = t_in_valid && t_in_ready;
                if (accepted) sent = sent + 1;
                if (t_out_valid && t_out_ready) begin
                    if (expected_error != 0 || received >= t_keep ||
                        t_out_score !== expected_score[received] || t_out_index !== expected_index[received])
                        $fatal(1, "tile case %0d rank %0d got %h/%h expected %h/%h", case_number,
                               received, t_out_score, t_out_index, expected_score[received], expected_index[received]);
                    if (t_out_last !== (received + 1 == t_keep)) $fatal(1, "tile LAST mismatch");
                    received = received + 1;
                end
                cycles = cycles + 1;
                if (cycles > 200000) $fatal(1, "tile watchdog case %0d", case_number);
                @(negedge clk);
            end
            t_in_valid = 0; t_out_ready = 0;
            if (t_error != expected_error) $fatal(1, "tile error code mismatch");
            if (expected_error != 1 && sent != t_count) $fatal(1, "tile did not drain input");
            if (received != (expected_error == 0 ? t_keep : 0)) $fatal(1, "tile output length mismatch");
            $display("TILE case=%0d n=%0d k=%0d cycles=%0d error=%0d", case_number, t_count, t_keep, cycles, t_error);
            total_cycles = total_cycles + cycles;
            repeat (3) begin @(posedge clk); if (!t_done) $fatal(1, "tile lost completion"); end
            @(negedge clk); t_done_ready = 1;
            @(posedge clk); @(negedge clk); t_done_ready = 0;
        end
    endtask

    task automatic run_merge;
        begin
            left_sent = 0; right_sent = 0; received = 0; cycles = 0;
            left_accepted = 0; right_accepted = 0; stalled = 0;
            @(negedge clk);
            if (!m_start_ready) $fatal(1, "merge not idle");
            m_start = 1;
            @(posedge clk); @(negedge clk); m_start = 0;
            while (!m_done) begin
                random_state = next_random(random_state);
                if (!l_valid || left_accepted) begin
                    l_valid = left_sent < l_count && random_state[0];
                    if (left_sent < l_count) begin l_score = source_score[left_sent]; l_index = source_index[left_sent]; end
                end
                if (!r_valid || right_accepted) begin
                    r_valid = right_sent < r_count && random_state[1];
                    if (right_sent < r_count) begin r_score = right_scores[right_sent]; r_index = right_indices[right_sent]; end
                end
                m_ready = random_state[2];
                @(posedge clk);
                if (stalled && (!m_valid || {m_score, m_index} !== held_record))
                    $fatal(1, "merge changed output during backpressure");
                stalled = m_valid && !m_ready;
                held_record = {m_score, m_index};
                left_accepted = l_valid && l_ready;
                right_accepted = r_valid && r_ready;
                if (left_accepted) left_sent = left_sent + 1;
                if (right_accepted) right_sent = right_sent + 1;
                if (m_valid && m_ready) begin
                    if (received >= m_keep || m_score !== expected_score[received] || m_index !== expected_index[received])
                        $fatal(1, "merge case %0d rank %0d mismatch", case_number, received);
                    if (m_last !== (received + 1 == m_keep)) $fatal(1, "merge LAST mismatch");
                    received = received + 1;
                end
                cycles = cycles + 1;
                if (cycles > 20000) $fatal(1, "merge watchdog");
                @(negedge clk);
            end
            l_valid = 0; r_valid = 0; m_ready = 0;
            if (m_error != expected_error || received != (expected_error == 1 ? 0 : m_keep))
                $fatal(1, "merge result mismatch");
            if (expected_error != 1 && (left_sent != l_count || right_sent != r_count))
                $fatal(1, "merge did not drain both inputs");
            total_cycles = total_cycles + cycles;
            @(negedge clk); m_done_ready = 1;
            @(posedge clk); @(negedge clk); m_done_ready = 0;
        end
    endtask

    initial begin
        repeat (5) @(posedge clk);
        @(negedge clk); rst_n = 1;
        fd = $fopen("tile_vectors.txt", "r");
        if (fd == 0) $fatal(1, "missing tile vectors");
        scanned = $fscanf(fd, "%d\n", cases);
        for (case_number = 0; case_number < cases; case_number = case_number + 1) begin
            scanned = $fscanf(fd, "%d %d %h %d\n", t_count, t_keep, t_base, expected_error);
            if (scanned != 4) $fatal(1, "invalid tile header");
            for (j = 0; j < t_count; j = j + 1) scanned = $fscanf(fd, "%h\n", source_score[j]);
            if (expected_error == 0)
                for (j = 0; j < t_keep; j = j + 1)
                    scanned = $fscanf(fd, "%h %h\n", expected_score[j], expected_index[j]);
            run_tile();
        end
        $fclose(fd);
        fd = $fopen("merge_vectors.txt", "r");
        if (fd == 0) $fatal(1, "missing merge vectors");
        scanned = $fscanf(fd, "%d\n", cases);
        for (case_number = 0; case_number < cases; case_number = case_number + 1) begin
            scanned = $fscanf(fd, "%d %d %d %d\n", l_count, r_count, m_keep, expected_error);
            if (scanned != 4) $fatal(1, "invalid merge header");
            for (j = 0; j < l_count; j = j + 1)
                scanned = $fscanf(fd, "%h %h\n", source_score[j], source_index[j]);
            for (j = 0; j < r_count; j = j + 1)
                scanned = $fscanf(fd, "%h %h\n", right_scores[j], right_indices[j]);
            if (expected_error != 1)
                for (j = 0; j < m_keep; j = j + 1)
                    scanned = $fscanf(fd, "%h %h\n", expected_score[j], expected_index[j]);
            run_merge();
        end
        $fclose(fd);
        $display("TOPK_SORT_PASS cycles=%0d", total_cycles);
        $finish;
    end
    initial begin #100000000; $fatal(1, "suite watchdog"); end
endmodule
