#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""tNG-H CHECKLIST ITEM 5: HOVER-ADDER MEASUREMENT (NG5 WAIT-branch).

Question: does parking the cursor inside kPreviewSpinZone (379,420-493,472)
make the newgame star field spin FASTER than the base beat (~60-65 deg/s,
S28 basis-integration law)? The original's code has a hover zone there
(t423 F7); the adder on top of the base beat has never been measured.

METHOD (identical instrument to S28 / r_tNGR_cadence_session.py PHASE D,
which is the ONLY alive cadence channel per REFUTED-ROUTES tNG-S S28 block):
  - scratch debugger session, title -> New Game, BREAK lottery laws;
  - PHASE 0: locate the pump window (arm pump leg 0x27a18 once, 10 s,
    cursor at OUT); BPDEL *;
  - PHASE A: cursor OUTSIDE (park 600,250), basis windows fwd@win+0x166
    over T = 2,2,2,5 s (control; reproduces S28 ~60 deg/s);
  - PHASE B: cursor INSIDE zone (move 436,446), settle 1.5 s, same windows;
  - PHASE C: cursor OUT again (reversibility check kills one-shot artifacts).
  dtheta wrapped to [-180,180] is ALIASING-CAPPED at 2.25 s (<=90 fires
  <127): S28's 10 s windows aliased (-62==-422). We use only <=5 s windows
  and report raw vectors so the arithmetic is re-checkable.
Verdict: MED(B) vs MED(A): >+10% => ADDER PRESENT (+deg/s number);
within +-10% => NEGATIVE (hover adds nothing measurable); BREAK/channel
loss => 1; harness => 2.

LAWS OBEYED: t302 freeze law (no clicks while RUN; every move happens
STOPPED); BREAK lottery settle 45 s x4; scratch game-wp only (assert in
r293); own ring dir; private Xvfb :97 + bundled x11vnc 5911
(LD_LIBRARY_PATH law); RFB move channel (t292: real warp, hover repaints);
SIGKILL recorded PID only; production :9 untouched.
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
XVNC = op.join(ROOT, "work/r1/localdeb/root/usr/bin/x11vnc")
DISP = ":97"
VNC_PORT = 5911
CURSOR_OUT = (600, 250)      # tNGS4 law: outside both starfields
CURSOR_IN = (436, 446)       # centre of kPreviewSpinZone 379..493 x 420..472
WINDOWS = (2.0, 2.0, 2.0, 5.0)


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
    if not f:
        return None
    return math.degrees(math.atan2(f[0], f[2]))


def _rfb_env():
    return dict(os.environ, RFB_XOFF="80", RFB_YOFF="100",
                RFB_PORT=str(VNC_PORT))


def rfb_move(x, y):
    return subprocess.run(
        [sys.executable, op.join(ROOT, "scripts", "r287_vncinput.py"),
         "move", str(x), str(y)], capture_output=True, timeout=30,
        env=_rfb_env())


def rfb_click(x, y):
    return subprocess.run(
        [sys.executable, op.join(ROOT, "scripts", "r287_vncinput.py"),
         "click", str(x), str(y)], capture_output=True, timeout=30,
        env=_rfb_env())


def rfb_key(name):
    return subprocess.run(
        [sys.executable, op.join(ROOT, "scripts", "r287_vncinput.py"),
         "key", name], capture_output=True, timeout=30, env=_rfb_env())


def med(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2] if xs else None


