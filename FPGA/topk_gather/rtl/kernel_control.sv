// AXI4-Lite control plane, one submitted job and one retained completion.
// Local address window is 256 bytes; the SoC interconnect owns its mapping.
// RESET is initialization after external STOP/drain, never a recovery command.
module kernel_control #(
    parameter integer DESCRIPTOR_WORDS = 22,
    parameter logic [31:0] ABI_VERSION = 32'h00010000,
    parameter logic [31:0] FORMAT_POLICY = 0
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
    output logic [31:0] descriptor [0:DESCRIPTOR_WORDS-1],
    input logic descriptor_legal,
    output logic start_valid,
    input logic start_ready,
    input logic done_valid,
    output logic done_ready,
    input logic [63:0] done_job_id,
    input logic [3:0] error_code,
    input logic [31:0] read_transactions, write_transactions,
    output logic irq
);
    typedef enum logic [1:0] {IDLE, LAUNCH, RUNNING, COMPLETE} state_t;
    state_t state;
    logic aw_held, w_held;
    logic [7:0] write_offset;
    logic [31:0] write_word;
    logic [3:0] write_strobe;
    logic [63:0] last_job, completed_job, cycles;
    logic [3:0] completed_error;
    logic [31:0] completed_reads, completed_writes;
    logic [63:0] requested_job;
    integer i, lane;
    localparam logic [7:0] LAST_DESCRIPTOR = 8'h40 + 4*(DESCRIPTOR_WORDS-1);

    assign requested_job = {descriptor[1], descriptor[0]};
    assign s_axi_awready = !aw_held && !s_axi_bvalid;
    assign s_axi_wready = !w_held && !s_axi_bvalid;
    assign s_axi_arready = !s_axi_rvalid;
    assign start_valid = state == LAUNCH;
    assign done_ready = state == RUNNING;
    assign irq = state == COMPLETE;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE; aw_held <= 0; w_held <= 0;
            write_offset <= 0; write_word <= 0; write_strobe <= 0;
            s_axi_bvalid <= 0; s_axi_bresp <= 0;
            s_axi_rvalid <= 0; s_axi_rdata <= 0; s_axi_rresp <= 0;
            last_job <= 0; completed_job <= 0; cycles <= 0;
            completed_error <= 0; completed_reads <= 0; completed_writes <= 0;
            for (i = 0; i < DESCRIPTOR_WORDS; i = i + 1) descriptor[i] <= 0;
        end else begin
            if (s_axi_bvalid && s_axi_bready) s_axi_bvalid <= 0;
            if (s_axi_rvalid && s_axi_rready) s_axi_rvalid <= 0;
            if (s_axi_awvalid && s_axi_awready) begin
                aw_held <= 1; write_offset <= s_axi_awaddr;
            end
            if (s_axi_wvalid && s_axi_wready) begin
                w_held <= 1; write_word <= s_axi_wdata; write_strobe <= s_axi_wstrb;
            end
            if (state == LAUNCH || state == RUNNING) cycles <= cycles + 1;
            if (start_valid && start_ready) state <= RUNNING;
            if (done_valid && done_ready) begin
                state <= COMPLETE;
                completed_job <= done_job_id;
                // Identity mismatch cannot be published as a successful job.
                completed_error <= done_job_id != last_job ? 4'd9 : error_code;
                completed_reads <= read_transactions; completed_writes <= write_transactions;
            end

            // AW and W may arrive in either order. Commit once, then retain B.
            if (aw_held && w_held && !s_axi_bvalid) begin
                aw_held <= 0; w_held <= 0;
                s_axi_bvalid <= 1; s_axi_bresp <= 0;
                if (write_offset[1:0] != 0) s_axi_bresp <= 2;
                else if (write_strobe == 0) begin end
                else if (write_offset >= 8'h40 && write_offset <= LAST_DESCRIPTOR) begin
                    if (state != IDLE) s_axi_bresp <= 2;
                    else for (lane = 0; lane < 4; lane = lane + 1)
                        if (write_strobe[lane])
                            descriptor[(write_offset-8'h40)/4][lane*8 +: 8] <= write_word[lane*8 +: 8];
                end else if (write_offset == 8'h0c && write_strobe == 4'hf) begin
                    if (write_word == 1 && state == IDLE && requested_job > last_job && descriptor_legal) begin
                        state <= LAUNCH; last_job <= requested_job; cycles <= 0;
                        completed_error <= 0; completed_reads <= 0; completed_writes <= 0;
                    end else if (write_word == 2 && state == COMPLETE) state <= IDLE;
                    else s_axi_bresp <= 2;
                end else s_axi_bresp <= 2;
            end
            if (s_axi_arvalid && s_axi_arready) begin
                s_axi_rvalid <= 1; s_axi_rresp <= 0; s_axi_rdata <= 0;
                if (s_axi_araddr[1:0] != 0) s_axi_rresp <= 2;
                else if (s_axi_araddr >= 8'h40 && s_axi_araddr <= LAST_DESCRIPTOR)
                    s_axi_rdata <= descriptor[(s_axi_araddr-8'h40)/4];
                else case (s_axi_araddr)
                    8'h00: s_axi_rdata <= 32'h544b4731; // TKG1
                    8'h04: s_axi_rdata <= ABI_VERSION;
                    8'h08: s_axi_rdata <= {20'd0, completed_error, 5'd0,
                                           state == COMPLETE, state == LAUNCH || state == RUNNING, state == IDLE};
                    8'h10: s_axi_rdata <= completed_job[31:0];
                    8'h14: s_axi_rdata <= completed_job[63:32];
                    8'h18: s_axi_rdata <= cycles[31:0];
                    8'h1c: s_axi_rdata <= cycles[63:32];
                    8'h20: s_axi_rdata <= completed_reads;
                    8'h24: s_axi_rdata <= completed_writes;
                    8'h28: s_axi_rdata <= 256;
                    8'h2c: s_axi_rdata <= FORMAT_POLICY;
                    default: s_axi_rresp <= 2;
                endcase
            end
        end
    end
endmodule
