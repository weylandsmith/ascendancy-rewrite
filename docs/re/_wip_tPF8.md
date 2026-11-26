# _wip_tPF8 — tPF-8 RESEARCH-TREE VISIBILITY (D28 item 21), 2026-11-26

Task (STATE.md NEXT ACTION): item 21 = "Lines should only lead away from known
technologies — in the beginning of the game, when no technologies are known,
there should only be three circles displayed, with no lines or other circles."
Derive WHICH lines/nodes the vendor renders visible at rest (vs only on
hover/select), and whether the port's off-frame frontier at rest
(TRSV1c-D) is vendor law or port fit error. Steps: (1) edge-draw gate at
bytes; (2) census our render vs t252; (3) ship + pins + mutation + witness.

SITTING CHECK ran FIRST: scripts/r1_t85g_sitting.py exit 0, 45,227 trusted
rows, output byte-identical to tPF7b_pre_sitting.out (newest t=1335) — no new
user sitting, stale assignment STOOD.

## P1 EDGE-BLOCK RAW DISASM (0x48270..0x483f7, t442_disasm on
## work/ascend_restored.bin -> work/tPF8_edge.asm)
Per-row prereq loop (esi = row*0x4b + j walking rec+0x40 prereq bytes,
edi = j counter 0..5):
  0x48277 mov cl,[esi+0x74784]   ; j-th prereq byte p of THIS row
  0x4827d cmp ecx,0xff / je 0x48383   ; 0xFF -> BREAK whole loop (no line,
                                       ; straight to chip/node block)
  0x48290 mov eax,0x74744 / mov dx,cx / call 0x46d3c  ; legality(p)
  0x4829f je 0x482ec              ; ILLEGAL prereq -> skip line, next j
  colour: 0x6b - clamp(chop(0.25*(0.5*(depth_this+depth_p)+posz)),+-3);
          p == selected word[win+0x9db] -> 0xf3   (0x48316..0x48321)
  endpoints: (this.x, this.y - 27) -> (p.x, p.y + 27)
     (0x48327 [ebp+ecx*2+0x6b9] sar16 add 0x1b ; 0x4834a..0x48353 this.y
      sar16 sub 0x1b — CONFIRMS the tRS-V1b correction verbatim)
  call 0x5bf71 (line primitive), loop 0x4837a cmp edi,5 jl 0x48275.
So THE EDGE GATE = legality(PREREQ END) via 0x46d3c, evaluated per prereq j.

## P2 DRAW-LOOP CONTROL FLOW (0x48160->0x48524 head, body 0x4856f..0x483f7
## back-edge; raw work/tPF8_gate.asm + t442 0x48150..0x48295) [verified]
Loop head 0x48524: row = word[win+0x913+2k] (projection-list order);
  0x48566 call 0x46d3c(THIS row); 0x4856d je 0x48504 -> NEXT ROW. The gate
  PRECEDES the entire body: shape word q (0x481aa..0x48244), PREREQ-EDGE
  loop (0x48275..0x48383), study chip (0x4838a q!=0), NODE blit
  (0x483fa..0x48501). => an ILLEGAL row paints NOTHING at all -- no disk,
  no chip, NO EDGES FROM IT.
Legality 0x46d3c verbatim (work/tPF8_legal.asm) [verified]:
  race bit = 1<<byte[0x7458e] (ebx=-1 at BOTH call sites -> caller race);
  OWNED (dword[rec+0x47]>>24 & bit) -> LEGAL (0x46d88 jmp 0x46dd5);
  else loop j 0..4: prereq byte rec+0x40+j; 0xFF terminates (vacuous
  all-owned -> LEGAL -- ROOTS ARE ALWAYS LEGAL, OWNED OR NOT);
  any prereq whose rec+0x47 bit is CLEAR -> ILLEGAL (ebp=0).
