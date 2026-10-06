#!/usr/bin/env python3
"""r1_slot_delta.py — what changes BETWEEN ADJACENT slots of a live campaign?

Purpose (docs/STATE.md NEXT ACTION 2026-10-05l): in a long capture of a
RUNNING campaign, consecutive autosave slots differ only by what the game
touched since the last save. Adjacent-pair physical-region histograms isolate
turn/economy/AI mutation hotspots — the earliest-vs-latest diff (r1_deep_diff)
blends them all together.

For each mtime-consecutive pair (same campaign): changed-byte count and the
top physical 64 KiB regions; changed u32s are classified by the pointer law
(re-derived per run): rv in image span -> file offset rv-P0, else runtime
heap. Region addresses are GUEST PHYSICAL.

Usage: r1_slot_delta.py --run-dir work/r1/r1deep-... [--campaign-rec0]
  --campaign-rec0 : skip pairs whose planet rec0 name differs (campaign
                    restart belongs to r1_campaign_probe, not delta census)
Exit 0 ok / 2 harness.
"""
import argparse
import os
import struct
import sys
import zipfile
import collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base  # noqa: E402

PAY = "work/ascend_payload.bin"
PLANET_P0 = 0x26d07b
STRIDE_P = 123


def img_span():
    """Pointer law: runtime u32 = P0 + payload_file_offset(target), so the
    image-class range is [P0, P0 + len(payload)). len computed every run."""
    return 0x1BF450, 0x1BF450 + os.path.getsize(PAY)


def rec0_name(mem, H):
    seg = mem[PLANET_P0 + H:]
    z = seg.find(b"\x00")
    return seg[:z if 0 <= z <= 30 else 0].decode("ascii", "replace")


def load_slots(run_dir):
    sd = os.path.join(run_dir, "save")
    if not os.path.isdir(sd):
        return None
    pay = open(PAY, "rb").read()
    anch = build_anchors(pay)
    out = []
    for f in sorted(os.listdir(sd), key=lambda f: os.stat(os.path.join(sd, f)).st_mtime):
        if not f.endswith(".sav"):
            continue
        mem = zipfile.ZipFile(os.path.join(sd, f)).read("Memory")
        votes, _ = find_base(mem, anch)
        if not votes:
            continue
        H = votes.most_common(1)[0][0] - 0x1BF450
        out.append((f, mem, H))
    return out


def delta_pair(fa, mema, Ha, fb, memb, Hb, mask=()):
    """changed bytes keyed by GUEST PHYSICAL (a-anchored)."""
    IMG_LO, IMG_HI = img_span()
    def masked(lo):
        return any(a <= lo < b for a, b in mask)
    n = min(len(mema), len(memb)) - max(Ha, Hb)
    changed = 0
    regions = collections.Counter()
    refs = []
    p = 0
    a, b = mema, memb
    # walk in 64 KiB pages of PHYSICAL space
    PAGE = 0x10000
    for pg in range((n - 0x100000) // PAGE + 1 if n > 0x100000 else 0):
        lo = 0x100000 + pg * PAGE
        if masked(lo):
            continue
        ia, ib = lo + Ha, lo + Hb
        sa = a[ia:ia + PAGE]
        sb = b[ib:ib + PAGE]
        seg_changed = 0
        for k in range(min(len(sa), len(sb))):
            if sa[k] != sb[k]:
                seg_changed += 1
        if seg_changed:
            changed += seg_changed
            regions[hex(lo)] = seg_changed
            # u32 law census inside changed page (aligned)
            for k in range(0, min(len(sa), len(sb)) - 3, 4):
                if sa[k:k + 4] != sb[k:k + 4]:
                    rv = struct.unpack("<I", sb[k:k + 4])[0]
                    if IMG_LO <= rv < IMG_HI:
                        refs.append((lo + k, "img", rv - 0x1BF450))
                    elif rv != 0:
                        refs.append((lo + k, "heap", rv))
    return changed, regions, refs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--campaign-rec0", action="store_true")
    ap.add_argument("--max-pairs", type=int, default=19)
    ap.add_argument("--mask", default="",
                    help="comma list of physical ranges to ignore, e.g. "
                         "0x370000-0x3c0000. MEASURED (run 221429): "
                         "0x370000-0x3bffff is the game's RAM render buffer "
                         "(smooth byte gradients, entropy 6.4, churns every "
                         "redraw ~64K/s); mask it to see GAME state mutate.")
    args = ap.parse_args()
    if not os.path.exists(PAY):
        print("[delta] no payload needle; nothing to anchor against"); return 0
    slots = load_slots(args.run_dir)
    if slots is None or len(slots) < 2:
        print("[delta] harness: need >=2 anchored slots"); return 2

    total = 0
    pairs_done = 0
    hot = collections.Counter()
    mask = []
    for part in args.mask.split(","):
        part = part.strip()
        if not part:
            continue
        a_, b_ = part.split("-")
        mask.append((int(a_, 16), int(b_, 16)))
    for i in range(1, min(len(slots), args.max_pairs + 1)):
        fa, mema, Ha = slots[i - 1]
        fb, memb, Hb = slots[i]
        if args.campaign_rec0 and rec0_name(mema, Ha) != rec0_name(memb, Hb):
            print(f"{fa}->{fb}: CAMPAIGN RESTART ({rec0_name(mema,Ha)!r} -> "
                  f"{rec0_name(memb,Hb)!r}) — skipped for delta census")
            continue
        changed, regions, refs = delta_pair(fa, mema, Ha, fb, memb, Hb, mask)
        pairs_done += 1
        total += changed
        nimg = sum(1 for _, t, _ in refs if t == "img")
        for r, c in regions.most_common(5):
            hot[r] += c
        print(f"{fa}->{fb}: changed={changed} pages={len(regions)} "
              f"changed_u32={len(refs)} (img-law {nimg}, heap {len(refs)-nimg}) "
              f"top={regions.most_common(3)}")
    print(f"[delta] {pairs_done} pairs, total changed {total}")
    print("[delta] hottest physical regions:", hot.most_common(12))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
