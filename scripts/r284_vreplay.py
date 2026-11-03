#!/usr/bin/env python3
"""r284_vreplay.py — REPLAY the decoded producer FUN_00024274 against real saves.

The law being replayed (Ghidra FUN_00024274 + FUN_00024f24 tail, cross-checked
instruction-for-instruction against objdump of work/ascend_payload.bin; full
write-up docs/re/_wip_t284.md):

    V = 0
    if (home(player)->m14 >> playerIdx) & 1:        # race-record +7 ptr = HOME STAR
        V = 1
        allied = { r : rel[player][r] == 3 }        # 3 = ALLIANCE (OQ-023 CLOSED)
        flood(home):
          for lane in star.laneList (star+0x2c, count star+0x44):
            if lane.mark: continue
            far = lane.ep0 if lane.ep0 != star else lane.ep1
            if (far.m17 >> playerIdx) & 1 and ((m14| m15) & ~(allied|1<<player) & 0x7f) == 0:
                if no live ship has (+0x59 == lane and owner != player
                                    and rel[player][owner] != 3):
                    lane.mark = 1 ; V += 1 ; flood(far)

Pointer convention (THE 0x88 trap, docs/BLOCKED.md + score.md S2): a stored u32
pointer decodes as X = p - (B - 0x88 + 0x82bb0), while DIRECT data reads use
mem[B + 0x82bb0 + X]. Verified here per-save by the star self-handle law
(dword[star+2] >> 16 == star index, t205 20/20).

Validation per save: predicted V vs stored u32[0x482fb], and the predicted
visited-lane set vs the save's lane pool +0x21 marks (the pass clears all marks
at the start of the end-turn pass, so the replay starts from marks=0).

Saves captured DURING the ~3 s recompute window legitimately read low (partial
accumulation) — report them, don't call them failures. Exit 0 ran, 1 no data.
"""
import os, struct, sys, glob, zipfile, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_slot as SL

ROOT = "/home/hrethric/projects/ascendancy"
OFF = 0x82bb0
H = 0x88

X_PLAYER = 0x7458e
X_RACEC = 0x13b98
X_RELBASE = 0x12fd6
X_STARS = 0x13bc5
X_STARC = 0x16145
X_LANES = 0x16147
X_LANEC = 0x177d3
X_SHIPS = 0x3a095
X_SHIPC = 0x43489
X_V = 0x482fb
X_HOME = 0x12e1d
STAR_S, LANE_S, SHIP_S, RACE_S = 0x60, 0x27, 0x162, 0x1ee


class S:
    def __init__(self, mem, B):
        self.mem, self.B = mem, B
        self.d = B + OFF          # direct-read base
        self.p = B - H + OFF      # pointer-decode base

    def u8(self, X):  return self.mem[self.d + X]
    def u16(self, X): return struct.unpack_from("<H", self.mem, self.d + X)[0]
    def u32(self, X): return struct.unpack_from("<I", self.mem, self.d + X)[0]

    def ptrX(self, p):
        """Decode a stored u32 pointer to a data offset X, or None."""
        if p == 0:
            return None
        X = p - self.p
        return X if 0 <= X < 0x8cc83 else None

    def idx(self, p, base, stride):
        X = self.ptrX(p)
        if X is None or X < base:
            return None
        if (X - base) % stride:
            return None
        return (X - base) // stride

    def ship(self, k):
        r = self.d + X_SHIPS + k * SHIP_S
        return dict(owner=struct.unpack_from("<I", self.mem, r + 0x54)[0] >> 16,
                    kind=self.mem[r + 0x58],
                    tgt=struct.unpack_from("<I", self.mem, r + 0x59)[0])

    def lane(self, i):
        r = self.d + X_LANES + i * LANE_S
        return dict(ep0=struct.unpack_from("<I", self.mem, r)[0],
                    ep1=struct.unpack_from("<I", self.mem, r + 4)[0],
                    mask=self.mem[r + 0x20],
                    mark=struct.unpack_from("<H", self.mem, r + 0x21)[0])

    def star(self, i):
        r = self.d + X_STARS + i * STAR_S
        return dict(m14=self.mem[r + 0x14], m15=self.mem[r + 0x15],
                    m16=self.mem[r + 0x16], m17=self.mem[r + 0x17],
                    selfh=struct.unpack_from("<I", self.mem, r + 2)[0] >> 16,
                    nlane=struct.unpack_from("<H", self.mem, r + 0x44)[0],
                    lanes=[struct.unpack_from("<I", self.mem, r + 0x2c + 4 * j)[0]
                           for j in range(min(struct.unpack_from("<H", self.mem, r + 0x44)[0], 64))])

    def rel(self, a, b):
        return self.mem[self.d + X_RELBASE + a * RACE_S + b]


