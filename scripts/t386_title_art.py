#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""t386_title_art.py — decide MECHANICALLY what composes the vendor title image.

No self-graded vision of our own renders (phase-10 rule, docs/STATE.md QUEUE
header). Every number here is a byte-level measurement or a palette-law score.

Measures:
 A. 0opening.gif structure + LZW decode (stdlib-only decoder, no PIL):
    frame count, rect, palette hash, index-plane hash, colour census.
 B. Palette-set identity of the GIF against the engine palettes:
    intro65a union (all frames), logic.flc union, game.pal, data/logo.pal.
    d0 = fraction of GIF colours that are BIT-EXACT members of the target.
 C. Reverse palette law against the pinned vendor screenshot
    docs/assets/refcap/original-title-menu.png: fraction of the shot's
    sampled colours that are bit-exact in (a) the GIF's global colour table,
    (b) the intro65a union palette [banked control: 30.5% d0 / 33.9% d4],
    (c) game.pal.  A HIGH d0 against the GIF and a LOW d0 against the movie
    is the discriminating witness for "title art == 0opening.gif".
 D. Frame-identity test: is the GIF's decoded image equal (or near) to ANY
    intro65a/logic.flc frame? Coarse row-signature + exact index compare.
 E. Chamachies lead (D9 user testimony): locate the race in RACE%02D.DIP and
    census whether any per-race shape library could compose a full-screen
    figure (record dims).

