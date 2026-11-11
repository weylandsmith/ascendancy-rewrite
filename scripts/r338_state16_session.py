#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t338 — STATE-16 LIVE DRIVE: witness the BatControlWnd mode-1 arming chain
while the game is ACTUALLY in battle state 16 (core+0x4228 == 16).

S0 SITTING CHECK: done by the iteration (tail-seek newest turn 1086 == corpus).

S1 TRIGGER (MEASURED, docs/re/_wip_t338.md S1): the five state-16 saves of run
work/r1/t299-leg-20261105-112859 (43..47.sav) sit EXACTLY inside the star1
census window — the galaxy-map pip click (238,282) ENTERS the Icarus system
(battle) view = state 16; Escape exits it. The click is deterministic from the
md5-pinned RESUME.GAM (t307/t308 reproduced the enter diff).

Question (docs/STATE.md NEXT t338): with current-state==16, do ANY of the eight
t332 chain legs fire? New routing legs prove the state-16 machinery is live:
  hit_test_56890 0x56890  hit-test fn ENTRY (t337 reader inventory; HOT)
  focus_56aa4    0x56AA4  focus-set arm inside the hit-test fn
  setstate_56e10 0x56E10  SET-STATE entry (edx = new state id; t337 sole writer
                         of core+0x4228 at 0x56f66)
  ringa_55ea3    0x55EA3  RING-A code-1 resolver arm (`call 0x56e10` — the
                         state-switch path t337 named)

Sub-batteries (t330 entry-consumption law: an armed ENTRY leg eats the window):
  S: {setstate_56e10, ringa_55ea3, btn_hdlr} armed ACROSS the enter click —
     witness = stop with edx=0x10 at setstate_56e10.
  A: downstream chain {tbl15ef1, gate15fed, post1615d, relay1616f, post161d1,
     mode1_1b7dd, backch_1b180} + btn_hdlr control — clicked the state-16
     family rows (windows.txt text-space centres; W/S/Z/I child buttons,
     My^Items/Other^Items, BatListWnd interior, TOGGRID/BATROTLEFT/BATZOOMIN).
  B: {fn156d4_entry, btn_hdlr} ALONE — separates "never messaged" from
     "a downstream leg ate it".
  H: {hit_test_56890, focus_56aa4} ALONE (hot: fires on mouse traffic) —
     proves state-16 click routing EXECUTES while A/B are zero.
Oracles: per-save CURRENT-STATE u16 via the r337 fingerprint (state axis,
independent of the debugger) + BatControlWnd/BatModeWnd magic-record b7/b9
(r332 batrec oracle). Destructive rows (ABANDON, Pass/Auto/Repeat) LAST.

