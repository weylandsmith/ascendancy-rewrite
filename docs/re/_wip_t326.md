# t326 WIP — PHASE BOMB FORCED-CAPTURE (OQ-016 residue 1, the nuke law)

## S0. Session start (fresh, 2026-11-07)
- Assigned: STATE.md NEXT = t326 verbatim. Queue rows t327/t328 follow.
- Sitting check: NEGATIVE — playcap tail-seek newest turn 1086 == corpus
  (file mtime 2026-11-07 02:17, writer idle). r1_t85g_sitting.py NOT run.
- git clean at session start (tree == 26b278d t325).

## S1. Target definition (from docs, verbatim)
- gizmo 70 Phase^Bomb, gizmos.txt row `5 4 25 0 1 40 0 0 13 3 255`
  (Cat5 special, Power4, Range25, Level0, NumUses1, Industry40, Sp1=0, Sp2=0,
  ResReq=13, flag 3). gizhelp gizmo70: "launched at a planet and destroys
  structures on the planet's surface. used only once ... short range".
- Residue-1 witness bar (OPEN-QUESTIONS + BLOCKED §Nuke): identify the
  dispatch entry by which code first writes FF into a mid-record planet slot
  byte at launch time; bank the witnessed destruction law to economy.md.
- Static prior state (BLOCKED §Nuke): CMP-imm70 sites all dead ends
  (0x796ad/0x79a02/0x7a49a ASCII parsing; 0x3f6eb AI 70-TURN reject; 0x3ddc0
  msg-id region; 0x820xx data). Claim: "special-device effects are
  DATA-DISPATCHED (no in-code caller; same shape as event-24 dispatch 0x4402a)".
- t329 carried law (BINDING, cited): gizmo-use orders arm ONLY via the
  batmode-family state-word tail 0x15c63/0x15da6 gated on [ebp+0xb1]
  (writerless per t323 census + t324 RAM); commit edges 0x25560/0x25570
  (t88a, mode==1 only) unreachable without the armed order.

