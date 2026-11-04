# state-v2-full archive snapshot — 2026-11-03 (docs slim)

Taken before the 2026-11-03 documentation slim (STATE.md 4077->298 lines,
OPEN-QUESTIONS.md 1846->907, BLOCKED.md 615->~150, docs/re/_wip_*.md +
stop-report.md removed from the live tree). Everything the live docs dropped is
here, byte-identical to the working tree at snapshot time:

  STATE.md             md5 a2faccfb648418045b2647be66364f10
  OPEN-QUESTIONS.md    md5 e897be73e0fd4b06cb51aa0881c0ff5d
  BLOCKED.md           md5 2e7c0940e11e839390abb7c9ebf4c1a6
  stop-report.md       md5 5a061b7ce7b572bbaec67f494718b6cb
  wip/_wip_t*.md       153 per-iteration working notes (t12..t292), 1.3 MB

Verify: md5sum <file>. To find which iteration discovered X, grep wip/ then the
STATE.md LANDED blocks. The distilled laws (what the loop actually runs on)
remain live in docs/re/*.md — this archive is provenance + project history, not
a working surface. Slim rationale + user-facing decision surface:
docs/DECISIONS.md.
