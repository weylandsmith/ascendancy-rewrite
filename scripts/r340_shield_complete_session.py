#!/usr/bin/env python3
"""r340_shield_complete_session.py — t340 OQ-016 residue-(4) FINAL witness.

ONE launch (t325's own stated budget). Question: at the shield build-
completion turn (Gridsor I pending item 26, acc=30 IND=6 @ turn 1086 =>
completion ~turn 1091), does ANY observable dword move per turn in the item
slot / build-queue struct? Watch the WHOLE slot dword + the build-queue acc,
NOT byte+3 (t325 census law: byte+3==0 on all 44 pending rows, constant 15 on
43 completed rows).

Chain = scripts/r325_shield_session.py FIXED version verbatim (early-arm-at-
title BPLM 0x25EAF4 survives load, deterministic heap member 0x25eb7c, popup
drain ppm-P6 + root->window-rel (80,100) — re-verified offline this session:
detector returns (406,442) on the real t325 stall popup drain_0.png). NEW vs
t325: (a) ring sample every 15 s -> turns.jsonl {turn, acc, pending item, cap,
slot76 raw, ALL cap slot dwords}; (b) battery runs to turn >= 1093, NOT to a
fire — a BPLM fire is banked (regs/EIP/dump_stopped) then BPDEL * + RUN and
the battery CONTINUES (fire = the completion write witness, ring-diff = the
per-turn law).

Laws honoured: own ring dir (two-writer), kill-by-recorded-PID SIGKILL, xsend
arg1 = window title, core=normal, scratch only, production :9 NEVER touched.
Exit: 0 = completion turn witnessed (slot dword changed or pending moved),
1 = negative (absence-only third time), 2 = harness error.
"""
import json
import os
import shutil
import socket
import struct
import subprocess
import sys
import threading
import time
import time as _t

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import r1_wp_session as W            # noqa: E402
import r1_income_law as IL           # noqa: E402
import r1_sav_scan as SS             # noqa: E402
import r325_shield_session as T325   # noqa: E402  (FIXED helpers, verbatim)

TARGET_PLANET = T325.TARGET_PLANET
PENDING_ITEM = T325.PENDING_ITEM
SLOT_IDX = T325.SLOT_IDX
RESERVED = T325.RESERVED
NEXTTURN = W.NEXTTURN
EARLY_LIN = 0x25EAF4
DISP = "97"
PORT = 55997
BATTERY_S = 2400
DEADLINE_TURN = 1093


def dspec(d):
    return d if d.startswith(":") else f":{d}"


W_ANCH = None


def sample_ring(savedir):
    """-> dict or None. Re-resolves Gridsor I per sample (heap-move-safe)."""
    B, mem, p = T325.latest_ring(savedir)
    if mem is None:
        return None
    for base, cells, cap, arr in IL.find_records(mem):
        name = mem[base + 0x24:base + 0x33].split(b"\x00")[0]
        if name != TARGET_PLANET:
            continue
        dwords = [struct.unpack_from("<I", mem, arr + 4 * i)[0]
                  for i in range(cap)]
        return {
            "wall": time.strftime("%H:%M:%S"),
            "ring": os.path.basename(p),
            "B": B,
            "turn": T325.read_turn(mem, B),
            "acc": struct.unpack_from("<H", mem, base + 0x50)[0],
            "item": mem[base + 0x54],
            "cap": cap,
            "slot76": dwords[SLOT_IDX] if SLOT_IDX < cap else None,
            "dwords": dwords,
        }
    return None


