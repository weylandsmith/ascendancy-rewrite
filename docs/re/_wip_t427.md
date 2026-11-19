# t427 — PLANETS LIST SCREEN CYCLE (D17) — working log

Target screen: STATUS rail PLANETS LIST = STATE 10, STATUSWND TYPE 16
(7,7-632,472 SHAPEFRAME 0) child STATPLANLST TYPE 10 ln1035 (7,46-632,472
SHAPEFRAME 7). NOT the PLANETALLOC PLANLIST (ln1503, state 17, t406
territory). Authority: docs/re/_wip_t417.md F1-F10 (chrome/geometry shipped
t417b), docs/re/planets-ui.md S8 (t402 row-string cluster), docs/re/_wip_t405.md
(hit-map, arrows).

## F1 [measured 2026-11-19, work/r331_disasm.txt verbatim] — ROW-PAINT
FUNCTION 0x504d0 (enclosing fn 0x500e0+0x1002 per functions_full.tsv; the
t402 "cluster 0x50647..0x5091f" is the STRING tail of THIS function).
Entry regs (regparm-ish): EAX -> [esp+0xb0] = widget ptr; ECX->EDI = mode
flag; EDX->EBP = row param ptr.

### Record bank law (same bank as cosmos stars, planets-ui S2)
0x504e4  edx = [ebp+0xa] SAR 0x10          ; row dword HIGH word = bank idx
0x504f1  esi = 0x13bc5 + idx*0x60          ; stride-0x60 runtime record
0x504fd  slot = WORD ds:0x8957e            ; big-art lib slot global

### BLIT #1 BIG ART (0x50525..0x5053a)
FUN_0x1fc34(cache 0x9f10c, slot=[0x8957e]) -> payload; on NULL vendor logs
0x41@0x85634 (error-string law). Then FUN_0x5caac(desc+4, payload,
SELECTOR=u32 [esi+0x0], x=75, y=75). SELECTOR = the runtime record's +0
dword — the SAME K law as the map star pips (planets-ui S3) but WITHOUT the
4*K+cls banding and WITHOUT the +0xd view-class term: raw K, fixed (75,75)
inside the row.

