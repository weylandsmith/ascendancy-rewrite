# score.md — score screen + end-condition presenter laws (t73)

All image offsets are FILE OFFSETS into work/ascend_restored.bin (base-0
address space, pointer law docs/re/r1-savestate.md). Live-RAM indices use the
corollary form: member_idx = B + 0x82BB0 + X for image-VA X of loaded data,
and code-block anchor B for payload offsets; H = 136 (dosbox-x 2025.02.01).

## S1. Dark zone [verified]

Ghidra auto-analysis (ghp5, 1,144 functions) produced ZERO functions in
0x26b32..0x284bb (functions_full.tsv: predecessor 0x26a9c size 0x96, next
0x284bc). Every prior static-xref route (06s, t52, t72) was structurally
blind there — the banked lesson: raw `objdump -D -b binary -m i386 -M intel`
over work/ascend_restored.bin reads the dark zone directly, no Ghidra needed.

work/attribution.tsv est_func is a BACKWARD-SCAN estimate, not a function
start: all 36 coswnd.cpp est_func values landed mid-function (0/36 appear in
functions_full.tsv). Re-resolved via containing-function lookup -> 12 real
functions, all decompiled (scripts/coswnd_run.sh -> work/coswnd_decomp/).

## S2. Score disproducer law [verified verbatim, raw bytes 0x28054..0x280f5]

    28054: call 0x55240
    28059: mov  esi, ds:0x10ba0            ; DAT tune/player gate
    2805f: cmp  esi, -1        jne 0x28256 ; gate 1
    28068: cmp  esi, [ebp+0x58e] jne 0x28256; gate 2 (multiplayer-off screen)
    28074: mov  eax, ds:0x482fb
    28079: push eax                          ; arg: STARS CONTROLLED %d (pool 0x83b16)
    2807a: push 0xf66                        ; pool-relative imm = 0x83b16-0x82bb0 (OQ-004 law)
    28084: call 0x76c79                      ; sprintf-family
    280be: mov  edx, ds:0x482fb              ; N
    280c4: lea  eax,[edx*4]; 280cb sub eax,edx      ; 3N
    280cd: shl  eax,3; 280d0 add edx,eax            ; N + 24N = 25N
    280d2: mov  ebx, ds:0x16143; 280d8 shl edx,2    ; 100N ; ebx hi-word via:
    280db: sar  ebx,0x10                             ; T = (int16)(DAT_00016143 >> 16)
    280de: mov  eax,edx; 280e0 sar edx,0x1f; 280e3 idiv ebx
    280e5: push eax                                  ; arg: PERCENT CONTROLLED %d (pool 0x83b2a)
    280e6: push 0xf7a                                ; = 0x83b2a-0x82bb0
    280f0: call 0x76c79

LAW: displayed percent = TRUNC(100 * DAT_000482fb / T), T = signed high u16 of
DAT_00016143; the count line prints DAT_000482fb directly. T cross-checks as
the count of stride-0x60 records enumerated by FUN_00028fc0 (work/coswnd_decomp
/28fc0.c: loop bound `DAT_00016143._2_2_`, record base &LAB stride 0x60 — the
star-record stride of the STAR TABLE LAW, r1-savestate.md). So T = total stars;
[inferred] DAT_000482fb = player-controlled star count (producer untraced).

