"""Decode consecutive, physically sampled 512-bit HP2 records (ABI HPT1)."""
import argparse
import json
from pathlib import Path

FLAGS = ['PS_HP2_resetn', 'PL_HP2_resetn', 'GP_reset', 'HP_reset', 'FCLK_RESET0_N',
    'DDR_ui_reset', 'DDR_calibrated', 'reserved_heartbeat', 'PS_ARVALID_copy', 'PS_RVALID_copy',
    'S01_ARVALID_copy', 'S01_RVALID_copy', 'S01_AWVALID', 'S01_WVALID', 'S01_BVALID',
    'PS_AWVALID', 'PS_WVALID', 'PS_BVALID', 'sys_rst_n', 'soft_reset',
    'DDR_calibrated_copy', 'DDR_ui_reset_copy', 'HP_reset_copy', 'PL_HP2_resetn_copy', 'pl_rst_n']
FIELDS = {'ARADDR': (0, 32), 'ARID': (32, 6), 'ARLEN': (38, 4), 'ARSIZE': (42, 3),
    'ARBURST': (45, 2), 'ARLOCK': (47, 2), 'ARCACHE': (49, 4), 'ARPROT': (53, 3), 'ARQOS': (56, 4),
    'ARVALID': (60, 1), 'ARREADY': (61, 1), 'RVALID': (62, 1), 'RREADY': (63, 1),
    'RID': (64, 6), 'RRESP': (70, 2), 'RLAST': (72, 1)}

def decode_record(words):
    if len(words) != 16 or any(type(w) != int or not 0 <= w < 2 ** 32 for w in words):
        raise ValueError('Invalid raw sample words')
    value = sum(w << (32 * i) for i, w in enumerate(words))
    take = lambda bit, width: (value >> bit) & ((1 << width) - 1)
    row = {'HP_cycle': take(0, 64)}
    for name, offset, data in [('PS', 64, 283), ('S01', 137, 347), ('HC2', 210, 411)]:
        row.update({name + '_' + key: take(offset + bit, width) for key, (bit, width) in FIELDS.items()})
        row[name + '_RDATA'] = take(data, 64)
    flags = take(475, 32)
    row.update({name: (flags >> i) & 1 for i, name in enumerate(FLAGS)})
    row['raw_flags'] = flags
    return row

def decode(snapshot):
    if snapshot['abi'] != 0x48505401 or snapshot['format'] != 0x01028010:
        raise ValueError('Wrong physical trace ABI/format')
    result = {'sampling': 'Consecutive source_clk rising edges; nominal HP 200 MHz / 5 ns',
        'boot_id': snapshot['boot_id'], 'status': snapshot['status'], 'banks': [],
        'limits': ['BRAM recorder, not a vendor ILA export.',
        'Flags are pin levels sampled in HP domain; asynchronous flags have edge uncertainty.',
        'No coverage before PL configuration or while HP clock is absent.',
        'RDATA/RID/RRESP/RLAST have protocol meaning only when RVALID=1.',
        'DDR_calibrated is PL MIG init_calib_complete, not a PS DDR initialization indicator.',
        'Initial high does not establish an observed reset release edge.',
        'No PS internal FIFO occupancy or reset completion proof.']}
    for bank in snapshot['banks']:
        if not bank['published']:
            result['banks'].append(dict(bank=bank['bank'], published=False,
                fired=bool(snapshot['status'] & (1 << (2 * bank['bank'])))))
            continue
        rows = [decode_record(w) for w in bank['samples']]
        count = bank['count']
        index = bank['trigger_index']
        cycle = bank['trigger_cycle']
        if not (len(rows) == count and 96 <= count <= 128 and 0 <= index <= 32 and count == 96 + index):
            raise ValueError('Malformed capture descriptor')
        if any(b['HP_cycle'] != a['HP_cycle'] + 1 for a, b in zip(rows, rows[1:])):
            raise ValueError('Samples are not consecutive; raw retained')
        if rows[index]['HP_cycle'] != cycle:
            raise ValueError('Trigger cycle differs')
        key = 'PS_RVALID' if bank['bank'] == 0 else 'PL_HP2_resetn'
        if rows[index][key] != 1 or (index and rows[index - 1][key] != 0):
            raise ValueError('Trigger level/edge differs')
        signals = ['PS', 'S01', 'HC2']
        handshakes = {s + '_' + ch: sum(r[s + '_' + ch + 'VALID'] and r[s + '_' + ch + 'READY'] for r in rows)
            for s in signals for ch in ('AR', 'R')}
        result['banks'].append(dict(bank=bank['bank'], published=True, count=count,
            trigger_index=index, trigger_cycle=cycle, first_HP_cycle=rows[0]['HP_cycle'],
            last_HP_cycle=rows[-1]['HP_cycle'], trigger_initial_high=index == 0,
            observed_reset_release_edge=bank['bank'] == 1 and index > 0,
            handshakes=handshakes, rows=rows))
    return result

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('raw', type=Path)
    p.add_argument('output', type=Path)
    a = p.parse_args()
    result = decode(json.loads(a.raw.read_text()))
    with a.output.open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    print(json.dumps({'published_banks': sum(b['published'] for b in result['banks'])}))
