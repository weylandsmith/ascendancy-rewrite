#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r335b_item_array.py — t335 DECISIVE CENSUS: what the win+0x6d stride-13 array IS.

Hypotheses (from _wip_t335.md S1-S3):
  H1 (t334's premise): the array holds STATE-line records -> PREDICTS records for
     all 104 windows with STATE count>0 and counter == STATE count.
  H2 (item array): the array holds TEXTITEM/SHAPEITEM records -> PREDICTS records
     only for windows having those keywords, counter == number of item lines,
     byte0 = 0 for TEXTITEM / 1 for SHAPEITEM, u32@+1 = interner pool offset
     (ds:0x6fda8 + u32) resolving to the item's literal NAME for tag 0.
Truth side = ON-DISK extracted/ascend00/windows.txt (t333's "text resident in
saves" did NOT reproduce: NUMCONTROLS in 0/284 save dirs).
Laws (not re-derived): window record magic u32 0x12345678 + ASCII NAME @+0x20;
save-member addr = B + 0x82bb0 + X (r1_slot.py); needle gate u32 turn @+0x12e10
in 1..4000 AND >=100 window records before ANY ds: read.
Exit 0 = measured.
"""
import os, sys, struct, zipfile, glob, re, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import r1_slot as RS

MAGIC = b"\x78\x56\x34\x12"
OFF = 0x82bb0
OFF_TURN = 0x12e10
POOL = 0x6fda8


def file_truth():
    wt = open(os.path.join(ROOT, "extracted", "ascend00",
                           "windows.txt"), "rb").read().decode("latin-1").replace("\r", "")
    names = list(re.finditer(r"(?m)^NAME\s+(\S+)", wt))
    blocks = {}
    for i, m in enumerate(names):
        seg = wt[m.end(): names[i + 1].start() if i + 1 < len(names) else len(wt)]
        s = re.search(r"(?m)^STATE\s+(\d+)((?:\s+\d+)*)", seg)
        items = re.findall(r"(?m)^(TEXTITEM|SHAPEITEM)\s+(\d+)\s+(\S+)\s+(\d+)\s+(\d+)\s+(\d+)", seg)
        blocks.setdefault(m.group(1), {
            "state": (int(s.group(1)), [int(x) for x in s.group(2).split()]) if s else None,
            "items": [(k, int(t), nm, [int(a), int(b), int(c)])
                      for k, t, nm, a, b, c in items],
        })
    return blocks


def main():
    dirs = []
    prod = os.path.join(ROOT, "work", "r1", "playcap", "save")
    if os.path.isdir(prod):
        dirs.append(prod)
    for pat in ("dbg-t332-*/save", "t299-leg-*/save", "dbg-t331-*/save"):
        for d in sorted(glob.glob(os.path.join(ROOT, "work", "r1", pat))):
            if d not in dirs:
                dirs.append(d)
    dirs = dirs[:20]
    blocks = file_truth()
    n_item_windows = sum(1 for b in blocks.values() if b["items"])

    ok = rej = 0
    a1_hist = collections.Counter()
    agree_state = collections.Counter()      # a1 == STATE count?
    agree_items = collections.Counter()      # a1 == #item lines?
    tag_kind = collections.Counter()         # (byte0, item kind) positional
    pool_match = collections.Counter()       # tag0 u32 -> pool str == item name
    pool_examples = []
    windows_with_recs = collections.Counter()
    tag1_records = collections.Counter()

    for d in dirs:
        for f in sorted(f for f in os.listdir(d) if f.endswith(".sav"))[:12]:
            try:
                mem = zipfile.ZipFile(os.path.join(d, f)).read("Memory")
            except Exception:
                continue
            B = RS.base_of(mem, RS.anchors_cached(ROOT, pay) if False else anch)
            if B is None or not (1 <= struct.unpack_from("<I", mem, B + OFF + OFF_TURN)[0] <= 4000):
                rej += 1
                continue
            recs_found = 0
            for mo in re.finditer(MAGIC, mem):
                b = mo.start()
                if b + 0xc0 > len(mem):
                    continue
                nm = mem[b + 0x20:b + 0x40].split(b"\x00")[0]
                if not (2 <= len(nm) <= 24 and all(32 <= c < 127 for c in nm)):
                    continue
                nm = nm.decode("ascii", "replace")
                a1 = struct.unpack_from("<H", mem, b + 0xa1)[0]
                a1_hist[a1] += 1
                tb = blocks.get(nm)
                if tb:
                    sc = tb["state"][0] if tb["state"] else 0
                    agree_state["eq" if a1 == sc else "neq"] += 1
                    agree_items["eq" if a1 == len(tb["items"]) else "neq"] += 1
                if a1:
                    recs_found += 1
                    windows_with_recs[nm] += 1
                    for i in range(a1):
                        r = mem[b + 0x6d + 13 * i: b + 0x6d + 13 * (i + 1)]
                        tag = r[0]
                        u32 = struct.unpack_from("<I", r, 1)[0]
                        kind = tb["items"][i][0] if tb and i < len(tb["items"]) else "?"
                        tag_kind[(tag, kind)] += 1
                        if tag == 0:
                            ps = mem[B + OFF + POOL + u32: B + OFF + POOL + u32 + 40].split(b"\x00")[0]
                            want = tb["items"][i][2] if tb and i < len(tb["items"]) else None
                            hit = (ps.decode("ascii", "replace") == want)
                            pool_match["hit" if hit else "miss"] += 1
                            if len(pool_examples) < 12 and (not hit or f == "41.sav"):
                                pool_examples.append((f, nm, i, hex(u32), ps.decode("ascii", "replace"), want))
                        else:
                            tag1_records[(hex(u32), struct.unpack_from("<I", r, 5)[0])] += 1
            ok += 1

    print(f"[1] saves ok={ok} rejected={rej}; file windows={len(blocks)}, "
          f"windows with TEXTITEM/SHAPEITEM lines={n_item_windows}")
    print("[2] [win+0xa1] histogram:", dict(sorted(a1_hist.items())))
    print("[3] H1 a1 == STATE count:", dict(agree_state))
    print("    H2 a1 == #item lines:", dict(agree_items))
    print("[4] distinct windows ever having a1>0:", len(windows_with_recs),
          sorted(windows_with_recs))
    print("[5] (record byte0, file item kind) pairs:", dict(tag_kind))
    print("[6] tag==0: pool string == file item NAME:", dict(pool_match))
    for e in pool_examples[:12]:
        print("      ", e)
    print("[7] tag==1 (u32@+1, u32@+5) top:", tag1_records.most_common(10))
    print("\nVERDICT h1_eq=%s h2_eq=%s poolhit=%s a1hist=%s" %
          (agree_state.get("eq", 0), agree_items.get("eq", 0),
           dict(pool_match), dict(sorted(a1_hist.items()))))
    return 0


pay = None
anch = None
if __name__ == "__main__":
    pay = RS.load_payload(ROOT)
    anch = RS.anchors_cached(ROOT, pay)
    sys.exit(main())
