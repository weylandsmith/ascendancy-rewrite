# WIP t99 — W6-A6: FUN_00043b50 race-maintenance TAIL + 0x2ef60 JUMP-TABLE CASES

Status: IN PROGRESS. Session started 2026-10-27. No new sitting (live-timeline
mtime Oct 26 15:44 unchanged) -> assignment stands.

## Assignment (docs/STATE.md NEXT ACTION t99)
1. Full objdump of FUN_00043b50 0x43b50..ret-walk extent. Banked already:
   gate word 0x6780[row+0x19a hi] > row+0x19e -> early return; edx==1 leg =
   jump table [eax*4+0x2ef60] on (row+0x19d-5)&0xff, cases 5..0xf
   (0x441c1..0x441d2 dispatch); edx==0 leg = integrity reset 0x43bd0,
   attitude floor 0x43c36, moves x2 0x43c5b; OPEN = tail past 0x43c5b
   (star-table walk 0x43c79..).
2. Dump 11 entries at candidate table address — CHECK FIRST the t96 address
   law: disasm immediates are cs-RELATIVE, restored FILE = cs-rel + 0x14bb0
   for obj0 code addresses. Candidates: FILE 0x2ef60 (assignment's reading)
   vs FILE 0x43b10 (= 0x2ef60 cs-rel + 0x14bb0). Adjudicate empirically:
   valid table = 11 u32s all inside FUN_00043b50 extent.
3. Disassemble every case body (cases 5..0xf).
4. Store-form store census (r1_t86 pattern) for every field written.
5. Meanings: row+0x19d, row+0x19e, 0x6780 word — cited or explicit UNMAPPED.
Bank to aicode.md §2e-expansion. No rewrite delta this session (one-task).

## Method notes carried in
- objdump -b binary -m i386 -M intel on work/ascend_restored.bin; VA==FILE
  offset in this image; --start-address needs 0x prefix (t91 trap).
- Entries in obj0 jump tables are PLAIN u32 file addresses (t96 law, the
  0x1d840 table self-verified); NO fixup decoding.
- R13/R14 active: do not re-open SO-name tie; do not touch LE debug tables.
- game/ untouched; scratch only.

## FINDINGS

### F1. ADDRESS LAW RE-CONFIRMED + TABLE DECODED (cited)
`jmp DWORD PTR cs:[eax*4+0x2ef60]` @0x441d8 resolves to restored FILE
0x43b10 (= 0x2ef60 + 0x14bb0 code-object intra base, t96 law). RAW FILE
0x2ef60 is pool garbage (15/16 u32 out of code range; 2 coincidental
in-image values 0x38988/0x936 = mid-inscription reads, NOT table entries).
TABLE AT FILE 0x43b10, 16 u32 entries, ALL inside FUN extent 0x43bbaf..
0x441bf (tool scripts/r1_t99_maint_census.py):
  al=0(19d=5)->0x43baf | 1(6)->0x43bf0 | 2(7)->0x43c3f | 3(8)->0x43c79 |
  4(9)->0x43d33 | 5(10)->0x43de4 | 6(11)->0x43e98 | 7(12)->0x43eec |
  8(13)->0x43fba | 9(14)->0x4402a | 10(15)->0x4400a NOP | 11(16)->0x4405f |
  12(17)->0x440b5 | 13(18)->0x4400a NOP | 14(19)->0x4414e | 15(20)->0x4418e
Gate correction: 0x441d0 `cmp al,0xf; ja 0x4400a` -> out-of-range keys jump
to the COUNTER-BUMP exit (0x4400a), i.e. unknown status still re-arms the
cadence counter. §2e's "cases 5..0xf" was right; the 16th case al=15 is
19d=20 -> 0x4418e.

### F2. FUNCTION EXTENT + SHAPE (ret-walk, objdump -D — note: -d shows
nothing on binary-format images, must use -D)
FUN_00043b50 = 0x43b50..0x44029 (prologue sub esp,0x6e4; locals [esp+0x6c4]
= RETURN VALUE, [esp+0x6c8] = counter temp).
Flow: cadence gate (word table 0x6780 idx=(row+0x19a>>24) > row+0x19e ->
return -1 UNBUMPED); [esp+6c4]:=-1; cmp edx,1 -> je 0x441c1 (dispatch).
CRITICAL: the edx!=1 fall-through at 0x43b9c RETURNS -1 IMMEDIATELY — all
maintenance bodies (0x43bb0..) are reachable ONLY via the jump table
(edx==1). Case bodies fall through to common tails:
  T1 exit 0x4400a: row+0x19e := temp[esp+6c8] (bumped/zeroed), return temp
  T2 0x43fe5.. (case 8 only): temp := cadence_word - row+0x19e -> T1
  (cases 0..7 bodies at 0x43baf..0x43d32 fall to 0x43fe5 too? NO — verified
   per case below; 0x43c0a/0x43c4c/0x43c71 jump 0x4400a when loops end)

