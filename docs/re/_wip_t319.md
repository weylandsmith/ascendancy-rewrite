# t319 WIP — pump caller/gate separation run

## S0. Assignment (docs/STATE.md NEXT ACTION t319; REFUTED-ROUTES t318 amendment (3) is the binding shape spec)
Separate the three surviving explanations for "fn 0x56b5c's poster road never
delivers a msg to FLEETWND" in ONE scratch capture:
  (A) caller-never: the poster call-site 0x54ac5 is never reached on click traffic;
  (B) poster-gate-never-equal: the block at 0x54a3f/0x54a88 is reached but the
      equalities fail so msg 4 (not 0xc) — or nothing — is posted;
  (C) pump-entry-never: fn 0x56b5c is never called at all in this build while
      armed (then s2_56cda's traffic arrives via fn 0x56ca4 only).
Legset (5): pump_entry_56b5c=0x56B5C, p54a47=0x54A47, p54a88=0x54A88,
s2_56c74, s2_56cda. fn51cc4_entry + writer pair DROPPED (zero twice, strictly
downstream). Choreography: proven --shipclick 4 VERBATIM + standard tail
(same command shape as run t299-leg-20261106-021602 rc=0).

## S1. Leg bytes — payload-verified THIS session vs work/ascend_payload.bin (identity mapping, size 0x8cc83)
- 0x56B5C: 56 57 55 83 ec 10 89 c7 66 89 54 24 08  (fn entry; at stop eax=window
  rec candidate (mov eax,esi not yet executed -> esi check too), edx=msg id,
  ret0=[esp] = which of the NINE E8 callers fired, esp_p8 = 4th push arg.)
- 0x54A47: 8b 1d f0 84 04 00  (first instruction of the ds:0x484a4-EQUAL road;
  reached only past cmp edi,ds:0x484a4 @0x54a3f jne 0x54a88.)
- 0x54A88: 3b be a4 4d 02 00  (the cmp edi,[esi+0x24da4]; at stop edi=msg id
  candidate, esi=core obj; equal AND [esi+0x489e]==0 -> msg 0xc poster 0x54aa9,
  else msg 4 poster 0x54ab2 — both land on call 0x56b5c @0x54ac5.)
Static control-flow facts re-read this session from work/t91_code_disasm.txt
(lines 77080-77250, verbatim):
- The ONLY in-function path into 0x54a3f is `je 0x54a3f` @0x549e7 (line 77184),
  taken iff [esi+0x24da8]==0xffffffff (0x549de-0x549e7).
- 0x549e9: cmp [esi+0x489e],0; jne 0x54a26 (0x489e!=0 road writes
  [esi+0x489e]=0 + [esi+0x48a2]=-1 and jumps 0x54aca — NO pump call).
- 0x549f2-0x54a21: fn 0x4fb30(0x78638,0) + fn 0x5a1e4 + fn 0x57020 then jmp
  0x54aca — also NO pump call.
- Equal road @0x54a47: fn 0x5be9b(ds:0x4850c, ds:0x484ec, ds:0x484f0) ->
  ds:0xa1ffc; pump ONLY if [[esi+0x21d92]+0x39]!=0 (je 0x54aca @0x54a72);
  else msg-0x3f1 dispatch call [edi+8] @0x54a83 (leg s2_54a83 exists).
- 0x54a88 road: msg 0xc iff edi==[esi+0x24da4] AND [esi+0x489e]==0.
  NOTE: on the path arriving via 0x549e7 (489e==0 branch fell through at
  0x549f0), [esi+0x489e] IS 0 — so the +0x489e term cannot block THIS road;
  the discriminating datum is edi vs [core+0x24da4].
- t318 measured gate_7e89e ([obj+0x489e]) — re-read from this run's oracles too.
Nine E8 callers of fn 0x56b5c (t318 law): 0x53fa3 d / 0x54976 3 / 0x54ac5 4|0xc /
0x54b36 5 / 0x5531e f / 0x5548c e / 0x55f82 d / 0x56f0f 2 / 0x57003 1.
ret0 at a pump_entry stop - 5 = the call site; ret0-1 semantics per bank_stop
(ret0 = [esp] = return addr; ret0_file_off = file offset of the return addr;
call site = ret0_file_off-5 for an E8 5-byte call — r319_analyze prints both).

## S1.5 Full poster decision tree inside fn 0x54650 (static, t91_code_disasm 77040-77250, verbatim this session)
Entry gate 0x54823: edi=ds:0x484a0; jne 0x5497b skips the 0x54832-0x54976
block (which holds caller 0x54976 msg 3). Straight (484a0==-1) runs the fn
0x59bf4/0x56d1c/0x5526c sub-block, then 0x54934: cmp -1,ds:0x484a4 ... fn
0x54d18; eax==-1 -> 0x5495b POSTS msg 3 via call 0x56b5c @0x54976.
Shared tail 0x5497b: ebx=ds:0x484dc; **cmp ebx,-1; jne 0x54aca** — reaching
0x549e7 (the je into the poster block 0x54a3f) REQUIRES ds:0x484dc==-1;
0x549d1 requires ds:0x484d0!=0; 0x549de requires [obj+0x24da8]==-1 -> je 0x54a3f.
So the poster-block conjunction at fire time:
  ds:0x484dc==-1 AND ds:0x484d0!=0 AND [obj+0x24da8]==-1.
Inside 0x54a3f edi = [obj+0x24da8] (set at 0x549de) == -1 always.
  - equal road (edi==ds:0x484a4, needs 484a4==-1 too): fn 0x5be9b query; pump
    ONLY if [[obj+0x21d92]+0x39]!=0 else msg-0x3f1 dispatch @0x54a83.
  - unequal road 0x54a88: cmp -1,[obj+0x24da4] -> msg 0xc requires
    [obj+0x24da4]==-1 (AND [obj+0x489e]==0); ELSE msg 4 @0x54ab2.
IDLE VALUES (48.sav via scripts/r319_gate_read.py, NEW script, law = oracle
form B+SL.OFF+X; cross-checks t318 oracle gate_484ec=0x1ff EXACT):
  ds484a4=0 ds484d0=0 ds484dc=0 m24da8=0xffffffff m24da4=0 m489e=0 m48a6=0
  m21d92=0xfe9d88 -> rec 'WMGRDEBUG' (magic 0x12345678, ptr 0x28a4f8-linear-law)
  mode4226_hi=0x11 (48.sav; t318 oracle per-phase read 0x1/0x11/0x12 churns)
At IDLE the conjunction FAILS (484dc=0) -> the poster region is skipped every
idle main-loop pass — consistent with s2_56c74=0 whole-log while s2_56cda
(periodic 0x3b via fn 0x56ca4) fires 26x. The click-record writers of
ds:0x484a0/484dc live in fn 0x2a6xx-0x2a9xx family (2a724/2a737/2a814/2a850/
2a92d write 484a0; 2a7bb/2a7c4/2a802/2a844/2a8ba write 484dc) — the t317
gutter-click path decoded to fn 0x33058 bookkeeping, NOT this family.
LIVE QUESTION (t319 legs answer it): does ANY click traffic set 484dc=-1 +
484d0!=0 so the block runs, and if so which pump road fires. p54a47/p54a88
bank edi at the gates; pump_entry banks ret0 -> caller.

## S2. Harness wiring
- LEGS registry in scripts/r299_leg_session.py: +pump_entry_56b5c, +p54a47,
  +p54a88 (bytes above; no custom bank code needed — bank_stop already banks
  regs incl. esi/edi/edx, ret0 + call-site, magic-rec names for esi/eax/ebp).
- scripts/r319_relaunch.sh NEW (r318 pattern: attempt-1 short-circuit law,
  rc=2 never retry); scripts/r319_analyze.py NEW.

## S4. RESULT (run complete, SESSION END rc=0 03:35:15, census-measured 9 windows, 108 hits)
pty-whole-log-census: pump_entry_56b5c=1 | p54a47=0 | p54a88=1 | s2_56c74=1 |
s2_56cda=106. Banked: s2_56cda 107 (102x msg 0x3b COSMOSWnd, 4x msg 8
STATSHIPLST gutter clicks t317-verbatim, 1x msg 0x193 STATSHIPLST self-send)
+ pump_entry 1. 0x1c01/0x1c02 literal absent every banked stop.

### S4.1 THE POSTER ROAD FIRED — CALL SITE 0x54ac5, MSG 4 (first live witness)
Banked EV stop 03:19:09 tag=post-rearm (6 s after the shipclick_620x453 click
inside its armed window): leg=pump_entry_56b5c eip=0x215fac edx=0x4 (MSG 4)
esi=eax=0x2bc35c (core obj) edi=0xffffffff ret0=0x213f1a -> file 0x54aca =
E8 call site 0x54ac5 = THE POSTER (caller histogram 1/1 POSTER) esp_p8=0x0
(the 4th push at 0x54aa6 = edx=0 — the msg-4 poster form verbatim).
p54a88 + s2_56c74 fires were pty-render-only (re-arm-gap; t305 census law):
render contexts verified this session — '(Running)3ED8 3BBEA44D0200 cmp
edi,[esi+00024DA4]' and '(Running)60C4 FF5508 call near dword [ebp+0008]'.

### S4.2 Three-way verdict
(A) caller-never: REFUTED — the poster call site fired live (EV-banked).
(C) pump-entry-never: REFUTED — entry fired once, s2_56c74 fired once.
(B) gate-never-equal: CONFIRMED as the blocker, with the exact equality named:
    at the fire edi=[obj+0x24da8]=-1 (set at 0x549de; banked edi=0xffffffff
    verbatim); ds:0x484a4=0 (idle read) -> unequal; [obj+0x24da4]=0 (idle read)
    -> cmp UNEQUAL -> 0x54ab0 msg-4 poster. msg 0xc REQUIRES [obj+0x24da4]==-1
    — never observed as anything but 0 (48.sav; t318 oracles never read it,
    t319 gate_read adds it: m24da4=0). [obj+0x489e]==0 already true.
    s2_56c74's single fire attributes to THIS msg-4 call [inferred: pty census
    says the pump entry ran exactly once whole-run, so the dispatch fire
    cannot belong to any other caller].
