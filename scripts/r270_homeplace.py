#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t270: HOME-PLACEMENT VERIFICATION (OQ-016 residue; offline). KEEPER.

Questions (STATE.md t270 assignment):
 (a) where do the 7 home stars sit relative to the T=50 shell structure
     (slot, radius, shell index, min inter-home distance)?
 (b) run-local random or template-fixed — home STAR identity across
     independent lineages (fresh r1ad/r1deep sessions vs production).
 (c) vendor resume.gam static-init signature re-read (7 owners 0..6).

Laws (cited):
  * OQ-011 pointer law: member = phys + H, H = B - 0x1BF450; guest linear ==
    physical; data-seg X at member B + 0x82bb0 + X.
  * Star record (r1-savestate.md): base(k) = NAME(k) - 0x1C, stride 0x60;
    name @ base+0x1C; idx u32 @ base+0x4 (name-0x18); pos f32[3] @ base+0x8
    (name-0x14); owner bitmask byte @ base+0x30 (name+0x14); planet ptrs u32[5]
    @ base+0x46 (name+0x2A), target = planet NAME phys - 0x24, LIVE iff name
    prefix == star name.
  * HOME STAR POINTER: DWORD[data 0x12e1d + race*0x1ee] == phys of the home
    star's FIRST PLANET-POINTER SLOT == base(k)+0x60 == NAME(k)+0x44
    [MEASURED t270: remainder (ptr-(NAME0+0x44)) % 0x60 == 0 in every slot
    for every participating race; the race's own planet (NAME+0x33 == race)
    is inside record k's LIVE list in 25/25 t<=2 observations -> home == k.
    ptr == 0 -> race not in game.]
  * Planet owner byte NAME+0x33 (t248); resume.gam static init exactly 7
    records owners 0..6 (t248 PROOF 4).
  * Shell law T=50 (OQ-012/025 CLOSED): radii 440/365/290/215/140/65/50 by
    slot runs 26/12/6/3/1/1/1; radius = hypot(x,y,z).

