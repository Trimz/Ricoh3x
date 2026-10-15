"""Find ARM movw/movt pairs (or literal words) that build a 32-bit constant."""
import struct, sys
r = open(sys.argv[1], 'rb').read(); B = 0x53000000
n = len(r) // 4; W = struct.unpack('<%dI' % n, r[:n * 4])
for c in [int(x, 0) for x in sys.argv[2:]]:
    lo, hi = c & 0xFFFF, c >> 16
    hits = []
    for i, w in enumerate(W):
        if (w & 0x0FF00000) == 0x03000000 and (((w >> 4) & 0xF000) | (w & 0xFFF)) == lo:
            rd = (w >> 12) & 0xF
            for j in range(i + 1, min(n, i + 10)):
                v = W[j]
                if (v & 0x0FF00000) == 0x03400000 and (v >> 12) & 0xF == rd and (((v >> 4) & 0xF000) | (v & 0xFFF)) == hi:
                    hits.append(('movw/t', hex(B + i * 4))); break
        if w == c: hits.append(('lit', hex(B + i * 4)))
    print(hex(c), hits[:20])
