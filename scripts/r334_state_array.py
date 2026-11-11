#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r334_state_array.py — t334 STATE-ARRAY + ds:0x13b98 OFFLINE CENSUS (zero capture).

Measures the two claims _wip_t334.md S5/S8 rest on:
 (A) THE STATE LINE HAS A RUNTIME HOME: the parse loop 0x57f3e..0x57ff5 writes a
     per-WINDOW INLINE array at win+0x6d, stride 13, slot = BYTE flag + u32
     handle (`mov BYTE PTR [ecx],0/1` + `mov DWORD PTR [ecx+0x1],eax`, ecx += 0xd),
     slot count = the parsed STATE-line count. Checks per window record:
       - flags of the 4 slots vs the resident-text STATE count for the same name
       - whether each u32 handle points at a window record (magic+NAME law) and
         which NAME — i.e. IS THE HANDLE THE RESOLVED STATE TARGET WINDOW?
 (B) THE LOOP BOUND ds:0x13b98 (0x58ae8/0x58b26) — read as WORD at member address
     B + 0x82bb0 + 0x13b98 (r1_slot.py law: member address = B + 0x82bb0 + X for
     every obj1 data offset X — a self-correction this iteration: an earlier run
     used B + 0x13b98 and rejected 196/196 saves, which was MY mapping error, not
     a law change; the t333 "+0x88 delta is not constant" warning applies to
     pointer-value->member conversions, not to obj1 data offsets). Needle gate
     before ANY ds: read: u32 at B+0x82bb0+0x12e10 (DAT_00012e10 turn counter)
     in 1..4000 AND >= 100 magic+NAME window records; failures counted, not read.

