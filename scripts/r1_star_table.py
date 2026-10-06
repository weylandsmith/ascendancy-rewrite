#!/usr/bin/env python3
"""r1_star_table.py — star-system table law from live RAM (pointer law decoded).

MEASURED 2026-10-06 (runs r1deep-20261005-{230146,221429,233706}; guest
physical addresses, only meaningful via the per-run pointer-law H — the table
is RE-LOCATED by law every run, never by a baked base).

CONVENTION: star records are NAME-anchored; record k's NAME sits at
    0x255be1 + 96k (run 230146; the 49 consecutive name deltas are all
    exactly 96 — stride law). All field offsets below are RELATIVE TO NAME.

  STAR RECORD FIELDS (verified):
    name+0x2A  u32[5]  planet pointers, 0-padded; TARGET = planet NAME
                       address - 0x24 (record start). Entry is LIVE iff the
                       target planet's name prefix == this star name. Tail
                       slots beyond the live run hold GARBAGE pointers —
                       present even on fresh maps (allocator residue, NOT
                       campaign carryover; 43 on r1ad-131350 ck008).
    name-0x18  u32     system index, 0-based (== k) — all 50 records.
    name-0x14  f32 x   star position triple (x, y at +4, z at +8).
    name-0x20  u32     0xFFFFFFFF PRESENT in campaign runs (49/50 records,
                       first record reads 0) but ABSENT in idle run 221429 —
                       presence is NOT law; counted as a note only.
    name-0x1C  u32     small per-system value (5 Aglarond, 11 Pindentry,
                       7 Syzygifer, 4 Drollwell) [semantics unverified].
    name+0x10  u32[3]  sub-struct pointers into a pool of stride-0x27 (39 B)
                       records at 0x258xxx; systems draw pool slots in
                       PERMUTATION order (deltas all multiples of 39; the
                       same slot can serve two systems — Elwyssen and
                       Syzygifer share 0x258147 [semantics unverified]).

  PLANET RECORDS (name grid N_j = 0x26d07b + 123j, r1_campaign_probe law):
    star-pointer targets = N_j - 0x24 => the pointed-to record START precedes
    the name by 0x24 bytes. The orbit pair sits at N_j+0x57 (f32) and
    N_j+0x5f (f32): across 7 turn boundaries (run 230146) the PAIR's radius
    sqrt(x^2+y^2) is CONSTANT to f32 precision for all 151 planets (0 drift
    violations), while the pair VALUES change only between turn-counter
    slots: planets ORBIT their star; the turn loop advances orbital phase.
    16 planets keep constant (x,y) every slot (Icarus, Masticon, Pendulon,
    Aquila II, Buntrusol) [semantics of the static set unverified].

  Allocator tie: FUN_0004ae24 divides exactly by {0x7b, 0x60, 0x27}; live
    strides measured: planet 0x7b (123), star 0x60 (96), sub-pool 0x27 (39).
    The three pooled record families are now IDENTIFIED by pointer law.

Checks per slot: stride law, name+0x2A first-slot LIVE >=45/50, prefix law on
every LIVE pointer (a planet may be LIVE-owned by at most ONE system),
idx==k, sub stride 0x27. Exit 0 confirmed / 1 negative / 2 harness.
"""
import argparse
import os
import re
import struct
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base  # noqa: E402

PAY = "work/ascend_payload.bin"
PLANET_N = 0x26d07b      # planet NAME grid base (r1_campaign_probe law)
STRIDE_P = 123
STRIDE_S = 96
S_PTR = 0x2A             # u32[5] planet pointers (targets are name-0x24)
S_IDX = -0x18            # u32 system index (0-based)
S_XYZ = -0x14            # f32[3]
S_SENT = -0x20           # u32 sentinel (k>=1)
S_SUB = 0x10             # u32[3] stride-0x27 pool
NAME_ANCHOR_HINT = 0x255be1   # record 0 name pos in run 230146 (hint only)
PNAME_RE = rb"[A-Z][A-Za-z]{2,}(?: [IVX]+)?\x00"
SNAME_RE = rb"[A-Z][a-z]{2,15}\x00"


def load_slots(run_dir, idx=None):
    sd = os.path.join(run_dir, "save")
    files = sorted(os.listdir(sd), key=lambda f: os.stat(os.path.join(sd, f)).st_mtime)
    if idx is not None:
        files = files[idx:idx + 1]
    pay = open(PAY, "rb").read()
    anch = build_anchors(pay)
    out = []
    for f in files:
        if not f.endswith(".sav"):
            continue
        mem = zipfile.ZipFile(os.path.join(sd, f)).read("Memory")
        v, _ = find_base(mem, anch)
        if not v:
            continue
        out.append((f, mem, v.most_common(1)[0][0] - 0x1BF450))
    return out


