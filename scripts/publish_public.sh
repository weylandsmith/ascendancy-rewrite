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

git rm -r -q --cached --ignore-unmatch \
    game extracted work \
    artifacts/ascend_restored.bin artifacts/functions_full.tsv

FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --prune-empty \
    --index-filter 'git rm -r -q --cached --ignore-unmatch \
      game extracted work \
      artifacts/ascend_restored.bin artifacts/functions_full.tsv' -- --all >/dev/null

# filter-branch keeps refs/original backups; without this the vendor blobs
# survive gc and the strip is cosmetic (VERIFIED 2026-11-11: 100M->9.7M).
git for-each-ref --format='delete %(refname)' refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now -q

# ---- verification gates (fail closed) -------------------------------------
V=$(git rev-list --objects --all | grep -cE '^.* (game/|extracted/|work/|artifacts/ascend_restored\.bin)' || true)
[ "$V" = "0" ] || { echo "FAIL: $V vendor-path objects remain in history" >&2; exit 3; }
git checkout -q . 2>/dev/null || true
for keep in rewrite/src/game/campaign.cpp docs/re LICENSE NOTICE README.md; do
    [ -e "$keep" ] || { echo "FAIL: $keep missing from stripped tree" >&2; exit 4; }
done
echo "OK: vendor-free history, $(git rev-list --objects --all | wc -l) objects, $(du -sh .git | cut -f1) .git, tree intact."
echo "Next (USER-gated): git remote remove origin; git remote add origin <your-github-url>; git push -u origin main"
