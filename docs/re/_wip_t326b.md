
# t326b WIP — STATIC WALK fn(0x17c54) + fn(0x16147) (decides Phase Bomb launch road)

## S0. Start (fresh session 2026-11-07). Sitting check NEGATIVE (playcap newest turn=1086).

## S1. Assets + segmentation law (measured)
- work/t91_code_disasm.txt = objdump of work/ascend_restored.bin, 140824 insns,
  range 0x14bb0..0x826a5. Pad-run segmentation: int3/nop runs delimit functions
  (527 pad-runs). NOTE objdump mnemonic lives AFTER 2nd TAB (bytes column first) —
  first-pass script bug fixed (r326b_extract.py).
- fn(0x17c54) = 0x17b2c..0x17f1e (285 insns) -> work/r326b_0x17c54.txt;
  functions_full.tsv row 17b2c size 1011 (0x3f3) => END 0x17f1f MATCHES pad-run law.
- fn(0x16147): pad-run law gives 0x15630..0x1641a but tsv says fn 0x156d4 size 2551
  => END 0x160cb, so 0x16147 is NOT in fn(0x156d4); tsv has NO function containing
  0x16147 (gap 0x160cb..0x16754). 0x16129 disassembles as raw bytes "00 00 00"
  (badbar) => tsv segmentation dead there; pad-run fn 0x15630..0x1641a is the
  working unit (verify entry later).

## S2. SITE 0x16147 READ (verbatim, work/r326b_0x16147.txt)
0x1612c mov eax,ebp; 0x1612e mov BYTE[ebp+0xb9],0x1; 0x16135 call 0x16cf0;
0x1613a mov eax,[ebp+0xbb]; 0x16140 call 0x17224; 0x16145 jmp 0x16162   <-- SKIPS 0x16147
0x16147 mov ebx,0x51 (81)          <-- msg-id-in-ebx PRECEDENT, block entered from elsewhere
0x1614d mov edx,[ebp+0xbb]; 0x16153 mov eax,0x7a35c; 0x1615a xor ecx,ecx;
0x1615a.. edx=[[ebp+0xbb]+0x41]; 0x1615d call 0x56ca4
0x16162: tail -> mov edx,0x1c01; mov eax,ebp; call [ebx+0xc]; return -1.
- 0x16122 clears [ebp+0xb1]=0 ~25B BEFORE 0x16147 => t326's "post-shaped sibling"
  framing is WRONG: 0x16147 is a separate block reached by an edge TBD; the clear
  feeds the 0x16135 call path (eax=this-object ebp).
- OPEN: who jumps to 0x16147; what is 0x56ca4 (post? string-format?); what ebx
  holds at 0x16162 on the 0x16147 path (tail uses [ebx+0xc] — ebx was 0x51!).

## S3. 0x56ca4 DECODED (disasm lines 79837-8959) — MESSAGE POSTER, 16-bit id
fn 0x56ca4: esi=eax(obj), edi=ebx(id), ebx=ecx, edx arg (stack +0xc).
  gate: sar16([obj+0x4226]) < 0 -> return (window-dead guard).
  0x56cc4: eax = edx*3 (lea edx*4; sub edx) -> slot = [[obj + edx*3 + 4]];
  esi2 = [slot+0xa7]; call [esi2+0x8](obj, msgid=sign_ext(bx=edi), edx_hi16).
=> classic SendPost(window, msg, data): vtable+0x8 dispatch, msg id is the
   LOW 16 BITS of ebx. ebx=0x51 at 0x16147 -> posts MSG 81 (0x51) with
   data = sar16([[ebp+0xbb]+0x41]). THE SIBLING SITE IS A REAL POSTER.
   (t326's windows.txt grep failed because it searched SENDMESSAGE, the
   script verb, not the engine post primitive.)
