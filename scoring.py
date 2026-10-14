"""
scoring.py
Stage Time v4 - deterministic rubrics

Every score here is arithmetic with a stated reason attached. The LLM grades
only content, structure, directness and premise handling. It never overrides
a number computed in this file, and a cap that the model asks for is only
applied when a deterministic marker or a known ground truth corroborates it.

Main session rubric, 100 points:
  pace 20, fluency 25, completion 15, variety 10, volume 15, steadiness 15

Components that could not be measured are dropped from the denominator,
never scored zero, and the notes say so. Steadiness defaults to full marks
and only deducts against a calibrated baseline.
"""

from __future__ import annotations

from typing import Any, Optional


def clamp(v: Any, lo: int, hi: int, default: int = 0) -> int:
    """Models return numbers as strings, floats, or not at all."""
    try:
        n = int(round(float(v)))
    except (TypeError, ValueError):
        return default
    return max(lo, min(hi, n))


def _band(value: float, lo: float, hi: float, points: int,
          falloff: float) -> tuple[int, Optional[str]]:
    """Full points inside the band, linear falloff outside it."""
    if lo <= value <= hi:
        return points, None
    dist = (lo - value) if value < lo else (value - hi)
    lost = min(points, round(dist / falloff * points))
    side = "under" if value < lo else "over"
    return points - lost, side


def _total(parts: dict[str, int], maxes: dict[str, int]) -> tuple[int, int, int]:
    earned = sum(parts.values())
    possible = sum(maxes.values()) or 1
    return max(0, min(100, round(earned / possible * 100))), earned, possible


# ----------------------------------------------------------------------
# Main session score
# ----------------------------------------------------------------------

def session_score(text_m: dict, acoustics: Optional[dict], target_s: float,
                  level: int = 1, tolerance: Optional[float] = None) -> dict:
    notes: list[str] = []
    parts: dict[str, int] = {}
    caps = {"pace": 20, "fluency": 25, "completion": 15,
            "variety": 10, "volume": 15, "steadiness": 15}
    if tolerance is None:
        tolerance = max(1.0, 4.0 - 0.5 * (level - 1))

    has_text = text_m["pace"]["word_count"] > 0

    if has_text:
        # Pace, 20. Target 130 to 150 WPM.
        wpm = text_m["pace"]["wpm"]
        pts, side = _band(wpm, 130, 150, 20, 60)
        parts["pace"] = pts
        if side == "under":
            notes.append(f"{wpm:.0f} WPM is slow. Target is 130 to 150.")
        elif side == "over":
            notes.append(f"{wpm:.0f} WPM is fast. Replace rushing with pauses.")

        # Fluency, 25. Tolerance tightens as levels rise.
        pct = text_m["fillers"]["pct"]
        if pct <= tolerance:
            parts["fluency"] = 25
        else:
            over = pct - tolerance
            parts["fluency"] = max(0, 25 - round(over * 6))
            top = list(text_m["fillers"]["counts"])[:3]
            notes.append(
                f"Fillers at {pct:.1f} percent against a {tolerance:.1f} limit"
                + (f". Most used: {', '.join(top)}." if top else ".")
            )

        # Variety, 10.
        uwr = text_m["variety"]["unique_word_ratio"]
        parts["variety"] = 10 if uwr >= 0.55 else max(0, round(uwr / 0.55 * 10))
    else:
        for k in ("pace", "fluency", "variety"):
            caps.pop(k)
        notes.append("Transcription is off, so pace, fillers and word choice were "
                     "not measured. The score is out of what was measured.")

    # Completion, 15. Duration is known from the recording even without a
    # transcript.
    dur = text_m["pace"]["duration_s"]
    if target_s > 0:
        ratio = dur / target_s
        pts, side = _band(ratio, 0.8, 1.2, 15, 0.5)
        parts["completion"] = pts
        if side == "under":
            notes.append(f"Ran {dur:.0f}s against a {target_s:.0f}s target.")
        elif side == "over":
            notes.append(f"Ran long at {dur:.0f}s against {target_s:.0f}s.")
    else:
        parts["completion"] = 15

    # Volume, 15.
    vs = (acoustics or {}).get("volume_score", {}).get("score")
    if vs is None:
        caps.pop("volume")
        notes.append("Volume not measured: acoustics off, or audio too quiet or too short.")
    else:
        parts["volume"] = round(vs / 100 * 15)
        notes.extend((acoustics or {})["volume_score"].get("notes", []))

    # Steadiness, 15. Full marks unless a baseline exists and votes cross.
    cmp_ = (acoustics or {}).get("baseline_comparison")
    if not cmp_:
        parts["steadiness"] = 15
    else:
        votes = cmp_.get("unsteady_votes", 0)
        parts["steadiness"] = {0: 15, 1: 15, 2: 11, 3: 7, 4: 4}.get(votes, 15)
        notes.extend(cmp_.get("flags", []))

    parts = {k: v for k, v in parts.items() if k in caps}
    total, earned, possible = _total(parts, caps)
    return {
        "total": total,
        "raw": earned,
        "possible": possible,
        "parts": parts,
        "max": caps,
        "notes": notes,
        "unscored": False,
        "filler_tolerance_pct": tolerance,
    }


