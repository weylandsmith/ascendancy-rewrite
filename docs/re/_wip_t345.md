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

