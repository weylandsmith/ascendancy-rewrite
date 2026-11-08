# _wip_t344 — MOUSE-CURSOR DRAW-WITNESS (OQ-005) — working notes

## S0. Setup
- Sitting check NEGATIVE: tail-seek newest live-timeline turn 1086 == corpus
  (file grew only from production session writes). No r1_t85g_sitting.py run.
- game/ read-only; production :9 never signalled so far.

## S1. SELECTOR FOUND (static, zero capture) — the MOUSE.SHP open+set chain
Whole-image disasm work/r331_disasm.txt + artifacts/ascend_restored.bin.

1. t328's "zero u32 refs to MOUSE.SHP" was the WRONG SCAN. Pool-relative
   immediate law (OQ-004 CLOSED, docs/re/datafiles.md): imm = str_off -
   0x82BB0. String 'DATA\MOUSE.SHP' is at payload offset 0x84314 (sole
   verbatim occurrence, scripts/r344_mouse_refs.py exit 0), so the imm to
   hunt is 0x1764, NOT 0x84314. Scan of the whole image: exactly ONE code
   site holds u32 0x1764 and ZERO hold 0x84314 — the t328 negative is fully
   explained, the referrer IS an immediate.
2. THE OPENER: fn 0x309d4 (file bytes verbatim):
   - guard: ds:0x484cc != 0 (0x309e0) AND [obj+0x733]==0 lazy-open (0x309e9)
   - 0x309f9 `mov edx,0x1764` ; 0x309f4 `mov ebx,0x200` ; eax=esp buffer
     -> call fn 0x20728 (name open), then fn 0x207ac, fn 0x20acc; result
     handle STORED [esi+0x733] (0x30a15); assert on null: ebx=0x2b3(691),
     edx=0x1773 -> '..\gsystem.cpp' (verified string at 0x84323) — so this
     lives in gsystem.cpp.
   - 0x30a41: edx=[esi+0x737], eax=[esi+0x733] -> call fn 0x64ea9 (shape
     select/lookup on the MOUSE.SHP library; [obj+0x737] = current index).
   - fn 0x3095c (sibling) is the teardown: frees [esi],[esi+0x10],[esi+0x73b]
     — [0x733] NOT freed there (persistent library).