def analyse(path, log):
    """Per-turn diffs: movers of slot76 / any slot / acc between turns."""
    rows = [json.loads(l) for l in open(path) if l.strip()]
    if not rows:
        log("ANALYSE: no samples")
        return False
    by_turn = {}
    for r in rows:
        by_turn.setdefault(r["turn"], r)  # first sample of each turn
    turns = sorted(by_turn)
    log(f"ANALYSE: {len(rows)} samples, turns {turns[0]}..{turns[-1]}")
    completion = None
    for r in rows:
        if r["item"] != PENDING_ITEM or (r["slot76"] not in
                                         (0x00001A01, None)):
            completion = r
            break
    movers_total = {}
    prev = None
    for tn in turns:
        r = by_turn[tn]
        if prev is not None:
            dm = []
            if r["acc"] != prev["acc"]:
                dm.append(f"acc {prev['acc']}->{r['acc']}")
            if r["item"] != prev["item"]:
                dm.append(f"item {prev['item']}->{r['item']}")
            if r["slot76"] != prev["slot76"]:
                dm.append(f"slot76 "
                          f"{prev['slot76'] and hex(prev['slot76'])}->"
                          f"{r['slot76'] and hex(r['slot76'])}")
            if len(r["dwords"]) == len(prev["dwords"]):
                for i, (a, b_) in enumerate(zip(prev["dwords"], r["dwords"])):
                    if a != b_:
                        movers_total[i] = movers_total.get(i, 0) + 1
                        if i != SLOT_IDX:
                            dm.append(f"slot{i} {hex(a)}->{hex(b_)}")
            log(f"turn {prev['turn']}->{tn}: " + ("; ".join(dm) or "NO MOVER"))
        prev = r
    log(f"ANALYSE: any-mover slot histogram (all 83 slots): {movers_total}")
    if completion:
        log(f"COMPLETION WITNESSED at turn {completion['turn']} "
            f"(wall {completion['wall']}, acc={completion['acc']}, "
            f"item={completion['item']}, slot76="
            f"{hex(completion['slot76']) if completion['slot76'] is not None else '?'})")
        return True
    log("ANALYSE: no completion observed in sampled turns — honest negative")
    return False


