"""Decode raw r26 words; distinguish HP handshakes from synchronized GP levels."""
import argparse
import json
from pathlib import Path

LEVELS = ['PS_HP2_resetn', 'PL_HP2_resetn', 'GP_reset', 'HP_reset', 'FCLK_RESET0_N',
    'DDR_ui_reset', 'DDR_calibrated', 'HP_clock_active', 'PS_ARVALID', 'PS_RVALID',
    'HDMI_ARVALID', 'HDMI_RVALID', 'legacy_AWVALID', 'legacy_WVALID', 'legacy_BVALID',
    'PS_AWVALID', 'PS_WVALID', 'PS_BVALID', 'sys_rst_n', 'soft_reset']
FIRST = ['PS_release_or_initial_high', 'PL_release_or_initial_high', 'PS_RVALID',
    'HDMI_RVALID', 'PS_ARVALID', 'HDMI_ARVALID', 'HP_clock_activity', 'write_VALID']

def decode(w):
    if len(w) != 128 or w[0] != 0x50534c01 or (w[1] & 3) != 3 or w[7] != 1:
        raise ValueError('Wrong ABI, publication or capture ordinal; preserve raw')
    u64 = lambda i: w[i] | (w[i + 1] << 32)
    levels = lambda x: {n: bool(x & (1 << i)) for i, n in enumerate(LEVELS)}
    seen = (w[1] >> 3) & 255
    first = {n: (u64(8 + 2 * i) if seen & (1 << i) else None) for i, n in enumerate(FIRST)}
    a, b = first[FIRST[0]], first[FIRST[1]]
    ordering = 'not observed'
    if a is not None and b is not None:
        ordering = 'unresolved within 3 GP cycles' if abs(a - b) < 3 else('PS earlier' if a < b else 'PL earlier')
    high_ordering = ordering
    if w[4] & 3:
        ordering = 'unresolved: initial high is not an observed release edge'
    def last_edge(i, bit, first_high):
        value = u64(i)
        if value == 0 or (w[4] & (1 << bit) and value == first_high):
            return None
        return value
    events = [{'GP_cycle': u64(64 + 3 * i), 'levels': levels(w[66 + 3 * i])} for i in range(min(w[6],
        16))]
    source_seen = w[34] & 15
    result = {'ABI': '0x50534c01', 'GP_freeze_cycle': u64(2), 'initial_GP_levels': levels(w[4]),
        'final_GP_levels': levels(w[5]), 'first_GP_cycle': first, 'first_release_order': ordering,
        'first_high_observation_order': high_ordering,
        'last_PS_release_GP_cycle': last_edge(24, 0, a), 'last_PL_release_GP_cycle': last_edge(26, 1,
        b),
        'last_PS_high_indication_GP_cycle': u64(24), 'last_PL_high_indication_GP_cycle': u64(26),
        'last_HP_heartbeat_GP_cycle': u64(28), 'HP_heartbeat_age_GP_cycles': w[30],
        'event_overflow': bool(w[1] & 4), 'events': events, 'HP_freeze_cycle': u64(32),
        'raw_HP_handshakes': dict(zip(['PS_AR', 'PS_R', 'legacy_AW', 'legacy_W', 'legacy_B', 'PS_AW',
        'PS_W', 'PS_B'], w[36: 44])),
        'HP_count_overflow_mask': (w[34] >> 4) & 255,
        'first_PS_AR_HP_cycle': u64(44) if source_seen & 1 else None,
        'first_raw_PS_RVALID_HP_cycle': u64(46) if source_seen & 2 else None,
        'first_write_handshake_HP_cycle': u64(48) if source_seen & 4 else None,
        'first_raw_PS_RVALID_pins': w[50] if source_seen & 2 else None,
        'first_raw_PS_RVALID_levels': {k: v for k, v in levels(w[51]).items() if k != 'HP_clock_active'} if source_seen & 2 else None,
        'first_PL_ready_PS_RVALID_HP_cycle': u64(53) if source_seen & 8 else None,
        'first_PL_ready_PS_RVALID_pins': w[55] if source_seen & 8 else None,
        'limits': ['GP records synchronized levels, may miss short pulses; HP counts are raw including reset.',
        'GP and HP FREEZE cuts differ; first high at observation start does not prove a reset edge.',
        'Event overflow leaves dedicated first records valid but can hide later transitions.',
        'HP activity expires 255 GP cycles after last divided heartbeat; it is a coarse clock witness.',
        'No pre-configuration/clockless request coverage or direct PS FIFO occupancy.']}
    return result

def main():
    p = argparse.ArgumentParser()
    p.add_argument('raw', type=Path)
    p.add_argument('output', type=Path)
    a = p.parse_args()
    records = [json.loads(x) for x in a.raw.read_text().splitlines() if x.strip()]
    snapshot = next(x for x in records if x.get('event') == 'ps_release_snapshot')
    result = decode(snapshot['words'])
    with a.output.open('x') as f:
        json.dump(result, f, indent=2)
    print(json.dumps({k: result[k] for k in ('first_release_order', 'event_overflow', 'raw_HP_handshakes')}))

if __name__ == '__main__':
    main()
