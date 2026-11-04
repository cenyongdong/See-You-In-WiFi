from pathlib import Path
import sys, json, copy
C = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(C / 'FPGA/hdmi_candidate/software'))
from decode_hp2_protocol import decode, TRIGGER_MASK, category
from hp2_protocol_checks import RECOMMENDATION_BITS
recs = sum(1 << i for i in (92, 93, 95))
hard = (1 << 59) | (1 << 159)
assert all((TRIGGER_MASK >> i & 1) == (category(i) != 'recommendation') for i in range(160))
first = dict(published=True, HP_cycle=800, status=recs, status_words=[recs >> (32 * i) & 0xffffffff for i in range(5)])
rows = []
for i in range(128):
    status = recs | (hard if i >= 32 else 0)
    packed = 1000 + i | ((1 << 64) - 1) << 137 | status << 386
    rows.append([packed >> (32 * j) & 0xffffffff for j in range(18)])
raw = dict(abi=0x48505002, format=0x02018012, boot_id='UNIT_FIXTURE_NOT_BOARD', status=3, trigger_mask=TRIGGER_MASK,
    first_indication=first,
    capture=dict(count=128, trigger_index=32, trigger_cycle=1032, first_status=recs | hard, first_status_words=[(recs | hard) >> (32 * i) & 0xffffffff for i in range(5)],
    samples=rows))
actual = decode(raw)
assert actual['first_indication']['status'] == recs and actual['rows'][31]['PC_status'] == recs
assert actual['rows'][32]['PC_status'] == recs | hard and actual['rows'][0]['PS_RDATA'] == (1 << 64) - 1
assert actual['first_protocol_rule_in_window']['checks'][0]['bit'] == 59
quiet = copy.deepcopy(raw)
quiet['status'] = 0
quiet.pop('capture')
result = decode(quiet)
assert not result['published'] and result['first_indication']['checks']
for kind in ('mask', 'previous_error', 'word_precision'):
    bad = copy.deepcopy(raw)
    if kind == 'mask':
        bad['trigger_mask'] ^= 1 << 92
    if kind == 'previous_error':
        bad['capture']['samples'][31][13] |= 1 << 29  # PC bit59 at overall bit445
    if kind == 'word_precision':
        bad['first_indication']['status_words'][2] ^= 1
    try:
        decode(bad)
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid capture accepted: ' + kind)
print('Modern decoder: recommendation prefix, high status bit159, full RDATA64, witness-only and malformed evidence cases passed')
