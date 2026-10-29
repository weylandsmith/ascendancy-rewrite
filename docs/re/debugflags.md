# debugflags.md — nougat.lf / flash.pop gate map (t85e)

Flag law (score.md S8): DAT_00010ba0 = -1 iff fopen("nougat.lf","r")
succeeded at boot (single writer 0x21309); DAT_00010ba4 = -1 iff
"flash.pop" exists (single writer 0x2132b). Gate polarity below = the
branch that EXECUTES DEBUG BEHAVIOR. Player-confirmed t85e: with
nougat.lf present (web build), hovering a ship shows power/moves/
integrity/orders — that is gate 0x1d9fe working exactly as decoded.

## nougat.lf (DAT_00010ba0), 24 gate sites

| site | module | polarity | behavior (disasm-grounded) |
|---|---|---|---|
| 0x1d9fe | batcon | armed | SHIP-HOVER READOUT: ship rec [edx+0x34]/[+0x54]>>16 -> race row lookup [0x12e17 name byte]; flag==0 skips the whole info path. PLAYER-CONFIRMED. |
| 0x250aa | cosmos | armed | NUMSHIPS.DBG DUMP: fopen("numships.dbg","at"), loop T (0x16145) over star-owner block 0x13bc5 (+0x1c), writes per-star ship census. |
| 0x28059 | batcon | armed AND toggle [ebp+0x58e]==-1 | SCORE OVERLAY: sprintf "STARS CONTROLLED %d" (DAT_482fb) + "PERCENT CONTROLLED %d" (100*DAT_482fb/T law S2). |
| 0x2736f | batmode | armed | TOGGLE HANDLER for the overlay: not [esi+0x58e]; sits in the cosmos-window message chain right after the [esi+0x582]/ds:0x9f0f8 next-turn-continue checks — a click/key on the map view flips the overlay. Exact trigger message NOT statically pinned. |
| 0x29092 | coswnd | armed | COS%05d.BUG STATE DUMP: sprintf pool 0x100c 'cos%05d.bug' with DAT_00012e10 (TURN), then 0x53fe8 write path ('APE CACHE' 0x676 context) — per-turn full cosmos dump [trigger cadence = coswnd paint/event path, not pinned]. |
| 0x273a0 | batmode | armed | REVEAL-ALL (map family): for i<word[0x177d3]: byte [0x16147+i*0x27 +0x20] |= 1<<player(0x7458e) — sets the player bit in EVERY stride-0x27 map record. |
| 0x27401 | batmode | armed | REVEAL-ALL (star family): for i<T(0x16145): byte [0x13bdc+i*0x60] |= 1<<player AND [0x13bdb+i*0x60] |= — writes the 0x13bc5 star-owner block neighbours directly. |
| 0x27476 | batmode | armed | DIPLO ROW CLONE: loops diplo rows (stride 0x1ee @0x12e16, bound word[0x13b98]); copies template word [edx+0x12feb] into third-party matrix [0x12fc8], attitude [+0x1b2+2*idx] AND state byte [+0x1c0+idx] — overwrites relation cells wholesale. DANGEROUS to live campaign state. |
| 0x47828 | batcon | armed | FAMILY-0x4b REVEAL + ARRAY PRIME: count word[0x74744]: byte [0x74743+i*0x4b] |= 1<<player; then word[0x76492+i*2]=0xffff, word[0x764a0+i*2]=0. Which family (0x4b stride) NOT pinned — candidate research/item list. |
| 0x478a0 | batcon | armed | sibling of 0x47828 (same loop shape, different entry) [not expanded] |
| 0x47929 | batfxa | armed | [not expanded] |
| 0x3ad62 | batcon | armed | MUTATION HOOKS on ptr [ds:0x43508]: add WORD [+0x50],0xC8 (=+200) then item call 0x38f68; 0x3ad8d: inc WORD [+0x55] then activator 0x38ba4 (governor/item family, income-law.md S14); 0x3adbf: call 0x38f68; 0x3addb: copy WORD [+0x4a]->[+0x42]; 0x3adfc: read BYTE [+0x57]; 0x3ae72 sibling — cheat-style give/activate handlers on the selected-object pointer. |
| 0x54d5c | batcon | armed | NOT [ds:0xa2048] + gated vtable call 0x56e10(-1,2) behind [ecx+0x4226]>>16==8 |
| 0x54ef4/0x54f4f | batcon | mixed | AUDIO: armed path loads 'WINEVENT.BIN' via 0x598fc (the OQ-022 digital-music engine that is otherwise unreachable in every captured state); float 1.0 to [ecx+0x24dac], zeroes [0x489e]/[0x48a2]. nougat.lf is the door OQ-022 said had no door. |
| 0x27513 | batfx | armed | early-return fx gate (effect body runs only armed) |