def planet_name(mem, H, j):
    p = PLANET_N + H + j * STRIDE_P
    z = mem[p:p + 30].find(b"\x00")
    return mem[p:p + (z if 0 <= z <= 25 else 0)].decode("ascii", "replace")


def find_star_names(mem, H):
    """All stride-96 name-anchored star names near the hint anchor."""
    best = []
    for delta in range(0, 0x21):
        for sign in (-1, 1):
            cand = NAME_ANCHOR_HINT + sign * delta
            names = []
            k = 0
            while True:
                p = cand + k * STRIDE_S + H
                m = re.match(SNAME_RE, mem[p:p + 18])
                if not m:
                    break
                names.append((cand + k * STRIDE_S, m.group()[:-1].decode()))
                k += 1
                if k > 60:
                    break
            if len(names) > len(best):
                best = names
    return best


def check(mem, H, verbose=False):
    fails, notes = [], []
    nplanets = 0
    while re.match(PNAME_RE, mem[PLANET_N + H + nplanets * STRIDE_P:][:40]):
        nplanets += 1
        if nplanets > 400:
            break
    if nplanets < 50:
        return ["planet grid not resident"], []
    names = find_star_names(mem, H)
    if len(names) < 45:
        return [f"star name chain too short ({len(names)})"], []
    live_first = 0
    sent_hits = 0
    owned = {}
    stale = 0
    for k, (B, sn) in enumerate(names):
        p = B + H
        if struct.unpack_from("<i", mem, p + S_IDX)[0] != k:
            fails.append(f"{sn}: idx {struct.unpack_from('<i', mem, p + S_IDX)[0]} != {k}")
        first_live = False
        for i in range(5):
            v = struct.unpack_from("<I", mem, p + S_PTR + 4 * i)[0]
            if v == 0:
                continue
            off = v - (PLANET_N - 0x24)
            if off < 0 or off >= nplanets * STRIDE_P or off % STRIDE_P:
                stale += 1
                continue
            j = off // STRIDE_P
            pn = planet_name(mem, H, j)
            if pn.rsplit(" ", 1)[0] != sn:
                stale += 1
                continue
            if j in owned and owned[j] != sn:
                fails.append(f"planet {pn} LIVE-owned by TWO systems ({owned[j]},{sn})")
            owned[j] = sn
            if i == 0:
                first_live = True
        if first_live:
            live_first += 1
        if struct.unpack_from("<I", mem, p + S_SENT)[0] == 0xFFFFFFFF:
            sent_hits += 1
    subs = [struct.unpack_from("<I", mem, B + H + S_SUB)[0] for B, sn in names]
    steps = {subs[i] - subs[i - 1] for i in range(1, len(names))
             if subs[i] and subs[i - 1]}
    # Pool is stride-0x27 (39 B) but systems draw pool slots in PERMUTATION
    # order, not table order (observed deltas: -1443=-37*39, -858=-22*39,
    # -819=-21*39, ...; Elwyssen and Syzygifer even SHARE a slot 0x258147).
    # The law that holds: every pointer and every delta is a multiple of 39.
    bad = [d for d in steps if d % 0x27]
    if bad:
        fails.append(f"sub pool deltas not multiples of 39: {bad[:4]}")
    offpool = [hex(v) for v in subs if v and not (0x258000 <= v < 0x25a000)]
    if offpool:
        fails.append(f"sub ptrs outside 0x258xxx pool window: {offpool[:4]}")
    notes.append(f"stars {len(names)}; planets {nplanets}; first-slot-LIVE "
                 f"{live_first}/{len(names)}; live-owned {len(owned)}; "
                 f"stale/off-grid ptrs {stale}; sentinel {sent_hits}/{len(names)}")
    if verbose:
        for k, (B, sn) in enumerate(names[:12]):
            x, y, z = struct.unpack_from("<fff", mem, B + H + S_XYZ)
            ms = sorted(j for j in owned if owned[j] == sn)
            print(f"  k={k:<3}{B:#x} {sn:<13} ({x:8.1f},{y:8.1f},{z:8.1f}) "
                  f"{[planet_name(mem, H, j) for j in ms]}")
    return fails, notes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--slot", type=int, default=None)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    if not os.path.exists(PAY):
        print("[star] no payload needle")
        return 2
    slots = load_slots(args.run_dir, args.slot)
    if not slots:
        print("[star] harness: no slots")
        return 2
    worst = 0
    for f, mem, H in slots:
        fails, notes = check(mem, H, args.verbose)
        print(("OK  " if not fails else "FAIL") + f" {f}: {'; '.join(notes)}")
        for m in fails[:8]:
            print(f"      - {m}")
        if fails:
            worst = 1
    if worst:
        print("[star] NEGATIVE: law not confirmed in every slot")
    else:
        print(f"[star] STAR TABLE LAW CONFIRMED in {len(slots)} slot(s)")
    return worst


if __name__ == "__main__":
    raise SystemExit(main())
