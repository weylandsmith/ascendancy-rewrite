# _wip_t379 — DEATH vs RECLAIM SHAPES INTO SHIPSIM (queue row verbatim)

Fresh session. Sitting check RING-FIRST: `scripts/t368_ring_turn.py` ->
max_turn=1254 (20/20 slots), and a bounded tail-SEEK (300 KB, OOM law) of
work/r1/playcap/live-timeline.jsonl shows rows still turn 1254 (wall
02:00:59 -> 02:01:31). The capture is live but NO new turn boundary occurred
=> assignment stands (t379 is a zero-capture row; witnesses banked).

## S1 MEASURED — THE TWO SHAPES ARE ONE LAW + AN OBSERVATION ARTIFACT
Tools: scripts/r379_shape_census.py (per-save count word + full-window dead
census + s12/s40 detail) and scripts/r379_shape_verify.py (record byte
identity + changed-slot census + counter pair). Banks:
work/r1/bank-play-20261111/ (t1253, orders placed) vs
work/r1/bank-play-20261111-late/ (t1254, turn ended). 20/20 base-verified on
each side; the numbers below are IDENTICAL on all 40 saves (no drift).

  t1253: array count word (u32 @ B+kDataSeg+0x43489 >> 16) = 41
         window range(41) = slots 0..40; full-window dead = 66, first dead
         slot 41 (i.e. NO dead row inside the window);
         s12 handle 0x00020000 kind 4 name 'Medium' (LIVE);
         s40 handle 0x00000000 kind 1 name 'Intil-Za' (race 0 = player).
  t1254: array count word = 40
         window range(40) = slots 0..39; full-window dead = 67, first dead
         slot 12 (the corpse is INSIDE the window);
         s12 handle 0xffff0000 kind 0 name '' (DEAD MARKER, C4 shape);
         s40 handle 0x00000000 kind 1 name 'Intil-Za' — STILL PRESENT in the
         full window.

  T1 (load-bearing): slot 40's WHOLE 0x162 record is BYTE-IDENTICAL across
     the boundary (sha256 f22c12451fe74fc4d0ed7ddf.. both sides). The vendor
     never wrote that record.
  T2: changed-slot census over the full 0..0x6a window (verbatim):
     changed=[0, 1, 2, 4, 6, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
     21, 22, 23, 25, 26, 27, 28, 29, 30, 31, 34, 35, 36, 37, 38]
     (ships genuinely moved/refuelled across a turn — a nonzero census is
     expected and is NOT the claim); s40 NOT in changed; s12 IS in changed
     (the death).
     Slots 39 and 41..106 unchanged. NO compaction/shift: records did not move
     down into the corpse slot.

