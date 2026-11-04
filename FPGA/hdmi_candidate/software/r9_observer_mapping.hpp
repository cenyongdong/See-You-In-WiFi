#pragma once
#include "dma_probe_evidence.hpp"
#include <atomic>
#include <sys/mman.h>
#include <sys/stat.h>
namespace {
class Mapping {
public:
    explicit Mapping(bool read_only = false) : read_only_(read_only) {
        fd_ = ::open("/dev/mem", (read_only ? O_RDONLY : O_RDWR) | O_SYNC | O_CLOEXEC);
        if (fd_ < 0)
            throw pose::dma_probe_evidence::io_error("open", "/dev/mem");
        struct stat st{};
        if (::fstat(fd_, &st) != 0 || !S_ISCHR(st.st_mode)) {
            ::close(fd_);
            fd_ = -1;
            throw std::runtime_error("Expected physical CSR character device");
        }
        data_ = ::mmap(nullptr, 4096, PROT_READ | (read_only ? 0 : PROT_WRITE), MAP_SHARED, fd_, 0x400b0000);
        if (data_ == MAP_FAILED) {
            ::close(fd_);
            fd_ = -1;
            throw std::runtime_error("Cannot map r9 CSR page");
        }
        csr_ = reinterpret_cast<volatile std::uint32_t *>(static_cast<char *>(data_) + 0x400);
    }
    ~Mapping() {
        if (data_ != MAP_FAILED)
            ::munmap(data_, 4096);
        if (fd_ >= 0)
            ::close(fd_);
    }
    Mapping(const Mapping &) = delete;
    Mapping &operator=(const Mapping &) = delete;
    std::uint32_t read(unsigned off) const {
        const auto value = csr_[off / 4];
        std::atomic_thread_fence(std::memory_order_seq_cst);
        return value;
    }
    void write(unsigned off, std::uint32_t value) {
        pose::r9_startup::need(!read_only_, "Read-only observer mapping");
        pose::r9_startup::need(off == 0 && (value == 1 || value == 2), "Only observer ARM/FREEZE allowed");
        std::atomic_thread_fence(std::memory_order_seq_cst);
        csr_[0] = value;
        std::atomic_thread_fence(std::memory_order_seq_cst);
    }

private:
    bool read_only_;
    int fd_ = -1;
    void *data_ = MAP_FAILED;
    volatile std::uint32_t *csr_ = nullptr;
};
}
