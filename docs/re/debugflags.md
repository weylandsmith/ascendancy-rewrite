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