RECONCILIATION (the queue asked for exactly this): there is ONE end-of-life
shape in the corpus — the C4 in-place corpse (docs/re/_wip_t364.md C4, law
0x249b4..0x24a30: owner word :=0xffff, kind :=0, name(+0x34) :=0, DEC live
count) — corroborated here at s12. The "slot-vanished" reading of s40 is NOT
a second vendor shape: it is the SAME law's count decrement (41->40) applied
to an enumeration that is `range(count)`. Because the watcher (and the
vendor's own scan, r1_slot.ship_array_law / FUN_00022304) enumerates
`for k in range(min(count, 0x6b))`, a death ANYWHERE shrinks the window by
one, and the record at the OLD HIGHEST index (here 40, 'Intil-Za') falls
outside it while remaining byte-for-byte intact. The fleet-list law is what
makes this visible rather than benign: the count word is NOT the census
(ships.md S64-adjacent fleet-list item 3, MEASURED 4 live rows past a count of
30), so the orphaned record is a LIVE-looking player ship that the count-based
walk no longer reaches.

## S2 HONEST NEGATIVES (rows stay open; nothing here closes an OQ)
- The DEC word the C4 finalizer decrements, [ds:0x3067b], reads 0 in BOTH
  banks (guard u32[ds:0x30679]>>16 == 0 on both sides). It is therefore NOT
  the array count word at 0x43489>>16, and this measurement does NOT attribute
  the 41->40 decrement to 0x249b4. The decrement is MEASURED at the count word
  (40 saves, zero drift); its writer is UNATTRIBUTED. Do not wire a claim that
  0x249b4 owns the count word.
- Whether the orphaned s40 ('Intil-Za') is still in the game per the USER's
  view (fleet list UI) is unmeasured: the UI list is not the count-word walk
  (selfplay.md right-click law banked, no selection widget). The user's M5
  testimony says the ship was lost; the RAM says the record survived. Both
  statements stand; the discriminator is the UI list, unreachable here.
- Handle 0x00000000 on s40: race 0 by the t273 law (race == handle>>16), so it
  is counted live by the marker law. Whether handle 0 additionally means
  "unallocated" is NOT cited — do not infer it.

## S3 CODE CONTRACT (what lands in shipsim)
ShipSim models the array as a fixed-capacity window with an explicit count,
NOT as a compacting vector:
 1. DEATH is in place: owner := -1 (0xffff), kind := 0, name cleared,
    inventory ring UNTOUCHED (M6 law, S64 addendum: dead keeps cap/filled),
    record bytes otherwise untouched. The corpse stays at its index.
 2. The enumerated count decrements by exactly 1 per death (41->40 measured).
    NO compaction: no record moves, so the highest in-window record can be
    orphaned (byte-identical, still reachable only by index).
 3. `shipAt(i)`/index access reads the FULL capacity (the orphan is still in
    memory); the count-based walk sees only 0..count-1. That distinction is
    the artifact and must be pinned so a future refactor to a compacting
    vector cannot silently erase it.

## S4 MEASURED — THE COUNT WORD IS THE LIVE CENSUS; THE ARRAY IS NON-COMPACTING
Follow-up probe (execute_code over the same two banks, offsets cited above):

  t1253: count word 41 | live records over the FULL 0..0x6a array = 41
         | walk window range(41) = slots 0..40 holds 41 live, 0 dead.
         PACKED: count == live census == window contents.
  t1254: count word 40 | live records over the full array = 40 (ids
         [0..11, 13..40]) | walk window range(40) = slots 0..39 holds
         39 LIVE + 1 CORPSE (s12).
         UN-PACKED: count still == live census (40), but because the death at
         index 12 did NOT move any record, the window shifted one short and
         now contains the corpse while the top live record (s40) sits OUTSIDE
         it.

So the vendor array is a packed-live-record array whose count word is the live
census, and the C4 finalizer's DEC keeps `count == live` TRUE without
relocating anything — which necessarily (a) leaves the corpse inside the
window and (b) orphans the highest-index live record. ONE mechanism, two
appearances. The queue's premise "the AI death kept position with owner->0xffff
while s40 GONE entirely" resolves to: s12 is the death (owner 0x00020000 ->
0xffff0000, kind 4->0, name 'Medium'->'') and s40's disappearance is the
consequence of the count DEC at index 12, not an action on s40.

WITNESS VALUES for the pins (slot 12 across the boundary; CHANGED = the three
finalizer stores, everything else byte-identical):
  handle +0x54   0x00020000 (race 2)  ->  0xffff0000 (0xffff)   CHANGED
  kind   +0x58   4                    ->  0                     CHANGED
  name   +0x34   'Medium'             ->  ''                    CHANGED
  type   +0x67   2                    ->  2                     same
  pos    +0x9e   (1280.0,-1760.0,1344.0) -> SAME                same (frozen)
  power  +0x88   1                    ->  1                     same
  integ  +0x8c   20                   ->  20                    same
  eta    +0x52   1018                 ->  1018                  same
  invCap +0x15a  10                   ->  10                    same
  filled +0x15e  10                   ->  10                    same
  ring   +0xab   [28,28,17,43,1,36,73,43,13,13,255*15] -> SAME  same
  => the M6 "death keeps inventory" law is now corroborated at RECORD level
     (cap 10 / filled 10 / ten non-FF cidx bytes intact), not only via the
     tl row.
Slot 40 ('Intil-Za', the orphan): handle 0x00000000 (race 0), kind 1,
  pos (0,0,0), power 40, integ 40, eta 1241, invCap 25, filled 25, ring fully
  populated — byte-identical on both sides.

CORRECTION TO AN EARLIER NOTE (banked, not silently fixed): docs/re/ships.md
S64 addendum describes slot 12 as "was 'Medium' own0". MEASURED t1253 handle
0x00020000 => race 2 (t273 law: race == handle>>16), not own0. The name and
slot are right; the owner half of that sentence is wrong.

HONEST NEGATIVES (added):
- Whether a LATER turn re-packs the array (moving s40 back into the window) is
  UNMEASURED — the corpus has exactly one post-death bank. Do NOT model
  deferred compaction; the pins assert only "no compaction at the death
  boundary".