OOM LAW: one slot inflated at a time. Exit 0 = ran with findings.
"""
import os, re, struct, sys, zipfile, math, glob, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_slot as S

OFF = 0x82bb0
STRIDE_S, STRIDE_P = 96, 123
SNAME_RE = rb"[A-Z][a-z]{2,15}\x00"
PNAME_RE = rb"[A-Z][A-Za-z]{2,}(?: [IVX]+)?\x00"
SHELLS = [440, 365, 290, 215, 140, 65, 50]
NAME_HINT = 0x255be1     # NAME(0) phys (run 230146; hint only)
PLANET_HINT = 0x26d07b   # planet NAME(0) phys (hint, verified per-slot)


def chain(mem, H):
    best, k0 = [], None
    for d in range(0x21):
        for sign in (-1, 1):
            p = NAME_HINT + sign * d
            names, k = [], 0
            while k <= 60:
                m = re.match(SNAME_RE, mem[p + H + k * STRIDE_S:p + H + k * STRIDE_S + 18])
                if not m:
                    break
                names.append(m.group()[:-1].decode())
                k += 1
            if len(names) > len(best):
                best, k0 = names, p
    return k0, best


def shell_of(r):
    best, bd = None, None
    for i, rad in enumerate(SHELLS):
        d = abs(r - rad)
        if bd is None or d < bd:
            best, bd = i, d
    return best, bd


def analyze(path, label, quiet=False):
    try:
        mem = zipfile.ZipFile(path).read("Memory")
    except Exception as e:
        print(f"[{label}] UNREADABLE {e}")
        return None
    pay = S.load_payload("."); anch = S.anchors_cached(".", pay)
    B = S.base_of(mem, anch)
    if B is None:
        return None
    H = B - 0x1BF450
    turn = struct.unpack_from("<I", mem, B + OFF + 0x12e10)[0]
    T = struct.unpack_from("<H", mem, B + OFF + 0x16145)[0]
    if turn == 0:
        # TRUST LAW t270: at turn 0 the race-row home pointers are template
        # RESIDUE (identical garbage across fresh runs; t269 found ALL T/
        # selector anomalies are turn-0 frames too). Homes only become true
        # game state at turn >= 1.
        return None
    k0, names = chain(mem, H)
    if len(names) < 45 or k0 is None:
        return None

    def base(k):
        return k0 + k * STRIDE_S - 0x1C
    def pos(k):
        return struct.unpack_from("<3f", mem, base(k) + 0x8 + H)
    def own(k):
        # OWNER BYTE at name-0x8 (== base+0x14; t246 disasm BYTE[eax+0x14]
        # indexes from the RECORD BASE, consistent with t248 PROOF 1).
        # MEASURED r270 (prefix-filtered live-planet OR): (byte & 0x7f) ==
        # (OR(1<<owner) & 0x7f) 50/50 bank-t1254/48.sav (bit7 = separate
        # flag; fresh runs show a race-7 planet setting OR bit7 -> the mask).
        return mem[base(k) + 0x14 + H]
    def live_planets(k):
        out = []
        sn = names[k]
        for i in range(5):
            v = struct.unpack_from("<I", mem, base(k) + 0x46 + 4 * i + H)[0]
            oo = v - ((PLANET_HINT - 0x24) & 0xFFFFFFFF)
            if not (0 <= oo < 400 * STRIDE_P) or oo % STRIDE_P:
                continue
            j = oo // STRIDE_P
            p = PLANET_HINT + j * STRIDE_P + H
            z = mem[p:p + 30].find(b"\x00")
            if not (0 <= z <= 25):
                continue
            pn = mem[p:p + z].decode("ascii", "replace")
            if pn.rsplit(" ", 1)[0] != sn:
                continue
            out.append((pn, mem[p + 0x33]))
        return out

    homes = []
    for r in range(8):
        ptr = struct.unpack_from("<I", mem, B + OFF + 0x12e1d + r * 0x1ee)[0]
        h = {"race": r, "ptr": ptr, "k": None, "star": None, "radius": None,
             "shell": None, "home_planet": None, "orbit_idx": None,
             "star_ownbyte": None}
        if ptr:
            # HOME JOIN (t270 MEASURED): ptr == base(k) EXACTLY where
            # base(k) = NAME(k) - 0x1C. (The record-0 base equals k0 - 0x1C.)
            rel = ptr - (k0 - 0x1C)
            if rel >= 0 and rel % STRIDE_S == 0:
                k = rel // STRIDE_S
                if k < min(T, len(names)):
                    h["k"] = k
                    h["star"] = names[k]
                    h["star_ownbyte"] = own(k)
                    x, y, z = pos(k)
                    h["radius"] = round(math.sqrt(x * x + y * y + z * z), 1)
                    h["shell"], _ = shell_of(h["radius"])
                    lp = live_planets(k)
                    mine = [p for p in lp if p[1] == r]
                    if mine:
                        h["home_planet"] = mine[0][0]
                        h["orbit_idx"] = mine[0][0].rsplit(" ", 1)[1]
        homes.append(h)

    part = [h for h in homes
            if h["k"] is not None and (h["star_ownbyte"] >> h["race"]) & 1]
    skipped = [h["race"] for h in homes
               if h["k"] is not None and not (h["star_ownbyte"] >> h["race"]) & 1]
    md, pair = None, None
    for i in range(len(part)):
        for j in range(i + 1, len(part)):
            d = math.dist(pos(part[i]["k"]), pos(part[j]["k"]))
            if md is None or d < md:
                md, pair = d, (part[i]["race"], part[j]["race"])
    out = {"label": label, "turn": turn, "T": T, "homes": part,
           "min_inter_home": (round(md, 1), pair) if md else None}
    if not quiet:
        print(f"[{label}] t={turn} T={T} n_home={len(part)} "
              f"min_inter_home={out['min_inter_home']}")
        for h in part:
            print(f"    race{h['race']}: k={h['k']} {h['star']} "
                  f"r={h['radius']} shell={h['shell']} ownbyte={hex(h['star_ownbyte'])} "
                  f"home_planet={h['home_planet']} (orbit {h['orbit_idx']})")
    return out


def resume_gam():
    """(c) vendor static-init signature re-read (t248 PROOF 4 method)."""
    raw = open("game/resume.gam", "rb").read()
    hits = [m.start() for m in re.finditer(PNAME_RE, raw)]
    hs = set(hits)
    best, run = None, 0
    for h in hits:
        n, p = 0, h
        while p in hs:
            n += 1; p += STRIDE_P
        if n > run:
            best, run = h, n
    if best is None:
        print("[resume.gam] planet run not found")
        return None
    while (best - STRIDE_P) in hs and (best - 2 * STRIDE_P) in hs:
        best -= STRIDE_P
    cens, homes = collections.Counter(), []
    j = 0
    for j in range(400):
        p = best + j * STRIDE_P
        m = re.match(PNAME_RE, raw[p:p + 40])
        if not m:
            break
        o = raw[p + 0x33]
        cens[o] += 1
        if o < 7:
            homes.append((o, m.group()[:-1].decode()))
    print(f"[resume.gam] base {hex(best)} recs={j} owner_hist={dict(cens)}")
    print(f"    home planets (owner<7): {homes}")
    # orbit radii of the 7 template homes (galacto-centric orbit law)
    for o, nm in homes:
        j = next(jj for jj in range(400)
                 if raw[best + jj * STRIDE_P:best + jj * STRIDE_P + 40].startswith(nm.encode()))
        ox, oy = struct.unpack_from("<2f", raw, best + j * STRIDE_P + 0x57)
        print(f"      r{o} {nm}: orbit radius {round(math.sqrt(ox*ox+oy*oy),1)}")
    return {"label": "resume.gam", "homes": None, "owner_hist": dict(cens),
            "home_planets": homes}


def main():
    targets = [
        ("prod-t1254", "work/r1/bank-t1254/48.sav"),
        ("prod-t249open", "work/r1/bank-t249-live-open/60.sav"),
        ("prod-t251predrive", "work/r1/bank-t251-predrive/41.sav"),
        ("prod-t1236", "work/r1/bank-t261-final-1236/41.sav"),
    ]
    # independent lineages: earliest slot with turn>=1 per run (t=0 rows are
    # template residue per the trust law above)
    for run in sorted(glob.glob("work/r1/r1deep-*") + glob.glob("work/r1/r1ad-*")):
        sd = os.path.join(run, "save")
        if not os.path.isdir(sd):
            continue
        files = sorted(glob.glob(sd + "/*.sav"), key=lambda f: os.stat(f).st_mtime)
        pick = None
        for f in files:
            try:
                mem = zipfile.ZipFile(f).read("Memory")
                Bv = S.base_of(mem, S.anchors_cached(".", S.load_payload(".")))
                if Bv is None:
                    continue
                if struct.unpack_from("<I", mem, Bv + OFF + 0x12e10)[0] >= 1:
                    pick = f
                    break
            except Exception:
                continue
        if pick:
            targets.append((os.path.basename(run), pick))
    res = []
    for label, path in targets:
        r = analyze(path, label)
        if r:
            res.append(r)
    resume_gam()

    print("\n=== (a) HOME SLOT / SHELL DISTRIBUTION (per home record) ===")
    slot_hist = collections.Counter()
    shell_hist = collections.Counter()
    mins = []
    for r in res:
        for h in r["homes"]:
            slot_hist[h["k"]] += 1
            shell_hist[h["shell"]] += 1
        if r["min_inter_home"]:
            mins.append(r["min_inter_home"][0])
    print("slot hist:", dict(sorted(slot_hist.items())))
    print("shell hist (0=r440..6=r50):", dict(sorted(shell_hist.items())))
    if mins:
        mins.sort()
        print(f"min inter-home dist over {len(mins)} lineages: "
              f"min={mins[0]} p25={mins[len(mins)//4]} median={mins[len(mins)//2]} max={mins[-1]}")

    print("\n=== (b) CROSS-LINEAGE HOME STAR SETS ===")
    byset = collections.defaultdict(list)
    for r in res:
        if not r["homes"]:
            continue
        key = tuple((h["race"], h["star"], h["k"]) for h in r["homes"])
        byset[key].append(r["label"])
    for key, labs in byset.items():
        print(f"set ({len(labs)}): {list(key)[:3]}... {labs}")
    print(f"DISTINCT SETS: {len(byset)} over {len(res)} analysable slots")
    # per-race star-name diversity
    names_by_race = collections.defaultdict(set)
    ks_by_race = collections.defaultdict(list)
    for r in res:
        for h in r["homes"]:
            names_by_race[h["race"]].add(h["star"])
            ks_by_race[h["race"]].append(h["k"])
    for r_ in sorted(names_by_race):
        print(f"race{r_}: {len(names_by_race[r_])} distinct home stars, "
              f"slots {sorted(ks_by_race[r_])}")

if __name__ == "__main__":
    main()
