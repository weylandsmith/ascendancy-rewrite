#!/usr/bin/env python3
"""t251 — witness miner for the two play-gated OQ residues.

WITNESS (a) [OQ-016 / diplomacy row 13 clamp witnesses]: a multi-volley
battle against a NON-at-war owner. From the trusted stream (r1_stream
observations(trust=True) ONLY — t214 law: raw row arithmetic is
writer-multiplicity garbage), consecutive trusted points where a live
ship's window changes beyond coords/state (damage application, t85 law)
while relation.states[attacker][victim] != 2 (not WAR) — plus ship
disappearance (destruction) under the same non-war condition.
Multi-volley proxy: changes persisting across >=2 consecutive trusted
pairs on the same slot-pair (the 10 s ring cannot resolve intra-battle
order — t85 honest scope; a second volley between two autosaves IS the
observable).

WITNESS (b) [OQ-021 S6 semantic non-join + aicode P7 label]: a
mid-campaign slot with V=dword[0x482fb]>1 AND some byte[star+0x15]
nonzero. The watcher timeline does NOT carry +0x15, so this witness is
mined from the on-disk slot ZIPs (bank dirs + live ring) — same reader
as r212_predicate_corr (r1_slot base vote, P = B+0x82BB0), extended to
report the join row-by-row instead of only V==ownP correlation.

Rewind caveat (MEASURED t251): the live :9 session was relaunched from
the user's RESUME.GAM at turn 1086 while the timeline already holds
turns up to 1335 -> trust=True's watermark (1335) drops ALL new-session
rows. The new session's window is therefore mined trust=False PAIRED BY
WALL-CLOCK (r1_stream's own sanctioned caveat), and reported separately
from the trust=True corpus pass.

usage: r1_t251_mine.py [--window HH:MM:SS-HH:MM:SS] [--banks dir,...]
Exit 0 always (findings printed; honest negatives are findings).
"""
import argparse, glob, json, os, struct, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r1_stream as ST
import r1_slot as S

