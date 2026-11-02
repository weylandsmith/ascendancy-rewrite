#!/usr/bin/env python3
"""t269 — OQ-021 VICTORY-THRESHOLD MINING on the driven corpus.

Question: the vendor's end-ctrl.txt header says "Player controls over half the
galaxy" (docs/re/turnloop.md citation); the rewrite ships >1/2
(campaign.cpp). Has ANY captured frame ever approached/crossed the threshold,
and does the selector byte (DAT_00043510) ever arm?

Schema (scripts/r1_slot.py read_slot + r1_playcap_watch.py process):
  turn=u32[0x12e10]  T=u32[0x16143]>>16 (TOTAL STARS, score.md S2 disproducer
  law: displayed percent = TRUNC(100*V/T))  V=score_stars=u32[0x482fb]
  selector_byte=u8[0x43510]  rank=u16[0x4350c]
  systems_any / systems_full / planets_mine (watcher star-table derivation)

Laws honoured (each cited):
  OOM law (t251): single streaming pass over the file ITERATOR (never read(),
    never json.load of the whole file), header-scalar slices only, rows never
    buffered. ship_raw/relation fields are never touched.
  Dedup (file, file_mtime_ns) (t85b/t259 orphan-writer law).
  Corpus gate on file_mtime_ns EPOCH ns (t261 law: wall strings are HH:MM:SS
    and collide across days).
  Per-SEGMENT trust (t262 generalisation of t255): session = mtime gap > 600 s;
    split at reload class (V==0 at turn <= watermark) and foreign-lineage class
    (turn drop > 2 while V!=0).

usage: r269_vthreshold.py [LO_EPOCH_S] [HI_EPOCH_S]   (defaults: whole file)
output -> stdout (small: per-segment summary + V-change boundaries + event hits)
"""
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSONL = os.path.join(ROOT, "work/r1/playcap", "live-timeline.jsonl")


def fnum(line, key):
    """Value of '"key": <int>' or None. Brace-agnostic (t258 hygiene: never
    assume what follows the value — parse digits and stop)."""
    pat = '"%s": ' % key
    i = line.find(pat)
    if i < 0:
        return None
    i += len(pat)
    j = i
    while j < len(line) and line[j].isdigit():
        j += 1
    if j == i:
        return None
    return int(line[i:j])


def fstr(line, key):
    pat = '"%s": "' % key
    i = line.find(pat)
    if i < 0:
        return None
    i += len(pat)
    j = line.find('"', i)
    return line[i:j]


