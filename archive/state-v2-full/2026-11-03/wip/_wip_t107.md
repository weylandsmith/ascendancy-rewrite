# t107 WIP — WORD-WRITER CENSUS AUDIT (STATIC)

Assignment (docs/STATE.md t107): re-validate every banked "writers
accounted / no writer exists" claim produced by a byte-pattern store census,
using the FIXED tool scripts/r1_t106_writers.py (0x66 prefix included +
function-start boundary decode; see income-law.md S-T106-TOOL).

## P0 — method law (from t106)
- r1_t86_write_census.py: encodings() dropped b"\x66" operand-size prefixes
  AND dis_at() decoded a window at addr&~0xF (desync). Net effect: ZERO
  16-bit word writes ever entered a banked t86-style census; boundary
  rejections also silently dropped real sites.
- Fixed tool accepts a site iff some decode base (function start preferred)
  yields an instruction starting exactly at addr whose text contains
  +0x<off>. Kinds tagged mov32/mov8/sub/add/mov16/... ; word kinds = names
  ending "16" plus C7-with-66.

## Audit scope (priority offsets from the assignment)
ship POWER +0x88, order state +0x5d, planet flags +0x66, growth counter
+0x4e, build queue +0x50/+0x52, channel words +0x44/+0x46/+0x48.
CENSUS-CITED CLOSED ROWS additionally in scope (each closure leans on a
t86-style "writers accounted" claim):
- OQ-010 shield-layer identity: [reg+0x90] writer census (combat.md S2d,
  OPEN-QUESTIONS.md:61-62) -> audit 0x90.
- income-law.md:200 "+0x67 zero raw-census hits" claim -> audit 0x67.
- income-law.md:1543 +0x54 field identity (r1_0x54_writer_sweep.py, its own
  tool — check whether IT was 66-blind) -> audit 0x54.
- aicode.md:475 +0x58 order imm sites (r1_t94_order_census.py) -> audit 0x58
  for word imm forms.
Already re-verified at t105/t106 (do not redo): +0x42, +0x55.

## Results table (fill as runs land)
(per-offset table final home: docs/re/census-audit.md)

## Adjudications (fill)

## P1 — battery run (fixed tool r1_t106_writers.py vs PRE-FIX tool from git d8dda8f)
Offsets: 44 46 48 4e 50 50 52 54 58 5d 66 67 88 90 (12 unique + 0x88 control).
Two traps hit during analysis, disclosed: (a) substring filter "WORD PTR" also
matches DWORD PTR — true-16-bit count MUST use (?<!D)WORD PTR; (b) the working-tree
r1_t86 at session start was ALREADY patched by t106 (banked "fixed") — the honest
pre-fix baseline is `git show d8dda8f:scripts/r1_t86_write_census.py` (/tmp/t107_orig.py).
Counts (fixed vs pre-fix verified; true-16-bit sites fixed vs pre-fix):
  0x44 30/19, W 9/0 | 0x46 12/4, W 3/0 | 0x48 19/13, W 3/0 | 0x4e 26/20, W 5/0
  0x50 22/11, W 8/0 | 0x52 33/23, W 9/0 | 0x54 26/12, W 0/0 | 0x58 39/20, W 0/0
  0x5d 29/6, W 3/0 | 0x66 43/38, W 0/0 | 0x67 31/8, W 0/0 | 0x88 22/18(+4 rejected
  boundary-desync false negatives), W 0/0 | 0x90 14/13, W 0/0
CONFIRMED: pre-fix tool produced ZERO 16-bit-word sites on every offset (the 0x66
encodings were generated as kinds but never prepended) — t106 claim reproduces exactly.
CONTROL +0x88: 4 real sites silently dropped by window desync (0x4a307, 0x4a710,
0x4c1c5, 0x4c62a banked at t106; all re-found by fixed tool).

