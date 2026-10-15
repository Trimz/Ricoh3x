"""GR IIIx (fw 1.60) settings toolkit: decode exports, diff them, build card scripts.

    python3 -I tools/grsettings.py decode  KB609.DOM [filter]
    python3 -I tools/grsettings.py diff    A.DOM B.DOM
    python3 -I tools/grsettings.py profile KB609.DOM > my.profile      # editable "Item = Value" lines
    python3 -I tools/grsettings.py script  my.profile OUTDIR [--export] [--force]

`script` validates every line against data/userdata_set_values.tsv and writes
OUTDIR/script/startup.ttl (CRLF, with marker lines in C:\\grset.txt). With
--export it also writes OUTDIR/script/shutdown.ttl that exports the saved
settings (dd_out) so the result can be checked with `diff`.

Items on the deny list (resets, language, wireless, user-mode registry,
internal state) and profiles with more than 20 items are refused unless --force.
WARNING: a 956-item round-trip "restore" left the test camera freezing after every
shot, surviving a settings reset and a firmware reinstall. Read
docs/incident-2026-10-15.md. Do not use --force for bulk writes.
"""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TSV = os.path.join(HERE, '..', 'data', 'userdata_set_values.tsv')

DENY_PREFIX = (
    'Common',                 # internal state: Tv/Av/Sv, menu cursor positions, live view geometry
    'SetupMenuReset',         # resets whole settings groups
    'SetupLanguage',          # can make the UI unreadable
    'SetupWlan', 'SetupBleMode', 'SetupAutoTransmit', 'SetupJpegTransmit', 'SetupRawTransmit',
    'SetupMovieTransmit', 'SetupTransmitResize', 'SetupPowerOffImageTransfer',
    'PlayJpegTransmitReserve', 'PlayRawTransmitReserve', 'PlayMovieTransmitReserve',
    'CustomSettingBox',       # user-mode registry U1-U3
    'PlayPlaybackFunctionLastSelectItem', 'PlayPlaybackDetailPage',
)

FMT = {'u8': '<B', 'u16': '<H', 'u32': '<I', 'f32': '<f'}
MAX_ITEMS = 20  # see docs/incident-2026-10-15.md


# ---------- table ----------

class Item:
    def __init__(self, row):
        self.name, self.kind, values, self.setter, self.handler, self.store = row
        self.tokens = {}   # token -> internal value
        self.by_value = {}
        for tok in values.split(' ') if values else []:
            if '=' in tok:
                k, v = tok.rsplit('=', 1)
                self.tokens[k] = int(v)
                self.by_value.setdefault(int(v), k)
        if self.store:
            w, off = self.store.split('@')
            self.width = w.split('*')[0]
            self.offset = int(off, 16)
        else:
            self.width = self.offset = None

    def denied(self):
        return self.name.startswith(DENY_PREFIX)


def load_table(path=TSV):
    rows = [l.rstrip('\n').split('\t') for l in open(path)][1:]
    return {r[0]: Item(r) for r in rows}


# ---------- export file ----------

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


def load_export(path):
    recs = {}
    for tag, body in chunks(open(path, 'rb').read()):
        for name, data in subrecords(body):
            recs[f'{tag}/{name}'] = data
    return recs


def decode(path, table):
    ud = load_export(path)['APP/APData01.bin']
    out = {}
    for it in table.values():
        if it.offset is None or it.offset + struct.calcsize(FMT[it.width]) > len(ud):
            continue
        raw = struct.unpack_from(FMT[it.width], ud, it.offset)[0]
        if it.kind == 'enum':
            mask = 0xFF if it.width == 'u8' else 0xFFFF if it.width == 'u16' else 0xFFFFFFFF
            val = next((k for v, k in it.by_value.items() if v & mask == raw), None)
        elif it.kind == 'float':
            val = repr(float(f'{raw:.9g}'))  # shortest text that round-trips the f32
        elif it.width == 'u16' and raw >= 0x8000 and raw != 0xFFFF:
            val = str(raw - 0x10000)  # signed 16-bit field (e.g. filter RGB); strtoul('-10') keeps the bits
        else:
            val = str(raw)
        out[it.name] = (val, raw)
    return out


