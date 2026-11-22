#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""tNGS cycle 3 W1 — AUTO-ROTATE WITNESS (newgame vs map). D21.

STATIC STATE (docs/re/_wip_tNGS.md S14, verified asm this session):
  COSMOSWnd msg handler 0x26b34; window-init leg branches on DAT_0007e582>>16:
    state==3 (ui-runtime.md:484 'NEWGAME state 3'): rect(17,12,324,320),
      FOV 35.0, camera init, and 0x26dd1 `mov dword [esi+0xc0], 1`
      = LATCH bit0 SET (ROTLEFT active, dir bit1=0 => +2 deg/tick per t416).
    state==0xd: rect(0,0,323,315) (NEGSCREEN class), no latch store read.
    generic tail 0x26c89: latch CLEAR.
  Pump leg 0x27a18 (msg 0x3b, ~1/s t302) rotates +-2deg/tick while bits set.
  Writer FUN_000283e4: eax=win, edx selector (-1=>0x53584 WORLD-Y, 0=>0x53554
  WORLD-X), f32 angle fld [esp+0xc] at entry (0x283f4, before any push).

LEGS (payload offsets; linear = P0+off):
  w1_writer 0x283E4  rotation writer entry  (FIRE = spin happening, NOW)
  w1_pump   0x27A18  msg-0x3b pump leg      (bank BYTE [win+0xc0] each fire)
  w1_hdlr   0x26B34  handler entry          (state word + NAME; cap 3 dumps)

VERDICT: writer fires at newgame => AUTO-SPIN ON (+axis/angle cited).
  Else pump fires with latch==0 (or nothing) => newgame field STATIC.
  Post-Begin map leg: map latch should read 0 (state-1 generic clear) —
  corroborates 'only the newgame field auto-spins'.

CHOREO: title (wait_title law) -> arm all legs stopped -> RUN -> verify
highlight R3 NewGame (t287 cyan-band law) -> RFB click (318,293) -> newgame
-> shot F1, poll 30 s, shot F2 -> field-diff = on-screen spin witness ->
RFB click Begin (566,422) -> map -> poll 15 s.

