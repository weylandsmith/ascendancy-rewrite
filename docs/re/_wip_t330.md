# t330 WIP — MOUSE-DIMS DRAW-CAPTURE (executing the t328 S4 design)

Assigned: docs/STATE.md NEXT ACTION t330. Design VERBATIM at
docs/re/_wip_t328.md S4. Question: for mouse.shp records k5/k6/k7, does the
vendor blit read dims from rec+0 (u16 pair 46x77, walk EXACT-H) or from the
canonical u32@+0x10 slot (zero component -> -1 refuse)?

## S0 PREFLIGHT FACTS (measured this session)
- Sitting check NEGATIVE: playcap tail-seek newest turn 1086 (8.46 GB file,
  tail-only read per OOM law). Production :9 pids 136357/136359 alive
  11:19+ — UNTOUCHED.
- work/r1/bin/dosbox-x-dbg present; venv python PIL ok; port 55999 free.
- LEGS (r299, 61 entries) + new legs last-4 collision audit PASSED:
  blit_entry 0x5CAAC -> lin 0x21BEFC (BEFC), blit_refuse 0x5CB2B -> BF7B,
  blit_deref 0x5CB59 -> BFAB — all unique vs all 61 existing and mutually.
- mouse.shp = extracted/ascend01/data/mouse.shp, 10435 B, magic 1.10,
  count 0x0c at +8, dir u64 from +0x10; k5 0x14a7 / k6 0x1cb5 / k7 0x24c3,
  spans 2062/2062/189 (k7 span differs from the t328 note's "2062 each" —
  MEASURED 189; t328 S1 GROUP E said span 2062 each: correction banked,
  k7 dir-span = 189 bytes; header/dims facts unchanged: u16@+0 = 46x77).
- Blit asm re-verified raw (t328 S1b): at 0x5cb59 (stop, instr NOT executed):
  ebx = shape struct = [ebp+8] (0x5cabc mov ebx,[esi] where esi=[ebp+8]);
  args [ebp+0xc]=payload base, [ebp+0x10]=selector u32 (S12 arg map).
  Dims gate reads [ebx+4]/[ebx+8] as i32, +1 must be > 0.
  Directory: entry_rel = u32[payload+8+8*sel] (0x5cb4d..0x5cb56); shape
  struct = payload + entry_rel; stream = shape+0x18.
- CACHE SLOT LAW (shp.md S12.2/S12.4 + r1_shp_ramtable.py): runtime cache
  ctx linear 0x2e1194; slot payload ptr u32 = u32[0x2e1194 + 4*idx]; buffer
  verbatim file copy at PAY+0x88 (magic '1.10'); size u32 =
  u32[0x2e1194+0x320+4*idx]. => slot idx = (PAY - 0x2e1194)//4 directly.
  NAME region ctx+0x7d0+idx*0x32 (S11).
- Panel buttons (windows.txt rects, window-rel == screen px per t250 law
  XOFF/YOFF handled by xsend path used by r293 click()): STATUS 474,130-
  632,160 -> (553,145); FLEET -> (553,184) [t308 verified]; RESEARCH ->
  (553,223) [r1_wp_session verified const]; SPECIALAB 474,247-632,277 ->
  (553,262); Intelligence 474,303-632,333 -> (553,318); RACES 474,286-316
  -> (553,301). RACES may be the race-status screen (diplomacy substitute).
- REFUTED scan: no blit/draw-capture route refuted for these 3 addresses
  (grep windows: only the 2024-era row-blit note, unrelated).

## S1 TOOL SHAPE (scripts/r330_blit_session.py)
Subclasses r1_dbg_session.DbgSession. Adds LEGSPEC hot=True entries for the
three blit legs (t302 re-arm law: hot legs stay armed in census mode).
PANEL phases = census_click(button, phase, window) then escape_to_map.
bank_stop override: AFTER super() (which banks regs + ret_stack), if leg is
blit_deref: dump 0x20 shape struct at ebx (dims i32 @+4/+8 + dir fields),
dump 0x90 payload head at [ebp+0xc] (verbatim copy at +0x88), compute slot
idx, dump 50 B name at 0x2e1194+0x7d0+idx*0x32. Attribution records ->
blit_attrib.json (phase-tagged). blit_refuse stops: dump shape struct at
ebx too (the -1 dims witness).
Verdict offline: scripts/r330_analyze.py — matches shape structs + payload
heads against extracted library files; counts census; applies the S4 verdict
grammar (refuse-attributed-to-mouse => canonical-slot law holds; 46x77
draw-attributed-to-mouse => u16@+0 holds; no mouse-attributed blit any phase
=> honest negative, k5/k6/k7 join UNREACHABLE class).
Expectations for the RUN itself (positive controls only; the mouse verdict is
post-hoc so a failed expectation never wastes the banked data):
  blit_entry>=1 (draws happen at all), btn_hdlr>=1 (clicks land).

