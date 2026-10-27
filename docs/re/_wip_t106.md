# t106 WIP — scenario-template PRESET SOURCE for the +0x55 seed deviation

ASSIGNMENT (STATE.md t106): the 1.37% of samples where WORD[rec+0x55] !=
NONBARREN(surface)//3 + 5 (income-law S10/T33: 71070/72066 = 98.62% corpus,
98.63% first-save-per-distinct-world, 27 worlds). Residual signed -17..+7,
attribution "[inferred] scenario/preset-row path" is the ONLY remaining
offline-named item on the OQ-016 open set.

BINDING PRIORS (do not re-try):
- T54b [verified negative]: the 21+21-dword preset blocks @0x88f90/@0x88fe4
  ship compiled in the EXE; signature grep of the whole extracted corpus =
  0 hits. The FILE-DRIVEN per-world-row hypothesis is dead for those two
  tables.
- T55 [verified raw-asm guard law]: preset copy fires for the ONE planet per
  group whose within-group index == fresh `rng % size`, and only when the
  scenario-entry match succeeded ([ESP+0x108] >= 0). Index-uniform.
- T55 RUN [verified]: the rng%11 row is consumed at generation and NEVER
  stored; rec+0x0c = world group index, rec+0x0e = type class. So per-world
  preset attribution is NOT recoverable from save-state correlation;
  LCG-replay-only. (Any leg of this iteration must respect that.)
- R7: +0x68/+0x69 are generation constants, not the clock. Trust rel32 edges
  + rewritten-site immediates only for statics.