def replay(s, verbose_marks=False):
    """Returns (predicted_V, visited_lane_set, note)."""
    pl = s.u8(X_PLAYER)
    nrace = s.u16(X_RACEC)
    nlanes = s.u16(X_LANEC)
    nships = s.u32(X_SHIPC) >> 16
    home_i = s.idx(s.u32(X_HOME + pl * RACE_S), X_STARS, STAR_S)
    if home_i is None:
        return None, set(), "home ptr not star-congruent"
    home = s.star(home_i)
    if not (home["m14"] >> pl) & 1:
        return 0, set(), "home m14 bit clear"
    allied = 0
    for r in range(nrace):
        if s.rel(pl, r) == 3:
            allied |= 1 << r
    allowed = allied | (1 << pl)
    ships = [s.ship(k) for k in range(min(nships if nships else 0x6b, 0x6b))]
    # NOTE: the original's inner loop scans ALL 0x6b slots and counts live ones;
    # scanning the live prefix is equivalent for the qualify test (seen>=live).
    live = [sh for sh in ships if sh["owner"] != 0xffffffff]

    visited = set()

    def flood(star_i, depth=0):
        if depth > 200:
            return
        st = s.star(star_i)
        for p in st["lanes"]:
            li = s.idx(p, X_LANES, LANE_S)
            if li is None or li in visited:
                continue
            ln = s.lane(li)
            far_i = s.idx(ln["ep0"], X_STARS, STAR_S)
            if far_i == star_i:
                far_i = s.idx(ln["ep1"], X_STARS, STAR_S)
            if far_i is None:
                continue
            far = s.star(far_i)
            if not (far["m17"] >> pl) & 1:
                continue
            if ((far["m14"] | far["m15"]) & ~allowed & 0x7f) != 0:
                continue
            contested = any(sh["tgt"] == p and sh["owner"] != pl and s.rel(pl, sh["owner"]) != 3
                            for sh in live)
            if contested:
                continue
            visited.add(li)
            flood(far_i, depth + 1)

    flood(home_i)
    return 1 + len(visited), visited, f"pl={pl} nrace={nrace} live={len(live)} nlanes={nlanes}"


def main():
    dirs = sys.argv[1:]
    if not dirs:
        dirs = sorted(glob.glob(os.path.join(ROOT, "work/r1/*/save")), key=os.path.getmtime)
    tot = collections.Counter()
    rows = []
    for d in dirs:
        for path in sorted(glob.glob(os.path.join(d, "*.sav")), key=os.path.getmtime):
            try:
                mem = zipfile.ZipFile(path).read("Memory")
            except Exception:
                continue
            if len(mem) < 0x90000:
                continue
            B = SL.base_of(mem, SL.anchors_cached(ROOT, SL.load_payload(ROOT)))
            if B is None:
                continue
            s = S(mem, B)
            turn = s.u32(0x12e10)
            V = s.u32(X_V)
            if turn == 0 and V == 0:
                continue                      # title slot
            pred, vis, note = replay(s)
            if pred is None:
                tot["replay-inapplicable"] += 1
                continue
            # lane +0x21 marks present in the save (the pass's own footprint)
            marks = {i for i in range(min(s.u16(X_LANEC), 200)) if s.lane(i)["mark"]}
            agree = "EXACT" if pred == V else ("partial" if V < pred else "V>PRED")
            tot[agree] += 1
            rows.append((os.path.relpath(path, ROOT), turn, V, pred, len(vis),
                         len(marks), len(marks - vis), len(vis - marks), note))
    print(f"{'save':52s} {'t':>5s} {'V':>3s} {'pred':>4s} {'vis':>4s} {'mk':>4s} "
          f"{'mk-vis':>6s} {'vis-mk':>6s}  note")
    for r in rows:
        print(f"{r[0]:52s} {r[1]:5d} {r[2]:3d} {r[3]:4d} {r[4]:4d} {r[5]:4d} "
              f"{r[6]:6d} {r[7]:6d}  {r[8]}")
    print(f"\nTOTALS {dict(tot)}  (n={len(rows)})")
    ex = [r for r in rows if r[2] == r[3] and r[2] > 1]
    print(f"EXACT-and-nonzero: {len(ex)}")
    for r in ex[:12]:
        print("   ", r)
    return 0 if rows else 1


if __name__ == "__main__":
    raise SystemExit(main())
