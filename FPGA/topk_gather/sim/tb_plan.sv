`timescale 1ns/1ps
// Execute C++ planner jobs on the actual tile/merge RTL. Every merge consumes
// records emitted by earlier RTL jobs, not precomputed reference runs.
module tb_plan #(parameter integer USE_MEMORY_MERGE = 0);
    localparam integer MAX_N = 2048, SCORE_ARRAY_BASE = 32'h80000;
    logic clk = 0, rst_n = 0;
    always #5 clk = ~clk;
    logic t_start = 0, t_start_ready, t_in_valid = 0, t_in_ready;
    logic t_valid, t_ready = 0, t_last, t_done, t_done_ready = 0;
    logic [31:0] t_count, t_keep, t_in_score, t_score;
    logic [63:0] t_base, t_index;
    logic [3:0] t_error;
    generate if (!USE_MEMORY_MERGE) begin : stream_tiles
    topk_tile tile_dut(
        .abort_job(1'b0),
        .clk(clk), .rst_n(rst_n), .start_valid(t_start), .start_ready(t_start_ready),
        .input_count(t_count), .keep_count(t_keep), .index_base(t_base),
        .in_score(t_in_score), .in_valid(t_in_valid), .in_ready(t_in_ready),
        .out_score(t_score), .out_index(t_index), .out_valid(t_valid), .out_ready(t_ready),
        .out_last(t_last), .done_valid(t_done), .done_ready(t_done_ready), .error_code(t_error));
    end endgenerate
    logic m_start = 0, m_start_ready, l_valid = 0, l_ready, r_valid = 0, r_ready;
    logic m_valid, m_ready = 0, m_last, m_done, m_done_ready = 0;
    logic [31:0] l_count, r_count, m_keep, l_score, r_score, m_score;
    logic [63:0] l_index, r_index, m_index;
    logic [3:0] m_error;
    generate if (!USE_MEMORY_MERGE) begin : stream_merges
    topk_merge merge_dut(
        .abort_job(1'b0),
        .clk(clk), .rst_n(rst_n), .start_valid(m_start), .start_ready(m_start_ready),
        .left_count(l_count), .right_count(r_count), .keep_count(m_keep),
        .left_score(l_score), .left_index(l_index), .left_valid(l_valid), .left_ready(l_ready),
        .right_score(r_score), .right_index(r_index), .right_valid(r_valid), .right_ready(r_ready),
        .out_score(m_score), .out_index(m_index), .out_valid(m_valid), .out_ready(m_ready),
        .out_last(m_last), .done_valid(m_done), .done_ready(m_done_ready), .error_code(m_error));
    end endgenerate

    logic [31:0] scores [0:4*MAX_N-1], run_score [0:64*MAX_N-1], expected_score [0:4*MAX_N-1];
    logic [63:0] run_index [0:64*MAX_N-1], expected_index [0:4*MAX_N-1];
    integer run_count [0:63];
    integer run_address [0:63], run_bytes [0:63], binding_count [0:63], run_batch [0:63], run_arena [0:63];
    logic run_live [0:63];
    integer kinds [0:127], batches [0:127], offsets [0:127], counts [0:127], keeps [0:127];
    integer lefts [0:127], rights [0:127], outputs [0:127];
    integer fd, result_fd, actual_fd, scratch_fd, scanned, cases, scratch_cases, case_number, batch_count, n, k, job_count;
    integer arena_bytes, binding_runs;
    integer j, b, job, sent, received, left_sent, right_sent, cycles, total_cycles = 0;
    logic accepted, left_accepted, right_accepted;
    logic [31:0] random_state = 32'hcafe1234;
    always @(posedge clk) random_state <= {random_state[30:0], random_state[31] ^ random_state[21] ^ random_state[1] ^ random_state[0]};

    logic mm_start = 0, mm_ready, mm_done, mm_done_ready = 0, mm_operation = 0;
    logic [3:0] mm_error;
    logic [31:0] mm_left_base, mm_left_bytes, mm_left_count, mm_right_base, mm_right_bytes, mm_right_count;
    logic [31:0] mm_destination_base, mm_destination_bytes, mm_keep;
    logic [63:0] mm_job, mm_done_job, mm_limit;
    logic [31:0] mm_read_address, mm_write_address;
    logic mm_read_valid, mm_read_ready, mm_response_valid = 0, mm_response_ready;
    logic [511:0] mm_read_data, mm_write_data;
    logic [63:0] mm_write_enable, mm_fence_job, mm_response_job;
    logic mm_write_valid, mm_write_ready, mm_fence_valid, mm_fence_ready;
    logic mm_fence_response = 0, mm_fence_response_ready;
    integer mm_reads = 0, mm_writes = 0;
    generate if (USE_MEMORY_MERGE) begin : memory_merges
        memory_stage dut(
            .clk(clk), .rst_n(rst_n), .operation_merge(mm_operation), .start_valid(mm_start), .start_ready(mm_ready),
            .index_base({32'd0, offsets[job]}), .score_element_bytes(3'd4),
            .job_id(mm_job), .index_limit(mm_limit), .left_base(mm_left_base), .left_bytes(mm_left_bytes), .left_count(mm_left_count),
            .right_base(mm_right_base), .right_bytes(mm_right_bytes), .right_count(mm_right_count),
            .destination_base(mm_destination_base), .destination_bytes(mm_destination_bytes), .keep_count(mm_keep),
            .read_address(mm_read_address), .read_valid(mm_read_valid), .read_ready(mm_read_ready), .read_data(mm_read_data),
            .read_response_valid(mm_response_valid), .read_response_ready(mm_response_ready), .read_error(1'b0),
            .write_address(mm_write_address), .write_data(mm_write_data), .write_enable(mm_write_enable),
            .write_valid(mm_write_valid), .write_ready(mm_write_ready),
            .fence_valid(mm_fence_valid), .fence_ready(mm_fence_ready), .fence_job_id(mm_fence_job),
            .fence_response_valid(mm_fence_response), .fence_response_ready(mm_fence_response_ready),
            .fence_response_job_id(mm_response_job), .fence_error(1'b0), .done_valid(mm_done), .done_ready(mm_done_ready),
            .done_job_id(mm_done_job), .error_code(mm_error));
    end else begin
        assign mm_read_valid = 0; assign mm_write_valid = 0; assign mm_fence_valid = 0;
        assign mm_ready = 0; assign mm_done = 0; assign mm_error = 0;
    end endgenerate

    logic mm_read_pending = 0, mm_write_pending = 0, mm_fence_pending = 0;
    logic [31:0] mm_held_read, mm_held_write;
    logic [511:0] mm_held_data;
    logic [63:0] mm_held_mask;
    integer mm_read_delay = 0, mm_write_delay = 0, mm_p;
    assign mm_read_ready = !mm_read_pending && random_state[4];
    assign mm_write_ready = !mm_write_pending && random_state[5];
    assign mm_fence_ready = !mm_fence_pending;
    always @(posedge clk) if (rst_n && USE_MEMORY_MERGE) begin
        if (mm_read_valid && mm_read_ready) begin
            if (mm_read_address[5:0] || !(
                (mm_read_address >= mm_left_base && mm_read_address+64 <= mm_left_base+mm_left_bytes) ||
                (mm_read_address >= mm_right_base && mm_read_address+64 <= mm_right_base+mm_right_bytes)))
                $fatal(1, "planned merge read exceeds bound run");
            mm_read_pending <= 1; mm_held_read <= mm_read_address; mm_read_delay <= 1+random_state[9:6];
            mm_reads <= mm_reads + 1;
        end
        if (mm_read_pending && !mm_response_valid) begin
            if (mm_read_delay != 0) mm_read_delay <= mm_read_delay - 1;
            else begin
                if (kinds[job] == 0) begin
                    for (mm_p = 0; mm_p < 16; mm_p = mm_p+1)
                        mm_read_data[mm_p*32 +: 32] <= scores[(mm_held_read-SCORE_ARRAY_BASE)/4+mm_p];
                end else begin
                    for (mm_p = 0; mm_p < 4; mm_p = mm_p + 1)
                        mm_read_data[mm_p*128 +: 128] <= {run_index[mm_held_read/16+mm_p], 32'd0, run_score[mm_held_read/16+mm_p]};
                end
                mm_response_valid <= 1;
            end
        end
        if (mm_response_valid && mm_response_ready) begin mm_response_valid <= 0; mm_read_pending <= 0; end
        if (mm_write_valid && mm_write_ready) begin
            if (mm_write_address[5:0] || mm_write_address < mm_destination_base ||
                mm_write_address+64 > mm_destination_base+mm_destination_bytes)
                $fatal(1, "planned merge write exceeds bound run");
            mm_write_pending <= 1; mm_held_write <= mm_write_address; mm_held_data <= mm_write_data;
            mm_held_mask <= mm_write_enable; mm_write_delay <= 5+random_state[12:10]; mm_writes <= mm_writes+1;
        end
        if (mm_write_pending) begin
            if (mm_write_delay != 0) mm_write_delay <= mm_write_delay-1;
            else begin
                for (mm_p = 0; mm_p < 4; mm_p = mm_p + 1) begin
                    if (mm_held_mask[mm_p*16 +: 16] == 16'hffff) begin
                        if (mm_held_data[mm_p*128+32 +: 32] != 0) $fatal(1, "packed reserved field nonzero");
                        run_score[mm_held_write/16+mm_p] <= mm_held_data[mm_p*128 +: 32];
                        run_index[mm_held_write/16+mm_p] <= mm_held_data[mm_p*128+64 +: 64];
                    end else if (mm_held_mask[mm_p*16 +: 16] != 0) $fatal(1, "partial packed record write");
                end
                mm_write_pending <= 0;
            end
        end
        if (mm_fence_valid && mm_fence_ready) begin
            if (mm_fence_job != mm_job || mm_read_pending) $fatal(1, "planned merge fence ownership");
            mm_fence_pending <= 1;
        end
        if (mm_fence_pending && !mm_write_pending && !mm_fence_response) begin
            mm_fence_response <= 1; mm_response_job <= mm_job;
        end
        if (mm_fence_response && mm_fence_response_ready) begin mm_fence_response <= 0; mm_fence_pending <= 0; end
        if (mm_done && (mm_read_pending || mm_write_pending || mm_fence_pending)) $fatal(1, "planned merge not drained");
    end

    function automatic integer slot(input integer run_id, position);
        slot = run_address[run_id] / 16 + position;
    endfunction
    task automatic reserve_output(input integer run_id);
        begin
            if (run_id < 0 || run_id >= binding_runs || run_live[run_id] ||
                run_batch[run_id] != batches[job] || binding_count[run_id] != keeps[job])
                $fatal(1, "invalid output run binding");
            for (integer other = 0; other < binding_runs; other = other + 1)
                if (run_live[other] && run_address[run_id] < run_address[other]+run_bytes[other] &&
                    run_address[other] < run_address[run_id]+run_bytes[run_id])
                    $fatal(1, "output overwrites a live scratch interval");
            run_live[run_id] = 1;
        end
    endtask

    task automatic sort_job;
        begin
            reserve_output(outputs[job]);
            t_count = counts[job]; t_keep = keeps[job]; t_base = offsets[job];
            sent = 0; received = 0; accepted = 0; cycles = 0;
            @(negedge clk); t_start = 1;
            @(posedge clk); @(negedge clk); t_start = 0;
            while (!t_done) begin
                if (!t_in_valid || accepted) begin
                    t_in_valid = sent < t_count && random_state[0];
                    if (sent < t_count) t_in_score = scores[batches[job]*MAX_N + offsets[job] + sent];
                end
                t_ready = random_state[2];
                @(posedge clk);
                accepted = t_in_valid && t_in_ready;
                if (accepted) sent = sent + 1;
                if (t_valid && t_ready) begin
                    if (received >= t_keep) $fatal(1, "tile emitted excess records");
                    run_score[slot(outputs[job], received)] = t_score;
                    run_index[slot(outputs[job], received)] = t_index;
                    received = received + 1;
                end
                cycles = cycles + 1;
                if (cycles > 200000) $fatal(1, "planned tile watchdog");
                @(negedge clk);
            end
            if (t_error != 0 || sent != t_count || received != t_keep) $fatal(1, "planned tile failed");
            run_count[outputs[job]] = received;
            t_in_valid = 0; t_ready = 0; t_done_ready = 1;
            @(posedge clk); @(negedge clk); t_done_ready = 0;
            total_cycles = total_cycles + cycles;
        end
    endtask

    task automatic merge_job;
        begin
            if (!run_live[lefts[job]] || !run_live[rights[job]] ||
                run_arena[lefts[job]] != run_arena[rights[job]] ||
                run_arena[lefts[job]] == run_arena[outputs[job]])
                $fatal(1, "invalid physical merge input arenas");
            reserve_output(outputs[job]);
            l_count = run_count[lefts[job]]; r_count = run_count[rights[job]]; m_keep = keeps[job];
            left_sent = 0; right_sent = 0; received = 0; cycles = 0;
            left_accepted = 0; right_accepted = 0;
            @(negedge clk); m_start = 1;
            @(posedge clk); @(negedge clk); m_start = 0;
            while (!m_done) begin
                if (!l_valid || left_accepted) begin
                    l_valid = left_sent < l_count && random_state[0];
                    l_score = run_score[slot(lefts[job], left_sent)];
                    l_index = run_index[slot(lefts[job], left_sent)];
                end
                if (!r_valid || right_accepted) begin
                    r_valid = right_sent < r_count && random_state[1];
                    r_score = run_score[slot(rights[job], right_sent)];
                    r_index = run_index[slot(rights[job], right_sent)];
                end
                m_ready = random_state[2];
                @(posedge clk);
                left_accepted = l_valid && l_ready; right_accepted = r_valid && r_ready;
                if (left_accepted) left_sent = left_sent + 1;
                if (right_accepted) right_sent = right_sent + 1;
                if (m_valid && m_ready) begin
                    if (received >= m_keep) $fatal(1, "merge emitted excess records");
                    run_score[slot(outputs[job], received)] = m_score;
                    run_index[slot(outputs[job], received)] = m_index;
                    received = received + 1;
                end
                cycles = cycles + 1;
                if (cycles > 20000) $fatal(1, "planned merge watchdog");
                @(negedge clk);
            end
            if (m_error != 0 || left_sent != l_count || right_sent != r_count || received != m_keep)
                $fatal(1, "planned merge failed or did not drain");
            run_count[outputs[job]] = received;
            run_live[lefts[job]] = 0; run_live[rights[job]] = 0;
            l_valid = 0; r_valid = 0; m_ready = 0; m_done_ready = 1;
            @(posedge clk); @(negedge clk); m_done_ready = 0;
            total_cycles = total_cycles + cycles;
        end
    endtask

    task automatic memory_merge_job;
        begin
            if (kinds[job] == 1 && (!run_live[lefts[job]] || !run_live[rights[job]] ||
                run_arena[lefts[job]] != run_arena[rights[job]] ||
                run_arena[lefts[job]] == run_arena[outputs[job]])) $fatal(1, "invalid physical memory merge arenas");
            reserve_output(outputs[job]);
            if (kinds[job] == 0) begin
                mm_left_base = SCORE_ARRAY_BASE+(batches[job]*MAX_N+offsets[job])*4;
                mm_left_bytes = (counts[job]*4+63)/64*64; mm_left_count = counts[job];
                mm_right_base = 0; mm_right_bytes = 0; mm_right_count = 0;
            end else begin
                mm_left_base = run_address[lefts[job]]; mm_left_bytes = run_bytes[lefts[job]];
                mm_right_base = run_address[rights[job]]; mm_right_bytes = run_bytes[rights[job]];
                mm_left_count = run_count[lefts[job]]; mm_right_count = run_count[rights[job]];
            end
            mm_destination_base = run_address[outputs[job]]; mm_destination_bytes = run_bytes[outputs[job]];
            mm_keep = keeps[job]; mm_limit = n; mm_job = case_number*128+job+1;
            mm_operation = kinds[job] == 1;
            if (!mm_ready) $fatal(1, "memory merge not ready for next planned job");
            mm_start = 1; @(posedge clk); @(negedge clk); mm_start = 0; cycles = 0;
            while (!mm_done) begin
                mm_operation = random_state[3]; // The accepted engine must stay selected.
                mm_start = random_state[4];     // Busy must reject additional starts.
                @(posedge clk); @(negedge clk); cycles = cycles+1;
                if (cycles > 100000) begin
                    $display("MEMORY_MERGE_DEBUG job=%0d left=%h/%0d right=%h/%0d dst=%h/%0d error=%0d reads=%0d writes=%0d read_pending=%0d write_pending=%0d fence_pending=%0d",
                             job, mm_left_base, mm_left_count, mm_right_base, mm_right_count, mm_destination_base, mm_keep,
                             mm_error, mm_reads, mm_writes, mm_read_pending, mm_write_pending, mm_fence_pending);
                    $fatal(1, "planned memory merge watchdog");
                end
            end
            mm_start = 0;
            if (mm_error || mm_done_job != mm_job) $fatal(1, "planned memory merge failed");
            run_count[outputs[job]] = mm_keep;
            if (kinds[job] == 1) begin run_live[lefts[job]] = 0; run_live[rights[job]] = 0; end
            mm_done_ready = 1; @(posedge clk); @(negedge clk); mm_done_ready = 0;
            total_cycles = total_cycles + cycles;
        end
    endtask

    initial begin
        repeat (5) @(posedge clk);
        @(negedge clk); rst_n = 1;
        fd = $fopen("plan_vectors.txt", "r");
        scratch_fd = $fopen("plan_scratch.txt", "r");
        result_fd = $fopen("selected_indices.txt", "w");
        actual_fd = $fopen("actual_runs.txt", "w");
        if (!fd || !scratch_fd || !result_fd || !actual_fd) $fatal(1, "missing plan vectors/output");
        scanned = $fscanf(fd, "%d\n", cases);
        scanned = $fscanf(scratch_fd, "%d\n", scratch_cases);
        if (cases != scratch_cases) $fatal(1, "scratch plan count differs");
        for (case_number = 0; case_number < cases; case_number = case_number + 1) begin
            scanned = $fscanf(fd, "%d %d %d %d\n", batch_count, n, k, job_count);
            if (scanned != 4 || n > MAX_N || batch_count > 4 || job_count > 128) $fatal(1, "bad plan header");
            scanned = $fscanf(scratch_fd, "%d %d\n", arena_bytes, binding_runs);
            if (scanned != 2 || binding_runs > 64) $fatal(1, "bad scratch binding header");
            for (j = 0; j < binding_runs; j = j + 1) begin
                scanned = $fscanf(scratch_fd, "%h %d %d %d %d\n", run_address[j], run_bytes[j], binding_count[j], run_batch[j], run_arena[j]);
                if (scanned != 5 || run_address[j] % 64 || run_bytes[j] % 64 || run_bytes[j] > arena_bytes ||
                    (run_address[j] + run_bytes[j]) / 16 >= 64*MAX_N || binding_count[j]*16 > run_bytes[j])
                    $fatal(1, "scratch binding exceeds memory");
                run_live[j] = 0;
            end
            for (b = 0; b < batch_count; b = b + 1)
                for (j = 0; j < n; j = j + 1) scanned = $fscanf(fd, "%h\n", scores[b*MAX_N+j]);
            for (j = 0; j < job_count; j = j + 1)
                scanned = $fscanf(fd, "%d %d %d %d %d %d %d %d\n", kinds[j], batches[j], offsets[j], counts[j], keeps[j], lefts[j], rights[j], outputs[j]);
            for (b = 0; b < batch_count; b = b + 1)
                for (j = 0; j < k; j = j + 1)
                    scanned = $fscanf(fd, "%h %h\n", expected_score[b*MAX_N+j], expected_index[b*MAX_N+j]);
            for (job = 0; job < job_count; job = job + 1) begin
                if (kinds[job] == 0) begin
                    if (USE_MEMORY_MERGE) memory_merge_job(); else sort_job();
                end
                else if (kinds[job] == 1) begin
                    if (USE_MEMORY_MERGE) memory_merge_job(); else merge_job();
                end
                else begin
                    if (run_count[lefts[job]] != k) $fatal(1, "final run size mismatch");
                    $fwrite(result_fd, "%0d %0d %0d %0d\n", case_number, batches[job], n, k);
                    $fwrite(actual_fd, "%0d %0d %0d %0d\n", case_number, batches[job], n, k);
                    for (j = 0; j < k; j = j + 1) begin
                        $fwrite(actual_fd, "%h %h\n", run_score[slot(lefts[job], j)], run_index[slot(lefts[job], j)]);
                        $fwrite(result_fd, "%h\n", run_index[slot(lefts[job], j)]);
                    end
                    $fflush(actual_fd); $fflush(result_fd);
                    for (j = 0; j < k; j = j + 1) begin
                        if (run_score[slot(lefts[job], j)] !== expected_score[batches[job]*MAX_N+j] ||
                            run_index[slot(lefts[job], j)] !== expected_index[batches[job]*MAX_N+j])
                            $fatal(1, "global TopK mismatch case=%0d batch=%0d rank=%0d", case_number, batches[job], j);
                    end
                    run_live[lefts[job]] = 0;
                end
            end
            $display("PLAN case=%0d batches=%0d n=%0d k=%0d jobs=%0d PASS", case_number, batch_count, n, k, job_count);
        end
        $fclose(fd); $fclose(scratch_fd); $fclose(result_fd); $fclose(actual_fd);
        $display("TOPK_PLAN_PASS cycles=%0d memory_merge=%0d reads=%0d writes=%0d", total_cycles, USE_MEMORY_MERGE, mm_reads, mm_writes);
        $finish;
    end
    initial begin #100000000; $fatal(1, "plan suite watchdog"); end
endmodule
