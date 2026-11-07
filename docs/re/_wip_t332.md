# t332 WIP — BatControlWnd CHAIN LIVE WITNESS (capture; OQ-016 residue-1 last uncited edge)

## S0. Start (fresh session 2026-11-08)
- Sitting check NEGATIVE: 40 MB tail-seek of work/r1/playcap/live-timeline.jsonl -> max turn 1086
  (== corpus). r1_t85g_sitting.py NOT run. Watcher-only growth (watch.log/watch.out mtime fresh).
- DECISIONS.md: grep -i ANSWER -> no matches. No user verdict to consume; execute the assigned task.
- Production :9 untouched: timeout 136357 + dosbox-x 136359 (ps at start). Never killed by this session
  until the scratch teardown (which kills ONLY scratch-recorded PIDs).
- Assignment source: STATE.md NEXT ACTION t332. Outcomes (A) mode1_1b7dd fires -> residue-1 CLOSED
  CLASS candidate (still needs nuke-effect witness); (B) entry fires, gate/post zero -> name the leg
  that eats it; (C) entry zero whole-log with a valid battery -> the fifth leg is finally INSTRUMENTED.
- DEAD, not re-trod: t331 static routes, t326b indexing family, jump-table raw-file reads (law C5),
  t324 class-table routes, REFUTED-ROUTES t322/t323 amendments, everything in the t331 AMENDMENT.

## S1. PRE-FLIGHT STATIC READ (fresh objdump 0x16060..0x16200, work/ascend_restored.bin) — TWO CORRECTIONS

### S1a. THE UNCITED DELIVERY EDGE HAS A CANDIDATE: fn 0x156d4's OWN TAIL SELF-RELAYS msg 0x1c01
t331's open question was "who delivers msg 0x1c01 to registry slot 61 (BatControlWnd)" — its imm census
found no external poster. The fresh decode shows the poster is INTERNAL to the handler and is a
CLASS-TABLE call, not a registry post, which is exactly why an immediate-census cannot see it:

    16147: bb 51 00 00 00    mov ebx,0x51            ; t331 post #1 leg
    ...
    1615d: e8 42 0b 04 00    call 0x56ca4            ; POST 0x51 -> slot 63 (BatModeWnd)
    16162: 8b 9d a7 00 00 00 mov ebx,DWORD [ebp+0xa7] ; <- SHARED TAIL (reached from 0x16071 shield
    16168: ba 01 1c 00 00    mov edx,0x1c01           ;            jmp, 0x16145 jmp, AND fallthrough
    1616d: 89 e8             mov eax,ebp              ;            of the 0x51 post call
    1616f: ff 53 0c          call DWORD [ebx+0xc]     ; class-table SLOT 3 of [ebp+0xa7] = BatControlWnd's
                                                       ; OWN table -> msg 0x1c01 re-enters the SAME window
=> the 0x1c01 loop is SELF-FEEDING: every 0x1c01 pass ends by posting 0x1c01 to itself through its own
   class table (slot 3), which is how the b9 state machine advances (pass 1 sets b9, pass 2 takes
   table[1] -> gate 0x15fed). Site 0x1616f is r299's existing leg `s2_1616f` (armed in t310/t311/t312,
   ZERO whole-log in all three — but those batteries only clicked galaxy-map pips and system views,
   never the My^Items/Other^Items item rects, per t331 correction C4).
=> LEGSET CHANGE: `relay1616f` (0x1616F) is added as an 8th leg. It is the single most informative site
   for the assignment's stated goal (name the 0x1c01 delivery edge): relay1616f>0 with fn156d4_entry>0
   cites the self-relay as the carrier; entry>0 with relay==0 means every pass bailed before the tail.
   Last-4 token 55BF — audited free vs all 8 armed legs and the full r299 LEGS table.

