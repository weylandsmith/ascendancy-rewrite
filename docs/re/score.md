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

## S4. Comparator status [open]

ZERO write encodings to DAT_00043510/0x4350c anywhere in 0x200..0x82bb0 for
A0/A2/88/8A/89 /r modrm-05/c7 /0 modrm-05/A3/80-group (byte-exact pattern
scan). With S3 showing consumers read the byte at 0x2c01d, the EVALUATOR must
write it via base+disp addressing (not moffs), plausibly from the same dark
zone as S2 (never analysed). The >1/2-vs-2/3 threshold constant is NOT in the
S2 evidence; OQ-021 stays open. Rewrite default `mine*2 > total`
(rewrite/src/game/campaign.cpp:738) unchanged.