### F3. CALLERS (rel32 census, tool §3): EXACTLY 3
- 0x3eb3c inside AI chain FUN_0003e6e0: edx:=1, eax:=race row -> THE
  DISPATCH path (AI turn only).
- 0x37baf + 0x37cb1 (module with 0x37b37 refs — event/UI family): a u16
  arg dx switch (cmp 1/jb, jbe, cmp 0x32 je) calls with edx=0 (-> return -1
  only) or other values; post-call reads [esi+0x19a], compares eax==-1.
  NOT fully adjudicated this pass (context beyond budget cut — named next).

### F4. row+0x19d WRITER CENSUS (tool §4): ONE writer image-wide
0x4460f `mov BYTE PTR [esi+0x19d],al` (paired 0x44617 row+0x19e:=0) — read
0x4460f body NEXT for the status-assignment law. READERS: cmp ==0 at
0x3a20b; ==1 at 0x495fa; ==2 at 0x38484/0x3f276/0x3f447/0x410ca; ==0x12 at
0x49a17/0x4a867/0x50f89; dispatcher 0x441c1. (Abs form [eax*2+0x12fb3] —
stride-2 BYTE array view at diplomacy-matrix phase; do NOT conflate with
race-row stride 0x1ee.)
row+0x19e WRITERS: 0x44011 (this fn T1 exit), 0x44617 (zeroed on status
assign), 0x3e7df (FUN_0003e6e0 — read NEXT; read at 0x3e7cf + 0x3e7ed
same neighborhood).
0x6780 TABLE: 64 u16 words dumped (values look scenario-initialized, e.g.
1792/26384/526/15256/1/4103/3538/41986...); writer census PENDING (tool
§4c only covers +0x19a disp refs: 0x37b37/0x37be0/0x37cb6/0x3e7ed + this fn).

### F5. CADENCE TABLE 0x6780 IS A DATA-OBJECT ADDRESS — tool §2 read it
wrong (at file 0x6780 = code bytes). Correct dump (FILE = 0x82bb0+0x6780,
data-object base law): words[0..31] = 0,0,0,0,0,60,100,62,77,90,150,70,63,
66,72,0,92,100,0,89,68,0,65535,65531,7452,30,6938,0,3340,3854,37,2 —
plausible DAY THRESHOLDS (scenario data, not code constants).
Index = (row+0x19a >> 24); row+0x19a hi byte aliases +0x19d (same dword).

### F6. row+0x19d INIT + row+1 LINK (0x4460f context read)
Enclosing fn of 0x4460f/0x44617 is a key=value race-row LOADER (pattern:
push buf[esp+0x100], push [esp+4], push KEYSTR (pool 0x84e4d/0x84e59/
0x84e5f/0x84e65 or numeric-literal keys 0x2297/0x22a3), call 0x77fe1,
store result word to row+0x1d7/+0x1d9/+0x1db/+0x1dd/+0x1e1/+0x1e5...):
  0x4460c: mov al,[esi+0x1]           <- race-row byte +1
  0x4460f: mov [esi+0x19d],al         <- STATUS := row+1
  0x44617: mov [esi+0x19e],0          <- counter := 0
=> the jump-table dispatch key row+0x19d IS the scenario-file row byte +1
   [verified store]; sole writer; readers cmp-values {0,1,2,0x12} banked.
Module identity of 0x444f3-region fn: string pool 0x84e4d.. adjacent —
CHECK next against race.txt debug path (r1_datafile_strings law).

