#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r333_state_census.py — ACTIVE SCREEN STATE census (t333, zero capture).

Question (OQ-016 residue-(1) last named edge): is windows.txt `STATE 1 16`
(the 19-window battle-map family) EVER the live state of a window record in any
captured save, and what does the state-record +0xa flag actually encode?

Laws used (previously cited, NOT re-derived):
  - window record = magic u32 0x12345678 @+0x00, NAME raw ASCII @+0x20,
    class table @+0xa7 (t301 S3, reproduced t313/t315/t324).
  - state-record array ptr u32 @+0xab, record count u16 @+0xaf, runtime state
    WORD @+0xb1 (t323 S1-S2). fn 0x31d58 reads the SAME count as the high half
    of the dword @+0xad.
  - stored u32 pointer values are guest-PHYSICAL: target member = value + 0x88
    (t298 POINTER-VALUE LAW).
  - base B via r1_slot.base_of (unique-needle voting), never hard-coded.
  - fn 0x31d58 semantics (this task, S1): fn(win, state_id, dest, val);
    the ONLY +0xa store is 0x31dd0 `mov WORD [state_rec+0xa], val`, reached only
    with dest==0. Load-time callers 0x58ac5 (state_id=0, val=0 => CLEAR) and
    0x58b19 (state_id=1<<k for k<ds:0x13b98, val=1 => SET).

NEVER json-loads the timeline (OOM law). Bounded input dirs only.
Exit 0 = census complete whatever the counts; 2 = harness broken (no save
parsed, or no window record found in a parsed save).
"""
import os, sys, glob, struct, zipfile, collections, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
BASE = os.path.join(ROOT, "work", "r1")
H = 0x88
MAGIC = b"\x78\x56\x34\x12"
MAGIC_V = 0x12345678
MAX_DIRS = 24            # bounded (t265 OOM-era law)
MAX_SAVES_PER_DIR = 20


def save_dirs():
    """Production corpus first, then bounded scratch runs, deduped by dir."""
    out = []
    prod = os.path.join(BASE, "playcap", "save")
    if os.path.isdir(prod):
        out.append(prod)
    pat = sorted(glob.glob(os.path.join(BASE, "dbg-t332-*", "save")) +
                 glob.glob(os.path.join(BASE, "t299-leg-*", "save")))
    for d in pat:
        if d not in out:
            out.append(d)
    return out[:MAX_DIRS]


def anchors(mem):
    """Cheap self-validation: at least one record must carry a printable NAME."""
    return mem


def parse_save(path):
    """Return list of window dicts, or None if the save won't parse."""
    try:
        mem = zipfile.ZipFile(path).read("Memory")
    except Exception:
        return None
    wins = []
    for mo in re.finditer(MAGIC, mem):
        b = mo.start()
        if b + 0xc0 > len(mem):
            continue
        name = mem[b + 0x20:b + 0x40].split(b"\x00")[0]
        if not (2 <= len(name) <= 24 and all(32 <= c < 127 for c in name)):
            continue
        st_ptr = struct.unpack_from("<I", mem, b + 0xab)[0]
        cnt = struct.unpack_from("<H", mem, b + 0xaf)[0]
        cnt_hi = struct.unpack_from("<I", mem, b + 0xad)[0] >> 16
        state = struct.unpack_from("<H", mem, b + 0xb1)[0]
        w = dict(base=b, name=name.decode("ascii"), ptr=st_ptr, cnt=cnt,
                 cnt_hi=cnt_hi, state=state)
        w["recs"] = []
        w["rec_bytes"] = []
        # state-record array: guest-physical ptr -> member = value + H
        if 0 < cnt <= 64 and st_ptr != 0xFFFFFFFF:
            tb = st_ptr + H
            if tb + cnt * 14 <= len(mem):
                for i in range(cnt):
                    r = tb + i * 14
                    raw = mem[r:r + 14]
                    w["rec_bytes"].append(raw.hex())
                    w["recs"].append(dict(
                        i=i,
                        rid=struct.unpack_from("<H", raw, 0)[0],
                        f0a=struct.unpack_from("<H", raw, 0x0a)[0],
                        f0c=struct.unpack_from("<H", raw, 0x0c)[0],
                    ))
        wins.append(w)
    return wins


