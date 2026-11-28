# tCITE-AUDIT — docs/re code-citation boundary audit (2026-11-27)

## P0 Premise audit (before spending anything)
- DECISIONS.md branch check: `grep -n "ADJ OQ-\|ADJ D3" docs/DECISIONS.md` -> EMPTY.
  No ruling block landed. Branch (B): ONE control-plane hygiene audit, thinnest
  real one. Last sitting work/r1/playcap/live-timeline.jsonl mtime 2026-11-26
  00:30 (unchanged since the tOQ19-AUDIT sitting check) -> no new play sitting,
  assignment stands.
- Class-spend check vs docs/REFUTED-ROUTES.md: this audit touches NO capture,
  NO budget class, NO scripted-mouse/debugger route. It reads only
  docs/re/*.md, work/ascend_restored.bin, work/functions_full.tsv. Not a
  re-queue of a spent class.
- Prior-audit check: docs/re/census-audit.md is a WRITE-CENSUS verifier audit
  (t107/t108, tool-level). r1_t108_disp32_audit.py adjudicates disp32 claims by
  VALUE. NOTHING in scripts/ reads docs/re and checks a cited code address
  against an INSTRUCTION BOUNDARY. The failure mode is live and documented:
  tPF-4 landed "0x3cca4 start was mid-instruction, dispatch ends 0x3cca7".
  So the class is unspent.
- Authority for the boundary check: pointer law (OQ-011 CLOSED) -> guest linear
  == physical, restored image is imagebase 0 (OQ-008 CLOSED), obj0 code span
  [0x14bb0,0x82bb0). work/functions_full.tsv = ghp5 function starts (1,144).

## Method (one pass, zero capture)
1. Extract every 0x hex token from the DURABLE law docs (docs/re/*.md excluding
   _wip_* and *_draft_*), keep tokens in the obj0 code span.
2. Decode each ghp5 function from its OWN start for its own size (capstone,
   1-byte fallback on undecodable bytes) and collect the set of instruction
   boundary addresses.
3. A cited code address that is NOT in the boundary set is a candidate defect:
   either (a) the doc cites a mid-instruction site (real doc defect — fix the
   doc), or (b) the token is not an instruction site at all (data blob inside a
   function, jump-table entry, a value used as an immediate, a file offset that
   coincidentally lands in the code range). Every candidate is adjudicated by
   hand-disasm before any claim.

## P1 Pipeline (tools this task: scripts/tCITE_boundary_audit.py,
## tCITE_adjudicate.py, tCITE_full.py, tCITE_callsites.py; run with
## ~/tools/revenv/bin/python — .venv has NO capstone)
- 53 durable docs/re/*.md (excluding _wip_/_draft_), 5,358 code-span
  (0x14bb0..0x82bb0) hex tokens. Candidates (not a ghp5-decoded instruction
  boundary): 1,235. Auto-adjudication: JUMPTAB 496 (u32 stored outside any
  function names the addr = dispatch target, fine), OPERAND 653 (sits inside
  a valid instruction = byte-scan/fixup anchor convention, fine unless prose
  claims a call/entry SITE), REACHABLE 18 (real insn sites in ghp5 map holes),
  RESIDUAL 68 -> 62 unique with site-role prose, all hand-adjudicated (P2).

## P2 Hand adjudications (62 unique; verdicts)
- DATA addresses inside obj0 code range or inside ghp5-mapped data blobs
  (0x7478b, 0x43502/0x43508, 0x7a358/0x7a35c, 0x7653c (runtime rebased,
  ships.md:334 cites B+0x82bb0+0x7653c explicitly), 0x701e0, 0x18247 param
  chain, 0x2c030-0x2c034 jump-table interiors, 0x79950/0x79c20, 0x3a0e9
  computed-base, 0x177d3, 0x1642c/0x33375 literal-census sites) — FINE, my
  token classifier just can't see the ds:/DAT prose on the wrapped line.
- Range-edge cites (0x14bb0 code-span bound, 0x42c60..0x42e6e, 0x3144a..,
  0x16060..0x16200, 0x27560..0x27e7f, 0x1da8a..0x1daaf, 0x22034 body end
  [insn at 0x22034 confirmed], 0x37e40 header range end, 0x465aa range end,
  0x23a20 loop start [reachable], 0x30b90..0x30bf3 sweep range) — FINE.
- Byte-verified code cites whose site lives in a ghp5 MAP HOLE (boot.md
  0x52a67 `call 0x238e8` VERBATIM at bytes; 0x52d6c, 0x52e58, 0x544f8 mov
  VERBATIM, 0x2ef60, census-audit 0x41830/0x41835) — FINE; NEW LAW:
  ghp5 functions_full.tsv is INCOMPLETE as a boundary oracle (map holes
  0x52axx region, GAP 0x2b3d2..0x2cf04 — the latter already documented
  ui-runtime.md t442), so "not a boundary" is a CANDIDATE, never a refutation.
- ui-runtime.md:773 internal calls 0x2b774->0x2c034, 0x2ba35->0x2c4f5,
  0x2bb09->0x2c2c9: all three VERIFIED as E8 rel32 operands (forward-decode
  desync on data islands was my artifact). FINE.
- aicode.md 0x1e0e70 cites = RUNTIME addresses (kind0 0x1dcdd9 context,
  runtime img) — out of file span; FINE. combat.md 0x4bb56 = call SITE
  (insn `call 0x4b740` at 0x4bb56, VERBATIM); dosbox-debugger.md 0x54ac5 =
  call site (`call 0x56b5c` @0x54ac5, ret0@0x54aca matches doc); ships.md
  0x54b79 = post-call post-site (fn 0x55ae8 sole E8 caller 0x54b74 cited
  consistently); ships.md 0x2554f = call site (`call 0x41260` @0x2554f,
  `or edi,eax` @0x25554 VERBATIM). ALL FINE.
- boot.md:306 `call 0x52a67` — call SITE convention, insn VERBATIM. FINE.

## P3 DEFECTS FOUND (2 in 5,358 tokens = 99.96% clean)
1. TRUE MIS-CITATION — ships.md:1833 (and origin _wip_t310.md:24,53):
   "star LABEL builder (string ids 0x2b13/0x2b14, format call 0x250bb)".
   ZERO rel32 call operands name 0x250bb anywhere in the code span (E8 scan
   2,734 targets; raw u32 0x250bb occurs once, at 0x3e898, unrelated). The
   label builder fn 0x51b68..0x51e8e's actual format chain (decoded from fn
   start, VERIFIED): 0x51bc0 `mov eax,0x2b13` (id select; 0x2b14 not seen in
   this fn — t310 claim of BOTH ids is loose), 0x51c17 `call 0x21a20`
   (format, 18 referrers), 0x51c23 `call 0x76c79` (140 referrers).
   0x250bb sits mid-instruction (0x250b7 `mov edx,0x838bf` spans it) — the
   shape says a byte-window artifact was read as a call target. FIXED in
   ships.md with cited bytes; _wip_t310.md annotated (wips are history,
   annotated not rewritten). No rewrite code depended on it (grep: no
   250bb in rewrite/).
2. PRECISION — aicode.md:83 `0x3e6f0 status<0 -> eliminated branch`: the
   gate is `cmp dword [eax+3],-1` @0x3e6ee + `je 0x3e81a` @0x3e6f2; 0x3e6f0
   is mid-instruction. Law itself correct (je target + follow-on 0x402d8
   @0x3e6f8 VERBATIM). Fixed to 0x3e6ee.

## P4 Standing lessons (banked)
- A code-address citation classifies into SITE / OPERAND-ANCHOR / DATA /
  RUNTIME / RANGE-EDGE before it can be called wrong; the boundary-oracle
  (ghp5 tsv) has holes, so refutation needs a POSITIVE contradiction
  (e.g. zero rel32 referrers for a claimed call target), never mere
  non-boundary.
- The one real defect survived t310's own re-verification because the claim
  was checked as "0x250bb exists in the region", not "a call names 0x250bb".
  Call-target cites must be validated against E8 operands (or the call's
  bytes), not against region membership.

## P5 tCITE_callsites.py standing disposition (10 residual OFFENDER lines,
## all FINE — do NOT re-adjudicate these shapes):
- CALL-SITE cites (the E8 opcode sits AT the cited addr; the doc names the
  site, not the target): boot.md 0x52a67 (`call 0x238e8` VERBATIM),
  combat.md 0x4bb56 (`call 0x4b740` VERBATIM), dosbox-debugger.md+ships.md
  0x54ac5 (`call 0x56b5c`, ret0@0x54aca consistent), ships.md 0x54b79
  (post-call post-site; sole E8 caller 0x54b74 cited alongside), ships.md
  0x2554f (`call 0x41260` + `or edi,eax` @0x25554 VERBATIM), ui-runtime.md
  0x2b774 (E8 operand -> 0x2c034, VERIFIED via operand scan).
- RUNTIME addresses (out of file span): aicode.md 0x1e0e70 x2 (runtime img
  addresses in the kind0/kind1 tail context).
- ships.md:1835 is THIS audit's own correction quoting the dead 0x250bb.
The scanner is a CANDIDATE generator; the P2/P5 adjudications are the verdicts.
