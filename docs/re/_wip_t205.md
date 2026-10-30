# t205 — WIP: identity of the stride-0x60 block at static 0x13bc4/0x13bc5

Task: docs/STATE.md NEXT ACTION t205 (adjudicate STAR table vs SPECIES/RACE
table vs SCALAR). Trigger triage first: timeline work/r1/playcap/live-timeline
.jsonl size check + tree state below; dosbox process state below.

## S0 — trigger triage
- live-timeline.jsonl mtime 1793294532 / size 5,721,578,066 / tail md5
  9054cc6c… == frozen baselines EXACTLY; dosbox-x not running; tree clean at
  6c144fe. No new sitting -> STATE t205 assignment stands.

## S1 — STATIC: encoding census of the disputed addresses [VERIFIED]
Tools: scripts/r205b_operand_census.py (disp32 + indexed forms, obj0
[0x14bb0,0x82bb0), r201 resume-past-gaps), output work/t205_operand_census.txt
(103 sites). Scripts written this session; capstone via ~/tools/revenv.

1. `0x13b98` (race-count word) — 40+ ABSOLUTE word reads, all `mov/cmp reg,
   word ptr [0x13b98]` (0x165c2, 0x21dc5, 0x24281, 0x27483, 0x29a47, 0x32006,
   0x439fb, 0x43a5c, 0x44bc5, 0x45ea1, ...). ZERO strided/indexed consumers.
2. `0x13bc4` — EIGHT sites, ALL scalar absolute, ZERO strided, ZERO writers in
   obj0: 0x2b848 `cmp byte[0x13bc4],0` / 0x2b932 `...,1` / 0x2ba19 `...,2` (a
   three-way switch in one module), 0x39070 `cmp ...,2`, 0x3f086 `mov dl,...`,
   0x40955 `mov ah,...`, 0x40bdd `cmp ...,2`, 0x43a99 `movsx dx,byte[0x13bc4]`.
   => 0x13bc4 is a SCALAR GLOBAL that merely abuts the table. It is NOT a row
   field and NOT a table base. income-law.md S6-caveat(a) "species table
   DAT_00013bc4 stride 0x60" is REFUTED (see S3).
3. `0x13bc5` as an immediate base appears as `mov ebx, 0x13bc5` at 0x39f94
   (planet-event caller of 0x43a4c) — verbatim this session:
       0x39f85 mov ebx,[esi+0xa] ; 0x39f88 sar ebx,0x10
       0x39f8b lea eax,[ebx*4]   ; 0x39f92 sub eax,ebx      (x3)
       0x39f94 mov ebx,0x13bc5   ; 0x39f99 shl eax,5 (x32)  -> 96*idx
       0x39f9c add ebx,eax       => EDX(arg2) = 0x13bc5 + 96*([esi+0xa]>>16)
       0x39f9e..0x39fb5 the diplo row = 0x12e16 + 494*(edx-derived idx)
       0x39fba call 0x43a4c
   So the 0x13bc5 table IS consumed at stride 96 — the question is only what
   the index space is (stars 0..49 or races 0..3).

## S2 — STATIC: 0x43a4c verbatim + the COMBAT caller [VERIFIED, t205d]
scripts/r205d_windows.py windows. Full handler 0x43a4c..0x43b0d re-read;
t204's transcription holds EXCEPT two operand corrections:

(C1) THIRD ARG (EBX) AT THE COMBAT CALLER IS NOT 0x13bc5-BASED. 0x4b84b..
     0x4b875 verbatim:
         0x4b84b mov eax,[esp+0xe] ; 0x4b852 sar eax,0x10  -> attacker idx
         0x4b84f mov edx,[esi+0x54]; 0x4b855 sar edx,0x10  -> victim idx
         0x4b85c..0x4b86a eax = victim*31*8-... = 494*victim
         0x4b868 mov ebx, ecx      <-- PASS-THROUGH, no 0x13bc5 arithmetic
         0x4b870 add eax,0x12e16   ; 0x4b875 call 0x43a4c
     t204 banked "EBX = 0x13bc5+96*(same row-owner idx)" for BOTH callers; the
     witness supports it only for 0x39fba/0x3a255. [ECX's provenance pending —
     probe P3.]
