#!/usr/bin/env python3
"""t297 — LIVE MOVE-ORDER WITNESS via the t296/t297 choreography (OQ-019 r1/r3).

GOAL: issue ONE player ship move order in a scratch session and witness it in
the ring: watched ship kind [+0x58] 4 -> 2 (t293 witness law) and/or a changed
byte-run in guest RAM at the batwin/ds globals, then End Turn x2 and confirm
THAT ship moved (fuel/moves deltas attributable to the issued slot).

WITNESS INSTRUMENTS (all pointer-law / ring, no debugger):
  W1 owner-0 ship kind census; kind 2 == issued move order (baseline {3,4,5}).
  W2 FULL-RAM DIFF between consecutive autosaves: every changed byte-run with
     offset relative to the payload base B and relative to B+0x43504. This
     locates [batwin+0xb7]/[win+0xaf] (window-object RAM), ds:0x43504 and
     ds:0x43508 EMPIRICALLY — the t296 S6.2 camera/global gap closed by
     measurement instead of inference.
  W3 u32 scan for pointers into the ship-record array (identifies the
     selection-global offset if plain B+0x43504 is not it).

CHOREOGRAPHY (docs/re/_wip_t297.md T297-S1, disasm 0x1b070/0x1b91c verbatim):
  title -> (318,333) Return to Current Game -> FLEET (553,184) -> row click
  (200,93) jumps to THAT ship's system (t253). Inside system view:
    A1 click SHIP CLUSTER centroid (select; G1..G4: kind-4 clip, kind2, owner,
       MOVES>0 — the target ship is PICKED FROM THE RING to satisfy gates).
    A2 left-click another object cluster (planet clip: pending kind 3 ->
       relay 0x326 leg @0x1bad3).
    A3 right-click empty black space (pending kind 1 -> 0x1ba45 legs; at mode
       0 the 0x1ba8c leg publishes ds:0x43508 + command ring code 0x11).
    A4 left-click empty (same leg, Button1).
    A5 right-click the ship cluster (t244 order-mode green marker).
    A6 double left-click empty.
  After EVERY click: W1+W2+W3. If kind 2 appears or the batwin run changes ->
  STOP battery, escape to map, End Turn x2 + popup drain, verdict on the
  watched slot. DO NOT plain-click star dots expecting SELECTION (REFUTED t296
  — dots are kind-3 clips); clicks here target clips AS DESTINATIONS after a
  verified selection, which is a different leg.

SAFETY (docs/BLOCKED.md runbook, binding): scratch copy work/r1/game-wp ONLY
(asserted, never game/); OWN ring dir + private Xvfb (production :9 untouched);
output=x11 (vblank autosave law); nosound; -time-limit; kill-by-recorded-PID in
finally (NEVER pkill); assert_on_map BEFORE every click (t285 orange-frac law);
NEVER Escape at the bare map; popup drain only off-map/after presses; big screen
diff after a clip click -> ONE Escape with title guard.

usage: r297_order_session.py [--disp 97] [--tl 1500] [--settle 45] [--boot 170]
Exit 0 = order ISSUED and flight WITNESSED on the watched slot.
     1 = honest negative (battery exhausted / no attributable movement).
     2 = harness error.
"""
import argparse
import glob
import json
import os
import os.path as op
import struct
import sys
import time
import zipfile

ROOT = op.abspath(op.join(op.dirname(__file__), ".."))
sys.path.insert(0, op.dirname(op.abspath(__file__)))
import r1_slot as SL                                    # noqa: E402
import r293_move_session as R293                        # noqa: E402


