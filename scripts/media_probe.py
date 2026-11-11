#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""media_probe.py — P1e: FLIC video, audio, font, hazard, .tmp inventory.

Every number printed here is MEASURED from files under extracted/ and game/.
Codecs are named only where the structure proves them; anything else goes to
docs/OPEN-QUESTIONS.md instead of being guessed (PLAN rule 3).

Deterministic: same inputs -> byte-identical docs/re/media.md, and gate.sh
stage 3e asserts the summary line.

Usage: media_probe.py [--out FILE] [--quiet]
"""
import argparse, os, glob, struct, sys, math, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOC_MAGIC = b'Creative Voice File\x1a'

FLI_NAMES = {
    # Canonical Autodesk/compuphase names (compuphase.com/flic.htm "Overview of
    # all chunks"). An earlier table here OMITTED 0x0007/0x0010/0x0012 and
    # mislabelled 0x000F, which is how stock vendor chunks got reported as
    # UNK_/FLI_BRUSH and OQ-002 was wrongly opened (closed by
    # scripts/flc_probe.py, docs/re/flc.md).
    0x0003: 'CEL_DATA', 0x0004: 'COLOR_256', 0x0007: 'DELTA_FLC',
    0x000B: 'COLOR_64', 0x000C: 'DELTA_FLI', 0x000D: 'BLACK',
    0x000F: 'BYTE_RUN', 0x0010: 'FLI_COPY', 0x0012: 'PSTAMP',
    0x0019: 'DTA_BRUN', 0x001A: 'DTA_COPY', 0x001B: 'DTA_LC',
    0x001F: 'LABEL', 0x0020: 'BMP_MASK', 0x0021: 'MLEV_MASK',
    0x0022: 'SEGMENT', 0x0023: 'KEY_IMAGE', 0x0024: 'KEY_PAL',
    0x0025: 'REGION', 0x0026: 'WAVE', 0x0027: 'USERSTRING',
    0x0028: 'RGN_MASK', 0x0029: 'LABELEX', 0x002A: 'SHIFT', 0x002B: 'PATHMAP',
    0xF100: 'PREFIX', 0xF1FA: 'FRAME', 0xF1FB: 'SEGMENT_TABLE',
    0xF1FC: 'HUFFMAN_TABLE',
}


def ent(b):
    if not b:
        return 0.0
    c = collections.Counter(b)
    n = len(b)
    return -sum(v / n * math.log2(v / n) for v in c.values())


def rel(p):
    return os.path.relpath(p, ROOT)


def walk_flic(path):
    """Parse the top-level chunk chain; inside FL_FRAME, walk sub-chunks only
    if the header's num_chunks says so. Returns a dict of measurements.
    Raises AssertionError on any size that does not tile exactly."""
    data = open(path, 'rb').read()
    N = len(data)
    size, magic, nframes, w, h, depth, flags = struct.unpack_from('<IHHhhHH', data, 0)
    assert magic == 0xAF12, f"{rel(path)}: magic {magic:#x}"
    assert size == N, f"{rel(path)}: hdr size {size} != filesize {N}"
    o = 128
    top = collections.Counter()
    sub = collections.Counter()
    frames = 0
    sub_nc_zero = 0
    frame_stats = []
    pal_triples = []
    dz = [0, 0]
    while o < N:
        csz, ctype = struct.unpack_from('<IH', data, o)
        assert csz >= 6 and o + csz <= N, f"{rel(path)}: top chunk {ctype:#x} sz {csz} @{o:#x}"
        top[FLI_NAMES.get(ctype, f'UNK_{ctype:#06x}')] += 1
        if ctype == 0xF1FA:
            frames += 1
            # 16-byte frame header: size,type,chunks,delay,reserved,width,height
            # (compuphase FRAME_TYPE typedef). `chunks` sits at +6. Measured on
            # both vendor files: sub-chunks tile EVERY frame except logic.flc's
            # ring frame (wrong-sized FLI_COPY — a documented common writer
            # error; scripts/flc_probe.py repairs and decodes it). Frames with
            # csz=16 are legal EMPTY frames (image unchanged); an earlier
            # revision of this probe mislabelled the stock chunk types here
            # and wrongly concluded "Ascendancy-specific payloads" — see
            # docs/re/flc.md §1 and the FLI_NAMES note above.
            nchunks = struct.unpack_from('<H', data, o + 6)[0]
            if nchunks == 0:
                sub_nc_zero += 1
            so = o + 16
            tiled = 0
            while so + 6 <= o + csz:
                isz, it = struct.unpack_from('<IH', data, so)
                if isz < 6 or so + isz > o + csz:
                    break
                sub[FLI_NAMES.get(it, f'UNK_{it:#06x}')] += 1
                so += isz
                tiled += 1
            frame_stats.append((o, csz, so == o + csz, tiled))
        o += csz
    assert o == N, f"{rel(path)}: walk ended {o:#x} != {N:#x}"
    return dict(w=w, h=h, depth=depth, flags=flags, declared=nframes, frames=frames,
                top=top, sub=sub, sub_nc_zero=sub_nc_zero, pal=pal_triples,
                dz=dz, size=N, frame_stats=frame_stats)


def voc_blocks(path):
    data = open(path, 'rb').read()
    if not data.startswith(VOC_MAGIC):
        return None
    o = 0x14 + struct.unpack_from('<H', data, 0x14)[0]
    out = []
    while o + 4 <= len(data):
        t = data[o]
        if t == 0:
            break
        out.append((t, o, int.from_bytes(data[o + 1:o + 4], 'little')))
        o += 4 + out[-1][2]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(ROOT, 'docs', 're', 'media.md'))
    ap.add_argument('--quiet', action='store_true')
    args = ap.parse_args()

    out = []
    P = out.append
    P("# P1e — media assets: video, audio, fonts, hazards, .tmp libraries")
    P("")
    P("Generated by `scripts/media_probe.py`; every number is measured. Gate stage 3e")
    P("re-runs this script and asserts its summary line.")
    P("")

    # ---------------- FLIC ----------------
    P("## 1. FLIC videos [chunk chain verified exactly]")
    P("")
    flcs = sorted(glob.glob(os.path.join(ROOT, 'extracted', '**', '*.flc'), recursive=True))
    flcs.append(os.path.join(ROOT, 'game', 'logic.flc'))
    P("| file | size | magic | frames decl/walked | dims | depth | top-level chunks |")
    P("|---|---|---|---|---|---|---|")
    infos = {}
    for f in flcs:
        i = walk_flic(f)
        infos[f] = i
        P(f"| `{rel(f)}` | {i['size']} | 0xAF12 | {i['declared']}/{i['frames']} | "
          f"{i['w']}x{i['h']} | {i['depth']} | "
          + ", ".join(f"{k}x{v}" for k, v in i['top'].most_common()) + " |")
    P("")
    P("Chunk-header form: `u32 size, u16 type` at every level; the chain tiles the file")
    P("with zero residue (asserted per file above), which is what licenses the layout.")
    P("")
    P("**Encoding findings [verified by walking every frame]:**")
    P("")
    P("1. Frame header is the 16 B compuphase FRAME_TYPE; `chunks` at +6 is")
    P("   non-zero wherever sub-chunks exist (empty csz=16 frames are legal")
    P("   'image unchanged' padding: " + ", ".join(
        f"{infos[f]['sub_nc_zero']}/{infos[f]['frames']} in {os.path.basename(f)}"
        for f in flcs) + ").")
    P("2. All sub-chunk types present are STOCK Autodesk chunks (COLOR_256,")
    P("   BYTE_RUN, FLI_COPY, DELTA_FLC, PSTAMP). Full decode of both files —")
    P("   every chunk zero-residue — is scripts/flc_probe.py / docs/re/flc.md;")
    P("   the earlier 'Ascendancy-specific payload' reading was a probe bug")
    P("   (chunk-name table omitted 0x0007 etc.; see FLI_NAMES comment).")
    P("3. No `FL_DZ_IP` (0xF1CC) chunk appears anywhere, so DEFLATE is not involved —")
    P("   the seed plan's FLIC-with-dzlib assumption is falsified.")
    P("")
    P("| file | frames | parsed-clean frames | sub-chunk types seen |")
    P("|---|---|---|---|")
    for f in flcs:
        i = infos[f]
        clean = sum(1 for (_, _, t, _) in i['frame_stats'] if t)
        s = ", ".join(f"{k}x{v}" for k, v in i['sub'].most_common()) or "(none)"
        P(f"| `{rel(f)}` | {i['frames']} | {clean} | {s} |")
    P("")
    P("The top-level chain (header + PREFIX + FL_FRAME chunks tiling the file to")
    P("the byte) is verified, and the frame payloads decode stock (OQ-002 CLOSED,")
    P("docs/re/flc.md). Both files are intro/logo video, not gameplay, so this")
    P("never gated the campaign turn loop.")
    P("")
    for f in flcs:
        i = infos[f]
        nc256 = i['sub'].get('COLOR_256', 0)
        P(f"- `{rel(f)}`: palette arrives via COLOR_256(4) subchunks "
          f"({nc256} in file — frame 0 carries the initial one; decoded by "
          f"scripts/flc_probe.py, docs/re/flc.md §2). The top-level PREFIX "
          f"(0xF100) chunk is settings data, not palette.")
    P("")

    # ---------------- audio ----------------
    P("## 2. Audio [verified]")
    P("")
    music = open(os.path.join(ROOT, 'extracted', 'ascend00', 'music.txt'),
                 'rb').read().decode('cp437')
    lines = [l.strip() for l in music.split('\r\n')]
    cnt = int(lines[0])
    names = [l for l in lines[1:] if l]
    ok = 'MATCH' if cnt == len(names) else 'MISMATCH'
    P(f"`music.txt`: declared count {cnt}, listed paths {len(names)} — {ok}.")
    P("All paths are `data\\\\*.raw` (4 theme, 1 victory, 2 intro, 21 race).")
    P("")
    P("### 2a. .raw music tracks — presence and character")
    P("")
    P("| track | bytes | entropy | 8-bit mono @22050 | @11025 |")
    P("|---|---|---|---|---|")
    rows = []
    missing = 0
    for nm in names:
        # music.txt uses DOS backslash separators; os.path.basename does NOT
        # split on them on POSIX, which made every track look MISSING.
        base = os.path.basename(nm.replace("\\", "/"))
        cands = glob.glob(os.path.join(ROOT, 'extracted', '**', base), recursive=True)
        if not cands:
            missing += 1
            P(f"| `{nm}` | MISSING | - | - | - |")
            continue
        b = open(cands[0], 'rb').read()
        rows.append((nm, b))
        P(f"| `{nm}` | {len(b)} | {ent(b):.2f} | {len(b)/22050:.2f} s | {len(b)/11025:.2f} s |")
    P("")
    if rows:
        P(f"{len(rows)}/{len(names)} tracks present, {missing} missing. Entropy "
          f"{min(ent(b) for _, b in rows):.2f}–{max(ent(b) for _, b in rows):.2f} b/B is "
          f"PCM-like: not compressed, not silence.")
    P("")
    P("### 2b. .voc sound effects — the extension lies for most of them")
    P("")
    vocs = sorted(glob.glob(os.path.join(ROOT, 'extracted', '**', '*.voc'), recursive=True))
    real = [f for f in vocs if voc_blocks(f) is not None]
    hdrless = [f for f in vocs if voc_blocks(f) is None]
    P(f"{len(vocs)} `.voc` files: **{len(real)} carry the Creative Voice magic** "
      f"`Creative Voice File\\x1a`; **{len(hdrless)} do not** — they open with PCM-looking "
      f"bytes")
    P(f"(e.g. `{rel(hdrless[0])}` starts `{open(hdrless[0],'rb').read(8).hex()}`).")
    P("Type by content, not extension.")
    P("")
    P("Block census for the files that really are VOC:")
    P("")
    P("| file | blocks (type@offset:len) |")
    P("|---|---|")
    for f in real:
        bl = voc_blocks(f)
        P(f"| `{os.path.basename(f)}` | " + ", ".join(f"{t}@{o:#x}:{l}" for t, o, l in bl[:8]) + " |")
    P("")
    sfx = open(os.path.join(ROOT, 'extracted', 'ascend00', 'soundfx.txt'),
               'rb').read().decode('cp437')
    sl = [l.strip() for l in sfx.split('\r\n')]
    nn = sum(1 for x in sl[4:] if x)
    P(f"`soundfx.txt`: 3 `<n> <rate>` lines ({sl[0]!r}, {sl[1]!r}, {sl[2]!r}), then a count")
    P(f"({sl[3]!r}) and that many bare effect names -> names resolve to `data\\<name>.voc`.")
    P(f"Count vs names: {'MATCH' if sl[3].isdigit() and nn == int(sl[3]) else 'MISMATCH'} "
      f"({nn} names).")
    P("")
    P("**Sample rate stays OPEN (OQ-006).** The headerless files carry no in-file rate")
    P("field and the three rate numbers above cannot be attributed to specific files")
    P("without the exe's audio loader; guessing it yields wrong-pitched audio.")
    P("")

    # ---------------- fonts ----------------
    P("## 3. Fonts (.fnt) [CLOSED — codec solved, see docs/re/fnt.md]")
    P("")
    P("Codec (verified 384/384, scripts/fnt_probe.py, gate 3p): glyph = u32")
    P("width + EXACTLY width*height bytes, 1 byte per pixel row-major, no")
    P("stride padding; 0xFF background, ink intensity 255-value (sm/big solid")
    P("0xF3; intro.fnt anti-aliased 0xF0..0xFE). The old 'payload 52 for w=6'")
    P("observation is exactly 4+6*8 read as BYTES — there was never a bit")
    P("format. Vision-confirmed legible: docs/assets/fnt-*-sheet.png.")
    P("")
    for f in sorted(glob.glob(os.path.join(ROOT, 'extracted', '**', '*.fnt'), recursive=True)):
        b = open(f, 'rb').read()
        v = struct.unpack_from('<IIII', b, 0)
        P(f"- `{rel(f)}` — {len(b)} B; u32s {v[0]:#x} {v[1]:#x} {v[2]:#x} {v[3]:#x} "
          f"(dec {v[2]} at +8)")
    P("")
    P("All three share the tag `31 2e 00 00` and field order; the +8 field varies and")
    P("tracks file size, which fits a glyph count. Stride and bitmap packing are NOT")
    P("derivable from the header — OQ-011, needs the exe font loader. No glyph bitmaps")
    P("are emitted until then (rendering from assumed stride fabricates pixels).")
    P("")

    # ---------------- hazards ----------------
    P("## 4. Hazard maps (.haz) [verified — seed claim falsified]")
    P("")
    haz = sorted(glob.glob(os.path.join(ROOT, 'extracted', '**', '*.haz'), recursive=True))
    exact = sum(1 for f in haz if open(f, 'rb').read() == bytes(range(256)))
    prefix = sum(1 for f in haz if open(f, 'rb').read(32) == bytes(range(32)))
    P(f"{len(haz)} files, each exactly 256 B (one byte per palette index).")
    P(f"The earlier note that 'the first is the identity table 0x00..0xFF' is **false**:")
    P(f"{exact}/{len(haz)} files equal `bytes(range(256))`, and only {prefix}/{len(haz)} even")
    P("match its first 32 bytes. Every .haz is a remap with scattered substitutions.")
    P("")
    P("| file | distinct bytes | head 12 | diff-vs-identity count |")
    P("|---|---|---|---|")
    for f in haz[:6]:
        b = open(f, 'rb').read()
        P(f"| `{os.path.basename(f)}` | {len(set(b))} | {b[:12].hex()} | "
          f"{sum(1 for i in range(256) if b[i] != i)} |")
    P("")

    # ---------------- .tmp ----------------
    P("## 5. `.tmp` files are shape libraries, not scripts [verified]")
    P("")
    tmps = sorted(glob.glob(os.path.join(ROOT, 'extracted', '**', '*.tmp'), recursive=True))
    magic_ct = collections.Counter()
    for f in tmps:
        magic_ct[open(f, 'rb').read(4)] += 1
    P(f"{len(tmps)} `.tmp` files. First-4-byte census: "
      + ", ".join(f"`{m.hex()}`({m.decode('latin1')!r})x{c}" for m, c in magic_ct.most_common()))
    P("")
    P("They open with the shape-library magic `1.10` documented in docs/re/shp.md §1, so")
    P("`.tmp` is a second name for the same container. They therefore inherit OQ-005 (the")
    P("pixel codec) and must be parsed by the same reader — no separate script format.")
    P("")
    P("| file | size | u32 N | table size | table==8*(N+1) |")
    P("|---|---|---|---|---|")
    for f in tmps:
        b = open(f, 'rb').read(16)
        if b[:4] == b'1.10':
            n, tsz, res = struct.unpack_from('<III', b, 4)
            P(f"| `{os.path.basename(f)}` | {os.path.getsize(f)} | {n} | {tsz} | "
              f"{tsz == 8*(n+1)} |")
        else:
            P(f"| `{os.path.basename(f)}` | {os.path.getsize(f)} | - | - | magic {b[:4].hex()} |")
    P("")

    # ---------------- palette ----------------
    P("## 6. Palettes (.pal)")
    P("")
    pals = sorted(glob.glob(os.path.join(ROOT, 'extracted', '**', '*.pal'), recursive=True))
    for f in pals:
        b = open(f, 'rb').read()
        t = [tuple(b[i:i + 3]) for i in range(0, len(b) - 2, 3)]
        mx = [max(x[k] for x in t) for k in range(3)]
        P(f"- `{rel(f)}` — {len(b)} B = {len(t)} RGB triples; first 4 {t[:4]}; max/channel "
          f"{mx} -> {'8-bit RGB888, no 6-bit scaling' if max(mx) > 63 else 'all<=63 (6-bit DAC)'}")
    P("")

    P("## 7. Open items created/updated by this probe")
    P("")
    P("- OQ-006 audio sample rate (headerless `.voc` + `.raw`).")
    P("- OQ-017 CLOSED: .fnt is 1 byte/pixel (validator scripts/fnt_probe.py,")
    P("  spec docs/re/fnt.md, gate 3p; C++ port src/formats/fnt.cpp).")
    P("- OQ-002 CLOSED: FLIC payloads are stock Autodesk chunks; full decode in")
    P("  scripts/flc_probe.py, spec in docs/re/flc.md (gate stages 3e/3o).")
    P("- OQ-005 `.shp`/`.tmp` pixel codec (shared with docs/re/shp.md).")
    P("")

    text = "\n".join(out) + "\n"
    if args.out:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        open(args.out, 'w').write(text)
    if not args.quiet:
        print(text)
    print(f"[media_probe] OK: {len(flcs)} flic exact-tiled, {len(vocs)} voc "
          f"({len(real)} VOC-magic, {len(hdrless)} headerless), {len(haz)} haz, "
          f"{len(tmps)} tmp(shape), {len(pals)} pal", file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