# ----------------------------------------------------------------------
# Q&A, deterministic parts
# ----------------------------------------------------------------------

def qa_deterministic(text_m: dict, latency_s: Optional[float]) -> dict:
    """Concision 15, composure 20, language confidence 20. The remaining 45
    points, directness and structure, come from the model."""
    notes: list[str] = []

    n = text_m["pace"]["word_count"]
    dur = text_m["pace"]["duration_s"]
    w_pts, w_side = _band(n, 60, 150, 8, 60)
    d_pts, _ = _band(dur, 25, 60, 7, 30)
    concision = w_pts + d_pts
    if w_side == "over":
        notes.append(f"{n} words. Under 150 lands harder.")
    elif w_side == "under":
        notes.append(f"{n} words is thin. Add one example.")

    composure = 20
    if latency_s is None:
        pass
    elif latency_s < 0.5:
        composure -= 8
        notes.append("You started before the question finished. Take the beat.")
    elif latency_s < 1.0:
        composure -= 3
        notes.append("Quick off the mark. One to two seconds reads as considered.")
    elif latency_s > 4.0:
        composure -= 5
        notes.append("Long gap before answering. Over four seconds reads as stuck.")

    hedge = text_m["hedges"]["per_100w"]
    filler = text_m["fillers"]["pct"]
    lang = 20
    if hedge > 2.5:
        lang -= min(12, round((hedge - 2.5) * 3))
        top = list(text_m["hedges"]["counts"])[:3]
        notes.append(
            f"Hedge density {hedge:.1f} per 100 words"
            + (f", mostly {', '.join(top)}." if top else ".")
        )
    if filler > 2.0:
        lang -= min(8, round((filler - 2.0) * 3))

    return {
        "concision_0_15": max(0, concision),
        "composure_0_20": max(0, composure),
        "language_0_20": max(0, lang),
        "notes": notes,
    }


def structure_points(coverage: Any, in_order: Any = True, max_pts: int = 20) -> int:
    """The model rates each framework step 0 (absent), 1 (partial), 2 (clear)."""
    if not isinstance(coverage, list) or not coverage:
        return 0
    vals = [clamp(c, 0, 2) for c in coverage]
    raw = sum(vals) / (2 * len(vals))
    pts = round(raw * max_pts)
    if in_order is False and pts > 0:
        pts = max(0, pts - 4)
    return pts


def _signpost_note(text_m: dict) -> Optional[str]:
    sp = text_m.get("signposts")
    if sp and sp.get("found"):
        return "Heard: " + ", ".join(sp["found"][:4]) + "."
    return None


def _missing_steps(framework: Optional[dict], coverage: Any) -> list[str]:
    if not framework or not isinstance(coverage, list):
        return []
    steps = framework["steps"]
    return [steps[i]["label"] for i, c in enumerate(coverage[:len(steps)])
            if clamp(c, 0, 2) == 0]


def _structure_blend(llm: dict, text_m: dict) -> int:
    """Model coverage (60 percent) blended with the signposts actually heard
    (40 percent). A small model's step judgement wobbles; the signposts do not."""
    model_pts = structure_points(llm["coverage"], llm.get("in_order", True))
    sp = text_m.get("signposts") or {}
    if sp.get("ratio") is None:
        return model_pts
    return round(0.6 * model_pts + 0.4 * sp["ratio"] * 20)