(C2) THE BITMAP WRITE IS BASE-RELATIVE, NOT A SCALAR. 0x43af0..0x43afa:
         mov eax,[edi+2] ; sar eax,0x10 ; shl dl,cl
         or byte ptr [eax + 0x48304], dl
     i.e. target = 0x48304 + (dword[edi+2]>>16). Measured dword[0x13bc5+
     96k+2] == k<<16 for k=0..49 (T3 below), so for a star record the target is
     0x48304 + star_index — an ARRAY indexed by the arg-2 record's index, not
     the single global byte t204 mirrored. t204's "[0x48304]==0 20/20 saves"
     census therefore sampled the wrong address whenever edi != record 0.

## S3 — LIVE CENSUS (20 playcap saves, pointer law, scripts/r205_table_identity.py)
counts: races u16[0x13b98]==4 (20/20), stars u16[0x16145]==50 (20/20),
T=u32[0x16143]>>16==50, turn 1086 corpus.
- T1 u32[0x13bc5+96k] in star-type set {0..12} for ALL k=0..49 (20/20 saves);
  reading the same dwords at base 0x13bc4 (off-by-one) VALID ONLY k>=51.
- T2 byte[0x13bc4] == 1 in 20/20 saves (constant).
- T3 dword[0x13bc5+96k+2] = {k<<16 : k=0..49} — 50 distinct per save, exactly
  the self-handle convention ((index<<16), cf. [esp+0xe]/[esi+0x54] sar 16).
- T4 rows 0..49 nonzero in 20/20 saves; row 50 has stray content (adjacent
  data), rows 51..59 zero. BOUNDARY LANDS ON 50 == STAR COUNT, not 4.
- Row 0 of the live save holds ASCII star name "Vega" (+0x2c region) and three
  IEEE floats (+0x08/+0x0c/+0x10 coords) — matches ships.md S11 star record.

VERDICT: 0x13bc5 + 0x60*k, k < 50(=[0x16145]) is the RUNTIME STAR RECORD TABLE
(per-star). t200's reading WINS. The per-RACE readings (aicode §3 gov-type
scalar, income-law S6(a) "species table stride 0x60") are the losers: the byte
at 0x13bc4 is scalar (zero strided sites image-wide) and the stride-96 table is
per-star. No third table is needed to explain the callers: the 0x39f85/0x3a2xx
sites pass a STAR record as arg-2 (identity: which star = pending P2).

## S6 — FINAL VERDICT (t205, 2026-10-30)

WINNER: (a) t200. 0x13bc5 + 0x60*k, k < 50 = the RUNTIME STAR RECORD TABLE
(per-star). Evidence chain (all cited this session):
  W1 static base census (r205c fixed, work/t205_bases.txt): 36 absolute-base
     sites on 0x13bc5 across the image; ZERO on 0x13bc4/0x13b98-as-base.
  W2 stride-96 arithmetic verbatim 0x39f85..0x39f9c / 0x4b823..0x4b834:
     record = 0x13bc5 + 96*idx (lea*4/sub/shl5 idiom), always star-derived
     (from a ship's +0x59 star pointer or an object's self-handle).
  W3 live census (r205_table_identity.py, work/t205_identity.txt, 20/20 saves):
     rows 0..49 initialised, type u32[+0] in {0..12} for ALL 50 rows,
     coords f32 +0x08/+0x0c/+0x10, ASCII name "Vega" at row0+0x1c, row 50+
     boundary lands EXACTLY at star count 50 (u16[0x16145]), not race count 4.
  W4 self-handle law MEASURED: dword[0x13bc5+96k+2]>>16 == k for all 50 rows,
     20/20 saves (mismatches only at k>=50 = the zero region).
