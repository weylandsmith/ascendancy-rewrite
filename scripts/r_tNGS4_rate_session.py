#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""tNG-S CYCLE 4 R1 — PRODUCTION 1 s-cadence RATE witness (D22 steer).

Question (docs/re/_wip_tNGS.md S26-X2c): the vendor big newgame field
ANIMATES continuously (matched bright stars median 3.16 content-px/s on
refcaps). Is the PRODUCTION scratch session the same, and what is the
ANGULAR rate? D22 rules: both fields spin continuously, mouse position
irrelevant; ~5 s/circuit is an EYEBALL figure — the witness must measure,
not assume.

Method (anti-aliasing law banked S26-X2a: 12 s sampling is blind to a
field whose decorrelation time is ~1 s; sample at 1 s x 60 s):
  * production /usr/bin/dosbox-x, scratch work/r1/game-wp ONLY (asserted),
    fresh Xvfb :97, own x11vnc 5911, RFB offsets 80/100 (S18) — the exact
    C3-proven firing harness (run c3-20261122-215511).
  * fire New Game via B_click2 (250,295) (C3 PROVEN channel).
  * PARK THE CURSOR at (600,250): OUTSIDE the big field box
    FIELD_BOX=(17,12,324,320) and OUTSIDE the Begin cluster window
    BEGIN_BOX_640=(515,380,565,465) (D22 640-space ~x520-560 y382-461),
    and outside the menu band x95..405. S22's cursor-in-panel scope was
    the trap; D22 says mouse position is irrelevant but the harness must
    not be able to contaminate either measurement.
  * 61 grabs at 1 s cadence. Per step vs PREVIOUS frame and vs f1:
      - changed-px (RGB-safe min-of-zero-bins law, c3 script) for big
        field, Begin cluster, control strip (500,30,630,80);
      - bright-peak nearest-neighbour match (3x3-max, lum>350, tol 6 px)
        -> displacement median/p25/p75 (content px/s);
      - ANGULAR: matched pairs' dtheta about the box centre (cross/dot),
        per-step median -> deg/s witness (D22-requested single-blob-style
        arc fit over all matched pairs).
  * Frames are all SAVED (caps/frames/) so lag curves / rotation
    correlation can be recomputed offline without re-running.

Verdict targets:
  production field moved at 1 s cadence  => vendor law ports: continuous
      spin; rate = angular median (code cross-check: t416 +-2deg/tick at
      the t302 ~1/s pump = ~2 deg/s).
  production field STATIC at 1 s cadence => vendor-vs-production split:
      the scratch session never had the pump alive; port decision then
      needs the vendor rate only (documented seam).

