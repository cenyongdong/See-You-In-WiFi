// Standalone, single-clock AXI4-Lite + AXI4 peripheral for the N <= 256 kernel.
// No SoC address, clock/reset crossing, SDK allocation, or NPU completion is
// implied by this wrapper. Those remain explicit platform integration work.
module topk_gather_device #(
    parameter integer GENERIC_SHAPES = 0,
    parameter integer FP16_FLUSH_TO_POSITIVE_ZERO = 0
) (
    input logic clk, rst_n,
    input logic [7:0] s_axi_awaddr,
    input logic s_axi_awvalid,
    output logic s_axi_awready,
    input logic [31:0] s_axi_wdata,
    input logic [3:0] s_axi_wstrb,
    input logic s_axi_wvalid,
    output logic s_axi_wready,
    output logic [1:0] s_axi_bresp,
    output logic s_axi_bvalid,
    input logic s_axi_bready,
    input logic [7:0] s_axi_araddr,
    input logic s_axi_arvalid,
    output logic s_axi_arready,
    output logic [31:0] s_axi_rdata,
    output logic [1:0] s_axi_rresp,
    output logic s_axi_rvalid,
    input logic s_axi_rready,
    output logic irq,
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
    localparam integer DESCRIPTOR_WORDS = GENERIC_SHAPES ? 32 : 22;
    // Minor version 1 explicitly changes the FP16 numeric contract. Software
    // must check both ABI and policy before publishing work to this variant.
    localparam logic [31:0] ABI_VERSION = (GENERIC_SHAPES ? 32'h00020000 : 32'h00010000) |
                                         (FP16_FLUSH_TO_POSITIVE_ZERO ? 32'd1 : 32'd0);
    logic [31:0] descriptor [0:DESCRIPTOR_WORDS-1];
    logic descriptor_legal;
    logic start_valid, start_ready, done_valid, done_ready;
    logic [63:0] done_job_id;
    logic [3:0] error_code;
    logic [31:0] read_transactions, write_transactions;
    logic [31:0] read_address, write_address;
    logic [511:0] read_data, write_data;
    logic [63:0] write_enable, fence_job_id, fence_response_job_id;
    logic read_valid, read_ready, read_response_valid, read_response_ready, read_error;
    logic write_valid, write_ready, fence_valid, fence_ready;
    logic fence_response_valid, fence_response_ready, fence_error;

    generate if (!GENERIC_SHAPES) begin : fast_format
        assign descriptor_legal = (descriptor[7] == 2 || descriptor[7] == 4) &&
                                  (descriptor[8] == 2 || descriptor[8] == 4) && descriptor[9] < 4;
    end else begin : command_format
        // Opcode 0 = score tile, 1 = merge, 2 = final run Gather.
        // Validate full-width format fields before narrowing any RTL port.
        assign descriptor_legal = descriptor[22] <= 2 && descriptor[30] == 0 && descriptor[31] == 0 &&
            (descriptor[22] != 0 || descriptor[7] == 2 || descriptor[7] == 4) &&
            (descriptor[22] != 2 || ((descriptor[8] == 2 || descriptor[8] == 4) && descriptor[9] < 4));
    end endgenerate
    kernel_control #(.DESCRIPTOR_WORDS(DESCRIPTOR_WORDS),
                     .ABI_VERSION(ABI_VERSION),
                     .FORMAT_POLICY(FP16_FLUSH_TO_POSITIVE_ZERO ? 32'd1 : 32'd0)) control(
        .clk(clk), .rst_n(rst_n),
        .s_axi_awaddr(s_axi_awaddr), .s_axi_awvalid(s_axi_awvalid), .s_axi_awready(s_axi_awready),
        .s_axi_wdata(s_axi_wdata), .s_axi_wstrb(s_axi_wstrb), .s_axi_wvalid(s_axi_wvalid), .s_axi_wready(s_axi_wready),
        .s_axi_bresp(s_axi_bresp), .s_axi_bvalid(s_axi_bvalid), .s_axi_bready(s_axi_bready),
        .s_axi_araddr(s_axi_araddr), .s_axi_arvalid(s_axi_arvalid), .s_axi_arready(s_axi_arready),
        .s_axi_rdata(s_axi_rdata), .s_axi_rresp(s_axi_rresp), .s_axi_rvalid(s_axi_rvalid), .s_axi_rready(s_axi_rready),
        .descriptor(descriptor), .descriptor_legal(descriptor_legal), .start_valid(start_valid), .start_ready(start_ready),
        .done_valid(done_valid), .done_ready(done_ready), .done_job_id(done_job_id), .error_code(error_code),
        .read_transactions(read_transactions), .write_transactions(write_transactions), .irq(irq));

    generate if (!GENERIC_SHAPES) begin : fast_path
    topk_gather_kernel #(.FP16_FLUSH_TO_POSITIVE_ZERO(FP16_FLUSH_TO_POSITIVE_ZERO)) kernel(
        .clk(clk), .rst_n(rst_n), .start_valid(start_valid), .start_ready(start_ready),
        .job_id({descriptor[1], descriptor[0]}), .input_count(descriptor[2]), .keep_count(descriptor[3]),
        .channels(descriptor[4]), .score_base(descriptor[5]), .score_bytes(descriptor[6]),
        .score_element_bytes(descriptor[7][2:0]), .element_bytes(descriptor[8][2:0]),
        .source_blocked16(descriptor[9][0]), .destination_blocked16(descriptor[9][1]),
        .source_base(descriptor[10]), .source_bytes(descriptor[11]),
        .source_row_stride(descriptor[12]), .source_block_stride(descriptor[13]),
        .destination_base(descriptor[14]), .destination_bytes(descriptor[15]),
        .destination_row_stride(descriptor[16]), .destination_block_stride(descriptor[17]),
        .selected_score_base(descriptor[18]), .selected_score_bytes(descriptor[19]),
        .selected_index_base(descriptor[20]), .selected_index_bytes(descriptor[21]),
        .read_address(read_address), .read_valid(read_valid), .read_ready(read_ready), .read_data(read_data),
        .read_response_valid(read_response_valid), .read_response_ready(read_response_ready), .read_error(read_error),
        .write_address(write_address), .write_data(write_data), .write_enable(write_enable),
        .write_valid(write_valid), .write_ready(write_ready),
        .fence_valid(fence_valid), .fence_ready(fence_ready), .fence_job_id(fence_job_id),
        .fence_response_valid(fence_response_valid), .fence_response_ready(fence_response_ready),
        .fence_response_job_id(fence_response_job_id), .fence_error(fence_error),
        .done_valid(done_valid), .done_ready(done_ready), .done_job_id(done_job_id), .error_code(error_code),
        .read_transactions(read_transactions), .write_transactions(write_transactions));
    end else begin : planned_path
        command_kernel #(.FP16_FLUSH_TO_POSITIVE_ZERO(FP16_FLUSH_TO_POSITIVE_ZERO)) kernel(
            .clk(clk), .rst_n(rst_n), .descriptor(descriptor), .start_valid(start_valid), .start_ready(start_ready),
            .read_address(read_address), .read_valid(read_valid), .read_ready(read_ready), .read_data(read_data),
            .read_response_valid(read_response_valid), .read_response_ready(read_response_ready), .read_error(read_error),
            .write_address(write_address), .write_data(write_data), .write_enable(write_enable), .write_valid(write_valid), .write_ready(write_ready),
            .fence_valid(fence_valid), .fence_ready(fence_ready), .fence_job_id(fence_job_id),
            .fence_response_valid(fence_response_valid), .fence_response_ready(fence_response_ready),
            .fence_response_job_id(fence_response_job_id), .fence_error(fence_error),
            .done_valid(done_valid), .done_ready(done_ready), .done_job_id(done_job_id), .error_code(error_code),
            .read_transactions(read_transactions), .write_transactions(write_transactions));
    end endgenerate

    axi_line_port memory_port(
        .clk(clk), .rst_n(rst_n),
        .read_address(read_address), .read_valid(read_valid), .read_ready(read_ready), .read_data(read_data),
        .read_response_valid(read_response_valid), .read_response_ready(read_response_ready), .read_error(read_error),
        .write_address(write_address), .write_data(write_data), .write_enable(write_enable),
        .write_valid(write_valid), .write_ready(write_ready),
        .fence_valid(fence_valid), .fence_ready(fence_ready), .fence_job_id(fence_job_id),
        .fence_response_valid(fence_response_valid), .fence_response_ready(fence_response_ready),
        .fence_response_job_id(fence_response_job_id), .fence_error(fence_error),
        .m_axi_araddr(m_axi_araddr), .m_axi_arlen(m_axi_arlen), .m_axi_arsize(m_axi_arsize),
        .m_axi_arburst(m_axi_arburst), .m_axi_arcache(m_axi_arcache), .m_axi_arid(m_axi_arid),
        .m_axi_arvalid(m_axi_arvalid), .m_axi_arready(m_axi_arready),
        .m_axi_rdata(m_axi_rdata), .m_axi_rresp(m_axi_rresp), .m_axi_rid(m_axi_rid),
        .m_axi_rlast(m_axi_rlast), .m_axi_rvalid(m_axi_rvalid), .m_axi_rready(m_axi_rready),
        .m_axi_awaddr(m_axi_awaddr), .m_axi_awlen(m_axi_awlen), .m_axi_awsize(m_axi_awsize),
        .m_axi_awburst(m_axi_awburst), .m_axi_awcache(m_axi_awcache), .m_axi_awid(m_axi_awid),
        .m_axi_awvalid(m_axi_awvalid), .m_axi_awready(m_axi_awready),
        .m_axi_wdata(m_axi_wdata), .m_axi_wstrb(m_axi_wstrb), .m_axi_wlast(m_axi_wlast),
        .m_axi_wvalid(m_axi_wvalid), .m_axi_wready(m_axi_wready),
        .m_axi_bresp(m_axi_bresp), .m_axi_bid(m_axi_bid), .m_axi_bvalid(m_axi_bvalid), .m_axi_bready(m_axi_bready));
endmodule
