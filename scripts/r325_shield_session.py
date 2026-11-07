#!/usr/bin/env python3
"""r325_shield_session.py — t325 PER-SLOT SHIELD-BYTE WRITNESS (OQ-016 res 4).

The scratch campaign (RESUME.GAM.user-oct29, md5-pinned) carries a PENDING
ORBITAL SHIELD build at Gridsor I: item 26, acc=30, reserved slot 76
raw=011a0000 (t271 reservation law; measured scripts/r325b_oct29_check.py).
Build law acc += word IND (t274 pin 0x39005/0x3907b), COST 60 runtime (item
row) => completion fires ~5 End-Turn clicks after load.

Flow: boot dbg dosbox-x on scratch (game-wp) -> Return to Current Game ->
resolve Gridsor I slot array from THIS session's own ring (vendor pointer
values are dead addresses; loader re-allocs) -> verify reserved pattern ->
BREAK (lottery, t286 law 2) -> BPLM (arr+4*76+3 - 0x88) (t286b off-by-H) ->
RUN -> NEXTTURN clicks + fire watch. Baseline 0 => NO artifact rejection
(t286b: first fire IS first write). On fire: bank regs/EIP/code+stack
(dump_stopped), BPDEL *, RUN, 2 more turns, bank ring-post for the value law.

Laws honoured: own ring dir (two-writer), kill-by-recorded-PID, xsend arg1 =
window title (t290), core=normal, never mount game/, production untouched.
Exit: 0 witnessed fire, 1 negative, 2 harness error.
"""
import glob
import os
import re
import shutil
import socket
import struct
import subprocess
import sys
import threading
import time
import time as _t
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import r1_wp_session as W            # noqa: E402  (constants + proven helpers)
import r1_income_law as IL           # noqa: E402
import r1_sav_scan as SS             # noqa: E402

TARGET_PLANET = b"Gridsor I"
PENDING_ITEM = 26
SLOT_IDX = 76
RESERVED = bytes([0x01, 0x1A, 0x00, 0x00])
NEXTTURN = W.NEXTTURN                 # (511, 67) window-rel
DISP = "97"
PORT = 55999


def dspec(d):
    return d if d.startswith(":") else f":{d}"


