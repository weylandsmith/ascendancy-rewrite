// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
// t409 SPECIAL ABILITY dialog law (docs/re/_wip_t409.md F1/F2).
//
// THE VENDOR BUTTON IS NOT DEAD [verified disassembly, restored image]:
// the msg-5 rail press lands in the winmgr path at 0x55ffb..0x56010 —
//   MOV EDX,0x85975 ("ABILITYWIN") ; CALL 0x56d1c (window-by-name lookup)
//   CALL 0x37b14                   ; the opener below
// and the opener 0x37b14..0x37b69 builds the dialog TEXT:
//   DL = [0x7458e] (player specnum) -> race record base 0x12e16 + specnum*494
//   -> [rec+0x19a] >> 24 = ability index -> sprintf("abil%02d") (pool
//   0x84848 file "help.txt") -> CALL 0x33f40 (topic panel opener).
// So the dialog shows the PLAYER SPECIES' help.txt `help abilNN` block in
// the ABILITYWIN modal (windows.txt ln2136: TYPE 22, STATE "0",
// 60,100-395,355, SHAPEFRAME -1 = CODE-DRAWN, children ABILBUTTON0/1 cover
// the SAME full rect and send msg 50 = the dialog-button dismiss family of
// the HELPWINDOW/EVENTWIN modal lib).
//
// THE BLOCK FORMAT [verified help.txt ln1713..2511, 21 blocks]:
//   help abilNN / text "<Race> Special Ability" endtext / pos 10 50
//   text <body> endtext / pos 10 125
//   [charged only] text "It will take %d day%s to amass the energy needed
//    to use your ability." endtext / pos 10 160
//   button title Use^Ability msg 1  +  button title Cancel msg 0   (charged)
//   button title OK msg 0                                          (passive)
// The `pos` lines are WINDOW-RELATIVE (10,50 / 10,125 / 10,160) — the first
// cited text geometry for this dialog; buttons carry NO pos (NAMED SEAM S1:
// ABILBUTTON0/1 full-rect hit law is the only button geometry in the table,
// so the port hits the WHOLE window rect as dismiss and draws the button
// faces at the cited body column; the vendor's per-button split of the full
// rect is unmapped).
//
// USE-ABILITY (button msg 1) is the PLAYER-triggered fire path: dispatcher
// 0x37b6a legs DX==1 -> CALL 0x43b50 with edx=1 (the cadence fn's probe
// arg). The rewrite's documented model AUTO-FIRES the player's ability on
// cadence (abilities.md §3 — the vendor EXCLUDES the player row from the AI
// firing loop, so click-to-use vs auto-fire is a SIM-semantics choice that
// would move the seed-regression md5). This iteration ships the DIALOG as
// read-only: the Use Ability face is drawn per the block, pressing it inside
// the dialog still dismisses, and the seam is named. Firing law stays
// abilities.md §3 until a dedicated sim row re-records the seeds.
#include <string>
#include <vector>

#include "ui/layout.h"

namespace ascend::ui {

struct AbilityButton {
    std::string title;  // '^' word-join already joined ("Use Ability")
    int msg = 0;        // verbatim msg field
};

struct AbilityPanel {
    int index = -1;         // the NN in "abilNN"
    std::string title;      // "<Race> Special Ability" (verbatim)
    std::string body;       // main text block (vendor line breaks kept)
    std::string chargeLine; // "" unless the block carries the %d day%s line
    std::vector<AbilityButton> buttons;
};

// Parse every `help abilNN` block out of help.txt. Expects exactly 21
// blocks, indices 0..20 contiguous (the gate-3m census); refuses otherwise.
bool loadAbilityPanels(const std::string& helpTxtPath,
                       std::vector<AbilityPanel>* out, std::string* err);

// The panel for ability index `idx` (== SpeciesAbility ordinal == the
// vendor's race-record +0x19a byte), or null out of domain.
const AbilityPanel* panelForIndex(const std::vector<AbilityPanel>& panels,
                                  int idx);

// The ABILITYWIN modal rect VERBATIM (windows.txt ln2136-2143): x0 60 y0
// 100 x1 395 y1 355.
extern const Rect kAbilityWin;

// Dialog hit law [verified]: ABILBUTTON0/1 BOTH cover the full ABILITYWIN
// rect (windows.txt ln2152-2185) — every click inside the modal is a
// dialog-button press (msg 50 dismiss family). Outside the rect: no-op.
bool abilityDialogHit(int x, int y);

// Format the charged block's "%d day%s" line (vendor template verbatim in
// the parsed chargeLine): remaining days + the plural law used across the
// port (n==1 -> "", else "s"; fleet-screen F10 sibling). [seam note] the
// vendor's remaining-days operand is unmapped; the port passes
// abilityChargeTurns - currentCharge (never below 0).
std::string formatChargeLine(const std::string& tmpl, int remaining);

// Greedy word-wrap for the body blocks: the vendor lines are already
// sentence-broken at ~70 chars but the 336-px modal fits ~50 small-font
// chars; wrapping is a PORT rendering choice (labelled seam S2), never a
// text change (the parser keeps the vendor bytes verbatim).
std::vector<std::string> wrapBody(const std::string& text, int maxChars);

}  // namespace ascend::ui