## flash.pop (DAT_00010ba4), 27 gate sites (summary)

* race.cpp 0x417aa/0x4193c/0x41980/0x41a38 (+0x4170b, 0x41f8a, 0x42036):
  restructure the AI decision loops (stack arrays masked &0x7, ship
  order/build classes) — OQ-005 territory.
* batcon 0x3e844/0x3ea6a/0x3eb2c: AI turn phase re-routed around the
  known attitude scorer 0x3ecb8 (+0x3ef2c, 0x44690 adjacency, 0x40ec0);
  armed skips the pairwise state-byte [+0x1c0] scan.
* raceneg 0x446a5/0x44758/0x44a61: ARM THE VENDOR ASSERTS — report calls
  0x2a428 with '..\raceneg.cpp' source tags; the assertion strings
  ('T%04d: R%d ship exists at %s, flags (%d) indicate otherwise.') live
  in the same pool cluster as the score strings (S8). Armed flash.pop can
  emit assertion output DURING AI turns.
* winmgr 0x5529d/0x55a66/0x55b6e + batcon 0x5549a/0x55fa1: turn-continue
  window ('NEXTTURNCONT' windows.txt) message path alters.

## t191: THE REAL KEY DISPATCH (supersedes the t85f leaf-address table)

t191 MEASURED (branch scan + disasm 0x27560..0x27e7f + runtime pointer scan):
the cosmos-window MESSAGE HANDLER is image 0x26b34 (prologue 56 57 55 83 ec
3c); its slot in the runtime dispatch table = member 0x247adc (physical
0x247a54 == data-seg image 0x88604) holding P0+0x26b34 (60.sav, B=0x1bf4d8;
pointer law pointer==P0+X). The static file image has ZERO dwords equal to
0x26b34 or to any reveal-block head — the binding exists only POST-RELOCATION
(OQ-011 law), which is exactly why every static hunt (t85f, t179c, t191 WIP
first pass) failed. Handler arg convention: DX = message class, ECX = payload.
DX==3 = KEYDOWN (cascade 0x27dcb..0x27e1b -> sub-cascade head 0x27614);
DX>3 does rect-bounds hit tests on [ESI+8/0xc/0x10/0x14] (mouse).

ECX = RAW AT SET-1 SCancode, binary-search cascade 0x27614..0x27669:

| scancode | char | leaf | behavior (disasm-grounded) |
|---|---|---|---|
| 0x13 | R | 0x27476 | DIPLO ROW CLONE (nougat-gated; DANGEROUS, see gate table) |
| 0x1f | S | 0x27401 | STAR REVEAL: for i<T: [0x13bdc+i*0x60] |= 1<<[0x7458e] (+[0x13bdb]) |
| 0x26 | L | 0x273a0 | LANE REVEAL: for i<word[0x177d3]: lane_pool[0x16147+i*0x27+0x20] |= 1<<byte[0x7458e]; then redraw CALL 0x28fc0 + 0x284bc + vtable [ESI+0xa7]+0xc. GATE CMP [0x10ba0],0 = nougat.lf |
| 0x2e | C | 0x2736f | SCORE-OVERLAY TOGGLE [ESI+0x58e] = NOT (nougat-gated) — consistent with t85f's player-observed 'c' screen; note ECX here is TESTed against 0x1f/0x2e ranges in the FIRST cascade (0x2762c JZ) |
| 0x0c | - | 0x275b0 | ZOOM OUT: float DAT_0009f108 *= pool const |
| 0x0d | = | 0x275e4 | ZOOM IN: DAT_0009f108 *= pool const |

