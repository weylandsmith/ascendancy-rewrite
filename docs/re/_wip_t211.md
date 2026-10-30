# t211 WIP — commit-chain tail: the 0x49f28 dispatch legs + cat-5 splash loop-bound identity

Trigger triage (session start 2026-10-30): timeline mtime 1793294532 /
size 5,721,578,066 / tail-64KiB md5 9054cc6c66802e6f80431d4ffa1416ee ==
frozen baselines EXACTLY, dosbox down, tree clean at 0620fc9 -> NO sitting;
STATE t211 stands. Windows via scripts/r205d_windows.py + ~/tools/revenv/bin/
python (project .venv lacks capstone). Image work/ascend_restored.bin.

## S1 — 0x49f28 dispatch law MEASURED (verbatim, 0x49f28..0x49f52)

    0x49f28 push ebx; push ecx
    0x49f2a mov ebx, eax                 ; EAX = ship/order object
    0x49f2c mov cl, byte [ebx + 0x62]
    0x49f2f xor eax, eax                 ; DEFAULT RESULT = 0
    0x49f31 test cl, cl
    0x49f33 jne 0x49f3e
    0x49f35 mov eax, ebx
    0x49f37 call 0x49f54                 ; [ship+0x62] == 0 LEG
    0x49f3c jmp 0x49f4a
    0x49f3e cmp cl, 1
    0x49f41 jne 0x49f4a                  ; cl >= 2: NO CALL AT ALL
    0x49f43 mov eax, ebx
    0x49f45 call 0x4a360                 ; [ship+0x62] == 1 LEG (t88/t210 path)
    0x49f4a mov [ebx + 0x84], eax        ; result stored on the object
    0x49f50 pop ecx; pop ebx; ret

THREE arms, not two: cl==0 -> 0x49f54 (functions_full.tsv span 0x49f54 +
1020 = ..0x4a350); cl==1 -> 0x4a360; cl>=2 -> NO call, [ship+0x84]=0
(EAX zeroed @0x49f2f before every branch). The STATE assignment's "else-
branch 0x49f54 (taken when [ship+0x62] != 1)" is imprecise: 0x49f54 is the
==0 leg; values >=2 silently no-op.

## S2 — 0x49f54 head (assert gate)

    0x49f5f mov ecx, eax                 ; ecx = ship
    0x49f61 mov edi, edx                 ; edi = 2nd arg (EDX at call time)
    0x49f63 cmp byte [eax + 0x58], 4
    0x49f67 je 0x49f80
    0x49f69 cmp byte [ecx + 0x58], 4     ; SAME object again (ecx==eax)
    0x49f6d je 0x49f80
    0x49f6f mov ebx, 0x309; mov edx, 0x25f3; call 0x2a428  ; VENDOR ASSERT

(0x4a360 guard shape is t210's; NOTE the t210-cited t83 "travel body
FUN_00049f54 walks min(d/160, MOVES)" — this is the SAME function: the
[ship+0x62]==0 leg is the TRAVEL/movement resolver, kind byte [+0x58]==4.)

## S3 — SECOND-DOOR ANSWER: NO (measured negative)

Tools scripts/r211_probe_a.py + r211_probe_b.py RC=0 (E8 byte-pass over obj0
0x14bb0..0x82bb0; callee BFS depth 3 over functions_full.tsv spans):
- E8 callers of 0x49f54 == EXACTLY {0x49f37} (the dispatcher itself) — no
  second direct entry into the travel leg.
- E8 callers of 0x4a360 == EXACTLY {0x49f45} — the attack-bearing leg is
  reachable ONLY through 0x49f28's cl==1 arm.
- Callee closure of 0x49f54 (24 functions, depth 3): ZERO hits into the
  attack family {0x4b740, 0x43a4c, 0x4cd90, 0x4b8e4, 0x4a360}; zero indirect
  jmp/call inside 0x49f54 (so E8-only closure is sound for this body).
  Direct calls in the body, all travel-side: 0x2a428 (assert reporter),
  0x76da0, 0x76e08 (x87 helpers), 0x52fa0, 0x533e0 (grid quantizer, t183),
  0x49880, 0x4a34f-adjacent 0x49a34.
=> The t210 commit law stands: the ONLY committed-order paths to 0x4b740 are
the six E8 callers t210 censused; the cl==0 else-branch is the movement
resolver and cannot charge. cl>=2 = silent no-op with result 0.

## S4 — THE cl>=2 POPULATION AND THE [ship+0x62] WRITER CENSUS

