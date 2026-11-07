#!/usr/bin/env python3
"""r333b_state_layout.py — t333 STATE-DECODING measurement (zero capture).

Why this script exists (supersedes r333_state_census.py's field map):
  Verbatim disassembly of the state machinery (work/r331_disasm.txt) pins the
  window-record layout as INTERLEAVED u16 pairs, and the previous census read
  the count from the wrong half. The reads, verbatim:

    fn 0x31d58 0x31d71  mov ebx,DWORD PTR [esi+0xad] ; sar ebx,0x10  -> COUNT
                         (dword@0xad = (word@0xad, word@0xaf); sar 16 => word@0xaf)
    fn 0x31d58 0x31d7e  mov ebx,DWORD PTR [esi+0xab]   -> TABLE PTR
    fn 0x31d58 0x31d84  cmp di,WORD PTR [edx+ebx*1]    -> record WORD +0x0 = STATE ID
    fn 0x31d58 0x31dd0  mov WORD PTR [eax+0xa],dx      -> record +0xa = FLAGS
    fn 0x31f30 0x31f37  cmp si,WORD PTR [eax+0xb1]     -> CURRENT INDEX
    fn 0x31f30 0x31f44  cmp si,WORD PTR [eax+0xaf]     -> assert if idx >= COUNT
    fn 0x31f30 0x31f5e  mov edx,DWORD PTR [ecx+0xaf] ; sar edx,0x10 -> word@0xb1
    fn 0x31f30 0x31faf  mov WORD PTR [ecx+0xb1],si     -> the switcher
    fn 0x32100 0x3224c  mov edx,DWORD PTR [esi+0xab] ...
                       movsx ecx,WORD PTR [edx+eax*2]  -> ecx = STATE ID of hit rec
                       mov eax,0x7a35c; mov edx,[esi+0x63]; call 0x56ca4

  => [win+0xab] TABLE PTR (u32), [win+0xaf] COUNT (u16), [win+0xb1] CURRENT
     RECORD INDEX (u16), records stride 14 with WORD +0 = STATE ID, WORD +0xa
     = FLAGS (bit0 present, bit1 current, bit2 toggled), WORD +0xc = shape size.
  => "Active screen state" for a window = TABLE[current].ID, NOT [win+0xb1].

windows.txt STATE-line grammar (verified this iteration):
    STATE <count> <id> [<id> ...]     e.g. "STATE 3 1 7 13" (RACECONTROLS:418)
                                      e.g. "STATE 1 16"    (BatModeWnd:1180)

Laws reused (not re-derived): magic u32 0x12345678 @+0x00 + RAW ASCII NAME @+0x20;
stored pointer values are guest-PHYSICAL, target member = value + 0x88.
NEVER json-loads the timeline (OOM law). Bounded dirs only. Exit 0 = measured.
"""
import os, sys, struct, zipfile, collections, glob, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = 0x88
MAGIC = b"\x78\x56\x34\x12"
MAX_DIRS = 26
MAX_SAVES_PER_DIR = 20
STRIDE = 14

# windows.txt ground truth: name -> list of state ids declared by its STATE line
def windows_txt_truth(path):
    truth = {}
    if not os.path.exists(path):
        return truth
    lines = open(path, "rb").read().decode("latin-1").splitlines()
    cur = None
    for ln in lines:
        m = re.match(r"\s*NAME\s+(\S+)", ln)
        if m:
            cur = m.group(1)
            continue
        s = re.match(r"\s*STATE\s+(-?\d+)((?:\s+-?\d+)*)", ln)
        if s and cur:
            n = int(s.group(1))
            ids = [int(x) for x in s.group(2).split()]
            truth[cur] = (n, ids)
    return truth


def parse_windows(mem):
    out = []
    for mo in re.finditer(MAGIC, mem):
        b = mo.start()
        if b + 0xc0 > len(mem):
            continue
        name = mem[b + 0x20:b + 0x40].split(b"\x00")[0]
        if not (2 <= len(name) <= 24 and all(32 <= c < 127 for c in name)):
            continue
        w = dict(base=b, name=name.decode("ascii", "replace"))
        w["cls"] = struct.unpack_from("<I", mem, b + 0xa7)[0]
        w["table"] = struct.unpack_from("<I", mem, b + 0xab)[0]
        w["count"] = struct.unpack_from("<H", mem, b + 0xaf)[0]
        w["cur"] = struct.unpack_from("<H", mem, b + 0xb1)[0]
        w["b7"] = mem[b + 0xb7]
        w["b9"] = mem[b + 0xb9]
        w["recs"] = []
        tb = w["table"] + H if w["table"] not in (0, 0xFFFFFFFF) else None
        if tb is not None and 0 < w["count"] <= 64 and tb + w["count"] * STRIDE <= len(mem):
            for i in range(w["count"]):
                r = tb + i * STRIDE
                raw = mem[r:r + STRIDE]
                w["recs"].append(dict(
                    i=i,
                    sid=struct.unpack_from("<H", raw, 0x0)[0],
                    x0=struct.unpack_from("<H", raw, 0x2)[0],
                    y0=struct.unpack_from("<H", raw, 0x4)[0],
                    x1=struct.unpack_from("<H", raw, 0x6)[0],
                    fl=struct.unpack_from("<H", raw, 0xa)[0],
                    sz=struct.unpack_from("<H", raw, 0xc)[0],
                ))
        out.append(w)
    return out


