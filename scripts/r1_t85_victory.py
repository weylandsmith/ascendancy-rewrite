#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r1_t85_victory.py RUN_DIR — OQ-021 end-ctrl threshold readout (t85).

Question: does the original fire Control victory at >1/2 of stars or at
>=2/3? Default in force: >1/2 (campaign.cpp:738).

Cited laws (score.md S3/S4, BLOCKED.md t73/t82):
  * scored stars = u32 DAT_000482fb ("STARS CONTROLLED %d" prints it);
    T = u32 DAT_00016143 >> 16; the score percent shown by the presenter is
    TRUNC(100*DAT_482fb / T).
  * end-presenter selector = BYTE DAT_00043510 (a nonzero selector means an
    ending screen was queued: 0 = none; value selects the end-*.txt file via
    the 0x2c03a..0x2c0b6 cluster). Rank u16 DAT_0004350c.
  * TRUST LAW: only slots with turn>0 count (title slots carry
    uninitialised selector bytes).
  * CAUTION: the comparator's WRITE of 0x43510 has never been located; the
    selector is evidence-by-observation, not evidence-by-code. The threshold
    question is closed by observation: the owned-share at the FIRST slot
    whose selector goes nonzero, plus every crossing candidate below.

Discriminating shares at T=50: >1/2 fires at 26; >=2/3 fires at 34 (>=) or
33 (2/3*50=33.33 -> >). A first nonzero-selector slot at 26..33 discriminates
>1/2; at 34+ it discriminates >=2/3.

Exit 0 = selector armed in some trusted slot (the closing observation
exists). 1 = ran, session never armed the selector (colonisation short of
threshold). 2 = harness error.
"""
import argparse, json, os, os.path, re, struct, sys, zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_slot as S
import r1_stream as ST


def trusted_observations(run_dir, root, anch, pay, trust=True):
    """Streaming merge (t85b): jsonl first (durable, cheap scalar scan),
    ring slots only as fallback when the jsonl has nothing. The OLD version
    json.loads'd every line AND ran S.timeline() over the ring — with a
    multi-sitting capture (4.3 GB jsonl) the analyzers sharing this layer
    were OOM-killed; the combat analyzer is now independent of this
    function."""
    obs = []
    jl = os.path.join(run_dir, "live-timeline.jsonl")
    seen = set()
    if os.path.isfile(jl):
        import r1_stream as ST
        stats = {}
        for j in ST.observations(run_dir, trust=trust, stats=stats):
            key = (j["file"], j.get("turn"))
            if key in seen:
                continue
            seen.add(key)
            obs.append(dict(file=j["file"], turn=j["turn"], T=j["T"],
                            score_stars=j["score_stars"],
                            selector_byte=j["selector_byte"],
                            rank=j.get("rank", 65535),
                            systems_any=j.get("systems_any"),
                            systems_full=j.get("systems_full"),
                            planets_mine=j.get("planets_mine"),
                            wall=j.get("wall", "?")))
        obs.sort(key=lambda o: o["turn"])
        return obs, stats
    for d in S.timeline(run_dir, pay, root, anch=anch, verbose=False):
        if d["in_game"]:
            obs.append(d)
    return obs, {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--no-trust", action="store_true")
    a = ap.parse_args()
    if not os.path.isdir(a.run_dir):
        print("harness-error: no run dir")
        return 2
    root = os.getcwd()
    pay = S.load_payload(root)
    anch = S.anchors_cached(root, pay)
    obs, stats = trusted_observations(a.run_dir, root, anch, pay,
                                      trust=not a.no_trust)
    print(ST.echo_note(stats))
    if not obs:
        print("No trusted (turn>0) slot: title-only capture or analyzer "
              "found no base. Play in past the title screen, then rerun.")
        return 1

    # t85b: ONE row per turn (the first trusted observation of that turn).
    # The t85 print loop emitted every slot-observation (~28k lines) and the
    # verdict keyed ONLY on DAT_482fb — which the t85 calibration already
    # proved is not raw owned-stars, and which on the multi-sitting capture
    # NEVER crossed half (max 23/50) while the planet-record census reached
    # 27 systems_any / 26 systems_full. Both series print now; the verdict
    # text says exactly what each can and cannot close.
    by_turn = {}
    for o in obs:
        by_turn.setdefault(o["turn"], o)
    turns = sorted(by_turn)
    print(f"trusted turns: {len(turns)}   range {turns[0]}..{turns[-1]}")
    print("turn   file    DAT482fb/T  sel  rank | sys_any sys_full planets")

    def show(o):
        T = o.get("T") or 1
        print(f"{o['turn']:<6} {o['file']:<7} "
              f"{o['score_stars']:>3}/{T:<3} {o['selector_byte']:<4} "
              f"{o.get('rank', 65535):<6} | {o.get('systems_any', '?'):>7} "
              f"{o.get('systems_full', '?'):>8} {o.get('planets_mine', '?'):>7}")

    armed = None
    key_turns = set()
    for t in turns:
        o = by_turn[t]
        if armed is None and o["selector_byte"] != 0:
            armed = o
            key_turns.update(turns[max(0, turns.index(t) - 2):])
    T = by_turn[turns[-1]].get("T") or 50
    x_dat = next((t for t in turns if by_turn[t]["score_stars"] * 2 > T), None)
    x_any = next((t for t in turns if (by_turn[t].get("systems_any") or 0) * 2 > T), None)
    x_full = next((t for t in turns if (by_turn[t].get("systems_full") or 0) * 2 > T), None)
    for t in turns:
        if t in key_turns or t in (x_dat, x_any, x_full) or t == turns[-1] \
           or by_turn[t]["selector_byte"]:
            show(by_turn[t])
    print(f"\ncrossings (>1/2 of T={T}): DAT_482fb at t={x_dat}; "
          f"systems_any at t={x_any}; systems_full at t={x_full}")
    max_dat = max(by_turn[t]["score_stars"] for t in turns)
    print(f"DAT_482fb max over trusted stream: {max_dat}/{T}")
    print()
    if armed:
        show(armed)
        print(f"SELECTOR ARMED first at t={armed['turn']} — pair with the "
              f"crossing rows above: armed below 2/3 of T discriminates "
              f">1/2 (vendor comment).")
        print("NEXT: bank in docs/re/score.md, upgrade campaign.cpp:738 if "
              "!= default, pin with a test.")
        return 0
    print("Selector never armed in any trusted observation.")
    if x_dat:
        print("DAT_482fb crossed half without arming — contradicts >1/2 "
              "IF DAT_482fb is the comparator's variable. Report whether an "
              "ending screen was visibly shown (you are the eyes; R13).")
    else:
        print(f"NOTE (t85b, multi-sitting capture): DAT_482fb never crossed "
              f"half (max {max_dat}/{T}) even though the owned-systems census "
              f"did (any@t={x_any}, full@t={x_full}). Consistent with the "
              f"comparator reading DAT_482fb and >1/2 NOT firing — but this "
              f"is CONSISTENCY, not a closing measurement: what DAT_482fb "
              f"actually tracks is itself unresolved (t85 calibration: "
              f"planets != stars). If you did NOT see a Control-victory "
              f"screen around your 26th colonization, say so — it supports "
              f"'>1/2 on DAT_482fb, and DAT_482fb lags/aggregates differently "
              f"than owned systems.'")
    return 1


if __name__ == "__main__":
    sys.exit(main())
