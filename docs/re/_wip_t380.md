# t380 WIP — QUANTIZER REST-ON-GRID INTO SHIPSIM PINS

## S0 SITTING CHECK (RING-FIRST) — NEGATIVE, assignment stands
- scripts/t368_ring_turn.py: parsed=20/20 max_turn=1254 min_turn=1254.
- live-timeline.jsonl 9,349,893,839 B (03:42), 400 KB tail-SEEK: 12 rows,
  ALL turn 1254, last file 52.sav wall 03:42:07 = ring rotation only.
  r1_t85g_sitting.py NOT run (no new turn boundary since t379).

## S1 STATIC RE-READS THIS SESSION (work/r331_disasm.txt, verbatim)

### S1a FUN_00049aa8 IS A QUANTIZING STORE (0x49aa8..0x49ac8)
  mov ebx,[edx]; mov [eax+0x9e],ebx; add eax,0x9e;
  mov ebx,[edx+4]; mov [eax+4],ebx; mov ebx,[edx+8]; mov [eax+8],ebx;
  call 0x533e0; pop ebx; ret
  => EVERY position store through this helper passes the triple through the
  quantizer. Callers found: 0x2202a (placement tail of FUN_00021f58, right
  before BYTE[+0x58]:=4 at 0x2202f), 0x399df (landing/scatter region builds
  a stack triple then stores via the helper), 0x49968.

### S1b FUN_000533e0 quantizer (0x533e0..) — g = ds:0x895dc = 32
  sign-directed bound (g or -g by fcomp [eax] vs 0), half-offset g/2=16,
  fadd [ecx], round via call 0x76e08, fistp, idiv ebx, imul, fstp [ecx].
  (full multi-axis extent: see S1b2 below)

### S1c WALK BODY FUN_00049f54 — quantize UNCONDITIONAL, COPY-BACK GATED
  entry: mov ecx,eax; mov edi,edx (arg2 home = edi, NO writes between entry
  and the gate — grep of [0x4a040,0x4a21b] + [0x4a21b,0x4a2d4] shows zero
  edi writes).
  0x4a23d lea esi,[ecx+0x9e]; raw pos+delta computed and stored to SCRATCH
  [ecx+0x78..0x80] (0x4a2ac..0x4a2ca);
  0x4a2cd mov eax,edx(=scratch ptr); 0x4a2cf CALL 0x533e0  <-- UNCONDITIONAL
  0x4a2d4 cmp edi,0x1; jne 0x4a342 (exit leg: mov eax,ebx; ret — NO pos
    store, NO power/moves bookkeeping)
  mode==1 leg 0x4a2d9..0x4a2ed: copies the THREE quantized scratch floats
    back to [ecx+0x9e..+0xa6]; then fild [ecx+0x94], power/moves math.
  => arg2==1 commits quantized pos; arg2!=1 is a DRY-RUN (scratch only).

### S1d CALLER CENSUS OF FUN_00049f28 (the walk wrapper; 0x49f2c tests
### BYTE[+0x62]: ==0 -> call walk with caller's edx; !=0 -> other legs)
  - 0x15cc5, 0x15df0: `xor edx,edx` BEFORE the call => arg2=0 DRY-RUN
    (scratch quantize only, NO store to +0x9e, no power/moves math, no
    completion flags 0x49ee9/0x49f1b).
  - 0x25560: `mov edx,0x1` => THE EXECUTOR COMMIT (the t364-banked
    "commit law mode==1 only 0x25560/0x25570" site).
  => LAW (static, instruction-level): EVERY COMMITTED WALK POSITION IS
     32-ALIGNED — the quantizer call 0x4a2cf is UNCONDITIONAL and the
     copy-back leg 0x4a2d9 is gated ONLY by mode==1, NOT by arrival.
     The t361-era "arrival-only snap" [INFERRED] reading is SUPERSEDED:
     arrival affects bookkeeping (0x4a2f0 fild [+0x94], power), never the
     snap. edi=arg2 verified NOT clobbered between entry (0x49f63
     mov edi,edx) and the gate (0x4a2d4; grep of edi stores over
     [0x4a040,0x4a2d4] = ZERO; 0x533e0 preserves edi).
  - QUANTIZER TIE SEMANTICS NOW BANKED (0x533e0 full read):
     q = trunc(round_even(v + 16*sign)) /_32 * -32-or-32 by sign => ties
     (v = 16 mod 32) go AWAY FROM ZERO. std::round(a/g)*g (the sim's
     snapGrid) is ALSO half-away-from-zero => sim matches vendor at ties.
     (t361 pin (d) comment "tie semantics not banked" is now resolvable;
     the pin itself stays valid — it avoids ties.)
  - RUNTIME CORROBORATION (banks, zero new capture): playtest s10 kind
     5->4 lane-END arrival arrival pos (-1280,-1952,384) = 40/61/12 x 32
     EXACT (S64 M5 row); magnetron landing M1 (1280,-1760,1344) all
     32-multiples; t362 census "st4 off-grid {}" on the drive corpus.
     ALL off-grid runtime rows are kind-5 LANE-LOCAL x (14, 28, 144.7 ->
     149.3 = march steps 14/28/14-over-3, NOT stored via 0x49aa8) or
     kind-2 cross-system frames — never a kind-4 commit.