THE 'l' ANOMALY IS RESOLVED: b-sting's sticky cheats are scancode-keyed, not
char-keyed — there is (and never was) a `cmp al,'l'`; the WIP's full
linear-decode census (80/81/83 /7 + 3c/3d, whole code region) found 'l'/'L'
compare immediates ONLY inside the printf/scanf front-end 0x795be..0x7a4bf
(length modifiers h/l/L/w, WIP Findings 1+3). STICKINESS LAW: no clear site
against the lane-pool addressing form exists image-wide (ships.md S23 L5
census; caveats there) — allocator zeros only at pool-create 0x248ab —
matches player "cannot be turned off".

[0x7458e] = CURRENT-PLAYER INDEX byte (writers 0x21aa0 pair-setter — sets
mask too, DL=0x0100/DH=0 when idx==0xFF spectator case — and 0x52cc6
new-game reset). Normal-play lane-visibility GRANT path (not a cheat):
function 0x46354, OR sites 0x463eb/0x46421, same rec+0x20 byte between two
empire masks — SEMANTICS CLOSED t192 (ships.md S23 L6): mutual lane-vision
share between the two diplo rows' empires, N = rand%(state==3 ? 6 : 3) + 1
grants per call (alliance doubles the budget), caller EBX selects
bidirectional (0x45778 alliance-formation) vs receive-only-for-the-player
(0x55f6e per-race event loop). Lane-paint READER of
rec+0x20: loop 0x25aa2..0x25b6d (stride 0x27, pool base data+0x3337, copies
+0x20/+0x21/+0x23 for painter 0x20c48).

t192 CONSEQUENCE FOR THE ABILITY ROWS BELOW (flagged, not re-derived): the
parenthetical "no exploration bookkeeping" in the SA_KnowStarLanes /
SA_KnowHomeWorlds filings is FALSE OF THE ORIGINAL — rec+0x20 (lanes) and
star-obj +0x16/+0x17 (stars) ARE per-empire exploration bookkeeping, and the
lane-paint loop copies rec+0x20 into its painter record. The rewrite's FILED
NO-OP disposition can still be right (the rewrite has no visibility layer at
all), but it must not be justified by claiming the original lacks one. What
remains UNMEASURED is whether the vendor UI actually withholds a lane whose
rec+0x20 lacks the viewer's bit (painter 0x20c48 was not walked t192).

## t85f: user-observed keys + external corroboration (LEAF ADDRESSES REJECTED BY t191)

