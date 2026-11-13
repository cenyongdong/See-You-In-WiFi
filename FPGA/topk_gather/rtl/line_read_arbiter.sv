// Two readers share one line port. Capture the address/owner before presenting
// VALID, and retain ownership until the response has been consumed.
module line_read_arbiter (
    input logic clk, rst_n,
    input logic [1:0][31:0] client_address,
    input logic [1:0] client_valid,
    output logic [1:0] client_ready,
    output logic [1:0] client_response_valid,
    input logic [1:0] client_response_ready,
    output logic [31:0] read_address,
    output logic read_valid,
    input logic read_ready,
    input logic read_response_valid,
    output logic read_response_ready,
    output logic idle
);
    typedef enum logic [1:0] {IDLE, REQUEST, RESPONSE} state_t;
    state_t state;
    logic owner, preferred, selected;
    assign selected = client_valid[preferred] ? preferred : !preferred;
    assign idle = state == IDLE;
    assign read_valid = state == REQUEST;
    assign read_response_ready = state == RESPONSE && client_response_ready[owner];
    always_comb begin
        client_ready = 0; client_response_valid = 0;
        if (state == REQUEST) client_ready[owner] = read_ready;
        if (state == RESPONSE) client_response_valid[owner] = read_response_valid;
    end
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin state <= IDLE; owner <= 0; preferred <= 0; read_address <= 0; end
        else case (state)
            IDLE: if (|client_valid) begin
                owner <= selected; read_address <= client_address[selected]; state <= REQUEST;
            end
            REQUEST: if (read_ready) state <= RESPONSE;
            RESPONSE: if (read_response_valid && read_response_ready) begin
                preferred <= !owner; state <= IDLE;
            end
            default: state <= IDLE;
        endcase
    end
endmodule
