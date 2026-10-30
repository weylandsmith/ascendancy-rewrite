# t212 WIP — OQ-021 DISPLAYED-COUNT WRITE SITE (DAT_000482fb)

## S0. Trigger triage (before any static work)
work/r1/playcap/live-timeline.jsonl: size 5,721,578,066 / mtime 1793294532
(2026-10-29 13:22:12.10) / tail-64KiB md5 9054cc6c66802e6f80431d4ffa1416ee
== the frozen t211 baselines EXACTLY. `pgrep -a dosbox` -> rc=1 (down). Tree
clean at HEAD 6bca4ce. => NO new sitting; STATE t212 stands.

## S1. What is already known (cited, not re-derived)
- Presenter law [verified, score.md S2]: 0x28074 `mov eax, ds:0x482fb` prints
  "STARS CONTROLLED %d"; 0x280be same dword -> TRUNC(100*N/T), T=(int16)
  (DAT_00016143>>16) == total stars.
- PRODUCER LEAD [verified for 0x48300 only, aicode.md P7]: turn-advance block
  0x250aa..0x2523e (gated DAT_00010ba0==-1) walks the stride-0x60 star table
  at 0x13bc5, tests byte [star+0x15] bit<<race, and `inc DAT_00048300` per
  owned star at 0x251a2. The doc explicitly flags: "the 0x482fb alias relation
  NOT re-measured this pass".
- GEOMETRY FACT: 0x48300 - 0x482fb = 5, and 0x48304 is the start of the
  PER-STAR attacked-mark byte array (t205/t206). So 0x482fb (dword read at
  0x28074 spans 0x482fb..0x482fe), 0x482ff/0x48300/0x48304 are four distinct
  neighbouring slots in the obj0 data segment — an "alias" is NOT automatic.
- OSCILLATION [measured t188b, score.md S8]: dword[0x482fb] moves 12..22
  across the t188b frames while systems_any=36 / systems_full=34 stay FLAT in
  the same frames => the numerator is not a plain owned-systems count.
- Comparator writes: ZERO direct encodings to 0x43510/0x4350c (t73, 8-form
  scan) — comparator ABSENT from the image (t76 exhaustive). Default >1/2
  stands. OQ-021 closure needs a play witness (watch-only); THIS iteration is
  the write-site residue only.

## S2. Plan (~15 probes)
A. Disassemble 0x250aa..0x2523e verbatim: what is written/stored where, and
   what per-star predicate gates the increment. (r205d_windows pattern,
   capstone in ~/tools/revenv.)
B. obj0 writer census for the region [0x482f0,0x48310): disp32 forms AND
   reg+disp/indexed forms, resume-past-gaps (t201 law), with a POSITIVE
   CONTROL (must reproduce the known 0x251a2 writer + the 0x48304 mark writer
   0x43afa) before trusting any zero.
C. Runtime-slot census over the 20-sav corpus: dword[0x482fb], dword[0x48300],
   and the per-star predicate inputs, per save; correlate which predicate
   reproduces the observed value.
D. Land: name the loop + predicate, or bank the narrowed chain as honest
   residue. Update OQ-021 STATUS + score.md.

## S3. MEASURED (probes: r205d window 0x250aa:0x2523e = work/t212_w1.txt;
##     scripts/r212_ref_census.py RC=0 controls OK = work/t212_census_a.txt)
(1) THE P7 LEAD IS THE WRONG SLOT [verified]. The 0x250aa..0x2523e block
    writes ONLY `inc word [0x48300]` (0x2519b) and the read-modify-write pair
    0x25217/0x25225. 0x48300 is NOT inside the displayed dword
    [0x482fb..0x482fe]. aicode.md's "alias relation NOT re-measured" caveat
    was load-bearing: NO alias. The block is moreover gated
    [0x10ba0]==-1 (0x250aa; banked saves hold 0 == the whole block SKIPPED in
    normal play) and calls the printf-family 0x7865a with format 0x838cf /
    file string 0x838bf + call 0x77ece(0x838bf, line 0xd12) per iteration —
    a DEBUG-DUMP-with-counter shape, not the score producer. (Star loop over
    u16[0x16145], inner race loop u16[0x13b98], owner test
    byte[star+0x15] bit<<race — the P7 walk IS there, but its counter is the
    debug counter.)
