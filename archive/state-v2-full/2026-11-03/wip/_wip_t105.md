# WIP t105 — STATIC PAIR: GOVOROM +0x42 key + "stride-45 table 0x74782"
(task from STATE.md t105; OQ-016-adjacent residuals named by t99 S6.4)

Sitting watch: live-timeline.jsonl mtime 2026-10-26 15:44 unchanged at
session start 2026-10-27 16:07 -> no new sitting, assignment stands.

## P1 (b) "STRIDE-45 TABLE 0x74782" — REFUTED AS AN INDEPENDENT TABLE;
## IT IS THE RESTREE RUNTIME COST WORD (row 0), base 0x74744 stride 75.

Measured (scripts/r1_t105_statics.py + r1_t105b_region.py, 60.sav,
item-table-anchored B=0x1bf4d8):
1. Cost-law census over candidate (base,stride) pairs: base 0x74782 stride 75
   matches the CITED OQ-013 runtime cost law (runtime = file_cost*(2*row-20)
   for row>10 clamp 65000, else file_cost) on 66/66 rows. Every stride-45
   variant: 0-1/66. Rows 0..4 words = 50/50/50/90/100 == restree.txt file
   costs rows 0..4 (t99's "live 50/90/100 for rows 0..4" was the stride-75
   law all along).
2. Name-anchor proof: "Orbital Structures" (spaced form, row 0) sits at
   member B+0xf72f6 = corollary X 0x74746 = (0x74744 record base) + 2 —
   exactly the OQ-013 record law (stride-75 record, name u8[60]@+2, runtime
   cost u16@+62 = base+62). Row deltas: 61x stride 75 across rows 0..65.
   => 0x74782 == 0x74744 + 62 == row-0 COST WORD, not a table base.
3. Instruction proof (restored image 0x4414e..0x44189, SA_FreeResearch body,
   boundary-verified decode):
     mov  bl,[ebp+0]; add ebx,ebx            ; ebx = 2*self
     mov  ax,[ebx+0x76492]                   ; research target t
     cmp  edx,0xffff; je 0x4400a
     lea  eax,[edx*4]; add eax,edx           ; 5t
     mov  edx,eax; shl eax,0x4; sub eax,edx  ; 80t - 5t = 75t   <<< *75
     mov  ax,[eax+0x74782]                   ; WORD (0x74744 + 75t + 62)
     mov  [ebx+0x764a0],ax                   ; progress := full cost
   t99 F17's "stride 45" came from stopping the decode at 5t (or an
   arithmetic slip); the decomposed imul is *75 == research-runtime stride.
   SEMANTICS NOW CITED: SA_FreeResearch (19 Chamachies) sets the research
   progress accumulator 0x764a0[2self] := runtimeCost(target row) — i.e.
   progress to FULL cost = vendor text "research complete in one day".
4. FILE bytes @0x74782 = 4c890000cd31c705... = pre-relocation garbage as the
   t81 trap predicts — only the live member leg is trustworthy here.
Ledger effect: aicode S6.3 line 19 "WORD[0x74782 + 45*t]" -> +75*t
correction; S6.4 OPEN-RESIDUALS item "stride-45 table 0x74782 identity
beyond cost-word" CLOSED (there is no stride-45 table; identity = restree
runtime cost word, both legs cited). _wip_t99 F17 carries a REFUTED marker.
No rewrite delta expected (rewrite FreeResearch leg uses Tech::runtimeCost —
verify against rewrite source before claiming).

## P2 (a) GOVOROM +0x42 — PREMISE CORRECTED, IDENTITY CLOSED: THE MIN KEY
## IS THE POPULATION COUNTER WORD ITSELF (t24 CLOSED pop law), NOT a cache.

