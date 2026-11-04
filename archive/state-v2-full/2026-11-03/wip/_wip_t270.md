# t270 WIP — HOME-PLACEMENT VERIFICATION (OQ-016 residue)
# Status: in flight. Fresh-session resume: read this file + STATE.md NEXT.

## Anchors loaded (cited, pre-existing laws — none invented here)
- Star record (stride 0x60, DAT base 0x13bc5; r1-savestate.md star-table +
  t246/t248 scripts): +0x4 u32 idx==k, +0x8 f32[3] position (name-0x14),
  +0x14 owner bitmask, +0x1C name, +0x2A u32[5] planet pointers (target =
  planet NAME addr - 0x24; LIVE iff planet name prefix == star name).
- HOME STAR LAW (t246/t248 disasm-cited @0x516d7): DWORD[0x12e1d +
  race*0x1ee] (race row 0x12e16 stride 0x1ee, +7) == runtime ADDRESS of that
  race's home STAR record inside the 0x13bc5 table.
- HOME PLANET LAW (t248 PROOF 4): planet table NAME+0x33 byte == race index,
  0xFF unowned; vendor resume.gam static init = EXACTLY 7 records 0..6.
- SHELL LAW (OQ-012/OQ-025 CLOSED, mapgen.md S4/S152): T=50 radii fixed
  440(k0..25), 365(26..37), 290(38..43), 215(44..46), 140(47), 65(48),
  50(49); radius = hypot(x,y,z) exact-float; NO min-separation law shipped.
- Orbit law: planet orbit pair f32 @ planet-name+0x57/+0x5f, galacto-centric,
  radius constant per planet.
- Precedent to test (b): t106 run-local finding for +0x55 seeds.

## Banks in scope (offline; NEVER loadstate)
bank-t1254/48.sav (prod t1254), bank-t249-live-open, bank-t251-predrive,
bank-t261-final-1236, game/resume.gam (vendor static init). Independent
LINEAGES for (b): old fresh-game runs work/r1/r1ad-*/r1deep-* (separate
sessions per r1_slot doc); production banks are ONE lineage.

## Findings

## S2 SEMANTICS + HOME PLANET (MEASURED, 6 fresh lineages t<=2 + production):
#   HOME STAR = record ka where ptr == base(ka)+0x60 (base = NAME - 0x1C),
#   NOT ka+1: decisive test = the race-r-owned planet (planet NAME+0x33 == r)
#   lives in record ka's live-planet list in 25/25 race0..4 observations
#   (Sophia I@29, Stavern III@28, Hurble IV@9, Ignatius I@16, Philadelphia
#   I@24, Flammifer II@39, Fletcher V@0, Ajax II@12, Delphinius II@18,
#   Luxor IV@25, Pendulon II@8, Crell I@31, Hope I@16, Aglarond III@13,
#   Discordia I@14, Philadelphia I@7, Corpuscle I@19, Discordia IV@18,
#   Synthos III@13, Tonsberg IV@28, Vishnu II@37, Ajax II@1, Corncob I@30,
#   Synthos I@23, Gridsor III@34, Smorgasbord III@30, Tensoric I@8,
#   Freblinsee I@27, Gasball III@19, Feculon II@20).
#   HOME PLANET orbit index VARIES (I..V: Fletcher V, Fletcher V, Luxor IV,
#   Smorgasbord III...) -> NOT always orbit I; consistent with t40/t42
#   "first colonisable choice" (the orbit pick is the terrain-aware step).
#   NON-PARTICIPATING race slots hold STATIC values across every fresh run
#   (r5=0x255fe5=k11, r6=0x255e05=k6 in ALL r1ad runs examined; production
#   5-empire banks read ptr 0 for r5/r6) -> the pointer is written per
#   participating empire at setup; unused rows = template residue.
## S3 JOIN RESOLVED (MEASURED, r270_homeplace.py + probe battery):
#   Star-record layout restated with base = NAME - 0x1C (stride 0x60):
#     base+0x4 u32 idx==k; base+0x8 f32[3] pos; base+0x14 OWNER BYTE;
#     base+0x1C name; base+0x46 u32[5] planet ptrs.
#   HOME POINTER: DWORD[data 0x12e1d + race*0x1ee] == phys of base(k) EXACTLY
#   (== NAME(k)+0x44 == the first planet-pointer slot). k = (ptr-(NAME0-0x1C))
#   // 0x60, remainder 0 in every participating observation.
#   DECISIVE SEMANTICS: at turn>=1 the home star's owner byte == 0x80 |
#   (1<<race) AND the race's own planet (planet NAME+0x33 == race, t248 law)
#   is inside that star's LIVE planet list (r1ad-131350 t1: Sophia I@29,
#   Stavern III@28, Hurble IV@9, Ignatius I@16, Philadelphia I@24; production
#   t1086/t1254: Oslo I@25, Philadelphia II@27, Sarsaparilla I@18). Home == k,
#   not k+1 (the k+1 reading came from anchoring on the name field).
#   TURN-0 TRUST LAW (t270): at turn 0 the race-row home pointers are
#   TEMPLATE RESIDUE (r5=base+11, r6=base+6 identical across every fresh run;
#   t269 found all T/selector anomalies in turn-0 frames too). Only turn>=1
#   home state is real. ptr==0 -> race not in game.
#   OWNER BYTE census (prefix-filtered live-planet OR identity): byte&0x7f ==
#   OR(1<<owner)&0x7f 50/50 bank-t1254/48.sav. bit7 on STAR records: set on
#   every home star at t=1 and still set on homes @t1254; non-home stars also
#   show bit7 -> semantics UNVERIFIED (t248 PROOF 1 already masks &0x7f).
#   Planet owner bytes carry NO bit7 (t248 102-count law holds raw ==race).

## S4 ANSWERS (from work/r1/t270_homeplace.out, 14 independent lineages):
#   (a) HOME SLOT vs SHELL: home slots span the table (hist 0..41), NOT an
#       outer-shell-only choice; min inter-home 3D distance 131.6..372.3
#       (median 228.1) over 13 lineages -- no hard min-separation law ships
#       (consistent with OQ-012 "closest observed pair 24.4"), but homes are
#       never adjacent-close in any observed game.
#   (b) RUN-LOCAL, NOT TEMPLATE: 14 DISTINCT home-star sets over 14
#       analysable lineages (incl. 4 production-bank slots = 1 lineage);
#       no two independent games share a home star for race 0. The resume.gam
#       7-owner signature re-confirmed EXACTLY (base 0x9b1a, hist {0..6:1
#       each, 255:144}; template homes Xerxes I/Stavern I/Hannibal III/
#       Gasball V/Burphee III/Hurble I/Vishnu IV, orbit radii 0/544..1216) --
#       it is the static-init image, NOT a placement template.
#   (c) REWRITE MISMATCH: campaign.cpp pickHomeStars() is deterministic
#       max-min BFS-hop spread with first-home-lowest-id; vendor homes are
#       run-local random, first home is NOT lowest id (Sophia@29,
#       Flammifer@39, Rhovid@1...), and vendor home PLANET = first colonisable
#       orbit (varies I..V; t40/t42 law), while rewrite seeds orbit-fixed.
#       NOT upgraded this iteration: the vendor's draw law (uniform over what
#       pool? rejection on what spacing?) is not yet pinned -- annotate.

