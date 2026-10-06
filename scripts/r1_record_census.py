#!/usr/bin/env python3
"""r1_record_census.py — per-record, per-offset census of planet-table churn.

Purpose (docs/STATE.md NEXT ACTION 2026-10-06, W1(b) analysis half): the
turn-boundary census so far is aggregate ("~600-950 changed per hot offset").
That cannot tell WHO changing records are or whether hot u16s are counters or
state-mixing noise. This script keys every changed byte by (record index,
intra-record offset) across mtime-consecutive slot pairs, splitting pairs by
the TURN-BOUNDARY law (turn counter u16 phys 0x254e10 changed vs unchanged).

Record convention HERE: name-anchored (record = 123 B window whose +0x00 is
the NUL-terminated planet name; base phys 0x26d07b per r1_campaign_probe law).
Deep-heap-census offsets (name at +0x59) convert as o' = o - 0x22.

Cluster analysis: head signature bytes +0x35..+0x3f (first slot) group records
that share defaults; churn per cluster separates mutating-state groups from
statics (unowned planets, etc.).

Counter-vs-noise test per hot offset over boundary pairs in time order:
flat (never changes) / monotone (one-direction, counter-shaped) / mixed.

Outputs (default <run-dir>/census/):
  census-boundary.tsv   per-offset stats over turn-boundary pairs
  census-idle.tsv       per-offset stats over non-boundary pairs
  clusters.txt          signature clusters + churn + member names
  records.txt           per-slot 123-B hexdump for --dump-records records
Exit 0 = census produced; 1 = negative; 2 = harness error.
"""
import argparse
import collections
import os
import re
import struct
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base  # noqa: E402

PAY = "work/ascend_payload.bin"
PLANET_P0 = 0x26d07b          # static across campaigns (r1_campaign_probe law)
TURN_C = 0x254e10             # u16 turn counter (byte-verified 2026-10-05l)
STRIDE = 123
NAME_RE = rb"[A-Z][A-Za-z]{2,}(?: [IVX]+)?\x00"


def load_slots(run_dir):
    """mtime-ordered slots: {f, mt, mem, H, n(records), turn, rec0}."""
    sd = os.path.join(run_dir, "save")
    if not os.path.isdir(sd):
        return []
    pay = open(PAY, "rb").read()
    anch = build_anchors(pay)
    out = []
    for f in sorted(os.listdir(sd), key=lambda f: os.stat(os.path.join(sd, f)).st_mtime):
        if not f.endswith(".sav"):
            continue
        try:
            st = os.stat(os.path.join(sd, f))
            mem = zipfile.ZipFile(os.path.join(sd, f)).read("Memory")
        except Exception as e:
            print(f"[census] {f}: {e!r}")
            continue
        votes, _ = find_base(mem, anch)
        if not votes:
            print(f"[census] {f}: base unresolved — skipped")
            continue
        H = votes.most_common(1)[0][0] - 0x1BF450
        n = 0
        while True:
            j = PLANET_P0 + n * STRIDE + H
            if j >= len(mem) or mem[j] == 0:
                break
            if not re.match(NAME_RE, mem[j:j + 40]):
                break
            n += 1
        turn = struct.unpack("<H", mem[TURN_C + H:TURN_C + H + 2])[0]
        seg = mem[PLANET_P0 + H:]
        z = seg.find(b"\x00")
        out.append({"f": f, "mt": st.st_mtime, "mem": mem, "H": H, "n": n,
                    "turn": turn,
                    "rec0": seg[:z if 0 <= z <= 30 else 0].decode("ascii", "replace")})
    return out


