# t194 WIP — visibility consumer hunt (OQ-026)

Session start 2026-10-29 ~14:12. Assigned task: STATE.md NEXT t194 = HUNT THE
VISIBILITY CONSUMER — decide OQ-026 (does the vendor UI/AI ever WITHHOLD a
fogged lane or star?).

## T0 — TRIGGER-A adjudication: FALSE ARM (stale tail-md5 baseline), no new sitting

The idle probe armed on "timeline CONTENT CHANGED: tail_md5 9054cc6c vs
baseline 25cca2cb". MEASURED, this session:

- live-timeline.jsonl size = 5,721,578,066 B — EQUALS the t193 re-frozen
  BASE_SIZE exactly (idle_probe.py:98), no bytes appended since t193's sitting.
- mtime_ns = 1793294532100000000 vs baseline 1793294532000000000 — a 100 ns
  delta: t193 froze the baseline from a SECOND-resolution `date`/stat view
  (idle_probe.py:97 comment "13:22:12"), losing the .1 ns fraction the actual
  stat carried. The file did not move; the baseline was imprecise.
- tail 64 KiB read directly (this session): contains exactly 3 rows, wall
  13:22:11..13:22:12, turn 1086 — i.e. the LAST ROWS OF THE SITTING t193
  ALREADY ADJUDICATED (docs/re/_wip_t193.md F1; watch.log tail identical).
- WHY tail md5 differs from BASE_TAIL_MD5: the t193 sitting appended
  18,846,978 B over the t192 edge state (5,702,731,088 -> 5,721,578,066), so
  the last 64 KiB is entirely new content; t193 re-froze size+mtime into
  idle_probe.py but NOT BASE_TAIL_MD5 (idle_probe.py:104 still the t151-era
  25cca2cb... — pre-append value). head md5 42a0bed0 unchanged as expected.
