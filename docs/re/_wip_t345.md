# WIP t345 — SHIELD-BYTE LAW -> REWRITE CODE SITE (OQ-016 residue-(4) follow-through)

Session start 2026-11-08 ~16:47 EST. Fresh session; STATE.md alone was sufficient.

## S0 SITTING CHECK (mandatory first action)
Tail-seek (400 KB window) of work/r1/playcap/live-timeline.jsonl (8,764,400,092 B):
newest turn = **1086** — NOT > 1086 => no new sitting, assignment stands. Production
dosbox-x pid 136359 + watch pid 136374 alive (untouched).

## S1 INPUTS READ (assignment premises)
- docs/re/income-law.md S-T325 (census: pending byte+3==0 44/44; completed 15 w/
  word2 0xf01 43/43) and S-T340 (completion handler CLOSED, "no code delta").
- Ledger docs/OPEN-QUESTIONS.md ~line 254: "OQ-016 residue list now EXHAUSTED
  ((1) cited-dead x8 = user ruling, (2)(3)(4) CLOSED, (6) CLOSED as
  misattribution)"; row STAYS OPEN pending D3 user adjudication. So residue-(4)
  is already closed as a LAW question; t345's live question is only whether the
  cited law is SUFFICIENT TO MODEL (code delta + pin) or not (bank the gap).
- rewrite/src/game/campaign.cpp:1012 buildPhase — models acc+=IND, completion,
  reset; comments cite 0x3928b/0x39290 verbatim. No word2 slot-state model.
