#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""tNGS cycle 3c — C3 CONTROL: PRODUCTION dosbox-x vs dbg input-deafness.

FAILURE CHAIN BEING CONTROLLED (docs/re/_wip_tNGS.md S17-S20):
  * xsend (XSendEvent) presses are SYNTHETIC on this SDL build: the
    XWarpPointer half moves the real cursor (hover repaints) but the press
    NEVER fires (S17, runs 151714/153216/153535).
  * With a LIVE RFB channel (x11vnc + LD_LIBRARY_PATH, S18) at the CORRECT
    offsets (80/100, S18) on the DBG build: hover lands on New Game and
    stays (vision 155718), guest RUNNING, yet double-click (S19) and key
    Return (S20, run 165042 orange=0.679) do NOT activate the row.
  * OPEN QUESTION this script decides: is the deafness the DBG BUILD or the
    FRESH-UNFOCUSED-XVFB ENVIRONMENT? Production (t439) has a proven firing
    RFB channel, so run the identical nav against /usr/bin/dosbox-x on a
    scratch copy at a fresh private Xvfb.

VERDICT LOGIC (measured = title orange fraction; title ~0.68, leaves when
< 0.20 — wait_title law r293:374):
  production LEAVES the title  => dbg build is INPUT-DEAF at fresh Xvfb;
      W1's dynamic half is dbg-instrument-limited -> W1 closes on the S14
      STATIC law (auto-latch 0x26dd1 fires iff state==3) with the named
      ceiling, and P4 ports with NO auto-spin for the newgame field.
      BONUS (only on this branch): two field grabs 12 s apart on the
      production newgame screen = a VISUAL spin witness for W1.
  production ALSO deaf        => the fresh-Xvfb unfocused-window class is
      the blocker (build-independent); same static-law close, ceiling named
      as the environment class instead of the build.

NAV LADDER (each rung recorded separately so the FIRST firing channel is
identified, not merely "something worked"):
  A RFB move(250,295)                    -> hover witness (band diff)
  B RFB click x2 (first=hover, 2nd=fire) -> orange
  C RFB press-HOLD 1.0 s                 -> orange
  D xsend key Return (XSetInputFocus)    -> orange
  E RFB  key Return (fires hovered row)  -> orange

SAFETY (GOAL.txt invariants + STATE.md 280-282):
  * mounts SCRATCH work/r1/game-wp ONLY (asserted, never game/)
  * OWN private Xvfb :97 + x11vnc 5911 (production :9/5910 untouched)
  * headless (-nogui), nosound, core=normal, -time-limit 900
  * kills ONLY recorded PIDs (self.child / self.vnc). NEVER pkill -x
    dosbox-x (matches the production ring 1470999), NEVER pkill Xvfb -u
  * bounded output dir, Oct-29 md5 asserted before copying RESUME.GAM
Exit: 0 = ran and verdict banked; 1 = negative (no verdict); 2 = harness.
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

ROOT = op.abspath(op.join(op.dirname(__file__), ".."))
sys.path.insert(0, op.join(ROOT, "scripts"))
import r293_move_session as R293                                # noqa: E402
from PIL import Image                                           # noqa: E402

SCRATCH = R293.SCRATCH                     # work/r1/game-wp
XV_BIN_SYS = shutil.which("x11vnc")
XV_DEB = op.join(ROOT, "work/r1/localdeb/root/usr/bin/x11vnc")
XV_LIB = op.join(ROOT, "work/r1/localdeb/root/usr/lib/x86_64-linux-gnu")
PROD_BIN = "/usr/bin/dosbox-x"
DISP = ":97"
VNC_PORT = 5911
XOFF, YOFF = 80, 100                       # fresh-Xvfb window origin (S18)
NEWGAME_XY = (250, 295)                    # fresh-title row 280..310 (S19)
FIELD_BOX = (17, 12, 324, 320)             # state==3 cosmos rect (S14)
CTRL_BOX = (400, 40, 630, 120)             # outside the field: noise floor


def log(logp, msg):
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    print(line, flush=True)
    with open(logp, "a") as fh:
        fh.write(line + "\n")


def orange_frac(im):
    """Same law as r293_move_session.orange_frac:129 (title ~0.68)."""
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


def teal_rows(im):
    """Hover band census (tNGS3 law, r_tNGS3_w1_session.teal_band): count
    px (r<40, g>55, b>60) per row; report rows with >50 hits."""
    if im is None:
        return []
    px = im.load()
    rows = []
    for y in range(100, 420):
        c = 0
        for x in range(95, 405, 3):
            r, g, b = px[x, y]
            if g > 55 and b > 60 and r < 40:
                c += 1
        if c > 50:
            rows.append(y)
    return rows


