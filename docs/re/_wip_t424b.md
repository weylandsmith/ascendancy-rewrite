# t424b WIP — RACE INTRO SCREEN CYCLE (background greyscale + text unreadable)

Task per docs/STATE.md NEXT ACTION 2026-11-19. Row hypothesis was "the intro
art needs the vendor palette transform the gif/cine path applies". NOTE:
payload scan [verified] finds NO .cine/.FLI strings at all (work/ascend_payload
.bin: b'.cine' 0 hits, b'.gif' 3 hits = logo.gif 0x834d8, scr%03d.gif 0x8473f,
0OPENING.GIF 0x835be) — there is no cine path; the gif sites are logo/title/
Alt-G screenshot (debugflags.md Alt-G). The hypothesis as written cannot be
tested; measured below what the vendor background actually is.

## F0 — VENDOR INTRO BACKGROUND IS DARK SPECKLE, NOT THE CHROME PAGE [measured]
Source: scratchpad/species-introduction-original.png (user vendor screenshot,
1041x780 = 640x480 x 1.6266; scaled => interpolation noise, so nearest-palette
classification with tol, exact-match census reported separately).

Exact-match census of the TEXT WELLS (header x50..620 y11..35; right well
x316..626 y50..240; body x12..626 y265..458), nearest-game.pal index:
    idx0 (0,0,0) 28.6% | idx200 (12,12,16) 23.1% | idx1 (12,12,12) 17.1%
  | idx196 (12,28,48) 2.3% | idx197 0.8% | idx195 0.4% | idx2 0.3%
  (remainder = text ink + interpolation blends; "dark other" 19.6% mostly
  nearest-idx 0/1/200 at distance 20-90, i.e. blends of the same families)
Chrome-family colours (97,97,97 / 77,113,117 / 85,125,125 / 89,134,138 / ...)
= 0.0% inside header and body wells; 5.7% in the right well (text-edge
coincidence); bright only ON the frame lines and the 3px gaps adjacent to
them (e.g. y40..45 header-gap 47% chrome-family = frame antialias).
Whole-image: dark (mean lum < 60) = 66.3%; body well dark = 84.7%;
header dark = 93.9%; top-band gaps (y2..7, y245..262 OUTSIDE the wells) carry
27-35% chrome-family.

CONCLUSION [inferred from verified census]: t415 F5's "backgrounds inside all
wells = the cosmos hash-noise texture (t414 law)" was a native-vision read of
SPECKLE PRESENCE, not colour; the vendor's in-well speckle is DARK
({0,1,200,196} family, ~40/32/24 relative mix of 0/200/1), while the port
paints the BRIGHT chrome page full-screen (vendortext.cpp runRaceIntro
chromePage block). That is the "background greyscale" the user sees: our
bright grey-teal field where the vendor shows near-black navy speckle. It is
ALSO the "text unreadable" cause for the body well: vendor body ink is race
green (56,170,85) on near-black; our port paints race ink (red via seam H3
static byte) on bright chrome = no contrast either way.

Same-family comparison [measured]: pinned original-planet-view.png mid region
(60,60)-(600,420): idx0 81.8 / 200 1.9 / 1 1.5 / 197 1.1 / 196 1.0 / 2 0.7 /
198 0.6 / 195 0.5 — same dark family, DIFFERENT mix (intro is far denser
speckle: 0 only ~40% of dark px vs 82% on planet view). original-strategic-map
mid: 99.6% pure black. So the intro background is its OWN surface, not the
map or planet backdrop copy. 17np k0 (CONTROL--17np--rec0--639x479.png, our
decode) census: 83.8% black + 8.8% idx242 teal + chrome-family lines = the
panel FRAME art, not the speckle — refutes "intro bg = 17np k0 blit".

## F1 — BOUNDARY LAW: chrome OUTSIDE the frame, dark speckle INSIDE [measured]
Classified every pixel of rows y=20,300 and columns x=150,450 of the vendor
screenshot against the chrome-family vs dark-family palettes (tol 800 sq-dist,
nearest-class):
  row y20:  chrome x0..5 and x636..639 ONLY; x7..633 all dark-class (the '.'
            runs = text glyph blends).
  row y300: chrome x0..5, x634..639; x7..633 dark-class.
  col x150: chrome y0..5 (and y474..479); y7..37 dark (header well);
            y46..248 = portrait art (its teals classify chrome-family — art,
            not background); y254..473 dark.
  col x450: chrome y0..3; y7..473 dark-class except portrait-free band — the
            right-well background IS dark.
=> LAW: the bright chrome page covers ONLY the screen-fixed margins outside
the outer frame rect (x0..6, x634..639, y0..6, y474..479). The ENTIRE frame
interior (7,7)-(633,473) — all three text wells AND the gaps between them —
is the dark speckle. Our port paints the bright chrome page full-screen:
that single defect is both "background greyscale" (bright grey-teal where
vendor shows near-black navy) and "text unreadable" (race ink on bright
field has no contrast; vendor race ink on near-black does).

