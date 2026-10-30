1|# t206 — WIP: CONSUMER LAW of the per-star attacked-mark array [0x48304]
2|
3|Task: docs/STATE.md NEXT ACTION t206. t205 established the WRITER
4|(byte[0x48304 + star_idx] |= 1<<victim, 0x43afa, engagement star;
5|_wip_t205.md S2/S6). This iteration censuses the READERS and decides for
6|each: decision (branch) / text-arg / propagation, with the
7|0x4610b/0x4611c read-modify-write pair checked head-on against t204's
8|PERMANENT claim.
9|
10|Sites under study (t205b census, _wip_t205 L117-122):
11|  readers  0x4162f (guard ebx==[0x7458e] current player),
12|           0x42bd2 (diplo-state==2 guard block),
13|           0x45e8d, 0x46213
14|  RW pair  0x4610b read / 0x4611c write  (candidate transfer/decay)
15|  bit-0    0x24e84 OR 1 / 0x24e39 AND 0xfe inside star-init 0x24f24,
16|           0x24e74 read, 0x25008 fill (mov eax,0x48304; call 0x76e30)
17|
18|## S0 — trigger triage
19|- live-timeline.jsonl size 5,721,578,066 == frozen baseline EXACTLY
20|  (mtime 2026-10-29 13:22:12.100000000); dosbox-x not running; tree clean
21|  at d9db21a. No sitting -> STATE t206 assignment stands.
22|
23|## S1 — function attribution (work/functions_full.tsv, spans OVERLAP —
24| Ghidra nested/inlined entries; pick the tightest) [verified]
25|  0x4162f  -> 0x41260..0x43270  (t183: the ORDER RESOLVER dispatcher)
26|  0x42bd2  -> inside 0x41e34..0x47ebb nesting; tightest own-fn unclear, the
27|               loop back-edge 0x42b7d is the unit-slot loop (see S3)
28|  0x45e8d, 0x4610b/0x4611c -> 0x45e48..0x465aa  (one function; 0x4612a
29|               call 0x55a60 = the t203 EVENT-FIRE helper)
30|  0x46213  -> 0x46144..0x463b8
31|  0x24e39/0x24e74/0x24e84 -> 0x24dd0..0x25108; 0x25008 also in
32|               0x24f24..0x258a7 (star-record init, t205)
33|  0x43afa  -> 0x43a4c..0x43be1  (t204 handler)
34|
35|## S2 — W4 THE 0x4610b/0x4611c RW PAIR [verified, work/t206_w2.txt]
36|0x46105..0x4612a verbatim (function 0x45e48..0x465aa, ebp = a star record):
37|    0x46105 mov ebx,[ebp+2] ; 0x46108 sar ebx,0x10    ; star index
38|    0x4610b mov cl,[ebx+0x48304]                      ; READ mark byte
39|    0x46111 mov eax,0x7a35c                           ; event-string (pool-rel)
40|    0x46116 or  cl,1                                  ; <== sets BIT 0 ONLY
41|    0x4611c mov [ebx+0x48304],cl                      ; WRITE back
42|    0x46122/0x46126 stack args; 0x4612a call 0x55a60  ; FIRE EVENT
43|VERDICTS:
44| (a) t204's PERMANENT claim SURVIVES head-on: the RMW is `or cl,1` — an
45|     OR-set of bit 0, NO decay, NO transfer between stars/races (same-byte
46|     read-modify-write only). The only clearer in the whole corpus is the
47|     0x24e39 AND 0xfe inside star-record INIT (see S5) — i.e. at game setup,
48|     not mid-play.
49| (b) This reader IS a producer of bit 0 mid-play: it ORs bit0 then fires an
50|     event via 0x55a60 with string 0x7a35c. Guard above (0x460eb..0x46103):
51|     [ebp+0x17] bit cl? -> value 3 else 0x14 (20); cmp edx,-1 -> je skip.
52|     Context window 0x45e40..0x45ee0 pending (S4).
53|
54|## S2b — W1 0x4162f READER: DECISION, DISPLAY-FLAG WRITE [verified,
55| work/t206_w1.txt]
56|0x41610..0x4668 verbatim (inside order resolver 0x41260):
57|    0x41610 mov ah,[edi]            ; unit owner race byte
58|    0x41612 cmp ah,cl ; je skip     ; (cl from loop) 
59|    0x41618 mov cl,[0x7458e]        ; CURRENT PLAYER (t191 identity)
60|    0x4161e cmp ebx,ecx ; jne skip  ; owner must == current player
61|    0x41622 mov ebx,[esp+0x39c]     ; unit record handle -> [ebx+2]>>16 = STAR IDX
62|    0x4162f mov bl,[ebx+0x48304]    ; READ the per-star mark byte
63|    0x4163a mov cl,ah ; shl esi,cl  ; esi = 1<<owner
64|    0x41644 test ebx,esi ; je skip  ; IS the owner's bit marked at this star?
65|    0x41652 mov ch,[esp+ebx*2+0x36c] ; per-unit status byte (stack table)
66|    0x41659 or  ch,0x20              ; SET BIT5 on the unit's display status
67|    0x41661 store back
68|=> DECISION-bearing but the EFFECT is an "attacked" EXCLAMATION/notice bit
69|   (bit5) on the owner's units at the marked star, computed per frame from
70|   [0x48304] — the resolver's stack status table is the UI alert mirror.
71|   The mark stays the source of truth; the rewrite's attackedAt(star) IS the
72|   same channel (rewrite has a marks() consumer surface already).
73|   CAVEAT: mid-window decode seeded 0x41600 drifts 2 bytes (a je 0x41668
74|   lands mid-insn); re-verified from 0x4160b anchor. Boundary law R108: the
75|   chain from the je-target is self-consistent.
## S3 — W2 0x42bd2 READER (inside order resolver 0x41260..0x43270) [verified]
Loop over an entity's slot table (work/t206_w2.txt + head 0x42b68):
    per slot i < word[eax+0x5a]: slot ptr [esp+0x394] + 4*i -> [..+0x46];
    bl = byte[slot+0x57]; skip if 0xff; skip if bl == byte[edi] (self);
    skip if byte[row +0x1c0] == 2 (relation WAR, t189 identity);
    ch = [0x7458e] MUST equal byte[eax+0x57] (entity owner == current
    player); then bl = byte[star_idx + 0x48304] (star handle at
    [esp+0x394+2]>>16), edi = 1 << byte[edi] (self-race bit),
    TEST -> on SET: esi = eax (scan result nonzero at 0x42bf8).
