# t392 WIP — title text baseline + Alt-L/S/X second lines

## Findings (all MEASURED this session, 2026-11-14)

### F1 Vendor table law (extracted/ascend00/windows.txt L34-175, cited verbatim)
- Seven title buttons; WINITEMS counts: first four (INTRO, PLAYTUTORIAL,
  FRESHGAME, RESUME) = 1 item; LOAD/SAVE/EXITTODOS = 2 items.
- TEXTITEM grammar observed: `TEXTITEM <slot> <string> <font> <?> <dy>`
  - single-line buttons: `TEXTITEM 0 Play^Introduction 3 0 0` (font 3, dy 0)
  - LOAD: `TEXTITEM 0 Load^Game 2 0 4` + `TEXTITEM 0 Alt-L 2 0 18`
  - SAVE: `TEXTITEM 0 Save^Game 2 0 4` + `TEXTITEM 0 Alt-S 2 0 18`
  - EXITTODOS: `TEXTITEM 0 Exit^to^DOS 2 0 4` + `TEXTITEM 0 Alt-X 2 0 18`
  (exact slot digits repeat 0 on both items — the second field is the string;
  sub-grammar after the string stays OQ-015 territory, but the LAST field
  correlates with the measured ink rows: see F2.)
- Alt-X is in the vendor table -> user testimony (Alt-X on Exit) is table-
  corroborated, not just testimony.

### F2 Pixel measurement on the pinned vendor shot docs/assets/refcap/
original-title-menu.png (640x480; capture shift: shot row = logical row + 40,
verified by pure fill rows (0,0,8) at shot 360..390 == logical rect 320..390-1
of btn3... actually == btn3 y0+40..y1+40):
- btn0 (WINITEMS 1, font 3): white (215,215,215) ink rows dy 8..18 (11 rows);
  row profile 8:11 9:7 10:7 11:39 12:30 13:27 14:26 15:24 16:27 17:34 18:2.
- btn3 (WINITEMS 1, font 3): ink rows dy 8..17.
- btn4 LOAD (WINITEMS 2, font 2): LINE1 ink rows dy 4..13, LINE2 ink rows
  dy 18..27. btn5 SAVE: identical profile (dy 4..13 / 18..27).
- => DRAW LAW (port): single-line label TOP = y0+8; two-line buttons: line1
  TOP = y0+4, line2 TOP = y0+18. (dy fields 4/18 land exactly on the measured
  ink tops for font 2; font 3 with dy 0 lands at +8 — centring-equivalent.)
- HORIZONTAL: both lines centred on the rect centre. Measured x-spans
  (shot coords): btn4 L1 289..346 (centre 317.5), L2 305..331 (centre 318);
  rect centre (159+477)/2 = 318. Centring law stands.

### F3 PORT DELTA (work/r1/loop/t391-title.png, native 640x480)
- Our btn0 ink rows dy 4..14: profile 4:11 5:7 6:7 7:39 8:30 9:27 10:26
  11:24 12:27 13:34 14:2 == VENDOR profile shifted exactly -4 rows.
  => user's "text is a tad too high in the boxes" = title.cpp:174 draws at
  y0+4 where the vendor draws at y0+8. MEASURED, decisive.
- Our shot has ZERO second lines (dy 18..27 white = 0 on every button).

### F4 UNDERLINE NEGATIVE (task said "check the pin, do NOT invent")
- External vision read of the 3x-zoom crop (/tmp/t392-loadbtn.png) claimed
  the 'L' of Load is underlined. MECHANICAL REFUTATION: inside btn4's rect
  the colour census holds EXACTLY {fill (0,0,8), ink (215,215,215)} — no
  third colour — and row dy13 (white=29) is glyph-bottom, dy14 white=0:
  NO full-width or partial white underline row exists anywhere in rows
  dy0..30. The '^' in "Load^Game" is the word joiner (boot.md §1), NOT a
  rendered hotkey underline. Port renders NO underline.

### F5 HOTKEY LAW
- bootHotkey (rewrite/src/ui/boot.cpp:27) handles 'l','s' only. Vendor table
  carries Alt-X on EXITTODOS -> add 'x' -> BootState::Quit (same shape).
- Alt-L/Alt-S/Alt-X strings are DISPLAY strings (verbatim from table), drawn
  as the vendor's second line; the routing letters come from the same items.

### F6 HINT FACE = BIGFONT (decisive width census)
- Vendor ink x-spans (shot): "Load Game" L1 = 289..346 = 58 px; "Alt-L" L2 =
  305..331 = 27 px. bigfont no-gutter string widths: 59 and 28 (each span +1,
  consistent with ink-span-vs-layout-width edge effect). smfont: 52 and 22 —
  both FAR off. => the vendor draws BOTH lines in bigfont (the TEXTITEM font
  field 2 vs 3 distinction is NOT a face-size difference visible here; the
  port uses its large face for both, MEASURED). Horizontal CENTRING law
  re-confirmed: L1 centre 317.5, L2 centre 318, rect centre 318.

## Implementation contract
- boot.h/cpp: TitleButton gains `const char* hint` (nullptr for the four
  single-item buttons; "Alt-L"/"Alt-S"/"Alt-X" verbatim for LOAD/SAVE/
  EXITTODOS). bootHotkey adds 'x'.
- title.cpp draw loop: hint ? (line1 y0+4 centred, line2 y0+18 centred)
  : (line y0+8 centred). Same VendorText large face + kInk for both lines
  (vendor census: one ink colour inside the rect).
- Pins (new test file test_titletext_t392.cpp): geometry table (all 7 tops),
  hint presence/verbatim strings, hotkey map incl. 'x'->Quit + non-Title
  no-op, underline negative stated as "no underline field exists in the
  draw law".
