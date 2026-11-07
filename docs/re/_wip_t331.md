# t331 WIP — BatModeWnd ACTIVATION static walk (5th independent leg; OQ-016 residue-1 obstacle)

## S0. Start (fresh session 2026-11-08)
- Sitting check NEGATIVE: playcap tail-seek newest turn 1086 (== corpus). r1_t85g_sitting.py not run.
- DECISIONS.md: no ANSWER block (grep -i 'ANSWER' empty) -> D2 unanswered, execute assigned task.
- Production :9 untouched: Xvfb 1461 + timeout 136357 + dosbox-x 136359 (ps at start).
- Assignment source: STATE.md NEXT t331. Outcomes: (A) trigger cited -> queue t332 forced-capture;
  (B) no trigger -> residue (1) gains 5th UNREACHABLE leg, row stays open strict-close.
- DEAD (not re-trod): t322 mouse battery, t323 activation probes, t325/t326 shield legs,
  t306 batmode site list, t324 class-table routes.

## S1. Instrument (measured)
- Fresh whole-code objdump: objdump -D -b binary -mi386 -M addr32,intel
  --start-address 0x14bb0 --stop-address 0x82bb0 work/ascend_restored.bin
  -> work/r331_disasm.txt, 140902 lines, ZERO badbar (0.13 s). Chosen because the t91/tsv
  segmentation is proven broken past 0x160cb (t326b S1/S5) — a fresh decode cannot inherit
  the desync that hid the 0x16xxx family from t323's tsv-based census.

