#!/usr/bin/env python3
"""t369 — RING ORDER-DIFF: witnesses for the player's two-click destination.

TESTIMONY (docs/re/_wip_playtest_t369.md, hypothesis not law): selecting an
empty-space destination takes TWO clicks — first sets x/y, second sets z.
Prediction in RAM: between consecutive banked samples a destination triple
changes x/y while z holds, then the NEXT change moves z while x/y hold.
If both clicks land inside one 10 s ring gap we instead see ONE combined
change (class BOTH) — also reported, since XY->Z pairs + BOTH is the honest
shape of a real evening of play.

FIELDS DIFFED (pership-spec.md field map, all cited; churn set matches the
t366 census: +0x58/+0x59/+0x5d/+0x5e boundary-churn, +0x9e..a9 pos):
  +0x58 kind 0..5 | +0x59 target ptr | +0x5d act | +0x5e act-target |
  +0x67 order TYPE | +0x68 payload ptr (type-1 = 3-dword coord triple,
  derefs @0x49fb9/0x49fd7 — dereferenced in --dir mode only) |
  +0x6c f32[3] kind-3 absolute triple | +0x9e f32[3] position |
  +0xab gizmo ring (cidx set + u16 use-counters; decrements reported) |
  +0x15a cap | +0x15e filled.
POINTER LAW: within one session B is constant, so raw ptr equality across
samples of the same run is valid; --dir mode additionally rebases +0x59/+0x68
by (newB-oldB) per t298 before diffing (multi-run dirs).

DESTINATION TRIPLE (what the two-click law writes):
  kind/type 1 -> deref(+0x68) int triple   (--dir mode; tl mode: ptr change
                 only, class PITCHG)
  type 3      -> f32 triple at +0x6c
  other kinds -> no triple tracked

MODES:
  --dir DIR [DIR...]   .sav slots (Memory member), mtime order, dedup
                       (turn, content-hash). CONTROL MODE on
                       work/r1/bank-t1086-preplay -> expect 0 witnesses.
  --window LO_NS HI_NS live-timeline.jsonl rows (file_mtime_ns selector,
                       dedup (file,mt), in_game, turn>0, bounded 200 MB
                       tail-seek — OOM law).
  --selftest           synthetic two-click sequence must fire XY->Z.

Exit 0 = census complete (zero is a finding); 2 = harness error.
"""
import glob, hashlib, json, os, struct, sys, zipfile
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import r1_slot as S

JSONL = os.path.join(ROOT, "work", "r1", "playcap", "live-timeline.jsonl")
EPS = 1e-4


def parse_rec(b, mem=None):
    """Record bytes (+0x00..) -> dict of diffed fields."""
    if len(b) < 0x162:
        return None
    d = {
        "kind": b[0x58],
        "tgt": struct.unpack_from("<I", b, 0x59)[0],
        "act": b[0x5d],
        "atgt": struct.unpack_from("<I", b, 0x5e)[0],
        "type": b[0x67],
        "pay": struct.unpack_from("<I", b, 0x68)[0],
        "trip6c": struct.unpack_from("<3f", b, 0x6c),
        "pos": struct.unpack_from("<3f", b, 0x9e),
        "cap": struct.unpack_from("<I", b, 0x15a)[0],
        "own": struct.unpack_from("<I", b, 0x54)[0] >> 16,
    }
    cap = min(d["cap"], 25)
    ring = {}
    for i in range(cap):
        c = b[0xab + 7 * i]
        if c != 0xFF:
            ring[i] = (c, struct.unpack_from("<H", b, 0xab + 7 * i + 1)[0])
    d["ring"] = ring
    d["dest"] = None
    if mem is not None and d["type"] == 1 and d["pay"] != 0:
        try:
            d["dest"] = struct.unpack_from("<3i", mem, d["pay"])
        except Exception:
            pass
    return d


def dest_vec(d):
    """Comparable destination signature (x, y, z) or None."""
    if d is None:
        return None
    if d["dest"] is not None:
        return tuple(float(v) for v in d["dest"])
    if d["type"] == 3:
        return d["trip6c"]
    return None


def classify(pv, nv):
    """Classify a destination-vector change."""
    if pv is None or nv is None:
        return None
    dx, dy, dz = (nv[0] - pv[0], nv[1] - pv[1], nv[2] - pv[2])
    if abs(dx) < EPS and abs(dy) < EPS and abs(dz) < EPS:
        return None
    if abs(dz) < EPS:
        return "XY"
    if abs(dx) < EPS and abs(dy) < EPS:
        return "Z"
    return "BOTH"