def answer_score(det: dict, llm: Optional[dict], text_m: dict,
                 framework: Optional[dict]) -> dict:
    """Fair question. Directness 25 and structure 20 come from the model; when
    it is off, structure falls back to signposts and the total is scaled."""
    parts = {"concision": det["concision_0_15"], "composure": det["composure_0_20"],
             "language": det["language_0_20"]}
    maxes = {"concision": 15, "composure": 20, "language": 20}
    notes = list(det["notes"])
    sp = text_m.get("signposts") or {}

    if llm:
        parts["directness"] = clamp(llm.get("directness_0_25"), 0, 25)
        maxes["directness"] = 25
        if framework and isinstance(llm.get("coverage"), list):
            parts["structure"] = _structure_blend(llm, text_m)
            missing = _missing_steps(framework, llm["coverage"])
            if missing:
                notes.append(f"The grader did not hear these {framework['name']} steps: "
                             f"{', '.join(missing)}.")
        else:
            parts["structure"] = clamp(llm.get("structure_0_20"), 0, 20)
        maxes["structure"] = 20
        if llm.get("dodge_detected"):
            notes.append("Read as a dodge: no substantive answer in the first two sentences.")
    else:
        if framework and sp.get("ratio") is not None:
            parts["structure"] = round(sp["ratio"] * 20)
            maxes["structure"] = 20
            notes.append(f"Structure estimated from signposts only: {len(sp['found'])} "
                         f"of {sp['expected']} heard. The model is offline.")
        notes.append("Directness not graded: the model is offline.")

    heard = _signpost_note(text_m)
    if heard:
        notes.append(heard)
    total, earned, possible = _total(parts, maxes)
    return {"total": total, "parts": parts, "max": maxes, "notes": notes,
            "possible": possible}


# ----------------------------------------------------------------------
# Q&A, hostile turn
# ----------------------------------------------------------------------

def escalation_delta(hostile: dict, baseline_turns: list[dict]) -> Optional[dict]:
    """Compare a hostile turn against this speaker's own earlier turns in the
    same session. Same microphone, same room, minutes apart."""
    if not baseline_turns:
        return None

    def get(turn: dict, path: tuple[str, ...]) -> Optional[float]:
        node: Any = turn
        for p in path:
            node = node.get(p) if isinstance(node, dict) else None
        return float(node) if isinstance(node, (int, float)) else None

    def mean(path: tuple[str, ...]) -> Optional[float]:
        vals = [v for v in (get(t, path) for t in baseline_turns) if v is not None]
        return sum(vals) / len(vals) if vals else None

    paths = {
        "volume_db": ("acoustics", "volume", "median_db"),
        "pitch_pct": ("acoustics", "pitch", "median_hz"),
        "wpm_pct": ("text", "pace", "wpm"),
    }

    out: dict[str, float] = {}
    for name, path in paths.items():
        now = get(hostile, path)
        was = mean(path)
        if now is None or was is None or was == 0:
            continue
        if name == "volume_db":
            out[name] = round(now - was, 2)
        else:
            out[name] = round((now - was) / abs(was) * 100, 1)

    if not out:
        return None

    took_bait = sum([
        out.get("volume_db", 0) > 3.0,
        out.get("pitch_pct", 0) > 8.0,
        out.get("wpm_pct", 0) > 12.0,
    ]) >= 3

    return {"delta": out, "took_the_bait": took_bait}


