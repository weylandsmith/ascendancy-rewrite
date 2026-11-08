# t342 WIP — RESIDUE-(5) CORPUS CENSUS OF THE HUMAN BUILD QUEUE + UI-COMMAND LEG (ZERO CAPTURE)

Task: docs/STATE.md NEXT ACTION t342. Sitting check NEGATIVE (tail-seek of
work/r1/playcap/live-timeline.jsonl, newest turn 1086 == corpus; no new
sitting, so no r1_t85g_sitting.py run). Production :9 untouched; game/
read-only.

## S0 — LAWS IN USE (all banked, cited)
- heap-record law (t33/OQ-014): IL.find_records(m); rb base; name rb+0x24;
  OWNER BYTE rb+0x57 (== NAME+0x33, t248); queue cell WORD rb+0x52; queue
  item BYTE rb+0x54 (0xff=empty); acc WORD rb+0x50; local-flag DWORD rb+0x5a;
  IND rb+0x44; cells WORD rb+0x18; slot array ptr [rb+0x10]+0x88.
- DS-seg linear = B + 0x82bb0 (t340 verified via DS+0x12e10 == turn clock).
- netplay global u32 DS+0x10ba4; local player byte DS+0x7458e.
- item gate word u16 DS+0x73e46 + idx*40 (bit8 gates completion marker, t340);
  cost word u16 at gate-entry +2 (t340/t341: item0 flag0 COST30, item26 flag8
  COST60).
- turn clock u16 phys 0x254E10 mapped off = 0x254E10 + (B - 0x1BF450)
  (r1_colony_items.py law).
- t341 CLOSED facts (binding): sole queue-pair writer fn 0x38840
  0x38af5..0x38b26; UI uses the SAME chain (0x3ae99 in fn 0x3aa0a); selector
  runs on a LOCAL-race planet iff [p+0x5a]!=0 OR ds:0x10ba4!=0 (verbatim gate
  0x3eabf..0x3eacd); event-15 refresh-only.

## S1 — CENSUS DESIGN
Instrument scripts/r342_queue_census.py: per save dir (whole work/r1 corpus +
banks), per .sav: anchor-verified base + turn; owner histogram; EVERY owner-0
pending row (byte +0x54 != 0xff) with (name, item, cell, acc, IND, gate flag,
COST, [p+0x5a]); globals netplay/local; turn-adjacent pair diff per run dir
for the completion-then-queue signature (prev pending acc+COST-boundary ->
cur re-queued) on owner-0 planets.
ADJUDICATION:
- If netplay==0 everywhere and every pending owner-0 row has [p+0x5a]==0, the
  selector is statically EXCLUDED as their writer (gate 0x3eabf..0x3eacd) and
  the writer census (t341) leaves only the UI-command chain -> residue-(5)
  rows are player-input class -> OQ-016 residue list EXHAUSTED -> recommend
  park-on-sentinel (D3).
- If any owner-0 row shows a same-boundary completion-then-queue with no
  possible UI leg, name residue-(7) with save/turn/planet + capture design.
Corpus note: work/r1/playcap/caps is EMPTY (0 .sav) — honest negative; bank
t1254 + t340 ring-final + production playcap/save + all runs()/banks.

## S2 — RESULTS (pinned corpus: playcap + playcap/caps(EMPTY, honest
## negative) + bank-t1254 + t340 ring-final; scripts/r342_queue_census.py
## exit 0, work/r342_census_pinned.out; --all full-corpus run in flight
## work/r342_census_all.out)

S2.1 GLOBALS: netplay ds:0x10ba4 == 0 in 60/60 saves; local-player
ds:0x7458e == 0 in 60/60. Owner-0 record counts/save: playcap 80,
bank-t1254 102, t340 80 (matches t248/t341 histograms).

S2.2 PENDING owner-0 rows (item byte +0x54 != 0xff): 4891 total
(playcap 1600, bank-t1254 2020, t340 1271). Item histogram:
{0:299, 1:100, 6:1679, 7:180, 8:448, 21:20, 23:40, 26:60, 27:240, 28:59,
30:180, 33:40, 34:880, 35:266, 36:360, 38:40} — ALL real item ids 0..38,
no junk/>=39. *** [p+0x5a] == 0 in 4891/4891 PENDING ROWS *** -> with
netplay==0 the t341 verbatim gate 0x3eabf..0x3eacd STATICALLY EXCLUDES the
vendor selector (FUN_0003f130 via 0x3ea54) as the writer of EVERY observed
pending owner-0 row. The t341 writer census leaves the UI-command chain
(0x3aa0a -> 0x38818 -> 0x38840) as the only non-reset writer class.

S2.3 MY FIRST-PASS ANOMALY FLAGS COLLAPSE TO KNOWN-NORMAL LAWS (verified
by correlation, work/r342_census_pinned.out + inline probe on 41/45/58.sav):
- cell-ffff (920): 27/27 sampled are FLAG-BIT1 items {31,32,33,34,37} —
  verbatim t341 S1 writer pattern "+0x52:=0xffff then (item flag bit1 CLEAR
  -> +0x52:=cell arg)": bit1 SET keeps 0xffff. NOT an anomaly.
