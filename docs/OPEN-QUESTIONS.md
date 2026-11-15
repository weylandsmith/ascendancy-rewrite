# OPEN QUESTIONS — live closeout ledger (v2, strict-close)

Statuses: open | CLOSED. Nothing else. A question closes ONLY with cited
evidence (Ghidra address / extracted-file offset / pointer-law guest-phys
measurement from a named capture) + the rewrite site upgraded + docs/re/
updated + a gate or test pin. FINAL-DEFAULT is not closing (docs/GOAL.txt).
v1 full evidence text for every row: archive/ralph-v1/OPEN-QUESTIONS.md.
v2 FULL LEDGER (every CLOSED row's complete evidence text, archived
2026-11-03 when this file was slimmed to open rows + pointers):
archive/state-v2-full/2026-11-03/OPEN-QUESTIONS.md (md5 e897be73e0fd4b06cb51aa0881c0ff5d).
Full per-iteration working notes for ALL of v2: archive/state-v2-full/2026-11-03/wip/.
Do-not-retry prohibitions: docs/REFUTED-ROUTES.md.

Format: ID | area | question | status | what closes it (in-hand route)

OQ-005 | shp | .shp shape-library codec: in-record DIMS location for the
80-record residual class (container CLOSED 208/208; grammar CLOSED t61-t69)
| CLOSED 2026-11-09 t367 — D1 USER RULING, the row's own named closer | CLOSING (t367): USER RULING 2026-11-09 12:45:01 (from ruling page; duplicate submit 12:45:31, applied once), docs/DECISIONS.md, verbatim: "USER: D1 mouse k5/k6/k7 = keep as-is / D1 batch 41 dispositions = accept all 41 / D1 A6 keep=True, A7 keep=True, A8 keep=True / D1 B-rows misidentified = none" + notes (A series keep as historical curiosity; B3 = star-map research menu button icon; B4 unrecognized; B5-B16 new-game menu, B17-B29 planet-screen manufacturing indicators). The ask's closure bar was the ruling or a drawn-frame capture (R13 bars self-grading) — the ruling landed. t367 MEASURED (shp.md S28): k5/k6/k7 signed-bbox dims 78x47 walk 47/47 rows, planes byte-identical md5 b2d049bbf5b571bfc4ea3b97db7a4fa7 (census 543287, nonzero 3666); rewrite corner-anchor gate fallback (shp.cpp decode(), TEST shp_corner_anchor_fallback_t367) admits EXACTLY these 3 corpus-wide — cos_star k40..k51 / 1starmap k1 / sg50expl k9 stay rejected per the vendor blit -1 gate @0x5cb2b (S25.2). Decision sheet rebuilt via generator (dispositions final: 40 NO-ASK + 1 JUNK-CERTAIN + 3 KEEP-RULED). Residue render-fidelity testimony (B5-B29 top-part chain) banked shp.md S28 — not a ledger row. | CLOSED PORTION (full evidence: archive 2026-11-03 + shp.md):
control-byte grammar verbatim FUN_0005caac 0x5cca3..0x5ce77 (shp.md S9); blit
5-arg law + stream=PAY+(tsz|u64dir[k-1])+0x18 (S12/S14); runtime table uniform
delta{sel0:8,k>=1:24} 4 libs x 43 selectors live-RAM (S17 r1_shp_ramtable.py);
corpus MEASURED 208 libs/1557 recs/1484 decode-pass; dims-gate + span-bound
validator artifacts corrected t182/t197 (shp.md S18/S21 — do NOT re-litigate
those 31 records, they decode); cos_star selector law t200 (SEL=4*[star+0]+
cls ladder; k40..k51 addressable-empty, k52..k54 unreachable); pop-slot library
= 17np.shp (t254). CODE SITE: rewrite/src/formats/shp.{h,cpp} ShapeLibrary
(container laws, blit-faithful clamp, 4096 dims cap) + tests/test_shp.cpp.
RESIDUE (80 records/31 files, decomposed t278 shp.md S24.2): 25 zero-byte
ladder slots + 12 cos_star k40..k51 + 4 invalid-dims (mouse k6/k7, 1starmap k1,
sg50expl k9) + 2 t197 demotions (mouse k5, sg64expl k0) + 3cfgnew k12 (vendor
EOF truncation). W3 route EXECUTED NEGATIVE (all 75 decoder sites read dims
from record header only; docs/REFUTED-ROUTES). Closure class = human-verifiable
drawn frame (R13 blocks self-grading) OR user ruling on the shipped decision
sheet work/r1/shp_png/decision-sheet.md (88 rows, docs/DECISIONS.md D1) OR a
vendor draw-capture session. Blind sweeps FORBIDDEN (R2). Default in force:
decode per S16 V/A law, residual skip-and-warn in tooling only (rewrite renders
its own vector art; codec = validation asset). T328 FEASIBILITY PASS (shp.md
S25, cited): of the 44 C-rows, 39 are CITED-NO-WITNESS (12 cos_star k40..51
zero dims every slot -> blit -1 gate @0x5cb2b draws nothing; 25 ladder slots
zero STREAM bytes span==header + batfx.txt battle attribution; 1starmap k1
zero-stream + no selector), 1 junk-certain (3cfgnew k12 vendor EOF
truncation), 1 UNREACHABLE (sg64expl k0 combat, t323), and ONLY mouse
k5/k6/k7 remain witnessable — real art 46x77x2038B with dims u16@rec+0
(EXACT-H walk; t196 "not walkable" was canonical-slot-only) vs canonical
u32@+0x10 zero-component: a dims-slot-location dispute. T330 DRAW-CAPTURE
EXECUTED (run work/r1/dbg-t330b-20261107-080216, shp.md S26, cited): 4
live deref stops inside mouse.shp (records k0/k2) MEASURE draw-time dims =
u16 pair at rec+0 stored [H-1,W-1], u32@+0x10 REJECTED; blit_refuse 0 fires
whole-log; mouse.shp is on the blit path (bar-panel glyphs) loaded OUTSIDE
the 200-slot cache. C27-C29 'invalid dims' premise REFUTED ((46,77) = 78x47
valid under the +0 law); their drawn-frame witness stays impossible (no
selector names k5/k6/k7; CURSORSHAPE 2 only) -> they remain in the human
ask re-classified 'valid dims, no selector'. ROW STAYS OPEN strict-close:
generalizing the +0 law beyond mouse needs per-library witnesses (corpus
+0x10 uniformity check fails 1526/1567). T344 SELECTOR LAW + LIVE CORNER WITNESS (shp.md S27, cited): the MOUSE.SHP referrer IS an immediate — pool-relative imm 0x1764 at fn 0x309d4 0x309f9 (t328 zero-u32 scan scanned 0x84314, wrong value under the OQ-004 law); geometry query fn 0x64ea9->fn 0x61058: W=u32[rec+0x10]-u32[rec+0x8]+1, H=u32[rec+0x14]-u32[rec+0xc]+1, hotspot fn 0x6108c=int32[rec+8]/u16[rec+0xc]; FILE MEASURED 12/12 records bbox-diff == u16-pair+1 (slots AGREE on size, SIGNS carry the anchor) — k5/k6/k7 'zero-component' was one half of a signed bbox pair; k4..k7 are ONE 78x47 glyph at the four screen-corner anchors. Selector law fn 0x54650 (held->id1, release->id0) + mode chain 0x5473b..0x547a6 (cursor pos (0,0)/(0,639)/(479,0)/(479,639) -> id=mode+4). LIVE run work/r1/dbg-t344d-20261108-161132 leg cur_req=0x30AA7: root click (0,0) -> id 4 rec 0x48b=k4, (799,0) -> id 5 rec 0xc99=k5 (lib 0x2EC03C byte-exact TOC); exact edge required (guest 630 fires nothing). C27-C29 re-classified: valid dims, SELECTOR KNOWN (corner modes, TL/TR live-witnessed), drawn-frame pixels capture-limited (zero blit_deref at k5/k6/k7 offsets; corner glyph not drawn through FUN_0005caac in captured play). ROW STAYS OPEN strict-close: pixel MATCH never landed; generalization beyond mouse still needs per-library witnesses; D1 ask unchanged in substance. T347 DECISION-SHEET REBUILD (2026-11-09, ZERO capture, moves NO row): generator scripts/r1_t278_decision_sheet.py verified to run post-slim and reproduce decision-sheet.md BYTE-IDENTICAL (md5 54f07195806cd8cfe6b30c0d2db37ce9) from banked inputs only (index_t278pristine.txt + ids.tsv; all quotes/citations live in the script — no _wip dependency, none repointed). It now writes index.txt too (pointer header + identical bytes), repairing the t182-dumper-clobbers-index.txt pitfall structurally. Each of the 44 C-rows carries a cited DISPOSITION from the law table (S25/S26/S27 + t323), and the script ASSERTS the split: MEASURED 40 NO-ASK + 1 JUNK-CERTAIN (3cfgnew k12) + 3 ADJUDICABLE (mouse k5/k6/k7) = 44, i.e. 41 rows leave the ask. The assertion earned its keep: the author's hand-count of 38 failed the first run. Stale premises purged from the sheet (mouse 'invalid dims / only paint-capture could resolve'; k5 'W=0 H=46' half-pair; '16-record dims-unknown remainder'). docs/DECISIONS.md D1 rewritten to the t347 shape and the 10status/2savegam/4loadgam triad (A6-A8, user: 'possibly junk data') promoted from 'restatement only' to a live keep/junk call. HONEST NEGATIVE: no new measurement was produced — the ask shrank on paper only, the blocker is USER TIME, and R13 still bars self-grading. The k5/k6/k7 pixel route retired UNEXERCISED by the ruling, not refuted. | closed-by-ruling t367

