# WIP t193 session (opened 2026-10-29 ~12:59)

## Intake: TRIGGER-A armed, REAL new play (not a stale re-arm)
- Probe baselines were re-frozen by t192 at size 5,702,731,088 / mtime_ns 1793247164180000000 (Oct-29 00:12:44).
- Trigger report: size 5,706,032,159 mtime_ns 1793291822736000000 (Oct-29 12:37:02) -> growth ~3.30 MB AFTER the frozen baseline => REAL new sitting per t192's own note ("a fresh arm now means REAL new play").
- Session-start check (my own, 12:59): size 5,707,686,356 mtime 12:58:23 -> the sitting is STILL GROWING (watcher alive). Saves 41..58 sav mtimes roll 12:55:28..12:58:18 (rolling overwrite), 59/60 at 12:36:49/59. New screenshot work/r1/shp_png/reference/Screenshot_2026-10-29_12-31-38.png (12:31) = game window up. dosbox procs reported 'none' by the probe at 12:44 yet the timeline grew at 12:58 — the probe's proc-name match is unreliable (ps shows python3 lines; dosbox name mismatch), do NOT conclude capture-death from it.
- Named dir playcap-20261014-224611 is stale again (same as t192): growth is in the SHARED work/r1/playcap timeline.

## Assigned shape
Per loop law, a new sitting outranks the stale t193 assignment: adjudicate the
sitting window FIRST (scripts/r1_t192_window_adjudicate.py RUN=shared dir,
BASE=5702731088), bank what the new bytes are, then either advance the ledger
with witnesses or re-queue t193 (lane painter) with the sitting facts inline.

### F3 — SHARE PATH WITNESSED: rec+0x20 is a MULTI-BIT per-empire mask (MEASURED 20/20 mid-game saves, scripts/r1_t193_midgame_witness.py)
Mid-game save set (all 20 slots re-written 12:36..13:03, game at t=1086,
4 empires Chamachies(player,idx0)/Orfa/Ungooma/Minions):
  - lane rec+0x20 census (58 lanes x 20 saves = 1160 recs):
    {1:160, 3:80, 6:180, 7:220, 11:260, 15:260} — ZERO zeros, 100/1160 values
    MULTI-BIT (3=0b0011, 6=0b0110, 7, 11=0b1011, 15=0b1111). The t192
    new-game negative (census all single-bit {0,1,2,2,4,8,16}, share path
    zero witnesses) is now SUPERSEDED: FUN_00046354's OR-onto-existing-bit
    (0x463eb/0x46421) HAS fired — e.g. 11 = bit0|bit1|bit3 = lane visible to
    Chamachies+Orfa+Minions. Per-bit FOG census (58 lanes/save): bit0
    (player) visible 49 / fogged 9; Orfa bit1 50/8; Ungooma bit2 33/25;
    Minions bit3 26/32 — EVERY empire has fogged lanes mid-game, and the
    PLAYER'S FOG IS THE SHALLOWEST (values 6=0b110 and 15=0b1111 lack bit0 =
    the 9 AI-only lanes). [inferred] AI empires share far more aggressively
    with each other than with the player at this attitude profile
    (peace-with-att-300s, one war).
  - MASK IS STATIC ACROSS THE WHOLE SITTING: md5(+0x20 vector) and md5(+0x21
    vector) identical in 20/20 saves (4ca8c5c6 / 99522cd0) — the share grants
    all happened BEFORE the first captured save of this sitting (or on
    turn-advance only; the sitting covered t=1086 mostly within-turn).
  - t192's per-race list == {rec+0x20 == 1<<r} law is now FALSE mid-game
    (0 ok / 80 bad): lists hold cnt=2 per race (8 lanes total) and are a
    SUBSET of nonzero-mask lanes for every race, but no list equals the
    exact-single-bit set. RE-INTERPRET: [sub+0x2c] list = the race's OWN
    claimed/discovered lanes (the 8 bridge/special lanes 25,50 / 27,55 /
    18,54 / 2,57 — note 50..57 are the t190 BRIDGE lanes), NOT the visibility
    mirror. t192's 100/100 equality was an artifact of the new-game state
    where each race's own lanes were exactly its single-bit reveals.
  - rec+0x21: {0:720, 1:440} — NOT all-zero mid-game (440 ones). Correlates
    with mask: b21=1 exactly for masks {1,3,11-with-bit0...}: pairs
    (3,1)x4,(7,0)x11,(11,1)x10,(11,0)x3,(15,0)x13,(6,0)x9,(1,1)x8 — b21=1
    iff bit0 set? {1:8,3:4,11:10} = 22 lanes with bit0&b21=1... 11 appears
    with BOTH b21 values (10 vs 3) so not a pure function of +0x20. Writer
    still unmapped; semantics OPEN (flag stands).
  - star obj +0x16/+0x17 byte censuses show same multi-bit shape
    (+0x16: {1:160,6:180,7:160,11:240,15:260}; +0x17: {1:260,6:240,7:180,
    11:220,15:100}) over the first 50 stars; trailing zeros in the raw print
    were the loop's own pool addresses (script bug in census printing only —
    values 0 counted for stars beyond nstar... VERIFIED shape from first-50
    entries; +0x17 values are byte-shifted versions consistent with the
    +0x16 u16 read). TWIN FUN_00046524 share path has witnesses TOO.