probe_c store-form census (disp==0x62, cmp/test skipped, resume-on-gap; 40
store sites of 71 total refs over 140,156 decoded insns). Byte-form writers
with a SHIP base (dword/esp-base sites are different structs at the same
displacement — attribution by base usage, NOT by value):

  ==1 writers: 0x415b4 (inside order-resolver family 0x41260..), 0x423e2,
  0x4245f, 0x43392, 0x4340f, 0x43843, 0x43900 (order-set sites in the
  0x42b7d..0x4342f command family t206 mapped), 0x4a350, 0x4a591.
  ==0 writers: 0x41b69, 0x41c2f, 0x41dc9, 0x42b1f, 0x42da9, 0x42fba.
  AL-valued writers (value from a computed source, NOT enumerated {0,1}):
  0x15c6d, 0x15d98 (mov [edx+0x62],al), 0x42211, 0x43188 (mov [..],al).

The 0x4a350 site is the FIRST INSN of successor function 0x4a350 (span 83 ->
..0x4a3a2; 0x49f54's body RETs at 0x4a34f — my S2 span reading was right, so
0x4a350 is a separate, tight function): `mov byte [eax+0x62],1; mov byte
[eax+0x67],0; mov [eax+0x63],edx; xor edx,edx; mov [eax+0x68],ebx` — an
order-phase latch that flips the phase byte to 1 and zeroes the day-stamp.
What 0x4a350's CALLERS are (and hence whether arrival is the trigger) is NOT
measured this session — the latch semantics above are structural shape only,
NOT a causal handoff claim. The 0x15c6d/0x15d98/0x42211/0x43188 al-forms are
where values >=2 could originate; their value-source tracing is banked as the
residue (bounded follow-up if ever decision-bearing).

## S5 — SPLASH LOOP-BOUND ARRAYS NAMED: FUN_00022304 CO-LOCATION CENSUS AT THE ENGAGING SHIP'S STAR

probe_c writer census inside 0x4cd90 (span 2307 -> ..0x4d693): [esp+0x730]
ONE writer 0x4d09e, [esp+0x734] ONE writer 0x4d2a4, [esp+0x73c] ONE writer
0x4cd9d (mode, t210 re-confirmed). Both bounds are the return of the SAME
call shape:

    0x4d07c mov eax,[esi+0x59]        ; ESI = engaging ship
    0x4d07f call 0x22304              ; EDX = scratch out-buffer ([esp+0x504] / [esp+0x1ac])
    0x4d086 jle skip                  ; count<=0 -> loop skipped
    0x4d092 shl eax,2 (loop 1) / lea edx,[eax*4] (loop 2)
    => bound == 4 * N where N = 0x22304's return.

FUN_00022304 0x22304..0x223a1 VERBATIM (r205d_windows) — it is the SHIP-TABLE
CO-LOCATION CENSUS, exactly the t204-t207 idiom (base 0x3a095 @0x22313,
stride 0x162 @0x22325, bound `movsx ecx,dx; cmp ecx,0x6b; jge end` @0x2232d
= indices 0..107):

    skip if owner word dword[ship+0x54]>>16 == -1        (0x22343..0x2234c)
    kind byte = [ship+0x58]                              (0x2234e)
    if kind in {1,2,3}: location KEY = 0x13bc5 + 96*([[[ship+0x59]+0xa]>>16])
       (0x22361..0x22376)   ; two derefs -> STAR RECORD of t205 identity
    elif kind == 4:     location KEY = [ship+0x59] directly
       (0x2237a..0x22383)   ; lane-segment handle
    match key == EAX(arg1) -> append ship ptr to out-buffer, ++count
    (0x22388..0x22395; arg2 EDX==0 -> count-only, no writes)