VERDICT: DECISION (eligibility), current-player only; WAR-relation guard
sits adjacent. Feeds the resolver's result register (unit action
availability at an attacked star) — unit-ORDER semantics, NOT a diplo/AI
value channel.

## S4 — W3/W4 function 0x45e48..0x465aa = PER-STAR CONTACT-NOTICE handler
[verified, w3+w5+w7 windows]
Sole caller 0x4a90a inside the lane-march body 0x4a74c (t189). Arm context
0x4a8d4..0x4a90f: edi = star record via [[ship+0x59]] (current star); ship
owner ([ship+0x54]>>16) MUST == current player [0x7458e]; EBX=ship,
EDX=star -> call 0x45e48.
Body: owner byte [esi] == player else assert 0x2a428(0x534,"0x2414");
    0x45e87..0x45e9b bit0 GATE: (byte[star_idx+0x48304] & 1) SET -> return
    0 (0x46136) = already announced at this star, no re-fire;
    else loop races r < word[0x13b98], skip r == player, skip unless byte
    [edi + r*0x1ee + 0x1c0] == 0 (relation UNDISCOVERED), star-vision bit
    test (byte[edi+0x15]|byte[edi+0x14]) & (1<<player) -> edx 3 else 0x14,
    edx == -1 -> skip;
    0x46105..0x4612a THE RW PAIR: cl = byte[star_idx+0x48304]; or cl,1;
    store; call 0x55a60 (EDX=event code, EAX=0x7a35c = THE STRIDE-10 EVENT
    RING game-object base — aicode.md:979/:1042 — NOT a string; bytes at
    0x7a35c are code, re-measured this session).
