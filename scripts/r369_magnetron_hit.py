#!/usr/bin/env python3
"""t369 — MAGNETRON LANDING CENSUS over the play window (or any .sav dir).

Three counters, all from CITED laws (docs/re/ships.md S19 T3, S24 K3b,
pership-spec T-3; NOT re-derived):
  C1 CARRIAGE: ships whose gizmo ring (base +0xab, 25 slots stride 7,
     cidx u8 @slot+0, 0xFF empty) holds cidx 60 == 'Lane Magnetron'
     (loaded-table order law, r1_t185 census). Use-counter u16 @slot+1
     reported (decrement law ships.md:767).
  C2 LANDING (K3b): any st4 (+0x58==4) row off the 32-grid in x OR z.
     P(both jittered axes on-grid) < 0.1% per rng%200 law => off-grid st4
     is the magnetron-placed signature; on-grid st4 = walk/system control.
     y-mod-32 histogram printed alongside (placement adds EXACTLY -200.0
     before jitter; -200 % 32 == 24).
  C3 FRAME (W2): consecutive-row transition st!=5 -> st==5 with displacement
     >300 (S21 big-mover bound), y in [-200,0), x/z not both on-grid.
     st5 is a same-call transient; the landing ROW is st4, so C2 is the
     primary counter and C3 only fires if a capture tick catches the call.

MODES:
  dir  : r369_magnetron_hit.py --dir DIR [DIR...]   .sav slots (Memory
         member), mtime-ordered, dedup by content signature (turn, per-slot
         (kind,x,y,z) hash). THE CONTROL MODE: run on
         work/r1/bank-t1086-preplay — expect C1 as observed, C2=C3=0.
  tl   : r369_magnetron_hit.py --window LO_NS HI_NS  live-timeline.jsonl
         rows selected by file_mtime_ns in [LO,HI] (r265 selector law),
         dedup (file, mtime_ns), in_game AND turn>0; bounded tail-seek
         (OOM law), ship_raw = 177 u16 words verbatim window.

Exit 0 census complete (honest negatives are findings), 2 harness error.
"""
import glob, hashlib, json, json as J, os, struct, re, sys, zipfile
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import r1_slot as S

JSONL = os.path.join(ROOT, "work", "r1", "playcap", "live-timeline.jsonl")
MAG = 60
BIG = 300.0


def grid32(v):
    q = v / 32.0
    return abs(q - round(q)) < 1e-4


def parse_words(w177):
    """177-u16 window -> (kind, x, y, z, owner, mag_slots) or None."""
    if len(w177) != 177:
        return None
    b = struct.pack("<177H", *w177)
    st = b[0x58]
    x, y, z = struct.unpack_from("<3f", b, 0x9e)
    own = b[0x56]
    mags = []
    cap = min(struct.unpack_from("<I", b, 0x15a)[0], 25)
    for i in range(cap):
        if b[0xab + 7 * i] == MAG:
            mags.append(struct.unpack_from("<H", b, 0xab + 7 * i + 1)[0])
    return st, x, y, z, own, mags


def census(samples):
    """samples: list of (seq_label, {slot: parsed}) in time order.
    Returns counters dict."""
    c1 = []            # (label, slot, use_counters)
    c2 = []            # (label, slot, x, y, z, owner) off-grid st4
    c3 = []            # (label, slot, d, y, owner) W2 frames
    y_hist = Counter()
    st4_on = 0
    prev = None
    for label, s in samples:
        for sl, v in s.items():
            if v is None:
                continue
            st, x, y, z, own, mags = v
            if mags:
                c1.append((label, sl, mags))
            if st == 4:
                y_hist[round(y % 32.0, 3)] += 1
                if grid32(x) and grid32(z):
                    st4_on += 1
                else:
                    c2.append((label, sl, round(x, 3), round(y, 3),
                               round(z, 3), own))
        cur = {sl: v for sl, v in s.items() if v is not None}
        if prev is not None:
            for sl, v in cur.items():
                pv = prev[1].get(sl)
                if pv is None or v[0] != 5 or pv[0] == 5:
                    continue
                dx = v[1] - pv[1]; dy = v[2] - pv[2]; dz = v[3] - pv[3]
                d = (dx * dx + dy * dy + dz * dz) ** 0.5
                if d > BIG and -200.0 <= v[2] < 0.0 \
                        and not (grid32(v[1]) and grid32(v[3])):
                    c3.append((label, sl, round(d, 1), round(v[2], 3), v[4]))
        prev = (label, cur)
    return {"C1_carriage": c1, "C2_landing": c2, "C3_frame": c3,
            "y_mod32": dict(y_hist.most_common(8)), "st4_on_grid": st4_on}


