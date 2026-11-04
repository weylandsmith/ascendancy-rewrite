# WIP t181 — OQ-003 THREE-CLASS RAM DIFF (packed-entropy residue)

Session: 2026-10-28 ~16:15 EDT. Fresh session; resumed from docs/STATE.md alone.
Trigger: idle probe armed on PROMPT-CONTENT CHANGED only (no new capture —
live-timeline.jsonl mtime_ns == baseline 1793043841304000000, size 5691796463;
dosbox procs none). So the assignment is STATE.md NEXT ACTION = t181, no
sitting re-ingest needed (scripts/r1_t85g_sitting.py NOT run).

## The question (ledger wording, OPEN-QUESTIONS.md:157 OQ-003 + :197)
All field MEANINGS of the .gam planet record are closed; the ONLY residue is
"packed-entropy regions" (star-map heads class, shared with OQ-005). Working
theory under test: the save writer copies dirty memory, so those regions are
leftover uninitialized RAM, not game data.
Test (per STATE + the PLAIN restatement t179): compare the same byte region
across three classes ALREADY ON DISK —
  (i)   title-boot idle ring slots  = pre-game uninitialized baseline
        (proven baseline: DAT_00043510 selector reads 0xC500 garbage on title
        slots of both banked runs — r1_slot.py trust law, BLOCKED.md t82)
  (ii)  fresh New-Game saves        = load-initialized, zero play
  (iii) long campaign saves         = 01.SAV..04.SAV + RESUME.GAM + playcap ring
