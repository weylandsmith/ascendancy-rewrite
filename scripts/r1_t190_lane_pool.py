#!/usr/bin/env python3
"""t190: LANE POOL STRUCT + byte+0x23 census in saves (OQ-019 residue).

Static law banked this session (disasm citations in docs/re/_wip_t190.md):
  adjacency/HOP matrix = image 0x45beb (byte, 100-linear; FUN_0002351c
    zeroes then sets pair=1 per AUTHORED 39-byte lane record then BFS-fills
    hop distances 2,3,...; diagonal set 1 by FUN_00023e00 0x23e3a).
  star count u16 = image 0x16145; star slot objects img 0x13bc5 stride 0x60.
  LANE POOL = image 0x16147 stride 0x27=39, cap 148 (guard 0x2485f):
    rec[0]=star-A obj ptr, rec[4]=star-B obj ptr (0x248af/0x248b1),
    rec+0x20 byte zeroed at alloc (0x248ab); byte +0x23 NEVER initialized by
    the allocator; bit0 set ONLY at 0x247f7 (FUN_0002446c creator), read by
    the march gate 0x4a842 (x1/3 multiplier).
  lane count u16 = image 0x177D3 (=0x12e10+0x49c3 folded; cap-guard counter
    image 0x177D1 = 0x12e10+0x49c1 holds the AUTHORED count in phase 1).
  species gate-2 table: byte[image 0x12fb3 + idx*0x1ee + 0x12] == 0x12 -> x2
    (0x4a867: EAX = idx*247, CMP byte[EAX*2 + 0x12fb3]).
MEMBER LAW (OQ-014 corollary): member = B + 0x82bb0 + X; physical = member-88.
Ship rows B+0x82bb0+0x3a095 stride 0x162 bytes == the 177-u16 word repack
(0x162 = 2*177), so t189 byte offsets apply directly: state byte 0x58, lane
handle u32 at byte 0x59 (unaligned).
Exit 0 = sane window in >=1 save; 1 = negative.
"""
import os, sys, struct, zipfile, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = os.path.join(ROOT, "work", "r1", "playcap")
PAY = os.path.join(ROOT, "work", "ascend_payload.bin")
D = 0x82BB0
IMG_MATRIX, IMG_COUNT = 0x45BEB, 0x16145
IMG_POOL, IMG_NLANES, IMG_NAUTH = 0x16147, 0x177D3, 0x177D1
CAP = 148
IMG_SPECIES, SPECIES_STRIDE = 0x12FB3, 0x1EE
STRIDE = 0x27


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
    ok_saves = 0
    for p in saves():
        try:
            mem = zipfile.ZipFile(p).read("Memory")
        except Exception as e:
            print(f"{os.path.basename(p)}: unreadable {e}")
            continue
        votes, _ = find_base(mem, anch)
        if not votes:
            continue
        B = votes.most_common(1)[0][0]
        n = struct.unpack_from("<H", mem, B + D + IMG_COUNT)[0]
        win = mem[B + D + IMG_MATRIX: B + D + IMG_MATRIX + 100 * 100]
        sym = (sum(1 for i in range(n) for j in range(n)
                   if win[i * 100 + j] != win[j * 100 + i])
               if 0 < n <= 100 else -1)
        sane = 0 < n <= 100 and sym == 0
        print(f"-- {os.path.basename(p)}: B=0x{B:x} star_count={n} sym_viol={sym}")
        if not sane:
            continue
        ok_saves += 1
        vals = collections.Counter(win[: n * n])
        le12 = sum(v for k, v in vals.items() if k <= 12)
        print(f"   matrix: zeros:{vals.get(0, 0)} dist1:{vals.get(1, 0)}"
              f" dist2:{vals.get(2, 0)} n<=12:{le12}"
              f" 0xFF:{vals.get(255, 0)} other:{n * n - le12 - vals.get(255, 0)}")
        nl = struct.unpack_from("<H", mem, B + D + IMG_NLANES)[0]
        na = struct.unpack_from("<H", mem, B + D + IMG_NAUTH)[0]
        pool_off = B + D + IMG_POOL
        pool = mem[pool_off: pool_off + CAP * STRIDE]
        pool_lo, pool_hi = pool_off - 0x88, pool_off + CAP * STRIDE - 0x88
        walk = min(CAP, max(nl, 1))
        b23 = collections.Counter()
        nonz = inpool = 0
        flagged = []
        for i in range(walk):
            r = pool[i * STRIDE:(i + 1) * STRIDE]
            if len(r) < STRIDE:
                break
            a, b = struct.unpack_from("<II", r, 0)
            b23[r[0x23]] += 1
            if a or b:
                nonz += 1
            if pool_lo <= a < pool_hi or pool_lo <= b < pool_hi:
                inpool += 1
            if r[0x23] & 1:
                flagged.append(i)
        print(f"   nlanes(u16@0x177D3)={nl} nauth?(0x177D1)={na}"
              f" walked={walk} nonzero_recs={nonz} into-pool-ptrs={inpool}")
        print(f"   +0x23 CENSUS ({walk} recs): {dict(sorted(b23.items()))}")
        if flagged:
            print(f"   FLAG1 recs (first 20): {flagged[:20]}")
        for i in list(range(min(walk, 5))) + flagged[:5]:
            r = pool[i * STRIDE:(i + 1) * STRIDE]
            a, b = struct.unpack_from("<II", r, 0)
            ai = (a - pool_off + 0x88) // STRIDE if pool_lo <= a < pool_hi else None
            print(f"     rec{i:3d} a=0x{a:08x}{'#' + str(ai) if ai is not None else ''}"
                  f" b=0x{b:08x} +0x20={r[0x20]} +0x23=0x{r[0x23]:02x}")
        # species gate-2 column (24 rows)
        sp = mem[B + D + IMG_SPECIES: B + D + IMG_SPECIES + 24 * SPECIES_STRIDE + 0x120]
        col = collections.Counter(sp[k * SPECIES_STRIDE + 0x12]
                                  for k in range(24)
                                  if (k + 1) * SPECIES_STRIDE + 0x13 <= len(sp))
        print(f"   species col0x12 rows0..23: {dict(sorted(col.items()))}"
              f" hits0x12={col.get(0x12, 0)}")
        # ship st5 handles vs pool
        shb = B + D + 0x3A095
        nships = min(struct.unpack_from("<I", mem, B + D + 0x43489)[0] >> 16, 0x6B)
        amb = collections.Counter()
        shown = 0
        for k in range(nships):
            rec = mem[shb + k * 0x162: shb + (k + 1) * 0x162]
            if len(rec) < 0x162 or rec[0x58] != 5:
                continue
            h = struct.unpack_from("<I", rec, 0x59)[0]
            if pool_lo <= h < pool_hi:
                tag = "pool"
                if shown < 12:
                    print(f"     ship{k:02d} st5 h=0x{h:08x} recidx="
                          f"{(h - pool_off + 0x88) // STRIDE}"
                          f" mod39={(h - pool_off + 0x88) % STRIDE}"
                          f" b23=0x{pool[(h - pool_off + 0x88) // STRIDE * STRIDE + 0x23]:02x}"
                          if (h - pool_off + 0x88) // STRIDE < walk else
                          f"     ship{k:02d} st5 h=0x{h:08x} recidx="
                          f"{(h - pool_off + 0x88) // STRIDE} (beyond walk)")
                    shown += 1
            elif 0x200000 <= h < 0xA00000:
                tag = "ram-other"
            else:
                tag = "bogus"
            amb[tag] += 1
        print(f"   ships={nships} st5 handle classes: {dict(amb)}")
    print(f"\nsane_saves={ok_saves}")
    return 0 if ok_saves else 1


if __name__ == "__main__":
    sys.exit(main())
