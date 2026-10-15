"""Decode a GR IIIx settings export (C:\\KB609.DOM from `dd_out`) into item = value.

Uses data/userdata_set_values.tsv: the `store` column (e.g. u8@0x2aa) is the offset
inside sub-record APData01.bin (the active UserData struct; APData02..08 are the
other struct copies), and the `values` column maps internal numbers back to tokens.

Usage: python3 -I tools/dom_parse.py KB609.DOM data/userdata_set_values.tsv [filter]
Prints: item<TAB>value<TAB>raw
Export at least a few seconds after boot: an export at the very start of
startup.ttl returned default values (test 6).
"""
import struct
import sys


def chunks(d):
    p = 0
    while p + 8 <= len(d):
        tag = d[p:p + 4].rstrip(b'\0').decode('latin1')
        ln = struct.unpack_from('<I', d, p + 4)[0]
        yield tag, d[p + 8:p + 8 + ln]
        p += 8 + ln


def subrecords(b):
    q = 0
    while q + 0x18 <= len(b):
        h = b[q:q + 0x3c]
        plain = struct.unpack_from('<I', h, 0x14)[0] == 0 and struct.unpack_from('<I', h, 0x18)[0] == 0
        hl = 0x3c if plain else 0x14
        name = h[:0x14].split(b'\0')[0].decode('latin1')
        size = struct.unpack_from('<I', b, q + hl)[0]
        yield name, b[q + hl + 4:q + hl + 4 + size]
        q += hl + 4 + size


def load(path):
    recs = {}
    for tag, body in chunks(open(path, 'rb').read()):
        for name, data in subrecords(body):
            recs[f'{tag}/{name}'] = data
    return recs


FMT = {'u8': '<B', 'u16': '<H', 'u32': '<I', 'f32': '<f'}


def main():
    recs = load(sys.argv[1])
    ud = recs['APP/APData01.bin']
    flt = sys.argv[3] if len(sys.argv) > 3 else ''
    rows = [l.rstrip('\n').split('\t') for l in open(sys.argv[2])][1:]
    for item, kind, values, _setter, _handler, store in rows:
        if flt not in item or not store:
            continue
        width, off = store.split('@')
        off = int(off, 16)
        width = width.split('*')[0]
        if off + struct.calcsize(FMT[width]) > len(ud):
            continue
        raw = struct.unpack_from(FMT[width], ud, off)[0]
        val = raw
        if kind == 'enum':
            table = {}
            for tok in values.split(' '):
                if '=' in tok:
                    k, v = tok.rsplit('=', 1)
                    table.setdefault(int(v) & (0xFF if width == 'u8' else 0xFFFFFFFF), k)
            val = table.get(raw, f'?{raw}')
        elif width == 'f32':
            val = round(raw, 4)
        print(f'{item}\t{val}\t{raw}')


if __name__ == '__main__':
    main()