# ---------- profiles ----------

def parse_profile(path):
    items = []
    for n, line in enumerate(open(path), 1):
        line = line.split('#', 1)[0].strip()
        if not line:
            continue
        if '=' in line:
            k, v = (s.strip() for s in line.split('=', 1))
        else:
            k, _, v = line.partition(' ')
            v = v.strip()
        items.append((n, k, v))
    return items


def validate(table, name, value):
    it = table.get(name)
    if it is None:
        return 'unknown item'
    if it.kind == 'enum':
        if value not in it.tokens:
            return f'value must be one of: {" ".join(it.tokens)}'
    elif it.kind == 'int':
        try:
            int(value, 0)
        except ValueError:
            return 'integer expected'
    elif it.kind == 'float':
        try:
            float(value)
        except ValueError:
            return 'number expected'
    else:
        return f'item kind {it.kind!r} not supported'
    if ' ' in value or "'" in value:
        return 'value contains a space or quote'
    return None


def write_scripts(table, profile, outdir, export, force):
    lines, errors = [], []
    for n, k, v in parse_profile(profile):
        err = validate(table, k, v)
        if not err and table[k].denied() and not force:
            err = 'on the deny list (use --force only if you really mean it)'
        if err:
            errors.append(f'{profile}:{n}: {k} = {v}: {err}')
        else:
            lines.append(f"sendln 'UserData Set {k} {v}'")
    if len(lines) > MAX_ITEMS and not force:
        errors.append(f'{len(lines)} settings: refusing to write more than {MAX_ITEMS} at once. '
                      'A bulk write damaged the test camera (docs/incident-2026-10-15.md).')
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        sys.exit(1)
    os.makedirs(os.path.join(outdir, 'script'), exist_ok=True)
    head = [f'; generated by tools/grsettings.py from {os.path.basename(profile)}: {len(lines)} settings',
            "filecreate fh 'C:\\grset.txt'", "filewriteln fh 'start'", 'fileclose fh']
    tail = ["fileopen fh 'C:\\grset.txt' 1", "filewriteln fh 'all settings sent'", 'fileclose fh']
    with open(os.path.join(outdir, 'script', 'startup.ttl'), 'w', newline='') as f:
        f.write('\r\n'.join(head + lines + tail) + '\r\n')
    if export:
        with open(os.path.join(outdir, 'script', 'shutdown.ttl'), 'w', newline='') as f:
            f.write('\r\n'.join(['; export saved settings for verification', "sendln 'dd_out'"]) + '\r\n')
    print(f'{len(lines)} settings -> {outdir}/script/startup.ttl' + (' (+ shutdown.ttl export)' if export else ''))


# ---------- CLI ----------

def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    table = load_table()
    cmd = argv[1]
    if cmd == 'decode':
        flt = argv[3] if len(argv) > 3 else ''
        for k, (v, raw) in decode(argv[2], table).items():
            if flt in k:
                print(f'{k}\t{v if v is not None else "?"}\t{raw}')
    elif cmd == 'diff':
        a, b = decode(argv[2], table), decode(argv[3], table)
        for k in a:
            if a[k][1] != b.get(k, (None, None))[1]:
                print(f'{k}: {a[k][0]} -> {b[k][0]}')
    elif cmd == 'profile':
        for k, (v, raw) in decode(argv[2], table).items():
            it = table[k]
            if v is None or it.denied():
                continue
            if it.kind == 'int' and raw in (0xFFFFFFFF, 0xFFFF):
                continue  # sentinel "unset" values: do not write back
            print(f'{k} = {v}')
    elif cmd == 'script':
        write_scripts(table, argv[2], argv[3], '--export' in argv, '--force' in argv)
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
