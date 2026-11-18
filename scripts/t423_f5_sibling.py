#!/usr/bin/env python3
"""t423 F5: census the 3cfgnew.shp / 3cfgnew.tmp sibling pair + cos_star.shp.

Questions:
 1. Does the .tmp file carry the tail the .shp is truncated at (i.e. is k12
    intact when the record stream is read across the concatenation)?
 2. Record table (count, tsz, per-record dims) for both files.
 3. cos_star.shp record count + per-record dims (star sprite size law).
Prints a table only (no image data into context).
"""
import struct, sys, os

D = '/home/hrethric/projects/ascendancy/extracted/ascend01/data'


def table(name):
    p = os.path.join(D, name)
    data = open(p, 'rb').read()
    count, tsz = struct.unpack_from('<II', data, 4)
    print(f'{name}: size={len(data)} count={count} tsz={tsz} '
          f'table_span=0x10..{0x10+8*count:#x}')
    starts = []
    for i in range(count):
        if i == 0:
            starts.append(0x10 + tsz)
        else:
            starts.append(struct.unpack_from('<Q', data, 0x10 + 8 * (i - 1))[0])
    rows = []
    for i, rec in enumerate(starts):
        if rec + 0x18 > len(data):
            rows.append((i, rec, 'HEADER-OOB', None, None))
            continue
        w, h = struct.unpack_from('<II', data, rec)
        # declared pixel stream end = next record start (or EOF for last)
        nxt = starts[i + 1] if i + 1 < len(starts) else len(data)
        rows.append((i, rec, 'hdr', w, h))
    for i, rec, kind, w, h in rows:
        print(f'  k{i:<3} rec={rec:#07x} {kind} w={w} h={h}')
    return data, count, starts


print('=== 3cfgnew.shp ===')
shp, nshp, sstart = table('3cfgnew.shp')
print('=== 3cfgnew.tmp ===')
tmp, ntmp, tstart = table('3cfgnew.tmp')

print('=== tail overlap test ===')
# Does the shp truncate mid-record? Compare last record of shp against tmp.
print(f'shp len={len(shp)} tmp len={len(tmp)} concat={len(shp)+len(tmp)}')
# check whether tmp's byte-0 region matches the shp's tail bytes (would mean dup)
print('shp tail 32:', shp[-32:].hex())
print('tmp head 32:', tmp[:32].hex())
# how many shp records does tmp have? identical table?
print('record-start compare:')
for i in range(min(nshp, ntmp)):
    sv = (0x10) if i == 0 else struct.unpack_from('<Q', shp, 0x10 + 8*(i-1))[0]
    tv = (0x10) if i == 0 else struct.unpack_from('<Q', tmp, 0x10 + 8*(i-1))[0]
    print(f'  k{i}: shp_start={sv:#x} tmp_start={tv:#x}')

print('=== cos_star.shp ===')
table('cos_star.shp')