=> DRAWN SET = OWNED union FRONTIER (all-prereqs-owned), roots included.
=> EDGE EXISTENCE LAW: edge(row->prereq p) painted iff row legal AND p legal.
   At game start (roots unowned): every depth-1 row ILLEGAL -> skipped at
   0x4856d before its edge loop; roots have no prereqs -> NOTHING but the
   three root disks. D28 ITEM 21 IS THE DIRECT THEOREM OF THIS LAW.
SCREEN-AT-REST ARITHMETIC (cited constants: focal 1194.256, pos (0,0,-150),
Y=30k+15*(i&1), R<=23 => Z_cam in [127,173]) [inferred from verified laws]:
  k=0 (Y 0/15): screen y 240..254 -- the THREE ROOTS ARE ON-FRAME AT REST;
  k=1 (Y 30/45): 447..480 -- bottom-edge, and at game start ILLEGAL anyway;
  k>=2: >=654 off-frame. Witness tRSB1 row-3 y=684 matches k=2/3.
PORT STATE (rewrite/src/ui/researchview.cpp:235 s.legal = state != Blocked;
ui.cpp:3172 edge loop gates centres[i].visible + centres[pr].visible): the
edge law MATCHES. The port's SEED-5 rest log says first Available row = 3
(row 3), i.e. rows 0/2/6 are NOT Available -> the port OWNS the roots at
game start. VENDOR per D28 item 21 shows three frontier circles at start ->
the vendor does NOT own the roots. CANDIDATE ROOT CAUSE: the port's
starting-research mask, not the draw code. MEASURE OWED: vendor mask at the
earliest banked save (dword per row at ds:0x74744+row*0x4b+0x47, pointer
law) vs the port's initial tech set.

## P3 STARTING-MASK MEASUREMENT (scripts/tPF8_startmask_census.py + follow-up
## execute_code probes; outputs work/r1/tPF8_startmask.out) [verified]
92 banked saves read (base via r1_sav_scan anchors; mask ds:0x74744+0x4b*i
row names self-confirm: bytes at 0x74746 = 'Orbital Structures').
  - FAMILY A = 72 boot/headless r1sav-* captures (oct5/oct6/oct7): mask
    byte 0x00 for ALL 66 rows x ALL races; progress words ds:0x764a0 all 0;
    studied words ds:0x76492 = 0xffff (the no-study sentinel).
  - FAMILY B = 20 production-ring matrix saves (turn >= ~1250 self-play):
    47 rows nonzero, roots mask 0x0f (races 0-3 own the roots LATER).
=> VENDOR START LAW: ZERO techs owned for any race at game start. The D28
   item-21 report ("in the beginning ... only three circles, no lines") is
   EXACTLY the theorem of P1+P2 with this mask: roots 0/2/6 legal (no
   prereqs -> vacuous all-owned), every depth-1 row illegal -> skipped at
   0x4856d before its edge loop => three disks, zero lines.
=> PORT DEFECT: campaign.cpp:367-369 grants ownedTech rows {0,1,2}=true to
   EVERY owner at campaign build (pre-t45 default, never cited). Consequence
   chain: port frontier at start = depth-1 rows (children of 0/1/2), first
   Available logged row 3 at y=684 OFF-FRAME; the roots render as owned
   frames; item 21 reproduces verbatim.
=> TRSV1c-D RESOLVED (pending witness): the rest camera is FINE — root rows
   sit at column k=0 (Y=30*0+15*(i&1) in {0,15}) -> screen y = chop(1194.256
   *Y/150 + 0.5) + 240 = 240..252, INSIDE the RESWIN clip (7,46)-(476,472).
   The off-frame-at-rest frontier was a STATE error (wrong owned set), not a
   camera fit error. [inferred from cited laws; witness leg below]
   ARITHMETIC CORRECTION (recomputed, not transcribed): roots are column
   k=0 with Y=30*0+15*(i&1) in {0,15}; Y=0 -> y=240 at every depth, Y=15 ->
   y 344..381 over Z_cam in [127,173]. ALL THREE INSIDE the clip. Column
   k=1 (Y 30/45) -> y 447..663: bottom-edge/off-frame even if legal.
