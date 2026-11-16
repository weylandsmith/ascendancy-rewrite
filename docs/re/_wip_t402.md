# _wip_t402 — PLANETS LIST SCREEN (D11 "wrong and unusable")

Iteration context: fresh session, tree clean, ring max_turn=1254 (no new
sitting), page server alive :8613, no new USER: lines after 11:37 block.
Assignment = STATE.md NEXT = t402 verbatim: first pass at the PLANETALLOC/
planet-window law already banked (planetwin.{h,cpp} t276, planets-ui.md,
poppanel t263) -> render the real list screen: columns, per-planet name/
atmosphere/pop/manufacturing from the campaign model, chrome per windows.txt
(17np lib, state 17), click to select. Screenshots -> t402-*.png.

## S0 — WHAT IS ALREADY LAW (re-read, not re-derived)
- windows.txt state-17 section L1486-1620: PLANETALLOC parent TYPE 7
  0,0-639,479; PLANLIST TYPE 10 120,120-520,420; PLSQUARE TYPE 14
  152,120-487,375; five TYPE-29 panels PLRES/PLIND/PLPRO/PLPOP/PLBUILD
  (kPlanetPanels, planetwin.cpp:15-22). PARENT=PLSQUARE children x6 from
  L1622. ALL captured in ui::planetwin.
- BUT the user's D11 complaint is about the screen reached from the rail
  "Planets" button = STATUSWND state 10 (t249 live experiment clicked
  sidebar Planets at (553,145) -> sig-obj + "80 Planets Occupied, 26 Systems
  Controlled" header). STATE 10 = STATUSWND 7,7-632,472 + STATPLANLST TYPE 10
  7,46-632,472 SHAPEFRAME 7. The PLANETALLOC state-17 screen is the planet
  DETAIL/alloc screen (reached by selecting a planet), not the list.
- Header law #151 "%s  (%d Planet%s Occupied, %d System%s Controlled)"
  (double space byte-exact) — planetwin.h. Systems leg = sole-owner loop
  (FUN_00051684, selfplay.md PROOF 3); planets leg = screen-open snapshot
  count u16[list+0x8c7] == count(NAMED && NAME+0x33==race) at open (t249
  LIVE: 80/80 exact @t1086).
- Row content strings (static.txt, status.cpp region):
  #136 "(%s %s Planet)"; #137 "Self-Managed"; #138 " - No Progress";
  #139 " - %d day%s until completion"; #140 "Building %s%s"; #141 "No Project".
  Size words #41-45 Tiny/Small/Medium/Large/Enormous; type words #46-56
  Husk/Primordial/Congenial/Eden/Mineral/Supermineral/Chapel/Cathedral/
  Special/Tycoon/Cornucopia. refcap pin original-planet-view.png: "Xerxes I
  (Enormous Supermineral Planet)" + "No Project" assemble EXACTLY (refcap.md).
- Gauge law: PLRES clamp0..20(round(RES^0.75)) slot [0x6fd90], PLIND same on
  IND, PLPRO identity; POP band law SEL(i)=1+[i>=used]+[i>=pop] over i<cap,
  10/row, 17np k1 busy/k2 free/k3 empty (planets-ui.md S3/S4, poppanel t263).
- Campaign model analogs: planetAt(star) per STAR (rewrite models one planet
  per star!), ChannelWords channelWordsFor(star) (+0x44/+0x46/+0x48 incl.
  governor branch), popBandsFor(star), pendingItemFor/buildAccFor, items,
  sizeClassFor(surfaceCells), terrainRow (+0x16, NOT a type word — t281
  census refuted the homeworld reading).

## S1 — WITNESS READS (pinned/captured vendor shots, external-vision allowed
for the t3 capture = our live-capture of the ORIGINAL game)
- work/screens/t3/planets_header_t1086_after_open.png (800x600 capture of
  640x480, scale 1.25): external vision read: header "Chamachies (80 Planets
  Occupied, 26 Systems Controlled)" centred top; rows = per-planet entries:
  selection marker, SYSTEM circle art, system name (cyan), PLANET circle art,
  planet name + "(Large Cathedral Planet)" line 1, construction status line 2
  ("Building Research Campus - 2 days until completion"), three surface
  thumbnails, gauge dots block RIGHT (red); up/down arrow buttons right edge;
  black bg, cyan text, teal bevel chrome. Row pitch vision said ~150-160px in
  the 2x-resized crop = ~60px native (needs mechanical confirm).
