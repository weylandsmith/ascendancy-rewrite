# t441 WIP — SEAMS T436-A (species-screen portrait COUNT law) + T436-B (owner->racering ring INDEX law)

OFFLINE-FIRST iteration per STATE.md t441. Cited inputs: r1-savestate.md "TWO SAVE
COORDINATE SYSTEMS" (M = B+0x82bb0), _wip_t295.md S4 (STATE = M+0x12e10, race rows
STATE+0x1ee*r, count word[STATE+0xd88]), t423-newgame-law.md S10 (byte +8 = colour
index), t415 F3 (byte +7 = specnum), t423c2 (racering k0 green / k1 purple / k2
gold / k6 orange / k7 neutral), _wip_t436.md F5/F7/F8 (the t252 capture datum).

## T1 [MEASURED probe 1] THE t252 SESSION SAVE IS IN THE FROZEN CORPUS
`work/r1/bank-t251-live1255/45.sav` — turn 1255 (the t252 sweep turn per
ui-runtime.md §6a), B=0x1bf4d8, n=word[STATE+0xd88]=4, T=50. Production watcher
name law (scripts/r1_playcap_watch.py:relation: name byte row+7 -> DS+0x74590 +
nb*0x14) gives EXACTLY the t252 campaign roster:

    row0 Chamachies  spec=19  colour byte +8 = 0  (green)   ships 22
    row1 Orfa        spec= 2  colour byte +8 = 1  (purple)  ships  7
    row2 Ungooma     spec=11  colour byte +8 = 6  (orange)  ships  6
    row3 Minions     spec= 0  colour byte +8 = 2  (gold)    ships  0

The t252 species capture shows rows Orfa / Ungooma / "Extinct" (_wip_t436.md F7),
and the t252 INTEL census listed no Minions row (diplomacy.md §3(e): Minions
zero-presence in the old campaign) => the Extinct row IS row3 Minions, ships=0.
So the capture's race set and their colour bytes are MEASURED, not hypothesised.

## T2 [MEASURED] T436-B CLOSED: portrait ring index == race-record byte +8
Image census (venv PIL, the t252 pair, left field x<466): the species screen's
repaint over the cosmos is EXACTLY FOUR 109x109 blobs (diff >24, flood-fill):
centres (404,238) (234,407) (235,68) (64,239) — matching t436's four ring centres
within 3 px. Sampling the r50..55 band at each centre, BASELINE vs SPECIES:

    centre (235,68)  BASELINE 90% pure black | SPECIES (0,85,41)+(0,113,57) = racering k0 GREEN
    centre (64,239)  BASELINE 90% black      | SPECIES (99,52,107)+(132,69,140) = k1 PURPLE
    centre (404,238) BASELINE 90% black      | SPECIES (198,146,33)+(57,40,16) = k2 GOLD
    centre (234,407) BASELINE 90% black      | SPECIES (156,73,0)+(115,48,0) = k6 ORANGE