- income-law.md is HAND-AUTHORED (grep scripts/*.py: only cross-references in
  docstrings, no writer writes it) -> safe to bank here.

## S2 VERBATIM COMPLETION BLOCK (work/t91_code_disasm.txt lines ~43855-43905)
FUN_00038f68 marker block 0x39224..0x392a0:
  0x3923b mov ax, WORD [eax*8+0x73e46]  ; item gate word (idx*5*8)
  0x39245 and al,0x8 / 0x3924c je 0x39290        ; bit8 clear -> skip marker
  0x39252 cmp ax,[esi+0x18] / 0x39256 jb 0x39290 ; slot < cells -> skip marker
  0x3925b mov edx,0xf
  0x39260 cmp ch,0x1b / 0x39263 jne 0x3926a
  0x39265 mov edx,0x23                            ; ITEM 27 SPECIAL CASE
  0x3927a mov BYTE PTR [ebx+eax*1+0x3],0x0        ; zero byte3
  0x39288 shl edx,0x8
  0x3928b or  WORD PTR [ebx+eax*4+0x2],dx         ; word2 |= 0x0f00 / 0x2300
  0x39290/96/9a queue reset (+0x52=0xffff, +0x54=0xff, +0x50=0)
*** STRUCTURAL POINT t345: byte3 IS THE HIGH BYTE OF SLOT WORD2 (offset +0x2).
There is no independent byte3 field — the t325 "byte +3" census was reading the
marker half of the 16-bit slot state word. Values seen: 0x0f01 (normal), 0x2301
(item 27 class), 0x0001 (item 18, 30 slots — marker block SKIPPED).
Next probes: (P1) who READS word2's high byte / byte3 anywhere in-image;
(P2) item-table check — are 15 and 35 file fields of items 26/27 or hardcoded
semantics; (P3) is item 18's skip (bit8 of gate word) the law the rewrite should
carry.

## S3 P1 — READER CENSUS (work/t91_code_disasm.txt, parse scripts inline)
In-image census of slot-dword refs `*4+0x2` / `*4+0x3` = 27 sites. High-byte
(marker) CONSUMERS:
1. **0x396f2 (fn starting ~0x396cc, 2-arg eax=planet rec, edx=slot)** — THE LAW
   SITE: `mov ax,WORD[esi+eax*4+0x2]; sar eax,0x8; and eax,0x7f` -> ecx = marker
   (assert REPORTER 0x2a428 fires if >= 0x6b=107, msg ids 0x404/0x405 file
   0x1d69/0x1d77), then TWO TABLE LOOKUPS stride 0x162 = 354 bytes:
     `imul eax,eax,0x162; mov eax,DWORD[eax+0x3a0e9]; sar eax,0x10` -> field
     (assert if == -1), and return-address tail `imul; add eax,0x3a095` =>
     record base = 0x3a095 + marker*354, field(+0x54 hi-word) from 0x3a0e9
     (= base + 0x54). So THE MARKER BYTE IS NOT A BOOLEAN — IT IS AN INDEX INTO
     A 354-BYTE-STRIDE RECORD TABLE (DAT ~0x3a095..0x3a095+107*354).
   *** This REFINES t340's "one-time completion marker" reading: 0x0f/0x23 are
   TABLE INDICES (15, 35), which is exactly why t325 saw 15 for item 26 and why
   0x23 for item 27 is hardcoded at 0x39265. ***
2. 0x39ae5 (fn ~0x39ac5): reads word2 bit0 only (`xor ah,ah; and al,1`) — the
   ACTIVE law (t271), not the marker.
3. Recalc FUN_00038ba4 (0x38ba4..0x38f65, verbatim this session): reads slot
   byte0 (item id), byte1 (0xff=free), word2 & 0x1 (active) — NEVER the high
   byte. So shieldThreatFor (+0x59) does NOT depend on the marker value; the
   rewrite's bit-0x8 FLAGS threat model stands unchanged by P1.
4. Other `*4+0x2` sites: 0x38679/0x3869e (picker, bit0-class), 0x38d5a/95/dd0
   (recalc, bit0), 0x39164/0x391ce/0x3920d/0x3928b (the four known stores),
   0x4ad87/0x509ab (float contexts — NOT slot arrays, false positives of the
   pattern; different base semantics).
NEXT: (P2) dump the stride-354 table at file 0x3a095, inspect records 15 and 35;
(P2b) find the fn at 0x396cc + callers to name what the record feeds (cost?
strength? UI description?); (P3) whether items 18 vs 26/27 marker-skip (gate
bit8) is already modelled.

## S4 P2/P2b — WHAT THE MARKER FEEDS (verified)
- 0x396cc is a 3-instruction-scale RESOLVER inside the FUN_00038f68 blob
  (functions_full.tsv: fn 0x38f68 size 0x1392 => 0x38f68..0x3a2fa, so 0x396cc,
  0x39ae5, 0x396f2 are all IN it). Signature: eax = planet record, edx = CELL
  (call sites load `dx,WORD[..+0x52]` = the queue cell, t341 pair).
  Body verbatim: bound-assert cell < rec+0x1a; read slot word2; `sar 8; and 0x7f`
  -> idx; assert idx < 0x6b (107; aicode.md S2b says 101 cap, bound 0x6b);
  assert table[idx]+0x54 hi-word != 0xffff; RETURN 0x3a095 + idx*0x162.
  => THE MARKER BYTE IS CONSUMED AS AN INDEX INTO THE 354-BYTE-STRIDE SHIP/OWNER
  TABLE AT 0x3a095 (same table aicode.md S2b + dosbox-wp-t283 banked; static
  image bytes at 0x3a095 are code-shaped garbage because the LIVE array is a heap
  copy — t74 law cited there, so a static dump of "record 15" is MEANINGLESS,
  honest negative P2).
- 25 call sites of 0x396cc, EVERY one gated `cmp BYTE [slot+0x1],0x17` (item 23
  = Ship, combat.md:657) — i.e. the marker-as-ship-index consumer is the SHIP
  BUILD ORDER path: cancel (0x49d2c at 0x21f0e/0x38abe/0x3c9e9/0x3d867), cost
  triple (0x4a41c at 0x39525, income-law.md:453), UI name/refresh (0x3b015,
  0x3b674, 0x3df9b printf-arg 0x1fea, 0x3c929), combat engagement (0x3a0a4 ->
  call 0x4b740 = the hit-path t89 cites for shield absorb), AI fleet loops
  (0x42c39/0x42c50/0x42c97).
- *** CONTRADICTION t345 FOUND (the real finding): if byte3 were written ONLY by
  the completion block 0x3927a/0x3928b, every gated slot would carry the CONSTANT
  0x0f (or 0x23 for item 27), so 0x396cc could only ever return record 15/35 —
  impossible for a 25-site ship resolver. My `*4+0x2`/`*4+0x3` PATTERN CENSUS IS
  THEREFORE INCOMPLETE (PENDING P4): the completion block itself writes byte3 as
  `[ebx+eax*1+0x3]`, NOT `*4+0x3`, so any ship-index writer using `*1+0x3` or a
  pre-computed slot pointer was invisible to S3. S3's "sole writer" wording is
  retracted in advance of P4 — do not bank it.
- CONSISTENT CORPUS DATUM (t325, no new capture): completed item 18 (SURFACE
  shield) 30 slots word2=0x0001 byte3=0, completed item 26 (ORBITAL shield)
  43 slots byte3=0x0f. The completion block's `cmp ax,[esi+0x18]; jb skip`
  (slot < cells = surface) explains the 18-vs-26 split EXACTLY, independent of
  the item-flags bit8 term: SURFACE slots never take the marker, ORBITAL ones do.
  That is a NEW REFINEMENT of t340 clause 2 (t340 recorded the gate; this is the
  first time it is shown to be the term that actually explains the t325 census).

## S5 P4 — byte3 WRITER-FORM CENSUS (running)


## S5 P4 - byte3 WRITER-FORM CENSUS (COMPLETE)
Census over work/t91_code_disasm.txt (restored image disasm, 7,135,820 B):
- PTR [*1+0x3] forms: EXACTLY 1 site = 0x3927a (completion block itself). No
  hidden byte3 writer in that form.
- PTR [*4+0x2] forms: 27 sites (S3 list). S3 classification holds, but S3
  missed the SEMANTICS of one, which resolves the S4 contradiction:

*** SETTER fn 0x39760 (inside FUN_00038f68, verbatim 0x39760..0x3980e) IS THE
    ARBITRARY-INDEX WRITER - the PAIR of getter 0x396cc. Signature: eax =
    planet rec, edx = cell, ebx = RECORD POINTER (0x3a095 + idx*0x162). Body:
    assert cell < rec+0x1a (0x40e); assert cell >= rec+0x18 (assert 0x40f
    @0x39786 - ORBITAL ONLY, mirror of the completion block jb guard);
    idx = (ebx - 0x3a095) idiv 0x162; assert idx < 0x6b (0x413); assert
    table[idx]+0x54 hi-word != -1 (0x414, same validity assert as getter);
    0x397fa/0x39806: cx = word2; ch = 0; edi = idx<<8; or ecx,edi ->
    word2 = (word2 AND 0x00ff) | (idx << 8).
=> THE S4 CONTRADICTION DISSOLVES: the marker byte is NOT written only by the
   completion constants. fn 0x39760 stores ANY ship-record index into the slot
   marker half of word2, so the 25-site getter can legitimately return 101
   distinct records. S4 pre-retraction of S3 sole-writer wording SUPERSEDED by
   this cited getter/setter pair.
- Setter CALLERS (3, all verbatim this session):
  * 0x3987c (fn ~0x39810): ship-assign path - loops cells from rec+0x18
    (orbital base) for a free slot (slot byte+1 == 0xff), sets
    BYTE slot[+1] = 0x17 (item 23 Ship), WORD slot[+2] = 1 (active), then
    setter with ebx = ship record edi (whose +0x54 hi-word is the owner planet
    index, checked at 0x39823, and +0x58 = 3, +0x59 = planet rec).
  * 0x3b860 (fn ~0x3b80d): edx = cell [ebp-0x14], ebx = record from 0x40de0
    over table 0x12e16 + idx*33*8 (design/owner table).
  * 0x3f87b (fn ~0x3f7xx): after 0x38818(rec, 0x17) allocates a cell and
    0x40358, sets dx = si (cell), ebx = planet, ebx->ecx record.
=> LAW: the orbital build-slot marker byte = SHIP RECORD INDEX of the ship
   occupying/produced by that cell; set at assignment time by 0x39760, and set
   to the CONSTANT 15 (0x0f) / 35 (0x23 for item 27) by the completion block
   0x3927a/0x3928b when the item table flag bit 0x8 is set.
- Other *4+0x2 sites reclassified with context:
  * 0x21f37: cancel path - slot byte+1 = 0xff (free) + WORD word2 = 0 (kills
    marker AND active together), then rec +0x54=0xff/+0x50=0/+0x52=0xffff;
    guarded by cmp BYTE [edi+0x54],0x23; je skip (item 35 not cancelled).
  * 0x3ca2c: and BYTE slot[+2],0xfe = clear bit0 (deactivate) KEEPING marker.
  * 0x3e06d: READ full word2, and 0xffff, jne - slot non-empty test.
  * 0x35cd6: DIFFERENT ARRAY (base ds:0x701cc stride 4, index ds:0x701d4);
    writes BYTE +2 and WORD +0 - save-side table, false positive.
  * 0x80bf7: cmp DWORD [ecx+eax*4+2],0 in a generic container helper (calls
    0x80b48) - false positive.
  * 0x2a277/0x2aaa7 add BYTE [..+2],ah: data-shaped artifacts in non-code
    blocks, not writers.

## S6 P5 - RUNTIME GATE-WORD CENSUS (MEASURED, keeper script)
Static gate-word bytes at Ghidra 0x73e40 in work/ascend_restored.bin are
CODE-SHAPED GARBAGE (t74 law confirmed firsthand this session - the static
dump "bit8 set" list is 40 rows of nonsense). The LIVE table is the only
authority. scripts/r345_gate_word_census.py (exit 0, work/r345_gate_census.out):
48 saves (r1deep-* x 15 runs + t340-shieldc save/+ring-final/), pointer law
B + 0x82BB0 + 0x73E40 + idx*0x28, FLAGS word +6:
  bit8 SET exactly on {18, 19, 26, 27} - 48/48 saves, every row STABLE
  (single value per item across all samples). bit4 set exactly {17,28,29,30}.
=> (1) The marker path (completion block gate 0x3924c) is EXACTLY the four
   shield items - first cited measurement of the gate population (t340 verified
   item 26/27 words individually; this is the full 39-row census).
   (2) The rewrite readings campaign.cpp shieldThreatFor flags&8 (shields
   18/19/26/27) and orbitalThreatFor flags&4 (17/28/29/30) now match the
   RUNTIME table verbatim (they were file-file cited before; runtime-verified
   now at 48 saves).
   (3) Item 23 (Ship) flags=0x0000 bit8 CLEAR -> ship completions NEVER take
   the completion marker; ship-slot markers come ONLY from the setter 0x39760.
   Consistent with S5: two distinct marker-writer populations, no overlap.
## S7 P6 - LIVE SHIP-TABLE RECORDS 15/35 (first probe, t340 ring-final 60.sav)
base B+0x82bb0+0x3a095 stride 0x162 (r1_slot.py law). +0x54 DWORD hi16 = the
validity field the getter/setter asserts (!= 0xffff):
  rec  0 hi16=0xffff (free)   rec 15 hi16=0x0002 VALID, +0x00=4, +0x08=0e
  rec 35 hi16=0xffff (free in THIS run - item 27 never completed here)
  rec100/rec106 hi16=0xffff.
=> record 15 IS A LIVE VALID RECORD while a completed orbital shield carries
   marker 15. HYPOTHESIS (unverified): the shield-completion constant 15/35 is
   a PSEUDO-SHIP record index - completed shields "occupy" ship records 15
   (items 18/19/26) / 35 (item 27), which is exactly why the getter validity
   assert passes for shield slots, and why the combat engagement site 0x3a0a4
   -> 0x4b740 (hit path, shield absorb per t89) can resolve a shield through
   the SAME getter. NEXT: ships.md record layout on rec15 bytes; census rec15
   across saves (does it appear exactly when a shield is completed?); check
   whether any getter call-site reads a NON-item-23 slot (the S4 gate claim).

## S8 P7 - CORPUS VERDICT: H_INDEX CONFIRMED FOR SHIP SLOTS (keeper run)
scripts/r345_marker_census.py exit 0 (work/r345_marker_census.out; 60 saves,
playcap + caps + bank-t1254 + t340-shieldc). ITEM-23 slot rows byte3: 17
DISTINCT values {2,3,4,5,7,8,11,12,15,18,18,18,25x3,27,31x3,32,33,39,40};
80 planet-saves carry >1 distinct byte3 (e.g. 41.sav rec 0x26d3c1 cells 73/75/
76 -> 25/3/31). => byte3 on ship slots is a LIVE PER-SHIP INDEX, not a
constant. Shield contrast: item 18 1800 rows byte3 ALWAYS 0; item 26 2932 rows
byte3=15 + 108 rows 0; item 27 180 rows 35 + 240 rows 0.
P7b FOLLOW-THROUGH (inline census, same corpus, same saves): for every ACTIVE
item-23 row, resolve rec = B+0x82bb0+0x3a095 + byte3*0x162 and read
+0x54 hi16 (owner) / +0x58 (state) / +0x59 (planet ptr):
  360/360 ACTIVE rows: owner hi16 == planet owner byte AND +0x58 == 3 AND
  +0x59 == rb - 0x88 EXACTLY (guest-physical planet ptr; my walk carries the
  +0x88 member-header offset - the t33 law again, zero misses).
  140 inactive rows: same owner/still-points, state byte == 1.
=> FULL GETTER/SETTER CIRCLE WITNESSED AT CORPUS SCALE: word2 high byte on a
   ship slot == index of the ship record that names this planet back at +0x59.
   The marker byte is a UNION FIELD by slot class: ship slots (item 23) carry
   the ship index (writer 0x39760); completed bit8-gated items carry the
   constants 15/35 (writer 0x3928b); everything else 0.

## S9 P8 - SHIELD-MARKER VALIDITY + CONSUMER GATE (inertness of the constants)
Same corpus (60 saves): every item-18/19/26/27 slot row, marker validity
checked against rec = B+0x82bb0+0x3a095 + marker*0x162, +0x54 hi16 != 0xffff:
  item18 surf: 1780 rows marker0 bit0=1 (completed, NO marker - the cell<cells
    skip, S4), 20 rows marker0 bit0=0 (pending/inactive).
  item26 orb: 2932 rows marker15 VALID, 108 rows marker0 bit0=0 (pending).
  item27 orb: 180 rows marker35 VALID, 240 rows marker0 bit0=0.
  0 dangling markers. NOTE (honest): the 2932/180 counts are per-SAVE
  correlated (4 run lineages), not independent samples - "rec15/rec35 always
  valid" is 4 data points, not a law.
CONSUMER GATE: S3 found exactly TWO high-byte consumers - getter 0x396f2 and
0x39ae5 (bit0 only) - and ALL 25 getter call sites are gated on slot
byte1 == 0x17 (verified per-site this session; the 8 sites with no cmp within
8 lines all sit behind a 0x17 gate within 30 lines or in fn ~0x39810/0x49d2c
call chains whose entry gates it). => THE GETTER NEVER RUNS ON SHIELD SLOTS:
the constants 15/35 are functionally INERT one-time completion markers
(t340 reading HOLDS for shields); the index semantics is EXCLUSIVE to item-23
slots (writer 0x39760, the union field by slot class).

## S10 SYNTHESIS - THE COMPLETE MARKER LAW (all cited, t345)
Slot word2 (dword[slots+4*cell] >> 16) = (MARKER << 8) | ACTIVE-bit:
  WRITERS (census-exhaustive: *1+0x3 form = 1 site, *4+0x2 form = 27 sites,
  every writer classified S5):
    0x3928b completion: marker := 15 (item 27 -> 35) for gate-bit8 items
          {18,19,26,27} (runtime census 48/48, r345_gate_word_census.py) AND
          cell >= +0x18 (surface shields never marked - explains item 18
          1800/1800 byte3==0);
    0x39760 setter: marker := ship-record index (orbital-only assert 0x40f),
          3 callers (ship-assign 0x3987c, design path 0x3b860, 0x3f87b);
    0x391ce (dig word2:=0), 0x21f37 (cancel word2:=0), 0x3ca2c (bit0 clear,
          marker kept), 0x3920d (item 35 |= 2).
  CONSUMERS: getter 0x396cc (25 sites, item-23-gated) resolves marker -> ship
  record 0x3a095 + marker*0x162 (validity assert +0x54 hi16 != -1); corpus
  circle 360/360 ACTIVE ship rows: rec owner == planet owner, +0x59 == planet
  record, +0x58 == 3 (assign state).
  REWRITE DISPOSITION: the rewrite carries NO per-ship build-slot state
  (fleet_ launch abstraction, campaign.cpp:1489), so the marker byte has NO
  CODE SITE until the OQ-019 per-ship model lands - the measurement is DONE
  (this iteration), the gap is an implementation DECISION, not a measurement.
  shieldThreatFor/orbitalThreatFor (flags&8 / flags&4) now RUNTIME-VERIFIED
  against the same live table (exact sets {18,19,26,27}/{17,28,29,30}).
  NO rewrite code delta this iteration (queue row pre-authorises: insufficient
  -> bank the gap, change no code).