(2) STATIC WRITER CENSUS = ZERO [measured]. Full disp32/imm census over obj0
    [0x14bb0,0x82bb0), region [0x482f0,0x48310): 16 memory-operand hits =
      R dword[0x482fb] @0x28074,0x280be (presenter ONLY);
      word[0x48300] triple (the debug block above);
      the 0x48304 per-star attacked-mark family (t205/t206 — 11 sites, incl
      base+disp forms [edx/ebx/eax+0x48304]).
    Address-taking immediates: ONLY 0x25008 `mov eax,0x48304` (scenario-init
    memset) + 3 jump-target false positives. => NO disp32 write anywhere in
    obj0 touches 0x482fb..0x482fe. Resume-past-gaps was active; positive
    CONTROLS (0x28074 R, 0x280be R, 0x2519b W, 0x25008 imm) all found, so the
    zero is loadable for the forms the census covers.
(3) OBSERVED VALUES ARE BYTE-RANGED [re-read of score.md S6/S8 + OQ-021 row]:
    every banked DAT_482fb reading is < 256 (max 23; oscillation 12..22) =>
    bytes [0x482fc..0x482fe] are zero in all observed frames — the live value
    occupies byte 0x482fb. Blind spots that remain for the writer:
    (a) code OUTSIDE [0x14bb0,0x82bb0) (extending scan now);
    (b) a writer via a POINTER into the data segment (struct field holding
        addr 0x482fb, base+disp8 access — undetectable by disp-window census;
        t191 law says hunt RAM for such pointers);
    (c) rep-stos/copy init (t205 pattern) — cannot produce values 12..22,
        excluded as producer of the oscillation.

## S4. MEASURED (scripts/r212_raw_and_ptr.py RC=0; scripts/r212_code_identity.py
##     RC=0 on 60.sav B=0x1bf4d8; r212_ref_census widened to 0x48200..0x48400)
(1) DECODER-INDEPENDENT RAW SCAN (whole image 0..0x8cc83, no capstone): the
    LE pattern fb 82 04 00 occurs EXACTLY 4x: 0x2783, 0x27ae (RELOCATION-TABLE
    region — bytes there decode as fixup-record garbage; the 0x2740..0x2870
    window is a fixup table, not code: pattern 05 02 <4-byte data-seg addr>
    07 recurs incl 0x16143 at 0x2777, 0x7458e at 0x27c7, 0x13b98 at 0x27d0)
    + 0x28075, 0x280c0 = the two presenter moffs32 disp fields (mov eax,
    ds:0x482fb — opcode a1, disp at X+1). NO HIDDEN disp32 anywhere: the
    capstone zero is CONFIRMED byte-exact, not a desync artifact.
(2) LIVE-RAM POINTER CENSUS (60.sav, both candidate forms phys P0+X-0x88 and
    lin P0+X, targets 0x482f0..0x48310): 17 dwords total — 2 == the slot
    physical (0x28a2fb) at members 0x1e754d/0x1e7598, 3 == word[0x48300]
    sites, 12 == the 0x48304 mark family. r212_code_identity.py PROVES every
    one is the RELOCATED disp32 FIELD of its known instruction (prefix +
    relocated dword found byte-exact; unrelocated image forms absent = single
    patched load). => NO pointer variable anywhere in guest RAM points at the
    score block; base+disp8 writers need a DIFFERENT base (near-slot base not
    yet excluded: window widened next).
(3) WIDER disp32 census 0x48200..0x48400 (controls OK): still ZERO writes to
    0x482fb..0x482fe. New: 4 address-taking immediates `mov reg, 0x48368`
    (0x166d9/0x22674/0x27fd9/0x28e17) — NEIGHBOUR BASE CANDIDATE
    (0x48368-0x482fb = 0x6d, inside disp8 range) for a [reg+disp] writer.
