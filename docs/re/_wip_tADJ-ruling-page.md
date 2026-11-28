# tADJ-RULING-PAGE — D2/D3 adjudication page SHIPPED + round-trip VERIFIED

Session start 2026-11-27 ~20:24 EST. Fresh session; resumed from STATE.md
alone. Assignment: build and serve the ruling page for the two USER-RULING
rows (OQ-016, OQ-019) plus the D3 loop-lifetime question. HAND-AUTHORED file
(gate does not regenerate _wip_ notes; docs/re/*.md regeneration sweep at
gate is documented in BLOCKED.md:117).

## T1. Deliverable
scripts/tADJ_ruling_page.py (stdlib-only, stdlib python3). Writes
work/r1/d1page/index.html (9536 B) + copies one witness shot to
work/r1/d1page/d11/tadj-state16.png (the live state-16 battle-control screen
from work/r1/dbg-t338-20261107-224027/10_state16_screen.png — the very screen
whose chain legs are cited-dead for BOTH rows). Archives the prior sheet to
index-d17r2.html (dir convention: index-d1.html, index-d11.html).

## T2. MEASURED serving facts (server.py read + curl, this session)
- The ruling server is ALREADY RUNNING (pid 646702 since Nov 15),
  ThreadingHTTPServer 0.0.0.0:8613 (D11_PAGE_PORT default), serves
  ROOT/index.html FRESH PER REQUEST — no restart needed to ship a new sheet.
- do_GET static whitelist is ONLY /img/ and /d11/ (server.py:95). An
  adj/ subdir 404s (measured HTTP=404) — images MUST live under d11/. Trap
  banked: first page build used adj/, caught by the curl check.
- POST /ruling appends "## USER RULING <ts> (from ruling page)" + one
  "USER: <label> = <value>" line per field to DECISIONS_FILE
  (server.py ruling_block fields handler).

## T3. SUBMIT round-trip VERIFIED (scratch, per server.py's own law)
Scratch server on :8777 with D11_DECISIONS_FILE=/tmp/tadj-test/decisions.md
(NEVER the real docs/DECISIONS.md from a test — server.py docstring law).
POST of the exact page payload shape -> HTTP 200 "Ruling recorded" and the
verbatim block appended:
  USER: ADJ OQ-019 disposition = accept-cited-dead-and-close-with-residue | notes: selftest
  USER: ADJ OQ-016 disposition = name-a-new-capture-target | notes: selftest
  USER: ADJ D3 loop lifetime = idle-until-ruling
All three fields round-trip. Scratch server killed (pid located via
ss -tlnp, port freed); real server re-verified 200; real docs/DECISIONS.md
git-clean throughout (git status --porcelain empty on it).

## T4. Page content law (what the user sees)
- Row 1 OQ-019: {accept-cited-dead-and-close-with-residue, fund-debugger-
  witness (budget consequence stated verbatim: scripted-mouse class spent
  REFUTED-ROUTES.md:465-467 AND the debugger class carries t288 (dbg build
  aborts bank-savestate restore) + t299 (3 sessions, 8 static legs zero) —
  funding buys a NEW instrument class, not a rerun), defer}.
- Row 2 OQ-016: {accept-cited-dead, name-a-new-capture-target, defer}.
- Row 3 D3: {idle-until-ruling, hygiene-loop, run-until-zero, stop
  (states 18/20 closed — re-derived from scripts/ledger_audit.py THIS
  session: rows=20 open=[OQ-016,OQ-019] closed=18), defer}.
- Cited-dead evidence collapsed under <details> per row, verbatim from
  OPEN-QUESTIONS.md t324 note / :269 / t332+t338 legs / _wip_t329 S4.
- NOTHING pre-checked, no recommended marker; the t329 S4 draft is described
  as DO-NOT-APPLY until an accept ruling lands. Do-not-answer-FOR-the-user
  constraint held.

## T5. Not done / limits (honest)
- No ruling exists yet; no row moved. Strict-close: this iteration closes
  NOTHING — it ships the mechanism. If no ruling arrives, STATE.md's standing
  note (hygiene audits <=1 per session) governs the next launch.
- The page's D3 context block quotes GOAL.txt and DECISIONS.md:182 verbatim;
  D3 was deferred 2026-11-09 "until D1/D2 work has landed" — both landed
  (D1 rulings 2026-11-09; D2 flip t365), so re-asking is legitimate, not
  re-litigating.