### BLIT #2 SMALL ART (0x50565..0x50592)
slot = WORD ds:0x69d0 (second lib-slot global).
SELECTOR = 5*[ebp+0x16] + [ebp+0x14]  (words: +0x16 = TYPE, +0x14 = SIZE —
the same words the row STRING reads via word tables #46-56/#41-45).
Domain: type 0..10 x size 0..4 -> 0..54 (55 selectors). x=0xc8=200, y=75.
=> PLANET ART SELECTION LAW: small sphere per row = 5*terrainType + sizeIdx
from lib slot [0x69d0]. This is the "planets.shp record selection per row"
the D17 row asked for.

### OWNER GATE + BLIT #3 FLAG (0x505f1..0x50647)
0x505f6 cl = BYTE ds:0x7458e (current species); eax = 1<<species.
0x505fe edi = BYTE [esi+0x14] (row record owner-MASK byte — NB different
offset meaning vs the row param's +0x14 word; esi is the 0x60-stride record).
   gate: if edi == eax (record's owner mask == exactly this species bit)
         -> PAINT FLAG.
   else: per-species table walk: edx=species; eax = edx*32-edx=31*edx;
         eax = eax*8-edx = 247*edx; then cmp esi, [eax*2+0x12e1d] — i.e.
         per-species 494-byte block at 0x12e18, +5 = a dword POINTER; if it
         == esi -> test edi & (1<<species) (je skip) -> PAINT FLAG.
   FLAG PAINT = FUN_0x53dd8(ebx=10=x, edx=4=y, ecx=species) at 0x50642,
   then falls through into the 0x50647 string tail.
=> MARKER LAW: the thing at row x10,y4 is the SPECIES FLAG via FUN_0x53dd8
   (same family as raceflag k<specnum>, t426 plaque law). The RED capsule
   t417b shipped (x16..69) is NOT this call — see F2 for what paints the red
   selection capsule (still open).

### Year-tint leg (0x505cd..0x505e6)
cmp DWORD ds:0x484ec, 0x96 (150): if <150 -> [esp+0xa8]=0xf3 else
[esp+0xb4]=0xf3. [esp+0xa8]/[esp+0xb4] are set from a per-record byte at
0x505a9: al = BYTE[247*species*2 + 0x12e18], *4+0x13 — a per-species table
value (0x13 base, step 4). Semantics of 0xa8/0xb4 locals = [unverified]
(text colour? row tint?). Named seam.

## Open sub-items after F1
- Which lib files back slots [0x8957e] (big) and [0x69d0] (small)? Slot
  WRITER census next (grep disasm for writes to those globals).
- FUN_0x53dd8 = flag draw? decompile/census.
- Red selection capsule painter still unnamed.
- Ghidra headless UP (pid 1087023) but 0 open programs — import needed if
  decompile required; banked disasm work/r331_disasm.txt covers 0x500e0 fn.

## F2 [measured 2026-11-19] — LIB IDENTIFICATION (live-save cache dir)
scripts layer r1_slot (60.sav, B=0x1bf4d8): cache 0x9f10c dir count 150 at
+0x7d0 stride 0x32, names verbatim: SLOT 29 = data\planets.shp, SLOT 52 =
data\suns.shp, slot 32 = data\raceflag.shp. FUN_0x1fe20 = name->slot-index
resolver (walks dir, FUN_0x775aa case-insensitive strcmp, returns index or
0xffff; FUN_0x1f95c load leg when ebx==-1 and not found).
- INIT 0x51911..0x51953: slot [0x69d0] := resolve("data\\planets.shp")
  (edx=0x2ad8, reloc'd string; cache 0x9f10c). => SMALL ROW ART =
  planets.shp, selector 5*type+size (F1). D17 "planets.shp record
  selection per row" LAW CLOSED at the disasm level.
- INIT 0x51954..0x51996: resolve("DATA\\suns.shp") (string CITED VERBATIM
  at file 0x856a7) BUT the store is `mov ds:0x69ce,ax` — 0x69ce, NOT
  0x8957e. Byte-level full-binary scan: [0x8957e] has EXACTLY two refs in
  the whole image (0x50500 read, 0x51956 read) and ZERO writers; [0x69d0]
  one writer (0x51931); [0x69ce] one writer (0x51974).
  VENDOR BUG CANDIDATE [inferred from verbatim bytes]: the init intended
  [0x8957e] := suns slot but wrote 0x69ce; live save 60.sav reads
  [0x8957e]=0x0000, [0x69d0]=0xffff, [0x69ce]=0xffff (60.sav is a
  title-menu slot per the trust law -> statics may be stale; re-measure on
  an IN-GAME slot).
- If [0x8957e]==0 in-game: row blit #1 draws cache slot 0 = SMRACE19.SHP
  selector [esi+0] — implausible for the observed sun-like sphere; if the
  intended value (suns.shp slot) holds, selector raw-K star type indexes
  suns.shp = system SUN art. RESOLVE by in-game slot read next.
- [esi] = 0x13bc5 + 0x60*([ebp+0xa]>>16) = THE COSMOS STAR RECORD
  (planets-ui S2 stride/base cited) — confirms row param = star index.

## F3 [measured 2026-11-19] — INIT FN = STATUS WINDOW CONSTRUCTOR
functions_full.tsv: the slot-init block 0x51911..0x51996 lives in fn
0x51834..0x51f4c (the state-10 status window ctor; also sets [win+0x8c9]=0x8d
and edx=0x3b920 blit law at 0x518d4). So [0x69d0]/[0x69ce] resolve only once
the status screen is opened.
LIVE MEASUREMENT (scripts inline over all 20 IN-GAME playcap slots, t=1254):
[0x8957e]=0x0000 20/20, [0x69d0]=0xffff 20/20, [0x69ce]=0xffff 20/20 -> the
corpus NEVER opened the status screen (consistent: playcap drove the map).
So the statics are STALE, not evidence of the in-screen values. [0x8957e] has
EXACTLY 2 refs in the whole image (both READS) -> no direct writer exists; any
writer must be computed-address or overlay-side. NAMED SEAM T427-A:
"what value does [0x8957e] hold while the status screen is open".
Cache dir from 60.sav (count 150): slot 0 DATA\SMRACE19.SHP, 29 planets.shp,
32 raceflag.shp, 52 suns.shp. suns.shp COUNT=13 == the 13 starstat.txt star
types (mapgen S1) and blit #1 selector = raw star-type dword [esi+0] ->
STRONG [inferred] identity: big row art = suns.shp[K] (the system's SUN).
smrace19.shp is 1 record/16 B -> selector K>0 returns the -1 missing-dims
error = draws NOTHING, so "slot 0 = SMRACE19" is refuted by the vendor
capture's visible big sphere (t417 F5 x60..140 y67..175).
FLAG LAW REFINED (0x53dd8 = FUN_0x53dd8 -> FUN_0x53e58): payload =
FUN_0x1fc34(0x9f10c, WORD ds:0x6fd84) = slot 32 = data\raceflag.shp (MEASURED
[0x6fd84]=32 in 60.sav); record = 4*species+0x13+... per 0x53e81..0x53e93
ramp: ebx = BYTE[247*species*2 + 0x12e17] (race row +0x1 = colour byte,
aicode.md 664 law) then dl = -i + (ebx+0x13) per i=0..4 -> writes 5 bytes
into ds:0x7d37e palette ramp (a SHADED FLAG: 5 luminance steps of the race
colour), then blits [esp+0x16]>>16 selector. => the vendor marker at
row (10,4) is a PALETTE-RAMP-SHADED raceflag, NOT flat red: this is the
t417b seam "marker FACE is flat (255,0,0) vs vendor red gradient" — ROOT
CAUSE FOUND (0x53e81..0x53ea5 palette ramp generator).

## F4 [verified 2026-11-19] — RAMP GENERATOR + CALLER LOOP (verbatim)
0x53e58 tail (0x53e97..0x53ece): loop i=0..4: ecx=0x13-i; dl written at
ds:0x7d37e+ecx = raceByte - i (dec dl each iter). i.e. PALETTE WINDOW
indices 15..19 := raceByte, raceByte-1, -2, -3, -4. Then call 0x5cf77
(palette update, arg = ds:0x7d37e) then FUN_0x5cf96(edi=x, ebp=y,
payload, [esp+0x16]>>16 selector, blit). => FLAG FACE LAW: raceflag
record indices 15..19 (the t426 census idx15/19 family) are REMAPPED per
species to the race's palette colour + its 4 darker neighbours — the
vendor flag is SHADED by 5 palette steps. The palette window base is
ds:0x7d37e. raceByte = BYTE[0x12e17 + 247*species] (race row +0x1;
aicode.md 664 stride law).
CALLER LAW 0x4fb30..0x4fb89 (fn calling 0x500e0 at 0x4fb59): iterates
[eax+0x376]>>16 ROWS; per row: esi=[row+0x358]; skip if 0x689ee(esi)==4;
push 0, push ([esi+0xe]>>16), push esi, call 0x685e0 = row-surface rect
lookup => row-local coords: blit #1 (75,75), small art (200,75), flag
(10,4) are ROW-SURFACE coords (t417b pitch 141 maps them to screen).

## F5 [measured 2026-11-19] — t417b RED CAPSULE REFUTED; VENDOR ROW ANATOMY
(t3 capture /tmp/t417_t3_game640.png, red-dominant census + native vision on
/t427_row0.png (2x crop y46..198)):
- ROW 0 anatomy L->R: (1) GREEN raceflag rect x~10..30 y~57..82 (flag law
  F4, race palette ramp — the player species here is green); (2) BIG RED-
  ORANGE SUN art spanning x~16..175 y~59..184 (measured red-dominant bbox
  row0 x16..544 incl. pop dots; the sphere itself x16..~145); (3) blue
  planet sphere x~175..250; (4) green SYSTEM name "Oslo" above the sun
  right edge x~250; (5) small moon/asteroid x~255..275; (6) planet name
  "Oslo II (Large Cathedral Planet)" x~288+; (7) line2 "Building Research
  Campus - 2 days until completion"; (8) THREE thumbnail rects x~297..445
  (surface/structure art); (9) pop-dot block x~495..544 (RED dots);
  (10) scrollbar + arrow box right.
- THE t417b "red selection capsule x16..69 y+2..26" WAS THE SUN ART's
  upper-left arc. Rows 1/2 (unselected, t3 same shot) have ZERO red px
  below x185 (row1 red n=1302 min x185; row2 n=823 min x358) -> NO capsule
  on unselected rows either; row 0 (selected) capsule = sun. REFUTED with
  the row-2 control. Port must DELETE the flat (255,0,0) capsule.
- suns.shp RECORD DIMS (unified law V/A/B, verified this session):
  k0 61x68, k1 62x63, k2 63x63, k3 68x70, k4 55x55, k5 54x54, k6 55x54,
  k7 54x54, k8 53x52, k9 45x46, k10 38x37, k11 40x43, k12 37x37.
  13 records = 13 starstat types. MEASURED drawn sun ~130x126 ~= 2x k1 —
  SCALE LAW OPEN (T427-B): either a 2x draw path (flag used FUN_0x5cf96,
  NOT 0x5caac — 0x5cf96 may be the scaled/tonal variant) or the row
  surface is composited 2x. planets.shp dims ladder k0..k4 =
  11/18/25/35/47 (size axis) repeated per type group (k05.. = 11/18/25...)
  — MEASURED blue sphere ~75px > max 47: SAME 2x-family question.

## F6 [measured 2026-11-19] — DRAW-TIME DIMS CONFIRMED = u16 pair rec+0
(t330 mouse-only law now corroborated on suns.shp/planets.shp by ROW-WALK:
suns k1..k12 u16(+0,+2)=(149,149) -> 150x150; row-walk consumes the record
span EXACTLY (i-end 0x0 for k1/k5/k12 at H=150 rows); planets k1..k54
(99,99) -> 100x100 exact-span at H=100. k0 virtual slot = u32 pair law V
(suns 61x68, planets 11x11, exact walk). The +0x10 u32 pair I first read
(62x63 etc.) is NOT draw dims — row-walk with H=63 DESYNCS. => the port's
ShapeLibrary must use the rec+0 [H-1][W-1] u16 pair for these libs.
MEASURED DRAW EXTENTS (t3): sun warm art x16..145 y59..184 (bbox INSIDE
the 150x150 frame — transparent margin); blue planet x174..259 y66..155
(inside 100x100); green raceflag x12..26 y57..81 (14x24 at ~(10,4)+2).
Blit (x,y) semantics: row-surface coords; flag (10,4) top-left fits
measured +2; sun/planet (75,75)/(200,75) fit as RECORD CENTRE (sun centre
measured (80.5,121.5) vs 57+75=132; +-11px — row-surface origin offset
[unverified], port will centre at measured screen rects).
DOT GRID (pop pips): x498..544 pitch 5 (10 cols), row bands y107..124
pitch 5 (4 rows visible row0) = row-relative y+50..+67 — the port's
single 10-band strip at x428 is WRONG COLUMN + wrong shape (grid, not
strip). NOTE t417b F5 called x428..481 "thumbnails" — the 3 thumbnail
runs MEASURED now are x288..342, 358..412 (+ third ~428..481): pitch 70,
w~54.
SELECTION LAW [measured, decisive]: line1 text colour WHITE (255,255,255)
on row 0 (selected) vs GREEN (0,170,82) on rows 1/2 — NO capsule, NO
marker rect. THE t417b red flat capsule is REFUTED (it was fitted to the
sun art's upper-left arc; rows 1/2 red-pixel control below x185 = ZERO).

## F7 — PORT PLAN (decided this iteration; anchors cited to MEASURED rects,
## row-surface origin offset = NAMED SEAM T427-C — blit (75,75)/(200,75)
## do not map cleanly to screen for the ART calls (flag (10,4) top-left fits
## within +2; art fits as CENTRE anchor +-7px on row 0; per-row masks are
## noisy (system-name cyan + moon contaminate). Do NOT invent a law; blit
## at measured centres and cite.
1. formats/shp.cpp: DIMS FALLBACK — if the current u32 law's row-walk
   fails, try u16 pair rec+0 ([H-1,W-1], t330 law, now corroborated by
   EXACT-SPAN walk on suns k1/k5/k12 @150 rows and planets k1/k4/k9 @100
   rows). Pure fallback: zero change where current law walks OK.
2. ui.cpp status rows: DELETE red capsule (F6 refutation); selection law =
   line1 WHITE (255,255,255) vs GREEN (0,170,82) (F6 measured 522/551/375
   px). Add suns.shp to the chrome libs; blit suns[star.type] centred at
   row-top + (80,64); blit raceflagLib[species] top-left (10, rowtop+4)
   (flag law F4; palette-ramp tint = seam); planets.shp record 5*type+size
   centred at row-top + (208,53) [measured blue bbox y66..155 x174..245].
   Pop pips: 10x4 DOT GRID pitch 5 at x498, y=rowtop+50 (F6), replacing
   the single strip.
3. Pins test_statusrow_t427.cpp: dims fallback (suns k1 = 150x150 walk),
   selection colour law, dot-grid geometry, membership of sun selector
   domain 0..12. Mutation x3. Witness: Xvfb shot + census (row0 line1
   white>200px, rows1/2 green, sun warm px x16..145 >500, flag green
   present, NO flat (255,0,0) capsule block, pip grid cols 498..544).

## F8 [LANDED 2026-11-19] — implementation + suite
- statuslist.h: pure kStatusArtScale=2 / sun-planet-flag anchors /
  kStatusLine1Sel white / kStatusLine1Norm green / statusPipAt 10x4 grid
  (all cited to F1-F6 above).
- ui.cpp: kLibFiles 7->8 (suns.shp joins; libFor loop 7->8); status row
  painter = sun blitShapeScaled(suns[s.type]) centre (80,y+64) 2x;
  raceflag blit (12,y) every owned row; planets 5*type+size scaled centre
  (215,y+53) 2x; line1 colour law white/green; pip grid via statusPipAt;
  RED CAPSULE DELETED (F6 refutation).
- PINS test_statusrow_t427.cpp x5 (suns 13-rec domain + k0 61x68 + all
  content dims <=70 [the 150x150 u16 header pair must NOT leak]; planets
  55-rec ladder 11..47 group restart + decode k24; selection colours
  distinct white/green; pip grid 498/107..543/122 + capacity 40; anchors
  + scale + rows-top/pitch). SUITE 442/0/0 (437+5).
- NOT RUN THIS ITERATION (budget): Xvfb witness + mutation campaign +
  full gate before compaction notice — NEXT SESSION OWNS them (see
  STATE NEXT ACTION). kStatusMarkerRect constant RETAINED in statusbg.h
  (t417b pin still checks it) though the painter no longer uses it —
  re-scope or retire with the witness next session.

## F9 [t427b, measured 2026-11-19] — WITNESS PASS on our own render
scripts/t427_statusrow_witness.sh (Xvfb :97, seed 5 --species 0; RESUME ->
STATUS rail -> shot; row-0 click -> Escape -> shot) +
scripts/t427_witness_census.py VERDICT PASS 14/14 on /tmp/t427_shots/:
open row0 line1 GREEN g=413 w=0; sel row0 WHITE w=413 g=0 (the colour IS
the marker — same-row control, stronger than two rows in one frame); rows
1/2 never WHITE; NO flat (255,0,0) capsule px on any row (n255=0 x3); sun
warm px x16..145 n=6512; raceflag px x12..26 n=336 (needs --species 0:
default playerSpecies=-1 paints nothing — fixture law, not a port bug);
pip dots start x498 exactly, dot-start pitch 5/5/5/5/5, 2px dots; old
x428..481 strip zone n=0; planet art px x150..245 n=976.
FIXTURE NOTE: seed 5 owns ONE planet ("1 Planet Occupied") — rows 1/2 are
empty; GREEN/WHITE control is the same row across the two shots.
CAPSULE RETIREMENT (t427b step 4): kStatusMarkerRect DELETED from
statusbg.h; test_statusbg_marker_and_wells_t417b re-scoped to
statusbg_wells_t417b (arrow-well navy half kept, capsule half deleted,
citing F6). Suite 442/0/0 after re-scope; GATE_EXIT=0; LEDGER AUDIT OK.