SAFETY (GOAL.txt invariants): scratch only; headless; -time-limit 900;
kills ONLY recorded PIDs (never pkill -x dosbox-x — production ring
1470999; never pkill Xvfb -u — matches :9).
Exit: 0 = witness banked; 1 = negative; 2 = harness.
"""
import hashlib
import json
import os
import os.path as op
import shutil
import signal
import subprocess
import sys
import time

import numpy as np

ROOT = op.abspath(op.join(op.dirname(__file__), ".."))
sys.path.insert(0, op.join(ROOT, "scripts"))
import r293_move_session as R293                                # noqa: E402
from PIL import Image                                           # noqa: E402

SCRATCH = R293.SCRATCH
XV_BIN_SYS = shutil.which("x11vnc")
XV_DEB = op.join(ROOT, "work/r1/localdeb/root/usr/bin/x11vnc")
XV_LIB = op.join(ROOT, "work/r1/localdeb/root/usr/lib/x86_64-linux-gnu")
PROD_BIN = "/usr/bin/dosbox-x"
DISP = ":97"
VNC_PORT = 5911
XOFF, YOFF = 80, 100
NEWGAME_XY = (250, 295)
PARK_XY = (600, 250)
FIELD_BOX = (17, 12, 324, 320)          # vendor big field (S14/C3)
BEGIN_BOX = (515, 380, 565, 465)        # D22 Begin cluster, 640-space
CTRL_BOX = (500, 30, 630, 80)           # control strip (park spot is
                                         # (600,250), well below it)
N_SAMPLES = 61
CADENCE_S = 1.0


def log(logp, msg):
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    print(line, flush=True)
    with open(logp, "a") as fh:
        fh.write(line + "\n")


def orange_frac(im):
    if im is None:
        return -1.0
    px = im.load()
    tot = orange = 0
    for y in range(0, 330, 3):
        for x in range(0, 640, 4):
            r, g, b = px[x, y]
            tot += 1
            if r > 140 and g > 50 and b < 110 and r - b > 70:
                orange += 1
    return orange / max(1, tot)


def crop_px_changed(a, b, box):
    from PIL import ImageChops
    ca, cb = a.crop(box), b.crop(box)
    d = ImageChops.difference(ca, cb)
    h = d.histogram()
    npix = ca.size[0] * ca.size[1]
    unchanged = min(h[0], h[256], h[512])
    return npix - unchanged


def peaks(arr, lum_min=350.0):
    """3x3-max local peaks on an HxW luminance array. Returns Nx2 (x,y)."""
    h, w = arr.shape
    p = np.pad(arr, 1, mode="constant", constant_values=0.0)
    mx = p[1:-1, 1:-1].copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            np.maximum(mx, p[1 + dy:1 + dy + h, 1 + dx:1 + dx + w], out=mx)
    m = (arr >= mx) & (arr > lum_min)
    ys, xs = np.nonzero(m)
    return np.stack([xs, ys], axis=1).astype(float)


def match_stats(a_arr, b_arr, tol=6.0):
    """Nearest-neighbour peak match. Returns dict with n, disp percentiles,
    dtheta_deg percentiles (about box centre == array centre)."""
    pa, pb = peaks(a_arr), peaks(b_arr)
    out = {"n_a": int(len(pa)), "n_b": int(len(pb))}
    if len(pa) == 0 or len(pb) == 0:
        out["n"] = 0
        return out
    cy, cx = a_arr.shape[1] / 2.0, a_arr.shape[0] / 2.0
    cy = a_arr.shape[0] / 2.0
    d2 = ((pa[:, None, 0] - pb[None, :, 0]) ** 2 +
          (pa[:, None, 1] - pb[None, :, 1]) ** 2)
    i = np.argmin(d2, axis=1)
    dmin = np.sqrt(d2[np.arange(len(pa)), i])
    sel = dmin <= tol
    d = dmin[sel]
    out["n"] = int(sel.sum())
    if out["n"]:
        out["disp_med"] = round(float(np.median(d)), 2)
        out["disp_p25"] = round(float(np.percentile(d, 25)), 2)
        out["disp_p75"] = round(float(np.percentile(d, 75)), 2)
        q = pb[i[sel]]
        p = pa[sel]
        v1 = p - np.array([cx, cy])
        v2 = q - np.array([cx, cy])
        cross = v1[:, 0] * v2[:, 1] - v1[:, 1] * v2[:, 0]
        dot = v1[:, 0] * v2[:, 0] + v1[:, 1] * v2[:, 1]
        th = np.degrees(np.arctan2(cross, dot))
        # only stars with real radius contribute a meaningful angle
        r = np.hypot(v1[:, 0], v1[:, 1])
        ok = r >= 25.0
        if ok.sum():
            out["dth_n"] = int(ok.sum())
            out["dth_med"] = round(float(np.median(th[ok])), 3)
            out["dth_med_abs"] = round(float(np.median(np.abs(th[ok]))), 3)
    return out


def lum_arr(im, box):
    a = np.asarray(im.crop(box), dtype=np.float64)
    return 0.299 * a[:, :, 0] + 0.587 * a[:, :, 1] + 0.114 * a[:, :, 2]


class Grabber:
    def __init__(self, out):
        self.out = out
        self.no = 0

    def __call__(self, name):
        self.no += 1
        raw = op.join(self.out, f"_raw_{self.no:03d}_{name}.png")
        r = subprocess.run(["import", "-window", "root", raw],
                           capture_output=True, timeout=30,
                           env=dict(os.environ, DISPLAY=DISP))
        if r.returncode != 0:
            log(op.join(self.out, "session.log"),
                f"grab FAILED {name}: {r.stderr[:200]!r}")
            return None
        img = Image.open(raw).convert("RGB")
        return img.crop((XOFF, YOFF, XOFF + 640, YOFF + 480))


class Rfb:
    def __init__(self):
        import r287_vncinput as V
        self.V = V
        os.environ["RFB_PORT"] = str(VNC_PORT)
        V.PORT = VNC_PORT
        V.XOFF, V.YOFF = XOFF, YOFF
        self.s = None

    def open(self):
        self.s = self.V.session()
        return self.s is not None

    def move(self, x, y):
        self.V.ptr(self.s, x, y, 0)

    def click(self, x, y):
        self.move(x, y)
        time.sleep(0.25)
        self.V.ptr(self.s, x, y, 1)
        time.sleep(0.08)
        self.V.ptr(self.s, x, y, 0)

    def key(self, name):
        ks = self.V.KSYM[name]
        self.V.keyev(self.s, ks, 1)
        time.sleep(0.05)
        self.V.keyev(self.s, ks, 0)

    def close(self):
        try:
            time.sleep(0.15)
            self.s.close()
        except Exception:
            pass


def main():
    out = op.join(ROOT, "work", "r1",
                  f"tngs4-{time.strftime('%Y%m%d-%H%M%S')}")
    os.makedirs(op.join(out, "save"), exist_ok=True)
    os.makedirs(op.join(out, "caps", "frames"), exist_ok=True)
    logp = op.join(out, "session.log")
    rec = {"task": "tNGS4-R1", "out": out, "steps": [], "verdict": None,
           "park": PARK_XY, "cadence_s": CADENCE_S, "n": N_SAMPLES}

    def save():
        with open(op.join(out, "tngs4.json"), "w") as fh:
            json.dump(rec, fh, indent=1)

    assert op.abspath(SCRATCH).startswith(op.join(ROOT, "work")), SCRATCH
    assert not op.abspath(SCRATCH).startswith(op.join(ROOT, "game") + op.sep)
    assert op.exists(PROD_BIN)
    xv_bin = XV_BIN_SYS or (XV_DEB if op.exists(XV_DEB) else None)
    assert xv_bin, "no x11vnc"
    assert op.exists(R293.OCT29)
    md5 = hashlib.md5(open(R293.OCT29, "rb").read()).hexdigest()
    assert md5 == R293.OCT29_MD5, f"Oct-29 backup md5 drift {md5}"
    save()

    xv = child = vnc = None
    rfb = Rfb()
    grab = Grabber(out)
    try:
        shutil.copy2(R293.OCT29, op.join(SCRATCH, "RESUME.GAM"))
        low = op.join(SCRATCH, "resume.gam")
        if op.exists(low):
            os.rename(low, low + ".vendor-t4")

        conf = op.join(out, "session.conf")
        with open(conf, "w") as fh:
            fh.write(f"""[dosbox]
