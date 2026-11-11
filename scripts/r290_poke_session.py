#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t290: THRESHOLD-FREEZE / POKE at the end-turn pass — measure the comparator.

STATIC LAW THIS INSTRUMENT TESTS (docs/re/_wip_t290.md S1-S2, read verbatim
this session from work/ascend_payload.bin):
  End-of-turn evaluator FUN_00024a34 (file 0x24a34), sole caller 0x252e9 runs
  AFTER the V producer (t284 protocol), gated iff selector DAT_43510 == 0 AND
  dword[0x10ba4] == 0 (MEASURED 0 in banked banks). Comparator @0x24bba:
      eax = floor(2*T/3)+1 ; edi = V ; skip-lose iff eax > edi
  => Control victory iff V >= floor(2T/3)+1. T=50 (only T in corpus) -> 34.

INSTRUMENT (why freeze beats a plain mid-flood poke): the V flood re-reads V
and increments per admit (0x2439d..0x243a8 `mov ecx,[V]; inc ecx; mov [V],ecx`),
so a plain poked value only sticks upward. The debugger's FM breakpoint
(BKPNT_MEMORY_FREEZE, debug.cpp:2875 + the check loop :870-874) writes the
frozen byte back on EVERY instruction-loop-top heavy check (core_normal.cpp:182)
— it overrules the flood deterministically and the evaluator's read at 0x24bb3
sees exactly the frozen value. Freeze granularity is ONE byte; V values 0..50
fit the low byte (upper bytes are always 0 — every producer store is a dword
with zero upper bytes).

