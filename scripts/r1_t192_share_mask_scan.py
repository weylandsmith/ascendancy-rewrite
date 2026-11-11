#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t192 (rev2): MEASURE lane/star visibility share residues in real saves.

Addressing conventions (empirically re-verified this session on 60.sav,
mem[B+D+X] is the loop convention -- r1_playcap_watch.py:82 M = B + S.OFF,
S.OFF = 0x82bb0 = D; mem[B+D+0x74590] is the validated race-name table, so
mem[B+D+X] for any Ghidra image X):
  CURRENT PLAYER INDEX  X = 0x7458e
  PAIRED MASK BYTE      Ghidra X = 0x89324  (payload stores imm 0x6774;
                        0x89324-0x82bb0 == 0x6774) -- BOTH candidate offsets
                        are read here because the two conventions differ for
                        X >= 0x82bb0; the census decides which tracks 1<<idx.
  DIPLO ROW BASE        X = 0x12e16 + 0x1ee*idx  (row+0x00 = own empire idx)
  SUB-OBJECT PTR        X = 0x12e1d + 0x1ee*idx  (asm 0x22e3b/0x22e41 read
                        [ESI+0xd] with ESI = 0x12e10 + 0x1ee*idx; verified:
                        60.sav row0 holds 0x002563a5 at row+0x07)
  SUB COUNT             u16 [sub + 0x44]         (0x2205b / 0x22e7a)
  SUB REC LIST          u32 [sub + 0x2c + 4*i]    (0x2206e / 0x22e5a / 0x22f1d)
  ENDPOINT OBJ PTRS     u32 [rec + 0] , [rec + 4] (lane allocator 0x248af/81)
  LANE POOL             X = 0x16147 stride 0x27, count u16 X = 0x177d3
  STAR SLOT BASE        X = 0x13bc5 stride 0x60, count u16 X = 0x16145
