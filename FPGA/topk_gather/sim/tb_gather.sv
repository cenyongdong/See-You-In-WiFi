`timescale 1ns/1ps
module tb_gather #(parameter integer USE_COALESCER = 0, USE_FUSION = 0, USE_MEMORY_OUTPUT = 0, USE_SORTED_RUN = 0, USE_RECORD_FILE = 0);
    localparam integer MEMORY_BYTES = 1048576;
    localparam integer SRC_BASE = 64;
    localparam integer DST_BASE = 524288;
    localparam integer SCORE_BASE = MEMORY_BYTES - (USE_SORTED_RUN ? 65536 : 2048);
    localparam integer SCORE_OUTPUT = MEMORY_BYTES - (USE_SORTED_RUN ? 32768 : 4096);
    localparam integer INDEX_OUTPUT = MEMORY_BYTES - (USE_SORTED_RUN ? 16384 : 8192);
    logic clk = 0, rst_n = 0;
    always #5 clk = ~clk;
    logic start_valid = 0, start_ready, index_valid = 0, index_ready;
    logic [63:0] job_id = 0, index_data, done_job_id, fence_job_id, fence_response_job_id;
    logic [31:0] input_count, keep_count, channels, source_bytes, destination_bytes;
    logic [31:0] source_row_stride, source_block_stride, destination_row_stride, destination_block_stride;
    logic [2:0] element_bytes;
    logic source_blocked16, destination_blocked16;
    logic [31:0] read_address, write_address, read_transactions, write_transactions;
    logic [511:0] read_data = 0, write_data;
    logic [63:0] write_enable;
    logic read_valid, read_ready, read_response_valid = 0, read_response_ready, read_error = 0;
    logic write_valid, write_ready, fence_valid, fence_ready;
    logic fence_response_valid, fence_response_ready, fence_error;
    logic done_valid, done_ready = 0;
    logic [3:0] error_code;
    logic [31:0] record_score;
    logic [63:0] record_index;
    logic record_valid, record_ready = 0, record_last;
    integer fault = 0, read_count = 0;
    logic [31:0] score_bytes;
    logic [31:0] score_address;
    logic [31:0] selected_score_bytes, selected_index_bytes, selected_score_base, selected_index_base;
    assign score_bytes = fault == 11 ? 64 : ((USE_SORTED_RUN ? keep_count*16 : input_count*2) + 63) / 64 * 64;
    assign score_address = fault == 10 ? DST_BASE : SCORE_BASE;
    assign selected_score_bytes = fault == 13 ? 64 : (keep_count * 4 + 63) / 64 * 64;
    assign selected_index_bytes = fault == 14 ? 64 : (keep_count * 8 + 63) / 64 * 64;
    assign selected_score_base = fault == 12 ? SRC_BASE : SCORE_OUTPUT;
    assign selected_index_base = fault == 15 ? DST_BASE : INDEX_OUTPUT;
    generate if (!USE_FUSION) begin : gather_only
    gather_engine dut(
        .clk(clk), .rst_n(rst_n), .abort_job(1'b0), .start_valid(start_valid), .start_ready(start_ready),
        .job_id(job_id), .input_count(input_count), .keep_count(keep_count), .channels(channels),
        .element_bytes(element_bytes), .source_blocked16(source_blocked16),
        .destination_blocked16(destination_blocked16), .source_base(SRC_BASE), .source_bytes(source_bytes),
        .source_row_stride(source_row_stride), .source_block_stride(source_block_stride),
        .destination_base(DST_BASE), .destination_bytes(destination_bytes),
        .destination_row_stride(destination_row_stride), .destination_block_stride(destination_block_stride),
        .index_data(index_data), .index_valid(index_valid), .index_ready(index_ready),
        .read_address(read_address), .read_valid(read_valid), .read_ready(read_ready), .read_data(read_data),
        .read_response_valid(read_response_valid), .read_response_ready(read_response_ready), .read_error(read_error),
        .write_address(write_address), .write_data(write_data), .write_enable(write_enable),
        .write_valid(write_valid), .write_ready(write_ready), .fence_valid(fence_valid), .fence_ready(fence_ready),
        .fence_job_id(fence_job_id), .fence_response_valid(fence_response_valid),
        .fence_response_ready(fence_response_ready), .fence_response_job_id(fence_response_job_id),
        .fence_error(fence_error), .done_valid(done_valid), .done_ready(done_ready), .done_job_id(done_job_id),
        .error_code(error_code), .read_transactions(read_transactions), .write_transactions(write_transactions));
        assign record_valid = 0;
        assign record_score = 0; assign record_index = 0; assign record_last = 0;
    end else if (!USE_MEMORY_OUTPUT) begin : fused
        assign index_ready = 0;
        topk_gather_tile #(.INPUT_IS_SORTED_RUN(USE_SORTED_RUN)) dut(
            .clk(clk), .rst_n(rst_n), .start_valid(start_valid), .start_ready(start_ready),
            .job_id(job_id), .input_count(input_count), .keep_count(keep_count), .channels(channels),
            .score_base(score_address), .score_bytes(score_bytes), .score_element_bytes(3'd2),
            .record_score(record_score), .record_index(record_index), .record_valid(record_valid),
            .record_ready(record_ready), .record_last(record_last),
            .element_bytes(element_bytes), .source_blocked16(source_blocked16),
            .destination_blocked16(destination_blocked16), .source_base(SRC_BASE), .source_bytes(source_bytes),
            .source_row_stride(source_row_stride), .source_block_stride(source_block_stride),
            .destination_base(DST_BASE), .destination_bytes(destination_bytes),
            .destination_row_stride(destination_row_stride), .destination_block_stride(destination_block_stride),
            .read_address(read_address), .read_valid(read_valid), .read_ready(read_ready), .read_data(read_data),
            .read_response_valid(read_response_valid), .read_response_ready(read_response_ready), .read_error(read_error),
            .write_address(write_address), .write_data(write_data), .write_enable(write_enable),
            .write_valid(write_valid), .write_ready(write_ready), .fence_valid(fence_valid), .fence_ready(fence_ready),
            .fence_job_id(fence_job_id), .fence_response_valid(fence_response_valid),
            .fence_response_ready(fence_response_ready), .fence_response_job_id(fence_response_job_id),
            .fence_error(fence_error), .done_valid(done_valid), .done_ready(done_ready), .done_job_id(done_job_id),
            .error_code(error_code), .read_transactions(read_transactions), .write_transactions(write_transactions));
    end else begin : memory_kernel
        assign index_ready = 0;
        assign record_valid = 0; assign record_score = 0; assign record_index = 0; assign record_last = 0;
        topk_gather_kernel #(.INPUT_IS_SORTED_RUN(USE_SORTED_RUN)) dut(
            .clk(clk), .rst_n(rst_n), .start_valid(start_valid), .start_ready(start_ready), .job_id(job_id),
            .input_count(input_count), .keep_count(keep_count), .channels(channels),
            .score_base(score_address), .score_bytes(score_bytes), .score_element_bytes(3'd2),
            .element_bytes(element_bytes), .source_blocked16(source_blocked16),
            .destination_blocked16(destination_blocked16), .source_base(SRC_BASE), .source_bytes(source_bytes),
            .source_row_stride(source_row_stride), .source_block_stride(source_block_stride),
            .destination_base(DST_BASE), .destination_bytes(destination_bytes),
            .destination_row_stride(destination_row_stride), .destination_block_stride(destination_block_stride),
            .selected_score_base(selected_score_base), .selected_score_bytes(selected_score_bytes),
            .selected_index_base(selected_index_base), .selected_index_bytes(selected_index_bytes),
            .read_address(read_address), .read_valid(read_valid), .read_ready(read_ready), .read_data(read_data),
            .read_response_valid(read_response_valid), .read_response_ready(read_response_ready), .read_error(read_error),
            .write_address(write_address), .write_data(write_data), .write_enable(write_enable),
            .write_valid(write_valid), .write_ready(write_ready), .fence_valid(fence_valid), .fence_ready(fence_ready),
            .fence_job_id(fence_job_id), .fence_response_valid(fence_response_valid),
            .fence_response_ready(fence_response_ready), .fence_response_job_id(fence_response_job_id),
            .fence_error(fence_error), .done_valid(done_valid), .done_ready(done_ready), .done_job_id(done_job_id),
            .error_code(error_code), .read_transactions(read_transactions), .write_transactions(write_transactions));
    end endgenerate

    logic [31:0] bus_write_address;
    logic [511:0] bus_write_data;
    logic [63:0] bus_write_enable, bus_fence_job_id, bus_fence_response_job_id;
    logic bus_write_valid, bus_write_ready, bus_fence_valid, bus_fence_ready;
    logic bus_fence_response_valid = 0, bus_fence_response_ready, bus_fence_error = 0;
    generate if (USE_COALESCER) begin : buffered
        write_coalescer coalescer(
            .clk(clk), .rst_n(rst_n), .write_address(write_address), .write_data(write_data),
            .write_enable(write_enable), .write_valid(write_valid), .write_ready(write_ready),
            .fence_valid(fence_valid), .fence_ready(fence_ready), .fence_job_id(fence_job_id),
            .fence_response_valid(fence_response_valid), .fence_response_ready(fence_response_ready),
            .fence_response_job_id(fence_response_job_id), .fence_error(fence_error),
            .downstream_write_address(bus_write_address), .downstream_write_data(bus_write_data),
            .downstream_write_enable(bus_write_enable), .downstream_write_valid(bus_write_valid),
            .downstream_write_ready(bus_write_ready), .downstream_fence_valid(bus_fence_valid),
            .downstream_fence_ready(bus_fence_ready), .downstream_fence_job_id(bus_fence_job_id),
            .downstream_fence_response_valid(bus_fence_response_valid),
            .downstream_fence_response_ready(bus_fence_response_ready),
            .downstream_fence_response_job_id(bus_fence_response_job_id),
            .downstream_fence_error(bus_fence_error));
    end else begin : unbuffered
        assign bus_write_address = write_address;
        assign bus_write_data = write_data;
        assign bus_write_enable = write_enable;
        assign bus_write_valid = write_valid;
        assign write_ready = bus_write_ready;
        assign bus_fence_valid = fence_valid;
        assign bus_fence_job_id = fence_job_id;
        assign fence_ready = bus_fence_ready;
        assign fence_response_valid = bus_fence_response_valid;
        assign bus_fence_response_ready = fence_response_ready;
        assign fence_response_job_id = bus_fence_response_job_id;
        assign fence_error = bus_fence_error;
    end endgenerate

    byte memory [0:MEMORY_BYTES-1];
    byte source_reference [0:524287], expected [0:524287];
    logic [63:0] indices [0:4095];
    logic [31:0] actual_run_scores [0:4095];
    logic [63:0] actual_run_index;
    logic [511:0] queue_data [0:8191];
    logic [63:0] queue_enable [0:8191];
    logic [31:0] queue_address [0:8191];
    integer queue_read = 0, queue_write = 0, commit_delay = 0;
    integer read_delay = 0, fence_delay = 0;
    logic read_pending = 0, fence_pending = 0, stale_sent = 0, visibility_ack = 0;
    logic [31:0] held_read_address;
    logic [31:0] random_state = 32'hcafe3301;
    integer p;
    assign read_ready = !read_pending && random_state[0];
    assign bus_write_ready = random_state[1] && queue_write < 8192;
    assign bus_fence_ready = !fence_pending;

    // Memory model deliberately separates write acceptance from visibility.
    always @(posedge clk) begin
        if (rst_n) begin
            random_state <= {random_state[30:0], random_state[31] ^ random_state[21] ^ random_state[1] ^ random_state[0]};
            if (read_valid && read_ready) begin
                if (read_address[5:0] != 0 ||
                    !((read_address >= SRC_BASE && read_address + 64 <= SRC_BASE + source_bytes) ||
                      (USE_FUSION && read_address >= SCORE_BASE && read_address + 64 <= SCORE_BASE + score_bytes)))
                    $fatal(1, "read outside allocation: %h", read_address);
                held_read_address <= read_address;
                read_pending <= 1;
                read_delay <= 1 + random_state[7:4];
                read_count <= read_count + 1;
            end
            if (read_pending && !read_response_valid) begin
                if (read_delay != 0) read_delay <= read_delay - 1;
                else begin
                    for (p = 0; p < 64; p = p + 1) read_data[p*8 +: 8] <= memory[held_read_address+p];
                    read_response_valid <= 1;
                    read_error <= (fault == 2 && read_count == 2) ||
                                  (fault == 8 && held_read_address < SCORE_BASE) ||
                                  (fault == 17 && read_count == 30);
                end
            end
            if (read_response_valid && read_response_ready) begin
                read_response_valid <= 0; read_pending <= 0; read_error <= 0;
            end
            if (bus_write_valid && bus_write_ready) begin
                if (bus_write_address[5:0] != 0 || bus_write_enable == 0 ||
                    !((bus_write_address >= DST_BASE && bus_write_address + 64 <= DST_BASE + destination_bytes) ||
                      (USE_MEMORY_OUTPUT && bus_write_address >= SCORE_OUTPUT &&
                       bus_write_address + 64 <= SCORE_OUTPUT + selected_score_bytes) ||
                      (USE_MEMORY_OUTPUT && bus_write_address >= INDEX_OUTPUT &&
                       bus_write_address + 64 <= INDEX_OUTPUT + selected_index_bytes)))
                    $fatal(1, "write outside allocation or empty mask");
                queue_data[queue_write] <= bus_write_data;
                queue_address[queue_write] <= bus_write_address;
                queue_enable[queue_write] <= bus_write_enable;
                queue_write <= queue_write + 1;
            end
            if (queue_read < queue_write) begin
                if (commit_delay > 0) commit_delay <= commit_delay - 1;
                else begin
                    for (p = 0; p < 64; p = p + 1)
                        if (queue_enable[queue_read][p]) memory[queue_address[queue_read]+p] <= queue_data[queue_read][p*8 +: 8];
                    queue_read <= queue_read + 1;
                    commit_delay <= 5 + random_state[8:4];
                end
            end
            if (bus_fence_valid && bus_fence_ready) begin
                if (bus_fence_job_id != job_id) $fatal(1, "buffer changed job identity");
                fence_pending <= 1;
                fence_delay <= fault == 7 ? 1000 : 30;
            end
            if (fence_pending && !bus_fence_response_valid) begin
                if (fault == 3 && !stale_sent) begin
                    bus_fence_response_valid <= 1;
                    bus_fence_response_job_id <= job_id - 1;
                    stale_sent <= 1;
                end else if (fence_delay > 0) fence_delay <= fence_delay - 1;
                else if (queue_read == queue_write && !read_pending) begin
                    bus_fence_response_valid <= 1;
                    bus_fence_response_job_id <= job_id;
                    bus_fence_error <= fault == 6;
                end
            end
            if (bus_fence_response_valid && bus_fence_response_ready) begin
                bus_fence_response_valid <= 0;
                if (bus_fence_response_job_id == job_id) begin
                    fence_pending <= 0;
                    visibility_ack <= 1;
                end
            end
            if (done_valid && (error_code != 1 || read_count != 0 || queue_write != 0) &&
                (!visibility_ack || queue_read != queue_write || read_pending))
                $fatal(1, "DONE before writes became visible and requests drained");
        end
    end

    integer fd, records_fd, cases, case_number, scanned, j, b, sent, cycles, expected_error;
    integer size_value, source_layout, destination_layout;
    integer record_count;
    logic [15:0] half_score;
    logic [31:0] expected_score_word;
    logic [63:0] expected_index_word;
    logic [511:0] word;
    logic accepted, stalled_write, stalled_read, stalled_record;
    logic [607:0] held_write;
    logic [31:0] held_request_address;
    logic [96:0] held_record;
    function automatic logic [15:0] integer_half(input integer value);
        integer leading;
        begin
            leading = 0;
            for (integer bit_number = 0; bit_number < 10; bit_number = bit_number + 1)
                if (value & (1 << bit_number)) leading = bit_number;
            integer_half = ((leading + 15) << 10) | ((value - (1 << leading)) << (10 - leading));
        end
    endfunction
    function automatic logic [31:0] integer_float(input integer value);
        integer leading;
        begin
            leading = 0;
            for (integer bit_number = 0; bit_number < 23; bit_number = bit_number + 1)
                if (value & (1 << bit_number)) leading = bit_number;
            integer_float = ((leading + 127) << 23) | ((value - (1 << leading)) << (23 - leading));
        end
    endfunction
    task automatic save_output(input integer case_id, port_id, base, length);
        integer output_fd;
        begin
            output_fd = $fopen($sformatf("actual_case_%0d_port_%0d.bin", case_id, port_id), "wb");
            if (!output_fd) $fatal(1, "cannot preserve actual output");
            for (integer byte_number = 0; byte_number < length; byte_number = byte_number + 1)
                $fwrite(output_fd, "%c", memory[base+byte_number]);
            $fclose(output_fd);
        end
    endtask
    initial begin
        for (j = 0; j < MEMORY_BYTES; j = j + 1) memory[j] = 8'ha5;
        repeat (5) @(posedge clk);
        @(negedge clk); rst_n = 1;
        fd = $fopen("gather_vectors.txt", "r");
        if (!fd) $fatal(1, "missing gather vectors");
        if (USE_RECORD_FILE) begin
            records_fd = $fopen("run_records.txt", "r");
            if (!records_fd) $fatal(1, "missing actual completed run");
        end
        scanned = $fscanf(fd, "%d\n", cases);
        for (case_number = 0; case_number < cases; case_number = case_number + 1) begin
            scanned = $fscanf(fd, "%d %d %d %d %d %d %d %d %d %d\n", input_count, keep_count, channels,
                size_value, source_layout, destination_layout, source_bytes, destination_bytes, fault, expected_error);
            if (scanned != 10) $fatal(1, "invalid gather header");
            #1; // Let descriptor-derived allocation sizes settle before initialization.
            if (keep_count > 4096 || source_bytes + SRC_BASE >= DST_BASE ||
                destination_bytes + DST_BASE + 64 > MEMORY_BYTES)
                $fatal(1, "test vector exceeds simulation memory");
            element_bytes = size_value;
            source_blocked16 = source_layout;
            destination_blocked16 = destination_layout;
            source_row_stride = (source_layout ? 16 : channels) * size_value;
            destination_row_stride = (destination_layout ? 16 : channels) * size_value;
            source_block_stride = input_count * source_row_stride;
            destination_block_stride = keep_count * destination_row_stride;
            for (j = 0; j < keep_count; j = j + 1) scanned = $fscanf(fd, "%h\n", indices[j]);
            if (USE_SORTED_RUN) begin
                // The completed plan ABI is FP32 bits, zero reserved, uint64 index.
                for (j = 0; j < score_bytes; j = j + 1) memory[SCORE_BASE+j] = 0;
                for (j = 0; j < keep_count; j = j + 1) begin
                    expected_score_word = fault == 16 ? (j[0] ? 32'h80000000 : 0) : integer_float(keep_count-j);
                    if (USE_RECORD_FILE) begin
                        scanned = $fscanf(records_fd, "%h %h\n", actual_run_scores[j], actual_run_index);
                        if (scanned != 2 || actual_run_index !== indices[j]) $fatal(1, "actual run record mismatch");
                        expected_score_word = actual_run_scores[j];
                    end
                    for (b = 0; b < 4; b = b + 1) memory[SCORE_BASE+16*j+b] = expected_score_word[b*8 +: 8];
                    for (b = 0; b < 8; b = b + 1) memory[SCORE_BASE+16*j+8+b] = indices[j][b*8 +: 8];
                end
                if (fault == 9) begin
                    memory[SCORE_BASE+16*(keep_count-1)+2] = 8'hc0;
                    memory[SCORE_BASE+16*(keep_count-1)+3] = 8'h7f;
                end
                if (fault == 18) memory[SCORE_BASE+16*(keep_count-1)+4] = 1;
            end else if (USE_FUSION) begin
                for (j = 0; j < score_bytes; j = j + 1) memory[SCORE_BASE+j] = 0;
                for (j = 0; j < input_count; j = j + 1) memory[SCORE_BASE+2*j+1] = 8'hbc; // -1
                for (j = 0; j < keep_count; j = j + 1) begin
                    half_score = integer_half(keep_count - j);
                    memory[SCORE_BASE+2*indices[j]] = half_score[7:0];
                    memory[SCORE_BASE+2*indices[j]+1] = half_score[15:8];
                end
                if (fault == 16)
                    for (j = 0; j < input_count; j = j + 1) begin
                        memory[SCORE_BASE+2*j] = 0;
                        memory[SCORE_BASE+2*j+1] = j[0] ? 8'h80 : 8'h00;
                    end
                if (fault == 9) begin // A nonfinite score invalidates the entire job.
                    memory[SCORE_BASE+2*(input_count-1)] = 8'h00;
                    memory[SCORE_BASE+2*(input_count-1)+1] = 8'h7e;
                end
            end
            for (j = 0; j < source_bytes; j = j + 64) begin
                scanned = $fscanf(fd, "%h\n", word);
                for (b = 0; b < 64; b = b + 1) begin memory[SRC_BASE+j+b] = word[b*8 +: 8]; source_reference[j+b] = word[b*8 +: 8]; end
            end
            for (j = 0; j < destination_bytes; j = j + 64) begin
                scanned = $fscanf(fd, "%h\n", word);
                for (b = 0; b < 64; b = b + 1) begin expected[j+b] = word[b*8 +: 8]; memory[DST_BASE+j+b] = 8'ha5; end
            end
            for (j = 0; j < 64; j = j + 1) memory[DST_BASE+destination_bytes+j] = 8'ha5;
            if (USE_MEMORY_OUTPUT) begin
                for (j = 0; j < selected_score_bytes + 128; j = j + 1) memory[SCORE_OUTPUT-64+j] = 8'ha5;
                for (j = 0; j < selected_index_bytes + 128; j = j + 1) memory[INDEX_OUTPUT-64+j] = 8'ha5;
            end
            if (fault == 4) source_row_stride = source_row_stride + 4;
            if (fault == 5) source_bytes = 64;
            @(negedge clk);
            queue_read = 0; queue_write = 0; read_count = 0;
            visibility_ack = 0; stale_sent = 0; stalled_write = 0;
            stalled_read = 0; stalled_record = 0;
            bus_fence_error = 0;
            job_id = job_id + 1; sent = 0; cycles = 0; accepted = 0;
            record_count = 0;
            if (!start_ready) $fatal(1, "gather not idle");
            start_valid = 1;
            @(posedge clk); @(negedge clk); start_valid = 0;
            while (!done_valid) begin
                record_ready = random_state[10];
                if (!index_valid || accepted) begin
                    index_valid = sent < keep_count && random_state[9];
                    if (sent < keep_count) index_data = indices[sent];
                end
                @(posedge clk);
                if (stalled_read && (!read_valid || read_address !== held_request_address))
                    $fatal(1, "read request changed while backpressured");
                stalled_read = read_valid && !read_ready;
                held_request_address = read_address;
                if (stalled_record && (!record_valid || {record_last, record_score, record_index} !== held_record))
                    $fatal(1, "selected record changed while backpressured");
                stalled_record = record_valid && !record_ready;
                held_record = {record_last, record_score, record_index};
                if (stalled_write && (!write_valid || {write_address, write_enable, write_data} !== held_write))
                    $fatal(1, "write changed while backpressured");
                stalled_write = write_valid && !write_ready;
                held_write = {write_address, write_enable, write_data};
                accepted = index_valid && index_ready;
                if (accepted) sent = sent + 1;
                if (record_valid && record_ready) begin
                    if (record_count >= keep_count || record_index !== indices[record_count] ||
                        record_score !== integer_float(keep_count - record_count) ||
                        record_last != (record_count + 1 == keep_count))
                        $fatal(1, "fused score/index mismatch");
                    record_count = record_count + 1;
                end
                cycles = cycles + 1;
                if (cycles > 1000000) $fatal(1, "gather watchdog");
                @(negedge clk);
            end
            index_valid = 0;
            if (fault == 17 && queue_write == 0) $fatal(1, "late read failure did not exercise partial writes");
            save_output(case_number, 0, DST_BASE, destination_bytes);
            if (USE_MEMORY_OUTPUT) begin
                save_output(case_number, 1, SCORE_OUTPUT, selected_score_bytes);
                save_output(case_number, 2, INDEX_OUTPUT, selected_index_bytes);
            end
            if (done_job_id != job_id || error_code != expected_error ||
                (!USE_FUSION && sent != (expected_error == 1 ? 0 : keep_count)))
                $fatal(1, "gather completion mismatch case=%0d error=%0d expected=%0d", case_number, error_code, expected_error);
            if (fault == 0 || fault == 3 || fault == 7 || fault == 16)
                for (j = 0; j < destination_bytes; j = j + 1)
                    if (memory[DST_BASE+j] !== expected[j])
                        $fatal(1, "gather payload mismatch case=%0d byte=%0d got=%h expected=%h", case_number, j, memory[DST_BASE+j], expected[j]);
            if (USE_FUSION && !USE_MEMORY_OUTPUT && (fault == 0 || fault == 3 || fault == 7) && record_count != keep_count)
                $fatal(1, "missing fused records");
            if (USE_MEMORY_OUTPUT) begin
                if (fault == 0 || fault == 3 || fault == 7 || fault == 16) begin
                    for (j = 0; j < keep_count; j = j + 1) begin
                        expected_score_word = fault == 16 ? (j[0] ? 32'h80000000 : 0) : integer_float(keep_count-j);
                        if (USE_RECORD_FILE) expected_score_word = actual_run_scores[j];
                        expected_index_word = indices[j];
                        for (b = 0; b < 4; b = b + 1)
                            if (memory[SCORE_OUTPUT+4*j+b] !== expected_score_word[b*8 +: 8])
                                $fatal(1, "selected score writeback mismatch case=%0d index=%0d", case_number, j);
                        for (b = 0; b < 8; b = b + 1)
                            if (memory[INDEX_OUTPUT+8*j+b] !== expected_index_word[b*8 +: 8])
                                $fatal(1, "selected index writeback mismatch case=%0d index=%0d", case_number, j);
                    end
                    for (j = keep_count*4; j < selected_score_bytes; j = j + 1)
                        if (memory[SCORE_OUTPUT+j] !== 8'ha5)
                            $fatal(1, "score allocation tail changed case=%0d byte=%0d actual=%h", case_number, j, memory[SCORE_OUTPUT+j]);
                    for (j = keep_count*8; j < selected_index_bytes; j = j + 1)
                        if (memory[INDEX_OUTPUT+j] !== 8'ha5) $fatal(1, "index allocation tail changed");
                end
                for (j = 0; j < 64; j = j + 1)
                    if (memory[SCORE_OUTPUT-64+j] !== 8'ha5 || memory[SCORE_OUTPUT+selected_score_bytes+j] !== 8'ha5 ||
                        memory[INDEX_OUTPUT-64+j] !== 8'ha5 || memory[INDEX_OUTPUT+selected_index_bytes+j] !== 8'ha5)
                        $fatal(1, "record writeback guard overwritten");
            end
            for (j = 0; j < source_bytes; j = j + 1)
                if (memory[SRC_BASE+j] !== source_reference[j]) $fatal(1, "source overwritten");
            for (j = 0; j < 64; j = j + 1)
                if (memory[DST_BASE+destination_bytes+j] !== 8'ha5 || memory[DST_BASE-64+j] !== 8'ha5)
                    $fatal(1, "output guard overwritten");
            $display("GATHER case=%0d n=%0d k=%0d c=%0d bytes=%0d layouts=%0d/%0d cycles=%0d reads=%0d writes=%0d bus_writes=%0d error=%0d",
                case_number, input_count, keep_count, channels, element_bytes, source_layout, destination_layout,
                cycles, read_transactions, write_transactions, queue_write, error_code);
            repeat (2) @(posedge clk);
            @(negedge clk); done_ready = 1;
            @(posedge clk); @(negedge clk); done_ready = 0;
        end
        $fclose(fd);
        if (USE_RECORD_FILE) $fclose(records_fd);
        $display("TOPK_GATHER_PASS cases=%0d", cases);
        $finish;
    end
    initial begin #200000000; $fatal(1, "gather suite watchdog"); end
endmodule
