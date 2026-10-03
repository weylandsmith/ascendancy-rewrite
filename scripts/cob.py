#!/usr/bin/env python3
"""Ascendancy .cob resource-archive reader (format reverse-engineered from the
game shipped in ./game).

Structure discovered by this project (see docs/COB-FORMAT.md):
  u32                file count
  N x name           NUL-terminated ASCII, zero-padded so each name record is
                     aligned to 4 bytes (name + NULs, min 1 NUL)
  (N+1?) x u32       little-endian offset table following the names
  blob bytes...

The offset table is verified-monotonic for ascend00.  For the other archives
the entries may be compressed; `unpack` dumps raw slices and `probe` prints
per-entry entropy/magic so the codec can be identified.
"""
import struct, sys, os, math, collections

def read_dir(p):
    b = open(p, 'rb').read()
    n = struct.unpack_from('<I', b, 0)[0]
    off, names = 4, []
    for _ in range(n):
        j = b.find(b'\x00', off)
        names.append(b[off:j].decode('latin1'))
        off = j + 1
        while off < len(b) and b[off] == 0:
            off += 1
    return b, n, names, off

def offsets(b, n, dir_end, filesize):
    """Heuristic: table is u32 LE; try N then N+1 entries; accept a table whose
    values are strictly increasing, all < filesize, and whose span best matches
    the data area (dir_end .. filesize)."""
    best = None
    for cnt in (n, n + 1):
        vals = list(struct.unpack_from(f'<{cnt}I', b, dir_end))
        if not all(vals[i] < vals[i + 1] for i in range(len(vals) - 1)):
            continue
        lo = vals[0] if cnt == n else vals[0]
        # score: how well [dir_end+4*cnt, filesize] aligns with first data offset
        gap = abs(vals[0] - (dir_end + 4 * cnt))
        if best is None or gap < best[0]:
            best = (gap, vals)
    return best[1] if best else None

def entropy(d):
    if not d: return 0.0
    c = collections.Counter(d); n = len(d)
    return -sum((v/n)*math.log2(v/n) for v in c.values())

def cmd_list(p):
    b, n, names, de = read_dir(p)
    o = offsets(b, n, de, len(b))
    print(f'{p}: {n} entries, dir_end={de}, size={len(b)}, table={"ok" if o else "NOT FOUND"}')
    for i, nm in enumerate(names[:20]):
        size = (o[i+1]-o[i]) if o and i+1 < len(o) else -1
        print(f'  [{i:3}] {nm:32} {size}')
    if len(names) > 20: print(f'  ... {len(names)-20} more')

def cmd_probe(p):
    b, n, names, de = read_dir(p)
    o = offsets(b, n, de, len(b))
    if not o:
        print('no clean monotonic offset table; dumping dir_end region')
        print(b[de:de+64].hex(' ')); return
    for i, nm in enumerate(names):
        if i+1 >= len(o): break
        d = b[o[i]:o[i+1]]
        e = entropy(d)
        head = d[:4].hex()
        printable = sum(1 for x in d[:200] if 9 <= x <= 126) / max(1, min(200, len(d)))
        flag = 'TEXT' if printable > 0.95 else ('HIGH-ENTROPY' if e > 7.7 else 'data')
        print(f'[{i:3}] {nm:32} len={len(d):9} ent={e:5.2f} magic={head:8} {flag}')

def cmd_extract(p, outdir, only=None):
    b, n, names, de = read_dir(p)
    o = offsets(b, n, de, len(b))
    if not o:
        sys.exit('cannot extract: offset table unresolved')
    os.makedirs(outdir, exist_ok=True)
    k = 0
    for i, nm in enumerate(names):
        if i+1 >= len(o): break
        if only and only.lower() not in nm.lower(): continue
        d = b[o[i]:o[i+1]]
        dst = os.path.join(outdir, nm.replace('\\', '/'))
        os.makedirs(os.path.dirname(dst) or outdir, exist_ok=True)
        open(dst, 'wb').write(d); k += 1
    print(f'extracted {k} files to {outdir}')

if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit('usage: cob.py list|probe|extract <file.cob> [outdir] [namefilter]')
    cmd, p = sys.argv[1], sys.argv[2]
    if cmd == 'list': cmd_list(p)
    elif cmd == 'probe': cmd_probe(p)
    elif cmd == 'extract': cmd_extract(p, sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
    else: sys.exit('unknown command')
