#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r1_playcap_watch.py OUT_DIR — LIVE collector for a played session (t85).

WHY THIS EXISTS: the ring is autosave=10 41-60 (10 s cadence law, docs/
BLOCKED.md runbook), so a slot is overwritten ~200 s after it is written.
r1_playcap.sh's inline tail runs only AFTER dosbox exits — by then the
victory crossing, the fire exchange, and the war declaration have all
rolled off. This collector parses each new slot the moment it lands and
appends one JSON line to OUT_DIR/live-timeline.jsonl. The offline
analyzers (r1_t85_relation/victory/combat) read the ring as the primary
source and this file as the durable record.

Writes (all under OUT_DIR, all bounded):
  live-timeline.jsonl  one line per (slot-file, mtime) — scalars + ships
                       + validated relation matrix. SCHEMA t257: 17 keys.
                       "day" is a PURE ALIAS of "turn" (t249b: the green
                       7-segment readout IS the zero-padded turn counter;
                       dword==turn intersects only the turn site 0x254e98
                       plus two heap addresses — no maintained day scalar at
                       any stable data offset, both sessions). Rows written
                       before t257 have 16 keys and no "day"; consumers must
                       treat day as optional (j.get("day", j["turn"])).
  watch.log            human-readable mirror

Usage: r1_playcap_watch.py OUT_DIR [--once]   (--once = single pass, for
post-hoc runs over already-captured dirs)
Exit 0 always unless OUT_DIR missing (2).
"""
import glob, json, os, struct, sys, time, zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_slot as S

import re
NAME_RE = re.compile(rb"[A-Za-z][A-Za-z '^_.\-]{2,19}")


def dosbox_alive():
    for p in os.listdir("/proc"):
        if not p.isdigit():
            continue
        try:
            with open(f"/proc/{p}/comm") as f:
                if f.read().strip() == "dosbox-x":
                    return True
        except OSError:
            pass
    return False


KEYS = {0x1c9: "DECLARE_WAR", 0x1cb: "ACCEPT_PEACE", 0x1cd: "PROPOSE_PEACE",
        0x1cf: "BREAK_ALLIANCE", 0x1d1: "ACCEPT_ALLIANCE",
        0x1d3: "PROPOSE_ALLIANCE", 0x1d5: "START_ATTITUDE"}


def relation(mem, M):
    """Full OQ-023 window (t85 revision): per §7 the state field is
    record+0x1c0+TARGET idx — a MATRIX, not a vector. (The first watcher
    version stored only the target-0 column; that is why the idle corpora
    'contained only value 1' — they sampled 5 cells out of n*(n-1).)
    atts[i][j] = attitude of i toward j (+0x1b2+2j); th[i] = race i's own
    DIPVALUES thresholds; tp = third-party matrix (&DAT_00012fd6)[i*0x1ee+j]."""
    n = struct.unpack_from("<I", mem, M + 0x13b96)[0] >> 16
    if n < 2 or n > 40:
        return None
    names = []
    for i in range(n):
        nb = mem[M + 0x12e17 + 0x1ee * i]
        nm = mem[M + 0x74590 + nb * 0x14: M + 0x74590 + nb * 0x14 + 20
                 ].split(b"\x00")[0]
        if not NAME_RE.fullmatch(nm):
            return None          # base validation failed — discard, never guess
        names.append(nm.decode("latin-1"))
    return dict(
        n=n, names=names,
        states=[[mem[M + 0x12e16 + 0x1ee * i + 0x1c0 + j] for j in range(n)]
                for i in range(n)],
        atts=[[struct.unpack_from("<h", mem, M + 0x12e16 + 0x1ee * i
                                   + 0x1b2 + 2 * j)[0] for j in range(n)]
              for i in range(n)],
        th=[{v: struct.unpack_from("<h", mem, M + 0x12e16 + 0x1ee * i + k)[0]
             for k, v in KEYS.items()} for i in range(n)],
        matrix=[[mem[M + 0x12fd6 + i * 0x1ee + j] for j in range(n)]
                for i in range(n)],
    )


def process(sp, mem, B):
    M = B + S.OFF
    d = S.read_slot(sp, mem, B)
    # t257: "day" is a pure alias of "turn" (t249b law, docs/re/selfplay.md
    # "t249b DAY-COUNTER PINNED"). No second RAM read — none exists.
    d["day"] = d["turn"]
    d["ships"] = [
        dict(slot=k, owner=v["owner"], state=v["state"], design=v["design"],
             xyz=[round(c, 4) for c in v["xyz"]])
        for k, v in enumerate(S.ship_records(mem, B))
    ]
    # raw typed window of every ship slot so the combat analyzer never needs
    # a field-meaning guess: stride 0x162 = 354 B = 177 u16 (verbatim window;
    # known offsets index directly: +0x10/0x54/0x58/0x9e/0xac/0x15a)
    base, n = S.ship_array_law(mem, B)
    d["ship_raw"] = {
        str(k): list(struct.unpack_from("<177H", mem, base + k * 0x162))
        for k in range(min(n, 0x6b))
    }
    d["relation"] = relation(mem, M)
    # t85 OQ-021 candidate variables. MEASURED on the user's own t478
    # campaign: DAT_000482fb stayed 1 while the player grew to 4 systems /
    # 5 planets => the [inferred] "DAT_482fb == player-owned star count" is
    # FALSE as stated. The session must therefore bank, per slot:
    #   systems_any   systems with >=1 player planet   (validated law)
    #   systems_full  systems where player owns EVERY planet record
    #                 (this equals 1 on the t478 slot == DAT_482fb — the
    #                  leading hypothesis, to be tested across a long run)
    #   planets       player planet count
    try:
        from r1_income_law import find_records
        star = {}
        for rec in find_records(mem):
            rb = rec[0]
            star.setdefault(mem[rb + 0x0c], []).append(mem[rb + 0x57])
        mine_any = [s for s, v in star.items() if 0 in v]
        mine_full = [s for s, v in star.items() if v and all(o == 0 for o in v)]
        d["systems_any"] = len(mine_any)
        d["systems_full"] = len(mine_full)
        d["planets_mine"] = sum(1 for v in star.values() if 0 in v)
        d["T_known"] = d["T"]
    except Exception as e:
        d["systems_error"] = repr(e)[:120]
    return d


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    out = sys.argv[1]
    once = "--once" in sys.argv
    no_exit = "--no-exit" in sys.argv
    if not os.path.isdir(out):
        print(f"harness-error: no out dir {out}")
        return 2
    root = os.getcwd()
    pay = S.load_payload(root)
    anch = S.anchors_cached(root, pay)
    jlp = os.path.join(out, "live-timeline.jsonl")
    seen = set()
    if os.path.isfile(jlp):        # t85: re-ingest NEVER duplicates lines
        for line in open(jlp):     # (restarts across sittings must be free)
            try:
                j0 = json.loads(line)
                seen.add((j0["file"], j0["file_mtime_ns"]))
            except Exception:
                pass
    jl = open(jlp, "a")
    lg = open(os.path.join(out, "watch.log"), "a")

    def emit(msg):
        print(msg, flush=True)
        lg.write(msg + "\n")
        lg.flush()

    # t85b: the jsonl-derived `seen` above is the ONLY dedup. An earlier
    # version re-assigned `seen = set()` here, which wiped it and re-emitted
    # every pre-existing ring slot on every restart (73k dup rows banked
    # across sittings before this fix). Do not reintroduce a reset.
    emit(f"watch: start {time.strftime('%H:%M:%S')} once={once} "
         f"({len(seen)} prior observations deduped)")
    while True:
        for sp in sorted(glob.glob(os.path.join(out, "save", "*.sav"))):
            st = os.stat(sp)
            key = (os.path.basename(sp), int(st.st_mtime_ns))
            if key in seen:
                continue
            seen.add(key)
            try:
                mem = zipfile.ZipFile(sp).read("Memory")
            except Exception as e:      # partial write race: re-check next tick
                if not once:
                    seen.discard(key)
                continue
            if len(mem) < 0x90000:
                continue
            B = S.base_of(mem, anch)
            if B is None:
                emit(f"  {key[0]}: no base vote (game not running?)")
                continue
            try:
                d = process(sp, mem, B)
            except Exception:
                import traceback, io
                tb = io.StringIO()
                traceback.print_exc(file=tb)
                emit(f"  {key[0]}: PROCESS ERROR (slot skipped):\n"
                     + tb.getvalue()[-400:])
                continue
            d["file_mtime_ns"] = key[1]
            d["wall"] = time.strftime("%H:%M:%S")
            jl.write(json.dumps(d) + "\n")
            jl.flush()
            rel = d.get("relation")
            nz = 0
            if rel:
                nz = sum(1 for row in rel["states"] for v in row if v)
            emit(f"  {key[0]} {d['wall']} t={d['turn']} "
                 f"SYSTEMS mine_any={d.get('systems_any')} "
                 f"full={d.get('systems_full')} planets={d.get('planets_mine')} "
                 f"| DAT_482fb={d['score_stars']}/{d['T']} "
                 f"sel={d['selector_byte']} ships={len(d['ships'])} "
                 f"rel_nonzero_cells={nz} "
                 + ("" if d["in_game"] else " [TITLE — untrusted]"))
        if once or (not no_exit and not dosbox_alive()):
            emit(f"watch: done {time.strftime('%H:%M:%S')} "
                 f"({len(seen)} slot files seen)")
            return 0
        time.sleep(5)


if __name__ == "__main__":
    sys.exit(main())