=> BIT 0 SEMANTICS CLOSED: bit0 = "contact/event announced at this star"
   LATCH (gate BEFORE the write at 0x45e93; fire-then-latch shape).
   t204's PERMANENT claim for victim bits 1..7 SURVIVES head-on: the only
   mid-play RMW on the byte is OR 1 — no decay, no transfer.

## S4b — W5 function 0x46144..0x463b8 = FIRST-CONTACT ESTABLISH (peace
init + notice) [verified, w7]
Sole caller 0x4a932 (same march-body branch where the star vision masks
ALREADY contain the player bit: byte[edi+0x15]|byte[edi+0x14] test at
0x4a921..0x4a92c). Body:
    0x4616c race = u16 handle [esp-2] >>16 (the OTHER empire);
    0x46182..0x4618e if byte[edi+0x15] has bit(race) -> jump 0x46208
      (vision-only re-check path, skips relation init);
    0x461a4 relation byte [edi + race*stride + 0x1c0]: if != 0 -> 0x461fe
      branch; if == 0 (UNDISCOVERED): SET to 1 = PEACE (t187 identity) +
      contact bookkeeping (word [esi+0x1d5] -> [row+0x1b2]; byte
      [player*494 + 0x12fd6] = 1);
    0x4620d..0x46220 bit0 gate AGAIN ((byte[star_idx+0x48304]&1)==0
      required), event codes 8/9 (0x461f5/0x46203 on the cl==2 leg),
      call 0x55a60 at 0x46233, then 0x4623e or byte[star_idx+0x48304],1 —
      latch set AFTER firing.
VERDICT: propagation (relation cells 0->1, first-contact bookkeeping) +
event fire; the mark byte is consumed ONLY as the bit0 latch, never as
victim bits. Victim bits never gate first contact.

## S5 — W6 bit-0 pair function 0x24dd0..0x25108 = turn-advance MARK
MAINTENANCE / notice producer [verified, w4 head + w6 tail]
Prologue 0x24dd0: EAX in = 0x12e10 diplo-table base (callers 0x55ed0/
0x55f98 pass mov eax,0x12e10 — t192 base), EDX = 1<<current-player
(0x24dde..0x24df6), ESI = EBP + 0xdb5 (a per-empire diplo context).
Sequence:
  (1) 0x24e0e call 0x439f4(EAX=star rec): builds mask of races r (r <
      word[0x13b98]) with row[r*0x1ee+0x12e19] != -1 AND byte[r + ESI +
      0x1c0] == 2 -> the WAR mask vs this context (t189 identity 2=WAR).
  (2) 0x24e1c..0x24e48: IF dword[rec+2]>>16 == 0 (row 0 / HOME star) THEN
      for k < word[ebp+0x3335]: AND 0xfe byte[0x48304+k] — CLEARS bit0 of
      the first N mark bytes (N = the u16 at block+0x3335 — candidate lane
      count, t190 bridge lanes 58-ish scale). HOME RE-ARM of the
      announcement latch.
  (3) 0x24e71..0x24e9d loop over k: read bit0; skip while SET (0x24e82);
      at the first CLEAR k: OR 1 (latch now) then require byte[rec+0x15]
      & player-bit (vision) else next k; 0x22304 collect occupants; per
      occupant: owner = [occ+0x54]>>16; skip if owner == player; require
      byte[owner*0x1ee + 0x12fd6] == 2; occupant [occ+0x88] > 0; then
      [ebp+4]++ and RETURN NONZERO (callers fire event EDX=0x13 at
      0x55ef7/0x55fb6).
CALLERS 0x55ed0/0x55f98 sit in the game-advance dispatch 0x55ae8..0x5620b
(same block banks 0x55f06 -> 0x24f24 star-record INIT, t191); 0x24f24's
0x25008 mov eax,0x48304 / call 0x76e30 = the SETUP FILL (zeroes the array
at scenario init — the only clear of VICTIM bits, at setup).
VERDICT: the ONLY mid-play clearer is bit0-scoped (home re-arm 0x24e39);
victim bits 1..7 are never cleared mid-play anywhere. PERMANENT stands.
Function semantics: per-turn "someone is under attack at a visible star"
notice (event 0x13), latched per star via bit0.

