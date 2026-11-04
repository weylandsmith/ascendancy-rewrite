# WIP t280 — AI GAP ROW 11: REMAINING BODIES AUDIT (pure code)

## S0 — Intake
- Pre-flight: r214_triage RC=0 — tail 400 rows ALL turn 645 (tutorial-lineage
  churn), 0 bad json, one canonical key shape; VNC client ESTAB :5910 -> t279
  HELD; production :9 pid 576895 alive. No sitting -> t280 verbatim.
- Scope: §6.3 has bodies for indices 5..13, 15..20; 15/18 are NOPs; t256
  upgraded 4 (12/17/19/20). Remaining 12 = active bodies {5,6,7,7,8,9,10,11,
  13,14} minus t256's four... precisely: 5 HealShips, 6 ForcePeace, 7
  DoublePower, 8 Repel, 9 Sap, 10 Cornucopia, 11 Bump, 13 Shield, 14
  MoreMaxPop + NOPs 15/18.

## S1 — MEASURED: §6.3 IS MISSING BODY 14 (SA_MoreMaxPop) — READ VERBATIM
- Jump-table re-read (restored FILE 0x43b10, 16 u32 LE, cases al=0..15 ==
  ability 5..20): entries 43baf bf0 3c3f 3c79 3d33 3de4 3e98 3eec 3fba
  **4402a** 4400a 4405f 440b5 4400a 4414e 4418e. Case index 9 (ability 14)
  -> 0x4402a: a body EXISTS; §6.3 jumps 13->15 and never documents it.
- Raw disasm (capstone, work/ascend_restored.bin, image addr == file offset):
    4402a mov edx, 0x2b057          ; static planet pool (t102 law)
    4402f xor edi, edi
    44031 jmp 0x44037
    44033 inc edi
    44034 add edx, 0x7b             ; stride 123
    44037 mov eax, [0x3a091]        ; dword; >>0x10 = u16@0x3a093 = planet
    4403c sar eax, 0x10             ;   count (STATE: bound 145) - loop bound
    4403f cmp edi, eax
    44041 jge 0x4400a               ; T1 exit (counter reset)
    44043 mov al, byte [edx+0x57]   ; planet OWNER byte (t248 law)
    44046 cmp al, byte [ebp]        ; vs self race byte
    44049 jne 0x44033
    4404b mov cx, word [edx+0x55]   ; capBase seed word (income-law S10)
    4404f add ecx, 2                ; +2 (word write: mov cx back at 44054)
    44052 mov eax, edx
    44054 mov word [edx+0x55], cx
    44058 call 0x38ba4              ; planet recalc (cap recompute)
    4405d jmp 0x44033
