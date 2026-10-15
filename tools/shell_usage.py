"""Extract usage text for every internal shell command (GR IIIx fw 1.60).

Shell handlers print help through FUN_536bae98(argv0, description, args[], nargs).
For each command in data/shell_commands.tsv this scans its handler (up to the
next handler) for that call, takes the description from the movw/movt r1 just
before it, and collects argument placeholders (strings starting with '<' or '[')
loaded anywhere in the handler.

Usage: python3 -I tools/shell_usage.py out/rtos.bin data/shell_commands.tsv > data/shell_usage.tsv
"""
import struct
import sys

B = 0x53000000
USAGE = 0x536BAE98

d = open(sys.argv[1], 'rb').read()


def w(a):
    return struct.unpack_from('<I', d, a - B)[0]


def cstr(a):
    o = a - B
    if not 0 <= o < len(d):
        return None
    x = d[o:o + 160].split(b'\0')[0]
    if x and all(32 <= c < 127 or c in (9, 10) for c in x):
        return x.decode().replace('\t', ' ').replace('\n', ' ').strip()
    return None


def imm16(x):
    return ((x >> 4) & 0xF000) | (x & 0xFFF)


def bl_target(a, x):
    off = x & 0xFFFFFF
    if off & 0x800000:
        off -= 0x1000000
    return a + 8 + off * 4


def strings_loaded(lo, hi):
    """(address, register, string) for every movw/movt pair in [lo, hi)."""
    out, pending = [], {}
    a = lo
    while a < hi:
        x = w(a)
        rd = (x >> 12) & 15
        if (x & 0x0FF00000) == 0x03000000:
            pending[rd] = imm16(x)
        elif (x & 0x0FF00000) == 0x03400000 and rd in pending:
            s = cstr(imm16(x) << 16 | pending.pop(rd))
            if s:
                out.append((a, rd, s))
        a += 4
    return out


def main():
    rows = [l.rstrip('\n').split('\t') for l in open(sys.argv[2])][1:]
    cmds = sorted((int(h, 16), n) for n, h in rows)
    print('name\thandler\tdescription\targs')
    for i, (h, name) in enumerate(cmds):
        end = cmds[i + 1][0] if i + 1 < len(cmds) and cmds[i + 1][0] > h else h + 0x800
        end = min(end, h + 0x2000)
        loads = strings_loaded(h, end)
        desc = ''
        a = h
        while a < end:
            x = w(a)
            if (x & 0x0F000000) == 0x0B000000 and bl_target(a, x) == USAGE:
                before = [s for (p, r, s) in loads if p < a and r == 1]
                desc = before[-1] if before else ''
                break
            a += 4
        args = []
        for _, _, s in loads:
            if s[:1] in '<[' and s not in args:
                args.append(s)
        print(f'{name}\t{h:#x}\t{desc}\t{" ".join(args)}')


if __name__ == '__main__':
    main()