def diff_samples(samples):
    """samples: [(label, base_or_None, {slot: rec})]. Returns report dict."""
    cls_hist = Counter()
    events = []         # every dest change in global order: (label, slot,
                        # own, class, v0, v1, seq)
    both = []           # combined-change events
    pitchg = []         # kind-1 payload ptr change w/o deref (tl mode)
    ring_dec = []       # gizmo use-counter decrements
    kind_hist = Counter()
    arbitrary_z = []    # dest changes landing on off-32-grid z (tl+dir)
    prev = None
    for label, B, s in samples:
        for sl, d in s.items():
            if d is None:
                continue
            kind_hist[d["kind"]] += 1
        if prev is not None:
            pB, ps = prev
            for sl, d in s.items():
                pd = ps.get(sl)
                if pd is None or d is None:
                    continue
                shift = (B - pB) if (B is not None and pB is not None) else 0
                # pointer-field compare (rebased)
                for fld in ("tgt", "atgt", "pay"):
                    pvv = pd[fld] + (shift if fld in ("tgt", "pay") else 0)
                    if pvv != d[fld]:
                        if fld == "pay" and pd["type"] == 1 and d["type"] == 1:
                            tag = "PAYPTR"
                        else:
                            tag = None
                        if tag:
                            pitchg.append((label, sl, pd["own"], tag,
                                           hex(pvv), hex(d[fld])))
                # destination-vector change
                dv0, dv = dest_vec(pd), dest_vec(d)
                c = classify(dv0, dv)
                if c and dv0 is not None and dv is not None:
                    cls_hist[c] += 1
                    rec = (label, sl, pd["own"], c,
                           tuple(round(v, 2) for v in dv0),
                           tuple(round(v, 2) for v in dv),
                           len(events))
                    events.append(rec)
                    if c == "BOTH":
                        both.append(rec)
                    if abs(dv[2] / 32.0 - round(dv[2] / 32.0)) >= 1e-4:
                        arbitrary_z.append(rec)
                # ring decrements (same cidx, lower use counter)
                for i, (c0, u0) in pd["ring"].items():
                    r1 = d["ring"].get(i)
                    if r1 and r1[0] == c0 and r1[1] < u0:
                        ring_dec.append((label, sl, pd["own"], c0, u0, r1[1]))
        prev = (B, s)
    # two-click witness = ADJACENT events in global event order: an XY
    # change immediately followed by a Z change on the same slot (a THIRD
    # interleaved dest change breaks adjacency by construction).
    two_click = []
    for a, b_ in zip(events, events[1:]):
        if a[3] == "XY" and b_[3] == "Z" and a[1] == b_[1]:
            two_click.append((a, b_))
    return {"cls": dict(cls_hist), "two_click": two_click, "both": both,
            "pitchg": pitchg, "ring_dec": ring_dec,
            "kind_hist": dict(kind_hist), "arbitrary_z": arbitrary_z}


def run_dir(d):
    files = sorted(glob.glob(os.path.join(d, "*.sav")), key=os.path.getmtime)
    pay = S.load_payload(ROOT)
    anch = S.anchors_cached(ROOT, pay)
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
        s = {k: parse_rec(mem[base + k * 0x162: base + (k + 1) * 0x162], mem)
             for k in range(n)}
        # signature = the FULL diffed field set (a dest-triple edit at a
        # STABLE payload ptr, or a ring edit, must not dedup away)
        h = hashlib.sha1()
        for i, d in sorted(s.items()):
            if d:
                h.update(struct.pack("<BIIIB", d["kind"], d["tgt"], d["atgt"],
                                     d["type"], d["pay"] & 0xFF))
                h.update(struct.pack("<6f", *d["trip6c"], *d["pos"]))
                if d["dest"] is not None:
                    h.update(struct.pack("<3i", *d["dest"]))
                h.update(repr(sorted(d["ring"].items())).encode())
        key = (dsc["turn"], h.hexdigest())
        if key in seen:
            continue
        seen.add(key)
        samples.append((f"{os.path.basename(f)} t{dsc['turn']}", B, s))
    return samples