1. Premise in the t105 assignment ("race-row field +0x42 population-
   correlated on GOVOROM rows in 60.sav") is FALSE as written: race rows
   (0x12e16 + 0x1ee*r) rows 0..20 carry pointer-garbage/zeros at +0x42
   (row2 +0x40.. = heap ptrs 0x2564 0x2545...), and NO GOVOROM race row
   exists in this campaign (rows 0..3 = Chamachies 19 / Orfa 2 / Ungooma 11
   / Minions 0 eliminated — t99 F18). GOVOROM = ability NUMBER 10
   (SA_Cornucopia) in the 21-entry vendor list; the real residual is t99
   F12/F18: the SA_Cornucopia body picks the owned planet with MIN
   WORD[planet_rec+0x42] — "+0x42-vs-population relation uncited".
2. BODY RE-VERIFIED instruction-by-instruction (restored 0x43de4..0x43e96,
   jump-table FILE 0x43b10 entry 5 == ability 10 pinned 16/16 this pass):
   walk static planet record pool 0x2b057 stride 0x7b (123), count
   hi16(dword ds:0x3a091) == 145 live; gate BYTE [rec+0x57]==self
   (mov bl,[eax+0x57]; cmp bl,[ebp]); skip WORD [rec+0x16]==10; MIN key
   WORD [rec+0x42] (init cx=0xffff, jbe prune); winner -> ecx=[rec+0x10]
   slot-array ptr, loop k < WORD[rec+0x18] (surface cells): slot class
   BYTE [ecx+4k] in {0,1} -> copy 3 u32 {2,3,4} (0x6838) + rng 0x7824f
   idiv 3 -> store class byte. (Matches t99 F12 exactly.)
3. IDENTITY CITED: +0x42 IS pop. Same word, same record layout, three
   independent legs: (i) t24 DECISIVE capture (income-law.md §6e, OQ-016
   pop-storage CLOSED): "pop = word +0x42; growth counter +0x4e; cap +0x4a";
   (ii) the growth-pass decompile work/coswnd_decomp/38f68.c:154-177 reads
   param_1+0x42/+0x4a/+0x4e with param_1+0x12 == growth-inc == the STATE
   heap law +0x12 — SAME layout, so pop(+0x42) == the Cornucopia min key;
   (iii) live 60.sav fit: owner0 min-key worlds have SMALL +0x42 with large
   caps (colony pop 2..13 vs cap 97..115), the home world Vega IV
   +0x42=61 vs cap 83 (cells 73+10, mature pop), and pool row 3
   (+0x42=61, +0x16=10) is that same homeworld record — the skip
   [rec+0x16]==10 leg = homeworld exclusion [inferred from this match].
   => derived-cache vs stored-decision: STORED COUNTER (colonize :=2,
   growth +1/tick, events +=2, recalc clamp only) — never a cache of
   another field.

4. WRITER CENSUS (the assignment's r1_t86_write_census pattern, +0x42):
   verified 10 sites image-wide, ZERO on the race-row stride (0x1ee-base
   walks never appear; hits are UI/font/other-module add8 forms +
   0x3b0a7 'mov DWORD [edx+0x42],0x10a10002' whose LOW WORD == 2 == the
   t24-colonization set pop:=2 (t24 cited site 0x3b0c8 same function
   region) — corroboration, not a new claim). The inc/dec forms t86 does
   not pattern (inc grp) cover the growth pass: 0x393a9/0x393b5/0x393e4
   'inc WORD [esi+0x42]' (growth tick, matches 38f68.c +0x42/+0x4e/+0x4a
   reads). VERDICT: +0x42 is a STORED COUNTER with cited writer set
   (colonize :=2, growth +1, event20 +=2, recalc clamp 0x38f01..0x38f58,
   event24 :=cap) — NOT a derived cache, and NOT a race-row field.
5. LIVE 60.sav consistency leg: pool rows 145 (count law
   hi16(dword X0x3a091)==145); max growth counter +0x4e == 48 < 50
   (t81 census law holds at T=1254); 64 rows pop>=cap all carry
   counter==0 (LAB_000393f9 force-zero law, zero violations); 15 rows
   carry +0x16==10 (the body's excluded class, t99 F12 skip-leg pinned;
   semantic label of class 10 NOT claimed).

## P3 DECISION + LEDGER EFFECT
Both aicode.md S6.4 OPEN-RESIDUALS items touched this iteration are CLOSED
BY MEASUREMENT: (i) "GOVOROM +0x42-vs-pop relation uncited" -> +0x42 IS
pop (identity with the t24 CLOSED pop law; three legs P2.3); (ii) "stride-45
table 0x74782 identity" -> no stride-45 table exists; 0x74782 is the row-0
runtime COST WORD of the research-state table @0x74744 stride 75 (OQ-013
record law +62; t91 P3 base cited), *75 decomposition byte-pinned P1.3.
aicode.md S6.3 line corrected (45*t -> 75*t). OQ-016 STAYS OPEN (strict-
close: terrain/nuke wiring, home-placement, minutiae, preset source,
live-UI-trace armer all remain). No rewrite delta: both laws are per-record
fields of the vendor's aggregate-invisible tables (research progress word
already wired as Tech::runtimeCost; rewrite FreeResearch already completes
the queued tech, Cornucopia already keys on pop).
