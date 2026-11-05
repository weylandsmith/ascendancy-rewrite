# t303 — MSG-CENSUS AT THE DISPATCH ENTRY (WIP)

## S0. Task (STATE.md t303 assignment)
t302 LIVE-confirmed the dispatch law (cos_hdlr stop names COSMOSWnd msg 0x3b;
btn_hdlr/NEXTTURN edx=0x7 positive control; map clicks fire no class-table
slot leg). Missing datum: the MSG VALUE (edx) per map click at the cos_hdlr
slot-2 handler / the five dispatch call sites. Deliverable: msg-id census
{sprite-click:[..], planet-click:[..], empty-click:[..]}.

## S1. CALL-SITE BYTES VERIFIED (payload work/ascend_payload.bin, 0x8cc83,
##     this session — t301 S6.1 offsets confirmed, ff 51 04 occurs EXACTLY 5x)
```
0x26eda  before 8b 88 a7 00 00 00 89 ea 47 | at ff 51 04 66 3b 7e
0x30d02  before 8b 88 a7 00 00 00 0f bf d2 | at ff 51 04 5e 59 c3
0x7a7eb  before 00 00 00 39 ea 74 07 89 ca | at ff 51 04 eb 13 ff
0x7aa3e  before 00 00 20 75 de 89 d8 89 ca | at ff 51 04 85 ff 0f
0x7b020  before 85 1c 28 0a 00 89 da 89 f8 | at ff 51 04 8b 5e 0a
```
ff5104 site list == [0x26eda, 0x30d02, 0x7a7eb, 0x7aa3e, 0x7b020] verbatim.
0x26eda and 0x30d02 are preceded by `mov ecx,[eax+0xa7]` (8b 88 a7 00 00 00)
= class-table load; eax = window record at those two sites.

## S2. INSTRUMENT DESIGN (scripts/r299_leg_session.py patched with --census)
LAWS driving the design (t302, do not re-trip):
- resuming with the FIRED BP armed re-stops at same EIP -> FREEZE. Protocol
  BPDEL(fired) -> RUN -> liveness(autosave .sav growth) -> BREAK -> re-arm ->
  RUN is already in resume_and_rearm.
- CENSUS inverts the t302 DROP policy: re-arm ALL legs after every stop
  (census wants every msg id, not one witness per leg).
- NEW t303 freeze-hazard the t302 structure hides: with a HOT leg (cos_hdlr,
  0x3b pump ~1/s) armed, ANY un-polled click (drain_popups, open_fleet, row
  jump) stops the guest and nobody banks it -> freeze mid-choreography.
  FIX: census mode arms legs ONLY around the measured click and BPDEL * +
  liveness-checked RUN between choreography steps. Per-click protocol:
  assert_on_map -> BREAK -> pmode arm-time gate -> arm_all(cos_hdlr + 5
  call-site legs) -> RUN -> MCP click -> poll pty census window (~60 s, bank
  EVERY stop tagged) -> EXEC BPDEL * -> ensure_running (autosave-growth
  liveness; RUN only if dead) -> next choreography step.
- Quiet is impossible while cos_hdlr armed (0x3b pump); attribution is by edx
  VALUE per stop, not by stop/no-stop. 0x3b = periodic noise; any other edx
  in the click window = the click's dispatch msg.
- Final PTY CENSUS over the whole mtylog per leg pattern (same
  `(?<![0-9A-Fa-f])<6hex> [0-9A-F]` law) catches anything poll_stop missed.

LEGS armed in census mode: cos_hdlr 0x26b34 + disp_26eda/30d02/7a7eb/7aa3e/
7b020 (call SITES: stop BEFORE the call, caller window-record reg still live).

## S3. RUN LOG
- Harness patches (py_compile OK, --help OK): LEGS += disp_26eda/30d02/7a7eb/
  7aa3e/7b020; census mode = re-arm ALL per stop (witnessed-set bypassed),
  bank-window policy (bank EVERY stop for N s, cap 6, NOT until-quiet — the
  0x3b pump means quiet never comes); census_click = assert_on_map ->
  arm_census (BREAK + pmode gate + arm_all + payload control dump) -> RUN ->
  MCP click -> census_window -> disarm_run (BREAK, BPDEL *, BPLIST-empty,
  RUN, autosave liveness). Choreography between clicks runs LEG-FREE (t302
  freeze law). pty_peek (non-consuming) added for the re-fire liveness
  shortcut. census-arm FAILURE path does BPDEL * before RUN. Baseline window
  15 s; click windows 45 s as run.
