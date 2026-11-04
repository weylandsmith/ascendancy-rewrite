# WIP t202 — AI GAP ROW 4: DEMOLISH CHANNEL (buildPhase 0x3f130 body)
Trigger triage: timeline size 5,721,578,066 == frozen baseline exactly,
dosbox down, tree clean at 85afdf7 -> no sitting; STATE NEXT stands.

## S0 Source
work/ai_selector_disasm.txt (870 lines) = the AI build evaluator body
FUN_0003f130 (planet obj EDX=esi; fields per OQ-014/t199: +0x10 slot-array
ptr, +0x18 cell count, +0x1c proj progress?, +0x20 orbital progress, +0x42
pop TOTAL, +0x4a cap (cells+10), +0x4c pop USED, +0x57 planet idx; slot =
4B {_, itemIdx@+1, flags, shield}). Item table base image 0x73e40, stride
0x28; item byte+3 = MPOP-word low byte read, word = [ebx+1] sar 0x18 ->
high byte of dword at +1; item byte+5 = REQUIRES.

## S1 OVER-CAP EMERGENCY 0x3f178..0x3f209 (verbatim decode)
- gate: used(+0x4c) < cap(+0x4a) -> jb 0x3f21c (skip block).
- walk i<cells over slots ptr(+0x10)+4i: skip cell item 0xff (empty) and
  item 5; skip item iff byte[+3]==0 (u8 low byte zero); candidate iff
  MPOP(hi)= (u32[item+1]>>24) > best (STRICT >, ties keep FIRST cell);
  best cell idx -> [esp+0xd0] (init -1).
- if found (0x3f1e0): DEMOLISH call 0x38840(eax=planet, edx=cellIdx,
  ecx=1, ebx=itemIdx) @0x3f1eb.
- recheck 0x3f1fb: if used(+0x4c) >= pop(+0x42) -> RETURN 0x3f74c; else
  jmp 0x3f22f (continue into the normal pipeline).
- if NOT found (0x3f20b): call 0x2a424 + 0x3a4e0(planet) then RETURN
  (assert/assert-then-recalc path — NOT modelled in rewrite; bank as
  honest negative).

## S2 NO-FREE-POP LAW 0x3f21c..0x3f229
- cap branch lands here: if used(+0x4c) >= pop(+0x42) -> RETURN; if
  [esi+0x1c]==2 -> RETURN (progress-state guard).

## S3 MIN-REQUIRES DEMOLISH SWEEP 0x3f354..0x3f418 (free pop exists)
- entered from 0x3f2c2 (research-mask bit for species NOT set) and from
  the tubes block fallthrough.
