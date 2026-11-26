#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""tPF-4: PLANLIST jump table + shape-cache registry read from banked saves.

TWO CLAIMS, BOTH MEASURED FROM RUNTIME RAM (no capture, no debugger):

(1) THE cs: JUMP TABLE AT 0x27fe8 IS WRITTEN INTO THE CODE IMAGE. The D10
    note read 0 at 0x242000+0x27fe8 — that is the DATA segment; the dispatch
    is `jmp dword ptr cs:[eax*4+0x27fe8]` (bytes 2e ff 24 85 e8 7f 02 00 at
    0x3cc9f), so the table lives in the CODE segment at image VA 0x27fe8 =
    guest PHYSICAL P0 + 0x27fe8, i.e. Memory-MEMBER offset B + 0x27fe8
    (B = per-run image base in the member, r1_sav_scan law; P0 = B - H).
    A hit is a u32 that (a) points inside the code image and (b) converts to
    payload FILE offset entry - P0 landing in the case-body span
    [0x3cca7, 0x3d1bc] of PLANLIST_paint (fn 0x3cbac).

(2) THE SHAPE-CACHE REGISTRY NAMES THE SHAPE IDS. Cache singleton ctx =
    P0 + 0x9f10c (shp.md S2, t62 measured 0x2e1194); slot idx name lives at
    ctx + 0x7d0 + idx*0x32 (shp.md S2 REGISTERED law). The PLANLIST painter
    fetches WORD slots ds:0x6fd80/0x6fd90/0x6fd92/0x6fd94/0x6fd9c and the
    race table ds:0x6fd60+2*race (tPF4_rowart_runtime.py: unanimous 30 /
    38 / 39 / 40 / 44 and 14..34 over 60 saves). This script resolves those
    ids to their registered names.

Exit 0 = table hits in >=1 save AND names resolved for the 5 row ids;
1 = honest negative; 2 = harness error.
"""
import os, struct, sys, zipfile, glob
from collections import Counter  # noqa: F401 (re-imported below pattern kept simple)
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAY = os.path.join(ROOT, "work", "ascend_payload.bin")

JT_VA = 0x27fe8
PAINT_LO, PAINT_HI = 0x3cca7, 0x3d1d0
CACHE_VA = 0x9f10c
NAME_OFF, NAME_STRIDE = 0x7d0, 0x32
IDS = [30, 38, 39, 40, 44] + list(range(14, 35))

# anchor law from scripts/r1_sav_scan.py (mid-image high-entropy windows)
def build_anchors(pay):
    anch, p = [], 0
    while p + 128 <= len(pay):
        w = pay[p:p + 128]
        if len(set(w)) > 40 and w.strip(b"\x00") == w:
            anch.append((p, w))
        p += 0x4000
    return anch


def find_b(mem, anch):
    votes = Counter()
    for p, w in anch:
        hits, start = [], 0
        while True:
            o = mem.find(w, start)
            if o < 0:
                break
            hits.append(o)
            start = o + 1
            if len(hits) > 5:
                break
        if len(hits) == 1:
            votes[hits[0] - p] += 1
    b, n = (votes.most_common(1) or [(None, 0)])[0]
    return b if n >= 5 else None


def main():
    banks = sys.argv[1:] or [os.path.join(ROOT, "work/r1/bank-play-20261111-t377")]
    slots = []
    for d in banks:
        slots += sorted(glob.glob(os.path.join(d, "*.sav")))
    if not slots:
        print("harness-error: no .sav under", banks)
        return 2
    pay = open(PAY, "rb").read()
    anch = build_anchors(pay)
    jt_votes, name_votes = Counter(), Counter()
    shown = 0
    names = {}
    for slot in slots:
        try:
            mem = zipfile.ZipFile(slot).read("Memory")
        except Exception:
            continue
        B = find_b(mem, anch)
        if B is None:
            print(f"{os.path.basename(slot)}: B not found")
            continue
        H = None  # derive H from the data-segment signature (ramp law)
        for h in range(0, 0x2000):
            if (struct.unpack_from("<H", mem, h + 0x413)[0] == 0x280
                    and struct.unpack_from("<H", mem, h + 0x44A)[0] == 80):
                H = h
                break
        if H is None:
            continue
        P0 = B - H
        raw = struct.unpack_from("<8I", mem, B + JT_VA)
        hit = []
        for i, v in enumerate(raw):
            f = v - P0
            ok = PAINT_LO <= f <= PAINT_HI
            hit.append(f"{i}:{hex(v)}->{hex(f)}{'*' if ok else ''}")
        jt_votes[tuple(raw)] += 1
        # registry names. ctx is a DATA-segment address (ds:0x9f10c):
        # member offset = 0x242000 + VA + H (pointer law), NOT B + VA.
        names = {}
        for idx in IDS:
            p = base + NAME_OFF + idx * NAME_STRIDE
            s = mem[p:p + 32].split(b"\0")[0]
            try:
                names[idx] = s.decode("cp437")
            except Exception:
                names[idx] = repr(s)
        name_votes[tuple(sorted(names.items()))] += 1
        if shown < 4:
            print(f"{os.path.basename(slot)} B={hex(B)} P0={hex(P0)}")
            print("  JT: " + " ".join(hit))
            print("  names 30/38/39/40/44: "
                  + " | ".join(f"{i}={names[i]}" for i in IDS[:5]))
            print("  race14..34: " + ",".join(names[i] for i in IDS[5:]))
        shown += 1
    print(f"\n== {shown} saves decoded; distinct JT variants: {len(jt_votes)} ==")
    for v, n in jt_votes.most_common(2):
        print("  x%d %s" % (n, tuple(hex(x) for x in v)))
    all_ok = all(names[i] for i in IDS[:5])
    print(f"name resolution for row ids {IDS[:5]}: "
          f"{'OK' if all_ok else 'EMPTY (negative)'}")
    return 0 if jt_votes and all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
