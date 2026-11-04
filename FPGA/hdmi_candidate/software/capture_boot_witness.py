"""Decode the complete raw JSONL produced by capture_boot_witness.cpp; no MMIO."""
import argparse, json
from pathlib import Path

def decode(w):
    flags = w[1]
    gp = w[18]
    return dict(scope='first source clocks after configuration; retained across local PL reset',
        source_cycles=None if flags & (1 << 17) else((flags >> 24) << 32) | w[2],
        GP_cycles=None if gp & (1 << 16) else((gp >> 24) << 32) | w[15],
        source_flags=(flags >> 8) & 31, GP_sampled_source_flags=(gp >> 1) & 31,
        PS_AR_raw_handshakes=w[3], PS_R_raw_handshakes=w[4],
        HDMI_AR_raw_handshakes=w[5], HDMI_R_raw_handshakes=w[6],
        first_PS_AR_seen=bool(flags & 1), first_PS_RVALID_seen=bool(flags & 2),
        first_HDMI_AR_seen=bool(flags & 4), PS_RVALID_before_any_observed_AR=bool(flags & 8),
        raw_AR_during_reset=bool(flags & 16), raw_AR_before_calibration=bool(flags & 32),
        PS_RVALID_during_reset=bool(flags & 64), handshake_counter_overflows=(flags >> 13) & 15,
        first_PS_AR_address=hex(w[7]), first_PS_AR_ID=(w[8] >> 4) & 63,
        first_PS_RID=(w[9] >> 19) & 63, first_PS_RRESP=(w[9] >> 25) & 3,
        first_PS_RVALID_cycle_mod_2_32=w[10],
        first_HDMI_AR_address=hex(w[11]), first_HDMI_AR_cycle_mod_2_32=w[12],
        GP_reset_assertions=w[13], HP2_reset_assertions=w[14],
        GP_reset_high_cycles=w[16], HP2_reset_low_GP_cycles=w[17],
        GP_counter_overflows=(gp >> 8) & 15, GP_reset_seen=bool(gp & (1 << 13)),
        HP2_reset_seen=bool(gp & (1 << 12)), snapshot_published=bool(gp & 128),
        cut='source before FREEZE edge; GP before CSR acknowledgement commit')

def prefix_counts(boot, legacy):
    """Both banks share the source FREEZE edge; don't subtract wrapped counters."""
    if len(legacy) != 104 or legacy[0] != 0x41495201:
        raise ValueError('Legacy snapshot ABI/count differs')
    overflows = (boot[1] >> 13) & 15
    result = {}
    for bit, (name, index) in enumerate([('PS_AR', 88), ('PS_R', 89), ('HDMI_AR', 72), ('HDMI_R', 73)]):
        total = boot[3 + bit]
        window = legacy[index]
        if overflows & (1 << bit):
            result[name] = None
        elif total < window:
            raise ValueError('Boot/epoch snapshots inconsistent; preserve and stop interpretation')
        else:
            result[name] = total - window
    return result

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('raw', type=Path)
    p.add_argument('--legacy', type=Path, help='Raw 104-word trace from the same completed FREEZE')
    a = p.parse_args()
    rows = [json.loads(line) for line in a.raw.read_text().splitlines() if line.strip()]
    before = next(x for x in rows if x.get('event') == 'boot_witness_initial')
    snapshot = next(x for x in rows if x.get('event') == 'boot_witness_snapshot')
    w = snapshot['words']
    seq = before['expected_sequence']
    if not (len(w) == 19 and w[0] == 0x42545201 and w[18] & 128 and before['abi'] == 0x41495201 and before['count'] == 104 and
        before['status'] == 0 and before['request'] == before['response'] == seq and snapshot['after'] == dict(status=0,
        request=seq, response=seq)):
        raise RuntimeError('Raw witness identity/generation invalid; do not reinterpret it')
    result = decode(w)
    if a.legacy:
        epochs = [json.loads(line) for line in a.legacy.read_text().splitlines() if line.strip()]
        matches = [x for x in epochs if len(x.get('words', [])) == 104 and x.get('sequence', x.get('request')) == seq]
        if len(matches) != 1:
            raise ValueError('Expected exactly one matching legacy FREEZE')
        result['raw_handshakes_at_or_before_current_ARM'] = prefix_counts(w, matches[0]['words'])
    print(json.dumps(result, indent=2))
if __name__ == '__main__':
    main()