- scripts/r303_relaunch.sh NEW (3 attempts, success tell "SESSION END rc=0").
- ATTEMPT 1 work/r1/t299-leg-20261105-015611 rc=1; ATTEMPT 2
  work/r1/t299-leg-20261105-020416 rc=1 IDENTICAL signature; attempt 3 killed
  early (reproduction achieved; one-battery law). ZERO freezes across 2 full
  sessions — the census arm/click/disarm cycle BEATS the t302 freeze bug.

## S4. MEASURED (attempt 1; attempt 2 reproduces every line)
- Instrument alive: census control MATCH=True x5 (MEMDUMPBIN vs payload);
  baseline window (no click) banked STOPs cos_hdlr edx=0x3b win[eax]
  name='COSMOSWnd' repeatedly (post-rearm cascade banked them); autosave
  cadence 10 s unbroken t=1086 whole session (guest alive, never frozen).
- WHOLE-LOG PTY CENSUS: {'cos_hdlr': 15, 'disp_26eda': 0, 'disp_30d02': 0,
  'disp_7a7eb': 0, 'disp_7aa3e': 0, 'disp_7b020': 0} — across the ENTIRE
  session (baseline storm + 4 click windows) the five slot-1 `call [ecx+4]`
  sites NEVER executed while cos_hdlr executed 15x.
- View: star='Icarus', sprites=[(48,151,296)], planet=(439,331),
  empty=(236,200) (same points as t300/t302).
- sprite click (48,151): 0 stops banked, BUT the click LANDED: pixel diff
  13_census_view->14_precheck(pre-click precheck identical, diff 0) ->
  15_precheck = 66717 px; VISION on 15_precheck: modal dialog "Ship
  'Sparrowhawk'" with buttons Leave Orbit / Abandon / Cancel. So a WORKING
  map click that opens the ship dialog touches NONE of the 6 armed legs.
- planet/empty/control_nextturn windows: 0 stops; INVALID-AS-CONTROLS —
  (a) the modal dialog opened by the sprite click was NEVER closed
  (census_click has no close_eventwin — t298 law re-broken, instrument
  defect), so those clicks hit the dialog (screen diffs 225/207 px =
  swallowed); (b) the armed set never included btn_hdlr, so NEXTTURN could
  not be witnessed by construction. Turn stayed 1086 (verified via
  zipfile 'Memory' B+OFF+0x12e10 across all 20 autosaves of both runs).

## S5. REFUTATION (offline, from t302's OWN logs + t303 whole-log census)
1. t302 run 004605 log: 00:48:10 're-armed 7 legs ok=True' (BPLIST includes
   0160:1F0158 = router) then 00:48:21 STOP endturn-p1 leg=btn_hdlr — the
   WORKING End-Turn click reached the slot-2 handler WITHOUT router (slot 1)
   ever stopping. Same shape in t303: cos_hdlr (slot 2) fired 15x with the
   5 slot-1 sites armed and silent — the 0x3b pump itself does not traverse
   ff 51 04. => t301 S6.2 "every click (working or not) walks slot1 0x30d08"
   is REFUTED (filed REFUTED-ROUTES t303). Slot 1 == 0x30d08 in every table
   remains [verified]; it is simply NOT the universal msg dispatch point.
2. Static census this session (payload): call [ecx+0xc] (slot 3) = 7 sites
   (0x1d836, 0x314e1, 0x32235, 0x32ecc, 0x3cb5c, 0x3cb6e, 0x4e634);
   `mov r32,[r32+0xa7]` = 21 sites (cluster 0x14de8..0x14f14 x6, plus
   0x1d82c, 0x2cb4a, 0x3c941, 0x49556/0x495c4/0x4982f, 0x4eabd, the 2 known
   ff5104 predecessors); indexed calls `ff 14 <modrm>` = ZERO for every
   reg/idx combo. Strings 'Leave Orbit'/'Abandon'/'Scientist Takeover' NOT
   in payload plaintext -> the system-view dialog chrome is not obj1
   plaintext (compressed or another module) [verified: not-in-plaintext].
3. E8 direct calls to cos_hdlr/btn_hdlr/cos_s3/router/cos_entry: ZERO
   (consistent — handlers are table-reached, but by WHAT instruction is now
   the open question; the +0xa7 21-site cluster is the candidate).

## S6. NEXT (t304): CALLER WITNESS AT THE cos_hdlr STOP — DUMP [esp]
The pump DELIVERS 0x3b to cos_hdlr through the real (unknown) dispatch
instruction. At any cos_hdlr stop the return address at [esp] names the
CALLER EIP VERBATIM — one MEMDUMPBIN(esp,8) per stop, attribute
ret&0xFFFFFF-P0 to a file offset, static-read around it -> the true dispatch
site. Then repeat the click census armed at THAT site (+ close_eventwin
between clicks + btn_hdlr in the armed set as NEXTTURN control). Patch =
bank_stop dumps esp 8 bytes, records ret0/ret1 + eip_file_off attribution.