def main():
    truth = windows_txt_truth(os.path.join(ROOT, "extracted", "ascend00", "windows.txt"))
    print(f"windows.txt STATE-line truth loaded: {len(truth)} windows declared")

    dirs = []
    prod = os.path.join(ROOT, "work", "r1", "playcap", "save")
    if os.path.isdir(prod):
        dirs.append(prod)
    for pat in ("dbg-t332-*/save", "t299-leg-*/save", "dbg-t331-*/save"):
        for d in sorted(glob.glob(os.path.join(ROOT, "work", "r1", pat))):
            if d not in dirs:
                dirs.append(d)
    dirs = dirs[:MAX_DIRS]
    if not dirs:
        print("HARNESS: no save dirs")
        return 2

    saves = 0
    total_recs = 0
    active_sid = collections.Counter()        # TABLE[cur].sid histogram
    curidx_hist = collections.Counter()       # raw [win+0xb1] histogram
    flag_hist = collections.Counter()
    id16_active = collections.Counter()       # windows declaring id 16: is it ACTIVE?
    id16_resident = collections.Counter()
    table_null = collections.Counter()        # declaring windows with NULL table
    count_mismatch = collections.Counter()    # runtime count vs windows.txt count
    name_rows = collections.defaultdict(collections.Counter)
    sample_printed = set()

    for d in dirs:
        files = sorted(f for f in os.listdir(d) if f.endswith(".sav"))[:MAX_SAVES_PER_DIR]
        for f in files:
            try:
                mem = zipfile.ZipFile(os.path.join(d, f)).read("Memory")
            except Exception:
                continue
            saves += 1
            for w in parse_windows(mem):
                curidx_hist[w["cur"]] += 1
                if w["table"] in (0, 0xFFFFFFFF):
                    table_null[w["name"]] += 1
                for r in w["recs"]:
                    total_recs += 1
                    flag_hist[r["fl"]] += 1
                    if r["sid"] == 16:
                        id16_resident[w["name"]] += 1
                        if r["i"] == w["cur"]:
                            id16_active[w["name"] + "|ACTIVE"] += 1
                        else:
                            id16_active[w["name"] + "|inert"] += 1
                if w["recs"]:
                    a = w["recs"][w["cur"]]["sid"] if w["cur"] < len(w["recs"]) else None
                    active_sid[a] += 1
                    name_rows[w["name"]][a] += 1
                if w["name"] in truth and w["recs"]:
                    count_mismatch[(w["name"], w["count"], truth[w["name"]][0],
                                    tuple(sorted(r["sid"] for r in w["recs"])) ==
                                    tuple(sorted(truth[w["name"]][1])))] += 1
                if w["name"] in ("BatControlWnd", "BatModeWnd", "NEXTTURNCONT",
                                 "COSMOSWnd", "RACECONTROLS") and w["recs"] \
                        and w["name"] not in sample_printed:
                    sample_printed.add(w["name"])
                    print(f"\n  SAMPLE {w['name']} member={hex(w['base'])} "
                          f"cls={hex(w['cls'])} table={hex(w['table'])} "
                          f"(->member {hex(w['table']+H) if w['table'] not in (0,0xFFFFFFFF) else 'NULL'}) "
                          f"count={w['count']} cur={w['cur']} +0xb7={w['b7']} +0xb9={w['b9']}")
                    for r in w["recs"][:12]:
                        star = " <== CURRENT" if r["i"] == w["cur"] else ""
                        print(f"      rec[{r['i']:2d}] sid={r['sid']:3d} "
                              f"rect=({r['x0']},{r['y0']})-({r['x1']},?) "
                              f"flags={r['fl']} size={r['sz']}{star}")

    print("\n[1] [win+0xb1] RAW WORD histogram (this is an INDEX, not a state id):")
    for v, n in sorted(curidx_hist.items())[:20]:
        print(f"    +0xb1 = {v:5d}  windows={n}")

    print("\n[2] ACTIVE STATE ID per window = TABLE[[win+0xb1]].sid, over every "
          "window with a decodable table:")
    tot = sum(active_sid.values())
    for v, n in sorted(active_sid.items(), key=lambda kv: -kv[1])[:25]:
        mark = "   <== 16 = battle-map family ACTIVE" if v == 16 else ""
        print(f"    active sid {v}  windows={n} ({100.0*n/max(tot,1):.1f}%){mark}")
    print(f"    => state id 16 EVER measured ACTIVE: "
          f"{'YES' if active_sid.get(16) else 'NEVER'}")

    print("\n[3] windows DECLARING state id 16 (windows.txt): resident vs active:")
    if not id16_resident:
        print("    none of the 20 state-16 windows has a DECODABLE state table "
              "in any parsed save")
    for k, n in id16_active.most_common(30):
        print(f"    {k}: {n}")

    print("\n[4] state-record FLAGS (+0xa) histogram over %d records:" % total_recs)
    for v, n in sorted(flag_hist.items())[:16]:
        bits = "".join(str((v >> k) & 1) for k in range(4))
        print(f"    +0xa = {v:5d} (bits0-3={bits})  records={n}")

    print("\n[5] windows.txt count vs runtime count (name, rt_count, txt_count, ids_match):")
    mm = [k for k in count_mismatch]
    if not mm:
        print("    no window had BOTH a decodable table and a windows.txt STATE line")
    for k in mm[:20]:
        print(f"    {k[0]:16s} runtime_count={k[1]:3d} txt_count={k[2]:3d} ids_match={k[3]}  n={count_mismatch[k]}")

    print("\n[6] window names with NULL/absent state table (top 25):")
    for k, n in table_null.most_common(25):
        star = " *" if k in truth else ""
        print(f"    {k:16s} null_table={n}{star}")

    print("\nVERDICT:")
    print(f"  saves={saves} window_records={sum(curidx_hist.values())} "
          f"state_records={total_recs}")
    print(f"  state16_active={'YES' if active_sid.get(16) else 'NEVER'}  "
          f"state16_resident_in_decodable_table={'YES' if id16_resident else 'NO'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
