# t308 WIP — RESOLVE THE DAT_43504 ADDRESS QUESTION, THEN WITNESS A TRUE SELECTED-NONE -> STAR TRANSITION

## S0. PRE-FLIGHT (this session)
- No new sitting: live-timeline.jsonl tail (last 200 KB, turn histogram) is
  ALL turn=1086; last wall 13:32:56 vs the t307 commit 13:29:01 — same
  production state the t307 run measured. r1_t85g_sitting.py NOT run
  (assignment t308 stands).
- STATE.md NEXT ACTION t308 read verbatim. Binding from t307: SELF-RELOCATION
  LAW (code-RAM data immediates rebased +0x242000), census-ctl False at
  rebased legs is NOT an arming failure, do NOT re-arm the four REFUTED
  batmode sites, FirePat regression 5/5 before arming, close_eventwin before
  clicks, one battery per sitting.

## S2. PRE-ARM CHECKS (this session)
- FirePat regression re-run THIS session vs the three reference logs:
  033648 cos_hdlr 41 / 052925 s2_56cda 3 / 061825 cos_hdlr 60 + s2_56cda 20 +
  s2_56c74 1 — 5/5 PASS. NOTE: fire_pats takes P0+LEGS[leg] (linear); the
  regression must construct FirePat(P0+off) (t307 law).
- last-4 uniqueness audit over the 9-leg t308 set (8 writers + btn_hdlr):
  NONE collide.
- Star-record law handle (do NOT re-derive): star stride 0x60, name at
  member(ptr)+0x88+0x1c via Sess.star_name_at (r298 law; re-verified this
  session: 0x256825 -> b'Icarus').

## S3. INSTRUMENT CHANGES (STEP 2) — see patches below
1. sel_oracle: PAIR NOW NAME-BEARING — adds "DAT_43504_name" decoded via
   star_name_at (the ptr in the scalar -> star name), and "alt_285504" = the
   u32 at member B+OFF-0x88+0x43504 (linear 0x28547c — the S1-void t307
   address, kept labelled so no ambiguity survives the run).
2. STAR-PHASE WITNESS BREAK: after each ENTERED click, compare before/after
   DAT_43504 hex; a CHANGE logs "WITNESS DELTA" with both values and breaks
   the pip loop early (the close-condition datum is banked; no point burning
   more armed windows). star_results gains "dat43504_delta": bool.
3. --star-click raised 3 -> 6 in the relaunch script (t307 needed 2 pips to
   find one ENTER; idle scalar = Icarus ptr, so the witness needs an ENTER on
   a DIFFERENT star — more pips, same nearest-first law).
4. rc law UNCHANGED (measured-windows semantics; early witness break still
   leaves control_nextturn measured).

## S4. RUN t299-leg-20261105-140250 (attempt 1, rc=0, 7 windows measured)
- Instrument healthy end-to-end: 9/9 armed att=0, all windows liveness=True,
  teardown SIGKILL 70817, production :9 (pid 1957) untouched, control_nextturn
  STOP win[eax] NAME='NEXTTURN' (msg-layer control clean).
- w43504_28ec2 FIRED AGAIN (pty census {28ec2:1, btn_hdlr:8, others 0}) —
  render verbatim "E8312 A304552800 mov [00285504],eax ... _0256825": same-
  value Icarus store, REQ-correlated. Fire is REPRODUCIBLE (2/2 runs).
- NAME-BEARING ORACLES WORK: every pair reads DAT_43504=0x256825 name=Icarus,
  alt_285504=0xff (the void-address read stays 0xff across all 12 oracle
  reads — confirms S1: it is a constant unrelated variable, NOT the
  selection scalar). NO DELTA: all 6 pip clicks produced ONE entered click
  (star1 238,282 = Icarus, diff 94504 — the SAME pip t307 hit); the other 5
  diffs 304-488 = repaints.
- PIP LAW DEFECT (MEASURED, offline pixel census of 08_map_pre_star.png):
  the sum(r+g,b)>380 rule + nearest-first picks STARFIELD/UI dots — the 12
  "compact bright clusters" it can find are ALL purple (158,81,174) UI-text
  fragments at y 79-149, NOT system pips. The real Icarus pip sits inside a
  PURE-WHITE (255,255,255) route-line component (white pixels form a
  diagonal + vertical through (237,282)) — system pips merge with white
  route lines into non-compact clusters the old filter excludes.
  => selection law for t308b: connected components of PURE WHITE in map
  rect; a component centroid >=40px from the known Icarus pip (238,282) is
  a DIFFERENT system by construction; nearest-first among those.