Laws reused (not re-derived): magic u32 0x12345678 @rec+0x00 + RAW ASCII NAME
@rec+0x20; STATE grammar `STATE <count> <id>...` (t333, 123/123); NEVER
json-load the timeline. Exit 0 = measured.
"""
import os, sys, struct, zipfile, glob, re, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import r1_slot as RS

MAGIC = b"\x78\x56\x34\x12"
STATE_OFF = 0x6d
STRIDE = 13
SLOTS = 4
OFF = 0x82bb0
OFF_TURN = 0x12e10


def parse_windows(mem):
    out = []
    for mo in re.finditer(MAGIC, mem):
        b = mo.start()
        if b + 0xc0 > len(mem):
            continue
        name = mem[b + 0x20:b + 0x40].split(b"\x00")[0]
        if not (2 <= len(name) <= 24 and all(32 <= c < 127 for c in name)):
            continue
        w = {"base": b, "name": name.decode("ascii", "replace"), "slots": []}
        for i in range(SLOTS):
            r = b + STATE_OFF + i * STRIDE
            if r + STRIDE > len(mem):
                break
            flag = mem[r]
            h = struct.unpack_from("<I", mem, r + 1)[0]
            w["slots"].append((flag, h))
        w["table"] = struct.unpack_from("<I", mem, b + 0xab)[0]
        w["count"] = struct.unpack_from("<H", mem, b + 0xaf)[0]
        out.append(w)
    return out


def resident_text_truth(mem):
    """Parse the windows.txt copy resident IN THE SAVE (t333: text verbatim in
    saves) straight out of the Memory member: find each `NAME <X>` ... block and
    its first STATE line before the next NAME."""
    truth = {}
    pos = 0
    cur = None
    while True:
        m = re.compile(rb"NAME\s+([A-Za-z][A-Za-z0-9_]{1,23})").search(mem, pos)
        if not m:
            break
        # require the token to be followed by whitespace (avoid NAME fragments)
        after = mem[m.end():m.end() + 1]
        if after and after not in (b" ", b"\r", b"\t"):
            pos = m.end()
            continue
        name = m.group(1).decode("ascii")
        seg = mem[m.end():m.end() + 4000]
        nxt = re.search(rb"\bNAME\s+", seg)
        if nxt:
            seg = seg[:nxt.start()]
        s = re.search(rb"STATE\s+(\d+)((?:\s+\d+)*)", seg)
        if s:
            truth[name] = (int(s.group(1)),
                           [int(x) for x in s.group(2).split()])
        cur = name
        pos = m.end()
    return truth


def main():
    dirs = []
    prod = os.path.join(ROOT, "work", "r1", "playcap", "save")
    if os.path.isdir(prod):
        dirs.append(prod)
    for pat in ("dbg-t332-*/save", "t299-leg-*/save", "dbg-t331-*/save"):
        for d in sorted(glob.glob(os.path.join(ROOT, "work", "r1", pat))):
            if d not in dirs:
                dirs.append(d)
    dirs = dirs[:20]
    if not dirs:
        print("HARNESS: no save dirs")
        return 2

    pay = RS.load_payload(ROOT)
    anch = RS.anchors_cached(ROOT, pay)

    saves_ok = saves_reject = 0
    bound_hist = collections.Counter()
    bound_by_turn = []
    flag_hist = collections.Counter()          # (n_slots_flag_set) vs text count
    match_rows = collections.Counter()         # count==text_count : yes/no
    handle_is_window = collections.Counter()
    handle_names = collections.Counter()
    sample_done = set()
    nonzero_slots_windows = 0

    for d in dirs:
        files = sorted(f for f in os.listdir(d) if f.endswith(".sav"))[:12]
        for f in files:
            try:
                mem = zipfile.ZipFile(os.path.join(d, f)).read("Memory")
            except Exception:
                continue
            B = RS.base_of(mem, anch)
            wins = parse_windows(mem) if B is not None else []
            if B is None or not (1 <= struct.unpack_from("<I", mem, B + OFF + OFF_TURN)[0] <= 4000) \
                    or len(wins) < 100:
                saves_reject += 1
                continue
            saves_ok += 1
            turn = struct.unpack_from("<I", mem, B + OFF + OFF_TURN)[0]
            bv = struct.unpack_from("<H", mem, B + OFF + 0x13b98)[0]
            bound_hist[bv] += 1
            bound_by_turn.append((turn, bv))

            truth = resident_text_truth(mem)
            for w in wins:
                flags = tuple(fl for fl, _ in w["slots"])
                nset = sum(1 for fl in flags if fl)
                flag_hist[flags] += 1
                if nset:
                    nonzero_slots_windows += 1
                t = truth.get(w["name"])
                if t is not None:
                    match_rows[(t[0], nset)] += 1
                for fl, h in w["slots"]:
                    if fl and h not in (0, 0xFFFFFFFF):
                        mb = h - 0x88
                        ok = 0 <= mb < len(mem) - 0x40 and mem[mb:mb + 4] == MAGIC
                        handle_is_window["points_at_magic" if ok else "not_magic"] += 1
                        if ok:
                            hn = mem[mb + 0x20:mb + 0x40].split(b"\x00")[0]
                            handle_names[hn.decode("ascii", "replace")] += 1
                        if ok and w["name"] not in sample_done and w["name"] in truth:
                            sample_done.add(w["name"])
                            print(f"\n  SAMPLE {w['name']} turn={turn} slots="
                                  f"{[(hex(h), fl) for fl, h in w['slots']]} "
                                  f"text STATE={truth[w['name']]} "
                                  f"(+0xab={hex(w['table'])} +0xaf={w['count']})")
                            for fl, h in w["slots"]:
                                if fl and h not in (0, 0xFFFFFFFF):
                                    mb = h - 0x88
                                    if 0 <= mb < len(mem) - 0x40 and mem[mb:mb+4] == MAGIC:
                                        hn = mem[mb+0x20:mb+0x40].split(b"\x00")[0].decode("ascii","replace")
                                        print(f"      handle {hex(h)} -> window {hn}")

    print(f"\n[1] saves needle-verified={saves_ok} rejected={saves_reject}")
    print("[2] WORD ds:0x13b98 histogram (needle-verified saves only):")
    for v, n in sorted(bound_hist.items()):
        print(f"    ds:0x13b98 = {v:5d}  saves={n}")
    if bound_by_turn:
        print(f"    turn range covered {min(t for t,_ in bound_by_turn)}.."
              f"{max(t for t,_ in bound_by_turn)}")

    print("\n[3] win+0x6d slot-FLAG tuples (4 slots) histogram:")
    for v, n in flag_hist.most_common(12):
        print(f"    flags={v}  windows={n}")
    print(f"    windows with >=1 set slot: {nonzero_slots_windows}")

    print("\n[4] resident-text STATE count vs set-slot count (text_count, nset):")
    tot = sum(match_rows.values())
    agree = sum(n for (tc, ns), n in match_rows.items() if tc == ns)
    for k, n in sorted(match_rows.items(), key=lambda kv: -kv[1])[:15]:
        print(f"    text={k[0]} set_slots={k[1]}  n={n}"
              + ("   <== AGREE" if k[0] == k[1] else ""))
    print(f"    agreement: {agree}/{tot}")

    print("\n[5] set-slot u32 handles: do they point at window records?")
    for k, n in handle_is_window.items():
        print(f"    {k}: {n}")
    print("    top target window names:")
    for k, n in handle_names.most_common(15):
        print(f"      {k}: {n}")
    print("\nVERDICT: saves=%d ds13b98_hist=%s state_array_slots_nonzero=%d"
          % (saves_ok, dict(bound_hist), nonzero_slots_windows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