- sentinel ecx=0x1869f (99999 — never binds; REQUIRES u8<=255 always < it
  unless 0xFF? NO: 0xFF=255 < 99999, so item with REQUIRES 0xFF CAN be
  picked if it's first-minimal — CHECK: cmp bl,ecx jge skip: 255<99999
  passes. So 0xFF-requirement items are NOT excluded by the sentinel; the
  0x1869f is a dead init (honest negative, dossier said "never binds" —
  refine: it never binds as a PRUNER, first candidate always wins initial
  comparison).
- walk cells: skip 0xff; skip iff MPOP(hi) >= (cap(+0x4a) - pop(+0x42))
  [note cap-pop here, the FREE-cell margin, computed once per iter into
  [esp+0xcc]]; candidate iff REQUIRES(byte+5) < best-requires (STRICT <,
  ties keep FIRST cell).
- if found (0x3f3e3 else 0x3f41e): DEMOLISH 0x38840 same shape @0x3f403;
  recheck free = pop(+0x42)-used(+0x4c); if <= 0 -> RETURN.
- NO candidate -> 0x3f41e normal pipeline (0x3f41e is shared entry).

## S4 TUBES PRIORITY 0x3f2c8..0x3f349 (research-mask set, for context)
- mask dword [0x7478b + 5*pltype] bit (1<<[esi+0x57]) set -> if
  FIND(item 21) 0x3958c != 0xffff: DEMOLISH it @0x3f2ff, CHECK avail
  item 36 (0x3830c, ebx=0x24) else RETURN, QUEUE-BUY orbital item 36
  (0x38718 edx=0x24 ecx=0); else (item21 absent) 0x3f33b: 0x38818(24)
  guard, cmp 0xffff jne RETURN.
- rewrite: no research-mask/scoring analog for tubes; SCOPE CALL TBD.

## S5 CORRECTIONS FROM RAW RE-READ (t28/STATE summary errors, verbatim lines)
1. OVER-CAP PICK IS **LARGEST UPOP AMONG MPOP==0 ITEMS**, NOT largest MPOP.
   0x3f1bb `cmp byte[item+3],0; jne next` (SKIP if MPOP nonzero);
   0x3f1c1 `mov ebx,[ebx+1]; sar ebx,0x18` = byte+4 = UPOP (item layout
   byte0 IND +1 RES +2 PROS +3 MPOP +4 UPOP, income-law S6); 0x3f1c7
   `cmp ebx,ebp; jle next` strict >, ebp init 0 (0x3f17c xor ebp,ebp) =>
   candidate needs UPOP > 0. No CB skip in sweep but CB skip here (0x3f1a8).
   T28/STATE "largest MPOP (gate >0)" had the byte identity inverted.
2. PRE-TRIAGE SKIP GATE @0x3f252..0x3f28f (STATE omitted it entirely).
   FINAL TRACE (eax=setne(eNR,emptyB); ebx=eax-1 => ebx==0 iff counts
   DIFFER; `xor ebx,ebx` (=>skip) ONLY when ability==2; jl 0x3f295 runs
   triage when eNR<2; je 0x3f41e skips when ebx==0):
     SKIP triage iff (emptyNR != emptyBarren) OR (ability == 2)
     RUN triage  iff emptyNR < 2 OR (emptyNR == emptyBarren AND ability != 2)
   (emptyNR = +0x1c empty NON-ROCK; emptyBarren = +0x20 subset with cls==0.
   COUNTS-DIFFER means a buildable (cls!=0) empty exists -> NORMAL planet,
   triage SKIPPED; counts-equal means only-barren empties -> sweep so the
   AI can convert pop into the barren cell it CAN'T build on... wait
   ability!=2 can't build black: sweep frees a pop+cell pair for the buy
   tail anyway. Economic sense: triage = emergency-vacancy channel, never
   runs on healthy planets. THE WIP S1 LINE 2 FIRST VERSION WAS CORRECT;
   a mid-session "correction" inverted it — this block is the final law,
   cross-checked by r202_triage_census gate proxy (360/1340 open).
   ability byte [0x12fb3+494*owner] (diplo +0x19d); ==2 == BuildOnBlack.
   SHARED PRE-SCORING GATE @0x3f41e: eNR==0 -> RETURN; (emptyB==eNR &&
   ability!=2) -> RETURN; free-pop<=0 -> msgbox 0x30c and CONTINUE (NOT
   return) into the buy tail; buy tail 0x3f478 0x38818(pick cell) fails ->
   buy tubes 21 + RETURN. NOTE 0x3f4b8 cmd1(ecx=1) on the pick-tail cell
   BEFORE the chain call 0x3f4d5 — UNMODELLED residue (t28 bank labelled
   'cmd1 on current +0x52 target'; semantics not re-derived this session).
3. SHARED PRE-SCORING GATE @0x3f41e..0x3f44f: [+0x1c]==0 -> RETURN;
   [+0x1c]==[+0x20] (all empty cells cls-0 = unbuildable) && ability!=2 ->
   RETURN (no scoring at all). ability-2 race can score on cls-0 only.
4. SWEEP MARGIN = cap(+0x4a) - pop(+0x42) [esp+0xc8 - 0xcc verified],
   candidate iff MPOP STRICTLY < margin AND REQUIRES < best (0x1869f
   sentinel never prunes; first-min wins ties; NO item-5 skip in sweep --
   Colony Base CAN be swept).
5. OVER-CAP NO-CANDIDATE PATH @0x3f20b: call 0x2a424 + FUN_0003a4e0(rec)
   then RETURN (assert/recalc; not modelled -- honest negative).
6. TUBES GATE INPUT = mask byte of RESEARCH ROW [byte 0x743e5]
   (0x3f297 mov dl,[0x743e5]; 75*X indexing to 0x7478b tail), bit(owner).
   t28 MEASURED: all 66 mask bytes == 0 across 26 slots x 13 captures ->
   tubes branch DEAD in shipped scenario corpus (honest negative to re-cite).

## S6 SEMANTIC PUZZLE TO MEASURE BEFORE CODING
S6 recalc: +0x4c = UPOP sum over INACTIVE slots only (pending draw). If
that's the whole story, used>=cap means used==pop==cap (clamp law), the
demolish can never change +0x4c (demolished active slot never contributed),
and BOTH rechecks always return -> triage dead. But t198 corpus says used
tracks pop (player "mostly busy"). MEASURE per record: used vs pop vs cap
vs SUM UPOP of ACTIVE items vs pending-UPOP; decide the +0x4c analog truth
(rewrite usedPopFor currently = pending UPOP + automation per S6/t45).
Also census per save: owner ability numbers (diplo row +0x19d), byte
[0x743e5], [+0x1c]/[+0x20] (name-anchored: sys+0x1c = NAME-8, +0x20 =
NAME-4, +0x42 = NAME+0x1e, +0x4a = NAME+0x26, +0x4c = NAME+0x28), then
classify which corpus records WOULD fire each branch.

## S7 Rewrite wiring map (decided)
Insert in buildPhase AI branch BEFORE the t201 emergency-chain block
(original order: triage 0x3f178/0x3f354 < 0x3f4d5 chain < 0x3f4ec scorer).
Demolish = erase ps.items[k] + matching ps.itemCells[k] (income/cap auto-
recompute; all rewrite items ACTIVE so cmd1 internal gate mpop <= cap-pop).

## S8 MEASUREMENTS (r202_triage_census.py + r202c_usedpop_adjudicate.py RC=0,
2900 recs / 20 saves; dump work/r1/t202_triage_dump.txt)
- ADDRESSING PITFALL FIXED: member base B = H + 0x1BF450 (H = find_base vote
  - 0x1BF450, canonical B 0x1BF450). My first pass used H - 0x1BF450 ->
  negative indices wrapped to tail/zeros SILENTLY (item table all-zero);
  planet-window self-checks (IND 77/RES 52/PROS 16) caught layout, the
  item self-check (name@+10 vs planitem.txt) is the one for item addressing.
  Verified live: member 0x2b5ec8 == 'Factory' at B+0x82bb0+0x73e40.
- (used>=cap, used>=pop, pop>=cap) hist: {(T,T,T):220, (F,F,T):680,
  (F,F,F):660, (F,T,F):1340} -> used>=cap fires on 220/2900 (7.6%) and
  always with used==pop==cap (the t199 invariant used<=pop<=cap holds).
  OVER-CAP BRANCH IS LIVE TRAFFIC, not theoretical.
- +0x4c ADJUDICATION (r202c): per save 59/145 used==ACTIVE-UPOP-sum, 45/145
  used==pop-ACTIVE, and the OTHERS are exactly actU+1 examples (51/50+1,
  61/60+1, 34/33+1, 3-vs-pop-3, 4-vs-3) = active workers + Automation
  bonus (diplo row +0x19d==2 at 0x12fb3 = SA_MoreMaxPop index 14 — the
  +0x54 governor==35 term of the t45 recalc branch). INACTIVE-SUM model
  (naive S6 reading) predicts 0/1 for mature planets that read 51/61 ->
  REFUTED as the whole story; the rewrite's usedPopFor (pending UPOP +
  gov-35, campaign.h:220) already encodes the correct decomposition — the
  rewrite's ACTIVE items ARE the worker set, so at selector time
  (no pending) rewrite used==0 NEVER fires used>=cap. THE BRIDGE: the
  220 witnesses are exactly planets pinned at pop==cap; since cap and pop
  are the rewrite's storedCapFor/pop, gate the emergency on
  pop >= cap && !emptyCells (semantic equivalent of used==pop==cap for
  the rewrite's always-working-pop model [documented default]).
- OVER-CAP CANDIDATE LAW RE-VERIFIED against item file: skip item 5, skip
  MPOP!=0, pick LARGEST UPOP strict>, first cell wins ties (Vega IV items
  6/8: MPOP0 UPOP1 — candidates; item 3 MPOP3 skipped).
- RECHECK 0x3f1fb fires used>=pop on all 220 PRE-demolish, but the recheck
  reads +0x4c AFTER the demolish recalc: the victim was ACTIVE (not a
  +0x4c contributor under any reading) -> used unchanged by the cmd itself;
  with used==pop==cap the post-demolish value recomputes to active-sum
  < pop -> CONTINUE (0x3f22f) into the sweep region/scoring. Demolish's
  real effect: frees one surface cell (+0x1c up) + drops channel income;
  growth then unfloors (LAB_000393f9 stops forcing +0x4e=0).
- GATE OPEN census: 360/1340 free-pop recs have c1c<2 (my proxy from the
  empty non-rock non-cls0 count — EXACT operand identity [unverified],
  the original's +0x1c/+0x20 come from recalc stores); c1c==c20 in 240+200
  (all-unbuildable-empty shapes) — ability != 2 there -> gate open.
- MIN-REQUIRES SWEEP VICTIMS: 80/1340 predicted (margin cap-pop>0 + item
  MPOP < margin); the sweep runs AFTER the over-cap block per STATE
  ordering note.
- ABILITY TABLE MEASURED (60.sav, image law B+0x82bb0+0x12e16 stride 0x1ee,
  row+0 = owner idx 0..4 + 0xff pad, ability byte row+0x19d):
  {0:19 IndustryBoost, 1:2 BuildOnBlack, 2:11 BumpShipsInLanes, 3:0
  SuperMarines, 4:8 RepelAlienShips} — species.cpp enum identity ties the
  ==2 override to SA_BuildOnBlack (help L1763 "build on black squares" —
  semantically coherent with a vacancy/cls-0 override!! [inferred]).
- ZERO in-corpus item-loss witnesses across adjacent saves (snapshot ring
  same-turn cluster) -> no direct demolition EVENT witness; branch
  preconditions measured instead (honest negative).
- TUBES BRANCH stays DEAD-code: research-mask bytes all-zero measured t28
  (26 slots x 13 captures) -> banked comment, not modelled (gap map row 4
  tubes sub-item stays GAP-as-dead-path, documented).

## S9 DECISION (rewrite shape)
Pure static picker (pin-able without tables):
  overCapDemolishPick(items, mpop[], upop[], requiresIgnored): first cell
  order, skip item 5, skip mpop!=0, strict-max upop (ties first), gate
  upop>0 (ebp init 0).
  minRequiresDemolishPick(items, mpop[], req[], margin): occupied cells
  only, skip mpop>=margin, strict-min req (0xFF participates), ties first.
Wiring: AI branch, after ind0/usedPop, BEFORE t201 block; over-cap gate
pop>=cap && no empty non-rock cell (rewrite bridge, documented); on pick:
erase items[k]+itemCells[k], NO return (original continues via 0x3f22f);
sweep after gate-open path only when pop-used>0; post-sweep recheck
pop-used<=0 -> skip queue. Pre-scoring gate 0x3f41e (empty==0 or
empty==cls0empty && ability!=2 -> skip queue) modelled via cell scan.
Ability-2 override via species table if cheaply reachable, else documented
default [verify wiring point in code].

## S10 t203 candidate banked NOW (so next session starts clean)
Gap map row 7: free-tech grant on build completion FUN_00046e84 (sole
caller 0x39173, ai-dossier S3c: picks uniformly among legal rows, marks
OWNED, never touches target slot) — rewrite completion path does NOT
grant. Static, small, cites existing dossier.
```

## S11 +0x4c ADJUDICATION (r202d_usedpop_models.py RC=0, 2900 recs)
Model M4 = UPOP sum over ALL slotted items (active+inactive, excl item 23
Ship, excl item flags&0x40, excl slot flags&2) matches used on 2760/2900
(95.2%). The remaining 140 match ONLY actU+1 (M3) — the Automation-bonus
shape (recalc c18 += Automation UPOP when governor byte == 0x23; byte+0x54
census values are NOT item indices in-corpus {0x02,0x08,0x24,0x06,0x07,
0xFF...}, so the t26 cmd3 "+0x54:=item idx" reading does NOT hold in mid-
game saves — the pending/target word identity stays [unverified] residue;
t201's "+0x54 pending" field label inherits the same caveat).
M6/M7 == M4 identically because the pending-upop term measures 0 on
2900/2900 (autosave ring never catches pending != 0xFFFF; INERT in corpus).
M1 (inactive-only, naive S6) survives ONLY on the 820 both-zero rows —
REFUTED as the whole story (mature planets read 51/61, inactive 0/1).
CONSEQUENCES:
 - rewrite usedPopFor UPGRADES: pending-UPOP -> total item UPOP (+gov35
   term kept); player cmd0 gates keep original semantics (live used word).
 - OVER-CAP EMERGENCY semantics [measured + inferred-from-law]: a planet
   whose item-UPOP demand >= cap can ONLY be relieved by demolishing an
   MPOP>0 item — that LOWERS cap(+0x4a recalc) so the clamped pop word
   can grow past the old ceiling and unused pop re-opens. Demolishing a
   UPOP-only item (what the sweep picks) converts demand into free cell
   space. The chain is economically coherent: over-cap -> kill a
   cap-buster -> triage sweep -> queue producers.
 - r202 FIRST-PASS pitfall #2: slot walk capw<40 silently skipped every
   big planet (cap 55/83) — census B "0 candidates" pre-fix was TWO bugs
   (B sign + capw bound). Fixed -> 220 candidates 220/220.

## S12 CALLER-SIDE EMERGENCY SEMANTICS INVERTED (t202 discovery, VERBATIM)
work/ai_selector_disasm.txt tail:
  3f4d5 call 0x3fc4c
  3f4da cmp eax, -1
  3f4dd je 0x3f74c        <-- -1 JUMPS TO FUNCTION RETURN
  3f4e3/3f4ec call 0x3fec4 (need class) -> candidate loop 0x3f528
The t201 STATE line "ret -1 skips scoring @0x3f4da" INVERTED the edge:
  * chain returns -1  -> selector returns WITHOUT normal scoring;
  * chain returns != -1 -> NORMAL need-class scoring runs (0x3fec4).
The chain's own buys happen INSIDE FUN_0003fc4c (buy blocks at
0x3fd15/0x3fdbf/0x3fe5e/... per t201's verbatim pass), so a forced chain
pick already materialised; the non-(-1) fallthrough then MAY queue another
item. REWRITE GAP THIS CREATES (t201 side): current buildPhase does
`pick=chainPick; if(pick<0){normal scorer}` — inverted vs the original.
t202 SCOPE DECISION: fix buildPhase to original order:
  1. triage sweeps (this task); 2. forced = chainPick: forced>=0 -> queue
  it (chain-buy semantics); forced<0 -> RETURN (selector consumed turn,
  no queue); normal scoring ONLY on forced>=0 fallthrough [documented:
  single-queue model queues the forced item; the original's second
  normal-queue leg on forced>=0 kept? NO — rewrite queue is 1 deep;
  queue forced, skip normal this turn].
  PIN the edge: chain-forced planets queue forced item; chain-none planets
  queue NOTHING this turn.
Pure emergencyChainPick() itself stays UNCHANGED (its internal control
flow was verbatim-banked t201; only caller wiring changes).

## S12 CORRECTION of S12-draft (no t201 wiring bug)
The je-0x3f74c edge fires when the CHAIN returns 0xffffffff, and every
SUCCESSFUL in-chain buy path ends `mov eax,0xffffffff; ret` (t201_fc4c
lines 19/62/116/158/193), while the NO-FORCE exit is `3feb9 xor eax,eax`.
So original semantics: forced+bought -> selector RETURNS (no scoring);
no force (0) -> scoring 0x3fec4 runs. REWRITE emergencyChainPick returns
item id on force / -1 on no-force and `if (pick<0) {scorer}` -- the two
-minus signs are DIFFERENT values on the two sides; the t201 wiring is
FAITHFUL. No fix needed (S12's earlier draft, written before reading
t201_fc4c tails, claimed inversion -- it was wrong; keep this entry to
stop a future session "fixing" a non-bug).

## S13 FINAL buildPhase AI-branch flow (wired t202)
1 ind0>0 (0x3f146; 0x3f758 special gate NOT modelled -- no ship model).
2 OVER-CAP 0x3f178 (usedPopFor>=storedCapFor): victim via cell-indexed
  scan (skip empty/-1, skip item 5, skip MPOP!=0, LARGEST UPOP strict>,
  init best 0 so UPOP==0 never wins); none -> SKIP selector (0x3f20b
  assert+recalc+return); else erase item+cell, recompute, used'>=pop ->
  SKIP (0x3f203 verbatim jae return).
3 NON-OVER-CAP: used>=pop -> SKIP (0x3f220 no-free-pop-no-build law).
4 TRIAGE GATE 0x3f252: SKIP triage iff eNR>=2 AND (eNR!=eB OR ab==BB);
  RUNS iff eNR<2 OR (eNR==eB AND ab!=BB). eNR=empty NON-ROCK surface
  cells (+0x1c recalc), eB=empty cls-0 cells (+0x20 subset), ab=owner
  ability (abilityOf==BuildOnBlack <-> byte 2, M4 census + species enum).
  MEANING: emergency vacancy channel -- fires only when NO buildable
  (non-barren) vacancy exists (or <2 empties); healthy planets NEVER
  triage. TUBES leg 0x3f2c8 DEAD-code comment (research mask all-zero,
  t28 26x13 measurement) -> straight to sweep.
5 SWEEP 0x3f354 min-REQUIRES (margin=cap-pop; skip MPOP>=margin; strict-<
  req wins, 0xFF PARTICIPATES (255<0x1869f sentinel never prunes -- t28
  "sentinel never binds" stands, its reason corrected); first cell wins
  ties; NO item-5 skip). Demolish; post free-pop recheck 0x3f414 MODELLED
  BUT UNREACHABLE: pre-guard (3) ensures used<pop and demolish only
  LOWERS used -> free>0 always. HONEST NEGATIVE: 0x3f418 return path
  dead in the original too UNLESS state mutated between (recalc asserts)
  -- the 0x3f23b msgbox 0x2ba leg is likewise a debug assert.
6 SHARED GATE 0x3f41e (AFTER any demolish, recomputed facts): eNR==0 ->
  SKIP; eB==eNR && ab!=BB -> SKIP. 0x3f478 random-cell + 0x3f4b8 cmd1-
  noop-on-empty + tubes-buy-on-fail: rewrite queue path stands (t201
  documented deviations); 0x3f4b8 cmd1 semantics stay [unverified] bank.
7 CHAIN (t201) -> SCORER exactly as t201 wired.

## S14 HANDOFF (budget stop: MEASUREMENTS LANDED, CODE DEFERRED)
Implemented this session: NOTHING in rewrite/ (usedPopFor upgrade drafted,
REVERTED — blast radius on campaign_pop_band_law_t199 + needClassFor
untestable in remaining budget; do it WITH the pins in t202b).
Landed: r202_triage_census.py (gate proxies + over-cap/sweep victim
counts + diplo ability census; run RC=0, dump work/r1/t202_triage_dump.txt),
r202b_layout_verify.py (item-table member addressing self-check: B =
H + 0x1BF450, name@+10 vs planitem.txt), r202c_usedpop_adjudicate.py,
r202d_usedpop_models.py (M4 2760/2900, M3-residual 140, pending term
INERT 2900/2900). Laws S1..S13 are FINAL (S2 gate = triage runs iff
eNR<2 OR (eNR==eB AND ability!=BuildOnBlack); sweep min-REQUIRES incl
0xFF; over-cap victim = largest-UPOP among MPOP==0 non-CB cells).
T202B SCOPE (pure code + pins, all inputs in this file):
 1. usedPopFor -> item-UPOP-sum per S11 (update t199 pop-band pin
    expectations + needClassFor comment; governor law t45 stays).
 2. buildPhase AI branch: over-cap block + triage gate + sweep per S13
    (insert BEFORE t201 emergency block; keep t201 wiring — S12 proves it
    faithful).
 3. Pins: overCapDemolishPick / minRequiresDemolishPick pure statics +
    end-to-end advance() witness that an AI planet at used==cap demollishes.
 4. ai-dossier gap row 4 -> MODELLED (tubes sub-item: dead-path note);
    income-law.md S9 OVER-CAP paragraph CORRECTION (largest-MPOP ->
    largest-UPOP-among-MPOP-0; cite this file S1).
UNRESOLVED RESIDUES (honest, keep open): +0x54 word identity mid-game
(t26 cmd3 reading contradicts census); 0x3f4b8 cmd1-on-tail semantics;
M3-shape 140 rows discriminator; msgbox-legs are debug asserts (banked).
