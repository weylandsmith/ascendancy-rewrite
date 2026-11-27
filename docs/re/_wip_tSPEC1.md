# _wip_tSPEC1 — Begin species pick must reach PLAY (D33-L2)

Assignment (STATE.md tSPEC-1): port drops the RACELIST species pick before
world-gen; vendor home planet TYPE is per-species (tPL-D1 tables T1/T2
payload 0x88f90 / 0x88fe4, MEASURED 85/85 homes). PLUMB: wheel species ->
NewGameSettings -> cfg.playerSpecies -> home terrain row + art.
Pins: Chamachies -> size idx 3 + terrain row 7 in PLAY; Minions differs
(spec0 4/5). Witness: two Begin runs, different species, different home
terrain census. Re-derive at bytes what the vendor Begin writes about the
PLAYER SPECIES (tNG-B state base 0x12e10 sibling of atmosphere 0x52b44).

## S1 VENDOR SPECIES-ARM LAW [verified disasm this session,
## scripts/t442_disasm.py over FUN_00022ce4 0x22ce4..0x2313f]
The PLAYERS_MORE wheel click arm (0x52e58 -> call 0x22ce4) carries THREE
args (tNGB B2 banked: eax=0x12e10 state, ebx-hi=word[win+0xb3] SELECTED
RACE ROW, edx-hi=word[win+0xb9] SPECIES COUNT). New byte-level detail this
session:
- 0x22d05 `mov word ptr [eax+0xd88], dx` — player count = species word.
- HOME STAR assignment loop 0x22e82..0x22f67: per player k<word[+0xd88],
  `call 0x7824f; idiv starcount` -> random free star; sets star(+0x14) |=
  0x80|(1<<k), OR bit into +0x17 + system recs. Positions NEVER written.
- SPECIES DRAW loop 0x22f6c..0x22ff6: per player k:
    * k==0 (PLAYER): 0x22f8d `mov bl,[esp+0x10]` (= param_1 = the SELECTED
      RACE ROW word) -> `call 0x3e6bc` at 0x22fa6. NO rand.
    * k>0 (AI): 0x22fba `call 0x7824f; idiv 0x15` (rand%21) -> distinctness
      scan 0x22fd8..0x22fed over byte[raceRow k'*0x1ee + state+7] vs bl,
      re-draw on collision -> `call 0x3e6bc`.
  => VENDOR LAW: the PLAYER'S species is the RACELIST selection (word
  win+0xb3-hi), AI species are rand%21 distinct. The species-COUNT wheel
  only changes N (word[+0xd88]) + re-rolls home stars + re-draws AI species;
  the player row is constant across count clicks.
- Post-draw stat nudges 0x22ff8.. (race-row +0x1cf..+0x1db words +=
  -0x14/-0x1e per player; then a +0x14 leg) — out of scope here.

OPEN: meaning of word[win+0xb3] (row idx vs specnum), what 0x3e6bc stores
(row -> race record +7?), and how Begin's worldgen 0x238e8 consumes
race-row+7 for the HOME size/row tables (t30 site 0x23aeb `mov dl,[eax+7]`
— EAX=race row per tPL-D1 correction).

## S2 WORD ALIASING + RACELIST ARM + 0x3e6bc DECODE [verified disasm this
## session: 0x52c3d init block, 0x52d6c..0x52db8 RACELIST arm, 0x52e58
## species-count arm, 0x22ce4 player branch, 0x3e6bc/0x3e648]
WORD ALIASING LAW (the same unaligned-dword trick as the B1 ladder
`dword[esp+rank*4-2]`): for THIS window, hiword(dword[win+0xb1]) ==
word[win+0xb3], hiword(dword[win+0xb7]) == word[win+0xb9] (B2-banked F7
pairing), hiword(dword[win+0xb5]) == word[win+0xb7], hiword(dword[win+0xb9])
== word[win+0xbb]. Every "sar eax,0x10 after mov eax,[ebp+0xbN]" is a READ
of word[+0xbN+2]. => word[+0xb3] is the SELECTED RACE ROW word:
- INIT 0x52c8c `mov word ptr [ebp+0xb3], 0` — vendor DEFAULT player species
  = row 0 (specnum 0, Minions).
- RACELIST CLICK ARM 0x52d6c: guard `cmp word[+0xb3], ebx(clicked); je done`
  (same row = no-op); else 0x52d83 `mov word ptr [ebp+0xb3], ax` (= clicked
  row) THEN 0x52d8d/98 reload `ebx = hiword(dword[+0xb1])` (= the NEW row)
  and call 0x22ce4(0x12e10, ebx=row, edx=word[+0xb7]=count). The write
  precedes the reload — the call carries the NEW row.
- SPECIES-COUNT arm 0x52e58 call site likewise passes ebx =
  hiword(dword[+0xb1]) = word[+0xb3] => COUNT clicks PRESERVE the player
  row; only a RACELIST click changes it.