# ---- popup drain (t245 MEASURED laws, scripts/r1_t245_turndrive.py) --------
# Construction popups SERIALIZE input (NEXTTURN swallowed while open); Escape
# does NOT close them; OK click does. Box dark w/ cyan trim -> detect by
# WHITE-TEXT pixel count in band y 330..470 x 170..486. Hit rect = label-row
# top - 3 (y=443 works, 455/460 MISS). t245 ran on root with the dosbox window
# at origin (80,100); our Xvfb 800x600 renders the SAME origin (measured:
# content bbox (80,100)-(716,576)) -> drain clicks convert root->window-rel.
def popup_ok_center(img_path):
    # ppm:- HAS a header (rgb:- is HEADERLESS raw bytes — using it made this
    # detector silently return None all of attempt 3; fixed this session).
    r = subprocess.run(["convert", img_path, "ppm:-"], capture_output=True,
                       timeout=30)
    if r.returncode != 0 or len(r.stdout) < 20:
        return None
    data = r.stdout
    m = re.match(rb"P6\s+(\d+)\s+(\d+)\s+255\s", data)
    if not m:
        return None
    IW, IH = int(m.group(1)), int(m.group(2))
    px = data[m.end():]

    def white(x, y):
        k = (y * IW + x) * 3
        return px[k] > 190 and px[k+1] > 190 and px[k+2] > 190
    rows = {}
    for y in range(330, min(470, IH)):
        xs = [x for x in range(170, min(486, IW)) if white(x, y)]
        if len(xs) > 8:
            rows[y] = xs
    if sum(len(v) for v in rows.values()) < 120:
        return None
    ybot = max(rows)
    groups = []
    for x in sorted(set(rows[ybot])):
        if groups and x - groups[-1][-1] <= 8:
            groups[-1].append(x)
        else:
            groups.append([x])
    okg = groups[-1]
    ytop = min(y for y in rows if y >= ybot - 12)
    return (sum(okg) // len(okg), ytop - 3)


def drain_popups(disp, log, maxn=25, outdir="."):
    """t245 LAW: detector works in ROOT px (import -window root); xsend takes
    WINDOW-RELATIVE coords -> subtract the window origin (80,100; re-verified
    this session: content bbox of drain_0.png == (80,100)-(716,576))."""
    XOFF, YOFF = 80, 100
    closed = 0
    for k in range(maxn):
        p = os.path.join(outdir, f"drain_{k}.png")
        if not W.grab(disp, p):
            break
        c = popup_ok_center(p)
        if c is None:
            return closed
        log(f"popup OK at root {c} -> window-rel ({c[0]-XOFF},{c[1]-YOFF})")
        W.xsend(disp, ["click", str(c[0] - XOFF), str(c[1] - YOFF)], log)
        closed += 1
        time.sleep(2.5)
    return closed


def latest_ring(savedir):
    """Newest readable ring slot -> (B, mem, path) or (None,None,None)."""
    for p in sorted(glob.glob(os.path.join(savedir, "*.sav")),
                    key=os.path.getmtime, reverse=True):
        try:
            mem = zipfile.ZipFile(p).read("Memory")
        except Exception:
            continue
        votes, _ = SS.find_base(mem, W_ANCH)
        if votes and votes.most_common(1)[0][1] >= 5:
            return votes.most_common(1)[0][0], mem, p
    return None, None, None


def read_turn(mem, B):
    return struct.unpack_from("<I", mem, B + W.OBJ1_OFF + 0x12E10)[0]


def find_target(mem, log):
    """-> (base, arr, slot_addr_member, lin) or None. Verifies the pending
    build AND the reserved-slot pattern before trusting any address."""
    for base, cells, cap, arr in IL.find_records(mem):
        name = mem[base + 0x24:base + 0x33].split(b"\x00")[0]
        if name != TARGET_PLANET:
            continue
        it = mem[base + 0x54]
        acc = struct.unpack_from("<H", mem, base + 0x50)[0]
        ind = struct.unpack_from("<H", mem, base + 0x44)[0]
        s = arr + 4 * SLOT_IDX
        raw4 = mem[s:s + 4]
        log(f"Gridsor I: pending item={it} acc={acc} IND={ind} cap={cap} "
            f"slot{SLOT_IDX} raw={raw4.hex()}")
        if it != PENDING_ITEM:
            log("pending item moved (build completed before arming?) — "
                "honest negative for THIS attempt")
            return None
        if raw4 != RESERVED:
            log(f"reserved pattern mismatch (want {RESERVED.hex()}) — "
                "refusing to arm a blind byte")
            return None
        member = s + 3
        lin = member - W.H
        log(f"TARGET byte3 member=0x{member:x} -> BPLM linear=0x{lin:08X}")
        return base, arr, member, lin
    log("Gridsor I record not found in this ring slot")
    return None


def main():
    t_start = _t.time()
    ts = time.strftime("%Y%m%d-%H%M%S")
    out = os.path.join(ROOT, "work/r1", f"t325-shield-{ts}")
    os.makedirs(out, exist_ok=True)
    savedir = os.path.join(out, "save")
    os.makedirs(savedir, exist_ok=True)   # autosave failure kills window (t283)
    runlog = os.path.join(out, "session.log")
    ptylog = os.path.join(out, "mcp-pty.log")
    transcript = os.path.join(out, "mcp-transcript.txt")

    def log(msg):
        line = f"{time.strftime('%H:%M:%S')} {msg}"
        print(line, flush=True)
        with open(runlog, "a") as fh:
            fh.write(line + "\n")

    # ---- preflight ---------------------------------------------------------
    for p, why in [(W.DBG_BIN, "debugger binary"), (W.SCRATCH, "scratch"),
                   (W.PAYLOAD, "payload"), (W.OCT29, "oct29 state"),
                   (W.XSEND, "xsend")]:
        if not os.path.exists(p):
            log(f"HARNESS ERROR: missing {why} {p}")
            return 2
    import hashlib
    if hashlib.md5(open(W.OCT29, "rb").read()).hexdigest() != W.OCT29_MD5:
        log("HARNESS ERROR: oct29 md5 mismatch")
        return 2
    if os.path.abspath(W.SCRATCH).startswith(os.path.join(ROOT, "game") + os.sep):
        log("HARNESS ERROR: scratch inside game/")
        return 2

    shutil.copy2(W.OCT29, os.path.join(W.SCRATCH, "RESUME.GAM"))
    low = os.path.join(W.SCRATCH, "resume.gam")
    if os.path.exists(low):
        os.rename(low, low + ".vendor-t325")

    conf = os.path.join(out, "session.conf")
    with open(conf, "w") as fh:
        fh.write(f"""[dosbox]
machine=svga_s3
memsize=16
mcp_server={PORT}
captures={out}/caps
autosave=10 41-60
saveremark=false
[cpu]
core=normal
[sdl]
output=x11
fullscreen=false
autolock=false
[mixer]
nosound=true
[autoexec]
MOUNT C {W.SCRATCH}
C:
ASCEND.EXE
""")

    xv = subprocess.Popen(["Xvfb", dspec(DISP), "-screen", "0", "800x600x24"],
                          stdout=open(os.path.join(out, "xvfb.out"), "wb"),
                          stderr=subprocess.STDOUT)
    time.sleep(1.5)
    ls = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ls.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ls.bind(("127.0.0.1", PORT))
    ls.listen(1)
    ls.settimeout(2.0)
    import pty
    master, slave = pty.openpty()
    threading.Thread(target=W.drain, args=(master, ptylog), daemon=True).start()
    env = dict(os.environ, DISPLAY=dspec(DISP), TERM="xterm")
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
        env.pop(k, None)
    child = subprocess.Popen(
        [W.DBG_BIN, "-conf", conf, "-nogui", "-savedir", savedir,
         "-time-limit", "3600"],
        stdin=slave, stdout=slave, stderr=slave, cwd=out, env=env,
        close_fds=True)
    os.close(slave)
    log(f"spawned dosbox-x-dbg pid={child.pid} display={dspec(DISP)} out={out}")

    rc = 1
    try:
        # ---- MCP connect ---------------------------------------------------
        conn = None
        t0 = _t.time()
        while _t.time() - t0 < 200:
            try:
                conn, addr = ls.accept()
                log(f"MCP connected OUT from {addr} after {_t.time()-t0:.1f}s")
                break
            except socket.timeout:
                if child.poll() is not None:
                    log(f"child exited early rc={child.returncode}")
                    return 2
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
            return W.read_until_end(f, f"END {rid}", budget)

        lines, ok, hdr = req("PING", 10.0)
        if "PONG" not in " ".join(lines):
            log(f"NEGATIVE: no PONG (hdr={hdr})")
            return 1
        log("settling 45 s before the resume click")
        time.sleep(45)

        # ---- EARLY ARM (attempt-3 shape): BREAK at the TITLE screen where
        # survival is t282's 3/3 class; t286 law 1: BPLM SURVIVES campaign
        # load. Target addr deterministic 0x25EAF4 (member 0x25eb7c identical
        # 2/2 independent sessions + production). Boot/load fires are drained
        # and logged, NOT counted as the witness.
        EARLY_LIN = 0x25EAF4
        stopped = False
        for attempt in range(3):
            lines, ok, hdr = req("BREAK", 60.0)
            log(f"TITLE BREAK#{attempt} hdr={hdr} frame_ok={ok}")
            if hdr is not None and not hdr.rstrip().endswith("ERR"):
                stopped = True
                break
            hdr = None
            lines, ok, _ = req("PING", 15.0)
            if "PONG" not in " ".join(lines):
                log(f"TITLE BREAK#{attempt}: channel dead — attempt fails")
                return 1
            time.sleep(10)
        if not stopped:
            log("NEGATIVE: title BREAK never stopped (lottery)")
            return 1
        f0 = os.path.join(out, "byte_at_arm.bin")
        lines, ok, hdr = req(f"EXEC MEMDUMPBIN 0000:{EARLY_LIN:08X} 1 {f0}", 15.0)
        val = None
        if os.path.exists(f0) and os.path.getsize(f0) == 1:
            val = open(f0, "rb").read()[0]
        log(f"EARLY byte at arm = {val} (hdr={hdr})")
        expect_artifact = (val is not None and (val & 0xFF) != 0)
        lines, ok, hdr = req(f"EXEC BPLM {EARLY_LIN:08X}", 15.0)
        log(f"arm BPLM {EARLY_LIN:08X} hdr={hdr} lines={lines}")
        lines, ok, hdr = req("EXEC BPLIST", 10.0)
        armed = [l for l in lines if "BPLM" in l]
        log(f"armed: {armed}")
        if len(armed) != 1:
            log(f"NEGATIVE: expected 1 BPLM, got {armed}")
            return 2
        seen_boot = W.fire_lines(ptylog)
        lines, ok, hdr = req("EXEC RUN", 10.0)
        log(f"EARLY RUN hdr={hdr} — entering campaign WITH bp armed")

        # entry loop with boot-fire drain (t286 early-armed shape)
        a = os.path.join(out, "screen_pre_click.png")
        b = os.path.join(out, "screen_post_click.png")
        W.grab(DISP, a)
        entered = False
        t0 = _t.time()
        last_click = 0.0
        while _t.time() - t0 < 240 and not entered:
            cur = W.fire_lines(ptylog)
            new = [l for l in cur if l not in seen_boot]
            if new:
                seen_boot = cur
                for l in new:
                    le, _, _ = req("EXEC EV eip", 8.0)
                    nums = [x.strip() for x in le if x.strip()]
                    log(f"BOOT/LOAD FIRE eip={nums[-1] if nums else '?'}: {l}")
                    with open(os.path.join(out, "boot-fires.txt"), "a") as bf:
                        bf.write((nums[-1] if nums else "?") + " " + l + "\n")
                lines, ok, hdr = req("EXEC RUN", 10.0)
                if hdr is None:
                    log("NEGATIVE: channel dead after boot fire")
                    return 1
                continue
            if _t.time() - last_click > 20:
                W.xsend(DISP, ["click", str(W.RETURN_TO_GAME[0]),
                               str(W.RETURN_TO_GAME[1])], log)
                last_click = _t.time()
            time.sleep(2.0)
            if W.grab(DISP, b) and W.diff_px(a, b) > 2000:
                entered = True
                shutil.copy2(b, os.path.join(out, "screen_entered_early.png"))
                log("ENTER(early): screen reacted — campaign load presumed")
        if not entered:
            log("NEGATIVE: early-armed entry never showed a screen change")
            return 1
        n0 = drain_popups(DISP, log, maxn=10, outdir=out)
        if n0:
            log(f"post-entry popup drain closed {n0}")
        entered_early = True

        # ---- resolve target from THIS session's ring -----------------------
        global W_ANCH
        pay = open(W.PAYLOAD, "rb").read()
        W_ANCH = SS.build_anchors(pay)
        B = memr = slotp = None
        t0 = _t.time()
        tgt = None
        seen_resolve = seen_boot
        while _t.time() - t0 < 240 and tgt is None:
            # a fire here STOPS the CPU (ring would freeze) — drain + RUN
            curf = W.fire_lines(ptylog)
            newf = [l for l in curf if l not in seen_resolve]
            if newf:
                seen_resolve = curf
                for l in newf:
                    le, _, _ = req("EXEC EV eip", 8.0)
                    nums = [x.strip() for x in le if x.strip()]
                    log(f"LOAD-PHASE FIRE eip={nums[-1] if nums else '?'}: {l}")
                    with open(os.path.join(out, "boot-fires.txt"), "a") as bf:
                        bf.write((nums[-1] if nums else "?") + " " + l + "\n")
                lines, ok, hdr = req("EXEC RUN", 10.0)
                if hdr is None:
                    log("NEGATIVE: channel dead during resolve-drain")
                    return 1
                continue
            B, memr, slotp = latest_ring(savedir)
            if B is not None:
                tgt = find_target(memr, log)
                if tgt is None:
                    time.sleep(10)
            else:
                log("ring slot not yet baseable; waiting")
                time.sleep(10)
        if tgt is None:
            log("NEGATIVE: target never resolved (build state or record law)")
            shutil.copytree(savedir, os.path.join(out, "ring-negative"),
                            dirs_exist_ok=True)
            return 1
        base, arr, member, lin = tgt
        if lin != EARLY_LIN:
            log(f"NOTE: armed 0x{EARLY_LIN:08X} but ring-resolved lin is "
                f"0x{lin:08X} — deterministic-heap assumption BROKEN; the "
                "armed bp watches the wrong byte this attempt")
        if B != 0x1bf4d8:
            log(f"NOTE: base B={B:#x} != 0x1bf4d8 (deterministic-heap base); "
                "target resolved from names, so still valid")

        # ---- RUN + End-Turn click battery (popup-aware, t245 laws) --------
        seen = W.fire_lines(ptylog)
        lines, ok, hdr = req("EXEC RUN", 10.0)
        log(f"RUN hdr={hdr} — clicking NEXTTURN {NEXTTURN} every 10 s, "
            "draining popups between turns")
        tf = open(transcript, "w")
        tf.write(f"t325 shield witness {ts}\ntarget Gridsor I slot{SLOT_IDX} "
                 f"member=0x{member:x} lin=0x{lin:08X} val_at_arm={val}\n")
        fires = []
        t0 = _t.time()
        last_click = 0.0
        no_advance = 0
        last_turn = read_turn(memr, B) if memr is not None else None
        last_ring_check = 0.0
        while _t.time() - t0 < 750:
            cur = W.fire_lines(ptylog)
            new = [l for l in cur if l not in seen]
            if new:
                seen = cur
                for l in new:
                    log(f"FIRE +{_t.time()-t0:.1f}s: {l}")
                le, _, _ = req("EXEC EV eip", 8.0)
                nums = [x.strip() for x in le if x.strip()]
                eip = int(nums[-1], 16) if nums else None
                log(f"fire EIP={eip:#x}" if eip else "fire EIP unread")
                art = bool(W.FIRE_RE.search(new[-1])) and \
                    W.FIRE_RE.search(new[-1]).group(1).upper() == "00"
                if art and expect_artifact:
                    log("baseline-artifact fire — rejecting, RUN again")
                    expect_artifact = False
                    req("EXEC RUN", 10.0)
                    continue
                fires.append((new, eip))
                break
            if _t.time() - last_click > 10:
                W.xsend(DISP, ["click", str(NEXTTURN[0]), str(NEXTTURN[1])], log)
                last_click = _t.time()
            if _t.time() - last_ring_check > 30 and child.poll() is None:
                B2, memr2, _ = latest_ring(savedir)
                if B2 is not None:
                    t2 = read_turn(memr2, B2)
                    if last_turn is not None:
                        if t2 == last_turn:
                            no_advance += 1
                        else:
                            no_advance = 0
                        log(f"ring turn {t2} (no-advance streak {no_advance})")
                        if no_advance >= 2:
                            # t245: popups SERIALIZE input — drain OK-clicks
                            # (Escape does NOT close construction popups)
                            n = drain_popups(DISP, log, maxn=6, outdir=out)
                            log(f"popup drain closed {n}")
                            no_advance = 0
                    last_turn = t2
                last_ring_check = _t.time()
            time.sleep(2.0)

        tf.write("=== fires:\n")
        for fls, feip in fires:
            for l in fls:
                tf.write(f"  eip={feip and hex(feip)} {l}\n")
        tf.flush()

        if not fires:
            log("NEGATIVE: no fire in 900 s click battery (budget banked)")
            W.grab(DISP, os.path.join(out, "screen_after_battery.png"))
            tf.close()
            shutil.copytree(savedir, os.path.join(out, "ring-final"),
                            dirs_exist_ok=True)
            return 1

        # ---- witness banked: registers, code, stack -------------------------
        phase, real = fires[0]
        regs = {}
        for r_ in ["eip", "cs", "ds", "esp", "eax", "ebx", "ecx", "edx",
                   "esi", "edi", "ebp", "flags"]:
            lines, ok, hdr = req(f"EXEC EV {r_}", 10.0)
            nums = [l.strip() for l in lines if l.strip()]
            regs[r_] = nums[-1] if nums else "?"
        log("regs: " + " ".join(f"{k}={v}" for k, v in regs.items()))
        eip = fires[0][1]
        esp = None
        try:
            esp = int(regs["esp"], 16)
        except Exception:
            pass
        bank = W.dump_stopped(req, out, B, log, eip=eip, esp=esp)
        tf.write(f"=== stopped state banked to {bank}\n")

        # ---- post-fire recovery: clear bp, resume, 2 more turns, bank ring -
        lines, ok, hdr = req("EXEC BPDEL *", 10.0)
        log(f"BPDEL * hdr={hdr}")
        lines, ok, hdr = req("EXEC RUN", 10.0)
        log(f"post-fire RUN hdr={hdr}")
        time.sleep(5)
        for i in range(3):
            W.xsend(DISP, ["click", str(NEXTTURN[0]), str(NEXTTURN[1])], log)
            time.sleep(15)
        t0 = _t.time()
        postB = post_mem = None
        while _t.time() - t0 < 120:
            postB, post_mem, _ = latest_ring(savedir)
            if post_mem is not None and read_turn(post_mem, postB) >= (last_turn or 0):
                break
            time.sleep(10)
        if post_mem is not None:
            pt = read_turn(post_mem, postB)
            msg = f"post ring turn {pt} base {postB:#x}"
            s = arr + 4 * SLOT_IDX
            if postB == B:
                msg += (f" | post slot{SLOT_IDX} raw={post_mem[s:s+4].hex()}"
                        f" byte3={post_mem[s+3]}"
                        f" pending item={post_mem[base+0x54]}"
                        f" acc={struct.unpack_from('<H', post_mem, base+0x50)[0]}")
            tf.write("=== " + msg + "\n")
            log(msg)
        tf.close()
        shutil.copytree(savedir, os.path.join(out, "ring-final"),
                        dirs_exist_ok=True)
        rc = 0
    finally:
        W.kill_rec(child.pid, "dosbox-x-dbg")
        W.kill_rec(xv.pid, "Xvfb")
        ls.close()
        try:
            os.close(master)
        except OSError:
            pass
    log(f"DONE rc={rc} out={out} ({_t.time()-t_start:.0f}s)")
    return rc


if __name__ == "__main__":
    sys.exit(main())
