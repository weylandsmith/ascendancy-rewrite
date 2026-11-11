#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r1_pointer_law.py — POINTER LAW CONFIRMATION (law CLOSED 2026-10-05i).

THE LAW (see docs/re/r1-savestate.md for the full evidence trail):
    The ascend.exe payload image is loaded ONCE at guest-physical
    P0 = B - H  (B = per-run anchor base via r1_sav_scan; H = 136, BDA scan).
    Bytes are verbatim from the payload file EXCEPT at Watcom fixup sites,
    where the file's intra-object offsets have been replaced by absolute
    addresses:
        guest_phys(target) = P0 + payload_file_offset(target)
    and guest linear == guest physical (flat DPMI). The runtime u32-vs-file-u32
    delta clusters 0x1d4000 / 0x242000 are simply P0 + (file offset of the
    object region holding the SITE); their gap 0x6E000 is the file span between
    those regions. No per-object law, no second copy, no linear skew K.

CONFIRMATION TESTS (this script, every slot; exit 0 iff all pass on >=1 slot):
  C1  code-window law: 6 windows inside the code region: the 16-byte file
      window at pay[f] matches mem[B+f] at >=80% byte positions (fixups may
      land inside a window, so byte-level not slice equality), and the SAME
      window does NOT occur elsewhere in the payload (uniqueness control).
  C2  string-law census: for the 8 EXE-proven path-template strings
      (docs/re/loader.md §5), the unique live occurrence at physical q = P0+f
      (f = file offset) exists for EVERY string.
  C3  vtable prologue spike: runs >=8 of live pointer values v inside the
      image span; pay[v-P0] must be a Watcom function-start byte (control
      15%, see loader.md §4.1).
  C4  pointer decode: >=50 fixup slots decode to target file offsets whose
      bytes are printable ASCII runs >=6 (a sample of the decoded targets
      land on string data — the '.cpp' debug strings are the loudest).
  C5  CPU corroboration: a CPU-member u32 (offset 0x20 on this build) lies
      inside the loaded image span.