0x22ce4 PLAYER BRANCH (loop 0x22f6c, k=0 == player):
- 0x22f8d `mov bl,[esp+0x10]` — param ebx low byte saved at 0x22ced entry
  (= selected row). NO rand for the player; AI k>0 draw rand%21 (0x22fba
  call 0x7824f / idiv 0x15) with distinctness scan 0x22fd8..0x22fed against
  byte[raceRow k'*0x1ee + state + 7] and re-draw on collision.
- 0x22fa6 call 0x3e6bc(eax = state+6 + k*0x1ee RACE ROW, edx = k, bl =
  specnum). 0x3e6bc: call 0x3e648(row) = reset block (zero +0x1aa..+0x1ea
  defaults); `mov byte ptr [row], dl` -> row+0 = owner index k; if
  byte[row+1] != bl: byte[row+1] = bl, call 0x44290.
  IDENTITY: race record = state + 6 + k*0x1ee; +0 owner idx, +7 SPECNUM.
  The param IS the specnum (AI distinctness domain 0..20, stored verbatim).
=> VENDOR PLAYER-SPECIES LAW: player specnum = word[win+0xb3] = the RACELIST
row index clicked (default 0). It reaches play state race-row+7 at CLICK
time (state-identity law). Begin's worldgen 0x238e8 then builds home worlds
reading race-row+7 (t30 0x23aeb `mov dl,[eax+7]` -> T1/T2 index; tPL-D1
MEASURED 85/85: home size=T1[spec], home terrain row=T2[spec]).
PORT GAP CONFIRMED: title.cpp RACELIST click (ui/title.cpp:1273) only sets
selSlot + log; newGameSettings() carries no species; buildCampaign applies
o.playerSpecies (CLI flag, default -1 -> RNG home) — i.e. the user's
"medium eden REGARDLESS of species" is exactly the -1 rng path on every
Begin rebuild.
## S3 WORLDGEN CONTAINMENT [verified this session]
Begin's worldgen call 0x52a67 `call 0x238e8` lands in the function whose
ret is at 0x23dfc; the per-star loop 0x23a2a..0x23d22 (t30-banked) sits
INSIDE it, including the table copies 0x23ac4/0x23ad2 and the index read
0x23aeb `mov dl,[eax+7]` -> T1/T2 picks 0x23aee/af1. So the byte 0x22ce4
wrote at click time (race-row+7) is exactly what Begin's worldgen consumes
for the home planet — no second writer needed. The special-mode gate
0x23aaa/0x23ab4 (esp+0x108 >= 0 && esp+0xf8 == esp+0x114) is the same
tPL-D1-banked condition the 85/85 corpus witness covers (26/26 fresh games
took the table path).
## S4 PORT PLUMB LANDED (this session)
- menulaw.h NewGameSettings gains `species` (player specnum, word[win+0xb3],
  vendor init 0); newGameSettings() takes playerSpecies (default 0 keeps
  every existing caller compiling and identity-mapped).
- title.cpp Begin press feeds `scrollOffset + selSlot` (the SAME expression
  the species-pick log + intro use); apply line now prints species.
- main.cpp buildCampaign: `playerSpecies = (apply && apply->set) ?
  apply->species : o.playerSpecies` — CLI --species stays authority on every
  non-Begin build (headless matrix untouched); AI roster skip-skip + cfg use
  the new local. Live line extended `newgame live ... species %d` + new
  `newgame home <name> cells %d row %d` (witness-readable consequence).
- PINS tests/test_species_pick_tspec1.cpp x4 (handoff identity incl. vendor
  default 0; title feeds RACELIST expr — anchored on `*newGameOut =
  newGameSettings(` because kBeginNewGameBtn also hits paint sites, args
  extracted between the call's parens so the species-pick LOG line cannot
  false-satisfy; main prefers apply->species; behavior: seed x {5,7,2024}
  Chamachies 45/row7 vs Minions 73/row5 DIFFER). Suite 617->621/0/0.
  TRAP LEARNED: slurp idiom is `ss << f.rdbuf()` not `f << ss.rdbuf()`.
## S5 MUTATIONS + WITNESS LANDED (this session)
MUTATIONS scripts/tSPEC1_mutate.sh: M1 handoff drops species arg -> CAUGHT
(species_handoff_identity :104); M2 Begin press feeds constant -> CAUGHT
(plumb_title :130; anchor spans the newline so the species-pick LOG line
cannot collide); M3 buildCampaign reverts to CLI-only -> CAUGHT
(plumb_main :145). restore() copies back + md5-verifies x3 (tPF-6), no git
checkout mid-cycle (tPF-7a). REBUILD-before-witness honored (tESC-1): the
witness ran on a fresh full build AFTER the mutation cycle.
WITNESS scripts/tSPEC1_species_witness.sh rc=0 MEASURED:
  A (no racelist click, vendor default row 0): 'newgame live stars 50 owners
     5 gov 1 species 0' + 'newgame home Parsimony cells 73 row 5' (Minions
     T1[0]=4/T2[0]=5).
  B (18x down arrow -> offset 18, slot-1 click -> 'select specnum 19',
     BEGIN): 'newgame live ... species 19' + 'newgame home Parsimony cells
     45 row 7' (Chamachies T1[19]=3/T2[19]=7). Same seed, same star NAME,
     different TYPE — the exact user-facing law.
  TRAP: 'newgame live' prints only after runTitleScreen RETURNS (post-intro)
  — dismiss the intro BEFORE grepping it (tXT1 order). Per-press arrow
  asserts (tPF-9): 'ui raceconfig arrow down offset N' grep'd per press.
PRE-FIX SHAPE (the D33-L2 defect, honest): both runs printed species -1 and
the SAME rng-drawn home (medium eden regardless of species), because the
Begin rebuild read cfg.playerSpecies = CLI --species (never set on the UI
path).
RESIDUES (documented defaults, no cited law lifted): AI species rand%21
order/stream interplay vs the port's roster-first mapping (the port assigns
AI specnums as "first specnums not the player's"; vendor draws distinct
rand — same DISTINCTNESS law, different draw stream; tPL-D1 home TABLES hold
for either since they key on specnum only); race-row stat nudges
0x22ff8.. (+0x1cf..+0x1db += -0x14/-0x1e, then a +0x14 leg) NOT modelled —
no consumer identified this cycle; word[win+0xb3] cap 0x15 guard unprobed
(roster is exactly 21, UI cannot select past it).
