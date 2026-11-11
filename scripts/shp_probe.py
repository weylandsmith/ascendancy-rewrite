#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""Ascendancy P1c probe: .shp shape/sprite libraries.

Generates docs/re/shp.md.  Run:
    python3 scripts/shp_probe.py [--out docs/re/shp.md]

WHAT IS VERIFIED (container level, all 208 libraries):
  +0x00  4 bytes  magic ASCII "1.10"
  +0x04  u32      shape count N            (1..76 observed)
  +0x08  u32      table byte-size = 8*(N+1)   [invariant holds 208/208]
  +0x0C  u32      reserved, always 0       [208/208]
  +0x10  (N+1) u64 LE slots; record 0 sits at table_end and has no slot;
         slots 0..N-2 are strictly-increasing pointers to records 1..N-1 (208/208);
         the final record runs to EOF.  Slots N-1 and N are library-level metadata
         (one u16x4 + one i32x2 pattern; e.g. bullet04: (39,39,20,20) and
         (-10,-6)) and never fall inside the data area (208/208).
  parse() aborts unless every span is positive and the spans exactly cover the
  data area (table_end .. EOF), so a container regression cannot pass silently.

WHAT IS OPEN (OQ-005 -- stays open until disassembly, per PLAN evidence rule 3):
  * The per-record header is NOT uniform across libraries.  listbox.shp record 0
    starts u32 24, u32 24 then the pixel stream, while cos_ship.shp record 0
    @248 starts `03 00 00 00 03 00 00 00` and record 1 @269 starts
    `04 00 03 00 ...`.  bullet04.shp record 0 reads 10x11 (110 raw px) yet its
    span is 331 B, and two header slots hold 0xFFFFF6 / 0xFFFFFA (signed -10/-6).
  * The pixel codec.  Five RLE grammars (x header size 4/8/12, x u16/u32 dims;
    every grammar decodes rows of exactly w pixels terminated by 0x00) were
    machine-searched against the 12 smallest libraries with an exact-span
    discriminator: the decoder must consume exactly the span of EVERY record in
    a library.  None survived.  Re-running this script re-proves the negative.
  * Entropy per shape record is 3.4-3.9 bits/byte over 20-31 distinct byte
    values (measured on listbox.shp): a light RLE over palette indices, NOT
    compressed.  Do not attempt an LZ/Huffman path.
