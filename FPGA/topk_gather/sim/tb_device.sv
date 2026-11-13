`timescale 1ns/1ps
// Full control -> kernel -> AXI -> byte memory -> retained completion test.
// C++ emits register images; an independent CPU full sort emits expected data.
module tb_device #(
    parameter integer GENERIC_SHAPES = 0,
    parameter integer FP16_FLUSH_TO_POSITIVE_ZERO = 0
);
    localparam integer MEMORY_BYTES = GENERIC_SHAPES ? 2097152 : 524288;
    localparam integer DESCRIPTOR_WORDS = GENERIC_SHAPES ? 32 : 22;
    logic clk = 0, rst_n = 0;
    always #5 clk = ~clk;
    logic [7:0] s_axi_awaddr = 0, s_axi_araddr = 0;
    logic s_axi_awvalid = 0, s_axi_awready, s_axi_wvalid = 0, s_axi_wready;
    logic [31:0] s_axi_wdata = 0, s_axi_rdata;
    logic [3:0] s_axi_wstrb = 0;
    logic [1:0] s_axi_bresp, s_axi_rresp;
    logic s_axi_bvalid, s_axi_bready = 0, s_axi_arvalid = 0, s_axi_arready;
    logic s_axi_rvalid, s_axi_rready = 0, irq;
    logic [31:0] m_axi_araddr, m_axi_awaddr;
    logic [7:0] m_axi_arlen, m_axi_awlen;
    logic [2:0] m_axi_arsize, m_axi_awsize;
    logic [1:0] m_axi_arburst, m_axi_awburst;
    logic [3:0] m_axi_arcache, m_axi_arid, m_axi_awcache, m_axi_awid;
    logic m_axi_arvalid, m_axi_arready, m_axi_awvalid, m_axi_awready;
    logic [511:0] m_axi_rdata = 0, m_axi_wdata;
    logic [63:0] m_axi_wstrb;
    logic [1:0] m_axi_rresp = 0, m_axi_bresp = 0;
    logic [3:0] m_axi_rid = 0, m_axi_bid = 0;
    logic m_axi_rlast = 1, m_axi_rvalid = 0, m_axi_rready;
    logic m_axi_wlast, m_axi_wvalid, m_axi_wready, m_axi_bvalid = 0, m_axi_bready;
    topk_gather_device #(.GENERIC_SHAPES(GENERIC_SHAPES),
                        .FP16_FLUSH_TO_POSITIVE_ZERO(FP16_FLUSH_TO_POSITIVE_ZERO)) dut(.*);

    byte memory [0:MEMORY_BYTES-1], expected [0:MEMORY_BYTES-1];
    logic [31:0] descriptor [0:31];
    logic [31:0] rng = 32'hd3301311;
    logic read_pending = 0, aw_pending = 0, w_pending = 0;
    logic [31:0] held_read, held_write;
    logic [511:0] held_data;
    logic [63:0] held_mask;
    integer read_delay = 0, write_delay = 0, reads = 0, writes = 0, responses = 0;
    integer fault = 0, expected_error, case_number = 0, p;
    integer fd, cases, scanned, i, cycles, initialize_memory, input_regions, output_regions, region, region_base, region_bytes;
    logic foreign_sent = 0;
    assign m_axi_arready = !read_pending && rng[0];
    assign m_axi_awready = !aw_pending && !m_axi_bvalid && rng[1];
    assign m_axi_wready = !w_pending && !m_axi_bvalid && rng[2];

    function automatic logic inside_allocation(input logic [31:0] address, base, bytes);
        inside_allocation = address >= base && {1'b0, address}+64 <= {1'b0, base}+bytes;
    endfunction
    function automatic logic output_allocation(input integer address);
        output_allocation =
            (address >= descriptor[14] && address < descriptor[14] + descriptor[15]) ||
            (address >= descriptor[18] && address < descriptor[18] + descriptor[19]) ||
            (address >= descriptor[20] && address < descriptor[20] + descriptor[21]);
    endfunction

    // AW/W are independent; bytes become visible only before the matching B.
    // The first write waits 200 cycles so acceptance cannot masquerade as DONE.
    always @(posedge clk) if (rst_n) begin
        rng <= {rng[30:0], rng[31] ^ rng[21] ^ rng[1] ^ rng[0]};
        if (m_axi_arvalid && m_axi_arready) begin
            if (m_axi_araddr[5:0] || m_axi_arlen != 0 || m_axi_arsize != 6 ||
                m_axi_arburst != 1 || m_axi_arcache != 0 || m_axi_arid != 0 ||
                !(inside_allocation(m_axi_araddr, descriptor[5], descriptor[6]) ||
                  inside_allocation(m_axi_araddr, descriptor[10], descriptor[11]) ||
                  (GENERIC_SHAPES && descriptor[22] == 1 && inside_allocation(m_axi_araddr, descriptor[23], descriptor[24]))))
                $fatal(1, "invalid peripheral AXI read");
            held_read <= m_axi_araddr; read_pending <= 1;
            read_delay <= 1 + rng[7:4]; reads <= reads + 1;
        end
        if (read_pending && !m_axi_rvalid) begin
            if (read_delay != 0) read_delay <= read_delay - 1;
            else begin
                for (p = 0; p < 64; p = p + 1) m_axi_rdata[p*8 +: 8] <= memory[held_read+p];
                m_axi_rvalid <= 1;
                m_axi_rresp <= (fault == 1 && reads == 2) ||
                              (fault == 2 && reads == 30) ? 2 : 0;
                m_axi_rid <= fault == 4 && !foreign_sent ? 1 : 0;
            end
        end
        if (m_axi_rvalid && m_axi_rready) begin
            m_axi_rvalid <= 0; m_axi_rresp <= 0; m_axi_rid <= 0;
            if (m_axi_rid != 0) begin foreign_sent <= 1; read_delay <= 5; end
            else read_pending <= 0;
        end
        if (m_axi_awvalid && m_axi_awready) begin
            if (m_axi_awaddr[5:0] || m_axi_awlen != 0 || m_axi_awsize != 6 ||
                m_axi_awburst != 1 || m_axi_awcache != 0 || m_axi_awid != 0 ||
                !(inside_allocation(m_axi_awaddr, descriptor[14], descriptor[15]) ||
                  inside_allocation(m_axi_awaddr, descriptor[18], descriptor[19]) ||
                  inside_allocation(m_axi_awaddr, descriptor[20], descriptor[21])))
                $fatal(1, "invalid peripheral AXI write");
            held_write <= m_axi_awaddr; aw_pending <= 1; writes <= writes + 1;
            write_delay <= writes == 0 ? 200 : 1 + rng[11:8];
        end
        if (m_axi_wvalid && m_axi_wready) begin
            if (!m_axi_wlast || !m_axi_wstrb) $fatal(1, "invalid peripheral AXI W");
            held_data <= m_axi_wdata; held_mask <= m_axi_wstrb; w_pending <= 1;
        end
        if (aw_pending && w_pending && !m_axi_bvalid) begin
            if (write_delay != 0) begin
                write_delay <= write_delay - 1;
                if (irq) $fatal(1, "completion before write visibility");
            end else begin
                for (p = 0; p < 64; p = p + 1)
                    if (held_mask[p]) memory[held_write+p] <= held_data[p*8 +: 8];
                m_axi_bvalid <= 1;
                m_axi_bresp <= fault == 3 && writes == 2 ? 2 : 0;
            end
        end
        if (m_axi_bvalid && m_axi_bready) begin
            aw_pending <= 0; w_pending <= 0; m_axi_bvalid <= 0; m_axi_bresp <= 0;
            responses <= responses + 1;
        end
        if (irq && (read_pending || aw_pending || w_pending || m_axi_bvalid || m_axi_rvalid))
            $fatal(1, "completion has outstanding memory operations");
    end

    task automatic tick;
        @(posedge clk); @(negedge clk);
    endtask

    task automatic write_register(input logic [7:0] address, input logic [31:0] value,
                                  input logic [3:0] strobe, input logic expect_error);
        integer cycle, aw_delay, w_delay;
        logic aw_seen, w_seen;
        begin
            aw_seen = 0; w_seen = 0; cycle = 0;
            aw_delay = rng[3:0]; w_delay = rng[7:4];
            s_axi_awaddr = address; s_axi_wdata = value; s_axi_wstrb = strobe;
            while (!aw_seen || !w_seen) begin
                s_axi_awvalid = !aw_seen && cycle >= aw_delay;
                s_axi_wvalid = !w_seen && cycle >= w_delay;
                @(posedge clk);
                if (s_axi_awvalid && s_axi_awready) aw_seen = 1;
                if (s_axi_wvalid && s_axi_wready) w_seen = 1;
                @(negedge clk); cycle = cycle + 1;
                if (cycle > 100) $fatal(1, "AXI-Lite write handshake watchdog");
            end
            s_axi_awvalid = 0; s_axi_wvalid = 0;
            while (!s_axi_bvalid) tick();
            repeat (4) begin
                if (!s_axi_bvalid || s_axi_bresp != (expect_error ? 2 : 0) || s_axi_awready || s_axi_wready)
                    $fatal(1, "AXI-Lite B lost/stale addr=%h value=%h got=%h", address, value, s_axi_bresp);
                tick();
            end
            s_axi_bready = 1; tick(); s_axi_bready = 0;
        end
    endtask

    task automatic read_register(input logic [7:0] address, input logic expect_error,
                                 output logic [31:0] value);
        begin
            s_axi_araddr = address; s_axi_arvalid = 1;
            while (!s_axi_arready) tick();
            tick(); s_axi_arvalid = 0;
            while (!s_axi_rvalid) tick();
            value = s_axi_rdata;
            repeat (3) begin
                if (!s_axi_rvalid || s_axi_rdata !== value || s_axi_rresp != (expect_error ? 2 : 0))
                    $fatal(1, "AXI-Lite R changed while stalled");
                tick();
            end
            s_axi_rready = 1; tick(); s_axi_rready = 0;
        end
    endtask

    task automatic load_bytes(input integer base, size, input logic is_input);
        integer i, value, scanned;
        begin
            if (base < 0 || size < 0 || base+size > MEMORY_BYTES) $fatal(1, "fixture outside memory");
            for (i = 0; i < size; i = i + 1) begin
                scanned = $fscanf(fd, "%h\n", value);
                if (scanned != 1) $fatal(1, "truncated device bytes");
                expected[base+i] = value;
                if (is_input) memory[base+i] = value;
            end
        end
    endtask
    task automatic save_output(input integer base, size, input string port_name);
        integer output_fd, i;
        string name;
        begin
            name = $sformatf("actual_%0d_%s.bin", case_number, port_name);
            output_fd = $fopen(name, "wb");
            if (!output_fd) $fatal(1, "cannot save actual peripheral output");
            for (i = 0; i < size; i = i + 1) $fwrite(output_fd, "%c", memory[base+i]);
            $fclose(output_fd);
        end
    endtask

    logic [31:0] value, elapsed;
    initial begin
        repeat (5) tick(); rst_n = 1; tick();
        read_register('h00, 0, value);
        if (value != 'h544b4731) $fatal(1, "wrong peripheral identity");
        read_register('h04, 0, value);
        if (value != ((GENERIC_SHAPES ? 'h00020000 : 'h00010000) |
                     (FP16_FLUSH_TO_POSITIVE_ZERO ? 1 : 0))) $fatal(1, "wrong ABI");
        read_register('h2c, 0, value);
        if (value != (FP16_FLUSH_TO_POSITIVE_ZERO ? 1 : 0)) $fatal(1, "wrong FP16 policy");
        read_register('h28, 0, value);
        if (value != 256) $fatal(1, "wrong tile capacity");
        read_register('h03, 1, value); read_register('hfc, 1, value);
        write_register('h00, 0, 15, 1); write_register('h0c, 2, 15, 1);
        fd = $fopen("device_vectors.txt", "r");
        if (!fd) $fatal(1, "missing C++ device vectors");
        scanned = $fscanf(fd, "%d\n", cases);
        for (case_number = 0; case_number < cases; case_number = case_number + 1) begin
            if (GENERIC_SHAPES)
                scanned = $fscanf(fd, "%d %d %d %d %d\n", fault, expected_error, initialize_memory, input_regions, output_regions);
            else begin
                scanned = $fscanf(fd, "%d %d\n", fault, expected_error);
                initialize_memory = 1;
            end
            if (scanned != (GENERIC_SHAPES ? 5 : 2)) $fatal(1, "bad peripheral case header");
            for (i = 0; i < DESCRIPTOR_WORDS; i = i + 1) scanned = $fscanf(fd, "%h\n", descriptor[i]);
            if (initialize_memory)
                for (i = 0; i < MEMORY_BYTES; i = i + 1) begin memory[i] = 'ha5; expected[i] = 'ha5; end
            if (GENERIC_SHAPES) begin
                for (region = 0; region < input_regions+output_regions; region = region+1) begin
                    scanned = $fscanf(fd, "%h %d\n", region_base, region_bytes);
                    if (scanned != 2 || region_base < 0 || region_bytes < 0 || region_base+region_bytes > MEMORY_BYTES)
                        $fatal(1, "command fixture region outside memory");
                    load_bytes(region_base, region_bytes, region < input_regions);
                end
            end else begin
                load_bytes(descriptor[5], descriptor[6], 1);
                load_bytes(descriptor[10], descriptor[11], 1);
                load_bytes(descriptor[14], descriptor[15], 0);
                load_bytes(descriptor[18], descriptor[19], 0);
                load_bytes(descriptor[20], descriptor[21], 0);
            end
            reads = 0; writes = 0; responses = 0; foreign_sent = 0;
            for (i = 0; i < DESCRIPTOR_WORDS; i = i + 1) write_register('h40 + 4*i, descriptor[i], 15, 0);
            // Byte strobes and full-width validation must not silently accept
            // a truncation such as element size 0x104 becoming four bytes.
            if (GENERIC_SHAPES) begin
                write_register('h98, 3, 15, 0); write_register('h0c, 1, 15, 1);
                write_register('h98, descriptor[22], 15, 0);
                write_register('hb8, 1, 15, 0); write_register('h0c, 1, 15, 1);
                write_register('hb8, 0, 15, 0);
            end
            if (!GENERIC_SHAPES || descriptor[22] == 0) begin
                write_register('h5c, 'h104, 15, 0); write_register('h0c, 1, 15, 1);
                write_register('h5c, descriptor[7], 15, 0);
            end else if (descriptor[22] == 2) begin
                write_register('h60, 'h104, 15, 0); write_register('h0c, 1, 15, 1);
                write_register('h60, descriptor[8], 15, 0);
            end
            write_register('h50, 'hffffffff, 0, 0);
            read_register('h50, 0, value);
            if (value != descriptor[4]) $fatal(1, "zero byte strobe changed descriptor");
            write_register('h40, 'h000000aa, 1, 0);
            read_register('h40, 0, value);
            if (value != ((descriptor[0] & 'hffffff00) | 'haa)) $fatal(1, "partial register write failed");
            write_register('h40, descriptor[0], 15, 0);
            write_register('h0c, 1, 15, 0);
            write_register('h0c, 1, 15, 1);
            write_register('h50, 99, 15, 1);
            cycles = 0;
            while (!irq) begin
                tick(); cycles = cycles + 1;
                if (cycles > 300000) $fatal(1, "peripheral job watchdog case=%0d", case_number);
            end
            save_output(descriptor[14], descriptor[15], "primary");
            save_output(descriptor[18], descriptor[19], "scores");
            save_output(descriptor[20], descriptor[21], "indices");
            read_register('h08, 0, value);
            if (value != (4 | expected_error << 8)) $fatal(1, "peripheral completion status %h", value);
            read_register('h10, 0, value);
            if (value != descriptor[0]) $fatal(1, "completed identity low mismatch");
            read_register('h14, 0, value);
            if (value != descriptor[1]) $fatal(1, "completed identity high mismatch");
            read_register('h18, 0, elapsed);
            repeat (20) tick(); read_register('h18, 0, value);
            if (value != elapsed || elapsed == 0) $fatal(1, "completion cycle count not retained");
            read_register('h20, 0, value);
            if (value != reads) $fatal(1, "read counter mismatch");
            read_register('h24, 0, value);
            if (value != writes || writes != responses) $fatal(1, "write/fence counter mismatch");
            for (i = 0; i < MEMORY_BYTES; i = i + 1)
                if ((!expected_error || !output_allocation(i)) && memory[i] !== expected[i])
                    $fatal(1, "peripheral byte mismatch case=%0d addr=%h actual=%h expected=%h", case_number, i, memory[i], expected[i]);
            if (fault == 5 && (reads || writes)) $fatal(1, "invalid descriptor accessed DDR");
            write_register('h0c, 2, 15, 0);
            if (irq) $fatal(1, "completion ACK not consumed");
            write_register('h0c, 1, 15, 1); // Same ID remains rejected after ACK.
            $display("DEVICE case=%0d n=%0d k=%0d cycles=%0d reads=%0d writes=%0d error=%0d PASS",
                     case_number, descriptor[2], descriptor[3], elapsed, reads, writes, expected_error);
        end
        $fclose(fd);
        if (GENERIC_SHAPES) $display("TOPK_COMMAND_DEVICE_PASS commands=%0d", cases);
        else $display("TOPK_DEVICE_PASS cases=%0d", cases);
        $finish;
    end
    initial begin #200000000; $fatal(1, "peripheral suite watchdog"); end
endmodule
