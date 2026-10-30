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
