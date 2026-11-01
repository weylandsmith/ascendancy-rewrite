#!/usr/bin/env python3
"""t249 S2: PIN THE HEADER-PLANETS COUNTER via the list-object hypothesis.

Static law (this session, Ghidra insn census operand '0x8c7', 20 hits):
u16 @obj+0x8c7 is a SCROLLABLE-LIST ITEM COUNT (add-routine FUN_00032d1c
increments at 0x32eb6, zeros at 0x325b5/0x33015, trap >0xff at 0x32d2d;
entries at obj+0xcb stride 8, entry ptr written at 0xcb+count*8).
FUN_00051684 reads u16[(u32[widget+0xab])+0x8c7] for the header PLANETS %d.

Instrument (heap-safe, unlike t248's fixed-offset intersection): per-slot,
enumerate u32 P with u16[P+0x8c7]==want, VALIDATE each P by list semantics:
entry k ptr P+0xcb+8k must point to a NAMED planet record (stride-0x7b
name-run anchored) whose NAME+0x33 owner == race. Report validated chain +
pointer sites of P-0xab (the widget+0xab slot).
"""
import struct, sys, zipfile, glob, os, re, collections
sys.path.insert(0, "os.path.dirname(os.path.abspath('.'))" if False else "scripts")
import r1_slot as S

STRIDE = 123; NAMEW = 19
NAME_RE = rb"[A-Z][A-Za-z]{2,}(?: [IVX]+)?\x00"

def load(path):
    mem = zipfile.ZipFile(path).read("Memory")
    B = S.base_of(mem, anch)
    return mem, B

def planet_index(mem):
    hits = set(m.start() for m in re.finditer(NAME_RE, mem))
    cands = [h for h in hits if all(h + i*STRIDE in hits for i in range(15))]
    def runlen(c):
        n = 0; p = c
        while p in hits: n += 1; p += STRIDE
        return n
    c = max(cands, key=runlen); base = c
    while base - STRIDE in hits: base -= STRIDE
    recs = {}
    for k in range(160):
        j = base + k*STRIDE
        raw = mem[j:j+NAMEW]
        if raw.strip(b"\x00") == b"": continue
        recs[j] = (raw.split(b"\x00")[0].decode(errors="replace"), mem[j+0x33])
    return base, recs

pay = S.load_payload("."); anch = S.anchors_cached(".", pay)

def probe(label, path, want, second_want=None):
    mem, B = load(path)
    OFF = 0x82bb0
    race = mem[B + OFF + 0x7458e]
    turn = struct.unpack_from("<I", mem, B + OFF + 0x12e10)[0]
    base, recs = planet_index(mem)
    n_mine = sum(1 for j, (nm, ow) in recs.items() if ow == race)
    print(f"== {label} ({os.path.basename(path)}) turn {turn} race {race} "
          f"named {len(recs)} count(owner==race) {n_mine} want {want}")
    # scan aligned u32 P: u16[P+0x8c7]==want, P plausible heap/linear
    cands = []
    for o in range(0, len(mem) - 0x8ff, 4):
        v = struct.unpack_from("<H", mem, o + 0x8c7)[0]
        if v == want:
            P = o
            if not (0x10000 < P < len(mem) - 0x8d0):
                continue
            cands.append(P)
    print(f"   raw candidates u16[P+0x8c7]=={want}: {len(cands)}")
    validated = []
    for P in cands:
        ok = bad = 0
        first_bad = None
        for k in range(want):
            e = struct.unpack_from("<I", mem, P + 0xc7 + k*8)[0]
            if e in recs and recs[e][1] == race:
                ok += 1
            else:
                bad += 1
                if first_bad is None:
                    first_bad = (k, hex(e), recs.get(e, None))
        if ok == want:
            validated.append(P)
            print(f"   VALIDATED P={P:#x} all {want} entries -> named "
                  f"race-{race} planet records")
        elif ok >= max(2, want//2) and len(validated) < 3:
            print(f"   partial  P={P:#x} ok {ok}/{want} first_bad {first_bad}")
    # widget anchor: pointer sites of P-0xab
    for P in validated:
        tgt = struct.pack("<I", P - 0xab)
        sites = [m.start() for m in re.finditer(re.escape(tgt), mem)]
        print(f"   ptr-sites of (P-0xab)={P-0xab:#x}: {len(sites)} -> "
              f"{[hex(s) for s in sites[:12]]}")
        for s in sites:
            dsx = s - B - OFF
            tag = "DATA-SEG" if 0 <= dsx < 0x20000 else "heap/other"
            print(f"      site {s:#x} dsx={dsx:#x} {tag}")
    # secondary want check at validated offsets (e.g. count==1 at t1254? no:
    # check the SAME P in the other slot handled by caller)
    return mem, B, validated

if __name__ == "__main__":
    slots = [s for s in sorted(glob.glob("work/r1/playcap/save/*.sav"),
                               key=os.path.getmtime) if os.path.getsize(s) > 200000]
    a = probe("t1086 ring", slots[-1], 60)
    c = probe("t1254 bank", "work/r1/bank-t1254/48.sav", 102)
