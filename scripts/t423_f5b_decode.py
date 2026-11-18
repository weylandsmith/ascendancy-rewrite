#!/usr/bin/env python3
"""t423 F5b: correct-offset record census + k12 decode test.

Banked layout (scripts/t414_3cfgnew_dump.py): k0 hdr at 0x10+tsz, pixels
immediately after the 0x10-byte header; k>0 start at table[i-1], header at
rec+0x10 (w,h u32), pixel stream at rec+0x18.
Tests: (1) dims per record; (2) does each record's run-stream terminate
 cleanly (0-per-row) BEFORE its successor's start -> intact; (3) same test
 for cos_star.shp k0..k51.
"""
import struct, os

D = '/home/hrethric/projects/ascendancy/extracted/ascend01/data'


def records(data):
    count, tsz = struct.unpack_from('<II', data, 4)
    starts = [0x10 + tsz] + [struct.unpack_from('<Q', data, 0x10 + 8 * i)[0]
                             for i in range(count - 1)]
    return count, tsz, starts


def walk(data, stream, W, H, limit):
    """Run-decode; return (rows_done, end_pos, status)."""
    pos = 0
    for row in range(H):
        px = 0
        while True:
            if stream + pos >= limit:
                return row, stream + pos, 'OOB-BOUND'
            if stream + pos >= len(data):
                return row, stream + pos, 'EOF'
            c = data[stream + pos]; pos += 1
            if c == 0:
                break
            if c == 1:
                if stream + pos >= len(data):
                    return row, stream + pos, 'EOF'
                L = data[stream + pos]; pos += 1; px += L; continue
            if c & 1:
                n = c >> 1
                pos += n
                px += n
            else:
                v = data[stream + pos]; pos += 1
                px += (c >> 1)
            if px > W + 400:
                return row, stream + pos, 'ROW-OVERRUN'
    return H, stream + pos, 'OK'


def census(name, maxrec=None):
    data = open(os.path.join(D, name), 'rb').read()
    count, tsz, starts = records(data)
    print(f'--- {name}: size={len(data)} count={count} tsz={tsz} ---')
    n = count if maxrec is None else min(maxrec, count)
    for i in range(n):
        rec = starts[i]
        if rec + 0x18 > len(data):
            print(f'  k{i:<3} rec={rec:#07x} HEADER-OOB')
            continue
        off = rec if i == 0 else rec + 0x10
        w, h = struct.unpack_from('<II', data, off)
        stream = (rec + 0x10) if i == 0 else (rec + 0x18)
        nxt = starts[i + 1] if i + 1 < count else len(data)
        if w == 0 or h == 0 or w > 1024 or h > 1024:
            print(f'  k{i:<3} rec={rec:#07x} dims w={w} h={h} (implausible)')
            continue
        rows, end, st = walk(data, stream, w, h, nxt)
        slack = nxt - end
        print(f'  k{i:<3} rec={rec:#07x} w={w} h={h} decode={st} '
              f'rows={rows}/{h} end={end:#07x} next={nxt:#07x} slack={slack}')


census('3cfgnew.shp')
census('cos_star.shp')
