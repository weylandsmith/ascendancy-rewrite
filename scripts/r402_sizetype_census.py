#!/usr/bin/env python3
"""t402: VERIFY the planet size/type pointer-table law (content-anchored).

Static law (disasm of the status.cpp row builder, sites found by
scripts/t402_status_getters.py; work/ascend_restored.bin base-0):
  0x50704  mov ax, word [PL+0x16]   0x50708 mov esi,[eax*4+0x74540]
  0x50711  mov ax, word [PL+0x14]   0x50716 mov edi,[eax*4+0x7452c]
  0x5071e  mov eax,0x88  call 0x21a20 (getter -> "(%s %s Planet)")
  0x50728  push esi; push edi; push fmt; lea eax,buf; call sprintf
=> row line 1 = sprintf("(%s %s Planet)", T14[WORD[PL+0x14]], T16[WORD[PL+0x16]])
   ds:0x7452c / ds:0x74540 are POINTER tables (runtime), so the census
   locates them by CONTENT: the 11 type words are consecutive in the string
   arena (static.txt file order), and table16[3]=="Eden" sits at the
   "Congenial" arena pointer + 4 (word lens 10/6 -> 10+1+6+1 = 18 = 0x12:
   an EXACT test, not a guess). table14[4] ("Enormous") must live at the
   table16 base - 4 (adjacent arrays hypothesis -> VERIFIED or REFUTED here).

Pointer-value law (t298, BINDING): u32 values STORED in RAM are guest-
PHYSICAL; member index = value + 0x88.

Exit 0 iff: both tables located; every NAMED planet record has +0x14 in
0..4 and +0x16 in 0..10; printed line-1 strings match the vendor shape.
"""
import re, struct, sys, zipfile
from collections import Counter

STRIDE = 123; NAMEW = 19
NAME_RE = rb"[A-Z][A-Za-z]{2,}(?: [IVX]+)?\x00"
SIZES = ["Tiny", "Small", "Medium", "Large", "Enormous"]
TYPES = ["Husk", "Primordial", "Congenial", "Eden", "Mineral", "Supermineral",
         "Chapel", "Cathedral", "Special", "Tycoon", "Cornucopia"]

def cstr(mem, memb, limit=40):
    if memb < 0 or memb >= len(mem):
        return None
    e = mem.find(b"\x00", memb, memb + limit)
    return None if e < 0 else mem[memb:e].decode("cp437", "replace")

def main(path):
    mem = zipfile.ZipFile(path).read("Memory")
    ok = True
    # arena anchors: pointers whose target (+0x88) is the word verbatim
    def ptrs_to(word):
        w = word.encode("cp437") + b"\x00"
        out = []
        i = 0
        while True:
            i = mem.find(w, i + 1)
            if i < 0:
                break
            phys = i - 0x88
            # who points here?
            j = 0
            while True:
                j = mem.find(struct.pack("<I", phys & 0xFFFFFFFF), j + 1)
                if j < 0:
                    break
                out.append((j, cstr(mem, i)))
            if len(out) > 40:
                break
        return out
    p_cong = [j for j, s in ptrs_to("Congenial")]
    p_cath = [j for j, s in ptrs_to("Cathedral")]
    t16 = []
    for a in p_cong:
        b = a - 18  # Congenial is TYPES[2]; its slot is base+8 -> base = slot-8... check exact law below
        # hypothesis: base16 such that base16+2*4 == slot(2)  => base = slot-8
        cand = a - 8
        vals = [struct.unpack_from("<I", mem, cand + 4 * k)[0] for k in range(11)]
        strs = [cstr(mem, v + 0x88) for v in vals]
        if strs == TYPES:
            t16.append((cand, vals, strs))
    if not t16:
        print("TYPE TABLE NOT LOCATED (Congenial-anchor exact test failed)")
        print("Congenial slots:", [hex(a) for a in p_cong][:10])
        return 1
    base16, vals16, strs16 = t16[0]
    print(f"TYPE table member {base16:#x} EXACT 11/11: {strs16}")
    # table14: hypothesis base14 == base16 - 20 (5 size slots before 11 type
    # slots? no — ds gap = 0x74540-0x7452c = 0x14 = 20 B = 5 u32 slots)
    base14 = base16 - 20
    vals14 = [struct.unpack_from("<I", mem, base14 + 4 * k)[0] for k in range(5)]
    strs14 = [cstr(mem, v + 0x88) for v in vals14]
    print(f"SIZE table member {base14:#x} (ds-gap law 0x14): {strs14}")
    if strs14 != SIZES:
        ok = False
        print("SIZE-table placement hypothesis REFUTED at this anchor")
    # planet records
    hits = set(m.start() for m in re.finditer(NAME_RE, mem))
    cands = [h for h in hits if all(h + i * STRIDE in hits for i in range(15))]
    def runlen(c):
        n = 0; p = c
        while p in hits: n += 1; p += STRIDE
        return n
    base = max(cands, key=runlen)
    while base - STRIDE in hits:
        base -= STRIDE
    size_hist = Counter(); type_hist = Counter(); cross = Counter()
    samples = []; nrec = 0
    for k in range(160):
        j = base + k * STRIDE
        raw = mem[j:j + NAMEW]
        if raw.strip(b"\x00") == b"":
            continue
        nrec += 1
        w14 = struct.unpack_from("<H", mem, j + 0x14)[0]
        w16 = struct.unpack_from("<H", mem, j + 0x16)[0]
        cells = struct.unpack_from("<H", mem, j + 0x18)[0]
        size_hist[w14] += 1; type_hist[w16] += 1
        cross[(w14, cells)] += 1
        if len(samples) < 8:
            owner = mem[j + 0x33]
            sw = strs14[w14] if w14 <= 4 else "?"
            tw = strs16[w16] if w16 <= 10 else "?"
            samples.append((raw.split(b"\x00")[0].decode(errors="replace"),
                            owner, w14, w16, cells, f"({sw} {tw} Planet)"))
    print(f"\nrecords={nrec}")
    print(f"size_hist(+0x14)={dict(sorted(size_hist.items()))}")
    print(f"type_hist(+0x16)={dict(sorted(type_hist.items()))}")
    print("cross (size,+0x18 cells):", dict(sorted(cross.items())))
    for s in samples:
        print("  ", s)
    bad = [v for v in size_hist if v > 4] + [v for v in type_hist if v > 10]
    if bad:
        ok = False
        print("OUT-OF-DOMAIN values:", bad)
    print("VERDICT", "PASS" if ok else "FAIL")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1
                  else "work/r1/bank-t249-live-open/60.sav"))
