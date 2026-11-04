module tb_batch;
 reg clk=0,resetn=0;always #5 clk=~clk;
 reg wv=0,rv=0,rr=1;reg [7:0] wa=0,ra=0;reg [31:0] wd=0;wire wr,ar,rvalid;wire [31:0] rd;
 localparam N=5400;
 csi_batch #(.SAMPLES(N)) dut(clk,resetn,wv,wa,wd,wr,rv,ra,ar,rvalid,rd,rr);
wire  gold_wr_ready;
wire  gold_rd_ready;
wire  gold_rsp_valid;
wire [31:0] gold_rsp_data;
gold_csi_batch #(.SAMPLES(N)) reference_dut(.clk(clk),.resetn(resetn),.wr_valid(wv),.wr_addr(wa),.wr_data(wd),.wr_ready(gold_wr_ready),.rd_valid(rv),.rd_addr(ra),.rd_ready(gold_rd_ready),.rsp_valid(gold_rsp_valid),.rsp_data(gold_rsp_data),.rsp_ready(rr));
integer compared_cycles=0;
always @(negedge clk) begin
 #0.001;
 if(resetn) begin
 compared_cycles=compared_cycles+1;
 if(wr !== gold_wr_ready) $fatal(1,"cycle mismatch wr_ready");
 if(ar !== gold_rd_ready) $fatal(1,"cycle mismatch rd_ready");
 if(rvalid !== gold_rsp_valid) $fatal(1,"cycle mismatch rsp_valid");
 if(rd !== gold_rsp_data) $fatal(1,"cycle mismatch rsp_data");
end
end

 reg [31:0] expect_m[0:N-1],expect_a[0:N-1];
 task write(input [7:0] a,input [31:0] v);begin @(negedge clk);wa=a;wd=v;wv=1;@(negedge clk);wv=0;end endtask
 task read(input [7:0] a,output [31:0] v);begin
  @(negedge clk);ra=a;rv=1;while(!ar)@(negedge clk);@(negedge clk);rv=0;
  while(!rvalid)@(negedge clk);v=rd;@(negedge clk);
 end endtask
 integer f,i,k,g,rc,overlapped=0;reg [31:0] x,y,v,stamp;
 initial begin
  repeat(3)@(negedge clk);resetn=1;
  read(0,v);if(v!==32'h43534903)$fatal(1,"ABI");
  // Incomplete input must reject START without touching any external resource.
  write(16,1);read(4,v);if(v!==4)$fatal(1,"Incomplete batch not rejected");
  for(k=0;k<2;k=k+1)begin
   write(16,2);read(4,v);if(v!==0)$fatal(1,"Reset");
   f=$fopen("vectors.hex","r");
   for(i=0;i<N;i=i+1)begin
    if(i!=0 && i%1836==0)begin $fclose(f);f=$fopen("vectors.hex","r");end
    rc=$fscanf(f,"%h %h %h %h\n",x,y,expect_m[i],expect_a[i]);if(rc!=4)$fatal(1,"Vector read");
    write(32,x);write(32,y);
   end
   $fclose(f);read(8,v);if(v!=2*N)$fatal(1,"Load count");
   write(44,2*N-2);read(48,v);if(v!==x)$fatal(1,"Input real readback");
   write(44,2*N-1);read(48,v);if(v!==y)$fatal(1,"Input imaginary readback");
   write(12,k+1);write(16,1);
   for(g=0;g<N/90;g=g+1)begin
    v=0;while(v<(g+1)*180)begin
     read(68,v);if(v%180 || v>2*N)$fatal(1,"Partial/invalid published group");
    end
    if(k==1)#100000; // Delayed consumer: producer may finish while draining.
    read(4,v);if(v[2])$fatal(1,"Hardware error");if(v[0])overlapped=overlapped+1;
    for(i=g*90;i<(g+1)*90;i=i+1)begin
     read(36,v);if(v!==expect_m[i])$fatal(1,"Magnitude %0d %h/%h",i,v,expect_m[i]);
     read(36,v);if(v!==expect_a[i])$fatal(1,"Angle %0d %h/%h",i,v,expect_a[i]);
    end
   end
   read(4,v);if(v!=2)$fatal(1,"Completion state %h",v);
   read(20,stamp);if(stamp!=k+1)$fatal(1,"Completion tag");
   read(28,v);if(v!=k+1)$fatal(1,"Completion count");
   read(40,v);if(v!=2*N)$fatal(1,"Read count");
  end
  read(36,v);read(4,v);if(v!=6)$fatal(1,"Overread not rejected");
  if(overlapped==0)$fatal(1,"No concurrent producer/consumer coverage");
  $display("CSI_BATCH_PASS two streaming batches, fast/slow consumers, numeric outputs, overlap=%0d",overlapped);$display("CYCLE_EQUIVALENCE_PASS cycles=%0d",compared_cycles);$finish;
 end
 initial begin #20000000;$fatal(1,"Batch timeout");end
endmodule
