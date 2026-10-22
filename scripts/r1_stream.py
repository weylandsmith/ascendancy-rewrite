#!/usr/bin/env python3
"""r1_stream.py — shared STREAMING observation layer over live-timeline.jsonl.

WHY THIS EXISTS (t85b): a multi-sitting capture's jsonl grows to gigabytes
(191k lines / 4.3 GB banked by the OQ-010/021/023 playcap). Loading it into
a list costs MEASURED ~65 MB per 1,000 observations (every in-game line
carries up to 107 x 177-u16 ship windows) -> projected ~12 GB on 16 GB: the
t85 combat analyzer was OOM-killed (signal 9, "Killed", after swap thrash).
This layer keeps ONLY a small offset index in RAM and yields parsed rows one
at a time; consecutive-pair diffing analyzers need prev+cur, not the world.

DATA-HYGIENE LAWS, each measured on the banked stream before adoption:
  * ORDER LAW: sittings re-launched watchers/collectors that appended
    interleaved (twelve stale watcher processes were found running, up to 6
    days old). Wall-clock file order is NOT observation order. Trusted order =
    (file_mtime_ns, file, byte-offset).
  * DEDUP LAW: keep the FIRST line per (file, file_mtime_ns). A watcher bug
    (a `seen = set()` re-init after the jsonl re-ingest, FIXED t85b) banked
    73,052 duplicate rows across sittings.
  * STALE-INSTANCE LAW (mechanism identified t85b from the banked mtime
    ladder): the user reattaches by launching ANOTHER dosbox instance that
    picks up "Return to Current Game". Both instances autosave into the same
    OUT/save ring. The stale instance's autosaves are always one End-Turn
    BEHIND the live one (it loaded from the savefile, and only advances when
    its player window ends a turn), then resume from the loaded turn when it
    finally follows (banked example: live at t=780..782 while the stale
    instance re-banked t=692/693/695/719 thousands of times over days, each
    of its resumption jumps one turn below live). A running campaign never
    ends a turn at a turn number BELOW the highest trusted turn, so in
    trusted order: turn < running max turn -> stale-instance autosave,
    dropped, counted, REPORTED (never silently). CAVEAT: if the user
    deliberately loads an older save mid-sitting, that IS a real rewind —
    rerun with trust=False and pair rows by wall-clock instead.

Usage:  for row in observations(run_dir, stats=stats): ...
stats (optional dict) receives rows/dups/stale/bad/trusted counts and a
frozen-turn histogram of dropped echoes. Ring-dir fallback is NOT duplicated
here — analyzers keep their existing S.timeline() fallback for pre-watcher
runs.
"""
import json, os

JSONL = "live-timeline.jsonl"


def _scan_scalars(line):
    """Cheap header scan (json.dumps default separators are a fixed format
    the watcher itself writes). Returns (file, turn, mtime_ns) or None."""
    i = line.find('"file": "')
    if i < 0:
        return None
    i += 8
    j = line.find('"', i)
    fn = line[i:j]
    i = line.find('"turn": ')
    if i < 0:
        return None
    i += 8
    j = line.find(",", i)
    try:
        turn = int(line[i:j])
    except ValueError:
        return None
    mt = 0
    i = line.find('"file_mtime_ns": ')
    if i >= 0:
        i += 17
        j = line.find(",", i)
        if j < 0:
            j = line.find("}", i)
        try:
            mt = int(line[i:j])
        except ValueError:
            mt = 0
    return fn, turn, mt


def build_index(path):
    """One cheap scan -> sorted [(mtime_ns, file, offset)], dup count, bad count.
    No json.loads here (full-parse over 4.3 GB is ~60 s; scan is ~20 s)."""
    entries, seen, n_bad = [], set(), 0
    with open(path, "r", errors="replace") as f:
        while True:
            off = f.tell()
            line = f.readline()
            if not line:
                break
            s = _scan_scalars(line)
            if s is None:
                n_bad += 1
                continue
            fn, turn, mt = s
            key = (fn, mt)
            if key in seen:
                continue
            seen.add(key)
            entries.append((mt, fn, off))
    entries.sort()
    return entries, len(seen), n_bad


def observations(run_dir, trust=True, stats=None):
    """Yield parsed observation dicts in trusted order, one at a time.
    trust=True applies the STALE-ECHO law; trust=False yields all (deduped)."""
    path = os.path.join(run_dir, JSONL)
    if not os.path.isfile(path):
        return
    entries, n_uniq, n_bad = build_index(path)
    st = stats if stats is not None else {}
    n_dups_dropped = 0
    st.setdefault("rows_seen_total", n_uniq + n_bad)  # unique lines; true raw
    st["lines_indexed"] = len(entries)
    st["bad_lines"] = n_bad
    n_stale = n_trusted = 0
    frozen = {}
    watermark = 0
    with open(path, "r", errors="replace") as f:
        for mt, fn, off in entries:
            f.seek(off)
            try:
                j = json.loads(f.readline())
            except Exception:
                st["bad_lines"] = st.get("bad_lines", 0) + 1
                continue
            if j.get("turn", 0) <= 0:
                continue                      # title slots untrusted (t82 law)
            if trust and j["turn"] < watermark:
                n_stale += 1
                frozen[j["turn"]] = frozen.get(j["turn"], 0) + 1
                continue
            watermark = max(watermark, j["turn"])
            n_trusted += 1
            yield j
    st["stale_echoes"] = n_stale
    st["frozen_echo_turns"] = frozen
    st["trusted"] = n_trusted


def echo_note(stats):
    """One-line human summary of what the trust law removed, for analyzers."""
    s = []
    if stats.get("lines_indexed"):
        s.append(f"{stats['lines_indexed']} unique slot-observations indexed")
    if stats.get("stale_echoes"):
        fr = stats.get("frozen_echo_turns") or {}
        tops = ", ".join(f"t={t}x{c}" for t, c in
                         sorted(fr.items(), key=lambda x: -x[1])[:4])
        s.append(f"{stats['stale_echoes']} STALE-ECHO rows dropped "
                 f"(frozen autosaves: {tops}; stale-instance law, see "
                 f"r1_stream docstring — if you LOADED an older save mid-run "
                 f"that is real, rerun with trust off)")
    if stats.get("bad_lines"):
        s.append(f"{stats['bad_lines']} unparsable lines skipped")
    s.append(f"{stats.get('trusted', 0)} trusted points")
    return "; ".join(s)
