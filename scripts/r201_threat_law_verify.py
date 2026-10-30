#!/usr/bin/env python3
"""t201 — VERIFY THREAT-BYTE LAWS (corrected control-flow reading).

From FUN_00038ba4 recalc disasm (work/t201_recalc_scan.txt, verbatim):
  loop over slots ebp < word[rec+0x1a] (sys cap):
    cl = slot byte1 (item); esi = slotptr+edx (slot base)
    cl==0xff (empty) -> 0x38c4d branch
    di = word[slot+2] (slot flags); bit0 (0x38cab) = ACTIVE
      ACTIVE  -> sums item IND/RES/PROS; then @0x38d23:
                 word[item*0x28+0x73e46] (item FLAGS) & 4 -> inc [esp+0x24]
      NOT act -> @0x38c07: cl==0x17 skip; slotflag&2 skip; itemflag&0x40
                 skip; else accumulate item UPOP (cap contribution)
      (0x38c4d free/null branch: ebp>=cap -> inc [esp+0xc]; else
                 itemflag&8 skip; null-item count; ...)
  ENTRY: t58 == t59 == 0 ALWAYS (xored @0x38baf then stored BOTH locals
  0x38bd0/0x38bd8; no reload of old values).
  EXITS: byte[rec+0x58]=al from [esp+0x24] @0x38ef7;
         byte[rec+0x59]=al from [esp+4]  @0x38efe.
Hypotheses to test against the corpus (20 saves x 145 recs):
  H58: rec+0x58 == #{ACTIVE slots (word[slot+2]&1) whose item itemflag&4}
  H59: rec+0+0x59 == #{items in slots (any state) with itemflag&8}
Item flags: LIVE item table member B+0x82bb0+0x73e40+0x28*item +6 (u16;
OQ-014 field map FLAGS u16@+6). Slot ptr sys+0x10 (j-0x14 member=ptr+0x88).
RC=0 always.
"""
import os, sys, re, struct, zipfile, collections
sys.path.insert(0, "/home/hrethric/projects/ascendancy/scripts")
from r1_sav_scan import build_anchors, find_base

ROOT = "/home/hrethric/projects/ascendancy"
RUN = os.path.join(ROOT, "work/r1/playcap")
PAY = os.path.join(ROOT, "work/ascend_payload.bin")
PLANET_P0 = 0x26D07B
STRIDE = 123
NAME_RE = rb"[A-Z][A-Za-z]{2,}(?: [IVX]+)?\x00"


def main():
    pay = open(PAY, "rb").read()
    anch = build_anchors(pay)
    ok58 = ok59 = ok59b = tot = bad = 0
    flag_hist = collections.Counter()
    ex = []
    for f in sorted(os.listdir(os.path.join(RUN, "save"))):
        if not f.endswith(".sav"):
            continue
        mem = zipfile.ZipFile(os.path.join(RUN, "save", f)).read("Memory")
        votes, _ = find_base(mem, anch)
        if not votes:
            continue
        H = votes.most_common(1)[0][0] - 0x1BF450
        B = 0x1BF450 + H
        n = 0
        while True:
            j = PLANET_P0 + n * STRIDE + H
            if j >= len(mem) or mem[j] == 0 or not re.match(NAME_RE, mem[j:j+40]):
                break
            n += 1
        for k in range(n):
            j = PLANET_P0 + k * STRIDE + H
            sp = struct.unpack_from("<I", mem, j - 0x14)[0]
            cap = struct.unpack_from("<H", mem, j - 0x0A)[0]   # sys+0x1a
            if not (512 < sp < 0x4000000) or not (0 < cap <= 83):
                continue
            sl = sp + 0x88
            t58 = t59 = t59b = 0
            for i in range(cap):
                base = sl + 4 * i
                item = mem[base + 1]
                if item == 0xff:
                    continue
                sflags = struct.unpack_from("<H", mem, base + 2)[0]
                iflag = struct.unpack_from("<H", mem,
                        B + 0x82BB0 + 0x73E40 + 0x28 * item + 6)[0]
                if sflags & 1:                       # ACTIVE slot
                    if iflag & 4:
                        t58 += 1
                    elif iflag & 8:
                        t59 += 1                     # je 0x38be5 path
                    if iflag & 8:
                        t59b += 1                    # variant: any ACTIVE &8
                else:
                    pass
            tot += 1
            a, b = mem[j + 0x34], mem[j + 0x35]
            ok58 += (a == t58)
            ok59 += (b == t59)
            ok59b += (b == t59b)
            if (a != t58 or b != t59) and len(ex) < 10:
                ex.append((f, k, (a, b), (t58, t59)))
    print(f"recs checked {tot}")
    print(f"H58 (active-slots flag4 count) agreement: {ok58}/{tot}")
    print(f"H59 (active &!4 &8) agreement: {ok59}/{tot}")
    print(f"H59b (active &8) agreement: {ok59b}/{tot}")
    print("examples (stored, computed):", ex)


main()
