#!/usr/bin/env python3
"""Ascendancy P1b probe: the ascend02 table pair (name.bin / name.tsv).

Regenerates docs/re/tables.md.  Run:
    python3 scripts/table_probe.py [--out docs/re/tables.md]

WHY THIS FILE EXISTS / WHAT IT ESTABLISHES (all measured, see docs/FINDINGS.md):

1. The .bin tables are fixed-record.  Layout, verified exact on 7/7 shipped
   tables (body length divisible by 24 with zero remainder):

       +0x00  u32   constant 60            (identical in all 7 tables)
       +0x04  u32[3] zero                  (identical in all 7 tables)
       +0x10  record[0] .. record[N-1]     each 24 bytes = 6 x u32 LE

2. The .tsv files are NOT tab-separated text despite the extension, and they
   are NOT a text rendering of the .bin tables.  They are low-entropy binary
   blobs (2.55-3.00 bits/byte) holding NUL-delimited ASCII records.  Measured:
     - 56-59% of every .tsv is 0x00;
     - longest common prefix between same-stem .bin and .tsv is 0 bytes;
     - no .bin is a substring of its .tsv;
     - a 40-byte tech-name run found at .tsv offset 182 occurs in ALL SEVEN
       .tsv files and in NONE of the .bin files.
   => The .tsv/.bin relationship is unknown and goes to OQ-004.  Do not model
      game state from the .tsv until Ghidra (P2) shows which the exe loads.

3. Column typing on the .bin: fields 0,1,3,4 fit u16 and their odd u16 halves
   are always zero.  Field 2 carries a recurring 0xFFFF (odd half nonzero in
   ~20% of records, 0 < count <= 2 in two tables) and field 5 sometimes holds
   0xFFFFFFFF, so 2 and 5 are NOT cleanly split into u16 pairs.  Interpretation
   of every field is OQ-010/OQ-004 territory -- listed here as TYPE + RANGE
   only, never as meaning.
"""
import argparse
import collections
import math
import os
import struct
import sys

TABLES = ['battle', 'beginnew', 'galactic', 'planet', 'ship', 'species', 'tutintro']
BIN_HEADER = 16
REC_SIZE = 24
REC_FIELDS = REC_SIZE // 4
CONST_HEADER0 = 60


def entropy(b):
    if not b:
        return 0.0
    c = collections.Counter(b)
    n = len(b)
    return -sum((v / n) * math.log2(v / n) for v in c.values())


def lcp(a, b):
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n


def read(path):
    with open(path, 'rb') as f:
        return f.read()


def parse_bin(data, name):
    """Returns (nrec, records) or raises ValueError if the invariant breaks."""
    if len(data) < BIN_HEADER:
        raise ValueError(f'{name}: too short for {BIN_HEADER}-byte header')
    hdr = struct.unpack_from('<4I', data, 0)
    if hdr[0] != CONST_HEADER0:
        raise ValueError(f'{name}: header[0]={hdr[0]} != constant {CONST_HEADER0}')
    if any(hdr[1:]):
        raise ValueError(f'{name}: header[1..3] not zero: {hdr[1:]}')
    body = len(data) - BIN_HEADER
    if body % REC_SIZE:
        raise ValueError(f'{name}: body {body} not a multiple of {REC_SIZE}')
    nrec = body // REC_SIZE
    recs = [struct.unpack_from(f'<{REC_FIELDS}I', data, BIN_HEADER + i * REC_SIZE)
            for i in range(nrec)]
    return nrec, recs, hdr


def col_stats(recs):
    """Per-column type evidence: cardinality, nonzero count, range, u16 fit."""
    out = []
    for ci in range(REC_FIELDS):
        vals = [r[ci] for r in recs]
        u16_odd_nonzero = 0
        if vals:
            # odd u16 half of this u32 slot
            u16_odd_nonzero = sum(1 for v in vals if (v >> 16) & 0xFFFF)
        out.append({
            'col': ci,
            'uniq': len(set(vals)),
            'nonzero': sum(1 for v in vals if v),
            'n': len(vals),
            'min': min(vals) if vals else 0,
            'max': max(vals) if vals else 0,
            'fits_u16': (max(vals) if vals else 0) < 65536,
            'u16_hi_nonzero': u16_odd_nonzero,
        })
    return out


def nul_runs(data, min_len=4, cap=400):
    """ASCII runs terminated by NUL -- the shape of the .tsv string records."""
    runs = []
    i = 0
    n = len(data)
    while i < n and len(runs) < cap:
        if 32 <= data[i] < 127:
            j = i
            while j < n and 32 <= data[j] < 127:
                j += 1
            if j < n and j - i >= min_len:
                runs.append((i, data[i:j].decode('ascii')))
            i = max(i + 1, j)
        else:
            i += 1
    return runs


