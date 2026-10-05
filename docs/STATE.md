# STATE — machine-readable working memory for the loop
# Update EVERY turn. A fresh session must be able to resume from THIS file alone.
# NOTE 2026-10-04: multi-patch batches mangled this file twice (a turn-log entry
# swallowed the CURRENT FOCUS heading; entries merged). Repair-by-rewrite done.
# Rule going forward: ONE patch per region, read_file verify after.

phase: P4
milestone: 3  # 0..6 ; gate.sh keys build/test stages off milestone >= 3
updated: 2026-10-04T21:05
turn_log_recent:
  - "seed: environment installed, cob.py extracts 471 files, Ghidra+MCP wired, plan written"
  - "crash forensics (2026-10-03): ENOSPC from a 12.39 GB dosbox probe log (see
     DOSBOX RULE below). Uncommitted work lost; recovered from seed state."
  - "P1b: .bin SOLVED (16B hdr + N x 24B / 6 x u32, 7/7 exact, docs/re/tables.md).
     OQ-001 CLOSED (offset table is N not N+1; cob.py had dropped each archive's
     last file — fixed, existing 468 byte-identical). Seed's '.tsv = text .bin'
     FALSIFIED. LESSON kept: verify the number, then write the sentence; never
     write read_file LINE_NUM| output back into source (deleted shp_probe.py once)."
  - "P1c: .shp CONTAINER SOLVED 208/208 (docs/re/shp.md, gate 3c: magic 1.10,
     u32 N, table_size==8*(N+1), N+1 u64 slots, rec0 at table_end, last->EOF).
     CODEC OPEN (OQ-005): 5 RLE grammars x hdr 4/8/12 x u16/u32 dims, exact-span
     discriminator, 12 smallest libs = 0 survivors. NO PNG renders until the
     codec is known — rendering with an unknown codec fabricates pixels."
  - "P1d/P1e/P1f: savegame correlation (docs/re/savegame.md, gate 3f: sparse
     u32-LE, stride-75 tech chain vs restree.txt; full record map OPEN = OQ-003);
     media inventory (docs/re/media.md, gate 3e: 2 FLICs exact-tiled, 15 real
     VOC + 77 headerless PCM, sample rate OPEN = OQ-006); text (docs/re/text.md,
     gate 3g: CP437-clean + 34 exe module names)."
  - "P2 loader model (docs/re/loader.md): payload = MZ+0x3c (0x2a50)..EOF,
     576,643 B. File order == memory order (le_contiguity_test.py: rel32 targets
     76:1 in-page, 135:1 inter-page vs shuffled control) => raw load at
     imagebase 0 valid FOR CONTROL FLOW; Seed2.java bootstraps 269 functions
     headless (work/functions.tsv, 14.2%). ABSOLUTE BASE C REFUTED by four
     scripted tests (vtable plateau 25/169 vs 0.4 exp; ebx-vote 71 < spacing
     control 82; zero anchor-valued operands in 604k insns; high-imm->ASCII
     4/52 vs 1.0) — do NOT attempt a fifth static scheme. Data identity needs
     the RUNTIME base (R1). Gate 3h pins loader.md + Seed2.java + probe health.
     Ghidra API footguns in loader.md footer (currentProgram is a FIELD;
     getBytes(arg3) is an ARRAY OFFSET -> silent zero images; -cspec flag)."
  - "docs/BLOCKED.md: R1 (dosbox runtime dump -> exact formulas) vs R2
     (data-first from extracted files, contract-compliant) vs hybrid. Working
     default = C hybrid, R2-priority, bounded R1 attempts interleaved."
  - "P4 mapgen (this turn): docs/re/mapgen.md + src/game/{starstat,mapgen} +
     6 tests (14/14 green). Facts: starstat.txt 13 types, pct sum 100.01, mean
     lanes 2.225; names.txt = 100 bases NOT 101 (0x1A EOF marker fooled Python
     strip(); erratum recorded in mapgen.md); snapshot galactic.tsv: 75 stars,
     177 planets, orbits I..V only, orbit-I count == star count, pp/star
     {1:17,2:12,3:15,4:18,5:13} -> uniform 1..5; all 177 roman bases in
     names.txt. Generator: seeded mt19937, rejection placement (sep>=60),
     NN-tree spine + distance-ascending capped top-up (sum(deg)+2<=target AND
     deg+1<=type-mean per endpoint; the first cap formula FAILED the +-0.35
     mean-degree test and was fixed). OQ-012 = the 4 documented choices."
  - "P4 research (this turn): restree.txt SOLVED as 'NAME flag cost prereq*
     255', 66 main rows + 40 ALL-CAPS variant rows (cost 20 flat, flag 0..4);
     acyclic, 3 roots, 3 FORWARD prereq refs so file order is NOT topological
     (naive recursion RecursionError was the control that refuted 'field1 is
     an index'). docs/re/research.md + src/game/research.{h,cpp} + 5 tests
     (19/19). OQ-013 = variant-field semantics, default union. ERRATUM:
     mapgen.md's '177 planets' was unreproducible; re-measured 223 (I75
     II58 III46 IV31 V13 = 223, 75/75 bases in names.txt) and corrected.
     Also found galactic.tsv carries research-tree strings too -> .tsv are
     per-context string pools (OQ-004 unchanged, corroborated)."
  - "P4 gizmos/economy (this turn): gizmos.txt + planitem.txt both carry the
     VENDORS OWN format docs above '#'. 76 gizmos (10W/6Sh/5Dr/6Sc/5G/44Spec;
     damage 1..13, shields 1..5, all gated by restree rows - third independent
     cross-validation of restree numbering: FergnatzLens->44, Plasmatron->29).
     39 items = 33 gated + 5x255 + 1x254 (254 UNDOCUMENTED sentinel, record
     verbatim). docs/re/gizmos.md + docs/re/economy.md + src/game/economy.* +
     6 tests (25/25), gate 3j, OQ-014; OQ-010 narrowed (device constants in
     data, application formula not). THREE self-caught errors this turn, all
     caught by controls or raw-data re-checks: (1) vacuous range check -
     testing v[7] for tech-range passes because flag bits 0..7 live in
     [0,106); (2) field-index drift - v[6] vs v[7] only differs on the 19
     len>8 rows, semantics decide (Shield->Superconductivity vs nonsense
     Shield->Spacetime Surfing); (3) test constant typed from memory (Ship
     cost 30 vs real 20 - the ADJACENT row's value)."
  - "P4 ui/species/diplomacy (this turn): windows.txt is a window+resource
     manifest, not per-screen widget layout (docs/re/ui.md): 2,067 keyed lines
     over 60 distinct keys; 132 window TYPE defs (124 named; the 8 unnamed are
     ALL TYPE 100 shape-file overlays - measured rule); NUMTABLES 23 asserted
     == 23 TABLE (.haz palette) lines; all 42 backslash DATA\ paths resolve in
     extracted/ (existence check itself initially tripped the KNOWN backslash
     basename footgun - split on BOTH separators before trusting 'missing').
     NUM_STARS/NUM_LANES are SINGLETON values 100 under the COSMOS window
     (snapshot display table), NOT small/large map options - the actual
     new-game size options remain glyph-baked in 3cfgnew.tmp (OQ-012 OPEN,
     re-checked and still open). history.txt: 21 species specnum 0..20 contiguous; raceNN.dip
     headers give names + unique SA_<Ability> tokens (docs/re/species.md);
     specnum<->raceNN mapping inferred from blurb cross-refs. DIP: races share
     one 15-key set, player carries strict 8-key subset; NEGATIVE values are
     legal (BIO_MAXNEGATIVE negative in all 21; first revision of ui_probe
     silently dropped them with isdigit - its own subset assertion caught it;
     dip_probe.py always parsed 15 correctly) -> docs/re/diplomacy.md +
     src/game/diplomacy.{h,cpp} (parse, sinusoidal mood model [inferred],
     %m%y%s%t renderer, threshold policy [inferred]) + 10 tests (35/35), gate
     3k, OQ-015 (token table + DA_ selection order)."
  - "P4 TURN LOOP + PLAYTHROUGH (this turn): end-*.txt SOLVED as the five
     vendor victory conditions (docs/re/turnloop.md §1; scripts/endtext_probe
     asserts comment+enddesc/congrat+10-ranks grammar - ranks walker must
     stop at keywords, ran past congrat and miscounted 20 once).
     campaign.{h,cpp}: homes spread + economy(stockpiled IND/RES) + logistic
     pop w/ PROS + gated item builds + research(RES->cheapest/random) +
     colonisation(one lane/turn) + WAR/capture [inferred model: pop/10 +
     owned weapon level 1..13 vs pop/10 + shield 1..5 + terrain 2, fortify 2]
     + diplomacy war table (START_ATTITUDE initialises relations - zero-init
     would declare war turn 1, data says no). Victory: Control >1/2 (end-ctrl)
     / Extinct (end-xtnc, waits for last colony ship) / LastAlive (end-dest);
     end-capt + end-unit NOT evaluated (need R1 bookkeeping - stated, not
     faked). --campaign N --seed S in main. 42/42 tests incl determinism +
     no-op-after-victory. THREE self-caught model bugs via behaviour tests:
     income-reassign starved economies (must stockpile); fortify checked on
     ATTACKER star -> 5k oscillating captures, frozen front; docs/code drift
     on PROS caught by re-read. PLAYTHROUGH.md = real captured runs: seed
     2024 Control t51, seed 42 Extinct t55, Xvfb seed 13 Control t50. Gate
     3l (grammar + both VICTORY lines + live binary smoke). OQ-016 = the
     documented-default constants (R1 replaces §3-5 wholesale)."
  - "SA_ ABILITIES WIRED (audit finding closed, 2026-10-04e): docs/re/
     abilities.md is the spec (vendor text help.txt L1713-2511; 21 blocks,
     14 charged / 7 passive [verified], race02 header tokenless -> ability
     via help-abil02 title 'Orfa'). New game/species.{h,cpp} (roster three-
     source loader, charge model default 30 [OQ-020], kNotes one cited line
     per token); campaign: abilityPhase() first in advance() + hooks
     (combat invincible/block/double/super, growth cap/rich, hops +1,
     sap/steal/peace/research/boost); --species N plays that species. 4 FILED
     NO-OPs (BuildOnBlack + 3 knowledge: no grid/no fog in the sim) +
     CauseWar partial (no AI-AI attitudes, R1). 4 self-caught bugs: (1)
     regex captured token without SA_ prefix -> silent title miss; (2)
     title->token map keyed by token; (3) generic per-capture hull damage
     starved all empires -> 8/8 seeds Extinct (removed; sap is the only
     damage channel); (4) RNG DISCIPLINE: def-noise draw became conditional
     and silently diverged the campaign stream by t195 while t40 matched -
     abilities must never add/skip draws (documented in abilities.md §3).
     70/70 tests (15 new), gate 3m (ability_probe + smoke fires
     SA_HealShips), PLAYTHROUGH regenerated (Control 201/211 + Extinct 215).",
  - "2026-10-04f: ALL FIVE end-*.txt victory conditions now evaluated
     (turnloop.md §1 rewritten). checkVictory gains Captured (owns every AI
     setup home via new homeStar_, checked before Control) and Unification
     (every live AI allied to player, no player-AI war bit; player-relative
     because the dip model has no AI-AI relations). Real gap fixed on the
     way: diplomacyPhase computed ProposePeace and DROPPED IT — now accepts
     when attitude >= PROPOSE_PEACE, else refuses; peace event emitted.
     Extinct fleetPending-grace kept; the redundant alive==1&&mine==0 dup
     removed. FastLaneTravel bug: +1 hop was applied to drive LEVEL before
     lvl/2 (no-op at odd quotients) — now +1 on hop count. Self-caught while
     writing a test with memorized constants (*3<=100*2/2+52 nonsense) —
     test rewritten to cite-only assertions per skill rule. 73/73 tests
     (3 new: enum->file mapping pinned, end-capt reachability skip-logged,
     peace-implies-war). Sweep: Control 198/201/211, Extinct x5 — victory
     records machine-regenerated. OQ-021 filed (end-ctrl comment 'over half'
     vs manual 'two-thirds'). Gate green pre-commit."
  - "2026-10-04g (option C activated): user chose C (hybrid, B-priority);
     docs/BLOCKED.md rewritten as the C runbook. R1 cadence is now CODED, not
     prose: scripts/r1_attempt.sh + scripts/r1_tracer.py, run at session
     start by launch_ralph.sh when work/r1/attempt-* is >12h old. Verified
     env facts: dosbox-x 2025.02.01 makes itself UNTRACEABLE early (ATTACH=16
     and SEIZE=0x4206 -> EPERM, /proc/pid/maps EACCES from t+2s; identical
     probes on a plain child succeed — harness self-check pins this), so the
     external-dump route is dead on this box; -break-start (in-process
     debugger, strings-verified) is the remaining route, grammar UNVERIFIED
     — pilot manually under pty+timeout before automating. Harness ran for
     real (attempt 20261004-205846: TRACABLE=no, exit 1, no stray procs).
     Safety invariants coded in: dosbox runs a COPY (work/r1/game), headless
     output=dummy+nosound+stdin=/dev/null+-time-limit, kills by pkill -x
     (pkill -f matched the gate shell's own cmdline once — never again), all
     output head -c 4000. Gate 3n added. rsync absent on host; cp -a used."

## CURRENT FOCUS
P5b next. CONTRACT-CORE MET (see Run A/B/C + gate 3l). DONE P4: mapgen,
research, gizmos, items, ui-manifest, species, diplomacy, turn loop.
DONE P5a (docs/re/ui-runtime.md): SDL2+SDL2_ttf window over the LIVE
campaign — cosmos view (circles; .shp sprites stay OQ-005), NEXT TURN
button + status + event pane; gates 4c (Xvfb autoplay run) and 4c-b
(synthetic XSendEvent click advances a real turn — tools/xsend, no
xdotool on host; SDL re-reads pointer for synthetic events -> warp first).
Owner palette SEARCHED and pixel-verified: 0/42 pair-checks fail under
deuteranopia AND protanopia simulation of the rendered framebuffer;
neutrals also coded by dot SIZE. Font = Liberation substitute (vendor
.fnt header/stride partly known, codec OPEN as OQ-017).
DONE P5b (docs/re/audio.md): vendor sample container cracked on all 15
headered .voc (rate/bits/ch explicit; PCM bytes 42..EOF-1); all 86 SFX +
theme00 music load through SDL2_mixer (--audio, --mute); UI plays
click08/laser01/bang01 on interactions; gate 4d + 5 audio unit tests.
OQ-006 NARROWED to headerless-file rate only (22050 default documented,
FFT check tried and recorded as inconclusive); OQ-018 for the remaining
header fields + theme selection. DONE ships spec (docs/re/ships.md —
contract's "ships" system): hull rows (Ship 20/req1, Shipyard 240/req0),
all five drive rows w/ gates (2/2, 4/10, 6/23, 6/46, 10/54; "Hypersphere
Driver" is a WEAPON), Shipyard launch precondition + drive-hops BFS
launch range, combat inputs already gizmo-gated. Opening position =
tutorial.txt state (Factory+Lab+Shipyard, restree rows 0-2) — economy
needed it after gating (total_owned test caught the stall). PLAYTHROUGH.md
now GENERATED by scripts/record_playthrough.sh from real runs (victory
~t201 seed 2024 under ship gating; slower by design — Shipyard economy.
OQ-019 opened for per-ship design. 56/56 tests.
SA_ SPECIES ABILITIES WIRED 2026-10-04e (docs/re/abilities.md, gate 3m,
70/70 tests; the species.md "?" for specnum 2 resolved = SA_BuildOnBlack).
Remaining to full contract: P6 README + final STATE checklist pass.
R1-blocked and stated-as-open in specs: exact combat arithmetic (OQ-010),
save/load (OQ-003), AI orderings
(OQ-015/016), headerless sample-rate ground truth (OQ-006).
AUDIT FINDING 2026-10-04d (session killed mid-audit by a model-latency
timeout; loop stopped by user): the 21 species SA_<Ability> tokens are
PARSED (diplomacy.cpp header scan) and string-tested but NONE affect
campaign behaviour — docs/re/species.md is a roster only, effects live
nowhere. Repo otherwise verified unchanged by the audit (reflog: zero
commits c1b6d3f..d85b281; d85b281 = committed one-char include-quote fix
in main.cpp). Finding scheduled in NEXT ACTION — must not be lost.

## NEXT ACTION (exactly one)
OPERATE UNDER OPTION C (user decision 2026-10-04g; docs/BLOCKED.md is the
runbook). Per turn: do B-priority work (from docs/OPEN-QUESTIONS.md or the
phase list), then run the R1 cadence check: `ls -t work/r1/attempt-* 2>/dev/null |
head -1` — if missing or older than 12 h, run `bash scripts/r1_attempt.sh`
ONCE (bounded by design; exit 1 = normal negative, record one line and move
on; exit 0 = R1 LIVE -> begin formula upgrades per BLOCKED.md §DECISION.3;
exit 2 = harness error, fix harness, do not log negative). SA_ ability wiring
DONE (2026-10-04e; gate 3m). All five end-*.txt victory conditions evaluated
2026-10-04f (73/73 tests). No open non-R1 item remains; CONTRACT CHECKLIST
fully [x]. R1 = exe runtime base is the master key: unblocks
OQ-003 saves, OQ-005 sprites, OQ-010 combat arithmetic, OQ-017 vendor font,
OQ-006 headerless sample rate, OQ-020 exact ability charge days, and
CauseWar's third-party redirect. Verification criterion holds: gate 0 +
CONTRACT CHECKLIST + PLAYTHROUGH victory record, all green 2026-10-04f.

## KNOWN-ISSUES / PARKING LOT
- DOSBOX RULE (caused the 12 GB crash): never launch dosbox with stdout/stderr
  redirected to a log unless you FIRST confirmed it will not sit at an
  interactive prompt; dosbox-x re-prints "Are you sure to quit anyway now?"
  forever when kill-signalled or fed EOF at a prompt. Bound
  (`timeout 60 ... | head -c 1M`) or drive via pty. nosound=true (no audio hw).
  dosbox-x has NO gdb stub (strings: 0 markers; `-break-start` debugger is
  separate and UNVERIFIED — see docs/BLOCKED.md). Salvaged log head shows the
  game DID boot under dosbox (XMS/EMS, videomode 69).
- R1 harness invariants (2026-10-04g, enforced in scripts/r1_attempt.sh):
  NEVER mount game/ in dosbox (scratch copy work/r1/game; gate 3n checks no
  'ascendancy/game' path reaches a conf); kill ONLY by `pkill -x dosbox-x`
  (`pkill -f dosbox` once matched the calling shell's own cmdline and killed
  the gate mid-run); dosbox-x self-blocks ptrace (ATTACH/SEIZE EPERM within
  2 s — do not hand-roll tracer probes outside scripts/r1_tracer.py, which
  self-checks against a plain child first); rsync is NOT installed.
- resume.gam may be a different game version than the shipped exe — verify
  version stamps before trusting it as golden data (OQ-003 territory).
- radare2 unavailable on Debian 13; no LE-capable Python pkg cached offline;
  do not waste turns hunting for either.
- Ghidra MCP server may be down; restart via scripts/ghidra_headless_up.sh
  (127.0.0.1:8089). After restart, verify any loaded program has NONZERO
  memory before trusting results (getBytes misuse produced silent zero images).
  Full API contract: docs/re/loader.md footer.

## DEFINITION-OF-DONE (from goal contract)
Verification = gate exit 0 + this checklist complete + PLAYTHROUGH.md
victory record. CHECKLIST SEMANTICS (stated, so marks are honest):
[x] = done with cited evidence; [~] = done-with-open-subitem where the
open part is (a) an unknown filed in OPEN-QUESTIONS per the goal's own
constraint, and (b) blocked on R1 (docs/BLOCKED.md) — never silently
missing. CONTRACT CHECKLIST (the judge's list) follows the phase list.

## CONTRACT CHECKLIST
[x] boots under Xvfb (PLAYTHROUGH Run C/D/E/F; gate 4c)
[x] loads the ORIGINAL extracted data (manifest-driven everywhere; gate
    checksums on game/; probes assert 132 windows/21 species/86 sfx)
[x] seeded campaign plays turn loop to victory (Run A/B; gate 3l)
[x] system specs docs/re/: mapgen, economy, research, production
    (economy.md+planitem), ships (ships.md), combat (turnloop.md §5 +
    ships.md §4), AI (ai-data.md + diplomacy.md), diplomacy, UI (ui.md +
    ui-runtime.md), audio (audio.md)
[x] every constant/formula cites docs/ which cites offsets/addresses
    ([verified]/[inferred] tags throughout; inferred -> OQ)
[x] README.md build+play instructions
[x] gate green end-of-turn every turn (git log, per-commit)
[x] PLAYTHROUGH.md victory record, machine-regenerated
    (scripts/record_playthrough.sh)

## CHECKLIST (PLAN phases)
[P0] env verified
[x] P1a .cob format spec (docs/FINDINGS.md)
[~] P1b .tsv/.bin tables — .bin SPEC COMPLETE (docs/re/tables.md, 7/7 exact);
        .tsv = string pools + numeric area; grammar OPEN (OQ-004; runtime-
        dependent per docs/re/loader.md). Seed claim .tsv = text .bin falsified.
[~] P1c .shp sprites — CONTAINER SPEC COMPLETE + gate-asserted (docs/re/shp.md,
        gate 3c; 208 libs / 1557 records). Pixel codec OPEN (OQ-005).
[~] P1d .gam saves — CORRELATION ONLY (docs/re/savegame.md, gate 3f). Full
        record map OPEN (OQ-003): needs runtime; P6 save/load depends on it.
[~] P1e FLIC/audio inventory — COMPLETE inventory (docs/re/media.md, gate 3e);
        sample rate OPEN (OQ-006).
[~] P1f text encodings — COMPLETE (docs/re/text.md, gate 3g): CP437, 0x1A EOF
        markers (NOT whitespace to C isspace), 34 exe module names.
[~] P2 exe model — docs/re/loader.md: raw-load model usable for control flow
        (269 functions seeded); static data base REFUTED (4 tests); runtime
        base deferred to R1 (docs/BLOCKED.md). Per-subsystem Ghidra specs are
        superseded by R2 data specs unless R1 succeeds.
[x] P3 engine skeleton — BUILDS + BOOTS (gate 4/4b). C++17 + SDL2 2.32.4 /
        SDL2_mixer 2.8.1; readers ported 1:1; boots headless AND Xvfb/x11.
        Render surface + input pump: shipped in P5a/P5b (gates 4c/4c-b/4d).
[x] P4 systems — mapgen, research, gizmos, items, ui-manifest, species,
        diplomacy, TURN LOOP + seeded VICTORY playthrough (docs/re/*.md
        incl. turnloop.md; gates 3i/3j/3k/3l; OQ-012..016 tracked).
        56/56 tests; PLAYTHROUGH.md shows Control + Extinct victories
        headless and under Xvfb. Exact combat arithmetic stays open
        (OQ-010) INSIDE the working loop — documented-default model.
[~] P5 UI+media — RENDERED UI shipped (ui-runtime.md; gates 4c/4c-b:
        Xvfb boot + injected-click advances a real turn) and AUDIO shipped
        (audio.md; gate 4d: all 86 vendor SFX + theme00 load). Open
        subitems are R1-blocked unknowns, filed: vendor .fnt codec (OQ-017
        -> Liberation substitute), .shp pixel codec (OQ-005 -> documented
        circles), headerless sample rate (OQ-006 -> 22050 default),
        dosbox screenshot comparison (needs a reference capture harness).
[x] P6 full campaign playable to victory (Run A: Control t201 seed 2024
        under full ship gating; B: Extinct; gate 3l re-runs it every
        commit) + README.md complete. Open-questions policy applied: the
        goal contract itself routes unknowns to OPEN-QUESTIONS.md, so the
        list is NOT empty — every entry is filed, cited, and R1-bounded;
        none is silently missing.