CALLERS PASS arg1 = [engaging_ship+0x59] — i.e. for a kind-4 (transit)
engager the key matches other transit ships' handles (same lane segment);
for kind 1/2/3 ships their key is a STAR RECORD address, which can only
match a transit handle... NOT equal — so the practical match set is: ships
whose location folds to the same STAR RECORD as arg1 when arg1 is itself a
star-record address, plus kind-4 ships sharing a handle. (My first S5 draft
said "lane segment group" — WRONG for the star case; corrected same session:
the function is location-agnostic co-location, keyed by star record OR lane
handle depending on the VISITED ship's kind, with the arg compared raw.)

NAMED UPPER BOUND: splash multiplier <= N-1 where N = co-located ship count
at the engaging ship's location (0x22304 census), further filtered per-victim
in loop 2 by owner != engaging owner (0x4d2be) AND diplo byte
[0x12fd6 + 0x1ee*owner] == 2 (0x4d2ca); self-skip witness 0x4d0ac/0x4d0ae
(loop 1 `cmp esi,edx; je 0x4d196`). The corpus-free static question ("what
count do the bounds mirror") is ANSWERED: the star-garrison/co-location
count, not the lane table and not the entity list.

## S6 — BLOCK 0x4a350 IS UNBOUND CORPUS-WIDE (honest negative) + THE 0x4a591 PRE-ARM

probe_d + probe_e (decoded branch edges over the FULL obj0, resume-on-gap,
140,156 insns): edges into 0x4a350 == ZERO; CONTROLS: edges into 0x49f54 ==
EXACTLY {0x49f37} and into 0x4a360 == EXACTLY {0x49f45} (the E8 scanner also
reproduces t210's six callers of 0x4b740 EXACTLY: {0x1a146,0x39d9f,0x3a0b3,
0x4bb56,0x4d191,0x4d2dd} — scanner validated before trusting the zero).
Image dwords == 0x4a350: ZERO. probe_f (RAM pointer-law scan, t191's
handler-binding class; 3 saves playcap-20261013, B=0x1bf4d8, P0=0x1bf450):
aligned dwords == P0+0x4a350: ZERO (controls P0+0x49f28, P0+0x49f54 also
zero — consistent with E8-direct-only reachability).
=> Neither static nor RAM binds 0x4a350; the phase-flip block is UNBOUND
(NOT claimed DEAD — strict-close: absence of a binding is measured, absence
of ALL possible dynamic reachers is not). The cl==1 population is therefore
entirely the S4 constant writers.

0x4a591 context MEASURED (0x4a570..0x4a5fc — the cat-0 volley preamble, the
block immediately above t210's volley loop 0x4a5c1): an order-kind switch on
DX sets the day/stamp byte [eax+0x67]: DX==0 -> 2 (0x4a570), DX in {1,2} ->
1 (0x4a579 via jbe), DX==3 -> 0 (0x4a582), else vendor assert 0x4a5b0
(strings 0x3e5/0x2623); EVERY arm also writes [eax+0x68]=EBX and falls to
0x4a5c1; the 0x4a58b/0x4a591 path sets ECX=lea[eax+0xab] (gizmo ring head,
t184 inventory law) and [eax+0x62]=1 — i.e. the volley preamble ARMS
phase=1 on the ship, then the slot loop 0x4a5c9..0x4a5f1 scans ring slots
(cidx 0xFF skip @0x4a5d9, gizmo cat byte [eax+0x7653e]==0 gate @0x4a5e8),
stores the slot ptr [esi+0x63]=ecx and calls 0x49f28 with edx=0 (the t210
dry-run). So the t210 commit law's dry-run loop is exactly this preamble +
scan; the phase byte it reads was set HERE (or by the ==1 order-setters),
never by the travel leg.

S4 AMENDMENT: the 0x42211/0x43188 al-form sites sit at addresses whose
immediately preceding byte is UNDECODABLE (0x42210 0x00, 0x43187 0x00) — by
the t108 boundary law (mid-insn coverage = reject) treat both as
alignment-suspect, not established writers. The only sound al-valued ship
base+0x62 writers are the 0x15c6d/0x15d98 family (AL from local [esp+0x50],
preceded by a value-range switch cmp al,4 / cmp al,2 @0x15c55..0x15c5d —
inside a UI/setup function at 0x15bd0-family, NOT the order path; value
source tracing banked as residue, low priority).

## VERDICTS (the two t211 questions, answered)
1. SECOND DOOR: NO. 0x49f28's cl==0 leg (travel resolver 0x49f54) has
   exactly one entry edge (the dispatcher), zero attack-family callees to
   depth 3, zero indirect edges; cl>=2 no-ops with result 0. The attack
   price 0x43a4c remains reachable from committed orders ONLY via the six
   t210-censused callers. The commit law stands unchanged.
2. SPLASH BOUND NAMED: both [esp+0x730]/[esp+0x734] == 4 * FUN_00022304(
   [engaging_ship+0x59]) — the CO-LOCATED SHIP COUNT at the engaging ship's
   location (ship table 0x3a095+0x162*i, i<108, owner!=-1; location key =
   star record 0x13bc5+96*idx for kinds 1/2/3, raw lane handle for kind 4).
   Self-skip 0x4d0ac; loop-2 per-victim gates owner!= @0x4d2be and
   diplo byte [0x12fd6+0x1ee*owner]==2 @0x4d2ca.
REWRITE: NO semantic change (OQ-019 boundary rule; no cited per-commit loop
to convert). Docs: OQ-016 STATUS t211 appended; ai-dossier row 13 residue
shrinks (splash bound no longer "runtime entity-loop bounds play-gated" for
the STATIC identity — only for live N values).

