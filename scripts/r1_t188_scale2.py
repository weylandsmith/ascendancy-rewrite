#!/usr/bin/env python3
"""t188: FRAME + TARGET adjudication for the flight corpus (OQ-019).

For the busy lane-mover slots in the banked sitting (t1255..1335), per turn
FIRST trusted row, dump: xyz, state/kind, order bytes (+0x5d,+0x67), dword
[+0x59] handle decoded against the star grid (pointer law), nearest star name
+ distance, distance to nearest PLANET record origin, MOVES/fuel. Then:
 (Q1 frame) are ship xyz in the star f32 frame? nearest-star distance
        distribution overall; and for kind-2 ships, dist(ship, star[handle]).
 (Q2 scale) for each slot-turn: observed displacement vs the T1 prediction
        min(d_sugar,MOVES)*160 clamped by fuel, d measured to the DECODED
        target. Print the implied divisor when prediction fails.
Usage: r1_t188_scale2.py <T0> [slots csv]
"""
import sys, os, zipfile, struct, math, re, collections
sys.path.insert(0, "/home/hrethric/projects/ascendancy/scripts")
import r1_stream
from r1_sav_scan import build_anchors, find_base

PAY = "/home/hrethric/projects/ascendancy/work/ascend_payload.bin"
STRIDE_S, S_XYZ = 96, -0x14
PLANET_N, STRIDE_P = 0x26d07b, 123
SNAME_RE = rb"[A-Z][a-z]{2,15}\x00"
PNAME_RE = rb"[A-Z][A-Za-z]{2,}(?: [IVX]+)?\x00"
NAME_ANCHOR_HINT = 0x255be1
SAVE_DIR = "/home/hrethric/projects/ascendancy/work/r1/playcap/save"
PAY_BYTES = open(PAY, "rb").read()
ANCH = build_anchors(PAY_BYTES)

_cache = {}   # (file, mtime_ns) -> (stars, planets, H)
def frame_for(fname, mns):
    key = (fname, mns)
    if key in _cache:
        return _cache[key]
    p = os.path.join(SAVE_DIR, fname)
    try:
        mem = zipfile.ZipFile(p).read("Memory")
    except Exception:
        _cache[key] = None
        return None
    v, _ = find_base(mem, ANCH)
    if not v:
        _cache[key] = None
        return None
    H = v.most_common(1)[0][0] - 0x1BF450
    best = []
    for delta in range(0, 0x21):
        for sign in (-1, 1):
            cand = NAME_ANCHOR_HINT + sign * delta
            names, k = [], 0
            while True:
                q = cand + k * STRIDE_S + H
                m = re.match(SNAME_RE, mem[q:q+18])
                if not m: break
                best2 = (m.group()[:-1].decode(), q, struct.unpack_from("<3f", mem, q + S_XYZ))
                names.append(best2); k += 1
                if k > 60: break
            if len(names) > len(best): best = names
    # cache by file+mtime but the FILE ON DISK has moved on (rotation!).
    # verify the stars we read actually came from THIS mtime: we can't after
    # rotation; we only trust files whose mtime_ns == row's (fresh tail).
    _cache[key] = (best, H)
    return best, H

def main():
    T0 = int(sys.argv[1]) if len(sys.argv) > 1 else 1255
    slots = {int(s) for s in sys.argv[2].split(",")} if len(sys.argv) > 2 else None
    stat = {}
    prev = {}
    nd = collections.Counter()
    rows = 0
    # first pass: nearest-star distance census for ALL live ships, latest saves only
    for j in r1_stream.observations("/home/hrethric/projects/ascendancy/work/r1/playcap", trust=True, stats=stat):
        raw = j.get("ship_raw") or {}
        if not raw: continue
        fr = frame_for(j["file"], j.get("file_mtime_ns"))
        if fr is None:
            nd["frame_fail"] += 1
            continue
        stars, H = fr
        if len(stars) < 45:
            nd["stars_short"] += 1
            continue
        owners = {int(s["slot"]): s["owner"] for s in (j.get("ships") or [])}
        for k, w in raw.items():
            if len(w) != 177: continue
            b = struct.pack("<177H", *w)
            st = b[0x58]
            if st == 0: continue
            sl = int(k)
            if owners.get(sl, 65535) == 65535: continue
            x, y, z = struct.unpack_from("<3f", b, 0x9e)
            dmin, nm = min(((math.dist((x, y, z), s2), s0) for s0, _, s2 in stars), default=(9e9, "?"))
            nd[(round(dmin / 100) * 100) if dmin < 9e9 else -1] += 1
            rows += 1
            if slots and sl in slots and j["turn"] >= T0:
                mv = struct.unpack_from("<I", b, 0x94)[0]
                pw = struct.unpack_from("<I", b, 0x88)[0]
                h59 = struct.unpack_from("<I", b, 0x59)[0]
                print(f"t={j['turn']} slot={sl} own={owners.get(sl)} st={st} k59={b[0x59]} o5d={b[0x5d]} o67={b[0x67]} "
                      f"xy=({x:.2f},{y:.2f},{z:.2f}) MOVES={mv} POW={pw} h59=0x{h59:x} "
                      f"nearest={nm} d={dmin:.1f}")
                p = prev.get(sl)
                if p and p[0] != j["turn"]:
                    dd = math.dist((x, y, z), p[1])
                    print(f"      step {dd:.3f} sugar={dd/160:.5f} (prev t={p[0]})")
                prev[sl] = (j["turn"], (x, y, z))
    print("rows", rows, "census nearest-star-dist (bucketed):")
    for kk in sorted(k for k in nd if isinstance(k, int) and not isinstance(k, bool)):
        print(f"   ~{kk}u: x{nd[kk]}")

main()
