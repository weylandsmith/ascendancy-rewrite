# t-d1page notes (2026-11-09, assistant, off-loop) — D1 ruling page + MEASURED mouse decode

## Ruling page (user-facing)
- Served at http://192.168.8.11:8613/ from /tmp/d1page (server.py, stdlib HTTPServer,
  background pid 41010 in THIS session's process group — dies with the session;
  restart: cd /tmp/d1page && python3 server.py).
- POST /ruling APPENDS a "## USER RULING <ts>" block with USER: lines to
  docs/DECISIONS.md = exactly the sentinel BRANCH-2 trigger (mtime + USER: grep).
  No test-POST was ever made (policy blocked curl); grep USER: still 0.
- Page asks: mouse k5/k6/k7 keep/junk; batch-accept 41; A6-A8 keep checkboxes;
  B1-B29 misID checkboxes; notes. B-images = on-disk XREC renders; mouse image =
  the render below (k5 plane; k4-k7 planes byte-identical, see law).

## MEASURED (file measurements, bankable; vision of our own render is NOT close
## evidence per R13 — the USER ruling is the closer)
- mouse.shp k5/k6/k7, dims taken from the t344 bbox law (78x47 for all of
  k4..k7), stream rec+0x18: rowwalk_free completes EXACTLY 47 rows for all
  four records, stream ends at byte 2062 == span end (4/4). The rewrite
  decoder FAILs them ONLY at its dims gate (reads the u32 pair at rec+0x10
  and rejects the zero half of the SIGNED bbox pair) — the stream itself is
  clean under the banked X-class law.
- The four painted planes k4..k7 are BYTE-IDENTICAL (md5 b2d049bbf5b5 each):
  one glyph, four anchors, mechanically confirmed at the pixel-plane level
  (independent of vision). Glyph = 78x47 "Exit <ESC>" corner prompt (white +
  lime text, beveled frame) per vision of our render — identification flavor
  only.
- Implication for the rewrite (when D1 lands): a signed-bbox-aware dims read
  at rec+0x10 (abs() or bbox-diff law shp.md S27) would decode k4..k7 without
  touching the -1 blit gate; validator index.txt would move 3-4 records from
  DECODE-FAIL. Do NOT apply before the ruling (OQ-005 is the user's row).