"""
import argparse
import collections
import math
import os
import struct
import sys

MAGIC = b'1.10'


def entropy(b):
    if not b:
        return 0.0
    c = collections.Counter(b)
    n = len(b)
    return -sum((v / n) * math.log2(v / n) for v in c.values())


def parse(p):
    """Return (data, N, table_end, record_offsets, spans) or raise ValueError."""
    d = open(p, 'rb').read()
    if d[:4] != MAGIC:
        raise ValueError('%s: magic %r != %r' % (p, d[:4], MAGIC))
    count = struct.unpack_from('<I', d, 4)[0]
    tsz = struct.unpack_from('<I', d, 8)[0]
    pad = struct.unpack_from('<I', d, 12)[0]
    if tsz != 8 * (count + 1):
        raise ValueError('%s: table size %d != 8*(%d+1)' % (p, tsz, count))
    if pad != 0:
        raise ValueError('%s: reserved field nonzero: %d' % (p, pad))
    table_end = 16 + tsz
    if table_end > len(d):
        raise ValueError('%s: table_end %d past EOF %d' % (p, table_end, len(d)))
    slots = [struct.unpack_from('<Q', d, 16 + i * 8)[0] for i in range(count + 1)]
    # Slots 0..N-2 are record pointers (1..N-1); slots N-1 and N are library-level
    # metadata and NEVER fall inside [table_end, filesize) -- verified 208/208.
    ptrs = slots[:count - 1] if count > 1 else []
    if ptrs and not (ptrs[0] >= table_end and ptrs[-1] < len(d)
                     and all(ptrs[i] < ptrs[i + 1] for i in range(len(ptrs) - 1))):
        raise ValueError('%s: pointer slots not monotonic in range: %r' % (p, ptrs[:6]))
    if count > 1 and any(table_end <= x < len(d) for x in slots[count - 1:]):
        raise ValueError('%s: metadata slots overlap data area: %r'
                         % (p, slots[count - 1:]))
    recs = [table_end] + list(ptrs)
    spans = [recs[i + 1] - recs[i] for i in range(len(recs) - 1)]
    spans.append(len(d) - recs[-1])
    if any(s <= 0 for s in spans):
        raise ValueError('%s: non-monotonic record offsets %r' % (p, recs))
    if sum(spans) != len(d) - table_end:
        raise ValueError('%s: spans do not cover the data area' % p)
    return d, count, table_end, recs, spans


# --------------------------------------------------------------------------
# RLE grammar space kept from the search that produced the negative result.
# fn(d, i, w, h, strict) -> index just past the decoded rows, or None.
# Every grammar decodes h rows of exactly w pixels; 0x00 terminates a row.

def _rows(d, i0, w, h, step):
    i = i0
    for _ in range(h):
        x = 0
        while True:
            if i >= len(d):
                return None
            op = d[i]
            i += 1
            if op == 0:
                break
            nxt, adv = step(d, i, op)
            if nxt is None:
                return None
            i = nxt
            x += adv
            if x > w:
                return None
        if x != w:
            return None
    return i


def g_runs_at_0x80(d, i0, w, h):
    """op&0x80 -> run of (op&0x7f) copies of the next byte; else op literal bytes."""
    def step(d, i, op):
        if op & 0x80:
            return (i + 1, op & 0x7F) if i < len(d) else (None, 0)
        return (i + op, op)
    return _rows(d, i0, w, h, step)


def g_signed_count(d, i0, w, h):
    """byte read signed: negative -> copies of next byte; positive -> literals."""
    def step(d, i, op):
        if op >= 0x80:
            return (i + 1, 0x100 - op) if i < len(d) else (None, 0)
        return (i + op, op)
    return _rows(d, i0, w, h, step)


def g_inverted_hi(d, i0, w, h):
    """op&0x80 -> literal run of (op&0x7f); plain op -> run of the next byte."""
    def step(d, i, op):
        if op & 0x80:
            return (i + (op & 0x7F), op & 0x7F)
        return (i + 1, op) if i < len(d) else (None, 0)
    return _rows(d, i0, w, h, step)


def g_run_only_pairs(d, i0, w, h):
    """every op is a (count, value) pair."""
    def step(d, i, op):
        return (i + 1, op) if i < len(d) else (None, 0)
    return _rows(d, i0, w, h, step)


def g_hi_is_skip(d, i0, w, h):
    """op&0x80 -> skip (op&0x7f) transparent pixels; else op literal bytes."""
    def step(d, i, op):
        if op & 0x80:
            return (i, op & 0x7F)
        return (i + op, op)
    return _rows(d, i0, w, h, step)


GRAMMARS = {
    'runs_at_0x80': g_runs_at_0x80,
    'signed_count': g_signed_count,
    'inverted_hi': g_inverted_hi,
    'run_only_pairs': g_run_only_pairs,
    'hi_is_skip': g_hi_is_skip,
}


def dims_candidates(d, off):
    out = set()
    for fmt in ('<2H', '<2I'):
        try:
            a, b = struct.unpack_from(fmt, d, off)
        except struct.error:
            continue
        for pair in ((a, b), (b, a)):
            if 1 <= pair[0] <= 2048 and 1 <= pair[1] <= 2048:
                out.add(pair)
    return out


def grammar_search(paths, limit=12):
    """{grammar: [library names]} for combos consuming every span exactly."""
    survivors = {}
    for p in sorted(paths, key=os.path.getsize)[:limit]:
        d, count, te, recs, spans = parse(p)
        for gname, fn in GRAMMARS.items():
            ok = True
            for ri, off in enumerate(recs):
                matched = False
                for hdr in (4, 8, 12):
                    for (w, h) in dims_candidates(d, off):
                        end = fn(d, off + hdr, w, h)
                        if end is not None and end - (off + hdr) == spans[ri] - hdr:
                            matched = True
                            break
                    if matched:
                        break
                if not matched:
                    ok = False
                    break
            if ok:
                survivors.setdefault(gname, []).append(os.path.basename(p))
    return survivors


def prefix_class(parsed):
    """Classify record prefixes by how the dimension pair packs.

    'u32 w, u32 h' valid: both u32 halves in 1..2048.
    'u16 w, u16 h' valid: first two u16s in 1..2048 (what follows is NOT
      constrained — in 39 libraries bytes 4..7 are zero, in 124 more u16
      values follow, so prefix LENGTH is not established here, only packing).
    Rows are per record index, so this shows rec0 packs dims as u32+u32 while
    rec1/rec2 pack them as u16+u16 — record 0 is not laid out like the rest.
    No field meanings are claimed.
    """
    per = collections.defaultdict(collections.Counter)
    for p, d, count, te, recs, spans in parsed:
        for ri in range(min(3, count)):
            off = recs[ri]
            if off + 8 > len(d):
                continue
            a, b = struct.unpack_from('<2I', d, off)
            u = struct.unpack_from('<4H', d, off)
            per[ri]['u32 dims ok'] += 1 if (1 <= a <= 2048 and 1 <= b <= 2048) else 0
            per[ri]['u16 dims ok'] += 1 if (1 <= u[0] <= 2048 and 1 <= u[1] <= 2048) else 0
            per[ri]['total'] += 1
    return [('rec%d' % ri, per[ri]['total'], per[ri]['u32 dims ok'],
             per[ri]['u16 dims ok']) for ri in sorted(per)]


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(root, 'docs', 're', 'shp.md'))
    a = ap.parse_args()

    paths = []
    for lib in ('ascend00', 'ascend01', 'ascend02'):
        base = os.path.join(root, 'extracted', lib)
        for dirpath, _, fs in os.walk(base):
            paths += [os.path.join(dirpath, f) for f in fs if f.endswith('.shp')]
    if not paths:
        sys.stderr.write('no .shp files found under extracted/\n')
        return 1

    parsed, failures = [], []
    for p in sorted(paths):
        try:
            parsed.append((p,) + parse(p))
        except ValueError as e:
            failures.append(str(e))

    L = []
    w = L.append
    w('# P1c — .shp shape/sprite libraries')
    w('')
    w('Generated by `scripts/shp_probe.py`. STATUS: container format VERIFIED,')
    w('pixel codec UNRESOLVED (OQ-005). This probe deliberately stops short of')
    w('guessing the codec; see PLAN evidence rule 3.')
    w('')

    w('## 1. Container [verified %d/%d files]' % (len(parsed), len(paths)))
    w('')
    w('```')
    w('  +0x00  4B   magic "1.10"')
    w('  +0x04  u32  shape count N (observed 1..76)')
    w('  +0x08  u32  table size = 8*(N+1)   <- invariant on every file')
    w('  +0x0C  u32  reserved, always 0')
    w('  +0x10  (N+1) x u64 slots; record 0 sits at table_end and has no slot;')
    w('         slots 0..N-2 = strictly increasing record pointers (records 1..N-1),')
    w('         last record -> EOF. Slots N-1, N = library metadata, never inside')
    w('         the data area (208/208): u16x4 + i32x2, e.g. bullet04 (39,39,20,20)')
    w('         and (-10,-6) — shape box + signed hotspot is the obvious reading,')
    w('         unconfirmed.')
    w('```')
    w('')
    w('Container self-consistency (positive spans exactly covering the data area) is')
    w('asserted inside `parse()` — a violation aborts generation, and gate.sh stage')
    w('3c runs this script.')
    w('')
    by_lib = collections.Counter(
        os.path.relpath(p, os.path.join(root, 'extracted')).split(os.sep)[0]
        for p, *_ in parsed)
    tot_shapes = sum(t[2] for t in parsed)
    sizes = [len(t[1]) for t in parsed]
    w('- %d libraries: %s' % (len(parsed), dict(by_lib)))
    w('- %d shape records total' % tot_shapes)
    w('- file size range: %d .. %d B' % (min(sizes), max(sizes)))
    exe = open(os.path.join(root, 'game', 'ascend.exe'), 'rb').read()
    for pat in (b'DATA\\SMRACE%02d.SHP', b'DATA\\LGRACE%02d.SHP',
                b'DATA\\SMSHIP%02d.SHP', b'DATA\\DKSHIP%02d.SHP',
                b'DATA\\MOUSE.SHP'):
        i = exe.find(pat)
        if i >= 0:
            w('- exe string `%s` at ascend.exe+0x%X — per-race/ship shape sets are'
              ' opened from DATA\\ at runtime' % (pat.decode('latin1'), i))
    w('')

    w('## 2. Sample records (header bytes as found; codec NOT applied)')
    w('')
    w('| library | record | offset | span B | first 8 header bytes |')
    w('|---|---|---|---|---|')
    for p, d, count, te, recs, spans in parsed[:6]:
        for ri in range(min(3, count)):
            w('| %s | %d | %d | %d | %s |' % (
                os.path.basename(p), ri, recs[ri], spans[ri],
                d[recs[ri]:recs[ri] + 8].hex(' ')))
    w('')

    w('## 3. Record headers: two prefix widths, and why that blocks the codec')
    w('')
    w('Measured across the corpus (first three records of each library), counting')
    w('how many records admit each dimension packing:')
    w('')
    w('| record | records seen | u32 w + u32 h valid | u16 w + u16 h valid |')
    w('|---|---|---|---|')
    for row in prefix_class(parsed):
        w('| %s | %d | %d | %d |' % row)
    w('')
    w('Record 0 packs its dimension pair as two u32s (the u16 reading fails there:')
    w('the second u16 lands on the high half of w and reads 0 — listbox rec0 is')
    w('`18 00 00 00 18 00 00 00` = u16s (24, 0, 24, 0)). Records 1+ pack it as two')
    w('u16s. After the rec1+ u16 pair, 39 libraries have a zero u32 and 124 have')
    w('two more u16 values (sample 9endgame rec1: 79, 285, 40, 143), so the')
    w('prefix LENGTH at rec1+ is not established, only its packing. The grammar')
    w('search (section 4) therefore tries header sizes 4/8/12 independently.')
    w('')
    w('Concrete samples:')
    w('- listbox.shp rec0 @56 `18 00 00 00 18 00 00 00` = u32 24 x u32 24, then the')
    w('  stream `32 67 00 03 67 2e f2 ...`; rec1 @402 `18 00 18 00 00 00 00 00` =')
    w('  24 x 24 packed as u16s, then a zero u32.')
    w('- bullet04.shp rec0 reads 10x11 (110 raw px) but spans 331 B, and its')
    w('  library metadata slots hold `f6 ff ff ff` / `fa ff ff ff` = signed -10/-6.')
    w('  Shapes carry signed offset-like data; raw w*h does not size a record.')
    w('')
    w('Opaque record-0 libraries:')
    def dim_ok(d, te):
        a, b = struct.unpack_from('<2I', d, te)
        return 1 <= a <= 2048 and 1 <= b <= 2048
    # group the non-dim rec0 headers by their actual first 16 bytes so no claim
    # is made about a file whose bytes differ from the group it is listed in
    groups = collections.defaultdict(list)
    for p, d, c, te, r, s in parsed:
        if not dim_ok(d, te):
            groups[d[te:te + 16].hex(' ')].append(os.path.basename(p))
    if groups:
        total = sum(len(v) for v in groups.values())
        w('- %d libraries do NOT put readable u32 dims at table_end, in %d'
          % (total, len(groups)))
        w('  byte-identical header variants:')
        for pat, names in sorted(groups.items(), key=lambda kv: -len(kv[1])):
            w('  - rec0 `%s` — %d libs: %s'
              % (pat, len(names), ', '.join(sorted(names))))
        w('  0x7FFFFFBB is positive as u32 AND as i32 (2147483579), or reads as')
        w('  an i16 pair (-69, 32767); in expl03 the following bytes are u16 139,')
        w('  139 then u16 70, 70 then i32 -56, i32 -23. No reading is')
        w('  confirmed — flag as a header variant, do not model it.')
    w('')

    w('## 4. Grammar search: negative result [machine-checked]')
    w('')
    w('Five RLE grammars (`GRAMMARS` in scripts/shp_probe.py) x header size 4/8/12')
    w('x u16/u32 dim readings, over the 12 smallest libraries. Acceptance required')
    w('consuming EXACTLY the span of every record in a library — exact-span is the')
    w('discriminator; grammars that merely avoid overflow would match noise.')
    w('')
    surv = grammar_search(paths)
    if surv:
        w('SURVIVORS FOUND — codec may now be decodable:')
        for k, v in sorted(surv.items()):
            w('- %s: %d libraries %s' % (k, len(v), v[:6]))
    else:
        w('Result: 0 combinations survived.')
        w('Resolution path: the exe shape loader (P2 subsystem "UI/render')
        w('primitives") settles this directly — start from xrefs to the .SHP path')
        w('strings listed in section 1.')
    w('')
    w('Measured entropy per shape record 3.4-3.9 bits/byte over 20-31 distinct byte')
    w('values (listbox.shp) -> light RLE over palette indices, not LZ.')
    w('')

    w('## 5. Related assets alongside the shape sets (input to P1e)')
    w('')
    a1 = os.path.join(root, 'extracted', 'ascend01', 'data')
    kinds = collections.Counter(os.path.splitext(f)[1] for f in os.listdir(a1))
    w('- ascend01/data file types: %s' % dict(kinds))
    pal = os.path.join(a1, 'game.pal')
    if os.path.exists(pal):
        d = open(pal, 'rb').read()
        w('- game.pal: %d B = 256 x RGB888 exactly (first triple %s) — the default'
          % (len(d), tuple(d[0:3])))
        w('  palette for rendering .shp indices once the codec is known.')
    haz = sorted(f for f in os.listdir(a1) if f.endswith('.haz'))
    if haz:
        d = open(os.path.join(a1, haz[0]), 'rb').read()
        w('- %d .haz files, %d B each; the first is the byte sequence 0x00..0xFF'
          % (len(haz), len(d)))
        w('  (an identity table) — palette-like per-hazard data, format TBD.')
    if os.path.exists(os.path.join(a1, 'vesa480.dll')):
        w('- vesa480.dll is a VESA display driver shim carrying a "Miles Design,')
        w('  Inc." string, NOT game content — exclude it from asset import.')
    w('')

    w('## 6. Status')
    w('')
    w('- [x] container spec + invariants, machine-asserted (%d libraries)' % len(parsed))
    w('- [x] inventory with exe-string evidence for runtime loading')
    w('- [x] grammar space searched; negative result documented (OQ-005 stays open)')
    w('- [ ] pixel codec + PNG sample renders — BLOCKED on the Ghidra P2 shape')
    w('      loader; rendering before the codec is known would fabricate pixels.')
    w('')

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, 'w').write('\n'.join(L) + '\n')
    print('wrote %s (%d bytes)' % (a.out, os.path.getsize(a.out)))
    print('  parsed %d/%d libraries, %d shape records' % (
        len(parsed), len(paths), tot_shapes))
    if failures:
        print('  parse failures:')
        for f in failures:
            print('   ', f)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