The four hues are exactly the four races' colour bytes {0,1,2,6} — a bijection.
DECISIVE DISCRIMINATOR (the case STATE.md asked for, "owners where species !=
owner%7"): row2 Ungooma has OWNER INDEX 2 but COLOUR BYTE 6.
  - T436-B hypothesis (index = owner%7) predicts Ungooma's ring = k2 = GOLD.
  - colour-byte law predicts k6 = ORANGE.
Gold (k2) is already occupied at a DIFFERENT centre by row3 Minions (colour 2,
ships 0), and the hues are all distinct (t423c2 distinctness law) — so Ungooma
cannot be gold: its ring is ORANGE. **INDEX = RACE-RECORD BYTE +8.** The port's
`racering k<owner%7>` (docs/re/ui-runtime.md:676) is WRONG for every race whose
colour byte differs from its row index — here 2 of 4 (Ungooma 6!=2, Minions 2!=3).
SECOND WITNESS, ring-independent: t436 F7 measured the ROW NAME/FLAG INK as Orfa
purple / Ungooma orange == the same byte +8 values (1, 6). Byte +8 is the
display-colour source at both the row-ink site and the portrait-ring site, exactly
as FUN_000232ec writes it.

## T3 [MEASURED, CORRECTION to t295] STAR RECORD BASE IS STATE+0xd8d, NOT +0xdb5
row+0xd home pointers (45.sav): 0x256525 / 0x2565e5 / 0x256285 / 0x255c85. The
stride-0x60 NAME run t295 found at STATE+0xdb5 starts at (homeptr)+0x28, so the
RECORD BASE t295 used is 0x28 ABOVE the pointer the code stores. Measured layout
relative to the stored pointer P:
    P+0x2c  dword sequential star index 0..T-1   (verified 0,1,...,49 across all
            50 records — self-describing, no pointer arithmetic needed)
    P+0x30 / P+0x34  float map x / map y
    P+0x3c  byte bit7 marker | (1<<race)   [t295's "entry+0x14"]
    P+0x3e / P+0x3f  per-star bitsets      [t295's "entry+0x17"]
    P+0x44  20 B star name                 [t295's "entry+0x1c"]
  => star record base = STATE + 0xd8d + 0x60*j. t295's DRAW LAW (uniform
rejection sampling, distinct-by-construction) is unaffected; only the address
arithmetic in its S4 was wrong. Any consumer adding t295's disp8 offsets to
STATE+0xdb5 reads fields 0x28 late. scripts/t441_race_table_census.py implements
the corrected base and decodes 50/50 star records.

## T4 [MEASURED] THE FOUR PORTRAITS ARE NOT AT THE RACE HOME STARS
row+0xd homeptr -> star index/name/float map coords (45.sav):
    Chamachies -> #24 Menthol    (30.3, -421.9)   player, ships 22
    Orfa       -> #26 Barataria  (-244.3, 214.7)
    Ungooma    -> #17 Binomer    (362.4, -234.4)
    Minions    -> #1  Ephemera   (376.9, -226.9)  ships 0 (eliminated)
The four species-screen blob centres are (235,68) (64,239) (404,238) (234,407) —
a symmetric plus/cross pattern about roughly (234,238): two blobs share y~238
(x 64 and 404), two share x~235 (y 68 and 407). Race home stars do NOT form that
pattern in any plausible projection: Orfa's home Barataria (y=+214.7) and Ungooma's
home Binomer (y=-234.4) have OPPOSITE-sign map y, yet both their rings sit at the
SAME screen y (238). A continuous monotone map cannot put +215 and -234 at the same
screen row while also placing Menthol at y=68 and Ephemera at y=407. => the ring
centres are SCREEN-SLOT positions of a fixed four-slot layout, NOT projections of
homeStarFor(owner). t436's "portraits are centred on the AI species HOME STARS"
(resting on "the baseline carries a star marker under each") is REFUTED: the
baseline band at all four centres is 90% pure black; there is no star marker there.
Consequence for T436-A: the COUNT cannot be a home-world/visibility law at all —
the screen paints a fixed 4-slot ring layout, and the question becomes which races
fill which slot (and what happens when n>4).

## T6 [MEASURED] THE LAYOUT IS A FIXED FOUR-SLOT CARDINAL SQUARE; THE PLAYER HAS A
## PORTRAIT; SLOT k = RACE ROW k AT ANGLE 90+90k; t436's STAR-MARKER EVIDENCE IS VOID
Slot geometry (venv PIL, baseline + both t252 species captures — species2_game.png
and species_menu_game.png give IDENTICAL blob sets, n=9416/9338/9320/8479 px):
    mean centre (234.2, 238.0)  [kCosmosWnd{7,7,465,472} centre = (236,239)]
    top (235,68)    r=170.0 angle= 89.7
    left (64,239)   r=170.3 angle=180.3
    right (404,238) r=169.8 angle=  0.0
    bottom (234,407) r=169.0 angle=269.9
A perfect r=170 circle at the four cardinals about the cosmos centre. No projection
of four random home stars does that (and T4's y-sign contradiction stands). The
repaint census finds NO fifth blob >=200 px in either capture.

MEASURED TRIPLES (race row -> colour byte -> ring slot):
    row0 Chamachies (PLAYER) colour 0 -> TOP    (89.7)
    row1 Orfa                colour 1 -> LEFT  (180.3)
    row2 Ungooma             colour 6 -> BOTTOM(269.9)
    row3 Minions             colour 2 -> RIGHT (  0.0)
=> SLOT INDEX = RACE ROW INDEX, angle = (90 + 90*k) degrees, r = 170, measured
   89.7/180.3/269.9/0.0 — monotone counterclockwise from top, EXACT. [SINGLE
   CAMPAIGN: n=4 fits both "90+90k" and "90+(360/n)k"; the r=170 radius and the
   row->slot identity are one-sample too. Pin the geometry as measured, name the
   n-generalisation.]
   (An earlier draft of this section claimed "slot order == ascending colour
   index" — WRONG: sorting the colours {0,1,2,6} onto (top,left,right,bottom) was
   fitting the slot order to the answer. Row order is the monotone one.)
=> **THE PLAYER DOES GET A PORTRAIT** (row0 = player, TOP slot), by construction
   of the row->slot law. t436's "the player home star carries NO portrait" came
   from putting the player home at screen (129,410) (the biggest white blob) and
   finding no ring there; the player's ring is at the TOP slot. The port's
   "player home carries NO portrait [measured F8]" comment (ui.cpp:1266) and
   speciesmenu.h's SEAM T436-A text are both WRONG.

t436's supporting evidence "the baseline carries a star marker under each
portrait centre" is REFUTED directly: white-marker blobs (r,g,b>200) in the
baseline left field number SEVEN total — (76,118) (107,393) (121,268) (129,410)
(315,57) (337,349) (411,249) — and the distance from each ring slot centre to the
nearest one is top 80.8 px, left 64.0, right 13.0, bottom 105.0. t436's test was
"brightest px WITHIN 12 px"; the true-slot distances are 64-105 for three of four
slots. The r50..55 band at every slot is 90% pure black in the baseline and
coloured in the species capture: the rings are ADDED by the species screen, over
empty space. (Random-point within-12px base rate 1.6% — the test was fine, the
t436 measurement of "carries a marker" was wrong.)

COUNT LAW (T436-A): the species screen paints ONE RING PER RACE TABLE ROW
(word[STATE+0xd88] = 4 in this campaign) at slot k = row k — player included,
contact/elimination state IRRELEVANT (Minions is eliminated, ships=0, and still
gets a ring at RIGHT, while the ROWS list prints "Extinct" for it: rows and rings
use DIFFERENT filters). The port's current law (one portrait per KNOWN AI owner,
projected at projectStar(homeStarFor(o)), player excluded) is wrong on COUNT
source, POSITION, and FILTER, and wrong on COLOUR INDEX via owner%7 (T2).

## T5 [OPEN] WHAT T441 DID NOT SETTLE (t441 session exit state)
- n>4 CAMPAIGNS: word[STATE+0xd88] ranges 3..7 in the corpus (t273 tutorial n=3,
  production n=4, new-game max 7), but the ONLY species-screen captures in the
  tree are the t252 4-row campaign. The port ships angle 90+360/n (keeps 7 rows
  distinct; fixed-90 overlaps rows 4..6 on 0..2) — NAMED, mutation-pinned as the
  unmeasured tail. t442's static hunt for the painter function settles it.
- THE 5TH DIFF BLOB (60 px at (337,349), pure black, 9x14): too small for a ring;
  likely a text/icon repaint. Not a portrait.
- row+0x1c0 relation bytes read 0 for all pairs in 45.sav while the t287 'c'
  overlay showed live relations — the relation matrix field law used here
  (watcher row+0x1c0+j) needs re-checking against a save the watcher logged; NOT
  load-bearing for T2/T3/T4. Flagged, not re-derived.
