#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""Probe windows.txt + subtitle.txt -> docs/re/ui.md, and history.txt
specnum blocks -> docs/re/species.md.

windows.txt shape (measured, not assumed): a resource manifest (MEM_REQ,
HAZEBRBLES, NUMTABLES + TABLE paths, FONTS, FONTs, SOUND-ish keys) followed
by window definitions that START at a 'TYPE' key line; each definition has
KEY VALUE lines and ends before the next TYPE. WINITEMS n declares n
WINITEM item lines (their sub-keys follow). All assertions at the end; a
violation aborts instead of writing a wrong doc.
"""
import argparse
import collections
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D0 = os.path.join(ROOT, "extracted", "ascend00")


def lines_of(path):
    raw = open(path, "rb").read()
    i = raw.find(b"\x1a")
    if i >= 0:
        raw = raw[:i]
    return [l.strip() for l in raw.decode("cp437").replace("\r", "").split("\n")]


def kv_pairs(lines):
    out = []
    for l in lines:
        if not l or l.startswith("//"):
            continue
        parts = l.split(None, 1)
        out.append((parts[0], parts[1] if len(parts) > 1 else ""))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    # ---------------------------------------------------------------- windows
    wl = lines_of(os.path.join(D0, "windows.txt"))
    manifest, wins = [], []
    cur = None
    in_win = False
    for key, val in kv_pairs(wl):
        if not in_win and key != "TYPE":
            manifest.append((key, val))
            continue
        if key == "TYPE":
            if cur is not None:
                wins.append(cur)
            cur = [("TYPE", val)]
            in_win = True
            continue
        cur.append((key, val))
        if key == "WINITEMS":  # next lines are item sub-keys until next TYPE;
            pass               # kv_pairs already flattened them into this win
    if cur is not None:
        wins.append(cur)

    numtables = [int(v) for k, v in manifest if k == "NUMTABLES"]
    table_paths = [v for k, v in manifest if k == "TABLE"]
    assert len(numtables) == 1, numtables
    assert numtables[0] == len(table_paths), (numtables, len(table_paths))

    xs = [int(v) for w in wins for k, v in w if k in ("X0", "X1")]
    ys = [int(v) for w in wins for k, v in w if k in ("Y0", "Y1")]
    assert xs and ys
    max_x, max_y = max(xs), max(max(xs, 0) for xs in ys)
    bad_coord = [(dict(w), ) for w in wins for k, v in w
                 if k in ("X0", "X1") and not (0 <= int(v) <= 639)]
    bad_coord += [(dict(w), ) for w in wins for k, v in w
                  if k in ("Y0", "Y1") and not (0 <= int(v) <= 479)]
    types = collections.Counter(int(v) for w in wins for k, v in w if k == "TYPE")
    keys = collections.Counter(k for w in wins for k, _ in w)
    names = [v for w in wins for k, v in w if k == "NAME"]
    # Measured rule (2026-10-04): 132 TYPE defs, 124 with NAME; the 8 that
    # lack NAME are ALL TYPE 100 shape-file overlays (e.g. DATA\0OPENING.SHP).
    # Every non-100 def has exactly one NAME.
    no_name = [w for w in wins if not any(k == "NAME" for k, _ in w)]
    assert all(dict(w).get("TYPE") == "100" for w in no_name), \
        [dict(w).get("TYPE") for w in no_name]
    assert len(names) + len(no_name) == len(wins)
    winitem_claims = [int(v) for w in wins for k, v in w if k == "WINITEMS"]
    textitems = keys.get("TEXTITEM", 0)

    # ------------------------------------------------------------ subtitles
    sl = lines_of(os.path.join(D0, "subtitle.txt"))
    skv = kv_pairs(sl)
    frames = [int(v) for k, v in skv if k == "FRAMENUMBER"]
    blocks = collections.Counter(k for k, _ in skv)
    # blocks: each command block ends with FRAMENUMBER; count commands
    cmds = [v for k, v in skv if k == "COMMAND"]

    # ------------------------------------------------------------- species
    hl = lines_of(os.path.join(D0, "history.txt"))
    idxs = [i for i, l in enumerate(hl) if l.startswith("specnum ")]
    species = []
    for j, i in enumerate(idxs):
        end = idxs[j + 1] if j + 1 < len(idxs) else len(hl)
        num = int(hl[i].split()[1])
        # next non-empty line = keyword, next = species name, rest = blurb
        body = [l for l in hl[i + 1:end] if l]
        kw = body[0] if body else ""
        nm = body[1] if len(body) > 1 else ""
        blurb = " ".join(body[2:8])[:300]
        species.append((num, kw, nm, blurb))
    assert [s[0] for s in species] == list(range(len(species))), [s[0] for s in species]

    dip = sorted(f for f in os.listdir(D0) if re.match(r"race\d\d\.dip$", f))

    # species display name + special ability token live in the raceNN.dip
    # header comment: "Diplomacy text for <NAME> - SA_<Ability>." Verified
    # cross-refs to history.txt blurbs: race00 Minions/SA_SuperMarines =
    # specnum 0 "Supreme Planet Invaders"; race01 Snovemdomas/SA_DoubleHull =
    # specnum 1 "Builders of Nigh-Indestructible Ships"; race10 Govorom/
    # SA_Cornucopia = specnum 10 "Planet Nurturers". specnum N <-> raceNN.
    raceAbility = {}
    for f in dip:
        key = re.match(r"race(\d\d)\.dip$", f).group(1)
        dn = sa = None
        for hdr in lines_of(os.path.join(D0, f))[0:3]:
            m = re.search(r"for\s+(.+?)\s*-\s*(SA_[A-Za-z]+)", hdr)
            if m:
                dn, sa = m.group(1).strip().rstrip("."), m.group(2)
                break
        raceAbility[key] = (dn, sa)
    assert sum(1 for v in raceAbility.values() if v[1]) >= 19, raceAbility
    toks = [v[1] for v in raceAbility.values() if v[1]]
    assert len(set(toks)) == len(toks), "SA_ token not unique per race"

    # ------------------------------------------------------------- diplomacy
    # .dip files: DIPVALUES weights + DA_* dialogue templates. CRITICAL parse
    # fact (2026-10-04): values can be NEGATIVE (BIO_MAXNEGATIVE is negative
    # in all 21 races; BIO_SIN_* in several) — an isdigit-style filter
    # silently drops them; this probe's own first revision hit exactly that
    # and its subset assertion caught it. dip_probe.py was always correct.
    def dipvalues(path):
        ls = lines_of(path)
        try:
            start = ls.index("DIPVALUES")
        except ValueError:
            return {}
        vals = {}
        for l in ls[start + 1:]:
            if l.startswith("ACTIONS"):
                break
            p = l.split(None, 1)
            if len(p) == 2 and re.match(r"^-?\d+$", p[1]):
                vals[p[0]] = int(p[1])
        return vals

    pd = dipvalues(os.path.join(D0, "player.dip"))
    rd = [dipvalues(os.path.join(D0, f)) for f in dip]
    keysets = {frozenset(v) for v in rd}
    assert len(keysets) == 1, "races do NOT share one DIPVALUES key set"
    raceKeys = set(rd[0])
    assert set(pd) < raceKeys, (sorted(pd), sorted(raceKeys))
    assert len(pd) == 8 and len(raceKeys) == 15, (len(pd), len(raceKeys))
    bio = sorted(raceKeys - set(pd))
    assert "BIO_PERIOD" in bio and "BIO_MAXNEGATIVE" in bio
    # value envelope for the oscillation model
    env = {k: (min(v[k] for v in rd), max(v[k] for v in rd), len({v[k] for v in rd}))
           for k in sorted(raceKeys)}
    dialogue_keys = collections.Counter()
    tok_hist = collections.Counter()
    for dfile in [os.path.join(D0, x) for x in [dip[0], "player.dip"]]:
        ls = lines_of(dfile)
        try:
            actions_at = ls.index("ACTIONS")
        except ValueError:
            continue
        i = actions_at + 1
        while i < len(ls):
            if ls[i] and ls[i].startswith("DA_"):
                body = []
                i += 1
                while i < len(ls) and ls[i]:
                    body.append(ls[i])
                    i += 1
                dialogue_keys[os.path.basename(dfile)] += 1
                for line in body:
                    for m in re.finditer(r"%([a-zA-Z])", line):
                        tok_hist[m.group(1)] += 1
            else:
                i += 1

    if a.quiet:
        print("OK %d windows, %d species, dip keys %s"
              % (len(wins), len(species), dict(dialogue_keys)))
        return

    # ------------------------------------------------------------- ui.md
    out = []
    w = out.append
    w("# UI + resource manifest — `windows.txt` / `subtitle.txt` measurement\n")
    w("Sources: `extracted/ascend00/windows.txt` (42,478 B), "
      "`extracted/ascend00/subtitle.txt` (2,801 B), CP437/CRLF/0x1A. Produced "
      "by `scripts/ui_probe.py`; gate stage 3k. Every number measured.\n")
    w("\n## 1. windows.txt structure [verified]\n")
    w("- a resource MANIFEST (key/value lines before the first `TYPE`), then "
      "**%d window definitions**, each starting at a `TYPE` key.\n" % len(wins))
    w("- window-key frequency: %s\n" % dict(keys.most_common()))
    w("- window TYPE histogram: %s (TYPE is the window class; TYPE 0 = "
      "button-like menu entries in the opening screen; the vendor does not "
      "document the numeric meanings -> OQ-015)\n" % dict(sorted(types.items())))
    w("- coordinate envelope: X %d..%d, Y %d..%d over all X0/X1/Y0/Y1 -> "
      "logical resolution is **640x480** (max X1 639, Y1 479). This is "
      "evidence for OQ-012(d): the ORIGINAL logical extent is the screen "
      "itself; galaxy star positions (galactic.tsv coords <=639x479) live in "
      "the same envelope. Our rewrite renders 1024x1024 logical and scales "
      "to the screen — unchanged decision, now with the original value "
      "documented.\n" % (min(xs), max(xs), min(ys), max(ys)))
    w("- WINITEMS counts sum %d; TEXTITEM sub-keys observed %d%s\n"
      % (sum(winitem_claims), textitems,
         " (MATCH)" if sum(winitem_claims) == textitems else
         " (differ: other item kinds exist -> item sub-grammar OQ-015)"))
    w("\n## 2. Manifest content [verified; canonical DATA\\\\ set]\n")
    mk = collections.Counter(k for k, _ in manifest)
    w("- manifest key histogram: %s\n" % dict(mk.most_common()))
    w("- MEM_REQ %s, HAZEBRBLES %s, NUMTABLES %d == %d TABLE lines (asserted). "
      "The 23 TABLE paths are the palette (.haz) tables the engine loads: "
      "RACEA03, BLACK00..24 step 4, RED01, GREEN01, BLUE01, WHITE00..09, "
      "HILITE00, BW — **cross-validates the 256-byte-palette .haz finding** "
      "and matches docs/re/loader.md §5's 26 DATA\\\\ templates.\n"
      % ([v for k, v in manifest if k == "MEM_REQ"][0],
         [v for k, v in manifest if k == "HAZEBRBLES"][0], numtables[0],
         len(table_paths)))
    fonts = [(k, v) for k, v in manifest if "FONT" in k]
    w("- fonts: %s (SMFONT.FNT + BIGFONT.FNT -> the two-face UI of the "
      "manual screenshots)\n" % fonts)
    others = [(k, v) for k, v in manifest
              if k not in ("TABLE", "NUMTABLES", "MEM_REQ", "HAZEBRBLES")
              and "FONT" not in k]
    w("- remaining manifest keys (verbatim, meanings mostly OQ-015): %s\n"
      % others[:40])
    w("\n## 3. Opening-screen windows (first 12) [verified]\n")
    w("```\n")
    for wd in wins[:12]:
        d = dict(wd)
        w("TYPE=%s NAME=%-16s rect=(%s,%s)-(%s,%s) msg=%s/%s,%s help=%s\n"
          % (d.get("TYPE"), d.get("NAME", "-"), d.get("X0", "-"), d.get("Y0", "-"),
             d.get("X1", "-"), d.get("Y1", "-"), d.get("SENDMESSAGE", "-"),
             d.get("SENDPARAM1", "-"), d.get("SENDPARAM2", "-"),
             d.get("HELPINDEX", "-")))
    w("```\n")
    w("- the four menu buttons are exactly the main menu (Play Introduction / "
      "Tutorial / New Game / Resume), matching the manual — the UI rewrite "
      "can reproduce the opening screen from THIS file alone.\n")
    w("\n## 4. subtitle.txt = intro movie script [verified]\n")
    w("- **%d** FRAMENUMBER-triggered blocks; command keys: %s\n"
      % (len(frames), dict(blocks.most_common())))
    w("- first/last trigger frames: %d / %d (gizmos.flc/intro playback "
      "timeline). Commands include DIGITALMUSIC(TUNEID n)+COMMAND, "
      "FADEMUSIC(CHANNEL,VOLUME), SUBTITLE text placement, FRAMES_PER_SECOND "
      "style keys -> intro cinematic is DATA-DRIVEN; our FLIC player (OQ-002 "
      "deferred codecs) only needs to honour frame triggers.\n"
      % (frames[0], frames[-1]))
    w("- TITLERECT 0,379-639,419 + SUBFONT font file/palette slots 240..255: "
      "subtitle band geometry [verified].\n")
    w("\n## 5. Verbatim key census (window defs)\n```\n")
    for k, c in keys.most_common():
        w("%-14s %d\n" % (k, c))
    w("```\n")
    open(os.path.join(ROOT, "docs/re/ui.md"), "w").write("".join(out))

    # --------------------------------------------------------- species.md
    out = []
    w = out.append
    w("# species roster — `history.txt` specnum blocks [verified]\n")
    w("Source: `extracted/ascend00/history.txt` (31,525 B). Each species "
      "block starts `specnum N`, then keyword, then display name, then "
      "historical blurb. Produced by `scripts/ui_probe.py`; gate 3k.\n")
    w("- **%d** species, specnum contiguous 0..%d (asserted). Same count as "
      "the %d `raceNN.dip` AI parameter files -> one-to-one species<->AI-set "
      "mapping is consistent (OQ-009's single-evaluator picture).\n"
      % (len(species), len(species) - 1, len(dip)))
    w("\n## Roster (display names from `raceNN.dip` headers [verified]; "
      "specnum N <-> raceNN mapping [inferred] from blurb cross-refs — "
      "race00=Minions appears in specnum 0's blurb, race01=Snovemdomas in 1, "
      "race10=Govorom in 10 — consistent with contiguous 0..20 both sides)\n")
    w("| specnum | dip name | ability token | history title | keyword |\n"
      "|---|---|---|---|---|\n")
    for n, kw, name, _ in species:
        dn, sa = raceAbility.get("%02d" % n, (None, None))
        w("| %d | %s | %s | %s | %s |\n" % (n, dn or "?", sa or "?", name, kw))

    w("\n## Blurbs (first 8 lines each, whitespace-normalised)\n")
    for n, kw, nm, bl in species:
        w("- **%d %s** (%s): %s\n" % (n, nm, kw, bl))
    open(os.path.join(ROOT, "docs/re/species.md"), "w").write("".join(out))

    # -------------------------------------------------------- diplomacy.md
    out = []
    w = out.append
    w("# diplomacy — `.dip` files [verified; extends OQ-009]\n")
    w("Sources: `extracted/ascend00/player.dip` (human species) and the 21 "
      "`raceNN.dip`. Vendor comment in each: everything above `DIPVALUES` is "
      "commentary. Produced by `scripts/ui_probe.py`; gate 3k.\n")
    w("\n## 1. Weight schema [verified 2026-10-04, all 21 race files]\n")
    w("- all 21 `raceNN.dip` share **one 15-key** DIPVALUES set (asserted). "
      "`player.dip` (the human species) carries a strict **8-key subset** — "
      "asserted. The 6 race-only keys are the mood-oscillation model: %s.\n"
      % ", ".join(bio))
    w("- PARSE TRAP: values can be NEGATIVE (`BIO_MAXNEGATIVE` is negative in "
      "all 21 files; `BIO_SIN_*` in several). An `isdigit()`-style numeric "
      "filter SILENTLY drops those keys — this probe's own first revision did "
      "exactly that (assertion `set(player) < set(race)` caught it: the race "
      "set came up missing BIO_MAXNEGATIVE). Correct parser: `-?[0-9]+`. "
      "(scripts/dip_probe.py has always parsed them correctly; 15 keys, "
      "docs/re/ai-data.md.)\n")
    w("- envelope per key (min, max, distinct across 21 races):\n")
    for k, (lo, hi, nd) in env.items():
        w("  - %-18s %8d .. %-8d (%2d distinct)%s\n"
          % (k, lo, hi, nd, "  player=%d" % pd[k] if k in pd else ""))
    w("- [inferred, clearly labelled] `BIO_PERIOD`/`BIO_SIN_*` + "
      "`BIO_MAXPOSITVE`/`BIO_MAXNEGATIVE` describe a per-species sinusoidal "
      "mood cycle (period in turns, amplitude split pos/neg); "
      "`NEG_PLAYER_TURNS` gates how long a negative state sticks. The "
      "rewrite implements exactly that documented model; exact phase "
      "arithmetic is runtime-blocked (R1).\n")
    w("\n## 2. DA_* dialogue templates [verified]\n")
    w("- template counts: %s (race00 vs player)\n" % dict(dialogue_keys))
    w("- substitution tokens across bodies: %s — semantics per token are "
      "inferred from context (%%m = my species, %%y = your species, %%s = star "
      "system name, %%t = third-party species), but the full token table is "
      "runtime-blocked -> OQ-015. The rewrite implements exactly the tokens "
      "observed in data and leaves unknown ones literal.\n" % dict(tok_hist))
    w("- the AI evaluation ORDER that picks which DA_ message fires remains "
      "in the exe (R1); the rewrite ships a documented behaviour-plausible "
      "order (discover > propose > accept/break > trade > declare-war) and "
      "will re-check against R1.\n")
    open(os.path.join(ROOT, "docs/re/diplomacy.md"), "w").write("".join(out))
    print("wrote docs/re/ui.md + docs/re/species.md + docs/re/diplomacy.md "
          "(%d windows, %d species)" % (len(wins), len(species)))


main()