### S1b. CLICK COORDINATES ARE GAME/TEXT SPACE; THE (80,100) ORIGIN IS A GRAB-TIME OFFSET
STATE.md t332 says: click My^Items "SCREEN (593,218) (window rect 479,103-548,133 + window-origin
(80,100) t325 law)". That number is the rect centre in ROOT/SCREEN space: 479+80=559 .. 548+80=628,
103+100=203 .. 133+100=233 is exactly t331's own "My^Items screen (559..628, 203..233)", and
(513+80, 118+100) = (593, 218). So the assignment named the RIGHT POINT IN THE WRONG SPACE:
`send(["click", x, y])` delivers GAME coordinates (640x480), which are the same numbers windows.txt
uses — proven by the two targets the drive has used for dozens of iterations:
    NEXTTURN  (511,67)  = centre of windows.txt rect 474,52-548,82   (64 clean turns, t261 drive)
    FLEET     (553,184) = centre of windows.txt rect 474,169-632,199 (t253/t299/t330)
`grab()` reads root and crops at (XOFF,YOFF)=(80,100) (r293_move_session.py:73, :121), which is why
screen-space numbers appear in capture notes at all. THE BATTERY THEREFORE CLICKS THE RECT CENTRES
IN TEXT SPACE, and keeps the assignment's literal as a control probe:
    My^Items    rect 479,103-548,133 -> click (513,118)   [root form: (593,218)]
    Other^Items rect 557,103-626,133 -> click (591,118)
    BatListWnd  rect 474,142-632,394 -> click (553,200) (item-row band)
    literal     (593,218) as a game click = inside BatListWnd, kept as the control probe
RUN EVIDENCE THAT THE DISTINCTION IS REAL (S7a): the (513,118) click reached a window (NEXTTURNCONT)
and the (593,218) click reached a DIFFERENT window (PLBUILD) — two different hit-tests, so the two
number spaces are not interchangeable at click time.
windows.txt values re-read this session from extracted/ascend00/windows.txt (NAME/rect/SENDMESSAGE):
My^Items TYPE 32 SENDMESSAGE 804(=0x324) MOUSEFOCUS 1; Other^Items TYPE 0 SENDMESSAGE 805(=0x325);
BatModeWnd TYPE 4 STATE 1 16 CURSORSHAPE 2; BatControlWnd TYPE 19 STATE 1 16 rect 0,0-0,0;
BatListWnd TYPE 10 PARENT BatControlWnd STATE 1 16.
(513,118)/(591,118) are also exactly the two points the t322 amendment names as never clicked.

### S1c. Gate/post map re-verified verbatim (no drift from t331)
0x16076 mov BYTE[ebp+0xb0],1 / 0x1607d mov [ebp+0xb1],esi / 0x16083 mov ax,[eax+0x33] (gizmo flags) /
0x16089 and al,0x40 / 0x1608e je 0x16147 (bit40 CLEAR -> post 0x51 leg). 0x16181 block (bit40 SET):
0x1618b call 0x32f34 / 0x161a8 call 0x32fa4 / 0x161c3 mov [ebp+0xb1],eax / 0x161d1 call 0x56ca4.
Entry tree re-verified: 0x156ec cmp dx,0x327 ... 0x1571f cmp dx,0x1c01 / 0x1572a jbe 0x15ebf;
0x15ebf mov eax,[ebp+0xbb]; 0x15ec5 cmp BYTE[eax+0xb7],4 -> je 0x1589b reject; 0x15ed2 mov al,[ebp+0xb9];
0x15ed8 dec al; 0x15ee4 cmp al,3; 0x15ee6 ja 0x15b39 reject; 0x15ef1 jmp DWORD cs:[eax*4+0xb04].

