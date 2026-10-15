"""Static extractor for the `UserData Set <Item> <Value>` shell command (GR IIIx fw 1.60).

Walks the item strcmp chain in the Set handler (FUN_5334688c), follows each
item's tail-call to its value parser, and classifies it as:
  enum   - strcmp chain over argv[3]; each token -> constant passed to a setter
  float  - strtod (0x53143b48)
  int    - strtoul/strtol (0x53143e20 / 0x53143ff0)
  ?      - anything else (inspect by hand)

Usage: python3 -I tools/userdata_values.py out/rtos.bin > docs/userdata_set_values.tsv
Output columns: item, kind, values (token=enum ...), setter address, handler address.
"""
import struct
import sys

B = 0x53000000
SET_LO, SET_HI = 0x5334688C, 0x5334CA00
STRCMP = 0x531416E8
STRTOD, STRTOUL, STRTOL = 0x53143B48, 0x53143E20, 0x53143FF0
MODEL_GETTERS = {0x5320AD88, 0x5320B31C}

d = open(sys.argv[1], 'rb').read()


def w(a):
    return struct.unpack_from('<I', d, a - B)[0]


def cstr(a):
    o = a - B
    if not 0 <= o < len(d):
        return None
    x = d[o:o + 96].split(b'\0')[0]
    return x.decode() if x and all(32 <= c < 127 for c in x) else None


def imm16(x):
    return ((x >> 4) & 0xF000) | (x & 0xFFF)


def branch_target(a, x):
    off = x & 0xFFFFFF
    if off & 0x800000:
        off -= 0x1000000
    return a + 8 + off * 4


def blx_target(a, x):  # BLX immediate (ARM -> Thumb or ARM)
    return branch_target(a, x) + ((x >> 24) & 1) * 2


def call_target(a, x):
    if (x & 0xFE000000) == 0xFA000000:
        return blx_target(a, x)
    if (x & 0x0F000000) == 0x0B000000:
        return branch_target(a, x)
    return None


def arm_imm(x):
    rot = ((x >> 8) & 0xF) * 2
    v = x & 0xFF
    return ((v >> rot) | (v << (32 - rot))) & 0xFFFFFFFF


def r1_string(a, limit=5):
    """If a movw r1 at a is completed by a movt r1 within `limit` words, return the string."""
    x = w(a)
    if (x & 0x0FF0F000) != 0x03001000:
        return None
    for k in range(1, limit):
        y = w(a + 4 * k)
        if (y & 0x0FF0F000) == 0x03401000:
            return cstr(imm16(y) << 16 | imm16(x))
    return None


def item_chain():
    out, a = [], SET_LO
    while a < SET_HI:
        n = r1_string(a)
        if n:
            for k in range(2, 10):
                x = w(a + 4 * k)
                if (x & 0xFF000000) == 0x0A000000:  # beq
                    out.append((n, branch_target(a + 4 * k, x)))
                    break
        a += 4
    return out


def tail(t):
    for k in range(10):
        x = w(t + 4 * k)
        if (x & 0xFF000000) == 0xEA000000:
            return branch_target(t + 4 * k, x)
    return t


def value_at(x0):
    """From a token's branch target, find the constant put in r1 before the setter call."""
    r1, a = None, x0
    for _ in range(12):
        x = w(a)
        if (x & 0x0FFFF000) == 0x03A01000:
            r1 = arm_imm(x)
        elif (x & 0x0FFFF000) == 0x03E01000:
            r1 = (~arm_imm(x)) & 0xFFFFFFFF
        elif (x & 0x0FF0F000) == 0x03001000:
            r1 = imm16(x)
        elif x == 0xE1A01004:  # cpy r1,r4 (strcmp result == 0)
            r1 = 0
        t = call_target(a, x)
        if t is not None and t not in MODEL_GETTERS:
            return r1, t
        a += 4
    return r1, None


def analyse(h):
    # numeric parsers appear in the first few instructions
    for k in range(16):
        x = w(h + 4 * k)
        t = call_target(h + 4 * k, x)
        if t == STRTOD:
            return 'float', [], None
        if t in (STRTOUL, STRTOL):
            return 'int', [], None
        if t == STRCMP:
            break
    toks, setter = [], None
    a = h
    for _ in range(600):
        x = w(a)
        if call_target(a, x) == STRCMP:
            # token: movw/movt r1 pair in the few words before the call,
            # compared against argv[3] (ldr r0,[r5,#0xc])
            back = [a - 4 * k for k in range(1, 8)]
            if not {0xE595000C, 0xE591000C} & {w(b) for b in back}:
                break
            tok = next((s for s in (r1_string(b) for b in reversed(back)) if s), None)
            if tok is None:
                break
            for k in range(1, 4):
                y = w(a + 4 * k)
                if (y & 0x0F000000) == 0x0A000000 and (y >> 28) in (0, 1):
                    if y >> 28 == 0:  # beq -> this token's branch
                        v, s = value_at(branch_target(a + 4 * k, y))
                    else:  # bne -> error; fall-through handles this (last) token
                        v, s = value_at(a + 4 * (k + 1))
                    toks.append((tok, v))
                    setter = setter or s
                    break
            else:
                break
            if y >> 28 == 1:
                break
        a += 4
    return ('enum' if toks else '?'), toks, setter


def main():
    print('item\tkind\tvalues\tsetter\thandler')
    for item, t in item_chain():
        h = tail(t)
        kind, toks, setter = analyse(h)
        vals = ' '.join(f'{k}={v}' if v is not None else k for k, v in toks)
        print(f'{item}\t{kind}\t{vals}\t{setter and hex(setter) or ""}\t{h:#x}')


if __name__ == '__main__':
    main()