- cell-oob (579): sampled only item 28 Orbital Missile Base — orbit slots
  live at index >= cells (t340 law: slot>=cells skips the surface marker).
  NOT an anomaly.
- acc-over-cost (286): ONLY cost-1 items (33/34/35, cost word +8 == 1,
  runtime item table names_ok VERIFIED). Completion-gate explanation in
  progress (S2.5).
Runtime item table (this save set): item 0 Factory cost 30, item 26 Orbital
Shield cost 60 — t340/t341 measurements reproduced.

S2.4 TRANSITIONS (adjacent-save, dt==1, per owner-0 planet): PROGRESS 188,
DRAIN 5, FRESH-QUEUE 0, SAME-ITEM-REQUEUE 0, NEW-ITEM 0,
*** complete-then-requeue signature on owner-0: 0 events ***. HONEST
CAVEAT: ring dirs are saved in RING order not turn order — pairing must
sort by turn; --all rerun with fixed pairing pending (S2.6).

## S2.5 — THE acc-over-cost CLASS IS THE GOVERNOR-ITEM CLASS (t45 law),
## NOT ANOMALOUS (cited per-profile census over playcap + t340 saves):
per-item profiles (n, acc range, distinct accs, cell range, "already built
in slot" saves):
  item 0 Factory    n=279 acc 1..29  (COST 30) cells 4..33   in_slot 279
  item 6 MegaFac    n=1159 acc 0..108 (COST 110)             in_slot 1159
  item 34 SciTko    n=360 acc=0 ONLY cell=0xffff ONLY in_slot 0
  item 35 Automation n=166 acc 0..105 cell 1..71 in_slot 0
  (items 33/34/35 = Endless Party / Scientist Takeover / Automation,
  runtime item table names VERIFIED, cost word +8 == 1 for all three.)
- item 34 rows (acc==0, cell==0xffff, never in any slot) match the BANKED
  mode-3 UI law EXACTLY: income-law.md S (t45 closure) "a governor value
  33/34/35 arises only when the player/AI cell-SELECTS a special item
  (§413 mode 3 writes +0x54 := item idx)" — a pure +0x54 write, no cell,
  no acc. That is the UI-command leg, not a vendor queue op.
- item 35 acc GROWS +IND/turn on human planets (Mukwonago I t1089..1091:
  acc 45->60->75, IND=15 verbatim) — the queue accumulator 0x3909f
  `add ecx,eax; mov [esi+0x50],cx` runs while +0x54 != 0xff, and the
  completion/marker gates are FLAG-BIT tests (0x38fc1 requires gate-word
  bit 0x4; t340's marker block 0x3924c requires bit 0x8) — governor items
  (flags 0x22/0x01) are NOT normal constructions; they persist as +0x54
  governor state (t45 branch law 0x38e00/0x38e0b/0x38e16 fires every
  recalc while set). acc>COST(1) is therefore NOT a completion-boundary
  violation; it is the governor-state accumulation. [static + measured]
- ALL other pending items have acc <= COST and cells in range -> ordinary
  construction rows (Factory/Agriplot/MegaFac/Hydroponics/Research Campus/
  Orbital* /Terraforming/Xeno — all UI-orderable).
## S2.5b CORPUS-GLOBAL [p+0x5a]: histogram over ALL owner-0 rows (not just
## pending): {0: 5240} — ZERO nonzero in the pinned corpus. Combined with
## netplay==0 (60/60) the t341 gate 0x3eabf..0x3eacd excludes the vendor
## selector from EVERY owner-0 row in the pinned corpus.
## S2.6 — PINNED-CENSUS FINAL NUMBERS (scripts/r342_queue_census.py exit 0,
## work/r342_census_pinned.out; turn-sorted pairing + AI positive control):
- owner-0 pending rows 4891; [p+0x5a]==0 in 4891/4891; netplay 0 in 60/60.
- anomalies after law-correct classification: ONLY 40 rows, all bank-t1254
  item 23 (Ship) on Vega II/IV acc 1424/1190 vs item-table COST 20 — FALSE
  POSITIVE by the banked t27 law (income-law.md S8: "item 23 (Ship) costing
  the ship-design value (FUN_000396cc/FUN_0004a41c)"; measured slot word2
  0x2700/0x2800 bit0 CLEAR = the ship is in-construction at bank time t1254,
  acc is the industry total toward the design cost, frozen because the bank
  saves are all the SAME turn t1254 (20 copies)). NOT residue.
- governor acc-over-cost rows (t45 law, normal): {35: 246}.
- orbit-slot rows informational: {23:40, 26:60, 27:240, 28:59, 30:180} — all
  orbital item classes (t340 slot>=cells law).
- owner-0 transitions: PROGRESS 247, DRAIN 8, FRESH-QUEUE 0, SAME-ITEM-
  REQUEUE 0, NEW-ITEM 0; complete-then-requeue on owner-0: 0.
- *** POSITIVE CONTROL (AI rows, same instrument): NEW-ITEM 3, PROGRESS 73,
  boundary re-queue 3 — Gridsor I t1090->1091 (item 26 acc 54+6>=60 -> item
  0 queued, the t340/t341 witness reproduced), Arcturus I t1090->1091
  (item 8 acc 154+11>=160 -> item 20), Sarsaparilla III t1092->t1093
  (item 20 acc 114+6>=120 -> item 8). The signature the instrument hunts
  FIRES on AI planets and NEVER on owner-0 planets. ***
- ALL 8 owner-0 DRAINs are COMPLETIONS with the slot activated (slot word2
  bit0 SET next save: Smorgasbord III, Delphinius II, Pulveran I (item 35 ->
  word2 0x3 = Automation |=2 law verbatim), Elwyssen I, Crimea I, Gravitus
  III (word2 0x101), Zilker II, Ribulon III) — and NONE of the 8 is followed
  by a new queue row in the same boundary (queue word 0xffff/0xff next save
  in all 8; the NEW-ITEM class on owner-0 is ZERO). Completion-then-queue is
  an AI-selector behavior; the human completions drain to empty and STAY
  empty until a click — the t341 13/13 law widened to the whole pinned
  corpus (0 counterexamples).
## S2.7 UI-COMMAND LEG VERBATIM (fn 0x3aa0a = planet-window command fn):
- 0x3ae72 gated ds:0x10ba0!=0 (nougat debug flag, debugflags.md) -> 0x3ae99
  call 0x38818 (debug build only).
- 0x3b0d1 (colonize path: sets owner [edx+0x57], pop :=2, star OR-bit — the
  t248/t249 laws) call 0x38840 directly.
- 0x3d887 (ship-design path via 0x396cc) call 0x38840.
- Other 0x38840 callers inside fn 0x3aa0a: 0x3b349/0x3b411/0x3b482/0x3c9fc/
  0x3ca44/0x3daa9 (queue-edit UI arms). fn 0x3a174 callers 0x3a3f0/0x3a455
  (demolish/rebuild family: slot byte==0x12/0x13 + active-bit gates).
- fn 0x38f68 caller 0x3a12d = the demolish-completion site (0x3a153 reset
  tail after). None of these legs is gated on [p+0x5a] or on owner — they
  are the PLAYER's window (ds:0x43508 = current window record), i.e. writes
  reachable ONLY through posted UI messages (t305 banked: msg-0x8 pump on
  PLANETALLOC/PLIND window records).
=> Every pending owner-0 row in the corpus is either (a) an ordinary
construction row (UI-order class, cell valid, acc<=effective COST), (b) a
governor value 33/34/35 (t45 mode-3 UI law: pure +0x54 write, cell 0xffff
for 34, never in slot), or (c) frozen bank-state ship row (t27 ship-cost
law). ZERO rows require a vendor-selector write, and the selector is
statically excluded anyway (gate + [p+0x5a]==0 + netplay==0).
## S2.8 FULL-CORPUS CONFIRMATION (scripts/r342_queue_census.py --all, exit 0,
## work/r342_census_all.out, every work/r1/* dir): 3324 saves, 144,302
## owner-0 pending rows — [p+0x5a]==0 in 144302/144302; netplay==0 and
## local==0 in 3324/3324. Owner-0 transitions: PROGRESS 3955, DRAIN 138,
## *** complete-then-requeue 0 ***; AI control on the same instrument: 180
## boundary re-queues (Gridsor I x3, Arcturus I x2, Millitrin I, Flammifer
## III, Sarsaparilla III x2, Syntor IV, Amoroso I/II, Ephemera I, Highbeam
## IV, Cambria IV, Byzantium II, Vernunft I, ...). Anomaly flags beyond the
## three known law-classes: 364 rows, ALL item 23 (Ship) acc>COST-table-20
## (Xerxes I 77..112 etc.) — the t27 design-cost class again. Item
## histogram includes only real items (adds 12:9, 14:45 Hyperpower/Internet
## — ordinary constructions). NO counterexample anywhere in the corpus.
## (Cosmetic: dirs listed as '' in anomaly lines when the run-dir path ends
## with '/' — basename('d/')==''; does not affect any count.)

## LEDGER DISPOSITION (landed)
- residue-(5) DISPOSITIONED player-input class with cited measurement
  (S2.2/S2.5/S2.6/S2.7). NOT a strict-close of the OQ-016 ROW — the row
  stays open; residue list EXHAUSTED; remaining movement = user
  adjudication (D2/D3 per DECISIONS.md).
- Banked: income-law.md S-T342 + t45 corpus-correction block (S14);
  REFUTED-ROUTES t342 amendments 1-2; buildPhase comment upgraded
  (campaign.cpp, comment-only); STATE.md LANDED t342 + NEXT=t343 VERBATIM.
- Corrections learned the hard way (worth remembering): (a) item COST word
  is +8 not +2 (income-law S8 was already right); (b) ring save dirs are
  RING order — always sort by the u16 clock before pairing; (c) bank dirs
  hold 20 copies of the SAME turn (no transitions derivable, frozen rows
  are expected); (d) t45's "NEVER occur" claims can be corpus-limited —
  re-measure against the production campaign before quoting them.
