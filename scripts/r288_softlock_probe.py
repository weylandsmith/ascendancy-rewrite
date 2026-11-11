#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t288: SOFTLOCK-CLASS LIVE PROBE — restore the soft save, watch the game's
own pending-input globals, inject a key, name the dead half.

Laws this encodes (all previously measured; see docs/re/selfplay.md t260/t261/
t266, docs/re/dosbox-debugger.md t282/t286, docs/re/_wip_t288.md S0-S1b):
 * loadstate is Capture-MENU-only (GUI, no -nogui); xsend synthetic BUTTON
   events drive the SDL2 menu; keys are delivered too (t260/t287).
 * TL-BOUNCE: NEVER -time-limit a process you loadstate INTO. Bound externally.
 * OWN ring dir (TWO-WRITER law); scratch mount only (never game/, never :9).
 * BREAK is a per-attempt lottery (t286 law 2) -> relaunch loop, arm at TITLE
   (t282 3/3 class); BPLM survives save-restore (t286 law 1).
 * The debugger binary is work/r1/bin/dosbox-x-dbg (mcp_server conf option);
   the RELEASE /usr/bin/dosbox-x has ZERO BPLM strings -> fallback session
   (--binary rel --no-break) still answers the ring-level question.
 * Cross-version load: bank is DOSBox-X 2025.02.01, dbg build is 2026.10.01
   master -> forceloadstate=true set as the documented mismatch bypass.

Instrument: BPLM on data:0x484c6 (pending-input CHAR; the msg word is
data:0x484c4 — t103 P13 relay law; census S1/S1b: softlocked saves sit STUCK
at (msg=1,char=0x1b), healthy idle sits (0,0), healthy post-'c' (0x2e,0x63)).
Inject 'c' (char 0x63) into the RESTORED soft session:
   ring globals change  -> the game-side pump WRITES: dead half is downstream.
   globals frozen       -> pump never writes the key: event bridge dead.
BPLM fires (when armed) print the value pair; EV eip banks the writer EIP.

Exit 0 = restored + injected + censored (fires optional).
     1 = negative (no load / no ring rows). 2 = harness error.
"""
import argparse
import glob
import json
import os
import pty
import shutil
import signal
import socket
import struct
import subprocess
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_sav_scan as SS                                   # noqa: E402
import r1_wp_session as WP                                 # noqa: E402

DBG = os.path.join(ROOT, "work/r1/bin/dosbox-x-dbg")
REL = "/usr/bin/dosbox-x"
MOUNTDIR = os.path.join(ROOT, "work/r1/game-t288")
SRC = os.path.join(ROOT, "work/r1/bank-t251-live1255/60.sav")
SRC_MD5 = "0024340df46c0375ce6472e085345e71"
RESUME_MD5 = "5b382afbb789186c3654f3cec085b2e2"           # Oct-29 (t287 law)
PAYLOAD = WP.PAYLOAD
H, OBJ1_OFF = WP.H, WP.OBJ1_OFF
CAPTURE_MENU = (315, 8)      # t260 measured on 2025.02.01 GUI
LOAD_ROW = (350, 197)        # t260 measured on 2025.02.01 GUI
NEUTRAL = (200, 300)         # starmap neutral spot (t286 run-4 law)
OFF_MSG, OFF_CHAR = 0x484c4, 0x484c6
OFF_MX, OFF_MY = 0x48ec, 0x484f0
TURN_OFF = 0x12e10           # t249b day==turn site (readout dword == turn)


def md5(p):
    import hashlib
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def census(mem, B):
    b = B + OBJ1_OFF
    g = lambda off, fmt="<H": struct.unpack_from(fmt, mem, b + off)[0]
    return dict(msg=g(OFF_MSG), char=g(OFF_CHAR), mx=g(OFF_MX), my=g(OFF_MY),
                turn=g(TURN_OFF, "<I"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--disp", default="91")
    ap.add_argument("--port", type=int, default=55998)
    ap.add_argument("--settle", type=int, default=45)
    ap.add_argument("--binary", choices=["dbg", "rel"], default="dbg")
    ap.add_argument("--no-break", action="store_true")
    ap.add_argument("--attempts", type=int, default=2)
    ap.add_argument("--campaign-wait", type=int, default=300)
    ap.add_argument("--inject-wait", type=int, default=25)
    ap.add_argument("--no-load", action="store_true",
                    help="healthy CONTROL mode: skip Capture->Load; enter the "
                         "campaign via Return-to-Game click (t286-proven "
                         "channel) and run the same injections; expect turn "
                         "1086 (RESUME.GAM), not 1255")
    args = ap.parse_args()

    if md5(SRC) != SRC_MD5:
        print(f"HARNESS ERROR: bank md5 {md5(SRC)}"); return 2
    if not os.path.isdir(MOUNTDIR):
        print(f"HARNESS ERROR: no scratch mount {MOUNTDIR}"); return 2
    if md5(os.path.join(MOUNTDIR, "RESUME.GAM")) != RESUME_MD5:
        print("HARNESS ERROR: scratch RESUME.GAM != Oct-29"); return 2
    BIN = DBG if args.binary == "dbg" else REL
    if args.binary == "dbg" and not os.path.exists(DBG):
        print("HARNESS ERROR: dbg binary missing"); return 2
    no_break = args.no_break or args.binary == "rel"

    pay = open(PAYLOAD, "rb").read()
    anch = SS.build_anchors(pay)
    results = dict(binary=args.binary, attempts=[])

    for attempt in range(args.attempts):
        out = os.path.join(ROOT, "work/r1",
                           f"t288-probe-{args.binary}-a{attempt}-"
                           f"{time.strftime('%Y%m%d-%H%M%S')}")
        os.makedirs(out)
        savedir = os.path.join(out, "save")
        os.makedirs(savedir)
        shutil.copy2(SRC, os.path.join(savedir, "60.sav"))
        runlog = os.path.join(out, "session.log")
        ptylog = os.path.join(out, "pty.log")
        conf = os.path.join(out, "probe.conf")

        def log(msg):
            line = f"{time.strftime('%H:%M:%S')} {msg}"
            print(line, flush=True)
            with open(runlog, "a") as fh:
                fh.write(line + "\n")

        with open(conf, "w") as fh:
            fh.write(f"""[dosbox]
