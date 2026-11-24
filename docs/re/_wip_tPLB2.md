# tPL-B2 — PRODUCTIVITY-BOX POPUPS (D26) — WIP

Task (STATE.md NEXT 2026-11-24): clicking a top-row productivity indicator
(PLIND/PLPRO/PLPOP) pops an info window. Witness text verbatim:
"Crimea 1 / Prosperity: 1 per day / Population will grow in 50 days"
(/ = line break). Derive templates + values law from windows.txt/string
table; port all indicator boxes; CLOSE = live witness of each popup.

Sitting check ran FIRST: playcap tail 45/46/47.sav all turn=1086 (wall
~03:04, production dosbox-x pid 1623906 alive) — no new sitting, stale
assignment stood.

## P1 — windows.txt indicator widgets [verified]
extracted/ascend00/windows.txt: children of PLANETALLOC —
 - PLIND  X0 123 Y0 7   X1 230 Y1 106  SENDMESSAGE 50 PARAM1 1 HELP plind
 - PLPRO  X0 239 Y0 7   X1 346 Y1 106  SENDMESSAGE 50 PARAM1 2 HELP plpro
 - PLPOP  X0 355 Y0 7   X1 454 Y1 106  SENDMESSAGE 50 PARAM1 4 HELP plpop
 - PLRES  rect 7,7..114,106 SENDMESSAGE 50 PARAM1 0 (planets-ui §2 key 0)
 - PLBUILD X0 463 Y0 8  X1 632 Y1 106  SENDMESSAGE 51 PARAM1 1
planets-ui.md §2 selector law: widget byte +0x47 (=SENDPARAM1) with remaps
4->3 and SENDMESSAGE==51->4 gives keys 0..4 = PLRES/PLIND/PLPRO/PLPOP/PLBUILD.

## P2 — STRING TEMPLATES [verified, extracted/ascend00/static.txt]
getter(n) == nth quoted string of static.txt (getter law CLOSED t96,
docs/re/aicode.md: getter 0x21a20, table img 0x10ba8, count ds:0x12e0c).
 - #99  "%s %s: %d per day"          (static.txt:293)
 - #100 "%s will %s in %d day%s."    (static.txt:296)
 - #96  "Owned by |%d|%s"            (static.txt:284)
 - #97  "Maximum Population  %d"     (static.txt:287)
 - #98  "Self Managed"               (static.txt:290)
 - #70  "Prosperity"  #71 "Population"  #72 "grow"  #73 "%s is not growing."
 - #28 "" / #29 "s"  (plural suffix, plural arm 0x3e560..0x3e576)

## P3 — POPUP BUILDER located (restored image 0x3e3c0..0x3e5db, GAP fn)
Raw disasm (objdump, work/ascend_restored.bin). Sequence per line: push
args, getter(n), push fmt, push buf (ebp-0x9e, 0x76c79=sprintf t96), then
0x2fb38 with eax=0x7d3a2 (display object), ebx = hold ticks:
 - L-A 0x3e3cc: sprintf(buf, getter(96) "Owned by |%d|%s",
        raceIdx(0x12e18[star-owner stride law]*4+0x13), ebp+0x42)  hold 0x5a
 - L-B 0x3e432: sprintf(buf, getter(97) "Maximum Population  %d",
        u16[planet(0x43508)+0x4a])  hold 0x78
 - L-C 0x3e47a: IF planet[+0x57]==player(0x7458e) && planet[+0x5a]==0xffff:
        0x2fb38(buf, getter(98) "Self Managed", ebx=0x96)
 - L-D 0x3e4db: IF [ebp+0x72]!=0: sprintf(buf, getter(99)
        "%s %s: %d per day", planet+0x24 (NAME), [ebp+0x72] (indicator
        word ptr), u16[ebp+0x7e])  hold 0xf
 - L-E 0x3e530: IF [ebp+0x6e]!=0: if u16[ebp+0x7a]==0xffff -> sprintf(buf,
        [ebp+0x62] fmt, [ebp+0x5a]); else sprintf(buf, getter(100)
        "%s will %s in %d day%s.", [ebp+0x5a], [ebp+0x6a],
        u16[ebp+0x7a], getter(28|29) plural from u16[ebp+0x7a])  hold 0x50
 - tail 0x3e5bf: if [ebp+0x76] && u16[[ebp+0x76]+0x6b] -> call 0x314a8(0)
