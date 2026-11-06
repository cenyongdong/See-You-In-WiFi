#include "pcap_stream.hpp"
#include <algorithm>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
using B = std::vector<unsigned char>;

void u16(B& b, unsigned x) {
	b.push_back(x);
	b.push_back(x >> 8);
}

void u32(B& b, unsigned x) {
	u16(b, x);
	u16(b, x >> 16);
}

void net16(B& b, size_t p, unsigned x) {
	b[p] = x >> 8;
	b[p + 1] = x;
}

B head() {
	B b;
	u32(b, 0xa1b2c3d4);
	u16(b, 2);
	u16(b, 4);
	u32(b, 0);
	u32(b, 0);
	u32(b, 65535);
	u32(b, 1);
	return b;
}

B frame(unsigned port = 5500, unsigned vlans = 0, unsigned ihl = 20) {
	B b(14);
	net16(b, 12, vlans ? 0x8100 : 0x800);
	for (unsigned i = 0; i < vlans; i++) {
		b.push_back(0);
		b.push_back(1);
		b.push_back(i + 1 < vlans ? 0x81 : 8);
		b.push_back(0);
	}
	const size_t p = b.size();
	b.resize(p + ihl + 11);
	b[p] = 0x40 + (ihl / 4);
	net16(b, p + 2, ihl + 11);
	b[p + 9] = 17;
	net16(b, p + ihl + 2, port);
	net16(b, p + ihl + 4, 11);
	b[p + ihl + 8] = 1;
	b[p + ihl + 9] = 2;
	b[p + ihl + 10] = 3;
	return b;
}

void record(B& b, const B& f, unsigned t = 1) {
	u32(b, 10);
	u32(b, t);
	u32(b, f.size());
	u32(b, f.size());
	b.insert(b.end(), f.begin(), f.end());
}

void check(bool ok, const char* m) {
	if (!ok)
		throw std::runtime_error(m);
}

size_t checks = 0;

void bad(const B& b, const char* what) {
	nexmon_board::PcapStream p;
	bool threw = false;
	try {
		p.append(b.data(), b.size());
		p.finish();
	} catch (const std::exception&) {
		threw = true;
	}
	check(threw, what);
	++checks;
}

int main(int argc, char** argv) {
	try {
		B b = head();
		record(b, frame(5500), 1);
		record(b, frame(5501, 2, 24), 2);
		record(b, frame(9999), 3);
		for (size_t chunk = 1; chunk < 200; chunk++) {
			nexmon_board::PcapStream p;
			std::vector<nexmon_board::Datagram> all;
			for (size_t i = 0; i < b.size(); i += chunk) {
				auto o = p.append(b.data() + i, std::min(chunk, b.size() - i));
				all.insert(all.end(), o.begin(), o.end());
			}
			check(p.complete(), "whole record boundary");
			p.finish();
			p.finish();
			check(p.packets() == 3 && p.bytes() == b.size(), "counts");
			check(all.size() == 2 && all[0].port == 5500 && all[1].port == 5501, "ordered selection");
			check(
				all[1].timestamp_us == 10000002 && all[1].payload == B({1, 2, 3}), "VLAN/IP options payload");
			++checks;
		}
		B t = b;
		t[0] = 0xa1;
		bad(t, "bad endian");
		t = b;
		t[0] = 0x4d;
		t[1] = 0x3c;
		bad(t, "nanosecond magic");
		for (size_t n : {size_t(0), size_t(23), size_t(25), b.size() - 1})
			bad(B(b.begin(), b.begin() + n), "truncated tail");
		t = b;
		t[36] = 0;
		bad(t, "truncated captured frame");
		t = head();
		record(t, frame(), 1000000);
		bad(t, "invalid usec");
		t = head();
		record(t, frame(), 2);
		record(t, frame(), 1);
		bad(t, "time rollback");
		t = head();
		record(t, frame(5500, 3));
		bad(t, "three VLANs");
		auto f = frame();
		f[14] = 0x44;
		t = head();
		record(t, f);
		bad(t, "bad IHL");
		f = frame();
		f[14 + 20 + 4] = 0;
		f[14 + 20 + 5] = 10;
		t = head();
		record(t, f);
		bad(t, "bad UDP length");
		f = frame();
		f[14 + 6] = 0x20;
		t = head();
		record(t, f);
		bad(t, "IP fragmentation");
		t = head();
		for (unsigned i = 0; i < 40001; i++)
			record(t, frame(), i);
		bad(t, "packet budget");
		t = head();
		record(t, frame(), 1);
		f = frame();
		f[14] = 0x44;
		record(t, f, 2);
		record(t, frame(5501), 3);
		for (size_t chunk : {size_t(1), size_t(137), t.size()}) {
			nexmon_board::PcapStream isolated(true, true);
			std::vector<nexmon_board::Datagram> all;
			for (size_t i = 0; i < t.size(); i += chunk) {
				auto o = isolated.append(t.data() + i, std::min(chunk, t.size() - i));
				all.insert(all.end(), o.begin(), o.end());
			}
			isolated.finish();
			check(all.size() == 2 && all[1].port == 5501, "bad record affected following frame");
			check(isolated.packets() == 3 && isolated.rejected_frames() == 1, "bad record accounting");
			const auto& issue = isolated.last_issue();
			check(issue.packet == 2 && issue.timestamp_us == 10000002 && issue.frame_prefix[14] == 0x44,
				"bad record original header missing");
			++checks;
		}
		t = head();
		record(t, frame(), 2);
		record(t, frame(), 1);
		{
			nexmon_board::PcapStream isolated(true, true);
			bool threw = false;
			try {
				isolated.append(t.data(), t.size());
			} catch (const std::exception&) {
				threw = true;
			}
			check(threw, "isolation hid framing/clock error");
			++checks;
		}
		nexmon_board::PcapStream p;
		unsigned char x = 0;
		bool byte_limit = false;
		try {
			p.append(&x, 32u * 1024u * 1024u + 1);
		} catch (const std::exception& e) {
			byte_limit = std::string(e.what()).find("byte budget") != std::string::npos;
		}
		check(byte_limit, "byte budget");
		++checks;
		if (argc == 2) {
			std::ifstream in(argv[1], std::ios::binary);
			check(bool(in), "real PCAP open");
			nexmon_board::PcapStream real;
			char bytes[137];
			size_t selected = 0;
			while (in) {
				in.read(bytes, sizeof(bytes));
				auto count = in.gcount();
				if (count)
					selected += real.append(reinterpret_cast<unsigned char*>(bytes), size_t(count)).size();
			}
			real.finish();
			std::cout << "real_packets=" << real.packets() << " selected=" << selected
					  << " bytes=" << real.bytes() << "\n";
		}
		std::cout << "passed=" << checks << "\n";
		return 0;
	} catch (const std::exception& e) {
		std::cerr << e.what() << "\n";
		return 1;
	}
}
