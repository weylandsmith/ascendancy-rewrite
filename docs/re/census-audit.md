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

## 2. Per-offset table (t109 PURGED: re-run 2026-10-27 with the t108-FIXED
## boundary rule + code-span filter [0x14bb0,0x82bb0); the pre-t109 numbers
## were produced by the DEFECTIVE verifier and are kept struck-through only)

Purge method (t109): every offset re-censused twice — limited-op tool
(`r1_t106_writers.py`, the S2 op set) and full-op tool
(`r1_t107_writers_full.py`) — both carrying the S8 authoritative
function-start rule; sites then split in-code vs data-region. Raw dumps
session scratch: /tmp/t109_lim.txt, /tmp/t109_full.txt (+0x55/+0x42:
/tmp/t109_t106.txt). Cross-check: full-op in-code +0x66 = 15, reproducing
the hand-adjudicated S7 count exactly.

Offsets audited: ship POWER +0x88, order state +0x5d, planet flags +0x66,
+0x67, growth counter +0x4e, build accumulator +0x50, build queue/slot +0x52,
+0x54 (selected item), order kind +0x58, IND +0x44, +0x46, +0x48, shield
+0x90.

CORRECTED TRUTH COLUMN = full-op IN-CODE sites. WORD = true 16-bit sites
(`(?<!D)WORD PTR`), in-code. The old verifier inflated every byte-op-heavy
offset; inflation was concentrated in byte families (S8).

| off | ~~fixed verified (old verifier)~~ | lim-op ver | lim in-code | **full-op in-code** | WORD | ~~pre-fix WORD~~ | verdict |
|-----|------------------------------|------------|-------------|---------------------|------|------------------|---------|
| +0x44 | ~~30~~ | 24 | 20 | **22** | 11 | 0 | safe (all in banked families, see 3) |
| +0x46 | ~~12~~ | 11 | 7 | **7** | 3 | 0 | safe |
| +0x48 | ~~19~~ | 16 | 9 | **10** | 3 | 0 | safe |
| +0x4e | ~~26~~ | 25 | 8 | **8** | 5 | 0 | safe |
| +0x50 | ~~22~~ | 17 | 13 | **13** | 8 | 0 | safe |
| +0x52 | ~~33~~ | 27 | 23 | **23** | 9 | 0 | safe |
| +0x54 | ~~26~~ | 26 | 22 | **22** | 0 | 0 | safe |
| +0x58 | ~~39~~ | 38 | 32 | **32** | 0 | 0 | safe + 1 doc fix (kind-2 writer) |
| +0x5d | ~~29~~ | 25 | 25 | **25** | 3 | 0 | safe (word sites other-struct) |
| +0x66 | ~~43~~ | 14 | 13 | **15** | 0 | 0 | safe — S7 law COMPLETE |
| +0x67 | ~~31~~ | 31 | 30 | **30** | 0 | 0 | safe |
| +0x88 | ~~23~~ | 22 | 22 | **23** | 0 | 0 | safe + burn-class doc fix |
| +0x90 | ~~14~~ | 14 | 14 | **14** | 0 | 0 | 1 site MISSING from S2d -> amended |

Word-site counts are UNCHANGED from the pre-purge S2 table on all 13 offsets
(9/3/3/5/8/9/0/0/3/0/0/0/0 -> full-op adds +0x44: 9->11, +0x50: ->8 equal).
That is the structural confirmation of the S8 claim: WORD/DWORD sites always
passed the fn-start decode; the phantom load was byte-op-only. Data-region
exclusions (verified-but-outside-code-span, full-op): +0x44:4 +0x46:4 +0x48:7
+0x4e:22 +0x50:5 +0x52:8 +0x54:5 +0x58:6 +0x66:6 +0x67:2 (the fn-111
`and8`/pool cluster of S4.5 + obj1 pool bytes).

Full-op-minus-limited-op op-family gap sites (all banked S4 items, now with
correct counts around them): 0x21b77+0x21b85 (INC WORD +0x44 ship-completion),
0x467b6 (+0x48), 0x39084 (INC +0x50 alien IND<4), 0x37f7b+0x39229 (the +0x66
|=2/|=1 pair — the limited-op op set does NOT generate group-80 /1, so the
banked flag pair is found ONLY by the full-op tool), 0x41d80 (DEC +0x88 burn).

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
  0x3909f/0x390a0 [t108: 0x3909f verified; 0x390a0 is NOT an insn start —
  range-notation fragment, see S7], 0x39290/0x3929a/0x39315/0x3932b/0x393f9, 0x3a61d..0x3a655):
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

