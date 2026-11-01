# WIP t254 — POPULATION-SLOT LIBRARY + PLANITEM RULING (2026-11-01)

Harness: no live-game dependency for the render legs; live :9 session used ONLY
for the planet-screen panel comparison (DISPLAY=:9, xsend, `import -window
root`). Pre-sweep hazard check RUN and CLEAN this session:
`DISPLAY=:9 xwininfo -root -tree | grep -i warning` printed NOTHING (exit 1);
dosbox-x PID 479968 (etime 03:04 at check time), ring turn 1255.

## S1. Static dims census CORRECTED (this session) [verified]
First pass read u16 pairs and printed nonsense (e.g. planets k1 "99,99 / 18,0").
The law (scripts/r1_shp_unifiedlaw.py header + rec_state) is a u32 PAIR at
rec (k==0) / rec+0x10 (k>=1). Re-measured with the correct slots:

  planets.shp   n=55  V1+A54  dims uniq 13: (11,11)(12,11)(18,18)(19,18)
                        (25,25)(25,26)(26,25)(34,34)(35,34)(35,35)(47,46)
                        (47,47)(48,47)
                ORDER LAW [verified from the seq]: 11 consecutive groups of
                5 = the SIZE LADDER 11,18,25,35,47 (x5 biomes), i.e.
                k = 5*size + biome. NO record smaller than 11x11.
  planitem.shp  n=40  V1+A39  dims uniq 9, dominant 33x33 (k0..k7 measured
                        all 33x33); smallest class (24,23)/(34,18).
  planal00..10  n=5   V1+A4   dims 47x47, 75x74, 103x103, 140x140, 189x189
                        — IDENTICAL dim ladder in all 11 libs (size ladder,
                        not pose set; consistent with the t196 vision kill:
                        "these are surface textures").
  planres/planpro n=21 all 107x99; planind n=21 all 107x99 (13 X-class).
  listbox 24x24/14x14, bullet04 10x11/9x9, 14intel 18x18/28x28/5x6/6x6.

CONSEQUENCE FOR THE POP-SLOT QUESTION [inferred from verified dims]:
the PLPOP paint (planets-ui.md S4, 0x3ce39..0x3cef8) advances EDI += 0x0a per
slot and EBP += 0x0a per row (TEN slots/row, 10 px pitch). A library whose
SMALLEST record is 11x11 (planets.shp) or 33x33 (planitem.shp) or 47x47
(planalNN) cannot be the slot-icon art drawn on a 10 px pitch — the icons
would overlap every neighbour. Corpus-wide search for libs with >=3 records
of W<=10,H<=11 returns EXACTLY: 14intel(3), 17np(6), bullet04(4), cos_ship(28),
cos_star(43), mouse(6), sg32bull(4), sg45bull(4), shipicon(6). The pop-slot
library (global [0x6fd9c]) is therefore one of THOSE (or an unlisted lib), and
the t254 candidate list (planets/planalNN/planitem) is structurally EXCLUDED
by geometry. [verified measurement; the exclusion inference is stated as such]

## S2. gwshare.txt load-list fact [verified]
extracted/ascend00/gwshare.txt lines 33-37 list data\planets.shp, then
data\planitem.shp, restree, raceflag, racering, smhome, shipicon, listbox,
help, planres/planind/planpro, 14intel, smraces. So shipicon.shp and
listbox.shp ARE on the galaxy load list (pop icons must be resident to paint
the planet screen) — consistent with S1's exclusion set.

## S3. planitem ruling inputs
- t244 agent observation (selfplay.md S3): planet screen PLBUILD panel showed
  "Automation / 2 days until completion" + item art, "confirming planitem.shp
  = current-project item art hypothesis".
- t196 vision (shp.md S20): planitem.shp = DISTINCT item/project icons
  (factory, crystal spire, military base, domes), NOT animation frames.
- Structural: 40 recs vs the 39-row OQ-014 item table; 33x33 dominant.
  RULING LEGS THIS SESSION: (a) per-record id table for all 40 planitem recs
  rendered on the corrected palette; (b) the 10px-pitch geometry law above
  KILLS any "planitem = population slot icon" reading; (c) current-project
  panel art identity stays a player/vision identification, NOT self-graded
  (R13).

