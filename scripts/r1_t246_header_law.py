#!/usr/bin/env python3
"""t246: verify the PLANETALLOC header law decoded from the binary at
0x51685..0x517c0 (getter(151) call site 0x51798).

LAW (static, disasm-cited, work/ascend_restored.bin):
  count loop 0x516a4..0x516e0:
    eax = 0x13bc5 (data img, 0x60-stride table), bound si = WORD ds:0x16145
    test: BYTE[eax+0x14] == (1 << BYTE ds:0x7458e)      [sole-owner bitmask]
    exclusion (0x516d1): skip entry whose ADDRESS equals
      DWORD[0x12e1d + race*0x1ee]  (race record +7 dword)
    -> ebx counts, formatted via getter(151)
       "%s  (%d Planet%s Occupied, %d System%s Controlled)"
    second count comes from WORD[ui_obj+0x8c7] (0x5172e), NOT this loop.
Addresses follow the slot law: member addr = B + 0x82bb0 + X (r1_slot.py);
runtime entry address = B + OFF + 0x13bc5 + i*0x60 (the cmp compares against
a stored pointer, which lives in runtime space).

Observed live (t244 screenshot): "Chamachies (60 Planets Occupied,
26 Systems Controlled)" at t=1086, while the ring's score walk gives
planets=26 / systems_any=26 for the same turn. This script measures whether
the loop reproduces 60.
"""
import zipfile, glob, os, struct, sys
sys.path.insert(0, "scripts")
import r1_sav_scan as SS
import r1_slot as S

OFF = 0x82bb0

def analyze(path, mem, B, label):
    race = mem[B + OFF + 0x7458e]
    T = struct.unpack_from("<H", mem, B + OFF + 0x16145)[0]
    excl = struct.unpack_from("<I", mem, B + OFF + 0x12e1d + race * 0x1ee)[0]
    base_rt = B + OFF + 0x13bc5
    hist = {}
    sole = 0; sole_excl = 0; bitset = 0
    for i in range(T):
        e_rt = base_rt + i * 0x60
        b = mem[e_rt + 0x14]
        hist[b] = hist.get(b, 0) + 1
        if b == (1 << race):
            sole += 1
            if e_rt != excl:
                sole_excl += 1
        if (b >> race) & 1:
            bitset += 1
    turn = struct.unpack_from("<I", mem, B + OFF + 0x12e10)[0]
    print(f"[{label}] {os.path.basename(path)} turn={turn} race={race} T={T} "
          f"excl_ptr={hex(excl)}")
    print(f"   owner-byte hist: {sorted(hist.items(), key=lambda kv:-kv[1])[:8]}")
    print(f"   sole-owner(==1<<race): {sole}   after exclusion: {sole_excl}   "
          f"bit-set(>= co-own): {bitset}")
    return turn, sole, sole_excl, bitset

def main():
    pay = S.load_payload(".")
    anch = S.anchors_cached(".", pay)
    slots = S.slots_by_mtime("work/r1/playcap")
    if not slots:
        print("no slots"); return 1
    # freshest slot (live game) + one slot near t=1086 if present
    targets = [("freshest", slots[-1])]
    for sp in slots:
        try:
            mem = zipfile.ZipFile(sp).read("Memory")
            B = S.base_of(mem, anch)
            if B and struct.unpack_from("<I", mem, B + OFF + 0x12e10)[0] == 1086:
                targets.append(("t1086", sp))
                break
        except Exception:
            continue
    for label, sp in targets:
        mem = zipfile.ZipFile(sp).read("Memory")
        B = S.base_of(mem, anch)
        if not B:
            print(f"[{label}] no base vote"); continue
        analyze(sp, mem, B, label)

sys.exit(main())