(4) THE CURRENT RING IS THE NEW-GAME RING (t212 slot census, 20/20 saves
    t=1086 wall-clock-stale row: dword[482fb]=0, owned_stars=4, dword[48300]
    =0, dword[48304]=0) — the t187 sitting overwrote campaign state (banked
    t188 note). Oscillation witnesses (12..22) live only in the watch logs +
    OLDER banked run dirs (r1sav-*/r1deep-* incl the t85b long campaign).
    Writer-chain correlation needs those campaign slots, not this ring.

## S5. MEASURED — the writer is absent from every statically-encodable form
scripts/r212_base_disp.py RC=0 (140,156 decoded insns — resume-past-gaps
count matches t211's census EXACTLY; first draft of this tool died at the
first gap and reported 8,961 — t201 pitfall re-hit, caught by the count).
  * 145 base-load sites (`mov/lea reg, imm32` with imm in the data-segment
    neighbourhood [0x47f00,0x48b00)) enumerated; forward-traced each until the
    base register is modified (WALK<=400): ZERO memory writes into
    [0x482f0,0x48300), ZERO [reg+disp] writes landing 0x48300..0x48380, and
    ZERO rep-while-EDI-at-base sites among them.
  * Combined with S3(2)/S4(1)/(2): over the WHOLE restored image there is NO
    disp32 encoding targeting any byte of the displayed dword except the two
    presenter READS (raw byte scan fb 82 04 00 = 4 hits, 2 fixup-table +
    2 presenter disp fields at 0x28075/0x280c0); NO aligned RAM dword points
    into 0x482f0..0x48310 in 60.sav except relocated operand fields of known
    instructions (all byte-exact-identified, r212_code_identity RC=0); NO
    immediate-loaded base feeds a [reg+disp] store into the window.
  * CONCLUSION [verified within these shapes]: the 12..22 oscillation is
    produced by a store whose ADDRESS IS COMPUTED at runtime — candidates
    surviving: (i) scaled-index form [reg+index*scale+disp] with runtime
    index; (ii) a base loaded from MEMORY (e.g. 0x27758 `mov ebp,[0x484ec]`
    class) plus disp; (iii) rep movsb/stosd span-crossing (t205's
    enumeration-blind class); (iv) transient pointer held only in registers
    (invisible to any snapshot). None is enumerable statically; the decisive
    instrument is a RUNTIME WRITE-WATCHPOINT (dosbox-x memwatch class) — which
    is exactly the interactive-session class OQ-021 already needs for the
    comparator firing test. The static route to the write-site is EXHAUSTED;
    this is an honest negative, NOT a closure.

## S6. SEMANTIC side-observation (banked, unadjudicated)
scripts/r212_predicate_corr.py RC=0 over r1sav-*/r1deep-*/playcap (90 trusted
saves): V in {0,1} everywhere (the corpus holds no mid-campaign SLOTS any
more — the t85b 12..23 trajectory exists only in watch logs). In every save
with V==1, byte[star+0x15]==0 on ALL 50 star rows (occupied=0) — so V==1 at
t=1..9 does NOT join to the +0x15 "owner bit" reading aicode.md P7 gives that
byte (t206's cited use of +0x15 is a VISION byte). Do NOT re-derive P7's
owner-bit label as measured: it is [unverified], and the join FAILURE at the
one scored field available (V) argues the label is wrong or slot-shifted in
those runs. Current-ring counter-witness: 4 nonzero +0x15 bytes with V==0.
No closure either way (a mid-game slot with both fields non-degenerate is the
required witness; ring holds none).

## S7. REWRITE IMPACT
None. OQ-021's rewrite default (>1/2 on the displayed count analog,
campaign.cpp:738) is untouched; no semantic claim was added or removed. The
iteration's product is the writer-site negative + the P7 slot correction.



