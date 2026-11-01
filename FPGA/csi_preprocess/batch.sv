// Independent simple-dual-port input/output buffers. Avoid read/write sharing
// across both physical ports; retain bounded readback for device verification.
// GP slave only. No DMA, external memory addresses, or asynchronous clocks.
module csi_batch #(parameter SAMPLES=5400)(
 input wire clk,resetn,
 input wire wr_valid,input wire [7:0] wr_addr,input wire [31:0] wr_data,output wire wr_ready,
 input wire rd_valid,input wire [7:0] rd_addr,output wire rd_ready,
 output reg rsp_valid,output reg [31:0] rsp_data,input wire rsp_ready
);
 localparam WORDS=2*SAMPLES;
 // Explicit power-of-two banks avoid rounding each 10800-word buffer up to
 // 16384 words (32 BRAM36 total would exceed the remaining device capacity).
 (* ram_style="block" *)reg [31:0] input_low[0:8191],input_high[0:4095];
 (* ram_style="block" *)reg [31:0] output_low[0:8191],output_high[0:4095];
 reg [13:0] loaded,read_pointer,index,published_words;
 reg [7:0] group_word;
 reg [31:0] tag,completed,cycles,elapsed,completion_count;
 reg fault,finished;
 reg [3:0] state;
 reg [13:0] inspect_pointer;reg [7:0] fault_reason;
 wire busy=state!=0;
 reg [31:0] re,im,input_low_q,input_high_q,output_low_q,output_high_q;
 reg input_bank,output_bank;
 wire [31:0] port_a=output_bank?output_high_q:output_low_q;
 wire [31:0] port_b=input_bank?input_high_q:input_low_q;
 wire data_write=wr_valid && wr_addr==8'h20 && !busy && !finished && loaded<WORDS;
 wire [13:0] addr_b=!busy?inspect_pointer:((state==3 || state==4 || state==10 || state==8)?index+1'b1:index);
 wire [13:0] result_address=state==8?index+1'b1:index;
 wire result_write=state==7 || state==8;
 wire [31:0] pm;wire signed [31:0] pa;wire pb,pd,pe;
 reg polar_start;reg [31:0] saved_m,saved_a;
 csi_polar polar(clk,resetn,polar_start,re,im,pb,pd,pe,pm,pa);
 // Match the qualified overlay's separate write/read-port coding style.
 always @(posedge clk)begin
  if(data_write && !loaded[13])input_low[loaded[12:0]]<=wr_data;
  if(data_write && loaded[13])input_high[loaded[11:0]]<=wr_data;
  input_low_q<=input_low[addr_b[12:0]];
  input_high_q<=input_high[addr_b[11:0]];
  input_bank<=addr_b[13];
 end
 always @(posedge clk)begin
  if(result_write && !result_address[13])output_low[result_address[12:0]]<=state==7?saved_m:saved_a;
  if(result_write && result_address[13])output_high[result_address[11:0]]<=state==7?saved_m:saved_a;
  output_low_q<=output_low[read_pointer[12:0]];
  output_high_q<=output_high[read_pointer[11:0]];
  output_bank<=read_pointer[13];
 end
 reg pending;reg [7:0] pending_addr;
 assign wr_ready=1;
 assign rd_ready=!pending && !rsp_valid;
 always @(posedge clk)begin
  if(!resetn)begin
   loaded<=0;read_pointer<=0;index<=0;published_words<=0;group_word<=0;tag<=0;completed<=0;cycles<=0;elapsed<=0;completion_count<=0;
   fault<=0;finished<=0;state<=0;re<=0;im<=0;polar_start<=0;saved_m<=0;saved_a<=0;
   pending<=0;pending_addr<=0;rsp_valid<=0;rsp_data<=0;
   inspect_pointer<=0;fault_reason<=0;
  end else begin
   polar_start<=0;
   if(rsp_valid && rsp_ready)rsp_valid<=0;
   if(rd_valid && rd_ready)begin pending<=1;pending_addr<=rd_addr;end
   if(pending)begin
    pending<=0;rsp_valid<=1;
    case(pending_addr)
     0:rsp_data<=32'h43534903;
     4:rsp_data<={29'd0,fault,finished,busy};
     8:rsp_data<=loaded;
     12:rsp_data<=tag;
     20:rsp_data<=completed;
     24:rsp_data<=elapsed;
     28:rsp_data<=completion_count;
     36:begin
      // Publish only complete 90-complex groups. Port A writes later samples
      // while port B drains already committed words; never read a live write.
      if(!fault && read_pointer<published_words)begin rsp_data<=port_a;read_pointer<=read_pointer+1;end
      else begin rsp_data<=0;fault<=1;fault_reason<=4;end
     end
     40:rsp_data<=read_pointer;
     44:rsp_data<=inspect_pointer;
     48:rsp_data<=busy?32'd0:port_b;
     52:rsp_data<=index;
     56:rsp_data<=re;
     60:rsp_data<=im;
     64:rsp_data<=fault_reason;
     68:rsp_data<=published_words;
     default:rsp_data<=0;
    endcase
   end
   if(busy)cycles<=cycles+1;
   case(state)
    1:state<=9;
    9:state<=2;
    2:begin re<=port_b;state<=3;end
    3:state<=10;
    10:state<=4;
    4:begin im<=port_b;state<=5;end
    5:begin polar_start<=1;state<=6;end
    6:if(pd)begin
     if(pe)begin fault<=1;fault_reason<=5;state<=0;finished<=0;end
     else begin saved_m<=pm;saved_a<=pa;state<=7;end
    end
    7:state<=8;
    8:begin
     if(group_word==178 || index==WORDS-2)begin published_words<=index+2;group_word<=0;end
     else group_word<=group_word+2;
     if(index==WORDS-2)begin state<=0;finished<=1;elapsed<=cycles+1;completed<=tag;completion_count<=completion_count+1;end
     else begin index<=index+2;state<=1;end
    end
   endcase
   if(wr_valid)begin
    if(busy)begin fault<=1;fault_reason<=1;end
    else case(wr_addr)
     12:tag<=wr_data;
     16:begin
      if(wr_data==2)begin loaded<=0;read_pointer<=0;published_words<=0;group_word<=0;finished<=0;fault<=0;fault_reason<=0;end
      else if(wr_data==1 && loaded==WORDS && !fault)begin state<=1;index<=0;cycles<=0;finished<=0;published_words<=0;group_word<=0;end
      else begin fault<=1;fault_reason<=2;end
     end
     32:begin if(loaded<WORDS && !finished)loaded<=loaded+1;else begin fault<=1;fault_reason<=3;end end
     44:begin if(wr_data<WORDS)inspect_pointer<=wr_data[13:0];else begin fault<=1;fault_reason<=6;end end
     default:begin fault<=1;fault_reason<=7;end
    endcase
   end
  end
 end
endmodule