def band_changed(a, b):
    """Rows in 100..420 whose rendered content differs (hover witness)."""
    if a is None or b is None:
        return -1
    pa, pb = a.load(), b.load()
    rows = 0
    for y in range(100, 420):
        for x in range(95, 405, 8):
            if pa[x, y] != pb[x, y]:
                rows += 1
                break
    return rows


def crop_px_changed(a, b, box):
    """RGB-safe changed-pixel count. ImageChops.difference(...).histogram()
    on RGB has 768 bins (3 channels x 256); summing hist[0:256] subtracts
    only the RED channel's zeros, so the naive `sum - npix*3` form is ALWAYS
    -2*npix (measured this session: field=-189112 for a 307x308 crop). The
    correct count uses the per-channel zero-bins h[0],h[256],h[512]."""
    from PIL import ImageChops
    ca, cb = a.crop(box), b.crop(box)
    d = ImageChops.difference(ca, cb)
    h = d.histogram()
    npix = ca.size[0] * ca.size[1]
    unchanged = min(h[0], h[256], h[512])
    return npix - unchanged


class Grabber:
    """import -window root on DISP, crop the 640x480 game content."""

    def __init__(self, out):
        self.out = out
        self.no = 0

    def __call__(self, name):
        self.no += 1
        raw = op.join(self.out, f"_raw_{self.no:02d}_{name}.png")
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
    """Persistent RFB client to our OWN x11vnc (r287_vncinput primitives)."""

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

    def press(self, x, y):
        self.V.ptr(self.s, x, y, 1)

    def release(self, x, y):
        self.V.ptr(self.s, x, y, 0)

    def click(self, x, y):
        self.move(x, y)
        time.sleep(0.25)
        self.press(x, y)
        time.sleep(0.08)
        self.release(x, y)

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
                  f"c3-{time.strftime('%Y%m%d-%H%M%S')}")
    os.makedirs(op.join(out, "save"), exist_ok=True)
    os.makedirs(op.join(out, "caps"), exist_ok=True)
    logp = op.join(out, "session.log")
    rec = {"task": "tNGS3c-C3", "out": out, "steps": [], "verdict": None}

    def save():
        with open(op.join(out, "c3.json"), "w") as fh:
            json.dump(rec, fh, indent=1)

    # ---- preflight asserts (GOAL invariants) ----
    assert op.abspath(SCRATCH).startswith(op.join(ROOT, "work")), SCRATCH
    assert not op.abspath(SCRATCH).startswith(op.join(ROOT, "game") + op.sep)
    assert op.exists(PROD_BIN), "production dosbox-x missing"
    xv_bin = XV_BIN_SYS or (XV_DEB if op.exists(XV_DEB) else None)
    assert xv_bin, "no x11vnc (system or bundled)"
    rec["x11vnc"] = xv_bin
    assert op.exists(R293.OCT29)
    md5 = hashlib.md5(open(R293.OCT29, "rb").read()).hexdigest()
    assert md5 == R293.OCT29_MD5, f"Oct-29 backup md5 drift {md5}"
    save()

    xv = child = vnc = None
    rfb = Rfb()
    grab = Grabber(out)
    try:
        # ---- RESUME.GAM parity with the dbg sessions (menu geometry!) ----
        shutil.copy2(R293.OCT29, op.join(SCRATCH, "RESUME.GAM"))
        low = op.join(SCRATCH, "resume.gam")
        if op.exists(low):
            os.rename(low, low + ".vendor-c3")

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
        log(logp, f"spawned PRODUCTION dosbox-x pid={child.pid} disp={DISP}")

        vnc = subprocess.Popen(
            [xv_bin, "-display", DISP, "-rfbport", str(VNC_PORT),
             "-localhost", "-nopw", "-forever", "-shared"],
            stdout=open(op.join(out, "x11vnc.out"), "wb"),
            stderr=subprocess.STDOUT,
            env=dict(os.environ, LD_LIBRARY_PATH=XV_LIB))
        rec["vnc_pid"] = vnc.pid
        time.sleep(3)

        # ---- title wait (wait_title law: orange>0.20 twice) ----
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
        time.sleep(25)                       # let the menu fully settle
        base = grab("title_settled")
        rec["title_orange"] = round(orange_frac(base), 3)
        rec["title_teal_rows"] = teal_rows(base)
        save()
        log(logp, f"settled title orange={rec['title_orange']} "
                  f"teal={rec['title_teal_rows']}")

        if not rfb.open():
            rec["verdict"] = "HARNESS: RFB connect failed"
            save()
            return 2

        def step(label, act, settle=8):
            """Run one nav rung; record hover + orange AFTER it."""
            before = orange_frac(grab(f"pre_{label}")) if label == "A" else None
            act()
            time.sleep(settle)
            im = grab(f"post_{label}")
            o = orange_frac(im)
            e = {"rung": label, "orange_after": round(o, 3),
                 "teal_rows_after": teal_rows(im)}
            if label == "A":
                e["orange_before"] = round(before, 3)
                e["hover_rows_changed"] = band_changed(base, im)
            rec["steps"].append(e)
            save()
            log(logp, f"RUNG {label}: orange={o:.3f} teal={e['teal_rows_after']}"
                      + (f" hoverrows={e.get('hover_rows_changed')}"
                         if label == "A" else ""))
            return o

        # A: hover witness (proves the RFB channel is live on THIS session)
        step("A_hover", lambda: rfb.move(*NEWGAME_XY), settle=3)
        # B: click pair (first=hover, second=fire)
        o = step("B_click2", lambda: (rfb.click(*NEWGAME_XY), time.sleep(2),
                                      rfb.click(*NEWGAME_XY)), settle=8)
        fired = o < 0.20
        fired_rung = "B_click2" if fired else None
        # C: 1-s press-hold (only if B failed)
        if not fired:
            def hold():
                rfb.move(*NEWGAME_XY)
                time.sleep(0.4)
                rfb.press(*NEWGAME_XY)
                time.sleep(1.0)
                rfb.release(*NEWGAME_XY)
            o = step("C_hold1s", hold, settle=8)
            fired, fired_rung = (o < 0.20, "C_hold1s") if o < 0.20 else (False, None)
        # D: xsend key Return (XSetInputFocus first — S19 fallback)
        if not fired:
            def xk():
                # xsend.c signature: xsend TITLE (key KEYSYM [ch]|...) — the
                # first arg is the window TITLE (r1_t260 law), and xsend
                # XSetInputFocuses the window before sending (S19 note).
                subprocess.run([op.join(ROOT, "tools", "xsend"),
                                "DOSBox-X", "key", "Return"],
                               capture_output=True, timeout=20,
                               env=dict(os.environ, DISPLAY=DISP))
            o = step("D_xsend_return", xk, settle=8)
            fired, fired_rung = (o < 0.20, "D_xsend_return") if o < 0.20 else (False, None)
        # E: RFB key Return (fires the hovered row, t287 law)
        if not fired:
            o = step("E_rfb_return", lambda: rfb.key("Return"), settle=8)
            fired, fired_rung = (o < 0.20, "E_rfb_return") if o < 0.20 else (False, None)

        rfb.close()

        if fired:
            rec["verdict"] = (f"PRODUCTION FIRES via {fired_rung} "
                              f"(orange {rec['title_orange']} -> "
                              f"{rec['steps'][-1]['orange_after']}) => the "
                              "DBG BUILD is input-deaf at fresh Xvfb; W1 "
                              "dynamic half is dbg-instrument-limited")
            # SPIN WITNESS (argv[1:] = n_samples interval_s). Production
            # reaches the newgame screen, so W1's dynamic half is testable
            # WITHOUT the debugger: sample the state==3 cosmos rect over a
            # baseline long enough that the t416 +-2deg/tick law at the ~1/s
            # pump (t302) would rotate the field by n*interval degrees.
            # Control box OUTSIDE the field separates twinkle/repaint from
            # motion. Pixel-changed counts use the RGB-safe law (min of the
            # three zero-bins), NOT the histogram-sum form (always degenerate
            # on RGB — measured -2*npix this session).
            try:
                n = int(sys.argv[1]) if len(sys.argv) > 1 else 2
                iv = float(sys.argv[2]) if len(sys.argv) > 2 else 12.0
                frames = []
                for i in range(n):
                    im = grab(f"ng_spin_{i+1}")
                    if im is None:
                        break
                    frames.append(im)
                    rec.setdefault("spin_px", []).append({
                        "i": i + 1,
                        "wall": time.strftime("%H:%M:%S"),
                        "field": crop_px_changed(frames[0], im, FIELD_BOX),
                        "ctrl": crop_px_changed(frames[0], im, CTRL_BOX)})
                    save()
                    log(logp, f"SPIN {i+1}/{n} "
                              f"field={rec['spin_px'][-1]['field']} "
                              f"ctrl={rec['spin_px'][-1]['ctrl']}")
                    if i + 1 < n:
                        time.sleep(iv)
                rec["spin_baseline_s"] = (n - 1) * iv
                rec["spin_expected_deg"] = round((n - 1) * iv, 1)
            except Exception as e:
                rec["spin_error"] = str(e)[:200]
        else:
            rec["verdict"] = ("PRODUCTION ALSO DEAF (all 5 rungs; orange "
                              f"stuck at {rec['steps'][-1]['orange_after']}) "
                              "=> fresh-unfocused-Xvfb window class is the "
                              "blocker, build-independent")
        save()
        log(logp, f"VERDICT {rec['verdict']}")
        return 0
    finally:
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
