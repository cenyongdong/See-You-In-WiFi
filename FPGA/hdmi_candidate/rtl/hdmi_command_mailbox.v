// Single in-flight mailbox. Multi-bit payload stays fixed until the response
// toggle returns; each side resets together with the enclosing bus subsystem.
// The source must keep valid/payload stable while ready is low.
module hdmi_command_mailbox
    #(parameter COMMAND_BITS = 72, RESPONSE_BITS = 160)
    (input wire source_clk,
        input wire source_resetn,
        input wire source_valid,
        output wire source_ready,
        input wire [COMMAND_BITS - 1 : 0] source_command,
        output reg source_response_valid,
        output reg [RESPONSE_BITS - 1 : 0] source_response,
        input wire target_clk,
        input wire target_resetn,
        output wire target_valid,
        input wire target_ready,
        output wire [COMMAND_BITS - 1 : 0] target_command,
        input wire [RESPONSE_BITS - 1 : 0] target_response);
    reg request_toggle, response_toggle;
    reg [COMMAND_BITS - 1 : 0] payload_hold;
    reg [RESPONSE_BITS - 1 : 0] response_hold;
    (* ASYNC_REG = "TRUE" *) reg [1 : 0] request_sync, response_sync;
    reg response_seen;
    assign source_ready = request_toggle == response_sync[1];
    assign target_valid = request_sync[1] != response_toggle;
    assign target_command = payload_hold;
    always @(posedge source_clk or negedge source_resetn) begin
        if (!source_resetn) begin
            request_toggle <= 0;
            payload_hold <= 0;
            response_sync <= 0;
            response_seen <= 0;
            source_response_valid <= 0;
            source_response <= 0;
        end else begin
            response_sync <= {response_sync[0], response_toggle};
            source_response_valid <= 0;
            if (source_valid && source_ready) begin
                payload_hold <= source_command;
                request_toggle <= !request_toggle;
            end
            if (response_sync[1] != response_seen) begin
                source_response <= response_hold;
                source_response_valid <= 1;
                response_seen <= response_sync[1];
            end
        end
    end
    always @(posedge target_clk or negedge target_resetn) begin
        if (!target_resetn) begin
            request_sync <= 0;
            response_toggle <= 0;
            response_hold <= 0;
        end else begin
            request_sync <= {request_sync[0], request_toggle};
            if (target_valid && target_ready) begin
                response_hold <= target_response;
                response_toggle <= request_sync[1];
            end
        end
    end
endmodule