---

# t108 FULL-OP RE-AUDIT OF REMAINING CENSUS-CITED CLAIMS + +0x66
# ATTRIBUTION (2026-10-27)

Hand-authored continuation. Assignment: STATE.md t108. Tools:
scripts/r1_t108_disp32_audit.py (NEW), r1_t106_writers.py +
r1_t107_writers_full.py (both FIXED this iteration), whole-span decode
workbench `objdump -b binary -D -m i386 -M intel --start-address=0x14bb0
--stop-address=0x82bb0 work/ascend_restored.bin` (session scratch
/tmp/t108_spanspan.txt, 140,902 insns, sequential from the obj0 start =
authoritative instruction boundaries).

## 6. Item (1): the five census-cited claims outside the t107 offset list

METHOD: for disp32 questions the pattern generator is REPLACED by
encoding-agnostic whole-span decode (no blind spots by construction). This
immediately exposed a THIRD generator blind spot: r1_t106/t107 generate
mod=01/10 + SIB forms only — never the mod=00 rm=101 absolute-direct form
(`88 35 disp32`) nor moffs A0-A3. (The banked 0x7458e law came from a raw
byte-scan of `8e 45 07`, not that generator, and survives.)

| claim | verdict | evidence |
|-------|---------|----------|
| aicode S7.3 "ds:0x7458e EXACTLY two store sites" | HOLDS | span decode: exactly `mov BYTE PTR ds:0x7458e,dh` 0x21aa0 + `mov BYTE PTR ds:0x7458e,dl` 0x52cc6 memory-destination; 275 reads; zero other-op writes; zero FPU. Owning-instruction map over all 277 raw u32 runs agrees. 0x52cc6 sits beyond the tsv extent of fn 0x520ec(+0x39) — dark-zone site, adjudicable only by the span chain (t103 banked it independently). |
| aicode S8.2 "[ui+0xccb] one store, zero readers" | HOLDS (addr corrected) | store starts at 0x37bb9 (aicode note said 0x37bbb = imm-byte address; corrected in-place). Raw u32 0x00000ccb occurs exactly ONCE in the whole span (that disp); span decode names 0xccb in exactly that store. |
| income-law 6d(a) "no FPU touches [reg+0x67]" | HOLDS, scope annotated | zero FPU mnemonics with +0x67 any form (span decode + tool LEG C); 8 raw u32 0x67 runs = branch displacements/imm32 only. Annotation added in-place: NON-FPU stores at +0x67 exist (S7 table) and are planet-recalc/template/design-table/UI-local — none is pop storage. |
| combat.md S2g caller-census re-run | RE-RUN GREEN RC=0 | callers(0x4b740) = {0x1a146,0x39d9f,0x3a0b3,0x4bb56,0x4d191,0x4d2dd} identical to banked set; LCG 0x7825b unique; zero rng edges. |
| diplomacy.md:252 stride-0x1ee raw census | ANNOTATE-ONLY, no tool liability | it is a RAM-window VALUE census (values at fixed offsets in save slots), not a code store-pattern census — the t106/t107 tool blindness classes do not apply; already RETRACTED in diplomacy.md S10 by cross-audit. |

## 7. Item (2): +0x66 attribution — and the BOUNDARY VERIFICATION DEFECT

While attributing the 27 "+0x66 in-code full-op sites" of S4.5, re-checking
each candidate against the containing function's decode chain from its
function start (functions_full.tsv start+size window) left 15/68. The rest
never had an instruction starting at the candidate address. Example:
0x41835 "add BYTE PTR [eax+0x66],al" decodes when objdump is started at
0x41835 or 0x41830, but the real chain from fn 0x41260 runs ...0x41830
pushf / 0x41831 and al,0xb0 / 0x41833 add eax,[eax] / 0x41838 cmp eax,ebx —
0x41835 is mid-instruction.

ROOT CAUSE [verified]: boundary_ok accepted decode bases addr&~0xF and
(addr&~0xF)-16 IN ADDITION to the function start; for a 16-byte-aligned
candidate, base==addr means objdump starts decoding AT the candidate and any
pattern self-verifies (R7 recurrence inside our own verifier). Two further
holes found while fixing and fixed:
(a) objdump WRAPS long instructions: the tail prints as an address line with
    bytes in the normal bytes-field but no mnemonic (`544ff: 00 ff ff` =
    tail of the 10-byte mov at 0x544f8). Skipping such lines left holes the
    mid-inspection test fell through; tails are now merged into the previous
    instruction's length.