planet record base 0x43508 = DAT_00043508 (current planet record; +0x24
NAME per aicode, +0x4a max pop u16, +0x57 owner byte, +0x5a governor).
=> L-D is the "Crimea Prosperity: 1 per day" line; L-E the grow-in-N-days
line. OPEN: function entry + who sets ebp struct fields +0x5a/+0x62/
+0x6a/+0x6e/+0x72/+0x76/+0x7a/+0x7e, and the msg-50 click arm that calls
this builder.

## P4 — POPUP BUILDER ENTRY + CASE LAW [verified, GAP fn entry 0x3db80]
Prologue: `push ebp; mov esp,ebp; sub 0x21c,esp; sub 0x82,ebp` — the
callers' frame convention passes the widget in EAX -> [ebp+0x76]. Window
ops 0x55240(0x7a35c, w+4), 0x5e940(w+4, 0xf2), shape 0x1fc34(0x9f10c,
WORD[0x6fd8e],0,0,0), 0x5caac copies the 20-byte widget record to
ebp+0x2e; derived anchors ebp+0x32=w[8]+10, +0x36=w[0xc]+10,
+0x3a=w[8]+0x145, +0x3e=w[0xc]+0xcf; the 20B record + 0xff flag are then
copied to the DISPLAY object 0x7d3aa/0x7d3be (queue consumer).
Fields zeroed: +0x72 (indicator-name str), +0x5a, +0x6a, +0x62, +0x6e,
+0x7e; +0x7a = 0xffff (countdown sentinel).
DISPATCH 0x3dc59: `jmp *%cs:0x28fb8(,dword[0x74528],4)` after `cmp $4; ja
0x3e4db` (key>4 = no indicator lines). ds:0x74528 = THE INDICATOR KEY,
written ONLY at 0x3d811 (`mov -0x28(%ebp),%eax; mov %eax,0x74528; mov
-0x1c(%ebp),%ax; mov %ax,0xab(%widget)`) — the msg-50 arm 0x3db26
(`cmp $0x32,%dx; je 0x3d80b`) of the PLANETALLOC message handler (msg
dispatch band 0x3db06/0x3dad2: dx=50 -> store key+cell; the builder runs
on the repaint, invoked through a RELOCATED jump table — image bytes at
0x28fb8 are code, t43/planets-ui §2 law, so static callers are invisible
BY LAW, not by failure).
CASE BODIES (recovered from the branch bodies; key->entry mapping per
windows.txt SENDPARAM1 semantics 0=PLRES 1=PLIND 2=PLPRO 4=PLPOP):
 - 0x3dc61 RESEARCH (PLIND): +0x72=getter(65)"Research", +0x7e=
   u16[planet+0x46] (research/day); dx=WORD[0x76492+2*ownerRace]; if
   dx<0xffff: +0x6e=-1, +0x5a = tech-name ptr 0x74746+75*dx (RESTREE
   stride-75 law, OQ-013), countdown +0x7a = 0x47010(0x46de0(0x74744,
   race) leg, WORD[0x764a0+2*owner] + WORD[0x74782+...] leg);
   +0x6a=getter(66)"be discovered", +0x62=getter(67)"No progress is being
   made on %s."
 - 0x3dd17 INDUSTRY (PLPRO->? see NOTE): +0x72=getter(68)"Industry",
   +0x7e=u16[planet+0x44] (industry/day); build item =
   u16[planet+0x52] via planet[+0x10] cell array; if item byte <0xff:
   +0x5a = item NAME 0x73e40+40*item+0xa (planitem names); if item==0x17
   (23, Ship) sprintf 0x1fea appends race name (0x396cc); countdown
   +0x7a=0x47010(0x47010-legs(0x44,0x50)); +0x6e=-1;
   +0x6a=getter(69)"be completed", +0x62=getter(67).
 - 0x3ddc0 PROSPERITY: +0x72=getter(70)"Prosperity", +0x7e=
   u16[planet+0x48] (prosperity/day), +0x5a=getter(71)"Population",
   +0x6a=getter(72)"grow", +0x6e=-1; if u16[planet+0x42] (pop) <
   u16[planet+0x4a] (maxpop): +0x7a = 0x47010(u16[+0x48] pros,
   u16[+0x4e], [0x66e4]) and if !=0xffff draw L-D+L-E; if countdown
   0xffff: +0x62=getter(73)"%s is not growing."; if pop>=max:
   +0x62=getter(74)"%s has no more room to grow."
   *** THIS IS THE USER WITNESS PATH: L-D "Crimea Prosperity: 1 per day"
   + L-E "Population will grow in 50 days." (user's "Crimea 1" = the
   planet NAME string itself carries the numeric suffix — names.txt
   duplicate-suffix class; template #99 has exactly 3 args.) ***
 - 0x3de5a SQUARE case (PLRES click w/ cell selected): if
   widget+0xab>=planet+0x18 -> getter(83)"Orbital" branch; item name
   0x73e40+40*item+0xa, Ship 0x1fea+race, "Automated " getter(84) vs
   0x1ff2 on cell byte &2, getter(85)" on %s Square", build-progress
   getter(86)"No progress"/getter(87)"%d day%s until completion" via
   0x394d8+0x47010; surface-colour descriptions getter(75..83) WHITE/
   BLACK/RED/GREEN/BLUE + "industry"/"industry"/"research" modifiers +
   0x3df1f Orbital tail.
 - 0x3e2c8 FULL-INFO chain (planet-header click): line0 = planet+0x24
   name ALONE (hold 0xf); getter(94)"%s %s Planet" via size tables
   0x74540[planet+0x16] / 0x7452c[planet+0x14] (hold 0x3c); owner name
   (getter(95)"No One" if +0x57==0xff else race name 0x74590+20*
   race(0x12e17)) then L-A getter(96)"Owned by |%d|%s" (hold 0x5a),
   L-B getter(97)"Maximum Population  %d" u16[+0x4a] (hold 0x78), L-C
   getter(98)"Self Managed" iff owner==player && governor +0x5a==0xffff
   (hold 0x96), then L-D/L-E if set.
0x2fb38(display 0x7d3a2, edx=0, ecx=line, ebx=HOLD ticks, 2, -1, -1, 0) =
THE LINE-PUSH PRIMITIVE (Corn popup queue; hold values observed
0xf/0x3c/0x5a/0x78/0x96/0x50/0x32/0x14).
0x47010 = countdown/division helper (u16 legs; 0xffff = "no progress").
TAIL 0x3e5bf: if [ebp+0x76] && u16[[ebp+0x76]+0x6b] -> 0x314a8(0) (sound?
SFX channel op) — NOT modelled.

## P5 — msg-50 TRIGGER LAW [verified]
PLANETALLOC handler band 0x3db06: `cmp $4,%dx / jb; cmp $5 / jbe 0x3d80b;
cmp $7 / jb 0x3d7e0; cmp $7 / jbe 0x3d7b5; cmp $0x32(50) / je 0x3d80b`.
0x3d80b arm = store key->ds:0x74528 + clicked cell->widget+0xab, return
0 (repaint shows the popup via the builder). PLIND/PLPRO/PLPOP all
SENDMESSAGE 50 with SENDPARAM1 1/2/4 — the PARAM1 rides in -0x28(%ebp)
(the same +0x47 slot the planets-ui §2 selector reads).

## PORT STATE CHECK + NEXT
NEXT: check rewrite ui.cpp indicator click handling; implement popup
content law (pure fn indicatorPopupLines(key, planet fields) -> lines)
+ on-screen popup render + pins; witness via tplv2_port_witness.sh
recipe (xsend CLICK mode is CORRECT here — indicator clicks are real
clicks; PLIND box centre ~(176,56), PLPRO ~(292,56), PLPOP ~(404,56)
window-rel + window origin).

## P6 — LIVE JUMP-TABLE VERDICT (41.sav, work/tplb2_jumptab.py) [verified]
Known selector table (image 0x27fe8, planets-ui S2) found at member
0x1fc070 => P0 = 0x1bf450; the case table at image 0x28fb8 sits at member
0x1fd040 (delta 0xfd0 EXACT). KEY->BODY MAPPING (P0-subtracted entries):
  key 0 (PLRES, PARAM1 0)  -> 0x3dc61 RESEARCH   (name getter65, +0x46)
  key 1 (PLIND, PARAM1 1)  -> 0x3dd17 INDUSTRY   (name getter68, +0x44)
  key 2 (PLPRO, PARAM1 2)  -> 0x3ddc0 PROSPERITY (name getter70, +0x48)
  key 3                    -> 0x3de5a SQUARE (cell info seam; no window
                             sends 3 — POP remap 4->3 is the OTHER switch)
  key 4 (PLPOP, PARAM1 4)  -> 0x3e2c8 FULL-INFO chain
=> PLRES = RESEARCH box, PLIND = INDUSTRY, PLPRO = PROSPERITY (the user's
"plant box in the middle" = PLPRO; witness text matches the key-2 law),
PLPOP = FULL-INFO popup. NOTE the popup RECT law: (wx+10, wy+10)..
(wx+335, wy+217) from the clicked widget origin (ebp+0x32/0x36/0x3a/0x3e
= wrec[8]+10, wrec[0xc]+10, wrec[8]+0x145, wrec[0xc]+0xcf). The user's
3-line reading of the PLPRO popup = L-D WRAPPING ("Crimea 1" /
"Prosperity: 1 per day") + L-E; the content law is 2 sprintf lines.

PER-KEY CONTENT LAW (port target; planet rec = DAT_00043508):
 key 0 RESEARCH:  L-D "%s Research: %d per day" (name, u16[+0x46]);
   t = WORD[0x76492+2*ownerRace]; if t != 0xffff: tech name = RESTREE
   record 0x74746+75t (stride 75 OQ-013; name at rec+0); countdown via
   0x46de0(0x74744) + WORD[0x764a0+2r] + WORD[0x74782+75t] -> 0x47010;
   L-E "<tech> will be discovered in D day%s." or
   "No progress is being made on <tech>." (getter 66/67).
 key 1 INDUSTRY:  L-D "%s Industry: %d per day" (name, u16[+0x44]);
   c = u16[+0x52] build cell; item = cell4(c)[+1]; if item != 0xff:
   name = planitem name RAM mirror (0x73e40+40*item+0xa); countdown
   0x47010(0x394d8(0xff,u16[+0x44],u16[+0x50]) legs); L-E "<item> will
   be completed in D day%s." / "No progress is being made on <item>."
 key 2 PROSPERITY: L-D "%s Prosperity: %d per day" (name, u16[+0x48]);
   if u16[+0x42] (pop) < u16[+0x4a] (maxpop): cd = 0x47010(u16[+0x48],
   u16[+0x4e], dword[0x66e4]); cd != 0xffff -> L-E "Population will grow
   in D day%s." (= USER WITNESS) else "Population is not growing."
   (getter 73); pop >= maxpop -> "Population has no more room to grow."
   (getter 74).
 key 4 FULL-INFO: L0 planet+0x24 name (hold 0xf); L1 getter(94) "%s %s
   Planet" from RUNTIME pointer tables 0x7452c[u16 planet+0x14] /
   0x74540[u16 planet+0x16] (runtime-derived; static seam — names likely
   names.txt size/atmos words, UNVERIFIED, named); L2 getter(96) "Owned
   by |%d|%s" (race id + race name table 0x74590+20*race(0x12e17));
   owner 0xff -> ebp+0x42 pre-filled getter(95) "No One" at 0x3e347;
   L3 getter(97) "Maximum Population  %d" u16[+0x4a]; L4 getter(98)
   "Self Managed" iff owner==player(0x7458e) && u16[+0x5a]==0xffff;
   L-D/L-E unset on a fresh key-4 visit (+0x72=0 -> skipped).
Plural suffix getter(28)""/getter(29)"s" iff count==1 (0x3e560 arm).
0x47010(a,b,...) countdown helper, 0xffff = no progress; 0x66e4 growth
divisor global (READ from saves; OQ-016 adjacent — note not close).
*** 0x47010 LAW [verified 2026-11-24, objdump 0x47010..0x470a0 + tail
0x46de0..0x46e60]: 0x47010(acc, rate, target) -> if rate<=0 return 0xffff;
d = acc - target; if d<=0 return 1; return ceil(d/rate) clamped >=1.
0x46de0 = research-acc getter: dword[0x74744 + 4*race] (per-race research
bank). PROSPERITY call site passes (u16[+0x4e] growthCounter, u16[+0x48]
pros/day, dword[0x66e4]) => days = ceil((growthCounter_target - counter)/
pros-per-day-ish per the same shape — port mirrors 0x47010 verbatim. ***
0x2fb38(display 0x7d3a2, edx=0, ecx=str, ebx=HOLD, 2, -1, -1, 0) line
push; holds per line: name 0xf, planet-type 0x3c, owned-by 0x5a, maxpop
0x78, self-managed 0x96, per-day 0xf, grow 0x50.

## P7 — THIS SESSION (fresh iteration): disasm re-verification [verified]
Re-ran objdump on work/ascend_restored.bin — every WIP claim above holds:
 - KEY-2 PROSPERITY BODY 0x3ddc0..0x3de59 EXACT: +0x72=getter(70),
   +0x7e=u16[0x43508+0x48], +0x5a=getter(71), +0x6a=getter(72),
   +0x6e=-1; if u16[+0x42] > u16[+0x4a] -> ELSE branch getter(74);
   else cd=0x47010(eax=dword[0x66e4], edx=u16[+0x4e], ebx=u16[+0x48]) ->
   +0x7a; and 0xffff -> +0x62=getter(73); NOTE CALLING CONVENTION:
   eax=TARGET(0x66e4 wrap), edx=ACC(counter +0x4e), ebx=RATE(pros/day).
 - TAIL 0x3e4db..0x3e5db EXACT: L-D gated on [ebp+0x72]!=0 —
   sprintf(-0x9e(ebp), getter(99), name=planet+0x24, [ebp+0x72],
   u16[ebp+0x7e]) then 0x2fb38(eax=0x7d3a2, edx=0, ecx=buf, ebx=0xf,
   push 2, -1, -1, 0); L-E gated on [ebp+0x6e]!=0: if u16[ebp+0x7a]==
   0xffff -> sprintf(buf, [ebp+0x62], [ebp+0x5a]) (getter73/67 "%s ...");
   else plural = getter(28) iff cd==1 else getter(29); sprintf(buf,
   getter(100), [ebp+0x5a], [ebp+0x6a], u16[ebp+0x7a], plural); push,
   ebx=0x50, same 0x2fb38 shape. ARG ORDER in #100: subject, verb, days.
 - 0x47010 EXACT (0x47010..0x47034): eax=target ecx=acc? NO — ecx pushed,
   ecx=eax on entry (eax=arg1=target); if ebx(rate)<=0 -> eax=0xffff;
   else ecx-=edx (target-acc); edx=(ecx-1); idiv ebx; eax=quot+1;
   clamp: if eax<1 eax=1. => days = max(1, (target-acc-1)/rate + 1) ==
   ceil((target-acc)/rate) floored at 1; rate<=0 -> 0xffff. [verified]
   statuslist.cpp statusDays is the SAME law on the IND leg (cost-acc).
 - static.txt strings re-extracted via getter==nth-quoted-string law:
   28'' 29's' 65 Research 66 'be discovered' 67 'No progress is being
   made on %s.' 68 Industry 69 'be completed' 70 Prosperity 71 Population
   72 grow 73 '%s is not growing.' 74 '%s has no more room to grow.'
   94 '%s %s Planet' 95 'No One' 96 'Owned by |%d|%s' 97 'Maximum
   Population  %d' (TWO spaces) 98 'Self Managed' 99 '%s %s: %d per day'
   100 '%s will %s in %d day%s.' [verified against file]

## P8 — PORT LANDED (code + pins) [verified by build+suite]
 - NEW rewrite/src/ui/indpopups.{h,cpp}: countdownDays (0x47010 verbatim),
   indicatorPopupRect (wrec+10/+0x145/+0xcf law), IndicatorContent +
   indicatorLines (L-D/L-E incl. plural pair + sentinel legs),
   fullInfoLines (key-4 chain incl. "Maximum Population  %d" two-space
   verbatim + raceChipCode), popupLinesFor (Campaign-fed per-key cases).
   SEAMS NAMED: TPLB2-A (0x394d8 Ship/Automation cost legs — statuslist
   precedent), TPLB2-B (inline |%d| chip directive not rendered; code
   computed+pinned), TPLB2-C (chip raceIdx runtime table 0x12e18 analog =
   owner specnum), hold-tick consumer unrecovered -> port shows all lines
   until next planet-screen click (documented default).
 - Campaign::queuedTechFor(owner) read added (WORD[0x76492+2r] analog).
 - ui.cpp: msg-50 ARM inserted BEFORE the tile arms (panel click wins over
   PLSQUARE even with a pick pending — windows.txt SENDMESSAGE law);
   dismiss on tile/order clicks + fresh on both planet-view openers;
   render block draws lines in the builder rect (backing shape = port
   affordance, TEXT = law).
 - pins tests/test_indpopups_tplb2.cpp (6 tests): countdown instruction
   values, rect law all 5 panels, L-D/L-E verbatim + gates + plural +
   sentinel, full-info chain + No One + chip code, campaign cases all 4
   keys (PLBUILD empty). Suite 511/0/0 (was 505).
 - HARNESS NOTE: tests/harness.h has CHECK/REQUIRE_DATA ONLY — no REQUIRE
   macro; local REQUIRE = CHECK+return idiom now pinned in this test file.

## P9 — LIVE PORT WITNESS [measured 2026-11-24, scripts/tplb2_port_witness.sh]
Seed-5 fresh campaign -> Amoroso I planet view (port window 640x480, :99):
 - ARM LOG: "ui planet popup plres (1 lines)" / plpro (2) / plpop (5) /
   plind (1) — per-key line counts match the builder law (no pending item
   -> INDUSTRY L-D only; RESEARCH L-D only pre-first-turn progress leg;
   POP = five-line full-info chain).
 - PIXEL CENSUS (scripts/tplb2_census.py) VERDICT PASS: each popup shot
   changes 93.8% of its OWN builder rect; no-overlap control (plpro shot
   inside the PLRES rect) 0/48319 px; dismissed shot pixel-IDENTICAL to
   rest (0/307200) — popup paints in the cited rect, leaks nothing, and
   the next-click dismiss holds.
 - VISION ORACLE on popup-plpro.png: popup reads EXACTLY
   "Amoroso I Prosperity: 1 per day" / "Population will grow in 50 days."
   — the D26 user witness ("Crimea 1 / Prosperity: 1 per day / Population
   will grow in 50 days") reproduced shape-for-shape from the ported law
   (name + getter99 + getter100 legs; counter 0 with pros 1 -> 50 days
   per 0x47010 with wrap 50).
 - xsend note: the click mode prints "(window died before release)" as a
   NOTICE when the app is killed after the shot sequence; the app log
   shows it survived every click (winpos + all shots succeeded).
