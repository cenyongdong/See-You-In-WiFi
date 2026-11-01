// Shared vectoring CORDIC. One FP32 complex sample per request; no vendor IP.
// Angle output is signed pi*2^-30. FP32 subnormal/nonfinite inputs are rejected.
module csi_polar(
 input wire clk,resetn,start,input wire [31:0] re,im,
 output wire busy,output reg done,error,
 output reg [31:0] magnitude,output reg signed [31:0] angle
);
 reg [2:0] state;reg [4:0] iteration;
 reg signed [42:0] x,y;
 reg signed [31:0] z;
 reg [7:0] exponent;
 reg [74:0] product;
 reg [43:0] mag;
 wire [7:0] er=re[30:23],ei=im[30:23];
 wire [7:0] em=er>ei?er:ei;
 wire [7:0] dr=em-er,di=em-ei;
 wire [42:0] nr=dr>=40?43'd0:({3'd0,1'b1,re[22:0],16'd0}>>dr);
 wire [42:0] ni=di>=40?43'd0:({3'd0,1'b1,im[22:0],16'd0}>>di);
 wire signed [42:0] nx=re[31]?-$signed(nr):$signed(nr);
 wire signed [42:0] ny=im[31]?-$signed(ni):$signed(ni);
 `include "atan_table.vh"
 assign busy=state!=0;
 integer b;reg [5:0] lead,shift;
 reg [43:0] significand,remainder_bits,half;
 reg [8:0] out_exp;
 always @* begin
  lead=0;for(b=0;b<44;b=b+1)if(mag[b])lead=b;
  shift=lead>=23?lead-23:0;
  significand=mag>>shift;
  remainder_bits=mag&((44'd1<<shift)-1);
  half=shift ? 44'd1<<(shift-1) : 0;
  if(shift && (remainder_bits>half || (remainder_bits==half && significand[0])))significand=significand+1;
  out_exp={1'b0,exponent}+lead-39;
  if(significand[24])begin significand=significand>>1;out_exp=out_exp+1;end
 end
 always @(posedge clk)begin
  if(!resetn)begin state<=0;done<=0;error<=0;magnitude<=0;angle<=0;x<=0;y<=0;z<=0;exponent<=0;iteration<=0;product<=0;mag<=0;end
  else begin
   done<=0;
   case(state)
    0:if(start)begin
     error<=0;
     if(er==255 || ei==255 || (er==0 && re[22:0]!=0) || (ei==0 && im[22:0]!=0))begin error<=1;done<=1;end
     else if(im[30:0]==0)begin magnitude<={1'b0,re[30:0]};angle<=re[31]?(im[31]?-32'sd1073741824:32'sd1073741824):0;done<=1;end
     else if(re[30:0]==0)begin magnitude<={1'b0,im[30:0]};angle<=im[31]?-32'sd536870912:32'sd536870912;done<=1;end
     else begin
      exponent<=em;iteration<=0;
      if(re[31])begin x<=-nx;y<=-ny;z<=im[31]?-32'sd1073741824:32'sd1073741824;end
      else begin x<=nx;y<=ny;z<=0;end
      state<=1;
     end
    end
    1:begin
     if(y>=0)begin x<=x+(y>>>iteration);y<=y-(x>>>iteration);z<=z+atan_step(iteration);end
     else begin x<=x-(y>>>iteration);y<=y+(x>>>iteration);z<=z-atan_step(iteration);end
     if(iteration==30)state<=2;else iteration<=iteration+1;
    end
    2:begin product<=$unsigned(x)*32'd1304065748;state<=3;end
    3:begin mag<=product>>31;state<=4;end
    4:begin
     magnitude<={1'b0,out_exp[7:0],significand[22:0]};angle<=z;
     if(out_exp==0 || out_exp>=255)error<=1;
     done<=1;state<=0;
    end
   endcase
  end
 end
endmodule
