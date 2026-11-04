// Functional control for the one-shot startup return consumer. No protocol
// checker, waveform/history storage, timestamp counter or checker-reset port.
// The held command/reply and toggle acknowledgement retain the r45 CDC model.
module hp2_deferred_control
    (input wire source_clk, csr_clk, csr_resetn,
        input wire ps_resetn, pl_resetn, hp_reset, any_request, reader_ready, rvalid,
        input wire [4 : 0] rid,
        input wire [1 : 0] rresp,
        input wire rlast, ps_rvalid,
        input wire [31 : 0] drain_status,
        output wire arm,
        mna_gp_ww_itf.slave csr);
    localparam [31 : 0] ABI = 32'h48444302;
    localparam [31 : 0] CONS = 32'h434f4e53, SNAP = 32'h534e4150;
    reg request_toggle = 0, ack_toggle = 0;
    reg [31 : 0] held_command = SNAP;
    (* ASYNC_REG = "TRUE", SHREG_EXTRACT = "NO" *) reg [1 : 0] request_sync = 0, ack_sync = 0;
    reg arm_used = 0, source_error = 0;
    reg [31 : 0] held_status = 0, held_flags = 0;
    wire pending = request_sync[1] != ack_toggle;
    wire idle = ps_resetn && pl_resetn && !hp_reset && !any_request && !reader_ready;
    wire arm_allowed = !arm_used && drain_status[2 : 0] == 0 && idle && rvalid && rid == 0 && rresp == 0;
    assign arm = pending && held_command == CONS && arm_allowed;
    always @(posedge source_clk) begin
        request_sync <= {request_sync[0], request_toggle};
        if (pending) begin
            held_status <= drain_status;
            held_flags <= {15'd0, ps_rvalid, rlast, rresp, rid, rvalid, reader_ready, any_request, hp_reset,
                pl_resetn, ps_resetn, source_error, arm_used};
            if (held_command == CONS) begin
                arm_used <= 1;
                if (!arm_allowed)
                    source_error <= 1;
            end else if (held_command != SNAP)
                source_error <= 1;
            ack_toggle <= request_sync[1];
        end
    end
    reg [31 : 0] request_sequence = 0, response_sequence = 0;
    reg busy = 0, command_error = 0, arm_issued = 0;
    reg [31 : 0] csr_status = 0, csr_flags = 0;
    reg read_valid = 0;
    reg [31 : 0] read_value = 0, selected;
    wire [7 : 0] offset = csr.araddr[7 : 0];
    assign csr.awwready = csr_resetn;
    assign csr.arready = csr_resetn && (!read_valid || csr.rready);
    assign csr.rvalid = read_valid;
    assign csr.rdata = read_value;
    always @* begin
        selected = 32'hbad00004;
        case (offset)
            8'h00:
                selected = {29'd0, arm_issued, command_error, busy};
            8'h04:
                selected = ABI;
            8'h08:
                selected = request_sequence;
            8'h0c:
                selected = response_sequence;
            8'h10:
                selected = csr_status;
            8'h14:
                selected = csr_flags;
        endcase
        if (offset[1 : 0] != 0)
            selected = 32'hbad00001;
    end
    always @(posedge csr_clk or negedge csr_resetn) begin
        if (!csr_resetn) begin
            request_toggle <= 0;
            held_command <= SNAP;
            ack_sync <= 0;
            request_sequence <= 0;
            response_sequence <= 0;
            busy <= 0;
            command_error <= 0;
            arm_issued <= 0;
            csr_status <= 0;
            csr_flags <= 0;
            read_valid <= 0;
            read_value <= 0;
        end else begin
            ack_sync <= {ack_sync[0], ack_toggle};
            if (busy && ack_sync[1] == request_toggle) begin
                csr_status <= held_status;
                csr_flags <= held_flags;
                response_sequence <= request_sequence;
                busy <= 0;
            end
            if (csr.awwvalid && csr.awwready) begin
                if (csr.awwaddr[7 : 0] == 0 && !busy &&
                    (csr.awwdata == SNAP || (csr.awwdata == CONS && !arm_issued))) begin
                    held_command <= csr.awwdata;
                    request_toggle <= !request_toggle;
                    request_sequence <= request_sequence + 1'b1;
                    busy <= 1;
                    if (csr.awwdata == CONS)
                        arm_issued <= 1;
                end else
                    command_error <= 1;
            end
            if (csr.arvalid && csr.arready) begin
                read_valid <= 1;
                read_value <= selected;
            end else if (csr.rready)
                read_valid <= 0;
        end
    end
endmodule