## S2. INSTRUMENT PRE-FLIGHT (measured, venv python)
payload == restored byte-for-byte at all 8 leg addresses (work/ascend_payload.bin vs
work/ascend_restored.bin, both 0x8cc83), P0 = 0x1bf450:
  fn156d4_entry 0x156D4 lin 0x1d4b24 tok 4B24  56 57 55 81 ec 8c 00 00 00 89 c5 89
  tbl15ef1      0x15EF1 lin 0x1d5341 tok 5341  2e ff 24 85 04 0b 00 00 83 fe 04 0f
  gate15fed     0x15FED lin 0x1d543d tok 543D  31 db 66 8b 9c 24 84 00 00 00 8b 85
  post1615d     0x1615D lin 0x1d55ad tok 55AD  e8 42 0b 04 00 8b 9d a7 00 00 00 ba
  relay1616f    0x1616F lin 0x1d55bf tok 55BF  ff 53 0c b8 ff ff ff ff 81 c4 8c 00
  post161d1     0x161D1 lin 0x1d5621 tok 5621  e8 ce 0a 04 00 b8 ff ff ff ff 81 c4
  mode1_1b7dd   0x1B7DD lin 0x1dac2d tok AC2D  c6 85 b7 00 00 00 01 31 c0 83 c4 14
  backch_1b180  0x1B180 lin 0x1da5d0 tok A5D0  e8 1f bb 03 00 89 e8 31 d2 e8 4e 26
Last-4 collision audit: no collisions among the 8 armed legs AND no new-token collision against the full
r299 LEGS table (61 entries) — t305 audit law satisfied.
Tooling: scripts/r332_batctrl_session.py (subclasses r1_dbg_session.DbgSession the way r330 does;
venv interpreter law; scratch game-wp only; private Xvfb; core=normal; kill-by-recorded-PID SIGKILL).