SAFETY: scratch game-wp only (preflight asserts); OWN ring dir; private Xvfb
(:97 default, NEVER production :9); core=normal; -time-limit; teardown SIGKILL
by RECORDED PID (t325 law); Oct-29 md5-verified RESUME.GAM; NEVER loadstate.
Exit 0 = session ran and control btn_hdlr fired; 1 = honest negative / control
silent / enter failed; 2 = harness error.
"""
import argparse
import json
import os
import os.path as op
import sys
import time

ROOT = op.abspath(op.join(op.dirname(__file__), ".."))
sys.path.insert(0, op.join(ROOT, "scripts"))
import r299_leg_session as L                        # noqa: E402
import r1_dbg_session as D                           # noqa: E402
import r332_batctrl_session as T332                  # noqa: E402
import r337_state_word as SW                         # noqa: E402

NEW_LEGS = {"hit_test_56890": 0x56890,   # hit-test fn entry (t337 inventory)
            "focus_56aa4":    0x56AA4,   # focus-set arm inside hit-test fn
            "setstate_56e10": 0x56E10,   # SET-STATE entry (edx=newstate)
            "ringa_55ea3":    0x55EA3}   # RING-A code-1 resolver arm -> 0x56e10
D.LEGS.update(NEW_LEGS)
L.LEGS.update(NEW_LEGS)
CTRL = "btn_hdlr"
LEGS_S = ["setstate_56e10", "ringa_55ea3", CTRL]
LEGS_A = ["tbl15ef1", "gate15fed", "post1615d", "relay1616f", "post161d1",
          "mode1_1b7dd", "backch_1b180", CTRL]
LEGS_B = ["fn156d4_entry", CTRL]
LEGS_H = ["hit_test_56890", "focus_56aa4"]
ALL_LEGS = list(dict.fromkeys(LEGS_S + LEGS_A + LEGS_B + LEGS_H))

ENTER = (238, 282)            # Icarus pip: MEASURED state-16 trigger (S1)
# state-16 family click rows (windows.txt text space; t332 law 5):
ROWS_A = [("myitems",    (513, 118)), ("otheritems", (591, 118)),
          ("w_btn",      (494, 118)), ("s_btn",      (533, 118)),
          ("z_btn",      (572, 118)), ("i_btn",      (611, 118)),
          ("batlist",    (553, 200)), ("toggrid",    (572, 418)),
          ("rotleft",    (486, 418)), ("zoomin",     (533, 410))]
ROWS_B = [("myitems",    (513, 118)), ("s_btn",      (533, 118)),
          ("i_btn",      (611, 118)), ("batlist",    (553, 200))]
ROWS_H = [("myitems",    (513, 118)), ("batlist",    (553, 200))]
ROWS_TAIL = [("pass",    (500, 70)), ("auto",       (604, 70)),
             ("repeat",  (552, 70))]     # LAST: may change state (combat round)


class S16Sess(T332.BatSess):
    """BatSess + per-save CURRENT-STATE oracle (r337 fingerprint)."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.per_id = SW.file_truth()
        self.state_hist = []

    def state_oracle(self, tag):
        s = self.s
        try:
            p = s.newest_sav()
            mm = s.read_mem(p) if p else None
            if not mm:
                return None
            B, votes, hname = SW.find_base(mm, self.per_id)
            row = {"tag": tag, "sav": op.basename(str(p)),
                   "B": hex(B) if B else None}
            if B:
                import struct
                row["state"] = struct.unpack_from("<H", mm, B + 0x4228)[0]
                row["groups"] = struct.unpack_from("<H", mm, B + 0x4226)[0]
            self.state_hist.append(row)
            with open(op.join(s.out, "state_hist.json"), "w") as fh:
                json.dump(self.state_hist, fh, indent=1)
            s.log(f"STATE-ORACLE {tag} sav={row['sav']} state={row.get('state')} "
                  f"groups={row.get('groups')}")
            return row
        except Exception as e:
            s.log(f"STATE-ORACLE {tag} error {e!r}")
            return None

    def run_phases(self):
        s = self.s
        res = {}
        map_im = s.grab("map0")
        # ---- S: state-switch witness, armed ACROSS the enter click ----
        self.state_oracle("S_map_before")
        self.set_legs(LEGS_S)
        res["S_enter"] = s.census_click(ENTER[0], ENTER[1], "S_enter", self.window)
        im16 = s.grab("state16_screen")
        dv = s.diff_px(map_im, im16) if im16 is not None else -1
        so = self.state_oracle("S_state16")
        res["S_entered"] = {"diff": dv, "state": (so or {}).get("state")}
        s.log(f"S: enter diff={dv} state={(so or {}).get('state')}")
        if dv < 15000 or (so or {}).get("state") != 16:
            s.log("S: ENTER FAILED / state!=16 — aborting battery (honest "
                  "negative; trigger did not reproduce this boot)")
            if not s.escape_to_map(map_im):
                return res
            return res
        # ---- A: downstream chain in state 16 ----
        self.set_legs(LEGS_A)
        for nm, xy in ROWS_A:
            res[f"A_{nm}"] = self.click_phase(xy, f"A_{nm}", self.window)
            cur = self.state_oracle(f"A_{nm}_state")
            if (cur or {}).get("state") != 16:
                s.log(f"A_{nm}: STATE LEFT 16 mid-battery — stopping A")
                break
        # ---- B: entry leg alone in state 16 (re-enter if state was lost) ----
        cur = self.state_oracle("B_pre")
        if (cur or {}).get("state") != 16:
            s.log("B: re-entering state 16 leg-free")
            if not s.escape_to_map(map_im):
                return res
            s.click(ENTER[0], ENTER[1], "B_reenter", wait=4.0)
            cur = self.state_oracle("B_reentered")
            if (cur or {}).get("state") != 16:
                s.log("B: re-enter failed — skipping B/H")
                return res
        self.set_legs(LEGS_B)
        for nm, xy in ROWS_B:
            res[f"B_{nm}"] = self.click_phase(xy, f"B_{nm}", self.window)
        # ---- H: routing legs alone (hot) ----
        self.set_legs(LEGS_H)
        for nm, xy in ROWS_H:
            res[f"H_{nm}"] = self.click_phase(xy, f"H_{nm}", self.window)
        # ---- tail: combat-round rows LAST (may leave state 16) ----
        self.set_legs(LEGS_A)
        for nm, xy in ROWS_TAIL:
            res[f"T_{nm}"] = self.click_phase(xy, f"T_{nm}", self.window)
        # ---- exit leg-free ----
        s.escape_to_map(map_im)
        self.state_oracle("final_map")
        return res


