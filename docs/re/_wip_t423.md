# t423 — NEW GAME SCREEN CYCLE (working log)

Task: PHASE-16 row t423. Seed defects (D17 verbatim in STATE.md:1896-1909):
(a) wheel icons repeat across steps; (b) hostile-atmosphere variant missing;
(c) extra art drawn below the circles; (d) species + planet art STILL 4x;
(e) species rings need THICK TEXTURED lines; (f) preview starfield fills the
VOLUME not a shell, stars LARGER + pixelated; (g) Begin New Game BUTTON spins
the starfield too. Law: derive from RE first (D17 law 2), no synthetic
stand-ins (law 1), iterate to clean (law 3), close only if the final grade has
no fixable defect (law 4).

## F0 — windows.txt state-3 table (census, verbatim lines)
[verified] extracted/ascend00/windows.txt
- L575-577  TYPE 100 STATENUMBER 3 SHAPEFILE DATA\3CFGNEW.SHP (lib header)
- L579-594  TYPE 18 NAME NEWGAMEWND PARENT NONE STATE "1 3"
            rect 334,12-488,364 SHAPEFRAME 0 HELPINDEX ngwnd WINITEMS 0
- L596-613  TYPE 0  GALAXY_MORE     PARENT NEWGAMEWND STATE "1 3" MOUSEFOCUS 1
            rect 7,381-122,472 SHAPEFRAME -1 SENDMESSAGE 501
            WINITEMS 2: SHAPEITEM 1 data\3cfgnew.shp 0 0 0 ; TEXTITEM 0 Star^Density 2 0 10
- L615-629  TYPE 0  PLAYERS_MORE    PARENT NEWGAMEWND STATE "1 3" MOUSEFOCUS 1
            rect 131,381-246,472 SHAPEFRAME -1 SENDMESSAGE 503
            WINITEMS 2: SHAPEITEM 1 data\3cfgnew.shp 0 0 0 ; TEXTITEM 0 Species 2 0 10
- L634-651  TYPE 0  DIFFICULTYMORE  PARENT NEWGAMEWND STATE "1 3" MOUSEFOCUS 1
            rect 255,381-370,472 SHAPEFRAME -1 SENDMESSAGE 505
            WINITEMS 2: SHAPEITEM 1 data\3cfgnew.shp 0 0 0 ; TEXTITEM 0 Atmosphere 2 0 10
- L654-668  TYPE 0  Player^Color    PARENT NONE STATE "1 3" MOUSEFOCUS 0
            rect 379,381-493,419 SHAPEFRAME -1 SENDMESSAGE 0 WINITEMS 0
- L670-684  TYPE 10 RACELIST        PARENT NEWGAMEWND STATE "1 3" MOUSEFOCUS 0
            rect 502,45-632,372 SHAPEFRAME 7 SENDMESSAGE 0
=> beginnew.txt is the TUTORIAL script (help infoNN pages), NOT the
   TEXTITEM/SHAPEFRAME table the queue row guessed. The real table is
   windows.txt state 3 (above). [verified] beginnew.txt read in full: 196
   lines, 9 tutorial pages, every button "msg 0". The queue's premise about
   beginnew.txt naming the per-state record is FALSE; the per-state record
   selector must come from the msg 501/503/505 handlers (F1).


## F1 — WHEEL LAW CLOSED [verified verbatim, capstone base-0 restored image]
State-3 message dispatcher 0x528eb (ebp=window mgr; msg id in dx). Entry
0x52903 copies the 5-dword table @0x895c8 to esp+0: values
{15,25,50,75,100} = the STAR COUNTS (matches the t78/OQ-012 ladder).
Dispatch chain 0x5290d..0x52f54:
- msg 501 GALAXY_MORE  -> 0x52db9 (density)
- msg 503 PLAYERS_MORE -> 0x52e58 (species)   [via 0x52f49 je]
- msg 505 DIFFICULTYMORE -> 0x52eec (atmosphere)
- msg 0x1c01 (7169)    -> 0x52d6c (RACELIST select: [mgr+0xb1] race idx)
- default 0x52945 -> FUN_000336b4 (generic handler; t-banked: zero DAT stores)
Counter fields on the mgr: +0xb5 hi-word = density idx, +0xb7 hi = species
val, +0xb9 hi = atmosphere val (u16 inc via `inc word ptr [eax+..]`).

