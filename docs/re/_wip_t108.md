# t108 WIP — FULL-OP RE-AUDIT OF REMAINING CENSUS-CITED CLAIMS + +0x66 ATTRIBUTION (2026-10-27)

Hand-authored scratch. Assignment: STATE.md t108. Two items:
(1) re-audit the five census-cited claims outside the t107 13-offset list:
    - income-law.md:200 "no FPU (D8-DF) touches [reg+0x67]" (scope annotation)
    - aicode.md 0x7458e "EXACTLY two store sites (opcode census)"
    - aicode.md/OPEN-QUESTIONS [ui+0xccb] disp32 census (store 0x37bbb ONLY,
      zero readers)
    - combat.md:272 caller census tool re-run (r1_t88_caller_census.py)
    - diplomacy.md:252 stride-0x1ee raw census (already RETRACTED §10 —
      decide whether it is a tool-validity item at all: it is a RAM-window
      VALUE census, not a code store-pattern census, so the t106 blind spot
      does not apply; annotate)
(2) +0x66 byte-OR site attribution (27 in-code sites, t107 §4.5): per site
    decide record class of the base (planet stride 123 / ship 0x6a / UI /
    other) via base-register provenance; any planet carrier must join the
    banked |=1/|=2 law (income-law S-T30). Clean "no planet carriers" also
    closes item (2).

## P1 (in progress)

## P1 item (1) — five census-cited claims re-audited

METHOD UPGRADE: whole-code-span function-start objdump decode ONCE
(0x14bb0..0x82bb0 -> /tmp/t108_spanspan.txt, 140,902 insns) replaces pattern
generation for disp32 questions — encoding-agnostic (no blind spots by
construction). Tool scripts/r1_t108_disp32_audit.py kept for the pattern-leg
(moffs/FPU/disp8) + a THIRD tool blind spot found: r1_t107 generator covers
mod=01/10 + SIB only — NEVER the mod=00 rm=101 absolute-direct form
(88 35 disp32) nor moffs A0-A3. The span decode closes that class.

- CLAIM aicode S7.3 "ds:0x7458e EXACTLY two store sites (opcode census on
  8e 45 07)": RE-AUDIT HOLDS. Span decode: exactly 2 stores image-wide
  (0x21aa0 mov BYTE ds:0x7458e,dh + 0x52cc6 mov BYTE ds:0x7458e,dl), 275
  reads, zero other-op writes. The v1 tool's "14 WRITE sites" were
  byte-pattern candidates accepted on MISALIGNED window decodes
  (shl BYTE PTR [eax+0x7458e],0x69 class — absent from the span decode);
  its accepted set also MISSED the two real byte stores (88 35/88 15
  absolute-direct not generated). Net: claim stands on the span decode.
- CLAIM aicode S8.2 "[ui+0xccb] disp32 census EXACTLY one hit (store
  0x37bbb), zero readers": ALMOST HOLDS — exact store 0x37bb9
  `mov BYTE PTR [ebp+0xccb],0x2` (t103 doc cites 0x37bbb = address of the
  imm byte, off by 2; aicode:1169 correct to 0x37bb9). Span decode: ONE
  reference total in code span -> zero readers CONFIRMED; raw u32 0x00000ccb
  occurs ONCE in the whole span (inside that store's disp field).
- CLAIM income-law 6d(a) "no FPU (D8-DF) touches [reg+disp8=0x67] or
  disp32=0x67": HOLDS. Span decode: ZERO FPU mnemonics with +0x67 (any
  form); all 89 non-FPU [reg+0x67] refs are 86 mov / 2 cmp / 1 sub; the 8
  raw u32 0x67 occurrences in the span are branch displacements + one
  imm32, zero disp32 operands; tool LEG C = 0. Annotate scope: FPU-only
  claim TRUE; non-FPU stores at +0x67 EXIST (t107 audited that offset).
- CLAIM combat.md S2g r1_t88_caller_census re-run: RE-RUN GREEN RC=0 —
  callers(0x4b740) == 6 sites {302917=0x4a360? no: {0x1a106? dec->hex
  106822=0x1a106, 315793=0x4d1d1, 237747=0x3a0b3? ...}} values identical to
  banked set; LCG 0x7825b unique; zero rng edges. CLAIM INTACT.
- CLAIM diplomacy.md:252 stride-0x1ee raw census: NOT a code-store census
  (RAM-window VALUE census, t106/t107 blind spots inapplicable) and already
  RETRACTED in §10 by cross-audit. Item closed as annotate-only: §10 already
  records why the readings are untrusted; no tool liability added.

## P2 item (2) — +0x66 attribution: THIRD boundary defect found

The t107 full-op run reported 77 verified +0x66 sites, 68 in the code span,
t107 S4.5 called 27 of them "in-code". Re-verification with decode from the
ENCLOSING FUNCTION START (functions_full.tsv start+size window) leaves
15/68. The rest never had an instruction starting at the candidate address.

ROOT CAUSE [verified]: r1_t107_writers_full.boundary_ok fallback bases
include addr&~0xF; when the candidate IS 16-byte aligned, objdump starts
decoding AT the candidate -> every byte pattern trivially "verifies". Proof
site: 0x41835 `add BYTE PTR [eax+0x66],al` decodes at that base, but from
the fn 0x41260 start (same window covers 0x41d80 which decoded fine — the
t104-observed bank site) 0x41835 is MID-INSTRUCTION. => byte-family census
results (00/08/20/28/30/C0/D0/FE/FF /0,/1 byte ops, incl. 80-group imm8)
MUST be function-start-boundary-verified; addr&~0xF fallback valid ONLY for
dword-aligned encodings. AMEND census-audit S5 + fix tool.

