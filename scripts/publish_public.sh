#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# publish_public.sh — build a pushable public tree FROM A FRESH CLONE.
# Never run against the working repo: it rewrites ALL history.
#
# Excludes (user decision 2026-11-10 + t371 landmine notes):
#   game/ extracted/        vendor copyrighted distribution files
#   work/                   capture corpus + live session state (gitignored
#                           anyway; listed for defense-in-depth)
#   artifacts/ascend_restored.bin, artifacts/functions_full.tsv
#                           derivatives of the vendor EXE (t371
#                           PUBLISH-CONDITIONAL); regenerable:
#                           python3 scripts/r1_restore_sites.py + Ghidra
#                           headless (see docs/re/loader.md)
#
# Usage: bash scripts/publish_public.sh <output-dir>
set -euo pipefail
OUT="${1:?usage: publish_public.sh <output-dir>}"
SRC="$(cd "$(dirname "$0")/.." && pwd)"

[ -e "$OUT" ] && { echo "REFUSING: $OUT exists (fresh dir required)" >&2; exit 2; }

git clone -q "$SRC" "$OUT"
cd "$OUT"

# NOTE: do NOT pre-stage removals with `git rm --cached` — a dirty index makes
# filter-branch refuse ("Your index contains uncommitted changes"). The
# --index-filter below performs the removal per commit. (Verified 2026-11-11.)

FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --prune-empty \
    --index-filter 'git rm -r -q --cached --ignore-unmatch \
      game extracted work archive/user-saves \
      artifacts/ascend_restored.bin artifacts/functions_full.tsv' \
    --env-filter 'export GIT_AUTHOR_NAME="Weyland Smith" GIT_COMMITTER_NAME="Weyland Smith";
      if [ -n "${GITHUB_USER:-}" ]; then
        export GIT_AUTHOR_EMAIL="$GITHUB_USER@users.noreply.github.com" GIT_COMMITTER_EMAIL="$GITHUB_USER@users.noreply.github.com";
      fi' -- --all >/dev/null

# 1b. HISTORY SCRUB (t383): a tip-only redaction of a personal email leaves it
# inside old blobs (MEASURED 2026-11-12: 25 historical copies of
# docs/re/_license_draft_t372.md held the pre-t383 address). Rewrite every
# blob across all history. NOTE: this box's git filter-branch has NO
# --blob-filter (that flag belongs to git-filter-repo, not installed) — first
# attempt exit 1 with usage text. --tree-filter works; sed is scoped to the
# ONE path that ever held the address. The sed eats the LOCAL PART too
# ([A-Za-z0-9._%+-]* before the domain pattern) — an earlier
# [[:space:][:punct:]] class stopped at '@' and would have leaked the
# username.
SCRUB_PATTERN="${SCRUB_PATTERN:-[ISP-DOMAIN]}"
SCRUB_PATHS="${SCRUB_PATHS:-docs/re/_license_draft_t372.md}"
TREE_SED=""
for p in $SCRUB_PATHS; do
    TREE_SED="$TREE_SED [ -f \"$p\" ] && sed -i -e 's/[A-Za-z0-9._%+-]*${SCRUB_PATTERN}[A-Za-z0-9.-]*/[REDACTED-EMAIL]/g' \"$p\" || true;"
done
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --tree-filter "$TREE_SED" -- --all >/dev/null

# filter-branch keeps refs/original backups; without this the vendor blobs
# survive gc and the strip is cosmetic (VERIFIED 2026-11-11: 100M->9.7M).
git for-each-ref --format='delete %(refname)' refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now -q

# ---- verification gates (fail closed) -------------------------------------
V=$(git rev-list --objects --all | grep -cE '^.* (game/|extracted/|work/|artifacts/ascend_restored\.bin)' || true)
[ "$V" = "0" ] || { echo "FAIL: $V vendor-path objects remain in history" >&2; exit 3; }
# t383 gate: NO blob in the rewritten history may contain the scrub pattern
# (batch cat-file; per-commit git grep over rev-list timed out at 300 s).
git rev-list --objects --all | cut -d' ' -f1 | sort -u | \
  xargs -r git cat-file --batch 2>/dev/null > /tmp/pubpush_blobscan.$$ || true
if grep -a "$SCRUB_PATTERN" /tmp/pubpush_blobscan.$$ > /dev/null; then
    rm -f /tmp/pubpush_blobscan.$$
    echo "FAIL: scrub pattern '$SCRUB_PATTERN' still present in some blob" >&2; exit 5
fi
rm -f /tmp/pubpush_blobscan.$$
git checkout -q . 2>/dev/null || true
for keep in rewrite/src/game/campaign.cpp docs/re LICENSE NOTICE README.md; do
    [ -e "$keep" ] || { echo "FAIL: $keep missing from stripped tree" >&2; exit 4; }
done
echo "OK: vendor-free history, $(git rev-list --objects --all | wc -l) objects, $(du -sh .git | cut -f1) .git, tree intact."
echo "Next (USER-gated): git remote remove origin; git remote add origin <your-github-url>; git push -u origin main"