def main():
    LO = int(sys.argv[1]) * 10**9 if len(sys.argv) > 1 else 0
    HI = int(sys.argv[2]) * 10**9 if len(sys.argv) > 2 else None

    size = os.path.getsize(JSONL)
    print("corpus %s size=%d gate=[%s,%s]" % (
        JSONL, size,
        time.strftime("%Y-%m-%d %H:%M", time.localtime(LO / 1e9)) if LO else "-",
        time.strftime("%Y-%m-%d %H:%M", time.localtime(HI / 1e9)) if HI else "-"))

    seen = set()
    n_lines = n_gate = n_dedup = n_noturn = 0
    Tvals = {}          # T -> row count (census: is total-stars constant?)
    selvals = {}        # selector_byte -> row count
    rankvals = {}       # rank -> row count (0xffff = "none yet" sentinel)
    events = []         # threshold / selector-arm witnesses (verbatim-ish)
    segs = []
    seg = None
    prev_mt = None

    def flush_cur():
        if seg is not None and seg["cur"] is not None:
            seg["boundaries"].append(seg["cur"])
            seg["cur"] = None

    def close_seg():
        nonlocal seg
        if seg is None:
            return
        flush_cur()
        segs.append(seg)
        seg = None

    def new_seg(mt):
        nonlocal seg
        close_seg()
        seg = {"sid": len(segs), "start": mt, "wm": -1, "rows": 0,
               "boundaries": [], "cur": None, "cur_turn": None,
               "maxV": 0, "maxV_turn": None, "maxPct": 0.0,
               "maxPct_turn": None, "n_v0": 0, "min_turn": None,
               "max_turn": None}
        return seg

    with open(JSONL, "r", errors="replace") as f:
        for line in f:                       # lazy iterator: bounded RSS
            n_lines += 1
            mt = fnum(line, "file_mtime_ns")
            if mt is None:
                n_gate += 1
                continue
            if mt < LO or (HI is not None and mt > HI):
                continue
            fn = fstr(line, "file")
            if fn is None:
                n_gate += 1
                continue
            key = (fn, mt)
            if key in seen:
                n_dedup += 1
                continue
            seen.add(key)
            turn = fnum(line, "turn")
            if turn is None:
                n_noturn += 1
                continue
            V = fnum(line, "score_stars") or 0
            T = fnum(line, "T")
            sel = fnum(line, "selector_byte")
            rank = fnum(line, "rank")
            s_any = fnum(line, "systems_any")
            s_full = fnum(line, "systems_full")
            pm = fnum(line, "planets_mine")
            wall = fstr(line, "wall")

            Tvals[T] = Tvals.get(T, 0) + 1
            selvals[sel] = selvals.get(sel, 0) + 1
            rankvals[rank] = rankvals.get(rank, 0) + 1

            # ---- segmentation (t262 law) ----
            if seg is None or (mt - prev_mt) > 600_000_000_000:
                new_seg(mt)
            else:
                if V == 0 and turn <= seg["wm"]:
                    new_seg(mt)                       # reload class
                elif seg["wm"] - turn > 2 and V != 0:
                    new_seg(mt)                       # foreign-lineage class
            seg["rows"] += 1
            seg["wm"] = max(seg["wm"], turn)
            if seg["min_turn"] is None or turn < seg["min_turn"]:
                seg["min_turn"] = turn
            if seg["max_turn"] is None or turn > seg["max_turn"]:
                seg["max_turn"] = turn
            prev_mt = mt

            # ---- threshold / selector witness (THE closure class) ----
            pct = (100.0 * V / T) if T else 0.0
            if V >= 25 or (sel not in (0, None)):
                events.append((mt, fn, turn, V, T, sel, rank, s_any, s_full,
                               round(pct, 1)))

            if V > seg["maxV"]:
                seg["maxV"], seg["maxV_turn"] = V, turn
            if pct > seg["maxPct"]:
                seg["maxPct"], seg["maxPct_turn"] = pct, turn
                seg["maxPct_T"] = T

            # ---- boundary snapshot bookkeeping (per turn, keep last) ----
            if turn != seg["cur_turn"]:
                flush_cur()
                seg["cur_turn"] = turn
                seg["cur"] = {"turn": turn, "V": V, "T": T, "sel": sel,
                              "any": s_any, "full": s_full, "pm": pm,
                              "mt": mt, "wall": wall}
            elif seg["cur"] is not None:
                seg["cur"] = {"turn": turn, "V": V, "T": T, "sel": sel,
                              "any": s_any, "full": s_full, "pm": pm,
                              "mt": mt, "wall": wall}
    close_seg()

    print("lines=%d gated_out=%d dedup=%d noturn=%d segments=%d" % (
        n_lines, n_gate, n_dedup, n_noturn, len(segs)))
    print("\n== T (total stars) census ==")
    for T, c in sorted(Tvals.items(), key=lambda kv: -kv[1])[:10]:
        print("  T=%s rows=%d" % (T, c))
    print("\n== selector_byte census ==")
    for s, c in sorted(selvals.items(), key=lambda kv: str(kv[0])):
        print("  sel=%s rows=%d" % (s, c))
    print("\n== rank census (0xffff=65535 sentinel 'none yet') ==")
    for rk, c in sorted(rankvals.items(), key=lambda kv: -kv[1])[:10]:
        print("  rank=%s rows=%d" % (rk, c))

    print("\n== per-segment summary (sid start turn-range rows maxV@turn "
          "maxPct@turn) ==")
    for s in segs:
        print("  %4d %s t%s..%s rows=%-6d maxV=%-3d@t%-5s maxPct=%.1f@t%s" % (
            s["sid"],
            time.strftime("%m-%d %H:%M", time.localtime(s["start"] / 1e9)),
            s["min_turn"], s["max_turn"], s["rows"],
            s["maxV"], s["maxV_turn"], s["maxPct"], s["maxPct_turn"]))

    print("\n== V-change boundaries (per segment; turn,V,T,any,full,pm) ==")
    n_b = 0
    for s in segs:
        bs = s["boundaries"]
        prev = None
        shown = 0
        for b in bs:
            if prev is not None and b["V"] != prev["V"]:
                print("  seg%d t%s->%s V %s->%s (T=%s any=%s full=%s pm=%s "
                      "%s)" % (s["sid"], prev["turn"], b["turn"], prev["V"],
                               b["V"], b["T"], b["any"], b["full"], b["pm"],
                               b["wall"]))
                n_b += 1
                shown += 1
            prev = b
        if shown > 40:
            print("  (seg%d: %d V-change boundaries total)" % (s["sid"], shown))
    print("total V-change boundaries=%d" % n_b)

    print("\n== THRESHOLD/EVENT WITNESSES (V>=25 or selector!=0) ==")
    if not events:
        print("  NONE — zero rows with V>=25, zero rows with selector armed")
    else:
        for e in events[:200]:
            print("  mt=%d %s t=%s V=%s T=%s sel=%s rank=%s any=%s full=%s "
                  "pct=%s" % e)
        if len(events) > 200:
            print("  (%d total)" % len(events))

    # distance-to-half statement
    best = None
    for s in segs:
        if best is None or s["maxPct"] > best["maxPct"]:
            best = s
    if best:
        T = best.get("maxPct_T")
        half = (T // 2 + 1) if T else None
        print("\n== DISTANCE-TO-HALF ==")
        print("  corpus max percent-controlled = %.1f%% at seg%d t%s "
              "(V=%d, T=%s stars)" % (best["maxPct"], best["sid"],
                                      best["maxPct_turn"], best["maxV"], T))
        if half is not None:
            print("  strict-majority V>=%d needs %d more controlled stars"
                  % (half, half - best["maxV"]))


if __name__ == "__main__":
    main()
