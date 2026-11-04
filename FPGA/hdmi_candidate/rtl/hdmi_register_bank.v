// Local CSR bus adapter, deliberately independent of AXI-Lite channel handling.
// The enclosing bus bridge MUST honor write_ready. No current-board base address
// is assigned to these candidate offsets. One software thread owns the commands.
module hdmi_register_bank
    (input wire clk,
        input wire resetn,
        input wire write_valid,
        output wire write_ready,
        input wire [7 : 0] write_offset,
        input wire [31 : 0] write_data,
        input wire [3 : 0] write_strobe,
        input wire [7 : 0] read_offset,
        output reg [31 : 0] read_data,
        output reg command_valid,
        input wire command_ready,
        output reg [71 : 0] command,
        input wire response_valid,
        input wire [159 : 0] response);
    reg [31 : 0] address_arg, id_arg, issued_count, response_count;
    reg [159 : 0] snapshot;
    reg csr_error;
    integer i;
    assign write_ready = !command_valid;
    always @(posedge clk or negedge resetn) begin
        if (!resetn) begin
            address_arg <= 0;
            id_arg <= 0;
            issued_count <= 0;
            response_count <= 0;
            snapshot <= 0;
            csr_error <= 0;
            command_valid <= 0;
            command <= 0;
        end else begin
            if (command_valid && command_ready)
                command_valid <= 0;
            if (response_valid) begin
                snapshot <= response;
                response_count <= response_count + 1'b1;
            end
            if (write_valid && write_ready) begin
                case (write_offset)
                    8'h04:
                        for (i = 0; i < 4; i = i + 1)
                            if (write_strobe[i])
                                address_arg[i * 8 +: 8] <= write_data[i * 8 +: 8];
                    8'h08:
                        for (i = 0; i < 4; i = i + 1)
                            if (write_strobe[i])
                                id_arg[i * 8 +: 8] <= write_data[i * 8 +: 8];
                    8'h0c: begin
                        if (write_strobe != 4'hf || write_data > 4)
                            csr_error <= 1;
                        else begin
                            command <= {write_data[3 : 0], 4'd0, id_arg, address_arg};
                            command_valid <= 1;
                            issued_count <= issued_count + 1'b1;
                        end
                    end
                    8'h2c:
                        if (write_strobe[0] && write_data[0])
                            csr_error <= 0;
                    default:
                        csr_error <= 1;
                endcase
            end
        end
    end
    always @* begin
        case (read_offset)
            8'h00:
                read_data = 32'h48444d01;
            8'h04:
                read_data = address_arg;
            8'h08:
                read_data = id_arg;
            8'h10:
                read_data = snapshot[31 : 0];
            8'h14:
                read_data = snapshot[63 : 32];
            8'h18:
                read_data = snapshot[95 : 64];
            8'h1c:
                read_data = snapshot[127 : 96];
            8'h20:
                read_data = snapshot[159 : 128];
            8'h24:
                read_data = issued_count;
            8'h28:
                read_data = response_count;
            8'h2c:
                read_data = {29'd0, csr_error, !command_ready, command_valid};
            default:
                read_data = 0;
        endcase
    end
endmodule