machine=svga_s3
memsize=16
core=normal
mcp_server={args.port}
captures={out}/caps
autosave=10 41-60
saveremark=false
saveslot=60
forceloadstate=true
[sdl]
output=x11
fullscreen=false
autolock=false
[mixer]
nosound=true
[autoexec]
MOUNT C {MOUNTDIR}
C:
ASCEND.EXE
""")
        rec = dict(out=out)
        xv = subprocess.Popen(["Xvfb", WP.dspec(args.disp), "-screen", "0",
                               "800x600x24"],
                              stdout=open(os.path.join(out, "xvfb.out"), "wb"),
                              stderr=subprocess.STDOUT)
        time.sleep(1.5)
        ls = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ls.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ls.bind(("127.0.0.1", args.port))
        ls.listen(1)
        ls.settimeout(2.0)
        master, slave = pty.openpty()
        import threading
        threading.Thread(target=WP.drain, args=(master, ptylog),
                         daemon=True).start()
        env = dict(os.environ, DISPLAY=WP.dspec(args.disp), TERM="xterm")
        for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
            env.pop(k, None)
        # NO -nogui (menu law), NO -time-limit (TL-BOUNCE law). Bounded by the
        # script's own finally + a belt: the harness kills by recorded pid.
        child = subprocess.Popen([BIN, "-conf", conf, "-savedir", savedir],
                                 stdin=slave, stdout=slave, stderr=slave,
                                 cwd=out, env=env, close_fds=True)
        os.close(slave)
        log(f"spawned pid={child.pid} disp={WP.dspec(args.disp)} out={out}")
        try:
            conn = None
            if not no_break:
                t0 = time.time()
                while time.time() - t0 < 90:
                    try:
                        conn, _ = ls.accept()
                        log(f"mcp connected after {time.time()-t0:.1f}s")
                        break
                    except socket.timeout:
                        if child.poll() is not None:
                            log(f"child exited early rc={child.returncode}")
                            break
                if conn is None:
                    rec["fail"] = "no mcp connection"
                    results["attempts"].append(rec)
                    continue
                conn.settimeout(0.5)
                f = conn.makefile("rwb")
                seq = [0]

                def req(verb, budget=30.0):
                    seq[0] += 1
                    rid = str(seq[0])
                    try:
                        f.write(f"REQ {rid} {verb}\n".encode())
                        f.flush()
                    except OSError as e:
                        log(f"channel dead ({e}) at {verb!r}")
                        return [], False, None
                    return WP.read_until_end(f, f"END {rid}", budget)
            else:
                req = None
                t0 = time.time()
                while time.time() - t0 < 90 and child.poll() is None:
                    if WP.window_alive(args.disp):
                        break
                    time.sleep(2)

            log(f"settling {args.settle}s")
            time.sleep(args.settle)
            WP.grab(args.disp, os.path.join(out, "screen_title.png"))

            armed = False
            lin = None
            if not no_break:
                lines, ok, hdr = req("PING", 15.0)
                if "PONG" not in " ".join(lines):
                    rec["fail"] = "no PONG at title"
                    results["attempts"].append(rec)
                    continue
                # title base for the derived address
                Bt, memt, slot = WP.ring_mem(savedir, anch, log, budget=120.0)
                log(f"TITLE base B={Bt and hex(Bt)} slot={slot}")
                rec["title_base"] = Bt
                if Bt is None:
                    log("NEGATIVE(arm): no base vote at title; continuing "
                        "without bp")
                else:
                    lin = Bt - H + OBJ1_OFF + OFF_CHAR
                    lines, ok, hdr = req("BREAK", 60.0)
                    log(f"BREAK hdr={hdr} lines={lines[:4]}")
                    if hdr is not None and not hdr.rstrip().endswith("ERR"):
                        lines, ok, hdr = req(f"EXEC BPLM {lin:08X}", 15.0)
                        lines, ok, hdr = req("EXEC BPLIST", 10.0)
                        ab = [l for l in lines if "BPLM" in l]
                        log(f"armed: {ab}")
                        armed = (len(ab) == 1)
                        rec["armed"] = ab
                    else:
                        log("BREAK lottery LOST this attempt")
            if not no_break:
                lines, ok, hdr = req("EXEC RUN", 10.0)
                log(f"RUN hdr={hdr} — entering load phase with bp armed")
                if hdr is None:
                    rec["fail"] = "RUN channel dead"
                    results["attempts"].append(rec)
                    continue
            else:
                log("rel-binary: no debugger; ring-level probe only")

            def seen_fires():
                if not os.path.exists(ptylog):
                    return []
                txt = open(ptylog, "rb").read().decode("utf-8", "replace")
                return [l.strip() for l in txt.splitlines()
                        if "Memory breakpoint" in l]

            seen = seen_fires()

            # ---- Capture -> Load state (menu clicks; verify by LOG) --------
            if args.no_load:
                entered = WP.enter_campaign(out, args.disp, log)
                rec["entered"] = entered
                if not entered:
                    rec.setdefault("fail", "control entry click never moved screen")
                    results["attempts"].append(rec)
                    continue
            else:
                log("opening Capture menu")
                WP.xsend(args.disp, ["click", str(CAPTURE_MENU[0]),
                                     str(CAPTURE_MENU[1])], log)
                time.sleep(1.5)
                WP.grab(args.disp, os.path.join(out, "screen_capturemenu.png"))
                log(f"clicking Load state row {LOAD_ROW}")
                WP.xsend(args.disp, ["click", str(LOAD_ROW[0]),
                                     str(LOAD_ROW[1])], log)
            loaded = False
            t0 = time.time()
            while (not args.no_load) and time.time() - t0 < 120:
                time.sleep(4)
                cur = seen_fires()
                new = [l for l in cur if l not in seen]
                if new:
                    seen = cur
                    eips = []
                    if not no_break:
                        for _ in new:
                            le, _, _ = req("EXEC EV eip", 8.0)
                            nums = [x.strip() for x in le if x.strip()]
                            eips.append(nums[-1] if nums else "?")
                        log(f"LOAD-PHASE FIRES eips={eips} vals={new[:6]}")
                        req("EXEC RUN", 10.0)
                    else:
                        log(f"FIRES (unarmed read): {new[:6]}")
                    continue
                with open(os.path.join(out, "pty.log"), errors="replace") as fh:
                    tail = fh.read()
                if "Loaded. (Slot 60)" in tail or "Loading state from slot: 60" in tail:
                    loaded = True
                    log("LOG confirms loadstate")
                    break
            rec["loaded_log"] = loaded

            # ---- ring confirms turn 1255 -----------------------------------
            B, mem, slot = WP.ring_mem(savedir, anch, log,
                                       budget=args.campaign_wait)
            if B is None:
                rec.setdefault("fail", "no campaign rows after load")
                WP.grab(args.disp, os.path.join(out, "screen_nocamp.png"))
                results["attempts"].append(rec)
                continue
            c0 = census(mem, B)
            log(f"RING {os.path.basename(slot)} B={B:#x} census={c0}")
            rec["census_post_load"] = c0
            if c0["turn"] != 1255:
                log(f"NOTE: ring turn {c0['turn']} != 1255 (churn? record as-is)")
            WP.grab(args.disp, os.path.join(out, "screen_after_load.png"))

            # ---- INJECTIONS -------------------------------------------------
            # NOTE (t282 law): a fire STOPS the CPU and autosave does not tick
            # while stopped — ring reads then go STALE. So check fires FIRST;
            # a fire IS the positive result and gets its EIP + dump banked.
            def fire_note(tag):
                cur = seen_fires()
                new = [l for l in cur if l not in seen]
                if not new:
                    return False
                seen[:] = cur
                eips = []
                if not no_break:
                    for _ in new:
                        le, _, _ = req("EXEC EV eip", 8.0)
                        nums = [x.strip() for x in le if x.strip()]
                        eips.append(nums[-1] if nums else "?")
                    WP.dump_stopped(req, out, B, log,
                                    eip=(int(eips[0], 16)
                                         if eips and eips[0] != "?" else None))
                    req("EXEC RUN", 10.0)
                log(f"FIRE during {tag}: eips={eips} vals={new[:6]}")
                rec.setdefault("phase_fires", []).append(
                    {"tag": tag, "eips": eips, "lines": new[:6]})
                return True

            tl = []
            tl.append(("post_load", c0))
            log("inject neutral click (warps pointer)")
            WP.xsend(args.disp, ["click", str(NEUTRAL[0]), str(NEUTRAL[1])], log)
            time.sleep(args.inject_wait)
            fire_note("click")
            B2, mem2, s2 = WP.ring_mem(savedir, anch, log, budget=40.0)
            if mem2 is not None:
                tl.append(("after_click", census(mem2, B2)))
                log(f"census after_click: {tl[-1]}")
            log("inject KEY 'c' (char 0x63)")
            WP.xsend(args.disp, ["key", "c"], log)
            time.sleep(args.inject_wait)
            B3, mem3, s3 = WP.ring_mem(savedir, anch, log, budget=40.0)
            if mem3 is not None:
                tl.append(("after_key", census(mem3, B3)))
                log(f"census after_key: {tl[-1]}")
            log("inject KEY 'c' again + wait a full ring lap")
            WP.xsend(args.disp, ["key", "c"], log)
            time.sleep(args.inject_wait * 2)
            B4, mem4, s4 = WP.ring_mem(savedir, anch, log, budget=40.0)
            if mem4 is not None:
                tl.append(("after_key2", census(mem4, B4)))
                log(f"census after_key2: {tl[-1]}")
            rec["timeline"] = tl
            cur = seen_fires()
            rec["fires_all"] = list(cur)
            if armed and not no_break:
                le, _, _ = req("EXEC EV eip", 8.0)
                rec["eip_now"] = [x.strip() for x in le if x.strip()]
                bank = WP.dump_stopped(req, out, B, log)
                rec["dump"] = bank
            shutil.copytree(savedir, os.path.join(out, "ring-final"),
                            dirs_exist_ok=True)
            WP.grab(args.disp, os.path.join(out, "screen_final.png"))
            rec["ok"] = True
            results["attempts"].append(rec)
            break   # one good attempt is enough
        finally:
            WP.kill_rec(child.pid, "dosbox")
            WP.kill_rec(xv.pid, "Xvfb")
            ls.close()
            try:
                os.close(master)
            except OSError:
                pass

    with open(os.path.join(ROOT, "work/r1", "t288_results.json"), "w") as fh:
        json.dump(results, fh, indent=1)
    ok_any = any(a.get("ok") for a in results["attempts"])
    print(f"DONE ok={ok_any} results=work/r1/t288_results.json")
    return 0 if ok_any else 1


if __name__ == "__main__":
    sys.exit(main())