Pointers in the blob are GUEST-PHYSICAL: blob_offset = ptr - 88 (t190 law,
r1_t190_lane_pool.py: recidx = (h - pool_off + 0x88) // 39), so every pointer
read here is converted with PTR2OFF = lambda p: ptr - 0x88 before indexing.
"""
import os, sys, struct, zipfile, collections
sys.path.insert(0, "/home/hrethric/projects/ascendancy/scripts")
from r1_sav_scan import build_anchors, find_base

ROOT = "/home/hrethric/projects/ascendancy"
RUN = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "work/r1/playcap")
PAY = os.path.join(ROOT, "work/ascend_payload.bin")
D = 0x82BB0
PHYS = 0x88                   # blob_offset = guest_phys + 0x88 (t190:
#   pool_lo = pool_off - 0x88, recidx = (h - pool_off + 0x88)//39)
X_CUR = 0x7458E
X_PAIR_ABS, X_PAIR_IMM = 0x89324, 0x89324 - D
X_ROW, STRIDE_ROW = 0x12E16, 0x1EE
X_SUBPTR = 0x12E1D
X_POOL, S_POOL = 0x16147, 0x27
X_NLANES, X_NSTAR, X_NRACES = 0x177D3, 0x16145, 0x13B98
S_STAR = 0x60
X_STAR_MASK_FIELD = 0x16          # star obj +0x16/+0x17 (FUN_00046524)


def saves():
    for d in ("save", "ck"):
        sd = os.path.join(RUN, d)
        if os.path.isdir(sd):
            for f in sorted(os.listdir(sd)):
                if f.endswith(".sav"):
                    yield os.path.join(sd, f)


def main():
    pay = open(PAY, "rb").read()
    anch = build_anchors(pay)
    ns = 0
    c_abs = collections.Counter()
    c_imm = collections.Counter()
    rows = []
    lane_hits = star_hits = neither = 0
    mod_hist = collections.Counter()
    samples = []
    subcnt = collections.Counter()
    for p in saves():
        try:
            mem = zipfile.ZipFile(p).read("Memory")
        except Exception:
            continue
        votes, _ = find_base(mem, anch)
        if not votes:
            continue
        B = votes.most_common(1)[0][0]
        M = B + D
        ns += 1
        idx = mem[M + X_CUR]
        pa = mem[M + X_PAIR_ABS] if M + X_PAIR_ABS < len(mem) else None
        pi = mem[M + X_PAIR_IMM]
        exp = 0x00 if idx >= 0x20 else (1 << idx)
        c_abs[(idx, pa, exp, pa == exp)] += 1
        c_imm[(idx, pi, exp, pi == exp)] += 1
        nr = struct.unpack_from("<H", mem, M + X_NRACES)[0]
        nlane = struct.unpack_from("<H", mem, M + X_NLANES)[0]
        nstar = struct.unpack_from("<H", mem, M + X_NSTAR)[0]
        pool_base = M + X_POOL
        star_base = M + 0x13BC5
        recs = 0
        for r in range(min(nr, 24)):
            sub_phys = struct.unpack_from("<I", mem, M + X_SUBPTR + STRIDE_ROW * r)[0]
            sub = sub_phys + PHYS
            if not (0x1000 < sub < len(mem) - 0x900):
                continue
            cnt = struct.unpack_from("<H", mem, sub + 0x44)[0]
            subcnt[cnt] += 1
            recs += 1
            for i in range(min(cnt, 400)):
                rec_phys = struct.unpack_from("<I", mem, sub + 0x2C + 4 * i)[0]
                rec = rec_phys + PHYS
                if rec_phys == 0 or not (0x1000 < rec < len(mem) - 8):
                    continue
                dL, dS = rec - pool_base, rec - star_base
                is_lane = dL >= 0 and dL % S_POOL == 0 and dL // S_POOL < max(nlane, 1)
                is_star = dS >= 0 and dS % S_STAR == 0 and dS // S_STAR < max(nstar, 1)
                mod_hist[(dL % 39) if dL >= 0 else -1] += 1
                if is_lane:
                    lane_hits += 1
                elif is_star:
                    star_hits += 1
                else:
                    neither += 1
                    if len(samples) < 10:
                        samples.append(f"{os.path.basename(p)} r={r} i={i} "
                                       f"rec=0x{rec_phys:x} dLane={dL}(m39={dL%39}) "
                                       f"dStar={dS}(m96={dS%96})")
        rows.append(f"{os.path.basename(p)} B=0x{B:x} idx={idx} pair_imm=0x{pi:02x} "
                    f"pair_abs={'-' if pa is None else hex(pa)} nr={nr} nlanes={nlane} "
                    f"nstar={nstar} subs={recs}")
    print(f"saves={ns}")
    print("== LEG C: paired mask byte census (idx, value, expected 1<<idx, match) ==")
    print("  at B+D+0x89324 (Ghidra image addr): " +
          ", ".join(f"idx{i}:0x{v:02x}/exp0x{e:02x}{'=' if m else '!'}x{n}"
                    for (i, v, e, m), n in sorted(c_abs.items())))
    print("  at B+D+0x6774  (payload imm addr):  " +
          ", ".join(f"idx{i}:0x{v:02x}/exp0x{e:02x}{'=' if m else '!'}x{n}"
                    for (i, v, e, m), n in sorted(c_imm.items())))
    print("\n== LEG B: [sub+0x2c+4*i] classification ==")
    print(f"  lane_pool_congruent={lane_hits}  star_slot_congruent={star_hits}  "
          f"neither={neither}")
    print("  mod39 histogram (dLane): " +
          ", ".join(f"{k}:{v}" for k, v in sorted(mod_hist.items())[:15]))
    print("  sub count word[sub+0x44] values: " +
          ", ".join(f"{k}x{v}" for k, v in sorted(subcnt.items())[:15]))
    for s in samples:
        print("  " + s)
    print("\nper-save:")
    for r in rows:
        print("  " + r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
