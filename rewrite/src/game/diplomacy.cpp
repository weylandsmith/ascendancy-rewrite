#include "game/diplomacy.h"

#include <algorithm>
#include <cmath>
#include <fstream>
#include <sstream>

#include "game/starstat.h"  // cp437ToUtf8

namespace ascend::game {
namespace {

// .dip files are CP437 with CRLF and a 0x1A EOF marker (same container
// conventions as the other ascend00 text; docs/re/text.md).
std::vector<std::string> dipLines(const std::string& decoded) {
    std::vector<std::string> out;
    std::string cur;
    for (char c : decoded) {
        if (c == '\x1A') break;
        if (c == '\r') continue;
        if (c == '\n') { out.push_back(cur); cur.clear(); }
        else cur += c;
    }
    out.push_back(cur);
    return out;
}

bool isSignedInt(const std::string& s, int* v) {
    if (s.empty()) return false;
    size_t i = (s[0] == '-' || s[0] == '+') ? 1 : 0;
    if (i == s.size()) return false;
    for (; i < s.size(); ++i)
        if (s[i] < '0' || s[i] > '9') return false;
    try { *v = std::stoi(s); } catch (...) { return false; }
    return true;
}

// key -> member. NOTE: vendor spelling "BIO_MAXPOSITVE" (sic) preserved —
// docs/re/diplomacy.md §1.
bool setKey(DipValues* v, const std::string& key, int val) {
    auto put = [&](const std::string& name, int& field) {
        if (key == name) { field = val; return true; }
        return false;
    };
    if (put("ACCEPT_ALLIANCE", v->acceptAlliance)) return true;
    if (put("ACCEPT_PEACE", v->acceptPeace)) return true;
    if (put("BREAK_ALLIANCE", v->breakAlliance)) return true;
    if (put("DECLARE_WAR", v->declareWar)) return true;
    if (put("PROPOSE_ALLIANCE", v->proposeAlliance)) return true;
    if (put("PROPOSE_PEACE", v->proposePeace)) return true;
    if (put("SHIP_PATIENCE", v->shipPatience)) return true;
    if (put("START_ATTITUDE", v->startAttitude)) return true;
    if (put("BIO_MAXNEGATIVE", v->bioMaxNegative)) { v->hasOscillation = true; return true; }
    if (put("BIO_MAXPOSITVE", v->bioMaxPositive)) { v->hasOscillation = true; return true; }
    if (put("BIO_PERIOD", v->bioPeriod)) { v->hasOscillation = true; return true; }
    if (put("BIO_SIN_X", v->bioSinX)) { v->hasOscillation = true; return true; }
    if (put("BIO_SIN_HALF_X", v->bioSinHalfX)) { v->hasOscillation = true; return true; }
    if (put("BIO_SIN_TWICE_X", v->bioSinTwiceX)) { v->hasOscillation = true; return true; }
    if (put("NEG_PLAYER_TURNS", v->negPlayerTurns)) return true;
    return false;  // unknown key
}

}  // namespace

bool DipValues::parse(const std::string& text, DipValues* out, std::string* err) {
    *out = DipValues{};
    auto lines = dipLines(text);
    size_t start = -1;
    for (size_t i = 0; i < lines.size(); ++i)
        if (lines[i] == "DIPVALUES") { start = i; break; }
    if (start == static_cast<size_t>(-1)) { *err = ".dip: no DIPVALUES line"; return false; }
    int seen = 0;
    for (size_t i = start + 1; i < lines.size(); ++i) {
        if (lines[i] == "ACTIONS") break;
        if (lines[i].empty()) continue;
        std::istringstream ss(lines[i]);
        std::string key, valTok;
        if (!(ss >> key >> valTok)) { *err = ".dip:" + std::to_string(i + 1) + ": malformed DIPVALUES row"; return false; }
        int val;
        // Negative values are legal and significant (BIO_MAXNEGATIVE is
        // negative in all 21 races) — an isdigit-style test silently drops
        // them; use signed parse (docs/re/diplomacy.md §1 parse trap).
        if (!isSignedInt(valTok, &val)) { *err = ".dip:" + std::to_string(i + 1) + ": non-integer value '" + valTok + "'"; return false; }
        if (!setKey(out, key, val)) { *err = ".dip:" + std::to_string(i + 1) + ": unknown key '" + key + "'"; return false; }
        ++seen;
    }
    // No fixed key count is required by the data: player.dip has 8, raceNN
    // have 15 (docs/re/diplomacy.md §1). Any unknown key is still an error.
    if (seen < 1) { *err = ".dip: DIPVALUES block empty"; return false; }
    return true;
}

bool DipValues::loadFromFile(const std::string& path, DipValues* out, std::string* err) {
    std::ifstream f(path, std::ios::binary);
    if (!f) { *err = path + ": cannot open"; return false; }
    std::stringstream buf;
    buf << f.rdbuf();
    // DIPVALUES keys/values are ASCII; decode CP437 for uniformity anyway.
    return parse(cp437ToUtf8(buf.str()), out, err);
}

bool DipFile::loadFromFile(const std::string& path, std::string* err) {
    std::ifstream f(path, std::ios::binary);
    if (!f) { *err = path + ": cannot open"; return false; }
    std::stringstream buf;
    buf << f.rdbuf();
    std::string text = buf.str();
    if (!DipValues::parse(text, &values, err)) return false;
    auto lines = dipLines(text);
    // header comment: "Diplomacy text for <NAME> - SA_<Ability>."
    for (size_t i = 0; i < std::min<size_t>(3, lines.size()); ++i) {
        const std::string& h = lines[i];
        auto forPos = h.find("for ");
        auto saPos = h.find("SA_");
        if (forPos != std::string::npos) {
            // Tokenless headers exist: race02.dip is "Diplomacy text for
            // Orfa." with no SA_ token [verified]; displayName parses either
            // shape, abilityToken stays "" when absent (resolved by
            // game/species.cpp against help.txt help-abil02 title "Orfa").
            const size_t nameEnd = (saPos != std::string::npos && saPos > forPos)
                                       ? saPos : h.size();
            displayName = h.substr(forPos + 4, nameEnd - forPos - 4);
            while (!displayName.empty() && (displayName.back() == '-' || displayName.back() == ' ' || displayName.back() == '.'))
                displayName.pop_back();
            if (saPos != std::string::npos && saPos > forPos) {
                abilityToken = h.substr(saPos);
                size_t end = 0;
                while (end < abilityToken.size() &&
                       (isalnum(abilityToken[end]) || abilityToken[end] == '_')) ++end;
                abilityToken.resize(end);
            }
            break;
        }
    }
    // DA_ blocks: "DA_Key" line, body lines until blank line (verified
    // structure of the 15 DA_ keys in race00.dip).
    for (size_t i = 0; i < lines.size(); ++i) {
        if (lines[i].rfind("DA_", 0) != 0) continue;
        std::string body;
        size_t j = i + 1;
        for (; j < lines.size() && !lines[j].empty(); ++j) {
            if (!body.empty()) body += " ";
            body += lines[j];
        }
        dialogue[lines[i]] = body;
        i = j - 1;
    }
    return true;
}

AttitudeModel::AttitudeModel(const DipValues& v) : v_(v) {
    coeffAbsSum_ = std::abs(v.bioSinX) + std::abs(v.bioSinHalfX) +
                   std::abs(v.bioSinTwiceX);
}

double AttitudeModel::mood(int turn) const {
    if (!v_.hasOscillation || v_.bioPeriod <= 0 || coeffAbsSum_ == 0) return 0.0;
    double x = 2.0 * M_PI * static_cast<double>(turn) / v_.bioPeriod;
    double s = v_.bioSinX * std::sin(x) + v_.bioSinHalfX * std::sin(x / 2.0) +
               v_.bioSinTwiceX * std::sin(2.0 * x);
    // Scale the unit-range blend into the species' [neg, pos] envelope:
    // positive blends map to bioMaxPositive, negative to bioMaxNegative
    // (docs/re/diplomacy.md §1, [inferred] exact mapping).
    double unit = s / coeffAbsSum_;
    return unit >= 0 ? unit * v_.bioMaxPositive : unit * -v_.bioMaxNegative;
}

std::string renderDialogue(const std::string& body, const std::string& me,
                           const std::string& you, const std::string& star,
                           const std::string& third) {
    std::string out;
    out.reserve(body.size());
    for (size_t i = 0; i < body.size(); ++i) {
        if (body[i] != '%' || i + 1 >= body.size()) { out += body[i]; continue; }
        char t = body[i + 1];
        const std::string* rep = nullptr;
        switch (t) {
            case 'm': rep = &me; break;
            case 'y': rep = &you; break;
            case 's': rep = &star; break;
            case 't': rep = &third; break;
            default: break;
        }
        if (rep) { out += *rep; ++i; }
        else out += body[i];  // unknown token stays literal (documented default)
    }
    return out;
}

const char* dipActionName(DipAction a) {
    switch (a) {
        case DipAction::None: return "None";
        case DipAction::ProposePeace: return "ProposePeace";
        case DipAction::ProposeAlliance: return "ProposeAlliance";
        case DipAction::AcceptPeace: return "AcceptPeace";
        case DipAction::AcceptAlliance: return "AcceptAlliance";
        case DipAction::BreakAlliance: return "BreakAlliance";
        case DipAction::DeclareWar: return "DeclareWar";
    }
    return "?";
}

DipAction decideDipAction(const DipValues& v, const AttitudeModel& mood,
                          int turn, DipPolicyState* st) {
    // MEASURED chooser (docs/re/diplomacy.md §7 FUN_00044a44 + §8 field
    // map): thresholds are the vendor DIPVALUES weights, loaded POSITIONALLY
    // from raceNN.dip (loader FUN_00044290; DECLARE_WAR->+0x1c9 ...
    // PROPOSE_ALLIANCE->+0x1d3, ascending-enforced). Original comparisons
    // are STRICT: declare-war iff att < DECLARE_WAR; propose-alliance iff
    // PROPOSE_ALLIANCE < att; break-alliance iff att < BREAK_ALLIANCE;
    // offer-peace iff PROPOSE_PEACE < att.
    // §9 (t14): the original ALSO emits trade messages (DA idx 4/5/6) on a
    // turn % NEG_PLAYER_TURNS cadence behind share/multiple floors
    // (0.9/2.0, 0.9/1.6, 0.85/1.7; min counts 5/3/5) and third-party
    // messages (10/7/9, roll<80). The rewrite's dialogue AI has no
    // trade/third-party offer engine — §9 preserves the measured law for
    // future wiring; decideDipAction stays the threshold-exact two-party
    // main-branch model (scope decision, not a silent stub).
    double m = mood.mood(turn);
    int att = st->attitude + static_cast<int>(m);
    // NEG_PLAYER_TURNS: a negative excursion sticks (drags the baseline
    // proportionally longer) — [inferred] reading: apply full mood while |m|
    // pushes down, decay otherwise.
    if (m < 0) att = st->attitude + static_cast<int>(m * 2);

    DipAction act = DipAction::None;
    if (!st->atWar && !st->allied) {
        // strict > per §7 (state1: PROPOSE_ALLIANCE < att -> DA idx 3)
        if (att > v.proposeAlliance) act = DipAction::ProposeAlliance;
        // original ALSO gates declare-war on per-race tech level
        // (DAT_00013b9c word hi > 2) — DipPolicyState has no tech field;
        // documented extension, not copied (§8).
        else if (att < v.declareWar) act = DipAction::DeclareWar;
    } else if (st->allied) {
        // §7 state3: att < BREAK_ALLIANCE -> DA idx 8
        if (att < v.breakAlliance) act = DipAction::BreakAlliance;
    } else {  // at war
        // §7 state3: PROPOSE_PEACE < att -> DA idx 13 (strict)
        if (att > v.proposePeace) act = DipAction::ProposePeace;
    }

    switch (act) {
        case DipAction::DeclareWar: st->atWar = true; att -= v.negPlayerTurns / 4; break;
        case DipAction::BreakAlliance: st->allied = false; att -= v.negPlayerTurns / 4; break;
        case DipAction::ProposeAlliance: break;  // state changes only on accept
        case DipAction::ProposePeace: break;
        default: break;
    }
    st->attitude = att;
    return act;
}

}  // namespace ascend::game
