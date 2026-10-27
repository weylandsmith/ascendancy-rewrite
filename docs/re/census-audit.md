# t107 WORD-WRITER CENSUS AUDIT (2026-10-27)

Hand-authored; no generator touches this file. Assignment: STATE.md t107 —
re-validate banked "writers accounted" claims produced by byte-pattern store
censuses against the fixed tool, after t106 proved `r1_t86_write_census.py`
was structurally blind to 16-bit word writes (income-law.md S-T106-TOOL).

## 1. Method and baselines

- FIXED tool: `scripts/r1_t106_writers.py` (0x66 prefixes generated AND
  prepended; boundary accept only on instruction starting exactly at addr,
  function-start decode preferred).
- HONEST pre-fix baseline: `git show d8dda8f:scripts/r1_t86_write_census.py`
  (the working-tree copy at t107 session start had ALREADY been patched by
  t106 — re-running it would show a false clean history; disclosed).
- NEW tool this task: `scripts/r1_t107_writers_full.py` — same shapes and
  boundary check, but adds the write-op families the t86 op set never
  included: AND 20/21, OR 08/09, XOR 30/31, ADC 10/11, SBB 18/19,
  XCHG 86/87, group 80/81/83 /0../5, INC/DEC FE/FF /0,/1 (+66), NEG/NOT
  F6/F7 /2,/3, shifts C0/C1/D0/D1/D2/D3 (all +66 where legal).
- Two analysis traps hit and corrected, disclosed: (a) substring match on
  "WORD PTR" also matches "DWORD PTR" — true-16-bit filter is
  `(?<!D)WORD PTR`; (b) `boundary_ok` will happily accept objdump's decode
  of DATA bytes (function-start list can misalign; obj0 code span per the
  pointer law is [0x14bb0,0x82bb0) — byte-family op results MUST be
  code-span filtered).

## 2. Per-offset table (fixed tool; WORD = true 16-bit sites)

Offsets audited: ship POWER +0x88, order state +0x5d, planet flags +0x66,
+0x67, growth counter +0x4e, build accumulator +0x50, build queue/slot +0x52,
+0x54 (selected item), order kind +0x58, IND +0x44, +0x46, +0x48, shield
+0x90. Full site lists: /tmp/t107_census.txt (session scratch) reproducible
via `python3 scripts/r1_t106_writers.py <offs>` and the full-op tool.

| off | fixed verified | pre-fix (d8dda8f) | WORD sites (fixed) | pre-fix WORD | verdict |
|-----|----------------|-------------------|--------------------|--------------|---------|
| +0x44 | 30 | 19 | 9  | 0 | safe (all in banked families, see 3) |
| +0x46 | 12 | 4  | 3  | 0 | safe |
| +0x48 | 19 | 13 | 3  | 0 | safe |
| +0x4e | 26 | 20 | 5  | 0 | safe |
| +0x50 | 22 | 11 | 8  | 0 | safe |
| +0x52 | 33 | 23 | 9  | 0 | safe |
| +0x54 | 26 | 12 | 0  | 0 | safe |
| +0x58 | 39 | 20 | 0  | 0 | safe + 1 doc fix (kind-2 writer) |
| +0x5d | 29 | 6  | 3  | 0 | safe (word sites other-struct) |
| +0x66 | 43 | 38 | 0  | 0 | safe |
| +0x67 | 31 | 8  | 0  | 0 | safe |
| +0x88 | 23 (full-op) | 18, 4 desync-rejects | 0 | 0 | safe + burn-class doc fix |
| +0x90 | 14 | 13 | 0  | 0 | 1 site MISSING from S2d -> amended |

CONFIRMED [verified]: the pre-fix tool produced ZERO 16-bit-word sites on
every offset — t106's claim reproduces exactly (the `mov3216` kind labels it
printed were pattern-bookkeeping lies: the 0x66 byte was never prepended, so
a "mov3216" hit decoded as a plain DWORD store).

CONTROL +0x88: 4 real sites the banked t86-era census silently dropped by
window desync (fixed-tool set = 23 with full-op incl. 0x41d80 DEC; banked
S7.4/S2j text carried the surviving 18). The banked POWER/recharge law was
NOT falsified by the recovered sites (3/4 are re-grant/copy paths already
described at S7.4; the 4th is the new burn path below).

## 3. New 16-bit sites — adjudication (all harmless unless stated)

Every new word site falls in a writer family ALREADY banked through
independent evidence, or in a proven other-struct context:

- FUN_00037d80 / FUN_00038ba4 / FUN_00038f68 / FUN_00038840 / FUN_0003a558
  word stores +0x44/46/48/4e/50/52 (0x37f31..0x37f45, 0x38ecf..0x38edf,
  0x3909f/0x390a0, 0x39290/0x3929a/0x39315/0x3932b/0x393f9, 0x3a61d..0x3a655):
  init pair-copy, recalc store, accrual, reset, and the 1:1 template copy —
  i.e. exactly the writer set income-law.md 6c banked FROM A DIFFERENT TOOL
  (w16 byte-mask `66 89|01|29|21|81|c7|ff`, t23). The pop/income closures
  NEVER depended on r1_t86. HOLDING FACT.