Block-conjunction key (how the block got entered at all): ds:0x484dc==-1 +
ds:0x484d0!=0 (0x5497b/0x549d1 gates) — set by the mouse-state recorder fn
0x2a7a4 (0x2a7a8-0x2a7bb: arg2 != ds:0x484d0 -> store + set -1). It happened
ONCE this run, right after a gutter click.

### S4.3 What this does NOT say
- No 0x1c01 anywhere: the msg-4 poster is NOT the destination-widget road;
  the OQ-019 residue (0x1c01 -> FLEETWND -> DAT_43508 store) is STILL unwitnessed.
- fn51cc4_entry was not armed this run (dropped per shape spec) — FLEETWND
  msg entry zero is NOT re-measured here; t317/t318 zeros stand.
- One poster fire in a 28-min run means the conjunction is rare; the msg-4
  broadcast evidently does nothing observable (DAT_43508 oracles unmoved all
  phases; turn 1086->1087 only via NEXTTURN control).

## S5. WRITER OF THE BLOCKER MEMBER FOUND (static bonus, t91_code_disasm
## 76950-77000 verbatim) — [core+0x24da4] is the MOUSE-ACTIVE flag of fn 0x54650 itself:
- 0x54673-0x546b4 (every fn 0x54650 pass): edi=ds:0x484ac (mouse-state word;
  writer fn 0x2a6xx @0x2a629 sets -1 on activity, 0x2a635 clears); iff
  484ac!=0 AND [esi+0x24da4]==0 AND [esi+0x489e]==0 -> **mov -1,[esi+0x24da4]**
  @0x546a5 + call fn 0x30a60(0x484f8, edx=1, ebx=0), jmp 0x5470e.