## S2 RUN LOG
ATTEMPT 1 (run work/r1/dbg-t330-20261107-073530, rc=0 banked, thin):
preflight OK (raw bytes at 0x5caac=55 8b ec.., 0x5cb2b=b8 ff ff ff ff..,
0x5cb59=8b 36 03 75 0c..); campaign ENTERED (t=1086, ring 30 ships, base
B=0x1BF4D8 verified); 6 census windows armed around real clicks at
windows.txt bar rects STATUS/FLEET/RESEARCH/SPECIALAB/RACES/Intelligence
(553,145/184/223/262/301/318) + baseline + edges.
MEASURED: (1) blit_entry fired EXACTLY ONE STOP PER PANEL WINDOW
(status/fleet/research/specialab/races/intel 1 each; baseline 0, edges 0);
whole-log census {blit_entry:6, blit_refuse:0, blit_deref:0}. ALL SIX share
ret0=0x64aa6 (call site 0x64aa1; bytes at 0x64aa6: 83 c4 14 = cdecl
ADD ESP,0x14 five-arg cleanup — generic 5-arg blit consumer, NOT the widget
0x31467 site). (2) MY ATTRIBUTION HOOK WAS DEAD: DbgSession COMPOSES
L.Sess (self.s); overriding bank_stop on the wrapper subclasses nothing —
banked hits carry regs+ret_stack only, no hdr/lib dumps. analyze rc=2.
(3) CACHE CTX LAW CORRECTION: guest ctx = B + 0x9F10C is WRONG for the
.sav path — the ck113 absolute 0x2E1194 IS the ctx in this run too (B is
deterministic 0x1BF4D8; 0x25E55C scan = garbage). Registry word 0xFFFFFFFF
(nonzero = live, S11.2). Registered slots: raceflag, listbox, 1STARMAP.SHP,
1starmap.tmp. (4) DECISIVE POSITIVE: MOUSE.SHP VERBATIM COPY PRESENT at
sav-linear 0x2EC0C4 (64-B head match + FULL 10435-byte match) — the library
IS loaded in this save state (absent from ck113 autoplay inventory).
(5) deref never fired even armed across all windows; entry-stop BPDEL+RUN
lets the in-flight blit pass deref un-stopped (heavy-check does NOT re-enter
mid-block after RUN — mechanism [unverified], but empirically entry-leg
stops consume the window). ATTEMPT 2 DESIGN: legs WITHOUT blit_entry
(refuse+deref+btn_hdlr) so the guest runs through the gate and stops AT
deref mid-blit (t306 mid-block precedent); attribution hook moved to the
Sess instance (monkey-patch s.bank_stop).

## S3 VERDICT [MEASURED, run work/r1/dbg-t330b-20261107-080216]
Census {blit_deref:15, blit_refuse:0, blit_minus2:0, btn_hdlr:10}; 8
attribution rows banked (rec_head 32B matched against extracted libs).
PHASE-TAGGED MOUSE STOPS 4/4 (status#0 k2, fleet#0 k0, research#0 k0,
specialab#0 k0): runtime hdr (W-1,H-1) == FILE (u16@+2, u16@+0) of the
matched record, and NEVER the u32@+0x10 pair (k0: hdr (11,15) = (+2=11,
+0=15); +0x10 (10,14) rejected). => DRAW-TIME DIMS SLOT = rec+0 u16 PAIR,
ORDER [H-1 at +0, W-1 at +2]. mouse.shp is drawn EVERY right-bar panel
open (k0 = button glyph, drawn at the button rect x,y 553,184/223/262;
k2 at 8,8). blit_refuse fired ZERO times across all phases: the vendor
never refused a dims blit in captured UI.
post-rearm rows (pixptr 0x2f2af8, hdr 639x479 full-screen shape) are a
cascade artifact mid-BPDEL/RUN — EXCLUDED from the verdict (different
shape, dims match neither candidate).
CONSEQUENCES: (1) C27-C29 (mouse k5/k6/k7) 'invalid dims' classification
REFUTED — u16@+0 (46,77) = H=47 x W=78 VALID dims under the measured law;
(2) k5/k6/k7 still never SELECTED by windows.txt (CURSORSHAPE 2 = plain
arrow, L216/L1186) => drawn-frame witness for THOSE records remains
impossible, but the slot-location DISPUTE is closed by measurement for
the mouse library; (3) the dims-slot question for the OTHER 1.10 libs:
measured law holds for mouse k0/k2; generalization to all libs is
[inferred], corpus spot-check u32@+0x10 == (u16@+2-1, u16@+0-1) fails
1526/1567 records (the +0x10 pair is a DIFFERENT quantity, often the
same-order raw dims, e.g. 14intel k5 (6,5)@+0 vs (5,6)@+0x10).
(4) TOOL LAWS banked: entry-leg stop CONSUMES the census window (heavy
check does not re-enter mid-block after RUN — deref never fires once
entry is armed: run 073530 entry-armed vs 080216 deref-armed);
DbgSession COMPOSES Sess -> instance-patch s.bank_stop; cache ctx =
0x2E1194 ABSOLUTE in .sav (P0+0x9F10C wrong for .sav); mouse PAY
0x2EC03C lives OUTSIDE the 200-slot cache (gsystem path) — attribute by
rec_head bytes, not slot name; verbatim copy at PAY+0x88 confirmed.