OQ-016 | loop | campaign per-turn constants: income formula, pop growth
curve/cap, starting items, build order, expansion cadence, home placement
| open | CLOSED SUB-LAWS (full evidence + retraction history: archive
2026-11-03 + docs/re/income-law.md): income channel law 138/139 battery (pin
campaign_channel_law_oq016); POP GROWTH pop==+0x42 UPOP dots, counter-50,
colonise :=2 (verified chase capture r1deep-20261007-224831); BUILD QUEUE + AI
SELECTOR LAW (queue 1/planet, acc+=stored IND 0x39005, complete acc>=COST
0x390a3, selector queue-empty-only caller 0x3ead6, COST/IND>=70 abort; rewrite
buildPhase pendingItem/buildAcc + pin campaign_build_queue_law_oq016); POP-CAP
recalc +0x4a = clamp(0..100, +0x55 + MPOP sum ALL active slots) 72066/72066
(income-law T33 — t31/t32 '+2 residual' was the missing +0x88 harness artefact,
RETRACTED); +0x55 seed law nb//3+5 @0x37f84..0x37f9e + pin
campaign_pop_cap_seed_law_oq016; TERRAIN GENERATION LAW end-to-end (rng%5 size,
rng%11 row, draw chain @0x37eb7..0x37ee0, T36); terrain-mutation via item-36 +
world-gen |8 rock only (t29b 40k-sample census); HOME JOIN MEASURED t270
(DWORD[0x12e1d+race*0x1ee] == star base NAME-0x1C; trust turn>=1 only, turn-0 =
template residue) + home placement RUN-LOCAL (11 distinct sets/11 lineages;
rewrite pickHomeStars was a documented MISMATCH (deterministic max-min BFS) —
SUPERSEDED t295 by the cited HOME-STAR DRAW LAW, see S-T295 below);
pending-build reserves its
slot (t271: byte1:=item id, word2 bit0 CLEAR — pending IS ring-observable).
ATTRIBUTION FIXES t273 (binding for all future mining): owner INDEX byte +0x56
(NOT handle u16+0x54); stale-echo pairs mint phantom deltas; the t251 mine is
VOID on both bugs; damage-vs-non-at-war-owner STILL ZERO corpus-wide.
RESIDUE (each with a route): (1) Phase Bomb nuke law — t326 PREFLIGHT
MEASUREMENT 2026-11-07 (docs/re/income-law.md S-T326 + docs/re/_wip_t326.md
S1-S5, tool scripts/r326_precensus.py exit 0): known-tech mask field LOCATED
(ds:0x7478e+0x4b*i bit(1<<race), count word ds:0x74744; cheat-body law);
race 0 AND 2 ALREADY OWN row13 Molecular^Explosives at t=1086 (research leg
vacuous); cidx-70 carriers ZERO in 30 ship rows; 30 owner-0 ORBITAL Shipyards
exist (build leg UI-satisfiable). t326b WALK LANDED 2026-11-07
(docs/re/ships.md S49 + docs/re/_wip_t326b.md S1-S8): the 0x4d/0x4e
"value-writing family" is TABLE INDEXING (gizmo-index space, fn 0x17b2c, ZERO
posters cited — INDEXING half STANDS). t331 STATIC WALK 2026-11-08
(docs/re/_wip_t331.md S6-S7, fresh whole-code objdump): t326b's CONSUMER leg
REFUTED — fn 0x1aef8 dispatch tail 0x1b7cd cmp dx,0x50 / jb / jbe means dx==0x51
FALLS THROUGH onto 0x1b7dd BYTE[+0xb7]=1 (MODE-1 ARMED, bytes cited); both 0x51
posters (0x1615d, 0x161d1 inside BatControlWnd handler fn 0x156d4, class 0x5850 =
file-0x88400 table, ctor fn 0x15630) target [[ebp+0xbb]+0x41] = registry slot 63 =
BatModeWnd MEASURED (record resident 20/20 saves, state 0, class P0+0x88498);
the entry = msg 0x1c01 delivered to slot 61 -> jump table (RAM-rebased, member
0x1d4b04) entry[1] -> gizmo-flag gate 0x15fed (bit0x80 abort / 0x20 shield fn
0x49e78 / CLEAR -> post 0x51; Phase^Bomb gizmos.txt flag_list {3} => all three
bits CLEAR by FILE DATA). RESIDUE 1 = ALIVE-IN-IMAGE cited; sole uncited edge =
who posts 0x1c01 to slot 61 (image-wide imm census: none; road law fn 0x33320).
t322 armed-zero re-scoped: fn 0x156d4 NEVER armed in any capture. t332 forced
capture JUSTIFIED (legs named at _wip_t331 S7). t332 CAPTURE EXECUTED 2026-11-08
(work/r1/dbg-t332-20261107-124717 rc=0, docs/re/ships.md S51 + _wip_t332.md
S4-S8, tool scripts/r332_batctrl_session.py): ALL EIGHT chain legs {fn156d4_entry
0x156D4, tbl15ef1, gate15fed, post1615d, relay1616f 0x1616F, post161d1,
mode1_1b7dd 0x1B7DD, backch_1b180} ZERO whole-log with control btn_hdlr firing 8x;
save axis holds BatControlWnd[+0xb7]=0/+0xb9=0 and BatModeWnd[+0xb7]=0 in every
save before/after every click. The delivery edge is now NAMED MECHANICALLY (it was
never an immediate): fn 0x156d4's own shared tail 0x16162..0x1616f relays msg 0x1c01
to ITSELF through its class table (`mov ebx,[ebp+0xa7]; mov edx,0x1c01; mov eax,ebp;
call [ebx+0xc]`) — which is why t331's imm census saw nothing. WHY ZERO, MEASURED:
STATE 1 16 is EXCLUSIVELY the 19-window battle-map family (fresh windows.txt census)
while banked stops name the owners of the My^Items/Other^Items pixels as
NEXTTURNCONT (state 1) on the map and PLIND/PLBUILD (state 17) in the rowjump view —
the t253 rowjump enters the PLANET/orbital state, NOT a battle screen. t333 THEN
TOOK THE LAST NAMED EDGE (the "global active-screen-state writer") AND FOUND IT IS
A CATEGORY ERROR, so it is no longer an edge: fn 0x31d58's ONLY store 0x31dd0
`mov WORD PTR [eax+0xa],dx` writes a CONTROL record, byte-decoded against
windows.txt:429 `RACE1CONTROL 1 479 449 495 465 0 20` (id,x,y,x,y,flags,size —
ids 1,2,4,8,16,32,64 = the RACEnCONTROL bitmasks), so [win+0xab] is the CONTROL
table and the loader loop 0x58aff..0x58b3e `shl eax,cl` writes per-race-slot
ENABLEMENT (measured 372/372 saves: ids 1,2,4,8 flags=5, ids 16,32,64 flags=0);
there is NO global active-state datum (`mov WORD/BYTE PTR ds:0x13b98` = ZERO hits
in the whole 139,026-insn image, so the loader's loop bound has no writer); and
BatControlWnd 0xfdbebc / BatModeWnd 0xfdc924 measure +0xab=+0xaf=+0xb1=0 in
372/372 saves, which makes the sole runtime switcher fn 0x31f30 bounds-assert on
them (it cannot be called successfully with count=0). windows.txt STATE-line
grammar MEASURED 123/123 lines: `STATE <count> <id>...`, so BatModeWnd's
`STATE 1 16` = one state of id 16, and the state-16 family is 20 windows (t332
said 19). CONSEQUENCE FOR THE ROUTE: it no longer points at fn 0x31d58 and no
capture is justified; the STATE line is consumed at windows.txt PARSE TIME and its
runtime home is NOT in the window record — the keyword literals (PARENT,
NUMCONTROLS, SHAPEFRAME, HELPINDEX, X0, BACKGRNDCOLOR) occur ZERO times in
work/ascend_restored.bin / ascend_payload.bin / ascend_raw.bin / t73c_obj1slab.bin
and only in game/ascend00.cob (NUMCONTROLS n=1 @0x2aefb, PARENT n=123), so any
further walk needs the archive-side parser, not the RE image. t334 THEN WALKED
THE ATTACH SITE 2026-11-08 (docs/re/ships.md S53 + docs/re/_wip_t334.md S0-S13,
tools scripts/r334_parse_map.py + scripts/r334_state_array.py both exit 0): the
STATE line DOES have a parse-built runtime home — parse loop 0x57ee6..0x57ff5
writes win+0x6d stride 13 (id==0: NAME->handle via 0x315c4 then compactor
0x31690 `dst=win+13*[win+0xa1]+0x6d`, 13-byte movs, counter [win+0xa1]++; id==1:
tag + u16 index via 0x1fe20; else vendor assert winmgr.cpp:0xcd6), CORRECTING
t333's "runtime home is not in the window record" wording — BUT the array's only
in-image WALKER is paint fn 0x31384 (literal +0x6d operands: only 0x57f06 and
0x316de; walker reaches slots via `add ebp,0x6d`+`add ebp,0xd` arithmetic; its
2 callers 0x3117f/0x3135a are inside paint fn 0x30fb8, reachable in-image only
through an outside-image table — 0 LE pointers to 0x30fb8 in the bin), rendering
slots as TEXT/HANDLES (byte0 0 -> format 0x7d3aa, 1 -> resolve fn 0x1fc34, >1 ->
assert) — never a screen selector; and 196 needle-verified
saves show the slots zero/garbage (agreement only on count==0 cases; [win+0xa1]
nonzero exactly for the id==0 family). ds:0x13b98 = WORD 4 MEASURED 196/196
(cites t333's [inferred] enablement bound; 4 = player count). The attach sites
0x57d56/0x57e48 are fallthrough-only sequential parse code guarded by scanner
status [esp+0x3a6] (no writer in-body); no allocator at the attach site.
DISPOSITION: residue (1) keeps its "no runtime screen-selection mechanism in this
image" verdict, now cited by mechanism-completeness rather than absence; no
capture justified (the parse machinery is fully walked; the surviving unknown —
what consumed the array in the vendor's full build — is outside this image).
t335 RE-DERIVED THE BRANCH VERBATIM AND FALSIFIED THE STATE-ARRAY READING
2026-11-08 (docs/re/ships.md S54 + docs/re/_wip_t335.md S0-S4, tools
scripts/r335_state_records.py + scripts/r335b_item_array.py both exit 0, 196/196
needle-verified saves, truth side = on-disk windows.txt): the win+0x6d stride-13
array is the WINDOW-ITEM array — [win+0xa1] == TEXTITEM+SHAPEITEM line count
22398/22398 EXACT (vs the STATE count: eq 3844/neq 18554); record byte0 == item
kind (0 TEXTITEM/1 SHAPEITEM) 4900/4900; tag0 u32@+1 resolves through interner
ds:0x6fda8 to the file item's literal name verbatim 3528/3528; windows ever
having records == exactly the 15 item-line windows. The id-branch tests the
item-kind %d output (ds:0x3107="%s %d", file kinds {0,1}), so the else-assert
0x5804c is unreachable for shipped data and the `STATE 1 16` paradox DISSOLVES —
the STATE line has NO consumer in fn 0x575e4; "t334: the STATE line DOES have a
parse-built runtime home at win+0x6d" is RETRACTED (mis-attribution of the item
builder; fn 0x31690's 0x9f-gate is the counter<4 item cap, not a type check).
t333's "windows.txt resident in saves" also fails to reproduce: NUMCONTROLS in 0
of 284 save dirs. RESIDUE-(1) DISPOSITION after t335: the STATE ids have no
in-image consumer at all (control table ruled out t333, item array t335, no
global datum t333); "no runtime screen-selection mechanism in this image" stands,
now with the STATE-line consumer question closed BY MEASUREMENT rather than
inference. t336 RE-OPENED-THEN-CLOSED THE STORE SIDE 2026-11-08: the STATE ids DO have a store — the GLOBAL winmgr per-id window-handle table winmgr+0x3068 (u16 count) / +0x306a (32 u32 handles) at stride 0x8e per id, written by fn 0x57194 from parse block 0x59021 (PARENT-block fallthrough, fmts '%s %d' 0x85fdb + '%d' 0x85fe1); MEASURED 196/196 needle-verified saves at W=0x2bc3e4, 16/18 ids EXACT windows.txt order (id 1 runtime-appended EVENTWIN/Go^to^Planet/OK in 16 saves, id 17 slot-substituted in 22), sum(counts)=135=file STATE tokens, winmgr+0x4226=18=distinct ids (scripts/r336d_state_census.py exit 0; docs/re/ships.md S55 + docs/re/_wip_t336.md S4). STATE-line DISPOSITION now: stored in a live runtime registry, not a window-record field. t337 CLOSED THE READER SIDE 2026-11-08 (docs/re/ships.md S56 + docs/re/_wip_t337.md S0-S7, tools scripts/r337_state_readers.py + scripts/r337_state_word.py both exit 0): the table's readers are the SCREEN ROUTING machinery — dword winmgr+0x4226 is TWO u16s (LOW group count, HIGH = CURRENT STATE ID winmgr+0x4228, sole runtime writer 0x56f66 inside SET-STATE fn 0x56e10), MEASURED 537 saves at B=0x2bc3e4: histogram {0:122, 1:236, 16:5, 17:174} with group[state] residency 537/537 (the 5 state-16 saves = work/r1/t299-leg-20261105-112859/save/43..47.sav, i.e. recorded play DOES enter the battle state). STATE switching is a click-posted RING-A record (poster fn 0x56ad4, code-1 arm of resolver fn 0x55df4 passes the record's u32 PARAM as the new state; static param-0x10 posters 0x28ed8/0x51ad1/0x5200f/0x36b0b). t333's "there is NO global active-screen-state datum" is SUPERSEDED (the datum exists: u16 core+0x4228); t335's "the STATE ids have no in-image consumer at all" is SUPERSEDED by t336 (store) + t337 (readers). NO fn 0x56b5c broadcast site ever targets group 16 (all 9 sites name fixed groups {1,2,3,4,5,d,e,f}), and BatModeWnd magic-rec +0xb7 = 0 in every save including the state-16 five — the mode-1 arming edge SURVIVES. t338 DROVE THE GAME INTO STATE 16 LIVE AND THE CHAIN IS ZERO THERE TOO 2026-11-08 (work/r1/dbg-t338-20261107-224027 rc=0, docs/re/ships.md S57 + docs/re/_wip_t338.md, tool scripts/r338_state16_session.py): the state-16 TRIGGER is MEASURED (galaxy-map Icarus-pip click (238,282) enters the system view; SET-STATE fn 0x56e10 witnessed with edx=0x10 on core 0x2bc35c; 13 oracle reads state==16 through the battery; hit_test fn 0x56890 fired x2 and btn_hdlr x17 ON the state-16 family rows — pixels t332 measured NEXTTURNCONT-owned in state 1), yet all eight chain legs {0x156D4, 0x15EF1, 0x15FED, 0x1615D, 0x1616F, 0x161D1, 0x1B7DD, 0x1B180} are pty-whole-log ZERO with BatModeWnd +0xb7==1 in 0 oracle reads. SECOND independent zero; t337's "wrong screen state" candidate explanation for t332 is REFUTED as the cause. Mechanism banked: every state-16 row click routes to a CHILD button record (My^Items/Other^Items/W..I/Pass/Auto/Repeat); BatControlWnd itself is a TYPE-19 parent with rect 0,0-0,0 and can NEVER be a mouse hit target — entry at fn 0x156d4 requires a non-mouse 0x1c01 poster to registry slot 61. Evidence: docs/re/ships.md S52 + S53 + S54 + S55 + S56 + S57 + docs/re/_wip_t333.md +
docs/re/_wip_t334.md + docs/re/_wip_t335.md S0-S4 + scripts/r333b_state_layout.py
(exit 0, 372 saves) + scripts/r334_state_array.py (exit 0, 196 saves) +
scripts/r335b_item_array.py (exit 0, 196 saves) + scripts/r338_state16_session.py
(run rc=0) + scripts/r339_intake_census.py + r339_cfg156d4.py + r339_xreach.py
(exit 0; docs/re/ships.md S58 + docs/re/_wip_t339.md S0-S7). t339 LANDED THE
INTAKE DECODE 2026-11-07: NO poster of 0x1c01 to slot 61 exists — the eighth
leg is cited-dead BY CONSTRUCTION (whole-image literal census, windows.txt
max SENDMESSAGE 1006, CFG gate-block reachability, ctor b9=0 default exit,
0x320 posters aimed at BatModeWnd's NULL state table), and the 804..813
parent-post road is structurally blocked (pump parent-priority 0x56c34 +
parent rect 0,0-0,0). Row stays OPEN strict-close: the ONLY movement left is
user ruling D2-c (accept cited-dead, DECISIONS.md D3/OQ-016 note).; (2) setup-time home DRAW law — CLOSED
MEASURED
2026-11-04 t295: uniform rejection draw per race in race order, k=draw%T,
store row_r+0xd @0x22edd, claim gate 0x22ee0 (FUN_00022ce4 0x22eb4..0x22f55
full disasm + census scripts/r295_home_draw.py: equal-marker 30/30 turn<=2,
distinct 36/36, index chi2=31.0 df=49 crit 74.92); docs/re/income-law.md
S-T295 + docs/re/_wip_t295.md; rewrite pickHomeStars upgraded, stream
interleave vs world-gen stays UNMEASURED (isolated homeLcg_, distribution
law); (3) word[+0x16] template source — CLOSED MEASURED 2026-11-04 t294:
FILE TABLE, planitem.txt ASCII block after '#' (scalar->DS:0x66e4 @0x3802c,
11x4 weights->0x744f4 row-major @0x3801e..0x38067, grid B->0x7445c, grid C
->0x744a8); EXE-constant hypothesis dead two ways (0x744f4 past the
initialised data segment; image-wide SIB-aware store census = ONE writer,
the loader @0x3805f); file == banked runtime == live RAM 58/59/60.sav; the
INDEX itself stays the rng%11 draw @0x23a97; rewrite upgraded
(TerrainTables+loadTerrainTables economy.{h,cpp}, cfg.terrain consumed
campaign.cpp, main.cpp injects; pins tests/test_terrain_t294.cpp x5,
mutation-verified; income-law.md t294 block); (4) per-slot shield-byte
consumer (OQ-019 family) — CLOSED MEASURED 2026-11-08 t340 (ONE launch,
work/r1/t340-shieldc-20261108-014705 rc=0, docs/re/income-law.md S-T340,
tools scripts/r340_shield_complete_session.py + r340_writer_site.py +
r340_slot_writers.py exit 0): whole-83-slot per-turn ring diff — while
pending the SOLE mover is the acc word += stored IND; at the completion turn
(54+6=60>=COST 60, t1091) FUN_00038f68 0x3928b `or WORD [ebx+eax*4+2],dx`
(dx=0x0f00; gate flag-word bit8 SET @DS:0x74256 measured + slot>=cells) sets
word2 0x0000->0x0f01 (byte3=15 = ONE-TIME marker, t325 census fully
explained), then 0x39290..0x3929a resets +0x52=0xffff/+0x54=0xff/acc=0;
BPLM fired EXACTLY ONCE at EIP-linear 0x1f86e0=file 0x39290, esi=Gridsor I
record linear verified. NEW named observation (candidate residue 6, NOT
part of the closure): slot43 byte1 ff->00 at the same boundary = item 0
FACTORY auto-reserved on the HUMAN planet at completion, queuer undecoded —
the buildPhase "no auto selector on player planets" comment claim needs a
witness. t341 CLOSED CANDIDATE RESIDUE-(6) 2026-11-08 WITH CITED MEASUREMENT
(zero capture; docs/re/income-law.md S-T341 + docs/re/_wip_t341.md S0-S5,
tools scripts/r341_dis.py + r341_queue_writers.py + r341_writer_paths.py exit
0): the t340 "HUMAN planet" reading was an OWNER MISATTRIBUTION — Gridsor I
owner byte (NAME+0x33 == +0x57, t248 law) = 1 (AI) in all 20 ring saves; the
re-queue is the banked AI selector (fn 0x24f24 turn tail runs FUN_00038f68
per planet BEFORE FUN_0003e6e0/FUN_0003ea54 per race; queue-empty caller
0x3ead6; sole writer fn 0x38840 0x38af5..0x38b26; item 0 absent + COST/IND=5
< 70 -> deterministic first pick per t28 law). MEASURED LAW BANKED: the
vendor NEVER auto-queues for the human (local-race gate 0x3eabf..0x3eacd on
[p+0x5a]!=0, all owned planets read 0; 13/13 empty owner-0 queues persisted
over 7 turns). buildPhase comment upgraded to cite the witness; no code
delta. Rewrite buildPhase confirmed, comment cites 0x3928b/0x39290;
(5) human build-order minutiae — DISPOSITIONED PLAYER-INPUT CLASS 2026-11-08
t342 (ZERO capture; docs/re/income-law.md S-T342 + docs/re/_wip_t342.md, tool
scripts/r342_queue_census.py exit 0): corpus census of 4891 pending owner-0
queue rows (60 saves: playcap t1086 + bank-t1254 + t340 ring; caps EMPTY),
FULL-CORPUS PASS 3324 saves / 144,302 owner-0 pending rows, 0
complete-then-requeue vs AI control 180 —
[p+0x5a]==0 4891/4891, netplay==0 60/60 (selector gate 0x3eabf..0x3eacd
statically excludes FUN_0003f130 from every row); turn-sorted transitions
owner-0 PROGRESS 247 / DRAIN 8 / complete-then-requeue 0 while the SAME
instrument fires the AI signature 3/3 (Gridsor I, Arcturus I, Sarsaparilla
III); all 8 human DRAINs = completion + slot word2 bit0 SET + queue empty
next save; every anomaly class collapses to a banked law (flag-bit1 0xffff
cell t341; orbit slots cap=cells+10 t340; governor 33/34/35 acc-growth +
mode-3 select t45; ship COST=design value t27 with frozen bank rows). UI
writer legs named verbatim (fn 0x3aa0a 0x3b0d1/0x3d887/0x3b349/0x3b411/
0x3b482/0x3c9fc/0x3ca44/0x3daa9; fn 0x3a174 0x3a3f0/0x3a455; 0x3ae99 nougat-
gated). NO residue-(7): no pending owner-0 row requires a non-UI writer.
buildPhase comment upgraded to cite the corpus witness (no code delta). The
OQ-016 residue list is now EXHAUSTED ((1) cited-dead x8 legs = user ruling,
(2)(3)(4) CLOSED, (6) CLOSED as misattribution) — row movement per D3 is
USER ADJUDICATION; row stays open strict-close.
item-35/35 completion branches = MEASURED zero-witness + AI-unreachable
(REFUTED t271, re-open conditions there). t299 debugger leg witness ran
(2026-11-04): zero fires; t301 re-attributed as ARMING-FAILURE not a bypass
law (see OQ-019 note + ships.md S28); no OQ-016
constant moved, row stays open. T345 (residue-(4) follow-through, income-law.md
S-T345): marker-byte law closed MEASUREMENT-WISE — gate-bit8 population =
{18,19,26,27} runtime 48/48 (scripts/r345_gate_word_census.py exit 0), writer
census exhaustive (completion 0x3928b constants 15/35 vs setter fn 0x39760
ship-index; getter 0x396cc 25/25 sites item-23-gated -> shield constants inert),
corpus circle 360/360 ACTIVE ship rows resolve owner+0x59+0x58==3 (scripts/
r345_marker_census.py exit 0). Rewrite code site NOT landed: no per-ship
build-slot state exists to carry it (OQ-019 boundary); shieldThreatFor/
orbitalThreatFor sets runtime-verified unchanged. No code delta; row stays
open per D3. t397: D11 grading page is the answer channel
(http://<this-host>:8613/, work/r1/d1page + scripts/t397_grading_page.py);
acceptance close still requires the USER ruling, nothing closed here.

OQ-027 | audio | intro TUNEID index base + per-button vendor SFX id
| open | OPENED t388b 2026-11-14 (docs/re/audio.md §6). Two named residues
of the sound-fidelity row. (a) TUNEID base: subtitle.txt DIGITALMUSIC
TUNEID 6@FRAMENUMBER 20 / 7@988 maps into music.txt either 0- or 1-based;
the tune table is heap-relative (FUN_00074a88 stores [handle+0x8868]; same
limitation class as audio.md §3.4 +0x48a6 fields — no static base). Port
law in force: 1-based (6=intro00, 7=intro01; sizes fit that order only:
intro00 2,000,000 B = 90.7 s covers frames 20..988 unlooped; 0-based would
loop intro01 ~4x + play race00 over the opening). Closes on: user hearing
(user = grader) or a capture read of the heap tune table via the pointer
law. (b) per-button SFX id: FUN_000500e0 UI callers 0x17488/0x1749b read
indices from control-record +0x1bcc/+0x1bce (runtime window-item tables);
windows.txt SOUNDCHANNEL census {0 x118, -0 x1} carries NO sound id. Port
names (click08 NEXTTURN / laser01 map / bang01 captured) stay DOCUMENTED
port choices (audio.md §5). Closes on: capture diff of +0x1bcc across
control classes, or user hearing. --audio-trace instrument ships for the
wiring half (pins audio_tune_switch_law + audio_subtitle_script_cues_oq018;
t395 adds boot_tune_entry_law_t395, audio_invalid_tune_guard_t395,
audio_click08_offmanifest_t395 — the last one MEASURED click08.voc is off
soundfx.txt, so play("click08") had been a no-op; census re-run
scripts/t395_soundchannel_census.py re-pins {0 x118, -0 x1}, closes nothing).
t397: item (a)+(b) both askable on the D11 grading page (item 4 = paste the
`audio:`/`degraded:` startup line); row OPEN until the ruling lands.

OQ-019 | ships | per-ship design model (hull+gizmo inventory), sugar-cube->
hop scale, vendor cost hack, Orbital Docks effect
| open | CLOSED PORTION (full evidence: archive 2026-11-03 + docs/re/ships.md):
gizmo record law FUN_00049074 stride 0x6a x 76 == file census, RESREQ bitmask
+0x33, cat-switch copies Level->+0x52/56/5e/62, generator Power->+0x66 (§6);
cost hack CLOSED t16/§9 (sole gizmo-record write = loader parse 0x491b5; the
inherited +0x46-writers pointer is STALE — do NOT re-census); inventory law
CLOSED t46 (landed ship = active item-23 ring row, §10); Orbital Docks readers
§12-13 (upkeep/propulsion/range/step/fuel; executor has NO drive->distance
term); BUDGETS CITED t101: MOVES=[ship+0x94] refilled each resolver call to
drive stat SUM [ship+0x10] (FUN_0004a658, live 32/35), POWER=[ship+0x88];
SCALE MEASURED t183 (ships.md §17): FUN_00049f54 walks min(d/160, MOVES) sugar
units per resolver call, steps=max(1,round(walk)) capped by fuel; const pool
live 20/20 (1/160@0x25ff, 32.0, 5.0, grid quantizer DAT_000895dc=32);
round-robin = min-fuel one-ship-per-call inside turn loop FUN_00024f24
 (0x12e10 zero obj0 writers — no autonomous day-tick); LANE-STEP
LAW two corpora zero violations (|dx| == step0 or step0/3, step0=u16[+0x8]+
u16[+0xc]; /3 lane-scoped) + TURN-ATOMICITY (same-turn st5 dx EXACTLY 0,
17,595 pairs — t187 '4.67=3 substeps' DEAD, 4.6667 is one step); st4 = DWELL
state, in-system march resolves inside one turn boundary, invisible at 10 s
ring cadence (t265, 21 runs d=0.00 — corpus mining class CLOSED t49/t58/t265,
scripted capture ONLY); MAGNETRON runtime witness ZERO x3 (t265 off-grid
instrument P(false neg)<0.1%, t273, t285) — use-site stays static-cited
(gizhelp.txt:1173-1181 verbatim; kind==5 handler 0x21f58).
t359 NOTE (2026-11-09): user ruling D2=(b) commissioned the per-ship sim; its
BUILD CONTRACT is docs/re/pership-spec.md (t359, zero new measurement — a
dossier of already-cited laws + explicit non-goals; row closure still per the
t329 disposition packet / user acceptance at t365, NOT on this file).
t363R NOTE (2026-11-09): the sim MODEL now carries the gizmo inventory
(ring + recalc + upkeep burn + carrier/cargo fields, shipsim.{h,cpp}, ships.md
S62) — the magnetron/Phase-Bomb residue HOME is the ring field + carriesCode
accessor (zero-carried in the corpus; C5 chooser NOT modelled, per spec N4/N2).
Row STAYS OPEN (strict-close, user-gated): no named residue closer was touched;
the sugar-cube-clamp and destination-widget residues are unchanged.
t365 NOTE (2026-11-10): MODEL EXISTS, AWAITING USER ACCEPTANCE — the engine
flip landed: Campaign::combatPhase() resolves every engagement in the per-ship
engine (campaign_fleet_bridge.{h,cpp} driving ShipSim; aggregate demoted to
game/aggregate_oracle.{h,cpp}, test-only), pinned-seed suite green (223/0) and
seeds 1/2024/23 byte-identical pre/post (docs/re/engine-flip-t365.md). Closure
remains the user's call per the t329 packet.
t366 NOTE (2026-11-10): I/O SURFACE COMPLETE — write side shipped
(shipsave.{h,cpp} serializeRecord/writeShipRecords/rebaseRecord; write-back
byte-identical on 20/20 ring saves; pins test_shipsave_t366 x3, suite 226/0,
mutation 6/6; ships.md S63 + docs/re/_wip_t366.md). No game-emitted vendor
save is headlessly producable (cited-broken click path); honest note banked.
Closure remains the user's call.
t370 NOTE (2026-11-11, playtest witnesses, ships.md S64): residue-(1)
destination-widget annotated MEASUREMENT-WISE (amended, NOT deleted, NOT
closed — user-gated). First runtime witnesses from the user's own session
(turn 1253->1254, banks work/r1/bank-play-20261111{,-late}/): magnetron use
WITNESSED (power burn = gizmos.txt Power field exact, ring slot consumed);
gizmo use-counter decrements WITNESSED (cidx==gizmos.txt entry index for
9/60/73); empty-space destination orders write [+0x6c] triple ATOMICALLY per
issued order (type->3, one frame) — the two-click x/y-then-z testimony is
UNRESOLVED at field level because the 10 s watcher cadence cannot resolve
clicks inside one gap (adjacent XY->Z census = 0, cadence-blind, not
refuted); placement source vs star triples UNIDENTIFIED (honest negative S64
neg-(a)). Row closure remains the user's call per the t329 packet.
t377 NOTE (2026-11-11, static re-read + RAM corroboration, ships.md S19
corrections C1/C2 in place, full audit docs/re/_wip_t377.md): the magnetron
USE-SITE law was corrected against raw bytes — the range gate rejects a TOO-
CLOSE target (fail iff dist < Range*32; t185's wording inverted), the
TARGETLANE flag is a return-word bit not a commit gate (0x4cbd4 tests bit0
only), and the dispatcher prologue DECs the slot use word BEFORE the handler
ungated (a failed use still consumes). RAM design-row readout
(scripts/r377_design_rows.py, bank 3/3): row 60 cat=5 flags=0x2 power=10
range=50 numUses=1 == file row exactly. Code landing NOT done this session
(budget); sim seam design banked _wip S3. Row STAYS OPEN (user-gated;
strict-close — corrections refine cited law, they are not the named closer).
t377R NOTE (2026-11-12, CODE LANDED): the corrected law is now IN THE
REWRITE — ShipSim::useMagnetron (rewrite/src/game/shipsim.{h,cpp}) composes
C7-DEC-before-handler -> C1 corrected range gate -> C2 bit0-only commit
(TARGETLANE wired as a return flag, bridge bitpos 1) -> C3 min-charge ->
FUN_00021f58 placement + snapGrid -> C4 clearSlot single-use. 12 pins
test_shipsim_t377.cpp (M1 burn-exact/slot-gone/placement-form; C7
gate-fail-DECs x2; mode-0 lands nothing; zero-carried; no-second-use),
MUTATION 9/9 CAUGHT, suite 238/0. ships.md S65. Row STILL OPEN — the named
closer (sugar-cube residue, user ruling) is untouched; strict-close holds.
t378 NOTE (2026-11-12, CODE LANDED): the M3 destination-atomicity law is now
IN THE REWRITE — ShipSim::issueDestination/clearDestination
(rewrite/src/game/shipsim.{h,cpp}): the empty-space order writes type 3 + the
+0x6c triple in ONE step (4 witnessed issue frames), refusal writes nothing
(sim-level no-target sentinel — the cited 0xffff sentinel is the OWNER-half
law at 0x24a00/death, already pinned t364/t360, NOT an order-field value
honest negative _wip_t378 S2); order-end clears both atomically; object
orders refuse. 4 pins test_shipsim_t378.cpp, MUTATION 9/9 CAUGHT, suite
242/0. ships.md S66. Row STILL OPEN (user deferred; two-click sub-gap stays
cadence-blind, N8).
t379 NOTE (2026-11-12, CODE LANDED): the M5 death-vs-reclaim shapes are
RECONCILED to ONE measured law and are IN THE REWRITE — the C4 corpse is
in-place (word-level witness: exactly 5/177 words change; +0x62/+0x63/+0x68
RETAINED, the pre-t379 clears removed) and the "slot vanished" reading is the
count DEC at a lower index orphaning the top live record (s40 byte-identical,
never written). New seam ShipSim::liveCount/countWindow/orphanedShips mirrors
the count-word walk law (count == live census, 60/60 saves; corpse in-window;
orphan id >= census). 5 pins test_shipsim_t379.cpp (incl. corpus dead-row
shape both banks + s40 byte-identity), MUTATION 9/9 CAUGHT, suite 247/0.
ships.md S67. HONEST NEGATIVES banked (_wip_t379 S2/S4/S5): DEC writer
unattributed ([ds:0x3067b]==0 both banks), corpse refill-skip cause
unmeasured, s12 death producer unattributed (integrity survived — NOT the
hull<1 path in this witness). Row STILL OPEN (user deferred).
t380 NOTE (2026-11-12, CODE LANDED + CORRECTION): the QUANTIZER STORE LAW is
now in the rewrite and the S64 mid-transit signal is REFRAMED — every
committed galactic position store (walk incl. PARTIAL walks, placement,
scatter) passes the triple through FUN_000533e0 g=32 (walk quantizer call
0x4a2cf unconditional, copy-back gated by mode==1 only; placement 0x2202a and
scatter 0x399df store via the quantizing helper 0x49aa8); the t361-era
"arrival-time-only snap" reading is SUPERSEDED. Runtime census
(scripts/r380_grid_census.py): kinds 1/3/4 rest rows 100% on the 32-grid
(4020+800 rows, zero exceptions); ALL off-grid rows are kind-5 LANE-LOCAL
frames (S22 L4), so the (14,1,-224)/(28,0,-2144)/144.7 rows never contradicted
the law. 6 pins test_shipsim_t380.cpp (mid-transit snap, tie-away-from-zero,
lane-END grid rest, lane-local frame boundary, scatter invariant, corpus
census), 2 goldens corrected in place, MUTATION 7/7 CAUGHT incl. M7 = the
superseded arrival-gated reading. ships.md S68; _wip_t380 S1..S5. Row STILL
OPEN (user deferred).
t381 NOTE (2026-11-12, CODE LANDED + CORRECTION): the S64 M2 row is RE-READ
from the raw stream — the "LOST 2x Invasion Module" summary HID multiplicity
(Ignatz held SIX cidx-73 slots; EXACTLY the first TWO cleared at launch, four
survive). The consumption site is FUN_0003a174 0x3a2a2..0x3a38b: need :=
min(count, activeShieldUnits+1), walk-order first-match clearSlot — landed as
ShipSim::resolveInvasion. Handler-1 FUN_0004c794 CHARGES design[+0x36] under
gate affordable AND inRange AND (flags AND 0xc) (0xc = TARGETORBIT|
TARGETSURFACE, first cited consumer as a gate): the t364 "non-gun handlers
charge nothing" reading is SUPERSEDED; M2 -6 EXACT pinned twice. ds:0x85312
== f32 2.0 file-measured; cidx-0x2f handler-1 range leg is DEAD (dist*0.75
vs dist). 10 pins test_shipsim_t381.cpp, MUTATION 10/10 CAUGHT
(scripts/r381_mutate.sh). ships.md S69; _wip_t381 S0..S3. Row STILL OPEN
(user deferred).
RESIDUE: (1) sugar-cube per-turn clamp/arrival granularity — t293 SPENT the
3-launch scripted-capture budget, NEGATIVE (order never issued: orbital-grid
dot-clicks navigate, never select; full autopsy docs/re/_wip_t293.md +
ships.md t293 block; drive background=true, 420 s foreground cap kills a full
session). t296 CLOSED THE SELECTION SUB-PROBLEM STATICALLY (ships.md S24 +
_wip_t296 S1..S9, every block re-dumped verbatim): four cited gates — clip
exists iff [ship+0x58]==4 (builder 0x1d6bb), clip kind==2 (0x1b6fc/0x1b9f6),
owner [ship+0x54]>>16==ds:0x7458e (0x1b709/0x1ba16), MOVES [ship+0x88]>0
(0x1b716/0x1ba2c) -> [batwin+0xb7]:=2 (0x1b71f/0x1ba39); the dots are kind-3
PLANET clips so G2 always skipped, and in mode 2 a plain map click CLEARS
selection (0x1b114). REMAINING UNKNOWN = the destination-entry widget that
posts msg 0x50 (ds:0x43508 := [sel+0x42+ebx*4] @0x1b5dd/0x1b5e6 + command-ring
0x56ad4 code 0x11): no widget-side poster outside the batmode family in the
image-wide imm census; t297 re-read the msg-4 ROUTER 0x1b070..0x1b0d6
(verbatim, _wip_t297 S1/S2): a non-null [win+0xaf] routes EVERY click to the
batcon handler 0x1b91c(ecx=1) BEFORE the mode-2 deselect branch, and the
0x1ba8c leg publishes ds:0x43508 + ring code 0x11 directly at mode 0 — the
mouse route MAY reach publication with NO msg-0x50 widget. LIVE SESSION #1
t297 (work/r1/t297-order-20261104-152048, scripts/r297_order_session.py)
NEGATIVE: picker bug aimed it at an owner-1 ship (owner==0 filter missing —
fixed same-session), no kind-2 ever appeared. MEASURED corrections T297-A: ds
globals live at B+0x82bb0+X NOT B+X, and BOTH have non-order writers (0x43504
= 0x256825 non-null at idle t1086; 0x43508 churns without input) -> DELTA-only
witnesses. T297-B: batwin INSTANCE unpinned (u32 0x1aef8 zero refs in RAM;
0x1b91c only inside a verbatim payload-image copy at 0x22cac1/0x22eb3b).
GATING FACT: at t=1086 owner 0 has NO kind-4 ship (11 ships, kinds {3,5}) —
nothing is selectable; slot 8 becomes kind-4 MOVES=12 at t=1087 (the t293 5->4
lander) -> t298 MUST End-Turn ONCE before picking, target slot 8, and find the
sprite by COLOUR CLASS (ships.md S25). LIVE SESSION #2 t298
(work/r1/t298-order-20261104-174236, scripts/r298_order_session.py, 3
launches, mouse budget SPENT): End-Turn-once worked, full S1-S7 battery ran,
STILL no kind-2 — but the battery never saw the target (ships.md S26):
FLEET-LIST ORDER IS NOT ARRAY ORDER (measured rows Sparrowhawk/Erebor/
Erchamion/Ignatz = slots 18/7/16/22; sort law UNKNOWN) and unbounded colour
finders return SIDEBAR CHROME (client rect x 7..465 hard bound). New
measured law: RAM pointer VALUES are guest-PHYSICAL (target = member
value+0x88; t297-B zero-refs negative refuted — physical pattern of 0x1aef8
has 1 hit @0x247978); ds:0x43504 = current-system STAR record ptr ("Icarus"
read from it) = system-identity oracle; ship_array_law count 30 UNDERCOUNTS
(named owner-0 ships at 31/32/33; header "14 Ships" == 14 named records);
command ring churns from non-order input (delta-only, not an oracle).
NEXT WITNESS = DEBUGGER CLASS t299 (BPLM 0x1ba39/0x1ba5e/0x1baa7/0x1bad3/
0x1b114, r290 poke skeleton, dosbox-debugger.md) — no fourth mouse launch.
t299 RUN (2026-11-04, 6 debugger sessions work/r1/t299-leg-*): instrument
PROVEN (8 code BPs armed incl. handler 0x1aef8 + router 0x1b070, control
MEMDUMPBIN byte-exact) and NEGATIVE x3 with attribution: the same sessions'
FLEET/row/End-Turn clicks changed game state, yet ship/planet/empty clicks
in the Icarus system view fired ZERO legs. t301 RE-ATTRIBUTES the negative
(runs t299-leg-{213540,214042} + offline law, ships.md S28 + _wip_t301): the
TOGGRID control-click ZEROED but was INVALID (rect 557,403-587,433 pixel-black
in the Icarus view; windows.txt gives the SAME rect to TOGSHIPS/COSMOSWnd and
TOGGRID/BatModeWnd — sibling ambiguity), and the offline dispatch law shows
every msg goes `mov ecx,[win+0xa7]; call [ecx+4]` into the ACTIVE window's
class table (slot 1 = universal dispatcher file 0x30d08, verified in all
sampled tables). t299/t300 armed NEITHER slot-1 NOR the active class slots —
zero-fires = ATTRIBUTION FAILURE, not a bypass law; the WORKING FLEET/End-Turn
clicks executed type-0 class 0x247cb8 legs nobody armed. Window-record law
(magic 0x12345678, NAME@+0x20, table@+0xa7) + re-armed r299_leg_session.py
(router/cos_*/btn_* legs, stop dumps record NAME) are in hand; NEXT = one
debugger run, witness on the class the stops name (ships.md S28). t302 RAN IT
(run work/r1/t299-leg-20261105-004605 rc=0, ships.md S29 + _wip_t302): the
dispatch law is LIVE-CONFIRMED (cos_hdlr stop names COSMOSWnd, msg 0x3b
periodic; End-Turn fires btn_hdlr on NEXTTURN record with edx=0x7 ==
windows.txt SENDMESSAGE 7 VERBATIM = positive control; the turn-advancing
click fires COSMOS slot 3 edx=0x0). The t299-era zero-fires are fully
re-attributed: wrong legs + a fire-detector pattern that never matched this
build's DrawCode form. t303 RAN THE CENSUS (2 sessions
work/r1/t299-leg-20261105-{015611,020416} rc=1, _wip_t303 + REFUTED t303
amendment): whole-log pty census {cos_hdlr:15, all five call-[ecx+4] sites:0}
— the 0x3b pump reaches cos_hdlr WITHOUT slot 1, and t302's own log shows
btn_hdlr firing with router armed+silent, so the t301 "universal slot-1
router" law is REFUTED; a pixel-proven WORKING sprite click (modal "Ship
'Sparrowhawk'" dialog, vision-cited) fired NONE of cos_hdlr+5 sites. Map-click
entry is neither cos_hdlr nor slot-1 [verified negative]; the real dispatch
instruction is UNKNOWN. REMAINING RESIDUE: no per-ship selection WRITER
witnessed; t304 = [esp] caller-witness at any cos_hdlr stop (bank_stop
already patched: ret_stack.ret0/ret0_file_off) -> arm census at the named
caller; controls need close_eventwin between clicks + btn_hdlr armed. Row
stays open.
(2) per-ship build/redesign path =
BUILD DECISION not RE unknown (t256c census 62,762 rows, AI dossier row 16
GAP->BOUNDARY; docs/DECISIONS.md D3); (3) magnetron witnessed use (scriptable
via t289 drive class). | open
t304 note (run t299-leg-20261105-033648, ret_stack witnesses): the working sprite click DOES walk the class msg layer — btn_hdlr msg 0x1 NAME='Leave Orbit' via pump site file 0x56cda (ff 56 08 call [esi+8]); planet/empty clicks both hit the SAME 'Cancel' record msg 0x4 via 0x56c74 = modal residue, controls INVALID-AS-RUN (re-run with dialog-drain loop needed); NEXTTURN = btn_hdlr msg 0x8 NAME='PLSQUARE' direct E8 call site 0x3d38f. Selection WRITER still unnamed — row stays open (strict-close).
t305 note (run t299-leg-20261105-061825 rc=0, close_eventwin pre-arm + FIXED fire detector, docs/re/_wip_t305.md S4): per-target msg-ids MEASURED under normal core — baseline pump s2_56cda+cos_hdlr msg 0x3b COSMOSWnd (15/60 s); sprite(48,151) s2_56cda x2 msg 0x8 NAME='PLIND' + btn_hdlr x1; planet(439,331) s2_56cda msg 0x8 NAME='PLANETALLOC' (t304 'Cancel residue' SUPERSEDED for planet once drain applied); empty(236,200) fires ONLY site 0x56c74 (unbanked render, autosave-gap proven); NEXTTURN s2_56cda x2 msg 0x8 NAME='PLSQUARE' + btn_hdlr x1; 20 other slot-2 sites ZERO in every window. Selection WRITER still unnamed (msg 0x8 = repaint/dispatch at window records, not the selection store) — row stays open (strict-close).
t306 note (run t299-leg-20261105-101054 rc=0, batmode sites armed under corrected core + FirePat, docs/re/_wip_t306.md + ships.md S32): BATMODE STATIC-GATE ROUTE CLOSED AS A NEGATIVE — working sprite click (48,151, PLIND msg 0x8 btn_hdlr witnessed, control alive) fired ZERO at entry 0x1aef8, msg-4 router 0x1b070, and BOTH effect writers 0x1b71f/0x1ba39; selection oracle pairs moved nothing attributable (consistent with gating fact: t=1086 owner-0 has no kind-4 ship, but entry/router zeros are pre-gate). Writer hunt re-scoped to the non-batmode t296 store-census members: DAT_43508 {0x51a8e, 0x51fc2, 0x55bbd} + DAT_43504 {0x28ec2, 0x28ef6, 0x36b01, 0x52003, 0x55d35} (ships.md S24/S32). Selection WRITER still unnamed — row stays open (strict-close).
t307 note (run t299-leg-20261105-112859 rc=0, the eight non-batmode census
legs armed from the galaxy map + new --star-click battery, docs/re/_wip_t307.md
+ ships.md S33): FIRST LIVE FIRE AT A CENSUS MEMBER — w43504_28ec2 stopped
with EAX=0x256825 (Icarus star record) seconds after the (238,282) star click
that ENTERED the system (REQ-correlated pty render, follow-on bytes match
disasm 0x28ec7..0x28ed8 incl. ring post code 0x10). The writer is the COSMOS
FALLBACK star-select publisher (fn 0x28e70, caller 0x27332; gates: empty clip
list [win+0x582]==0, ds:0x7e582>>16==1), NOT the per-ship selection writer —
OQ-019 residue (per-ship select + destination widget) UNTOUCHED, row stays
open. Census instrument now LIVE-VALIDATED (it catches these writers), so the
seven remaining zeros are context statements. Binding instrument law from the
fire: data-segment immediates are REBASED +0x242000 in code RAM
(a3 04 55 28 00 @0x28ec2). NEXT: resolve the DAT-base question (true
DAT_43504 = B+OFF-0x88+X reads 0xff idle = SELECTED-NONE vs the t297-A
oracle address 0x28558c star ptr — ds:0x4358c zero disasm refs), then the
ring-consumer windows (0x55a60 family fires only on a turn advance).
t308 note (runs t299-leg-20261105-{140250,143815} both rc=0, docs/re/_wip_t308.md
+ ships.md S34): DAT-BASE QUESTION CLOSED — the oracle was NEVER off-target
(sav Memory member = linear+0x88; member B+SL.OFF+0x43504 IS linear 0x285504 =
the rebased store target; the t307 0xff datum read the member as if linear = a
different variable, REFUTED t308 amendment). DAT_43504 STAR-CASE WRITER FULLY
WITNESSED WITH A REAL DELTA: green-annulus pip law click (182,284) ENTERED
Vega; w43504_28ec2 stopped EAX=0x255BC5 (= star-record base k=0, name law
0x255be1-0x1c 'Vega'; screenshot vision 'Vega / White Dwarf'); oracle pair
0x256825 'Icarus' -> 0x255bc5 'Vega'; fire reproduced 3/3; DAT_43508 unchanged
(order-destination semantics consistent). STILL OPEN (strict-close): OQ-019
residue = per-SHIP selection writer (kind-2 clip; no kind-4 owner-0 ship at
t=1086) + the msg-0x50 destination widget (DAT_43508 legs zero x3 runs,
instrument live-validated); NEW SHARPENED HOLE: ring code 0x10 POSTED 3x but
the 0x55a60 consumer family never ran inside any armed window incl. a
NEXTTURN-msg window — consumer timing unresolved. NEXT: t309 ring-consumer
windows (arm the 0x55a60 family + advance the turn INSIDE the armed window).
t309 note (run t299-leg-20261105-161711 rc=0, consumer/post family legs armed
in every window incl. two HOT HOLDS, docs/re/_wip_t309.md + ships.md S35):
THE RING SELECTION CHANNEL IS DORMANT AT MAP IDLE — measured, not inferred:
leg ringB_post (RING-B POST FN ENTRY 0x55a60, gate-free prefix) fired ZERO
whole-log across baseline+star+hold+nextturn+hold, snapshots ringB_count=0/
widx=0 in EVERY window, consumer 0x55ae8 zero, and the star-click RING-A post
BODY never ran (its sole side effect inc [core+0x44ac] left idx 0 through
every snapshot; post-fn entry leg zero too). RING-B is structurally shut at
idle (pump gate [core+0x475a]==0 blocks unconditionally), so 'consumer timing'
was the wrong question — SELECTION IS RENDER-DIRECT (direct DAT stores). NEW
WRITER INVENTORY (whole-image a3+89/15 sweep): DAT_43504 has SIX writers (the
t296 census missed 0x51ac9 in fn 0x51b68, edx=0x13bc5+32*k star record addr);
DAT_43508 has SIX (missed 0x55bcc); fn 0x51b68 owns three of twelve. mode4226
IS A VIEW ID (map=1, system=0x10) — the consumer's mode==1 gate confines it to
the galaxy map. Star witness delta reproduced 4th time (Icarus->Vega). Turn
advance across NEXTTURN UNRESOLVED (1086->1086 but 10 s sav granularity,
t260 law — claim neither way). OQ-019 row STAYS OPEN (strict-close): per-ship
selection writer + msg-0x50 destination widget still unnamed; NEXT t310 = arm
fn 0x51b68 trio + ringA post entry/body legs {0x56ad4,0x56b4e} + snapshot
rd(0x7e5aa)/rd(0x7e89e), star-click + hold; EAX dump at 0x56ad4 settles the
core-base identity live.
t310 note (run t299-leg-20261105-173627 rc=0 attempt 2, order battery pre-turn
1086->1087 + sprite + planet + digit keys 1..9 + NEXTTURN, legs {w43508_51a8e,
w43508_51fc2, w51ac9 NEW, w43504_52003, s2_1616f NEW, btn_hdlr}, docs/re/
_wip_t310.md + ships.md S36): THE WRITER'S CLASS IS NAMED — fn 0x51834 is the
STATUSWND msg handler (RAM class-grid scan: fn entry+P0 exactly 1 hit RAM
0x248050; sole window-magic referrer of the instance class ptr 0x247FC0 named
'STATUSWND'; FILE-image scan 0 hits = relocation blindness CONFIRMED). The
msg-0x1c01 destination path (0x51A67: mouse-X gate -> DAT_43508=system ptr +
ring-A 0x11 / DAT_43504=star addr 0x13bc5+k*96 + ring-A 0x10) was NOT reached:
whole-log zeros on all five writer/relay legs with btn_hdlr x4 alive; digit
keys entered the dispatcher (ret0 0x56c77, ret1='1') but a 'Cancel' popup held
focus, not STATUSWND. ds:0x484ec MEASURED = last mouse X (0x30/0x1b7 after
x=48/x=439 clicks) — 'turn gate' reading REFUTED (REFUTED-ROUTES t310
amendment binding). Span fix: 0x51ac9 lives in fn 0x51834, NOT fn 0x51b68
(label builder). OQ-019 row STAYS OPEN (strict-close): destination-widget
fire still unwitnessed; per-ship select untouched. NEXT t311 = STATUSWND-
focused digit keys: close_eventwin to the bare map immediately before the key
window + ENTRY leg at fn 0x51834 0x51834 (dx=msg id, ret0=dispatch site) —
witnesses or refutes 0x1c01->STATUSWND in one run.
t311 note (run t299-leg-20261105-182822 rc=0 attempt 1, ENTRY leg
fn51834_entry FIRST (census MATCH=True 7/7) + {w43508_51a8e, w51ac9,
s2_1616f, btn_hdlr}, battery pre-turn 1086->1087 -> close_eventwin +
assert_on_map BARE MAP -> digit keys 1..9 one armed window (post-arm popup
reguard) -> sprite -> planet -> NEXTTURN -> hold, docs/re/_wip_t311.md +
ships.md S37): BRANCH (c) MEASURED — STATUSWND RECEIVES NO MSG TRAFFIC AT ALL
(entry leg gate-free, fires for any caller; whole-log fn51834_entry:0 with
btn_hdlr x4 alive). Focus defect FIXED: bare-map keys hit btn_hdlr window
'NEXTTURNCONT' (edx=0x3, ret0 file 0x3177d), NOT the 'Cancel' popup — the
key-focused window on the bare map is a button-family class, so the digit-key
sender's call [esi+8] structurally cannot reach fn 0x51834 from map focus.
0x1c01-into-STATUSWND REFUTED as a live trigger (REFUTED-ROUTES t311
amendment binding). OQ-019 row STAYS OPEN (strict-close, honest negative):
destination-widget fire still unwitnessed; per-ship select untouched. NEXT
t312 = ORDER-PLACEMENT choreography (t298-B: select ship mode 0->2 -> click
planet clip dl==3 @0x1bad3 relay 0x326 ecx=4) with the TWO NEVER-ARMED
destination writers armed — w43508_51fc2 + w43504_52003 (the fn 0x51b68 pair;
0x51ac9 belongs to fn 0x51834 per t310 span fix) — plus s2_356a5 (the digit
sender's own call site, closes the t311 sender question) + fn51834_entry
first; all four legs already exist in LEGS, no script delta. fn 0x51b68 is
table-member-called (t309), the run names its caller from ret_stack. Pre-turn
gate must yield a kind-4 owner-0 ship (t298 law) or the sprite select is a
no-op.
t312 note (run t299-leg-20261105-192246 rc=0 attempt 1, BREAK lottery won
first try, scripts/r312_relaunch.sh, zero script delta; legset fn51834_entry,
w43504_52003, w43508_51fc2, s2_356a5, btn_hdlr; battery = t298-B order shape
pre-turn 1086->1087 -> bare-map keys -> rowjump -> sprite 48x151 -> planet
439x331 -> NEXTTURN, docs/re/_wip_t312.md + ships.md S38): BRANCH (b)
MEASURED — SECOND HONEST NEGATIVE. Whole-log {fn51834_entry:0,
w43504_52003:0, w43508_51fc2:0, s2_356a5:0, btn_hdlr:4}, census MATCH=True
7/7. DECISIVE: sel43510=0 in EVERY oracle snapshot (sprite_before AND
sprite_after included) and mode4226 0x1->0x11 is the map->system VIEW id —
the sprite-pixel click NEVER selects, so the t298-B order never exists and
fn 0x51b68's writer pair stays structurally dark (REFUTED-ROUTES t312
amendment binding: sprite-pixel select DEAD; both msg-0x1c01 senders
s2_1616f+s2_356a5 measured dead — do not re-run any map/key battery shape
for this row). SENDER QUESTION CLOSED (negative): digit keys reach a window
(btn_hdlr 'NEXTTURNCONT') yet s2_356a5 zero => the taken keysym path is not
the 0x1c01 sender. OQ-019 row STAYS OPEN (strict-close): the two residues
(destination fire + per-ship select) are ONE hole. NEXT t313 = fn 0x51b68
CALLER hunt OFFLINE on this run's own save/ dir — class-grid RAM scan for
0x51b68+P0 (t310 route: grid slot index FIRST, then infer which table the
game consults; file scan is blind, RAM only), and inventory what dispatches
slot hits for that class; only if the caller names a FLEET-window path does
a new capture shape earn its keep.
t313 note (OFFLINE, zero capture; save dir of run t299-leg-20261105-192246;
scripts/r313_class_scan.py + r313_name_b.py + r313_fleetwnd_map.py +
r313_writer_callers.py + r313_handler_chain.py; docs/re/_wip_t313.md +
ships.md S39 + REFUTED-ROUTES t313 amendment): CALLER HUNT LANDED — THE
WRITERS ARE FLEETWND's. 0x51b68 is mid-body of fn 0x51b64 = FLEETWND class-
grid slot 3 (cp 0x247fa8, magic rec 0xfe7a90 'FLEETWND'); FLEETWND handler fn
0x51cc4 has its OWN msg-0x1c01 path (je 0x51f3b exact) -> confirm leg (ecx==5,
string 0x2b6b) or jne 0x52059 -> system-state table (file 0x3d100 unrelocated;
RAM instance 0x211188 {0x51fb5 x3, 0x51ff6, 0x52037} runtime-composed, whole-
RAM unique, identical 3/3 savs) -> state 1/2/3 writes DAT_43508+ring 0x11,
state 4 writes DAT_43504+ring 0x10. CLASS LAW FIXED (grid stride 6, cp =
base-0x88, dispatcher 0x30d37 call [cp+0xc]; t310's slot-4 was an 8-byte-
shifted read). t312 dark writers EXPLAINED: digit 0x1c01 hit 'NEXTTURNCONT'
focus, never FLEETWND. Row STAYS OPEN (strict-close — offline chain names the
mechanism but no live store witnessed). NEXT t314: ONE capture — legs
fn51cc4_entry (NEW, census leg[0]) + w43508_51fc2 + w43504_52003 + btn_hdlr
control; establish FLEET-window focus via open_fleet, then digit-key + a
map-click x>150 variant; oracle DAT_43504/43508 + sel43510 + mode4226.
t314 note (runs t299-leg-20261105-{210255,212402} both rc=0, docs/re/
_wip_t314.md S0-S7 + ships.md S40 + REFUTED-ROUTES t314 amendment): FLEETWND-
FOCUS TEST RUN VALID + NEGATIVE. Run 1 exposed a drive law (rowjump click
(200,93) CLOSES the FLEET window, rails 188->0) so its keys went to 'PLBUILD'
— invalid, not counted. Run 2 VERIFIED focus at arm (reguard logs rails=188,
popup-closed) then pressed 1..9: whole-log census {fn51cc4_entry:0,
w43508_51fc2:0, w43504_52003:0, btn_hdlr:4} — FLEETWND received NO msg of any
kind with its window open; the single fleet_keys stop was btn_hdlr win=
'STATSHIPLST' edx=0x3 ret0 file 0x32943 (inside STATSHIPLST's own slot-2 fn,
cp 0x247c70 read from RAM). GAP named: s2_356a5 was NOT armed run 2, so
"sender never fires under FLEET focus" stays t312-extrapolation. Offline this
session (objdump verbatim): sender branch 0x35675..0x356a5 fully decoded —
gated on [ebp+0xaf] (max digit 9, 10 if ==1), sends edx=0x1c01 ecx=0 via
call [esi+8] on ITS OWN window [ebp]; fn 0x32fa4 = 8-stride accessor
[[win]+0xc7+idx*8] (idx from msg arg, 0..0xff bound) — the writer-block state
byte [eax+0x58] reads a TABLE-SELECTED record (t313 "system-record" label
unproven); STATSHIPLST[+0x58]==0 in 40/40 saves across both runs (rec datum
only); payload store census for [r+0x58] = ZERO sites (computed offsets, file
blind). Row STAYS OPEN (strict-close — no live store witnessed). NEXT t315
(offline, zero capture): name the digit-handler window — find the fn containing
0x35696 (ret-bounded walk + E8 census), then RAM grid scan for fn+P0 (r313
route, NEW target so not spent) and magic-rec naming; that window is who the
digit key talks to, and its class decides whether FLEETWND can EVER receive
0x1c01 from keys.
t315 note (OFFLINE, zero capture; scripts/r315_handler_scan.py; docs/re/
_wip_t315.md S0-S6 + ships.md S41 + REFUTED-ROUTES t315 amendment): DIGIT-
HANDLER WINDOW NAMED — IT IS 'LOADSCREEN' (loadwin.cpp save/load screen). fn
0x35696 lives in fn 0x354f8 (unique prologue 56 57 55 81 ec 44 01; ZERO E8
callers); RAM hit exactly 1 @0x247db0, grid 0x247da8 slot 2, cp 0x247d20,
magic rec 0xfd705c NAME='LOADSCREEN' 3/3 saves both runs (controls 1-hit
exact, 5th reproduction). The digit->0x1c01 route is a MENU MECHANISM:
FLEETWND can NEVER receive 0x1c01 from keys (t314 zero explained, not just
measured). Whole-payload 0x1c01 census CLOSED at 5 sites (LOADSCREEN sender,
BatControlWnd receiver fn 0x16420 grid slot 3 cp 0x247850, relay 0x16169
t311-dead, msg-emit builder 0x33375 via fn 0x56ca4, E8-operand false
positive 0x1756b) — no in-game-window sender exists. GATE CHAIN MEASURED
EXACT: caller 0x51f3b eax=[rec+0xab] -> fn 0x32fa4 [win+0xc7+idx*8] ->
record; gate 0x52059 rec[+0x58] in 1..5; writer arms copy rec[+0x59..c] to
DAT_43508/43504. FLEETWND chain 0xfe7a90 -> inst 0xfe7ac0 -> slot0 rec
0x600000: GATE BYTE GUEST 0x600058 == 0, datum 0x600059..c == 0, 212/212
valid-chain saves (221 have [win+0xab]==0 -> accessor error path). Row
STAYS OPEN (strict-close — no live store witnessed; the gate byte was again
never evaluated live). NEXT t316 = the state-byte WATCHPOINT route on guest
0x600058 designed against the msg-emit path fn 0x56ca4 (NEW target), the
only route left that can witness a writer (key shapes are dead-by-mechanism
per t315 amendment; FLEET-rect interior click still untried as the intake
shape, t314 residue (a)).
t316 note (OFFLINE, zero capture; scripts/r316_registry_dump.py +
r316_registry_probe.py; docs/re/_wip_t316.md S1-S5 + ships.md S42 +
REFUTED-ROUTES t316 amendment binding): THE DYNAMIC 0x1c01 EMIT TARGETS
FLEETWND BY SLOT ID. Emit-builder = fn 0x33320 (sole `bb 01 1c 00 00`
0x33374; span [0x33320,0x33456); EXACTLY ONE E8 caller 0x32778 inside
STATSHIPLST slot-2 fn 0x32664 in-rect msg-0xc branch — NOT a map/HUD pump).
Road selector global 0x9f100 (runtime 0x2e1100) == 0 measured -> 0x1c01 road
(else 0x1c02); target edx = [w+0x63] == 95 in 685/685 saves; rec+0x41 =
registry slot-id PROVEN STATICALLY (ctor fn 0x3264c stores fn 0x5712c's
return there; FLEETWND rec [+0x41] == 95). Chain continuous end-to-end
offline: ship-list in-rect click -> fn 0x33320 -> fn 0x56ca4(0x7a35c, edx=95,
msg) -> [slot95].win = FLEETWND rec -> call [rec+0xa7+8] = fn 0x51cc4 ->
gate 0x600058 -> writer pair DAT_43508/43504. HONEST NEGATIVE: registry table
[mode 0x4226]==0 AND [count 0x3000]==0 in 685/685 saves, zero RAM pointers
to the FLEETWND rec — REGISTRY IS RUNTIME-REBUILT, save scans can never
witness delivery (third blindness class). Row STAYS OPEN (strict-close: no
live store witnessed; chain is static-cited only). NEXT t317 = THE LIVE
CAPTURE per REFUTED-ROUTES t316 amendment (4): legs {fn 0x56ca4 entry,
fn51cc4_entry, w43508_51fc2, w43504_52003}; FLEET open + click inside
STATSHIPLST rect (7,46,632,472; verify fn 0x33058 msg-arg semantics vs the
[w+0xbf]=28 guard BEFORE picking coordinates); NO rowjump.
t317 note (LIVE run work/r1/t299-leg-20261106-012002 rc=0 + offline;
docs/re/_wip_t317.md S0-S8 + ships.md S43 + REFUTED-ROUTES t317 amendment
binding): THE t316 CHAIN INTAKE IS LIVE-REFUTED. Vendor gutter clicks
(x=620, strip law 632-[w+0xbf]28 verified, [w+0xb3]=-1) arrive at registry
dispatcher fn 0x56ca4 AS MSG 8 ON STATSHIPLST'S OWN ENTRY (4/4 clicks,
edi=edx=0x8, eax=0xfe7ac0 NAME='STATSHIPLST', coords verbatim ebx=620;
baseline 0) -> fn 0x33058 row bookkeeping (gutter sub-branch 0x33158 =
self-send 0x193 + row-table clearers fn 0x56730/fn 0x56434, decoded NOT
dispatchers). WHOLE-LOG fn51cc4_entry ZERO, w43508/w43504 ZERO,
gate 0x600058=0 datum 0 after every window, oracles unmoved: NO 0x1c01
delivery happened; the emit road's msg-0xc premise never occurs and
[w+0x4f]=0x30 is additionally required (0x66; direct-store census CLOSED —
sole store movb $0,[r+0x4f] @0x30bdb, so 0x66 is copy-written). Row STAYS
OPEN (strict-close: no live store witnessed). NEW SEED: the msg-0xc/4
delivery road into fn 0x32664 is the BROADCAST PUMP fn 0x56b5c (per-entry
slot-2 dispatch call *[tgt+0xa7+8] @file 0x56c74; posters 0x54aa9/0x54ab2
driven by click record ds:0x484ec/0x484f0; suppression ds:0xa2024) — t317
armed s2_56cda only, so msg-0xc/4 deliveries were structurally invisible.
NEXT t318 = ONE live run legs {s2_56c74, s2_56cda, fn51cc4_entry,
w43508_51fc2, w43504_52003} + the proven --shipclick choreography
(_wip_t317 S8); a msg-4/0xc stop at s2_56c74 on the STATSHIPLST rec plus
s2_56cda edi=0x1c01 closes the destination-fire residue.
t318 note (LIVE run work/r1/t299-leg-20261106-021602 rc=0 + offline;
docs/re/_wip_t318.md S0-S6 + ships.md S44 + REFUTED-ROUTES t318 amendment
binding): THE PUMP DISPATCH IS COLD. 9 armed census windows (540 s, 6 legs,
full standard tail incl. ONE witnessed turn boundary (pre-turn 1086->1087;
the NEXTTURN after-oracle still read turn 1087, so a second advance is
UNWITNESSED): s2_56c74 ZERO whole-log;
s2_56cda 26 (18x msg 0x3b COSMOSWnd periodic; 4x msg 8 STATSHIPLST at the
x=620 gutter clicks — t317 reproduced verbatim; msg 8/6 PLIND; 2x msg 8
PLANETALLOC); fn51cc4_entry ZERO (2nd independent confirmation NO msg of any
id reaches FLEETWND); writers ZERO; literal 0x1c01/0x1c02 absent from every
banked reg/stack. Honest scope: legs are deleted between windows and during
fire-cycle re-arm gaps, so this is "delivered nothing observable", NOT "fn
0x56b5c never called". Static poster-block re-read (disasm 77195-77245): the
msg-4-vs-0xc choice at pump-call 0x54ac5 is gated by cmp edi,ds:0x484a4
(0x54a3f) then cmp edi,[esi+0x24da4] (0x54a88) + [esi+0x489e]==0 — the
poster gate is the NAMED BLOCKER. Row STAYS OPEN (strict-close: no live
store witnessed). NEXT t319 = ONE run legs {pump_entry_56b5c 0x56B5C,
p54a47, p54a88, s2_56c74, s2_56cda} same choreography — separates
caller-never / gate-never-equal / mask-empty in one shot (_wip_t318 S6).
t319 note (LIVE run work/r1/t299-leg-20261106-030727 rc=0 attempt-1 +
offline; docs/re/_wip_t319.md S0-S5 + ships.md S45 + REFUTED-ROUTES t319
amendment binding; scripts/r319_{relaunch,analyze,gate_read}.py NEW;
r299_leg_session.py LEGS +3): THE POSTER ROAD FIRED LIVE — THE THREE-WAY
QUESTION RESOLVED AS GATE-NEVER-EQUAL. Banked EV stop 6 s after gutter click
y=453: fn 0x56b5c entry, edx=0x4 MSG-4 (NOT 0xc), esi=eax=0x2bc35c core obj,
edi=0xffffffff (=[core+0x24da8]), ret0 file 0x54aca = E8 call site 0x54ac5
THE POSTER, esp_p8=0. pty-whole-log-census {pump_entry:1, p54a47:0,
p54a88:1, s2_56c74:1, s2_56cda:106 (102x msg 0x3b COSMOSWnd, 4x msg 8
STATSHIPLST gutter VERBATIM 3rd time, 1x msg 0x193 self-send)}; the
p54a88/s2_56c74 counts are re-arm-gap renders (t305 law; contexts verified
verbatim). msg 0xc REQUIRES [core+0x24da4]==-1 — measured 0 (r319_gate_read,
oracle-law addressing, cross-checks t318 gate_484ec=0x1ff exact); equal road
requires ds:0x484a4==-1 — measured 0. Block-entry key ds:0x484dc==-1 AND
ds:0x484d0!=0 set by mouse-state recorder fn 0x2a7a4 — ONCE in 28 min. NO
0x1c01/0x1c02 literal in any of 108 banked stops; DAT oracles unmoved: the
msg-4 poster is NOT the destination road. Row STAYS OPEN (strict-close: no
live store witnessed). WRITER CENSUS LANDED SAME ITERATION (static,
_wip_t319 S5): [core+0x24da4] is fn 0x54650's OWN mouse-active flag — set -1
@0x546a5 iff ds:0x484ac!=0 (writer fn 0x2a629), reset 0 @0x546d0 iff
ds:0x484ac==0; so msg 0xc fires iff the mouse is ACTIVE in the SAME main-loop
pass the poster block runs; the witnessed msg-4 = the quiet pass. NEXT t320 =
offline ds:0x484ac census over the run's own save dir (r319_gate_read now
prints it) + fn 0x51cc4 msg-4 branch decode; only if the census shows input
traffic CAN hold 484ac!=0 at poster time does the mouse-active-poster-pass
capture shape earn its keep.
t320 note (LIVE run work/r1/t299-leg-20261106-041522 rc=0 attempt-1;
docs/re/_wip_t320.md S0-S11 + ships.md S46 + REFUTED-ROUTES t320 amendment
binding; scripts/r320_relaunch.sh NEW; r299_leg_session.py +--pulse-clicks):
THE MOUSE-ACTIVE POSTER-PASS RUN FIRED THE POSTER 27x — ALL MSG 4, ZERO MSG
0xc. pty-whole-log-census pump=27 (caller histogram 27/27 POSTER 0x54ac5,
every stop edx=0x4 edi=0xffffffff esp_p8=0); baseline windows 0 (idle law);
28 pulse clicks logged inside armed windows; 1/20 run saves froze the entry
conjunction (484d0=1, 484dc=-1) — save axis corroborates the traffic law,
saves remain BLIND to 484ac/24da4 (19/20 all-zero). ds:0x484ac RECLASSIFIED
(static, t91_code_disasm 24853-24866 verbatim): BIOS int 16h AH=2 BUTTON-HELD
word — -1 iff left/right held AT POLL, cleared by the next ms-scale poll; a
50-ms pulse press cannot cover the ~20 s poster period. xdotool absent + SDL
rejects synthetic motion: motion levers dead here. Row STAYS OPEN (strict-
close: no msg-0xc stop, no live 0x1c01/DAT_43508 store). NEXT t321 = the
press-only Button1 HOLD shape (xsend.c clickhold/clickrelease, release
ALWAYS before tail) IF the loop still wants the 0xc road; else the fn 0x51cc4
msg-4 branch decode (offline, t319 S6) — the msg-4 poster has now been shown
twice to move no oracle.
t321 note (OFFLINE decode, zero capture; docs/re/_wip_t321.md S0-S7 +
ships.md S47 + REFUTED-ROUTES t321 amendment binding): fn 0x51cc4 FULLY
DECODED — msg 4 AND msg 0xc have NO dedicated branch (fall through 0x51d00
-> tail-call fn 0x336b4), and fn 0x336b4's complete tree stores NOTHING to
ds:0x43508/0x43504 (msg 4 -> rect-gated ring-post or registry forward fn
0x56ca4; msg 0xc -> rect-gated ring post code 5 only). The 0x1c01 handler
0x51f3b -> 0x52059 state table (RAM instance {0x51fb5 x3, 0x51ff6, 0x52037},
t313) is the window's ONLY store road. msg-0x50 sender census re-closed
image-wide (3 mov edx,0x50 sites all non-msg). DECISIVE HARNESS FACT: the
batcon-family stores 0x1b5e6/0x1baa7 (fn 0x1aef8/fn 0x1b91c, t296 chain)
were NEVER ARMED as legs in any capture t307..t320 — every writer-zero
negative covered the OTHER eight sites only. Row STAYS OPEN (strict-close:
offline decode + re-verification, no live store witnessed this iteration).
NEXT t322 = batcon two-click capture, legs {batmode_dead 0x1aef8,
fn1b91c_entry 0x1b91c, w43508_1b5e6 NEW, w43508_1baa7 NEW} + btn_hdlr
control + Icarus-view battery, recorder-first reads of [win+0xaf]/[+0xb3]/
[+0xb7]; decision tree _wip_t321 S7 (a: 1aef8 fires -> script choreography
from live state; b: 1aef8 silent with btn_hdlr alive -> blocker = BatModeWnd
window composition/activation, offline STATE-bytes probe). Button1 HOLD for
the pump is DEAD per REFUTED t321(1).
t322 note (LIVE capture work/r1/t299-leg-20261106-055549 rc=0 attempt-1;
docs/re/_wip_t322.md S0-S6 + ships.md S48 + REFUTED-ROUTES t322 amendment
binding): the batcon click-road legs {batmode_dead 0x1AEF8, fn1b91c_entry
0x1B91C, w43508_1b5e6, w43508_1baa7} were armed LIVE FOR THE FIRST TIME over
the full t298-shape battery (pre-turn 1086->1087, fleet open, rowjump, sprite
48x151, planet 439x331, NEXTTURN). MEASURED decision-tree branch (b): pty
whole-log {batmode_dead:0, fn1b91c_entry:0, w43508_1b5e6:0, w43508_1baa7:0,
btn_hdlr:3} — BatModeWnd received ZERO msgs all session while the control
lived and the instrument verified (census-ctl MATCH=True); sel43510=0 9/9;
DAT_43508 churn 0x26fe77->0x26f00d writer-less (writer-less law re-observed).
THE t321(3) BLIND SPOT IS NOW CLOSED AS A BLIND SPOT: the mouse road was
tested and is dead IN-CAPTURE — BatModeWnd is composition-shielded at the
campaign/system map (windows.txt line 1178 STATE 1 16 never active in captured
sessions). Row STAYS OPEN (strict-close: no live store witnessed; the negative
is the datum). NEXT t323 = OFFLINE activation decode ONLY (zero capture,
per _wip_t321 S7 decision tree): who writes the window-record STATE field /
what shows BatModeWnd (fn 0x1d7dc / fn 0x1be10 exit-side candidates, registry
instance via t313/t316 tools, handler member 0x247978); a capture is justified
ONLY after the decode names a concrete activator widget/keypress. NO third
mouse battery.
t323 note (OFFLINE activation decode, zero capture; docs/re/_wip_t323.md
S0-S6 + ships.md S49 + REFUTED-ROUTES t323 amendment binding): THE ACTIVATOR
DOES NOT EXIST — honest negative, census-complete. STATE 1 16 is NOT a
visibility flag: the STATE line builds the per-window state-RECORD table at
windows.txt load (14B records; loader fn 0x31d58, sizing fn 0x32000); runtime
state = WORD [win+0xb1]. COMPLETE [win+0xb1] writer census (14 sites, all
classified): constructors fn 0x31c54/0x3377c/0x33d08/0x33c34; char-input
cycler fn 0x339a4 (unreachable for BatModeWnd — no char handler in its msg
tree, t296 S5+t321); fn 0x364d2 (writes the TABLE not a window field); the
ONLY runtime switcher fn 0x31f30 <- EXCLUSIVELY fn 0x32100 (generic
state-rect-click msgs 0..8, jump table cs:[0x1d524]) which is NOT in the
cited BATMODE class table (t296). Every runtime "BatModeWnd" naming is inert
or foreign: fn 0x2351c name arg = dead assert-string (overwritten @0x23558;
body = layout bookkeeping ds:0x48c44); fn 0x528ec@0x52a76 result unused;
fn 0x156d4 (BATCTRL) stores the lookup unread and resets BatListWnd instead.
fn 0x1d7dc = repaint/teardown, fn 0x1be10 = cursor chooser — neither writes
state. Msg 0x53/0x50 re-probe inside the candidate set: no poster exists
(fn 0x32100 covers msgs 0..8 only). DISPOSITION per task spec: OQ-019
select/destination residues (destination widget msg 0x50, live stores via
fn 0x1b5e6/0x1baa7) = UNREACHABLE-BY-CAPTURE; law stands static-cited (t296
S5 four gates + t321 S1-S4); t322 armed-zero EXPLAINED as design, not an
untried activator. Row STAYS OPEN (strict-close: no live store witnessed;
the narrowed negative is the datum). Re-open condition: RAM census showing a
[rec+0xb1] writer (e.g. fn 0x32100) installed in BatModeWnd's RAM class
table at [rec+0xa7]. NEXT: OQ-019 remaining live-open scope = the sharpened
t308 ring-consumer hole is CLOSED (t309/t310); with the mouse+activation
roads both dead, the per-ship select leg has NO remaining capture route at
t=1086 — remaining candidates must come from a DIFFERENT sitting/save state
(kind-4 owner-0 ship exists) or the row's residue is dispositioned
permanently per the t323 amendment.
t324 note (OFFLINE, zero capture/zero guest boot; scripts/r324_census.py +
docs/re/_wip_t324.md S0-S4): THE t323 RE-OPEN CONDITION IS DISCHARGED —
NEGATIVE ABSOLUTE. Live-RAM census of the BatModeWnd class table (read
surface = production save `Memory` ZIP member per the pointer law; 10/10
saves 50..59 t=1086 identical; model validated per-save via the Icarus star
record 0x256825 name read): the table at data payload offset 0x58e8 — the
SOLE `[rec+0xa7]` install target (image census, 62 stores: 0x58e8 only at fn
0x1ac21) — reproduces the cited BATMODE table BYTE-FOR-BYTE: RAM slots
0x1da04c/0x1f0158/0x1da348/0x1dcca8/0x1f0608/0x1dde2c == P0+0x1abfc/0x30d08/
0x1aef8/0x1d858/0x311b8/0x1e9dc (6/6 in-code), fn 0x32100 ABSENT (and
0x31f30/0x339a4 too). Rebase model measured: table base = unrebased data
offset, slots = P0+static fn offset. Caveat (honest): the census anchored on
the unique installer's target offset, not on a physically located BatModeWnd
RECORD — no resident record exists in the t=1086 save (no u32 -> "BatModeWnd"
name pool found), consistent with t322's never-in-view finding; that state is
itself the closed class. Task-text correction: [wmgr+0x3337] stride 0x27 is
the LANE POOL (data 0x16147), not a window-name registry. Every OQ-019
capture route is now cited-dead: t319/t320 pump, t322 mouse, t323
activation, t324 class-table. Row STAYS OPEN (strict-close: no live SELECT
store ever witnessed — this is a cited-dead-route closure). Disposition
packet = t329 (drafts only; the row closes on USER ruling).
t329 note (DISPOSITION PACKET delivered, zero capture; docs/re/_wip_t329.md
S1-S5 + scripts/r329_magnetron_census.py exit 0): final row text DRAFTED at
_wip_t329 S4 — DO NOT APPLY; row status flips to closed ONLY on USER ruling
(D2 commission, or accept boundary + cited-dead notes). New MEASUREMENT this
iteration (magnetron residue): carriage census — production playcap/save
(t=1086) 20 saves/600 ship-rows hold ZERO cidx-60 (Lane Magnetron) slots,
while scratch epochs t261-drive (360 owner-0 slots) and t288-probe-* (252)
DID carry and STILL produced zero uses across the t265/t273/t285 mines ->
residue is WITNESS-CLASS, not absence-only. Scripted-drive idea RETIRED
(cited-indirect, _wip_t329 S2): gizmo-use orders arm only via the batmode
family state-WORD tail 0x15c63/0x15da6 (`mov eax,[ebp+0xb1]` gate -> [ship
+0x62/0x63/0x67] stores), the field t323 proved has no in-session writer and
t324 proved unswitchable in live RAM; commit edges 0x25560/0x25570 (t88a) are
unreachable without the armed order. CAVEAT banked: no census names the
window record owning the 0x15xxx block — identity inferred from t88 'batmode'
labels + gate shape, closure class same as t323 accepted. Row STAYS OPEN.
t397 NOTE: acceptance stays DEFERRED per standing ruling (do NOT re-ask);
the D11 grading page does NOT ask D2 and must not be edited to. Nothing
closed; only a USER ruling on the deferred packet closes the residue.
CLOSED (slimmed 2026-11-03: full evidence text of every row below lives in
archive/state-v2-full/2026-11-03/OPEN-QUESTIONS.md and the cited law file.
DO NOT re-open, re-derive, or re-census any of these from a fresh session —
the law-file citation is the working handle; re-treading is iteration waste.
Format identical to open rows: ID | area | question | CLOSED date+task | evidence; code site.)
OQ-003 | gam | .gam packed-entropy residue | CLOSED 2026-10-13 t181 | measured three-class disclaim scripts/r1_t181_banddiff.py (band boot-vs-played 432/2048 vs header/S-table 87-100%); docs/re/savegame.md section t181; rewrite unchanged (fresh-start-only)
OQ-004 | tables | which tables load; .cob container grammar | CLOSED 2026-10-06 06s | u32 N + N x 50B names + N x u32 offsets, ascend00 54/54 md5; RAM name table 0x250c1c 3/3 captures; pool-relative immediate law 337 sites; docs/re/datafiles.md S3-S5 (gate 3i2 scripts/cob_probe.py); no rewrite delta (reads extracted dir directly)
OQ-006 | audio | headerless sample rate | CLOSED 2026-10-07 | DEVICE rate 22050 measured (open chain PUSH 0x5622 @0x4f690 -> setter 0x6e000 stores [obj+0x3c]; default 11025 always overwritten); docs/re/audio.md 3.1; pin audio_open_rate_measured_oq006; channels documented default mono (no vendor field)
OQ-010 | rules | combat damage application | CLOSED 2026-10-14 t89 | firing order 0x4a5c1, damage design[+0x52]/[+0x4a] no hit roll (measured-negative), shield-then-hull absorb, death 0x49d2c, commit mode==1 0x25560/0x25570; docs/re/combat.md S2d..S2j; rewrite campaign.cpp attackScore/defenseScore/combatPhase + pin campaign_combat_law_oq010
OQ-012 | mapgen | size options + pps + shell position | CLOSED (a 2026-10-12, b-d 06o/06p/06q/06k) | density cycle 50/75/100/15/25; pps U{1..5}; shell position law; docs/re/mapgen.md; rewrite --stars knob + upgraded shells (rewrite site mapgen.cpp)
OQ-013 | tables | restree semantics | CLOSED 2026-10-06 | live = 66 main rows; stride 75 record map; COST LAW runtime = file_cost x (row-20) clamp 65000 reproduced 66/66 (0x4691d..0x46a15); docs/re/research.md 6; rewrite Tech::runtimeCost + 2 pinned tests
OQ-014 | tables | planitem unknowns | CLOSED 2026-10-06 | loader FUN_00037fc0 + checker FUN_0003830c; stride 0x28 record map 39/39 byte-exact; REQUIRES law avail iff req==0xFF || (req<66 && owned) -> 254 DEAD; grid C row sums = size-class cells 2650/2650; docs/re/economy.md section 4; 3 pin tests (gate 3l Trucking grep); rewrite requiresAvailable
OQ-015 | dip | DA_ template order + %token | CLOSED 2026-10-08 t12-t14 | chooser FUN_00044a44 == ACTIONS pool idx; %token census 22/22 == {%m,%y,%s,%t}; pins dip_action_chooser_law_oq015_t12/d_t13/d_t14; rewrite unchanged (trade gates -> engine build, docs/PLAN.md A7)
OQ-018 | audio | soundfx.txt pairs + VOC + theme map | CLOSED 2026-10-07 | voiceBand law 327/328 spans == disk sizes; VOC u16@25==0x0911 15/15; race->theme REFUTED (DAT_00010ba0 sole writer 0x21309); docs/re/audio.md 2.1; rewrite/src/formats/voc.cpp pins + test_audio_voice_band_law_oq018
OQ-020 | abilities | charge days for 14 charged SA_ | CLOSED 2026-10-15 t100 | cadence word WORD[0x6780+2*ability] == FILE 0x89330 zero writers (5:60 6:100 7:62 8:77 9:90 10:150 11:70 12:63 13:66 14:72 16:92 17:100 19:89 20:68); wired kCad[21] in rewrite/src/game/species.cpp abilityChargeTurns + COUNT-UP law; verify scripts/r1_t100_cad_verify.py
OQ-021 | victory | end-ctrl threshold | CLOSED 2026-11-03 t292 | LIVE presenter witness: BPLM sentinel 0028A2FB mid-pass stop 0x24274, evaluator FUN_00024a34, sel 0->5 DAT_00043510 @0x24d9f + rank 42 DAT_0004350c @0x24dab, end-ctrl.txt verbatim on screen; comparator V >= floor(2T/3)+1 MEASURED; run work/r1/t290-poke-a40-20261103-165405; docs/re/score.md S18-S20; rewrite arm campaign.cpp:2157 upgraded t291 + pins test_control_t291.cpp
OQ-022 | audio | music span-vs-check contradiction | CLOSED 2026-10-07 t8 | guard @0x59984 precedes checked call; DS:0xa200c all-zeros 10/10 saves; engine INACTIVE in captured states; docs/re/audio.md 3.4; no rewrite dependency
OQ-023 | dip | relation-state enum semantics | CLOSED 2026-10-29 t189b | state-3 ALLIANCE event OBSERVED @t1335 (cell0i=celli0=3, att +10/+10, 68 rows, scripts/r1_t188_state3_arbiter.py RC=0); flip 631>570 = static law 0x4562f/0x45641; enum 2=WAR/1=PEACE/3=ALLIANCE; docs/re/diplomacy.md 13+16; rewrite unchanged diplomacy.cpp:227/:244; engine residual -> PLAN.md A7
OQ-024 | rules | planet GOVERNOR assignment | CLOSED 2026-10-09 t45 | @0x38df0 branch pinned verbatim (item 33 -> PROS+=IND>>2, 34 -> RES+=IND>>2); [0x743b9]>>0x18 == UPOP(35) 32/32 saves; activator @0x38b26 sole trigger 0/2810; rewrite PlanetState::governor + pin campaign_governor_law_t45; docs/re/economy.md
OQ-025 | mapgen | non-default-density position law | CLOSED 2026-10-15 t79 | shell radii fixed at every size, populations halving law (T//2+1 then halve), reproduces T=50 battery exactly; docs/re/mapgen.md; rewrite shellRadiiFor replaces i%50 wrap
OQ-026 | visibility | fogged lane/star gating | CLOSED 2026-10-29 t195 | implement+pin at the row's own bar: viewerMaskFor == FUN_00021a84 verbatim, filter == 0x2914e AND, shareLaneVision == FUN_00046354 shape; rewrite laneVis_/starLaneVis_/starSelVis_ (obj +0x16/+0x17 twins); pin campaign_visibility_law_oq026_t195; docs/re/ships.md S23 L10

- > OQ-001 .cob offsets -> formats/cob.h reader (format block cites this ledger + FINDINGS P1a)
- > OQ-002 FLIC codec -> formats/flic.h (cites docs/re/flc.md)
- > OQ-007 CP437 -> decode sites game/species.cpp, game/research.cpp, game/starstat.cpp, game/economy.cpp, game/diplomacy.cpp
- > OQ-008 loader control-flow model -> ANALYSIS-ONLY (rewrite is fresh-start-only; no loader in rewrite; spec docs/re/loader.md)
- > OQ-009 AI data side -> ANALYSIS-ONLY input to the W-B-gated diplomacy/AI build (docs/re/ai-data.md; nothing shipped reads it yet)
- > OQ-011 POINTER LAW (scripts/r1_pointer_law.py 12/12 slots, gate 3q) -> measurement instrument only, cited by capture scripts + campaign.cpp:593
- > OQ-017 .fnt codec + UI wiring -> formats/fnt.h (cites docs/re/fnt.md) + ui/ui.cpp wiring
