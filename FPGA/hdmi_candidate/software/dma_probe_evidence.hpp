#pragma once
#include <algorithm>
#include <cerrno>
#include <cstring>
#include <ostream>
#include <stdexcept>
#include <streambuf>
#include <string>
#include <vector>
#include <fcntl.h>
#include <unistd.h>
namespace pose::dma_probe_evidence {
std::runtime_error io_error(const std::string &operation, const std::string &path) {
    const int saved_errno = errno;
    return std::runtime_error(operation + ": " + path + ": " + std::strerror(saved_errno));
}

// O_EXCL prevents evidence replacement. No buffered userspace bytes remain
// when _Exit preserves the SDK's possibly in-flight allocation after a fault.
class ExclusiveLogBuffer final : public std::streambuf {
public:
    explicit ExclusiveLogBuffer(const std::string &path)
        : fd_(::open(path.c_str(), O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC | O_NOFOLLOW, 0600)) {
        if (fd_ < 0)
            throw io_error("Cannot create fresh trace", path);
    }
    ~ExclusiveLogBuffer() override {
        if (fd_ >= 0)
            ::close(fd_);
    }
    ExclusiveLogBuffer(const ExclusiveLogBuffer &) = delete;
    ExclusiveLogBuffer &operator=(const ExclusiveLogBuffer &) = delete;
    void commit() {
        if (!okay_)
            throw std::runtime_error("Evidence trace write previously failed");
        while (::fsync(fd_) != 0) {
            if (errno != EINTR)
                throw io_error("Trace fsync failed", "trace");
        }
    }

protected:
    std::streamsize xsputn(const char *data, std::streamsize bytes) override {
        std::streamsize written = 0;
        while (written < bytes) {
            const auto result = ::write(fd_, data + written, static_cast<std::size_t>(bytes - written));
            if (result < 0 && errno == EINTR)
                continue;
            if (result <= 0) {
                okay_ = false;
                break;
            }
            written += static_cast<std::streamsize>(result);
        }
        return written;
    }
    int_type overflow(int_type value) override {
        if (traits_type::eq_int_type(value, traits_type::eof()))
            return traits_type::not_eof(value);
        const char byte = traits_type::to_char_type(value);
        return xsputn(&byte, 1) == 1 ? value : traits_type::eof();
    }
    int sync() override {
        return okay_ ? 0 : -1;
    }

private:
    int fd_ = -1;
    bool okay_ = true;
};

class EvidenceLog final {
public:
    explicit EvidenceLog(const std::string &path) : buffer_(path), stream_(&buffer_) {
    }
    std::ostream &stream() noexcept {
        return stream_;
    }
    void commit() {
        stream_.flush();
        if (!stream_)
            throw std::runtime_error("Evidence trace stream failed");
        buffer_.commit();
    }

private:
    ExclusiveLogBuffer buffer_;
    std::ostream stream_;
};

std::string quoted(const std::string &value) {
    constexpr char digits[] = "0123456789abcdef";
    std::string result = "\"";
    for (const unsigned char byte : value) {
        if (byte == '"' || byte == '\\') {
            result.push_back('\\');
            result.push_back(static_cast<char>(byte));
        } else if (byte < 0x20) {
            result += "\\u00";
            result.push_back(digits[byte >> 4]);
            result.push_back(digits[byte & 0x0f]);
        } else
            result.push_back(static_cast<char>(byte));
    }
    result.push_back('"');
    return result;
}

std::string artifact(const std::string &trace, std::size_t bytes, const char *role) {
    return trace + "." + std::to_string(bytes) + "." + role + ".bin";
}

void save_binary_fresh(const std::string &path, const std::vector<char> &bytes) {
    const int fd = ::open(path.c_str(), O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC | O_NOFOLLOW, 0600);
    if (fd < 0)
        throw io_error("Cannot create fresh binary evidence", path);
    try {
        std::size_t written = 0;
        while (written < bytes.size()) {
            const auto count = ::write(fd, bytes.data() + written, bytes.size() - written);
            if (count < 0 && errno == EINTR)
                continue;
            if (count <= 0) {
                if (count == 0)
                    errno = EIO;
                throw io_error("Binary evidence write failed", path);
            }
            written += static_cast<std::size_t>(count);
        }
        while (::fsync(fd) != 0) {
            if (errno != EINTR)
                throw io_error("Binary evidence fsync failed", path);
        }
    } catch (...) {
        ::close(fd);
        throw;
    }
    if (::close(fd) != 0)
        throw io_error("Binary evidence close failed", path);
}

void flush_log(std::ostream &log) {
    log.flush();
    if (!log)
        throw std::runtime_error("Evidence trace write failed");
}

}