def record_rows(s):
    """list of n 123-B bytes objects for one slot."""
    base = PLANET_P0 + s["H"]
    return [s["mem"][base + r * STRIDE: base + (r + 1) * STRIDE]
            for r in range(s["n"])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--out", default=None, help="default <run-dir>/census")
    ap.add_argument("--dump-records", default="0,1,2,25,150",
                    help="comma list of record indices to hexdump")
    args = ap.parse_args()

    out_dir = args.out or os.path.join(args.run_dir, "census")
    os.makedirs(out_dir, exist_ok=True)

    slots = [s for s in load_slots(args.run_dir) if s["n"] >= 50]
    if len(slots) < 2:
        print("[census] NEGATIVE: no slots with a resident planet table")
        return 1

    # single-campaign window (a restart mid-window would poison the census)
    if len({s["rec0"] for s in slots}) > 1:
        print("[census] multiple campaigns in window; cutting at transition")
        keep = [slots[0]]
        for s in slots[1:]:
            if s["rec0"] != keep[0]["rec0"]:
                break
            keep.append(s)
        slots = keep
        if len(slots) < 2:
            print("[census] NEGATIVE: <2 slots before transition")
            return 1

    nrec = min(s["n"] for s in slots)
    rows = [record_rows(s) for s in slots]   # rows[i][r] = 123 B
    print(f"[census] {len(slots)} slots campaign {slots[0]['rec0']!r} "
          f"records={nrec}")
    print("[census] turn sequence (mtime order):", [s["turn"] for s in slots])

    boundary = [i for i in range(1, len(slots))
                if slots[i]["turn"] != slots[i - 1]["turn"]]
    nonbound = [i for i in range(1, len(slots))
                if slots[i]["turn"] == slots[i - 1]["turn"]]
    print(f"[census] boundary transitions={len(boundary)} "
          f"non-boundary={len(nonbound)}")

    def pair_census(idxs):
        changed_off = collections.Counter()   # off -> changed bytes
        recs_off = collections.Counter()      # off -> distinct records that changed
        rec_any = collections.Counter()       # record -> offsets changed (boundary only matters)
        for i in idxs:
            for r in range(nrec):
                ra, rb = rows[i - 1][r], rows[i][r]
                offs = [o for o in range(STRIDE) if ra[o] != rb[o]]
                for o in offs:
                    changed_off[o] += 1
                for o in offs:
                    recs_off[o] += 1
                rec_any[r] += len(offs)
        return changed_off, recs_off, rec_any

    bchg, brecs, rec_any = pair_census(boundary)
    nichg, nrecs, _ = pair_census(nonbound)

    # hot offsets: any boundary change
    hot = sorted(bchg)
    # monotony split per hot offset (u8 view over ALL slots; boundary context
    # is in the turn list — a change on a non-boundary step is itself evidence)
    lines = []
    for o in hot:
        mono = flat = mix = 0
        dh = collections.Counter()
        for r in range(nrec):
            vals = [rows[i][r][o] for i in range(len(slots))]
            fw = sum(1 for i in range(1, len(vals)) if vals[i] > vals[i - 1])
            bw = sum(1 for i in range(1, len(vals)) if vals[i] < vals[i - 1])
            if fw == 0 and bw == 0:
                flat += 1
            elif fw == 0 or bw == 0:
                mono += 1
            else:
                mix += 1
            for i in range(1, len(vals)):
                if vals[i] != vals[i - 1]:
                    dh[(vals[i] - vals[i - 1]) & 0xFF] += 1
        lines.append((o, bchg[o], brecs[o], mono, flat, mix, dh.most_common(5)))

    with open(os.path.join(out_dir, "census-boundary.tsv"), "w") as fh:
        fh.write("off\tchanged_bytes\trecords_changed\tmono\tflat\tmix\ttop_u8_deltas\n")
        for o, c, rc, mono, flat, mix, top in lines:
            fh.write(f"0x{o:02x}\t{c}\t{rc}\t{mono}\t{flat}\t{mix}\t{top}\n")
    with open(os.path.join(out_dir, "census-idle.tsv"), "w") as fh:
        fh.write("off\tchanged_bytes\trecords_changed\n")
        for o in sorted(nichg):
            fh.write(f"0x{o:02x}\t{nichg[o]}\t{nrecs[o]}\n")

    # clusters by head signature +0x35..+0x3f (first slot)
    sig_of = {r: bytes(rows[0][r][0x35:0x40]) for r in range(nrec)}
    clusters = collections.defaultdict(list)
    for r, s in sig_of.items():
        clusters[s].append(r)

    def rec_name(i, r):
        seg = rows[i][r]
        z = seg.find(b"\x00")
        return seg[:z if 0 <= z <= 20 else 0].decode("ascii", "replace")

    with open(os.path.join(out_dir, "clusters.txt"), "w") as fh:
        fh.write("# clusters: records sharing head sig +0x35..0x3f (slot 0); "
                 "churn = boundary-transition steps where >=1 member record "
                 "differs; names[0]=slot0 -> names[-1]=last slot\n")
        for sig, rs in sorted(clusters.items(), key=lambda kv: -len(kv[1])):
            churn = sum(1 for i in boundary
                        if any(rows[i - 1][r] != rows[i][r] for r in rs))
            names = [rec_name(0, rs[0]), rec_name(len(slots) - 1, rs[0])]
            fh.write(f"{sig.hex()}  n={len(rs):3d} churn={churn:4d}/{len(boundary)}"
                     f"  first_member={names[0]!r}->{names[1]!r}"
                     f"  members={rs[:10]}{'...' if len(rs) > 10 else ''}\n")
    print("[census] clusters.txt:")
    with open(os.path.join(out_dir, "clusters.txt")) as fh:
        sys.stdout.write(fh.read())

    # hexdumps
    dpath = os.path.join(out_dir, "records.txt")
    dump = [int(x) for x in args.dump_records.split(",") if x.strip()]
    with open(dpath, "w") as fh:
        for r in dump:
            if r >= nrec:
                continue
            fh.write(f"== record {r} {rec_name(0, r)!r} -> "
                     f"{rec_name(len(slots)-1, r)!r}\n")
            for i, s in enumerate(slots):
                hexs = " ".join(f"{b:02x}" for b in rows[i][r])
                fh.write(f"{s['f']} t={s['turn']:<3} {hexs}\n")
    print(f"[census] hexdumps -> {dpath}")

    print(f"[census] boundary-ONLY offsets: {sorted(set(hot) - set(nichg))}")
    print(f"[census] churn-in-both offsets: {sorted(set(hot) & set(nichg))}")
    idle_recs = {r for i in nonbound for r in range(nrec)
                 if rows[i - 1][r] != rows[i][r]}
    print(f"[census] records changing OFF boundaries (idle churn): "
          f"{sorted(idle_recs)}")
    print("[census] top boundary offsets (bytes / records / mono,flat,mix / deltas):")
    for o, c, rc, mono, flat, mix, top in sorted(lines, key=lambda x: -x[1])[:16]:
        print(f"  +0x{o:02x}: {c:5d} recs={rc:3d} mono={mono} flat={flat} "
              f"mix={mix} top={top}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