3. THE SETTER: fn 0x5a1e4 (t322's "cursor chooser callee"):
   eax=core obj; gate [core+0x24da4] (THE t319 mouse-active flag) != 0 AND
   ecx != -1 -> `mov eax,0x484f8; call fn 0x30a60` (0x5a1f9..0x5a1fe).
   fn 0x30a60: esi:=edx, ecx:=ebx; ebx==0 -> ecx := [eax+0x733] = the
   MOUSE.SHP handle verbatim. Callers: 0x1be54 (fn 0x1be10, eax=0x7a35c,
   ecx=ebx=0, edx=shape id), 0x1b7aa, 0x27c3b, 0x27cab, 0x28c6d, 0x28d44,
   0x547a6.
4. THE CHOOSER: fn 0x1be10 (verbatim): fires iff [eax+0x41]==ds:0x7d35e
   (ACTIVE window); bl=[win+0xb7]; edx=[win+0xb8]; bl==1 -> edx+=8;
   bl in {2,3} -> edx+=6; [win+0xaf]!=0 -> edx+=1; then fn 0x5a1e4. So the
   cursor shape id = [win+0xb8] + {0,6,8} (+1) — window-mode-keyed.
5. NOT the cursor: the dispatcher at fn 0x5a208..0x5a3ed (jump table
   cs:[0x45694], cmp ax,0x13) resolves '.tmp' screen names
   ('DATA\1starmap.tmp' @0x863a2 direct; 'DATA\3cfgnew.tmp' 0x3804,
   '7racesel' 0x3815, '8shipdes' 0x3827, '9ENDGAME' 0x863e9, '12start'
   0x384b, '13negot' 0x385c, '16battle' 0x386d, '20res' 0x387f,
   '10status' 0x388e pool-relative) via fn 0x1fe20 (name->id, pool
   ds:0x9f10c) then fn 0x1fc34 + BLIT fn 0x5caac (push 0x4850c) — a
   .tmp-screen blitter, NOT mouse.shp. (Noted so nobody re-hunts it.)

## S2. DIMS-LAW RESOLUTION (static, zero capture) — the t328 "dispute" dissolves
work/r331_disasm.txt verbatim + scripts/r344_dimslaw.py over
extracted/ascend01/data/mouse.shp (10435 B = t330's banked copy size):

1. THE GEOMETRY QUERY the cursor chain uses is fn 0x64ea9 -> fn 0x61058 /
   fn 0x6108c (0x61058 verbatim 0x61072..0x61083):
       W = u32[rec+0x10] - u32[rec+0x8] + 1
       H = u32[rec+0x14] - u32[rec+0xc] + 1   (returned (W<<16)|H)
   fn 0x64ea9 caches: ds:0xa2090=W, ds:0xa20cc=H, ds:0xa20a0=W*H,
   ds:0xa20b0=int32[rec+8], ds:0xa20b4=u16[rec+0xc] (hotspot), memoised on
   (lib,idx) via ds:0xa208c/ds:0xa2074.
2. FILE-vs-FORMULA TABLE (TOC = u32 @8+8*i verbatim, rec = lib + [TOC];
   k0@0x68 / k2@0x257 reproduce t330's witnessed offsets):
   idx:  W,H from bbox-difference; u16 pair+1 = (W,H) at (+2,+0)
     0: 12,16 / (12,16)  [CORRECTION t344 re-check: first draft of this
        table said bbox 12,15 — arithmetic slip; i32@+c=-1, i32@+14=14 ->
        H=14-(-1)+1=16. ALL 12 RECORDS AGREE 12/12.]
     1: 27,23 (27,23)   2: 17,17   3: 17,17
     4: 78,47 (78,47)   5: 78,47   6: 78,47   7: 78,47
     8..11: 17,17 each
3. K5/K6/K7 ARE NOT JUNK AND HAVE NO ZERO-DIMS SLOT. t328 read only
   u32@+0x10/+0x14 and saw (0,46)/(77,0)/(0,0) "zero component" — but the
   canonical slot is a SIGNED bbox PAIR: k5 = (-77,0,0,46), k6 = (0,-46,77,0),
   k7 = (-77,-46,0,0) (i32 at +8/+c/+10/+14). Difference law gives 78x47
   for ALL of k4..k7 — identical to k4's (0,0,77,46). The four records are
   corner-anchor variants of ONE 78x47 glyph (walk op-counts identical
   1987 for k5/k6/k7; k4 stream 2038 B = t328's EXACT-H stream).
   => dims-SLOT-LOCATION dispute CLOSED for the mouse lib by static law +
   t330's live gate witness (gate = u16 pair at hdr+4/+8 = file u16@+2/+0,
   inc-then-jle at 0x5cabe..0x5cacd; bbox = positioning/clipping).
   Both slots valid; neither is "the" dims slot — they serve different
   consumers. ShapeLibrary.decode needs BOTH readings: gate W-1/H-1 pair
   AND bbox hotspot.
4. (Retired: the "k0 mismatch" first-draft claim was an arithmetic slip in
   THIS file, corrected at S2.2 — bbox and u16-pair readings agree 12/12.
   Logged here so a later session treats the pair-law as unbroken.)
5. SELECTOR SEMANTICS verbatim (fn 0x5a1e4 re-read): call fn 0x30a60 fires
   iff NOT(mouse-active [core+0x24da4]) OR ecx==-1 (i.e. shape updates are
   SUPPRESSED while the mouse is held — fn 0x1be10 passes ecx=0 so the
   chooser updates only in mouse-quiet passes). fn 0x30a60 callee: ebx==0 ->
   lib := [eax+0x733] with eax=0x484f8 (gsystem obj, NOT the 0x7a35c core —
   fn 0x5a1e4 overwrites eax at 0x5a1f9); asserts at 0x30a74 (lib null) /
   0x30a89 (id<0) on '..\gsystem.cpp'; then fn 0x64ea9(lib,id) and returns
   -1. THE REQUEST POINT for census = 0x30aa7 (call fn 0x64ea9; eax=lib,
   edx=shape id).
6. CHOOSER ARITHMETIC (fn 0x1be10): id = [win+0xb8] + (bl==1 ? 8 : bl in
   {2,3} ? 6 : 0) + ([win+0xaf]!=0), fires iff [win+0x41]==ds:0x7d35e.
   => k5/k6/k7 reachable iff some active window carries [win+0xb8] in
   {4,5,5+ctl,6(+6? no: 0+6=6 mode2),0+6+1=7...}. Concretely: id5 needs
   b8=5 (mode0) or b8=4+ctl; id6 needs b8=6 (mode0) or b8=0 in mode2/3;
   id7 needs b8=7 or b8=6+ctl or b8=0+ctl in mode2/3. windows.txt
   CURSORSHAPE values decide (t328: only 2 on cosmos L216 + BatModeWnd
   L1186 — full value census pending below).

## S3. THE COMPLETE SELECTOR LAW (static, verbatim) — k4..k7 ids are the
## mouse-mode words; cited proof chain for the OQ-005 dims dispute

1. fn 0x54650 (per-pass mouse pass, core=eax):
   - BUTTON-HELD arm 0x54687..0x546b4: iff ds:0x484ac!=0 (BIOS button word,
     t319 law) AND [core+0x24da4]==0 AND [core+0x489e]==0 ->
     edx=1, eax=0x484f8, ebx=0, call fn 0x30a60 => MOUSE.SHP shape 1
     (button cursor); THEN sets [core+0x24da4]=-1 (mouse-active flag).
   - RELEASE arm 0x546b6..0x546d6: iff flag!=0 AND button==0 -> edx=0,
     call fn 0x30a60 => shape 0 (arrow), clears flag (0x546d0).
2. Mode chain 0x54741..0x547a6 (same core; edx = key scan code, ebp =
   ds:0x484ec key/click record):
     mode 0 <- edx==0        && ds:0x484ec==0      (0x5474f)
     mode 1 <- edx==0        && ds:0x484ec==0x27f  (0x5475b)
     mode 2 <- edx==0x1df    && ds:0x484ec==0      (0x54774)
     mode 3 <- edx==0x1df    && ds:0x484ec==0x27f  (0x54783)
     else   -> NO update, exit at 0x54788.
   On CHANGE (eax != [core+0x24da8]): store, then
   edx = (mode==-1 ? 0 : mode+4)  (0x54790..0x5479d) -> fn 0x5a1e4.
   => IDS 5,6,7 ARE PRODUCED VERBATIM AS mode+4 FOR mode {1,2,3}; id 4 =
   mode 0. THE t344(a) SELECTOR IS FOUND, cited, and its ids align exactly
   with mouse.shp records k4..k7 (the 78x47 quartet of S2).
3. fn 0x5a1e4 gate (0x5a1e8..0x5a1f7): calls fn 0x30a60 iff
   [core+0x24da4]==0 OR ecx==-1. Both callers above pass ecx=0, so shape
   updates flow only while the mouse is NOT held.
4. fn 0x30a60(eax=obj 0x484f8, edx=id, ebx=0 -> lib:=[eax+0x733]) ->
   fn 0x64ea9(lib,id) geometry query at CALL SITE 0x30aa7. fn 0x64ea9
   memoises on (ds:0xa208c=lib, ds:0xa2074=id) and computes via fn 0x61058
   / fn 0x6108c: W=u32[rec+0x10]-u32[rec+0x8]+1,
   H=u32[rec+0x14]-u32[rec+0xc]+1, area->ds:0xa20a0,
   hotspot int32[rec+8]->ds:0xa20b0, u16[rec+0xc]->ds:0xa20b4.
   Pixel consumers of those globals: fn 0x6485c / fn 0x64ade (refcount-0
   transitions from fn 0x64e3a/0x64e76) + fn 0x656ca / fn 0x65cc3 families.
5. FILE MEASUREMENT (S2.2): k4..k7 ALL yield W=78 H=47 under the vendor
   formula. t328's "zero-component canonical slot" was reading ONE half of
   a signed bbox PAIR (k5=(-77,0,0,46), k6=(0,-46,77,0), k7=(-77,-46,0,0))
   — hotspot anchors, not dims. t330's LIVE witness (dims gate reads the
   u16 pair @hdr+4/+8 = file +2/+0, inc-then-jle 0x5cabe..0x5cacd) holds
   for the same records. CONCLUSION: both slots are real and serve
   different law consumers; the dims-SLOT-LOCATION dispute for the mouse
   library is CLOSED by static law + file measurement + t330's live gate
   evidence. NO rewrite code change (shp.cpp dims reading stays per the
   t330 generalization bound — other libraries still need their own
   witnesses).
6. LAUNCH DECISION: static law names the census point (call site 0x30aa7 /
   fn 0x64ea9 entry) and the expected ids. ONE launch armed at fn 0x64ea9
   entry to census live (lib,id) pairs upgrades "static predicts" to "live
   witnessed". Pixel-level DRAW-CONTENT witness for k5/k6/k7 stays
   capture-limited if the mode ids never fire — mode reachability needs
   ds:0x484ec==639 (t318 measured 0x1ff, never 0x27f) or scan 479, so the
   honest expectation is ids 0/1/4 only. If ids 5..7 fire zero, the class
   becomes capture-limited and the row says so.

## S4. Launch state (t344(b))
- Tool scripts/r344_cursor_session.py (composes r330 BlitSess; leg cur_req =
  file 0x30AA7 `call 0x64ea9` — payload bytes verified e8 fd 43 03 00,
  unique 1x; preflight rc=0; port 55999 free; last-4 collision ok vs
  blit_deref 0x5CB59 + btn_hdlr 0x336b4).
- CORNER SEMANTICS REFINED (disasm verbatim 0x5473b..0x54783, reading
  ds:0x484f0 = cursor Y, ds:0x484ec = cursor X):
    mode 0 <- (y==0,   x==0)   TL  -> id 4; k4 bbox (0,0,77,46) anchor TL
    mode 1 <- (y==0,   x==639) TR  -> id 5; k5 bbox (-77,0,0,46)  anchor TR
    mode 2 <- (y==479, x==0)   BL  -> id 6; k6 bbox (0,-46,77,0)  anchor BL
    mode 3 <- (y==479, x==639) BR  -> id 7; k7 bbox (-77,-46,0,0) anchor BR
  THE FOUR RECORDS ARE ONE 78x47 GLYPH ANCHORED AT THE FOUR SCREEN CORNERS —
  the signed bbox pair IS the anchor, hotspot law = fn 0x6108c. Gates before
  evaluation: [core+0x24da4]==0 (mouse quiet) AND [core+0x489e]==0 AND
  distinct-group count ([core+0x4226]>>16)!=0 (t337 word).
- Click plan (launch 1, superseded by the launch-2 calibration in
  scripts/r344_cursor_session.py): root clicks outside the content;
  control = STATUS bar button (t330 k0 drawer) + pip enter-system.
  Outputs: work/r344_session.out (launch 1), work/r344_session2.out,
  run dirs work/r1/dbg-t344-*, dbg-t344r-*, dbg-t344c-* (failed),
  dbg-t344d-* (the WITNESS run, S5).

## S5. LIVE WITNESS RESULT (launch t344d, attempt 1 rc=0, run
## work/r1/dbg-t344d-20261108-161132) — SELECTOR WITNESSED, PIXEL DRAW NOT
- PTY whole-log census {cur_req:4, mode_upd:2, blit_deref:7, btn_hdlr:1}.
- cur_req rows (all lib_ptr 0x2EC03C = the verbatim MOUSE.SHP base t330
  found; rec_rel resolves to the FILE TOC offsets byte-exactly):
    16:13:55 id 4 rec 0x48b  <- right after root click (0,0)   = TL corner
    16:14:00 id 0 rec 0x68   <- release arm (fn 0x54650 0x546d6 path)
    16:14:34 id 5 rec 0xc99  <- right after root click (799,0)  = TR corner
    16:15:12 id 0 rec 0x68   <- c_bl window release
  => THE CORNER SELECTOR LAW IS WITNESSED LIVE: clicking the top-left edge
  makes the vendor request mouse.shp k4 (TL anchor 0,0), top-right requests
  k5 (TR anchor -77,0). Launch 1 (root 788 -> guest ~630) fired NEITHER —
  the guest must be AT the exact edge value, corroborating the cmp law.
  ids 6/7 (bottom corners) not reached: the t285 title-eject law stopped
  the sweep (bottom-edge clicks at (0,599) fell in the pre-check after a
  title re-entry; honest negative for BL/BR requests, mechanism identical).
- mode_upd leg: pty log shows 2 FIRING lines attributed (census counted 2)
  but bank_stop attribution returned leg=None for them (attribute()
  compares eip == P0+LEGS[name]; the fires' eip landed elsewhere —
  re-arm-gap renders, t305 law class). Zero banked mode rows; the cur_req
  evidence stands alone.
- blit_deref rows banked sel=0 (k0, u16@0 (15,11) = t330 law reproduced)
  and sel=2 (k2 16x16) during corner clicks; NO deref at k5/k6/k7 offsets
  -> the 78x47 corner glyph is NOT drawn through FUN_0005caac in this
  corpus; pixel-level draw-content for k5/k6/k7 = capture-limited class.
- TOOL FIX LANDED (scripts/r1_dbg_session.py teardown): SIGKILLed Xvfb
  leaves /tmp/.X<d>-lock + socket; later attempts die "Server is already
  active" (cost t344c both attempts). Teardown now removes the lock only
  when its pid == the pid it killed (verified: t344d att1 teardown line
  "removed stale X97 lock+socket (owner==killed pid)").