- 0x546b6-0x546d6 reset road: iff 24da4!=0 AND ds:0x484ac==0 -> store 0 +
  fn 0x30a60(..., edx=0); then msg 6/7 broadcasts to [obj+0x3002] slot via fn 0x56ca4.
- Therefore at the poster cmp 0x54a88: msg 0xc fires iff the mouse was ACTIVE
  in THIS fn 0x54650 pass (24da4 just set -1); msg 4 fires when the mouse went
  quiet before this pass (24da4 reset to 0 at 0x546d0, or never set). Our
  witnessed msg-4 fire = the pass where ds:0x484ac was already 0.
- Other writers: 0x54532 mov 0,[ecx+0x24da4] (separate fn); 0x54b10 mov 0
  (downstream of 0x54b02 cmp -1 in the tail); reader 0x5a1e8 inside fn
  0x5a1e4 (on the no-poster road only).
- t320 SHAPE IMPLICATION (inferred, needs live check): the t317 gutter click
  ALREADY sets the entry conjunction (484dc=-1 via fn 0x2a7a4); the missing
  ingredient for msg 0xc was the 484ac mouse-activity flag being set in the
  SAME main-loop pass the poster block runs. A click shape that keeps the
  mouse busy at poster time (e.g. click held/moved, or a second input
  immediately before) is the candidate — arm {pump_entry_56b5c} + read
  ds:0x484ac/0x24da4 oracle pair per window. Per t318 amendment (3) this is
  the ONLY remaining capture shape with a named mechanism; try the OFFLINE
  ds:0x484ac save census FIRST (r319_gate_read extended with ds484ac) to see
  whether any recorded input traffic ever set it.
## S6. Original-behaviour note for the rewrite (OQ-019 family, not closing):
## the vendor broadcasts msg 4 (not 0xc) to all mask-registered windows when
## the mouse goes quiet after activity; 0xc only in the active pass. No
## DAT_43508/0x1c01 involvement either way (108-stop witness).

## S5.1 ds:0x484ac SAVE CENSUS (r319_gate_read, all 20 saves of the run):
## (ac,d0,dc,m24da4) = (0,0,0,0) in EVERY save — the flags are TRANSIENT
## per-main-loop-pass and the autosave cadence is ~10 s (t260 law), so saves
## are BLIND to them: this is not evidence against the mechanism (the live
## banked poster fire already proves the conjunction occurs on click traffic).
## A msg-0xc witness therefore REQUIRES a live leg stop, and the only leg
## that names the road is pump_entry_56b5c itself (edx==0xc).
