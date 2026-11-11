#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""shp_tokenize.py — OQ-005 tokenisation-grammar search (analysis, not
assertion; exit 0 unless it crashes; report -> docs/re/shp-tokenize.md).

The fixed-grammar sweep (shp_probe.py, gate 3c) proved 5 grammars x 3 header
sizes die on exact-span. This probe searches the GRAMMAR ITSELF: for each
record we BFS exact-cover tokenisations under several rule families and
pixel-accounting models, and report FOUND (with the winning trace for
hand-verification) or a structured negative.

Hand facts that shaped the rules (measured 2026-10-05, listbox/cos_ship hex):
  * cos_ship: rec0 (3x3) and the thirteen 4x3 records share a STRUCTURALLY
    identical 13-byte body `01 02 04 X 00 08 X 00 01 02 04 X 00` — the only
    varying positions across the 4x3 group are the three X bytes
    ([3,6,11], palette-like colour indices co-varying per ship); every
    count-like byte (01/02/04/00/08) is CONSTANT across 3x3 AND 4x3. A
    stream-carried pixel count can therefore not exist for this grammar;
    pixel extents must come from the record header (or a model none of the
    rule families below express).
  * rec1+ prefix is 24 B on every record printed so far in cos_ship,
    bullet04 and listbox: +0 u16 w,u16 h (own box) | +4..+11 i32 fields
    (hotspot/flags, vary) | +16 u32 w0,u32 h0 (BASE-sprite dims in the
    samples inspected — NOT machine-verified corpus-wide; used here only as
    a sanity gate so a FOUND trace can never come from a mis-cut prefix).
  * Corpus-wide machine checks this session (all on correct prefixes):
    (a) h-segments-of-[u8 len + payload] exact tiling: 3 hits / 1530 records
        (shipicon/restree/cos_star; segments don't tile the sprite) = noise;
    (b) tokenisation-grammar BFS, 4 rule families, 25 smallest libraries x
        4 records: 100/100 NEGATIVE (docs/re/shp-tokenize.md).
  * listbox rec0 body repeats values 0x67/0x6c/0x6e with 0xf2 every ~6
    bytes: candidate segment/end-of-line marker.
  * dims: rec0 u32 w + u32 h; rec1+ u16 w + u16 h at +0 (163/163).

Rule families (tokens; c = pixel count byte, v = palette value):
  FLAT   [c,v] runs, c>=1, sum == w*h exactly (1 trailing pad byte allowed)
  EOLLN  [c,v] runs + 0x00 end-of-line; line sums == w; h lines exact cover
  F2LN   3-byte [c,v,e] per segment; e is a cursor byte: cursor model
         end-cursor = prev_end + gap + c with gap>=0, f2 terminates line;
         every line closed by f2; also accepts 2-byte [c,v] segments
  DOC1   Truevision DOC1 ops: 0x00 EOL, 0x01 skip8, 0x02 dup(c,v),
         0x03 literal(c, c bytes), 0x40/0x80/0xC0 24-bit variants
Acceptance is ALWAYS exact byte-cover of the body + h lines closed.
"""
import glob, os, struct, sys
from collections import deque, Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_SOL = 4


def parse_lib(p):
    d = open(p, 'rb').read()
    n, ts, res = struct.unpack_from('<III', d, 4)
    slots = [struct.unpack_from('<Q', d, 16 + 8 * i)[0] for i in range(n + 1)]
    starts = sorted({16 + ts} | {slots[i] for i in range(n - 1)} | {len(d)})
    recs = [(starts[j], starts[j + 1] - starts[j]) for j in range(len(starts) - 1)]
    return d, n, recs


def dims_and_body(rb, is_rec0):
    if is_rec0 and len(rb) >= 8:
        w, h = struct.unpack_from('<II', rb, 0)
        if 1 <= w <= 512 and 1 <= h <= 512:
            return w, h, rb[8:]
    # rec1+ prefix is 24 B (cos_ship/bullet04/listbox anatomy, 2026-10-05):
    # +0 u16 w,u16 h | +4..+11 varies (offsets/half-size/flags) | +16 u32 w0,
    # u32 h0 = BASE-sprite dims | body from +24. Require +16 dims sane too so
    # we never decode a body from a wrong prefix.
    if len(rb) >= 24:
        w, h = struct.unpack_from('<HH', rb, 0)
        w0, h0 = struct.unpack_from('<II', rb, 16)
        if 1 <= w <= 512 and 1 <= h <= 512 and 1 <= w0 <= 512 and 1 <= h0 <= 512:
            return w, h, rb[24:]
    return 0, 0, rb[len(rb):]


def run_flat(body, w, h):
    """FLAT: [c,v]* (+optional trailing pad byte). sum c == w*h."""
    sols = []
    total = w * h
    for pad in (0, 1):
        b = body[:len(body) - pad] if pad else body
        if len(b) % 2:
            continue
        cs = [b[i] for i in range(0, len(b), 2)]
        if all(c >= 1 for c in cs) and sum(cs) == total:
            sols.append([('flat', i, b[i:i + 2]) for i in range(0, len(b), 2)])
    return sols


def run_eol_lines(body, w, h):
    """EOLLN: runs [c,v] closed by 0x00 per line; col==w at EOL required."""
    sols = []
    # BFS (line, col, pos)
    q = deque([(0, 0, 0, [])])
    seen = set()
    while q and len(sols) < MAX_SOL:
        line, col, pos, path = q.popleft()
        if (line, col, pos) in seen:
            continue
        seen.add((line, col, pos))
        if pos == len(body):
            if line == h and col == 0:
                sols.append(path)
            continue
        c = body[pos]
        if c >= 1 and pos + 1 < len(body) and col + c <= w:
            ncol = col + c
            q.append((line + 1 if ncol == w else line, 0 if ncol == w else ncol,
                      pos + 2, path + [('run', pos, body[pos:pos + 2])]))
        if c == 0x00 and col == w:
            q.append((line + 1, 0, pos + 1, path + [('eol', pos, b'\x00')]))
    return sols


def run_f2_lines(body, w, h):
    """F2LN: per line, a sequence of 3-byte [c,v,e] (e = end cursor, must be
    > prev cursor, c pixels ending AT e: start = e-c >= prev) and optional
    2-byte [c,v] segments continuing from prev cursor; line terminated by f2
    at col<=w with trailing pixels allowed (gap = transparency)."""
    sols = []
    q = deque([(0, 0, 0, [])])   # pos, line, cursor, path
    seen = set()
    while q and len(sols) < MAX_SOL:
        pos, line, cur, path = q.popleft()
        if (pos, line, cur) in seen:
            continue
        seen.add((pos, line, cur))
        if pos == len(body):
            if line == h and cur == 0:
                sols.append(path)
            continue
        if line >= h:
            continue
        b = body
        if b[pos] == 0xF2:
            if cur > 0:  # line drew something; close it
                q.append((pos + 1, line + 1, 0, path + [('f2', pos, b[pos:pos + 1])]))
            continue
        # 3-byte segment [c, v, e]: e-c >= prev cursor, e <= w
        if pos + 3 <= len(b):
            c, v, e = b[pos], b[pos + 1], b[pos + 2]
            if 1 <= c and e <= w and e - c >= cur:
                q.append((pos + 3, line, e,
                          path + [('seg3', pos, b[pos:pos + 3])]))
        # 2-byte run [c, v] continuing from cursor; capped at w
        if pos + 2 <= len(b):
            c, v = b[pos], b[pos + 1]
            if 1 <= c and cur + c <= w:
                q.append((pos + 2, line, cur + c,
                          path + [('run2', pos, b[pos:pos + 2])]))
    return sols


def run_doc1(body, w, h):
    """DOC1 ops; EOL op required to close lines (early EOL = transparent pad,
    recorded); exact cover."""
    sols = []
    q = deque([(0, 0, 0, 0, [])])   # pos, line, col, earlypad, path
    seen = set()
    b = body
    while q and len(sols) < MAX_SOL:
        pos, line, col, pad, path = q.popleft()
        if (pos, line, col) in seen:
            continue
        seen.add((pos, line, col))
        if pos == len(b):
            if line == h and col == 0:
                sols.append(path)
            continue
        if line >= h:
            continue
        op = b[pos]
        def push(npos, ncol, tag, nbytes=1, npad=pad):
            nline, nc = (line + 1, 0) if ncol == w else (line, ncol)
            q.append((npos, nline, nc, npad, path + [(tag, pos, b[pos:npos])]))
        if op == 0x00 and col == w:
            push(pos + 1, 0, 'eol', npad=pad)
        elif op == 0x00 and col < w:            # early EOL -> transparent rest
            push(pos + 1, w, 'eol-early', npad=pad + (w - col))
        elif op == 0x01 and pos + 1 < len(b):   # skip
            n = b[pos + 1]
            if col + n <= w:
                push(pos + 2, col + n, 'skip')
        elif op == 0x02 and pos + 2 < len(b):   # dup
            n = b[pos + 1]
            if n >= 1 and col + n <= w:
                push(pos + 3, col + n, 'dup')
        elif op == 0x03 and pos + 1 < len(b):   # literal n bytes
            n = b[pos + 1]
            if n >= 1 and col + n <= w and pos + 2 + n <= len(b):
                push(pos + 2 + n, col + n, 'lit')
        elif 0x40 <= op <= 0x7F and pos + 3 < len(b):     # dup big
            n = (op & 0x3F) << 16 | b[pos + 1] | b[pos + 2] << 8
            if 1 <= n <= 0x3F0000 and col + n <= w:
                push(pos + 4, col + n, 'dup-big')
        elif 0x80 <= op <= 0xBF and pos + 3 < len(b):     # skip big
            n = (op & 0x3F) << 16 | b[pos + 1] | b[pos + 2] << 8
            if col + n <= w:
                push(pos + 3, col + n, 'skip-big')
        elif 0xC0 <= op <= 0xFF and pos + 1 < len(b):     # literal big
            n = (op & 0x3F) << 16 | b[pos + 1]
            if col + n <= w and pos + 2 + n <= len(b):
                push(pos + 2 + n, col + n, 'lit-big')
    return sols


RULES = [('FLAT', run_flat), ('EOLLN', run_eol_lines), ('F2LN', run_f2_lines),
         ('DOC1', run_doc1)]


def main():
    libs = sorted(glob.glob(os.path.join(ROOT, 'extracted/*/data/*.shp')),
                  key=os.path.getsize)
    P_lines = []
    P = P_lines.append
    P('# .shp tokenisation-grammar search (OQ-005 structural probe)')
    P('')
    P('Generated by scripts/shp_tokenize.py; rule families and hand facts in')
    P('the script docstring. Acceptance = exact byte-cover + h lines closed;')
    P('a FOUND trace is published for hand verification, never auto-trusted.')
    P('')
    tally = Counter()
    traces = []
    for p in libs[:25]:
        d, n, recs = parse_lib(p)
        base = os.path.basename(p)
        rows = []
        for ri, (s, span) in enumerate(recs[:4]):
            rb = d[s:s + span]
            w, h, body = dims_and_body(rb, ri == 0)
            if w == 0:
                rows.append(f'- rec{ri}@{s}: dims unreadable (opaque header variant)')
                tally['dims_opaque'] += 1
                continue
            hits = []
            for name, fn in RULES:
                try:
                    sols = fn(body, w, h)
                except Exception:
                    sols = []
                if sols:
                    hits.append(name)
            if hits:
                nm = '+'.join(hits)
                rows.append(f'- rec{ri}@{s} {w}x{h} body={len(body)}: FOUND {nm}')
                tally[nm] += 1
                if len(traces) < 8:
                    name, fn = next(r for r in RULES if r[0] == hits[0])
                    traces.append((base, ri, w, h, hits[0], fn(body, w, h)[0]))
            else:
                rows.append(f'- rec{ri}@{s} {w}x{h} body={len(body)}: negative (all rule families)')
                tally['none'] += 1
        P(f'## {base} (n={n})')
        P('')
        P_lines.extend(rows)
        P('')
    P('## Tally')
    P('')
    for k, v in sorted(tally.items()):
        P(f'- {k}: {v}')
    if traces:
        P('')
        P('## Winning traces')
        P('')
        for base, ri, w, h, rule, path in traces:
            P(f'### {base} rec{ri} {w}x{h} via {rule}')
            P('')
            for kind, pos, tb in path[:30]:
                P(f'- +{pos:<4} {kind:<7} {tb.hex()}')
    out = os.path.join(ROOT, 'docs', 're', 'shp-tokenize.md')
    open(out, 'w').write('\n'.join(P_lines) + '\n')
    print('[shp_tokenize]', dict(sorted(tally.items())))
    print('  report ->', out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