def run_dir(d, pay, anch):
    files = sorted(glob.glob(os.path.join(d, "*.sav")), key=os.path.getmtime)
    samples, seen = [], set()
    for f in files:
        try:
            mem = zipfile.ZipFile(f).read("Memory")
        except Exception:
            continue
        B = S.base_of(mem, anch)
        if B is None or len(mem) < 0x90000:
            continue
        dsc = S.read_slot(f, mem, B)
        if not dsc["in_game"]:
            continue
        base, n = S.ship_array_law(mem, B)
        s = {}
        for k in range(n):
            w = struct.unpack_from("<177H", mem, base + k * 0x162)
            s[k] = parse_words(w)
        # signature = st, pos (rounded), AND the gizmo ring (mags): a
        # carriage-only or landing-only edit must never dedup away
        sig = hashlib.sha1(repr([
            (t[0], round(t[1], 2), round(t[2], 2), round(t[3], 2), t[5])
            if t else None for t in s.values()
        ] + [
            (k, v[5]) for k, v in sorted(s.items()) if v
        ]).encode()).hexdigest()
        key = (dsc["turn"], sig)
        if key in seen:
            continue
        seen.add(key)
        samples.append((f"{os.path.basename(f)} t{dsc['turn']}", s))
    return samples


def run_tl(lo_ns, hi_ns, jsonl=None):
    jsonl = jsonl or JSONL
    size = os.path.getsize(jsonl)
    # bounded region: start from the window end, seek back 200 MB (OOM law;
    # the playtest is one evening — 200 MB ~ 8000 rows ~ 22 h at 10 s cadence)
    # hi bound is a FILTER, not a seek target (row offsets don't map to time).
    seek = 200_000_000
    samples, seen = [], set()
    with open(jsonl, "r", errors="replace") as fh:
        fh.seek(max(0, size - seek))
        fh.readline()
        for line in fh:
            if not line.endswith("\n"):
                continue
            i = line.find('"file_mtime_ns": ')
            if i < 0:
                continue
            j = line.find(",", i)
            mt = int(line[i + 17:j])
            if not (lo_ns <= mt <= (hi_ns if hi_ns and hi_ns > 0 else 1 << 62)):
                continue
            fi = line.find('"file": "')
            fn = line[fi + 8:line.find('"', fi + 8)] if fi >= 0 else "?"
            key = (fn, mt)
            if key in seen:
                continue
            seen.add(key)
            if '"in_game": true' not in line:
                continue
            ti = line.find('"turn": ')
            turn = int(line[ti + 8:line.find(",", ti)])
            if turn <= 0:
                continue
            try:
                ob = J.loads(line)
            except Exception:
                continue
            s = {k: parse_words(w) for k, w in (ob.get("ship_raw") or {}).items()}
            samples.append((f"{fn} t{turn} {ob.get('wall','?')}", s))
    return samples


def report(tag, samples, res):
    print(f"== {tag}: {len(samples)} deduped in-game slot-samples")
    print(f"C1 magnetron(60) carriage: {len(res['C1_carriage'])}")
    for e in res["C1_carriage"][:20]:
        print(f"   slot={e[1]} use_counters={e[2]} @ {e[0]}")
    print(f"C2 OFF-GRID st4 landing rows: {len(res['C2_landing'])} "
          f"(on-grid st4 rows: {res['st4_on_grid']})")
    for e in res["C2_landing"][:20]:
        print(f"   slot={e[1]} own={e[5]} xyz=({e[2]},{e[3]},{e[4]}) @ {e[0]}")
    print(f"C3 W2 placement frames: {len(res['C3_frame'])}")
    for e in res["C3_frame"][:20]:
        print(f"   slot={e[1]} d={e[2]} y={e[3]} own={e[4]} @ {e[0]}")
    print(f"st4 y-mod-32 histogram: {res['y_mod32']}")


def main():
    argv = sys.argv[1:]
    pay = S.load_payload(ROOT)
    anch = S.anchors_cached(ROOT, pay)
    if "--dir" in argv:
        dirs = []
        i = argv.index("--dir") + 1
        while i < len(argv) and not argv[i].startswith("--"):
            dirs.append(argv[i]); i += 1
        if not dirs:
            print("usage: --dir DIR [DIR...]"); return 2
        for d in dirs:
            samples = run_dir(d, pay, anch)
            report(d, samples, census(samples))
        return 0
    if "--window" in argv:
        i = argv.index("--window") + 1
        lo = int(argv[i]); hi = int(argv[i + 1]) if i + 1 < len(argv) else -1
        samples = run_tl(lo, hi, jsonl=argv[argv.index("--jsonl") + 1]
                         if "--jsonl" in argv else None)
        if not samples:
            print(f"NO ROWS in window [{lo},{hi}] — window not banked or "
                  "wrong bounds. Honest negative.")
            return 0
        report(f"timeline window {lo}..{hi}", samples, census(samples))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