### F7. PER-TURN COUNTER IN FUN_0003e6e0 tail (0x3e7bf..0x3e815, cited)
After ship-list kill loop (0x4a74c per ship) + decision block 0x3ea54:
  eax := [[ebp+7]+0x14] & 0x80        <- row ptr +1 -> byte +0x14 bit 0x80
  if zero -> exit (NO counter bump)
  ebx := row+0x19e + 1; row+0x19e := ebx              <- THE BUMP
  if race == player (DAT_0007458e) -> exit
  if ebx != 0 AND ebx != cadence_word[(row+0x19a>>24)] -> exit
  else edx:=0x18(24) eax:=0x7a35c ecx:=0 ebx:=0 call 0x55a60  <- EVENT 24
     (0x55a60 = event queue; t88 banked it for death events)
=> cadence law: every AI race fires EVENT 24 (name TBD) once per
   cadence_word(row+1) turns [row+0x19a hi aliases row+1? — 0x19a hi byte
   == byte 0x19d == row+1 per F6 init... NOT yet cited: who writes +0x19a;
   tool §4c shows refs only 0x37b37/0x37be0/0x37cb6 + this fn].

### F10. PROFILE-SOURCE — REVISED (row4 stale)
rows 0..3 (ACTIVE: DAT_0x13b96 hi == 4 in the campaign member) all satisfy
+0x19d == row byte +1 == dword19a hi (19/2/11/0). Row4 (+0x19d=20, byte+1=9)
is BEYOND the active race count = title-member stale data (t82 class).
LAW [verified static+live]: dispatch key row+0x19d is copied from race-row
byte +1 at race-generation (enclosing fn 0x44290.. = raceneg.cpp per debug
paths at pool 0x84e30); sole writer 0x4460f. dword[+0x19a] hi byte is the
same storage (row0 dword19a=0x13000000 -> +0x19d=19 byte-exact).

### F9. LIVE VERIFICATION + CADENCE GATE LAW (playcap/save/60.sav T=1254;
corollary index B+0x82BB0+X; base vote clean; IN-CAMPAIGN member only)
  row0 b+1=19 +19d=19 +19e=8  cad[19]=89  gate 89<=8 FAIL (player row,
       call gated at 0x3eb3c too: race!=player || DAT_0010ba4==-1)
  row1 b+1=2  +19d=2  +19e=1  cad[2]=0    gate 0<=1 PASS -> maintenance
       (profile 2 = MOVES x2) runs EVERY AI turn
  row2 b+1=11 +19d=11 +19e=64 cad[11]=70  FAIL (runs again at c>=70)
  row3 b+1=0  +19d=0  +19e=0  cad[0]=0    gate 0<=0 PASS but profile 0 has
       NO table entry -> ja -> T1 counter reset (no-op)
CADENCE LAW [verified]: counter row+0x19e bumped +1 per AI-race turn turn in
FUN_0003e6e0 tail iff [[row+7]+0x14]&0x80; maintenance executes iff
cad[k] <= counter; exit T1 stores counter := 0 (re-starts the period;
period = cad+1 ticks); case al8 EXIT GOES TO T2 (0x43fe5) which stores
counter := cad - counter INSTEAD (phase-preserving variant).
cad table 0x6780 is FILE-EMBEDDED (loads only at 0x37bf1/0x3e7f6/0x43b6f/
0x43fee, ZERO stores image-wide -> constant scenario table [verified neg]).
NOTE 0x441c9 stores [esp+0x6c8] := ebx(0) BEFORE dispatch — that is why
T1 resets to 0 for all bodies that don't take the T2 path.