DENSITY (0x52db9): inc +0xb5; if idx==5 -> 0 (mod-5 cycle, 5 steps — no
repeat possible in the vendor). Record select:
  edx = dword[esp + idx*4 - 2] sar 16  (the count's HIGH WORD: 15/25 -> 0,
  50/75/100 -> 0 too since all < 65536 => ALWAYS 0?? NO — `mov edx,[esp+edx*4-2]`
  loads the DWORD count then `sar edx,0x10` takes the high word = 0 for every
  entry; the value actually stored into the child comes from FUN_000226e4's
  return path below. READ CAREFULLY: after the call chain,
  0x52e2b: child = [[ebp+0x67]] (first child of table 0x7a360 entry),
  [child+0x72] = edx sar 16 where edx = [mgr+0xb5] => FRAME = density IDX
  (0..4). So the DENSITY WHEEL = 3cfgnew k(densityIdx), cycle 0..4.
  [the esp-table read feeds FUN_000226e4 (star-count-driven preview regen),
   NOT the frame byte.]
SPECIES (0x52e58): inc +0xb7; if val==8 -> 3 (cycle 3..7 species COUNT;
  0x52e68 cmp 8 / 0x52e6d mov word +0xb7,3). FUN_00022ce4(0x12e10, race?,
  count). Frame store 0x52eba: child = [[ebp+0x67]+4] (second child),
  [child+0x72] = (val sar 16) + 2  => FRAME = k(2 + (count-3)) = k(2+v) with
  v = 0..4 over counts 3..7. FIRST PAINT at screen open uses val's INITIAL
  table value ([0x89600] runtime; static file byte -1).
ATMOSPHERE (0x52eec): inc +0xb9; if val==3 -> 0 (cycle 0..2). Frame store
  0x52f17: child = [[ebp+0x67]+8] (third child), [child+0x72] = val + 0xa
  => FRAME = k10/k11/k12 (Peaceful/Neutral/Hostile).
SHAPEITEM parse law: child+0x72 (runtime frame idx) REPLACES the file's
SHAPEFRAME/SHAPEITEM frame at paint time => the per-state record is a RUNTIME
FIELD, which is why the windows.txt table shows k0 for all three wheels.
RACE PALETTE: 0x52a26 call FUN_000232ec(0x12e10, playerColorIdx) — decompile
shows it stores the color idx at [mgr+8] then fills the race-slot array
(stride 0x1ee, [mgr+8..]) with rand()%7 DISTINCT-ADJACENT values via the
Borland LCG 0x7824f. Player-color panel rect 379,381-493,419 WINITEMS 0 =>
its six icon row is CODE-DRAWN from that array (t401 S3 vision: six vertical
rects = raceflag class shapes; the array picks which species colours).
BUTTON-HOLD LAW (defect g): 0x52993 / 0x529c1 call FUN_00056ad4(0x7a35c, 5,
0x69b8|0x69c4) when the cursor is INSIDE 387,420-493,476 (cmp ebx 0x17b/0x1ed
ecx 0x1a4/0x1d8 — the BEGIN-button zone below/right of the color panel).
FUN_00056ad4 = timer/arm (decompile pending F2).


## F2 — mouse msgs + player-color law [verified disasm 0x52f59..0x52f92]
Dispatcher lower chain: msg 2/4/5/6 -> 0x529d2; msg 0xc -> 0x52962; msg
0/1 -> default. 0x529d2 (button-down family): if cursor INSIDE x(379,493)
y(420,472) — the player-colour CHIP zone (t414 measured chips rows
434..459): FUN_0004fb30(0x78638,0); chip idx = (x-0x17b)>>4 (16-px chips
from x=379); store word [win+0xb5] = idx; FUN_000232ec(0x12e10, idx) ->
reassign race colours; invalidate ([win+0xa7] vtable +0xc call dword).
else fall through 0x529a4 FUN_00052678 (cursor hit-test) -> default.
FUN_00056ad4 = TIMER/SCRIPT ARM [verified decompile]: writes a 10-byte
script slot at [obj+0x422c + slot*10] (type word param_2, param_3 ptr),
increments script count [obj+0x44ac]. Scripts @0x69b8/@0x69c4 are packed
opcodes (op 2 = SET ds:imm32 — sets ds:0x7458e (specnum global); op 0x0e/
0x1b terminators UNDECODED — NAMED, not needed for the wheel/spin rows).
=> BEGIN BUTTON: windows.txt state-3 census = NO record (t401 negative
   RE-CONFIRMED F0: the six records are NEWGAMEWND/GALAXY_MORE/PLAYERS_
   MORE/DIFFICULTYMORE/Player^Color/RACELIST). The Begin box is NOT a
   window-table object; its click route rides the default handler chain.
   "spin while button held" therefore CANNOT come from SENDMESSAGE —
   honest negative on the table half; the spin must live in the state-3
   cosmos repaint path (F4).

CONSEQUENCES vs port (audit in F3): (1) density frames k0..k4 by IDX — the
t414 "ladder-rank" mapping is right ONLY if ladder rank == idx; the vendor
cycles the idx directly, count table {15,25,50,75,100} is the density->N law;
(2) species frame k(2+v) over counts 3..7 — matches t401 anchor k7@Five ONLY
if v = count-3 (v=2+2=4? k(2+2)=k4 NOT k7 — RE-DERIVE: [0x89600] static -1;
runtime val at first paint unknown. The ADDEND is +2 to the CYCLING COUNT?
0x52ec9 `add edx,2` where edx = val sar 16 and val cycles 3..7 => frames
k5..k9! Anchors: count 3 -> k5, Five -> k7 — EXACTLY the t401 S8 measurement
(Five = k7 class) and t401 S5 montage (k5=3 icons, k7=4 icons — MORE icons
at higher counts: k7 at Five has 4 icons... count 5 -> k7 shows 4 AI + self?
icons = AI species count 4 at Five: CONSISTENT);
(3) atmosphere k10/11/12 CONFIRMED as the vendor law incl. k12 Hostile — the
k12 record is EOF-truncated (t401) so the port's blank refusal is a DECODE
problem, not a law problem; (4) the vendor draws EXACTLY ONE record per wheel
(child+0x72), never well+overlay stacked => "extra art below the circles" =
the port stacking SHAPEITEM k0 + frame record.

## F4 — PREVIEW STARFIELD PLACEMENT LAW CLOSED [verified decompile FUN_00022728]
Density click -> 0x52dfe call FUN_000226e4(0x12e10,...) = REGENERATE:
FUN_000226e4 { [mgr+4]=0; DAT_00006a2c=0x20; FUN_00022878; FUN_00022728;
FUN_000234a4; FUN_00022ce4 }. FUN_00022728: per star i in 0..N-1 (records
stride 0xd at DAT_0003067e, z at +0xd law matches cosmos node+0xd t399):
  xz-plane point: radius 300.0 (0x43960000), angle = rand() % [rec+0x1c]
  (seed word) -> FUN_0005324c (the t416 WORLD-Y per-vector rotation: x/z
  mix) -> x,y = rotated; z = (rand() % 600 - 300) ADDED to rotated z.
=> VENDOR LAW: stars sit on a CIRCLE of radius 300 in the XY plane, each
   displaced along Z by UNIFORM(-300,+300): a FILLED CYLINDER VOLUME, not a
   shell. This is exactly the user D17 complaint "fills the VOLUME not a
   shell" — the port maps onto a SPHERE SHELL; the vendor fills depth
   uniformly. 300 radius + z +-300 IS the volume; projection = cosmos
   pinhole law (t399 FUN_00053374).
  RNG: Borland LCG 0x7824f (R-t422c banked) — the preview IS a rand()
  consumer. R-t422c "no paint path consumes rand()" stays TRUE for
  CHROME; this is the newgame REGENERATE path (on click, not per-frame
  paint), not walked there. NOT a contradiction: banked distinction.
  STAR SPRITE: COSMOSWnd STAR_SHAPES DATA\COS_STAR.SHP (windows.txt F0
  verbatim field). COS_STAR dims census pending F5 (OQ-005 unreadable).

## F3 — port audit vs F1/F4 (title.cpp RaceConfig)
- wheel frames: port newgameWheelFrame() maps density by LADDER RANK
  (value->rank) — vendor = plain idx 0..4 with the count table
  {15,25,50,75,100} AT IDX (0x895c8). Port ladder is {50,75,100,15,25}
  => port shows k0@50, vendor shows k0@15. THE REPEAT DEFECT root cause =
  rank mapping collision, not a vendor share. FIX: frame = idx directly;
  cycle order = idx 0..4 (counts 15,25,50,75,100).
- species: F1 store `add edx,2` on VAL cycling 3..7 => frames k5..k9;
  t401 S8 measured Five->k7 class [verified consistent: 5+2=7]. Port maps
  k(2+n) n=0..4 => k2..k6 — OFF BY THREE. FIX k(count+2).
- atmosphere: vendor k10/11/12 [verified] == port mapping; the HOSTILE gap
  = k12 record decode (EOF-truncated; t401 JUNK-CERTAIN). Row (b) = a
  DECODE repair not a law change: check the 3cfgnew.tmp sibling for the
  intact tail (F5).
- extra art below circles: vendor paints ONLY the [child+0x72] frame
  record — never a k0 well underlay. Port stacks SHAPEITEM k0 + frame
  (t401 S10 blit law). FIX: drop the k0 underlay.
- preview: port splitmix sphere SHELL N=count; vendor = LCG circle r=300
  + uniform z +-300 (F4). FIX law + sprite size (F5).
- player colour: vendor chip zone x379..493 y420..472, 16-px chips, click
  REASSIGNS race colours via FUN_000232ec (race-slot array stride 0x1ee,
  rand()%7 distinct-adjacent). Port paints static chips only (t414).



## F5 — sibling/tmp census + cos_star sprite law [verified, scripts/t423_f5_sibling.py + t423_f5b_decode.py]
- 3cfgnew.tmp is NOT an intact .shp sibling: magic "1.10" (0x312e3130),
  count=1 tsz=16, ONE record dims pair (479,639) unsigned = 639x479 SWAPPED
  (S16 residual class) = a FULL-SCREEN screen-state temp (640x480 minus
  border). Every shp lib with a .tmp sibling (10status, 13negot, 16battle,
  1starmap, 20res, 7racesel, 8shipdes) likely holds that screen's saved
  state => VENDOR GROUND-TRUTH SCREENSHOTS for grading (F6).
- 3cfgnew.shp k0..k12 census (correct offsets: dims k0 at 0x10+tsz, k>0 at
  rec+0x10; stream k0 at rec+8, k>0 at rec+0x18): 13 records, dims
  k0-k10 84x79, k5-k9 84x80, k11 88x79, k12 84x79. Header intact for k12.
- Row-walk WITH directory-span bound: EVERY record runs slack=0 (streams
  are exactly span-sized; walk stops mid-row ~55 at the next start) — the
  t197 X-class span-crossing behaviour, consistent with shp.cpp:180-187
  ("3cfgnew k0..k11" named in the no-span-bound comment).
- k12 (Hostile) hits TRUE EOF mid-row at 0x6ad5 = file end: the LAST
  record's stream is missing ~24 rows of bytes IN THE EXTRACTED FILE.
  k0..k11 recover by crossing spans; k12 has nothing past EOF. OPEN: is
  the truncation an extraction artifact (check source archive) or does the
  vendor file itself end there (then vendor k12 paints heap-garbage rows
  and the user's "hostile variant missing" = the vendor's own truncation,
  which the user would have seen as working — LESS LIKELY: user graded
  the vendor screen as HAVING the hostile art).
- cos_star.shp 55 records: k1..k15 2x2, k16..k39 1x1, k40..k51 zero-header
  (banked vendor-cannot-draw set, REFUTED-ROUTES L1329), k52 3x6, k53 8x8,
  k54 8x8 — the LARGER star sprites D17(f) wants. k0 header odd (w=2 h=2
  but stream overlaps k1; decode OOB at row 0). Sprite-size law pending:
  which k does the newgame preview use? (F4 regeneration path stores star
  records stride 0xd — frame idx likely a field there.)
## F5b — shipped-archive proof + bbox census [verified]
- k12 truncation is IN THE SHIPPED ARCHIVE: ascend01.cob entry
  data\3cfgnew.shp blob size=27349 md5 b2550068bb6260f8980d5de65d680db4 ==
  extracted twin; blob == [off_i, off_i+1) monotone table (cob.offsets OK,
  n=328). NOT an extraction artifact. The vendor file itself ends mid-k12
  row-stream => vendor paints k12 rows 0..~54 (the glyph rows) then
  desync/garbage rows exactly like the port's no-span model (t197). So the
  port's BLANK k12 refusal is a PORT bug (walkRows false-on-EOF), not a
  data gap: partial-decode-and-paint is the vendor behaviour.
- Record header rec+0x08 = SIGNED bbox (L,T,R,B) [verified 3cfgnew k1..k12
  + cos_star k1..k39,k52..k54 all sane]: 3cfgnew wheels bbox=(30,25,84,79)
  => GLYPH IS 55x55 at (30,25) inside the 84x79 canvas (k11 (27,25,88,79)
  62x55); stream rows ~= bbox height (walk stops ~55). cos_star: k1..k15
  2x2 px bbox(-2,-2,2,2); k16..k39 1x1 bbox(-1,-1,1,1); k52 3x6; k53/k54
  8x8 px bbox(-8,-8,8,8) 17x17 GLOW box — the LARGER star sprites D17(f).
  k40..k51 zero-header (banked cannot-draw). NOTE: canonical dims read at
  rec+0x10 == bbox (R,B) pair — t367 gate already knows slot overlap;
  banked live-measured decode model (H rows, span-cross, t197) STANDS.
## F6 — 3cfgnew.tmp is a SPARSE CHROME LAYER, not a screenshot [verified, scripts/t423_f6_tmpscreen.py]
- k0-law decode (W=639 H=479, stream rec+0x08) walks OK 479/479 rows, but
  only 30223 px (10%) non-transparent: row bands rows 0..47 + 368..479
  dense, middle rows ~21 px each; col bands x<64 and x>=448 dense. = the
  screen's saved CHROME FRAME/margin layer (texture bands + borders), NOT
  full-screen ground truth. No wheel/starfield content. Grading use:
  frame extents only. (tmp head dims (479,639) = swapped pair, S16 class.)

## F3-CORRECTION (this session, reading the REAL port code) [verified title.cpp/menulaw.cpp]
- newgameWheelFrame case 1 returns 2+value with value=speciesSetting 3..7
  => k5..k9 EXACTLY the vendor k(count+2) law. The WIP F3 "OFF BY THREE"
  was a MISREAD (it assumed n=0..4). No species fix needed.
- Density: vendor frame=idx over table {15,25,50,75,100} @0x895c8 (F1);
  port frame = RANK of the count in the SORTED ladder = same set, same
  bijection count->k0..k4 (50->k2, 75->k3, 100->k4, 15->k0, 25->k1). The
  t78 live cycle order 50,75,100,15,25 == vendor idx ring +phase 2 (a ring
  is order-invariant under rotation: Vacuous->Sparse->Avg->Dense->V.Dense
  wraps to the same ring t78 measured). Mapping EQUIVALENT; the pre-t414
  "k0,k1,k2,k2,k3" REPEAT is already fixed by t414's bijection. Residual
  D17 "repeats" witness therefore either predates t414 or is about the
  k0..k4 dot-wells being VISUALLY similar at panel scale — the vendor
  shows the same five records (law-identical), so the port cannot differ
  while the law holds: named seam, NOT a law defect.
- k12 hostile (defect b): CONFIRMED PORT bug — shipped-blob truncation
  (F5b) means vendor paints rows 0..~54 (bbox H=55 = the orb glyph) then
  desync/heap-garbage rows; port's walkRows false-on-EOF refuses the
  WHOLE record => blank panel. FIX: partial paint (rows decoded before EOF
  painted, below-EOF left transparent = named seam vs vendor garbage).
- Extra art below circles (defect c): port blits the full 84x79 record
  clipped to the panel; k0..k11 desync rows paint next-record bytes
  (t197 law) — same as the vendor's resident-bytes behaviour. With k12
  partial-painted the port matches the vendor model for all 13 records.
## F7 — spin pump + galaxy gen + sprite selector [verified decompile/xrefs]
- ds:0x7458e xrefs: 43 total, ZERO writes inside the state-3 dispatcher
  (sole WRITE = FUN_00021a84); DATA refs at 0x30f0/0x6a64 (the script
  operands @0x69b8: `02 8e4507 00 | 07 003b0e` = op2 SET ds:0x7458e, op7
  imm 0x3b). The button-hold arm (F2) queues that script; the cosmos
  repaint READS 0x7458e per star (FUN_00053fe8 chain). => spin law for the
  PORT: pump previewYaw whenever cursor inside the Begin zone
  (387..493 x 420..476 measured F2), ON TOP of the idle spin. No SEND-
  MESSAGE exists on the Begin box (windows.txt F0 negative re-confirmed).
- FUN_00022ce4 (species click regen, 0x22ce4): race-slot assignment loop
  picks stars via rand()%starCount (LCG FUN_0007824f), marks owner bits
  (1<<slot) on star+0x14/+0x17 + colonised planets; difficulty byte
  [mgr+0xdb4]: 0 = nerf starting stats (-30,-20 x6,+30), 2 = buff (+20s,
  +30,-20). NOT the preview paint path.
- STAR-PIP SPRITE LAW (t200 banked, planets-ui.md SS6): SEL = 4*type + cls,
  cls = 4-band ladder on v=round(z' + f32@ds:0x105e): >=220 -> 0, 1..219 ->
  1, -220..0 -> 2, < -220 -> 3. cos_star census (F5): types 0..3 land on
  2x2 records, types 4..9 on 1x1, types 10..12 on the zero-header k40..k51
  = vendor draws NOTHING for those. k52..k54 (3x6, 8x8x2) unaddressable by
  SEL (banked t399). => PREVIEW SPRITE LAW for the port: blit cos_star
  k(4*type+cls), skip zero-header classes; nearest-neighbour 2x = the
  user's "LARGER + pixelated".
## F8 — FUN_00022728 re-read (decompiler noise resolved) + racering [verified]
- The stride-0xd preview records DAT_0003067e: {float x,y,z} + a leading
  char index byte at DAT_0003067d (the 0x67d/0x67e overlap is the index
  byte, NOT a dims pair). Per star: vector (·,1000.0f,300.0f,0) rotated by
  FUN_0005324c at angle (rand%seedword + cum - prev); z += rand%600 - 300.
  The WIP F4 summary (circle r300 XY + uniform z ±300 = VOLUME) stands as
  the port law; the per-star seedword chain (seed[i+1]=cum) is decompiler
  artefact-adjacent — named seam on the exact angle distribution, NOT on
  the volume shape (both F4 readings agree on r300/z±300).
- Preview records carry NO type byte => the cosmos SEL=4*type+cls law
  (planets-ui §6) uses a different site for the state-3 preview; the port
  fixes K=0 (cls-only) and maps cls0->k1 (k0 header overlap fails the
  walk, F5) — NAMED SEAM, honest.
- racering.shp: 8 records, k0 53x53 (bbox zero), k1..k7 53x53
  bbox(-55,-55,53,53) — the portrait-ring RECORD for defect (e) (t401
  already cites racering k0 53x53). Port currently draws 1px vector rings;
  FIX: blit racering k0 native-size at both ring sites (desc + list),
  vector fallback only if the lib fails to load.
## F9 — regenerate chain consumers + port edits [verified decompile; edits applied]
- FUN_000234a4 (chain step 3) = galaxy GRAPH post-processing (planet/owner
  tables, FUN_00024018/0002446c) — NOT a preview paint site. Chain:
  FUN_00022878 full galaxy gen (N=100 candidates via LCG: type class from
  the 13-entry weight table DAT_000063aa, coords uniform(-500,500)^3 x
  scale) -> FUN_00022728 PREVIEW table (stride 0xd, circle r300 + z
  uniform +-300) -> FUN_000234a4 graph -> FUN_00022ce4 race assignment.
  The state-3 preview paint site is COSMOSWnd (STATE "4 1 3 7") reading
  display nodes; the stride-0xd preview records carry NO type byte —
  K=0 in SEL=4*K+cls is the honest reading (NAMED SEAM, port applies it).
- PORT EDITS (this session): (1) shp.cpp/h + test_shp.cpp: last-record
  PARTIAL walk (k12 hostile orb paints rows 0..~54, defect b); (2)
  title.cpp preview = circle r300 x depth 1000+-300 VOLUME (defect f
  placement) + cos_star sprites k(cls) at scale 2 pixelated (defect f
  sprite) + hover spin pump zone 387..493x420..476 x6 (defect g, F7);
  (3) racering.shp k0 record at both ring sites (defect e). Defect d
  (4x scale): vendor scale law NOT yet derived — the measured original
  portrait zone 96..109 px == 2x smrace (t401 S8); kept at measured 2x,
  row stays OPEN for the TYPE 10 list-handler decompile.
## F10 — witnesses [verified runs]
- scripts/t412_newgame_shot.sh rerun post-edits: /tmp/t412_shots/t412-newgame.png
  native-vision: starfield = SPREAD POINTS FILLING THE RECTANGLE (depth
  variety, 2px sprites), three wheel panels DISTINCT art, race portraits
  inside GREEN TEXTURED RINGS (racering record), no garbage.
- scripts/t423_hostile_shot.sh (new): one Atmosphere click -> summary
  "Hostile Atmosphere", panel shows the RED SPIKED ORB ART (k12 partial
  rows 0..~54 = the orb glyph; nothing below = the named seam, vendor
  paints heap there). Pre-fix this panel was BLANK. app.log: "click
  DIFFICULTYMORE msg 505 -> Hostile".
- BUILD+TESTS: cmake build clean; run_tests 421/0/0 (test_shp k12 pin
  FLIPPED from reject to partial-paint WITH the law change; content
  witness rows 25..50 nonzero).