RUN = os.path.join(os.path.dirname(HERE), "work/r1/playcap")
COORD_U16 = {0x9e // 2, (0x9e + 2) // 2, (0x9e + 4) // 2, (0x9e + 6) // 2}
OFF = 0x82BB0
STAR_BASE = 0x13BC5
STARS_WORD = 0x16145


def alive(w):
    return any(w) and not all(x == 0xFFFF for x in w)


def window_rows(path, lo, hi):
    """Streaming wall-clock window scan, json.loads per row (rows are huge;
    one at a time, never the file). lo/hi are HH:MM:SS strings (inclusive)."""
    with open(path, "r", errors="replace") as f:
        for line in f:
            i = line.find('"wall": "')
            if i < 0 or not (lo <= line[i + 8:i + 16] <= hi):
                continue
            try:
                yield json.loads(line)
            except Exception:
                continue


def dist_ok(tgt):
    """Engagement-scale proximity: same-system class. Galaxy coords span
    ~3000 units; co-located ships measured dist2==0.0 (t85 banked pairs);
    allow <= 60 units (3600 dist2) as 'engagement scale' [unverified bound,
    deliberately generous — vetting is human, the filter only drops obvious
    far-apart pairs]."""
    return tgt is not None and tgt[2] <= 3600.0


def mine_stream(rows, tag, strict=False):
    """Witness (a) over a sequence of observation dicts (already ordered).
    A damage/destruction candidate = live ship k whose window changes beyond
    coords (t85 law) or dies between consecutive points, WITH the nearest
    other-owner ship reported so the engagement partner (and its relation
    state) is checkable. streak[(att,vic)] counts consecutive candidate
    pairs on the same owner-pair = the multi-volley proxy (10 s ring cannot
    resolve intra-battle order — t85 honest scope)."""
    prev = None
    hits = []
    strict_hits = []
    streak = {}
    n = 0
    for j in rows:
        if j.get("ship_raw") is None or not j.get("in_game"):
            continue
        n += 1
        rel = j.get("relation")
        states = rel["states"] if rel else None
        names = rel["names"] if rel else []
        if prev is not None:
            rw1, rw2 = prev["ship_raw"], j["ship_raw"]
            sp1 = {s["slot"]: s for s in prev.get("ships", [])}
            for k in sorted(set(rw1) & set(rw2), key=int):
                w1, w2 = rw1[k], rw2[k]
                if not alive(w1):
                    continue
                o1 = w1[0x54 // 2] | (w1[0x54 // 2 + 1] << 16)
                o2 = w2[0x54 // 2] | (w2[0x54 // 2 + 1] << 16)
                if o1 == 0xFFFF:
                    continue
                diffs = [i for i in range(177)
                         if w1[i] != w2[i] and i not in COORD_U16]
                dead = not alive(w2)
                if not diffs and not dead:
                    continue
                if o2 != o1 and not dead:
                    continue  # owner flip = capture class, not damage
                # nearest other-owner ship in the PREVIOUS point (engagement
                # partner candidate)
                tgt = None
                s1 = sp1.get(int(k))
                if s1:
                    for s3 in prev.get("ships", []):
                        o3 = s3["owner"]
                        if o3 == o1 or o3 == 0xFFFF:
                            continue
                        d2 = sum((a - b) ** 2 for a, b in zip(s1["xyz"], s3["xyz"]))
                        if tgt is None or d2 < tgt[2]:
                            tgt = (s3["slot"], o3, d2)
                vic = tgt[1] if tgt else None
                relv = (states[o1][vic] if states and vic is not None
                        and o1 < len(states) and vic < len(states[0]) else None)
                if vic is not None:
                    key = (o1, vic)
                    streak[key] = streak.get(key, 0) + 1
                else:
                    streak[(o1, None)] = streak.get((o1, None), 0) + 1
                row = dict(tag=tag, turn=prev["turn"], j_to=j["turn"],
                           slot=k, att=o1, vic=vic, rel=relv,
                           streak=streak[(o1, vic)], dead=dead,
                           ndiff=len(diffs),
                           dist2=round(tgt[2], 1) if tgt else None,
                           wall=j.get("wall"),
                           att_name=names[o1] if o1 < len(names) else "?",
                           vic_name=(names[vic] if vic is not None and vic < len(names) else "?"))
                if relv != 2:
                    hits.append(row)
                    if (strict and vic is not None and relv is not None
                            and o1 < len(names) and dist_ok(tgt)):
                        strict_hits.append(row)
        prev = j
    return n, hits, strict_hits


def mine_slot_ram(banks):
    """Witness (b): V>1 AND any byte[star+0x15] nonzero, per slot file."""
    pay = open(os.path.join(os.path.dirname(HERE), "work/ascend_payload.bin"), "rb").read()
    anch = S.anchors_cached(os.path.dirname(HERE), pay)
    out = []
    nslots = 0
    for root in banks:
        for f in sorted(glob.glob(os.path.join(root, "*.sav"))) + \
                 sorted(glob.glob(os.path.join(root, "save", "*.sav"))):
            try:
                mem = zipfile.ZipFile(f).read("Memory")
            except Exception:
                continue
            B = S.base_of(mem, anch)
            if B is None:
                continue
            P = B + OFF
            V = struct.unpack_from("<I", mem, P + 0x482FB)[0]
            turn = struct.unpack_from("<I", mem, P + 0x12E10)[0]
            if turn == 0:
                continue
            nst = struct.unpack_from("<H", mem, P + STARS_WORD)[0]
            nz = [k for k in range(min(nst, 60))
                  if mem[P + STAR_BASE + 0x60 * k + 0x15]]
            nslots += 1
            if V > 1 and nz:
                out.append(dict(file=f, turn=turn, V=V,
                                stars_with_15=len(nz), first=nz[:8]))
    return nslots, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", default=None, help="HH:MM:SS-HH:MM:SS wall window (trust=False pass)")
    ap.add_argument("--banks", default=None, help="comma list of bank dirs for witness (b)")
    ap.add_argument("--strict", action="store_true", help="also collect engagement-scale strict hits")
    a = ap.parse_args()
    banks = (a.banks.split(",") if a.banks else
             sorted(glob.glob(os.path.join(os.path.dirname(HERE), "work/r1/bank-*"))))

    print("== PASS 1: witness (a) over TRUSTED stream ==")
    st = {}
    n, hits, shits = mine_stream(ST.observations(RUN, trust=True, stats=st), "trusted", strict=a.strict)
    print(f"trusted points={n}  {ST.echo_note(st)}")
    print(f"non-war damage/destruction candidate events: {len(hits)}")
    for h in hits[:40]:
        print("  ", h)
    if a.strict:
        print(f"  STRICT (engagement-scale, named parties, rel known): {len(shits)}")
        for h in shits[:60]:
            print("  *", h)

    if a.window:
        lo, hi = a.window.split("-")
        print(f"\n== PASS 2: witness (a) over NEW SESSION wall window {lo}..{hi} (trust=False) ==")
        n2, hits2, shits2 = mine_stream(window_rows(os.path.join(RUN, "live-timeline.jsonl"), lo, hi), "newsession", strict=a.strict)
        print(f"new-session in-game points={n2}")
        print(f"non-war damage/destruction candidate events: {len(hits2)}")
        for h in hits2[:40]:
            print("  ", h)
        if a.strict:
            print(f"  STRICT new-session: {len(shits2)}")
            for h in shits2[:60]:
                print("  *", h)

    print("\n== PASS 3: witness (b) V>1 AND byte[star+0x15] nonzero over slot banks ==")
    nslots, w2 = mine_slot_ram(banks)
    print(f"slots scanned={nslots}  witnesses={len(w2)}")
    for r in w2[:40]:
        print("  ", r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