User (web build, nougat.lf on): 's' lists all star systems, 'l' all lanes
(both STICKY — cannot be turned off), 'c' toggles a screen headed
"0 Biorythym (Neutral)" + per-player diplomacy figures + stars-controlled.
Independent community doc (b-sting.nl/ascendancy/cheats.html, content
lineage: Darth's Ascendancy page <- "The Way" by Jason Goldman) lists the
same cheat set from play. Codes it documents, mapped to our decode:

Starmap dispatch 0x79969..0x79c62 (key char at [esi+0x15], case-sensitive
binary search; uppercase leaves exist as distinct branches — b-sting uses
uppercase S/L/C for the sticky ones):

t191 REJECTION: the entire leaf-address table below sits inside the vprintf
format-spec parser (WIP Findings 1+3, disasm 0x798de..0x79d26 = width/
precision/sign engine) — every LEAF column value is void. The b-sting
code->behavior MAPPINGS (s/l/c/1..7/Alt-E rows) remain corroborated by the
t191 scancode cascade above; only the address column died.

| key | leaf | = |
|---|---|---|
| s/S | 0x79985 -> 0x79ace | REVEAL-ALL (gates 0x273a0 map-family 0x27-stride |=, 0x27401 star-family 0x60-stride |= b-sting "All stars explored"). STICKY LAW: reveal paths are OR-only, no inverse exists in code — matches user "can't be removed". |
| l   | (lane reveal) | b-sting "All starlanes exposed"; same OR-only stickiness. t179c caution LIFTED 2026-10-29: player RE-CONFIRMED 'l' displays all star lanes (re-test done, not key-mashing). The static anomaly stands as an OPEN HUNT, not a refutation of the observation: zero `cmp al,'l'` sites exist image-wide (t85f) -> check the scancode 0x1E path / dispatch-table indirection near 0x79950..0x79c20. Re-armed (STATE t184 un-deferred via t189b). |
| c   | 0x799e2 -> 0x79c35 (sets [esi+0x8]=1, clears flag bits 0x06 = redraw) | STATE-OF-GALAXY screen = 0x28059 displayer. Header "STARS CONTROLLED %d" (DAT_482fb) + "PERCENT CONTROLLED %d" (formula LIVE-VERIFIED in code 0x280c4..0x280e3: score*4-score=3*score, <<3=24*score, +score=25*score, <<2=100*score, idiv T -> TRUNC(100*score/T), T=(0x16143)>>16) + "BIORYTHM" header copied from 0x4850c + "%d Biorythym (%s)\n" + per-race rows "R%d %10s %d\n" (0x28128..0x28185: name tables PHASES@0x89050 = Peaceful/Neutral/Hostile stride12, RELNAMES@0x89074 = Unknown/Peace/War/Alliance stride10 — THE relation-state enum spelled out by the vendor: 3=Alliance, directly informs OQ-023). |
| 'c' toggle | gate 0x2736f handler: NOT [obj+0x58e] | user-confirmed toggle; displayer test at 0x2805f: shows only when [ebp+0x58e]==flag value (-1). |
| 1..7 | 0x799b7.. region | PLAY AS OTHER SPECIES (b-sting) — race-swap; art mismatch documented. Static hook sites [not individually pinned]. |
| 8   | [not pinned] | SEE EVERYTHING (b-sting) — candidate the 0x47828 family-0x4b reveal. |
| Alt-E | e-leaf 0x79971 | STEAL TECHNOLOGY each turn, re-press = off — a persistent toggle like 0x58e. |
| O / I | o-leaf / i-leaf | planet screen: MAX POP / FINISH PROJECT. |
| C / D / F (research screen) | C/D/F leaves | complete current / learn all / forget-all research. |
| T / R (planet screen) | [not pinned] | create colony / take over planet. |
| Shift-M | shift-state in handler | +1 pop slot (Yarrow credit in b-sting). |
| Alt-D | | show coordinates (x,y) — candidate the 0x28059-adjacent sprintf cluster. |
| Alt-W | | "useless internal data" window. |
| Alt-G | | GIF screenshot into ascend dir (b-sting: overwrites prior!). |

FLASH.POP EXTERNALLY = "let the game play itself" (continuous-advance
autopilot, crashes after 4h+). Matches our gate census: flash.pop gates
restructure the AI turn path + arm vendor asserts (raceneg) — a
self-driving QA harness, not cosmetics. Do NOT run in the capture dir.

b-sting CRASH/WIN NOTE: "the cheats below can cause the game to think you
have won. In order to prevent this, you must build something (or perform
any task) before going to the next day." => behavioural law candidate for
OQ-021: DAT_482fb is refreshed by player ACTIONS during the turn, and the
cheats inflate it without the reset path — score.md S6 live-slot zero
reads get consistent with action-driven recompute instead of boundary-only.
[unverified beyond the doc + S6]

## OPERATIONAL NOTES

1. HIGHEST PROJECT VALUE if the dumps fire on the web build: play a few
   turns with nougat.lf ON in the SCRATCH dir, then list the dir for
   numships.dbg and cos<000NN>.bug — those are per-boundary FULL state
   files (OQ-003 record map, OQ-010 post-combat census, OQ-021
   DAT_482fb at every turn in one shot).
2. Overlay: needs BOTH nougat.lf and the 0x58e toggle (map-view click/key,
   handler 0x2736f). Overlay showing PERCENT CONTROLLED = direct read of
   the OQ-021 comparator input.
3. DANGER: 0x27476 clone + 0x27401 owner-block writes mutate CAMPAIGN
   state. Never enable flag files in the capture campaign directory;
   scratch only.
4. Trigger cadences for 0x29092/0x250aa are [UNVERIFIED] — file presence
   after play is the test.