## S4. Live planet-screen comparison (log)
(see S5/S6 — live leg executed after the RAM closure)

## S5. POP-SLOT LIBRARY IDENTIFIED — 17np.shp [MEASURED, live-RAM bank-t251-live1255/41.sav]
Cited chain (strict-close grade):
1. PAINT LAW (planets-ui.md S4, 0x3ce39..0x3cef8): PLPOP draws the slot grid
   with `slot idx = u16[DAT 0x6fd9c]; cache 0x9f10c; FUN_0001fc34 -> blit
   FUN_0005caac`, selector SEL(i)=1+..+2 bands (1 busy / 2 free / 3 empty).
2. LIVE RAM (bank-t251-live1255/41.sav, turn 1255, B=0x1bf4d8, pointer law):
   u16[0x6fd9c] = 44. Adjacent array u16[0x6fd90..0x6fd9a] = 38,39,40,41,42,43
   (the planet-window library index globals; gauge trio + ship/list/help
   neighbours per gwshare order).
3. CACHE RESOLUTION (t68 law: slot PAY -> +0x88 verbatim 1.10 copy):
   slot 44 PAY=0x435400, copy at +0x88 magic 1.10, size+head match
   extracted/ascend01/data/17np.shp EXACTLY. Control: slot 41 -> 14intel.shp
   (same method), and gwshare.txt line 42 = 14intel, line 45 = 17np =>
   slot index == gwshare line number - 1 (45 entries, indices 0..44; 17np is
   the LAST boot-loaded library). Both controls agree [verified].
4. RECORD-LEVEL ID (vision-oracle, t193 law, 16x zoom of the rewrite's own
   renders): 17np k1 9x9 = SIDEWAYS-facing humanoid, red/pink body, holding a
   blue tool = BUSY pop icon; k2 7x9 = FRONT-facing yellow/gold figure =
   FREE pop icon; k3 8x8 = hollow GREEN ring = EMPTY-slot circle. k6/k7/k8 =
   2x2 red/yellow/green dots (mini legend markers). This matches the player's
   S19 testimony law EXACTLY (yellow-front free, reddish-sideways busy, empty
   circles) — the pose/colour law arrives corroborated record-for-record.
   Selector mapping: SEL 1 -> k1 (busy), SEL 2 -> k2 (free), SEL 3 -> k3
   (empty): record index == selector value (k0 = 639x479 panel frame, not a
   slot icon).
5. GEOMETRY CONSISTENCY [verified]: k1..k3 dims 9x9/7x9/8x8 all fit the
   0x0a (10 px) pitch law; the t254 assignment's candidates are EXCLUDED by
   dims (planets min 11x11, planitem min 24x23 class, planalNN min 47x47).
Consequence: the population-slot icon set is DONE; gwshare.txt:45 is the load
citation; "library identity STILL OPEN" (planets-ui.md S4, shp.md S22) is
SUPERSEDED by this measurement.

## S6. Live planet-screen leg (mechanics log)
- hazard check clean (xwininfo grep warning -> nothing); baseline shot
  work/r1/screens/t254/00_baseline.png.

## S7. Live leg results + honest negatives
- STATUS (553,145) -> planet LIST ("Chamachies (102 Planets Occupied, 36
  Systems Controlled)" — matches systems_any@1255 per t246 header law);
  row-2 click (200,105) -> Vega IV detail (Scientist Takeover project).
- PLPOP pixel census (10x10 cells, colour classes): rows 0-2 all 10 cells =
  busy-class signature (skin 239,130,99 + red 189,36,57); row 3: 6 busy +
  cells (7,3),(8,3) yellow-dominant (255,207,24 + 255,134,8) = FREE icons
  k2, cell (9,3) pure background = never painted. => used=37, pop=39 band
  shape (no EMPTY-ring band on this maxed planet — consistent: cap==pop).
  EMPTY k3 identity rests on the vision ID + selector table, not this planet.
- Escape on PLANETALLOC: screen unchanged (vision-verified) — modal law.
- DAT_43508 = 0x26f3e5; u16 at +0x42/+0x4a/+0x4c all ZERO in 3 live ring savs
  -> the pointer needs a different interpretation (handle? segment-relative?)
  or the fields live elsewhere mid-game. HONEST NEGATIVE; t198 law untouched.
