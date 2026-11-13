`timescale 1ns/1ps
module tb_axi;
    logic clk = 0, rst_n = 0;
    always #5 clk = ~clk;
    logic [31:0] read_address = 0, write_address = 0;
    logic read_valid = 0, read_ready, read_response_valid, read_response_ready = 0, read_error;
    logic [511:0] read_data, write_data = 0;
    logic [63:0] write_enable = 0;
    logic write_valid = 0, write_ready;
    logic fence_valid = 0, fence_ready, fence_response_valid, fence_response_ready = 0, fence_error;
    logic [63:0] fence_job_id = 0, fence_response_job_id;
    logic [31:0] m_axi_araddr, m_axi_awaddr;
    logic [7:0] m_axi_arlen, m_axi_awlen;
    logic [2:0] m_axi_arsize, m_axi_awsize;
    logic [1:0] m_axi_arburst, m_axi_awburst;
    logic [3:0] m_axi_arcache, m_axi_arid, m_axi_awcache, m_axi_awid;
    logic m_axi_arvalid, m_axi_arready = 0, m_axi_awvalid, m_axi_awready = 0;
    logic [511:0] m_axi_rdata = 0, m_axi_wdata;
    logic [63:0] m_axi_wstrb;
    logic [1:0] m_axi_rresp = 0, m_axi_bresp = 0;
    logic [3:0] m_axi_rid = 0, m_axi_bid = 0;
    logic m_axi_rlast = 0, m_axi_rvalid = 0, m_axi_rready;
    logic m_axi_wlast, m_axi_wvalid, m_axi_wready = 0, m_axi_bvalid = 0, m_axi_bready;
    axi_line_port dut(.*);
    integer checks = 0;
    logic [31:0] rng = 32'h3301311;
    always @(posedge clk) if (rst_n)
        rng <= {rng[30:0], rng[31] ^ rng[21] ^ rng[1] ^ rng[0]};

    task automatic tick;
        @(posedge clk); @(negedge clk);
    endtask

    task automatic verify_fence(input integer id, input logic expect_error);
        fence_valid = 1; fence_job_id = id;
        while (!fence_ready) tick();
        tick(); fence_valid = 0;
        while (!fence_response_valid) tick();
        repeat (5) begin
            if (fence_response_job_id != id || fence_error != expect_error ||
                read_ready || write_ready) $fatal(1, "fence state or result mismatch");
            tick();
        end
        fence_response_ready = 1; tick(); fence_response_ready = 0;
        checks = checks + 1;
    endtask

    task automatic write_case(input integer id, input integer fault);
        integer aw_delay, w_delay, i;
        logic aw_seen, w_seen;
        logic [511:0] expected_data;
        expected_data = {16{32'h33000000 + id}};
        write_address = id * 64; write_data = expected_data;
        write_enable = 64'h5555aaaa5555aaaa;
        write_valid = 1;
        if (!write_ready) $fatal(1, "write not ready");
        tick(); write_valid = 0;
        aw_delay = rng[3:0]; w_delay = rng[8:4];
        aw_seen = 0; w_seen = 0;
        for (i = 0; i < 40; i = i + 1) begin
            m_axi_awready = i >= aw_delay;
            m_axi_wready = i >= w_delay;
            if (m_axi_awvalid && (m_axi_awaddr != id * 64 || m_axi_awlen != 0 ||
                m_axi_awsize != 6 || m_axi_awburst != 1 || m_axi_awcache != 0 || m_axi_awid != 0))
                $fatal(1, "AXI address changed or attributes wrong");
            if (m_axi_wvalid && (m_axi_wdata !== expected_data ||
                m_axi_wstrb != write_enable || !m_axi_wlast)) $fatal(1, "AXI payload changed");
            if (m_axi_awvalid && m_axi_awready) begin
                if (aw_seen) $fatal(1, "duplicate AW"); aw_seen = 1;
            end
            if (m_axi_wvalid && m_axi_wready) begin
                if (w_seen) $fatal(1, "duplicate W"); w_seen = 1;
            end
            tick();
        end
        m_axi_awready = 0; m_axi_wready = 0;
        if (!aw_seen || !w_seen || !m_axi_bready) $fatal(1, "missing write beat");
        // Request completion while the write response is deliberately withheld.
        fence_valid = 1; fence_job_id = id;
        repeat (100) begin
            if (fence_ready || fence_response_valid || write_ready)
                $fatal(1, "write acceptance treated as completion");
            tick();
        end
        fence_valid = 0;
        m_axi_bresp = fault == 1 ? 2 : 0;
        m_axi_bid = fault == 2 ? 1 : 0;
        m_axi_bvalid = 1; tick(); m_axi_bvalid = 0;
        m_axi_bresp = 0; m_axi_bid = 0;
        if (fault == 2) begin
            repeat (3) begin
                if (fence_ready || !m_axi_bready) $fatal(1, "foreign BID completed local write");
                tick();
            end
            m_axi_bvalid = 1; tick(); m_axi_bvalid = 0;
        end
        verify_fence(id, fault != 0);
    endtask

    task automatic read_case(input integer id, input integer fault);
        integer i;
        read_address = id * 64; read_valid = 1;
        if (!read_ready) $fatal(1, "read not ready");
        tick(); read_valid = 0;
        repeat (7) begin
            if (!m_axi_arvalid || m_axi_araddr != id * 64 || m_axi_arlen != 0 ||
                m_axi_arsize != 6 || m_axi_arburst != 1 || m_axi_arcache != 0 || m_axi_arid != 0)
                $fatal(1, "AR changed while stalled");
            tick();
        end
        m_axi_arready = 1; tick(); m_axi_arready = 0;
        fence_valid = 1; fence_job_id = id;
        repeat (20) begin
            if (fence_ready || fence_response_valid) $fatal(1, "fence before RLAST");
            tick();
        end
        fence_valid = 0;
        if (fault == 3) begin
            m_axi_rvalid = 1; m_axi_rlast = 0; tick(); m_axi_rvalid = 0;
            repeat (3) begin
                if (read_response_valid || !m_axi_rready) $fatal(1, "malformed burst not drained");
                tick();
            end
        end
        m_axi_rdata = {16{32'h12340000 + id}};
        m_axi_rresp = fault == 1 ? 2 : 0;
        m_axi_rid = fault == 2 ? 1 : 0;
        m_axi_rlast = 1; m_axi_rvalid = 1; tick(); m_axi_rvalid = 0;
        if (fault == 2) begin
            repeat (3) begin
                if (read_response_valid || !m_axi_rready) $fatal(1, "foreign RID completed local read");
                tick();
            end
            m_axi_rid = 0; m_axi_rvalid = 1; tick(); m_axi_rvalid = 0;
        end
        repeat (5) begin
            if (!read_response_valid || read_error != (fault != 0) ||
                read_data !== {16{32'h12340000 + id}} || fence_ready)
                $fatal(1, "read response mismatch or premature fence");
            tick();
        end
        read_response_ready = 1; tick(); read_response_ready = 0;
        m_axi_rresp = 0; m_axi_rid = 0;
        verify_fence(id, 0); // Read fault is reported on the read channel.
    endtask

    integer test;
    initial begin
        repeat (5) tick(); rst_n = 1;
        for (test = 1; test <= 64; test = test + 1) write_case(test, test % 3);
        for (test = 65; test <= 96; test = test + 1) read_case(test, test % 4);
        verify_fence(97, 0); // Error state must not leak into the next job.
        $display("TOPK_AXI_PASS cases=%0d", checks);
        $finish;
    end
    initial begin #10000000; $fatal(1, "AXI suite watchdog"); end
endmodule