## S3. BATTERY (as run)
phases: baseline(15s leg-armed hold) -> myitems_map(513,118) -> otheritems_map(591,118) ->
fleet_rowjump (LEG-FREE: enter_system_via_fleet = FLEET 553,184 then row-1 200,93) ->
myitems_sys(513,118) -> batlist_sys(553,200) -> literal_probe(593,218, the assignment's number) ->
escape_to_map -> hold(60s leg-armed, no click: measures spontaneous fn 0x156d4 traffic from the pump).
Ring oracle per phase (from the newest .sav, located BY NAME + magic, never by hard-coded offset):
BatControlWnd and BatModeWnd record field grids rec+0xa0..0xcf (covers b0/b1/b7/b7-mode/b9) —
the b9 progression is the state-machine witness; window records located by magic 0x12345678 with the
RAW ASCII name at +0x20 (t331 law), fields read relative to the magic offset.

## S4. RESULT — OUTCOME C (run work/r1/dbg-t332-20261107-124717, attempt 1, rc=0)

PTY whole-log census (authoritative counter, all 8 legs + control armed):
    fn156d4_entry 0   tbl15ef1 0   gate15fed 0   post1615d 0   relay1616f 0
    post161d1 0   mode1_1b7dd 0   backch_1b180 0   |   btn_hdlr 8  (CONTROL ALIVE)
Banked stops 8/8 attributed to btn_hdlr — i.e. every click landed on a REAL window and
named it, and none of those windows was BatControlWnd. phases.json: all 8 click/hold
phases executed, both rowjumps entered (A_rowjump/B_rowjump true), no arm failures,
disarm liveness True on every window, guest never frozen.
Save-axis corroboration (batrec.json, 19 oracle reads across the battery):
BatControlWnd rec 0xfdbe34 and BatModeWnd rec 0xfdc89c hold b7_mode=0 and b9=0 in EVERY
save before and after every click — no state-machine movement anywhere in the run.

VERDICT: the fifth leg is now INSTRUMENTED AND MEASURED, not inferred. fn 0x156d4
(BatControlWnd, registry slot 61) received NO message of ANY id across a battery that
(1) armed its entry leg (sub-battery B, dedicated windows, t330 heavy-check law),
(2) clicked the exact item rects t322 named as never clicked — (513,118)/(591,118) —
    on the strategic map AND in the entered view,
(3) plus BatListWnd-interior clicks (553,200) and the assignment's literal (593,218),
(4) and two leg-armed no-click hold windows (spontaneous pump traffic: zero).
Residue (1) stays OPEN strict-close (no live mode-1 store witnessed). D2-c strengthens.

## S7. WHY IT IS ZERO — MEASURED WINDOW OWNERSHIP + THE STATE-16 CENSUS (both fresh)

### S7a. The hit-test names the owning window at every click (banked stops, all 8)
| phase (click)              | window that handled it | msg | ret0 file |
| A/B_myitems_map (513,118)  | NEXTTURNCONT           | 4/8 | 0x3177d   |
| A/B_otheritems_map (591,118)| NEXTTURNCONT          | 4   | 0x3177d   |
| A/B_myitems_sys (513,118)  | PLIND                  | 8   | 0x3cb8d   |
| A_batlist_sys (553,200)    | PLBUILD                | 4   | 0x3cb8d   |
| A_literal (593,218)        | PLBUILD                | 4   | 0x3cb8d   |
(B_myitems_sys#0 eax=0xfd5e1c name-read empty, ret0=0x56cdd = the NEXTTURN dispatch site.)
The t253 FLEET rowjump enters the PLANET/orbital view — windows PLIND/PLBUILD/PLANETALLOC
— NOT a battle screen. So the pixels windows.txt gives to My^Items (479,103-548,133) and
Other^Items (557,103-626,133) are painted and hit-tested by state-1 (NEXTTURNCONT) and
state-17 (PLIND/PLBUILD) windows in every state this session could reach.

### S7b. STATE 16 is EXCLUSIVELY the battle-map family — 19 windows, no overlap with any
state reached in any capture (fresh parse of extracted/ascend00/windows.txt):
STATE 1 16 windows (19): BatControlWnd, BatListWnd, BatModeWnd, TOGGRID, BATROTLEFT,
BATROTRIGHT, BATZOOMIN, BATZOOMOUT, RECENTER, TOGELEV, ABANDON, My^Items, Other^Items,
Repeat, Pass, Auto, W, S, Z, I. Control states measured this run: NEXTTURN/NEXTTURNCONT
STATE 1 1; PLIND/PLBUILD/PLANETALLOC STATE 1 17; FLEETWND STATE 1 18; COSMOSWnd STATE 4 1 3 7 13.
=> The activation obstacle is not a widget and not a pixel: it is the GAME-LEVEL ACTIVE
   SCREEN STATE, which must take the value 16 for this window family to be composed at all.
   t323 closed the per-window route ([win+0xb1] writers are constructors + the char cycler +
   the bounds-asserting setter fn 0x31f30). What has NEVER been decoded is the GLOBAL
   active-state writer — who sets the screen-mode id the STATE-line composition law
   (fn 0x31d58 / the composition loop 0x5898e..0x58b3e) consumes. That is the one named
   edge left for residue (1), and it is a ZERO-CAPTURE question (t333).

## S8. Instrument laws banked this iteration
1. CLICKS ARE windows.txt-SPACE; GRABS ARE root-space (XOFF,YOFF=80,100). Do not add the
   origin to a click target. (r293_move_session.py:73/:121 vs NEXTTURN (511,67) / FLEET
   (553,184), both measured working.) The t332 assignment's (593,218) is a grab-space number.
2. `census control MATCH` compares raw RAM against work/ascend_payload.bin, so it is
   FALSE for any leg whose instruction carries a RELOCATED immediate (tbl15ef1's disp32).
   Judge arming by BPLIST + observed fires, never by that probe alone. (Same run: control
   MATCH=False at arm 1 with 8/8 BPs set, MATCH=True later at the entry leg.)
3. Operand capture must use BYTE-granular reads at each field offset (+0xb0/+0xb7/+0xb9 are
   bytes interleaved with DWORD pointers at +0xb5/+0xbb); a 4-strided grid silently mis-reads.
4. At a class-table ebp (e.g. btn_hdlr stops where ebp=0x247ca0 = the type-25 toggle table),
   the field-grid read is class-table data, not a window record — expect garbage there.

## S9. Safety ledger
Run dir work/r1/dbg-t332-20261107-124717; scratch game-wp only; own ring dir; private Xvfb :97.
Teardown SIGKILL dosbox pid=174711 + xvfb pid=174707 (recorded PIDs only). Production :9
(Xvfb 1461, timeout 136357, dosbox-x 136359) NEVER signalled — ps-verified after teardown.


## S5. MEASURED DURING THE RUN (banked mid-flight)

### S5a. JUMP-TABLE ADDRESS SPACE CORRECTION (small, law-level)
The live instruction at 0x15ef1 dumped from RAM reads `ff 24 85 04 4b 1d 00` -> disp32 = 0x1d4b04,
which is a LINEAR (runtime) address, NOT a .sav member offset. Reading the member at 0x1d4b04 yields
code-looking garbage (0x90c35ad0...); reading it at +0x88 = member 0x1d4b8c yields the table:
    [0]=0x1d5349 [1]=0x1d543d [2]=0x1d55d1 [3]=0x1d5349 [4]=0x1d569d [5]=0x1d5635
  -> file offsets 0x15ef9, **0x15fed (GATE)**, 0x16181, 0x15ef9, 0x1624d, 0x161e5
EXACT match to t331's entries[0..3] (its "member 0x1d4b04" was the linear value mislabelled; member =
linear + 0x88 per the pointer law). The b9 dispatch `mov al,[ebp+0xb9]; dec al; cmp al,3; ja reject`
makes only indices 0..3 reachable, so entry[1]=0x15fed is the gate leg and indices 4/5 are dead —
t331's chain structure CONFIRMED LIVE IN RAM (first time the table itself has been witnessed as data).
CAUTION BANKED: the r299 `census control MATCH` probe compares a RAW-RAM dump against
work/ascend_payload.bin, so it reads False for any leg whose instruction contains a RELOCATED
immediate (here bytes 4-7 differ). It is NOT an arming failure — BPLIST listed all 8 BPs and the
guest fired. Do not read control MATCH=False as a broken run.

### S5b. FIRST CLICK MEASUREMENT — the item-rect pixels on the STRATEGIC MAP belong to NEXTTURNCONT
Stop A_myitems_map#0 (click (513,118), the My^Items rect centre, on the bare strategic map):
  leg=btn_hdlr eip_file=0x336b4, msg_id_lo=4, eax=esi=0xfd6240 with MAGIC + NAME **NEXTTURNCONT**,
  ret0_file_off=0x3177d (the same dispatch site t308 measured for star clicks), ebp=0x247ca0 = the
  type-25 toggle CLASS TABLE (so the operand-capture field grid read at that ebp is class-table data,
  not a window record — noted, harmless noise in operand.json for class-table ebp stops).
=> The instrument is alive AND the click landed on a real window; that window is NOT BatControlWnd's
   My^Items child. Direct corroboration of the t322 composition-shielding claim AT THE PIXEL LEVEL:
   on the strategic map, windows.txt rect 479,103-548,133 is owned by the NEXTTURN container family,
   so BatControlWnd's type-32 child cannot receive msg 0x324 there. The state-16 (battle/orbital)
   phases A_myitems_sys / B_myitems_sys are therefore the decisive ones.

## S6. Run bookkeeping
- Run dir work/r1/dbg-t332-20261107-124717; launch pid recorded in session.log; teardown = SIGKILL of
  that recorded PID + its Xvfb only. Production :9 (136357/136359) never signalled.
- Scratch game-wp only; own ring dir; base B=0x1bf4d8 == EXPECT_BASE (armed addresses valid).
- pre_battery save-axis oracle (41-shape law, located by NAME+magic): BatControlWnd rec 0xfdbe34
  slot41=61 b7_mode=0 b9=0; BatModeWnd rec 0xfdc89c slot41=63 b7_mode=0 b9=0; BatListWnd 0xfdbf40
  slot41=62 — reproduces t331's 20-save measurement exactly on the scratch session's own first save.

