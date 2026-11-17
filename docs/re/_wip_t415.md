# t415 WIP — RACE INTRO FRAMING + ART

## F1 — LGRACE/SMRACE string sites located [verified, payload scan]
Pool base 0x82BB0 (t412 law). Full-string pool offsets:
  DATA\SMRACE%02d.SHP = 0x83704 (pool 0xB54)
  DATA\LGRACE%02d.SHP = 0x83718 (pool 0xB68)
  DATA\SMSHIP%02d.SHP = 0x8372C (pool 0xB7C)
Immediate-push sites (PUSH imm32 `68 <off> 00 00`), exactly ONE each:
  0x233d6 SMRACE / 0x233ff LGRACE / 0x23427 SMSHIP — inside the shape
  loader cluster at ~0x23388 (matches datafiles.md §2 "one loader at
  0x23388"). So LGRACE = the LARGE race portrait lib, SMRACE = small.
  (t401 S2 banked lgraceNN 296x199 large portrait.)

## F2 — FUN_0002b48a render tail, verbatim immediates [verified, Ghidra 7.0]
Three text/box calls (FUN_0002fb38) with rect structs built on stack; the
field roles ARE resolvable from FUN_0002fb38's own body (it reads
struct+0x0c/+0x10 as box origin, +0x14/+0x18 as extent, stores wrap y at
+0xf3), so t412's "do NOT read them as rects" was too conservative:
  * call#1 rect  x0=7   y0=261(0x105) x1=632(0x278) y1=465(0x1d1)  -> BODY
    (the 1000-B acStack_624 buffer; bottom band)
  * call#2 rect  x0=312(0x138) y0=46(0x2e) x1=632(0x278) y1=245(0xf5)
    -> RIGHT PANEL, 320 x 199 px
  * call#3 rect  x0=7   y0=7   x1=632(0x278) y1=37(0x25)  -> HEADER
    (the "%s: " POWER line; ink = racebyte*4+0x13)
  Window setup: FUN_0005caac(&DAT_0004850c, FUN_0001fc34(0,7,0x2e));
  a FUN_00053dd8 (window-draw helper -> FUN_00053e58) sits between call#2
  and call#3 with rect (7,7,632,37).
KEY: right-panel height 199 == LGRACE record height EXACTLY (t401 banked
lgrace00 296x199) and width 320 = 296 + 2*12 margin. HYPOTHESIS: call#2's
rect is the LGRACE portrait well. Still: no shape blit inside FUN_0002b48a
(t412 verified) — the portrait must be drawn by the window/shape layer.

## F3 — SMRACE/LGRACE per-race preload law [verified, Ghidra FUN_00023388]
FUN_00023388(param_1 = game state): loops i < *(short*)(state+0xd88)
(the race count), stride 0x1ee (the diplo/race table stride), reads the
race byte at state+7+i*0x1ee, and registers FOUR shape libs per race via
FUN_00076c79 (sprintf) + FUN_0001fa60 (add-to-load-table):
  DATA\SMRACE%02d.SHP (pool 0xb54), DATA\LGRACE%02d.SHP (0xb68),
  DATA\SMSHIP%02d.SHP (0xb7c), DATA\DKSHIP%02d.SHP (0xb90)
FUN_0001fa60 law: filename -> table slot at param_1+2000+idx*0x32,
max 200 slots, errors if len>31 or count>199. So EVERY race's LGRACE
portrait is resident from boot — the intro can blit it without a load.
Race byte = state+0x1ee*i+7 (same stride as the ink table 0x12e18 law).

