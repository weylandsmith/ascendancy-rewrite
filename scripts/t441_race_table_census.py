#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t441 OFFLINE CENSUS — seams T436-A (species-screen portrait COUNT) and
T436-B (owner -> racering ring INDEX). Zero capture, read-only.

Law stack (cited, not re-derived):
  - DS-seg linear M = B + 0x82bb0 (t340 / r1_slot.OFF); campaign STATE = M +
    0x12e10, dword[STATE] = turn clock (docs/re/_wip_t295.md S4).
  - race rows row_r = STATE + 0x1ee*r, count = word[STATE+0xd88] (t295 S4:163);
    +7 = specnum (t415 F3 FUN_00023388 preload), +8 = colour index 0..7
    (t423-newgame-law.md S10 FUN_000232ec), +0xd = home-star POINTER (0x22edd).
  - race name = DS + 0x74590 + specnum*0x14 (scripts/r1_playcap_watch.py
    `relation`, the production watcher law).

STAR RECORD MAP [MEASURED t441, bank-t251-live1255/45.sav, pointer-anchored so
it cannot drift with the base]: P = the dword at row+0xd (t295's home-star
pointer). Then
    P+0x2c  dword  sequential star index 0..T-1   (self-describing)
    P+0x30  float  map x        P+0x34 float map y
    P+0x3c  byte   bit7 home marker | (1<<race)   (= t295's entry+0x14: t295's
                     "ebp = state+0xdb5" is P+0x28, i.e. the doc's entry base is
                     0x28 ABOVE the pointer value the code stores)
    P+0x3e  byte   per-star bitset (duplicated at +0x3f)
    P+0x44  20 B   star name
  => star record base = STATE + 0xd8d + 0x60*j; the stride-0x60 name run t295
  found at STATE+0xdb5 starts at this base + 0x28.
"""
import os, struct, sys, glob, zipfile, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r1_slot as S

ROOT = os.path.abspath(os.path.join(HERE, ".."))
OFF = S.OFF
NBAR = 0x74590
RING_HUE = {0: "green", 1: "purple", 2: "gold", 3: "pink", 4: "tan",
            5: "blue", 6: "orange", 7: "NEUTRAL-grey"}


def decode_stars(mem, STATE, T):
    """Star records indexed by their own +0x2c value."""
    out = {}
    for j in range(T):
        p = STATE + 0xd8d + 0x60 * j
        idx = struct.unpack_from("<I", mem, p + 0x2c)[0]
        if idx >= 512:
            continue
        x, y = struct.unpack_from("<ff", mem, p + 0x30)
        out[idx] = dict(ptr=p, seq=j, name=mem[p + 0x44:p + 0x58]
                        .split(b"\x00")[0].decode("latin-1", "replace"),
                        x=x, y=y, marker=mem[p + 0x3c], bits=mem[p + 0x3e])
    return out


def census(mem, B, path):
    M = B + OFF
    STATE = M + 0x12e10
    turn = struct.unpack_from("<I", mem, STATE)[0]
    n = struct.unpack_from("<H", mem, STATE + 0xd88)[0]
    T = struct.unpack_from("<I", mem, STATE + 0x3333)[0] >> 16
    st = decode_stars(mem, STATE, min(T, 255) if T else 0)
    ships = collections.Counter()
    try:
        base, nsh = S.ship_array_law(mem, B)
        for k in range(min(nsh, 0x6b)):
            o = struct.unpack_from("<I", mem, base + k * 0x162 + 0x54)[0] >> 16
            if o < 40:
                ships[o] += 1
    except Exception:
        pass
    rows = []
    for r in range(min(n, 40)):
        row = STATE + 0x1ee * r
        spec = mem[row + 7]
        col = mem[row + 8]
        p = struct.unpack_from("<I", mem, row + 0xd)[0]
        rec = next((v for v in st.values() if v["ptr"] == p), None)
        rows.append(dict(
            r=r, spec=spec, colour=col, hue=RING_HUE.get(col, "?"),
            name=mem[M + NBAR + spec * 0x14:M + NBAR + spec * 0x14 + 20]
                 .split(b"\x00")[0].decode("latin-1", "replace"),
            ptr_idx=(rec["seq"] if rec else None),
            ptr_star=(rec["name"] if rec else None),
            ptr_xy=(tuple(round(c, 1) for c in (rec["x"], rec["y"])) if rec else None),
            marker_star=next((f"{v['name']}#{v['seq']}" for v in st.values()
                              if v["marker"] & 0x80 and (v["marker"] & 0x0f) == (1 << (r % 8))),
                             None),
            ships=ships.get(r, 0),
            rel=[mem[row + 0x1c0 + j] for j in range(min(n, 40))]))
    markers = sorted(f"{v['name']}#{v['seq']}:{v['marker']:#04x}"
                     for v in st.values() if v["marker"] & 0x80)
    return dict(path=os.path.basename(path), turn=turn, n=n, T=T, B=B,
                rows=rows, markers=markers, stars=st)


def main():
    dirs = sys.argv[1:]
    pay = S.load_payload(ROOT)
    anch = S.anchors_cached(ROOT, pay)
    for d in dirs:
        saves = sorted(glob.glob(os.path.join(d, "*.sav")), key=os.path.getmtime)
        if not saves:
            print(f"## {d}: NO SAVES")
            continue
        seen = {}
        for p in saves:
            try:
                mem = zipfile.ZipFile(p).read("Memory")
                B = S.base_of(mem, anch)
                if B is None:
                    print(f"  {os.path.basename(p)} base=UNRESOLVED")
                    continue
                c = census(mem, B, p)
            except Exception as e:
                print(f"  {os.path.basename(p)} ERR {repr(e)[:70]}")
                continue
            seen.setdefault(c["turn"], c)
        for t in sorted(seen):
            c = seen[t]
            print(f"## dir={os.path.basename(d)} {c['path']} turn={c['turn']} "
                  f"n={c['n']} T={c['T']} decoded={len(c['stars'])} "
                  f"markers={c['markers']}")
            for rw in c["rows"]:
                print(f"   row{rw['r']:2d} spec={rw['spec']:3d} "
                      f"colour={rw['colour']:2d}({rw['hue']:12s}) "
                      f"homeptr={rw['ptr_star']!r}#{rw['ptr_idx']} "
                      f"xy={rw['ptr_xy']} markerHome={rw['marker_star']} "
                      f"ships={rw['ships']:3d} name={rw['name']!r} rel={rw['rel']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