TRUE in-code +0x66 WRITE sites (function-start verified, 15):
- fn 0x37d80 (recalc/init, banked): 0x37f28 BYTE:=0, 0x37f7b |=2  -- PLANET (banked law)
- fn 0x38f68 (growth, banked):      0x39229 |=1                   -- PLANET (banked law)
- fn 0x3a558 (template copy, t106): 0x3a696 BYTE [ebp+0x66],al    -- PLANET copy, not OR
- fn 0x49074 (gizmos.txt loader):   0x490e3 DWORD [edx+0x66],eax / 0x4923a :=0
                                     edx walks 0x7650c stride 0x6a = SHIP DESIGN table, NOT planet
- fn 0x34148 x2, fn 0x3db80 x6, fn 0x4e6fc x1: attribution in progress
No planet flag-bit OR outside the banked |=1/|=2 pair found.

## P3 — adjudication of the boundary defect's blast radius

(1) BANKED-SITE SPOT AUDIT (the load-bearing question): 37 site addresses
cited in census-audit S2/S3/S4 + income-law/aicode bank text re-verified by
function-start decode (wide windows): 36 OK, 1 phantom — 0x390a0 (cited
alongside 0x3909f in the t107 S3 range notation "0x3909f/0x390a0"; the real
store is 0x3909f `mov WORD PTR [esi+0x50],cx`, 4 bytes wide, so 0x390a0 is
mid-instruction). WORD/DWORD stores (the families the planet/income/combat
laws were banked FROM) are overwhelmingly REAL. The byte-op families are
where the misalignment artifacts concentrate (byte encodings hit
16-aligned-offset artifacts + every 1/16 of random code density).
(2) The "+27 in-code +0x66 sites" of t107 S4.5: only 15/68 candidates
survive true boundary check. Attribution of the 15:
  - 0x37f28 :=0 + 0x37f7b |=2   fn 0x37d80 recalc/init  -> PLANET, BANKED law
  - 0x39229 |=1                 fn 0x38f68 growth       -> PLANET, BANKED law
  - 0x3a696 mov BYTE [ebp+0x66],al  fn 0x3a558 = the 1:1 template field-copy
    CONSTRUCTOR (t106 banked FUN 0x3a558, callers 0x258dd/0x26044) — an
    instance of the banked copy law, NOT a flag setter.
  - 0x490e3/0x4923a fn 0x49074 gizmos.txt loader, edx walks 0x7650c stride
    0x6a (t86 design-table law re-verified at 0x490b7/0x490c3 in-window) ->
    SHIP DESIGN table field, not a planet carrier.
  - 0x341ac/0x34447 fn 0x34148, 0x3de7c..0x3df3e fn 0x3db80 x6, 0x4ec97 fn
    0x4e6fc: STACK-LOCAL slots — fn 0x3db80 + 0x4e6fc prologues do
    `sub ebp,0x82` frame rebasing (bytes 81 ed 82), so [ebp+0x66] addresses
    LOCALS below the frame, not any record; fn 0x34148 classic frame (push ebp; mov
    ebp,esp) so [ebp+0x66] is a stack scratch/arg slot, written 0 at
    0x37f28-style then INC'd as a loop counter (0x34440/0x34447), never a
    record base ([ebp+0x76] is that function's object-pointer arg).
  VERDICT: ZERO new planet-record flag carriers; the banked |=1/|=2 pair is
  the complete OR-set among boundary-verified sites. ITEM (2) CLOSED (clean
  "no planet carriers" outcome per assignment).
(3) TOOL FIX: boundary_ok's addr&~0xF fallback is self-fulfilling when the
candidate is itself 16-aligned (objdump starts decoding AT the candidate).
Fix in both r1_t106_writers.py and r1_t107_writers_full.py: fallback must
decode from base=addr-16 and WALK the decoded chain to prove addr is an
entry point; never accept a base >= addr.

## P4 — boundary rule v2: objdump wrap-tail semantics (tool fix round 2)

The first boundary_ok rewrite still accepted 0x544f6 as a "verified" site.
Root cause [verified at 0x544f4..0x54500]: objdump WRAPS long instructions —
`mov WORD PTR [ecx+edx*1+0x30ea],0xffff` at 0x544f8 (7 bytes) prints as
'544f8: 66 c7 84 11 ea 30 00' + a tail line '544ff: 00 ff ff' that carries
NO mnemonic. A parser that skips tail lines leaves addr 0x544f6 UNCOVERED,
so the authoritative mid-inspection test misses and the fallback path gets a
vote. FIX (both tools): merge tail-line byte counts into the previous
instruction's length, then mid-inspection is exact and phantoms die on the
fn-start rule. This is the same family as the 0x41835 artifact: the image
decode chain must be walked, never re-seeded near the candidate.

AUTHORITATIVE +0x66 STORE SET after both fixes (run t108_0x66_auth2):
recount pending; expected in-code = the 15 fn-start survivors (plus any
dark-zone 0x52xxx-class recoveries). Data-region entries (>=0x82bb0) are
excluded by the code-span law, not by the boundary rule.