(b) the fn-start chain must be AUTHORITATIVE: if it covers the candidate and
    puts it mid-insn, REJECT — no fallback vote (a fallback base can always
    be found whose misaligned decode puts a boundary at the candidate).
Both tools patched (r1_t106_writers.py, r1_t107_writers_full.py); control
checks: boundary_ok(0x544f6)=None, (0x37f7b)=OR ok, (0x41d80)=DEC ok.

Blast-radius spot audit: 37 banked site addresses cited in this file S2/S3/S4
+ income-law/aicode bank text, re-verified by fn-start decode: 36 OK, 1
phantom — 0x390a0, cited as part of the range notation "0x3909f/0x390a0" in
S3; the real store is 0x3909f (4-byte `mov WORD PTR [esi+0x50],cx`), the
"/0x390a0" fragment was a second address that never existed as an insn
start. WORD/DWORD sites (what the laws were actually banked from) are solid;
byte-op families carried the artifact load. S4.5's "27 in-code" and S2's
"+0x66 fixed verified 43" are SUPERSEDED by the table below.

FINAL +0x66 store census (fixed tools, code span [0x14bb0,0x82bb0),
function-start authoritative; file /tmp/t108_0x66_final.txt):

| site | fn | insn | record class of base |
|------|----|------|----------------------|
| 0x37f28 | 0x37d80 recalc/init | mov BYTE [esi+0x66],0 | PLANET — banked clear |
| 0x37f7b | 0x37d80 | or BYTE [esi+0x66],2 | PLANET — BANKED |=2 |
| 0x39229 | 0x38f68 growth | or BYTE [esi+0x66],1 | PLANET — BANKED |=1 |
| 0x3a696 | 0x3a558 ctor | mov BYTE [ebp+0x66],al | PLANET 1:1 template field COPY (t106 ctor law), not a flag setter |
| 0x490e3 | 0x49074 gizmos loader | mov DWORD [edx+0x66],eax | SHIP DESIGN table: edx walks 0x7650c stride 0x6a (in-window 0x490b7 mov edx,0x7650c; 0x490c3 [+0x52] law) |
| 0x4923a | 0x49074 | mov DWORD [edx+0x66],0 | same design-table post-pass |
| 0x341ac, 0x34447 | 0x34148 shp-cache UI family (shp.md queued callers) | mov DWORD [ebp+0x66],edx/ebx | STACK-LOCAL: classic frame (push ebp; mov ebp,esp); loop counter scaled `shl 2`, compared to [obj+0x69]>>16 = the banked shp record-count/selector >>16 law; object arg is [ebp+0x76] |
| 0x3de7c..0x3df3e (6 sites) | 0x3db80 shp-cache caller | mov DWORD [ebp+0x66],eax | STACK-LOCAL: prologue `sub ebp,0x82` rebases the frame, so [ebp+0x66] = caller-local below original ebp |
| 0x4ec97 | 0x4e6fc shp-cache caller | mov DWORD [ebp+0x66],eax | STACK-LOCAL (same `sub ebp,0x82` rebase) |

Data-region entries (0x87757/0x8790b/0x87a94/0x88158/0x8822b/0x88bd4, obj1
pool bytes decoded as code) are excluded by the S1(b) code-span law.

ITEM (2) VERDICT: clean no-new-carriers result — among ALL
boundary-verified +0x66 writes, the ONLY flag-bit OR-ing on a planet record
is the banked pair 0x37f7b (|=2) + 0x39229 (|=1) (income-law S-T30 region).
Zero additional planet flag carriers exist in the image; the banked +0x66
law is COMPLETE.

## 8. t108 ledger effect

- NO open row closes (strict-close): items (1)+(2) confirmed tool-validity
  and law-completeness; no open behaviour was measured to a new constant.
- NO banked law falsified. One citation defect (0x390a0 phantom address in
  S3 range notation) and one address slip (0x37bbb -> 0x37bb9) corrected.
- Method law UPGRADED (supersedes S5 item (b)): function-start decode chain
  is the ONLY acceptable boundary evidence — (i) never seed objdump at or
  above the candidate, (ii) merge wrapped tail lines into the previous insn
  length, (iii) mid-insn coverage on the fn-start chain = definitive REJECT.
  Prefer whole-span decode for disp32 questions: it is generator-free.