- INDEPENDENT CORROBORATION (banked, pre-existing): income-law.md S10 names
  the SAME site from the corpus side — "EVENT MODIFIERS of the seed word:
  +2: scan 0x4402a (planet base 0x2b057 stride 123 = 0x7b) adds 2 to EVERY
  owned planet's +0x55 then recalcs; no in-code caller found (data/vtable
  driven — event dispatch)". My read supplies the missing caller identity:
  THE CALLER IS THE ABILITY DISPATCH (0x441d8 jmp cs:[eax*4+0x2ef60], case
  al=9 == row+0x19d 14 == SA_MoreMaxPop, help.txt abil14 "The Mebes are good
  at populating... increase the maximum population of all your colonies").
- CITED BODY LAW: SA_MoreMaxPop 0x4402a — for EVERY planet in the static
  pool with owner == self: WORD capBase(+0x55) += 2, then per-planet recalc
  0x38ba4 (which re-seeds +0x4a = clamp(0,100, +0x55 + MPOP-sum)). NO
  pending-item gate (contrast IndustryBoost 0x4418e [p+0x54]!=0xff), NO
  [p+0x16]==10 skip (contrast Cornucopia), NO clone/rock gate. Delta +2,
  operand SEED word, NOT the capped cap.
- REWRITE DEFECT CONFIRMED: campaign.cpp:1720 `planets_[s].capBonus += 25
  [documented default]` — WRONG OPERAND (capBonus is added AFTER the 0..100
  clamp at storedCapFor campaign.cpp:809-812, vendor mutates the pre-clamp
  seed) AND WRONG MAGNITUDE (25 vs 2). The rewrite already carries the
  +0x55 analog as PlanetState::capBase (campaign.h:43) -> upgrade is
  `capBase += 2` verbatim.
- HONEST BOUNDARY: the t31 "+2 residual" class (1756/46132 samples where
  +0x4a == equation+2) is NOT explained by this body (firing moves +0x55 and
  +0x4a together, leaving the ledger equation intact); S10's residual stays
  open. [inferred] note only — the body itself is [verified].

## S2 — FULL BODY RE-READ vs §6.3 (capstone over work/ascend_restored.bin,
## listing banked work/t280_bodies.txt). Verdict per body:
- 5 HealShips / 7 DoublePower / 8 Repel / 9 Sap / 10 Cornucopia / 11 Bump /
  13 Shield / 16 BlockStarLanes / NOPs 15+18: §6.3 ACCURATE; rewrite keeps
  its documented aggregate abstractions (row 11 labels stand). Shield T2
  exit re-read: counter := cad - counter AT the equality point == 0, so the
  rewrite's single reset is EXACT (not just modelled).
- *** ERRATUM 1 (body 6 SA_ForcePeace 0x43bf0): the threshold is the TARGET
  ROW's PROPOSE_PEACE, not self's ACCEPT_PEACE. Raw: ebx = dword[row_x +
  0x1cb]; sar 16 -> word[row_x + 0x1cd] = PP(x) (field map diplomacy.md
  L179); ebx += 0x14; cell word[row_x + 0x1b2 + 2*self] (= att[self->x] per
  the row=victim/index=attacker law diplomacy.md:656) skipped iff >= PP(x)
  +20, else := PP(x)+20. §6.3's "([self+0x1cb]>>16)+20 / ACCEPT_PEACE"
  mislabels BOTH the row (eax iterates x, self-skip cmp eax,ebp precedes
  the load) and the field (>>16 lands on +0x1cd). Corrected law: floor
  att[self->x] at each x's own PP+20. Rewrite state carries no att[self->x]
  for x!=player and player->AI attitude is unmodelled -> NO code change
  this iteration (announce/end-wars divergence stays documented); erratum
  banked for any future wiring.
- *** ERRATUM 2 (body 17 SA_Hatred/CauseWar 0x440b5 — the body t256 wired):
  raw (verified instruction-walk, walking pointer [esp+0x6c0] starts at
  ebp=self and steps +1/byte through self's state window): OUTER k != self
  with byte[self + 0x1c0 + k] == 2 (state toward k == AT WAR) — §6.3 right;
  INNER x != self, x != k: cell word[row_x + 0x1b2 + 2k] == att[k->x]
  (enemy k's attitude toward third party x); THRESHOLD word[row_x + 0x1c9]
  == DECLARE_WAR(x) — the THIRD PARTY's line, NOT "[r+0x1c9]" as §6.3 says
  (edx = 0x12e16 + 0x1ee*x steps with eax=x; ecx = row_x + 2k); clamp
  att[k->x] := DW(x) iff att[k->x] > DW(x). So the vendor ceilings the
  ENEMY's attitude toward every onlooker at the onlooker's own war line ->
  k (low-DW enemies of the onlookers) trips its own declare-war chooser
  against them [inferred effect leg]. t256's Campaign::hatredClamp clamped
  att[x->self] at DW(r) — WRONG CELL AND WRONG THRESHOLD (inherited from
  §6.3's mislabel). Under the CORRECTED law the rewrite's two-party state
  (att = AI->player only) holds NONE of the law's cells (all att[k->x] are
  k,x != player = AI->AI, row 12's absent state; x==self==player is
  excluded by the law itself) -> CauseWar becomes ANNOUNCE-ONLY:
  hatredClamp + its mutation + pin species_cause_war_hatred_ceiling_t256
  RETIRED t280 (t256 measured nil blast radius: specnum 17 never in default
  AI slots 0..5, gate seeds unaffected).
- Body 14 SA_MoreMaxPop 0x4402a: NEW (S1) -> wire capBase += 2 verbatim.

## S4 — CELL-DIRECTION SELF-CORRECTION (banked before code shipped)
- My FIRST reading said row = victim (att[k->x]). Three banked witnesses
  refute that and agree on row = HOLDER, col = TARGET:
  (1) aicode.md §13.2: `mov ax,[esi + other*2 + 0x1b2]` annotated
      att[self][other], compared against SELF's ACCEPT_ALLIANCE;
  (2) diplomacy.md §19 (t207): the clamp at row(victim)+0x1b2+2*attacker
      "SLAMS the victim's attitude below its own declare-war line";
  (3) r1_playcap_watch.py relation() docstring: "atts[i][j] = attitude of
      i toward j (+0x1b2+2j)" — the live-RAM convention n x n census ran on.
- Consequences AFTER correction (docs corrected in aicode.md E2/E3, code
  comments, abilities.md rows):
  ForcePeace: floors att[x->self] at PP(x)+20 (chooser-armed peace, NOT
  same-turn end) -> rewrite keeps end-the-wars abstraction, DIVERGENCE
  labelled (floor needs player->AI attitudes, absent state).
  CauseWar: ceilings att[x->k] at DW(x) (onlooker's regard for the ENEMY)
  — every cell AI->AI -> announce-only under every owner; hatredClamp
  retired (t256 wired att[x->self] at DW(r) — wrong in BOTH operand slots
  of §6.3's formula).
- Note the honest boundary: the rewrite's CauseWar/ForcePeace state
  conclusion (no addressable cells) holds under BOTH direction readings;
  the correction changes WHAT the vendor does (banked law), not the
  retirement decision. t256's mutation-verified pin pinned §6.3's text;
  the new pins pin the corrected boundary.

## S5 — FINAL STATE
- Suite 158/0; mutations: capBase+=0 CAUGHT, dipState_ write in CauseWar
  CAUGHT; both reverted (git diff clean of probe markers).
- OQ ledger: OQ-016 ANNOTATED (caller identity of the +2 modifier CLOSED —
  a sub-residue, not the row), row STAYS OPEN; strict-close honored — the
  MoreMaxPop default->cited upgrade is rewrite-side law alignment, the row
  keeps its terrain/nuke/home/template sub-items.
- No OQ CLOSED this iteration. Ledger audit + index check must stay
  15/4.