## F4 — VENDOR INTRO SCREEN WITNESS + LGRACE IDENTITY [measured]
scratchpad/species-introduction-original.png (1041x780 = 640x480 x 1.6266;
untracked provenance = user-supplied vendor screenshot; native-vision
graded). Decoded lgrace00.shp k0 (296x199, game.pal 6-bit) IS the portrait
in that screenshot (mechanical Minion figure, identical composition).
Frame census (PIL bright-run scan, game px):
  outer frame  x~2..636 y~2..477; header frame bottom y 39..41;
  upper-band bottom frame y 247..250; bottom frame y 475..478;
  VERTICAL SEPARATOR x 304..307 (present in BOTH the y232..244 and
  y44..60 strips -> a real frame line, not art).
  => LEFT WELL ~ (7,46)..(305,245) = 299 x 200; right well (312,46)..(632,245)
     = 321 x 200 (the Ghidra call#2 rect); body well (7,261)..(632,465)
     (Ghidra call#1 rect); header (7,7)..(632,37) (Ghidra call#3 rect).
  LEFT WELL 299x200 vs lgrace 296x199: 3px slack -> template-match below.
  Header: small square emblem at left (~x14..44,y10..35) + centred
  "<Power>: <Title>" in race ink (green for Minions).
  Backgrounds inside all wells = the cosmos hash-noise texture (t414 law),
  NOT flat black.

## F5 — FULL INTRO LAYOUT LAW [measured off user screenshot + Ghidra rects agree]
Section->well mapping (decompile + screenshot content both agree):
  HEADER rect (7,7)-(632,37): raceflag k<specnum> NATIVE 14x24 at (9,10)
    (measured emblem bbox x9.4..24.1 y10.1..34.7; t401 banked raceflag =
    the bordered emblem class) + text "<Name>: <POWER>" in RACE INK,
    CENTRED (measured text x232..406, centre 319.4 == 320).
  RIGHT WELL (312,46)-(632,245) [Ghidra call#2 rect EXACT]: INTRO block,
    WHITE (measured brightest 255,255,255; Ghidra colour immediate 0xf3 ==
    243 -> game.pal[243] = (252,252,252) [verified]).
  BODY WELL (7,261)-(632,465) [Ghidra call#1 rect EXACT]: TEXT block +
    atmosphere-gated section appended (verified concat target acStack_624),
    RACE INK (measured (56,170,85) ~= pal[19] (0,168,80) for Minions).
  PORTRAIT: lgrace<specnum> k0 NATIVE 296x199 at (7,46) — template match
    MSE 73 at game origin (6.8,46.1) vs frame-interior (7,46); native
    scale (no scaling). lgrace lives in ascend02/data (extracted).
  FRAME (measured bright runs): outer rect (2,2)-(636,477), header
    divider y39..41, upper-band bottom divider y247..250, vertical sep
    x304..307 TOP BAND ONLY (present at y44..60 and y232..244). Frame
    colour (125,182,182) ~= game.pal[62] (124,180,180) [verified].
  Line pitch 13 [measured rows 56/69/82/95 and 271/284/298/310]; lines
    CENTRED per well (right line1 centre 473 vs well centre 472; body
    centre 315 vs 319.5). Vendor small-font advance ~5.5-5.8 px/char.
  Background = the chrome-page noise texture full-screen (t414 law); no
    black well fill (wells show the speckle in the screenshot).
  FUN_00053dd8 sits between the right-well and header text calls = the
    emblem/window-shape draw (-> FUN_00053e58); identity = raceflag by
    size+position match (14x24 native at the measured bbox).
## F6 — PORT CHANGE PLAN
  IntroPanel gains introWell (INTRO paras) + textWell (TEXT+gated paras);
  `paragraphs` KEPT (t412 pins). runRaceIntro signature + raceName param
  (title.cpp passes speciesNameAt(beginSpecies)); renderer = chrome page +
  frame law + portrait + emblem + centred wrapped text per well; lgrace
  loaded from extracted/ascend02/data/lgrace%02d.shp (refuse-once law).

## F7 — IMPLEMENTED + LIVE WITNESS [measured 2026-11-16]
Code: raceintro.{h,cpp} well split + measured layout constants;
vendortext.cpp runRaceIntro rewritten (chrome page + frame + lgrace
portrait + raceflag emblem + centred wells; +raceName param; title.cpp
passes speciesNameAt). Tests 403/0/0 (+raceintro_t415_well_split), 0
warnings.
WITNESS (work/r1/loop/walk/t415_raceintro.png, native-vision graded):
outer frame + header divider + band divider + vertical separator ALL
present at the measured coords (px sample (125,182,182) exact); lgrace00
portrait native at (7,46) inside its well; raceflag k0 emblem top-left;
header centred; right well white INTRO text; body well TEXT in race ink.
DEFECT (named seam, NOT fixed): body+header ink renders RED (220,60,52)
for Minions — the static-table byte 16 -> pal[83] — while the vendor
screenshot shows GREEN (56,170,85) ~= pal[19] = racebyte 0. The INK LAW
is verified (byte*4+0x13); the INPUT (runtime diplo-table row at
0x12e18+specnum*494) is scenario-populated and differs from the shipped
static dump — this is carried seam H3 (runtime race-colour byte census).
Do NOT "fix" by hardcoding green: one race's witness cannot set 21 bytes.
