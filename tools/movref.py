"""Find code that loads the address of a string via ARM movw/movt pairs or literal pools."""
import struct, re, sys
r = open(sys.argv[1], 'rb').read(); B = 0x53000000
n = len(r) // 4; W = struct.unpack('<%dI' % n, r[:n * 4])
movw, movt = {}, {}
for i, w in enumerate(W):
    imm = ((w >> 4) & 0xF000) | (w & 0xFFF); rd = (w >> 12) & 0xF
    if (w & 0x0FF00000) == 0x03000000: movw.setdefault((rd, imm), []).append(i)
    elif (w & 0x0FF00000) == 0x03400000: movt.setdefault(imm, []).append((i, rd))
def refs(addr):
    out = [('lit', B + i * 4) for i, w in enumerate(W) if w == addr]
    for (i, rd) in movt.get(addr >> 16, []):
        for j in movw.get((rd, addr & 0xFFFF), []):
            if abs(i - j) <= 8: out.append(('movw/t', B + min(i, j) * 4))
    return out
for s in sys.argv[2:]:
    for m in re.finditer(re.escape(s.encode()), r):
        a = B + m.start()
        print(f'{s!r} @{a:#x}:', [(k, hex(x)) for k, x in refs(a)][:8])
