#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t368 sitting check v3: read the LIVE RING turn directly (watcher dead =>
timeline tail is stale and cannot answer the sitting test).

Read-only: opens each ring .sav, unzips "Memory", finds the base with the
cached anchor law, reads the turn scalar (r1_slot OFF+0x12e10). Bounded output.
"""
import os, sys, zipfile, traceback
# t373: moved work/r1/ -> scripts/ (tracked-file landmine defuse,
# docs/re/packaging.md S3); path math now assumes scripts/ depth.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r1_slot as S

ROOT = os.path.abspath(os.path.join(HERE, '..'))
D = os.path.join(ROOT, 'work', 'r1', 'playcap', 'save')

pay = S.load_payload(ROOT)
anch = S.anchors_cached(ROOT, pay)

rows = []
for name in sorted(os.listdir(D)):
    if not name.endswith('.sav'):
        continue
    p = os.path.join(D, name)
    try:
        mem = zipfile.ZipFile(p).read("Memory")
    except Exception as e:
        rows.append((name, None, f"unzip:{repr(e)[:60]}"))
        continue
    try:
        B = S.base_of(mem, anch)
    except Exception as e:
        rows.append((name, None, f"base:{repr(e)[:60]}"))
        continue
    if B is None:
        rows.append((name, None, "base=UNRESOLVED"))
        continue
    d = S.read_slot(p, mem, B)
    rows.append((name, d["turn"], None))

mt = [t for _, t, _ in rows if t is not None]
for name, t, err in rows:
    print(f"{name}\tturn={t}" + (f"\tERR {err}" if err else ""))
print(f"\nparsed={len(mt)}/{len(rows)} max_turn={max(mt) if mt else 'NONE'} "
      f"min_turn={min(mt) if mt else 'NONE'}")