## F2 — DARK SPECKLE COLOUR LAW + GRAIN [measured, fit]
Fresh-draw census (nearest game.pal, tol 30, text-free dark px of all three
wells): idx0 (0,0,0) ~40% | idx200 (12,12,16) ~25% | idx1 (12,12,12) ~21% |
idx196 (12,28,48) ~6% | idx197/195/2 ~1% each. (Percentages of ALL well px
incl. text; renormalised over the four-family base: 0:48/200:29/1:24/196:8.)
GRAIN: mean |lum delta| at game-px lags 1..6 = 3.41,5.74,7.25,7.92,8.27,8.72
— rises sub-linearly = CORRELATED noise, not iid (iid would jump to plateau
by lag 2); class-match lag-1 0.66 h / 0.65 v (scaled-shot ceiling). Same
Markov shape as the t422 chrome law, different colour census. [inferred] the
generator is the same engine routine recoloured; the cited generator code is
NOT pinned this iteration (t433's memory-surface census is the route for it)
— port implements the MEASURED colour census + the t422 chain law, and the
chain's origin stays a named seam.
NOT the map/planet backdrop: strategic-map mid = 99.6% pure black,
planet-view mid = 81.8% black + idx242 teal (different mix); 17np k0 decode =
frame art (83.8% black + 8.8% teal 242 + chrome-family lines) — REFUTED as
the intro background source.

## F3 — INK WITNESS (H3 narrowing) [measured]
Vendor screenshot body/header ink (Minions, specnum 0) = (56,170,85) =
game.pal[19] => RUNTIME racebyte 0 for Minions. Our static kIntroRaceBytes[0]
= 16 -> pal[83] (red) — measured MISMATCH. Pin [0]=0 (the one witnessed
entry, witness cited); the other 20 static entries remain seam H3 (runtime
diplo table is scenario-populated; one race's witness cannot set 21 bytes —
t415 law honoured).

## F0b — GIF/CINE PREMISE [verified negative]
b'.cine'/'CINE'/'.FLI' = 0 hits in work/ascend_payload.bin. The queue's
"gif/cine path" does not exist; gif sites are logo (0x834d8), Alt-G
screenshot scr%03d.gif (0x8473f, debugflags.md), 0opening title (0x835be).
Title palette (t386 TSV) is title-only per title-art.md §4 refutation —
NOT the intro fix.

## F4 — IMPLEMENTED + TESTS [2026-11-20]
Code: mapchrome.{h,cpp} introSpeckleAt (stateless 5/25 Markov chain, distinct
splitmix salt, fresh-draw census 40/30/25/5 = pal 0/200/1/196); vendortext.cpp
runRaceIntro background = chrome page ONLY outside the frame margins
(x<=6||x>=634||y<=6||y>=474), dark speckle inside; raceintro.h
kIntroRaceBytes[0] 16 -> 0 (witness F3). INCIDENTAL BUG FIXED (found by the
witness run): the lgrace portrait path was built with snprintf into char[64]
— dataRoots longer than ~50 chars TRUNCATED the path (".../extracted/ascend0",
refusal in app.log) and the portrait silently never loaded; now std::string.
Tests: rewrite/tests/test_introspeckle_t424b.cpp (4 tests: deterministic,
census membership + shares, correlated-not-iid, decorrelated-from-chrome);
test_raceintro_t412 ink pin updated to the witnessed byte. Full suite
454/454, build 0 warnings.

## F5 — LIVE WITNESS [measured 2026-11-20]
scripts/t424b_intro_witness.sh (Xvfb :97, title -> New Game -> species ->
Begin; shot /tmp/t424b_shots/t424b-raceintro.png, specnum 1 SNOVEMDOMAS).
scripts/t424b_witness_census.py VERDICT PASS: right well dark share 0.936,
body well 0.911, side margins dark share 0.033 (chrome page intact), body
dark census 0.400/0.300/0.251/0.049 (idx0/200/1/196 — matches the fresh-draw
weights), grain same-colour adjacency 0.348 (> iid 0.315). Native-vision
grade of the shot: dark speckle field, header + right + body text all
readable, portrait loaded (the truncation fix), frame + dividers intact.
NAMED SEAMS carried: (a) speckle generator ORIGIN + exact parameters
(t433 memory-surface route; R-t424b(3) bars fitting them from the scaled
shot); (b) H3 race-colour bytes for the other 20 races (runtime diplo table;
t415 law); (c) T428-B witness-A lineage, T427-A..F unchanged (untouched this
row). LEDGER: closes NOTHING — the race-intro visuals have no OQ owner
(t414..t429 precedent); OQ-016/019/027 untouched.