## S2. Chain facts (file-derived, verbatim)
- gizmos.txt header law: "ResReq = The research node which allows this item,
  or 255 if no research required"; flag_list 255-terminated. Phase Bomb flags
  = {3} = GZ_TARGETSURFACE (8) ONLY — targets a planet SURFACE (consistent
  with gizhelp "launched at a planet and destroys structures on the planet's
  surface"). NOT GZ_TARGETSHIP/LANE/ORBIT.
- RESREQ = 13 -> restree row 13 (0-based, header line 66 count) =
  `Molecular^Explosives  0 120 7 9 255` — prereq chain: row 7
  `Spectral^Analysis (0 120 2)` -> row 2 `Tonklin^Diary (0 50)` (root), and
  row 9 `Momentum^Deconservation (0 140 3)` -> row 3 `Spacetime^Surfing
  (0 90 1 2)` -> rows 0/1/2. COSTs 120 + 140 (+ chain roots 50+90+50).
  gizmos.md S20 already established ResReq indexes == restree rows (2nd
  independent source).
- Phase Bomb is NOT a planitem (planitem.txt has no Bomb row; only
  Lush^Growth^Bomb item + Orbital^Missile^Base) => it enters a ship ONLY via
  ship DESIGN at a Shipyard (gizmo Industry 40 adds to ship cost).
- batfx.txt PhaseBomb row `44 60 49 65` (fx sprite ids, banked context).
- Production campaign t=1086: does race 0 ALREADY have tech 13? UNKNOWN —
  research-state RAM field not yet located. If yes, the route collapses to
  design+build+launch only.

## S3. Route decision log
- t329 binding law says gizmo-use orders arming is dead via the mouse road
  ([ebp+0xb1] writerless). CAUTION banked at session start: whether a Phase
  Bomb launch rides that same tail was UNTESTED. RESOLVED THIS SESSION by a
  whole-image sender census (S4) — the launch road is cited-dead two more
  ways. Decision: DO NOT spend the 4-launch capture on a refuted-by-census
  path; requeue a ONE-launch route-probe (armed commit-edge legs) and move
  t327 forward. (Queue law honoured: t326 is finished with a banked negative,
  its queue row replaced by t326b.)

## S4. MEASUREMENTS (this iteration, all offline; tool scripts/r326_precensus.py exit 0)
Production ring newest (45/52.sav, B=0x1bf4d8, t=1086 corpus):
1. KNOWN-TECH MASK FIELD LOCATED (new reusable law, from cheat body 0x47828
   verbatim): tech row i owned-mask byte at ds:0x7478e + 0x4b*i (save member
   B+0x82bb0+that), bit (1<<race); count word ds:0x74744 == 66 in play.
   research.md S6c "who-researched-what lives elsewhere and is still
   unmapped" — now mapped (mask semantics corroborated, see 2).
2. row13 = Molecular^Explosives mask = 0x05 -> RACES 0 AND 2 ALREADY OWN the
   Phase Bomb tech at t=1086. The recipe's research leg is VACUOUS in the
   corpus save; route collapses to design+build+launch.
   Prereq-closure check: 110 in-play edges, 10 violations — ALL 10 are
   race-0/2 deep-tree rows whose prereq chain passes through rows the race
   skipped (e.g. tech 50 Hyperdrive <- 33 not owned by race 0) => the vendor
   gate is NOT strict-AND on this mask reading; either the mask records
   something slightly different (available/researched-once) or the gate has a
   fallback. HONEST: mask semantics = corroborated-not-proven; do not wire
   the mask into the rewrite on this datum alone.
3. cidx-70 (Phase^Bomb) carriage census: ZERO carriers in 30 ship rows
   (owner-0 kinds {3:3, 5:8}). Same witness-class as t329's magnetron datum.
4. Shipyard(22) ACTIVE slots: 30, ALL owner-0, ALL class=1 (ORBITAL) —
   zero surface Shipyards; plus 2 pending Shipyard builds (Cambria II/IV).
   The BLOCKED recipe's "build at a Shipyard" is satisfiable in-UI (30 exist),
   and the class histogram confirms the OQ-014 row law family (Shipyard is
   an orbital row) — the recipe's planet-surface framing was sloppy.
5. MODE-1 ARMING MESSAGE CENSUS (whole work/t91_code_disasm.txt):
   `mov edx,0x4d` -> ONE site 0x15454 = call 0x2a428 (ebx=0x122, edx=0x4d) =
   the VENDOR ASSERT REPORTER, not a message post; 0x4e/0x4f/0x51 -> ZERO
   senders; 0x50 -> the three known non-post sites (t321 S5).
   windows.txt SENDMESSAGE census: values seen {..,71,74,76,84,..} — NOTHING
   in 77..81 (0x4d..0x51). And the msg->mode map: cmp dx,0x50 @0x1b7cd routes
   BELOW -> 0x1af4e, EQUAL -> 0x1b5ba (the t296 publish leg, which does NOT
   set mode), ABOVE -> 0x1b7dd sets BYTE[ebp+0xb7]=1 (mode 1).
   => NO SENDER EXISTS that can arm mode 1 in the captured build.
6. CHAIN COMPOSITION (inferred from 5 + carried cited laws): Phase Bomb
   launch needs (a) mode-1 arming msg — census-proved no sender (S4.5);
   (b) the gizmo-use-order tail 0x15c63/0x15da6 gated on [ebp+0xb1] —
   t323 writerless + t324 RAM-absent; (c) commit edges 0x25560/0x25570 —
   t329 unreachable unarmed. Three independent cited-dead legs.
   DISPOSITION: the nuke destruction law is UNREACHABLE-BY-CAPTURE in the
   captured build (closure class = cited, same class t323/t324 accepted for
   OQ-019). STRICT-CLOSE: OQ-016 residue 1 does NOT flip closed (no live
   destruction witness; static census is not a live measurement of the law).
7. CONSEQUENCE: the t326 4-launch forced-capture cannot reach its witness bar
   (launch is dead); spending launches to confirm three already-cited legs is
   re-trod. ONE-launch route-probe (t326b) is the cheap residual witness:
   arm legs at 0x1b7dd (mode-1 setter), 0x1b5ba (msg-50 publish), 0x25560,
   0x15c63 under the r325 early-arm-at-title shape; a zero-census with alive
   control converts S4.5 from static-cited to LIVE-cited for the OQ-016 row.

## S5. SECOND SENDER FOUND — the 0x17xxx gizmo-event block (OPEN, contradicts a clean "no sender")
Verbatim (work/t91_code_disasm.txt 3645-3715): inside the function enclosing
0x17c54, `call 0x39b6c` dispatches on al = BYTE[[edi]+1]; then a cascade
compares cl (same byte): 0x1c -> stack-dword[esp+0x54] := 0x4c (76); 0x1d ->
:= 0x4d (77); 0x1e -> := 0x4e (78); else assert reporter 0x2a438 (ebx=0x20e).
[esp+0x54] is then read at 0x17cf8 into edi and used as an INDEX into
[esi+0x1a92+edi*4] / [esi+0x1bcc+edi*4] before calls 0x1ce1c + 0x17694.
SIBLING SITE (same block family): 0x16147 `mov ebx,0x51` (81) with
edx=[ebp+0xbb], eax=0x7a35c, then a post-shaped call — 0x16122 clears
[ebp+0xb1]=0 right before it. Semantics UNWALKED: could be gizmo-USE event
posting (would REVIVE the launch road via a path t329's 0x15xxx scope missed)
or UI-string/table indexing (would corroborate dead). NOTE the 0x1c/0x1d/0x1e
dispatch keys are NOT 70/71/72, so even the revive hypothesis needs the walk.
DECISION (revised): t326 lands as an OFFLINE-CENSUS iteration (S4); the NEXT
task is the zero-capture static walk of fn(0x17c54) + fn containing 0x16147 —
it decides whether t326b (capture probe) or t327 (tool v2) runs next. Do NOT
run the 4-launch capture before that walk.
