#!/usr/bin/env python3
"""r335_state_records.py — t335 STATE-RECORD FILE-VS-RAM CENSUS (zero capture).

Semantics implemented (all VERBATIM from work/r331_disasm.txt this iteration):
  parse loop 0x57f3e..0x57ff5, per window record (magic 0x12345678 @+0, NAME @+0x20):
    count = u32 scanned from resident `STATE <count> ...` line; count<=0 -> skip
    slot cursor ecx = win+0x6d+13*i:
      id==0: byte0=0; u32 @+1 = 0x315c4(NAME-token handle); scan fmt '%s %d %d %d'
             writes int2 -> cursor+0x9, int3 -> cursor+0xb (u32 writes OVERLAP:
             int3 lands at record bytes 11..14, spilling 2 B into the next slot)
      id==1: byte0=1; u16 index @+1 (0x1fe20); same two int stores
      id >1: assert 0x2a438 (eax=0 -> 0x76c79(msg) -> int3 0x2a424) then FALLS
             THROUGH to the same advance: byte0/+1 UNWRITTEN (stale)
    compactor fn 0x31690 (called by ALL THREE branches at 0x57fb4):
      v = WORD [win+0xa1];  if (i16)v >= 4: ASSERT + return (no copy, no ++);
      else dst = win+0x6d+13*v, src = cursor (13-byte movs), [win+0xa1] = v+1.
      At fresh boot v tracks i -> self-copy -> v == entries processed.
  SAVE-MEMBER MAPPING LAW (r1_slot.py): member address = B + 0x82bb0 + X.
  NEEDLE GATE before ANY ds: read: u32 turn at B+0x82bb0+0x12e10 in 1..4000 AND
  >=100 magic+NAME window records; failures counted, never read.
Truth side: the windows.txt copy resident IN THE SAVE (t333 law), parsed per
NAME block. Reports per-family (ids-all-in-{0,1} vs any-id>1) tag agreement.
Exit 0 = measured.
"""
import os, sys, struct, zipfile, glob, re, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import r1_slot as RS

MAGIC = b"\x78\x56\x34\x12"
STATE_OFF = 0x6d
STRIDE = 13
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
        recs = []
        for i in range(6):
            r = b + STATE_OFF + i * STRIDE
            recs.append(mem[r:r + STRIDE])
        out.append({
            "base": b, "name": name.decode("ascii", "replace"),
            "recs": recs,
            "a1": struct.unpack_from("<H", mem, b + 0xa1)[0],
            "type_gate": struct.unpack_from("<I", mem, b + 0x9f)[0] >> 16,
            "raw_9f_a4": mem[b + 0x9f:b + 0xa5],
        })
    return out


def resident_text_truth(mem):
    truth = {}
    pos = 0
    while True:
        m = re.compile(rb"NAME\s+([A-Za-z][A-Za-z0-9_]{1,23})").search(mem, pos)
        if not m:
            break
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
    a1_hist = collections.Counter()                 # [win+0xa1] vs text count
    a1_by_textcount = collections.defaultdict(collections.Counter)
    tag_family = collections.defaultdict(collections.Counter)  # family -> tags
    tag1_u32 = collections.Counter()                # u32 @+1 when tag==1
    tag0_u32_window = collections.Counter()         # tag==0 u32 points at magic?
    spill_tag = collections.Counter()               # slot1 tag after id>1 slot0
    gate_hist = collections.Counter()               # [win+0x9f]>>16
    family_seen = collections.Counter()
    samples_done = set()
    sample_names = ("BatModeWnd", "BatControlWnd", "RACECONTROLS", "RACE1")

    def family(ids):
        if not ids:
            return "count0_or_no_ids"
        if all(i <= 1 for i in ids):
            return "ids_in_0_1"
        return "any_id_gt1"

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
            truth = resident_text_truth(mem)
            for w in wins:
                gate_hist[w["type_gate"]] += 1
                a1_hist[w["a1"]] += 1
                t = truth.get(w["name"])
                fam = family(t[1]) if t else "no_text"
                family_seen[fam] += 1
                if t:
                    a1_by_textcount[t[0]][w["a1"]] += 1
                    tags = tuple(r[0] for r in w["recs"][:4])
                    tag_family[fam][tags] += 1
                    # spill probe: slot0 took the else-branch (id>1) -> its byte0
                    # stale; scan int3 wrote u32 at slot0+11 = bytes 11,12 of slot0
                    # and 0,1 of slot1. Record slot1 tag distribution per family.
                for r in w["recs"]:
                    u32 = struct.unpack_from("<I", r, 1)[0]
                    if r[0] == 1:
                        tag1_u32[u32] += 1
                    elif r[0] == 0 and u32 not in (0, 0xFFFFFFFF):
                        mb = u32 - 0x88
                        ok = 0 <= mb < len(mem) - 4 and mem[mb:mb + 4] == MAGIC
                        tag0_u32_window["magic" if ok else "not_magic"] += 1
                if w["name"] in sample_names and w["name"] not in samples_done:
                    samples_done.add(w["name"])
                    print(f"\nSAMPLE {w['name']} turn={turn} [win+0xa1]={w['a1']} "
                          f"type_gate={w['type_gate']} text={t}")
                    for i, r in enumerate(w["recs"]):
                        print(f"  slot{i} {r.hex()}  tag={r[0]} u32@1={struct.unpack_from('<I', r, 1)[0]:#x} "
                              f"u32@9={struct.unpack_from('<I', r, 9)[0] if len(r) >= 13 else '-'} "
                              f"tail@5={r[5:9].hex()}")

    print(f"\n[1] saves needle-verified={saves_ok} rejected={saves_reject}")
    print("\n[2] [win+0xa1] histogram:", dict(sorted(a1_hist.items())[:8]))
    print("    [win+0x9f]>>16 (fn 0x31690 gate) histogram:",
          dict(sorted(gate_hist.items())[:8]))
    print("\n[3] window-record families (by resident-text STATE ids):",
          dict(family_seen))
    print("\n[4] [win+0xa1] vs TEXT count (text_count -> {a1: n}):")
    for tc, c in sorted(a1_by_textcount.items()):
        print(f"    text_count={tc}: {dict(sorted(c.items()))}"
              + ("   <== a1==count" if set(c) == {tc} else ""))
    print("\n[5] slot tag tuples (4 slots) per family:")
    for fam, c in tag_family.items():
        print(f"    {fam}:")
        for tags, n in c.most_common(6):
            print(f"      tags={tags} n={n}")
    print("\n[6] u32@+1 when tag==1 (top):",
          [(hex(k), n) for k, n in tag1_u32.most_common(10)])
    print("[7] u32@+1 when tag==0: ", dict(tag0_u32_window))
    print("\nVERDICT saves=%d a1_hist=%s families=%s" %
          (saves_ok, dict(sorted(a1_hist.items())), dict(family_seen)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