FIX (tPF-8 ship): delete the three-line grant in campaign.cpp; pins:
  (a) fresh campaign -> owned mask EMPTY for every owner;
  (b) frontier == EXACTLY {0,2,6} (roots, restree.txt prereq-empty rows);
  (c) zero paintable edges at start (edge law needs both endpoints legal);
  (d) root screen centres inside the clip rect at the rest camera (closes
      TRSV1c-D with measurement once the witness re-logs center 0/2/6
      WITHOUT dollying).

## P4 SHIP + PINS + MUTATION + WITNESS (this iteration)
SHIP: campaign.cpp constructor — the uncited rows-0/1/2 grant DELETED
  (replaced by the cited law comment); stale "banked open" note removed.
  No other engine delta; the draw/edge code already matched the law.
FIXTURE MIGRATIONS (all cited-in-place, law tests untouched):
  test_researchview_t408 partition pin: owned>0/avail>0 -> owned==0,
    avail==3 =={0,2,6}, blocked==63; set-study pin gets its Owned row via
    the cited free-grant channel (0x46f4f) and skips it for availRow.
  test_optionsfilter_tpf6: premise forced via setAllTechs(kPlayer,true)
    (the filter law is tech-state-independent; without it the base list is
    REQUIRES-empty and the test vacuous).
  test_campaign research_progresses 40->400 turns; ai picker 60->600;
  test_ships drive-hops 40->400; test_species FastLaneTravel 80->400 —
    the drive gate (resReq row 7) now needs 2->7 RESEARCHED first.
PINS tests/test_starttech_tpf8.cpp x5 (CMakeLists entry ADDED — tPF-4
  trap): (1) zero owned every owner; (2) frontier == EXACTLY roots {0,2,6}
  (MAIN rows only — variant prereqs pollute all(), OQ-013, first-draft fix);
  (3) zero paintable edges at start + ANTI-VACUITY (grant row 2 -> >=1
  edge); (4) roots on-frame inside the RESWIN clip at the rest camera
  (TRSV1c-D closed by measurement); (5) retired grant GONE + both edge
  gates present verbatim in ui.cpp. Suite 578 -> 583, 0 failed.
MUTATION 4/4 CAUGHT (scripts/tPF8_mutate.sh, snapshot preflight + copy-back
  + md5-verify): M1 grant re-introduced at definition 15 fails; M2
  s.legal=true polarity 3; M3 prereq-endpoint gate dropped in ui edge loop
  1 (the wiring pin's text check alone would NOT catch a semantic drop —
  the edges pin is load-bearing); M4 Y-centre 240->640 8. Restored
  md5 fac85a0c/2ac4d33c/9db07a9a, green after.
WITNESS VERDICT PASS (scripts/tPF8_witness.sh, seed 5, scratch Xvfb :99
  killed by PID): leg1 FIRST-available centre = row 0 (a ROOT) at (64,240)
  with ZERO dolly (center-log total 1 line); leg2 census
  (scripts/tPF8_rest_census.py) EXACTLY 3 ring-sized comps n=828 each,
  centres (63,239)/(406,239)/(234,343) — matching the k=0 arithmetic
  (Y0->240, Y15->~344..381) — zero strays >=12 px. Census crop law banked:
  exclude the y=46 header line and y>=456 panel row (chrome the tree law
  says nothing about; first run FAILed on them, not on the tree).
tRSB1_witness.sh RE-RUN post-fix VERDICT PASS: click re-derived row=0
  (99,240) -> "ui research study Orbital Structures", panel-green 0->754,
  local leg 848 px. ("window died before release" = t439 red herring.)
PLAYTHROUGH REGENERATED (record_playthrough.sh RC=0): all runs FINITE —
  A seed 2024 Extinct t1067, B seed 23 CONTROL t1582 (score 68%), C seed
  13 Extinct t536; smoke seeds 1 Extinct t557, 42 Extinct t10 (the zero-
  mask start makes early AI pressure lethal on some seeds — honest note,
  finiteness is the gate bar, not seed-specific outcomes).