def analyze(run):
    cpath = op.join(run, "census.json")
    if not op.exists(cpath):
        print("ANALYZE: no census.json")
        return 2
    census = json.load(open(cpath))["pty_census"]
    hits = json.load(open(op.join(run, "hits.json"))) if op.exists(op.join(run, "hits.json")) else []
    batrec = json.load(open(op.join(run, "batrec.json"))) if op.exists(op.join(run, "batrec.json")) else []
    state_hist = json.load(open(op.join(run, "state_hist.json"))) if op.exists(op.join(run, "state_hist.json")) else []
    control = census.get(CTRL, 0)
    entry = census.get("fn156d4_entry", 0)
    mode1 = census.get("mode1_1b7dd", 0)
    setst = census.get("setstate_56e10", 0)
    ringa = census.get("ringa_55ea3", 0)
    hit = census.get("hit_test_56890", 0)
    foc = census.get("focus_56aa4", 0)
    downstream = {k: census.get(k, 0) for k in LEGS_A if k != CTRL}
    # witness-class: a setstate stop with edx==0x10 (new state 16)
    setst16 = [h for h in hits if h.get("leg") == "setstate_56e10"
               and (h.get("msg_id_lo") == 0x10 or
                    (h.get("regs") or {}).get("edx") in ("0x10", "0x10"))]
    mode1_sav = sorted({(r["tag"], h["rec_runtime"]) for r in batrec
                        for h in r.get("BatModeWnd", []) if h.get("b7_mode") == 1})
    states_seen = sorted({r.get("state") for r in state_hist if "state" in r})
    if mode1 or mode1_sav:
        v = ("OUTCOME A: MODE-1 ARMING WITNESSED in state 16"
             + (f" (leg mode1_1b7dd x{mode1})" if mode1 else "")
             + (f" save-axis b7==1 at {mode1_sav[:3]}" if mode1_sav else "")
             + " — residue-1 arming edge CLOSED-CLASS candidate; nuke-effect "
               "witness still required before any closure claim (strict-close).")
    elif entry:
        eaten = [k for k, n in downstream.items() if n]
        v = ("OUTCOME B: fn 0x156d4 WAS messaged in state 16 (entry x%d) but "
             "mode-1 never fired. Legs that fired: %s. The arming question "
             "moves INSIDE fn 0x156d4 (msg 0x51 gate path); row stays open."
             % (entry, eaten or "NONE"))
    elif control and hit:
        v = ("OUTCOME C: instrument alive (btn_hdlr x%d) AND state-16 routing "
             "LIVE (hit_test x%d, focus x%d, setstate x%d edx16 x%d, ringa x%d) "
             "yet the ENTIRE chain {8 legs} is ZERO in state 16 — SECOND "
             "independent zero. The arming question moves to fn 0x156d4's "
             "internal gates (msg 0x51 path). Row stays OPEN strict-close."
             % (control, hit, foc, setst, len(setst16), ringa))
    elif control:
        v = ("OUTCOME C': control btn_hdlr x%d alive, chain ZERO, but routing "
             "legs also zero (H battery may not have run — check phases). "
             "Weaker than C; row stays open." % control)
    else:
        v = "VOID: control silent — battery did not exercise the UI. NOT evidence."
    out = {"census": census, "control": control, "entry": entry, "mode1": mode1,
           "setstate": setst, "setstate_edx16": len(setst16), "ringa": ringa,
           "hit_test": hit, "focus": foc, "downstream": downstream,
           "mode1_sav": mode1_sav, "states_seen": states_seen,
           "banked_stops": len(hits), "verdict": v}
    with open(op.join(run, "t338_verdict.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print("CENSUS", json.dumps(census))
    print("STATES SEEN", states_seen)
    print("BANKED STOPS", len(hits))
    print("VERDICT:", v)
    return 0 if control else 1


def live_attempt(tag, window, disp, port, tl, settle):
    ds = S16Sess(tag, ALL_LEGS, [], window, disp, port, tl, settle, 0)
    s = ds.s
    try:
        s.log(f"t338 start out={s.out} legsS={LEGS_S} legsA={LEGS_A} "
              f"legsB={LEGS_B} legsH={LEGS_H} window={window}")
        s.launch()
        conn = s.connect()
        if conn is None:
            s.log("NEGATIVE: no MCP connection")
            return 1
        lines, ok, hdr = s.req("PING", 10.0)
        if "PONG" not in " ".join(lines):
            s.log("NEGATIVE: no PONG")
            return 1
        s.log(f"settling {settle}s before BREAK")
        time.sleep(settle)
        if not s.do_break():
            s.log("NEGATIVE: BREAK lottery lost — relaunch")
            return 1
        lines, ok, hdr = s.req("EXEC RUN", 20.0)
        s.log(f"post-lottery RUN hdr={hdr}")
        s.pty_new()
        if not s.wait_title():
            s.log("NEGATIVE: title never appeared")
            return 1
        if not s.enter_campaign():
            s.log("NEGATIVE: campaign entry failed")
            return 1
        time.sleep(settle)
        closed = s.drain_popups()
        s.log(f"post-load drain closed {closed}")
        rows = s.ring_mem_rows()
        mem = s.read_mem(rows[-1]["path"]) if rows else None
        B = L.SL.base_of(mem, s.anch) if mem else None
        s.log(f"ring base B={hex(B) if B else None} (expect {hex(L.EXPECT_BASE)})")
        if B != L.EXPECT_BASE:
            s.log("NEGATIVE: base mismatch — armed addresses invalid")
            return 1
        ds.state_oracle("pre_battery")
        ds.batrec_oracle("pre_battery")
        s.census = True
        s.pay = open(L.R293.PAYLOAD, "rb").read()
        ph_res = ds.run_phases()
        if ph_res is None:
            return 2
        ds.whole_log_census()
        ds.bank_on_exit()
        with open(op.join(s.out, "phases.json"), "w") as fh:
            json.dump({k: (v if isinstance(v, (dict, int, float, bool, list))
                           else None)
                       for k, v in ph_res.items()}, fh, indent=1)
        return 0
    finally:
        ds.teardown()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="t338")
    ap.add_argument("--window", type=int, default=45)
    ap.add_argument("--disp", default="97")
    ap.add_argument("--port", type=int, default=55998)
    ap.add_argument("--tl", type=int, default=7200)
    ap.add_argument("--settle", type=int, default=45)
    ap.add_argument("--attempts", type=int, default=2)
    ap.add_argument("--offline", default=None, metavar="RUN_DIR")
    args = ap.parse_args()

    if args.offline:
        run = op.abspath(args.offline)
        rc = D.offline_run(run, [], ALL_LEGS)
        return analyze(run) or (0 if rc == 0 else 1)

    rc = D.preflight(ALL_LEGS)
    if rc:
        return rc
    if not D.port_free(args.port):
        print(f"HARNESS ERROR: MCP port {args.port} busy")
        return 2
    for i in range(1, args.attempts + 1):
        print(f"=== ATTEMPT {i} {time.strftime('%H:%M:%S')} ===", flush=True)
        rc = live_attempt(args.tag, args.window, args.disp, args.port,
                          args.tl, args.settle)
        cands = sorted((d for d in os.listdir(op.join(ROOT, "work/r1"))
                        if d.startswith(f"dbg-{args.tag}-")), reverse=True)
        run = op.join(ROOT, "work/r1", cands[0]) if cands else None
        print(f"attempt {i} rc={rc} run={run}", flush=True)
        if rc == 2:
            print("ATTEMPT harness error — NOT retrying")
            return 2
        if rc == 0 and run:
            ar = analyze(run)
            print(f"analyze rc={ar}")
            return 0 if ar == 0 else 1
    return 1


if __name__ == "__main__":
    sys.exit(main())
