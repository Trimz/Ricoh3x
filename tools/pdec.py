"""Decompressor for Ricoh/Pentax firmware LZ streams (fwdc243b.bin, GR IIIx).

Stream: sequence of blocks, each prefixed by a u16 BE length.
  0            -> end of stream
  n & 0x8000   -> stored block of (n & 0x7FFF) raw bytes
  otherwise    -> LZ block: u16 BE flag maps (MSB first, 1 = copy),
                  copy = 2 bytes: len = (b0 & 7) + 3 (10 => extended by following bytes until != 0xFF),
                  offset = ((b0 & 0xF8) << 5) | b1; block ends with a 0x0000 trailer.
"""
import sys


def dec_block(src, p, n, out):
    end = p + n - 2
    mask = 0
    cmap = 0
    while p < end:
        if mask == 0:
            cmap = (src[p] << 8) | src[p + 1]
            p += 2
            mask = 0x8000
            continue
        if cmap & mask:
            s0, s1 = src[p], src[p + 1]
            p += 2
            ln = (s0 & 7) + 3
            if ln == 10:
                while True:
                    b = src[p]
                    p += 1
                    ln += b
                    if b != 0xFF:
                        break
            off = ((s0 & 0xF8) << 5) | s1
            if off == 0 or off > len(out):
                raise ValueError('bad offset')
            st = len(out) - off
            for i in range(ln):
                out.append(out[st + i])
        else:
            out.append(src[p])
            p += 1
        mask >>= 1
    if src[p] or src[p + 1]:
        raise ValueError('missing trailer')


def chain(src, p):
    out = bytearray()
    nb = 0
    while True:
        n = (src[p] << 8) | src[p + 1]
        if n == 0:
            return out, p + 2, nb, True
        if n > 0x8000:
            ln = n & 0x7FFF
            out += src[p + 2:p + 2 + ln]
            p += 2 + ln
        else:
            dec_block(src, p + 2, n, out)
            p += 2 + n
        nb += 1


if __name__ == '__main__':
    d = open(sys.argv[1], 'rb').read()
    out, end, nb, ok = chain(d, 0x80)
    print('blocks', nb, 'end', hex(end), 'eof', ok, 'out', len(out))
    open(sys.argv[2], 'wb').write(out)
