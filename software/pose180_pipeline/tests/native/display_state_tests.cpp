#include "display_state.hpp"
#include <algorithm>
#include <array>
#include <iostream>
#include <stdexcept>

namespace {
namespace hdmi = pose::hdmi;
using State = pose180_demo::DisplayState;
using Kind = hdmi::NoticeKind;
constexpr std::uint64_t second = 1000000000;

void expect(bool ok, const char* message) {
	if (!ok)
		throw std::runtime_error(message);
}

void waiting_recovery_and_counts() {
	State state;
	auto first = state.hint(0, false, false);
	expect(first && first->kind == Kind::WaitingInput && !first->has_result,
		"Initial waiting screen pretended a model result existed");
	expect(state.next_tag() == 1, "First hardware submission tag differs");
	state.adopted_hint(*first, 0);
	expect(!state.hint(500000000, false, false), "Unchanged waiting view redrawn");
	expect(!state.hint(20 * second, false, false), "No-result waiting view acquired a fake age");
	auto syncing = state.hint(second, true, false);
	expect(syncing && syncing->kind == Kind::Resynchronizing, "Initial resync not visible");
	expect(state.next_tag() == 2, "Hint reused a hardware tag");
	state.adopted_hint(*syncing, second);
	// Real results bypass hint throttling and use the next presentation tag,
	// not inference sequence 1 or a reconnecting source frame identifier.
	expect(state.next_tag() == 3, "First real result collided with an earlier hint");
	state.adopted_result(second + 100000000);
	expect(state.results() == 1 && state.hints() == 2 && state.updates() == 3,
		"Hints inflated the real-result counter");
	expect(!state.hint(second + 600000000, true, false), "Brief missing window flickered RESULT");
	syncing = state.hint(2 * second + 100000000, true, false);
	expect(
		syncing && syncing->kind == Kind::Resynchronizing && syncing->has_result && syncing->age_seconds == 1,
		"Persistent resync did not preserve and age the real result");
	expect(state.next_tag() == 4, "Resync tag not monotonic");
	state.adopted_hint(*syncing, 2 * second + 100000000);
	expect(!state.hint(2 * second + 900000000, false, false), "Hint transition bypassed frequency bound");
	auto stale = state.hint(3 * second + 100000000, true, false);
	expect(stale && stale->kind == Kind::Stale && stale->age_seconds == 2 && stale->resynchronizing,
		"Old result was still presented as current");
	expect(state.next_tag() == 5, "Stale tag not monotonic");
	state.adopted_hint(*stale, 3 * second + 100000000);
	expect(!state.hint(4 * second + 100000000, true, true), "Isolation permitted a new device presentation");
	expect(state.next_tag() == 6, "Recovered real result collided with a hint");
	state.adopted_result(4 * second + 100000000);
	expect(!state.hint(4 * second + 600000000, false, false), "Recovered RESULT did not clear stale state");
	expect(state.results() == 2 && state.hints() == 4 && state.updates() == 6,
		"Successful hint adoption changed inference/adoption semantics");
	auto waiting = state.hint(5 * second + 100000000, false, false);
	expect(waiting && waiting->kind == Kind::WaitingInput && waiting->age_seconds == 1,
		"Missing input without resync has the wrong notice");
}

bool same_viewport(const std::vector<std::uint8_t>& a, const std::vector<std::uint8_t>& b) {
	// Full-width scene below the header; notices may only change the header.
	for (std::size_t y = 250; y < 1040; ++y)
		if (!std::equal(a.begin() + y * 1920 * 2, a.begin() + (y + 1) * 1920 * 2, b.begin() + y * 1920 * 2))
			return false;
	return true;
}

void real_pose_and_empty_notice_pixels() {
	auto background = hdmi::prepare_background();
	auto empty =
		hdmi::render_notice(hdmi::prepare_background(), nullptr, 0, {Kind::WaitingInput, false, false, 0});
	constexpr std::array<std::uint16_t, 7> bars{0xffff, 0xffe0, 0x07ff, 0x07e0, 0xf81f, 0xf800, 0x001f};
	expect(empty.detection_count == 0 && empty.score == 0, "Standby manufactured a detection");
	for (unsigned y = 0; y < hdmi::height; ++y)
		for (unsigned x = 0; x < hdmi::width; ++x) {
			const auto at = (y * hdmi::width + x) * 2;
			const auto pixel = std::uint16_t(empty.rgb565[at]) | (std::uint16_t(empty.rgb565[at + 1]) << 8);
			expect(pixel == bars[x * bars.size() / hdmi::width],
				"Standby bar order, extent or RGB565 packing differs");
		}
	auto initial_resync =
		hdmi::render_notice(hdmi::prepare_background(), nullptr, 0, {Kind::Resynchronizing, false, true, 0});
	expect(initial_resync.rgb565 == empty.rgb565, "No-result resync abandoned standby bars");
	std::array<float, 180> scores;
	scores.fill(0.1f);
	scores[179] = 0.8f;
	std::array<float, 7560> poses;
	for (std::size_t slot = 0; slot < 180; ++slot)
		for (std::size_t joint = 0; joint < 14; ++joint) {
			poses[slot * 42 + joint * 3] = 1.25f + float(joint % 4) * 0.125f;
			poses[slot * 42 + joint * 3 + 1] = 1.5f + float(joint % 3) * 0.1875f;
			poses[slot * 42 + joint * 3 + 2] = 2.75f + float(joint) * 0.0625f;
		}
	auto original = hdmi::render(hdmi::prepare_background(), scores.data(), poses.data(), 180, 42);
	expect(!same_viewport(background.rgb565, original.rgb565), "Test fixture did not produce visible joints");
	// Main retains only metadata after moving the CPU framebuffer back to its
	// one reusable canvas; a waiting render must not depend on a hidden copy.
	auto pixels = std::move(original.rgb565);
	auto notice = hdmi::render_notice(
		hdmi::prepare_background(), &original, 42, {Kind::Resynchronizing, true, true, 1});
	expect(same_viewport(pixels, notice.rgb565), "Resync changed the last real skeleton");
	expect(notice.top_index == 179 && notice.score == original.score &&
			notice.selected_raw == original.selected_raw && notice.projected == original.projected,
		"Notice altered highest-candidate selection or coordinates");
	auto stale = hdmi::render_notice(hdmi::prepare_background(), &original, 42, {Kind::Stale, true, true, 2});
	expect(same_viewport(pixels, stale.rgb565) && stale.rgb565 != notice.rgb565,
		"Stale label erased the pose or failed to change its visible status");
	auto older = hdmi::render_notice(hdmi::prepare_background(), &original, 42, {Kind::Stale, true, true, 3});
	// The approved minimal header omits numeric age. State still ages above,
	// but an unchanged STALE label must not add diagnostics back to the UI.
	expect(stale.rgb565 == older.rgb565, "Minimal stale view changed despite identical state and pose");
	auto restored = hdmi::render(hdmi::prepare_background(), scores.data(), poses.data(), 180, 42);
	expect(restored.rgb565 == pixels, "Resuming a real result left notice pixels behind");
	bool rejected = false;
	try {
		hdmi::render_notice(hdmi::prepare_background(), nullptr, 0, {Kind::Stale, true, false, 2});
	} catch (const std::runtime_error&) {
		rejected = true;
	}
	expect(rejected, "Notice accepted a missing last-result source");
}
}

int main() {
	try {
		waiting_recovery_and_counts();
		real_pose_and_empty_notice_pixels();
		std::cout << "display waiting/stale/recovery, unique tags, real-result counts and pixels passed\n";
		return 0;
	} catch (const std::exception& e) {
		std::cerr << "display state test failed: " << e.what() << '\n';
		return 1;
	}
}