Runtime relocation re-verified [verified, r1deep-20261007-224831 save/41.sav]:
immediate-free anchor window (image 0x280de..0x280e6) hits member 0x1e75b6 =
B+0x280de (B = 0x1bf4d8 vote); there push imm 0xf66 -> 0x242f66 and 0xf7a ->
0x242f7a (P0 + str_off, P0 = B-136 + ... payload-law form); data disp32s
relocate to GUEST-PHYSICAL (e.g. disp(0x482fb) = 0x28a2fb =
B+0x82bb0+0x482fb-0x88) — reading mem[disp] without +H is the known silent
0x88-low trap. Globals in fresh slots via corollary idx (mem[B+0x82bb0+X], same save):
DAT_482fb dword = 1 (campaign start, home system only — consistent with the
inferred owned-star semantics); DAT_4350c dword = 0xFFFFFFFF (rank sentinel
"none yet", matches FUN_0002bfa8's clamp(DAT/10-1) reading 06s measured);
DAT_43510 BYTE = 0x00 (no end condition fired) with adjacent dwords
0x255bc500/0x255fe500 (guest-physical heap ptrs — struct, not lone byte).

## S3. End-condition presenter = eventwnd.cpp [verified]

Jump-table handler cluster 0x2c03a..0x2c0b6 (dispatcher jmp [eax*4+0x173e0]
@0x2c033): five arms push pool-relative names 0x130c/0x1319/0x1333/0x1340
(= payload 0x83ebc/0x83ec9/0x83ee3/0x83ef0 = end-xtnc.txt, end-dest.txt,
end-unit.txt, end-ctrl.txt), each sprintf'd (0x76c79) then ReadFile-validated
(0x7739d) with strcmp(0x775aa) against 0x1371/0x1375; failure arm pushes
0x134d "Couldn't open %s" and assert-file 0x135e '..\eventwnd.cpp'. The
selector byte is read with `mov al,ds:0x43510` @0x2c01d; clamped then jumped
(`and eax,0xff; jmp [eax*4+...]` region 0x2c028..0x2c033). DAT_0004350c is
read at 0x2bfcb (`mov eax,ds:0x4350c; sar eax,18; dec; cmp 4; a`) — the rank
index law 06s found, inside the same function family.

## S5. Selector-writer hunt, t73b/t73c [verified negative, exhaustive-class]

Window 0x434d0..0x43540 (struct @0x4348d: count u16@+0x15=0x43502 measured 9;
u32@0x43504 = score-screen ptr field, WRITTEN at 0x51ac9/0x55c52 (modrm 15/2d)
— UI bookkeeping, reads at ~20 sites 0x3a89e..0x3e370 family; 0x43508 written
at 0x51a8e; DAT_43510 selector byte + DAT_4350c rank read-only at 0x2bf23/
0x2bfba/0x2bfca/0x2c01d/0x2c52b + 0x1d717/0x1d774 region uses 0x43502 count).

ZERO accesses to 0x4350c/0x4350d/0x43510 under: a0/a1/a2/a3 moffs; 88/89/c6/
c7/80/81 modrm mod=00 rm=05 disp32 (incl. SIB-0x25 form); mod=10 disp32 base
form; 39/3b/38/3a cmp; f6/f7; plus RUNTIME-RELOCATED full-16MiB scans of
banked saves (payload law P0+0x82bb0+X): relocated selector addr occurs
EXACTLY 3x (the 3 known readers 0x2bf23/0x2c01d/0x2c52b), struct base
0x4348d relocated occurs EXACTLY 1x (0x1d740 arm-builder mov edx,0x4348d ->
runtime 0x1dcc19 c6 35 (mov byte [edx+d8],imm8 — the END-EVENT QUEUE builder,
sub-record stride 13, type byte [0..8] measured identical across 2 runs)).
mod=10 [reg+0x4348d]: zero. f32 0.5 constant: single DATA site (bitmask ramp
0x7f720..0x7f738, zero refs); 2/3 float: ZERO occurrences image-wide.

CONCLUSION [strong inference]: the end-ctrl threshold is NOT an IEEE constant
and the selector is written via base+disp8 from a register loaded with the
struct base — whose ONLY loader site (0x1d740) builds end-EVENT records, not a
comparator. Remaining possibilities are a second base-loader via computed
address (unfindable statically by this method) or evaluator-side write inside
the dark zone via rep-movs block copy. STATIC ROUTE CLOSED-EXHAUSTIVE for this
method class; closing route = controlled-mutation capture (BLOCKED OQ-021:
inject owners >50% vs 60% at the 0x3a095 table, end-turn, observe DAT_43510
byte 0x2c01d-fires). Score law S2 stands (independent of threshold).

## S4. Comparator status [open] — superseded evidence, kept for the record

ZERO write encodings to DAT_00043510/0x4350c anywhere in 0x200..0x82bb0 for
A0/A2/88/8A/89 /r modrm-05/c7 /0 modrm-05/A3/80-group (byte-exact pattern
scan). With S3 showing consumers read the byte at 0x2c01d, the EVALUATOR must
write it via base+disp addressing (not moffs), plausibly from the same dark
zone as S2 (never analysed). The >1/2-vs-2/3 threshold constant is NOT in the
S2 evidence; OQ-021 stays open. Rewrite default `mine*2 > total`
(rewrite/src/game/campaign.cpp:738) unchanged.

## S6. DAT_482fb behavioural census, t85b [measured, one long campaign]

The user-run playcap (turns 37..1131, 28k trusted observations via
scripts/r1_stream.py trusted order — dedup + stale-instance laws) is the
first long original-game campaign with DAT_482fb banked every slot.
Observations (turn -> value; owned-systems census in parens):
  t367 1->2 (2); t486 2->3; t534 3->5; t560 5->6; t674 6->7; t678 7->9;
  t687 9->11 (11); t888 11->13 (12 any / 7 full); t910 13->11 (14);
  t912 11->22 (14!); t925 22->23; t1128 23->22; never 24+; selector byte
  DAT_43510 == 0 in EVERY trusted observation including the full capture at
  t=1131 with 27 systems_any / 26 systems_full / 27 planets.
Readings:
  * DAT_482fb tracks owned SYSTEMS closely for most of the run (equal to
    systems_any for long stretches), DROPS when systems are lost (t910
    13->11 == Minions capturing systems after the player's war), spikes
    11->22 at t912 with NO systems change (any stayed 14) — the one clear
    counter-example: it is not a pure owned-systems mirror. [unverified what
    t912 was: likely a one-shot score event; no screenshot evidence]
  * DECISIVE-ADJACENT FACT: at t=1131 the player holds 26 fully-owned
    systems (systems_full) with selector byte still 0. If systems_full were
    the comparator variable, >1/2 AND >=2/3 would both have queued an ending
    long before. Combined with the selector-writer absence (S5), the
    consistent picture is: the comparator evaluates DAT_482fb (never
    >= 24 in this run, so >1/2 of 50 never fires) — CONSISTENCY with >1/2
    on DAT_482fb, NOT a closing measurement (what closes: an observation
    where the selector ARMS, plus a screenshot of the end screen; R13).
  * Player testimony pending: did NOT report seeing a Control-victory screen
    by t1131 (capture still live as of t85b). Default >1/2 (campaign.cpp:738)
    stands unchanged.
  * t85b same-day follow-up: while the session sat AT t=1131 (no End Turn
    for hours, 27 systems), DAT_482fb read 0 in the live ring (was 22 at
    t1128..1131 boundaries). A held-turn word that zeroes on long idle is
    NOT a pure owned-systems counter; treat any single DAT_482fb read
    outside a turn-boundary pair as UNTRUSTED for score-law purposes.

## S7. t85c testimony: no score screen exists in the single-player UI

Player cannot find any score screen (game-screen options: Planets,
Ships, Research, Special Ability, Species). Consistent with S2's gates
(0x2805f esi==-1, 0x28068 multiplayer-off check): the disproducer is
gated off. The S2 pushes land on pool strings
"STARS CONTROLLED %d"/"PERCENT CONTROLLED %d" (image 0x83b16/0x83b2a,
neighbouring cosmos.cpp .dbg strings — debug-pool class); the
static.txt #15 string "Your score is %d%%.\nThis gives you the title
of %s" appears NOWHERE in ascend_restored.bin or ascend_payload.bin
(grep: None) [verified] — its presenter screen, if any, is
unlocated. CONSEQUENCE: the score-screen percent as OQ-021 discriminator
is DEAD; replacement closer = continue the live campaign until
boundary-measured DAT_482fb crosses T/2 = 25 (max banked 23) and watch
whether the end-ctrl event (0x2c01d selector arm -> end-ctrl.txt window)
fires. systems_full ALREADY reads 26 without selector arming, which does
NOT contradict the law: DAT_482fb != systems_full (banked 23 vs 26), so
the comparator input remains the DAT, producer untraced.

## S8. t85d: the esi gate DECODED — file-probe debug flags, no multiplayer

The S2 "gate 1 (esi)" and its label "multiplayer-off screen" were EARLY
GUESSES; t85d replaces them with a measured chain:
* DAT_00010ba0 has EXACTLY ONE writer image-wide: 0x21309
  `mov [0x10ba0],-1`, guarded by FUN_00077ece(eax="nougat.lf", edx="r")
  — fopen(path,"r") non-NULL. Pool neighbours (image 0x834e8..):
  'music.txt','..\corn.cpp','r','nougat.lf','r','flash.pop' [verified].
* Sibling flag DAT_00010ba4: one writer 0x2132b, probe edx="flash.pop".
* FUN_00077ece has 10 callers, all file probes: cob.cfg, nougat.lf,
  flash.pop, cosmos.txt, numships.dbg (mode-gated BY nougat: 0x250aa
  cmp DAT_10ba0,-1 / jne skips the open), reswin.txt(w), + 4 dynamic.
* neither nougat.lf nor flash.pop exists in any shipped tree (game/,
  work/r1/game/, recursive search) [verified]; cob.cfg DOES exist
  (lists ascend00..02.cob).
* Reader clusters (attribution.tsv): flag-0 (nougat) 24 sites —
  batcon.cpp 16, batmode.cpp 4, coswnd/batfx/batfxa/cosmos 1 each;
  flag-4 (flash.pop) 27 sites — batcon.cpp 14, race.cpp 6, raceneg.cpp
  4, winmgr.cpp 3.
* The score disproducer pool neighbourhood (0x83b16 "STARS CONTROLLED
  %d", 0x83b2a "PERCENT CONTROLLED %d") continues into
  "numships.dbg", "T%04d: %s flags (%d) show R%d ship, but none
  found.", "T%04d: R%d ship exists at %s, flags (%d) indicate
  otherwise.", "R%d %10s %d\n" — internal consistency-assertion strings.
CONCLUSION [verified chain + inferred reading]: this is NOT a debug
build, it is the SHIPPED release with its developer tooling compiled
in, gated by zero-byte flag files in the game directory ("nougat" =
internal mode name [meaning unverified]). The score disproducer is an
internal readout that needs the flag; the player-facing score screen
(static.txt #15 string) was cut from the image entirely.
MULTIPLAYER CAPABILITY CENSUS [verified, negative]: raw ascend.exe
(0x8f6d3) + restored image contain ZERO of: wsock/winsock/ws2_32/
netbios/ipx/modem/tapi/hotseat/'2 Player'/'multiplayer'/'network'
tokens (case-insensitive regex over full bytes); only DLL refs =
VESA480/VFXSCAN/MCGA (video); game text corpus (.txt x28) has no
multiplayer content. exe is LE (Linear Exec, DOS/4GW family;
dos4gw.exe ships in game/). NOTHING multiplayer exists in the code —
the prior score.md 'gate 2 (multiplayer-off screen)' label is hereby
corrected: gate 2 compares DAT_10ba0 against window field [ebp+0x58e]
(a toggled toggle per 0x2736f-0x27397), not a multiplayer state.

## S8 — t187 passive test continues (2026-10-28 live sitting):
DAT_482fb new highs WITHOUT selector arming: series t1255:14, t1261:12,
t1262..1267:15, t1271..1277:16, t1284:21 (T=50, systems_full=34,
systems_any=36 in the same rows). selector_byte == 0 in ALL 45140
trusted rows (r1_t187_delta.py; still zero-ever-armed across the whole
file scan). systems_full at 68% share with no arming re-confirms §S6's
systems_full-is-NOT-the-variable law at a NEW operating point. The
comparator boundary test (>=25 on DAT_482fb) is now 4 units away — if a
victory screen appears or sel arms, THAT is the closing measurement;
until then row OQ-021 STAYS OPEN (strict-close; consistent-with >1/2
only). Watch.out grep for sel=[1-9] and DAT_482fb>=25 is the cheap
next-iteration check.

## S9 — t212: the displayed count has NO statically-encodable writer [measured]

S2's "[inferred] DAT_000482fb = player-controlled star count (producer
untraced)" and aicode.md P7's claim that the 0x250aa star-owner walk produces
this value are BOTH now measured against:

1. WRONG SLOT [verified, work/t212_w1.txt = disasm 0x250aa..0x2523e]: that
   block writes ONLY `inc word [0x48300]` (0x2519b) and the RMW pair
   0x25217/0x25225. 0x48300 lies OUTSIDE the displayed dword
   [0x482fb..0x482fe] — the "0x48300 is the INC target, alias of 0x482fb"
   note in aicode.md P7 is FALSE (its own caveat, now discharged). The block
   is also gated `cmp dword [0x10ba0],-1` @0x250aa (banked play holds 0 →
   never runs) and calls 0x77ece(file 0x838bf, line 0xd12) + printf-family
   0x7865a (fmt 0x838cf) per iteration: a vendor DEBUG dump with a line
   counter, not the score producer.

2. ZERO WRITERS, three independent instruments (positive controls on each —
   a zero from a linear decoder is worthless without them, t211 law):
   * scripts/r212_ref_census.py (capstone, detail=True, resume-past-gaps),
     region widened to [0x48200,0x48400): 16 memory-operand refs total = the
     two presenter READS `mov eax/edx, ds:0x482fb` (0x28074, 0x280be), the
     word[0x48300] triple above, and the 0x48304 per-star attacked-mark
     family (t205/t206). Address-taking immediates: only 0x25008
     `mov eax,0x48304` (scenario-init memset) + jump-target false positives.
     Controls 0x28074/0x280be/0x2519b/0x25008 all found → RC=0.
   * DECODER-FREE raw byte scan of the whole restored image (0..0x8cc83):
     LE pattern `fb 82 04 00` occurs EXACTLY 4× — 0x2783, 0x27ae (inside the
     relocation-fixup table; the 0x2740..0x2870 window is fixup records: the
     recurring `05 02 <data-seg addr> 07` shape also carries 0x16143 @0x2777,
     0x7458e @0x27c7, 0x13b98 @0x27d0) plus 0x28075 and 0x280c0 = the disp
     fields of the two presenter moffs reads. So no undisplaced/desynced
     disp32 store to the slot exists anywhere in the image.
   * scripts/r212_raw_and_ptr.py + r212_code_identity.py (60.sav, B=0x1bf4d8,
     P0=B+0x82bb0=0x242088): all 17 dwords in guest RAM pointing into
     0x482f0..0x48310 (both candidate relocated forms) are the operand fields
     of the KNOWN instructions above — each found byte-exact as
     instruction-prefix + relocated disp32 (phys form P0+X-0x88; the lin form
     and the unrelocated image form are absent → single patched load). No
     pointer VARIABLE references the score block.
   * scripts/r212_base_disp.py (140,156 decoded insns — matches t211's census
     count exactly; a first draft died at the first gap with 8,961, the t201
     pitfall caught by the count check): enumerated 145 `mov/lea reg,imm32`
     loads with imm in the data-segment neighbourhood [0x47f00,0x48b00) and
     traced each forward until the base register dies, reporting any
     [reg+disp] store (any width) landing in the window, plus any rep-while-
     EDI-at-base. ZERO hits.

3. WHAT THAT LEAVES: the S6/S8 oscillation (DAT_482fb walking 14,15,12,16,21,
   19,22 while systems_any/full stay flat) must come from a store whose
   address is COMPUTED at runtime, which no static census can enumerate:
   scaled-index with a runtime index, a base loaded from memory, a rep
   movsb/stosd span crossing the slot, or a pointer that only ever lives in
   registers. The decisive instrument is a runtime WRITE WATCHPOINT
   (dosbox-x-class) on guest-phys = B+0x82bb0+0x482fb-0x88 — the same
   interactive session OQ-021's comparator-firing test already needs, so the
   two asks should be served together. Row STAYS OPEN (strict-close).

4. SEMANTIC NON-JOIN [measured, scripts/r212_predicate_corr.py, 90 trusted
   saves over work/r1/r1sav-* + r1deep-* + playcap]: V=dword[0x482fb] ∈ {0,1}
   in every slot still on disk (the t85b 12..23 trajectory survives only in
   watch logs), and in EVERY V==1 save byte[star+0x15] is 0 across all 50
   star rows — while the current (new-game) ring holds 4 nonzero +0x15 bytes
   with V==0. So aicode.md P7's "star owner bit [star+0x15]" label is
 [unverified] and does not join to V; t206's cited +0x15 use is a VISION
 byte. A mid-campaign slot with both fields non-degenerate is the witness
 needed to settle it; the corpus holds none.
 [t251 CORRECTION: "the corpus holds none" was CORPUS-BLIND — the scan
 roots missed work/r1/bank-*. bank-t1254 (20 slots, t1254) V=23 with NINE
 +0x15 rows; bank-t251-live1255 (t1255) V=14 with TEN. Witness class
 OBSERVED; non-join holds on real slots (V != ownP 23vs9/14vs9, != occ);
 row 2 +0x15==0x3 co-ownership kills the single-owner-bit reading. See
 docs/re/selfplay.md t251 §3.]

## S10 — t255: V=DAT_482fb behavioural law from the FULL corpus (per-session trust) [measured]

Tools: scripts/r255d_persession.py (classification), r255f_traj.py
(trajectories), r255e_semantics.py (title-class + ship census); outputs
work/r1/t255d_persession.out, t255f_traj.out, t255e_sem.out; working log
docs/re/_wip_t255.md. Corpus: all 7.1 GB live-timeline.jsonl, 65,380 deduped
in-game rows, 25 sessions (mtime-gap split >600 s), Oct-15..Nov-1, turns
37..1335.

1. ZERO MID-TURN CHANGES: across every session, V changed ONLY between turn
   boundaries (39 turn-boundary changes, 0 same-turn changes). The t189b
   candidate "recomputed when a screen opens" is REFUTED — t249's controlled
   Planets-screen open at t1086 did not move V, and no session shows a
   same-turn V move. The player's 14->21 testimony = per-turn evolution
   observed at different turns.

2. V IS NOT SAVE-PERSISTED; FIRST-END-TURN RECOMPUTE IS DETERMINISTIC:
   every session's load turn reads V==0 (9,863 trusted V==0 rows; they carry
   FULL active worlds — 21-41 ships, 9+ systems — so they are NOT title
   snapshots: S00/S02-style post-load slots). The first End-Turn after load
   produces the value: Oct-31 19:51 restart sat at t1086 V=0 for 5.8 h, the
   first End-Turn (01:41) gave V=23; the Nov-1 08:11 restart from the same
   loaded state reproduced V=23 at t1087 EXACTLY. Same world state -> same
   recompute; the save never restores V. Consistent with t212's ZERO static
   writers: the writer is runtime-computed, and it fires on the turn clock,
   not the loader.

3. V != ANY TERRITORY SNAPSHOT (re-confirmed at new operating points): V=23
   held turns 1087..1096 while systems went 26->26.., ships 30->30+; the
   SAME turn t1254 read V=14 in the Oct-26 lineage and V=23 in the Oct-31
   lineage (both any=36) — V depends on lineage history, not the snapshot.
   Lag search over all 39 changes: only 7 hit any/full/planets at any past
   in-session turn (early-game coincidences). No V>=25 row and no selector
   arm anywhere in the corpus — the Control-victory boundary remains
   UNOBSERVED (row stays open, strict-close).

4. DECAY UNDER COMBAT [inferred from measured]: the 23->14 fall happened
   inside the unobserved self-play sprint t1096->t1255 (Nov-1 08:14:19
   V=23 -> 08:17:39 t1255 V=14; scripted End-Turn drive, AI combat running).
   V's recompute inputs include something combat destroys (t85g's t1157
   drop window had ship deaths). Next discriminator: per-owner ship census
   per turn vs V-change turns (ship_raw is banked in every row).

PARSING PITFALLS (t255): watcher APPENDS systems_*/T_known/file_mtime_ns/wall
at line END (head-600 parse sees None); '"file": "' is 9 chars — the
r1_stream.py header scan `i += 8` yields fn='' (dedup survives on mtime, but
file attribution there is silently empty); the GLOBAL stale-echo watermark
WRONGLY drops a campaign deliberately re-loaded at a lower turn — this
corpus needs PER-SESSION trust (r255d).

## S11 — t258: end-turn-recompute discriminator run over the FULL corpus [measured, negative]

Instrument scripts/r258_vdisc.py (KEEPER; single streaming pass, per-session
trust per the t255 law, boundary dump + candidicide + per-session V
trajectories in ONE pass; work/r1/t258_vdisc4.out). Corpus 303,625 lines /
7.43 GB, 53,412 trusted V!=0 rows, 9,997 V==0 rows, 25 sessions, dedup 237,718,
stale 3,437.

1. MID-TURN V CHANGES = 0 (53,412 trusted rows; real measurement with the
   fixed predicate — pass-1's identical 0 was an artifact of a tuple-index bug,
   see _wip_t258 S2). t255 §1 (V moves only at turn boundaries) re-corroborated.
   V-change TURN boundaries = 38; V-stable turn-boundary control population =
   795 (t255's 39 counted one extra boundary on a smaller corpus; the delta is
   corpus/trust-window, not a contradiction — every t255 boundary reproduces).

2. CANDIDICIDE (strict bar: changes at ALL 38 AND zero of the 795 stable
   boundaries): SURVIVORS = NONE.
   - T, rank(65535), selector_byte(0): constant corpus-wide -> dead on leg 1.
   - systems_any / systems_full / planets_mine: change at exactly 1 of 38 V
     boundaries (the S25 t1096->1255 sprint) yet also change at 1-2 V-STABLE
     boundaries -> dead BOTH legs. t85g's "not a territory count" re-proved at
     full-corpus scope.
   - alive_total/player/ai and ALL 12 per-owner order-kind counts: change at
     2-33 of 38 boundaries AND at 3-289 stable boundaries -> dead BOTH legs.
     The best-correlated features (A_k4/A_k5, 33/38) drown in 277-278 stable
     false-positives: order churn is ubiquitous, V moves are rare.
   - Closed-form aggregate fit over all 53,412 rows (same pass, second probe):
     alive_player 4,013/53,412; P_k4+P_k5+A_k4+A_k5 5,688 (10.6%); sum P_k3..5
     985; 2*(P_k4+P_k5) 154; alive_ai 3; sum_all_k 1 — all first-miss at t37
     (V=1 with zero ships: the fleet hadn't launched yet). No formula of the
     banked-feature space reproduces V; matches are coincidence at V's plateau
     values.

3. DETERMINISM, 3rd independent witness: the t1169->t1170->t1171 replay in two
   separate sessions (S14, S15) walks V 14->12->14 EXACTLY (t255 had only the
   V=23@t1087 pair). The recompute is a function of loaded world + turn clock,
   not of wall time or session identity.

4. V==0 IS A LOAD-CLASS, NOT turn==0: 33 distinct (session,turn) pairs carry
   V==0 at turns 692..1254 (e.g. S22/23/25 t1086, S19 t1254). First-post-load
   V table (22 load points) shows V NOT determined by the snapshot: t1087 reads
   V=23 with systems_full=25 (S22,S23) and V=23 with full=24 (S25); t1167 reads
   14 with full=27 (S14) vs full=29 (S15). V co-varies weakly with systems_full
   but is neither equal nor a function of it (lineage dependence, t255 §3).

5. SHAPE CLUES for the eventual formula (banked, [inferred] labels): steps are
   small (+-1/2) during growth but include DOUBLING (S07 t911->912 V 11->22)
   and HALVING (S13 t1140->1141 V 22->11) — a count of *items* changing by
   factor 2 in one turn suggests V counts a derived per-star quantity whose
   per-star values cross an integer threshold en masse (e.g. TRUNC/floor of a
   per-star score), OR the S2 disproducer reads a value recomputed from a
   structure that is itself rebuilt (halving = rebuild with a different unit).
   Non-monotone +-1/2 oscillations at plateaus (S17 t1246..1253: 14,15,13,15,14)
   mean at least one input oscillates per turn while territory is dead-flat.

6. CLOSURE BAR UNMET, row stays OPEN: zero rows with V>=25 in the entire corpus
   (max 23/50 = 46%), selector_byte never armed — the Control boundary remains
   UNOBSERVED, and the producer's write-site needs the runtime watchpoint
   (t212 conclusion unchanged; this iteration adds no static handle). The
   residual now REQUIRES a NEW interactive capture (watchpoint + drive past
   V>=25): recorded as a USER ASK in docs/BLOCKED.md. No rewrite change, no
   pin (campaign.cpp:2093 default >1/2 stays — CONSISTENT with every banked
   frame: V never crossed 25 and no victory screen ever appeared).

INSTRUMENT PITFALLS (t258, full detail _wip_t258 S2/S4): (a) prev-tuple index
drift silently merged mid-turn pairs into the turn-boundary population; (b) a
fast JSON slice that starts AFTER the opening '{' must re-add it —
json.loads('"0": [...]}') dies "Extra data: line 1 column 4"; (c) an
except-swallow + isinstance-guard turns a parse bug into a SILENT None — the
none_census print added mid-task is what caught it; (d) verifier agreement
against a reference parser is VACUOUS when both return None — assert non-degenerate
value content, not fast==reference equality.

## S12 — t261: driven-corpus +0x15 star-set growth table (OQ-021 S6/P7 witness material) [measured]

Drive session 2026-11-01 (production :9, base t1086 resumed from RESUME.GAM).
Banks bank-t261-final-1096 + bank-t261-t1255 decoded per-slot (scripts/
r261_harvest.py, KEEPER; star k = B+OFF+0x13BC5 + k*0x30 + 0x15 nonzero):
  t=1087 stars15=[4,24,36,44]
  t=1090 stars15=[4,24,32,36,44]     (32 joins; V=23 constant)
  t=1111 stars15=[4,14,24,32,36,44]  (14 joins)
  t=1255 stars15=[4,12,24,32,38,42,44] (t1255 campaign snapshot; V=14)
Same-turn slots are byte-identical in this field across ring churn (no
intra-turn flicker). V=23 held 1086->1111 while stars15 grew by 2 — the join
count does NOT track V within a run (S6 non-join re-corroborated on a NEW
session, first time from a DRIVEN corpus). Strict-close: no threshold event
observed; OQ-021 STAYS OPEN. Tool pitfalls banked: window_rows off-by-one in
r1_t251_mine (quote char in wall slice — silently ZERO rows since t251, fixed;
every earlier "newsession" pass was vacuous); wall=HH:MM:SS collides across
days -> gate on file_mtime_ns epoch, not wall alone.

## S13 — t262: CENSUS/INVENTORY TRIGGER discriminator on the DRIVEN corpus [measured]

Instruments scripts/r262_census_disc.py (KEEPER; segment-aware 2x2 contingency
+ functionality join; whole-file single pass, rows never buffered) and
scripts/r262_legA.py (KEEPER; leg-A deep field check). Corpus: every turn-
advancing session Oct-15..Nov-1 (the watcher stream; sessions split at mtime
gap >600 s, PLUS segment splits at reload class (V==0 at turn <= watermark)
and foreign-lineage class (turn drops >2 below watermark while V!=0 — the
t261 softlock oscillation and re-drive land in separate segments; t255
per-session-trust law generalized to per-SEGMENT). Dedup (file,
file_mtime_ns). 808 turn boundaries (Oct corpus run) + 207 (Oct-29+ run).

DEFINITIONS. Inventory signature = piecewise-constant fleet facts only:
live-ship count, per-owner count multiset, design-id multiset, gizmo-ring type
multiset (t256c decode law: owner u32@0x54>>16, design u32@0x10, ring byte
@0xab+7i, count u32@0x15a clamp 64). Order fields (kind/act/targets) are NOT
in the signature — in a drive they churn at ~half of all boundaries (539/808)
and t258 already killed them.

1. THE CENSUS IS NOT THE TRIGGER — BOTH LEGS DIE:
   leg A (V changed -> inventory changed): FAILS, 27 of 37 V-change boundaries
     have BYTE-IDENTICAL inventory (V&inv=10). Includes the t258 shape-clue
     boundaries the doubling/halving note pointed at: t911->912 V 11->22 and
     t1140->1141 V 22->11 both fire with inventory static — the fleet did not
     double or halve; V did. The S11.5 "items changing by factor 2" inference
     is REFUTED for the ship-inventory hypothesis.
   leg B (inventory changed -> V changed): FAILS, 121 inventory-change
     boundaries with V static (ship builds/losses happen and V doesn't move).
   (The two "V&inv" load-class boundaries t1111->1255 / t1096->1255 are the
   campaign-exit jump, not end-turns: turn-JUMP >1 flagged in output.)

2. FUNCTIONALITY KILL (strongest result): 18 of 149 inventory signatures
   carry MULTIPLE V values within one continuous segment. Worst case, driven
   session Oct-28 23:32->23:47 (turns 1255..1335, one lineage, monotone): ONE
   signature (n_live=37, owners {0:23,1:7,2:7}) carried V in {12,15,16,19,21,
   21,22} — trajectory 14,15,12,15,16,21,19,22,21 — while the fleet inventory
   was byte-identical throughout. V is therefore NOT a function of the ship
   census at fixed turn within a lineage; whatever feeds DAT_482fb re-evaluates
   every End-Turn from state the watcher does not capture (S11.5's "input that
   oscillates per turn" — now localized to NON-fleet state: candidates by
   elimination are per-star garrison/governor state, economy stockpiles, or
   research/abilities, none of which is in the row schema).

3. leg-A deep check (r262_legA.py): on all 27 static-inventory V-change
   boundaries, ship TARGET words changed 27/27 and kind-multiset 24/27 — so
   ships were moving, but movement is ubiquitous (539/808 boundaries churn
   with V static), so it is correlation-not-trigger exactly as t258 concluded
   for order features. ZERO boundaries where nothing banked moved yet V moved
   — but "targets moved" carries no information (see churn rate), so this is
   NOT a reprieve for the fleet hypothesis.

4. T261 RE-DRIVE CORPUS (1087->1236, 149 boundaries, V=23 constant, inventory
   sig static, order-churn 23): a fully STATIC-V stretch — the control
   population for future watchpoint work. The t262 pre-flight drive completed
   TARGET REACHED at 1236 (bank-t261-final-1236).

STRICT-CLOSE: OQ-021 STAYS OPEN. This iteration closes a HYPOTHESIS (census
trigger) by measurement, not the ledger row — the threshold (V>=25 / selector
arm) remains unobserved corpus-wide (max V=23; the driven Oct-28 late-run got
to 22 at t1301 then decayed 21 by t1335 — distance-to-half banked: 22/50).
The residue statement is now sharper: writer = per-End-Turn recompute over
NON-fleet state (S10.2 + S13.2), next instrument = dosbox-x write watchpoint
on 0x482fb during a drive that crosses V>=25 (USER ASK stays in BLOCKED.md).

## S14 — t269: VICTORY-THRESHOLD MINING over the full corpus [measured, negative + T census]

Instrument scripts/r269_vthreshold.py (KEEPER; single streaming pass, header-
scalar slices, per-SEGMENT trust law t262; anomaly locator scripts/r269_anom.py).
Corpus 7.69 GB / 314,173 lines / dedup 243,135 -> 71,038 trusted rows / 14,348
segments. Outputs work/r1/t269_vthreshold{,_rank}.out.

1. NO THRESHOLD EVENT, sharper than ever: zero rows V>=25; selector_byte
   census = {0: 71038} (never armed); AND rank census = {65535: 71045, 0: 2}
   — the rank slot DAT_0004350c left its sentinel in exactly TWO rows, both
   turn-0 title/new-game frames (see 3). The score evaluator
   (FUN_0002bfa8 clamp(DAT/10-1) family) NEVER ran during captured play.
   Three independent end-state variables (V, selector, rank) all sit in
   never-fired posture across 100% of trusted frames.
2. T CENSUS (first ever banked): T=u32[0x16143]>>16 = 50 in 71,023 rows;
   25 in 12; 0 in 2; 100 in 1. r269_anom.py located every anomaly: ALL are
   turn-0 in_game=False frames (title/new-game-setup, starfield mid-build —
   T=25 rows carry any=11/pm=11 at turn 0 = partially-populated setup state;
   T=0 rows are all-zero). CONCLUSION: every IN-GAME frame ever captured ran
   the T=50 galaxy; no small-galaxy campaign lineage exists in the corpus, so
   the threshold denominator was never variable. Half-threshold = V>=26 (or
   >=25 per "over half" reading) for every captured campaign.
3. DISTANCE-TO-HALF statement (the honest product, per task): corpus max
   percent-controlled = TRUNC(100*23/50) = 46.0% (V=23), observed at t925 and
   re-observed t958/t1015/t1016/t1087; strict majority needs 3 more controlled
   stars. systems_any reached 36 (> half of 50) WHILE V stayed <=23 and sel
   stayed 0 — the threshold-neighbourhood re-confirmation of the SEMANTIC
   NON-JOIN (S6/S9): a player owning planets in 36 of 50 systems never armed
   the end-ctrl selector, so V's producer gates on something narrower than
   territory ownership.
4. V-CHANGE BOUNDARY TABLE: 66 boundaries (vs t258's 38 — the per-segment
   trust law catches reload-class boundaries the global watermark dropped);
   shape clues 11->22 @t911->912 and 22->11 @t1140->1141 reproduced
   independently. Full table in the out file (turn-pair, V a->b, any/full/pm).
5. end-ctrl.txt VERBATIM re-read (extracted/ascend00/end-ctrl.txt): header
   comment lines 1-2 "Player controls over / half the galaxy."; enddesc
   "spans over two-thirds of the galaxy"; congrat "more than two-thirds of the
   stars ... the other species may continue to bicker over the stars that
   remain". The prose says two-thirds TWICE against the comment's half; the
   congrat text describes surviving species holding stars, consistent with
   either comparator. No numeric constant in the file — the contradiction
   stays code-only, and the code comparator remains unobserved.

STRICT-CLOSE: OQ-021 STAYS OPEN — a trajectory is not a threshold (task law).
Closure still requires the ENDGAME-window witness (selector arm + end-ctrl
screen), i.e. the interactive watchpoint session (USER ASK in BLOCKED.md).
Rewrite default >1/2 (campaign.cpp) remains CONSISTENT with every banked frame.