## S6 — LIVE VERIFICATION (scripts/r206_mark_context_census.py, RC=0)
  C1 dword[0x12e10+2]>>16 == 0 -> 20/20 saves: the 0x24dd0 callers
     (mov eax,0x12e10 at 0x55ecb/0x55f93) DO take the handle-index==0
     branch, so the 0x24e26 clear loop runs on every call.
  C2 MEASURED u16[0x12e10+0x3335] == 50 == STAR COUNT (20/20). The address
     0x12e10+0x3335 == 0x16145 — the SAME live star-count word t205 W3
     read (diplo block and star-count word overlap there; the loop bound is
     the star count, not lanes). => every 0x24dd0 call clears bit0 on ALL
     50 stars first, then walks stars re-latching (0x24e84) and announces
     AT MOST ONE (return after the first hit at 0x24f04).
  S5 FIX (self-correction, R108 discipline): with C1+C2 the walk at
     0x24e71 always starts from an all-cleared field; the latch is a
     CALL-SCOPED announcement suppression (one notice per call, event code
     0x13), not a permanent star state. bit0 is therefore NOT part of
     t204's PERMANENT claim — permanence holds only for the VICTIM bits
     1..7, whose sole mid-play writers are 0x43afa (OR 1<<victim) and the
     OR-1 RMWs; sole clear = setup fill 0x25008.
  W6 OCCUPANT LAW (w6 tail verbatim): notice fires iff, at a star whose
     vision byte [rec+0x15] has the player bit, an occupant (0x22304 list)
     exists with owner != player, relation byte [owner*0x1ee + 0x12fd6] ==
     2 (WAR; 0x12fd6-0x12e16 == +0x1c0 the t187 relation-state byte), and
     u32 [occ+0x88] > 0 -> [ebp+4]++ then nonzero return -> caller fires
     0x55a60 EDX=0x13.
  C3 honest-negative RE-MEASURED under the array reading: window
     [0x48304, +0x40) ALL-ZERO 20/20 — neither victim bits NOR the bit0
     latch have any witness in the captured corpus (t203/t204/t205
     zero-witness family extends to every consumer branch).

## S7 — COMBINED CONSUMER LAW (the answer to the task)
The per-star mark byte [0x48304 + star] carries TWO INDEPENDENT CHANNELS:
  VICTIM BITS 1..7 (writer 0x43afa at attack, t204; never cleared mid-play):
    - 0x4162f order resolver: owner==current-player AND bit set -> sets
      status bit5 on the owner's units at that star (unit alert mirror);
    - 0x42bd2 order resolver: same test (WAR-relation neighbour guard) ->
      marks the scan result nonzero (unit action availability).
    => CONSUMERS ARE UNIT-LEVEL ORDER/DISPLAY ONLY. No diplo-value, AI
      target-pick, or emitter feeds on victim bits. The rewrite's
      attackedAt/attackedMarks bookkeeping is FAITHFUL (its no-consumer
      status is the original's minus the per-unit alert layer the rewrite
      does not model); gap row 12 residue shrinks by the display part.
  BIT 0 (contact/notice latch, never written by the attack handler):
    producers/clearers 0x45e48 (fire-then-latch, gate 0x45e93 BEFORE),
    0x46144 first-contact establish (latch AFTER 0x4623e; relation 0->1
    PEACE init at 0x461a8), 0x24dd0 per-call clear-all + re-latch-one
    announcement (event 0x13). 0x46144's relation init (byte[row+0x1c0]
    0 -> 1) is a DIPLO-STATE WRITE discovered incidentally — it matches the
    t187 identity 1=PEACE and the t189 accept-path law; no rewrite delta
    (rewrite starts relations at known states).
  t204 PERMANENT claim: SURVIVES head-on (checked as the task demanded).
HONEST NEGATIVES: all bit-0 witnesses are structurally absent from the
20-save corpus (post-first-contact, no-fire scenarios); the exact event-code
semantics (8/9/0x13/0x14/3) are ring-codes, decoded only as "queued
announcement" (aicode :979/:1042); 0x2a428 assert strings banked verbatim.
