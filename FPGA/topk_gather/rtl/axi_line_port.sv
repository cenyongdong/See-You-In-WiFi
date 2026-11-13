// One 64-byte line per AXI4 transaction, one read and one write outstanding.
// A fence responds only after RLAST and B responses have been consumed. This
// adapter requires a real AXI response channel; User_Ddr ready is insufficient.
// Reset is permitted only after external STOP/drain, never as an abort fence.
module axi_line_port (
    input logic clk, rst_n,
    input logic [31:0] read_address,
    input logic read_valid,
    output logic read_ready,
    output logic [511:0] read_data,
    output logic read_response_valid,
    input logic read_response_ready,
    output logic read_error,
    input logic [31:0] write_address,
    input logic [511:0] write_data,
    input logic [63:0] write_enable,
    input logic write_valid,
    output logic write_ready,
    input logic fence_valid,
    output logic fence_ready,
    input logic [63:0] fence_job_id,
    output logic fence_response_valid,
    input logic fence_response_ready,
    output logic [63:0] fence_response_job_id,
    output logic fence_error,

    output logic [31:0] m_axi_araddr,
    output logic [7:0] m_axi_arlen,
    output logic [2:0] m_axi_arsize,
    output logic [1:0] m_axi_arburst,
    output logic [3:0] m_axi_arcache, m_axi_arid,
    output logic m_axi_arvalid,
    input logic m_axi_arready,
    input logic [511:0] m_axi_rdata,
    input logic [1:0] m_axi_rresp,
    input logic [3:0] m_axi_rid,
    input logic m_axi_rlast, m_axi_rvalid,
    output logic m_axi_rready,
    output logic [31:0] m_axi_awaddr,
    output logic [7:0] m_axi_awlen,
    output logic [2:0] m_axi_awsize,
    output logic [1:0] m_axi_awburst,
    output logic [3:0] m_axi_awcache, m_axi_awid,
    output logic m_axi_awvalid,
    input logic m_axi_awready,
    output logic [511:0] m_axi_wdata,
    output logic [63:0] m_axi_wstrb,
    output logic m_axi_wlast, m_axi_wvalid,
    input logic m_axi_wready,
    input logic [1:0] m_axi_bresp,
    input logic [3:0] m_axi_bid,
    input logic m_axi_bvalid,
    output logic m_axi_bready
);
    // A single fixed ID and non-bufferable requests require completion at the
    // addressed slave. CPU cache maintenance remains a separate host contract.
    typedef enum logic [1:0] {R_IDLE, R_ADDRESS, R_DATA, R_OUTPUT} read_state_t;
    typedef enum logic [1:0] {W_IDLE, W_SEND, W_RESPONSE} write_state_t;
    read_state_t read_state;
    write_state_t write_state;
    logic aw_pending, w_pending, read_extra_beat;
    logic write_fault;

    assign read_ready = read_state == R_IDLE && !fence_valid && !fence_response_valid;
    assign write_ready = write_state == W_IDLE && !fence_valid && !fence_response_valid;
    assign read_response_valid = read_state == R_OUTPUT;
    assign m_axi_arvalid = read_state == R_ADDRESS;
    assign m_axi_arlen = 0;
    assign m_axi_arsize = 6;
    assign m_axi_arburst = 1;
    assign m_axi_arcache = 0;
    assign m_axi_arid = 0;
    assign m_axi_rready = read_state == R_DATA;
    assign m_axi_awvalid = write_state == W_SEND && aw_pending;
    assign m_axi_wvalid = write_state == W_SEND && w_pending;
    assign m_axi_awlen = 0;
    assign m_axi_awsize = 6;
    assign m_axi_awburst = 1;
    assign m_axi_awcache = 0;
    assign m_axi_awid = 0;
    assign m_axi_wlast = 1;
    assign m_axi_bready = write_state == W_RESPONSE;
    assign fence_ready = read_state == R_IDLE && write_state == W_IDLE && !fence_response_valid;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            read_state <= R_IDLE; write_state <= W_IDLE;
            m_axi_araddr <= 0; m_axi_awaddr <= 0;
            m_axi_wdata <= 0; m_axi_wstrb <= 0;
            read_data <= 0; read_error <= 0; read_extra_beat <= 0;
            aw_pending <= 0; w_pending <= 0; write_fault <= 0;
            fence_response_valid <= 0; fence_response_job_id <= 0; fence_error <= 0;
        end else begin
            case (read_state)
                R_IDLE: if (read_valid && read_ready) begin
                    m_axi_araddr <= read_address;
                    read_error <= 0; read_extra_beat <= 0;
                    read_state <= R_ADDRESS;
                end
                R_ADDRESS: if (m_axi_arready) read_state <= R_DATA;
                R_DATA: if (m_axi_rvalid) begin
                    if (m_axi_rid != 0) read_error <= 1;
                    else begin
                        read_data <= m_axi_rdata;
                        read_error <= read_error || m_axi_rresp != 0 || !m_axi_rlast || read_extra_beat;
                        // A foreign ID is not this read's completion. A
                        // malformed burst is drained through its own RLAST.
                        read_extra_beat <= 1;
                        if (m_axi_rlast) read_state <= R_OUTPUT;
                    end
                end
                R_OUTPUT: if (read_response_ready) read_state <= R_IDLE;
                default: read_state <= R_IDLE;
            endcase
            case (write_state)
                W_IDLE: if (write_valid && write_ready) begin
                    m_axi_awaddr <= write_address;
                    m_axi_wdata <= write_data; m_axi_wstrb <= write_enable;
                    aw_pending <= 1; w_pending <= 1;
                    write_state <= W_SEND;
                end
                W_SEND: begin
                    if (m_axi_awready) aw_pending <= 0;
                    if (m_axi_wready) w_pending <= 0;
                    if ((!aw_pending || m_axi_awready) && (!w_pending || m_axi_wready))
                        write_state <= W_RESPONSE;
                end
                W_RESPONSE: if (m_axi_bvalid) begin
                    write_fault <= write_fault || m_axi_bresp != 0 || m_axi_bid != 0;
                    if (m_axi_bid == 0) write_state <= W_IDLE;
                end
                default: write_state <= W_IDLE;
            endcase
            if (fence_valid && fence_ready) begin
                fence_response_job_id <= fence_job_id;
                fence_error <= write_fault;
                fence_response_valid <= 1;
                write_fault <= 0;
            end
            if (fence_response_valid && fence_response_ready) fence_response_valid <= 0;
        end
    end
endmodule
