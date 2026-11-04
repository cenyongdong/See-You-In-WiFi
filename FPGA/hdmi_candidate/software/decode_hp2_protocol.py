"""Decode immutable 576-bit samples of the actual native AXI3 checker."""
import argparse, json
from pathlib import Path
from decode_hp2_cycletrace import FIELDS, FLAGS
from hp2_protocol_checks import CHECKS, TRIGGER_MASK

WRITE_FIELDS = {'AWADDR': (0, 32), 'AWID': (32, 6), 'AWLEN': (38, 4), 'AWSIZE': (42, 3),
    'AWBURST': (45, 2), 'AWLOCK': (47, 2), 'AWCACHE': (49, 4), 'AWPROT': (53, 3), 'AWQOS': (56, 4),
    'AWVALID': (60, 1), 'AWREADY': (61, 1), 'WDATA': (62, 64), 'WID': (126, 6), 'WSTRB': (132, 8),
    'WLAST': (140, 1), 'WVALID': (141, 1), 'WREADY': (142, 1), 'BID': (143, 6), 'BRESP': (149, 2),
    'BVALID': (151, 1), 'BREADY': (152, 1)}
PROTOCOL_FLAGS = FLAGS + ['PC_system_resetn', 'PC_checker_ready', 'PC_seen_reset_low', 'PC_asserted']
def category(bit):
    name = CHECKS.get(bit, '')
    if bit in (78, 80, 82):
        return 'checker_capacity'
    if bit in (79, 81):
        return 'checker_transaction_state'
    if 'RECM_' in name or 'RECS_' in name or bit in (92, 93, 94, 95, 96, 101):
        return 'recommendation'
    if bit in (104, 105, 106, 107):
        return 'AXI_error_response'
    if name.startswith(('AXI_ERR', 'AXI4LITE_ERR')):
        return 'protocol_rule'
    return 'configuration_check' if name else 'unmapped_status'

def checks(value):
    return [dict(bit=i, name=CHECKS.get(i, 'native_check_bit_' + str(i)), category=category(i)) for i in range(160) if value >> i & 1]

def decode_record_protocol(words):
    if len(words) != 18 or any(type(w) != int or not 0 <= w < 2 ** 32 for w in words):
        raise ValueError('Invalid protocol raw words')
    value = sum(w << (32 * i) for i, w in enumerate(words))
    take = lambda b, w: (value >> b) & ((1 << w) - 1)
    row = {'HP_cycle': take(0, 64)}
    row.update({'PS_' + name: take(64 + bit, width) for name, (bit, width) in FIELDS.items()})
    row['PS_RDATA'] = take(137, 64)
    row.update({'PS_' + name: take(201 + bit, width) for name, (bit, width) in WRITE_FIELDS.items()})
    flags = take(354, 32)
    row.update({name: (flags >> i) & 1 for i, name in enumerate(PROTOCOL_FLAGS)})
    row['raw_flags'] = flags
    row['PC_status'] = take(386, 160)
    return row

def decode(snapshot):
    modern = snapshot['abi'] == 0x48505002 and snapshot['format'] == 0x02018012
    if not modern and not (snapshot['abi'] == 0x48505001 and snapshot['format'] == 0x01018012):
        raise ValueError('Wrong protocol capture ABI/format')
    mask = TRIGGER_MASK if modern else(1 << 160) - 1
    if modern and snapshot.get('trigger_mask') != mask:
        raise ValueError('Actual trigger mask differs')
    status = snapshot['status']
    result = dict(boot_id=snapshot['boot_id'], status=status,
        published=bool(status & 2), fired=bool(status & 1), sampling='Actual consecutive HP edges, nominal 200MHz / 5ns',
        checker='Native axi_protocol_checker 2.0 Rev.4, AXI3, all 160 status bits',
        live_flags={name: bool(status >> bit & 1) for bit, name in [(2, 'PS_HP2_resetn'), (3, 'PC_system_resetn'),
        (4, 'PC_checker_ready'), (5, 'PC_seen_reset_low')]},
        limits=['No visibility before configuration or without HP clock.',
        'Native checker initializes independently; flags identify whether a PS reset-low was seen after checker startup.',
        'Missing pre-existing AR history can cause an unmatched-return report.',
        'Checker status reports have pipeline latency; preserve preceding raw samples.',
        'Window triggers on the first native indication, including vendor recommendations; classification is reported separately.',
        'Later indications beyond the frozen window are not captured by this first-indication buffer.',
        'Backpressure and vendor recommendation flags are not automatically protocol errors.'])
    if modern:
        result['trigger_semantics'] = 'First non-recommendation native status; full status preserved'
        result['limits'] = [x for x in result['limits'] if not x.startswith(('Window triggers', 'Later indications'))]
        result['limits'].append('First indication witness and first transaction-error window are independent; neither covers later changes after freezing.')
        witness = snapshot.get('first_indication', {})
        result['first_indication'] = dict(witness, checks=checks(witness.get('status', 0)))
        if witness.get('published'):
            if not witness.get('status') or len(witness.get('status_words', [])) != 5 or sum(w << (32 * i) for i,
                w in enumerate(witness['status_words'])) != witness['status']:
                raise ValueError('First-indication raw words differ')
    if not result['published']:
        return result
    bank = snapshot['capture']
    rows = [decode_record_protocol(words) for words in bank['samples']]
    count, index = bank['count'], bank['trigger_index']
    cycle = bank['trigger_cycle']
    if not (len(rows) == count == 96 + index and 0 <= index <= 32):
        raise ValueError('Malformed protocol descriptor')
    if any(b['HP_cycle'] != a['HP_cycle'] + 1 for a, b in zip(rows, rows[1:])):
        raise ValueError('Nonconsecutive protocol samples')
    if rows[index]['HP_cycle'] != cycle or not (rows[index]['PC_status'] & mask) or (index and rows[index - 1]['PC_status'] & mask):
        raise ValueError('Protocol trigger mismatch')
    if rows[index]['PC_status'] != bank['first_status']:
        raise ValueError('First status differs from actual trigger sample')
    if 'first_status_words' in bank and sum(w << (32 * i) for i, w in enumerate(bank['first_status_words'])) != bank['first_status']:
        raise ValueError('Raw first-status words differ')
    result.update(count=count, trigger_index=index, trigger_cycle=cycle, rows=rows,
        first_status=bank['first_status'], first_status_hex='0x' + format(bank['first_status'], '040x'),
        first_checks=checks(bank['first_status']),
        first_after_observed_PS_reset=bool(rows[index]['PC_seen_reset_low']),
        first_after_checker_ready=bool(rows[index]['PC_checker_ready']),
        handshakes={channel: sum(r['PS_' + channel + 'VALID'] and r['PS_' + channel + 'READY'] for r in rows) for channel in ['AR',
        'R', 'AW', 'W', 'B']})
    union = 0
    first_protocol = None
    for row in rows:
        union |= row['PC_status']
        actual = [c for c in checks(row['PC_status']) if c['category'] == 'protocol_rule']
        if actual and first_protocol is None:
            first_protocol = dict(HP_cycle=row['HP_cycle'], checks=actual)
    result.update(all_checks_in_window=checks(union), first_protocol_rule_in_window=first_protocol,
        checker_capacity_exceeded=any(c['category'] == 'checker_capacity' for c in checks(union)))
    return result

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('raw', type=Path)
    p.add_argument('output', type=Path)
    a = p.parse_args()
    result = decode(json.loads(a.raw.read_text()))
    a.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'rows'}))
