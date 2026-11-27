# _wip tPF-6a2 — TPF6-SHIP: close the 0x402d8 seam at bytes
Started 2026-11-26. Task = STATE.md NEXT ACTION: recover 0x402d8 body + table
identity + port decision for the last unrecovered leg inside checker 0x3830c.

## P1 0x402d8 BODY [verified, t442_disasm 0x402d8..0x40347, fn size 112 in
functions_full.tsv so the disasm is inside one function — no desync]
    edi = eax = arg = RACE DIPLOMACY ROW ptr (callers all pass 0x12e16 +
          race*0x1ee; 0x39b11 computes race*0x1ee via shl5/sub/shl3/sub/add)
    ebx = 1; edx = 0; eax(out) = 0
    call 0x40ec0            ; ebx=0 (no accumulator), edx=0 (no out array)
    ebp = eax               ; = count from 0x40ec0  (SEE P2/P4)
    loop i = 0 .. word[0x16145]-1 over edx = 0x13bc5 + i*0x60:   ; STAR table
        if byte[rec + 0x14] == (1 << byte[edi]) then inc ebx
        ; byte[edi] = race index (row+0), rec+0x14 = star owner mask (t248)
        ; equality with a single bit == SOLE ownership by that race
    eax = ebx                       ; 1 + soleOwnedStars(race)
    ebx = dword[edi + 7]            ; row+7 = POINTER (t246 exclusion ptr)
    eax -= ebp                      ; minus 0x40ec0 count
    bl = byte[[edi+7] + 0x14]       ; the pointed record's owner mask
    if bl & (1 << byte[edi]) then inc eax
    ret eax
=> LAW [inferred from verified bytes]:
   0x402d8(raceRow) = 1 + SOLE_STARS(race) - SHIPS(race) + HOME_BIT(race)
   HOME_BIT = 1 iff the record pointed at by row+7 has owner-bit(race) set.
   Caller 0x39b11 (the checker leg) requires > 0.

## P2 0x40ec0 = per-race SHIP census [verified 0x40ec0..0x40f7b]
    eax = row ptr (ebp), edx = out array (esp+4), ebx = u32 accumulator ptr
    walks the LIVE SHIP ARRAY base 0x3a095 stride 0x162 (pership-spec A1)
    per ship: v = SWORD(ship+0x54); if v == -1 skip; if v == byte[row] -> match
      match: count++ ([esp+8]); if edx!=0 store ship ptr; if ebx!=0
             ebx += (ship[+0xa7]>>24)+1
    loop bound: live ship count u32[0x43489]>>16 (ships.md/pership-spec S3)
    SHIP+0x54 == OWNER RACE cross-confirmed at 0x39a54 (0x396cc -> ship
      record, [ship+0x54]>>16 compared against world record +0x57 owner race;
      pership-spec: '+0x54 u32 owner handle, race index = value >> 16').
    Return law fix in P4: eax = MATCH COUNT.

## P3 capstone pitfall (banked): a whole-function capstone sweep for '+ 7]'
    hits duplicated per overlapping fn-start start (715 hits, unique ~10);
    dedupe by address. The row+7 WRITER census found 0x1a321 (a record-init
    fn, [esi+7]:=eax) among readers 0x171e4/0x1865d/0x186e0/0x1a245/0x1a6f2 —
    NOT conclusive for the diplo row; superseded by P7's t246 citation.

## P4 0x40ec0 loop law, RE-READ from raw bytes 0x40ee0..0x40f00
[verified; supersedes the 'out-ptr low half / 486' misread]:
    edx = [esp+8] (match count), edi = [esp+4] (out ptr), ecx = 0,
    edx = out + 4*count (next write slot); jmp into test
    0x40ef7: movsx edi,cx; cmp edi,0x6b; jge end   ; cx = OWN iteration
             counter (inc'd 0x40ef1) — scan capped at 107 SLOTS (= ship
             array cap 0x6b)
    0x40eff: mov edi,[0x43489]; sar edi,0x10; cmp esi,edi; jge end
             ; esi = MATCH counter — early stop once every live ship found
    slot empty test: [eax+0x54]>>16 == -1 -> skip (0x40f16)
    match: inc esi + [esp+8]; store if out!=0; acc += ([+0xa7]>>24)+1 if ebx!=0
  RETURN 0x40f70: eax = [esp+8] = MATCH COUNT. Semantics: race's ships =
  slots (of first 107) whose +0x54>>16 == race index. P2 stands.

## P4b ORDER PATH IS GATE-FREE [verified]: fn 0x38840 (order gate) contains
exactly ONE call — 0x38ba4. The 0x39a9c shipyard/census gate lives ONLY in
checker 0x3830c (0x38429), i.e. PLANLIST fill + popup Build loop. A queued
order is never re-gated. Port delta stays in projectOptionsFor + popup
lambda; projectOrderable unchanged.

