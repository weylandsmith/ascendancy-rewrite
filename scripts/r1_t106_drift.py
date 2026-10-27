#!/usr/bin/env python3
"""r1_t106_drift.py — is the +0x55 deviation POST-GENERATION terrain drift?

P1 [measured] established the deviation set is RUN-LOCAL and NAME-INDEPENDENT
(7/15 runs have zero deviating planets; no name deviates consistently), which
kills the per-world authored/preset attribution premise. Remaining candidates:

  (A) MID-GAME TERRAIN WRITERS change the surface grid after generation, so
      the SAVE's nb no longer equals the generator's count. Known writers:
      item-36 Terraforming completion (barren -> class), rock event |8,
      nuke/glassing (class -> 0). Predicts: the deviating planet's SURFACE
      WORDS DIFFER across saves within the run, at a turn boundary, and the
      delta explains d (dnb ~ 3*d).
  (B) EXTRACTION ALIASING: the +0x88 array read is wrong for those records
      (banked S10 678-682 says pointer moves are aliasing, not gameplay).
      Predicts: fingerprint instability WITHOUT turn-boundary alignment, and
      the law holds at some other save in the same run for the same planet.
  (C) A GENERATION-TIME SOURCE my nb cannot see (preset/LCG-only) — predicted
      stable words, stable d, law never holds for that planet in that run.

Per (run, save-slot, planet): fingerprint md5 of surface words, nb, r55, d.
Exit 0 always.
Usage: r1_t106_drift.py --runs work/r1/r1deep-20261005-233706 [--all-saves]
"""
import argparse, collections, glob, hashlib, hashlib, os, struct as st, sys, zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_income_law as IL
from r1_sav_scan import build_anchors, find_base

NAME_AT = 0x24
TURN_C = 0x254E10


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="work/r1/*")
    ap.add_argument("--all-saves", action="store_true")
    ap.add_argument("--max-report", type=int, default=25)
    args = ap.parse_args()
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    anch = build_anchors(open(IL.PAY, "rb").read())

    for run in sorted(glob.glob(os.path.join(ROOT, args.runs))):
        src = os.path.join(run, "save")
        if not os.path.isdir(src):
            continue
        svs = sorted(glob.glob(os.path.join(src, "*.sav")), key=os.path.getmtime)
        if not svs:
            continue
        snaps = []
        for f in svs:
            try:
                m = zipfile.ZipFile(f).read("Memory")
            except Exception:
                continue
            v, _ = find_base(m, anch)
            if not v:
                continue
            H = v.most_common(1)[0][0]
            recs = {}
            for base, cells, cap, arr in IL.find_records(m):
                name = m[base + NAME_AT:base + NAME_AT + 30].split(b"\x00")[0] \
                       .decode("cp437", "replace").strip()
                w = [m[arr + i * 4] for i in range(cap)]
                nb = sum(1 for c in w[:cells] if (c & 0xF) != 0)
                r55 = st.unpack_from("<H", m, base + 0x55)[0]
                recs[name] = (cells, cap, nb, r55,
                              hashlib.md5(bytes(w[:cells])).hexdigest()[:10],
                              arr)
            turn = st.unpack_from("<H", m, TURN_C + H)[0] if TURN_C + H + 2 <= len(m) else -1
            snaps.append((os.path.basename(f), turn, recs))
        if len(snaps) < 2:
            continue

        # planets deviating in ANY save of this run
        devnames = sorted({n for _, _, rs in snaps for n, r in rs.items()
                           if r[3] != (r[2] // 3 + 5)})
        n_saves = len(snaps)
        stable_d = moving_words = boundary_aligned = 0
        lines = []
        for n in devnames:
            seq = [(f, t, rs[n]) for f, t, rs in snaps if n in rs]
            if len(seq) < 2:
                lines.append((n, "single-sample", seq[0][2][3], seq[0][2][2]))
                continue
            ds = {r[3] - (r[2] // 3 + 5) for _, _, r in seq}
            fps = {r[4] for _, _, r in seq}
            # boundary alignment: saves where the fingerprint changed vs the
            # previous sampled save that had a turn increment
            changes = [i for i in range(1, len(seq))
                       if seq[i][2][4] != seq[i - 1][2][4]]
            turns_up = [i for i in range(1, len(seq))
                        if seq[i][1] > seq[i - 1][1]]
            al = bool(changes) and all(i in turns_up for i in changes)
            if len(fps) == 1:
                stable_d += 1
            else:
                moving_words += 1
                if al:
                    boundary_aligned += 1
            lines.append((n, f"d={sorted(ds)} fps={len(fps)} chg@{changes} "
                             f"turnup={turns_up[:3]}.. aligned={al}",
                          seq[-1][2][3], seq[-1][2][2]))
        tot_dev = sum(1 for _, _, rs in snaps for n, r in rs.items()
                      if r[3] != (r[2] // 3 + 5))
        print(f"== {os.path.basename(run)} saves={n_saves} turns="
              f"{[t for _, t, _ in snaps][:6]}.. dev_planets={len(devnames)}")
        print(f"   words STABLE (candidate C / generation-time): {stable_d}   "
              f"words MOVING (A or B): {moving_words}   "
              f"turn-boundary-aligned: {boundary_aligned}")
        for ln in lines[:args.max_report]:
            print(f"   {ln[0]:22s} {ln[1]}")


if __name__ == "__main__":
    main()