SEQUENCE (all addresses from --expect-base; t286b determinism law B=0x1bf4d8):
 1. BREAK at the TITLE screen (t282/t286 best class; r290_relaunch.sh wraps the
    lottery until 'armed:' appears in session.log).
 2. Arm BPLM sentinel on V linear = B-0x88+0x82bb0+0x482fb (== 0x28A2FB at
    expect-base; t283's own target; BPLM survives campaign load, t286 law 1).
 3. EXEC RUN, enter campaign via 'Return to Current Game' (318,333), screen-react
    law, then press END TURN (511,67) — the first V store of the fresh pass
    stops the CPU mid-pass BEFORE the evaluator runs (caller order 0x252bc call
    flood -> 0x252e9 call evaluator).
 4. AT THE STOP: read live ds (EV ds; flat model, bases 0 — witness t286b operand
    panel ss:[00FDA8B3]).
    freeze mode: BPDEL * ; SMV <Vlin> d:<N> ; FM <ds>:<Vlin>
    poke   mode: SMV <Vlin> d:<N> (keep sentinel; drain the increment storm —
               only safe for N >= threshold since writes stick upward)
 5. RUN. Drain fires (log every EIP as file offset). The pass completes: the
    evaluator reads V (frozen/poked), arms sel=5 + rank + fires the end event,
    or returns leaving sel 0. sel!=0 LATCHES (0x252da skips evaluation after).
 6. Evidence: ring rows via r1_slot (turn/V/sel/rank) + screenshots (the
    end-ctrl presenter = "Congratulations! ... over two-thirds" screen).

READ PRIMITIVES NOTE: MEMREAD is real-mode-only (debug.cpp:2983) and
MEMDUMPBIN-with-filename over EXEC is banked-dead (t283) — value verification
rides on fire lines, BPLIST baselines, and the ring.

SAFETY: scratch copy work/r1/game-wp only (asserted, never game/); OWN ring dir
(TWO-WRITER LAW); private Xvfb :96 (never :9); core=normal; -time-limit;
kill-by-recorded-PID in finally; NO Escape ever (t285 law); production :9
untouched.

usage: r290_poke_session.py [--mode freeze|poke] [--arm-value 34]
                            [--port 55999] [--disp 96]
Exit 0 = selector armed after the instrumented pass (comparator operand IS V).
     1 = ran with a negative.  2 = harness error.
"""
import argparse
import glob
import hashlib
import os
import pty
import re
import shutil
import signal
import socket
import struct
import subprocess
import subprocess
import sys
import threading
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_sav_scan as SS                                        # noqa: E402
import r1_slot as SL                                            # noqa: E402

DBG_BIN = os.path.join(ROOT, "work/r1/bin/dosbox-x-dbg")
SCRATCH = os.path.join(ROOT, "work/r1/game-wp")
PAYLOAD = os.path.join(ROOT, "work/ascend_payload.bin")
OCT29 = os.path.join(ROOT, "work/r1/game/RESUME.GAM.user-oct29")
OCT29_MD5 = "5b382afbb789186c3654f3cec085b2e2"
OBJ1_OFF = 0x82bb0
H = 0x88
V_OFF = 0x482fb
FN_FILE = 0x24a34          # evaluator entry (file)
SEED_LO, SEED_HI = 0x25290, 0x252e0     # producer seed region (file)
FLOOD_LO, FLOOD_HI = 0x24274, 0x243f5   # flood fn (file)
RETURN_TO_GAME = (318, 333)
NEXTTURN = (511, 67)
XSEND = os.path.join(ROOT, "tools/xsend")


def dspec(disp):
    return f":{str(disp).lstrip(':')}"


def read_until_end(f, end_marker, budget):
    lines, header = [], None
    t0 = time.time()
    while time.time() - t0 < budget:
        try:
            raw = f.readline()
        except (socket.timeout, OSError):
            continue
        if not raw:
            return lines, False, header
        line = raw.decode("utf-8", "replace").rstrip("\r\n")
        if line == end_marker:
            return lines, True, header
        if line.startswith("BEGIN event"):
            read_until_end(f, "END event", 2.0)
            continue
        if line.startswith("BEGIN "):
            header = line
            continue
        if line:
            lines.append(line)
    return lines, True, header


def drain(master_fd, path):
    with open(path, "wb") as fh:
        while True:
            try:
                data = os.read(master_fd, 65536)
            except OSError:
                return
            if not data:
                return
            fh.write(data)
            fh.flush()


def kill_rec(pid, name):
    try:
        os.kill(pid, signal.SIGKILL)
    except Exception:
        pass


def xsend(disp, args, log):
    # tools/xsend takes the WINDOW TITLE first ("DOSBox-X"), DISPLAY via env
    # (r1_wp_session.py:147 law; a display spec as arg1 is parsed as the
    # window title and every click silently no-ops with rc=1).
    env = dict(os.environ, DISPLAY=dspec(disp))
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
        env.pop(k, None)
    try:
        r = subprocess.run([XSEND, "DOSBox-X"] + args,
                           capture_output=True, text=True, timeout=30,
                           env=env)
        log(f"xsend {args} rc={r.returncode}")
        return r.returncode
    except Exception as e:
        log(f"xsend {args} EXC {e}")
        return -1


def grab(disp, path):
    try:
        r = subprocess.run(["import", "-window", "root", path],
                           capture_output=True, timeout=20,
                           env=dict(os.environ, DISPLAY=dspec(disp)))
        return r.returncode == 0 and os.path.exists(path)
    except Exception:
        return False


def diff_px(a, b):
    try:
        r = subprocess.run(["compare", "-metric", "AE", a, b, "/dev/null"],
                           capture_output=True, text=True, timeout=30)
        return float(r.stderr.strip() or "0")
    except Exception:
        return 0.0


def orange_frac(path):
    try:
        txt = subprocess.run(["convert", path, "-resize", "160x120!",
                              "-depth", "8", "txt:-"],
                             capture_output=True, text=True,
                             timeout=30).stdout
        tot = orange = 0
        for line in txt.splitlines()[1:]:
            m = re.search(r"#([0-9A-Fa-f]{6})", line)
            if not m:
                continue
            r_, g, b = (int(m.group(1)[i:i + 2], 16) for i in (0, 2, 4))
            tot += 1
            if r_ > 140 and g < 120 and b < 100:
                orange += 1
        return orange / max(1, tot)
    except Exception:
        return -1.0


def fire_lines(path):
    if not os.path.exists(path):
        return []
    txt = open(path, "rb").read().decode("utf-8", "replace")
    return [l for l in txt.splitlines() if "Memory breakpoint" in l]


def ring_rows(savedir, anch):
    rows = []
    for p in sorted(glob.glob(os.path.join(savedir, "*.sav")),
                    key=os.path.getmtime):
        try:
            import zipfile
            mem = zipfile.ZipFile(p).read("Memory")
        except Exception:
            continue
        B = SL.base_of(mem, anch)
        if B is None:
            continue
        try:
            rows.append(SL.read_slot(p, mem, B))
        except Exception:
            continue
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["freeze", "poke"], default="freeze")
    ap.add_argument("--arm-value", type=int, default=34,
                    help="value frozen/poked into V (34 arms per static law; "
                         "33 = strict-boundary control; 25 = refutes >1/2)")
    ap.add_argument("--port", type=int, default=55999)
    ap.add_argument("--disp", default="96")
    ap.add_argument("--tl", type=int, default=1500)
    ap.add_argument("--settle", type=int, default=45)
    ap.add_argument("--boot", type=int, default=60)
    ap.add_argument("--expect-base", default="0x1bf4d8")
    ap.add_argument("--fire-wait", type=int, default=300)
    ap.add_argument("--drain-wait", type=int, default=240)
    ap.add_argument("--final-wait", type=int, default=90)
    args = ap.parse_args()

    for p, why in [(DBG_BIN, "debugger binary"), (SCRATCH, "scratch copy"),
                   (PAYLOAD, "payload"), (OCT29, "Oct-29 campaign backup")]:
        if not os.path.exists(p):
            print(f"HARNESS ERROR: missing {why} {p}")
            return 2
    if os.path.abspath(SCRATCH).startswith(os.path.join(ROOT, "game") + os.sep):
        print("HARNESS ERROR: refusing to mount game/")
        return 2
    if hashlib.md5(open(OCT29, "rb").read()).hexdigest() != OCT29_MD5:
        print("HARNESS ERROR: Oct-29 backup md5 mismatch")
        return 2

    B_EXP = int(args.expect_base, 16)
    P0 = B_EXP - H
    V_LIN = P0 + OBJ1_OFF + V_OFF           # 0x28A2FB at expect-base

    out = os.path.join(ROOT, "work/r1",
                       f"t290-{args.mode}-a{args.arm_value}-"
                       f"{time.strftime('%Y%m%d-%H%M%S')}")
    os.makedirs(out, exist_ok=True)
    savedir = os.path.join(out, "save")
    os.makedirs(savedir, exist_ok=True)
    runlog_path = os.path.join(out, "session.log")
    transcript = os.path.join(out, "mcp-transcript.txt")
    ptylog = os.path.join(out, "mcp-pty.log")
    conf = os.path.join(out, "wp.conf")

    def log(msg):
        line = f"{time.strftime('%H:%M:%S')} {msg}"
        print(line, flush=True)
        with open(runlog_path, "a") as fh:
            fh.write(line + "\n")

    def bank(tag, text):
        with open(transcript, "a") as fh:
            fh.write(f"\n=== {tag}\n{text}\n")

    shutil.copy2(OCT29, os.path.join(SCRATCH, "RESUME.GAM"))
    low = os.path.join(SCRATCH, "resume.gam")
    if os.path.exists(low):
        os.rename(low, low + ".vendor-t290")

    with open(conf, "w") as fh:
        fh.write(f"""[dosbox]
machine=svga_s3
memsize=16
core=normal
mcp_server={args.port}
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

    xv = subprocess.Popen(["Xvfb", f":{args.disp}", "-screen", "0",
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
    threading.Thread(target=drain, args=(master, ptylog), daemon=True).start()
    env = dict(os.environ, DISPLAY=f":{args.disp}", TERM="xterm")
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
        env.pop(k, None)
    child = subprocess.Popen(
        [DBG_BIN, "-conf", conf, "-nogui", "-savedir", savedir,
         "-time-limit", str(args.tl)],
        stdin=slave, stdout=slave, stderr=slave, cwd=out, env=env,
        close_fds=True)
    os.close(slave)
    log(f"spawned pid={child.pid} display=:{args.disp} out={out}")
    log(f"mode={args.mode} arm_value={args.arm_value} V_LIN={V_LIN:#08x} "
        f"expect_base={B_EXP:#x}")

    rc = 1
    conn = None
    try:
        t0 = time.time()
        while time.time() - t0 < args.boot:
            try:
                conn, addr = ls.accept()
                log(f"connected OUT after {time.time()-t0:.1f}s")
                break
            except socket.timeout:
                if child.poll() is not None:
                    log(f"child exited early rc={child.returncode}")
                    break
        if conn is None:
            log("NEGATIVE: no MCP connection")
            return 1
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
            return read_until_end(f, f"END {rid}", budget)

        def ev(reg):
            lines, ok, hdr = req(f"EXEC EV {reg}", 10.0)
            nums = [l.strip() for l in lines if l.strip()]
            try:
                return int(nums[-1], 16), hdr
            except (ValueError, IndexError):
                return None, hdr

        lines, ok, hdr = req("PING", 10.0)
        if "PONG" not in " ".join(lines):
            log("NEGATIVE: no PONG")
            return 1
        log(f"settling {args.settle}s at title")
        time.sleep(args.settle)

        # ---- BREAK at title (lottery; relaunch wrapper owns retries) -------
        stopped = False
        for attempt in range(3):
            lines, ok, hdr = req("BREAK", 60.0)
            log(f"BREAK#{attempt} hdr={hdr} lines={lines[:3]}")
            if hdr is not None and not hdr.rstrip().endswith("ERR"):
                lines, ok, hdr = req("EXEC BPLIST", 10.0)
                if hdr is not None:
                    stopped = True
                    break
            lines, ok, _ = req("PING", 15.0)
            if "PONG" not in " ".join(lines):
                log("channel dead after BREAK (lottery loss)")
                return 1
            time.sleep(10.0)
        if not stopped:
            log("NEGATIVE: BREAK never stopped the debugger")
            return 1
        cs, _ = ev("cs")
        ds, _ = ev("ds")
        log(f"armed: debugger stopped at title (cs={cs and hex(cs)} "
            f"ds={ds and hex(ds)})")
        bank("title", f"cs={cs and hex(cs)} ds={ds and hex(ds)}")

        lines, ok, hdr = req(f"EXEC BPLM {V_LIN:08X}", 15.0)
        log(f"sentinel BPLM {V_LIN:08X} hdr={hdr} lines={lines}")
        lines, ok, hdr = req("EXEC BPLIST", 10.0)
        log(f"BPLIST: {lines}")
        bank("sentinel-armed", " | ".join(lines))
        if not [l for l in lines if "BPLM" in l]:
            log("NEGATIVE: sentinel BPLM not listed")
            return 1

        seen = fire_lines(ptylog)
        lines, ok, hdr = req("EXEC RUN", 10.0)
        log("RUN — entering campaign with sentinel armed")

        # ---- enter campaign -------------------------------------------------
        a = os.path.join(out, "screen_pre_click.png")
        b = os.path.join(out, "screen_post_click.png")
        grab(args.disp, a)
        entered = False
        t0 = time.time()
        last_click = 0.0
        while time.time() - t0 < 300 and not entered:
            cur = fire_lines(ptylog)
            new = [l for l in cur if l not in seen]
            if new:
                seen = cur
                eip, _ = ev("eip")
                log(f"ENTRY PHASE FIRE eip={eip and hex(eip)}: {new[-1]}")
                lines, ok, hdr = req("EXEC RUN", 10.0)
                if hdr is None:
                    log("NEGATIVE: channel dead after entry fire")
                    return 1
                continue
            if time.time() - last_click > 20:
                xsend(args.disp, ["click", str(RETURN_TO_GAME[0]),
                                  str(RETURN_TO_GAME[1])], log)
                last_click = time.time()
            time.sleep(2.0)
            if grab(args.disp, b) and diff_px(a, b) > 2000:
                entered = True
                shutil.copy2(b, os.path.join(out, "screen_entered.png"))
                log("ENTER: screen reacted — campaign load presumed")
        if not entered:
            log("NEGATIVE: campaign entry never reacted")
            return 1

        log("post-load settle 60s (ring base vote; no V writes until End Turn)")
        time.sleep(60)
        pay = open(PAYLOAD, "rb").read()
        anch = SS.build_anchors(pay)
        rows = ring_rows(savedir, anch)
        for r_ in rows[-3:]:
            log(f"ring {r_['file']}: turn={r_['turn']} V={r_['score_stars']} "
                f"sel={r_['selector_byte']} rank={r_['rank']}")
        if not rows or rows[-1]["turn"] == 0:
            log("NEGATIVE: ring shows no campaign")
            return 1
        if rows[-1]["selector_byte"] != 0:
            log(f"NEGATIVE: selector pre-instrument already "
                f"{rows[-1]['selector_byte']}")
            return 1
        bank("pre-instrument-ring", "\n".join(
            f"{r_['file']} t{r_['turn']} V{r_['score_stars']} "
            f"sel{r_['selector_byte']} rank{r_['rank']}" for r_ in rows[-4:]))

        # ---- END TURN: catch the mid-pass stop ------------------------------
        xsend(args.disp, ["click", str(NEXTTURN[0]), str(NEXTTURN[1])], log)
        stop_eip = None
        t0 = time.time()
        last_inject = time.time()
        while time.time() - t0 < args.fire_wait:
            cur = fire_lines(ptylog)
            new = [l for l in cur if l not in seen]
            if new:
                seen = cur
                stop_eip, _ = ev("eip")
                break
            s = os.path.join(out, f"screen_wait_{int(time.time()-t0)}.png")
            if grab(args.disp, s) and orange_frac(s) > 0.20:
                log("NEGATIVE: title menu on screen mid-wait (t285 class)")
                shutil.copy2(s, os.path.join(out, "screen_titlebail.png"))
                return 1
            if time.time() - last_inject > 25:
                xsend(args.disp, ["click", str(NEXTTURN[0]),
                                  str(NEXTTURN[1])], log)
                last_inject = time.time()
            time.sleep(2.0)
        if stop_eip is None:
            log("NEGATIVE: no sentinel fire after End Turn in budget — "
                "producer never ran (off-map? softlock? BP lost?)")
            grab(args.disp, os.path.join(out, "screen_firebail.png"))
            return 1
        fo = stop_eip - P0
        kind = ("SEED" if SEED_LO <= fo <= SEED_HI else
                "FLOOD" if FLOOD_LO <= fo <= FLOOD_HI else "OTHER")
        log(f"MID-PASS STOP eip={stop_eip:#x} file={fo:#x} [{kind}]")
        bank("mid-pass-stop", f"eip={stop_eip:#x} file={fo:#x} kind={kind}")

        live_ds, _ = ev("ds")
        live_esi, _ = ev("esi")
        log(f"at stop: ds={live_ds and hex(live_ds)} "
            f"esi={live_esi and hex(live_esi)}")
        bank("stop-registers", f"ds={live_ds and hex(live_ds)} "
                               f"esi={live_esi and hex(live_esi)} "
                               f"(esi==state ptr iff in campaign heap/BSS)")
        # FM/BPPM resolve via GetAddress(seg,off): needs a FLAT 32-bit data
        # selector (base 0, big). Witness: t286b operand panel printed
        # ss:[00FDA8B3] flat. Self-check: ds must be a plausible pmode
        # selector (>= 0x08) and NOT resolve 16-bit-masked; if in doubt use
        # seg 0000 (t282/t283 seg-0000 linear witness class).
        seg_for_fm = live_ds if (live_ds or 0) >= 0x08 else 0x0000

        # ---- THE INSTRUMENT -------------------------------------------------
        av = args.arm_value
        if args.mode == "freeze":
            lines, ok, hdr = req("EXEC BPDEL *", 10.0)
            log(f"BPDEL * hdr={hdr} lines={lines}")
            lines, ok, hdr = req(f"EXEC SMV {V_LIN:08X} d:{av}", 15.0)
            log(f"SMV V:={av} hdr={hdr} lines={lines}")
            lines, ok, hdr = req(f"EXEC FM {seg_for_fm:04X}:{V_LIN:08X}", 15.0)
            log(f"FM {seg_for_fm:04X}:{V_LIN:08X} hdr={hdr} lines={lines}")
            if "Set memory freeze" not in " ".join(lines):
                log("fallback: FM with seg 0000 (flat linear witness class)")
                lines, ok, hdr = req(f"EXEC FM 0000:{V_LIN:08X}", 15.0)
                log(f"FM 0000 hdr={hdr} lines={lines}")
            instrument_cmd = f"SMV d:{av} + FM {seg_for_fm:04X}:{V_LIN:08X}"
        else:
            lines, ok, hdr = req(f"EXEC SMV {V_LIN:08X} d:{av}", 15.0)
            log(f"SMV V:={av} hdr={hdr} lines={lines}")
            instrument_cmd = f"SMV d:{av} (poke, sentinel kept)"
        lines, ok, hdr = req("EXEC BPLIST", 10.0)
        log(f"BPLIST post-instrument: {lines}")
        bank("instrument", instrument_cmd + "\nBPLIST: " + " | ".join(lines))

        # ---- RUN: the pass completes with the frozen/poked V ----------------
        seen = fire_lines(ptylog)
        lines, ok, hdr = req("EXEC RUN", 10.0)
        log("DECISIVE RUN")
        fires_after = []
        t0 = time.time()
        quiet_since = None
        while time.time() - t0 < args.drain_wait:
            cur = fire_lines(ptylog)
            new = [l for l in cur if l not in seen]
            if new:
                seen = cur
                quiet_since = None
                eip2, _ = ev("eip")
                fo2 = (eip2 - P0) if eip2 is not None else None
                fires_after.append((eip2, fo2, new[-1]))
                log(f"POST-INSTRUMENT FIRE +{time.time()-t0:.1f}s "
                    f"eip={eip2 and hex(eip2)} file={fo2 and hex(fo2)}: "
                    f"{new[-1]}")
                lines, ok, hdr = req("EXEC RUN", 10.0)
                if hdr is None:
                    log("NEGATIVE: channel dead mid-drain")
                    return 1
            else:
                if quiet_since is None:
                    quiet_since = time.time()
                elif time.time() - quiet_since > 40:
                    break
            time.sleep(2.0)
        # release once more in case we sit stopped at the drain boundary
        lines, ok, hdr = req("EXEC RUN", 10.0)
        bank("post-instrument-fires",
             "\n".join(f"{e and hex(e)} {f and hex(f)} {l}"
                       for e, f, l in fires_after) or "(none)")

        # ---- EVIDENCE --------------------------------------------------------
        time.sleep(args.final_wait)
        grab(args.disp, os.path.join(out, "screen_final.png"))
        of = orange_frac(os.path.join(out, "screen_final.png"))
        log(f"final screen orange frac {of:.3f} (0.20 title gate; victory "
            "screen is dark starfield per presenter)")
        rows = ring_rows(savedir, anch)
        tf_rows = []
        for r_ in rows[-8:]:
            line = (f"{r_['file']} turn={r_['turn']} V={r_['score_stars']} "
                    f"sel={r_['selector_byte']} rank={r_['rank']}")
            log("ring " + line)
            tf_rows.append(line)
        bank("final-ring", "\n".join(tf_rows))
        armed = [r_ for r_ in rows if r_["selector_byte"] != 0]
        if armed:
            log(f"POSITIVE: selector armed -> "
                f"{[(r_['selector_byte'], r_['rank']) for r_ in armed]} — "
                f"comparator consumed V frozen/poked to {av}")
            rc = 0
        else:
            log(f"NEGATIVE: V frozen/poked to {av}, selector never armed "
                f"post-instrument (fires: {len(fires_after)})")
            rc = 1
    finally:
        shutil.copytree(savedir, os.path.join(out, "ring-final"),
                        dirs_exist_ok=True)
        kill_rec(child.pid, "dosbox-x-dbg")
        kill_rec(xv.pid, "Xvfb")
        ls.close()
        try:
            os.close(master)
        except OSError:
            pass
    log(f"DONE rc={rc} out={out}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