def hostile_deterministic(text_m: dict, latency_s: Optional[float],
                          esc: Optional[dict]) -> dict:
    """Composure is 30 of the 100 on a hostile turn. Premise handling,
    substance and structure come from the model."""
    notes: list[str] = []
    composure = 30

    if esc and esc.get("took_the_bait"):
        composure -= 14
        d = esc["delta"]
        notes.append(
            "You matched their energy: volume up "
            f"{d.get('volume_db', 0):.1f} dB, pitch up "
            f"{d.get('pitch_pct', 0):.0f} percent, pace up "
            f"{d.get('wpm_pct', 0):.0f} percent."
        )
    elif esc:
        d = esc["delta"]
        if d.get("volume_db", 0) > 3.0:
            composure -= 5
            notes.append("Volume rose. Hold it level, do not match theirs.")
        if d.get("wpm_pct", 0) > 12.0:
            composure -= 5
            notes.append("You sped up. Slow about 10 percent under pressure.")

    if latency_s is not None and latency_s < 0.5:
        composure -= 6
        notes.append("No beat before answering. Under attack the pause matters most.")

    marks = text_m.get("counterattack", {}).get("markers", [])
    if marks:
        notes.append(f"Counterattack language in your opening: {', '.join(marks)}.")

    return {
        "composure_0_30": max(0, composure),
        "counterattack_markers": marks,
        "credentials_defended": bool(text_m.get("credentials_defended", False)),
        "notes": notes,
    }


def apply_hostile_caps(llm: dict, det: dict, truth: Optional[str] = None) -> dict:
    """Caps override the model's generosity, but the model's own flags need
    corroboration before they cost anything serious.
      truth: 'loaded', 'clean' or None when the question came from the model."""
    premise = clamp(llm.get("premise_0_25"), 0, 25)
    substance = clamp(llm.get("substance_0_25"), 0, 25)
    composure = det["composure_0_30"]
    capped: list[str] = []
    notes: list[str] = []

    if llm.get("returned_personal_attack"):
        if det.get("counterattack_markers"):
            composure = min(composure, 5)
            capped.append("Personal attack returned: composure capped at 5.")
        else:
            composure = max(0, composure - 5)
            notes.append("The grader read this as returning the attack. No counterattack "
                         "phrases were heard, so only a light deduction applies.")

    if det.get("credentials_defended"):
        substance = min(substance, 10)
        capped.append("Credentials defended instead of evidence: substance capped at 10.")

    if llm.get("premise_accepted_wrongly"):
        if truth == "loaded":
            premise = 0
            capped.append("A false premise was accepted: premise handling scores 0.")
        elif truth is None:
            premise = premise // 2
            notes.append("The grader thought a premise was accepted. The question came "
                         "from the model, so the premise cannot be verified: half marks.")

    return {"composure_0_30": composure, "premise_0_25": premise,
            "substance_0_25": substance, "caps_applied": capped, "notes": notes}


def hostile_score(det: dict, llm: Optional[dict], text_m: dict,
                  framework: Optional[dict], truth: Optional[str] = None) -> dict:
    """Composure 30, premise 25, substance 25, structure 20 (framework coverage
    when a framework was set, else the model's close mark)."""
    parts = {"composure": det["composure_0_30"]}
    maxes = {"composure": 30}
    notes = list(det["notes"])
    caps_applied: list[str] = []

    if llm:
        adj = apply_hostile_caps(llm, det, truth)
        parts["composure"] = adj["composure_0_30"]
        parts["premise"] = adj["premise_0_25"]
        parts["substance"] = adj["substance_0_25"]
        maxes.update({"premise": 25, "substance": 25})
        caps_applied = adj["caps_applied"]
        notes.extend(adj["notes"])
        # The model is generous about premises. If the question is known to be
        # loaded and no premise-naming phrase was heard, it was swallowed.
        if truth == "loaded" and not text_m.get("premise_addressed"):
            parts["premise"] = min(parts["premise"], 10)
            notes.append("The false premise was never named. Say what the question "
                         "assumes before you answer it.")
        if framework and isinstance(llm.get("coverage"), list):
            parts["structure"] = _structure_blend(llm, text_m)
            missing = _missing_steps(framework, llm["coverage"])
            if missing:
                notes.append(f"The grader did not hear these {framework['name']} steps: "
                             f"{', '.join(missing)}.")
        else:
            parts["structure"] = clamp(llm.get("close_0_20"), 0, 20)
        maxes["structure"] = 20
    else:
        if det.get("credentials_defended"):
            caps_applied.append("Credentials defended instead of evidence.")
        sp = text_m.get("signposts") or {}
        if framework and sp.get("ratio") is not None:
            parts["structure"] = round(sp["ratio"] * 20)
            maxes["structure"] = 20
            notes.append(f"Structure estimated from signposts only: {len(sp['found'])} "
                         f"of {sp['expected']} heard. The model is offline.")
        notes.append("Premise handling and substance not graded: the model is offline.")

    heard = _signpost_note(text_m)
    if heard:
        notes.append(heard)
    total, earned, possible = _total(parts, maxes)
    return {"total": total, "parts": parts, "max": maxes, "notes": notes,
            "caps_applied": caps_applied, "possible": possible}