## P2 — NEW 16-bit writer sites, clusters (raw)
- PLANET-RECORD CONSTRUCTOR/copy family FUN_0003a558 (fn 498): word stores at
  +0x44/46/48/4e/50/52 (0x3a61d/625/62d/645/64d/655) — struct-copy of the channel
  words + growth counter into new records (t106 already found the same fn's +0x55).
- FUN_00037d80 (fn 575, planitem/init init per OQ-014) same word stores
  +0x44..+0x52 incl 0x37f8d WORD[esi+0x52],0xffff; +0x54 byte :=0xFF at 0x37f93.
- fn 1392 = FUN_00038f68 (pop-law fn, t24 layout): +0x4e 0x39315/0x3932b/0x393f9,
  +0x50 0x3909f/0x3929a, +0x52 0x39290, +0x54 byte 0x39296.
- fn 866 = FUN_00038840: +0x44/46/48 word ax (0x38ecf/d7/df), +0x52 0xffff x2 + ax
  (0x38b12), +0x54 byte 0x38a1f.
- fns 433/408/76: WORD +0x50:=0, +0x52:=0xffff, BYTE +0x54:=0xff triple = CLEAR-BUILD-QUEUE
  signature (0x21f42/48/0x3a153/59, 0x49de5).
- SHIP: 0x49307 WORD[eax+0x56]=0xffff + 0x49307-region DWORD +0x90=0, +0x8c=1,
  BYTE +0x5d=0 then +0x88=[+0x90] — SHIP RESET/CLEAR-ORDER block (verified disasm
  0x492f0..0x49340): power cleared WITH shield word + order state, power := shield
  field copy.
- ORDER KIND word-invisible? No: kind stores are BYTE; pre-fix tool missed them via
  DESYNC only. NEW byte imm sites vs pre-fix: +0x58 imm0 0x24a00 (clear-order path
  right after assert cmp kind==0 at 0x249e3), imm2 0x3ca60 (ISSUER: [ship+0x58]:=2
  + [+0x59]:=target right after call 0x38840(3, edi+0xb0) — banked text said kind 2
  "written by 0x4aa50 reg-form"; 0x3ca60 is a second, immediate-form writer).
- UI cluster 0x6d000-0x70xxx (banked: DIFFERENT structure).

## P3 — FULL-OP census (scripts/r1_t107_writers_full.py, NEW this task)
Discovery: the t86 blind spot was TWO-DIMENSIONAL. Besides 0x66 (word), the
banked op set never included AND/OR/XOR/ADC/SBB/XCHG/INC/DEC/NEG/NOT/shift
stores. Full-op tool re-found EVERY banked site of those families cited from
other evidence (0x21b85 INC word +0x44 ship-completion income-law:107;
0x39084 INC +0x50 income-law:161; +0x66 |=2 0x37f7b / |=1 0x39229
income-law:651/686) — cross-validates both directions.
NEW in-code full-op sites (after code-span filter [0x14bb0,0x82bb0)):
- 0x41d80 DEC DWORD [ship+0x88] (fn 2010 command-exec; adjacent 0x41dab
  BYTE +0x5d:=0 clear, 0x41d76 stores ptr ds:0x12e10 into [+0x67]) = a
  per-order one-POWER burn path NOT in the banked burn-class enumeration
  (aicode S7.4 named only 0x4a2d4..0x4a314 travel/upkeep + completion).
  AMEND aicode; harmless to rewrite (no per-ship POWER model).
- 0x49307 (fn 664) ship-RESET block: WORD [+0x56]:=0xffff, DWORD +0x90:=0,
  +0x8c:=1, BYTE +0x5d:=0, then +0x88 := [+0x90], +0x98 := [+0x8c]. Second
  reset-family zeroer of shield word beside banked INIT 0x4a756 — combat.md
  S2d "13 verified image-wide" UNDERSTATES by 1 (fixed tool: 14). AMEND.
- fn 3938 +0x66 rcl/rol imm-0x8b cluster + fn 111/0x83xxx-0x88xxx and8/xor8:
  boundary_ok accepts objdump's decode of DATA bytes (fn starts can be
  misaligned; code not guaranteed). All 0x83xxx+ sites are OUTSIDE the obj0
  code span (obj1 data); fn-3938 sites disasm-clean at 0x3bfc8 window shows
  no rcl. Treat as data artifacts; disclosed boundary_ok limitation: a
  code-span membership filter is required for byte-family op censuses.
- +0x44: 0x2252d WORD store / 0x22542 :=0 (fn 227), 0x22a30 :=0 (fn 1130) —
  ship-command-region struct, +0x44 = IND in PLANET records; not adjudicated
  individually (2 sites, marked unverified-harmless).
Word-site adjudication summary (P2 list): ALL new 16-bit sites fall in
already-banked writer families or proven other-struct contexts:
  pair-copy/init/recalc FUN_00037d80/0x38ba4/0x38f68/0x38840/0x3a558
  (the income-law 6c w16-mask census ALREADY named 0x37f3x/0x38ecx/0x3a6xx
  — the planet-field closures never depended on t86 at all);
  0x3ad74 event+200 and 0x441ba SA_IndustryBoost +=100 both banked
  (income-law 184, aicode 6.3 #20); 0x52:=0xffff clearers = build-queue
  clear signature; 0x557ff/0x5586f (fn 792) + 0x30bba (fn 147 block-init)
  = other-struct (offsets +0xc/+0x14/+0x33/+0x59/0x5b layout mismatch);
  0x26209/0x2621c = banked colonization +0x44 RMW law (FUN_00025d30).
NO banked closure falsified. Net ledger effect: zero rows close; two doc
amendments (combat.md S2d count+site, aicode burn class).