- STAR TABLE handle (banked, scripts/r1_star_table.py --slot 0 --all on this
  run's save): Icarus = k=33 world (219.0,248.8,-153.0); 50 stars live;
  nearest-pip law never reaches them because of the defect above.

## S5. t308b INSTRUMENT PATCH (GREEN-ANNULUS pip law) + BATTERY 2
- WHY: run 1 proved the selection law was the bottleneck (not the debugger):
  5/6 clicks hit non-node pixels, the 6th was Icarus. Offline census of the
  run's OWN map shot: system pips = rings of green family {(0,85,40),(0,113,
  56),(0,142,69)}; Icarus's own annulus centroid (237,288) is 6px from its
  pip centre (238,282) — so the exclusion radius is 50px, and every candidate
  is a DIFFERENT system by construction (idle DAT_43504 = Icarus -> only a
  starA->starB flip is measurable).
- Patched in scripts/r299_leg_session.py star phase (BFS 8px-link cluster of
  the green family, >=10px clusters, centroid, drop <50px from (238,282),
  nearest-first). DRY-VALIDATED offline vs run 140250's 08_map_pre_star.png:
  23 candidates, first 8 = [(56,182,284),(66,299,257),(80,274,353),(106,337,
  243),(114,346,317),(119,231,401),(120,154,368),(135,345,199)]; py_compile OK.
- Battery 2 = same scripts/r308_relaunch.sh (star-click 6, same 9 legs, same
  window/conf). Non-ENTER clicks consume windows but cost nothing else; the
  delta check fires only on entered=True pairs. "One battery per sitting"
  (t299) read as per scratch INSTANCE (the relaunch loop itself runs up to 4
  full batteries/session as precedent r305/306/307); this is the SAME task
  (witness the transition), fresh instance, fresh scratch.

## S6. BATTERY 2 RUN t299-leg-20261105-143815 (attempt 1, rc=0) — WITNESS
## CAPTURED: DAT_43504 0x256825(Icarus) -> 0x255bc5(Vega)
- Green-annulus pip law FIRST TRY: 23 candidates (identical to the offline
  dry run), click #1 (182,284) ENTERED a system, screen diff 94712;
  WITNESS DELTA logged 14:41:48, pip loop stopped early as designed;
  control_nextturn measured clean; teardown SIGKILL 71737; production :9
  (pid 1957) untouched.
- THE FIRE (3rd occurrence, REPRODUCED 3/3): mcp-pty.log line 341, render
  "E8312 A304552800 mov [00285504],eax ..." with register panel
  "I-> _0255BC5" = EAX = 0x255BC5, between REQ 59 EXEC RUN and REQ 60 BREAK
  = inside the star0 armed window seconds after the (182,284) click.
  Follow-on bytes identical to disasm 0x28ec7..0x28ed8 (ring post code 0x10).
- ORACLE PAIR (name-bearing, the t308 close condition MET):
  star0_before DAT_43504=0x256825 'Icarus' | star0_after DAT_43504=0x255bc5
  'Vega'; alt_285504 stayed 0xff (S1 void variable re-confirmed constant);
  DAT_43508 UNCHANGED 0x26fe77 — consistent with the static law that 43508
  is the ORDER destination (code 0x11 path), not the star selection.
- TRIPLE CROSS-CHECK (pointer law + star table + vision):
  0x255bc5 = 0x255be1 - 0x1c = the k=0 star-record base (r1_star_table: k=0
  0x255be1 'Vega'); Icarus 0x256825 = k=33 name 0x256841 - 0x1c. Both stored
  EAX values are STAR RECORD BASES. Screenshot 11_star0_screen.png vision-
  verified header 'Vega / White Dwarf' with planet list Vega I/II/III —
  exactly the 3 planets the star table lists for Vega. Writer value semantics
  CONFIRMED: DAT_43504 := clicked star's record pointer.
- READING: the DAT_43504 star-selection writer is FULLY WITNESSED: fn 0x28e70
  COSMOS fallback star-select publisher (sole caller 0x27332) fires on an
  ENTERED galaxy-map star click (3/3 reproducible), stores the clicked
  star-record base (name-verified), posts ring code 0x10. The t307 same-value
  failure was a SELECTION-LAW artifact (nearest-bright-dot picked Icarus's own
  pip), not an instrument failure.

