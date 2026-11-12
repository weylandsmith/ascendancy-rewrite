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
