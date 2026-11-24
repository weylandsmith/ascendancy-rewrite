# _wip_tRSB1 — RESEARCH SET-PROJECT (D26 "I can't set any projects")

Working log for tRS-B1, 2026-11-24. Control: STATE.md NEXT ACTION.
Sitting check ran FIRST: t368_ring_turn 20/20 turn=1086 == baseline -> no new
sitting, stale assignment stood.

## P0 — what is already in hand (do NOT re-derive)
- aicode.md S3b (t91): WRITE CENSUS of DAT_00076492[race] (the per-race
  research-target word == restree base+0x1d4e). Human picker writer =
  **0x47e34** ("research-window UI tail: stores selected row word
  [esi+0x9db] -> DAT_00076492[player] + legality gate FUN_00046d3c +
  FUN_0004fb30"). AI picker = FUN_00040018. Clears: 0x22db7 init, 0x43f5b
  completion, 0x47880/0x47985 UI clears.
- research.md S6: restree runtime base 0x74744 stride 0x4b; count
  WORD[0x74744]; row+0x47 owned-mask dword; +0x40 prereq bytes 0xFF-term;
  +0x3e runtime cost.
- Port: ui/researchview.{h,cpp} setStudy() (Available->queuedTech, else
  silent false) + ui.cpp kScreenResearch click branch (~L798) + render
  (~L2437). help.txt reswin click law cited ln1668-1690.
- tNGS cycle 2: FUN_0004709c IS THE TECH-TREE LAYOUT GENERATOR (asm dumps
  work/tNGS_gen1/2.asm): iterates RESTREE census, places nodes
  y=240+30*step+15*(step&1) radius, rotates 360/(slot-1)+0.1*i. Layout port
  = tRS-V1 (NEXT after this one); but the SET-PROJECT HIT law needs the
  vendor's node positions => derive the click->selected-row leg here and
  name the layout dependency.

## P1 — vendor set-project handler legs (disasm work/tRS_click_tail.asm)
0x47dc6..0x47e43 (inside the research-window UI function; payload offsets):
  mov cl,[0x7458e]                 ; race/specnum byte
  mov ebx,[eax*4+0x74744+0x47]     ; row+0x47 OWNED mask dword (eax=row)
  sar ebx,0x18; shl eax,cl; test   ; race bit set -> jne 0x47718 (REJECT:
                                   ; already owned)
  mov ebx,0xffffffff               ; terminator
  mov eax,0x74744; call 0x46d3c    ; LEGALITY = prereq chain walk (all prereqs
                                   ; owned); test eax -> je 0x47718 (REJECT)
  mov eax,0x78638; xor edx,edx; call 0x4fb30   ; (side effect TBD)
  mov al,[0x7458e]; lea edx,[eax*2]
  mov dword [0x764c0],0xffffffff   ; clear ADJACENT slots (0x764bc,+4)
  mov ax,word [esi+0x9db]          ; SELECTED ROW word (window record +0x9db)
  mov dword [0x764bc],0xffffffff
  mov word [edx+0x76492],ax        ; *** THE SET: DAT_00076492[race]=row
  ret
=> gate order = OWNED first, then PREREQ-LEGALITY — matches port setStudy()
   order (researchview.cpp:50-53).

## P2 — the FULL handler chain (work/tRS_reswin_fn.asm = 0x41e34..0x47eb0)
TWO-STAGE LAW, verbatim:
 (a) SELECT leg (sub 0x47478, called with edx=0 from 0x47da5): hit-tests the
     click against the PROJECTED node table. Bounds at 0x474fb..0x4752d:
     per-node words [winptr+0x5f1+2k] (x) and [+0x6b9+2k] (y), sar 16, and
     the click must satisfy |cx-nodeX| within +-0x19 AND |cy-nodeY| within
     +-0x19 — HIT HALF-SIZE 25 px (NOT the port's 30); a node also must pass
     call 0x46d3c (legality) BEFORE its row may be stored; store at 0x47548
     `mov word [edx+0x9db],ax` ONLY if != current (0x4753a je), and a CHANGE
     clears 0x764bc/0x764c0 to 0xffffffff (0x4754f/0x47555).
 (b) COMMIT leg 0x47d99..0x47e43 (msg arm dx>3, window dword [+0x35]!=0):
     reads word [esi+0x9db]; 0xffff -> no-op; then the P1 gate chain; then
     DAT_0x76492[specnum]=row; call 0x4fb30 with eax=0x78638 (side effect
     UNRECOVERED — named seam: candidate = sound/message, do not assert);
     clears 0x764bc/0x764c0 again.
 (c) CLEAR arms: 0x476f2 writes [esi+0x9db]=0xffff (screen-close path,
     paired 0x764b8/0xbc clears 0x476e6/0xeb); aicode t91 census already
     banked 0x47880/0x47985.
 FUN_00046d3c VERBATIM (work dump 0x46d3c..0x46dde): row already owned by
     race -> FALSE (jmp 0x46dd5 with ebp=-1); else walk <=5 prereq bytes
     row+0x40..0x44 (0xFF terminates), EVERY prereq must have the race bit
     in [prereq+0x47]>>24, ANY miss -> FALSE. => legality = ALL-prereqs-owned
     AND not-owned-itself — exactly the port setStudy() conjunction.
 0x764bc/0x764c0: NOT research state (target word is 0x76492 stride 2);
  these are per-window scratch (dossier/progress display pair) — the port
  has no analog state, no port delta owed. [inferred from stride math:
  0x76492+2*8 races = 0x764a2... the pair sits past the 8-race target array;
  no campaign-visible consumer found in the cited legs.]

## P3 — PORT STATE + PROBE (measured, this session)
- The port ALREADY implements the commit law: researchview.cpp setStudy()
  (owned->false, prereq-ALL->else queue) wired at ui.cpp:826 on the Node
  hit; arm landed t408 (604a352, 2026-11-16) — BEFORE the D26 ruling
  (2026-11-23), so the user's complaint stands against a build that had it.
- PROBE scripts/tRSB1_probe.sh (scratch Xvfb :99, seed 5, RESUME flow):
  10 clicks inside the field -> log shows TWO "ui research study" lines
  (Superconductivity, Spacetime Surfing) + two readout lines. VERDICT: the
  click->queuedTech LOOP WORKS in the current port. The complaint cannot be
  reproduced as "the handler is missing".
- Screenshot /tmp/trs_probe/research.png (vision): the tree paints all 66
  nodes as near-identical rings + a blue prereq-edge web; NO picture-in-
  disk affordance for Owned, the dim Blocked rings are indistinguishable
  from Available at a glance, and the right panel is BLANK at rest (t268
  law). => the most plausible root cause of "I can't set any projects" is
  the DRAWING (help reswin: "empty disks = technologies you CAN choose to
  study" — the vendor communicates clickability by the disk's CONTENT; the
  port's uniform rings communicate nothing) + the derived grid layout the
  user called "the tree not being drawn correctly". Attribution [inferred]
  from the witness pair (loop works; affordance absent) — NOT a closure.
- Vendor deltas found for tRS-V1 (fuel, do not half-port now): hit half-size
  25 not 30; the vendor hit-tests a PROJECTED node table (100 slots stride
  0xc at win+0x143, init 0x470c1..0x470ed, count-checked against
  word[0x74744] at 0x4715d) produced by the LAYOUT GENERATOR FUN_0004709c
  (dumps work/tNGS_gen1/2.asm); selection-change (not re-click) is the
  vendor's state transition; side effect 0x4fb30(0x78638) unrecovered.

## P4 — WITNESS (formal walkthrough)
scripts/tRSB1_witness.sh — RESUME -> RESEARCH rail -> click a KNOWN
Available node -> asserts (1) log "ui research study <name>", (2) pixel
census: right panel x484..632 gains green text px after the click and had
NONE before (panel-blank-at-rest is the t268 law, so the gain IS the
feedback signal), (3) a gold-rim ring exists at the clicked node after the
click. [RESULT: see below after run]

RESULT 2026-11-24: VERDICT PASS (post-hit-law-patch rerun). Log "ui research
study Superconductivity"; census panel-green 0->854, gold-rim near(136,154)
0->320. Vision read of after.png: "Current Project: / Superconductivity /
(0 days) / Allows / Mass Barrage Gun / Surface Shield" — the t252 panel
shape reproduced live. NOTE: the first witness run clicked (60,120) which is
NOT a node centre under the derived layout (probe luck ≠ law); the witness
pins centre (136,154), the deterministic derived-layout pixel that the probe
showed resolves to an Available node (log names the row: Superconductivity).

## P5 — PORT DELTA + PINS + MUTATION (shipped this session)
- researchview.cpp researchHit(): disc-of-scaled-radius REPLACED by the
  vendor +-24 inclusive square (kResHitHalf=24, researchview.h cites
  0x474fb..0x4752d). kResNodeRadius stays PAINT size only (t268 bbox law).
- PIN rewrite/tests/test_researchhit_trsb1.cpp: constant==24; corners
  (+-24,+-24) HIT row 30 (disc missed them — the discriminator); axis +-25
  never answers row 30 (disc accepted them). Neighbour-disjointness premise
  CHECKed explicitly (no centre within 49 px of row 30 on both axes).
- MUTATION: M-R1 kResHitHalf 24->25 CAUGHT (5 fails, pin names
  test_researchhit_trsb1.cpp:48); M-R2 disc law restored CAUGHT (12 fails,
  :71 corner leg). Both reverted, header md5 verified restored, suite
  516/0/0 (was 515). Witness re-run PASS post-patch.
- LAW BANKED: docs/re/research.md S7 (full two-stage handler law + the
  0x46d3c legality verbatim + seams TRSB1-A/B/C + the D26 attribution,
  labelled [inferred]).

## P6 — LEDGER + SITTING
- No OQ row touched (tRS tracks none, same posture as the tPL family —
  honest negative under strict-close; open=[016,019] unchanged).
- Production ring NOT touched this iteration (scratch Xvfb :99 only, killed
  BY PID; t368_ring_turn 20/20 turn=1086 at session start AND re-verified
  at finish).