machine=svga_s3
memsize=16
captures={out}/caps
autosave=10 41-60
saveremark=false
[sdl]
output=x11
fullscreen=false
autolock=false
[mixer]
nosound=true
[autoexec]
MOUNT C {SCRATCH}
C:
ASCEND.EXE
""")
        xv = subprocess.Popen(
            ["Xvfb", DISP, "-screen", "0", "800x600x24"],
            stdout=open(op.join(out, "xvfb.out"), "wb"),
            stderr=subprocess.STDOUT)
        time.sleep(2)
        assert op.exists(f"/tmp/.X11-unix/X{DISP[1:]}"), "Xvfb failed"

        env = dict(os.environ, DISPLAY=DISP, TERM="xterm")
        for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
            env.pop(k, None)
        child = subprocess.Popen(
            [PROD_BIN, "-conf", conf, "-nogui", "-savedir",
             op.join(out, "save"), "-time-limit", "900"],
            stdout=open(op.join(out, "dosbox.out"), "wb"),
            stderr=subprocess.STDOUT, cwd=out, env=env, close_fds=True)
        rec["dosbox_pid"] = child.pid
        log(logp, f"spawned PRODUCTION dosbox-x pid={child.pid}")

        vnc = subprocess.Popen(
            [xv_bin, "-display", DISP, "-rfbport", str(VNC_PORT),
             "-localhost", "-nopw", "-forever", "-shared"],
            stdout=open(op.join(out, "x11vnc.out"), "wb"),
            stderr=subprocess.STDOUT,
            env=dict(os.environ, LD_LIBRARY_PATH=XV_LIB))
        rec["vnc_pid"] = vnc.pid
        time.sleep(3)

        t0 = time.time()
        hits = 0
        while time.time() - t0 < 240:
            if child.poll() is not None:
                rec["verdict"] = (f"HARNESS: dosbox exited early rc="
                                  f"{child.returncode}")
                save()
                return 2
            time.sleep(5)
            f = orange_frac(grab("titlepoll"))
            log(logp, f"title poll orange={f:.3f} ({time.time()-t0:.0f}s)")
            if f > 0.20:
                hits += 1
                if hits >= 2:
                    break
            else:
                hits = 0
        else:
            rec["verdict"] = "NEGATIVE: title never appeared (240s)"
            save()
            return 1
        time.sleep(25)
        base = grab("title_settled")
        rec["title_orange"] = round(orange_frac(base), 3)
        save()

        if not rfb.open():
            rec["verdict"] = "HARNESS: RFB connect failed"
            save()
            return 2

        # RUNG A: hover first (C3 run 215511 fired only AFTER the hover
        # move landed — teal rows 240..270 -> 280..310; run 005304 clicked
        # 3x WITHOUT the hover settle and every pair missed).
        rfb.move(*NEWGAME_XY)
        time.sleep(3)
        rec["steps"].append({"rung": "A_hover"})
        save()
        # fire New Game (C3-proven B_click2; retry the pair up to 3x, then
        # RFB Return fallback)
        fired = False
        for attempt in range(1, 4):
            rfb.click(*NEWGAME_XY)
            time.sleep(2)
            rfb.click(*NEWGAME_XY)
            time.sleep(8)
            im = grab(f"post_fire{attempt}")
            o = orange_frac(im)
            rec["steps"].append({"rung": f"B_click2_x{attempt}",
                                 "orange_after": round(o, 3)})
            save()
            log(logp, f"B_click2 attempt {attempt} orange={o:.3f}")
            if o < 0.20:
                fired = True
                break
        if not fired:
            rfb.key("Return")
            time.sleep(8)
            o = orange_frac(grab("post_fire_return"))
            rec["steps"].append({"rung": "E_rfb_return",
                                 "orange_after": round(o, 3)})
            save()
            log(logp, f"E_rfb_return orange={o:.3f}")
            fired = o < 0.20
        if not fired:
            rec["verdict"] = f"NEGATIVE: New Game did not fire (orange {o:.3f})"
            save()
            return 1

        # park cursor OUTSIDE both fields, then let it settle
        rfb.move(*PARK_XY)
        time.sleep(3)
        f1 = grab("ng_f01")
        if f1 is None:
            rec["verdict"] = "HARNESS: grab failed on newgame"
            save()
            return 2
        f1.save(op.join(out, "caps", "frames", "f001.png"))

        prev = f1
        f1_big = lum_arr(f1, FIELD_BOX)
        f1_beg = lum_arr(f1, BEGIN_BOX)
        rec["samples"] = [{"i": 1, "wall": time.strftime("%H:%M:%S")}]
        for i in range(2, N_SAMPLES + 1):
            time.sleep(max(0.0, CADENCE_S - 0.6))
            im = grab(f"ng_f{i:02d}")
            if im is None:
                break
            im.save(op.join(out, "caps", "frames", f"f{i:03d}.png"))
            big = lum_arr(im, FIELD_BOX)
            beg = lum_arr(im, BEGIN_BOX)
            e = {"i": i, "wall": time.strftime("%H:%M:%S"),
                 "field_vs_prev": crop_px_changed(prev, im, FIELD_BOX),
                 "begin_vs_prev": crop_px_changed(prev, im, BEGIN_BOX),
                 "ctrl_vs_prev": crop_px_changed(prev, im, CTRL_BOX),
                 "field_vs_f1": crop_px_changed(f1, im, FIELD_BOX),
                 "begin_vs_f1": crop_px_changed(f1, im, BEGIN_BOX),
                 "big_match": match_stats(f1_big, big),
                 "big_match_prev": match_stats(lum_arr(prev, FIELD_BOX), big),
                 "beg_match_prev": match_stats(lum_arr(prev, BEGIN_BOX), beg)}
            rec["samples"].append(e)
            prev = im
            save()
            log(logp, f"S {i} fvp={e['field_vs_prev']} bvp={e['begin_vs_prev']} "
                      f"ctrl={e['ctrl_vs_prev']} "
                      f"bigmatch={e['big_match_prev'].get('n', 0)}/"
                      f"{e['big_match_prev'].get('disp_med')} "
                      f"dth={e['big_match_prev'].get('dth_med')} "
                      f"begmatch={e['beg_match_prev'].get('n', 0)}/"
                      f"{e['beg_match_prev'].get('disp_med')}")

        # roll-up
        ss = rec["samples"][1:]
        if ss:
            med = lambda k: round(float(np.median([s[k] for s in ss])), 2)
            rec["rollup"] = {
                "n_steps": len(ss),
                "field_vs_prev_med": med("field_vs_prev"),
                "begin_vs_prev_med": med("begin_vs_prev"),
                "ctrl_vs_prev_med": med("ctrl_vs_prev"),
                "big_disp_med": round(float(np.median(
                    [s["big_match_prev"]["disp_med"] for s in ss
                     if s["big_match_prev"].get("n", 0) >= 3])), 2)
                    if any(s["big_match_prev"].get("n", 0) >= 3 for s in ss) else None,
                "big_dth_med": round(float(np.median(
                    [s["big_match_prev"]["dth_med"] for s in ss
                     if "dth_med" in s["big_match_prev"]])), 3)
                    if any("dth_med" in s["big_match_prev"] for s in ss) else None,
                "beg_disp_med": round(float(np.median(
                    [s["beg_match_prev"]["disp_med"] for s in ss
                     if s["beg_match_prev"].get("n", 0) >= 3])), 2)
                    if any(s["beg_match_prev"].get("n", 0) >= 3 for s in ss) else None,
            }
        moved = (rec.get("rollup", {}).get("field_vs_prev_med", 0) > 100 and
                 rec.get("rollup", {}).get("ctrl_vs_prev_med", 999) < 50)
        rec["verdict"] = ("PRODUCTION FIELD ANIMATES at 1 s cadence "
                          "(see rollup)" if moved else
                          "NEGATIVE: production field static at 1 s cadence "
                          "while vendor animates => pump-alive split; port "
                          "rate must come from vendor law + code")
        save()
        log(logp, f"VERDICT {rec['verdict']}")
        return 0
    finally:
        rfb.close()
        for p in (vnc, xv, child):
            if p is None:
                continue
            try:
                os.kill(p.pid, signal.SIGKILL)
                log(logp, f"SIGKILL recorded pid={p.pid}")
            except Exception:
                pass
        save()


if __name__ == "__main__":
    sys.exit(main())