- 0x3ad74 (event +200 to +0x50) and 0x441ba (SA_IndustryBoost WORD +0x50
  += 100): both already banked (income-law S: event 23 line ~184; aicode 6.3
  #20).
- WORD +0x52:=0xffff septet (0x21f48, 0x37f8d, 0x38a19, 0x38af5, 0x39290,
  0x3a153, 0x49de5) + BYTE +0x54:=0xff six sites (0x21f3e, 0x37f93, 0x38a1f,
  0x39296, 0x3a159, 0x49dd2) = the banked clear-build-queue / governor-reset
  signature (income-law S14 names the same six clearers).
- fn 792 WORD +0x5d:=5/2 (0x557ff/0x5586f) and fn 147 WORD +0x5d:=0xffff
  (0x30bba): OTHER STRUCTURES — surrounding layout (+0xc/+0x14/+0x33/+0x59/
  +0x5b block init, 0x30b90..0x30bf3 field sweep) is not the 0x6a ship
  record; ship order-state +0x5d byte writer law (aicode S6, t94 order
  census + t104 observations) untouched. [verified by disasm windows]
- 0x26209/0x2621c (fn 1580): the banked colonization RMW law FUN_00025d30
  ([rec+0x44]=v+1, income-law t19) — already named.

## 4. Full-op census: the second blind spot, and what it cost

Cross-validation: the full-op tool re-found every banked site cited from
non-census evidence — 0x21b85 INC WORD +0x44 (ship-completion, income-law
t19/line 107), 0x39084 INC +0x50 (alien IND<4, income-law 6c), +0x66 |=2
0x37f7b and |=1 0x39229 (income-law S-T30 region 651/686). Census and bank
agree in both directions. [verified]

In-code NEW full-op sites after code-span filter, and their cost:

1. `0x41d80 dec DWORD PTR [esi+0x88]` (fn 2010 command-exec; block
   0x41d60..0x41daf: stores ptr ds:0x12e10 into [+0x67], DEC POWER, clears
   order state BYTE +0x5d:=0, jumps 0x41b8f) — a PER-ORDER one-POWER burn
   path absent from the banked burn-class enumeration (aicode S7.4 named
   only travel/upkeep 0x4a2d4..0x4a314 for the CONTROL class). AMENDED in
   aicode.md S7.4. Rewrite delta: none (aggregate model has no per-ship
   POWER).
2. `0x49307` block (fn 664 = FUN_0004929c): sequence
   WORD[+0x56]:=0xffff, DWORD +0x90:=0, +0x8c:=1, BYTE +0x5d:=0, then
   +0x88:=[+0x90], +0x98:=[+0x8c]. FUN_0004929c is banked (ships.md S8,
   t15b) as init_global_gizmos whose documented first step is "init
   ship-object template fields" — so this is the TEMPLATE-time shield/power
   zeroer, an addition to (not contradiction of) runtime INIT 0x4a756;
   combat.md S2d "13 verified image-wide" understated by one. AMENDED in
   combat.md S2d. No law change.
3. `+0x58` (order kind): imm-0 store 0x24a00 (assert-guarded
   `cmp BYTE [ecx+0x58],0` at 0x249e3, then kind:=0 with WORD +0x56:=0xffff
   — command CLEAR) and imm-2 store 0x3ca60 (`[edi+0xb0]` is a ship ptr:
   kind:=2, [+0x59]:=target, source [edi+0xab], followed by WORD
   [edi+0xb0]:=0xffff — a SECOND move-order issuer besides banked 0x22243/
   0x2228f). aicode S6 store list amended. Kind VALUES unchanged; banked
   exec-semantics law unaffected.
4. Data-region noise (all outside [0x14bb0,0x82bb0) or boundary-artifact):
   fn 111 / 0x83xxx-0x88xxx `and8 al/ch/cl/dl` family, fn 3938 rcl/rol
   imm-0x8b cluster — objdump decoding embedded data; excluded by the
   code-span filter law banked in §1(b). Zero load-bearing.
5. +0x66 full-op additions IN CODE (27: or8/rol/rcl across fns 408, 1130,
   483, 173, 253, 121, 143, 351, 152, 575, 1392, 3938, 2134, 987, 1002,
   168, 528 ...): +0x66 is a PLANET byte inside a large union-ish stride;
   the banked +0x66 law (flag bits 1/2 set at 0x39229/0x37f7b, OQ-016 S10
   region) cites those two setters DIRECTLY, not a census, so it stands.
   The extra sites sit at identical offsets in OTHER record classes (same
   trap t50+ recorded for +0x57/+0x0c). No amendment; flagged as a bounded
   known-unknown: per-struct attribution of +0x66 byte-OR sites is not
   claimed anywhere.

## 5. Ledger effect

- NO open row closes (strict-close: the audit produced tool-validity facts,
  not a measurement of an open behaviour). OQ-016 STAYS OPEN, same residual
  set as t106.
- NO closed row falsified. The t106 tool bug is now a bounded, tabled fact:
  word-write blindness cost ZERO closures (planet-field laws came from the
  t23 w16-mask census; combat laws came from t88/t94 call-censuses and t104
  observation; the three doc gaps found — S2d count, S6 store list, S7.4
  burn class — are amended in-place this iteration).
- OQ-010 addendum: shield-word +0x90 writer set image-wide = 14 (fixed
  tool), ship-record-class list in combat.md S2d corrected.
- Method law banked: byte-family store censuses over a flat image MUST
  (a) include 0x66 + full write-op set (use r1_t107_writers_full.py),
  (b) filter candidates to the obj0 code span, and (c) attribute hits per
  record class before any "only writers" claim (offset collision across
  planet/ship/UI structs is the norm at these disp values).