- The writer of the 41->40 decrement is UNATTRIBUTED (see S2: [ds:0x3067b] is
  0 in both banks, so it is not the count word).

## S5 MEASURED — WORD-LEVEL CORPSE DIFF: THE FINALIZER STORE SET IS 5 WORDS
Word diff of the WHOLE 0x162 corpse record (s12 t1253 -> t1254) — exactly FIVE
words differ, everything else byte-identical (172/177 words):

  +0x34 0x654d -> 0x6500   name BYTES: 'M','e' -> NUL,'e'. The store is
                           name[0] := 0, a ONE-BYTE NUL stamp — NOT a 20-byte
                           name clear. 'edium' is still in RAM; the C-string is
                           empty. (Refines C4's "+0x34 := 0".)
  +0x56 0x0002 -> 0xffff   owner WORD := 0xffff (verbatim C4). Consequence
                           pinned: handle u32@+0x54 0x00020000 -> 0xffff0000,
                           i.e. the dead marker law is the C4 word store seen
                           as the dword.
  +0x58 0x8504 -> 0x8500   kind byte := 0 with the HIGH byte (0x85, the +0x59
                           pointer's low byte) PRESERVED — so kind := 0 is a
                           byte store, and +0x59 (0x00255c85) is untouched.
  +0x5c 0x0100 -> 0x0000   +0x5d ACT := 0. NEW LEG: C4's verified disasm window
                           cited owner/kind/+0x34/DEC; the witness adds the act
                           clear. The sim already did act = 0 (previously
                           inherited) — now WITNESSED.
  +0x90 0x0006 -> 0x0000   shields u32 := 0. UNATTRIBUTED (see neg below).

  RETAINED across death (NOT cleared — the sim currently clears these three):
    +0x62 dispatcher gate  0x00 -> 0x00  (already 0 before: vacuous in this
                                          witness, not evidence of retention)
    +0x63 active slot ptr  0x00000000 -> 0x00000000 (same vacuity)
    +0x68 order payload    0x002589f6 -> 0x002589f6  RETAINED (nonzero before,
                                          nonzero after: real evidence)
    +0x67 order type       2 -> 2        RETAINED
    +0x88 power 1->1, +0x8c integrity 20->20, +0x52 eta 1018->1018,
    +0x18 powerMax 8->8, +0x9c status 0->0, ring cidx x10 AND ring USE-WORDS
    [0,0,0,0,1,0,0,0,0,0] -> IDENTICAL.
  => The rewrite's death finalizer must NOT clear +0x68 (and the +0x62/+0x63
     clears are unwitnessed hygiene, not law). The M6 "death keeps inventory"
     law now holds at USE-WORD level too, not just cidx/cap/filled.

HONEST NEGATIVES (S5):
- CAUSE of the s12 death is UNATTRIBUTED. integrity 20 == maxIntegrity-side
  value UNCHANGED across the boundary means this corpse was NOT produced by the
  hull<1 path (a hull kill leaves the clamped hull on the record; C4 touches no
  integrity field). So the corpus shows the death FINALIZER shape shared by a
  producer this capture does not identify. The sim's hull-kill path stays the
  only modelled producer; do NOT add "integrity := 0" to the finalizer.
- +0x90 := 0 cannot be attributed to the death path: the turn tail's upkeep
  zeroes +0x90 ALWAYS then re-adds affordable cat-1 contributions (t363 law),
  so a corpse with power 1 / powerMax 8 lands 0 either way. Indistinguishable
  with this corpus — NOT wired.
- The power-REFILL law (M5: player ships refill to design max) did NOT fire on
  the corpse (power 1 -> 1, powerMax 8). Live controls s0 73->84, s14 84->90,
  s28 80->90 all refilled. The corpse is INSIDE the count window (12 < 40), so
  window membership does not explain it; the tail's skip condition for a fresh
  corpse is UNMEASURED (order of death vs tail within the end turn unknown).

## S6 RING STATE NOTE (affects future iterations, not this one's result)
work/r1/playcap/save/41..60.sav (the PRODUCTION ring) now reads turn=1254,
count=40, window range(40) live=39 dead=1, live BEYOND window=[40] — i.e. the
t1086 frozen corpus that test_shipsave_t360 case (3) pins is GONE (rolled over;
that case self-skips once turn != 1086 by design, so the suite stays honest).
The ring shape MATCHES the bank-play-20261111-late bank exactly, which is the
same game state, not an independent corpus — no extra corroboration claimed.