SAFETY: scratch game-wp only (asserted); OWN ring dir; private Xvfb :97 +
x11vnc 5911 (production :9/:5910 untouched); core=normal; -time-limit;
SIGKILL recorded PID only; Oct-29 md5 RESUME.GAM. Exit 0 ran+verdict banked;
1 negative; 2 harness.
"""
import hashlib
import json
import os
import os.path as op
import signal
import struct
import subprocess
import sys
import time

ROOT = op.abspath(op.join(op.dirname(__file__), ".."))
sys.path.insert(0, op.join(ROOT, "scripts"))
import r299_leg_session as L                                  # noqa: E402
import r293_move_session as R293                              # noqa: E402

P0 = L.P0
W1 = {"w1_writer": 0x283E4, "w1_pump": 0x27A18, "w1_hdlr": 0x26B34}
L.LEGS.update(W1)
STATE_OFF = 0x7e582
XVNC = op.join(ROOT, "work/r1/localdeb/root/usr/bin/x11vnc")
DISP = ":97"
VNC_PORT = 5911
NEWGAME_CLICK = (318, 293)      # title slot R3 (273..313) centre
BEGIN_CLICK = (566, 422)        # t412 law
FIELD_BOX = (8, 8, 492, 372)    # cosmos well rect (tA2 law)

# SCRATCH-DISPLAY MENU LAW (tngs3w1 attempt-2 MEASURED: the t287 production
# slot table 193..473 does NOT apply to the fresh-boot menu — rows sit at
# ~125..360, pitch ~35). Detector = teal highlight band: count px
# (r<40, g>55, b>60) per row; band = contiguous rows >50 hits.
def teal_band(img):
    px = img.load()
    hits = {}
    for y in range(100, 420):
        c = 0
        for x in range(95, 405, 3):
            r, g, b = px[x, y]
            if g > 55 and b > 60 and r < 40:
                c += 1
        hits[y] = c
    best = (0, 0, 0)  # (len, center, maxh)
    inb = None
    for y in range(100, 421):
        h = hits.get(y, 0)
        if h > 50 and inb is None:
            inb = y
        elif h <= 50 and inb is not None:
            ln = y - inb
            cen = (inb + y - 1) // 2
            if ln > best[0]:
                best = (ln, cen, max(hits[k] for k in range(inb, y)))
            inb = None
    return best  # (band_len, band_center, max_hits) or (0,0,0)


class Args:
    pass


def hx(v):
    return f"{v:#x}" if isinstance(v, int) else None


def u32(b, o):
    try:
        return struct.unpack_from("<I", b, o)[0]
    except Exception:
        return None


def f32(b, o):
    try:
        return struct.unpack_from("<f", b, o)[0]
    except Exception:
        return None


def highlight_row(img):
    px = img.load()
    bands = []
    for (lo, hi) in SLOTS:
        hits = tot = 0
        for y in range(lo + 6, hi - 6, 2):
            for x in range(165, 470, 4):
                r_, g_, b_ = px[x, y]
                tot += 1
                if 10 <= r_ <= 24 and 58 <= g_ <= 80 and 62 <= b_ <= 84:
                    hits += 1
        bands.append(hits / max(tot, 1))
    best = max(range(len(bands)), key=lambda i: bands[i] or 0)
    if not bands[best] or bands[best] < 0.5:
        return None, bands
    return best, bands


def crop_diff(im1, im2, box):
    """im1/im2 are PIL crops already in game coords (Sess.grab law)."""
    from PIL import ImageChops
    a = im1.crop(box)
    b = im2.crop(box)
    d = ImageChops.difference(a, b)
    hist = d.histogram()
    changed = sum(hist[0:256]) - a.size[0] * a.size[1] * 3
    return changed


def rfb_move(x, y):
    # tNGS3b (S18): fresh-Xvfb window origin is (80,100) — vision-measured
    # game content 80..720 x 100..580 — the r287 defaults. The old 192/184
    # were production-drift values and WRONG here.
    env = dict(os.environ, RFB_XOFF="80", RFB_YOFF="100",
               RFB_PORT=str(VNC_PORT))
    r = subprocess.run([sys.executable, op.join(ROOT, "scripts", "r287_vncinput.py"),
                        "move", str(x), str(y)],
                       capture_output=True, timeout=30, env=env)
    return r.returncode


def rfb_click(x, y):
    env = dict(os.environ, RFB_XOFF="80", RFB_YOFF="100",
               RFB_PORT=str(VNC_PORT))
    r = subprocess.run([sys.executable, op.join(ROOT, "scripts", "r287_vncinput.py"),
                        "click", str(x), str(y)],
                       capture_output=True, timeout=30, env=env)
    return r.returncode


def rfb_key(name):
    env = dict(os.environ, RFB_XOFF="80", RFB_YOFF="100",
               RFB_PORT=str(VNC_PORT))
    r = subprocess.run([sys.executable, op.join(ROOT, "scripts", "r287_vncinput.py"),
                        "key", name],
                       capture_output=True, timeout=30, env=env)
    return r.returncode


def main():
    tag = "tngs3w1"
    out = op.join(ROOT, "work", "r1",
                  f"dbg-{tag}-{time.strftime('%Y%m%d-%H%M%S')}")
    os.makedirs(op.join(out, "save"), exist_ok=True)
    rec = {"legs": W1, "stops": [], "verdict": None}

    def save():
        with open(op.join(out, "w1.json"), "w") as fh:
            json.dump(rec, fh, indent=1)

    assert op.abspath(R293.SCRATCH).startswith(op.join(ROOT, "work"))
    assert hashlib.md5(open(R293.OCT29, "rb").read()).hexdigest() == R293.OCT29_MD5
    assert op.exists(L.DBG_BIN) and op.exists(XVNC)

    a = Args()
    a.disp, a.port, a.tl, a.boot = DISP, 55991, 900, 200
    s = L.Sess(a)
    s.out = out
    s.savedir = op.join(out, "save")
    s.logp = op.join(out, "session.log")
    s.dbl = op.join(out, "dosbox.out")
    s.ptylog = op.join(out, "mcp-pty.log")
    s.transcript = op.join(out, "mcp-transcript.txt")
    s.census = True
    dump_left = {"w1_writer": 6, "w1_pump": 6, "w1_hdlr": 3}
    phase = {"now": "title"}

    def win_ident(win):
        if not win or not (0x10000 <= win < 0x1000000):
            return {}
        hb = s.dump_mem(win, 0x40, f"w{win:x}")
        if not hb or len(hb) < 0x30:
            return {}
        lb = s.dump_mem(win + 0xc0, 4, f"l{win:x}")
        return {"magic_ok": u32(hb, 0) == 0x12345678,
                "name": hb[0x20:0x2c].split(b"\x00")[0].decode("latin1", "replace"),
                "latch": u32(lb, 0) if lb else None}

    def bank_leg(eip):
        name = next((k for k, v in W1.items() if P0 + v == eip), None)
        if not name:
            return None
        regs = {r: s.read_reg(r) for r in ("eax", "esi", "edx", "esp")}
        info = {"leg": name, "phase": phase["now"],
                "wall": time.strftime("%H:%M:%S"),
                "regs": {k: hx(v) for k, v in regs.items()}}
        if dump_left.get(name, 0) > 0:
            dump_left[name] -= 1
            st = s.dump_mem(P0 + STATE_OFF, 4, "st")
            info["state_word"] = (u32(st, 0) >> 16) if st else None
            # writer entry: eax=win BEFORE `mov ebx,eax`; pump leg is mid-
            # handler where esi=win (t416); hdlr entry: eax=win pre-mov.
            win = regs.get("esi") if name == "w1_pump" else regs.get("eax")
            info.update(win_ident(win))
            if name == "w1_writer":
                esp = regs.get("esp")
                ab = s.dump_mem(esp, 0x10, "ang") if esp else None
                if ab:
                    # BP stops BEFORE `push ebx; sub esp,4`, so the cdecl
                    # angle arg (fld [esp+0xc] AFTER that prologue) sits at
                    # [esp+4] NOW ([esp] = ret0).
                    info["angle_esp4"] = f32(ab, 0x4)
                    info["ret0"] = hx(u32(ab, 0))
                info["selector"] = regs.get("edx")
                sel = regs.get("edx")
                info["axis"] = ("world-Y" if sel in (0xFFFFFFFF, -1) else
                                "world-X" if sel == 0 else "OTHER")
        rec["stops"].append(info)
        save()
        s.log(f"W1 STOP {json.dumps(info)[:300]}")
        idx = s.bp_index_of(P0 + W1[name])
        if idx is not None:
            s.req(f"EXEC BPDEL {idx:X}", 10.0)
        s.req("EXEC RUN", 20.0)
        return info

    def poll(label, seconds, stop_cap=10):
        t_end = time.time() + seconds
        n = 0
        while time.time() < t_end and n < stop_cap:
            if not s.do_break():
                s.log(f"POLL {label}: BREAK lost")
                break
            eip = s.read_reg("eip")
            if eip and any(P0 + v == eip for v in W1.values()):
                bank_leg(eip)
                n += 1
                continue
            s.req("EXEC RUN", 15.0)
            time.sleep(1.0)
        s.log(f"POLL {label}: {n} leg stops")
        # leave the guest RUNNING and legs cleared of any pending halt
        s.req("EXEC RUN", 15.0)
        return n

    vnc = None
    try:
        s.launch()
        conn = s.connect()
        if conn is None:
            rec["verdict"] = "HARNESS: no MCP connection"
            save()
            return 2
        lines, _, _ = s.req("PING", 10.0)
        if "PONG" not in " ".join(lines):
            rec["verdict"] = "HARNESS: no PONG"
            save()
            return 2
        vnc = subprocess.Popen(
            [XVNC, "-display", DISP, "-rfbport", str(VNC_PORT),
             "-localhost", "-nopw", "-forever", "-shared"],
            stdout=open(op.join(out, "x11vnc.out"), "wb"),
            stderr=subprocess.STDOUT,
            # tNGS3b ROOT CAUSE (S18): without this the bundled x11vnc dies
            # at exec (libvncserver.so.1) and EVERY RFB input is silently
            # lost. Same env as r1_playcap_vnc.sh:158.
            env=dict(os.environ, LD_LIBRARY_PATH=op.join(
                ROOT, "work/r1/localdeb/root/usr/lib/x86_64-linux-gnu")))
        time.sleep(3)
        # t286 law: settle BEFORE the first BREAK; BREAK ITSELF IS A LOTTERY
        # (tngs3w1 attempt-3: hdr=None at 45 s settle, attempt-2 same code
        # succeeded) -> retry with re-settle up to 4 times.
        got = False
        for att in range(4):
            s.log(f"settling 45s before BREAK lottery (attempt {att})")
            time.sleep(45)
            if s.do_break():
                got = True
                break
            lines, _, _ = s.req("PING", 15.0)
            if "PONG" not in " ".join(lines):
                rec["verdict"] = f"NEGATIVE: channel dead at BREAK att {att}"
                save()
                return 1
        if not got:
            rec["verdict"] = "NEGATIVE: BREAK lottery lost x4"
            save()
            return 1
        s.req("EXEC RUN", 20.0)
        s.pty_new()
        if not s.wait_title():
            rec["verdict"] = "NEGATIVE: title never appeared"
            save()
            return 1
        if not s.do_break():
            rec["verdict"] = "NEGATIVE: BREAK lost pre-arm"
            save()
            return 1
        if not s.arm_all(list(W1)):
            rec["verdict"] = "HARNESS: arm failed"
            save()
            return 2
        s.req("EXEC RUN", 20.0)
        time.sleep(4)
        # title -> New Game. RFB IS UNAVAILABLE THIS BUILD (x11vnc bundled
        # binary fails: libvncserver.so.1 missing — tngs3w1 attempts 2-4
        # post-mortem: hover never moved, frames byte-identical). FALLBACK =
        # t292 LAW: on a FRESH PRIVATE Xvfb there is no stale hover, so the
        # xsend motion-warp click fires the row it warps to (cited:
        # r293.enter_campaign comment). SETTLED MENU GEOMETRY (vision-
        # measured on run 141025 ngv0, orange 0.679 = fully settled; navy-run
        # detector): rows 200-230 PlayIntro, 240-270 Tutorial(teal),
        # 280-310 NewGame -> CLICK y=295.
        # VERIFY after click = title orange GONE (enter_campaign law).
        im = s.grab("title_settled")
        rec["title_orange"] = round(s.orange_frac(im), 3) if im else None
        save()
        # tNGS3b (S18): RFB IS THE ONLY PROVEN FIRING CHANNEL (t292/t439);
        # xsend XSendEvent presses are synthetic (hover moves, never fires).
        # Fresh-boot rows (window coords): PlayIntro 200-230 / Tutorial
        # 240-270 / NewGame 280-310 -> click (250,295); r287 adds +80/+100.
        # Double-click insurance: first=hover, second=fire.
        rfb_move(250, 295)
        time.sleep(1)
        rfb_click(250, 295)
        time.sleep(2)
        rfb_click(250, 295)
        time.sleep(8)
        im2 = s.grab("after_ng_click")
        f2 = s.orange_frac(im2) if im2 else 1.0
        rec["after_ng_orange"] = round(f2, 3)
        save()
        # tNGS3b C2 (S19): if the RFB click pair did not fire, the hovered
        # row is provably New Game (vision on 155718 _raw_04) -> RFB key
        # Return fires the HOVERED row (t287 law).
        if f2 > 0.20:
            rfb_key("Return")
            time.sleep(8)
            im2 = s.grab("after_ng_key")
            f2 = s.orange_frac(im2) if im2 else 1.0
            rec["after_ng_orange_key"] = round(f2, 3)
            save()
        if f2 > 0.20:
            rec["verdict"] = "NEGATIVE: New Game click did not leave title"
            save()
            return 1
        f1 = s.grab("ng_f1")
        phase["now"] = "newgame"
        poll("newgame", 30)
        f2 = s.grab("ng_f2")
        if f1 and f2:
            rec["field_px_changed"] = crop_diff(f1, f2, FIELD_BOX)
            rec["field_box"] = FIELD_BOX
        save()
        # Begin -> campaign map (tNGS3b: RFB channel, S18; same-row
        # double-click insurance)
        rfb_move(*BEGIN_CLICK)
        time.sleep(1)
        rfb_click(*BEGIN_CLICK)
        time.sleep(2)
        rfb_click(*BEGIN_CLICK)
        time.sleep(4)
        rfb_move(320, 60)   # neutral hover: Return must NOT re-fire NewGame
        time.sleep(1)
        rfb_key("Return")   # tNGS3b C2: fire focused control if clicks deaf
        time.sleep(4)
        grab_map = s.grab("map_post")
        phase["now"] = "map"
        poll("map", 15, stop_cap=6)
        w = [x for x in rec["stops"] if x["leg"] == "w1_writer"
             and x["phase"] == "newgame"]
        wl = [x for x in rec["stops"] if x["leg"] == "w1_writer"
              and x["phase"] == "map"]
        p = [x for x in rec["stops"] if x["leg"] == "w1_pump"
             and x["phase"] == "newgame"]
        latched = [x for x in p if (x.get("latch") or 0) != 0]
        if w:
            rec["verdict"] = (f"AUTO-SPIN ON at newgame: writer {len(w)}x "
                              f"axes {sorted(set(x.get('axis') for x in w))} "
                              f"angles {[x.get('angle_esp4') for x in w]}")
        elif latched:
            rec["verdict"] = (f"AUTO-SPIN ON (pump-latched): {len(latched)}x "
                              f"latch {sorted(set(x.get('latch') for x in latched))}")
        elif p:
            rec["verdict"] = f"STATIC: pump {len(p)}x latch==0"
        else:
            rec["verdict"] = ("UNKNOWN: no leg fired in newgame window "
                              "(check arming/shots)")
        rec["map_writer_stops"] = len(wl)
        save()
        return 0
    finally:
        if vnc:
            try:
                vnc.kill()
            except Exception:
                pass
        if getattr(s, "child", None):
            try:
                os.kill(s.child.pid, signal.SIGKILL)
            except Exception:
                pass
        save()


if __name__ == "__main__":
    sys.exit(main())