## S2. FIRST CENSUS RESULT — [+0xb1] whole-image refs (grep '0xb1]' = 52 lines)
STORES to +0xb1 (13 sites — t323's census had 14 "sites" but did NOT include the 0x15xxx/0x16xxx family):
  0x1568c mov DWORD[eax+0xb1],0x0      (class-0x5850 field-init region)
  0x15ae3 mov DWORD[ebp+0xb1],0x0
  0x15b68 mov DWORD[ebp+0xb1],0x0
  0x15e9b mov DWORD[ebp+0xb1],0x0
  0x1607d mov DWORD[ebp+0xb1],esi      (t326b S5: = gizmo rec ptr, NOT a state id)
  0x16122 mov DWORD[ebp+0xb1],0x0
  0x161c3 mov DWORD[ebp+0xb1],eax      <-- INSIDE fn 0x156d4 body (t301 names fn 0x156d4 =
        BATCTRL/BatControlWnd class msg-handler slot-2; t323 cites fn 0x156d4 stores the
        fn 0x56d1c("BatModeWnd") result UNREAD). Classification pending S5.
  0x31c79 WORD[eax+0xb1]=0xffff        (ctor fn 0x31c54, t323)
  0x33787 WORD[eax+0xb1]=0x0           (ctor, t323)
  0x339a4 WORD[esi+0xb1]=ax            (char-cycler, t323)
  0x33c73 WORD[esi+0xb1]=cx            (t323 ctor family 0x33c34)
  0x33d1b WORD[eax+0xb1]=0xf3          (ctor fn 0x33d08, t323)
  0x364d2 WORD[edx+0xb1]=ax            (writes the TABLE not a window, t323)
  (0x31faf WORD[ecx+0xb1]=si = the fn 0x31f30 runtime switcher — appears in the
   fn-range, in t323; grep pattern '0xb1]' shows it as line 34588 '66 89 b1 b1...' — counted.)
READS: 0x15c38/0x15cf8/0x15e27/0x15e9b-region/0x160b5 (class-0x5850 handler family),
  0x31ec3/0x31f37/0x3219f, 0x338c4..0x33df4 cluster (cycler family).
NOTE the 0x15xxx family uses DWORD accesses on +0xb1 (field reuse: gizmo-rec pointer),
while the generic window layer uses WORD accesses — the same offset, TWO different record
families. DECIDING QUESTION: is the 0x15xxx/0x16xxx record family BatModeWnd's record?
ANSWERED S4: NO — class 0x5850 = BATCTRL (BatControlWnd): ctor fn 0x15630 installs
[rec+0xa7]=0x5850 (pool-relative: 0x82bb0+0x5850 = 0x88400 = live BatControlWnd class
value P0+0x88400 measured S3); t301's cited BATCTRL table [0x15630,_,0x156d4,0x16420]
lives at file 0x88400. So the 7 DWORD +0xb1 sites in 0x15xxx/0x16xxx are BatControlWnd's
OWN state field (same reuse t323 flagged), NOT BatModeWnd's.

## S3. NEW MEASUREMENT — THE BatModeWnd WINDOW RECORD IS RESIDENT IN THE CORPUS
(t324's honest caveat "no u32 -> BatModeWnd pool name => no record resident" was WRONG:
records store the RAW ASCII name at +0x20, not a pool-u32 ref. t324's class-table verdict
is UNAFFECTED — it anchored on the installer target, and the same record re-confirms it.)
Method: raw-ASCII scan of `Memory` member of work/r1/playcap/save/41.sav (B=0x1bf4d8,
P0=0x1bf450, Icarus-anchor law); magic u32 0x12345678 (t301 law) at name-0x20.
  "BatModeWnd" hits 3: member 0x2420e6, 0x244c7f (data-pool strings, no magic) +
  **member 0xfdc924 magic-backed RECORD**; BatControlWnd record 0xfdbebc; controls:
  COSMOSWnd 0xfd2398, FLEETWND 0xfe7a90 (= t313's record), STATUSWND 0xfd9fbc,
  PLANETALLOC 0xfe670c.
Fields read (member offsets; P0=0x1bf450):
  BatModeWnd    rec 0xfdc924: [win+0xb1] STATE WORD = 0; [+0xad]u32=0; [+0xaf]=0;
                [+0xa7]=0x2478e8 = P0+0x88498 = CITED BATMODE TABLE (t296 six slots,
                re-unpacked from restored image at file 0x88498: 0x1abfc,0x30d08,
                0x1aef8,0x1d858,0x311b8,0x1e9dc — EXACT; sole installer imm fn 0x1ac21
                `mov [eax+0xa7],0x58e8` pool-relative 0x82bb0+0x58e8=0x88498 re-verified);
                rect-low-bytes (7,0,7,0).
  BatControlWnd rec 0xfdbebc: state=0; [+0xa7]=0x247850 = P0+0x88400 = BATCTRL table;
                ctor fn 0x15630 `mov [eax+0xa7],0x5850` pool-relative verified.
  COSMOSWnd     state=253 (0xfd; NOT in its STATE ids {1,3,7,13} — id space includes
                special values near -1; ctor fn 0x33d08 writes 0xf3=243 same band);
  PLANETALLOC   [+0xad..+0xaf]=0xffff (t323 "-1 = none" law VERBATIM).
=> The window is CONSTRUCTED at boot and its state word MEASURABLY 0 across saves
   (20-save sweep pending S6). The activation blocker is now measurable, not inferred.
NOTE: "byte[+8]" in earlier notes = low byte of rect x0 (7) — NOT the fn 0x232ec switch
byte (fn 0x232ec writes [rec+0x8]=dl over ALL records; BatControlWnd/PLANETALLOC show 0,
the visible-map windows show 7 == windows.txt X0 values — the field is x0's low byte).

## S4. Class-table identity law (fresh, measured)
- Data class tables live at FILE 0x88xxx; installer imms are POOL-RELATIVE data offsets
  (imm + 0x82bb0 = file offset; RAM value = P0 + file offset). BATMODE file 0x88498
  (imm 0x58e8, sole installer fn 0x1ac21 — t324 re-verified); BATCTRL file 0x88400
  (imm 0x5850 in ctor fn 0x15654; live record value 0x247850 = P0+0x88400).
- Ctor shapes: fn 0x1abfc (BATMODE slot-0) test cl,4 -> assert str 0x88470 / else
  create fn 0x30ad8 + install table; reads/writes [rec+0x19be] child. NO +0xb1 write
  in ctor body 0x1abfc..0x1ac3c (state set by the generic create chain, construction-only).

## S6. DECIDING CORRECTION — t326b S8(3) REFUTED: MSG 0x51 (81) IS CONSUMED BY
## BatModeWnd AND THE POSTERS TARGET ITS OWN REGISTRY SLOT (all fresh-decoded)
(1) fn 0x1aef8 dispatch tail VERBATIM (bytes 66 83 fa 50 / 0f 82 77 f7 ff ff /
    0f 86 dd fd ff ff): 0x1b7cd cmp dx,0x50; 0x1b7d1 jb 0x1af4e (0x4d..0x4f -> default);
    0x1b7d7 jbe 0x1b5ba (0x50 -> publish leg, t296 law re-verified);
    **0x1b7dd FALLTHROUGH (dx==0x51): mov BYTE[ebp+0xb7],0x1 = MODE-1 ARMED.**
    t326b S8(3) claimed "0x51 > 0x50 falls to the default leg 0x1af7c" — WRONG:
    dx==0x51 fails BOTH `jb` and `jbe` and falls through onto the mode-1 store.
    (Tree entry into this sub-block: 0x1af2a cmp dx,0x52 / jb 0x1b7cd covers
    0x4d..0x51 — re-verified.)
(2) THE 0x51 POSTERS (image-wide `mov ebx,0x51` + poster-call shape; inside the
    BatControlWnd msg-handler fn 0x156d4 region): 0x16147->call 0x56ca4@0x1615d and
    0x16181-block->call 0x56ca4@0x161d1. Both: eax=0x7a35c (game object),
    edx = [[ebp+0xbb]+0x41]. [ebp+0xbb] SOLE writer 0x15769 = result of fn 0x56d1c
    (0x7a35c, imm 0x5e="BatModeWnd" — t323 VERIFIED imm); [ebp+0xb5] sole writer
    0x15793 = fn 0x56d1c(0x7a35c, imm 0x77="BatListWnd" — t323 VERIFIED).
    rec+0x41 = registry slot-id (t316 PROVEN law).
(3) LIVE MEASUREMENT (41.sav, law chain): BatModeWnd record runtime 0xfdc89c,
    slot-id[+0x41]=63; game-object registry (0x2bc35c+4+slot*12, t316/t319 law):
    slot 63 -> 0xfdc89c 'BatModeWnd' EXACT (controls: 0 NULL, 31 PLAYERS_MORE,
    32 DIFFICULTYMORE, 62 BatListWnd, 64 TOGGRID; highest populated 124).
    Poster dispatch re-verified VERBATIM 0x56ca4: guard sar16([obj+0x4226]);
    slot=[[obj+edx*12+4]]; call [[win+0xa7]+0x8] -> BatModeWnd class table slot 2
    = fn 0x1aef8. => POSTED 0x51 DELIVERS TO fn 0x1aef8 -> 0x1b7dd MODE-1.
(4) BatControlWnd identity (S4 law): class 0x5850 ctor fn 0x15630; msg tree fn
    0x156d4: 0x327/0x32b/0x32d/0x1c01/0x1c02 branches + sub-tree 0x162ac for
    dx<0x327 (0x322/0x323->0x15baa, 0x324->0x163e4, 0x325->0x158f3). windows.txt:
    children My^Items SENDMESSAGE 804(=0x324) rect 479,103-548,133 and
    Other^Items 805(=0x325) rect 557,103-626,133 — RIGHT-BAR widgets, MOUSEFOCUS 1.
    Block above BatControlWnd: TYPE 100 STATENUMBER 16 SHAPEFILE DATA\16BATTLE.SHP
    => state 16 = battle map; BatModeWnd/BatControlWnd/children all STATE 1 16.
(5) t322 re-scope: its legs armed fn 0x1aef8 (BatModeWnd slot 2) — BatModeWnd
    receives msg ONLY if a poster targets slot 63; fn 0x156d4 (BatControlWnd) was
    NEVER ARMED in any capture, and no battery ever clicked (513,118)/(591,118).
    The armed-zero is NOT evidence the 0x51 road is dead — the road's ENTRY was
    never instrumented.
OPEN (t332 legs): which fn 0x156d4 branch flows into the gate block containing
0x16147/0x16181 (0x1c01 leg? 0x324 leg? jump table? 0x16181 has NO direct j-edge);
gizmo gate WORD[[BatListWnd-current]+0x33] satisfiability at t=1086; button
visibility (STATE 1 16 vs current state 0 — see S7).

## S7. FULL ACTIVATION/ARMING CHAIN DECODED (VERDICT: OUTCOME A-MOST — road ALIVE,
## entry trigger = msg 0x1c01 delivery to BatControlWnd, capture legs named)
fn 0x156d4 BatControlWnd msg tree (VERBATIM 0x156ec..): >=0x327 set / 0x32b/0x32d
ba-toggles / 0x1c01 -> 0x15ebf / 0x1c02 -> 0x1625c / <0x327 sub-tree 0x162ac:
0x320 -> 0x15b5a, 0x324 -> 0x158c0 (My^Items), 0x325 -> 0x158f3 (Other^Items),
0xd -> 0x158a7, 0x1 -> 0x15758 (the ctor-name block: stores fn 0x56d1c("BatModeWnd")
->[ebp+0xbb], fn 0x56d1c("BatListWnd")->[ebp+0xb5] — t323 "result UNREAD" REFINED:
stored at msg-0x1 time, read by EVERY later branch).
0x1c01 BRANCH 0x15ebf VERBATIM: gate [[ebp+0xbb]+0xb7]==4 (BatModeWnd mode TRANSIENT)
-> reject 0x1589b; al = BYTE[ebp+0xb9]-1 (field-init 0 => al=0xff -> ja reject);
JUMP TABLE cs:[eax*4+0xb04] — REBASED in RAM (t313 law; file bytes at 0x836b4 are the
"...cosmos.cpp" assert string, RAW-READ FALSE ZERO — RAM scan found the table at member
0x1d4b04): entries [0]=0x15ef9 [1]=**0x15fed GATE BLOCK** [2]=0x16181 [3]=0x15ef9.
b9 STATE MACHINE writers: 0x15b51 b9=1 (msg 0x320 param al==0), 0x15b1e b9=2 (al==3),
0x15b48 b9=3 (al==2), plus 0x1c01-branch legs 0x15f1e/0x15f25 (b9=3) and 0x15f35 (b9=2,
when esi==4 and fn 0x32f34(accessor,[ebp+0xb5],param) high bit CLEAR) — and the same
0x1c01 pass POSTS MSG 0x53 to BatModeWnd (0x15f3c ebx=0x53 -> 0x15f75 poster,
edx=[[ebp+0xbb]+0x41]=63). So ONE 0x1c01 delivery sets b9=2 AND posts 0x53; the NEXT
0x1c01 goes table[1] -> GATE BLOCK.
GATE BLOCK 0x15fed VERBATIM: edx param -> fn 0x32f34(BatListWnd,[..]) reject-if-neg ->
fn 0x32fa4 accessor -> gizmo rec (cl=BYTE[rec] cidx; 0x7650c+0x6a*cidx+0x33 flags):
bit0x80 set -> ABORT; bit0x20 SET -> call fn 0x49e78 (SHIELD CHARGE, combat.md law) +
tail 0x1c01 return; bit0x20 CLEAR -> 0x16076: [ebp+0xb0]=1, [ebp+0xb1]=gizmo-rec,
bit0x40 CLEAR -> **je 0x16147: POST MSG 0x51 to [[ebp+0xbb]+0x41] = registry slot 63 =
BatModeWnd (MEASURED S6(3)) -> fn 0x1aef8 -> 0x1b7dd BYTE[+0xb7]=1 MODE-1 ARMED**;
bit0x40 SET -> 0x16181 block: [ebp+0xb1]=rec, SAME 0x51 post @0x161d1.
BACK-CHANNEL: fn 0x1aef8 ITSELF posts msg 0x320 to [[ebp+0xab]+0x41] (0x1b164/0x1b202,
inside msg-4 mouse legs; 0x1b127 posts 0x326) — BatModeWnd's [+0xab] is a BACKPOINTER
to BatControlWnd (its state-table field repurposed; [+0xab] NULL in saves where the
leg never ran — deref would fault, so the leg defines the field as non-null pointer).
SOLE 0x1c01 POSTERS image-wide (imm census 5 sites re-verified; fn 0x33320 emit-builder
VERBATIM): target edx=[esi+0x63] road of the PASSING window; STATSHIPLST road=95
(t316 685/685) -> FLEETWND. NO imm-0x1c01 poster with a BatControlWnd (61) target
exists statically; road-61 posters are the btn rect-hit leg fn 0x30e0e@0x30ecb
(msgs 804..813 from My^Items/Other^Items/Repeat/Pass/Auto/W/S/Z/I, windows.txt
VERBATIM) and fn 0x1aef8's 0x320/0x326 back-channel.
GIZMO FLAG SOURCE (t326b anomaly CLOSED): WORD[rec+0x33] writers = fn 0x49074 ONLY
(0x491ec store 0, 0x49221 or-bit from sscanf "%d" %s "gizmos.txt" flag_list, ended
255) = FILE-LOADED at scenario init (caller fn 0x4929c <- fn 0x4904c). gizmos.txt
flag enum VERBATIM: bit5=32 GZ_TOGGLEABLE, bit6=64 GZ_NOTARGET, bit7=128 GZ_PASSIVE.
Phase^Bomb row VERBATIM "5 4 25 0 1 40 0 0 13 3 255" -> flag_list {3}=bit0x8 ONLY:
bits 0x80/0x20/0x40 ALL CLEAR for Phase Bomb => the gate block's 0x51 leg is the
Phase-Bomb-appropriate path BY FILE DATA; a bit0x20 gizmo (any GZ_TOGGLEABLE, e.g.
shields-family) takes 0x49e78 instead.
CORRECTIONS BANKED (binding):
 C1 t326b S8(3) REFUTED (msg 0x51 fallthrough = mode-1 setter; see S6(1)).
 C2 t326b S7/S8 "post targets category-bit slot {0,0x20}" REFUTED: edx at both
    poster sites = [[ebp+0xbb]+0x41] = 63 (registry slot-id law t316), NOT the
    mask-0x20 value (straight-line re-read 0x16058..0x1614d: edx IS clobbered at
    0x1614c-0x1615a; t326b mis-attributed the gate value to the post index).
 C3 t324 caveat "no BatModeWnd u32 name ref => no resident record" REFUTED (S3:
    records store RAW ASCII at +0x20; record resident 20/20 saves).
 C4 t322 scope: armed-zero re-attributed — fn 0x156d4 (BatControlWnd slot 2) was
    NEVER armed in ANY capture; the chain ENTRY is untested, not refuted.
 C5 JUMP-TABLE LAW re-confirmed: cs:[disp32] tables are REBASED in RAM; file bytes
    at the disp32 can be assert-strings — NEVER raw-read a jump table from the file.
VERDICT: residue (1) (mode-1 arming / Phase-Bomb launch-msg) = ALIVE IN-IMAGE,
cited chain above; NOT the fifth UNREACHABLE leg. Sole uncited edge = who delivers
msg 0x1c01 to registry slot 61 (no static poster; engine pump or unindexed sender).
=> t332 FORCED CAPTURE justified (outcome A): legs {fn156d4_entry 0x156D4,
tbl15ef1 0x15EF1, gate15fed 0x15FED, post1615d 0x1615D, post161d1 0x161D1,
mode1_1b7dd 0x1B7DD, backch 0x1B180} + battery: FLEET-open -> system view ->
My^Items click SCREEN (593,218) (window rect 479,103-548,133 + (80,100) law) ->
BatListWnd item pick -> observe b9 progression + 0x1c01 arrival. If 0x1c01 never
arrives at slot 61 whole-log WITH entry leg armed, THAT is the fifth leg (honest,
instrumented this time).

## S5. SETTER BOUNDS LAW — MEASURED ON THE LIVE RECORD (decisive, new)
fn 0x31f30 VERBATIM (fresh decode): 0x31f44 `cmp si,WORD[eax+0xaf]; jl ok` else
ASSERT 0x2a428(ebx=0x396, edx=0x183e). WORD[win+0xaf] = state COUNT (t323 field map,
re-cited). Live BatModeWnd record 20/20 saves: [+0xab] TABLE PTR = NULL, [+0xad]=0,
[+0xaf]=0, [+0xb1] STATE = 0.
=> With count=0, fn 0x31f30 can only pass bounds for si < 0 (si=-1 -> skip-old-clear leg
   0x31f5e..0x31f86 -> store -1); ANY state id >= 0 trips the vendor assert BEFORE the
   store @0x31faf. The state word is unswitchable by the setter EVEN IF fn 0x32100 were
   in the class table (it is not — t323/t296; fresh E8-census re-verified: callers of
   0x31f30 = {0x321ad, 0x3221b} only, both inside fn 0x32100).
Sibling writers same gate shape: fn 0x33b34 (dec) 0x33b3b cmp si,[eax+0xaf] else assert
0x8f2/0x1909; fn 0x33b88 (inc) double-check 0x33bb6 cmp ax,[ecx+af]; jl else assert
0x904/0x1927. All dead against count=0.
fn 0x33c34 (installer [win+0xab]=edx; [win+0xaf]=cx; [win+0xb1]=strlen-1 pattern) sole
E8 caller 0x5597f = INSIDE the windows.txt window-constructor chain (fn 0x575e4; the
record at esp+0x28 is being built: rect fields +0xc/+0x14/+0x4/+0x45/+0x63 written
immediately before) => CONSTRUCTION-TIME only, never a runtime trigger.
fn 0x364d2: ZERO E8 callers (class-table member or dead) — re-verified fresh.
Cycler family fn 0x339a4/0x33b34/0x33b88 callers ALL inside fn 0x3377c..0x33ca5 (the
char-input cycler module; t323: BatModeWnd has NO char handler in its cited msg tree).