LOSER corrections banked:
  L1 income-law.md S6-caveat(a) "species table DAT_00013bc4 stride 0x60 holds
     nonzero small bytes at +0x15..+0x17": the bytes it saw ARE star-row
     fields (+0x15..+0x17 vision-mask/type area of the 0x13bc5 rows); no code
     walks 0x13bc4 strided — every 0x13bc4 reference image-wide (8 sites:
     0x2b848/0x2b932/0x2ba19/0x39070/0x3f086/0x40955/0x40bdd/0x43a99) is an
     ABSOLUTE scalar byte read; ZERO writers exist in the image (r205b +
     region [0,0x14bb0) re-scan + imm census): a scenario-init global
     initialised by a rep-stos/copy path OUTSIDE enumerated operands.
  L2 t204 S2/S17.1 "EBX=species record 0x13bc5+0x60*r (r=race)": the combat
     caller passes EBX = STAR record of the ENGAGEMENT location (chain
     0x4b81a mov eax,[esi+0x59] -> 0x4b823..34 table record -> 0x4b868
     mov ebx,ecx -> 0x4b875 call); the 0x39fba caller's [esi+0xa]>>16 index is
     a STAR index too. No per-race table at 0x13bc5 exists.
  L3 t204 mirror "[0x48304] = one global race-bitmap byte": 0x43afa is
     byte[0x48304 + star_index] |= 1<<victim-race — a PER-STAR BYTE ARRAY
     (W4 makes the index = arg-2 record's own row). t204's "value 0 in 20/20"
     census sampled address B+0x82bb0+0x48304 (star 0's cell only) — the
     negative still stands (star 0 clean; the full 0x40-byte window 0x48304..
     +0x3f measured ALL-ZERO 20/20 this session, so the honest negative
     survives unchanged).
  Array neighbourhood (r205b 0x48304 census, 12 sites): 0x24e39 AND 0xfe /
     0x24e84 OR 1 (bit-0 set/clear pair, function 0x24f24 = star-record init
     tail per its 0x25008 mov eax,0x48304;call 0x76e30 fill), 0x24e74 read;
     readers 0x4162f (guarded by ebx==[0x7458e] current-player), 0x42bd2 (in
     diplo state==2 guard block), 0x45e8d, 0x4610b/0x4611c read/write pair,
     0x46213. CONSUMER LAW (what decisions the mark drives) = t206 scope.

## S7 — CODE + PINS LANDED
- campaign.h: attacked_ -> std::vector<unsigned char> (per star, sized
  galaxy_.stars.size() in ctor next to war_/fortify_); attackedMarks()
  OR-reduce (pin surface preserved); attackedAt(star) accessor.
- campaign.cpp combatPhase: mark now written attacked_[nb] (engagement star),
  comment cites 0x4b82c/0x43afa + W4.
- pin diponattack_mark_is_per_star_t205 (fixture default owners s1..s4=1;
  engagement lands star 1; checks attackedAt(1) bit 1<<1, cells 0/2/3/4 clean,
  out-of-range 0). PITFALL HIT: fixture with owners referencing race 2 but a
  single dip file SEGFAULTS buildPhase (aiCount=1, no dip row for owner 2) —
  use the default-owner fixture or supply both dip files.
- 129 tests 0 failed. BLAST RADIUS: seed 2024 Control t1255 FINITE, seed 42
  Extinct t979 FINITE (unchanged — two-party projection: the player's own
  attacks at stars they never own keep the attitude math identical; mark
  placement is not a gameplay input in the rewrite).

## S8 — WHAT STAYS OPEN (honest residues)
- Semantics + value-range of the SCALAR 0x13bc4 ("gov-type" name is now
  unverified too): live 1 in 20/20 captures (one scenario family); comparators
  probe {0,1,2}; a 3-way switch lives at 0x2b848/0x2b932/0x2ba19; gates gated
  on ==2 (0x39070 research +0x50 channel, 0x40bdd design-field 0x49 leg,
  aicode §3 +1/planet gate) NEVER FIRE in captured scenarios. Writer not
  enumerated (operand-less init). Needs other-scenario saves — play-side.
- Consumer law of the per-star mark array (what the readers 0x4162f/0x42bd2/
  0x45e8d/0x4610b/0x46213 decide) + bit-0 set/clear pair semantics -> t206.
- [0x13bc4+1]=0x13bc5 adjacency: "header byte of the star table block" vs
  "abutting global" NOT distinguishable in-corpus (the byte is never written
  via enumerated operands and reads scalar everywhere). Either way the LAW
  consumes it scalar — no rewrite consequence either way.