### F11. CASE-BODY SEMANTICS (all 16 entries disassembled; ebx=0, temp :=
[esp+0x6c8]; EXIT T1=0x4400a stores row+0x19e := temp)
NOTE: internal al-labels in this block are OFF BY ONE for profiles 11..20
(0x43e98 is al=6/profile 11, not 12, etc.). THE AUTHORITATIVE PROFILE MAP
IS F18; this block keeps the raw bodies.
 profile cad live  leg
 5   62?  al0 0x43baf: ship list (0x40ec0): every ship +0x8c := +0x98
     (INTEGRITY restored to MAX). exit T1(temp=0).
 6        al1 0x43bf0: for EVERY OTHER race row (stride 0x1ee @0x12e16,
     count DAT_0x13b96 hi, skip self): if ([ecx+0x1b0]>>16) < ([eax+0x1cb]
     >>16 + 20) then [ecx+0x1b2] := that (ATTITUDE FLOOR toward self =
     other's-strength-word + 20). Ties t90 0x43c36 cite.
 7        al2 0x43c3f: every ship +0x88 (MOVES) <<= 1 (x2 RECHARGE — the
     t85g boundary law, race-gated at profile 7).
 8   live? al3 0x43c79: for each star with OWNER BIT byte+0x14 (self):
     0x22304(star)->ship array; every ship with owner==self && order kind
     [ship+0x58]==4 (HOLD): 0x220a8(star) issues kind:=5 then 0x21f58(self,
     ship) places at star pos w/ rng%200 jitter (t94 consumers) = HOLD
     SHIPS PULLED TO STAR.
 9        al4 0x43d33: star walk on byte+0x15 bits: every own ship +0x88
     (MOVES) := 0.
 10       al5 0x43de4: planet walk (0x2b057/0x7b, count DAT_0x3a091):
     own planets, skip [planet+0x16]==10, track MIN word [planet+0x42];
     on the min planet: slot array [planet+0x10], every slot whose class
     byte in {0,1}: 3-byte set {0x00,0x07,0x10} copied from data 0x6838,
     rng 0x7824f %3 -> slot class byte := picked value. RANDOM CELL-CLASS
     EVENT on own frontier planet (classes 0/7/16 semantics vs t35 chain:
     7 = LUSH? 16 = ? UNMAPPED pending).
 12       al6 0x43e98: LIVE system table walk (0x3a095 stride 0x162, count
     DAT_0x43489 hi): systems with owner!=-1 && [sys+0x58]==5: ecx :=
     [[sys+0x59]] or +4 variant (word [sys+0xa2]&0x7fffffff selects);
     0x21f58(eax=ecx, edx=sys) = place/keep-ship-at-system-star.
 13       al7 0x43eec: research-row loop (runtime base DAT_0x74744, stride
     0x4b, count = its own hi-word): edx = number of races with bit set in
     mask [row+0x7478b]>>24 (per-research-row race bitmask); if edx >= 2
     (CONTESTED tech): self joins mask [row+0x7478e] |= 1<<self; and if
     self's target word [2*self+0x76492] == this row idx: target := 0xffff,
     accumulator [2*self+0x764a0] := self_idx XOR target?? (edx:=ebx xor)
     = CONTESTED-TECH DROP-AND-RESWITCH maintenance leg.
 15       al10 0x4400a: NOP (cadence counter untouched).
 16  live row2=11? al11 0x4405f: star walk byte+0x14 owner bits: for every
     ship in own systems: [ship-rec+0x23] |= 2 (bit-2 flag set — panel
     kind3 arm tests &1; bit2 consumer elsewhere: UNMAPPED).
 17       al12 0x440b5: for every other row with state [row+0x1c0]==2 (AT
     WAR per t85c): for every third party (not self, not that row): if
     [third+0x1b2] (attitude toward self?) > [warrow+0x1c9] then clamp
     [third+0x1b2] := [warrow+0x1c9]. WARTIME ATTITUDE CEILING keyed to the
     enemy's +0x1c9 word.
 19  LIVE row0 (player, cad 89) al14 0x4414e: read own research target
     word [2*self+0x76492]; if 0xffff exit; ax := WORD[45*target + 0x74782]
     (research runtime record stride 45); store [2*self+0x764a0] := ax.
     = REFRESH-ACCUMULATOR leg (Chamachies profile).
 20  LIVE row4 (Minions, cad 68) al15 0x4418e: every own planet with
     [planet+0x54]!=0xff: WORD [planet+0x50] += 100.
### F12. PICK POOL CORRECTED (tool RC=0, data-intra law): 0x6838 holds u32
values 2,3,4 (FILE 0x893e8 = 02 00 00 00 03 00 00 00 04 00 00 00). The al5
leg copies 3 u32 (movs x3 = 12B), rng%3 -> writes the PICKED u32 to the
slot slot-class BYTE. Live slot-class histogram (60.sav, 145 planets x 16
slots): {0:462, 1:1326, 2:185, 3:168, 4:178} — classes 2/3/4 are exactly
the t35 chain values (barren/normal/rich). So al5 = ON THE OWNED PLANET
WITH MIN word[+0x42] (skipping +0x16==10), EVERY SLOT CURRENTLY 0 OR 1 is
RESET TO UNIFORM-BARREN/NORMAL/RICH [verified body; planet-choice key
+0x42 semantic UNMAPPED (candidates: least-developed; +0x50 rose-by-IND
per turn is the build-accumulator per income-law LIVE MEASUREMENT — +0x42
is NOT that)].

### F13. al7 CONTESTED-TECH MASK: operand address UNRESOLVED (honest).
Census 0x7478e refs = 5 (0x43f30/0x43f3c ours + 0x47853/0x478f7/0x47958 UI
research-window module); 0x7478b = 22 sites. BUT stride-0x4b phase-scan of
the whole data-intra span found NO table whose 66 records' +3 bytes lie in
0..4 (best 0) — the edi cursor + 0x7478b operand cannot index a live mask
table at face value. Either the research runtime base differs at runtime
(edi loop cursor + constant decode incomplete) or the mask lives heap-side.
SEMANTIC-LEVEL [verified from code alone]: row 13 maintenance (profile 12
races) counts races-per-research-row via [edi+0x7478b]>>24, and for any
row with >= 2 such races: self-bit into [edi+0x7478e]; if that row is
self's current target (0x76492[2*self]==row idx) -> target := 0xffff and
accumulator 0x764a0[2*self] := (i XOR row-idx) recompute. Exact address
law = named next-session residual.

### F14. CALLER ROLES (full disasm 0x37b6c..0x37cf6)
FUN_00037b6c = player-turn event TEXT leg (arg dx switch):
 dx==1 -> call 0x43b50(playerRow, edx=0): returns -1 unless cad<=counter
   (gate-pass with NO body => maintenance-due signal); if -1: writes
   BYTE [ebp+0xccb]:=2 + event 0x56ca4(...); else countdown = cad - counter;
   formats via static.txt getter strings 0x1c/0x1d (live table entries
   '' and 's' — member index = ptr+H law re-confirmed: entry [0x1c] at
   ptr 2437140 is a 1-byte string so [0x1d] overlaps its tail); getter
   0x1e='OK'. => UI COUNTDOWN FOR THE AI-MAINTENANCE DUE EVENT [verified
   flow, strings weakly decoded].
 dx==2 -> call 0x43b50(row, ebx) + push pool 'abres%02d' + profile-number
   (0x19a>>24) + 'help.txt' via 0x76c79 loader: FILE-NAME FORMATTER —
   'abres%02d' pool sits with 'RACE%02d.DIP' (0x21f0) family => the
   profile indexes an ABILITIES/RESOURCES scenario file per race NUMBER
   (abresNN)! Semantics of open NEXT.
 dx 3..0x31 (jbe 0x37bab covers 1..0x31? NO: jb 0x37ca1 for <1, jbe for
   <=1? exact: cmp 1 / jb / (cmp 2 implicit via jbe path 0x37bab on dx==1;
   cmp 0x32 je 0x37c9c for 50) — dx==2 arm re-calls with edx=ebx. Other
   values -> 0x33ff8 generic. [verified dispatch edges]
CALLER 0x3eb3c (FUN_0003e6e0 decision block) = THE AI-ONLY CALL (edx=1,
race != player unless DAT_0010ba4==-1) — t90 phase order re-confirmed.

### F15. FUN_0003e6e0 HEAD + EVENT IDs (full body now read):
row+3 == -1 (eliminated) -> exit. 0x402d8 (systems held) < 0 branch:
 per-ship loop, PLAYER-owned ships only enqueue EVENT 0xb (11) with
 ebx = ship[+0xa7]>>24 (star idx) -> 0x55a60 (event queue, depth cap 32,
 record stride 10: type word +0x475e/obj+0x4760/ctx+0x4764, counter
 +0x475a++). Zero-ships && 0x40f7c==0 -> EVENT 0xa (10). Tail (F7) ->
 EVENT 0x18 (24) per AI race when cadence EXACTLY met (note: exact ==, so
 if a turn is skipped the event slips one whole period — matches counter
 reset semantics: counter reset by T1 to 0; exact-match window hit is the
 ONE turn the counter equals cad).
 0x7a35c = GAME-OBJECT base for the event queue (299 immediate sites;
 queue fields [obj+0x4758 count hi-word], [0x55af3] gate ds:0x7a358==-1).
 EVENT 24 CONSUMER UNDECODED (P0 random-event module territory; named).

### F16. DIP-FIELD LOADER = FUN_00044290 (raceneg.cpp; RACE%02d.DIP via
pool 0x21f0 '%s %d' key=value scanner 0x77fe1): stores DECLARE-family to
row+0x1c7,+0x1c9,x2,+0x1cb,x2,+0x1cd,x2,+0x1cf,x2,+0x1d1,x2,+0x1d3,+0x1d5,
+0x1d7,+0x1d9,+0x1db,+0x1dd,+0x1e1,+0x1e5 (15 keys, 13 pair-overlap sites)
+ row+0x19d := [row+1] + row+0x19e := 0 (profile init). KEY LIST (race00
.dip DIPVALUES): DECLARE_WAR ACCEPT_PEACE PROPOSE_PEACE BREAK_ALLIANCE
ACCEPT_ALLIANCE PROPOSE_ALLIANCE START_ATTITUDE SHIP_PATIENCE BIO_PERIOD
BIO_MAXPOSITVE BIO_MAXNEGATIVE BIO_SIN_X BIO_SIN_HALF_X BIO_SIN_TWICE_X
NEG_PLAYER_TURNS = 15 keys == 15 stores (count match [verified]).
BIO_PERIOD in file is 180..800 (Minions 400) while the LIVE cadence table
0x6780 profile words are 0..150 — so row+0x19e period is NOT raw
BIO_PERIOD; conversion/scaling UNMEASURED (0x6780 has zero writers —
populated by the loader FUN_00044290 leg or scenario init; writer at
0x44512-0x44605 stores go to ROW words, not 0x6780; NAMED residual).

### F17. al14 (profile 19): word = [45*target + 0x74782]; stride 45 !=
research-runtime 75 — a DIFFERENT parallel table (0x74782 word0=50=cost?
[unverified]); refreshes progress accumulator 0x764a0[2*self]. SEMANTICS
PARTIAL: cited store, uncited meaning of the stride-45 word.
*** t105 REFUTED [verified]: stride is 75, not 45 — the body's index math
lea [edx*4]/add edx/shl 4/sub = 75t byte-pinned 0x4416b..0x44179; the word
IS the restree runtime cost (base 0x74744 = this file's research runtime,
cost u16 @ record+62; live fit 66/66 vs the OQ-013 cost law). No parallel
table. scripts/r1_t105_verify.py legs 2-3. ***

### F18. *** THE ABILITY MAP (help.txt, extracted/ascend00/help.txt §abil*/abres*) ***
The dispatcher key row+0x19d = SPECIAL ABILITY NUMBER; help.txt carries
'abil%02d' / 'abres%02d' sections PER RACE INDEX (abil00 Minions ..
abil20 Nimbuloids), and the 'abres%02d' + 'help.txt' push pair at 0x37cc0
is the UI opening the ability window. LIVE PROFILES: player=19 Chamachies,
1=Orfa(2), 2=Ungooma(11), 3=Minions(0, ELIMINATED row+3=-1) — exactly the
t85c race list. CASE BODIES vs VENDOR TEXT (every one matches):
 5 Fludentri  "repair all damage to your ships"      -> +0x8c := +0x98 all ships
 6 Baliflids  "force all aliens to make peace"       -> attitude floor push (strength+20)
 7 Swaparamans"double the power of all your ships"   -> +0x88 <<= 1  (** = POWER, see F19)
 8 Frutmaka   "warp alien ships out of your colonies' stars" -> in own stars, ALIEN (owner!=self) kind-4 ships re-placed via 0x220a8/0x21f58
 9 Shevar     "wipe out the power of all alien ships in systems you occupy" -> own systems: alien +0x88 (POWER) := 0
10 Govorom    "turn your LEAST POPULATED colony into a rich world" -> min-word[+0x42] own planet: barren-ish slots (0/1) := uniform {2,3,4}
11 Ungooma    "bump all ships in star lanes backward to their stars of origin" -> live sys table, [sys+0x58]==5 (lane): ship := at star (0x21f58)   [SA_BumpShipsInLanes, t85c]
12 Dubtaks    "steal any technology known by at least two other races" -> per research row: popcount(mask)>>=2 -> set own ownership bit; if row == own target: target:=0xffff (re-target)
13 Capelons   "make all your colonies invincible for one day" -> own planets: dword[+0x62] := 0xffffffff
15 Oculons    "see all star lanes" (passive)        -> NOP body (0x4400a)
16 Arbryls    "block all star lanes entering your colonized systems" -> lane entries: byte[+0x23] |= 2 (BLOCK BIT; table 0x16147)
17 Marmosians "cause aliens to strongly dislike any species at war with you" -> every state==2 warrow: third-party attitude [x+0x1b2] clamped DOWN to [warrow+0x1c9]
19 Chamachies "immediately achieve any discovery; research complete in one day" -> accumulator [self+0x764a0] := WORD[45*target + 0x74782]
20 Nimbuloids "boost the progress on all your colonies' projects" -> own planets (+0x54!=0xff): build accumulator WORD[+0x50] += 100
Passive/absent abilities: profiles 0 (Minions), 3 (Kambuchka), 4 (Hanshaks)
have no entry (ja -> counter bump only); 15/18 (Oculons/Chronomyst) map to
the two NOP entries. INTERNAL CONSISTENCY airtight: every shipped body
corresponds 1:1 to the vendor ability text of the same index.
al7 MASK LAW RESOLVED: operand [edi+0x7478b/e], edi = i*0x4b = DATA INTRA
of research row i (0x7478b = research runtime base) — raw-intra form
(t96-class caveat, live loader relocates). The mask = research row dword+0
byte +3 = PER-RACE OWNERSHIP BITMASK; LIVE 0x0f all rows at t1254 (all 4
races own all techs after 1254 turns — consistent). Earlier phase-scan
"no table found" was MY filter error (filtered hi<=4; masks are bitmasks).
Govorom +0x42 = least-populated key per vendor text (planet +0x55 = pop
per t81; +0x42-vs-+0x55 relation still uncited — vendor-text-cited only).

### F19. FIELD-CORRECTION CANDIDATE: +0x88 = POWER, not MOVES.
Panel fmt (t95) 'POWER %d MOVES %d INTEGRITY %d' args = +0x88/+0x94/+0x8c;
help.txt doubles +0x88-class effect for Swaparamans POWER and zeroes it for
Shevar POWER; combat.md S2d ALREADY banks "0x4a756 init sets +0x88 = gizmo
power sum". t85g/t90's '+0x88 = MOVES / boundary recharge = x2' label is
therefore WRONG for the doubling site (0x43c5b runs only for profile-7
races; no campaign race is 7 — the t85g 'boundary recharge' observation
needs a re-attribution pass: MOVES = +0x94 candidate). BANKED for the next
combat/turn-boundary pass; live t85g observations stand, only labels move.

### F20. 0x6780 = ABILITY COOLDOWN TABLE (per ability index):
cad[5]=60 6=100 7=62 8=77 9=90 10=150 11=70 12=63 13=66 14=72 16=92
17=100 19=89 20=68 (live == restored-file words; zero writers). UI leg
0x37b6c dx==1 shows countdown cad - counter ('%d day%s' plural-s pattern;
getter strings [0x1c]='' [0x1d]='s' live). VENDOR TEXT ties: 'It will take
%d day%s to amass the energy' (abil06) -> OQ-020 lead: SAME table may feed
the player amass period (t57c FUN_00039c10) — NOT yet cited; annotate only.
NOTE cad[6]=100 (Baliflids) but earlier F-note lines said 77 — table index
= ability number directly (ability 6 word = 100).

### VERDICT vs assignment
  bodies + both exits + the two 0x37b6c caller legs).
- row+0x19d MEANING CITED (scenario race-profile byte+1, sole writer
  0x4460f, dispatch key 5..20). row+0x19e CITED (per-profile cadence
  counter: +1/turn iff [[row+7]+0x14]&0x80, reset on fire, exact-match
  event window). 0x6780 word CITED as cadence-period constant table
  (zero-writer) WITH the BIO_PERIOD mismatch flagged UNMEASURED.
- OQ-016: A6 decode lands; row STAYS OPEN (strict-close: A7 event module,
  al7 mask address, cadence-vs-BIO_PERIOD scaling, abresNN file open).
- Rewrite delta candidates filed for NEXT, NOT implemented (one-task):
  per-profile AI maintenance (MOVES x2 on profile-2 cadence, integrity
  restore, attitude floor/ceiling, contested-tech reswitch) + the t85g
  boundary-recharge attribution is NOW profile-keyed (profile 7 = x2) —
  note rewrite growthPhase/turn loop currently recharges unconditionally;
  that is a citable delta (FUN_00043b50 case 7 + gate law).