- OQ-016 annotated (completeness of the +0x66 flag law is now a cited
  closure-grade fact inside the row's open residue list — the row stays
  open on its remaining capture-class items).

---

# t109 COUNT-COLUMN PURGE (2026-10-27)

Hand-authored continuation. Assignment: STATE.md t109. Mechanical pass only:
S2 replaced in place with corrected counts (task item 1), the t106 +0x55
four-WORD list and the four t107 amendment sites re-cited against the
authoritative rule (item 2), this section (item 3), then the closing control.
Working notes: docs/re/_wip_t109.md.

## 9. STOP-REPORT: the tool-liability bound, and what survives

HONEST STATEMENT (item 3): **no banked LAW changed in t106/t107/t108, and
none changed in this purge either.** What the three tool iterations cost the
corpus was COUNTS in byte-op families and two phantom citations; every law
that was banked from WORD/DWORD stores or from call-graph/decompile evidence
was never exposed to the defect. Evidence for that claim, from this pass:

1. Word-site counts are identical pre- and post-purge on all 13 offsets
   (S2 table): the defect class (self-verifying 16-aligned byte patterns +
   wrapped-tail coverage holes) only manufactured BYTE hits. Inflation
   magnitude was byte-dominated and offset-dependent — worst absolute:
   +0x66 43 -> 15 (S7), +0x4e 26 -> 8 (17 verified sites sit in the obj1
   data pool / fn 3938 data-decode region, 22 of 30 full-op verified sites
   for +0x4e are data-region); zero inflation at +0x54/+0x58/+0x5d/+0x67/+0x88/
   +0x90 in-code (lim in-code == old count minus at most data-region entries).
2. Every law-bearing site cited in the last three iterations survives the
   authoritative fn-start decode with its claimed disassembly: +0x55 quartet
   0x37f9a / 0x39224 / 0x44054 / 0x3a664 (the ONLY four word writers of +0x55
   in the code span — OQ-016's "FOUR sites" claim re-verified verbatim),
   colonise 0x23cac, t107 amendments 0x49307 (+0x90 set now cited as 14,
   combat S2d), 0x24a00 + 0x3ca60 (+0x58 set now cited as 32 in-code, aicode
   S6), 0x41d80 DEC +0x88 (+0x88 set now cited as 23, aicode S7.4), the
   +0x66 |=1/|=2 pair 0x39229/0x37f7b, and the op-family gap sites 0x21b77/
   0x21b85/0x467b6/0x39084.
3. Cross-method agreement: the t109 full-op in-code +0x66 set is EXACTLY the
   15 addresses S7 hand-adjudicated (tool == hand, no drift).
4. Closing control `scripts/r1_t108_disp32_audit.py` re-run RC=0 reproduces
   the S6 numbers exactly: 0x7458e = 277 raw u32 runs in span, 58 moffs-verified
   refs, 0 FPU-verified; 0xccb = exactly 1 raw occurrence, 0 moffs, 0 FPU;
   +0x67 = 8 raw runs, 0 moffs, 0 FPU. (Label note: the tool prints WRITE only
   for operand forms it decodes; the two absolute-direct stores 0x21aa0/0x52cc6
   are span-decode evidence per S6, not moffs-p-generator output — the scan2
   list here reads 58 refs / 0 WRITE, same as the t108 run it replaced.)

AMENDED IN-PLACE this pass: S2 table (replaced); OPEN-QUESTIONS OQ-016 t106
tool-leg sentence ("+0x55 now 12 verified sites (4 word), +0x42 28" ->
corrected counts struck in).

LIABILITY CLOSURE: after t109 every count in this file names a tool AND a
code-span rule; no doc anywhere is asked to trust the pre-t108 verifier.
Remaining open rows (OQ-003 residue, OQ-005, OQ-006, OQ-016 residual set,
OQ-019, OQ-021, OQ-023) are capture/user-gated per their row text and
REFUTED-ROUTES R11-R14 — no offline static work of any shape remains.

## 10. t109 ledger effect

- NO open row closes (strict-close): a purge produces corrected bookkeeping,
  not a measurement of open behaviour. OQ-016 STAYS OPEN, same residual set.
- NO banked law falsified (see S9 items 1-4).
- No new tool. No tool change (both purge runs used the t108-patched code).
