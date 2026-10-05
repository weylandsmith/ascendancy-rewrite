#!/usr/bin/env python3
"""r1_restore_sites.py — build the fixup-site-restored Ghidra image.

POINTER LAW (docs/re/r1-savestate.md, CLOSED 2026-10-05i):
    runtime_u32 = P0 + payload_file_offset(target), guest linear == physical.
Therefore the captured runtime u32 at a fixup site, MINUS P0, IS the payload
file offset of the target: writing runtime values into a copy of the payload
turns the static image into one whose data pointers speak payload-offset
units — exactly the address space Ghidra loads it in (base 0, file order ==
memory order, loader.md §2).

OUTPUTS
  work/ascend_restored.bin   payload with every IMAGE-CLASS differing
                             aligned u32 replaced by d = rv - P0 (the
                             payload-file offset of the target). heap /
                             conventional-mem diffs are runtime mutations
                             of globals, NOT link-time pointers, and are
                             deliberately NOT written.
  work/fixup_sites.tsv       ALL differing sites: f, file_u32, runtime_u32,
                             decoded=rv-P0, class (image-payload, image-bss,
                             conventional, heap/other).
 printed census             class counts + dereference profile (what the
                             target held at capture: ascii/data/zeros).
 Exit 0 on success; 2 harness-error (no captures, base not unanimous).
"""
import argparse, os, os.path, struct, sys, sys, zipfile
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base

PAYLOAD_SIZE = 0x8CC83
CBIMAGE = 0xA7710

def bda_h(mem):
    return [h for h in range(0, 0x2000)
            if struct.unpack_from("<H", mem, h + 0x413)[0] == 0x280
            and struct.unpack_from("<H", mem, h + 0x44A)[0] == 80]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--slot", help="default: the LAST slot (latest capture)")
    ap.add_argument("--needle", default="work/ascend_payload.bin")
    ap.add_argument("--out-bin", default="work/ascend_restored.bin")
    ap.add_argument("--out-tsv", default="work/fixup_sites.tsv")
    args = ap.parse_args()

    pay = open(args.needle, "rb").read()
    if len(pay) != PAYLOAD_SIZE:
        print(f"harness-error: payload size {len(pay):#x}"); return 2
    savedir = os.path.join(args.run_dir, "save")
    slots = sorted(f for f in os.listdir(savedir) if f.endswith(".sav"))
    if not slots:
        print("harness-error: no slots"); return 2
    slot = args.slot or slots[-1]
    mem = zipfile.ZipFile(os.path.join(savedir, slot)).read("Memory")
    hs = bda_h(mem)
    anch = build_anchors(pay)
    votes, _ = find_base(mem, anch)
    if len(hs) != 1 or not votes or votes.most_common(1)[0][1] < 5:
        print("harness-error: H or base not unique"); return 2
    H = hs[0]; B, _ = votes.most_common(1)[0]; P0 = B - H
    print(f"slot={slot} H={H:#x} B={B:#x} P0={P0:#x}")

    out = bytearray(pay)
    cls = Counter(); n = 0
    rows = []
    deref = Counter()
    for f in range(0, PAYLOAD_SIZE - 4, 4):
        rv = struct.unpack_from("<I", mem, B + f)[0]
        fv = struct.unpack_from("<I", pay, f)[0]
        if rv != fv:
            d = rv - P0
            if 0 <= d < PAYLOAD_SIZE: k = "image-payload"
            elif PAYLOAD_SIZE <= d < CBIMAGE: k = "image-bss"
            elif rv < 0xA0000: k = "conventional"     # direct phys < 640K
            else: k = "heap/other"
            cls[k] += 1
            # RESTORE only IMAGE-class sites, and write d (payload-file
            # offset), NOT rv — Ghidra loads the image at base 0, so d is the
            # address space its xrefs live in. heap/conventional diffs are the
            # running game MUTATING globals (runtime data flow, not link-time
            # pointers): writing them would bake title-screen state into a
            # supposedly static image. Sites stay in the TSV either way.
            if k == "image-payload":
                struct.pack_into("<I", out, f, d)
                n += 1
            # dereference test: what does the TARGET hold at capture time?
            seg = mem[H + rv:H + rv + 16] if 0 <= rv < len(mem) - H else b""
            pr = sum(1 for c in seg if 0x20 <= c < 0x7F)
            if not seg: deref["unreadable"] += 1
            elif seg == bytes(16): deref["zeros"] += 1
            elif pr >= 12: deref["ascii"] += 1
            else: deref["data"] += 1
            rows.append((f, fv, rv, d, k))
    open(args.out_bin, "wb").write(out)
    with open(args.out_tsv, "w") as t:
        t.write("file_off\tfile_u32\truntime_u32\tdecoded_off=rv-P0\tclass\n")
        for r in rows:
            t.write(f"0x{r[0]:x}\t0x{r[1]:x}\t0x{r[2]:x}\t"
                    + (f"0x{r[3]:x}" if r[3] >= 0 else f"-0x{-r[3]:x}")
                    + f"\t{r[4]}\n")
    print(f"restored image-pointer sites (value written = d=rv-P0): {n}")
    print(f"total differing sites in TSV: {len(rows)} -> {args.out_bin} / {args.out_tsv}")
    print("decoded-target classes: " + ", ".join(f"{k}:{v}" for k, v in cls.most_common()))
    print("dereference at target: " + ", ".join(f"{k}:{v}" for k, v in deref.most_common()))
    # NOTE: a naive wrong-base control (P0+k) is NOT discriminative — heap
    # pointers land 'above' at ANY shift, so class counts barely move
    # (measured: bss 173 vs 163 at +0x1000). The discriminative controls are
    # the C1-C5 battery in r1_pointer_law.py.
    return 0

if __name__ == "__main__":
    sys.exit(main())
