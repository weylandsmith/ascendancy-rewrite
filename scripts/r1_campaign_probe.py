#!/usr/bin/env python3
"""r1_campaign_probe.py — when did a NEW CAMPAIGN start inside a capture?

LAW (verified 2026-10-05k, runs 204919 + 215445): the planet record table
is static-addressed at phys 0x26d07b for ANY campaign (resumed or freshly
generated). Its record-0 NAME string therefore identifies WHICH campaign
a slot holds; a change between mtime-consecutive slots marks the exact
10-second autosave window in which New Game launched. No vision required.

Related law: rec0 bytes +0x68/+0x69 are per-record generation constants,
NOT a turn clock (identical (152,37) across a campaign restart and idle
slots; see docs/re/r1-savestate.md).

Usage: r1_campaign_probe.py --run-dir work/r1/r1deep-... [--phys 0x26d07b]
Exit 0 = slots readable and >=2 distinct campaign names seen (launch was
captured); 1 = single campaign across all slots (no launch in window);
2 = harness problem (no slots / member unreadable).
"""
import argparse
import datetime
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base  # noqa: E402

STRIDE_P = 123
PAY = "work/ascend_payload.bin"


def rec0_name(mem, p0_phys, H):
    seg = mem[p0_phys + H:]
    z = seg.find(b"\x00")
    return seg[:z if 0 <= z <= 30 else 0].decode("ascii", "replace")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--phys", default="0x26d07b",
                    help="planet table base (static across campaigns)")
    args = ap.parse_args()
    sd = os.path.join(args.run_dir, "save")
    if not os.path.isdir(sd):
        print("[probe] no save dir"); return 2
    if not os.path.exists(PAY):
        print("[probe] no payload needle (no captures on this machine?)"); return 0
    pay = open(PAY, "rb").read()
    anch = build_anchors(pay)
    p0 = int(args.phys, 16)

    rows = []
    for f in os.listdir(sd):
        if not f.endswith(".sav"):
            continue
        try:
            st = os.stat(os.path.join(sd, f))
            mem = zipfile.ZipFile(os.path.join(sd, f)).read("Memory")
        except Exception as e:
            print(f"[probe] {f}: {e!r}"); continue
        votes, _ = find_base(mem, anch)
        if not votes:
            print(f"[probe] {f}: base unresolved"); continue
        H = votes.most_common(1)[0][0] - 0x1BF450
        rows.append((st.st_mtime, f, rec0_name(mem, p0, H)))
    if not rows:
        print("[probe] zero readable slots"); return 2
    rows.sort()
    for mt, f, nm in rows:
        print(f, datetime.datetime.fromtimestamp(mt).strftime("%H:%M:%S"), repr(nm))
    names = {nm for _, _, nm in rows if nm}
    if len(names) >= 2:
        trans = [(rows[i][1], rows[i - 1][2], rows[i][2])
                 for i in range(1, len(rows)) if rows[i][2] != rows[i - 1][2] and rows[i][2] and rows[i - 1][2]]
        print(f"[probe] {len(names)} campaigns; transitions: {trans}")
        return 0
    print("[probe] single campaign across all slots")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
