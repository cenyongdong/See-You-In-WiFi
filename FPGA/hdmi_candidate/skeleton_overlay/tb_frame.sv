// Full-size rendering of software-generated synthetic three-person commands.
module tb_frame;
 reg clk=0,pclk=0,resetn=0,presetn=0;
 always #5 clk=~clk;always #3.367 pclk=~pclk;
 reg wr=0;reg [7:0] wa=0;reg [31:0] wd=0;wire ready,rr,rv;wire [31:0] rd;
 reg vs=0;wire oh,ov,od;wire [23:0] rgb;
 skeleton_overlay dut(clk,resetn,wr,wa,wd,ready,1'b0,8'd0,rr,rv,rd,1'b1,
  pclk,presetn,1'b0,vs,1'b0,24'd0,1'b0,oh,ov,od,rgb);
 `include "fixture_count.vh"
 reg [31:0] words[0:WORDS-1];integer i,f;
 task write(input [7:0] a,input [31:0] d);
  begin @(negedge clk);wa=a;wd=d;wr=1;@(negedge clk);wr=0;end
 endtask
 initial begin
  $readmemh("fixture.hex",words);
  #40;resetn=1;presetn=1;
  for(i=0;i<WORDS;i=i+1) write(32,words[i]);
  write(12,1);write(16,1);
  wait(dut.state==8);repeat(6)@(negedge pclk);vs=1;repeat(4)@(negedge pclk);vs=0;
  wait(dut.state==0);
  if(dut.error || dut.done_tag!=1) $fatal(1,"Frame rejected");
  f=$fopen("overlay.hex","w");
  for(i=0;i<518400;i=i+1) $fdisplay(f,"%x",dut.pixels[518400+i]);
  $fclose(f);
  $display("OVERLAY_PASS full-size commands=%0d cycles=%0d",WORDS,dut.draw_cycles);$finish;
 end
 initial begin #20000000;$fatal(1,"Timeout");end
endmodule