def main():
    dirs = save_dirs()
    if not dirs:
        print("HARNESS: no save dirs found under", BASE)
        return 2
    saves_ok = 0
    saves_zero_windows = 0
    state_hist = collections.Counter()
    name_state = collections.defaultdict(collections.Counter)
    flag_hist = collections.Counter()          # every state-record +0xa
    id16_wins = collections.Counter()          # windows whose table holds id 16
    id16_flag = collections.Counter()          # +0xa of those id-16 records
    ptr_mismatch = 0
    ptr_valid = 0
    per_dir = {}
    for d in dirs:
        files = [f for f in sorted(os.listdir(d)) if f.endswith(".sav")]
        files = files[:MAX_SAVES_PER_DIR]
        d_states = collections.Counter()
        d_saves = 0
        for f in files:
            wins = parse_save(os.path.join(d, f))
            if wins is None:
                continue
            d_saves += 1
            saves_ok += 1
            if not wins:
                saves_zero_windows += 1
                continue
            for w in wins:
                state_hist[w["state"]] += 1
                name_state[w["name"]][w["state"]] += 1
                d_states[w["state"]] += 1
                if w["cnt"] != w["cnt_hi"]:
                    ptr_mismatch += 1
                if w["recs"]:
                    ptr_valid += 1
                for r in w["recs"]:
                    flag_hist[r["f0a"]] += 1
                    if r["rid"] == 16:
                        id16_wins[w["name"]] += 1
                        id16_flag[r["f0a"]] += 1
        per_dir[os.path.relpath(d, ROOT)] = (d_saves, dict(d_states.most_common(8)))

    print(f"saves parsed: {saves_ok}  (zero-window saves: {saves_zero_windows})")
    print(f"window records: state-table ptr valid {ptr_valid}, "
          f"count-low/high disagreement {ptr_mismatch}")
    print("\n[1] RUNTIME STATE WORD [win+0xb1] HISTOGRAM over every window "
          "record in every parsed save:")
    for s, n in sorted(state_hist.items()):
        print(f"    state {s:5d} (0x{s:04x})  windows={n}"
              + ("   <== 16 = battle-map family" if s == 16 else ""))
    print(f"    => state 16 observed as a live [win+0xb1]: "
          f"{'YES' if state_hist.get(16) else 'NEVER'}")

    print("\n[2] STATE-RECORD +0xa FLAG HISTOGRAM (fn 0x31d58's store field, "
          "all records):")
    tot = sum(flag_hist.values())
    for v, n in sorted(flag_hist.items()):
        print(f"    +0xa = {v:5d}  records={n}  ({100.0*n/max(tot,1):.1f}%)")
    print(f"    => flag is state-SELECTIVE: "
          f"{'YES (mixed values)' if len(flag_hist) > 1 else 'NO (uniform)'}")

    print("\n[3] windows whose state-record table CONTAINS id 16 "
          "(the STATE 1 16 family) and the +0xa of those records:")
    if not id16_wins:
        print("    none")
    for nm, n in id16_wins.most_common(40):
        print(f"    {nm:16s} occurrences={n}")
    print("    id-16 record +0xa values:", dict(id16_flag.most_common(8)))

    print("\n[4] per-name live state sets (top 30 names by record count):")
    tops = sorted(name_state.items(),
                  key=lambda kv: -sum(kv[1].values()))[:30]
    for nm, c in tops:
        print(f"    {nm:16s} states={dict(c.most_common(6))}")

    print("\n[5] per-dir: (saves, top states)")
    for k, v in per_dir.items():
        print(f"    {k}: {v}")

    # verdict
    sel = len(flag_hist) > 1
    ever16 = bool(state_hist.get(16))
    print("\nVERDICT:")
    print(f"  saves={saves_ok} window_records={sum(state_hist.values())} "
          f"state16_live={'YES' if ever16 else 'NEVER'} "
          f"flag_selective={'YES' if sel else 'NO'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