### F4 — t191's "paint loop -> painter" label REFUTED: FUN_00025604 is a snapshot/serializer, and the rec+0x20 UI consumer remains UNMAPPED (Ghidra decompile 0x20c48 + 0x25aa2)
  - FUN_00020c48 decompiles to an ALLOCATION wrapper: stack-link loop, calls
    FUN_00077b40 (alloc; sets *(puVar1-8)=0x20c84 return-continuation, calls
    FUN_00077b47 = free/free-frag on over-read), returns block. NOT a painter.
  - The cited loop 0x25aa2..0x25b6d lives in FUN_00025604, which copies whole
    game-state structs into the allocated buffer: lane pool (base+0x3337,
    stride 0x27: fields rec+8..+0x23 incl. +0x20 byte, +0x21 u16, +0x23 u32,
    endpoint objs *(rec)*+2>>0x10), diplo rows (stride 0x1ee copy of 100 dwords
    + tail at +0x192), star slot refs, counts words 0x49c3/0x32dd1/0x3067b...
    = a game-state SNAPSHOT writer (save/AI-scan shape), not lane drawing.
  - CONSEQUENCE for leg (b): the existence of a rec+0x20 CONSUMER that HIDES
    lanes is still UNPROVEN statically. What IS proven now (F3) is that the
    mask is LIVE per-empire game data with fog bits (every empire fogged 8..32
    of 58 lanes mid-game) — bookkeeping a pure "no fog" game would not need.
    The abilities.md parenthetical "(UI draws every star)" is NOT yet refuted
    by a cited paint site either way -> it must not stand as cited
    justification; rewrite-gap row OQ-026 OPENED (see ledger edits) with
    closure route = find consumer (search `cmp/test byte [reg+0x20]` LOAD
    forms + star-painter xrefs from LAB_00013bc5 consumers) then implement+pin.

### F1 — the new bytes ARE real mid-game play (MEASURED 13:04, sequential suffix read)
Sequential read of the suffix from BASE-1 (8,159,208 B -> 314 rows parsed, all
in_game except 2):
  - turn histogram {1086: 192, 1254: 120, 0: 2}; wall 12:30:31 .. 13:03:52.
  - LAST row t=1086 wall 13:03:52: names Chamachies/Orfa/Ungooma/Minions,
    states rows [[0,1,1,2],[1,0,1,1],[1,1,0,1],[2,1,1,0]] (1=PEACE, 2=WAR per
    t85b/t187), atts up to 600; planets_mine 26; 30 ships present.
  - SHIP STATES in window include 1,3,4,5 (t192's ring had ship count 0; the
    t49/t58 "zero ship activity ever" corpus condition is now BROKEN for the
    first time -> state-4 rows EXIST in the ring at last t=1254, 35 'appear'
    events, 0 vanish, 0 owner-change, 0 relation transitions, 0 att |d|>=10).
  - t192's index-based window (83 entries / 42 trusted rows, monotonic wmark)
    DISCARDED the t=1086 rows as stale echoes (40) — the sitting is NOT
    monotone in file order: the resumed game runs t=1086 while older t=1254
    blob mtimes still trail. Any window adjudication on a RESUMED save must
    not use a single global wmark (banking this as a method caveat).

### F2 — task re-shape (sitting outranks the stale t193 queue item)
The t192 negative that gated the share law was exactly: "pool +0x20 census
{0:940,1:40,2:60,4:40,8:40,16:40} all single-bit = share path ZERO witnesses
in the NEW-GAME corpus; needs a mid-game shared-lane save." F1 says we now
have mid-game saves (all 20 sav slots re-written 12:36..13:03, real diplomacy,
ships flying). So this iteration = RE-RUN the census against the mid-game save
set and decide the share law with measurement. The lane-painter static walk
(st193 a/b/c) is re-queued, not started.