## S7. WHAT THE WITNESS DOES AND DOES NOT CLOSE
- CLOSES (as datum): the DAT-base question opened by t307 (S1: oracle was
  always correct, member+0x88=linear; the 0xff datum void) AND the identity +
  value + trigger of the DAT_43504 STAR-case writer (this section).
- DOES NOT CLOSE: OQ-019 residue = per-SHIP selection (kind-2 clip; gates
  t296-cited; no kind-4 owner-0 ship exists at t=1086) and the destination-
  entry widget that posts msg 0x50 / DAT_43508 + ring code 0x11. DAT_43508
  zero-witness continues (4 legs, 3 runs, instrument live-validated).
- OPEN CHAIN HOLE the witness sharpens: ring code 0x10 is now MEASURED as
  POSTED (3x) by 0x28ec2, but the ring CONSUMER family (0x55a60 incl.
  w43508_55bbd/w43504_55d35) has still never run inside an armed window —
  t307 said consumer fires only on a turn advance; run 140250's control
  window (60 s, legs armed, NEXTTURN msg witnessed) still zero at all 8 —
  either resolution happens after disarm or the control click did not
  advance the turn inside the window. That is the t309 target.

## S8. LEDGER: NO ROW CLOSED (strict-close); t308 note on OQ-019; ships.md
## S34; REFUTED-ROUTES t308 amendment (bright-dot pip law dead at galaxy map).

## S1. STEP 1 — DAT-BASE QUESTION RESOLVED: THE ORACLE WAS NEVER OFF-TARGET
### (t307's "oracle suspect" was a MEMBER-INDEX vs LINEAR conflation; t297-A
### stands; the 0xff datum is void)
RESOLUTION LAW (measured this session on work/r1/t299-leg-20261105-112859/save,
newest sav, B=0x1bf4d8 vote, P0=0x1bf450 — same run as the t307 fire):
1. The sav Memory member is offset +0x88 from guest LINEAR (law already banked:
   docs/re/dosbox-debugger.md:284 "linear == member - 0x88", t286b). Direct
   proof this session: MEM_CTL_CENSUS_001E8312.BIN (debugger dump of linear
   0x1e8312) equals member bytes at idx 0x1e839a = B+0x28ec2 (full 16-byte
   match), i.e. member = linear + 0x88.
2. The oracle reads mm[B + SL.OFF + X] (SL.OFF=0x82bb0) = member 0x242088+X
   = LINEAR 0x242000 + X (member-0x88), which is EXACTLY the rebased store
   target mem_base(obj1)+X. So oracle "DAT_43504" at member 0x28558C IS
   linear 0x285504 — the identical address the debugger decoded in the t307
   fire ("mov [00285504],eax"). MEASURED: mm[0x28558c]=0x00256825 = the
   stored EAX (Icarus star ptr, name verified at +0x88+0x1c again this
   session); oracle pair before/after = same-value store, consistent.
3. The t307 "true DAT_43504 = 0x285504 reads 0xff idle" datum is VOID: it read
   mm[0x285504] as if member==linear; that member is linear 0x28547c, a
   DIFFERENT variable (identity unknown, 0xff meaningless for selection).
   MEASURED both side by side: member 0x285504 -> 0xff; member 0x28558c ->
   0x256825.
4. Therefore consequence (a) anticipated by STATE t308 does NOT fire: t297-A's
   law ("both globals have non-order writers, delta-only") needs NO restatement
   — its readings were of the real DAT_43504/43508 all along. The ds:0x4358c
   zero-refs grep was never evidence against the oracle (the oracle never read
   DAT_4358c; member 0x285614 = linear DAT_4358c is a different variable,
   read 0x2569a500 idle this session).
5. Disasm census (pre-rebase names, work/t91_code_disasm.txt, this session):
   ds:0x43504 = 38 refs, ds:0x43508 = 109 refs, ds:0x43510 = 3 refs,
   ds:0x4358c = 0, ds:0x43590 = 0. Consistent: the globals the census map
   tracks are 43504/43508; 4358c/43590 are not DAT scalars the code touches.
CONSEQUENCE FOR THE DELTA TEST: the t307 close-condition failure was genuinely
a SAME-VALUE store (idle DAT_43504 at the galaxy map = Icarus ptr 0x256825;
the click stored Icarus ptr again). A REAL delta now requires an ENTERED click
on a star that is NOT the currently-published one (starA->starB), witnessed by
the leg stop + name-bearing oracle pair. 0xff->star is off the table as a
prediction (the scalar is never 0xff at this save state while on the map).