def main():
    t_start = _t.time()
    ts = time.strftime("%Y%m%d-%H%M%S")
    out = os.path.join(ROOT, "work/r1", f"t340-shieldc-{ts}")
    os.makedirs(out, exist_ok=True)
    savedir = os.path.join(out, "save")
    os.makedirs(savedir, exist_ok=True)
    runlog = os.path.join(out, "session.log")
    ptylog = os.path.join(out, "mcp-pty.log")
    samples_path = os.path.join(out, "turns.jsonl")

    def log(msg):
        line = f"{time.strftime('%H:%M:%S')} {msg}"
        print(line, flush=True)
        with open(runlog, "a") as fh:
            fh.write(line + "\n")

    # ---- preflight (t325 verbatim) ------------------------------------------
    for pth, why in [(W.DBG_BIN, "debugger binary"), (W.SCRATCH, "scratch"),
                     (W.PAYLOAD, "payload"), (W.OCT29, "oct29 state"),
                     (W.XSEND, "xsend")]:
        if not os.path.exists(pth):
            log(f"HARNESS ERROR: missing {why} {pth}")
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
        os.rename(low, low + ".vendor-t340")

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
    witnessed = False
    try:
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

        # ---- EARLY ARM at title (t325 attempt-3 shape, verbatim) -----------
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

        # entry loop with boot-fire drain (t325 verbatim)
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
        n0 = T325.drain_popups(DISP, log, maxn=10, outdir=out)
        if n0:
            log(f"post-entry popup drain closed {n0}")

        # ---- resolve target from THIS session's ring (t325 verbatim) -------
        # W_ANCH must live in r325's namespace: latest_ring() reads IT, not
        # ours (t340 launch-1 NameError — harness bug, fixed).
        pay = open(W.PAYLOAD, "rb").read()
        T325.W_ANCH = SS.build_anchors(pay)
        t0 = _t.time()
        tgt = None
        seen_resolve = seen_boot
        while _t.time() - t0 < 240 and tgt is None:
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
            B, memr, slotp = T325.latest_ring(savedir)
            if B is not None:
                tgt = T325.find_target(memr, log)
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

        # ---- battery: NEXTTURN clicks + 15 s ring samples to t>=1093 -------
        seen = W.fire_lines(ptylog)
        lines, ok, hdr = req("EXEC RUN", 10.0)
        log(f"RUN hdr={hdr} — clicking NEXTTURN {NEXTTURN} every 10 s, "
            f"sampling ring every 15 s, running to turn >= {DEADLINE_TURN}")
        fires = []
        t0 = _t.time()
        last_click = 0.0
        last_sample = 0.0
        no_advance = 0
        last_turn = T325.read_turn(memr, B) if memr is not None else None
        last_fire_bank = {}
        while _t.time() - t0 < BATTERY_S:
            cur = W.fire_lines(ptylog)
            new = [l for l in cur if l not in seen]
            if new:
                seen = cur
                for l in new:
                    log(f"FIRE +{_t.time()-t0:.1f}s: {l}")
                le, _, _ = req("EXEC EV eip", 8.0)
                nums = [x.strip() for x in le if x.strip()]
                eip = int(nums[-1], 16) if nums else None
                log(f"fire EIP={hex(eip)}" if eip else "fire EIP unread")
                art = bool(W.FIRE_RE.search(new[-1])) and \
                    W.FIRE_RE.search(new[-1]).group(1).upper() == "00"
                if art and expect_artifact:
                    log("baseline-artifact fire — rejecting, RUN again")
                    expect_artifact = False
                    req("EXEC RUN", 10.0)
                    continue
                fires.append((new, eip))
                # bank stopped state ONCE per eip, then clear bp + RUN and
                # CONTINUE the battery (t340 law: fire != end of session)
                if eip not in last_fire_bank:
                    regs = {}
                    for r_ in ["eip", "cs", "ds", "esp", "eax", "ebx", "ecx",
                               "edx", "esi", "edi", "ebp"]:
                        lines, ok, hdr = req(f"EXEC EV {r_}", 10.0)
                        nums2 = [l.strip() for l in lines if l.strip()]
                        regs[r_] = nums2[-1] if nums2 else "?"
                    log("fire regs: " + " ".join(f"{k}={v}"
                                                 for k, v in regs.items()))
                    esp = None
                    try:
                        esp = int(regs["esp"], 16)
                    except Exception:
                        pass
                    bank = W.dump_stopped(req, out, B, log, eip=eip, esp=esp)
                    last_fire_bank[eip] = bank
                lines, ok, hdr = req("EXEC BPDEL *", 10.0)
                log(f"BPDEL * hdr={hdr}")
                lines, ok, hdr = req("EXEC RUN", 10.0)
                log(f"post-fire RUN hdr={hdr}")
                continue
            if _t.time() - last_click > 10:
                W.xsend(DISP, ["click", str(NEXTTURN[0]), str(NEXTTURN[1])],
                        log)
                last_click = _t.time()
            if _t.time() - last_sample > 15:
                last_sample = _t.time()
                if child.poll() is None:
                    try:
                        s = sample_ring(savedir)
                    except Exception as e:
                        log(f"SAMPLE error: {e}")
                        s = None
                    if s is not None:
                        with open(samples_path, "a") as sf:
                            sf.write(json.dumps(s) + "\n")
                        t2 = s["turn"]
                        if last_turn is not None:
                            if t2 == last_turn:
                                no_advance += 1
                            else:
                                no_advance = 0
                            log(f"ring turn {t2} acc={s['acc']} "
                                f"item={s['item']} slot76="
                                f"{hex(s['slot76'])} (streak {no_advance})")
                            if no_advance >= 2:
                                n = T325.drain_popups(DISP, log, maxn=6,
                                                      outdir=out)
                                log(f"popup drain closed {n}")
                                no_advance = 0
                        last_turn = t2
                        if t2 >= DEADLINE_TURN:
                            log(f"DEADLINE reached: turn {t2} >= "
                                f"{DEADLINE_TURN}")
                            break
            time.sleep(2.0)

        W.grab(DISP, os.path.join(out, "screen_after_battery.png"))
        with open(os.path.join(out, "fires.txt"), "w") as ff:
            for fls, feip in fires:
                ff.write(f"eip={feip and hex(feip)}\n")
                for l in fls:
                    ff.write("  " + l + "\n")
        log(f"battery done: {len(fires)} real fire(s) "
            f"{[hex(e) for _, e in fires]}")
        witnessed = analyse(samples_path, log)
        shutil.copytree(savedir, os.path.join(out, "ring-final"),
                        dirs_exist_ok=True)
        rc = 0 if witnessed else 1
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
