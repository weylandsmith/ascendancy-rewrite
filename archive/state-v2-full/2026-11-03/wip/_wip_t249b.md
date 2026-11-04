# t249b — DAY-COUNTER DWORD HUNT (working log)

Task (verbatim from STATE queue): the planet screen shows a day counter (user
testimony "day 1254" at turn 1254 — day may equal turn in this campaign, which
makes a same-value dword a candidate). Census dwords == 1254 in
work/r1/bank-t1254/*.sav excluding heap noise; correlate against the known turn
dword at data offset 0x12e10. If pinned, note the watcher-schema addition for
t257. If not pinned, bank the negative + candidate list. STRICT-CLOSE applies.
No ledger row is expected to move (the day counter is not an OQ row).

Instrument lineage: scripts/r1_t249_sigscan.py (base vote + record walk +
content scan), scripts/r1_slot.py (turn u32 DAT_00012e10, member = B+0x82bb0+X,
guest phys = member - 0x88).

## S1 census method
Scan every 4-byte-aligned dword of the Memory member of all 20 bank slots for
value == 1254 (and == slot turn), intersect offsets ACROSS slots: a genuine
game-state field sits at a stable member offset in every slot, heap noise does
not. Region classification: data-seg window (B+0x82bb0 .. B+0x8cc83 = obj1),
low guest RAM (< B+0x82bb0 = code+data0), heap (everywhere else, no stable
identity across slots).

## S2 Leg A — bank-t1254 intersection census (scripts/r1_t249b_dayscan.py)
20/20 slots readable, all turn 1254 (base 0x1bf4d8, member 0x1044088).
Per-slot dword==1254 hit counts min=3 max=3, INTERSECTION=3 — the entire
value-1254 population is stable across slots (game was frozen; ring slots
near-identical). Candidates:
  member 0x254e98   X=0x12e10  — THE TURN DWORD (DAT_00012e10, r1_slot law)
  member 0xfd7268   (heap; stable only within this session)
  member 0x100141c  (heap; stable only within this session)
KEY STRUCTURAL FACT: there is NO second dword in the data segment (obj1
window B+0x82bb0..B+0x8cc83) equal to 1254 besides the turn counter itself.
If the displayed day were a maintained dword, it would live in the data seg
like every other game-state scalar (turn, T, score 0x482fb, selector 0x43510)
and would have survived. It did not.
## S3 u16 census + cross-session corroboration
u16==1254 in bank: min=max=29 hits/slot, intersection 29, ZERO in the data
segment (0 of 29 at B+0x82bb0..B+0x8cc83).
INDEPENDENT CROSS-SESSION CHECK (kills the "day field hides at the same
offset in the other session" hope): u16==1086 in the LIVE ring (20 slots,
turn 1086): intersection 148, again ZERO in the data segment; u32==1086
intersection = {0x254e98 (= turn dword X=0x12e10), 0x270248, 0x100117c} —
both non-turn sites are heap. A maintained day dword shared across sessions
would sit at a fixed data-seg offset in BOTH sessions like turn/T/score do.
There is none. Day != a stored scalar.

## S4 "Day %d" string forensics (the display-format route)
- "Day %d" is NOT in the exe payload (payload scan: zero hits for any
  Day/day literal; control restree.txt hit at payload 0x85014 proves the
  scan works). It comes from static.txt: ascend00.cob blob 15 'planhelp.txt'
  / blob 20 'static.txt' off 0x269d0, entry "// 17" under a loadwin.cpp
  comment block (verbatim context read from the blob: %d of %d Species Known
  / Extinct / Your score is %d%% ... / <EMPTY> / "Day %d" / "am" / "pm" /
  Fleet / Colonies ...).
- In live RAM the string pool is loaded verbatim: "Day %d" at member 0x253032
  (X=0x10faa, str_off=0x93b5a, relocated P0+str_off=0x252faa).
- REFERRER CENSUS (all-RAM u32 scans, self-calibrated on restree.txt:
  u32==P0+0x85014 == 0x244464 found at member 0x205dab, phys
  0x205d23 == P0+0x468d3 — the known loader site exactly; calibration GOOD):
  u32 == phys("Day %d") = 0x252faa has ONE nominal site, member 0x252c74 —
  and it is a FALSE POSITIVE: the pool bytes there are ASCII "\xaa/%\x00"
  (locale date-format fragments "?/%\0H/%\0M/%\0d/%\0l/%\0m/%\0o/%\0..."),
  whose AA 2F 25 00 spelling coincides with the little-endian pointer value.
  VERDICT: ZERO genuine referrers of the "Day %d" string in 16 MB. The pool-
  relative immediate law cannot apply (the string is not in the obj1 pool —
  static.txt loads VERBATIM into the heap), so the formatter reaches it via
  a runtime-computed pointer (same instrument-class as the OQ-021 writer).
## S5 PIN — the "day counter" IS the turn dword (MEASURED, 3 legs)
Leg 1 (screenshot, vision on external display — R13-clean, not grading a
render): work/screens/t3/resumed_t247.png (live :9 session at turn 1086) shows
ONE number-bearing string on the whole screen: a large green 7-segment digital
readout at the top of the right UI panel reading "01086" == the turn number
zero-padded to 5 digits. No second day/date readout exists on the planet
screen. The user's "day 1254" testimony (t247) was this same readout showing
01254 at turn 1254.
Leg 2 (census, S2+S3): at turn 1254 the ONLY dword == 1254 in the data segment
is X=0x12e10 (the turn counter, r1_slot law); the other two ==1254 sites are
heap. Cross-session at turn 1086, same result (only 0x12e10 in data seg). A
separate maintained day scalar would sit at a fixed data-seg offset in BOTH
sessions and did not. There is no independent day dword.
Leg 3 (1 turn == 1 day, from the t244 verbatim gauge readout): "Vega IV
Research: 52 per day / Megagraph Theory will be discovered in 37 days" —
research accrues once per turn, so "days" == turns numerically; the vendor's
own display equates them.
CONCLUSION: the planet-screen day counter = turn counter dword DAT_00012e10
(member B+0x82bb0+0x12e10, guest phys = member-0x88). day := turn; no new
storage. The "Day %d" pool string (static.txt entry 17, loadwin.cpp block) is
the load-game screen's day label, formatted from the same value via a
runtime-computed pointer (zero static referrers — S4).

## S6 watcher-schema note for t257
No new field is required: scripts/r1_playcap_watch.py already emits "turn"
(from u32 0x12e10), and day == turn. If a literal "day" key is wanted for
readability it is a pure alias of turn (no separate scan). t257's "needs t249b"
dependency is satisfied — fold this alias note into the watcher work rather
than adding a second RAM read.

## OUTCOME
No ledger row moves (the day counter is not an OQ row). Task resolves POSITIVE:
day dword pinned to DAT_00012e10 with cited measurement (screenshot + two-
session census + per-day==per-turn law). Honest negatives banked: zero static
referrers of "Day %d"; the single u32 hit was an ASCII false-positive.