## S4. EDGE INTO 0x16147 FOUND + GATE DECODED
Only intra-fn edge: 0x1608e `je 0x16147` (disasm line 1574). Path upstream:
  0x16061 movsx edx,dx; test; ==0 -> 0x16076: [ebp+0xb0]=1; [ebp+0xb1]=esi;
  ax=WORD[[eax]+0x33]  <-- t248 LAW: planet record +0x33 == owner race byte;
  and al,0x40 -> TEST bit 0x40 of the owner field -> set: falls through to
  0x1607x/other leg; CLEAR: je 0x16147 -> post msg 0x51(81) to
  [[obj+edx*3+4]] slot window (edx from upstream [[ebp+0xbb]-indexed walk),
  then tail 0x16162: ebx=[[ebp+0xa7]] (vtable self), edx=0x1c01,
  call [ebx+0xc] = engine event-return 0x1c01.
OPEN: what bit 0x40 of [planet+0x33] means (phase-bomb-already-detected?
  owner-is-player?); what msg 81 CONSUMES are (search cmp 0x51 in batmode
  fn 0x1aef8 + whole-image consumer census); what edx is at 0x16147 (set
  between 0x1608e and 0x1614d? verify straight-line).

## S5. fn(0x16147) IS A WINDOW-CLASS MESSAGE HANDLER (uclass 0x5850)
- 0x15630 = class ctor/dtor: on cl&4 -> [eax+0xa7]=0x5850; call 0x30ad8 (create
  window from spec). 0x15674 = field-init (fields +0xab,+0xac,+0xb0,+0xb1,+0xb5,
  +0xb9,+0xbf). fn body prologue 0x156d4 (push ebx/edx/esi/edi/ebp; sub esp,0x8c);
  tsv fn 0x156d4 size 2551 ENDS 0x160cb mid-instruction => tsv segmentation BROKEN
  past 0x160cb (badbar 00 00 00 at 0x16129 desync); objdump fresh range-decode
  (objdump -D -b binary -mi386 -M addr32,intel --start-address --stop-address)
  re-syncs cleanly. 0x16147 handler returns 0x1c01 via [ebx+0xc] (same engine
  event-return as fn 0x1aef8/BatModeWnd family).
- PATH to 0x16147 (fresh objdump, all straight-line verified):
  handler reads word [esp+0x84] = msg param1; call 0x32fa4(eax=[ebp+0xb5],edx=idx)
  -> eax = GIZMO RECORD ptr (stride 0x6a, base 0x7650c corroborated at 0x16036:
  imul idx*0x6a + 0x7650c); flags = WORD[[rec]+0x33]:
    bit7 (0x80) set -> ABORT (jne 0x15b39 path);
    then 0x16076 leg: [ebp+0xb0]=1, [ebp+0xb1]=rec; 0x16083 re-reads
      WORD[[esi]+0x33] mask 0x40: SET -> fallthrough 0x16094 (builds 0x2a-byte
      struct at esp+0x28, writes [[ebp+0xac]+0x62] record leg, then 0x1612c call
      0x16cf0 (child-find loop: [obj+0x67] child array, imm 0x13e, call 0x76ce0) +
      call 0x17224; jmp 0x16162 return)
      CLEAR -> je 0x16147: POSTS MSG 0x51(81) via 0x56ca4 (S3 law) then returns.
  => 0x16147 block is REACHABLE within this handler (gate: gizmo flag word
  [rec+0x33] bit 0x40 CLEAR, bit 0x80 CLEAR). NOT dead code.
- CRITICAL ANOMALY (unresolved): at 0x16147 edx = [rec+0x33] mask 0x20 (0 or
  0x20, straight-line from 0x16058) but 0x56ca4 uses edx as the slot INDEX
  ([[esi+edx*3+4]]). Either the post targets slot 0/0x20 deliberately or index
  semantics TBD. MUST resolve before claiming revive.

## S6. fn(0x17b2c) WALKED (fresh objdump range-decode; tsv size 1011 verified)
Shape: esi=this (obj with HUGE fields: +0x4f38,+0x4f3c,+0x4f44,+0x4f80,+0x5034,
+0x1d2a -- same object family as the game-state block, NOT a small widget).
Reads [[esi+0xab]+0x1] = kind byte; switch kind:
  kind==3: ebp=[[esi+0xab]+1] (record); loads [ebp+0x9e..0xa6] (3 dwords = XYZ)
    and [ebp+0x78..0x80] (3 dwords); [esp+0x54] = movsx BYTE[[[esi+0xab]+1]+0x62]
    ; [esp+0x50]=[[...]+0x84]; then eax = 0x76546 + 0x6a*[esp+0x54] ->
    [[esp+0x40]] = gizmo-rec field +0x3a (RANGE field per combat.md column law;
    base 0x76546 = 0x7650c+0x3a EXACT => design-table indexing CONFIRMED in code,
    file bytes at 0x7650c are UNRELOCATED garbage (scripts/r326b_gizmo_rows.py
    shows x86 opcodes at those file offsets) -- values need RAM, semantics do not).
  kind==2: ebp=[[esi+0xab]+1]; reads [ebp+0x0..8] (XYZ), [[ebp+0x6b]+4] rec ->
    [rec+0x9e..0xa6] XYZ; [esp+0x50]=[[ebp+0x6b]+8]; then 0x17c37: al=BYTE
    [[ebp+0x6b]+0x1] (design/gizmo rec kind byte), edx=[[esi+0xab]+1]+? ->
    call 0x39b6c(al,edx) (QUERY, return stored [esp+0x3c]=edx-out; NOT a post);
    RE-READS cl=BYTE[[rec]+1] at 0x17c5b: cl==0x1c -> [esp+0x54]:=0x4c;
    0x1d -> 0x4d; 0x1e -> 0x4e; else fallthrough to ASSERT REPORTER 0x2a438
    (ebx=0x20e, edx=0x1ae) at 0x17c8b.
  else: assert reporter (kind not in {2,3}).
KEY NUMERIC LAW (decisive): the values WRITTEN are 0x4c/0x4d/0x4e = 76/77/78 =
GIZMO INDICES (cidx space where t326 census says Phase Bomb-family rows live
just above 70); the KEYS 0x1c/0x1d/0x1e = 28/29/30 are a rec-kind/category
byte at design-rec +0x1 -- NOT gizmo ids (t326 note corroborated).
CONSUMER 0x17c9c+: edi=[esi+0x4f38] (guard, must be 0); sets [esi+0x5034]=2
(word); [esi+0x4f3c]=0; [esi+0x4f44]=[[esi+0x1d2a]+0x35] (ring member!);
writes BYTE ring+0=7, ring+0x33=0x12, ring+0x34=0; copies esp+0xc/0x10/0x14
(XYZ from rec) to [esi+0x4f80..]; then 0x17cf8: edi=[esp+0x54] (the 76/77/78
index) used as WORD index into [[esi]+0x1a92+edi*2]... (verify width next) +
[esi+0x1bcc+edi*4] before calls 0x1ce1c/0x17694.
=> NO MESSAGE POST IN fn(0x17b2c) UP TO 0x17d3c (all writes direct fields +
   ring record code 7). The t326 "mode-1 arming msgs 0x4d..0x51" framing for
   THIS family is WRONG: 0x4c/0x4d/0x4e here are TABLE INDICES (gizmo cidx),
   never placed in ebx/edx before a 0x56ca4-style post.
OPEN: fn(0x17b2c) callers + what code-7 ring record is (ring event queue?
  turn-event log?); width at 0x17d01 (mov ax,WORD [esi+edi*4+0x1a92] -- WORD
  read, dword-indexed stride 4 => table of dwords, low word used).

## S7. CONSUMER OF MSG 0x51 FOUND (breaks the clean-dead story) + fn identities
- fn 0x4709c (tsv size 987; objdump-synced) = window-class msg handler, msg-id
  in ecx, tree-dispatch (cmp 0x2e/0x49/0x4f/0x51). LEG 0x47ac0: `cmp ecx,0x51;
  je 0x47a53` -> block 0x47a53: [esi+0xe3] := 0xc2c80000 (float -4.0), then
  [ebx+0xc](self,0) event-return, call 0x47478, return 0. So MSG 81 HAS A REAL
  CONSUMER (window w/ field +0xe3 float, +0x898 word). Consumer window NAME TBD.
- POSTER 0x16147 target law (S3+S5 composed): 0x56ca4(eax=ds:0x7a35c) where
  0x7a35c = GLOBAL GAME OBJECT (299 refs image-wide; t264-era law); target
  window = [[0x7a35c + edx*3 + 4]] with edx = WORD[[gizmo-rec]+0x33] & 0x20
  (gizmo category bit; SAME bit gates shield charge at 0x49e78 per combat.md
  S(CHARGE) cited law). NOTE edx*3 then *4 => index*12 SLOT SPACE in the game
  object child table [[0x7a35c]+...] — NOT the [0..0x1f] small-index space
  BatModeWnd consumes; the game-object child slot at category-bit position
  receives msg 81.
- fn 0x16cf0 NAMED: child-widget finder loop (loop [ecx+0x6b] count, child
  array [ecx+0x67], call 0x76ce0 match const 0x13e, on miss assert 0x58c/0x147
  @0x2a428) then repaints children [child+0x35]/[child+0x39] per [ecx+0xb9]
  mode {2,3}. It is NOT a poster (t326 "post-shaped" gloss re-cited-dead).
- fn 0x56d1c = popup helper (sibling 0x56cf0 wraps it then posts via 0x56ca4;
  t290-era law re-corroborated: called with eax=0x7a35c, edx=msg-id 0x5e/0x77,
  ebx=0).
- fn(0x17b2c) call census (sed-range grep): {0x17030, 0x171c8 x2, 0x17694,
  0x1ce1c x2, 0x2a438, 0x39b6c, 0x4fb30 x2, 0x76da0, 0x76e08} — ZERO POSTERS
  (0x56ca4/0x56d1c absent) => fn(0x17b2c) CONFIRMED index/table family, NOT a
  msg sender. Its caller: 0x1750c inside fn ~0x17460 (a per-record loop over
  [[esi]+0x5032]>>16 entries calling family {0x17848,0x17a38,0x17b2c,0x17f20,
  0x18274,...} then common tail 0x174d3 -> [ecx+0x5036] bookkeeping + call
  0x1d7dc(fn 0x1d7dc = ring writers +0x1d36/+0x253a/+0x2d3e via 0x1a338)).
  fn 0x1ce1c = table accessor w/ bounds assert [eax+0x1a8e] (0x62b/0x83081) —
  the 0x1a92-table reader; fn 0x17694 iterates [ecx+0x1d32] ring (stride 0x35).
VERDICT TRAJECTORY: fn(0x17c54) family = OUTCOME B (index values, cited).
fn(0x16147) = OUTCOME A-shape POSTER (posts 81 to a game-object child slot),
but whether slot(category&0x20) == BatModeWnd (= would reach the 0x1b7cd
mode-1 road) is the DECIDING remaining question; if not, residue 1 stays
dead-by-composition (activation blocker t322 stands) with the post leg now
CITED-LIVE-CANDIDATE rather than static-dead.

## S8. FINAL VERDICT t326b — OUTCOME B (index values, cited dead for the launch road)
(1) fn(0x17b2c) call census = {0x17030,0x171c8x2,0x17694,0x1ce1cx2,0x2a438,
    0x39b6c,0x4fb30x2,0x76da0,0x76e08} — ZERO engine posters (0x56ca4/0x56d1c/
    0x56ad4 absent). The 0x4c/0x4d/0x4e writes are STACK-DWORD TABLE INDICES:
    consumer 0x17cf8 reads [esp+0x54] -> WORD [[esi]+0x1a92+edi*4] +
    [esi+0x1bcc+edi*4] before fn 0x1ce1c (bounds-checked accessor, count
    [eax+0x1a8e], assert 0x62b/0x83081) / fn 0x17694 (ring [ecx+0x1d32] stride
    0x35). Values 76/77/78 sit in the GIZMO-INDEX space (base law 0x7650c+0x6a*i;
    code-side corroboration 0x17bca: 0x76546 + 0x6a*idx = rec+0x3a RANGE).
    Keys 0x1c/0x1d/0x1e = rec byte +0x1 category, NOT ids (t326 corroborated).
(2) 0x16147: REAL POST (0x56ca4 vtable+0x8 law, S3) of msg 0x51(81), target =
    [[ds:0x7a35c + edx*3 + 4]] (game-object child table, 12-byte slots),
    edx = WORD[gizmo-rec+0x33] & 0x20 in {0,0x20} (straight-line verified fresh
    objdump 0x16033..0x16066; gate chain: bit0x80 -> abort 0x15b39; bit0x20 set
    -> call 0x49e78 (shield-charge per combat.md) + return 0x1c01; bit0x20 CLEAR
    -> je 0x16147 post). fn = class-0x5850 msg handler (ctor 0x15630 law;
    msg tree 0x156ec: >=0x327/0x32b/0x32d/0x1c01/0x1c02 branches).
(3) DECIDING CONSUMER LAW: BatModeWnd handler fn 0x1aef8 dispatch tree compares
    ONLY dx in {0x6,0xd,0x3b,0x46,0x47,0x4a,0x50} (sed-range census 7390-8010).
    0x51 > 0x50 falls to the default leg 0x1af7c. So EVEN IF the 0x16147 post
    targeted BatModeWnd, msg 81 cannot reach the mode-1 setter 0x1b7dd (whose
    sole entry is jbe 0x1b7d7 from cmp dx,0x50 @0x1b7cd, cited t296/ships.md).
    The actual 0x51 CONSUMER found image-wide: fn 0x4709c tree 0x47ac0
    `cmp ecx,0x51; je 0x47a53` -> [esi+0xe3] := 0xc2c80000 = FLOAT -100.0
    (verified struct.unpack), sibling 0x49742400 = +1000000.0 read at 0x47d03
    (fld) — a different window (gauge/score family), NOT batmode. Window name
    UNNAMED (class table not statically referenced; RAM-relocated per t303(5)).
(4) RESIDUE 1 STATUS: UNREACHABLE-BY-CAPTURE, cited, THREE+ independent dead
    legs: (a) t326 preflight census (no arming senders, carriers zero);
    (b) t323 writerless [ebp+0xb1]; (c) t329 commit-edge unreachability;
    (d) NEW t326b: the only msg-0x4d..0x51-family poster posts 81 to a
    game-object slot with an id BatModeWnd provably does not consume; the
    0x4c/0x4d/0x4e "msg ids" were never msg ids at all.
    Remaining live blocker for the batmode road = WINDOW ACTIVATION
    (windows.txt:1178 BatModeWnd STATE 1 16; t322 armed-zero x2). The 4-launch
    forced capture is VACUOUS for arming (research leg vacuous t326 + no
    reachable arming trigger cited) — DROP it; t327 (tool v2) is row 1.
ASSETS: scripts/r326b_extract.py (pad-run function segmentation over the t91
disasm; mnemonic = AFTER 2nd TAB law), scripts/r326b_gizmo_rows.py (shows
0x7650c file bytes are UNRELOCATED code — design-table VALUES need RAM).
LAW LEARNED: objdump range-decode (objdump -D -b binary -mi386 -M addr32,intel
--start-address --stop-address work/ascend_restored.bin) re-syncs past badbar
sites where the t91 tsv segmentation desyncs (00 00 00 pad at 0x16129, 0x156bf).
