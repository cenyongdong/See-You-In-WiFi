#include "hdmi_renderer.hpp"
#include <chrono>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>

int main(int argc,char** argv) {
    using namespace pose;
    const std::string out=argc>1 ? argv[1]:".";
    for(unsigned people: {0u,1u,3u}) {
        post::PresentationFrame frame;
        frame.id={1,123456789,1,1000000000};
        for(unsigned i=0;i<people;++i) {
            post::Person p;p.track=i+1;p.observed_ns=frame.id.source_ns;p.score=.9f;p.candidate=i;
            // Synthetic geometry, explicitly NOT an inference or accuracy sample.
            for(unsigned j=0;j<14;++j) {
                p.joints[3*j]=.9f+i*.65f+(j%4)*.125f;
                p.joints[3*j+1]=1.5f+(j%3)*.1875f;
                p.joints[3*j+2]=2.75f+j*.0625f;
            }
            frame.poses.push_back(p);
        }
        auto cpu=hdmi::render_presentation(hdmi::prepare_background(),frame);
        auto pl=hdmi::render_presentation({},frame,true);
        if(!pl.rgb565.empty() || pl.commands.empty() || pl.commands.size()>512 ||
           pl.detection_count!=cpu.detection_count) throw std::runtime_error("Overlay contract");
        for(unsigned i=0;i<people;++i)
            if(cpu.detections[i].projected!=pl.detections[i].projected || cpu.detections[i].raw!=pl.detections[i].raw)
                throw std::runtime_error("Projection or model data changed");
        const auto stem=out+"/fixture-"+std::to_string(people);
        std::ofstream hex(stem+".hex");
        for(auto word:pl.commands) hex<<std::hex<<std::setw(8)<<std::setfill('0')<<word<<'\n';
        std::ofstream raw(stem+"-ps.rgb565",std::ios::binary);
        raw.write(reinterpret_cast<const char*>(cpu.rgb565.data()),cpu.rgb565.size());
        double cpu_ms=0,pl_ms=0;
        hdmi::PreparedBackground canvas;
        for(unsigned n=0;n<100;++n) {
            auto start=std::chrono::steady_clock::now();
            hdmi::prepare_background(canvas);
            auto c=hdmi::render_presentation(std::move(canvas),frame);
            cpu_ms+=std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-start).count();
            canvas.rgb565=std::move(c.rgb565);
            start=std::chrono::steady_clock::now();
            auto h=hdmi::render_presentation({},frame,true);
            pl_ms+=std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-start).count();
        }
        std::cout<<"{\"source\":\"synthetic_cpu_only\",\"people\":"<<people
          <<",\"ps_prepare_ms\":"<<cpu_ms/100<<",\"pl_command_prepare_ms\":"<<pl_ms/100
          <<",\"command_words\":"<<pl.commands.size()<<",\"command_bytes\":"<<pl.commands.size()*4<<"}\n";
    }
    auto bg=hdmi::prepare_background();
    std::ofstream raw(out+"/background.rgb565",std::ios::binary);
    raw.write(reinterpret_cast<const char*>(bg.rgb565.data()),bg.rgb565.size());
    std::cout<<"OVERLAY_SOFTWARE_PASS projection/model-preservation/bounds/0-1-3-person\n";
}