## P5 CALLER CENSUS (per-function scan, tPF6b_callscan) [verified]
0x402d8 (4 sites): 0x39b11 (checker leg via 0x39a9c; sole caller of 0x39a9c
is 0x38429), 0x3e6f8, 0x40e02, 0x51b8c.
- 0x39b11: requires >0 else 0x39a9c returns 0 => checker REVOKES item 23 row.
- 0x51b8c (fn 0x51b64): edx = result; if result < 0 -> edx = -result; if
  result > 100 -> edx = 100; pushes edx + string sel (word[PLANETALLOC+0x8c7]
  ==1 ? 0x2b13 : 0x856c4) into a format call => DISPLAY path (clamped abs).
- 0x40e02 (fn 0x40de0): result <= 0 -> error 0x741@0x2098 then returns 0;
  >0 -> proceeds (0x24918 lookup on byte[ecx] = race idx).
- 0x3e6f8 (fn 0x3e6e0): stores eax, test: jge >=0 skips a 0x40ec0-enumerate
  loop over NEGATIVE results => caller distinguishes sign.

## P6 DISPLAY CROSS-CITATION [verified]
0x51b8c sits in the same format family as the t246 PLANETALLOC header law
("%s (%d Planets Occupied, %d Systems Controlled)") — word[PLANETALLOC+0x8c7]
is the screen-open snapshot selector (t249). The 0x402d8 value is a
per-race COUNT shown/clamped 0..100 with that header string family.
NOTE: 0x2b13/0x856c4 read as garbage in work/ascend_restored.bin (obj0 data
pool strings resolve only after relocation) — string content NOT claimed.

## P7 IDENTITY [verified from prior closed laws]
- arg edi = race diplo row 0x12e16 + race*0x1ee (aicode.md, diplomacy.md
  0x1ee stride law). byte[row+0] = race index (0x3e743 cmp al,[0x7458e]).
- [edi+7] = DWORD[race*0x1ee + 0x12e1d] = STAR RECORD pointer of the race's
  HOME system — EXACTLY the exclusion pointer in the t246 PLANETALLOC header
  law (scripts/r1_t246_header_law.py ln12, MEASURED live: 'skip entry whose
  ADDRESS equals DWORD[0x12e1d + race*0x1ee]').
- 0x13bc5 stride 0x60 = STAR table, byte +0x14 owner mask, count word[0x16145]
  == star count (t248, aicode.md ln144, diplomacy.md ln632 MEASURED 50==star
  count 20/20 saves).
=> 0x402d8(row) = 1 + SOLE_STARS(race) - SHIPS(race)
   + (1 iff HOME_STAR.owner_mask & (1<<race) else 0).
   Item 23 = 'Ship' (economy.md ln46 base list; item 22 = Shipyard ln45).
   0x39a9c gate: 0x402d8 > 0.

## P8 MEANING [inferred from P1+P7]
The revocation gate passes item 23 (Ship) iff
   SHIPS(race) < 1 + SOLE_STARS(race) + HOME_BIT(race).
i.e. a race may keep ordering Ships while its fleet is smaller than roughly
its system count (sole-controlled systems +1, home counts double when the
home star's mask still carries its bit). Ships >= systems+1 (+home slack) =>
the vendor stops offering new Ships in the PLANLIST/popup even with free
pop. This reads as an anti-spam fleet-to-expansion governor. [unverified
semantics; the FORMULA is what ships]

## P9 0x39a9c FULL BODY [verified 0x39a9c..0x39b24] — POSITIVE GATE, not
merely a revocation:
    ecx = planet obj; race = byte[ecx+0x57] (owner race; bounds-checked vs
    word[0x13b96]>>16 count, assert 0x47c@0x1daf)
    c = 0x3958c(planet, 0x16)  = first cell whose BUILT-ITEM byte (cell+1)
        == 22 (Shipyards). Cell-array law: u32 cells, byte+1 = built item id
        (0xff empty), word+2 = item<<8 | flags (0x39f00 family scans
        byte+1 for ids 0x12/0x13; 0x3a068-0x3a072 writes id<<8 into word+2).
    if NO shipyard cell (c == 0xffff)      -> RETURN 0  => checker FAILS 23
    if cell word bit0 == 0                 -> RETURN 0  => checker FAILS 23
    if 0x402d8(0x12e16+race*0x1ee) <= 0    -> RETURN 0  => checker FAILS 23
    else -1 (pass).
  *** So item 23 'Ship' passes the checker ONLY on a planet with an ACTIVE
  (word bit0) Shipyards cell AND while the owner race's SHIP census stays
  below 1 + SOLE_STARS + HOME_BIT. The tPF-6b port shows Ship rows on EVERY
  pop-passing planet — a genuine, citable divergence (both popup and fill go
  through the same checker 0x3830c).***
  bit0 semantics: distinguishes completed/active items (0x39b28 family
  counts cells with byte+1==0x12/0x13 AND bit0 set — 'active shipyards').
  [bit0 WRITER site not yet pinned — P10]
