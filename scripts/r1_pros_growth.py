#!/usr/bin/env python3
"""r1_pros_growth.py — T37 SPLIT: does the POP-GROWTH counter (+0x4e)
accumulate (a) the RAW item PROS sum (t24 law), (b) the GATED battery
accumulator (field + class-3 bonus when field != 0; T35), or (c) the
stored DISPLAY word +0x48 (accumulator - pop>>2, floored; T34 law)?

t24's decisive capture had NO class-3 PROS slots, so (a)==(b) there and
(c) coincided at small numbers. This battery scans consecutive-save
transitions where the planet HAS an active PROS item on a class-3 cell
at t0 — the only samples where (a)/(b)/(c) diverge by construction.

Growth tick law (FUN_00038f68, income-law.md S6b/S6c):
  if pop(+0x42) >= cap(+0x4a): counter := 0 (reset branch)
  else counter += INPUT (+1 more if owner != current player AND
       display PROS < 4); if counter >= 50 (DAT_000066e4): pop += 1
       (+1 more if first ACTIVE slot is Cloning Plant item 15), clamp
       pop <= cap, counter := 0.
Owner-turn alternation makes the +1 boost unknowable from saves, so it
is a FREE parameter {0,1} on every transition — that only ever
broadens acceptance, never invents a match.

Exit codes (R1): 0 = one hypothesis wins decisively on the divergent
(class-3) set; 1 = inconclusive/no divergent samples; 2 = harness bug.
"""
import argparse, glob, os, struct as st, sys, zipfile, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base  # noqa: E402
import r1_income_law as IL  # noqa: E402

NAME_AT, THRESH, CLONE = 0x24, 50, 15
TURN_PHYS, IMAGE_MAP_BASE = 0x254E10, 0x1BF450  # banked (r1-savestate.md
# :138 turn clock; r1_record_census.py H-mapping)


def turn_of(m, base):
    """u16 turn counter: phys 0x254e10 mapped into the Memory image via
    H = base - 0x1BF450 (r1_record_census law). None if implausible."""
    off = TURN_PHYS + (base - IMAGE_MAP_BASE)
    if not (0 <= off and off + 2 <= len(m)):
        return None
    t = st.unpack_from("<H", m, off)[0]
    return t if t < 20000 else None


def saves(run_dir, anch):
    files = sorted(glob.glob(os.path.join(run_dir, "save", "*.sav")),
                   key=os.path.getmtime) or \
           sorted(glob.glob(os.path.join(run_dir, "*.sav")), key=os.path.getmtime)
    out = []
    for f in files:
        try:
            m = zipfile.ZipFile(f).read("Memory")
        except Exception:
            continue
        v, _ = find_base(m, anch)  # PAYLOAD anchors (r1_income_channels
        if not v:                  # pattern); self-anchored images return
            continue               # wrong base -> silent zero-evidence
        out.append((os.path.basename(f), m, v.most_common(1)[0][0]))
    return out


def state(m, base, items):
    """name -> per-planet t-snapshot (owned planets only)."""
    out = {}
    for rec in IL.find_records(m):  # IL yields (rb, cells, cap, ...)-tuples
        rb = rec[0]
        if m[rb + 0x12] == 0xFF:
            continue
        name = m[rb + NAME_AT:m.index(b"\x00", rb + NAME_AT)].decode("cp437", "replace")
        if len(name) < 3:
            continue
        ptr = st.unpack_from("<I", m, rb + 0x10)[0] + 0x88
        capw = st.unpack_from("<H", m, rb + 0x1a)[0]
        surf = st.unpack_from("<H", m, rb + 0x18)[0]
        if not (0 <= ptr and ptr + capw * 4 <= len(m)):
            continue
        raw = gated = 0
        si = 0
        cls3 = False
        clone_active = False
        for k in range(capw):
            it = m[ptr + 4 * k + 1]
            if it == 0xFF or it >= IL.N_ITEMS:
                continue
            if not st.unpack_from("<H", m, ptr + 4 * k + 2)[0] & 1:
                continue
            if it == CLONE:
                clone_active = True
            p = items[it]["pros"]
            # placement law T37b: k-th SURFACE item on surface cell k;
            # orbital/special classes irrelevant unless field != 0 AND
            # class == 3 — the ring is class 1 (@0x37f12), specials sit on
            # the surface stream (unmeasured; they add 0 pros anyway).
            if it < 22:
                cls = m[ptr + 4 * si] if si < surf else 1
                si += 1
            else:
                cls = 1
            raw += p
            if p:
                gated += p + (1 if cls == 3 else 0)
                if cls == 3:
                    cls3 = True
        out[name] = dict(
            pop=st.unpack_from("<H", m, rb + 0x42)[0],
            cap=st.unpack_from("<H", m, rb + 0x4a)[0],
            disp=st.unpack_from("<H", m, rb + 0x48)[0],
            counter=st.unpack_from("<H", m, rb + 0x4e)[0],
            acc50=st.unpack_from("<H", m, rb + 0x50)[0],
            pend=st.unpack_from("<H", m, rb + 0x54)[0],
            raw=raw, gated=gated, cls3=cls3, clone=clone_active,
            turn=turn_of(m, base),
        )
    return out


