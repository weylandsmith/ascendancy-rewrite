# REFUTED ROUTES — do not retry (knowledge transfer from v1)

Read the matching section before starting any research action. Each entry:
what was tried, how it died, what evidence killed it. Re-running a FORBIDDEN
route costs a turn and is itself a contract violation (docs/GOAL.txt
constraints). Sources: v1 turn log (archive/ralph-v1/STATE.md),
docs/OPEN-QUESTIONS.md, docs/re/*.md, gate stages 3q/3r.

## R1. Static absolute load base for the Watcom LE image — FORBIDDEN (5th attempt)
Four independent scripted tests, all refuted (v1 2026-10-04):
- vtable plateau vote 25/169 vs 0.4 expected
- ebx-relative vote 71 < spacing control 82
- zero anchor-valued operands over 604k disassembled insns
- high-coverage-immediate->ASCII 4/52 vs 1.0 control
Pattern each time: plausible vote, dies to its control. Details docs/re/loader.md §4.
THE ANSWER instead: runtime pointer law, OQ-011 CLOSED — runtime_u32 =
P0 + payload_file_offset(target); P0 = B - H per-run from r1_sav_scan.py;
work/ascend_restored.bin is the Ghidra-ready artifact. Never hard-code a base.

## R2. Blind .shp pixel-codec sweeps — FORBIDDEN (7th sweep)
Six static angles exhausted, all negative (OQ-005): (1) 5 RLE grammars x hdr
offsets exact-span sweep, 0 survivors; (2) tokenisation-grammar BFS, 100/100
negative (scripts/shp_tokenize.py, docs/re/shp-tokenize.md); (3) u8-len-per-
line tiling 3/1530 = noise; (4) rec1+ +16 'base dims' refuted (33.9% == rec0);
(5) cos_ship same-box diff: only colour bytes [3,6,11] vary; (6) nested-sublib
/ metadata-slot negatives. Entropy 3.4-3.9 b/B => light RLE. Container is
CLOSED 208/208 (docs/re/shp.md). Only sanctioned route: find the exe shape
loader via call graph + live image (W3).

## R3. LE header field-map / 'page table' readings — CLOSED NEGATIVE
le_tables_anchored.py: no object parse sums cbObject==cbImage; the +0x100
stride 'page table' is code-pattern-ambiguous (0x90c300cd int3 run). Header
image size 0xa7710 is NOT summed-object memory (obj1 mem size >= 0xa28e3 from
stored maxima — identity open but NOT via the LE header). docs/re/
r1-savestate.md lists the trail. Pointer-law decoding of live RAM is the route.

## R4. External ptrace on dosbox-x — DEAD ON THIS BOX
dosbox-x 2025.02.01 self-blocks: PTRACE_ATTACH/SEIZE EPERM within 2 s,
/proc/pid/maps EACCES, while probes on a plain child succeed (harness
self-check). No gdb stub in the binary (strings: 0 markers). Do not hand-roll
tracer probes; scripts/r1_tracer.py is kept for the record only.

## R5. dosbox-x -break-start pilot — DO NOT PILOT
Superseded by the save-state route (captured the same state without a
debugger) and it walks straight into the DOSBOX RULE EOF-spam trap. v1
BLOCKED.md records the do-not-pilot decision.

## R6. gam_probe.py bare run — TRUNCATION FOOTGUN (not a research negative, but
it bit v1): running scripts/gam_probe.py without --out overwrites/truncates
hand-written docs/re/savegame.md sections (hit 2026-10-05k; restored via git
checkout). Always pass --out or read the script first.

## R7. Encoding-garbage readings recorded so they are not re-believed
- u32 0x343FD at a code site = coincidental CALL rel32, NOT an MSVC LCG
  constant. (Real LCG: hand-rolled glibc-constant at 0x7825b, unmapped.)
- 'mid-turn u16 table' claim = UTF-16 text misread.
- immediate-encoding frames: trust rel32 edges + rewritten-site immediates
  ONLY (worked refutation at 0x7478b, v1 attempt 3).
- +0x68/+0x69 in planet records are generation constants, NOT the turn clock
  (refuted same-minute in v1). The turn counter is u16 phys 0x254e10.
- member-offset H: compiled-header estimate 104 was 32 B short; measurement
  says 136 (size census exact + unique BDA signature). Re-derive per build.
- t108 BOUNDARY LAW (supersedes any pattern-census accept rule): the
  containing function's sequential objdump chain is AUTHORITATIVE for
  instruction boundaries — never seed objdump at or above the candidate
  (base==addr self-verifies every byte pattern), merge wrapped-tail lines
  into the previous insn length, and mid-insn coverage = definitive reject
  with no fallback vote. Prefer whole-span decode for disp32 questions
  (generator-free; also covers mod=00 rm=101 absolute-direct + moffs forms
  the r1_t106/t107 generators never produced). docs/re/census-audit.md S7.

## R8. Comparison-method traps in refcap (docs/re/refcap.md)
1:1 blit row search passes on black-row dominance; logic.flc palette control
is vacuous (shared engine palette); bbox-normalised frame ID unscored. The
live law: movie shots >=85% in intro65a union palette, menus far <2%.

## R9. Font readings corrected (do not re-adopt)
NOT a bit format (1 byte/pixel, 0xFF bg). Higher byte = BRIGHTER ink (the
'255-value=intensity' phrasing inverted rendered brightness; direction now
asserted by fnt_probe every gate run). Row-major geometric law dies on
smfont; 'AA core = stroke width' dead; font ink cannot be palette-relative
(only index 0 is grey in intro65a).

## R10. Media/misc dead ends
- radare2: not in Debian 13 repos. No LE-capable Python pkg cached offline.
- dosbox-x -help hangs without guards — strings on the binary instead.
- .tsv are NOT text-.bin (seed claim falsified; see docs/PLAN.md erratum).
- FLIC 'Ascendancy-specific payload' verdict was a chunk-NAME-TABLE bug
  (missing 0x0007 DELTA_FLC) — stock FLC with three measured quirks
  (docs/re/flc.md); do not re-open OQ-002 from old notes.
- .cob offset table is N not N+1; the old extractor silently dropped each
  archive's last file (fixed; gate asserts counts now).
- 2026-10-04h "contract complete" claim covered v1's contract ONLY; under
  v2's strict policy the open ledger still has 15 items — that sentence is
  not evidence anything in the ledger is done.

## R11. Terrain preset-row == 0x744f4[+0x16] as GENERATION row — REFUTED (t29b)
*** RETRACTED t35 — the refutation was the t33 raw-slot-array bug. ***
Re-running the SAME first-save battery with the corrected array
(+0x10 stored ptr + 0x88; 29 runs, ~150k cells, scripts/r1_terrain_authored.py
--runs 'work/r1/*'): barren% tracks the row's w0 monotonically, every row —
row0 w0=100 -> 99.3% barren; w0=50 -> 48.1%; w0=40 -> 41.3/37.8/40.3%;
w0=20 -> 20.9/22.8/20.8/20.8%; w0=0 -> 0.7% and 0.2%. The old "preset-0
planets show 51% barren" was a misaligned grid window. The save-time +0x16
ROW IS the generation row for the barren draw. Also settled same run:
AUTHORED-vs-GENERATED = GENERATED (410 planet names carry multiple grid
hashes across capture runs vs 13 identical — the identical ones are the
all-barren row-0 style grids that hash-collapse; 0x37d80 runs on every new
game, never mid-game). Residual residue: the ~0.7% barren leakage on w0=0
rows and full class-chain shape for classes 2..7 (only the barren leg is
w0-predicted by this battery). See income-law.md T35.
--- original text (kept for provenance) ---
The class-draw law itself is verified instruction-level (barren iff
rng<scaled(w0) @0x37e51..0x37ea4, cumulative chain @0x37eb7..0x37ee0,
rng 0..32767 @0x78269). But a 13-run first-save battery (~70k surface
cells binned by the SAVE's +0x16) refutes the row as the generation
source: preset 0 row [100,0,0,0] predicts all-barren, preset-0 planets
show 51% barren; no monotone reading fits. Do NOT wire rewrite cell-class
generation off the save-time +0x16 row. Sanctioned route: +0x16 writer
census post-world-gen, else scenario data-file lift (docs/re/income-law.md
S10 OPEN RESIDUE t29b).

## R12. Scenario-template PRESET SOURCE for the +0x55 seed deviation — REFUTED (t106)
The "[inferred] residual = scenario/preset-row worlds" reading of the seed-law
1.4% is dead as an attribution and the file-search route with it. Evidence
(docs/re/income-law.md T106, tools r1_t106_*): deviations are run-local (7/15
runs zero-deviation, 41/424 names ever deviate, none consistently), frozen for
the run (constant d + single grid fingerprint across 20 saves), not array
aliasing (6/322), and the contiguous slot-block join finds deviating grids in
NO data file at a rate BELOW the law-holding control (3/29 vs 12/72) — with
T54b (preset blocks are EXE constants) every file-loaded-grid variant is dead.
Do NOT re-census scenario files / RESUME.GAM for a per-world grid or seed
table, and do not re-test per-name consistency (grids are per-run instances;
R11). The residual's remaining question is WHICH event dispatch mutates +0x55
between generation and the first banked save (41..56.sav = mid-campaign) —
capture-class, alongside the rest of the OQ-016 open set.
## Meta-lessons (how v1 self-corrected; keep doing this)
- Verify the number, THEN write the sentence. Controls on every vote/census.
- Ambiguous windows don't vote (fake-base incident).
- Catch claims before they leave the tree; when wrong, correct the doc the
  same turn and record the episode (pointer-law retraction whiplash).
- Behaviour tests catch wrong inference even when constants are uncheckable
  (stockpile starvation, fortify-on-wrong-star oscillation).
- RNG discipline: features must never add/skip draws on the campaign stream.

## R12. Direct-reference scans for string/DAT sites in ascend_restored.bin — DEAD METHOD (t51)

- Proven-blindness demonstration: `planitem.txt` string @0x84888 has ZERO
  u32-immediate references and Ghidra `get_xrefs_to(0x84888)` == 0, yet its
  loader FUN_00037fc0 is CLOSED (OQ-014) — references are LEA-computed or the
  restored image lacks the reference metadata. Same for `resume.gam` (five
  string copies, all zero-xref), `cosmos.txt`, `DAT_00074508`.
- The 12 byte-scan hits for packed u32 0x857de (and kin) are MID-INSTRUCTION
  false positives: Ghidra reports 'No instruction at address' for every one.
  The lone contextable hit 0x38205 is PUSH EAX inside the item-table parser —
  unrelated bytes.
- DO NOT re-run: u32 scans of string addresses, search_byte_patterns on these
  VAs, get_xrefs_to on the same DATs. To find a field WRITER use runtime
  memory-modification capture or controlled save mutation instead.

## R13. Screenshot-reading for UI geometry — UNAVAILABLE (t55); AMENDED t196
- vision_analyze returns 500 'image input is not supported' for this
  deployment's model group (measured 2026-10-11). UI button geometry comes
  ONLY from windows.txt X0/Y0/X1/Y1 offsets (file evidence) + the banked
  click law (root = window + 40); verify every new click target by a RAM
  signal (turn counter / grid hash / needle), never by looking at pixels.
- AMENDMENT t196 [verified]: vision_analyze NOW WORKS on this deployment but
  INTERMITTENTLY (5 successes + 1 retry-after-500 in one session). The
  substantive bans above STAND: never self-grade our codec's correctness by
  pixels, never derive UI geometry from screenshots. Identification-by-context
  of vendor/external art is legitimate (t193 law; t196 delivered real IDs).
  NEW PITFALL: vision misreads small label digits on contact sheets — trust
  the generated report file's numbers, never the vision transcript's.

## R12 amendment (t60): file-provenance law for image scans

u32-immediate scans over ascend.exe MUST use work/ascend_restored.bin (the
Ghidra image with reconstructed VA immediates), NOT work/ascend_payload.bin
(same length 576643, 6244 differing bytes in 1069 clusters). The t59
"shp-string u32 scans zero hits" negative was a wrong-file artifact and is
VOID; corrected restored-image scan hit 6 of 16 shp/asset strings at base 0
(LGRACE/SMSHIP registration, planal, planets->FUN_0001fe20 chain, suns x2).
Absence remains uninformative (R12); presence is a lead.

## R13. "The 0x8c90 jump table ties order-KIND to SO NAME" — REFUTED (t96)
The table at cs-relative 0x8c90 (= FILE 0x1d840 restored; static and clean,
6 pointers to batmode.cpp panel bodies) is the SHIP-PANEL STATUS-text
dispatcher: each case builds a static.txt TEMPLATE string ('Sun %s',
'Planet %s', '\nMoving to Star Lane', 'Star Lane'/'Red Link', shared
POWER/MOVES/INTEGRITY tail). No case pushes an SO-name; the string getter
(FUN_00021a20) indexes game/static.txt (191 quoted strings), NOT the SO
block. Chasing kind->name through this table is dead (killed aicode.md §2h
disasm). Related banked trap: cs-relative immediates need the code-object
intra base (+0x14bb0), NOT member-index or section-base arithmetic;
t95's "0x8c90+0x1d4000 fixup decode" and "img 0x8dd9 case bodies" are VOID.

## R14. "WLINK ID-Info / LE symbol records will tie the SO name block" — REFUTED (t98)
ascend.exe was shipped WITHOUT debug info: DEBUG INFO OFF = DW(le+0x98) = 0
and LEN = DW(le+0x9c) = 0 (IBM LX spec rev 11 §2.2: zero offset = table
absent; header reads sealed by byte-exact tiling objtab(2x24B)->obj-page-
table(121x4B)->resident-name 'corn'->entry table, and loader-section end ==
DATA PAGES OFFSET 0x17600). Whole-file signature scan: NB03/NB00/NB02/
ODIAG/DWARF/OS21001 all ZERO; each SON* name occurs exactly once (the block
at exe-file 0x8b8b0 itself); no non-resident name table; no module-name
vocabulary. Tool scripts/r1_t98_wlink.py RC=0 prints the verdict. Do NOT
re-parse LE tables hunting for symbols — there are none; the SO block is
demand-page image data consumed by nothing (t97 censuses). A5 closes as
debug-only identifiers per the t97 rule (docs/re/aicode.md §2i). Related:
t97c's "object table at DW(le+0x30)" was FIXUP SECTION SIZE misread — the
correct offsets are DW(le+0x40)/DW(le+0x48) header-relative.

## R15. "0x79950..0x79c20 is the starmap key dispatch" + file-image dword
## hunts for handler bindings — REFUTED/DEAD METHOD (t191)
The t85f leaf table (0x79ace "s reveal", 0x79c35 "c overlay" ...) is inside a
vprintf FORMAT-SPEC engine (width/precision/sign/zero-pad; disasm
0x798de..0x79d26) — every leaf address in it is void. Separately: searching
the payload file for a dword == a code address to find dispatch-table
bindings is STRUCTURALLY DEAD — Watcom LE fixups patch those slots at load,
so the file image holds unrelocated offsets (t191: ZERO dwords == 0x26b34
(cosmos msg handler) or any reveal-block head, yet 60.sav RAM member 0x247adc
holds P0+0x26b34). THE ANSWER: (1) enumerate branch edges (linear decode
e9/eb/jcc8/jcc32) to find cascade entries; (2) scan RAM with the OQ-011
pointer law (member == P0+X). Char-immediate key compares do not exist in
this engine family — cheats are RAW AT SCANCODE keyed (debugflags.md t191:
0x1f S / 0x26 L / 0x2e C / 0x13 R, handler 0x26b34 DX==3). Full census banked:
'l'/'L' compare immediates exist ONLY as printf length modifiers
(0x79694/0x796b4/0x7a4b1/0x7a4bf). Do not re-hunt `cmp al,'l'`.

## t213 — RE-TRACING THE al-form [ship+0x62] VALUE SOURCE IS CLOSED WORK
The al-form writers 0x15c6d/0x15d98 (batcon order-commit dispatcher
0x156d4..0x17c25) were the last named static residue. t213 measured them
DOMINANCE-PROOF: site 1 writes phase==1 on every execution ([esp+0x50] has
exactly one byte-def 0x15c34/bl=1; cutting init block 0x15c14 makes the store
unreachable — 641->564 blocks), site 2 writes phase==0 on every execution
(reaching def 0x16385 `mov [esp],dh` under gate 0x16376 `test dh,dh`
zero-side; the dl=2 def 0x16361 is straight-line-overwritten; the 0x15e23
def-1 jumps to the tail and never reaches the store). Combined with t211's
constant-writer census, the static writer population of [ship+0x62] is COMPLETE
and BINARY {0,1}. Do NOT re-trace [esp+0x50]/[esp] defs, do NOT hunt another
">=2 phase producer", and do NOT treat 0x49f28's cl>=2 arm as a live route
(defensive dead code in the original — docs/re/_wip_t213.md S5/S6). Note the
order-arg codes {5,1,0,2} land in the DAY byte [ship+0x67], NOT +0x62 (t211
mis-locate, corrected) — do not re-read the switch as a phase-value ladder.

## t260 — HEADLESS (=-nogui) SAVESTATE RESTORE IS DEAD; THE GUI MENU IS THE ONLY PATH
dosbox-x 2025.02.01 has no loadstate CLI flag (--help verbatim: only
-conf/-savedir/-erasemapper/-startmapper/-defaultmapper/-nogui/-nomenu), no
autoexec command, and no [hotkeys] conf section (reference.full.conf grepped:
zero hits). CONF-ONLY LOAD IS REFUTED: saveslot=60 + forceloadstate=true sets
"Active save slot: 60" and never loads — forceloadstate is documented
(reference.conf L182) as a MISMATCH-BYPASS flag ("load even if it finds there
is a mismatch in the version, machine type, program name and/or memory size"),
not a trigger. HOTKEY ROUTES ARE REFUTED FOR tools/xsend: the menu prints the
chords Save state F12+S / Load state F12+L, but xsend sends keys with state=0
(no modifier support — xsend.c: "state=0 intentionally: synthetic modifiers
unverified"), and bare F12 is the hostkey. MAPPER-EDITOR BINDING IS REFUTED
WHILE THE GAME RUNS: the editor refuses with "Another program is already
running." (observed dialog). What WORKS (measured, docs/re/selfplay.md t260):
launch WITHOUT -nogui and click Capture -> Load state via xsend synthetic
BUTTON events (SDL2 accepts those), with -savedir pointed at a scratch copy of
the banked ZIP. Do NOT re-attempt: conf-only load, bare-F12, mapper-editor
binding mid-program, or any -nogui loadstate.

## t261 — THE t1255 BANK STATE IS NOT DRIVABLE: loadstate RESTORES IT INTO AN INPUT-DEAD GAME
Measured 2026-11-01 21:02-21:20 (docs/re/_wip_t261.md S1): the t260 load
sequence reproduces exactly (Loaded. (Slot 60), watcher row t=1255 V=14) but
the loaded game NEVER accepts input — 6 NEXTTURN presses no-advance, Escape
and 'c' legs 0 px, screen md5-frozen across minutes, ring core-state identical
across slots — while the SDL menu bar still responds to the same xsend path
(Capture dropdown opens, pixel-diff 0.043) and autosave churns. The t1254
softlock class is INSIDE the save. Do NOT plan any drive on a loadstate of
bank-t251-live1255; a restored state must first pass an INPUT-LIVENESS PROBE
('c'-toggle delta > 50 px). Structural decode of a round-trip re-save (t260's
verification) cannot see this.

## t265 — MINING st4 MID-TURN DISPLACEMENT FROM AUTOSAVE CORPORA IS DEAD
The OQ-019 "live in-system march" residue (t190/t193 form) is NOT observable
at 10 s autosave-ring granularity, corpus size notwithstanding: on the t261
DRIVE corpus (~150 real turn advances, healthy regimes isolated), every st4
run spanning turn advances has net displacement 0.00 with constant [+0x59],
every big mover is a 4<->5 frame switch, and same-turn st5 deltas are exactly
0 (ships.md S24). A ship resolves its in-system move inside one turn boundary.
Re-running this census on a bigger corpus wastes an iteration. The residue
needs a sub-ring instrument (runtime watchpoint class) or is dropped. Related
zero-census: magnetron landings leave an OFF-32-GRID st4 row (rng%200 on both
axes, 0x21f58) — 0 witnesses in 6,184 st4 rows; a player-activated use is the
only remaining witness route.

## t266 — DO NOT TRUST playcap ROWS 2026-11-01 21:38-23:06 AS PRODUCTION EVENTS: TWO-WRITER RING COLLISION (campaign-fingerprint law)
The t261 "production :9 softlock at 21:38" narrative is CONTENT-REFUTED: the
flip slot-pair (bank-t261-t1255 53->54, mtimes 21:38:12/22) changes CAMPAIGN
(md5 of the star->planet-owner table: f8bf068b76 -> e1d3bdc128), production's
dosbox.log has ZERO "Loading state from slot" lines, and the post-flip ring
holds only the restored-t1255 campaign. A stray second dosbox (savedir
redirected to playcap/save) wrote those slots; production's own autosave went
silent at 21:38:12 (its own silent guest hang is real, but every "t1255/V=14"
event attributed to production that evening — incl. the t265 slot-30 tail-
running feed — belongs to the RESTORED campaign's ring). LAW: fingerprint a
slot's campaign (star->owner-table md5, see selfplay.md t266) before trusting
ANY cross-session timeline claim; multi-writer windows look exactly like
engine anomalies otherwise. Evidence + quantified ~150 s oscillation:
docs/re/selfplay.md t266 block.

## t271 — WIRING the T39b Terraforming/Automation completion branches into the rewrite NOW — DEAD (zero-witness class)
The route "OQ-016 per-cell residue: implement item-36 completion (word2:=0,
byte1:=0xFF, byte0:=1 terrain mutation) and item-35 completion (word2|=2) in
buildPhase" is dead until re-open conditions hold. MEASURED (scripts/
r271_cellreach.py + r271b_tfdrill.py + r271c_pendctx.py, 1074 saves x 66 runs,
slot array via STATE locator law): item 35 appears in ZERO slots anywhere;
item 36 appears 78x ALWAYS as a player mid-progress queue (+0x54==36, word2
bit0 CLEAR, +0x50 acc 32..48 of COST 50, turn frozen on idle production
captures) — ZERO completions ever witnessed corpus-wide. Static: the original's
own AI can never buy either (scorer loop 0x3f528..0x3f592 excludes rows >=
[0x73e3c]==22 verbatim; emergency chain purchase sets {38,18,19,11}+{12,13,14,
15,37}, ai-dossier.md S10) — they are human-UI-only items and the rewrite has
no build UI (kBuildOrder documented stand-in). Wiring them adds behaviour the
captured original never exhibited (t256c principle). RE-OPEN CONDITIONS: (a) a
human build-order UI ships in the rewrite (then wire the T39b branch table
verbatim), or (b) a capture witnesses an ACTUAL item-36 completion (then the
mutation law gets its first live confirmation + a pin). Related banked facts
(pending reserves its slot byte1:=id/word2-clear; per-slot shield byte has no
mapped consumer; AI orbital shipyard-tail template {28,29,30,0,26} @0x89360):
docs/re/income-law.md T271.

## t272 — DOSBOX-X WRITE WATCHPOINT ON THIS BOX IS DEAD (instrument does not exist)
The installed dosbox-x 2025.02.01+dfsg-3 SDL2 has NO debugger command set
(strings -n 2: zero "bpm"/"bph"/"clrbp*"/"bplist"/"dbgcon"/"breakpoint"/
"watchpoint"; the DEBUGBOX internal errors "Bad command or filename"; the GUI
has no Debug menu despite en_US.lng carrying dead debugger strings; -break-start
is accepted and IGNORED — game boots to title, measured, screenshots in
work/r1/wp-t272/). /usr/bin/dosbox 0.74-3: zero debugger strings. No
bochs/qemu/valgrind on the box; ptrace stays dead (R4). DO NOT re-census this
binary and do NOT pilot -break-start again (GOAL.txt standing decision, now
empirically vindicated). Full trail docs/re/score.md S15. Related keeper: a
title-screen scratch boot does NOT have the ascend.exe image resident in guest
RAM (scripts/r272_scratch_resident.py) — any future debugger-class session must
click into a campaign first. If the user ever supplies a debugger-enabled
dosbox-x build, this route re-opens (S15.5).
SUPERSEDED 2026-11-02 (t282): the user authorised a build; upstream master with
--enable-debug=heavy (work/r1/bin/dosbox-x-dbg) ACCEPTS BPLM/BPPM/BPM over its TCP
MCP control channel and a BPLM MEASURED FIRED (docs/re/dosbox-debugger.md LIVE
VERIFICATION). The negative below holds ONLY for the dfsg /usr/bin/dosbox-x, which
production :9 still uses. DO NOT re-census either binary — t282 measured both
sides. Watchpoint work now runs on dosbox-x-dbg on a scratch copy.

## t277 — DETECTING A DOSBOX-X -time-limit DEATH FROM ITS LOG IS IMPOSSIBLE (KEEPER)
The t277 queue row asked for "the exact farewell line in the log or strings" for
the time-limit exit. IT DOES NOT EXIST, measured three ways: over the 290 MB
production log work/r1/vnc/dosbox.log `grep -c 'Shutting down'` == 0 and
`grep -c -i 'kill'` == 0; /usr/bin/dosbox-x holds only the help text ("Kill the
emulator after 'n' seconds") and the conf variable name; and the golden witness
on disk — work/r1/selftest-t111-playcap/dosbox.out, the t111 TL=90 self-test —
expired silently (9 saves == 90 s, last line `LOG: [21:10:42]: Saved.
(Slot 49)`, EOF right after the `Active save slot: 1 [Empty]` slot-list refresh).
DO NOT author another task that greps for a TL/shutdown marker, and do not treat
the trailing `Extracting: Program_Name/Time_Stamp/Save_Remark` churn as exit
evidence (it is the SAVE-path slot-metadata refresh, same misread class as the
t266 note). Liveness is /proc-polled from the recorded pid:
scripts/r1_game_health.py (T:WARN at 14400 s, T:EXPIRED after). Death CAUSE is
still diagnosable offline, but from the RING, not the log: ~2880 autosaves per
8 h of life == TL 28800 expiry (docs/re/selfplay.md t277 Law 1).

## t284 — CLASSIFYING A STORED POINTER BY (p - (B+0x82bb0)) MOD STRIDE IS DEAD (the 0x88 trap, third sighting)

While testing whether ship+0x59 can hold lane-pool pointers, decoding stored u32s
as X = p - (B + 0x82bb0) put every target "in the data segment but congruent to
NEITHER pool" — a false negative that nearly killed the contest-gate decode.
The stored-pointer law (OQ-011, and score.md S2's runtime-relocation note) is
X = p - (B - 0x88 + 0x82bb0): DIRECT data reads use B+0x82bb0+X, POINTERS decode
with the -0x88. Re-decoded, kind-5 orders land EXACTLY on lane records and
kind-4 exactly on star records (scripts/r284_deref.py's head classifies both
conventions side by side — keep it as the canonical reader). Any future
pointer-class census MUST decode via ptrX()-style -0x88 arithmetic or it will
manufacture "no such structure" negatives.

## t284 — "V (DAT_482fb) IS A LINEAGE/HISTORY FUNCTION" IS SUPERSEDED (do not mine history again)

S10 #3 read the same-turn V=14-vs-23 pair as requiring history. t284's replay
(scripts/r284_vreplay.py) reproduces EVERY banked V from the save's OWN snapshot
(state object + visibility masks + relation cells + ship order pointers):
295/409 EXACT, the 114 misses exactly the pre-first-end-turn slots whose stored
value is 0, and the predicted visited-lane set matches the persisted +0x21
marks 409/409. The lineage lives IN THOSE FIELDS, not in a hidden accumulator
of the past. Do not author V-tasks that diff turns looking for "carried state";
the closure route for the remaining residue is the THRESHOLD witness only
(selector arm + V>=25 + end screen).

## t285 — NAIVE DRIVE PROBES ARE DEADLY: Escape AT THE GALAXY MAP EXITS TO THE TITLE MENU, AND THE RING NEVER NOTICES (full chain + Nov-1 reattribution)

WITNESSED 2026-11-03 04:38 (screenshots banked, work/r1/bank-t285-flip1255/):
one Escape at the bare campaign map ejects to the TITLE MENU while autosave
keeps writing the RAM campaign — in_game stays True, so ring/watcher-based
title-menu guards are STRUCTURALLY BLIND (the ring_in_game() gate added today
catches death, not this). A subsequent popup-drain click hits the white title
rows; a Load Game click makes the game replace the RAM campaign (fp
3a189896 -> 39614c7c measured 20/20 both sides). Pixel-diff "input ALIVE"
during the ejection is the t266 starfield false positive. DEAD ROUTES: (a) any
driver that probes with Escape-first (the pre-t285 r1_t261_drive.py input_alive
— patched 'c'-first); (b) any campaign-identity claim from fp EQUALITY ACROSS a
load (the name-anchor locator drifts, recs 152->156; use the r1_slot
ship_records census across loads); (c) treating the t261/t266 RAM campaign swap
as a stray-second-dosbox event — the Nov-1 flip slots carry the SAME loaded
campaign fp as today's self-inflicted load, and the Nov-1 drive log shows the
identical probe/drain tell (docs/re/driver-selfharm-t285.md §3). The two-writer
RING law itself STANDS (ring-content corruption is still a second-writer
phenomenon). Every future drive row must satisfy the STATE.md DRIVE-CLASS
PRECONDITION (screen-based title-menu detection, STOP-AND-LOOK on 2
no-advances, no Escape at the map).

## t288 — THE DEBUGGER BUILD (work/r1/bin/dosbox-x-dbg) CANNOT RESTORE A 2025.02.01 SAVESTATE ZIP
Measured 2026-11-03 (work/r1/t288-probe-dbg-a0-20261103-104330): GUI-mode dbg
session (2026.10.01 master), BREAK lottery WON at the title screen, BPLM armed
('00. BPLM 0028A4C6 (00)'), EXEC RUN, Capture->Load state clicks delivered
(xsend rc=0): pty shows 'Loading state from slot: 60' then glibc
'corrupted size vs. prev_size' — process ABORTED mid-restore, 'Loaded. (Slot
60)' never printed. The abort is in the LOAD path (BREAK had already survived).
Mechanism [unverified]; do not retry dbg-restoring bank states for watchpoint
work. Route that WORKS for the input-global questions: release /usr/bin/dosbox-x
(2025.02.01, same version as the bank) + offline ring census of the game's own
globals (scripts/r288_softlock_probe.py, docs/re/selfplay.md t288). Writer-EIP
ambitions on restored states need a DIFFERENT instrument (e.g. same-version dbg
build), not this binary.

## t286b — A RING-MEMBER INDEX FED TO BPLM AS A LINEAR IS ALWAYS THE WRONG BYTE
Measured 2026-11-03: t286's entire zero-fire thread (runs 1/4/10, incl. the
run-10 "refill happened in the ring, bp armed, zero fires" puzzle) was ONE
bug: sig_hits/pointer scans over a save-zip Memory member return MEMBER
indices; guest-linear == member - 0x88 (H). Arming the member index watches a
byte 0x88 too high — run 10's armed byte is 0 in all 20 of its own slots
(dead byte, unfireable by construction), while the corrected byte flipped
0->80 across the observed refill. SILENT by nature (arm succeeds, BPLIST
lists it, nothing errors). DEAD: (a) any BPLM/linear consumer fed a
member-scan finding without -0x88; (b) the t286 candidate readings "BPLM
blind-heap arms unreliable", "the write path escapes the heavy check", "the
fire path dies post-restore" — all SUPERSEDED by the corrected positive
(wp-heap-planets-blind-20261103-114454 fired on attempt 1). Related trap: the
ring FREEZES at the last autosave before a fire (CPU stopped), so stack dumps
read from the ring around a fire are STALE — bank registers via EV over the
socket. Full account docs/re/_wip_t286b.md + dosbox-debugger.md t286b.


## t296 — CLICKING STAR DOTS TO SELECT A SHIP IS DEAD, AND NOW PROVEN SO
t293's three launches (dot-clicks navigate, never select) were OBSERVATION;
t296 cites the mechanism (ships.md S24): the orbital bright dots are kind-3
PLANET clips, and BOTH selection legs test `cmp BYTE [clip],0x2; jne skip`
(0x1b6fc msg-0x53, 0x1b9f6 mouse msg-4) — a planet clip can NEVER select.
Second binding negative from the same pass: in mode 2 (ship selected) a PLAIN
MAP CLICK DESELECTS — 0x1b0d6 reads WORD [win+0xbc], 0xffff ->
`mov BYTE PTR [win+0xb7],0x0` @0x1b114. DEAD: (a) any route that aims at
star/orbital dot pixels to select; (b) any choreography that plain-clicks the
map after selection expecting destination entry. Ship selection requires the
SHIP SPRITE clip, which exists only for kind-4 (in-system) ships (0x1d6bb).

## t298 — FLEET-ROW-BY-ARRAY-RANK NAVIGATION IS DEAD; UNBOUNDED SCREEN FINDERS DEAD
Row->ship mapping law was inferred, never measured; run-3 vision on the open
FLEET window: rows top->bottom = slots 18/7/16/22 (Sparrowhawk/Erebor/
Erchamion/Ignatz) — NOT array order, NOT name order, NOT kind order (sort law
UNKNOWN; the only reliable row identifier is the NAME rendered in the row).
Any future fleet-row automation must read the row name (vision or the ship
name field record+0x34 matched against a screen read), never its position.
Separately: screen finders without the BatModeWnd client-rect bound (x 7..465,
y>=112) return sidebar chrome as "sprites" (run 3: (597,140),(612,259)) —
every click aimed at them hits the sidebar. Fixed in r298_order_session.py.
The scripted MOUSE session class is also budget-spent by standing law
(t293 three + t297 one + t298 three): the next witness on the selection/order
legs is the debugger class (t299), not launch #4.

## t299 — THE STATIC BATMODE MSG LAYER IS NOT EXECUTED BY SYSTEM-VIEW CLICKS
Claim tested (t297 static reading): system-view ship clicks walk msg-4
router 0x1b070 -> batcon 0x1b91c -> select/publish legs, so a debugger BP
on those legs witnesses selection. MEASURED FALSE (3 debugger sessions
work/r1/t299-leg-20261104-{205111,205500,205849}, 8 code BPs armed incl.
handler ENTRY 0x1aef8 and router 0x1b070, MEMDUMPBIN control byte-exact,
pty 'Memory breakpoint' count 0): clicks on the validated ship sprite
(48,151), planet (439,331) and empty (236,200) in the Icarus system view
executed NONE of the eight addresses — IN SESSIONS WHERE FLEET-button,
row-jump and End-Turn clicks demonstrably changed game state (ring diffs
122756 / view change / t 1086->1087). windows.txt VERBATIM: BatModeWnd rect
7,7-465,472 contains all three click points; every named child button sits
x>=479, so no child intercepted them. Static cross-check: 0x1aef8 and
0x1b070 have ZERO E8 callsites and ZERO u32 refs in the payload image.
DEAD: any plan that witnesses system-view selection/orders by arming the
STATIC legs 0x1b91c/0x1ba39/0x1ba5e/0x1baa7/0x1bad3/0x1b114 (or the router)
and clicking ship/planet/empty pixels. NOT claimed: that selection is not
msg-dispatched SOMEWHERE (window-manager hit-test vs wrong handler
attribution is separated by the t301 TOGGRID control-click probe; see
docs/re/_wip_t299.md S8). t298's 'not refuted' is hereby a CITED negative.
T301 AMENDMENT (binding): the t301 control-click probe ran (2 full sessions,
t299-leg-{213540,214042}) and ZERO-FIRED, but the control was INVALID — rect
557,403-587,433 is pixel-BLACK in the Icarus view (uniq=2, mean~0) and
windows.txt assigns the same rect to TOGSHIPS/COSMOSWnd as to
TOGGRID/BatModeWnd (sibling windows, identical 7,7-465,472 rects). The probe
therefore separates NOTHING, and DEAD is now also: any control-click test at
a rect not pixel-verified non-black in the current view screenshot. The
underlying question was resolved OFFLINE instead (ships.md S28): dispatch =
`mov ecx,[win+0xa7]; call [ecx+4]` into the active window's class table, slot
1 = universal dispatcher file 0x30d08; the t299 zero-fires are an
ARMING-FAILURE (wrong class table), not evidence of a click bypass. The
stronger t300 claim 'system-view clicks never reach the batmode msg layer'
is downgraded: they may well reach BatMode/BatControl class legs — none were
ever armed (tables 0x2478e8/0x247850 slots 0/2/3). Witness route = re-armed
r299_leg_session.py (router+cos_*+btn_* legs; stops dump the window-record
NAME via magic 0x12345678 + +0x20).

## t302 AMENDMENT (binding): the t299-entry zero-fires are now FULLY
## re-attributed and the class-witness question is OPEN AGAIN (route proven,
## residue moved). Measurements (run work/r1/t299-leg-20261105-004605 rc=0 +
## pty re-scans of all 12 pre-t302 runs with the CORRECTED fire pattern):
(1) Pre-t302 zero-fires were REAL non-executions (corrected-pattern re-scan:
zero code-view renders for the old leg sets in every pty) — but the detector
itself had been DEAD until t302 (pattern `0160:001E5F84` never matches this
build's DrawCode form `1E5F84 56 push esi`), so any fire in t299-t301 runs
would ALSO have frozen the guest unnoticed. The t299/t300 state-advancing
clicks prove their guests stayed alive => genuinely no fire. Consistent.
(2) DEAD is now also: "map clicks dispatch through a class-table SLOT" —
sprite/planet/empty clicks (Icarus view, live guest, 5 un-witnessed legs
armed: cos_entry/cos_s5/btn_entry/router/batmode_dead) fired NONE (pty census
0 each). Equally DEAD: "clicks bypass the class msg layer" — End-Turn fired
btn_hdlr (table 0x247cb8 slot 2) on record NEXTTURN edx=0x7 == windows.txt
SENDMESSAGE 7 verbatim; the turn-advancing click fired COSMOS slot 3.
(3) Live law: msg edx=0x3b pumps COSMOS slot 2 (cos_hdlr, file 0x26b34) ~1/s
with eax=window record magic 0x12345678 NAME='COSMOSWnd' (3 samples) — any
armed hot leg guarantees re-stops; instrument must drop witnessed legs
(BPDEL-before-RUN protocol, docs/re/dosbox-debugger.md t302 block).
(4) Route forward (NOT refuted, t303): census edx at cos_hdlr entry per click
(census mode: same-leg re-arm every stop) + the five call-[ecx+4] sites
(img 0x26eda/0x30d02/0x7a7eb/0x7aa3e/0x7b020), then read the cos_hdlr
msg-switch statically. BatControl legs (0x15630/0x156d4/0x16420) remain
unarmed-and-untested; add only if the census points there.

## t303 AMENDMENT (binding): T301 S6.2 UNIVERSAL-SLOT-1 LAW IS REFUTED. The
## "every click (working or not) walks slot1 0x30d08" claim died on two
## independent witnesses (docs/re/_wip_t303.md S4-S5):
(1) t303 census (2 full sessions, runs work/r1/t299-leg-20261105-{015611,
020416}, instrument control MATCH=True x5, ZERO freezes — the arm/click/
disarm census cycle beats the t302 resume bug): whole-log pty census
{cos_hdlr: 15, disp_26eda: 0, disp_30d02: 0, disp_7a7eb: 0, disp_7aa3e: 0,
disp_7b020: 0}. The 0x3b pump delivers msg 0x3b to cos_hdlr (slot 2) WITHOUT
ever executing a single `call [ecx+4]` site. Slot 1 == P0+0x30d08 in every
class table remains [verified]; it is NOT the universal msg dispatch point.
(2) t302 run 004605's OWN log: 00:48:10 're-armed 7 legs ok=True' (BPLIST
contains 0160:1F0158=router) then 00:48:21 STOP endturn-p1 leg=btn_hdlr —
the positive-control End-Turn click reached slot 2 with router armed+silent.
(3) A WORKING map click that opens the ship dialog (sprite (48,151), pixel-
proven landed 66717 px, vision: modal "Ship 'Sparrowhawk'" Leave Orbit/
Abandon/Cancel) fired NONE of cos_hdlr + 5 slot-1 sites inside its 45 s
window. Map-click entry is NOT cos_hdlr and NOT slot-1 — the t303 assignment
premise ("map clicks must branch INSIDE the cos_hdlr slot-2 handler") is
DEAD as stated.
(4) Static (payload): indexed indirect calls ff 14 modrm = ZERO everywhere;
`mov r32,[r32+0xa7]` = 21 sites (cluster 0x14de8-0x14f14 x6 + 0x1d82c,
0x2cb4a, 0x3c941, 0x49556, 0x495c4, 0x4982f, 0x4eabd + the 2 ff5104
predecessors); dialog strings 'Leave Orbit'/'Abandon'/'Scientist Takeover'
NOT in payload plaintext. Route forward (t304, NOT refuted): at ANY cos_hdlr
stop dump [esp] — ret0 names the real dispatch caller verbatim (bank_stop
PATCHED for this, ret_stack.ret0/ret0_file_off); arm the census there.
DEAD too as a control design: planet/empty/NEXTTURN clicks taken while an
unclosed modal dialog is up (t298 law re-broken in t303 — close_eventwin
BEFORE every control click; and a NEXTTURN control needs btn_hdlr ARMED).

## t304 AMENDMENT (binding): (1) T302/T303 'MAP-CLICK ENTRY IS NOT THE CLASS
## MSG LAYER' IS RE-SCOPED: btn_hdlr msg 0x1 NAME='Leave Orbit' fired for the
## pixel-proven working sprite click (48,151), reached via pump call site file
## 0x56cda (ff 56 08 call [esi+8]; [esp] ret0=0x21612d witnessed 41+12 times,
## run work/r1/t299-leg-20261105-033648). Slot-1 stays dead (t303 stands);
## 'not cos_hdlr, not slot-1' stands; 'not the class msg layer' is DEAD.
## (2) THE PRE-t304 SITE-ZERO-FIRE LOGS ARE A CORE ARTIFACT, NOT GAME
## EVIDENCE: `core` is a [cpu] setting (canonical dosbox-x-2026.10.01.conf
## L494-497) but sat under [dosbox] in every session conf (inert) -> all
## t299..t304 runs ran the DYNAMIC core (pty warning verbatim); dynrec checks
## heavy BPs only at run-loop top (core_dynrec.cpp:268) = indirect-branch
## targets, so mid-block call-site BPs CANNOT stop. Do not re-read those logs
## as dispatch evidence; do not re-arm site legs under a conf whose [cpu]
## section is missing.
## (3) UNDER THE FIXED CONF ZERO STOPS BANK EVEN FOR cos_hdlr (runs
## t299-leg-20261105-051904/-052925, guest alive) — UNRESOLVED instrument
## anomaly (STATE t305). Do NOT conclude handlers stopped being called.

## t305 AMENDMENT (binding): THE t304-(3) "NORMAL CORE BANKS ZERO STOPS"
## NON-ANOMALY IS RESOLVED AS AN INSTRUMENT DEFECT — the stops were happening
## unbanked (fire-pattern blindness). SOURCE LAW (debug.cpp DrawCode): the stop
## line is the unique PAIR_BLACK_GREEN (ESC[30m ESC[42m) prefixed render, and
## its address token is the full 0160:0021612A form OR a LEADING-ZERO-STRIPPED
## SUFFIX of variable length ('1612A', '60C4') — no fixed-width regex works.
## Run t299-leg-20261105-061825 (rc=0, fixed FirePat detector) MEASURED the
## click->dispatch map under the correct core: baseline pump 0x56cda msg 0x3b
## COSMOSWnd; sprite msg 0x8 PLIND (+btn_hdlr); planet msg 0x8 PLANETALLOC
## (t304's planet 'Cancel residue' SUPERSEDED — drain was applied); empty ONLY
## site 0x56c74; NEXTTURN msg 0x8 PLSQUARE (+btn_hdlr); 20 other slot-2 sites
## cited ZERO. Do NOT re-run the census to re-confirm this map; the writer of
## the SELECTION STORE (DAT_000482fb) is the remaining datum (OQ-019 open).
## Any debugger-log reading pre-t305: apply FirePat regression first
## (docs/re/dosbox-debugger.md t305 block).

## t306 AMENDMENT (binding): THE BATMODE STATIC-GATE ROUTE TO THE LIVE
## SELECTION WITNESS IS DEAD. Run t299-leg-20261105-101054 (rc=0, corrected
## core + FirePat, positive control btn_hdlr alive): the working sprite click
## fired ZERO at BatModeWnd entry 0x1aef8, msg-4 router 0x1b070, and effect
## writers 0x1b71f/0x1ba39 (ships.md S32). Do NOT re-arm these four legs for
## map clicks and do NOT re-derive the t296 gate map (it stands statically —
## the click layer simply never dispatches into BatModeWnd from the system
## view). The selection-writer hunt continues ONLY at the non-batmode members of
## the t296 cited store census (ships.md S24/S32): DAT_43508 {0x51a8e, 0x51fc2,
## 0x55bbd} and DAT_43504 {0x28ec2, 0x28ef6 cosmos star-click, 0x36b01
## diplomacy row, 0x52003 ship order-target, 0x55d35} — or by naming a
## DIFFERENT live-witnessed trigger for msg 0x53/0x50 (t296's widget imm
## census found none outside the batmode family; re-derive only from a
## witnessed poster, not another click battery).

## t308 AMENDMENT (binding): THE BRIGHT-DOT GALAXY-MAP PIP LAW IS DEAD. The
## sum(r+g,b)>380 nearest-first rule (r293 enter_system legacy) selects purple
## UI-text fragments and field dots at the campaign map, and its one hit was
## Icarus's own pip twice (same-value store = invisible datum). Do NOT reuse
## it for star selection. Use the GREEN-ANNULUS law (ships.md S34: green
## family {(0,85,40),(0,113,56),(0,142,69)} BFS clusters >=10px, centroid,
## >=50px from the known Icarus pip (238,282)). Also binding: the sav Memory
## member is +0x88 off guest linear — any "DAT address" quoted WITHOUT that
## conversion is void (t307 S1); the oracle at B+SL.OFF+X is CORRECT and the
## DAT-base question is CLOSED, do not re-open it.

## t309 AMENDMENT (binding): THE RING SELECTION CHANNEL IS DEAD AS AN
## EXPLANATION AT MAP IDLE — do NOT arm the 0x55ae8 consumer family (or the
## 0x55a60/0x56ad4 post fns) hoping map/star/turn clicks light them up.
## Measured run t299-leg-20261105-161711: post-fn ENTRY legs (gate-free
## prefixes) fired ZERO whole-log incl. two hot holds; ringB count/widx
## snapshots 0 in every window; the star-click RING-A post body never ran
## (idx stayed 0). Selection is RENDER-DIRECT (direct DAT_43504/08 stores).
## Also dead: (1) the t296 'selection posts ring code 0x10' reading — the
## star click posts RING-A {code=edx=1, param=ebx=0x10}, and RING-B's two
## 0x10 posters {0x41c17, 0x499e0} are never called at idle; (2) ringA_resolver
## 0x55df4 AS AN IDLE POSITIVE CONTROL (caller gate ([core+0x44aa]>>16)>0 is
## itself unincrementable at idle — a zero there proves nothing); (3) any
## whole-log count computed as fire_pats(LEGS[name]) — the harness form is
## fire_pats(P0+LEGS[name]), bare offsets count ZERO.

## t310 AMENDMENT (binding): (1) ds:0x484ec IS LAST-MOUSE-X, NOT A TURN
## COUNTER (measured 2/2: 0x30 after an x=48 click, 0x1b7 after x=439) — the
## t296/ships-S24-era 'turn-gated ds:0x484ec>0x96' label on the 0x51a8e store
## is DEAD; the fn-0x51834 msg-0x1c01 branch selects on screen-X>150. Do not
## schedule or gate anything on 0x484ec as a turn proxy. (2) FILE-IMAGE u32
## scans for class-table membership are STRUCTURALLY BLIND (relocated entries:
## fn 0x51834, cos_hdlr, btn_hdlr all 0 hits in the file, 1/1/4 hits in the
## sav Memory member at rebased value entry+P0) — the RAM scan of a run's own
## .sav is the ONLY class-table route; do not re-run file scans to 'confirm'
## zero membership. (3) fn 0x51834 IS THE STATUSWND MSG HANDLER (class grid RAM
## 0x248040, instance [win+0xa7]=0x5fc0 rebased->0x247FC0, sole magic-bearing
## referrer named 'STATUSWND') — a destination-widget hypothesis must go
## through STATUSWND focus + msg 0x1c01 (senders: 0x16168 relay, 0x35696 digit
## keys), not through generic map clicks: whole-log zeros at all five writer/
## relay legs with btn_hdlr x4 alive (run t299-leg-20261105-173627).

## t311 AMENDMENT (binding): "STATUSWND-FOCUSED DIGIT KEYS SEND 0x1c01 TO THE
## DESTINATION WRITER" IS DEAD AS A LIVE TRIGGER. Run
## t299-leg-20261105-182822 (rc=0, ENTRY leg fn51834_entry armed FIRST,
## control btn_hdlr x4 alive): the fn 0x51834 entry fired ZERO whole-log —
## the entry BP fires for ANY caller, so STATUSWND received NO msg of ANY id
## on the bare-map/key/fleet/planet/NEXTTURN battery. Measured focus datum:
## digit keys on the bare map hit btn_hdlr window 'NEXTTURNCONT' (button-
## family class, edx=0x3, ret0 file 0x3177d) — the map's key-focused window
## is NOT STATUSWND, so the digit sender's call [esi+8] structurally cannot
## reach fn 0x51834 from map focus. Do NOT re-arm fn51834_entry hoping a map
## battery messages it; the writer hunt continues ONLY via the order-
## placement choreography with fn 0x51b68's writer legs {0x52003, 0x51ac9,
## 0x51fc2} armed (t309 S3.4 inventory). Also banked: DAT_43508 churns
## 0x26fe77<->0x26f00d across autosaves with ZERO armed writers firing — a
## DAT delta is never a witnessed store (t298-C law re-observed).

## t312 AMENDMENT (binding): (1) "SPRITE-PIXEL CLICK SELECTS THE SHIP" IS DEAD.
## Run t299-leg-20261105-192246 (rc=0 attempt 1, fn 0x51b68's writer pair
## {w43504_52003, w43508_51fc2} armed whole-battery, control btn_hdlr x4
## alive): sel43510 = 0 in EVERY oracle snapshot including sprite_before AND
## sprite_after at the validated sprite (48,151), and mode4226 0x1->0x11 is
## the map->system VIEW id (t309 law), not a selection mode. The click
## dispatches msg 0x8 to 'PLIND' (repaint, t305 law) and selects nothing —
## identical in t305/t306/t311/t312. The t311 amendment's "writer hunt
## continues ONLY via the order-placement choreography" is therefore ITSELF
## now spent: without selection there is no order, so do NOT re-run this
## battery shape with fn 0x51b68 legs armed again. (2) BOTH in-image msg-
## 0x1c01 SENDERS ARE MEASURED DEAD: s2_1616f zero (t311) AND s2_356a5 zero
## (t312) even though digit keys demonstrably reach a window (btn_hdlr
## 'NEXTTURNCONT'). Do not arm either sender hoping another battery shape
## fires it. The OQ-019 residue is ONE hole (per-ship select); the next
## route is the fn 0x51b68 CALLER hunt via the t310 class-grid RAM scan
## (grid containing 0x51b68+P0: slot index FIRST, then which table the game
## consults) or a FLEET-window selection path — not another map battery.

## t313 AMENDMENT (binding): (1) "fn 0x51b68 IS A FUNCTION / ORPHAN" IS DEAD.
0x51b68 is mid-body of fn 0x51b64 = FLEETWND class-grid slot 3 (grid base RAM
0x248030, cp 0x247fa8 named 'FLEETWND' via magic rec 0xfe7a90). The writer
pair {0x52003 DAT_43504, 0x51fc2 DAT_43508} + the 0x52037 block are the
msg-0x1c01 continuation of FLEETWND's handler fn 0x51cc4 (je 0x51f3b exact),
reached via the SYSTEM-STATE jump table (file 0x3d100 unrelocated; RAM
instance 0x211188 {0x51fb5 x3, 0x51ff6, 0x52037}, runtime-composed, whole-RAM
unique). Do NOT re-run offline caller censuses on these targets: E8/jcc/u32
censuses are all measured zero AND the live edge is the runtime table —
offline is EXHAUSTED (t313 S8). (2) THE DESTINATION-WIDGET HUNT IS FLEETWND,
NOT STATUSWND: STATUSWND's 0x1c01 path exists (t310) but FLEETWND has its own
(0x51f3b), and the t312 dark-writer datum is explained by focus: digit-key
0x1c01 landed on 'NEXTTURNCONT' (btn class), never FLEETWND. Any future
0x1c01 trigger attempt MUST establish FLEET-window focus first (open_fleet
route exists in r299_leg_session.py) and arm fn51cc4_entry as census leg[0];
re-arming STATUSWND legs or bare-map senders is spent (t311+t312 stand).
(3) CLASS-GRID LAW FIXED: grids are stride-6 at grid_base; cp = grid_base-0x88
(magic rec: magic at rec+0x00, NAME rec+0x20, cp rec+0xa7); dispatcher =
0x30d37 call [cp+0xc]. t310's '0x248040 slot 4' = 8-byte-shifted read — use
r313_class_scan.py / r313_name_b.py, not hand walks.

## t314 AMENDMENT (binding): (1) "A DIGIT KEY UNDER FLEET-WINDOW FOCUS REACHES
## FLEETWND's 0x1c01 PATH" IS DEAD. Run t299-leg-20261105-212402 (rc=0, focus
## VERIFIED at arm: rails=188 + popup-closed reguard): fn51cc4_entry (armed
## 10x, all windows incl. fleet_keys) fired ZERO whole-log — FLEETWND receives
## NO msg of any kind from the keyboard with its window open. The only
## fleet_keys stop was btn_hdlr win='STATSHIPLST' msg 3 (ret0 file 0x32943,
## inside STATSHIPLST's own slot-2 fn, cp 0x247c70). Do NOT re-run the
## open_fleet->digit-keys shape expecting FLEETWND traffic; the sender (fn
## 0x35696, gated on [ebp+0xaf], call [esi+8] on ITS OWN window [ebp]) talks
## to the key-handler window family, and that family is NOT FLEETWND. (2) The
## live 0x1c01 hunt is NOT dead — it re-scopes: FIRST name the digit-handler
## window offline (fn containing 0x35696 -> class grid via the r313 RAM route
## -> magic rec). Re-arming fn51cc4_entry for keys is
## spent; a future LIVE attempt must trigger whatever UI the handler window
## actually is, or find a non-key sender (relay 0x1616f stays t311-dead on the
## tested battery). (3) DRIVE LAW: the fleet rowjump click (200,93) CLOSES the
## FLEET window (rails 188->0 measured) — any FLEET-focus phase runs BEFORE
## rowjump and re-asserts fleet_open at arm.

## t315 AMENDMENT (binding): (1) "A DIGIT KEY CAN REACH AN IN-GAME WINDOW'S
0x1c01 PATH" IS DEAD BY CONSTRUCTION. The handler fn containing the sender
0x35696 is fn 0x354f8 = class 'LOADSCREEN' (grid base RAM 0x247da8 slot 2, cp
0x247d20, magic rec 0xfd705c, 3/3 saves, controls 1-hit exact; loadwin.cpp
strings 'loadscr'/'LOADLIST'/'%02d.sav'). Digit->0x1c01 is the save-slot-pick
mechanism of the load screen. Do NOT design any further key-driven capture
shape expecting in-game 0x1c01 traffic. (2) THE 0x1c01 SENDER INVENTORY IS
CLOSED (whole-payload literal census = 5 sites, one an E8-operand false
positive): LOADSCREEN sender 0x35697, BatControlWnd receiver-site 0x1642c
(fn 0x16420 grid slot 3, cp 0x247850), relay 0x16169 (t311-dead), msg-emit
builder 0x33375 (via fn 0x56ca4). NO in-game-window sender exists — re-sweep
for senders is spent. (3) WINDOW-BASE LAW: the magic rec (0xfe7a90 FLEETWND)
is the accessor window; rec+0xab = instance block (0xfe7ac0, 'fleetwin');
gate chain = [rec+0xab] then [inst+0xc7+idx*8] -> record; FLEETWND gate byte
= GUEST 0x600058 (const 0, 212/212 valid-chain saves; datum 0x600059..c
const 0). A stale probe using 0xfe7ac0 as the window reads name-string bytes —
wrong base. (4) P0 LAW: bytes at B+off, POINTER VALUES at P0=B-0x88; data
absolutes read from patched code bytes (DAT_7e582=0x2c0582 at B+0x35561).

## t316 AMENDMENT (binding): (1) "THE WINDOW REGISTRY CAN BE WITNESSED FROM A
SAVE" IS DEAD BY MEASUREMENT: [obj(0x7a35c)+0x4226]==0 AND [obj+0x3000]==0 in
685/685 saves (u32+u16 reads; corpus = all work/r1/t299-leg-*/save/*.sav +
playcap/save/*.sav), whole-RAM u32 census finds no pointer to the FLEETWND
magic rec, yet 126 magic recs persist and registration fn 0x5712c (sole
0x12345678 writer, file 0x57173) is ctor-wired. The registry is rebuilt
in-session and NOT persisted — do NOT design any further save-scan witness
against the registry, mode4226, or slot tables; only LIVE legs count.
(2) THE EMIT OWNER IS NAMED, DO NOT RE-HUNT: fn 0x33320 (0x1c01/0x1c02 pair
builder, sole E8 caller 0x32778 in STATSHIPLST slot-2 fn 0x32664 in-rect
msg-0xc branch); target edx=[w+0x63]=95=FLEETWND slot-id (rec+0x41 law, ctor
fn 0x3264c writes fn 0x5712c's return to rec+0x41). The t315 branch question
("map/HUD pump vs table excludes FLEETWND") is RESOLVED: STATSHIPLST emits AT
FLEETWND. (3) t315 S6's mode4226 RAM value 0x23c7969f was a cmpl-disp32
mis-parse — the true value is 0; do not cite it. (4) NEXT LIVE shape for
OQ-019 (t317): FLEET open (rails=188 reguard, NO rowjump) + click INSIDE
STATSHIPLST rect (7,46,632,472 per 60.sav; fn 0x33320 guard [w+0xbf]=28 means
the msg arg must exceed 28 — verify arg semantics in fn 0x33058 before
picking coordinates), legs {fn 0x56ca4 entry, fn51cc4_entry, w43508_51fc2,
w43504_52003}. Key-driven shapes stay dead (t314/t315).

## t317 AMENDMENT (binding): (1) "A STATSHIPLST GUTTER/ROW CLICK POSTS MSG
0xc (or 4/5) INTO fn 0x32664" IS DEAD BY LIVE MEASUREMENT: 4/4 clicks at
x=620 y{250,120,453,300} (run work/r1/t299-leg-20261106-012002, strip law
604<X<=632 verified from saves [w+0xb3]=-1 [w+0xbf]=28) arrived at fn 0x56ca4
AS MSG 8 DISPATCHED ON STATSHIPLST'S OWN REGISTRY ENTRY (edi=edx=0x8,
eax=0xfe7ac0 NAME='STATSHIPLST', ebx=620/ecx=ebp=Y verbatim; baseline window
0 stops). fn 0x32664's msg-8 arm -> fn 0x33058 (row bookkeeping; gutter
sub-branch self-sends 0x193 + clearers fn 0x56730/fn 0x56434). Do NOT design
another click-shape run expecting the t316 emit chain to fire from fn 0x56ca4.
(2) THE 0x1c01 DELIVERY NEVER HAPPENED: fn51cc4_entry ZERO whole-log,
w43508/w43504 ZERO, gate guest 0x600058=0 datum 0 after every window.
(3) THE msg-0xc/4 INTAKE ROAD IS THE BROADCAST PUMP fn 0x56b5c (slot-2
dispatch call *[tgt+0xa7+8] @file 0x56c74; posters 0x54aa9/0x54ab2 from the
click record ds:0x484ec/0x484f0; suppression ds:0xa2024). A run that arms
s2_56cda but NOT s2_56c74 CANNOT see msg-0xc/4 deliveries — t317's zero is
an ARMING SCOPE fact for msg 0xc/4, not a measurement of them.
(4) [w+0x4f] HAS NO BYTE-ADDRESSED WRITER (payload-wide census, disp8+disp32,
movb/movw/movl imm+reg: sole store movb $0,[r+0x4f] @0x30bdb); the measured
0x66 is template/record-copy written — do not hunt a setter instruction.
(5) NEXT LIVE SHAPE (t318): legs {s2_56c74, s2_56cda, fn51cc4_entry,
w43508_51fc2, w43504_52003} + the proven --shipclick choreography
(_wip_t317 S8).

## t318 AMENDMENT (binding): (1) "THE BROADCAST PUMP DELIVERS THE VENDOR
## CLICK (OR ANY MSG) TO FLEETWND VIA 0x56c74" IS DEAD FOR THE OBSERVED
## ROAD: run work/r1/t299-leg-20261106-021602 (rc=0, 9 armed windows, legs
## {s2_56c74, s2_56cda, fn51cc4_entry, w43508_51fc2, w43504_52003,
## btn_hdlr}) — s2_56c74 ZERO whole-log while s2_56cda fired 26x (18 msg
## 0x3b COSMOSWnd, 4 msg 8 STATSHIPLST at the x=620 gutter clicks, msg 8/6
## PLIND, 2x msg 8 PLANETALLOC). fn51cc4_entry ZERO a 2nd whole-run time;
## 0x1c01/0x1c02 literal absent from every banked reg/stack. Do NOT design
## another run betting the pump dispatch closes the destination-fire
## residue. SCOPE (do not overclaim): legs are deleted between census
## windows and during fire-cycle re-arm gaps — the zero is "nothing
## observable delivered", NOT "fn 0x56b5c never called".
## (2) THE NAMED BLOCKER MOVED TO THE POSTER GATE: static re-read
## (t91_code_disasm 77195-77245 verbatim) — pump call 0x54ac5 is reached
## past cmp edi,ds:0x484a4 @0x54a3f (equal road: fn 0x5be9b query, msg-0x3f1
## dispatch @0x54a83, pump ONLY if [[esi+0x21d92]+0x39]!=0) and cmp
## edi,[esi+0x24da4] @0x54a88 (equal AND [esi+0x489e]==0 -> msg 0xc, else
## msg 4). fn 0x56b5c has NINE E8 callers (0x53fa3 d, 0x54976 3, 0x54ac5
## 4/0xc, 0x54b36 5, 0x5531e f, 0x5548c e, 0x55f82 d, 0x56f0f 2, 0x57003 1).
## (3) NEXT LIVE SHAPE (t319, one run): legs {pump_entry_56b5c=0x56B5C
## (bytes 56 57 55 83 ec 10 89 c7 66 89 54 24 08), p54a47=0x54A47,
## p54a88=0x54A88, s2_56c74, s2_56cda} + the proven --shipclick 4 + standard
## tail; bank ret0 (caller) + edx (msg id) at the entry. fn51cc4_entry and
## the writer pair DROP (zero twice, downstream). If the entry never fires
## while p54a88 fires, the poster-gate equalities are decodable OFFLINE from
## saves (ds:0x484a4, [obj+0x24da4], [obj+0x489e] reads) — do not spend a
## second capture on the same legs.

## t319 AMENDMENT (binding): (1) THE THREE-WAY PUMP QUESTION IS RESOLVED —
## DO NOT RE-ARM {pump_entry_56b5c, p54a47, p54a88} TO ASK IT AGAIN: run
## work/r1/t299-leg-20261106-030727 (rc=0 attempt-1) banked the POSTER CALL
## SITE LIVE — pump_entry stop edx=0x4 (msg 4), esi=eax=0x2bc35c,
## edi=0xffffffff, ret0 file 0x54aca = E8 0x54ac5, 6 s after gutter click
## y=453. caller-never and pump-entry-never are DEAD readings; gate-never-
## equal CONFIRMED. (2) THE NAMED BLOCKER IS NOW THE EXACT EQUALITY: msg 0xc
## requires [core+0x24da4]==-1 (measured 0 in every save read via
## scripts/r319_gate_read.py; edi at the fire = [core+0x24da8] = -1 so the
## 0x54a88 cmp is unequal -> msg 4 @0x54ab0); the equal road requires
## ds:0x484a4==-1 (measured 0). [core+0x489e]==0 already true — do NOT spend
## a capture on +0x489e. (3) THE MSG-4 POSTER HAS NO OBSERVABLE EFFECT:
## whole-run DAT_43508/43504 oracles unmoved, 0x1c01/0x1c02 literal absent
## all 108 banked stops — betting another capture on "msg 4 eventually does
## the destination store" is dead until a writer census says otherwise.
## (4) BLOCK-ENTRY CONJUNCTION (law, do not re-derive): the poster region
## runs iff ds:0x484dc==-1 AND ds:0x484d0!=0 AND [core+0x24da8]==-1; the -1
## is set by mouse-state recorder fn 0x2a7a4 (0x2a7a8-0x2a7bb: arg2 !=
## ds:0x484d0 -> store arg2, set 484dc=-1). Fired ONCE in 28 min.

## t320 AMENDMENT (binding): (1) "A CLICK PULSE TRAIN MAKES THE POSTER PASS
## FIRE MSG 0xc" IS DEAD: run work/r1/t299-leg-20261106-041522 (rc=0
## attempt-1, legs {pump_entry_56b5c}, --shipclick 4 + --pulse-clicks 30) —
## 27/27 banked poster stops edx=0x4 (msg 4), zero msg 0xc, despite pulses
## logged inside the armed windows seconds before stops. DO NOT re-run any
## short-press click-train shape betting on the 24da4 gate. (2) ds:0x484ac IS
## THE BIOS BUTTON-HELD WORD (fn 0x2a5f0 = int 16h AH=2 poll; -1 @0x2a629 iff
## AL&1 or AL&2, else store 0 @0x2a635 — t91_code_disasm 24853-24866
## verbatim): the word is set ONLY while a button is physically held at poll
## time, and ms-scale polls clear it seconds after a 50-ms press. t319's
## "mouse-active flag" reading survives only as HELD-button. (3) THE POSTER
## BLOCK IS CLICK-TRAFFIC-DRIVEN, NOT RARE (corrects t319 S4.2 scope): 27
## fires in 18 min under traffic vs 1 in 28 min idle-ish; baseline windows
## still bank 0 (idle conjunction law holds); control_nextturn windows fired
## 3x with no pulses (484dc=-1 persists after traffic). (4) THE NEXT (t321)
## SHAPE IF PURSUED: press-only Button1 HOLD across the armed window (xsend.c
## press_only machinery; add clickhold/clickrelease, ALWAYS release before
## the run tail) — premise: DOSBox int16 AH=2 reports a parked synthetic
## ButtonPress as held. xdotool absent + SDL rejects synthetic MotionNotify:
## motion-shaped levers are dead on this host, full stop.

## t321 AMENDMENT (binding): (1) THE MSG-4/0xc -> DAT-STORE ROAD FROM
## FLEETWND DOES NOT EXIST — CLOSED STATICALLY, VERBATIM: fn 0x51cc4 has NO
## dedicated msg-4 or msg-0xc branch (dispatch cmp dx,2 @0x51ce5 / cmp
## dx,0x1c01 @0x51cf5; everything else falls through 0x51d00 -> tail-call fn
## 0x336b4), and fn 0x336b4's full tree (0x30f55/0x30de2/0x30f46/0x30dbb/
## 0x30dd2/0x30fa9/0x30f26) contains ZERO stores to ds:0x43508/0x43504 — msg
## 4 goes rect-gated ring-post-or-registry-forward, msg 0xc goes rect-gated
## ring post code 5 ONLY. DO NOT bet any further capture (incl. the t320(4)
## Button1-HOLD shape) on poster msg 4/0xc reaching the destination store:
## HOLD is now dead for OQ-019 regardless of whether it flips the poster
## gate. (2) MSG-0x50 HAS NO SENDER OUTSIDE fn 0x1aef8 (BatModeWnd): whole-
## image `mov edx,0x50` census = 3 sites (0x1519d nullified by `sub edx,eax`
## @0x151a2; 0x3a9e7 -> call fn 0x2fb38 103-caller generic; 0x71af3 -> fn
## 0x782be), none a msg dispatch; sole publish-block entry jbe 0x1b7d7 (cmp
## dx,0x50 @0x1b7cd). The t296 "destination-entry widget" framing is DEAD as
## a search target — publication is reachable ONLY via batcon msg-0x1c01
## legs (0x51fc2/0x52003 window-side) or the batcon click state machine fn
## 0x1b91c @0x1baa7 / fn 0x1aef8 @0x1b5e6. (3) HARNESS BLIND-SPOT (fix
## before any writer capture): r299_leg_session.py NEVER armed 0x1b5e6/
## 0x1baa7 (the LEGS dict lines 224-231 lists ONLY w43504_{28ec2,28ef6,
## 36b01,52003,55d35} + w43508_{51a8e,51fc2,55bbd}; 0x1b5e6 appears in
## scripts/ solely as r296_selection_note.py offline documentation, never
## as a leg). All "DAT writer zero whole-log" negatives t307..t312 are statements
## about the OTHER eight sites, NOT the batcon click road. (4) t297's "msg-4
## router 0x1b070 routes EVERY click to batcon 0x1b91c" is INTERNAL to fn
## 0x1aef8 (callers 0x1b0cc/0x1b1de inside it) — it is NOT a global router;
## do not cite it as a way for a galaxy click to reach fn 0x1b91c without
## BatModeWnd first receiving the msg.

## t322 AMENDMENT (binding): THE BATCON MOUSE ROAD IS DEAD IN-CAPTURE — DO
## NOT RUN A THIRD MOUSE BATTERY. The t321(3) blind spot was closed by the
## first-ever live arming of legs {batmode_dead 0x1AEF8, fn1b91c_entry 0x1B91C,
## w43508_1b5e6, w43508_1baa7} over the full t298-shape battery (run
## work/r1/t299-leg-20261106-055549 rc=0, census-ctl MATCH=True, btn_hdlr 3):
## pty whole-log ZERO at all four batcon legs; BatModeWnd received no msg at
## all, session-wide (t306 = second independent entry-zero). (1) DEAD: any
## further capture whose theory is "click the right pixel / in the right order
## and fn 0x1aef8 wakes" — the window is composition-shielded (windows.txt
## 1178 STATE 1 16 never active in captured sessions); no click can hit-test
## into it. (2) The ONLY remaining OQ-019 select/destination route is the
## OFFLINE activation decode (_wip_t322 S6: who writes the window-record STATE
## field / fn 0x1d7dc / fn 0x1be10 / registry instance 0x247978 neighbourhood);
## a capture is justified ONLY after that decode names a concrete activator
## widget or keypress. (3) Harness defect banked (fix before any future
## click-window capture): census_click closes popups BEFORE arming, so a
## popup that opens/persists after the reguard spends the armed window
## (t322 planet stop banked 'Cancel' instead of the map click).

## t323 AMENDMENT (binding): BATMODEWnd ACTIVATION HAS NO IN-SESSION TRIGGER
## — THE t322(2) ACTIVATION-DECODE ROUTE IS NOW ITSELF CLOSED (negative), AND
## WITH IT EVERY IN-CAMPAIGN ROUTE TO THE OQ-019 SELECT/DESTINATION RESIDUES.
## Census-complete static evidence: docs/re/_wip_t323.md S0-S6 + ships.md S49.
## (1) DEAD: any future attempt to "activate/show/switch BatModeWnd" from
## inside a captured campaign session (click, key, msg, or menu). The STATE
## line is the state-RECORD table (loader fn 0x31d58 / sizing fn 0x32000),
## runtime state = WORD [win+0xb1]; the image-wide [win+0xb1] writer census
## (14 sites) yields ONLY constructors (fn 0x31c54/0x3377c/0x33d08/0x33c34),
## the char-input cycler fn 0x339a4 (no char handler exists in BatModeWnd's
## cited msg tree), a table-not-window store (fn 0x364d2), and fn 0x31f30
## reachable EXCLUSIVELY through fn 0x32100 (generic state-rect-click msgs
## 0..8), which is NOT in the cited BATMODE class table (t296). The window's
## state is PINNED at construction.
## (2) DEAD as a search target: "the BatModeWnd name in code" as evidence of
## a control path. All three fn 0x2351c call sites (0x21530 boot-gated by
## fn 0x78283("resume.gam"), 0x24f96, 0x52a76) pass the name immediate as a
## DEAD assert-string arg (overwritten @0x23558 before use; body = layout
## bookkeeping at ds:0x48c44 + [wmgr+0x32dda]); fn 0x156d4 (BATCTRL) stores
## the fn 0x56d1c(0x5e="BatModeWnd") result UNREAD and resets BatListWnd
## instead. Do not re-open these as activator candidates.
## (3) DISPOSITION: OQ-019 select/destination residues (msg-0x50 destination
## publication, live DAT_43508/0x43504 stores via fn 0x1b5e6/0x1baa7, the
## kind-2 kind-clip per-ship select) = UNREACHABLE-BY-CAPTURE from the
## t=1086 sitting corpus; law stands static-cited (t296 S5 four gates, t321
## S1-S4). RE-OPEN CONDITION (narrow, explicit): a RAM class-table census
## showing any [rec+0xb1] writer (e.g. fn 0x32100) installed at
## BatModeWnd's [rec+0xa7] table, OR a DIFFERENT save/sitting where a
## kind-4 owner-0 ship exists AND BatModeWnd is witnessed live (entry leg
## fires) — absent either, no capture spends on this residue are justified.
## (4) fn 0x1d7dc (repaint/teardown) and fn 0x1be10 (cursor chooser, keyed
## on ds:0x7d35e==[win+0x41]) are NOT activators — t322 S6 candidate list
## retired.

## t331 AMENDMENT (binding): t326b's MSG-0x51 CONSUMER CLOSURE IS REFUTED — THE
## MODE-1 ARMING ROAD IS ALIVE-IN-IMAGE; and three route-framings die with it.
## Evidence: docs/re/_wip_t331.md S2-S7 (fresh whole-code objdump 139,026 insns,
## zero badbar; live-record reads via pointer law, 20/20 saves).
## (1) REFUTED: "BatModeWnd fn 0x1aef8 does not consume msg 0x51" (t326b S8(3)).
##     Dispatch tail bytes: 1b7cd 66 83 fa 50 (cmp dx,0x50); 1b7d1 jb 0x1af4e;
##     1b7d7 jbe 0x1b5ba; 1b7dd c6 85 b7 00 00 00 01 (BYTE[+0xb7]=1 MODE-1).
##     dx==0x51 fails jb AND jbe -> falls through onto the mode-1 store.
## (2) DEAD: reusing the t329 disposition-packet argument "no arming trigger
##     exists" for residue (1); replaced by the cited chain (msg 0x1c01 ->
##     BatControlWnd slot 61 -> RAM jump table member 0x1d4b04 entry[1] -> gate
##     0x15fed -> poster 0x1615d/0x161d1 -> slot 63 BatModeWnd -> 0x1b7dd).
##     Do NOT re-walk the 0x4c/0x4d/0x4e indexing family (t326b indexing half
##     STANDS) and do NOT re-derive the gizmo flag words: sole writer fn 0x49074
##     (gizmos.txt flag_list loader; Phase^Bomb flags = bit0x8 only).
## (3) DEAD: raw-reading a cs:[disp32] JUMP TABLE from the file image (t331 hit
##     the false-zero: file 0x836b4 holds the "...cosmos.cpp" assert string; the
##     live table is REBASED at member 0x1d4b04). Always RAM-scan by target-range.
## (4) DEAD: "no BatModeWnd window record is resident in the corpus" (t324
##     caveat). Records store RAW ASCII NAME at +0x20 (magic 0x12345678 at -0x20):
##     BatModeWnd rec runtime 0xfdc89c, slot-id[+0x41]=63, registry slot 63 MATCH,
##     20/20 t=1086 saves; state [+0xb1]=0, state-table [+0xab]=NULL (setter
##     fn 0x31f30 bounds-asserts any id>=0 with count 0 — construction-pinned).
## (5) SCOPE: t322's BatModeWnd armed-zero does NOT test the BatControlWnd chain
##     (fn 0x156d4 slot 2 never armed in ANY capture; no battery ever clicked
##     My^Items screen-rect (559..628, 203..233)). A t332 capture MUST arm
##     fn 0x156d4_entry before claiming any negative on this road.

## t332 AMENDMENT (binding): THE BatControlWnd CHAIN IS INSTRUMENTED-AND-MEASURED
## ZERO; NO FURTHER MOUSE BATTERY MAY TARGET IT, AND THE OBSTACLE IS THE ACTIVE
## SCREEN STATE. Evidence: work/r1/dbg-t332-20261107-124717 (rc=0, tool
## scripts/r332_batctrl_session.py), docs/re/_wip_t332.md S4-S8, docs/re/ships.md S51.
## (1) CLOSED-BY-MEASUREMENT (negative): t331 correction C4's blind spot. With the
##     entry leg fn156d4_entry 0x156D4 armed (dedicated sub-battery) AND the item
##     rects clicked — (513,118) My^Items and (591,118) Other^Items in text space,
##     on the strategic map and in the entered view — the pty whole-log census is
##     ZERO at all eight chain legs {0x156D4, 0x15EF1, 0x15FED, 0x1615D, 0x1616F,
##     0x161D1, 0x1B7DD, 0x1B180} with the control btn_hdlr firing 8x. BatControlWnd
##     received NO message of any id; the mode-1 store 0x1B7DD has never fired in
##     any capture. Do NOT re-run this battery to "catch it this time".
## (2) DEAD: any click-road route to the state-16 window family. Fresh windows.txt
##     census: STATE 1 16 is EXCLUSIVELY the 19-window battle-map family
##     {BatControlWnd, BatListWnd, BatModeWnd, TOGGRID, BATROTLEFT, BATROTRIGHT,
##     BATZOOMIN, BATZOOMOUT, RECENTER, TOGELEV, ABANDON, My^Items, Other^Items,
##     Repeat, Pass, Auto, W, S, Z, I}. Measured states in captures:
##     NEXTTURN/NEXTTURNCONT 1, PLIND/PLBUILD/PLANETALLOC 17, FLEETWND 18,
##     COSMOSWnd {1,3,7,13} — ZERO overlap with 16. Banked stops name the owning
##     window at the pixel: (513,118)/(591,118) -> NEXTTURNCONT (map) / PLIND
##     (rowjump view); (553,200)/(593,218) -> PLBUILD. The t253 FLEET rowjump
##     enters the PLANET/orbital state, NOT a battle screen — do not treat it as
##     reaching state 16.
## (3) THE ONE NAMED EDGE LEFT is ZERO-CAPTURE: the GLOBAL active-screen-state
##     writer (the id the windows.txt STATE-line composition law consumes: fn
##     0x31d58, composition loop 0x5898e..0x58b3e). Do not spend further captures
##     on residue (1) until that decode names an activator.
## (4) MECHANISM FOUND (not a refutation, the reason an imm census was blind): the
##     msg-0x1c01 delivery is fn 0x156d4's OWN shared tail 0x16162..0x1616f —
##     `mov ebx,[ebp+0xa7]; mov edx,0x1c01; mov eax,ebp; call [ebx+0xc]`, a
##     class-table SELF-RELAY. Immediate censuses cannot see table calls; do not
##     re-open "who posts 0x1c01 to slot 61" as an imm-census question.
## (5) LAW: click coordinates are GAME/text space (windows.txt numbers; NEXTTURN
##     (511,67), FLEET (553,184)). The (80,100) origin is a GRAB-TIME crop offset
##     (r293_move_session.py:73/:121). Screen-space forms like "My^Items screen
##     559..628,203..233" or "(593,218)" must be converted back (-80,-100) before
##     being used as click targets — measured: (513,118) and (593,218) hit
##     DIFFERENT windows (NEXTTURNCONT vs PLBUILD).

## t333 AMENDMENT (binding): THE ACTIVE-SCREEN-STATE ROUTE IS A CATEGORY ERROR,
## fn 0x31d58 IS A CONTROL-FLAG WRITER, AND FIXED-0x88 ds: READS ACROSS SAVE DIRS
## ARE INVALID. Evidence: docs/re/_wip_t333.md S0-S9, docs/re/ships.md S52,
## scripts/r333b_state_layout.py (exit 0, 372 saves / 42,780 window records).
## (1) DEAD: "the +0xa set / fn 0x31d58 names or selects the active screen
##     state". [win+0xab] is the per-window CONTROL table — byte-proved:
##     RACECONTROLS rec[0] `01 00|df 01 ef 01|c1 01 d1 01|05 00|14 00` ==
##     windows.txt:429 `RACE1CONTROL 1 479 449 495 465 0 20`; ids across recs are
##     the RACEnCONTROL bitmasks 1,2,4,8,16,32,64. fn 0x31d58's only store
##     0x31dd0 writes control flags. Do not re-open this as a screen-selection
##     question.
## (2) DEAD: hunting a GLOBAL active-screen-state datum. Zero store forms to
##     ds:0x13b98 over the entire code image (r331 disasm 0x14bb0..0x826a5 +
##     fresh 0x0..0x14bb0 objdump). Active screen is a parse-time property; the
##     windows.txt keyword literals (PARENT/NUMCONTROLS/SHAPEFRAME/HELPINDEX/X0/
##     BACKGRNDCOLOR) occur ZERO times in ascend_restored.bin, ascend_payload.bin,
##     ascend_raw.bin, t73c_obj1slab.bin — only in game/ascend00.cob. Do not hunt
##     the STATE-line consumer inside the RE image on keyword evidence.
## (3) LAW: [win+0xb1] is the CURRENT CONTROL INDEX (0/0xffff when no controls),
##     never a state id; [win+0xaf] is the control COUNT; the interleaved-u16
##     layout means u16@+0xad and u32@+0xad>>16 are DIFFERENT quantities. t333's
##     own S3 "layout contradiction" was this misread — do not cite it.
## (4) LAW: the .sav-member = linear + 0x88 delta is NOT constant across save
##     dirs. The +0x88 probe on playcap saves yields jump-table entries
##     0x1d5349/0x1d543d/0x1d55d1 where t332 (dbg-t331 run) measured
##     0x15ef9/0x15fed/0x16181. Re-derive per save (r1_slot.base_of) and validate
##     with a known needle IN THE SAME SAVE before reading any ds: global.
## (5) UNINFORMATIVE SHAPE: scanning window records for byte encodings of
##     OR(1<<state_id) matches 1-2 spurious offsets for EVERY window (~60
##     candidates each); small-int records defeat 2-byte value search.

## t334 AMENDMENT (binding): THE STATE LINE'S RUNTIME HOME IS win+0x6d (STRIDE
## 13, counter [win+0xa1]) AND IT IS WRITE-ONLY IN THE RE IMAGE; THE 0x3000-RANGE
## PARSER CONSTANTS ARE DATA-SEGMENT FORMAT STRINGS, NOT windows.txt OFFSETS.
## Evidence: docs/re/_wip_t334.md S0-S13, docs/re/ships.md S53,
## scripts/r334_parse_map.py (exit 0, 152 call-sites), scripts/r334_state_array.py
## (exit 0, 196 needle-verified saves).
## (1) CORRECTION (not refutation) of t333 amendment-(2) wording: "the STATE line
##     is consumed at parse time and its runtime home is NOT in the window
##     record" is WRONG as written — parse loop 0x57ee6..0x57ff5 (fn 0x575e4)
##     writes a per-window inline array at win+0x6d, stride 13, compacted by
##     fn 0x31690 (asserts [win+0x9f]>>16 >= 4; dst = win + 13*[win+0xa1] + 0x6d;
##     exactly 13 bytes via movs; [win+0xa1]++), non-zero ids != 1 hit vendor
##     assert winmgr.cpp:0xcd6 (0x5804c). The VALID part of t333's conclusion
##     survives on new evidence: the array's ONLY literal +0x6d operands are
##     0x57f06 and 0x316de (fresh 0x0..0x14bb0 objdump adds none), and the ONLY
##     in-image WALKER is paint fn 0x31384 (via `add ebp,0x6d`/`add ebp,0xd`
##     pointer arithmetic, callers EXACTLY 0x3117f/0x3135a inside paint fn
##     0x30fb8) which renders slots as TEXT/HANDLES (byte0 0/1/>1 -> format
##     0x7d3aa / fn 0x1fc34 / assert) — never a screen selector; and 196 saves
##     show battle-window counters [win+0xa1]=0 with agreement only on
##     count==0 windows. Do NOT re-open "the STATE line selects a screen at
##     runtime" and do NOT re-run the win+0x6d flag-array census unchanged —
##     [win+0xa1] is the slot counter, not the flags. (Interim retraction: an
##     earlier S12 reading "ds:0x6fda8 is a global stride-13 STATE array" is
##     WRONG — fn 0x315c4/0x31660 body is a `repnz scas` NAME INTERNER over a
##     0x400-byte string pool, counter ds:0x701a6; _wip_t334 S13.)
## (2) DEAD: treating the parser's 0x3000-range pushed constants as windows.txt
##     file offsets. Save-probe cited: ds:0x3008 at B+0x82bb0+0x3008 reads
##     `%s %d\0..\winmgr.cpp\0...` (scan FORMAT STRINGS in the loaded DATA
##     segment); the readable-ASCII coincidences in windows.txt at those numbers
##     are coincidences. Keyword matching lives in the scanner machinery
##     (0x7a1f7 + handler 0x77f64 + table 0x63402), consistent with t333's
##     keyword-literal ZERO result.
## (3) MEASURED: WORD ds:0x13b98 = 4 in 196/196 needle-verified saves (turns
##     1086-1087). This cites t333's [inferred] per-player-slot enablement bound
##     (ids 1,2,4,8 set / 16,32,64 clear). The value has NO writer in the code
##     image (t333 amendment-(2) stands) — it is initialised outside the
##     disassembled code. ds: READ LAW for obj1 data offsets is
##     member_addr = B + 0x82bb0 + X (r1_slot.py); using B + X rejects 196/196
##     saves — that is a harness error, distinct from t333 amendment-(4), which
##     governs pointer-value -> member conversions.
## (4) DEAD: hunting an allocator at the control-table attach sites. 0x57d56/
##     0x57e48 are fallthrough-only sequential parse code (whole-body
##     branch-target scan: no jump lands on the guard blocks); the stored value
##     is the scanner's parsed u32 copied verbatim under status [esp+0x3a6]>>16
##     == 15 (poison -1 under == 25 when parsed != 0); no imul-14 exists in the
##     2,328-insn parse fn.

## t335 AMENDMENT (2026-11-08) — BINDING. THE win+0x6d STRIDE-13 ARRAY IS THE
## WINDOW-ITEM ARRAY; FOUR ROUTES DIE HERE (evidence: docs/re/_wip_t335.md S1-S5,
## docs/re/ships.md S54, scripts/r335b_item_array.py exit 0, 196/196 saves).
## (1) DEAD, SUPERSEDING t334 amendment-(1): ANY further "STATE-line consumer at
##     win+0x6d" work. MEASURED: [win+0xa1] == TEXTITEM+SHAPEITEM line count
##     22398/22398 exact (STATE-count test fails 3844/18554); byte0 == item kind
##     4900/4900; tag0 u32@+1 -> interner ds:0x6fda8 string == file item NAME
##     verbatim 3528/3528; record-bearing windows == exactly the 15 item-line
##     windows. The block 0x57ee6..0x58062 (entry fn 0x575e4) is the
##     WINITEMS/TEXTITEM/SHAPEITEM builder: 0x3101 "%s %d" scans WINITEMS,
##     0x3107 "%s %d" scans the item kind, 0x310d/0x3119 "%s %d %d %d" the
##     name+triple. t334's STATE-array reading is RETRACTED (mis-attribution).
## (2) DEAD: the `STATE 1 16` assert-paradox line of attack (t334 handoff item
##     B). The branch tests the ITEM KIND (file values {0,1} only, 18+7 lines),
##     so else-assert 0x5804c (-> 0x2a438 eax=0 -> 0x76c79 -> int3 0x2a424) is
##     unreachable for shipped data; STATE ids never enter this block. Re-deriving
##     it further is exhausted.
## (3) DEAD: hunting resident windows.txt text in .sav Memory members. MEASURED:
##     `NUMCONTROLS` occurs in 0 of 284 save dirs; `STATE \d+` hits are C-literal
##     fragments (e.g. "BatModeWnd\0" beside "..\batcon.cpp" at 0x2420e6 in
##     41.sav). t333's "text IS resident (member 0x39db51)" does NOT reproduce in
##     the playcap corpus. File-vs-RAM diffs take truth from the ON-DISK
##     extracted/ascend00/windows.txt joined by window NAME (magic+NAME law).
## (4) LAW (not a route): fn 0x31690's `cmp ([eax+0x9f]>>16), 4` gate IS the u16
##     item counter at +0xa1 (same 16 bits) — a max-4-items cap, NOT a
##     window-type check; do not re-read it as a type assertion.

## t337 AMENDMENT (binding): (1) THE STATE-TABLE READER WALK IS DONE — the
complete reader inventory is docs/re/_wip_t337.md S1/S2 + ships.md S56 (16
functions over displacements +0x3066/+0x3068/+0x306a/+0x4226 and every
`imul *,0x8e` in the 139,026-insn image). Do NOT re-sweep for readers.
(2) DO NOT RE-ASSERT t333's "there is NO global active-screen-state datum":
the datum is u16 core+0x4228 (CURRENT STATE ID), sole runtime writer 0x56f66
inside SET-STATE fn 0x56e10, MEASURED 537 saves {0:122,1:236,16:5,17:174}.
Every `mov r32,[X+0x4226]; sar r32,0x10` site reads the CURRENT STATE, not the
group count (LOW u16 = count; inc 0x57207 / dec 0x5711e only).
(3) NO IN-IMAGE BROADCAST EVER TARGETS STATE GROUP 16: all nine fn 0x56b5c
call sites pass fixed immediates {1,2,3,4,5,0xd,0xe,0xf} (verbatim-cited
_wip_t337 S4). Hunting "a group-16 broadcast" is spent; state-16 traffic is
hit-test/post-to-handle routed (fn 0x56890 / 0x56ca4).
(4) t326/t331's "research leg vacuous"/"mode-1 armed-zero" re-reads stand, but
t332's zero-witness capture is now KNOWN to have run entirely in states
{0,1,17} — any future arming witness MUST run with core+0x4228==16 (resident
state-16 saves: work/r1/t299-leg-20261105-112859/save/43..47.sav); a zero log
from a non-16 state is NOT evidence of unreachability.

## t338 AMENDMENT (binding): THE STATE-16 LIVE DRIVE IS EXECUTED AND MEASURED
## ZERO; "THE OBSTACLE IS THE ACTIVE SCREEN STATE" IS SUPERSEDED; BatControlWnd
## CAN NEVER BE A MOUSE HIT TARGET. Evidence: work/r1/dbg-t338-20261107-224027
## (rc=0, tool scripts/r338_state16_session.py), docs/re/ships.md S57,
## docs/re/_wip_t338.md S0-S4.
## (1) CLOSED-BY-MEASUREMENT (negative): with the game DRIVEN INTO state 16
##     (SET-STATE fn 0x56e10 witnessed live with edx=0x10; 13 save-oracle reads
##     state==16; hit_test fn 0x56890 x2; btn_hdlr x17 on the state-16 family
##     rows), the pty whole-log census at all eight chain legs {0x156D4, 0x15EF1,
##     0x15FED, 0x1615D, 0x1616F, 0x161D1, 0x1B7DD, 0x1B180} is ZERO and
##     BatModeWnd +0xb7==1 appears in ZERO oracle reads. t332 clause (3)'s
##     obstacle-claim (captures sat in the wrong state) is SUPERSEDED — state 16
##     was reached, state-16 hit-testing ran, the chain stayed zero. Do NOT run
##     another mouse battery at this chain in ANY state; the closure-class is now
##     the fn 0x156d4 intake decode (who posts 0x1c01 to registry slot 61) or a
##     user ruling (D2-c).
## (2) LAW (trigger, measured + reproducible): state 16 is entered by the
##     galaxy-map Icarus-pip click (238,282) (enter diff 94504; the five
##     state-16 saves of t299-leg-20261105-112859 sit exactly inside that click's
##     census window; Escape exits). The FLEET rowjump enters state 17 (t332
##     stands). Do not re-hunt "how does play reach state 16".
## (3) LAW (geometry): BatControlWnd is TYPE 19 PARENT with rect 0,0-0,0 — it has
##     NO own hit rectangle; every state-16 row click lands on a CHILD button
##     record (banked names My^Items/Other^Items/Auto/Pass/TOGGRID/BATZOOMIN).
##     Any claim that a click reaches fn 0x156d4 must cite a POSTER to registry
##     slot 61, not a pixel.
## (4) INSTRUMENT NOTE: xsend click = ButtonPress+ButtonRelease at one
##     coordinate; focus_56aa4 (the [esp+4]==-1 arm) fired ZERO while hit_test
##     fired x2 — do not treat the focus leg as a generic mouse-traffic witness.

## t339 AMENDMENT (binding): THE BatControlWnd INTAKE IS DECODED; "SOMETHING
## POSTS 0x1c01 TO SLOT 61" IS DEAD BY CONSTRUCTION; THE 804..813 PARENT-POST
## ROAD IS STRUCTURALLY BLOCKED. Evidence: docs/re/ships.md S58,
## docs/re/_wip_t339.md S0-S7, scripts/r339_intake_census.py +
## r339_cfg156d4.py + r339_xreach.py (exit 0).
## (1) DO NOT DESIGN ANY FURTHER INTAKE/POSTER HUNT FOR SLOT 61 IN ANY FORM.
##     The whole-image 0x1c01/0x1c02 literal census (18 sites) + windows.txt
##     SENDMESSAGE census (39 values, max 1006) + CFG (gate block
##     {0x15fed,0x16147,0x16181} reachable ONLY via the rebased 0x15ef1 table
##     from the 0x1c01 branch; b9==0 external arrival exits at 0x15b39; b9 2/3
##     writers are inside the gate; 0x320 posters target BatModeWnd's NULL
##     state table) leave NO feed. Residue-(1) leg count = EIGHT, all named.
## (2) LAW (router): generic msg router fn 0x30c9c arms 4/5 (0x30e0e) and 0xc
##     (0x30f46->0x30edc) parent-post the child's SENDMESSAGE WORD ([w+0x45])
##     + SENDPARAM1 to [w+0x63]; arms 7/8 NEVER parent-post. LAW (parser):
##     [child+0x63] := parent slot-id at parse time (0x59012/0x5961d/0x5972b).
##     LAW (pump): fn 0x56b5c 0x56c34 skips delivery to any window with
##     [w+0x63]!=0 when msg>2 — parented children never receive 4/0xc; with
##     BatControlWnd rect 0,0-0,0 the bubbled msg dies in fn 0x336b4's
##     rect-test. Do not re-derive these.
## (3) SAVE-CLASS LAW (directly re-confirmed): the t299-leg-20261105-112859
##     saves 41..49 contain ZERO window-record name strings and ZERO magic
##     0x12345678 — window records are NOT in the save image AT ALL. Any
##     future question about window fields ([w+0x63], slot-ids, class ptrs)
##     is LIVE-LEGS-ONLY (t316 clause (1) extended from the registry table to
##     the records themselves); scripts/r339_rec_census.py exit 1 is the
##     reproduction, do not re-run save scans for records.

## t340 AMENDMENT (2026-11-08) — binding clauses, OQ-016 residue-(4) class
## (1) SHIELD COMPLETION LAW CLOSED (docs/re/income-law.md S-T340, live
##     witness + static cross-check): slot byte+3 (=15) is a ONE-TIME
##     completion marker written by FUN_00038f68 0x3928b word2 |= 0x0f00 at
##     the completion turn ONLY; while pending no slot byte moves at all
##     (sole mover = acc word += stored IND). Do NOT re-census byte+3 as a
##     progress value and do NOT spend another launch on residue-(4).
## (2) INSTRUMENT VERDICT on the t325 zero-fire launches (t325-shield-
##     20261107-005947/-013553): their stalls at turn 1087 were the
##     pre-fix headerless (rgb:-) popup detector, NOT the game — the
##     committed detector clears the exact stall popup (t340 drained 23 OK
##     clicks across 7 drain calls; t325's detector closed 0 on the same class).
##     Any future claim "t325 showed the game blocks turn advance" is VOID.
## (3) MEMDUMPBIN SYNTAX TRAP: `MEMDUMPBIN 0000:<8hex-linear> len file` ->
##     "Invalid memory dump arguments" on this dosbox-x-dbg build (t325's
##     byte-at-arm and t340's code/stack dumps all no-op'd). Use EXEC EV for
##     registers; do not trust a MEMDUMPBIN hdr=OK BEGIN as a file landing
##     without checking the file exists.

## t341 AMENDMENT (2026-11-08) — binding clauses, OQ-016 residue-(6) class
## (1) GRIDSOR I IS OWNER-1 (AI) — MEASURED in all 20 ring saves of
##     work/r1/t340-shieldc-20261108-014705 (owner byte [rec+0x57]==NAME+0x33
##     per the t248 law; named-pool census {0:80,1:11,2:13,255:41}). The t340
##     "item 0 FACTORY auto-reserved on the HUMAN planet" lead is a
##     MISATTRIBUTION, resolved in docs/re/income-law.md S-T341. Do NOT treat
##     Gridsor I as a human planet in any future witness, and do NOT re-open
##     residue-(6): the vendor NEVER auto-queues for the human (local-race
##     gate 0x3eabf..0x3eacd on [p+0x5a]!=0, all 104 owned planets read 0;
##     13/13 empty owner-0 queues persisted 7 turns while AI empires queued).
## (2) QUEUE-WRITER CENSUS CLOSED: the ONLY in-image stores of the planet
##     queue pair (+0x52 WORD cell / +0x54 BYTE item) are fn 0x38840
##     0x38af5..0x38b26 (chain 0x38818->0x3875c->0x38718->0x38753; 17 direct
##     callers incl. UI leg fn 0x3aa0a; selector legs in fn 0x3f130). Resets
##     live at 0x37f8d/0x3a153/0x39290; the 0x3a596..0x3a6b9 block is the
##     record COPY ctor, not a queue op. Reproduction:
##     scripts/r341_queue_writers.py + scripts/r341_writer_paths.py (exit 0).
##     Do not re-census.
## (3) STATIC STAR-TABLE READ TRAP: the data-seg star base 0x13bc5 does NOT
##     resolve in heap-moved scratch saves (owner-mask corroboration returned
##     garbage). Star-record claims need an anchor verified per-save (name
##     law), not the static base.

# t342 AMENDMENTS (binding, 2026-11-08; evidence docs/re/income-law.md
# S-T342 + work/r342_census_pinned.out, tool scripts/r342_queue_census.py):
## (1) RESIDUE-(5) "HUMAN BUILD-ORDER MINUTIAE" IS DISPOSITIONED
##     PLAYER-INPUT CLASS — do NOT re-census the human build queue looking
##     for a missing vendor law. 4891 pending owner-0 rows over the pinned
##     corpus: selector statically excluded ([p+0x5a]==0 4891/4891,
##     netplay==0 60/60, gate 0x3eabf..0x3eacd), complete-then-requeue
##     signature 0/247+8 while the AI control fires 3/3, and every row
##     class = UI order / governor 33-35 / frozen ship (t27 design-cost).
##     A future "anomaly" in these fields MUST first be tested against:
##     flag-bit1->0xffff cell law (t341), orbit-slot cap=cells+10 (t340),
##     governor acc-growth (t45), ship COST=design value (t27).
## (2) COST WORD == 1 IS NOT A COMPLETION BOUNDARY for governor values:
##     acc keeps accruing +IND/turn while +0x54 holds 33/34/35 (measured
##     45->60->75 at IND 15). Do not model a governor queue as a
##     cost-1 build.
