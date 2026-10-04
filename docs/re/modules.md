# Subsystem map from the shipped binary (P2 spine)

Evidence: `game/ascend.exe` is **not stripped of module names** — 34
distinct C/C++ source-file name strings occur, 595 times in total.
Each is cited by its first raw file offset, so any later claim can be traced.

| module | refs | first raw offset | inferred responsibility |
|---|---|---|---|
| `winmgr.c` | 86 | 0x08825a | window manager, event loop, render primitives |
| `cosmos.c` | 48 | 0x086066 | galaxy map, star lanes, map generation |
| `race.c` | 39 | 0x087616 | race/species attributes |
| `ssystem.c` | 32 | 0x087e2c | star system / planetary surface state |
| `raceneg.c` | 31 | 0x0877ff | (unassigned) |
| `batmode.c` | 28 | 0x08597a | battle mode driver (combat loop) |
| `eventwnd.c` | 28 | 0x0866de | event/UI dispatch DSL parser |
| `flic.c` | 28 | 0x086a0f | FLIC player |
| `planet.c` | 26 | 0x0872b6 | planet development, population, minerals |
| `gwindow.c` | 25 | 0x086db0 | generic window base class |
| `ship.c` | 25 | 0x087b69 | ship design, movement, systems |
| `coswnd.c` | 22 | 0x08643b | galaxy map window UI |
| `batcon.c` | 21 | 0x085606 | battle control / input during combat |
| `cache.c` | 19 | 0x085c82 | resource cache / shape loading |
| `status.c` | 16 | 0x088086 | status display, turn report |
| `batfxa.c` | 15 | 0x085852 | battle effects audio/animation |
| `batfx.c` | 14 | 0x08575a | battle effects rendering |
| `corn.c` | 14 | 0x085f07 | corner/minimap rendering |
| `gsystem.c` | 11 | 0x086cba | (unassigned) |
| `helpwin.c` | 10 | 0x086f66 | help windows |
| `shipwin.c` | 9 | 0x087d8e | ship window UI |
| `negwnd.c` | 8 | 0x0871b8 | negotiation window UI |
| `shipgiz.c` | 8 | 0x087cfa | ship gizmo sprites |
| `cfile.c` | 7 | 0x085e0a | file I/O abstraction |
| `planwin.c` | 7 | 0x0874a4 | planet window UI |
| `font.c` | 6 | 0x086c71 | font (.fnt) loading and text blit |
| `research.c` | 3 | 0x087a81 | technology tree progression |
| `flicwin.c` | 2 | 0x086c36 | FLIC window wrapper |
| `ascend.c` | 2 | 0x088b31 | entry point / init |
| `cob.c` | 1 | 0x085e88 | .cob archive reader |
| `loadwin.c` | 1 | 0x087178 | load-game window |
| `name.c` | 1 | 0x08719e | name generation |
| `psqwin.c` | 1 | 0x0875ae | planet-square / tile popup window |
| `reswin.c` | 1 | 0x087ac9 | research window UI |

Unassigned modules are listed as-is; roles above are **[inferred]** from the
name plus the extracted data files they obviously correspond to, and each one
must be confirmed against the code before a formula cites it (PLAN rule 1).

## What this does and does not buy us

- It gives the P2 deliverable structure (9 subsystems -> these 34 modules), so
  docs/re specs can be named after real compilation units.
- It does NOT give function addresses: without an LE loader the linear image
  cannot be reconstructed, so no function can be located. See docs/BLOCKED.md
  and OQ-008.

