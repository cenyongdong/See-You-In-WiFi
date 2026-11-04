// One pending read owner, independent combined address/data writes.
// Decode BEFORE the legacy bridge truncates to nine address bits.
module hdmi_cam_router
    #(parameter [31 : 0] HDMI_BASE = 32'h400b0000,
        parameter integer DECODE_LSB = 8)
    (input wire clk,
        input wire resetn,
        mna_gp_ww_itf.slave upstream,
        mna_gp_ww_itf.master camera,
        mna_gp_ww_itf.master hdmi);
    reg read_pending, read_hdmi;
    wire select_read = upstream.araddr[31 : DECODE_LSB] == HDMI_BASE[31 : DECODE_LSB];
    wire select_write = upstream.awwaddr[31 : DECODE_LSB] == HDMI_BASE[31 : DECODE_LSB];
    assign camera.araddr = upstream.araddr;
    assign hdmi.araddr = upstream.araddr;
    assign camera.arvalid = upstream.arvalid && !read_pending && !select_read;
    assign hdmi.arvalid = upstream.arvalid && !read_pending && select_read;
    assign upstream.arready = !read_pending && (select_read ? hdmi.arready : camera.arready);
    assign upstream.rdata = read_hdmi ? hdmi.rdata : camera.rdata;
    assign upstream.rvalid = read_pending && (read_hdmi ? hdmi.rvalid : camera.rvalid);
    assign camera.rready = read_pending && !read_hdmi && upstream.rready;
    assign hdmi.rready = read_pending && read_hdmi && upstream.rready;
    assign camera.awwaddr = upstream.awwaddr;
    assign camera.awwdata = upstream.awwdata;
    assign hdmi.awwaddr = upstream.awwaddr;
    assign hdmi.awwdata = upstream.awwdata;
    assign camera.awwvalid = upstream.awwvalid && !select_write;
    assign hdmi.awwvalid = upstream.awwvalid && select_write;
    assign upstream.awwready = select_write ? hdmi.awwready : camera.awwready;
    always @(posedge clk or negedge resetn) begin
        if (!resetn) begin
            read_pending <= 0;
            read_hdmi <= 0;
        end else begin
            if (upstream.arvalid && upstream.arready) begin
                read_pending <= 1;
                read_hdmi <= select_read;
            end
            if (upstream.rvalid && upstream.rready)
                read_pending <= 0;
        end
    end
endmodule