def main():
    tag = "tngh"
    out = op.join(ROOT, "work", "r1",
                  f"dbg-{tag}-{time.strftime('%Y%m%d-%H%M%S')}")
    os.makedirs(op.join(out, "save"), exist_ok=True)
    rec = {"legs": {"pump": PUMP_OFF}, "zone": [379, 420, 493, 472],
           "cursor_out": CURSOR_OUT, "cursor_in": CURSOR_IN,
           "fires": [], "phases": {}, "verdict": None}

    def save():
        with open(op.join(out, "tngh.json"), "w") as fh:
            json.dump(rec, fh, indent=1)

    assert op.abspath(R293.SCRATCH).startswith(op.join(ROOT, "work"))
    assert hashlib.md5(open(R293.OCT29, "rb").read()).hexdigest() == R293.OCT29_MD5
    assert op.exists(L.DBG_BIN) and op.exists(XVNC)

    a = Args()
    a.disp, a.port, a.tl, a.boot = DISP, 55992, 900, 200
    s = L.Sess(a)
    s.out = out
    s.savedir = op.join(out, "save")
    s.logp = op.join(out, "session.log")
    s.dbl = op.join(out, "dosbox.out")
    s.ptylog = op.join(out, "mcp-pty.log")
    s.transcript = op.join(out, "mcp-transcript.txt")

    def read_basis(win):
        b = s.dump_mem(win + 0x14e, 0x30, "basis")
        if not b:
            return None
        return {"A": f32v(b, 0x00), "up": f32v(b, 0x0C),
                "fwd": f32v(b, 0x18), "right": f32v(b, 0x24)}

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
        # title -> New Game (tNGS3b law)
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
        rfb_move(*CURSOR_OUT)
        time.sleep(1)

        # ---------- PHASE 0: locate the pump window (cursor OUT) ----------
        if not s.do_break():
            rec["verdict"] = "NEGATIVE: BREAK lost pre-arm"
            save()
            return 1
        L.LEGS["w1_pump"] = PUMP_OFF
        s.legs = ["w1_pump"]
        if not s.arm_all(s.legs):
            rec["verdict"] = "HARNESS: arm failed"
            save()
            return 2
        s.req("EXEC RUN", 20.0)
        t_end = time.time() + 30
        budget = 10
        # dosbox-x BP-hit eip REPORTING QUIRK (S30 run 20261123-124235): the
        # BREAK-caught stop at this leg reported eip = BP+6 (the next
        # instruction boundary, after `mov dh,[esi+0xc0]` 8ab6c0000000) six
        # times straight, while the S28 run reported the BP address itself.
        # A stop anywhere in the 6-byte load is a pump fire: esi valid, latch
        # byte loaded, no state mutated yet. Accept both.
        hit_eips = {P0 + PUMP_OFF, P0 + PUMP_OFF + 6}
        while time.time() < t_end and budget > 0:
            if s.do_break():
                eip = s.read_reg("eip")
                if eip in hit_eips:
                    esi = s.read_reg("esi")
                    if not (esi and 0x10000 <= esi < 0x1000000):
                        s.log(f"pump-region stop with junk esi={hx(esi)} "
                              "— not recorded as fire")
                    else:
                        fb = s.dump_mem(esi + 0xc0, 4, "latch")
                        rec["fires"].append({"wall": time.strftime("%H:%M:%S"),
                                             "win": hx(esi),
                                             "eip": hx(eip),
                                             "latch": u32(fb, 0) if fb else None})
                        save()
                        s.log(f"FIRE win={hx(esi)} eip={hx(eip)} latch="
                              f"{u32(fb, 0) if fb else None}")
                    break
                idx = s.bp_index_of(eip) if eip else None
                if idx is not None:
                    s.req(f"EXEC BPDEL {idx:X}", 10.0)
                s.req("EXEC RUN", 20.0)
                budget -= 1
                if time.time() < t_end and budget > 0:
                    time.sleep(1.0)
                    if s.do_break():
                        s.arm_all(s.legs)
                        s.req("EXEC RUN", 20.0)
            else:
                rec["verdict"] = "NEGATIVE: BREAK lost mid-P0"
                save()
                return 1
        win = None
        for f in rec["fires"]:
            if f["win"]:
                win = int(f["win"], 16)
                break
        if win is None:
            rec["verdict"] = "NEGATIVE: pump never fired at newgame (cursor OUT)"
            save()
            return 1
        s.req("EXEC BPDEL *", 15.0)
        s.req("EXEC RUN", 20.0)
        s.log(f"PHASE A-D win={hex(win)}")

        # ---------- PHASES A/B/C: basis windows per cursor state ----------
        def run_phase(name, cursor):
            if not s.do_break():
                rec["verdict"] = f"NEGATIVE: BREAK lost pre-{name}"
                save()
                return False
            rfb_move(*cursor)
            time.sleep(1.5)                     # settle hover state
            ws = []
            for T in WINDOWS:
                t0 = time.time()
                ba = read_basis(win)
                f0 = ba["fwd"] if ba else None
                s.req("EXEC RUN", 20.0)
                time.sleep(T)
                if not s.do_break():
                    rec["verdict"] = f"NEGATIVE: BREAK lost mid-{name}"
                    save()
                    return False
                t1 = time.time()
                bb = read_basis(win)
                wall = t1 - t0
                dth = None
                if f0 and bb and f0[2]:
                    a0 = yaw_of(f0)
                    a1 = yaw_of(bb["fwd"])
                    if a0 is not None and a1 is not None:
                        dth = (a1 - a0 + 180) % 360 - 180
                w = {"T": round(wall, 2),
                     "fwd_before": f0, "fwd_after": bb["fwd"] if bb else None,
                     "dtheta_deg": round(dth, 2) if dth is not None else None,
                     "deg_per_s": round(dth / wall, 2) if dth is not None else None}
                ws.append(w)
                s.log(f"{name} WINDOW {json.dumps(w)}")
            dps = [w["deg_per_s"] for w in ws if w["deg_per_s"] is not None]
            rec["phases"][name] = {"cursor": cursor, "windows": ws,
                                   "n": len(dps), "median_dps": med(dps)}
            save()
            return True

        if not run_phase("A_out", CURSOR_OUT):
            return 1
        if not run_phase("B_in", CURSOR_IN):
            return 1
        if not run_phase("C_out", CURSOR_OUT):
            return 1

        a_med = rec["phases"]["A_out"]["median_dps"]
        b_med = rec["phases"]["B_in"]["median_dps"]
        c_med = rec["phases"]["C_out"]["median_dps"]
        if a_med is None or b_med is None:
            rec["verdict"] = "NEGATIVE: no basis samples in A or B"
            save()
            return 1
        base = med([x for x in (a_med, c_med) if x is not None])
        if base == 0:
            rec["verdict"] = "NEGATIVE: base beat zero (pump dead?)"
            save()
            return 1
        ratio = b_med / base
        rec["base_median_dps"] = base
        rec["in_median_dps"] = b_med
        rec["ratio_in_over_out"] = round(ratio, 3)
        if abs(ratio - 1.0) > 0.10:
            rec["verdict"] = (f"MEASURED HOVER-ADDER: cursor OUT base "
                              f"{base} deg/s, INSIDE zone {b_med} deg/s "
                              f"(ratio {ratio:.2f})")
            save()
            return 0
        rec["verdict"] = (f"NEGATIVE (honest): hover adds nothing measurable — "
                          f"OUT {base} deg/s vs IN {b_med} deg/s "
                          f"(ratio {ratio:.2f}, +-10% band)")
        save()
        return 1
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