# ----------------------------------------------------------------------
# Drill modes: paraphrase, classify, gap, ask, comprehend
# ----------------------------------------------------------------------

def paraphrase_score(text_m: dict, markers: dict, llm: Optional[dict]) -> dict:
    """Neutralise it: restate the question without tone, and do not answer."""
    parts: dict[str, int] = {}
    maxes = {"kept_content": 30, "no_counterattack": 15, "brevity": 15,
             "did_not_answer": 10, "clean_delivery": 5}
    notes: list[str] = []

    echo = text_m.get("question_echo", {})
    kept = bool(echo.get("echoed")) or bool(llm and llm.get("kept_the_real_question"))
    parts["kept_content"] = 30 if kept else (15 if echo.get("overlap_terms") else 0)
    if not kept:
        notes.append("The restatement lost the question. Keep their nouns, drop their "
                     "adjectives.")
    marks = text_m.get("counterattack", {}).get("markers", [])
    parts["no_counterattack"] = 0 if marks else 15
    if marks:
        notes.append(f"Counterattack language: {', '.join(marks)}.")
    n = text_m["pace"]["word_count"]
    parts["brevity"] = 15 if n <= 35 else max(0, 15 - (n - 35) // 3)
    if n > 35:
        notes.append(f"{n} words. A neutral restatement is one sentence.")
    parts["did_not_answer"] = 0 if markers.get("answered") else 10
    if markers.get("answered"):
        notes.append("You answered it. This drill is only the restatement.")
    parts["clean_delivery"] = 5 if text_m["fillers"]["pct"] <= 2.0 else 0

    if llm:
        parts["neutral_tone"] = clamp(llm.get("neutral_restatement_0_25"), 0, 25)
        maxes["neutral_tone"] = 25
        if llm.get("added_argument"):
            notes.append("The grader heard an argument creeping into the restatement.")
    else:
        notes.append("Tone not graded: the model is offline.")

    total, earned, possible = _total(parts, maxes)
    return {"total": total, "parts": parts, "max": maxes, "notes": notes,
            "possible": possible}


def classify_score(cls: dict, truth_loaded: Optional[bool],
                   llm: Optional[dict]) -> dict:
    """Spot the premise: correct call both ways, then the reason."""
    parts: dict[str, int] = {}
    maxes: dict[str, int] = {"call": 70}
    notes: list[str] = []
    said = cls.get("said")
    if said is None:
        parts["call"] = 0
        notes.append("Start with the word 'loaded' or 'clean'. The call was not heard.")
        return {"total": 0, "parts": parts, "max": maxes, "notes": notes, "possible": 70,
                "said": said}
    correct = (said == "loaded") == bool(truth_loaded)
    parts["call"] = 70 if correct else 0
    if not correct:
        notes.append("Wrong call. " + ("There was no false premise in that one; "
                                       "manufacturing a grievance is also a fail."
                                       if not truth_loaded else
                                       "That question carried a false premise."))
        return {"total": 0, "parts": parts, "max": maxes, "notes": notes, "possible": 70,
                "said": said}
    if truth_loaded:
        parts["reason"] = 10 if cls.get("has_reason") else 0
        maxes["reason"] = 10
        if not cls.get("has_reason"):
            notes.append("Say 'loaded, because' and name the assumption.")
        if llm:
            parts["named_premise"] = clamp(llm.get("named_actual_premise_0_20"), 0, 20)
            maxes["named_premise"] = 20
        else:
            notes.append("Whether you named the right premise was not graded: model offline.")
    else:
        parts["restraint"] = 30
        maxes["restraint"] = 30
    total, earned, possible = _total(parts, maxes)
    return {"total": total, "parts": parts, "max": maxes, "notes": notes,
            "possible": possible, "said": said}


def gap_score(gap: dict, llm: Optional[dict]) -> dict:
    """Say what you do not know: clean admission, commitment, no guess."""
    parts: dict[str, int] = {}
    maxes = {"admission": 35, "commitment": 25, "no_apology": 10}
    notes: list[str] = []
    if gap.get("guessed") and not gap.get("admitted"):
        notes.append("That was a guess. Guessing scores zero; one follow-up would expose it.")
        return {"total": 0, "parts": {"admission": 0}, "max": maxes, "notes": notes,
                "possible": 70}
    parts["admission"] = 35 if gap.get("admitted") else 0
    if not gap.get("admitted"):
        notes.append("No clean admission heard. 'I do not have that in front of me' is enough.")
    if gap.get("guessed"):
        parts["admission"] = max(0, parts["admission"] - 20)
        notes.append("You admitted the gap and then guessed anyway. Stop after the admission.")
    parts["commitment"] = 25 if gap.get("committed") else 0
    if not gap.get("committed"):
        notes.append("No commitment heard. Say what you will send, by when, and how.")
    parts["no_apology"] = 0 if gap.get("apologised") else 10
    if gap.get("apologised"):
        notes.append("No apology needed. Not knowing a figure is not a fault.")
    if llm:
        parts["answered_what_you_could"] = clamp(llm.get("answered_what_they_could_0_30"), 0, 30)
        maxes["answered_what_you_could"] = 30
    else:
        notes.append("Whether you answered the part you could was not graded: model offline.")
    total, earned, possible = _total(parts, maxes)
    return {"total": total, "parts": parts, "max": maxes, "notes": notes,
            "possible": possible}


def ask_score(ask: dict, text_m: dict, llm: Optional[dict]) -> dict:
    """Ask cleanly: ask what it means, name it, do not apologise, do not hedge."""
    parts: dict[str, int] = {}
    maxes = {"asked": 40, "named_it": 10, "no_apology": 15, "is_question": 5,
             "no_hedging": 10}
    notes: list[str] = []
    parts["asked"] = 40 if ask.get("asked") else 0
    if not ask.get("asked"):
        notes.append("No question heard. 'What do you mean by that?' is the whole drill.")
    parts["named_it"] = 10 if ask.get("term_named") else 0
    if not ask.get("term_named"):
        notes.append("Name the term you are asking about. It shows you were listening.")
    parts["no_apology"] = 0 if ask.get("apologised") else 15
    if ask.get("apologised"):
        notes.append("Never open with sorry. It is not an apology, it is a question.")
    parts["is_question"] = 5 if ask.get("is_question") else 0
    hedge = text_m["hedges"]["per_100w"]
    parts["no_hedging"] = 10 if hedge <= 2.5 else max(0, 10 - round(hedge - 2.5))
    if hedge > 2.5:
        notes.append("Hedges crept in. The strongest version offers a guess at the meaning.")
    if llm:
        parts["direct_and_specific"] = clamp(llm.get("direct_and_specific_0_20"), 0, 20)
        maxes["direct_and_specific"] = 20
    else:
        notes.append("Directness of the question not graded: model offline.")
    total, earned, possible = _total(parts, maxes)
    return {"total": total, "parts": parts, "max": maxes, "notes": notes,
            "possible": possible}


COMPREHEND_POINTS = {
    "understood_and_answered": 100,
    "asked_then_answered": 100,
    "asked_only": 70,
    "understood_partially": 60,
    "dodged": 20,
    "guessed_wrong": 0,
}


def comprehend_score(ask: dict, llm: Optional[dict]) -> dict:
    """The bank meeting: understood and answered, or asked and then answered,
    both score full marks. Guessing wrong is the only fail."""
    notes: list[str] = []
    if llm and llm.get("outcome") in COMPREHEND_POINTS:
        outcome = llm["outcome"]
        pts = COMPREHEND_POINTS[outcome]
        if ask.get("asked") and pts < 70:
            pts = 70
            outcome = "asked_only"
        notes.append({"understood_and_answered": "You understood the shorthand and answered.",
                      "asked_then_answered": "You asked what it meant, then answered. Full marks.",
                      "asked_only": "You asked, which is right. Then answer the rest.",
                      "understood_partially": "Part of the shorthand was understood.",
                      "dodged": "Neither answered nor asked. Ask.",
                      "guessed_wrong": "You guessed the meaning and guessed wrong. Asking would have cost nothing."}[outcome])
        return {"total": pts, "outcome": outcome, "notes": notes, "possible": 100}
    if ask.get("asked"):
        notes.append("You asked what it meant. Comprehension not graded: model offline.")
        return {"total": 70, "outcome": "asked_only", "notes": notes, "possible": 100}
    notes.append("Comprehension needs the model, which is offline.")
    return {"total": None, "outcome": None, "notes": notes, "possible": 0}


# ----------------------------------------------------------------------
# Series summaries
# ----------------------------------------------------------------------

def series_summary(series: Optional[str], turns: list[dict]) -> dict:
    """turns: [{"score": {...}, "text": {...}, "acoustics": {...}}, ...]"""
    totals = [t.get("score", {}).get("total") for t in turns]
    totals = [x for x in totals if isinstance(x, (int, float))]
    mean = round(sum(totals) / len(totals)) if totals else None
    notes: list[str] = []
    series_score: Optional[int] = None

    if series == "escalate" and len(turns) >= 2:
        base = turns[0]
        held = 0
        judged = 0
        for t in turns[1:]:
            d = escalation_delta(t, [base])
            if not d:
                continue
            judged += 1
            delta = d["delta"]
            breaches = sum([delta.get("volume_db", 0) > 2.0,
                            delta.get("pitch_pct", 0) > 5.0,
                            delta.get("wpm_pct", 0) > 10.0])
            held += max(0, 3 - breaches) / 3
        if judged:
            series_score = round(held / judged * 100)
            notes.append("Escalation delta across turns: "
                         + ("flat. Calm is contagious." if series_score >= 80 else
                            "your voice followed theirs. Hold volume within 2 dB, pitch at "
                            "baseline, pace ten percent slower."))
        else:
            notes.append("Escalation delta needs acoustics or a transcript on every turn.")

    elif series == "return" and len(turns) >= 2:
        counts = [t.get("text", {}).get("pace", {}).get("word_count", 0) for t in turns]
        shrinking = sum(1 for a, b in zip(counts, counts[1:]) if b < a)
        series_score = round(shrinking / (len(counts) - 1) * 100)
        notes.append(f"Answer lengths: {', '.join(str(c) for c in counts)} words. "
                     + ("Each reply shorter than the last. You did not renegotiate."
                        if shrinking == len(counts) - 1 else
                        "Replies should shrink on each return. Reopening the topic is the trap."))

    return {"mean": mean, "series_score": series_score, "notes": notes}


# ----------------------------------------------------------------------
# Jargon score
# ----------------------------------------------------------------------

def jargon_score(j: dict) -> dict:
    """Technical language is never penalised. Figurative language scores
    harshly for an international audience and lightly for a US internal one."""
    d = j["density_per_100w"]
    audience = j.get("audience", "us_internal")
    score, notes = 100, []

    corp = d.get("corporate", 0.0)
    if corp > 2.0:
        score -= min(30, round((corp - 2.0) * 10))
        hits = j.get("corporate_hits", [])[:2]
        for h in hits:
            if h.get("plain"):
                notes.append(
                    f"'{h['term']}' used {h['count']} time"
                    f"{'s' if h['count'] > 1 else ''}. '{h['plain']}' is shorter "
                    "and reads stronger."
                )

    fig = d.get("figurative", 0.0)
    if audience == "international":
        if fig > 0:
            score -= min(35, round(fig * 15))
            terms = [h["term"] for h in j.get("figurative_hits", [])[:3]]
            if terms:
                notes.append(
                    "Figurative language on an international call: "
                    f"{', '.join(terms)}. These do not travel."
                )
    elif fig > 2.0:
        score -= min(15, round((fig - 2.0) * 6))

    for h in j.get("flagged_hits", []):
        score -= 10
        risk = h.get("risk") or h.get("subtext") or "ambiguous"
        notes.append(f"'{h['term']}': {risk}")

    swaps = j.get("latinate", {}).get("suggested_swaps", {})
    if swaps:
        pairs = ", ".join(f"{k} to {v}" for k, v in list(swaps.items())[:3])
        notes.append(f"Plainer options: {pairs}.")

    return {"score": max(0, min(100, score)), "notes": notes}
