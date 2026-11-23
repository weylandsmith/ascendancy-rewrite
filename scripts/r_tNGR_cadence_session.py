#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""tNG-R PUMP CADENCE MEASUREMENT (D23; user stopwatch 5.3 s/circuit vs
shipped 180 s/circuit — both cannot be true).

STATIC CHAIN (docs/re/_wip_tNGS.md S28-X0, verified asm this session):
  msg 0x3b is a SELF-REPOSTING DELAYED msg: poster 0x26c66 calls scheduler
  0x56374 with delay ebp=0x168 (360 units); the scheduler stamps
  slot+0x44c0 = DAT_000a2044 + 360; DAT_000a2044 (file off 0xa2044) is
  incremented ONLY by fn 0x53d84 (`inc dword [0xa2044]; ret`, callback entry
  in the table at file 0x8b35c). The UNIT of that clock is the open leg.
  Pump leg 0x27a18 (msg 0x3b) applies exactly +2 deg per fire to the camera
  BASIS at win+0x14e (applier 0x283e4 -> 0x53584 rotates win+0x15a and
  win+0x166 = (up, fwd), both about WORLD Y).

MEASURE (three channels, all from ONE scratch debugger session):
  C  hit-count: arm pump 0x27a18 at newgame, bank fires with wall stamps
     (naive rate; poll-overhead-caveated) + esi=win + [esi+0xc0] latch.
  D1 clock rate: RUN T s leg-free, BREAK, dump DAT_000a2044 twice -> units/s.
     cadence = units_per_s / 360; rate = 2 * cadence deg/s.
  D2 basis integration (aliasing-free): dump fwd (win+0x166, 12B) at window
     edges while running; total rotation / (2 deg) = fires; / T = cadence.
     Sign of the rotation closes the DIRECTION seam (checklist #5).
  D3 scheduler slot witness: dump win+0x44ae..0x44c4: pending msg word
     +0x44b2 == 0x3b and +0x44c0 - clock ~= 360 corroborates the repost law.

LAWS OBEYED: t302 freeze law (every fire -> BPDEL then RUN; no clicks while
armed); BREAK lottery (settle 45 s, retry x4); scratch game-wp only; own ring
dir; private Xvfb :97 + bundled x11vnc 5911 (LD_LIBRARY_PATH law); RFB click
channel (t292/tNGS3b: double-click insurance + Return fallback); SIGKILL
recorded PID only; cursor parked (600,250) OUTSIDE both fields (tNGS4 law)
during every RUN window so hover dials cannot pollute the basis.
Exit 0 verdict banked; 1 honest negative; 2 harness.
"""
import hashlib
import json
import math
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
PUMP_OFF = 0x27A18
CLOCK_OFF = 0xA2044          # DAT_000a2044 file offset
DELAY = 0x168                # repost delay, scheduler arg at 0x26c72
XVNC = op.join(ROOT, "work/r1/localdeb/root/usr/bin/x11vnc")
DISP = ":97"
VNC_PORT = 5911
CURSOR_PARK = (600, 250)     # tNGS4 law: outside both starfields


class Args:
    pass


def hx(v):
    return f"{v:#x}" if isinstance(v, int) else None


def u32(b, o):
    try:
        return struct.unpack_from("<I", b, o)[0]
    except Exception:
        return None


def f32v(b, o):
    try:
        return list(struct.unpack_from("<3f", b, o))
    except Exception:
        return None


def yaw_of(f):
    """Basis fwd (x,y,z) -> signed angle about world Y as stored by 0x5324c.
    Raw atan2(x, z): fwd rest = (0,0,1) -> 0. Sign convention is REPORTED,
    not assumed: both the number and the raw vectors are banked."""
    if not f:
        return None
    return math.degrees(math.atan2(f[0], f[2]))


def rfb_move(x, y):
    env = dict(os.environ, RFB_XOFF="80", RFB_YOFF="100",
               RFB_PORT=str(VNC_PORT))
    return subprocess.run(
        [sys.executable, op.join(ROOT, "scripts", "r287_vncinput.py"),
         "move", str(x), str(y)], capture_output=True, timeout=30, env=env)


def rfb_click(x, y):
    env = dict(os.environ, RFB_XOFF="80", RFB_YOFF="100",
               RFB_PORT=str(VNC_PORT))
    return subprocess.run(
        [sys.executable, op.join(ROOT, "scripts", "r287_vncinput.py"),
         "click", str(x), str(y)], capture_output=True, timeout=30, env=env)


def rfb_key(name):
    env = dict(os.environ, RFB_XOFF="80", RFB_YOFF="100",
               RFB_PORT=str(VNC_PORT))
    return subprocess.run(
        [sys.executable, op.join(ROOT, "scripts", "r287_vncinput.py"),
         "key", name], capture_output=True, timeout=30, env=env)


def main():
    tag = "tngr"
    out = op.join(ROOT, "work", "r1",
                  f"dbg-{tag}-{time.strftime('%Y%m%d-%H%M%S')}")
    os.makedirs(op.join(out, "save"), exist_ok=True)
    rec = {"legs": {"pump": PUMP_OFF, "cos_hdlr": 0x26B34},
           "delay_units": DELAY,
           "clock_file_off": CLOCK_OFF, "fires": [], "entry": [],
           "windows": [], "verdict": None}

    def save():
        with open(op.join(out, "tngr.json"), "w") as fh:
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
    lin_pump = P0 + PUMP_OFF
    lin_clock = P0 + CLOCK_OFF

    def read_clock():
        b = s.dump_mem(lin_clock, 4, "clk")
        return u32(b, 0) if b else None

    def read_basis(win):
        # basis block: A@+0x14e (1,0,0) up@+0x15a fwd@+0x166 right@+0x172
        b = s.dump_mem(win + 0x14e, 0x30, "basis")
        if not b:
            return None
        return {"A": f32v(b, 0x00), "up": f32v(b, 0x0C),
                "fwd": f32v(b, 0x18), "right": f32v(b, 0x24)}

    def read_sched(win):
        # scheduler slot0 (0x56374 law): base win+0x44ae stride 0x16;
        # +0x44ae param u32, +0x44b2 msg u16, +0x44b4 u32, +0x44b8 u32,
        # +0x44bc u32, +0x44c0 fire-at = clock + delay
        b = s.dump_mem(win + 0x44ae, 0x16, "sched")
        if not b:
            return None
        return {"p44ae": u32(b, 0), "msg": struct.unpack_from("<H", b, 4)[0],
                "p44b4": u32(b, 6), "p44b8": u32(b, 10),
                "p44bc": u32(b, 14), "fire_at": u32(b, 18)}

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
            env=dict(os.environ, LD_LIBRARY_PATH=op.join(
                ROOT, "work/r1/localdeb/root/usr/lib/x86_64-linux-gnu")))
        time.sleep(3)
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
        # title -> New Game (tNGS3b law: RFB double-click (250,295) + Return
        # fallback; verify = title orange GONE)
        im = s.grab("title_settled")
        rec["title_orange"] = round(s.orange_frac(im), 3) if im else None
        save()
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
        rfb_move(*CURSOR_PARK)      # park BEFORE any armed window
        time.sleep(1)

        # ---------- PHASE C: hit-count witness at the pump leg ----------
        if not s.do_break():
            rec["verdict"] = "NEGATIVE: BREAK lost pre-arm"
            save()
            return 1
        # r299 LEGS lacks the pump leg; inject then arm (arm_all reads
        # LEGS[name] — patching after a failed call would KeyError first).
        # cos_hdlr = handler ENTRY 0x26b34: register law (t425, verified from
        # sender 0x56ad4) eax=win edx=msg-id — the discriminator for whether
        # msg 0x3b is ever DELIVERED to the newgame window.
        L.LEGS["w1_pump"] = PUMP_OFF
        leg_off = {"w1_pump": PUMP_OFF, "cos_hdlr": 0x26B34}
        s.legs = ["w1_pump", "cos_hdlr"]
        if not s.arm_all(s.legs):
            rec["verdict"] = "HARNESS: arm failed"
            save()
            return 2
        s.req("EXEC RUN", 20.0)
        t_end = time.time() + 30
        stop_budget = 14
        while time.time() < t_end and stop_budget > 0:
            if s.do_break():
                eip = s.read_reg("eip")
                hit = next((n for n, o in leg_off.items()
                            if eip == P0 + o), None)
                if hit == "w1_pump":
                    regs = {r: s.read_reg(r) for r in ("esi",)}
                    win = regs.get("esi")
                    fb = s.dump_mem(win + 0xc0, 4, "latch") if win else None
                    rec["fires"].append({"wall": time.strftime("%H:%M:%S"),
                                         "t": round(time.time(), 3),
                                         "win": hx(win),
                                         "latch": u32(fb, 0) if fb else None})
                    save()
                    s.log(f"FIRE {len(rec['fires'])} win={hx(win)} "
                          f"latch={u32(fb, 0) if fb else None}")
                elif hit == "cos_hdlr":
                    regs = {r: s.read_reg(r) for r in ("eax", "edx")}
                    msg = regs.get("edx")
                    nm = None
                    if regs.get("eax") and 0x10000 <= regs["eax"] < 0x1000000:
                        hb = s.dump_mem(regs["eax"], 0x2c, "wnm")
                        if hb:
                            nm = hb[0x20:0x2c].split(b"\x00")[0].decode(
                                "latin1", "replace")
                    rec["entry"].append({"wall": time.strftime("%H:%M:%S"),
                                         "win": hx(regs.get("eax")),
                                         "msg": hx(msg), "name": nm})
                    save()
                    s.log(f"ENTRY msg={hx(msg)} win={hx(regs.get('eax'))} "
                          f"name={nm}")
                idx = s.bp_index_of(eip) if eip else None
                if idx is not None:
                    s.req(f"EXEC BPDEL {idx:X}", 10.0)
                s.req("EXEC RUN", 20.0)
                stop_budget -= 1
                # re-arm both legs after liveness (t302): stops need the legs
                if time.time() < t_end and stop_budget > 0:
                    time.sleep(1.0)
                    if s.do_break():
                        s.arm_all(s.legs)
                        s.req("EXEC RUN", 20.0)
            else:
                rec["verdict"] = "NEGATIVE: BREAK lottery lost mid-C"
                save()
                return 1
        wins = sorted(set(f["win"] for f in rec["fires"] if f["win"]))
        rec["pump_windows_seen"] = wins
        latches = sorted(set(f["latch"] for f in rec["fires"]))
        rec["latches_seen"] = latches
        save()

        # ---------- PHASE D: clock + basis integration, leg-free ----------
        s.req("EXEC BPDEL *", 15.0)
        s.req("EXEC RUN", 20.0)
        # pick the pump window (the one that fired; else the newgame COSMOSWnd
        # entry window — clock rate is window-independent)
        win = None
        for f in rec["fires"]:
            if f["win"]:
                win = int(f["win"], 16)
                break
        if win is None:
            for f in rec["entry"]:
                if f["win"] and f.get("name") == "COSMOSWnd":
                    win = int(f["win"], 16)
                    break
        if win is None:
            rec["verdict"] = ("NEGATIVE: no COSMOSWnd window handle in C "
                              f"(fires={len(rec['fires'])} "
                              f"entry={len(rec['entry'])})")
            save()
            return 1
        s.log(f"PHASE D win={hex(win)}")
        # scheduler slot witness (clock vs fire_at) — read STOPPED (the clock
        # and basis only move while running; edge samples must be quiescent)
        if not s.do_break():
            rec["verdict"] = "NEGATIVE: BREAK lost pre-D"
            save()
            return 1
        sc = read_sched(win)
        clk0 = read_clock()
        b0 = read_basis(win)
        rec["sched_slot"] = {k: (hex(v) if isinstance(v, int) else v)
                             for k, v in (sc or {}).items()}
        rec["sched_fire_minus_clock"] = ((sc["fire_at"] - clk0)
                                         if sc and clk0 is not None else None)
        save()
        for T in (2.0, 2.0, 2.0, 5.0, 10.0):
            t0 = time.time()
            c0 = read_clock()
            ba = read_basis(win)
            f0 = ba["fwd"] if ba else None
            s.req("EXEC RUN", 20.0)
            time.sleep(T)
            if not s.do_break():
                rec["verdict"] = "NEGATIVE: BREAK lost mid-D"
                save()
                return 1
            t1 = time.time()
            c1 = read_clock()
            bb = read_basis(win)
            wall = t1 - t0
            du = (c1 - c0) if (c0 is not None and c1 is not None) else None
            dth = None
            if f0 and bb and f0[2]:
                a0 = yaw_of(f0)
                a1 = yaw_of(bb["fwd"])
                if a0 is not None and a1 is not None:
                    dth = (a1 - a0 + 180) % 360 - 180   # wrap to [-180,180]
            w = {"T": round(wall, 2), "clock_units": du,
                 "units_per_s": round(du / wall, 1) if du is not None else None,
                 "fwd_before": f0, "fwd_after": bb["fwd"] if bb else None,
                 "dtheta_deg": round(dth, 2) if dth is not None else None,
                 "deg_per_s": round(dth / wall, 2) if dth is not None else None}
            # aliasing note: |dtheta|<=180 => fires <=90 => cadence<=45/s
            rec["windows"].append(w)
            s.log(f"WINDOW {json.dumps(w)}")
            save()
        # verdict math
        ups = [w["units_per_s"] for w in rec["windows"]
               if w.get("units_per_s") is not None and w["units_per_s"] > 0]
        dps = [w["deg_per_s"] for w in rec["windows"]
               if w.get("deg_per_s") is not None]
        if ups:
            ups.sort()
            med_up = ups[len(ups) // 2]
            cad = med_up / DELAY
            rec["clock_units_per_s_median"] = med_up
            rec["cadence_per_s_from_clock"] = round(cad, 3)
            rec["rate_deg_per_s_from_clock"] = round(2 * cad, 3)
        if dps:
            dps.sort()
            rec["deg_per_s_median_basis"] = dps[len(dps) // 2]
        if "clock_units_per_s_median" in rec or "deg_per_s_median_basis" in rec:
            r_clock = rec.get("rate_deg_per_s_from_clock")
            r_basis = rec.get("deg_per_s_median_basis")
            parts = []
            parts.append(f"pump fires at newgame: {len(rec['fires'])}")
            msgs = {}
            for f in rec["entry"]:
                msgs[f["msg"]] = msgs.get(f["msg"], 0) + 1
            parts.append(f"entry msgs {msgs}")
            if r_clock is not None:
                parts.append(f"clock {rec['clock_units_per_s_median']}/s "
                             f"/{DELAY} => {r_clock} deg/s")
            if r_basis is not None:
                parts.append(f"basis {r_basis} deg/s")
            rec["verdict"] = "MEASURED: " + "; ".join(parts)
        else:
            rec["verdict"] = "NEGATIVE: no clock/basis samples"
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