- MEASURED (mine, mechanical): pure-fill rows (33,56,57) at capture y146 and
  y572 -> native y116.8 / 457.6: the STATPLANLST interior frame lines.
- docs/assets/refcap/original-planet-view.png = the DETAIL screen (1-planet
  empire), header + "(Enormous Supermineral Planet)" + "No Project".

## S2 — SCOPE DECISION
Screen to implement = state 10 STATUS list (the rail Planets button target;
the D11 complaint). Click-to-select a row -> seam prints (the vendor's
next screen = PLANETALLOC state 17 detail; wiring the full detail screen is
beyond one iteration — named seam). Content law = cited strings + gauge/
pop laws; geometry = windows.txt rect + measured frame lines; per-row layout
= proportional from the witness with NAMED SEAMS where uncited.

## S4 — TYPE-WORD RESOLUTION + DAYS LAW (this session, cited)
- TYPE WORD = +0x16 = the rewrite's terrainRow ANALOG [verified consumer
  found]: the row builder 0x50704 reads WORD[PL+0x16] and indexes the 11-slot
  type table; the rewrite's PlanetState.terrainRow IS the +0x16 analog
  (income-law.md S10, t281 stored it precisely because SA_Cornucopia skips
  +0x16==10). t281 MEASURED terrainRow uniform over 0..10 = EXACTLY the type
  domain (11 words Husk..Cornucopia). The t281 tension resolves: the field
  has a consumer (the status-list type word), and word 10 == "Cornucopia"
  makes the SA_Cornucopia skip semantically coherent (skip already-rich
  worlds; row 10 is the zero-barren weight row). SIZE WORD = +0x14 =
  sizeClassFor(surfaceCells) (verified 1:1 across 484 saves, campaign.h).
  => line-1 words are DERIVABLE from the rewrite model, cited end to end.
- DAYS LAW [verified 0x39558 -> 0x394d8 -> 0x47010]:
    cost = WORD[0x73e48 + idx*5*8] (= planitem record COST u16@+8, relocated
    copy stride 40 = 5x8, OQ-014 record map); IND = WORD[PL+0x44];
    acc = WORD[PL+0x50]; slot-item bl from [ecx+0x10]+edi*4+1;
    bl==0x23 && IND-word(+0x52)==... -> cost *= 3 (Automation leg, not
    modelled — named);
    FUN_0x47010: IND <= 0 -> 0xffff sentinel (" - No Progress");
    else days = (cost - acc - 1)/IND + 1 == ceil((cost-acc)/IND)  [verified
    instruction-exact: sub ecx,edx; lea edx,[ecx-1]; idiv ebx; inc eax].
  Plural pair = getter(28)"" / getter(29)"s" AT 0x5084e/0x50855 (the generic
  pair, so the t276 [inferred] plural law is now CITED for #139).
- NAME + SUFFIX: name copied 20B (5x movsd) at 0x50683; the 136-format fills
  "(%s %s Planet)" ALONE; witness shows "Oslo II (Large Cathedral Planet)" ->
  line1 = name + " " + formatted (space join; single-string seam).
- SELF-MANAGED: [PL+0x5a]==-1 -> getter(137) replaces (0x5077f); rewrite has
  no per-planet governor==-1 state (governor law t45) -> leg exists in the
  pure module, unwired from Campaign, pinned synthetically.

## S5 — SCOPE (locked, ~30 probes used; implement now)
Module ui/statuslist.{h,cpp} (pure) + ui.cpp kScreenStatus branch + pins
test_statuslist_t402.cpp + witness scripts/t402_status_witness.sh (+census)
+ law block in docs/re/planets-ui.md + screenshots work/r1/loop/t402-*.png.
Vendor art paintable (OQ-005 CLOSED t367): 10status k0 backdrop (already
via backdropFor), planets.shp sphere via (type-group, sizeClass) ladder
[NAMED SEAM group law], 17np pop slots (cited), planitem.shp project icon
(plbuildIcon cited for 34, [inferred] identity elsewhere).

## S3 — PROBES RUN (this session)
- P1 STATIC ROW-ASSEMBLY LAW FOUND [verified, work/ascend_restored.bin
  base-0; sites via scripts/t402_status_getters.py — getter args are
  MOV EAX,imm32 + call 0x21a20 (regparm), NOT push]:
    0x50704 mov ax,[PL+0x16]; 0x50708 mov esi,[eax*4+0x74540]
    0x50711 mov ax,[PL+0x14]; 0x50716 mov edi,[eax*4+0x7452c]
    0x5071e getter(136) "(%s %s Planet)"; sprintf(buf, fmt, edi, esi)
    => LINE-1 LAW: "(<size> <type> Planet)" with size = string-table slot
       WORD[PL+0x14] (5 slots), type = WORD[PL+0x16] (11 slots).
    0x50770 ebx=[PL+0x5a]; if ebx==-1 -> getter(137) "Self-Managed"
       replaces the name field (0x5077f..).
    LINE-2 (project) LAW [verified 0x507ca..0x508b9]:
      if byte[PL+0x54]==0xFF -> "No Project" (141), and IF additionally
        u16[PL+0x42]==u16[PL+0x4c] (pop==used) -> "   (No Free Population)"
        (142) appended (0x508da..0x50913).
      else: planitem-record name = 10 chars at 0x73e40+5*idx*8+0xa (0x5088f);
        if item-flags byte (0x73e46+idx*5*8) AND 2 -> skip progress leg;
        else call 0x39558(planet) -> days (0xffff = sentinel):
          0xffff -> " - No Progress" (138)
          1      -> " - %d day%s until completion" with getter(28)"" 
          else   -> getter(29)"s"
        then sprintf "Building %s%s" (140) with (item name, progress).
  PLANITEM NAME TABLE [verified 0x5088f]: item display names are the
  planitem.txt rows' name field (stride 0x28 law, OQ-014 name30@+10 —
  runtime copy stride 40 = 5x8, name at +0xa: SAME record, relocated).