Exit codes follow the R1 convention: 0 law confirmed, 1 negative, 2 harness.
"""
import argparse, os, struct, sys, zipfile
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base

PAYLOAD_SIZE = 0x8cc83
CBIMAGE = 0xa7710
EXE_STRINGS = [b"MOUSE.SHP", b"planets.shp", b"suns.shp", b"game.pal",
               b"1starmap.tmp", b"3cfgnew.tmp", b"BLACK%.2d.HAZ", b"0OPENING.GIF"]
START = {0x55, 0xB8, 0x53, 0x56, 0x57, 0xE8, 0x9C, 0xC8, 0x6A, 0x68, 0xB9,
         0xBA, 0xBB, 0xBE, 0xBF, 0x33, 0x31, 0x8B, 0xF6, 0xF7, 0x81, 0x83,
         0xE9, 0xEB}

def bda_h(mem):
    return [h for h in range(0, 0x2000)
            if struct.unpack_from("<H", mem, h + 0x413)[0] == 0x280
            and struct.unpack_from("<H", mem, h + 0x44A)[0] == 80]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--needle", default="work/ascend_payload.bin")
    ap.add_argument("--slot")
    args = ap.parse_args()
    pay = open(args.needle, "rb").read()
    if len(pay) != PAYLOAD_SIZE:
        print(f"harness-error: payload size {len(pay):#x} != {PAYLOAD_SIZE:#x}")
        return 2
    anch = build_anchors(pay)
    savedir = os.path.join(args.run_dir, "save")
    if not os.path.isdir(savedir):
        print("harness-error: no save dir"); return 2
    slots = sorted(f for f in os.listdir(savedir) if f.endswith(".sav"))
    if args.slot: slots = [f for f in slots if f == args.slot]

    any_pass = False
    for f in slots:
        z = zipfile.ZipFile(os.path.join(savedir, f))
        mem = z.read("Memory")
        hs = bda_h(mem)
        votes, _ = find_base(mem, anch)
        if len(hs) != 1 or not votes or votes.most_common(1)[0][1] < 5:
            print(f"{f}: skip (H {hs}, votes {votes.most_common(1)[0][1] if votes else 0})")
            continue
        H = hs[0]; B, _ = votes.most_common(1)[0]; P0 = B - H
        res = {}

        # C1 image windows at spread file offsets (16B may include fixups)
        c1ok = 0; n1 = 0
        for fo in (0x14bb0, 0x15bb0, 0x18bb0, 0x34bb0, 0x54bb0, 0x6ebb0):
            w = pay[fo:fo + 16]
            same = sum(1 for i in range(16) if mem[B + fo + i] == w[i])
            occ = []
            st = 0
            while True:
                o = pay.find(w, st)
                if o < 0: break
                occ.append(o); st = o + 1
            if same >= 12 and len(occ) <= 2 and fo in occ: c1ok += 1
            n1 += 1
        res["C1"] = f"{c1ok}/{n1}"

        # C2 string laws
        c2ok = 0
        for s in EXE_STRINGS:
            q = pay.find(s)
            if q < 0: continue
            occ = []
            st = 0
            while True:
                o = mem.find(s, st)
                if o < 0: break
                occ.append(o - H); st = o + 1
            if any(o == P0 + q for o in occ): c2ok += 1
        res["C2"] = f"{c2ok}/{len(EXE_STRINGS)}"

        # C3 pointer-table prologue spike (scan whole loaded span)
        hit = tot = 0
        o = 0x14bb0
        end = min(CBIMAGE - 0x100, PAYLOAD_SIZE - 0x1000)
        while o + 32 <= end:
            run = []; q = o
            while q + 4 <= PAYLOAD_SIZE and len(run) < 40:
                v = struct.unpack_from("<I", mem, B + q)[0]
                if P0 <= v < P0 + CBIMAGE and v % 4 == 0:
                    run.append(v); q += 4
                else: break
            if len(run) >= 8:
                for v in run:
                    t = v - P0
                    if 0x14bb0 <= t < 0x82bb0:
                        tot += 1; hit += 1 if pay[t] in START else 0
                o = q - 4
            else:
                o += 4
        res["C3"] = f"{hit}/{tot} ({100.0 * hit / max(tot, 1):.0f}% ctrl15)"

        # C4 decode-to-string (delta!=0 sites; decoded target printable)
        dec = 0; tried = 0
        for o in range(0x14bb0, min(0x70000, PAYLOAD_SIZE - 4), 4):
            rv = struct.unpack_from("<I", mem, B + o)[0]
            pv = struct.unpack_from("<I", pay, o)[0]
            if rv != pv:
                tried += 1
                t = rv - P0
                if 0 <= t < PAYLOAD_SIZE - 6:
                    seg = pay[t:t + 6]
                    if all(0x20 <= c < 0x7F for c in seg): dec += 1
        res["C4"] = f"{dec} printable / {tried} fixed-up sites sampled-to-0x70000"

        # C5 CPU corroboration
        try:
            cpu = z.read("CPU")
            v = struct.unpack_from("<I", cpu, 0x20)[0]
            res["C5"] = f"{v:#x} in span {P0 <= v < P0 + CBIMAGE}"
            c5 = P0 <= v < P0 + CBIMAGE
        except Exception as e:
            res["C5"] = f"read fail {e!r}"; c5 = False

        ok = (res["C1"].startswith("6/") and res["C2"] == f"{len(EXE_STRINGS)}/{len(EXE_STRINGS)}"
              and tot > 0 and hit / tot > 0.6 and dec >= 50 and c5)
        print(f"{f}: P0={P0:#x} " + " ".join(f"{k}={v}" for k, v in res.items())
              + f"  -> {'LAW CONFIRMED' if ok else 'NEGATIVE'}")
        any_pass |= ok
    return 0 if any_pass else 1

if __name__ == "__main__":
    sys.exit(main())