- No new playcap-* dir (newest = playcap-202614 stale, the known non-signal);
  no dosbox procs; caps/ empty; save/*.sav mtimes all inside the 12:30..13:22
  sitting window; RESUME.GAM/ascend.cfg mtime 13:20:46 (in-window);
  lsof on the timeline: nobody holds it open.

CONCLUSION: TRIGGER-A is a STALE-BASELINE false arm (A6-class: edge md5 IS the
enacted test, and it fired — but against a pre-append tail baseline, so it
re-arms every session until re-frozen). The named "dir to adjudicate" is the
shared playcap dir whose content t193 already adjudicated. No re-run of
r1_t85g_sitting / r1_t193_midgame_witness needed — they consumed this exact
save set 40 min ago. FIX: re-freeze BASE_TAIL_MD5 = 9054cc6c66802e6f80431d4ffa1416ee
and BASE_MTIME_NS = 1793294532100000000 (full ns, stat -c %y not date-sec).
Consequence for the OQ-019 clause in NEXT-leg (c): turn never advanced
remains true; nothing to falsify.

Proceeding with the ASSIGNED t194 static task.

## Leg (a) plan — walk the repaint chain, not the censuses
Targets named-but-never-decompiled: 0x28fc0 (star enumerate, score.md:43 —
stride-0x60 record loop bound DAT_00016143._2_2_), 0x284bc, the vtable call
[ESI+0xa7]+0xc after them, all three fired by the 'l'-cheat block 0x273ca
(debugflags.md table row 0x26: "LANE REVEAL ... then redraw CALL 0x28fc0 +
0x284bc + vtable [ESI+0xa7]+0xc"). If the repaint SKIPS drawing when the
viewer bit (rec+0x20 vs 1<<[0x7458e]) is clear => UI withholds => OQ-026
closes toward implement. If it draws unconditionally => bank negative.
Probes used so far: ~20.

## A1 — CONSUMER FOUND (first probe): FUN_00028fc0 IS THE COSMOS LIST BUILDER
## AND ITS LANE LOOP FILTERS ON rec+0x20 & <viewer mask>

Ghidra decompile FUN_00028fc0 (image 0x28fc0; restored program). The function
builds a fixed-capacity display list (param_1+0xb3 = list base ptr,
+0xb7 = count, +0xb9 = capacity, FUN_0002a428 = grow/overflow call, entry
stride 0x15, entry = {ptr, kind u8 at +4}). Three loops:

1. STARS: loop bound `DAT_00016143._2_2_` (nstar), entry ptr =
   `&LAB_00013bc5 + i*0x60` (the star-object array, STAR_BASE/stride match the
   t193 census), kind=2 only when `(&DAT_00013bda)[i*0x60] != 0` (star rec
   +0x15 nonzero) AND `FUN_00022304(star) > 0`; the `DAT_00010ba0 == -1`
   branch (nougat) is the fallback-name path.
2. LANES  <<== THE FILTER:
       if (0 < DAT_000177d3)            // nlanes
         do {
           if (((&DAT_00016167)[i*0x27] & DAT_00089324) != 0) {
              entry.ptr  = &PTR_DAT_00016147 + i*0x27;   // lane rec
              entry.kind = 1;
              count++;
           }
         } while (i < DAT_000177d3);
   &DAT_00016167 == lane pool base 0x16147 + 0x20 — EXACTLY the visibility
   byte t190/t193 measured (rec+0x20, per-empire bitmask, OR-written by
   0x463eb/0x46421 and the nougat 'l' cheat 0x273ca). THE LANE IS ONLY PUT IN
   THE COSMOS LIST IF ITS +0x20 BIT ANDS NONZERO WITH DAT_00089324. A lane the
   viewer cannot see is NOT DRAWN — no entry, so no icon, no click target.
   => the WITHHOLD path exists in the paint/list layer: OQ-026's affirmative
   branch is live. (Kind codes so far: star=2, lane=1.)
3. THIRD LIST (stride 0x162 records, 0x6b max, bound DAT_00043489._2_2_,
   filter `*(int*)(0x3a0e9+e*0x162)>>0x10 != -1` and byte 0x3a0ed==5) —
   different object pool (encounters/events?), kind=2. Not the lane path;
   not chased this iteration.

NEXT: what is DAT_00089324 — per-empire viewer mask or debug all-visible?
That decides whether the withhold is real in normal play.

## A2 — DAT_00089324 IS THE RUNTIME VIEWER MASK; FULL WRITER LAW CLOSED

- get_xrefs_to 0x89324: exactly 2 refs (total=2): READ 0x2914e (the FUN_00028fc0
  lane filter) and WRITE 0x21aa6 (FUN_00021a84). search_instructions "89324"
  over 98,819 instrs agrees verbatim: `MOV byte ptr [0x89324], DL` @0x21aa6;
  `MOV DL, byte ptr [0x89324]` @0x2914e. THE FILTER BYTE AND THE SETTER BYTE
  ARE THE SAME BYTE — no other reader/writer exists program-wide.
- FUN_00021a84(param_1) decompiled (sole writer):
      if (param_1 == 0xff) { DAT_00089324 = -1; param_1 = 0; }   // 0xff -> all-ones
      else                 { DAT_00089324 = 1 << (param_1 & 0x1f); }
      DAT_0007458e = param_1;                                     // the t193 X_CUR
  => SETTING THE VIEWER ALSO SETS X_CUR: the [0x7458e] byte t191/t193 keyed the
  cheat writes on IS the viewer-species index; mask == (idx==0xff? 0xff : 1<<idx).
  This EXPLAINS t192's weak witness "(c) paired mask byte == 1<<[0x7458e]
  20/20 (weak: idx==0 all saves)" — it's not a coincidence, it's the same setter.
- Callers of FUN_00021a84 (search "21a84", 2 sites):
  (i)  0x21408 inside FUN_00020fd4 = BOOT/BOOTSTRAP (alloc, mem check, nougat
       probe FUN_00077ece -> DAT_00010ba0 = -1, race-option loading loop) —
       sets the viewer at game start (arg from preceding call chain; Ghidra
       regparm loss — [unverified] which arg value at this site).
  (ii) 0x2754f inside the COSMOS MSG-HANDLER CASCADE (t191 region 0x26b34..
       0x27xxx). ASM CONTEXT (get_assembly_context):
         0x27525 MOV EAX,0xff ; 0x2752a JMP 0x2754f
         0x2752c MOV AL,[ESP+0x2c] ; SUB AL,2 ; MOV EDX,[0x13b96] ; SAR EDX,0x10
         0x27540 CMP EAX,EDX ; JGE 0x27554
         0x27548 SUB AL,2 ; AND EAX,0xff ; 0x2754f CALL 0x21a84
       — a DEBUG/species-toggle key path (bounds-checked against dword
       [0x13b96]>>16 ~ nraces, arg = [ESP+0x2c]-4 or 0xff). Adjacent code calls
       FUN_00028fc0 at 0x2758e right after (repaint), same shape as the 'l'
       cheat block t191 mapped at 0x273ca..0x273dd.

## A3 — FUN_00028fc0 CALLERS: ALL FIVE SITES ARE IN THE COSMOS CASCADE

search_instructions "0x00028fc0": 5 CALL sites 0x26f67, 0x273df, 0x27454,
0x2758e, 0x2771c — ALL inside the t191 cosmos msg-handler region (0x26b34
block; 0x273df is the repaint right after the 'l' lane-cheat OR at 0x273ca;
0x2758e right after the viewer-mask call above). The list builder runs ONLY
as part of cosmos-window repaint => the filter gates what the cosmos window
shows, always, in every repaint.

## A4 — FUN_000284bc IS THE PAINTER OVER THAT LIST; CONFIRMS THE SKIP

Decompile FUN_000284bc: walks entries (stride 0x15) of the list param_1+0xb3,
branches on entry kind byte (piVar11+4 i.e. entry+4):
  kind 0 = STAR: screen x/y/z written from star record (+5/+7/+0xd coords);
  kind 1 = LANE: reads BOTH endpoint stars via lane rec, writes line coords —
         the branch ONLY runs for entries the filter admitted;
  kind 2 = event/encounter record draw (3D segment math; or the
         DAT_00043504-selected encounter);
  else  = FUN_0002a438 (error).
Kind-0 star sprite pick: `4 + 2*popcount(star+0x14 & [param_1+0xd8])` over 7
bits (occupancy mask AND a per-window viewer byte at cosmos-obj+0xd8) —
star OWNERSHIP coloring is mask-driven, but the star entry itself is added
UNCONDITIONALLY by the builder (no +0x16 gate in the paint path).
=> WITHHOLD LAW (lanes): a lane is drawn in the cosmos window IFF
   lane.rec+0x20 & viewer_mask(0x89324) != 0. Fogged lanes produce NO entry,
   so no pixels and no hit-target. STARS: always listed (the builder's only
   extra filter is an encounter-record test FUN_00022304 that ADDS kind-2
   entries, never removes stars; star+0x16/+0x17 are NOT consumed here).
   OQ-026 answer = AFFIRMATIVE for lanes; star-mask UI consumption negative
   in this path (residue: star +0x16 consumers elsewhere / AI side).

## A5 — LIVE-RAM WITNESS ON THE OCT-29 MID-GAME SAVES (20/20)

Probe: find_base per save (same anchors/law as r1_t193), read runtime bytes
(mask lives in the RELOCATED-IMAGE segment at B+0x89324 — NOT B+D+X; my first
cut read B+X without D for X_CUR and hit code bytes `cd 31`, second cut used
B+D for the mask and got zeros; the correct split is MASK=B+0x89324,
X_CUR=B+D+0x7458e):

  20/20 saves: viewer_mask byte = 0x01, X_CUR = 0, law
  mask == (X_CUR==0xff ? 0xff : 1<<X_CUR) holds 20/20 (weak by construction
  at idx==0 — the offset identity rests on the static unique-xref pair A2,
  this witness only shows consistency).
  With mask=0x01 the FUN_00028fc0 filter admits 49 of 58 lanes: 9 lanes carry
  no player bit and WOULD BE WITHHELD — consistent with t193's bit-0 fog
  count of 9 (pool census per save /20: value 6 -> 9 lanes/save, the only
  bit-0-free value in {1,3,6,7,11,15}).
  nraces=4, nlane=58 sanity-match the t193 census.

INTERPRETATION: during the Oct-29 sitting, the runtime viewer mask sat at
race-0 (Chamachies = the human's empire) and 9 AI-explored lanes were being
dropped from the cosmos list on every repaint. The player never noticed
because they had never seen those lanes — absence of an unseen lane is
invisible by construction. AFFIRMATIVE withhold law stands.

## A6 — STAR-SIDE CONSUMER FOUND: FUN_00028e70 GATES LANE-FOLLOW ON star+0x16 & VIEWER

search_instructions "[eax + 0x16]" (13 hits program-wide): the only
cosmos-region hit is 0x28f3f/0x28ee7 in FUN_00028e70. Decompiled: it is the
cosmos CLICK/HOTKEY handler on a selected star-obj (param_1+0xbb):
  mode DAT_0007e582>>16 == 1: `if ((*(byte*)(star+0x17) & DAT_00006774) != 0)`
     -> DAT_00043504 = star (select it) + FUN_00056ad4 (paint).
  mode ... == 0xd: unconditional select (event-jump path).
  other: `if ((*(byte*)(star+0x16) & DAT_00006774) != 0)` then walk the
     star's lane list (star+0x42>>16 entries at star+0x2c), find the lane
     touching both this star and param_1+0x586 object, FUN_000221c4 +
     rebuild: FUN_00028fc0 + FUN_000284bc + vtable repaint.
=> STAR +0x16/+0x17 ARE UI-CONSUMED: an invisible star cannot be selected /
   its lanes cannot be followed (the handler returns without action). AND
   DAT_00006774 IS THE t192(c) "paired mask byte" (payload B+0x82bb0+0x6774,
   measured == 1<<[0x7458e] 20/20) — it is the DATA-SEGMENT twin of the
   viewer mask used by UI code, closing that t192 "weak witness" as the
   same law seen from a second segment. Stars are still always DRAWN
   (builder kind-0 unconditional); their mask gates INTERACTION.

## VERDICT (OQ-026, decision-bearing citation set)

LANES: withheld from cosmos draw iff (lane.rec+0x20 & viewer_mask)==0
  [filter @0x2914e in FUN_00028fc0; sole reader/writer pair of 0x89324;
   painter FUN_000284bc only iterates the filtered list; all 5 builder
   call-sites are cosmos repaints]. STARS: always drawn, interaction-gated
   by (star+0x16/+0x17 & viewer twin 0x6774) [@0x28f3f..0x28ee7].
  VIEWER SETTER LAW: FUN_00021a84(idx): mask=0x89324=(idx==0xff?0xff:1<<idx),
  DAT_0007458e=idx; called at boot 0x21408 (FUN_00020fd4) and from the
  debug species-toggle cascade 0x2754f. Cheat 'l'/'reveal' paths and the
  0x46354/0x46524 share ORs OR bits onto records; the UI filter reads them.
=> OQ-026 DECIDED AFFIRMATIVE (of the two ledger branches, (2a)): closure
   moves to rewrite-side IMPLEMENT + PIN (visibility layer; SA_KnowHomeWorlds
   / SA_KnowStarLanes then have real effects). Row stays OPEN until the
   rewrite models it (strict-close: rewrite surface is part of that row's
   evidence bar — "rewrite models NO visibility layer at all").