## S2 SIM SITES vs THE LAW (rewrite/src/game/shipsim.cpp)
- snapGrid used at 0x814 (magnetron placement — CORRECT per S1a/S1c) and at
  walkLaw arrival (0x887).
- laneMarch lane-END placement (shipsim.cpp:930-932): star+jitter, NO snap —
  vendor equivalent goes through the quantizing store (0x2202a). CANDIDATE
  CORRECTION pending mode/caller check.
- landingAttempt scatter (shipsim.cpp:959-961): += j%1000-500, NO snap — the
  banked law cites FUN_00049aa8 for this store (quantizing). CANDIDATE.
- walkLaw mid-walk (non-arrival) no snap — t361-era [INFERRED]; t362 pin
  'pos 277.333' encodes it. Resolution needs the CALLER census of 0x49f54
  (what arg2 does the executor pass) — IN PROGRESS.

## S3 RUNTIME CENSUS (scripts/r380_grid_census.py, zero capture) — LAW CONFIRMED
Banks (5 dirs x 20 saves = 100): live rest rows 4020, off-grid 1140 (28.36%);
kinds census {1:200, 3:600, 4:1980, 5:1240}; OFF-BY-KIND {5: 1140} — kinds
1/3/4 ZERO off-grid rows. Production ring (20 saves): 800 rows, off 260,
off-by-kind {5:260} again zero exceptions.
EVERY off-grid row carries the S22-L4 LANE-LOCAL frame signature (y EXACTLY
0 or 1, z exact multiple of 32): "off-grid rows that are NOT the lane-local
frame: 0" on both sides. The mid-transit rows t370 read as quantizer evidence
((14,1,-224)x5, (28,0,-2144), 144.7->149.3) are kind-5 lane-local march
progress — the march never writes galactic +0x9e (laneX is a different field).
Timeline tail (200 MB, deduped): kind4 off-grid 0/19; kind5 off-grid 13/13
(8 with the pure lane-local signature; the other 5 have y=0 z=32/1824 shapes).
ADJUDICATION: rest-on-grid holds at EVERY committed GALACTIC store (kinds
1/3/4 + kind-5 lane-END arrival); kind-5 mid-lane rows are a different frame,
not law-breaks. t370's "mid-transit off-grid" signal is REFRAMED (it was kind
5 all along — consistent, not contradictory).

## S4 CODE + PINS + MUTATION (landed this iteration)
CODE (shipsim.{h,cpp}): walkLaw snap UNCONDITIONAL after the walk math
(bookkeeping order: moves := round(remaining RAW) unchanged — the snap feeds
no accumulator); laneMarch lane-END placement + landingAttempt scatter each
snap via snapGrid; shipsim.h walkLaw doc rewritten (INFERRED text removed).
PINS test_shipsim_t380.cpp x6: mid-transit snap (288 not 277.333, fmod
families); negative-coord tie AWAY-FROM-ZERO (-48->-64, -80->-96, -81->-96,
-47->-32); lane-END arrival on-grid (1152/288/992 = S64-M5 shape shape-law);
lane march stays lane-local (pos frozen, laneX off-grid OK — the frame
boundary pin); scatter on-grid invariant + |d|<=516 bound; corpus census
(20 saves, off-grid => kind5 && y in {0,1} && z on grid, floors 400/150).
TWO EXISTING GOLDENS CORRECTED IN PLACE (encoded the superseded reading):
t361 lane placement (1164,300,1006)->(1152,288,992); t362 clamp-operand
(277.333->288; mutant separation preserved — walk-operand mutant lands 320).
MUTATION 7/7 CAUGHT (r363r_mutate.py, checkpoint 7962fb8 FIRST per skill
rule 1): M1 walk-snap-removed (10 fail) / M2 grid-16 (16) / M3 snap floor =
toward-zero at negatives (7) / M4 lane-end-snap-removed (6) / M5
scatter-snap-removed (1, isolated by the t380 scatter pin) / M6
snap-identity (21) / M7 SNAP-ARRIVAL-GATED = the superseded t361 reading
restored (4 fails — the partial-walk pins ARE the isolator; the old suite
could not see this law, which is why the correction was invisible).
Clean revert verified: suite 253/0 post-campaign; git rewrite/ clean.
Campaign spot-check post-correction: --seed 2024 --campaign 1600 EXIT 0.

## S5 LEDGER DISPOSITION
No OQ row closes (strict-close): the correction refines an OQ-019-adjacent
model law; OQ-019 closure stays USER-GATED (t329 packet). NOTE appended to
the OQ-019 row: quantizer store law landed + the S64 "mid-transit off-grid"
signal reframed as kind-5 lane-local.