def run_tl(lo_ns, hi_ns, jsonl=None):
    jsonl = jsonl or JSONL
    size = os.path.getsize(jsonl)
    seek = 200_000_000   # ~22 h of 10 s cadence rows; OOM law bound
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
            mt = int(line[i + 17:line.find(",", i)])
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
            try:
                ob = json.loads(line)
            except Exception:
                continue
            if ob.get("turn", 0) <= 0:
                continue
            s = {}
            for k, w in (ob.get("ship_raw") or {}).items():
                b = struct.pack("<%dH" % len(w), *w) if len(w) == 177 else b""
                s[int(k)] = parse_rec(b) if b else None
            samples.append((f"{fn} t{ob['turn']} {ob.get('wall','?')}", None, s))
    return samples


def report(tag, samples, r):
    print(f"== {tag}: {len(samples)} deduped in-game samples")
    print(f"order-kind sample histogram: {r['kind_hist']}")
    print(f"destination change classes: {r['cls']}")
    print(f"TWO-CLICK witnesses (XY event immediately followed by Z event, "
          f"same slot): {len(r['two_click'])}")
    for a, b_ in r["two_click"][:10]:
        print(f"   slot={a[1]} own={a[2]}: {a[4]} ->(XY)-> {a[5]} "
              f"->(Z)-> {b_[5]}  [{a[0]} | {b_[0]}]")
    print(f"BOTH (combined, clicks inside one ring gap): {len(r['both'])}")
    for e in r["both"][:10]:
        print(f"   slot={e[1]} own={e[2]} {e[4]} -> {e[5]} @ {e[0]}")
    print(f"kind-1 payload-ptr changes (deref unavailable in tl mode): "
          f"{len(r['pitchg'])}")
    for e in r["pitchg"][:10]:
        print(f"   slot={e[1]} own={e[2]} {e[4]} -> {e[5]} @ {e[0]}")
    print(f"gizmo use-counter DECREMENTS: {len(r['ring_dec'])}")
    for e in r["ring_dec"][:10]:
        print(f"   slot={e[1]} own={e[2]} cidx={e[3]} {e[4]}->{e[5]} @ {e[0]}")
    print(f"dest landings with off-32-grid z (arbitrary-z candidates): "
          f"{len(r['arbitrary_z'])}")
    for e in r["arbitrary_z"][:10]:
        print(f"   slot={e[1]} own={e[2]} {e[3]} {e[4]} -> {e[5]} @ {e[0]}")


def selftest():
    """Synthetic two-click: dest (0,0,0) -> (100,200,0) -> (100,200,-300).
    Must produce exactly 1 two_click witness."""
    def rec(pay, trip=None, typ=1):
        b = bytearray(0x162)
        b[0x58] = 1
        b[0x67] = typ
        struct.pack_into("<I", b, 0x68, pay)
        if trip:
            struct.pack_into("<3f", b, 0x6c, *trip)
        return bytes(b)
    class FakeMem(bytes):
        pass
    mem = bytearray(0x400000)
    struct.pack_into("<3i", mem, 0x1000, 0, 0, 0)
    s0 = {0: parse_rec(rec(0x1000), mem)}
    struct.pack_into("<3i", mem, 0x1000, 100, 200, 0)
    s1 = {0: parse_rec(rec(0x1000), mem)}
    struct.pack_into("<3i", mem, 0x1000, 100, 200, -300)
    s2 = {0: parse_rec(rec(0x1000), mem)}
    r = diff_samples([("s0", 0, s0), ("s1", 0, s1), ("s2", 0, s2)])
    ok = len(r["two_click"]) == 1 and r["cls"] == {"XY": 1, "Z": 1}
    print(f"SELFTEST: two_click={len(r['two_click'])} cls={r['cls']} -> "
          f"{'PASS' if ok else 'FAIL'}")
    return 0 if ok else 2


def main():
    argv = sys.argv[1:]
    if "--selftest" in argv:
        return selftest()
    if "--dir" in argv:
        i = argv.index("--dir") + 1
        dirs = []
        while i < len(argv) and not argv[i].startswith("--"):
            dirs.append(argv[i]); i += 1
        for d in dirs:
            samples = run_dir(d)
            report(d, samples, diff_samples(samples))
        return 0
    if "--window" in argv:
        i = argv.index("--window") + 1
        lo = int(argv[i]); hi = int(argv[i + 1]) if i + 1 < len(argv) else -1
        samples = run_tl(lo, hi, jsonl=argv[argv.index("--jsonl") + 1]
                         if "--jsonl" in argv else None)
        if not samples:
            print(f"NO ROWS in window [{lo},{hi}] — honest negative.")
            return 0
        report(f"timeline {lo}..{hi}", samples, diff_samples(samples))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