def predict(p, inp):
    """Acceptable next-counter values for input `inp` over EXACTLY one
    growth tick (accruing), free boost {0,1}. Freeze transitions
    (counter unchanged) are NOT evidence and handled by the caller."""
    outs = set()
    for boost in (0, 1):
        v = p["counter"] + inp + boost
        if v >= THRESH:
            # S6b [verified]: on threshold the counter resets, and the
            # 18->4 sample shows SAME-TURN RE-ACCRUAL of one input pass.
            outs.add(0)
            outs.add(min(inp + boost, THRESH - 1))
        else:
            outs.add(v)
    return outs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="work/r1/*")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    runs = sorted(d for d in glob.glob(args.runs) if os.path.isdir(d))
    if not runs:
        print("harness-error: no runs matched", args.runs)
        return 2
    pay = open(IL.PAY, "rb").read()
    anch = build_anchors(pay)

    hyps = ("raw", "gated", "disp")
    win = collections.Counter()
    loss = collections.Counter()
    shared = collections.Counter()
    n_div = 0
    n_trans = 0
    reset_ok = reset_bad = 0
    n_frozen = 0
    dt_hist = collections.Counter()
    gd = dg = 0
    gd_ex = []
    examples = []
    for run in runs:
        svs = saves(run, anch)
        prev = None
        for slot, m, base in svs:
            items = IL.item_table(m, base)
            if items is None or not IL.names_ok(items):
                prev = None
                continue
            cur = state(m, base, items)
            if prev is not None:
                for name, c in cur.items():
                    p = prev.get(name)
                    if p is None:
                        continue
                    if p["pop"] >= p["cap"]:
                        # reset branch: expect counter 0 next (pop unchanged)
                        if c["counter"] == 0 or c["counter"] == p["counter"]:
                            reset_ok += 1
                        else:
                            reset_bad += 1
                        continue
                    n_trans += 1
                    # Turn-boundary discipline: evidence ONLY for dt==1
                    # (exactly one growth tick between saves). dt is the
                    # banked u16 clock (phys 0x254e10 via H-map); multi-
                    # tick spans let items change mid-span, so they are
                    # counted but NOT decisive.
                    dt = (None if p["turn"] is None or c["turn"] is None
                          else c["turn"] - p["turn"])
                    if dt is not None:
                        dt_hist[dt] += 1
                    # S6c [verified]: non-accrual turns FREEZE the
                    # counter; consecutive saves frequently straddle no
                    # End-Turn. Only MOVED counters are growth evidence.
                    # (The [ESP+0x50]/cap gate form was tried and
                    # REFUTED: acc50 is the build accumulator, not the
                    # IND-side growth counter — the IND counter is not
                    # reliably located; we do NOT guess the gate, we
                    # filter to observed motion.)
                    moved = c["counter"] != p["counter"]
                    preds = {h: predict(p, p[h]) for h in hyps}
                    matched = [h for h in hyps if c["counter"] in preds[h]] if moved else []
                    # divergent set: predictions differ AND a class-3 PROS
                    # cell was active at t0 AND the counter actually moved
                    distinct = len({frozenset(v) for v in preds.values()}) > 1
                    if p["cls3"] and distinct and moved and dt == 1:
                        n_div += 1
                        for h in hyps:
                            if h not in matched:
                                loss[h] += 1
                        if len(matched) == 1:
                            win[matched[0]] += 1
                        elif len(matched) > 1:
                            for h in matched:
                                shared[h] += 1
                        if len(examples) < 12:
                            examples.append(
                                f"{run.split('/')[-1]} {slot} {name}: "
                                f"c {p['counter']}->{c['counter']} "
                                f"raw={p['raw']} gated={p['gated']} "
                                f"disp={p['disp']} pop {p['pop']}->{c['pop']} "
                                f"matched={matched or '[]'}")
                    elif not moved:
                        n_frozen += 1
                    elif dt == 1 and p["disp"] != p["gated"]:
                        # global discriminator row: hypotheses disagree
                        for h in hyps:
                            loss[h] += 0  # keep loss divergent-only
                        if "disp" in matched and "gated" not in matched:
                            gd += 1
                            if len(gd_ex) < 10:
                                gd_ex.append(
                                    f"{run.split('/')[-1]} {slot} {name}: "
                                    f"c {p['counter']}->{c['counter']} "
                                    f"raw={p['raw']} gated={p['gated']} "
                                    f"disp={p['disp']} cls3={p['cls3']}")
                        elif "gated" in matched and "disp" not in matched:
                            dg += 1
                    else:
                        for h in matched:
                            shared[h] += 1
            prev = cur

    print(f"transitions (pop<cap): {n_trans}   DIVERGENT class-3: {n_div}")
    print(f"frozen-counter transitions (no growth evidence): {n_frozen}")
    print(f"reset-branch ok/mismatched: {reset_ok}/{reset_bad}")
    print("turn-delta histogram:", dict(sorted(dt_hist.items())[:12]))
    print("disp-matches-gated-doesnt:", gd, "  gated-matches-disp-doesnt:", dg)
    for e in gd_ex:
        print("  GD:", e)
    print("decisive wins:", dict(win))
    print("shared/coincident:", dict(shared))
    for e in examples:
        print("  ", e)
    if n_div == 0 and gd + dg == 0:
        print("INCONCLUSIVE: no divergent class-3 transitions in corpus; "
              "growth-input question stays open.")
        return 1
    # Elimination verdict: a hypothesis survives only with zero losses in
    # BOTH the divergent-class-3 set and the global disp/gated
    # discriminator (gd rows cost gated, dg rows cost disp, div rows cost
    # the non-matching hyps).
    fl = dict(loss)
    fl["gated"] += gd
    fl["disp"] += dg
    surv = [h for h in hyps if fl[h] == 0]
    print("final loss ledger:", fl)
    if len(surv) == 1 and n_div + gd + dg >= 4:
        print(f"VERDICT: growth counter input == {surv[0]} "
              f"(others eliminated: {fl})")
        return 0
    print("INCONCLUSIVE on divergent set (close or losses):", dict(win), dict(loss))
    return 1


if __name__ == "__main__":
    sys.exit(main())