LEG PLAN
1. Deviation census across all banked corpora (first save per run): per-world
   d = r55 - (nb//3+5); is the deviating set a FIXED world-name set? Does it
   cluster on size/row/cells/owner? Correlate +0x16 vs table-B row list.
2. +0x55 writer census (r1_t86_write_census.py 0x55) + targeted look at the
   scenario loader region FUN_00037fc0..0x3830c for a store into +0x55 or a
   template row copy; check whether the 0x744a8/0x744f4 runtime tables are
   image constants or file-loaded (T54b covered only the 21-dword blocks).
3. Model sweep for the deviating worlds: does d fall out of a count-CONVENTION
   difference (ring cells forced class 1 @0x37f0e; rock-bit class|8; slot-cap
   cells) rather than a preset source? Score candidate count models on the
   deviating subset.

FINDINGS

P1 — DEVIATION IS RUN-LOCAL, NOT WORLD-NAME-LOCAL (refutes the scenario-name
   attribution premise). scripts/r1_t106_deviation.py on the r1deep corpus
   (15 runs x first save, 2320 planet samples, 43 deviating = 1.85%):
   - 7 of 15 runs have ZERO deviating planets (151-161 planets each); the
     rest have 1..15 (r1deep-20261005-233706: 15/167 = 8.98%).
   - 424 distinct world names; only 41 ever deviate; names deviating in EVERY
     sample where they appear (n>=3): ZERO. Top name deviates 2/13 times.
     An authored/preset-per-world source would make the SAME name deviate in
     every run (grids are per-world); it does not.
   - deviation is NOT concentrated on any +0x16 row (0.58%..3.00% across rows
     0..10, i.e. flat) and NOT on any size class (1.17%..2.76%).
   - ALL 43 deviations are on UNOWNED planets (owner 0xFF: 43/2227 = 1.93%;
     owned planets 0/93).
   Count-convention sweep on the deviating subset: M2 (exclude word==8 =
   barren|rock) 5/43, M3 (non-zero over full slotcap) 1/43, M4 (exclude any
   rock-bit cell) 12/43 but M4 destroys the global law (27.84%) — no count
   convention explains the subset.
   Next: are the deviating planets' stored slot-array pointers UNSTABLE across
   saves in the same run (banked S10 line 678-682 "slot-array pointer moving =
P2 — DEVIATION IS FROZEN FOR THE RUN (rules out mid-game mutation AND aliasing
   for the residual set). scripts/r1_t106_drift.py --runs
   work/r1/r1deep-20261005-233706 (the 15-deviation run, 20 saves): all 15
   deviating planets carry a SINGLE surface-word fingerprint across all 20
   saves and a constant d (Aglarond IV d=-17, Aglarond I +4, Pulveran III -5,
   Ephemera I..IV +1/+1/+1/+2 ...). words MOVING = 0, so neither candidate A
   (terrain writers) nor B (extraction aliasing) applies. The residual is a
   GENERATION-TIME property of that run's world instance.
   STRUCTURE: deviating planets CLUSTER BY STAR SYSTEM within a run (Aglarond
   I/II/IV/V, Ephemera I/II/III/IV, Pulveran I/II/III/IV) — but with different
   d per planet, so it is not a uniform per-system offset.
   Since P1 shows grids are per-run-instance (banked R11: 410 names carry
P3 — DUMP: the seed word agrees with the stored +0x16 ROW but not with the
   GRID (scripts/r1_t106_dump.py, run r1deep-20261005-233706 save 50.sav,
   H=0x1bf4d8). Aglarond IV: row=0 = [100,0,0,0] (all-barren) and r55=5
   (= 0//3+5, exactly "generator counted ZERO non-barren") — the two
   generation OUTPUTS agree — yet its slot window shows 53 non-barren cells
   (d=-17). Sibling Aglarond III (row=9, size 0) d=0. So the deviation is NOT
   "seed computed from a different row": the seed+row pair is coherent, the
   SLOT ARRAY is the odd one out. Two live candidates:
     (i) the record's +0x10 array pointer does not own the window the
         generator counted (shared/aliased array, or window at a different
         offset/size);
     (ii) the grid was written by a second path after the seed store.
   Note name COLLISIONS exist: "Aglarond I" appears twice in ONE save with
   different grids (size 2/row 6 and size 3/row 10) — the name field is not a
   world key, so P1's 424-name statistics are a lower bound on distinct worlds
   and per-name tests are muddy by construction. Per-PLANET-RECORD keys
   (record base + array pointer) are the valid unit.

P4 — ALIASING REFUTED as the explanation. scripts/r1_t106_alias.py over ALL
   banked runs (first save each; 46 runs, ~7000 records): shared array
   pointers are RARE (0-4 per run) and explain 6 of 322 seed-law failures;
   316 failures sit on arrays owned by exactly ONE record.
   RUN-LEVEL SHAPE (same tool): failures-per-run is bimodal — 10 runs have
   EXACTLY 0 (r1sav-*, several r1deep), typical arms have 1-8, outliers
   r1thr-20261012-023112 = 78/153 (51%), r1thr-013404 = 13, r1thr-010746 = 12.
   A run-level switch shape points at a scenario/ruleset option, not per-world
   data. NB the r1thr/r1size/r1dens arms are MUTATION arms (mapgen.md 127-132
   maps r1size arms to star-cluster density options; savegame.md 98 says
   r1thr-001410 had rev1 injected) — the high-failure arms are the injected /
   special-mode ones, consistent with T30's special-mode preset path.

P5 — THE 78-FAILURE OUTLIER IS INJECTION-CONTAMINATED; the bimodality is
   partly an artifact. work/r1/r1thr-20261012-023112/inject.log: RESUME.GAM was
   MUTATED before this run ("chain recs 78 stars 29, injected stars
   owner=0", rec0 Xerxes I -> HERMESSEN). It and the six other r1thr arms +
   r1mut-092253 carry inject.log and are NOT clean new-game corpora for a
   generation-law study (savegame.md 98 banked the same caveat for 001410).
   Clean (no inject.log) runs still fail 0..10 planets (r1deep-20261007-222504
   8/161; r1ad-20261011-122006 10/147), so a residual exists in clean arms, but
   any statistics that include the injected arms are contaminated.
   COVERAGE CHECK on the row-0 coincidence read of Aglarond IV: its slot window
   has 20 class-1 RING cells (cells=73, cap=83) and nb=53; if the seed had
   counted the ring too, r55 would be 25, not 5 — the ring-count convention is
   excluded for this record. The stored row says 100% barren while the grid is
   73% non-barren, and r55 matches 'row says all barren' — but under the R11
   RETRACTION the save-time +0x16 row is NOT trusted as the generation row, so
   that coincidence is weak evidence. Decisive route = the +0x55 writer census.

P6 — TOOL BUG FOUND (affects the banked r1_t86 census method, not its t86
   conclusions only its coverage). r1_t86_write_census.py disassembles a 48-byte
   window at `addr & ~0xF`; objdump starts decoding at the WINDOW BASE, so when
   the base is not an instruction boundary the decode stream desynchronizes and
   the real site is "rejected" (R7 mid-instruction pattern, self-inflicted).
   PROOF: the world-gen seed store is at 0x37f9a (`66 89 46 55` =
   `mov WORD PTR [esi+0x55],ax`, objdump from 0x37f80 shows it cleanly), window
   base 0x37f90 is mid-instruction => dis_at(0x37f9a) returns None => the census
   reports only 8 verified writers for +0x55 and OMITS the seed writer itself.
   Fix used this iteration: r1_t106_writers.py tries all 16 window alignments
   per candidate and accepts a site only when some alignment decodes an
   instruction STARTING exactly at the address.
   STATIC SITE ALREADY IN HAND (world-gen writer, income-law S10 line 652-654,
   re-verified by objdump this turn): 0x37f84 mov edx,ecx / 0x37f8b idiv ebx
   (EBX=3) / 0x37f97 add eax,5 / 0x37f9a mov [esi+0x55],ax / 0x37f9e mov
   [esi+0x4a],ax. Note 0x37f8d/0x37f93 pre-set +0x52=0xFFFF, +0x54=0xFF and
   0x37fa4 sets +0x57=0xFF (owner) — i.e. this is the UNOWNED-record init path,
   consistent with P1's "all deviations on owner 0xFF".

P7 — WRITER CENSUS +0x55 COMPLETE (scripts/r1_t106_writers.py, encoding bug
   fixed: t86's encodings() never prepended the 0x66 operand-size prefix, so
   NO 16-bit word write was ever in its candidate set — the banked "10 verified
   sites" for 0x42 etc. were BYTE-writes only. Corrected census: candidates=39,
   verified=12):
     0x37f9a mov [esi+0x55],ax   world-gen seed (ecx/3+5)        [S10 CLOSED]
     0x39224 add [esi+0x55],0xa  Lush Growth Bomb +10 once        [S10 CLOSED]
     0x44054 mov [edx+0x55],cx   event scan +2                    [S10 CLOSED]
     0x3a664 mov [ebp+0x55],ax   ** the only word writer outside the closed
                                  trio ** — income-law.md:104 banks it as
                                  "assembly context 0x3a609..0x3a664" of the
                                  colonization walk. If it copies the SEED word
                                  planet->planet, it is a fourth carrier path.
     + eight BYTE add sites (all in image-mapped string/alloc regions 0x58005,
       0x663c0, 0x667f4, 0x67ab5, 0x71630, 0x757cf, 0x82d6a, 0x845a0 — data,
       not planet-record code [inferred from function ids 8631/303/1160/...]).
   Reading 0x3a609..0x3a664 next.

P8 — THE FOURTH WRITER IS A PLANET-RECORD CONSTRUCTOR, NOT AN EVENT
   (scripts/r1_t106_writers.py + objdump this turn). Site 0x3a664 sits inside
   FUN(0x3a558, size 498 per work/functions_full.tsv) whose body is a pure
   STRUCTURE COPY: fields from a caller stack block at the SAME offsets as the
   planet record — +0x00/+0x04/+0x08 u32, +0x0c/+0x0e/+0x14/+0x16/+0x18/+0x1a/
   +0x1c/+0x1e/+0x20/+0x22 u16, name +0x24 via `rep movsd` ECX=7 + `movsw`
   (0x3a5fe..0x3a60f, i.e. 30 bytes = the 60B? no: 7*4+2 = 32 bytes), then
   +0x42..+0x67 word/byte/dword copies INCLUDING +0x55 (0x3a660 mov eax,[esp+
   0x55] / 0x3a664 mov [ebp+0x55],ax).
   CALLERS (rel32 census, 2 sites): 0x258dd (inside a loop over
   WORD [eax+0x27283] — a star/planet COUNT field, the generation-loop shape)
   and 0x26044 (region boundary unreadable in a short window — the copy starts
   mid-instruction, R7 pattern; needs a from-0x26000 read).
   0x258dd and 0x26044 sit BETWEEN the scenario-init loop (0x23a20..0x23d22,
   T30) and 0x37d80 — i.e. this is the record-materialisation path that takes
   a PARAMETER RECORD (stack or table) and instantiates the planet.
   CONSEQUENCE FOR THE RESIDUAL: if the parameter record for a preset/scenario
   world carries a grid from DATA while +0x55 comes from the world-gen seed
   default, the grid and the seed word are DISJOINT SOURCES and the seed law is
   only a GENERATED-WORLD law. Aglarond IV fits exactly: +0x16=0 and r55=5
   ('row says all-barren, seed counted zero') while the window holds a rich
   73%-non-barren grid.
   DECISIVE TEST (data-join): extract each deviating planet's surface-word
   sequence and find it in the extracted data corpus + the restored image; then
   check whether non-deviating planets' grids are EVER found (control). A preset
   world's grid must come from a TABLE, a generated world's from the rng.

P9 — DATA-TEMPLATE JOIN NEGATIVE (scripts/r1_t106_srcscan.py v2; v1 was
   invalid — it searched the stride-4 COMPRESSED class sequence which exists
   nowhere contiguously, every hit was a -1 artifact; disclosed before use).
   Searching the CONTIGUOUS slot block m[arr..arr+4*cells] for 29 deviating and
   72 control planets across the r1deep corpus: DEV external hits 3/29,
   CONTROL external hits 12/72 — the deviation set has a LOWER external-hit
   rate than the control, i.e. no signal. Combined with T54b (the 21-dword
   preset blocks are EXE constants, 0 corpus hits), the "grid loaded from a
   scenario data file" route is NEGATIVE in the banked corpora.

P10 — FRAMING CORRECTION THAT DISSOLVES MOST OF THE RESIDUAL: the "first-save
   per world" samples used for the 98.63% law are NOT turn-0 snapshots — the
   banked first saves are saves 41..56 of each capture (deep runs start at
   t~1254-equivalent campaign states; r1deep first save = 41.sav..50.sav).
   Generation-time laws were therefore being tested AFTER 40+ turns of event
   modifiers. The banked +2 event scan (S10 @0x4402a..0x44058) and the item-37
   +10 law are exactly the kind of writer that produces +/- residuals against a
   generation law measured late. Supporting: P1 (deviations uncorrelated with
   row/size/name), P2 (frozen for the run = applied before the capture window),
   P4 (aliasing explains 6/322).
   The remaining structural question is therefore narrow: is there a +0x55
   writer that can store an ARBITRARY value (not +2/+10/seed)? The corrected
   census P7 leaves exactly one: 0x44054 `mov [edx+0x55],cx`.

P11 — +0x6b "DISCRIMINATOR" IS SAMPLING NOISE (self-caught before banking it
   as a finding). Full-corpus recount (54 clean runs, 8282 records):
   +0x6b==105 occurs ONCE (1/204 dev) vs 0/8078 ctrl; dev is otherwise 0 like
   ctrl. The first per-offset diff tool had no significance threshold — patched
   lesson: any per-offset distribution diff over ~200 vs ~8000 samples needs a
   two-proportion test (z=6.29 from ONE record is a single-event artifact, not
   a path marker). VERDICT OVERTURNED: header sets are indistinguishable.

P12 — SCOPE OF THE CENSUS BUG (checked, not assumed). The t86 byte-pattern
   bug (P6/P7) is specific to r1_t86_write_census.py. scripts/
   r1_t99_maint_census.py instead greps a TEXT disassembly stream for
   "+0xNN]" and classifies stores by mnemonic, so 16-bit writes DO appear
   provided its single objdump stream stays aligned at the target — a
   DIFFERENT (alignment-only) failure mode, milder. scripts/
   r1_0x54_writer_sweep.py has no 0x66 handling in a pattern generator at all
   and was not re-verified this iteration [unverified]. AUDIT TASK for a later
   turn: re-run every banked "writer census accounted" claim through the fixed
   r1_t86 / r1_t106_writers and flag any offset whose word writers were never
   enumerated (candidates: the +0x88 power, +0x5d order state, +0x66 flags).
   RETRACTION DISCIPLINE NOTE: an earlier draft of P12 asserted the t99 tool
   was byte-blind too; reading its source disproved it pre-commit.
