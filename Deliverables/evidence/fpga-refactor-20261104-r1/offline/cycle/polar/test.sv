module tb_polar;
 reg clk=0,resetn=0,start=0;always #5 clk=~clk;
 reg [31:0] re,im;wire busy,done,error;wire [31:0] magnitude;wire signed [31:0] angle;
 csi_polar dut(clk,resetn,start,re,im,busy,done,error,magnitude,angle);
wire  gold_busy;
wire  gold_done;
wire  gold_error;
wire [31:0] gold_magnitude;
wire [31:0] gold_angle;
gold_csi_polar  reference_dut(.clk(clk),.resetn(resetn),.start(start),.re(re),.im(im),.busy(gold_busy),.done(gold_done),.error(gold_error),.magnitude(gold_magnitude),.angle(gold_angle));
integer compared_cycles=0;
always @(negedge clk) begin
 #0.001;
 if(resetn) begin
 compared_cycles=compared_cycles+1;
 if(busy !== gold_busy) $fatal(1,"cycle mismatch busy");
 if(done !== gold_done) $fatal(1,"cycle mismatch done");
 if(error !== gold_error) $fatal(1,"cycle mismatch error");
 if(magnitude !== gold_magnitude) $fatal(1,"cycle mismatch magnitude");
 if(angle !== gold_angle) $fatal(1,"cycle mismatch angle");
end
end

 integer f,rc,count=0,cycles;reg [31:0] want_m,want_a;
 initial begin
  repeat(3)@(negedge clk);resetn=1;
  f=$fopen("vectors.hex","r");if(!f)$fatal(1,"Missing vectors");
  while(!$feof(f))begin
   rc=$fscanf(f,"%h %h %h %h\n",re,im,want_m,want_a);
   if(rc!=4)$fatal(1,"Bad vector");
   start=1;@(negedge clk);start=0;cycles=0;
   while(!done)begin @(negedge clk);cycles=cycles+1;if(cycles>50)$fatal(1,"Polar timeout");end
   if(error || magnitude!==want_m || angle!==want_a)$fatal(1,"Polar vector %d re=%h im=%h magnitude=%h/%h angle=%h/%h error=%b",count,re,im,magnitude,want_m,angle,want_a,error);
   count=count+1;@(negedge clk);
  end
  // Illegal numeric inputs must finish with an error, never hang.
  re=32'h7f800000;im=0;start=1;@(negedge clk);start=0;
  if(!done || !error)$fatal(1,"Infinity not rejected");
  @(negedge clk);re=1;im=0;start=1;@(negedge clk);start=0;
  if(!done || !error)$fatal(1,"Subnormal not rejected");
  $display("CSI_POLAR_PASS vectors=%0d",count);$display("CYCLE_EQUIVALENCE_PASS cycles=%0d",compared_cycles);$finish;
 end
 initial begin #2000000;$fatal(1,"Global watchdog");end
endmodule
