module tb_overlay;
 reg clk=0,pclk=0,resetn=0,presetn=0;
 always #5 clk=~clk;
 always #3.367 pclk=~pclk;
 reg wr=0;reg [7:0] wa=0;reg [31:0] wd=0;wire ready;
 wire rr,rv;wire [31:0] rd;
 reg hs=0,vs=0,de=0;wire oh,ov,od;wire [23:0] rgb;
 skeleton_overlay #(.W(32),.H(24)) dut(clk,resetn,wr,wa,wd,ready,1'b0,8'd0,rr,rv,rd,1'b1,
   pclk,presetn,hs,vs,de,24'h123456,1'b0,oh,ov,od,rgb);
 task write(input [7:0] a,input [31:0] d);
  begin @(negedge clk);wa=a;wd=d;wr=1;@(negedge clk);wr=0;end
 endtask
 task draw_command(input integer k,col,x0,y0,x1,y1);
  begin write(32,(col<<28)|(k<<24)|(y0<<10)|x0);write(32,(y1<<10)|x1);end
 endtask
 task submit(input integer tag);
  begin write(12,tag);write(16,1);end
 endtask
 task adopt;
  begin
   wait(dut.state==8);repeat(6)@(negedge pclk);
   if(dut.done_tag!=dut.completed) $fatal(1,"Tag unexpectedly published before vblank");
   vs=1;repeat(4)@(negedge pclk);vs=0;
   wait(dut.state==0);repeat(2)@(negedge clk);
  end
 endtask
 integer i,count,xx,yy,seen=0;
 reg check_pixels=0;
 reg [3:0] expected_ink;
 reg [23:0] expected_rgb;
 always @(negedge pclk) if(check_pixels && od) begin
  expected_ink=dut.pixels[768+(seen/64/2)*32+(seen%64)/2];
  case(expected_ink)
   0:expected_rgb=24'h123456;1:expected_rgb=24'h399eff;2:expected_rgb=24'heff3f7;
   3:expected_rgb=24'h103c31;4:expected_rgb=24'hb5f7de;5:expected_rgb=24'h4a3c21;6:expected_rgb=24'hffe3a5;
  endcase
  if(rgb!==expected_rgb) $fatal(1,"Composite alignment pixel=%d actual=%h expected=%h",seen,rgb,expected_rgb);
  seen=seen+1;
 end
 initial begin
  #40;resetn=1;presetn=1;
  draw_command(1,1,2,3,20,3); // horizontal inclusive
  draw_command(1,2,4,2,4,18); // vertical overlay priority
  draw_command(1,3,20,20,2,2); // reversed diagonal
  draw_command(2,4,28,20,0,0); // circular joint
  draw_command(3,5,10,8,14,10); // rectangle
  draw_command(4,6,23,1,65,0); // font A
  submit(1);adopt();
  if(dut.error || dut.done_tag!=1 || dut.completed!=1) $fatal(1,"First completion");
  for(i=5;i<=20;i=i+1) if(dut.pixels[768+3*32+i]!=1) $fatal(1,"Horizontal %d",i);
  if(dut.pixels[768+12*32+4]!=2) $fatal(1,"Vertical");
  if(dut.pixels[768+18*32+18]!=3) $fatal(1,"Reversed diagonal");
  count=0;for(i=0;i<768;i=i+1) if(dut.pixels[768+i]==4) count=count+1;
  if(count!=13) $fatal(1,"Disk size %d",count);
  if(dut.pixels[768+8*32+10]!=5 || dut.pixels[768+10*32+14]!=5) $fatal(1,"Rectangle");
  if(dut.pixels[768+1*32+24]!=6 || dut.pixels[768+1*32+23]!=0) $fatal(1,"Font");
  // Exercise the actual three-stage pixel pipeline, 2x scale and transparent background.
  @(negedge pclk);vs=1;repeat(4)@(negedge pclk);vs=0;check_pixels=1;
  for(yy=0;yy<48;yy=yy+1) begin
   repeat(8)@(negedge pclk);
   for(xx=0;xx<64;xx=xx+1) begin de=1;@(negedge pclk);end
   de=0;
  end
  repeat(8)@(negedge pclk);
  if(seen!=3072) $fatal(1,"Active pixel count %d",seen);
  check_pixels=0;
  // Busy writes must not corrupt the immutable bank or command stream.
  draw_command(1,2,0,0,31,23);submit(2);write(32,32'hffffffff);
  if(!dut.error) $fatal(1,"Busy write accepted");
  adopt();write(16,2);
  if(dut.pixels[768+12*32+4]!=2) $fatal(1,"Old bank overwritten");
  submit(3);adopt();
  for(i=0;i<768;i=i+1) if(dut.pixels[768+i]!=0) $fatal(1,"Transparent clear");
  // Invalid coordinates are bounded and do not write outside a bank.
  draw_command(1,1,40,0,2,2);submit(4);adopt();
  if(!dut.error) $fatal(1,"Invalid coordinate accepted");
  $display("OVERLAY_PASS line/disk/rect/font/priority/clear/busy/bounds/vblank/pixel-composition");$finish;
 end
 initial begin #2000000;$fatal(1,"Timeout");end
endmodule