- P2 SIZE/TYPE STRING TABLES located by CONTENT anchor in bank-t249-live-open/
  60.sav (scripts/r402_sizetype_census.py PASS): the 11 type words appear as
  a pointer array EXACTLY in static.txt order Husk..Cornucopia at member
  0x252ce8, and the 5 size words Tiny..Enormous at member 0x252cd4 —
  adjacent, gap = 0x14 = the ds:0x7452c/0x74540 delta. So the runtime tables
  ARE the static.txt word lists in file order: size idx 0..4, type idx 0..10.
- P3 RECORD-FIELD RESIDUE (honest): the t249 list-object walk
  (scripts/r402_listobj_census.py + session variants) resolves entries to the
  NAME-run records (stride 123, names decode: 'Oslo II','Vega IV'...) but
  WORD[+0x14]/[+0x16]/[+0x18] read ZERO in EVERY member of that array across
  60.sav AND 41.sav (cells-in-{7,11,23,45,73} window census = 2 hits total,
  random). The paint-visible record the row builder reads (0x50704 family)
  therefore lives in ANOTHER array than the name run — the name run is the
  list-HANDLE side (t249: entry = handle, rec = handle+0xac; the +0xac
  region decodes names but its u16 fields are zero). WHICH array holds the
  live words = NAMED RESIDUE (decider: a debugger walk of [ebp] in the row
  builder, or a same-turn RAM pair). The word VALUES themselves are cited
  from the disasm + refcap assembly ("Enormous Supermineral"); the rewrite
  feeds its OWN model (surfaceCells -> sizeClassFor; type = documented
  default seam — no cited type-draw law exists in banked RE).
- P2b ROW GEOMETRY MEASURED (green selection-marker runs on
  work/screens/t3/planets_header_t1086_after_open.png, capture->native /1.25):
  marker bands native y 128.0-143.2 / 240.8-256.0 / 353.6-368.8 -> row tops
  ~126/239/352, PITCH ~112.6 px (three rows visible in the 426-px interior =
  46..472). Marker = 15 px tall green bar at left edge x~16-66 native.
  Frame lines (pure fill (33,56,57)) native y 116.8 and 457.6.


## S5 — LAND (end of session)
statuslist.{h,cpp} + ui.cpp status branch + test_statuslist_t402.cpp (7 pins,
suite 347/0) + MUTATION 8/8 CAUGHT (driver t402_mutate.py, copy-revert; M4
SIGFPE re-scoped to M4b) + witness t402_status_witness.sh (open/scroll x2/
select "Amoroso"; shots work/r1/loop/t402-status-{open,scroll1,select}.png).
Banked to planets-ui.md S8. LEDGER: no OQ row matches (D11 chrome lives in
the STATE queue); strict-close — D11 planets item USER-PENDING, nothing closed.