Verdicts: stable in (iii) but garbage in (i) => play-initialized (name later);
churns in ALL three => true writer-side residue, disclaim in savegame.md;
OQ-003 closes either way (player decision, per the row's DECISION OPTIONS).

## Artifacts on disk (inventory this session)
- dosbox STATE zips (Memory member == full guest RAM, 17,055,880 B):
  work/r1/selftest-t111-playcap/save/*.sav  (class i + ii, TL=90 title boot)
  work/r1/playcap/save/*.sav                (class iii, 26-day ring)
  work/r1/playcap-20261014-224611/save/*.sav
  work/r1/r1ad-*, r1deep-*, r1thr-*/save/*.sav (older session corpora)
- GAME-NATIVE save files (raw, not zip): work/r1/game/01..04.SAV (87-91 KB),
  work/r1/game/RESUME.GAM (87,663 B Oct 21), work/r1/SAVINGS-backup-20261014/
  RESUME.GAM (75,603 B Oct 14), game/resume.gam (81,647 B — READ ONLY, gate
  checksummed; do not modify, may read).
- Base law: SS.find_base anchor vote (r1_sav_scan.py); data-space offset law
  member addr = B + 0x82bb0 + X (OQ-011 CLOSED). OFF=0x82bb0 in r1_slot.py.

## Hand-authorship check (BLOCKED.md trap)
gate.sh:95 runs scripts/gam_probe.py but writes /tmp/gam_gate.md — it does NOT
regenerate docs/re/savegame.md. So savegame.md is safe to hand-edit. (Verified
this session by reading the gate line, not assumed.)

## FINDING A (t181, measured) — "packed-entropy" is NOT high-Shannon anywhere
256-byte block entropy over ALL seven game-native save files on disk
(game/resume.gam GOLD-2008 81647B; work/r1/SAVINGS-backup-20261014/RESUME.GAM
75603B; work/r1/game/RESUME.GAM 87663B; 01.SAV 87663B; 02.SAV 91601B;
03.SAV 88021B; 04.SAV 90527B):
  mean 1.76-2.23 bits/B; MAXIMUM block entropy across all 2,316 blocks = 5.60;
  blocks >= 6.8 b/B: ZERO (0/2316). Histogram floor: 361 blocks <1 bit/B.
So the ledger's "packed-entropy regions" (OPEN-QUESTIONS.md:197, and t50's
"+0x0a 23 distinct 0..50328 packed look") cannot mean compressed or random
BLOBS — 7.7+ b/B would be the compressed signature (tables.md:130 cites the
same threshold for restree). The residue is a handful of packed u16-shaped
FIELDS plus a MOVING mid-entropy band, characterized below.
The mid-entropy (>=5.0) blocks are NOT at fixed offsets — they MOVE between
saves of the same world and between worlds:
  RESUME-021: 0x10b00 0x10d00 0x10f00 0x13b00 0x13c00 0x14100
  01.SAV    : 0x10b00 0x10d00 0x10f00 0x13b00 0x14100
  02.SAV    : 0x11800 0x11b00 0x11d00 0x11f00 0x12000 0x14b00 0x14c00
  03.SAV    : 0x10a00 0x10f00 0x11100 0x11200
  04.SAV    : 0x11500 0x11700 0x14800 0x14d00
  GOLD-2008 : 0xf900 (5.07) only.
A format field does not move. This is the first positive evidence FOR the
writer-copies-RAM theory (the theory the row is about), and it is measurable
without any capture.

## FINDING B (t181, measured) — same-world save pair localizes the mutable set
RESUME.GAM(Oct21) vs 01.SAV(Oct21), identical length 87,663, same world
(293 shared CP437 name tokens; A-only/B-only extras are 2-3 char noise):
2,874 differing bytes = 3.28%, 1,603 runs, LONGEST RUN 16 BYTES (0x15516),
no 256-byte block fully different. Diff mass clusters in 0x9500..0xd100
(the banked contiguous PLANET POOL 0x8e0e..0xd05c, savegame.md t80) and in
0x13b00..0x15500 (the mid-entropy band). Implications: (1) the save is
near-fully reproducible for one world, so the entropy band is the exception,
not the rule; (2) no region of the save is wholesale-session garbage — even
the band is only ~70/256 bytes different per block.

## FINDING C (t181, measured) — pre-load baseline vs loaded: the world tables
## DO NOT EXIST at title boot (class (i) is empty, as the task assumed)
32-byte needle at RESUME.GAM(Oct21) file 0x2146 (planet "Hope" name field,
verbatim A[0x2146:0x2166]) searched across all 49 zip slots of the three
playcap runs (base vote B=0x1bf4d8 unanimous in every slot):
  playcap-20261014-224611 (title boot, t=0 score=0, 20 slots): NOT FOUND.
  selftest-t111-playcap (loaded world, no play, 9 slots): FOUND at member
    0x255f69 (== B+0x96a91 == P0+0x96989, P0=B-136=0x1bf450).
  playcap (loaded world, played, 20 slots): FOUND at member 0x255f69 (same).
So class (i) proves the planet tables are allocated at game start, not present
at boot — the "pre-game uninitialized baseline" reading is correct, and it
also means class-(i) slots cannot be byte-compared region-by-region against a
world (there is no world). The usable three classes are therefore: FILE
(as written) / BOOT-A RAM (selftest, same world file, zero play) / BOOT-B RAM
(playcap, same world file, ~123 turns played) / title-boot RAM (unallocated).
Both boots loaded work/r1/game/RESUME.GAM (mtime Oct 21 02:27, never rewritten
by either session — the ring writes dosbox states, not game saves).

## FINDING D (t181, measured) — the save is a MULTI-BLOCK image, not one blob
512-byte chunk-verbatim scan of RESUME.GAM(Oct21) against playcap slot 41 RAM:
30/171 chunks verbatim. Chunk 0x11200..0x12600 is verbatim CONTIGUOUS (5,120 B
at constant delta 0x2b6718 == P0+0x233b68), while the planet-name region sits
at delta 0x234e23 (0x255f69 - 0x2146). Different file regions therefore land at
DIFFERENT guest addresses — the writer serialises separately-allocated blocks,
each with its own runtime base (consistent with t53 item 4: pointer fields
survive verbatim, are not rebuilt). Consequence for this task: any file<->RAM
region comparison must discover a per-region delta, never assume one.

## FINDING E (t181, measured) — pool deltas are ARITHMETIC, band deltas are not
Aligned-u32 census of the same-world pair (RESUME.GAM Oct21 vs 01.SAV Oct21):
  PLANET POOL (0x8e00..0xd100): 967/4288 u32 differ; top deltas
    0xffffff00(x22) 0x02000000(x21) 0x00010000(x19) 0x00000100(x17)
    0xffff0000(x17) 0xffffff81(x16) — byte-lane-stepped small changes, i.e.
    REAL COUNTERS being advanced/set between the two saves.
  ENTROPY BAND (0x13800..0x15800): only 101/1947 u32 differ; top deltas are
    singletons/noise (0x2 x5, 0xffffffff x4, 0x10000 x4). Values are FULL-RANGE
    (byte-length hist: 1B:243 2B:127 3B:223 4B:355 of 950 nonzero) and the
    differences are ASYMMETRIC-ZERO: RESUME 0x13ca2 = c511a487/c5da76c9 where
    01.SAV = 00000000/00000000, and conversely 01.SAV 0x154d6 = b2895798/
    3f07a8ca where RESUME = 0. b2895798+3f07a8ca also recurs verbatim at
    01.SAV:0x15516 (+0x40), so within a save the residue repeats mechanically.
    Float reading of the RESUME pair: c511a487 = -2346.6, c5da76c9 = -7087.9
    [inferred shape-match only, no claim made].
Interpretation: the band is NOT a format field block (fields do not appear in
one save and read as zero in another at the same offset; fields do not move).
It is session-variant copied memory — the writer's source for that span holds
whatever the process had there. This is the writer-copies-RAM theory MEASURED,
not assumed. (Contrast with the pool, which is stable world+play state.)

## FINDING F (t181, DECISIVE) — three-class diff at the save's located RAM
## addresses: the entropy band churns in ALL THREE classes => WRITER-SIDE
## COPIED MEMORY, disclaim. World tables do NOT churn.
Method: both in-game boots loaded the SAME world file (work/r1/game/
RESUME.GAM, Oct 21 02:27) — boot A = selftest-t111-playcap (New/Load, ZERO
play, all 9 slots t=1131), boot B = playcap (same world, ~123 turns played,
score 14). The chunk map of the file against boot-A RAM locates each save
region at its own guest address (delta per block, FINDING D):
  0x00200..0x01600 d=0x2b6718 (P0+0xf72c8)   header block
  0x02000..0x03000 d=0x253e23 ; 0x03200..0x09000 d=0x25676f (P0+0x9731f)
  0x09200..0x0d600 d=0x263fb1 (P0+0xa4b61)   PLANET POOL (+ 0xd600..0x11200
                                              same delta, 71.3% file-match)
  0x11200..0x12600 d=0x276b0c ; band 0x13c00..0x15200 d=0x2d3a0e (P0+0x1145be)
Same-address comparison boot A vs boot B over those spans:
  region      len     A==B same-addr   file==A
  HEADER      7168    99.7%            100.0%
  S-TABLE     24064   93.8%            100.0%
  POOL        17408   87.2%            100.0%   (diffs = play counters,
      e.g. file aff8a5c4 -> booted 04ff8a5c4 — arithmetic, FINDING E)
  B11200       5120   100.0%           100.0%
  BAND 0x13c00 5632   35.3%            100.0%
The BAND is byte-exact from the file into boot A (load = memcpy), and 64.7% of
it holds DIFFERENT full-range values at the same address after a played
session; boot B also relocated its own band elsewhere (96B needles from the
band find the boot-A copy at 0x2e760e and a duplicate at 0xfdca1c, nothing in
boot B). Across the FILE class the band churns between same-world saves
(FINDING E: asymmetric zeros at identical offsets, repeating mechanical value
pairs) and its >=5.0-b/B blocks MOVE offsets between worlds (FINDING A:
RESUME-014 has NO block >=5.0 at all, GOLD-2008 has exactly one).
Class (iii)/title-boot: tables unallocated — the 0x2146 needle is absent from
all 20 title-boot slots (FINDING C), and RESUME-014 (Oct 14) has no verbatim
presence anywhere either (FINDING C needle method).
VERDICT (measured, all three axes): the packed-entropy band satisfies the
task's disclaim test — it churns in every class (title = unallocated,
zero-play saves differ at the same offsets, played sessions overwrite it
in place at 64.7%). It is writer-side copied memory / scratch state, NOT a
save-format field set. The world tables (header, S-table, pool, 0x11200 block)
are the opposite: 87-100% stable across a 123-turn session and file-verbatim
at load — they are real serialized state and stay mapped as such.
LEAD banked honestly (NOT a claim): the band's byte stream parses as a run of
IEEE-754 f32 PAIRS with plausible magnitudes (pairs like c511a487/c5da76c9 =
-2346.6/-7087.9; boot-B d6c51013.. = -18401,-53308,-32700 per pair) — i.e. it
looks like a geometry/coordinate scratch buffer (star-map class per the
ledger's "star-map heads" hint) that the writer's block span happens to
cover. Naming it needs a live-UI trace; the row does not need it.

## Method notes / discipline
- STREAM: entropy computed in-process per region; never dump file bytes here.
- No second long capture; no game/ mount; no new capture at all this iteration.
- R12 (docs/REFUTED-ROUTES.md:146): absence of Ghidra xrefs is uninformative —
  so a static "no reader found" is NOT evidence of residue. Only cross-class
  byte measurement counts.

## CORRECTIONS to this WIP (apply when reading; final verdict is
## docs/re/savegame.md §t181, tool scripts/r1_t181_banddiff.py)
1. FINDINGS C/D as written here are SUPERSEDED, not withdrawn: the earlier
   chunk scan hit `mem.find(b'')==0` artifacts — RESUME-014 is 75,603 B
   (EOF 0x12753), so its "chunks verbatim in title slots" (incl. at member 0)
   were empty-slice matches. WITHDRAWN. scripts/r1_t181_corr.py (length-
   checked, content-bearing needles) shows title-boot slots DO carry the
   OCT-14 on-disk world verbatim (delta 0x25676f at 0x25996f/0x25a76f):
   class-(i) is NOT world-free. The multi-block/multi-delta FACT stands
   (re-measured cleanly by scripts/r1_t181_banddiff.py).
2. FINDING E float lead REFUTED by shape census: 13% (band) vs 5% (pool
   control) sane-f32 u32, 9% vs ~0.4% sane pairs — no coordinate claim.
3. FINDING F band stability 35.3% (wide span, mixed sub-deltas) refined to
   432/2048 = 21.1% at the clean constant-delta region 0x14000..0x14800.
   Verdict direction unchanged and strengthened: DISCLAIM.
