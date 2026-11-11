#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r1_deep_diff.py — measure whether a deeper capture went DEEP.

Compares the EARLIEST and LATEST autosave slot of one r1deep run (guest RAM
'Memory' members; H/B/P0 re-derived per slot via the pointer-law machinery,
r1_savestate.md). DEEP means the click actually loaded game state:

  changed_bytes      bytes differing between the two captures
  heap_changed       changed bytes OUTSIDE the image span [P0, P0+CBIMAGE)
                     (runtime data structures, the whole point)
  new_image_refs     u32 in a changed heap word whose decode d=rv-P0 lands
                     inside the payload image AND its file bytes are NOT
                     zero (a live structure pointing into real image data;
                     control: same census against zeros excluded)
  new_strings        printable runs >= 8 chars present in the LATE slot's
                     heap (outside image span) and absent from the EARLY
                     slot at the same physical address — loaded names/paths
                     (race/planet/ship strings land here; [unverified]
                     semantics until correlated to extracted/ tables)

Exit 0 iff changed_bytes >= --deep-bytes AND new_image_refs >= 50 AND
new_strings >= 5.  Exit 1 shallow/negative.  Exit 2 harness error.
Prints a compact census; all regions clamped to the member size.
"""
import argparse, os, re, struct, sys, zipfile
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base

CBIMAGE = 0xA7710
PAYLOAD_SIZE = 0x8CC83

def bda_h(mem):
    return [h for h in range(0, 0x2000)
            if struct.unpack_from("<H", mem, h + 0x413)[0] == 0x280
            and struct.unpack_from("<H", mem, h + 0x44A)[0] == 80]

def strings_at(buf, base):
    """printable runs >=8 inside buf (physical base ignored for set diff)."""
    return set(m.group() for m in re.finditer(rb"[\x20-\x7e]{8,}", buf))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--needle", default="work/ascend_payload.bin")
    ap.add_argument("--deep-bytes", type=int, default=100000)
    ap.add_argument("--needle-screen", default="",
                    help="string unique to the POST-click screen (e.g. "
                         "'cosmic exiles'); selects the pre-needle slot as "
                         "the early baseline")
    args = ap.parse_args()
    savedir = os.path.join(args.run_dir, "save")
    if not os.path.isdir(savedir):
        print("harness-error: no save dir"); return 2
    numbered = []
    for f in os.listdir(savedir):
        if not f.endswith(".sav"):
            continue
        # ORDER LAW: file mtime, NOT the slot number. autosave rotates a fixed
        # slot range (e.g. 41-60), so after a wrap the LOWEST-numbered slot is
        # the MOST RECENT write — numeric sort compared two near-identical
        # late frames and reported a false shallow (measured 2026-10-05k).
        numbered.append((os.path.getmtime(os.path.join(savedir, f)), f))
    numbered.sort()
    slots = [f for _, f in numbered]

    # BASELINE LAW (2026-10-05k): the EARLY frame must be a slot WITHOUT the
    # verify needle (pre-click state). If every slot has the needle, the
    # harness clicked before the first autosave (measured first-save latency
    # ~62 s from Xvfb start, twice) — schedule the click later. That's a
    # harness calibration error: exit 2.
    needle = None
    if args.needle_screen:
        needle = args.needle_screen.encode("latin-1")
        def has(f):
            mem = zipfile.ZipFile(os.path.join(savedir, f)).read("Memory")
            return needle in mem
        pre = [f for _, f in numbered if not has(f)]
        if not pre:
            print("harness-error: needle present in EVERY slot — click "
                  "landed before the first autosave; set SCHEDULE t >= 75")
            return 2
        slots = pre + [f for f in slots if f not in pre]
        keep = [slots[0], slots[-1]]
        slots = keep
    if len(slots) < 2:
        print("harness-error: need >= 2 slots"); return 2
    pay = open(args.needle, "rb").read()
    if len(pay) != PAYLOAD_SIZE:
        print("harness-error: payload size"); return 2
    anch = build_anchors(pay)

    def load(f):
        mem = zipfile.ZipFile(os.path.join(savedir, f)).read("Memory")
        hs = bda_h(mem)
        votes, _ = find_base(mem, anch)
        if len(hs) != 1 or not votes or votes.most_common(1)[0][1] < 5:
            return None
        H = hs[0]; B, _ = votes.most_common(1)[0]
        return mem, H, B

    a = load(slots[0]); b = load(slots[-1])
    if a is None or b is None:
        print(f"harness-error: anchor failed early={a is None} late={b is None}")
        return 2
    (ma, Ha, Ba), (mb, Hb, Bb) = a, b
    P0a, P0b = Ba - Ha, Bb - Hb
    n = min(len(ma), len(mb))
    print(f"early={slots[0]} H={Ha:#x} B={Ba:#x} P0={P0a:#x}")
    print(f"late ={slots[-1]} H={Hb:#x} B={Bb:#x} P0={P0b:#x}")

    changed = 0; heap_changed = 0
    heap_regions = []           # (start, run) of changed heap aligned words
    new_refs = 0; refs_seen = 0
    STEP = 4096
    for s in range(0, n - STEP, STEP):
        blk_a = ma[s:s + STEP]; blk_b = mb[s:s + STEP]
        if blk_a == blk_b:
            continue
        d = sum(1 for i in range(STEP) if blk_a[i] != blk_b[i])
        changed += d
        in_img = any(P0b <= p < P0b + CBIMAGE
                     for p in range(s - Ha, s - Ha + STEP))
        if not in_img:
            heap_changed += d
        # pointer census on aligned words that CHANGED (heap-class rv only)
        for o in range(0, STEP - 4, 4):
            va = struct.unpack_from("<I", blk_a, o)[0]
            vb = struct.unpack_from("<I", blk_b, o)[0]
            if va == vb: continue
            if P0b <= vb < P0b + PAYLOAD_SIZE:
                dv = vb - P0b
                refs_seen += 1
                tb = pay[dv:dv + 4]
                if tb and tb != bytes(4):
                    new_refs += 1
    # new-strings census: heap pages only (physical 0xA0000..0x1000000),
    # bounded to bound runtime; page-granular skip of identical pages
    early_s = set(); late_s = set()
    PAGE = 0x10000
    for s in range(0xA0000 + Ha, min(n - PAGE, 0x1000000 + Ha), PAGE):
        if ma[s:s + PAGE] == mb[s:s + PAGE]:
            continue
        late_s |= strings_at(mb[s:s + PAGE], s)
        early_s |= strings_at(ma[s:s + PAGE], s)
    new_strings = late_s - early_s
    sample = sorted(new_strings, key=lambda s: -len(s))[:8]

    print(f"changed_bytes={changed} heap_changed={heap_changed} "
          f"heap_image_refs={refs_seen} nonzeroderef={new_refs}")
    print(f"new_strings={len(new_strings)} sample={[x.decode(errors='replace') for x in sample]}")

    ok = changed >= args.deep_bytes and new_refs >= 50 and len(new_strings) >= 5
    if ok:
        # persist the heap-region census for the correlation step
        out = os.path.join(args.run_dir, "deep_census.txt")
        with open(out, "w") as t:
            t.write(f"early={slots[0]} late={slots[-1]} P0b={P0b:#x}\n")
            t.write(f"changed={changed} heap_changed={heap_changed} "
                    f"new_refs={new_refs} new_strings={len(new_strings)}\n")
            for x in sorted(new_strings):
                t.write("S\t" + x.decode(errors="replace") + "\n")
        print(f"census -> {out}")
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main())