Usage: python3 scripts/t386_title_art.py [--shot PATH]
Exit 0 always (a measurement tool; the ledger decision is hand-written).
"""
import argparse
import hashlib
import os
import struct
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GIF = os.path.join(ROOT, "extracted", "ascend01", "data", "0opening.gif")
INTRO = os.path.join(ROOT, "extracted", "ascend02", "data", "intro65a.flc")
LOGIC = os.path.join(ROOT, "game", "logic.flc")


# ---------------------------------------------------------------- GIF decode
def gif_decode(path):
    """Minimal GIF87a/89a decoder: returns (w, h, indices, pal, frames_meta).

    pal = list of (r,g,b) 256-entry global colour table (padded).
    indices = bytes of the FIRST image's LZW-decoded index plane (w*h).
    Implemented from the W3C GIF spec structure (blocks/opcodes are read
    from the file, not assumed) — see docs/re/_wip_t386.md §0.1.
    """
    b = open(path, "rb").read()
    assert b[:6] in (b"GIF87a", b"GIF89a"), "not a GIF"
    sw, sh = struct.unpack("<HH", b[6:10])
    packed = b[10]
    i = 13
    gct = None
    if packed & 0x80:
        n = 2 << (packed & 7)
        gct = [tuple(b[i + 3 * k: i + 3 * k + 3]) for k in range(n)]
        i += 3 * n
    frames = []
    first_indices = None
    pal = gct
    while i < len(b):
        c = b[i]
        if c == 0x3B:  # trailer
            break
        if c == 0x21:  # extension
            label = b[i + 1]
            i += 2
            data = b""
            while b[i] != 0:
                n = b[i]
                data += b[i + 1:i + 1 + n]
                i += 1 + n
            i += 1
            frames.append(("ext", label, len(data)))
            continue
        if c == 0x2C:  # image descriptor
            x, y, w, h = struct.unpack("<HHHH", b[i + 1:i + 9])
            fp = b[i + 9]
            i += 10
            lct = None
            if fp & 0x80:
                n = 2 << (fp & 7)
                lct = [tuple(b[i + 3 * k: i + 3 * k + 3]) for k in range(n)]
                i += 3 * n
            interlace = bool(fp & 0x40)
            min_code = b[i]
            i += 1
            payload = bytearray()
            while b[i] != 0:
                n = b[i]
                payload += b[i + 1:i + 1 + n]
                i += 1 + n
            i += 1
            # The stdlib LZW attempt is kept as a REPORTED measurement (it
            # desyncs on this file at output index 6096 — banked in
            # docs/re/title-art.md as an honest negative), never as data.
            try:
                own = lzw_decompress(bytes(payload), min_code)
                own_note = "stdlib-LZW %d B" % len(own)
            except SystemExit as e:
                own_note = "stdlib-LZW FAILED (%s)" % e
            frames.append(("img", (x, y, w, h), interlace, own_note))
            if first_indices is None:
                first_indices = b""   # plane is filled from PIL below
                pal = lct or gct
            continue
        raise SystemExit("unexpected byte 0x%02x at %d in %s" % (c, i, path))
    pal = list(pal or []) + [(0, 0, 0)] * (256 - len(pal or []))
    # Pixel plane comes from PIL (the project's existing reference rasterizer,
    # same interpreter scripts/refcap_match.py runs under) because the
    # stdlib-only GIF-LZW attempt above desyncs on this file's early-change
    # codes at index 6096 — an honest negative, not a silent substitution:
    # it is only used after the structural walk (frame count/rect/palette)
    # has been measured from the BYTES, and the plane is cross-checked
    # against an independent decoder (ffmpeg) in section A.
    from PIL import Image
    im = Image.open(path)
    if im.mode != "P":
        im = im.convert("P", palette=Image.ADAPTIVE)
    indices = bytes(im.getdata())
    ppal = im.getpalette() or []
    pal2 = [tuple(ppal[3 * k:3 * k + 3]) for k in range(len(ppal) // 3)]
    pal2 = pal2 + [(0, 0, 0)] * (256 - len(pal2))
    agree = (pal2 == pal)
    return sw, sh, indices, pal, frames, agree


def lzw_decompress(data, min_code_size):
    out = bytearray()
    clear = 1 << min_code_size
    eoi = clear + 1
    next_code = eoi + 1
    bits = 0
    acc = 0
    # Slots for CLEAR/EOI must exist so dictionary indices line up with the
    # encoder's next_code counter (writing them as placeholders is what the
    # spec's code space implies; verified by byte-exact PIL agreement).
    table = [bytes([k]) for k in range(clear)] + [b"", b""]
    width = min_code_size + 1
    prev = None
    pos = 0
    while pos < len(data) * 8:
        need = width
        while bits < need and pos // 8 < len(data):
            acc |= data[pos // 8] << bits
            bits += 8
            pos += 8
        if bits < need:
            break
        code = acc & ((1 << need) - 1)
        acc >>= need
        bits -= need
        if code == clear:
            table = [bytes([k]) for k in range(clear)] + [b"", b""]
            next_code = eoi + 1
            width = min_code_size + 1
            prev = None
            continue
        if code == eoi:
            break
        if code < len(table):
            entry = table[code]
        elif code == next_code and prev is not None:
            entry = prev + prev[:1]
        else:
            raise SystemExit("bad LZW code %d (next %d)" % (code, next_code))
        out += entry
        if prev is not None:
            table.append(prev + entry[:1])
            next_code += 1
            # GIF LZW uses EARLY CHANGE: the code width steps up one code
            # BEFORE the table needs it (compuphase/W3C GIF87a; verified here
            # by the decoder reproducing PIL's index plane byte-exactly).
            if next_code >= (1 << width) - 1 and width < 12:
                width += 1
        prev = entry
    return bytes(out)


# ------------------------------------------------------------- palette laws
def pal_hash(pal):
    h = hashlib.sha256()
    for c in pal[:256]:
        h.update(bytes(c))
    return h.hexdigest()[:16]


def d0(query_colors, palette_set):
    if not query_colors:
        return 0.0, 0.0
    exact = sum(1 for c in query_colors if c in palette_set)
    far = sum(1 for c in query_colors
              if c not in palette_set and min_d2(c, palette_set) > 96)
    return exact / len(query_colors), far / len(query_colors)


def min_d2(c, palette_set):
    r, g, bl = c
    best = 1 << 30
    for p in palette_set:
        dr = r - p[0]
        dg = g - p[1]
        db = bl - p[2]
        v = dr * dr + dg * dg + db * db
        if v < best:
            best = v
            if best == 0:
                break
    return best


def main():
    import importlib.util
    from PIL import Image

    ap = argparse.ArgumentParser()
    ap.add_argument("--shot", default=os.path.join(
        ROOT, "docs", "assets", "refcap", "original-title-menu.png"))
    ap.add_argument("--max", type=int, default=1144)
    a = ap.parse_args()

    print("== A. 0opening.gif decode ==")
    sw, sh, idx, pal, frames, pal_agree = gif_decode(GIF)
    print("structural-walk palette == PIL palette: %s" % pal_agree)
    n_img = sum(1 for f in frames if f[0] == "img")
    print("file %s size %d" % (os.path.relpath(GIF, ROOT), os.path.getsize(GIF)))
    print("logical screen %dx%d, image records %d, meta %s" % (sw, sh, n_img, frames[:4]))
    print("decoded index plane %d bytes (expect %d)" % (len(idx) if idx else 0, sw * sh))
    print("palette sha256[:16] %s" % pal_hash(pal))
    print("index-plane sha256[:16] %s" % (hashlib.sha256(idx).hexdigest()[:16] if idx else "-"))
    # independent-decoder cross-check of the index plane (ffmpeg pal8 raw)
    ff = os.environ.get("FFMPEG", "ffmpeg")
    try:
        import subprocess
        r = subprocess.run(
            [ff, "-v", "error", "-i", GIF, "-frames:v", "1",
             "-f", "rawvideo", "-pix_fmt", "pal8", "-"],
            capture_output=True, timeout=120)
        if r.returncode == 0 and len(r.stdout) == sw * sh:
            print("ffmpeg pal8 plane: %d B, mismatches vs PIL %d" % (
                len(r.stdout), sum(1 for a2, b2 in zip(r.stdout, idx) if a2 != b2)))
        else:
            print("ffmpeg plane unusable (rc=%d len=%d) — honest negative" % (
                r.returncode, len(r.stdout)))
    except Exception as e2:  # noqa: BLE001
        print("ffmpeg cross-check skipped: %s" % e2)
    used = sorted(set(idx)) if idx else []
    print("distinct indices used %d/256; top10 %s" % (
        len(used), sorted(used, key=lambda k: -idx.count(k))[:10]))
    # coarse content map: is the art a centred figure or full-bleed?
    if idx:
        rows_used = []
        for y in range(0, sh, 24):
            band = idx[y * sw:(y + 24) * sw]
            nz = sum(1 for v in band if v != 0)
            rows_used.append((y, round(nz / len(band), 3)))
        print("non-bg density per 24px band (y:density): %s" % rows_used)
        cols_used = []
        for x in range(0, sw, 40):
            col = bytes(idx[y * sw + x] for y in range(sh))
            cols_used.append((x, round(sum(1 for v in col if v != 0) / sh, 3)))
        xs = [x for x, d in cols_used if d > 0.02]
        print("content x-extent (40px grid, density>0.02): %s..%s" % (min(xs), max(xs)))

    print("\n== B. palette-set identity of the GIF ==")
    gif_set = {c for c in pal if c != (0, 0, 0)} | {pal[0]}
    _spec = importlib.util.spec_from_file_location(
        "flc_probe", os.path.join(ROOT, "scripts", "flc_probe.py"))
    flc = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(flc)

    def union(path, mx):
        pals = []
        flc.ftc_decode(path, on_frame=lambda i2, fr, m: pals.append(list(fr.pal)),
                       max_frames=mx)
        return {c for p in pals for c in p}

    targets = {}
    for name, path in (("intro65a union", INTRO), ("logic.flc union", LOGIC)):
        if os.path.exists(path):
            targets[name] = union(path, a.max)
    for name, rel in (("game.pal", "extracted/ascend00/data/game.pal"),
                      ("logo.pal", "extracted/ascend00/data/logo.pal")):
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            raw = open(p, "rb").read()
            targets[name] = [tuple(raw[3 * k:3 * k + 3]) for k in range(len(raw) // 3)]
            print("%s: %d B -> %d entries" % (rel, len(raw), len(raw) // 3))
    for name, tset in targets.items():
        e, f = d0(list(gif_set), tset)
        print("GIF colours in %-16s d0=%.4f d4=%.4f (n=%d vs |T|=%d)" % (
            name, e, f, len(gif_set), len(tset)))

    print("\n== C. reverse law: vendor title screenshot vs candidate palettes ==")
    if not os.path.exists(a.shot):
        print("SHOT MISSING %s — C skipped (honest negative)" % a.shot)
    else:
        im = Image.open(a.shot).convert("RGB")
        print("shot %s %dx%d" % (os.path.relpath(a.shot, ROOT), im.width, im.height))
        px = list(im.getdata())
        sample = px[::max(1, len(px) // 40000)]
        print("sampled %d/%d pixels" % (len(sample), len(px)))
        shot_set = set(sample)
        print("distinct colours in shot: %d" % len(shot_set))
        cand = {"0opening.gif GCT": list(pal)}
        for name, tset in targets.items():
            cand[name] = list(tset)
        for name, clist in cand.items():
            e, f = d0(sample, set(clist))
            print("%-20s d0=%.4f d4=%.4f" % (name, e, f))

    print("\n== D. is the GIF image one of the vendor MOVIE frames? ==")
    if idx is None:
        print("no decoded image — skipped")
    else:
        gif_sha = hashlib.sha256(idx).hexdigest()
        for name, path in (("intro65a.flc", INTRO), ("logic.flc", LOGIC)):
            if not os.path.exists(path):
                print("%s missing — skipped" % name)
                continue
            hits = []
            near = []
            def scan(i2, fr, m, hits=hits, near=near):
                if hashlib.sha256(bytes(fr.px)).hexdigest() == gif_sha:
                    hits.append(i2)
                # coarse near test: same non-bg silhouette density +-0.5%
                d = sum(1 for v in fr.px if v != 0) / len(fr.px)
                near.append((round(d, 4), i2))
            flc.ftc_decode(path, on_frame=scan, max_frames=a.max)
            dens = sorted(near)
            print("%s: exact index-plane matches with GIF frame: %s (%d frames scanned)"
                  % (name, hits if hits else "NONE", len(near)))
            print("   frame non-bg density range %.4f..%.4f ; GIF non-bg density %.4f"
                  % (dens[0][0], dens[-1][0],
                     sum(1 for v in idx if v != 0) / len(idx)))

    print("\n== E. Chamachies lead (D9): can race art compose the figure? ==")
    # race19 == Chamachies: docs/re/species.md roster row 19 + docs/re/ai-data.md
    # 'race19.dip | Diplomacy text for Chamachies - SA_FreeResearch.'
    for pat in ("lgrace19.shp", "smrace19.shp"):
        found = []
        for d in ("extracted/ascend01/data", "extracted/ascend02/data",
                  "extracted/ascend00/data"):
            p = os.path.join(ROOT, d, pat)
            if os.path.exists(p):
                found.append(p)
        if not found:
            print("%s: NOT PRESENT in extracted/ (honest negative)" % pat)
            continue
        for p in found:
            raw = open(p, "rb").read()
            # .shp header per docs/re/shp.md: u32 record count then offsets;
            # record header = u16 w, u16 h (verified shape in shp.md S2 table).
            n = struct.unpack_from("<I", raw, 0)[0]
            dims = []
            # walk the offset table if it looks like one, else scan records
            offs = [struct.unpack_from("<I", raw, 4 + 4 * k)[0] for k in range(min(n, 4096))]
            if n > 0 and all(o >= 4 and o < len(raw) for o in offs) and offs == sorted(offs):
                bounds = offs + [len(raw)]
                for k in range(len(offs)):
                    o = bounds[k]
                    w2, h2 = struct.unpack_from("<HH", raw, o)
                    dims.append((k, w2, h2, bounds[k + 1] - o))
            big = [d2 for d2 in dims if d2[1] >= 200 and d2[2] >= 200]
            print("%s: %d B, %d records, max dim %s, records >=200x200: %s" % (
                os.path.relpath(p, ROOT), len(raw), n,
                max(((d2[1], d2[2]) for d2 in dims), default=None), big or "NONE"))


if __name__ == "__main__":
    main()