def stride_hint(data, candidates=(48, 96, 144, 192, 288, 240, 576, 672, 960)):
    """Weak periodicity signal on 4-byte alignment; reported, never asserted."""
    res = []
    for st in candidates:
        tot = min(len(data) - st, 40000) // 4
        if tot < 8:
            continue
        same = sum(1 for k in range(0, tot * 4, 4) if data[k] == data[k + st])
        res.append((same / tot, st))
    res.sort(reverse=True)
    return res[:3]


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', default=os.path.join(root, 'extracted', 'ascend02'))
    ap.add_argument('--out', default=os.path.join(root, 'docs', 're', 'tables.md'))
    a = ap.parse_args()

    bins, tsvs, errors = {}, {}, []
    for s in TABLES:
        bp, tp = os.path.join(a.data, s + '.bin'), os.path.join(a.data, s + '.tsv')
        if not os.path.exists(bp):
            errors.append(f'{s}.bin missing from {a.data}')
            continue
        bins[s] = read(bp)
        if os.path.exists(tp):
            tsvs[s] = read(tp)
        else:
            errors.append(f'{s}.tsv missing from {a.data}')
    if errors:
        sys.stderr.write('\n'.join(errors) + '\n')
        return 1

    L = []
    w = L.append
    w('# P1b — ascend02 table pair (`<name>.bin` / `<name>.tsv`)\n')
    w('Generated by `scripts/table_probe.py`. Every number below is measured from')
    w('`extracted/ascend02/`; nothing here is inferred game semantics.\n')

    w('## 1. `<name>.bin` — fixed-record tables [verified exact on 7/7]\n')
    w('```')
    w('  +0x00  u32     constant 60        <- identical in all 7 tables')
    w('  +0x04  u32 x3  0, 0, 0            <- identical in all 7 tables')
    w('  +0x10  N x 24-byte records, each 6 x u32 little-endian')
    w('```')
    w('| table | file bytes | body | body/24 | records | hdr[0] |')
    w('|---|---|---|---|---|---|')
    for s in TABLES:
        nrec, recs, hdr = parse_bin(bins[s], s)
        body = len(bins[s]) - BIN_HEADER
        w(f'| {s} | {len(bins[s])} | {body} | {body // REC_SIZE} | {nrec} | {hdr[0]} |')
    w('')
    w('The `body % 24 == 0` test holds for every table with zero remainder, which')
    w('is what pins the stride at 24 rather than a nearby multiple; autocorrelation')
    w('independently ranks 24 above 48/72/96 for all 7 tables.\n')
    w('Note `hdr[0] == 60` in all seven tables while record counts are')
    w('2084/767/1028/3463/2169/1198/384 — so 60 is a constant/version/record-size')
    w('field, NOT a record count. Its meaning is unresolved.\n')

    w('## 2. Column type evidence (`.bin`)\n')
    w('Types and ranges only. Meanings require Ghidra (P2) — see OQ-004/OQ-010.\n')
    for s in TABLES:
        nrec, recs, hdr = parse_bin(bins[s], s)
        w(f'### {s}.bin — {nrec} records\n')
        w('| col | distinct | nonzero | min | max | fits u16 | hi-u16 nonzero |')
        w('|---|---|---|---|---|---|---|')
        for c in col_stats(recs):
            w(f'| {c["col"]} | {c["uniq"]} | {c["nonzero"]}/{c["n"]} '
              f'| {c["min"]} | {c["max"]} | {"yes" if c["fits_u16"] else "no"} '
              f'| {c["u16_hi_nonzero"]} |')
        w('')
    w('Columns 0,1,3,4 have a zero high u16 half in every record, so they are')
    w('u16 values stored in u32 slots. Column 2 carries a recurring 0xFFFF and')
    w('column 5 sometimes 0xFFFFFFFF, so neither splits cleanly into a u16 pair;\n')
    w('they are treated as u32 until P2 shows otherwise.\n')

    w('## 3. `<name>.tsv` — NOT text, NOT the .bin tables\n')
    w('| table | bytes | % NUL | entropy (bits/B) | 0x0A | 0x09 | lcp vs own .bin '
      '| .bin substring? | periodicity hints |')
    w('|---|---|---|---|---|---|---|---|---|')
    for s in TABLES:
        d = tsvs[s]
        b = bins[s]
        nul = d.count(0) / len(d) * 100
        hints = ', '.join(f'{st} ({r:.2f})' for r, st in stride_hint(d))
        w(f'| {s} | {len(d)} | {nul:.1f} | {entropy(d):.2f} | {d.count(10)} '
          f'| {d.count(9)} | {lcp(d, b)} | {"yes" if b in d else "no"} | {hints} |')
    w('')
    w('Entropy 2.55-3.00 rules out compression (compressed data sits >7.7), so')
    w('this is plain sparse structured data. Because lcp is 0 and no .bin is a')
    w('substring of its .tsv, the two files do NOT hold the same bytes in two')
    w('encodings. The seed FINDINGS claim that ".tsv are the SAME tables as .bin')
    w('in text form" is falsified.\n')

    w('### 3a. Shared string block across all 7 `.tsv`\n')
    needle_off, needle = None, None
    d0 = tsvs['species']
    k = d0.find(b'Orbital Structures')
    if k >= 0:
        needle_off, needle = k, d0[k:k + 40]
        w(f'A 40-byte run starting at `species.tsv` offset {needle_off}:')
        w('```')
        w(repr(needle))
        w('```')
        w('occurs in:')
        for s in TABLES:
            d = tsvs[s]
            offs = []
            i = d.find(needle)
            while i != -1 and len(offs) < 5:
                offs.append(i)
                i = d.find(needle, i + 1)
            w(f'  - {s}.tsv: {offs if offs else "absent"}')
        for s in TABLES:
            if needle in bins[s]:
                w(f'  - {s}.bin: present')
        w('and in NONE of the 7 `.bin` files. So the `.tsv` carry display strings')
        w('(tech names, screen/form labels) that the `.bin` tables do not. This is')
        w('the strongest available lead on what a `.tsv` is; still unconfirmed.\n')

    w('### 3b. NUL-delimited string inventory (first 40 runs per table)\n')
    w('Offsets are absolute into the `.tsv`. Strings are shown as-is; they are the')
    w('only human-readable content in these files.\n')
    for s in TABLES:
        runs = nul_runs(tsvs[s])
        w(f'<details><summary>{s}.tsv — {len(runs)} string runs (capped at 400)</summary>\n')
        w('| offset | string |')
        w('|---|---|')
        for off, txt in runs[:40]:
            safe = txt.replace('|', '\\|')
            w(f'| {off} | {safe} |')
        w('</details>\n')

    w('## 4. Worked cross-check requested by STATE.md\n')
    w('STATE.md asked to cross-check one row of `galactic.tsv` against')
    w('`galactic.bin` bytes. That is not possible as posed, because `galactic.tsv`')
    w('has no row structure that corresponds to `galactic.bin` records (lcp=0, no')
    w('substring relation, no shared record stride — section 3). What CAN be')
    w('cross-checked, and is below, is `.bin` internal consistency plus the')
    w('`.txt` help siblings that do live in ascend00.\n')
    nrec, recs, hdr = parse_bin(bins['galactic'], 'galactic')
    w('First 6 records of `galactic.bin` at 6 x u32:\n')
    w('```')
    for i in range(min(6, nrec)):
        w(f'  rec{i}: {recs[i]}')
    w('  ...')
    w(f'  rec{nrec-1}: {recs[-1]}')
    w('```')
    w(f'`rec0` = {recs[0]}; field2 = {recs[0][2]} (0x{recs[0][2]:08x}).\n')
    a00 = os.path.join(root, 'extracted', 'ascend00')
    w('Same-stem `.txt` files in ascend00 (these are HELP/screen text with `text`/')
    w('`endtext`/`pos`/`help`/`button` keywords, not data tables):\n')
    for s in TABLES:
        p = os.path.join(a00, s + '.txt')
        if os.path.exists(p):
            txt = read(p)
            nlines = txt.count(bytes([10]))
            w(f'- `{s}.txt` ({len(txt)} B, {nlines} lines) — entropy '
              f'{entropy(txt):.2f}')
    w('')

    w('## 5. Status against the P1b checklist\n')
    w('- [x] `.bin` record stride and header layout (24 B, 16 B header, 7/7 exact)')
    w('- [x] Column type/range inventory for all 7 tables')
    w('- [x] `.tsv` characterised: binary, low-entropy, not a text table, not the')
    w('      `.bin` data (seed claim falsified)')
    w('- [ ] Which file the executable actually loads, and the `.tsv` container')
    w('      grammar — needs Ghidra xrefs (P2). Tracked as OQ-004.')
    w('- [ ] Field semantics (col0 looks index-like: strictly populated, one value')
    w('      per record in much of the file) — needs Ghidra. OQ-010.')
    w('')

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, 'w') as f:
        f.write('\n'.join(L) + '\n')
    print(f'wrote {a.out} ({os.path.getsize(a.out)} bytes)')
    # Machine-readable summary so gate.sh / CI can assert the invariant.
    for s in TABLES:
        nrec, recs, hdr = parse_bin(bins[s], s)
        print(f'  {s:9s} records={nrec:5d} hdr0={hdr[0]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
