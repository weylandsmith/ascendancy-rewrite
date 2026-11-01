# t248 WIP — per-planet owner table hunt (banks the 102-planet law)
# FINAL: banked to docs/re/selfplay.md "### t248 PER-PLANET OWNER TABLE FOUND"
# (that section is the record; this file keeps the raw probe trail).

## S1. THE TABLE IS FOUND: planet-record OWNER byte = NAME+0x33
- Planet table: stride 123 (0x7b), name-anchored (r1-savestate.md name law).
  Banked t1254 slot work/r1/bank-t1254/48.sav: rec0 name "Vega I" at member
  idx 0x26d103 (phys 0x26d07b, pointer law H=0x88). Live-ring slot 41.sav
  (turn 1086): same base. 151 slots (t1254: 145 named + 6 blank-named).
- FIELD: byte at NAME+0x33 == owning race index; 0xFF == unowned.
  Cited measurements (scripts/r1_t248_owner2.py, r1_t248_fixed.py,
  r1_t248_orphan.py, run 2026-10-31 22:4x-23:0x):
  * t1254 (bank 48 + 55): owner hist over NAMED records
    {0:102, 1:11, 2:11, 255:21} -> count(owner==race0) = 102 == header
    "102 Planets Occupied" EXACT (the 151-slot walk reads 108 only because
    the 6 blank-named slots k=145..150 hold a stale 0; the law is
    NAMED && owner==race).
  * STRUCTURAL PROOF (strongest leg): for every colonised planet at BOTH
    t1254 (124) and t1086 (104), the star-record owner bitmask (+0x14,
    0x60-stride, img 0x13bc5, bound WORD ds:0x16145==50) satisfies
    starbyte & 0x7f == OR(1<<owner over that system's planets) — ZERO
    violations, all 50 systems name-keyed, at both timestamps.
  * STATIC INIT SIGNATURE: game/resume.gam (vendor 2008 file, 151 records,
    name@0x9b1a, stride 123) at NAME+0x33: hist {0:1,1:1,2:1,3:1,4:1,5:1,6:1,
    255:144} — exactly seven records hold 0..6 = each race's HOME planet, all
    else 0xFF. Owner-field initialisation pattern.
- NAME+0x65 == planet index within its system (values 0..4).
- Ghidra (this session): FUN_00051684 (0x51684, the planet-list header
  producer, region 0x51685..0x517c0) loops the 0x60-stride star table
  (0x5168d MOV EAX,0x13bc5; bound WORD [0x16145] @0x51692; owner test
  CMP ESI,EDI with EDI=1<<[0x7458e] @0x516c5; home-star exclusion
  CMP EAX,[ECX*0x1ee+0x12e1d] @0x516d7) and that loop-count is the header's
  SYSTEMS number (35 sole + home = 36 @t1254 EXACT). The header's PLANETS
  number is NOT that loop: the decompiled tail reads a stored u16 via
  *(u16*)(*(int*)(obj+0xab) + 0x8c7) — a heap-window slot, not a data-seg
  counter. The format-string fetch is MOV EAX,0x97 (=static.txt record 151)
  at 0x51798 feeding CALL 0x21a20.

## S2. t247's "+0x5a = colonised-planet count" is REFUTED
Star byte +0x5a == TOTAL planet SLOTS in the system, not colonised count:
sum(+0x5a) over all 50 stars == 145 == the named record count at t1254, and
per-system len(planets)==+0x5a for every name-keyed system at both timestamps
(the colonised reading matches only 3/5). Consequence: the t1254
"104 slots vs 102 header" delta is NOT a co-ownership split — the only
non-player planet inside a player-bit-set star is Fomalhaut II (owner 0xFF
unowned, star byte 0x1). All co-owned stars (Sarsaparilla 132, Arcturus 6,
Oslo 129, Philadelphia 130, Amoroso 6) have every planet owned by a party
whose bit is in the star byte; the player owns 4/4 Oslo planets.

## S3. HONEST NEGATIVE: the t1086 header (60) is NOT count(owner==race) (80)
At turn 1086 (live ring 41.sav, screenshot work/screens/t2/
planets_header_t1092.png "60 Planets Occupied, 26 Systems Controlled"):
count(NAMED && owner==race0) = 80, delta +20 vs the header's 60.
Swept and excluded as the header filter (scripts/r1_t248_pred.py, full
census over all 123 record offsets x 256 values, bit-k, and u16 reads,
scored ==60 @t1086 then re-scored @t1254):
  - single-byte ==v / !=v: NO offset hits 60 @t1086.
  - bit-k: 5 hits at 60 @t1086 (NAME+5 bit4 -> 60 @t1254; +48 bit4 -> 65;
    +51 bit1 -> 32; +89 bit3 -> 80; +101 bit0 -> 57). NONE also hits 102
    @t1254, so no single-bit filter explains both headers.
  - owner==race AND byte==v / !=v: no hit at 60.
Also: the t1086 table has 154 named records (k=145..153 named Masticon I-III,
Bob I-IV, Oslo I-II) while t1254 has 145 named + 6 blank — the map's slot
population differs between the two timestamps, itself a hint the header
counter and the table are maintained independently.
=> The header's planets number is a MAINTAINED counter (S1 Ghidra leg agrees:
   stored u16 through [obj+0xab]+0x8c7), and t246's u16@0x131b4 is neither
   that counter nor the count. What 20 of the 80 owned planets at t1086 lack
   remains UNMEASURED. Owner-field semantics (S1) stand independently of this.
Next instrument (t249): intersect "u16==60 @t1086" with "u16==102 @t1254"
across both corpora for the maintained header counter; then the writer sites.
