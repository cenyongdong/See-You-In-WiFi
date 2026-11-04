// 单槽交接：submit 等待相同 invocation 的完成；锁、通知与首个异常传播顺序保持不变。
// One owned result, finite waits and first-error wakeup; no SDK on publisher.
#pragma once
#include "application_core.hpp"
#include <condition_variable>
#include <mutex>
#include <optional>
class HdmiHandoff {
    std::mutex mutex_;
    std::condition_variable cv_;
    std::optional<pose_v1::application::Result> slot_;
    bool done_ = false;
    std::exception_ptr error_;
    template <class Predicate> void wait(std::unique_lock<std::mutex> &lock, Predicate predicate) {
        if (!cv_.wait_for(lock, std::chrono::seconds(5), [&] {
                return error_ || predicate();
            }))
            throw std::runtime_error("HDMI handoff 5s deadline");
        if (error_)
            std::rethrow_exception(error_);
    }

public:
    void fail(std::exception_ptr e) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (!error_)
            error_ = e;
        cv_.notify_all();
    }
    void submit(const pose_v1::application::Result &result) {
        std::unique_lock<std::mutex> lock(mutex_);
        if (error_)
            std::rethrow_exception(error_);
        if (slot_)
            throw std::runtime_error("Occupied HDMI handoff");
        slot_ = result;
        done_ = false;
        cv_.notify_all();
        wait(lock, [&] {
            return done_;
        });
        slot_.reset();
        cv_.notify_all();
    }
    pose_v1::application::Result take() {
        std::unique_lock<std::mutex> lock(mutex_);
        wait(lock, [&] {
            return slot_.has_value() && !done_;
        });
        return *slot_;
    }
    void complete(uint64_t invocation) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (!slot_ || slot_->invocation != invocation || done_)
            throw std::runtime_error("HDMI handoff identity differs");
        done_ = true;
        cv_.notify_all();
    }
};