class Sess(R293.Session):
    """r293 drive class + full-RAM diff witness + cluster finding."""

    def __init__(self, args):
        super().__init__(args)
        # re-aim evidence dir
        self.out = op.join(ROOT, "work/r1",
                           f"t297-order-{time.strftime('%Y%m%d-%H%M%S')}")
        os.makedirs(op.join(self.out, "save"), exist_ok=True)
        self.savedir = op.join(self.out, "save")
        self.logp = op.join(self.out, "session.log")
        self.dbl = op.join(self.out, "dosbox.out")
        self.evidence = []          # per-click witness records

    # ---------- RAM witness ----------
    def newest_sav(self):
        rows = self.ring_mem_rows()
        return rows[-1]["path"] if rows else None

    def read_mem(self, path):
        try:
            return zipfile.ZipFile(path).read("Memory")
        except Exception:
            return None

    def ram_diff(self, mem_a, mem_b):
        """Changed byte-runs [(start, hexa, hexb)]. XOR fast-path: int XOR +
        to_bytes locates changed positions ~10x faster than a byte loop."""
        runs = []
        if mem_a is None or mem_b is None or len(mem_a) != len(mem_b):
            return runs
        n = len(mem_a)
        x = (int.from_bytes(mem_a, "big") ^ int.from_bytes(mem_b, "big"))
        if x == 0:
            return runs
        xb = x.to_bytes(n, "big")
        changed = [i for i, by in enumerate(xb) if by]
        # group into runs with <=12B gaps, cap 96B width
        i = 0
        ci = 0
        while ci < len(changed):
            start = changed[ci]
            end = start + 1
            while ci + 1 < len(changed) and \
                    changed[ci + 1] - end <= 12 and end - start < 96:
                ci += 1
                end = changed[ci] + 1
            runs.append((start, mem_a[start:end].hex(), mem_b[start:end].hex()))
            ci += 1
        return runs

    def ship_state(self, mem, B):
        base, n = SL.ship_array_law(mem, B)
        out = {}
        for k in range(n):
            r = base + k * SL.SHIP["stride"]
            if r + SL.SHIP["stride"] > len(mem):
                break
            out[k] = dict(
                owner=struct.unpack_from("<I", mem, r + 0x54)[0] >> 16,
                kind=mem[r + 0x58],
                tgt=mem[r + 0x59],
                xyz=struct.unpack_from("<3f", mem, r + 0x9e),
                fuel=struct.unpack_from("<H", mem, r + 0x88)[0],
                moves=struct.unpack_from("<H", mem, r + 0x94)[0],
                addr=r)
        return out

    def ptr_scan(self, mem, B, recs):
        """u32 scan: addresses whose value equals a ship-record address."""
        addrs = {v["addr"]: k for k, v in recs.items()}
        hits = []
        for p in range(0, len(mem) - 4, 4):
            v = struct.unpack_from("<I", mem, p)[0]
            if v in addrs:
                hits.append((p, addrs[v]))
            if len(hits) >= 12:
                break
        return hits

    def witness(self, tag, mem_before, B, base_mem):
        """Read newest autosave; compare vs baseline; log + bank a record."""
        rec = {"tag": tag}
        p = self.newest_sav()
        mem = self.read_mem(p) if p else None
        if mem is None or B is None:
            rec["error"] = "no mem"
            self.evidence.append(rec)
            self.log(f"WITNESS {tag}: no memory yet")
            return rec, mem_before
        b2 = SL.base_of(mem, self.anch) or B
        st = self.ship_state(mem, b2)
        kind2 = sorted(k for k, v in st.items()
                       if v["owner"] == 0 and v["kind"] == 2)
        rec["turn"] = struct.unpack_from("<I", mem, b2 + SL.OFF + 0x12e10)[0]
        rec["kind2_owner0"] = kind2
        # t297-A: DAT globals live at B + SL.OFF + X (data-segment base), NOT
        # B + X; and they have non-order writers, so they are DELTA-only
        # witnesses (baseline captured at pre_click).
        rec["sel43504"] = struct.unpack_from("<I", mem,
                                             b2 + SL.OFF + 0x43504)[0]
        rec["dst43508"] = struct.unpack_from("<I", mem,
                                             b2 + SL.OFF + 0x43508)[0]
        runs = self.ram_diff(base_mem, mem)
        rec["n_runs"] = len(runs)
        rec["runs"] = [(hex(a), x[:32], y[:32]) for a, x, y in runs[:25]]
        if kind2:
            rec["ptr_hits"] = self.ptr_scan(mem, b2, st)
        self.evidence.append(rec)
        self.log(f"WITNESS {tag}: file={op.basename(str(p))} t={rec['turn']} "
                 f"kind2={kind2} sel43504={rec['sel43504']:#x} "
                 f"dst43508={rec['dst43508']:#x} runs={len(runs)}")
        for a, x, y in rec["runs"][:12]:
            self.log(f"   run @{a} : {x} -> {y}")
        return rec, mem

    # ---------- screen clusters ----------
    def clusters(self, im, thr=380, min_px=8):
        """Connected bright components in the system-view black field
        (ship/planet sprites). 8-neighbour flood on a 2px grid. Returns
        [(cx, cy, size)] sorted by size desc, map region only."""
        px = im.load()
        W, H = im.size
        gx, gy = W // 2, H // 2
        bright = [[False] * gx for _ in range(gy)]
        for y in range(gy):
            for x in range(gx):
                r, g, b = px[2 * x, 2 * y]
                if r + g + b > thr:
                    bright[y][x] = True
        seen = [[False] * gx for _ in range(gy)]
        out = []
        for y in range(gy):
            for x in range(gx):
                if not bright[y][x] or seen[y][x]:
                    continue
                stack = [(x, y)]
                comp = []
                seen[y][x] = True
                while stack and len(comp) < 400:
                    cx0, cy0 = stack.pop()
                    comp.append((cx0, cy0))
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            nx, ny = cx0 + dx, cy0 + dy
                            if 0 <= nx < gx and 0 <= ny < gy and \
                               bright[ny][nx] and not seen[ny][nx]:
                                seen[ny][nx] = True
                                stack.append((nx, ny))
                if len(comp) < min_px:
                    continue
                mx = min(c[0] for c in comp)
                Mx = max(c[0] for c in comp)
                my = min(c[1] for c in comp)
                My = max(c[1] for c in comp)
                # background star specks: tiny bbox; sprites: >=4 grid px span
                if (Mx - mx) + (My - my) < 4:
                    continue
                cx = int(sum(c[0] for c in comp) / len(comp)) * 2
                cy = int(sum(c[1] for c in comp) / len(comp)) * 2
                if not (40 < cx < 460 and 55 < cy < 445):
                    continue
                out.append((cx, cy, len(comp)))
        out.sort(key=lambda t: -t[2])
        return out

    def is_black_at(self, im, x, y, rad=6, frac=0.85):
        px = im.load()
        tot = dark = 0
        for yy in range(max(0, y - rad), min(im.height, y + rad)):
            for xx in range(max(0, x - rad), min(im.width, x + rad)):
                tot += 1
                if sum(px[xx, yy]) < 200:
                    dark += 1
        return tot and dark / tot >= frac

    def empty_point(self, im, clists):
        """A black-space point away from every cluster — a raw-map click."""
        for cand in ((236, 200), (140, 200), (300, 150), (400, 420),
                     (120, 300), (350, 250), (250, 380), (180, 120)):
            if all(abs(cand[0] - cx) > 40 or abs(cand[1] - cy) > 40
                   for cx, cy, _s in clists) and self.is_black_at(im, *cand):
                return cand
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--disp", default="97")
    ap.add_argument("--tl", type=int, default=1500)
    ap.add_argument("--settle", type=int, default=45)
    ap.add_argument("--boot", type=int, default=170)
    args = ap.parse_args()

    for p, why in [(R293.SCRATCH, "scratch copy"), (R293.PAYLOAD, "payload"),
                   (R293.OCT29, "Oct-29 campaign backup"),
                   (R293.DOSBOX, "dosbox-x")]:
        if not os.path.exists(p):
            print(f"HARNESS ERROR: missing {why} {p}")
            return 2
    if os.path.abspath(R293.SCRATCH).startswith(
            op.join(ROOT, "game") + op.sep):
        print("HARNESS ERROR: refusing to mount game/")
        return 2
    import hashlib
    if hashlib.md5(open(R293.OCT29, "rb").read()).hexdigest() != R293.OCT29_MD5:
        print("HARNESS ERROR: Oct-29 backup md5 mismatch")
        return 2

    s = Sess(args)
    s.log(f"t297 order-witness session start out={s.out}")
    s.launch()
    rc = 1
    try:
        if not s.wait_title():
            s.log("NEGATIVE: title never appeared")
            return 1
        if not s.enter_campaign():
            s.log("NEGATIVE: campaign entry failed")
            return 1
        time.sleep(s.a.settle)
        closed = s.drain_popups()
        s.log(f"post-load popup drain closed {closed}")

        rows0 = s.sample("loaded")
        if not rows0 or not rows0[-1].get("recs"):
            s.log("NEGATIVE: ring has no ship records")
            return 1
        recs0 = rows0[-1]["recs"]
        # PICK TARGET: owner-0 kind-4 ship with MOVES>0 (G1+G4 gates cited by
        # t296; a ship failing them can NEVER be selected).
        # t297 BUGFIX: rows0[-1]["recs"] is the FULL census (all owners) —
        # the candidate filter MUST test owner==0 (G3), which run #1 missed
        # and thereby targeted an owner-1 ship (selection impossible by law).
        cand = [k for k, v in recs0.items()
                if v["owner"] == 0 and v["kind"] == 4 and v["moves"] > 0]
        s.log(f"owner-0 ships={len(recs0)} kind4_moves>0={cand} "
              f"kinds={sorted(set(v['kind'] for v in recs0.values()))}")
        if not cand:
            cand = [k for k, v in recs0.items()
                    if v["owner"] == 0 and v["moves"] > 0]
            s.log(f"NO kind-4 candidate; fallback moves>0: {cand}")
        if not cand:
            s.log("NEGATIVE: no owner-0 ship with MOVES>0 (G4 hard gate)")
            return 1
        target = sorted(cand, key=int)[0]

        map_im = s.grab("map")
        sys_im = s.enter_system_via_fleet(map_im)
        if sys_im is None:
            s.log("NEGATIVE: fleet row-jump route failed to open a system")
            return 1
        s.log(f"in system view; target ship slot {target}")

        # baseline RAM for diffs
        p0 = s.newest_sav()
        mem0 = s.read_mem(p0)
        B = SL.base_of(mem0, s.anch) if mem0 else None
        if B is None:
            s.log("NEGATIVE: no payload base vote in baseline autosave")
            return 1
        st0 = s.ship_state(mem0, B)
        s.log(f"baseline {op.basename(p0)} B={B:#x} target state={st0.get(int(target))}")
        base_mtime = os.path.getmtime(p0)
        rec, _ = s.witness("pre_click", mem0, B, mem0)
        base_globals = {"sel43504": rec.get("sel43504"),
                        "dst43508": rec.get("dst43508")}
        s.log(f"baseline globals (t297-A correct address): "
              f"sel43504={base_globals['sel43504']:#x} "
              f"dst43508={base_globals['dst43508']:#x}")

        clists = s.clusters(sys_im)
        s.log(f"clusters(system_view)={clists}")

        def fresh_sav(after_mtime):
            """Wait for an autosave NEWER (by mtime) than after_mtime — the
            ring ROTATES filenames 41..60 so path equality means nothing."""
            t0 = time.time()
            while time.time() - t0 < 18:
                p = s.newest_sav()
                if p and os.path.getmtime(p) > after_mtime + 0.5:
                    return p
                time.sleep(2)
            return s.newest_sav()

        def click_step(name, kind, pt):
            """one click + wait for fresh autosave + witness (diff vs the
            session-start baseline mem0). Returns (rec, navigated)."""
            nonlocal base_mtime
            if not s.assert_on_map(name):
                return None, True
            s.send([kind, str(pt[0]), str(pt[1])])
            time.sleep(1.5)
            im = s.grab(name)
            navigated = im is not None and s.diff_px(sys_im, im) > 40000
            p_new = fresh_sav(base_mtime)
            mem_new = s.read_mem(p_new)
            if mem_new is not None:
                base_mtime = os.path.getmtime(p_new)
            rec, _m = s.witness(name, mem0, B, mem0)
            rec["navigated"] = navigated
            return rec, navigated

        issued = None
        # ---- battery ----
        if clists:
            ship_pt = clists[0]
            rec, nav = click_step("A1_select_ship", "click",
                                  (ship_pt[0], ship_pt[1]))
            if rec is None:
                return 1
            if nav:
                s.send(["key", "Escape"])
                time.sleep(2)
                chk = s.grab("A1_back")
                if chk is not None and s.orange_frac(chk) > 0.20:
                    s.log("NEGATIVE: Escape from system view hit TITLE")
                    return 1
                sys_im = chk if chk is not None else sys_im
        else:
            s.log("NO clusters found in system view — battery on empty pts")

        def check_issue(rec):
            # t297-A: DELTA vs the pre-click baseline, not absolute nonzero —
            # both DAT globals are non-zero (and ds:0x43508 churns) at idle.
            if not rec:
                return False
            if rec.get("kind2_owner0"):
                return True
            return (rec.get("dst43508") != base_globals["dst43508"]
                    and rec.get("dst43508", 0) != 0)

        order_pt = None
        # A2: left-click other object clusters (planet destination legs)
        for i, (cx, cy, sz) in enumerate(clists[1:4]):
            rec, nav = click_step(f"A2_dest_{i}", "click", (cx, cy))
            if rec is None:
                return 1
            if nav:
                s.send(["key", "Escape"])
                time.sleep(2)
                chk = s.grab(f"A2_back_{i}")
                if chk is not None and s.orange_frac(chk) > 0.20:
                    s.log("NEGATIVE: Escape hit TITLE")
                    return 1
                sys_im = chk if chk is not None else sys_im
            if check_issue(rec):
                issued = dict(how="A2 left-click object cluster",
                              click=[cx, cy])
                order_pt = (cx, cy)
                break

        # A3/A4: empty-space clicks (right then left) — the 0x1ba45/0x1ba8c
        # publish legs; destination = raw point.
        emp = s.empty_point(s.grab("emp_probe"), clists)
        s.log(f"empty point={emp}")
        if emp and not issued:
            for nm, kd in (("A3_empty_right", "click3"),
                           ("A4_empty_left", "click")):
                rec, nav = click_step(nm, kd, emp)
                if rec is None:
                    return 1
                if check_issue(rec):
                    issued = dict(how=f"{nm} (0x1ba45/0x1ba8c leg)",
                                  click=list(emp))
                    order_pt = emp
                    break

        # A5: right-click on the ship cluster itself (t244 green marker)
        if clists and not issued:
            rec, nav = click_step("A5_ship_right", "click3",
                                  (clists[0][0], clists[0][1]))
            if rec is None:
                return 1
            im = s.grab("A5_green")
            g = s.green_count(im) if im else -1
            s.log(f"A5 green={g}")
            if nav:
                s.send(["key", "Escape"])
                time.sleep(2)
                chk = s.grab("A5_back")
                if chk is not None and s.orange_frac(chk) > 0.20:
                    s.log("NEGATIVE: Escape hit TITLE")
                    return 1
                sys_im = chk if chk is not None else sys_im

        # A6: two-step ARM: right-click empty (arms, mode 1 per t244), then
        # left-click the same point.
        if emp and not issued:
            if not s.assert_on_map("A6a"):
                return 1
            s.send(["click3", str(emp[0]), str(emp[1])])
            time.sleep(2)
            s.grab("A6a_arm")
            if not s.assert_on_map("A6b"):
                return 1
            s.send(["click", str(emp[0]), str(emp[1])])
            time.sleep(1.5)
            s.grab("A6b_confirm")
            fresh_sav(base_mtime)
            rec, _ = s.witness("A6_arm_confirm", mem0, B, mem0)
            if check_issue(rec):
                issued = dict(how="A6 right-then-left empty (arm+confirm)",
                              click=list(emp))
                order_pt = emp

        s.log("BATTERY DONE issued=" + json.dumps(issued))

        # If nothing issued but kind2 appeared, still proceed to End Turn —
        # kind 2 alone is the order witness class (t293 law).
        proceed = issued is not None or any(
            (e.get("kind2_owner0") for e in s.evidence))
        if not proceed:
            s.log("NEGATIVE: battery exhausted, no order issued and no kind-2 "
                  "witness (honest negative; evidence dir above)")
            return 1

        # escape to bare map (verified ladder), End Turn x2 + drain
        if not s.escape_to_map(map_im):
            s.sample("not_on_map")
            s.log("NEGATIVE: could not get back to the bare map")
            return 1
        pre = s.sample("pre_turn")
        turn0 = max((d["turn"] for d in pre), default=0)
        turn_base = turn0
        presses = 0
        noadv = 0
        deadline = time.time() + 330
        rows = pre
        while time.time() < deadline and presses < 3:
            if not s.assert_on_map("end_turn"):
                break
            s.send(["click", str(R293.NEXTTURN[0]), str(R293.NEXTTURN[1])])
            presses += 1
            t0 = time.time()
            advanced = False
            while time.time() - t0 < 90:
                time.sleep(5)
                rows = s.ring_mem_rows()
                if rows and max(d["turn"] for d in rows) > turn0:
                    advanced = True
                    break
            s.log(f"press {presses}: advanced={advanced} "
                  f"turn_now={max((d['turn'] for d in rows), default=-1)}")
            if advanced:
                noadv = 0
                turn0 = max(d["turn"] for d in rows)
                s.sample(f"turn{turn0}")
                s.grab(f"map_after_t{turn0}")
                closed = s.drain_popups()
                if closed:
                    s.log(f"post-turn drain closed {closed}")
                if turn0 >= turn_base + 2:
                    break
            else:
                im = s.grab("noadv_check")
                if im is not None and s.eventwin_open(im):
                    if s.close_eventwin():
                        noadv = 0
                        continue
                noadv += 1
                if noadv >= 2:
                    s.log("STOP-AND-LOOK: 2 no-advance presses")
                    s.drain_popups()
                    break

        post = s.sample("final")
        # verdict: watched slot moved with order evidence
        moved = []
        if pre and post:
            pmap = pre[-1].get("recs") or {}
            for d in sorted(post, key=lambda x: x["turn"]):
                if d["turn"] <= pre[-1]["turn"]:
                    continue
                for k, v in (d.get("recs") or {}).items():
                    pv = pmap.get(k)
                    if not pv or v["xyz"] == pv["xyz"]:
                        continue
                    ev = (v["kind"] != pv["kind"] or v["moves"] != pv["moves"]
                          or v["fuel"] != pv["fuel"])
                    moved.append(dict(file=d["file"], turn=d["turn"],
                                      slot=int(k),
                                      pre=[list(pv["xyz"]), pv["kind"],
                                           pv["moves"], pv["fuel"]],
                                      post=[list(v["xyz"]), v["kind"],
                                            v["moves"], v["fuel"]],
                                      evidence=ev))
        kind2_post = sorted({int(k) for k in (post[-1].get("recs") or {})
                             if (post[-1]["recs"][k]["kind"] == 2
                                 and post[-1]["recs"][k]["owner"] == 0)})
        # the fleet row-jump lands on the FIRST-LISTED ship, which may not be
        # the ring-picked target; the ORDERED slot is whichever ship reached
        # kind 2 during the session (t293 witness law), plus the target.
        ordered_slots = set(kind2_post) | {int(target)}
        for e in s.evidence:
            ordered_slots |= {int(k) for k in (e.get("kind2_owner0") or [])}
        tgt_moved = [m for m in moved if m["slot"] in ordered_slots]
        s.log("VERDICT issued=" + json.dumps(issued) +
              f" target={target} tgt_moved={len(tgt_moved)} "
              f"kind2_post={kind2_post} moved_n={len(moved)}")
        with open(op.join(s.out, "verdict.json"), "w") as f:
            json.dump(dict(issued=issued, target=int(target),
                           evidence=s.evidence, moved=moved[:20],
                           tgt_moved=tgt_moved, kind2_post=kind2_post), f,
                      indent=1)
        kind2_seen = bool(kind2_post) or any(e.get("kind2_owner0")
                                             for e in s.evidence)
        if issued and kind2_seen and tgt_moved and \
                any(m["evidence"] for m in tgt_moved):
            s.log("POSITIVE: order issued + kind-2 witness + target slot "
                  "moved with order evidence across the turn boundary")
            rc = 0
        elif kind2_seen:
            s.log("PARTIAL: kind-2 order witness present; flight NOT "
                  "attributable this session — evidence banked")
            rc = 1
        elif issued:
            s.log("PARTIAL: click battery reported publication but no kind-2 "
                  "ship state — evidence banked, witness law unmet")
            rc = 1
        else:
            s.log("NEGATIVE: no witness")
            rc = 1
        return rc
    finally:
        s.log(f"final ring snapshot; rc={rc}; killing recorded pid "
              f"{s.child.pid}")
        try:
            s.sample("cleanup")
        except Exception:
            pass
        s.cleanup()


if __name__ == "__main__":
    sys.exit(main())
