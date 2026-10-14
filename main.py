"""
main.py
Stage Time v4 - local FastAPI backend

Runs entirely on one laptop. Nothing leaves the machine.
  Transcription  faster-whisper, small, int8, CPU
  Language       Ollama, qwen2.5:3b or whatever is pulled
  Speech         Kokoro-82M, or the browser's own voices when Kokoro is off
  Acoustics      praat-parselmouth

Every one of those is optional. If a service is missing the app degrades to
the deterministic scoring, the built in question bank and the browser's
voices, and /health tells the frontend what to grey out.

Handlers are plain functions on purpose: FastAPI runs them in a thread pool,
so a fifteen second model call never stalls the rest of the app.

Run:  uvicorn main:app --port 8000
"""

from __future__ import annotations

import json
import os
import random
import re
import shutil
import subprocess
import tempfile
import threading
import time
import uuid
from typing import Any, Optional

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

import content
import course
import frameworks as fw
import questions as qs
import scoring
import text_metrics as tm

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
os.makedirs(DATA, exist_ok=True)
TMP = os.path.join(tempfile.gettempdir(), "stage-time")
os.makedirs(TMP, exist_ok=True)

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:3b")
WHISPER_SIZE = os.environ.get("WHISPER_SIZE", "small")
# A prompt seeded with disfluencies keeps Whisper from tidying them away.
WHISPER_PROMPT = "Um, so, uh, I mean, like, you know... hmm, okay so, basically, er."

VERSION = "4.0"

app = FastAPI(title="Stage Time", version=VERSION)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://(127\.0\.0\.1|localhost)(:\d+)?$",
    allow_origins=["null"],
    allow_methods=["*"], allow_headers=["*"],
)

BANK = tm.JargonBank(os.path.join(HERE, "jargon-bank-seed.json"))

# Talking-head sprites cut by build_avatars.py. Optional: without the folder
# the roleplay shows initials instead of faces.
AVATARS = os.path.join(HERE, "avatars")
if os.path.isdir(AVATARS):
    app.mount("/avatars", StaticFiles(directory=AVATARS), name="avatars")


def _avatar_manifest() -> Optional[dict]:
    try:
        with open(os.path.join(AVATARS, "manifest.json"), encoding="utf-8") as fh:
            m = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None
    # Generated video loops (build_avatar_video.py) sit beside the stills; the big tiles play them.
    for actor, spec in (m.get("actors") or {}).items():
        d = os.path.join(AVATARS, actor)
        if os.path.exists(os.path.join(d, "idle.mp4")):
            # until the talking loop exists the listening loop stands in for it
            talk = "talk.mp4" if os.path.exists(os.path.join(d, "talk.mp4")) else "idle.mp4"
            spec["video"] = {"idle": "idle.mp4", "talk": talk}
    return m


# ----------------------------------------------------------------------
# Storage: plain JSON files. One user, one laptop.
# ----------------------------------------------------------------------

_io_lock = threading.Lock()


def _path(name: str) -> str:
    return os.path.join(DATA, name)


def load(name: str, default: Any) -> Any:
    try:
        with open(_path(name), encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save(name: str, obj: Any) -> None:
    with _io_lock:
        tmp = _path(name + ".tmp")
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, indent=2, ensure_ascii=False)
        os.replace(tmp, _path(name))


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def _level_for(n_sessions: int) -> int:
    level = 1
    for lv in content.LEVELS:
        if n_sessions >= lv["unlock_sessions"]:
            level = lv["lvl"]
    return level


def _tolerance_for(level: int) -> float:
    for lv in content.LEVELS:
        if lv["lvl"] == level:
            return float(lv["filler_tolerance"])
    return 4.0


def _scored_sessions(sessions: list[dict]) -> list[dict]:
    return [s for s in sessions if (s.get("score") or {}).get("total") is not None]


# Personal bank entries and spaced repetition state live in data/ and are
# folded into the seed bank at startup so detection and review see them.
for _e in load("bank_personal.json", []):
    if _e.get("term") and _e.get("category"):
        BANK.add(_e)
for _term, _srs in load("srs_seed.json", {}).items():
    if _term in BANK.entries:
        BANK.entries[_term]["srs"] = _srs


# ----------------------------------------------------------------------
# Optional services. Heavy models load in a background thread at startup so
# the first page load never waits on a download.
# ----------------------------------------------------------------------

_svc: dict[str, Any] = {"whisper": None, "kokoro": None, "acoustics": None}
_state: dict[str, str] = {"asr": "off", "tts": "off", "acoustics": "off"}
_errors: dict[str, str] = {}
_whisper_lock = threading.Lock()
_kokoro_lock = threading.Lock()


def _warm_up() -> None:
    try:
        import voice_metrics
        _svc["acoustics"] = voice_metrics
        _state["acoustics"] = "on"
    except Exception as exc:
        _state["acoustics"] = "off"
        _errors["acoustics"] = f"{type(exc).__name__}: {exc}"[:300]

    _state["asr"] = "loading"
    try:
        from faster_whisper import WhisperModel
        _svc["whisper"] = WhisperModel(WHISPER_SIZE, device="cpu", compute_type="int8")
        _state["asr"] = "on"
    except Exception as exc:
        _state["asr"] = "off"
        _errors["asr"] = f"{type(exc).__name__}: {exc}"[:300]

    _state["tts"] = "loading"
    try:
        from kokoro import KPipeline
        pipe = KPipeline(lang_code="a")
        with _kokoro_lock:
            for v in ("af_heart", "am_michael"):      # the two characters' voices
                for _ in pipe("Ready.", voice=v):
                    pass
        _svc["kokoro"] = pipe
        _state["tts"] = "on"
    except Exception as exc:
        _state["tts"] = "off"
        _errors["tts"] = f"{type(exc).__name__}: {exc}"[:300]


threading.Thread(target=_warm_up, name="stage-time-warm-up", daemon=True).start()


def acoustics_mod():
    return _svc["acoustics"]


_ollama_cache: dict[str, Any] = {"at": 0.0, "up": False}


def ollama_up() -> bool:
    if time.time() - _ollama_cache["at"] < 10:
        return bool(_ollama_cache["up"])
    up = False
    try:
        import httpx
        up = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=3).status_code == 200
    except Exception:
        up = False
    _ollama_cache.update({"at": time.time(), "up": up})
    return up


def _coerce(obj: Any, schema: dict) -> dict:
    """Make a model reply match its schema: numbers clamped to their range,
    booleans real booleans, enums valid, arrays of small ints, missing keys
    filled. Ollama enforces the shape; this enforces the types."""
    out: dict[str, Any] = {}
    if not isinstance(obj, dict):
        obj = {}
    for key, spec in schema.get("properties", {}).items():
        v = obj.get(key)
        t = spec.get("type")
        if t == "integer" or t == "number":
            out[key] = scoring.clamp(v, spec.get("minimum", 0), spec.get("maximum", 100),
                                     default=spec.get("minimum", 0))
        elif t == "boolean":
            out[key] = (v is True) or (isinstance(v, str) and v.lower() == "true")
        elif t == "array":
            items = spec.get("items", {})
            if not isinstance(v, list):
                v = []
            if items.get("type") == "integer":
                out[key] = [scoring.clamp(x, items.get("minimum", 0), items.get("maximum", 2))
                            for x in v]
            else:
                out[key] = [str(x) for x in v]
        else:
            if "enum" in spec:
                out[key] = v if v in spec["enum"] else spec["enum"][-1]
            else:
                s = ("" if v is None else str(v)).strip()
                # A small model sometimes echoes the length instruction or
                # emits a stray token instead of advice. Drop those.
                if key.endswith("fix") or key in ("better_opening", "what_they_should_have_said"):
                    if len(s.split()) < 3 or s.lower().startswith("at most"):
                        s = ""
                out[key] = s
    return out


def _salvage(text: str) -> Optional[dict]:
    """A small model can run past its token budget inside a string field,
    which leaves the JSON unterminated. Cut back to the last complete pair.
    Schemas list numbers and arrays before prose so nothing scored is lost."""
    start = text.find("{")
    if start == -1:
        return None
    body = text[start:]
    i = body.rfind(",")
    while i > 0:
        try:
            out = json.loads(body[:i] + "}")
            return out if isinstance(out, dict) else None
        except ValueError:
            i = body.rfind(",", 0, i)
    return None


def ollama_chat(messages: list[dict], schema: Optional[dict] = None,
                temperature: float = 0.2, timeout: int = 120,
                num_predict: int = 700) -> Optional[Any]:
    """One call to the local model. With a schema the reply is constrained to
    valid JSON of that shape and returned as a coerced dict. Without one the
    raw text comes back. None means the model is unavailable or failed."""
    try:
        import httpx
    except Exception:
        return None
    options: dict[str, Any] = {"temperature": temperature, "num_predict": num_predict}
    if temperature <= 0.1:
        options["seed"] = 7      # grading: the same answer always gets the same marks
    body: dict[str, Any] = {
        "model": OLLAMA_MODEL, "messages": messages, "stream": False,
        "options": options, "keep_alive": "30m",
    }
    if schema is not None:
        body["format"] = schema
    for attempt in range(2):
        try:
            r = httpx.post(f"{OLLAMA_URL}/api/chat", json=body, timeout=timeout)
            if r.status_code >= 400 and schema is not None and attempt == 0:
                body["format"] = "json"      # older servers: plain JSON mode
                continue
            r.raise_for_status()
            text = (r.json().get("message") or {}).get("content", "")
        except Exception:
            return None
        if schema is None:
            return text
        text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE)
        start, end = text.find("{"), text.rfind("}")
        try:
            return _coerce(json.loads(text[start:end + 1]), schema)
        except (ValueError, json.JSONDecodeError):
            saved = _salvage(text)
            if saved is not None:
                return _coerce(saved, schema)
            if attempt == 0:
                continue
            return None
    return None


def _schema(props: dict, required: Optional[list[str]] = None) -> dict:
    return {"type": "object", "properties": props,
            "required": required or list(props)}


def _int(lo: int, hi: int) -> dict:
    return {"type": "integer", "minimum": lo, "maximum": hi}


def _coverage(n: int) -> dict:
    return {"type": "array", "items": _int(0, 2), "minItems": n, "maxItems": n}


# ----------------------------------------------------------------------
# Health and content
# ----------------------------------------------------------------------

@app.get("/health")
def health() -> dict:
    return {
        "ok": True,
        "version": VERSION,
        "asr": _state["asr"] == "on",
        "llm": ollama_up(),
        "tts": _state["tts"] == "on",
        "acoustics": _state["acoustics"] == "on",
        "loading": {"asr": _state["asr"] == "loading", "tts": _state["tts"] == "loading"},
        "errors": _errors,
        "model": OLLAMA_MODEL,
        "bank_terms": len(BANK.terms),
        "questions": len(qs.QUESTIONS),
        "frameworks": len(fw.FRAMEWORKS),
    }


def _exercises() -> list[dict]:
    out = []
    for e in content.EXERCISES:
        flow = qs.DRILL_FLOWS.get(e["id"], {"flow": "record"})
        out.append({**e, **flow})
    for g in load("generated_drills.json", []):
        out.append({**g, "flow": "record", "source": "generated"})
    return out


@app.get("/content")
def get_content() -> dict:
    return {
        "levels": content.LEVELS,
        "exercises": _exercises(),
        "lessons": content.LESSONS,
        "personas": content.PERSONAS,
        "scenarios": content.SCENARIOS,
        "frameworks": fw.FRAMEWORKS,
        "kinds": fw.KINDS,
        "technical_terms": qs.TECHNICAL_TERMS,
        "persona_kinds": qs.PERSONA_KINDS,
        "returns": qs.RETURNS,
        "escalations": qs.ESCALATIONS,
        "avatars": _avatar_manifest(),
        "read_passage": content.READ_PASSAGE,
        "curriculum": content.CURRICULUM,
        "course": {"units": course.UNITS, "lessons": course.LESSONS},
    }


@app.get("/frameworks")
def get_frameworks() -> dict:
    return {"frameworks": fw.FRAMEWORKS, "kinds": fw.KINDS}


def _question_public(q: dict) -> dict:
    """What the frontend needs, including the ground truth it will hand back
    to the grader. It is the user's own laptop; nothing is hidden."""
    out = {"id": q["id"], "kind": q["kind"], "text": q["text"], "topic": q.get("topic"),
           "hostile": q["kind"] in qs.HOSTILE_KINDS,
           "recommended_framework": fw.recommended(q["kind"]),
           "frameworks": [f["id"] for f in fw.for_kind(q["kind"])]}
    for k in ("premise", "real_question", "parts", "term", "loaded"):
        if k in q:
            out[k] = q[k]
    return out


@app.get("/questions")
def get_questions(kinds: str = "opinion", n: int = 3, balanced: bool = False,
                  exclude: str = "") -> dict:
    ks = [k.strip() for k in kinds.split(",") if k.strip() in fw.KINDS]
    if not ks:
        raise HTTPException(400, "No valid kinds given.")
    ex = {x.strip() for x in exclude.split(",") if x.strip()}
    picked = qs.pick(ks, max(1, min(n, 12)), exclude=ex, balanced=balanced)
    return {"questions": [_question_public(q) for q in picked]}


QUESTION_SCHEMA = _schema({
    "text": {"type": "string"},
    "premise": {"type": "string"},
    "real_question": {"type": "string"},
})


@app.post("/questions/generate")
def generate_question(payload: dict) -> JSONResponse:
    kind = payload.get("kind", "opinion")
    if kind not in fw.KINDS:
        raise HTTPException(400, "Unknown kind.")
    topic = payload.get("topic") or ("process automation, operations and stakeholder "
                                     "management at a large bank, or general life")
    examples = [q["text"] for q in qs.QUESTIONS if q["kind"] == kind][:3]
    prompt = (f"Write ONE new question of this kind: {kind} ({fw.KINDS[kind]}).\n"
              f"Topic area: {topic}.\nExamples of the kind: {json.dumps(examples)}\n"
              "It must be different from the examples, at most 30 words, and spoken "
              "the way a real person asks in a meeting.\n"
              + ("It must smuggle in ONE false assumption. Put that assumption in "
                 "'premise' and the fair question underneath in 'real_question'."
                 if kind == "loaded" else
                 "Put the legitimate concern underneath in 'real_question' and leave "
                 "'premise' empty."))
    out = ollama_chat([{"role": "system", "content": "You write practice questions "
                                                     "for a public speaking coach. JSON only."},
                       {"role": "user", "content": prompt}], QUESTION_SCHEMA, temperature=0.8)
    if not out or not out.get("text"):
        return JSONResponse({"available": False,
                             "reason": "Question generator is offline. The bank has "
                                       f"{len(qs.QUESTIONS)} questions ready."})
    q = {"id": f"gen-{uuid.uuid4().hex[:6]}", "kind": kind, "text": out["text"],
         "topic": "generated"}
    if kind == "loaded":
        q["loaded"] = True
        q["premise"] = out.get("premise") or None
    if out.get("real_question"):
        q["real_question"] = out["real_question"]
    return JSONResponse({"available": True, "question": _question_public(q)})


# ----------------------------------------------------------------------
# History
# ----------------------------------------------------------------------

def _avg(path: list[str], rows: list[dict]) -> Optional[float]:
    vals = []
    for s in rows:
        node: Any = s
        for p in path:
            node = node.get(p) if isinstance(node, dict) else None
        if isinstance(node, (int, float)):
            vals.append(float(node))
    return round(sum(vals) / len(vals), 2) if vals else None


def _turn_rows(sessions: list[dict], mode: str) -> list[dict]:
    out = []
    for s in sessions:
        if s.get("mode") != mode:
            continue
        for t in s.get("turns") or []:
            out.append(t)
    return out


@app.get("/history")
def history() -> dict:
    sessions = load("sessions.json", [])
    baseline = load("baseline.json", {})
    scored = _scored_sessions(sessions)
    # Level is the unit you have reached on the path, or the session count if higher.
    _, current_lesson, _ = _course_state()
    unit_reached = course.BY_ID[current_lesson]["unit"] if current_lesson else len(course.UNITS)
    level = max(_level_for(len(scored)), unit_reached)

    practice = [s for s in sessions if s.get("mode") == "practice"]
    qdrill = [s for s in sessions if s.get("mode") == "qdrill"]
    roleplay_turns = _turn_rows(sessions, "roleplay")
    recent_scored = scored[-10:]

    pressure = None
    if len(practice) >= 3 and len(roleplay_turns) >= 3:
        keys = [("jitter", ["acoustics", "quality", "jitter_local_pct"]),
                ("hnr", ["acoustics", "quality", "hnr_db"]),
                ("volume_sd", ["acoustics", "volume", "consistency_sd_db"])]
        pressure = {
            "practice": {k: _avg(p, practice[-8:]) for k, p in keys},
            "roleplay": {k: _avg(p, roleplay_turns[-12:]) for k, p in keys},
        }
        if all(v is None for v in pressure["practice"].values()):
            pressure = None

    # Framework record: how each structure has gone for this speaker.
    fstats: dict[str, dict] = {}
    for s in qdrill:
        for t in s.get("turns") or []:
            fid = t.get("framework")
            total = (t.get("score") or {}).get("total")
            if fid and isinstance(total, (int, float)):
                st = fstats.setdefault(fid, {"n": 0, "sum": 0.0})
                st["n"] += 1
                st["sum"] += total
    framework_stats = {k: {"n": v["n"], "mean": round(v["sum"] / v["n"])}
                       for k, v in fstats.items()}

    vowel_n = len((baseline.get("vowel") or {}).get("takes", []))
    read_n = len((baseline.get("read") or {}).get("takes", []))
    today = time.strftime("%Y-%m-%d")
    due = [e["term"] for e in _all_bank_entries()
           if (e.get("srs") or {}).get("due") and e["srs"]["due"] <= today]

    # Streak and this week, from the dates of scored sessions.
    days = sorted({(s.get("at") or "")[:10] for s in scored if s.get("at")})
    streak = 0
    if days:
        import datetime as _dt
        cursor = _dt.date.today()
        dayset = set(days)
        if cursor.isoformat() not in dayset:
            cursor -= _dt.timedelta(days=1)
        while cursor.isoformat() in dayset:
            streak += 1
            cursor -= _dt.timedelta(days=1)
        week_cut = (_dt.date.today() - _dt.timedelta(days=6)).isoformat()
        week_sessions = sum(1 for s in scored if (s.get("at") or "")[:10] >= week_cut)
    else:
        week_sessions = 0

    # Trend: the last five against the five before, for the headline numbers.
    def _trend(path: list[str], rows: list[dict]) -> Optional[float]:
        if len(rows) < 6:
            return None
        now, was = _avg(path, rows[-5:]), _avg(path, rows[-10:-5])
        if now is None or was is None:
            return None
        return round(now - was, 1)

    calibrated = vowel_n >= 3 and read_n >= 1
    tolerance = _tolerance_for(level)
    a_filler = _avg(["text", "fillers", "pct"], practice[-10:])
    a_wpm = _avg(["text", "pace", "wpm"], practice[-10:])
    a_hedge = _avg(["text", "hedges", "per_100w"], practice[-10:])
    weakest = min(framework_stats.items(), key=lambda kv: kv[1]["mean"]) if framework_stats else None
    if not scored:
        fix_next = "Nothing measured yet. Begin today's session and the app will find the first habit to fix."
    elif not calibrated:
        fix_next = "Steadiness is not being measured yet. The warm-up in today's session gives the app your calm voice."
    elif a_filler is not None and a_filler > tolerance:
        fix_next = (f"Fillers sit at {a_filler:.1f} percent against a {tolerance:.1f} limit. "
                    "Replace each one with a silent beat, not a faster sentence.")
    elif a_wpm is not None and a_wpm > 160:
        fix_next = f"Pace averages {a_wpm:.0f} words a minute. Put silence where the next word wants to go."
    elif a_wpm is not None and 0 < a_wpm < 120:
        fix_next = f"Pace averages {a_wpm:.0f} words a minute. Aim for 130 to 150; shorter sentences, not faster ones."
    elif a_hedge is not None and a_hedge > 2.5:
        fix_next = f"Hedges run at {a_hedge:.1f} per hundred words. Say the claim, then the caveat if it is real."
    elif weakest and weakest[1]["mean"] < 70:
        fix_next = (f"{fw.by_id(weakest[0])['name'] if fw.by_id(weakest[0]) else weakest[0]} is your "
                    f"weakest structure at {weakest[1]['mean']}. Today's session brings it back.")
    else:
        fix_next = "The numbers are in range. Today's session raises the pressure a notch."

    return {
        "sessions": len(scored),
        "level": level,
        "streak_days": streak,
        "week_sessions": week_sessions,
        "trend": {
            "score": _trend(["score", "total"], scored),
            "wpm": _trend(["text", "pace", "wpm"], practice),
            "filler_pct": _trend(["text", "fillers", "pct"], practice),
        },
        "fix_next": fix_next,
        "filler_tolerance": tolerance,
        "next_level": next((lv for lv in content.LEVELS if lv["lvl"] == level + 1), None),
        "calibrated": vowel_n >= 3 and read_n >= 1,
        "calibration": {"vowel": vowel_n, "read": read_n,
                        "vowel_needed": 3, "read_needed": 1},
        "baseline_device": baseline.get("device_id"),
        "recent": [
            {"id": s.get("id"), "at": s.get("at"), "drill": s.get("drill"),
             "title": s.get("drill_title"), "mode": s.get("mode"),
             "score": (s.get("score") or {}).get("total"),
             "framework": s.get("framework"),
             "wpm": ((s.get("text") or {}).get("pace") or {}).get("wpm"),
             "filler_pct": ((s.get("text") or {}).get("fillers") or {}).get("pct")}
            for s in recent_scored
        ],
        "averages": {
            "score": _avg(["score", "total"], scored[-10:]),
            "wpm": _avg(["text", "pace", "wpm"], practice[-10:]),
            "filler_pct": _avg(["text", "fillers", "pct"], practice[-10:]),
            "hedge_per_100w": _avg(["text", "hedges", "per_100w"], practice[-10:]),
        },
        "pressure_delta": pressure,
        "framework_stats": framework_stats,
        "srs_due": due[:20],
    }


# ----------------------------------------------------------------------
# The path: a linear course with progress, and today's plan drawn from it
# ----------------------------------------------------------------------

def _course_state() -> tuple[list[dict], Optional[str], dict]:
    """Every lesson with its status. The first lesson not yet done is current;
    everything after it is locked. Done lessons stay open for another go."""
    prog = load("progress.json", {})
    out: list[dict] = []
    current: Optional[str] = None
    for lid in course.ORDER:
        l = course.BY_ID[lid]
        p = prog.get(lid)
        if p:
            status = "done"
        elif current is None:
            status, current = "current", lid
        else:
            status = "locked"
        best = (p or {}).get("best")
        out.append({**l, "status": status, "best": best, "last": (p or {}).get("last"),
                    "attempts": (p or {}).get("attempts", 0),
                    "star": bool(p and l.get("pass") is not None and (best or 0) >= l["pass"])})
    return out, current, prog


@app.get("/course")
def get_course() -> dict:
    lessons, current, _ = _course_state()
    units = []
    for u in course.UNITS:
        ls = [l for l in lessons if l["unit"] == u["n"]]
        units.append({**u, "lessons": ls, "done": sum(1 for l in ls if l["status"] == "done"),
                      "total": len(ls)})
    number = {lid: i + 1 for i, lid in enumerate(course.ORDER)}
    return {"units": units, "current": current, "number": number,
            "done": sum(1 for l in lessons if l["status"] == "done"), "total": len(lessons)}


@app.post("/course/complete")
def course_complete(payload: dict) -> dict:
    lid = payload.get("lesson")
    if lid not in course.BY_ID:
        raise HTTPException(404, "Unknown lesson.")
    score = payload.get("score")
    score = int(round(float(score))) if isinstance(score, (int, float)) else None
    prog = load("progress.json", {})
    p = prog.get(lid) or {"attempts": 0, "best": None}
    p["attempts"] = int(p.get("attempts", 0)) + 1
    p["last"] = time.strftime("%Y-%m-%d")
    p["score"] = score
    if score is not None:
        p["best"] = score if p.get("best") is None else max(int(p["best"]), score)
    prog[lid] = p
    save("progress.json", prog)
    return get_course()


@app.get("/profile")
def get_profile() -> dict:
    return {"minutes": 10, "goal": "", "onboarded": False, **load("profile.json", {})}


@app.post("/profile")
def set_profile(payload: dict) -> dict:
    prof = load("profile.json", {})
    for k in ("minutes", "goal", "onboarded", "name"):
        if k in payload:
            prof[k] = payload[k]
    save("profile.json", prof)
    return get_profile()


def _lesson_step(l: dict, review: bool = False) -> dict:
    n = course.ORDER.index(l["id"]) + 1
    return {"kind": "lesson",
            "title": ("Review: " if review else f"Lesson {n}: ") + l["title"],
            "detail": l["goal"], "minutes": l["minutes"],
            "params": {"lesson": l["id"], "review": review}}


def _make_plan(h: dict) -> list[dict]:
    """Today = the next lessons on the path that fit the daily minutes, plus one
    review of a lesson that did not earn its star, every other day."""
    import datetime as _dt
    day = _dt.date.today().toordinal()
    lessons, current, prog = _course_state()
    budget = max(4, int(load("profile.json", {}).get("minutes", 10) or 10))
    steps: list[dict] = []
    total = 0
    if current is not None:
        for lid in course.ORDER[course.ORDER.index(current):]:
            l = course.BY_ID[lid]
            if steps and total + l["minutes"] > budget:
                break
            steps.append(_lesson_step(l))
            total += l["minutes"]
            if len(steps) >= 3:
                break
    weak = sorted((p.get("last", ""), lid) for lid, p in prog.items()
                  if course.BY_ID.get(lid) and course.BY_ID[lid].get("pass") is not None
                  and (p.get("best") or 0) < course.BY_ID[lid]["pass"])
    if weak and (day % 2 == 0 or current is None) and (total + 4 <= budget or not steps):
        steps.append(_lesson_step(course.BY_ID[weak[0][1]], review=True))
    if not steps:
        l = course.BY_ID[course.ORDER[day % len(course.ORDER)]]
        steps.append(_lesson_step(l, review=True))
    for i, s in enumerate(steps):
        s["index"] = i
        s["done"] = False
    return steps


@app.get("/plan")
def get_plan(refresh: bool = False) -> dict:
    today = time.strftime("%Y-%m-%d")
    plan = load("plan.json", {})
    if refresh or plan.get("date") != today or not plan.get("steps"):
        plan = {"date": today, "steps": _make_plan(history())}
        save("plan.json", plan)
    plan["done_count"] = sum(1 for s in plan["steps"] if s.get("done"))
    plan["total_minutes"] = sum(s.get("minutes", 0) for s in plan["steps"])
    return plan


@app.post("/plan/step")
def plan_step(payload: dict) -> dict:
    plan = load("plan.json", {})
    idx = int(payload.get("index", -1))
    if 0 <= idx < len(plan.get("steps", [])):
        plan["steps"][idx]["done"] = bool(payload.get("done", True))
        save("plan.json", plan)
    return get_plan()


# ----------------------------------------------------------------------
# Audio plumbing
# ----------------------------------------------------------------------

def _save_upload(audio: UploadFile) -> str:
    """The suffix is fixed by us, never taken from the upload. ffmpeg sniffs
    the real container anyway."""
    name = (audio.filename or "").lower()
    suffix = ".wav" if name.endswith(".wav") else ".webm"
    fd, path = tempfile.mkstemp(prefix="st-", suffix=suffix, dir=TMP)
    with os.fdopen(fd, "wb") as fh:
        shutil.copyfileobj(audio.file, fh)
    return path


def _to_wav(path: str) -> Optional[str]:
    """Praat and Whisper want a real wav. Browsers give webm or ogg."""
    if path.lower().endswith(".wav"):
        return path
    if not shutil.which("ffmpeg"):
        return None
    out = path + ".wav"
    try:
        rc = subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-ac", "1",
             "-ar", "22050", out],
            capture_output=True, timeout=120,
        ).returncode
    except (subprocess.SubprocessError, OSError):
        return None
    return out if rc == 0 and os.path.exists(out) else None


def _cleanup(*paths: Optional[str]) -> None:
    for p in set(paths):
        if p and os.path.exists(p):
            try:
                os.remove(p)
            except OSError:
                pass


def _transcribe(wav: str) -> tuple[str, float]:
    model = _svc["whisper"]
    if not model:
        return "", 0.0
    with _whisper_lock:
        segments, info = model.transcribe(
            wav, beam_size=1, vad_filter=False,
            condition_on_previous_text=False, initial_prompt=WHISPER_PROMPT,
        )
        parts = [s.text for s in segments]
    return " ".join(parts).strip(), float(getattr(info, "duration", 0.0) or 0.0)


def _analyze_audio(wav: Optional[str], sustained_vowel: bool) -> Optional[dict]:
    vm = acoustics_mod()
    if not (vm and wav):
        return None
    try:
        all_base = load("baseline.json", {})
        slot = "vowel" if sustained_vowel else "read"
        base = all_base.get(slot) or None
        if base and not base.get("quality", {}).get("jitter_local_pct"):
            base = None
        acoustics = vm.analyze(wav, baseline=base, sustained_vowel=sustained_vowel)
        if base is None:
            acoustics["baseline_note"] = (
                "Steadiness not scored: no calm baseline recorded for "
                + ("the sustained vowel." if sustained_vowel
                   else "connected speech. Record the calm read on the Dashboard."))
        return acoustics
    except Exception:
        return None


@app.post("/transcribe")
def transcribe(
    audio: UploadFile = File(...),
    drill_id: str = Form("read-steady"),
    mode: str = Form("practice"),
    audience: str = Form("us_internal"),
    duration_s: float = Form(0.0),
    sustained_vowel: bool = Form(False),
    store: bool = Form(True),
) -> JSONResponse:
    """Transcribe and analyse one recording. With store=true it is a practice
    session and is scored on the main rubric. Question drills and roleplay
    call this with store=false, then /qa-score, then /sessions/series."""
    raw = _save_upload(audio)
    wav = _to_wav(raw)
    try:
        transcript, dur = ("", 0.0)
        if wav:
            try:
                transcript, dur = _transcribe(wav)
            except Exception:
                transcript, dur = "", 0.0
        dur = dur or duration_s

        drill = next((e for e in _exercises() if e["id"] == drill_id), None) or \
            next(e for e in content.EXERCISES if e["id"] == "read-steady")

        text_m = tm.analyze(transcript, dur or 1.0, bank=BANK, audience=audience)
        acoustics = _analyze_audio(wav, sustained_vowel)
    finally:
        _cleanup(raw, wav)

    sessions = load("sessions.json", [])
    level = _level_for(len(_scored_sessions(sessions)))
    score = scoring.session_score(text_m, acoustics, float(drill.get("time", 60)),
                                  level=level, tolerance=_tolerance_for(level))
    jscore = scoring.jargon_score(text_m["jargon"])

    session = {
        "id": uuid.uuid4().hex[:10], "at": _now(),
        "drill": drill["id"], "drill_title": drill["title"], "mode": mode,
        "audience": audience, "transcript": transcript,
        "text": text_m, "acoustics": acoustics,
        "score": score, "jargon_score": jscore,
        "asr": _state["asr"] == "on",
    }
    if store and mode == "practice":
        sessions.append(session)
        save("sessions.json", sessions[-300:])
        session["level"] = _level_for(len(_scored_sessions(sessions)))
    return JSONResponse(session)


@app.post("/calibrate")
def calibrate(
    audio: UploadFile = File(...),
    kind: str = Form("vowel"),
    device_id: str = Form("default"),
) -> JSONResponse:
    """Baselines are stored per task. A sustained vowel and connected speech
    are acoustically different jobs, so each gets its own baseline."""
    vm = acoustics_mod()
    if not vm:
        raise HTTPException(503, "Acoustic analysis is not available. "
                                 "Install praat-parselmouth and scipy.")
    if kind not in ("vowel", "read"):
        raise HTTPException(400, "kind must be 'vowel' or 'read'.")

    raw = _save_upload(audio)
    wav = _to_wav(raw)
    try:
        if not wav:
            raise HTTPException(400, "Could not read the audio. Install ffmpeg.")
        try:
            m = vm.analyze(wav, sustained_vowel=(kind == "vowel"))
        except Exception as exc:
            raise HTTPException(400, f"Could not analyse the audio: {exc}")
    finally:
        _cleanup(raw, wav)

    base = load("baseline.json", {})
    base["device_id"] = device_id
    base["updated"] = _now()

    slot = base.get(kind) or {"takes": []}
    slot["takes"] = (slot["takes"] + [{
        "at": _now(),
        "volume": m["volume"], "pitch": m["pitch"], "quality": m["quality"],
    }])[-6:]

    def median_of(group: str, key: str) -> Optional[float]:
        vals = sorted(t[group][key] for t in slot["takes"]
                      if (t.get(group) or {}).get(key) is not None)
        return vals[len(vals) // 2] if vals else None

    slot["volume"] = {"consistency_sd_db": median_of("volume", "consistency_sd_db")}
    slot["pitch"] = {"sd_semitones": median_of("pitch", "sd_semitones"),
                     "median_hz": median_of("pitch", "median_hz")}
    slot["quality"] = {"jitter_local_pct": median_of("quality", "jitter_local_pct"),
                       "shimmer_local_pct": median_of("quality", "shimmer_local_pct"),
                       "hnr_db": median_of("quality", "hnr_db")}
    base[kind] = slot
    save("baseline.json", base)

    vowel_n = len((base.get("vowel") or {}).get("takes", []))
    read_n = len((base.get("read") or {}).get("takes", []))
    return JSONResponse({
        "kind": kind,
        "takes": {"vowel": vowel_n, "read": read_n},
        "tremor": m.get("tremor"),
        "usable": bool((m.get("quality") or {}).get("usable")),
        "complete": vowel_n >= 3 and read_n >= 1,
    })


# ----------------------------------------------------------------------
# Grading: practice coaching and the question drills
# ----------------------------------------------------------------------

GRADER_SYSTEM = ("You are a strict, concise public speaking coach grading one spoken "
                 "answer. Judge only what the transcript shows. Quote the speaker's "
                 "actual words in notes. Reply with JSON only.")

COACH_SCHEMA = _schema({
    "content_score_0_20": _int(0, 20),
    "structure_note": {"type": "string"},
    "one_focus_fix": {"type": "string"},
})
# Ordering rule for every schema in this file: scored numbers, arrays and
# booleans first, free text last. The grammar emits keys in schema order, so a
# reply cut off by the token budget loses prose, never a score.


@app.post("/coach")
def coach(payload: dict) -> JSONResponse:
    t = (payload.get("transcript") or "").strip()
    m = payload.get("metrics", {})
    drill = payload.get("drill", {})
    if not t:
        return JSONResponse({"available": False, "reason": "No transcript to grade."})
    prompt = f"""DRILL: {drill.get('title', 'practice')}. {drill.get('desc', '')}
DETERMINISTIC METRICS (already computed, do not recompute, do not comment on): {json.dumps(m)}
TRANSCRIPT: \"\"\"{t}\"\"\"

Grade ONLY content and structure, the things a formula cannot see: an opening
that states the point, one clear point, logical flow, a deliberate ending.
Scoring guide: 0-6 rambling with no visible point; 7-12 a point exists but the
order wanders; 13-17 clear point, reason and ending; 18-20 tight, quotable.
structure_note: at most 40 words, specific, quote their words.
one_focus_fix: at most 25 words, one concrete action for the next attempt."""
    out = ollama_chat([{"role": "system", "content": GRADER_SYSTEM},
                       {"role": "user", "content": prompt}], COACH_SCHEMA)
    if not out:
        return JSONResponse({"available": False,
                             "reason": "Coaching model is offline. Your deterministic "
                                       "score above is complete."})
    return JSONResponse({"available": True, **out})


HOSTILITY_TYPES = ["loaded_premise", "compound", "false_dilemma", "statement",
                   "gotcha_detail", "status_attack", "off_topic", "not_actually_hostile"]

KIND_TO_HOSTILITY = {"loaded": "loaded_premise", "compound": "compound",
                     "false_dilemma": "false_dilemma", "statement": "statement",
                     "gotcha": "gotcha_detail", "status": "status_attack",
                     "off_topic": "off_topic"}


def _framework_block(f: Optional[dict]) -> str:
    if not f:
        return ""
    steps = "\n".join(f"  {i + 1}. {s['label']}: {s['cue']}" for i, s in enumerate(f["steps"]))
    return (f"\nFRAMEWORK THE SPEAKER WAS ASKED TO USE: {f['name']} ({f['tagline']})\n{steps}\n"
            f"Grader brief: {f['grader']}\n"
            "Rate 'coverage' with one integer per step in order: 0 absent, 1 partial, "
            "2 clearly present. Set 'in_order' false if the steps came in a different "
            "order.\n")


def _truth_block(truth: dict, kind: str) -> str:
    lines = []
    if truth.get("premise"):
        lines.append(f"The question carries this FALSE premise: {truth['premise']}")
    if truth.get("loaded") is False:
        lines.append("The question is fair. It carries NO false premise.")
    if truth.get("parts"):
        lines.append(f"The question fuses two questions: {json.dumps(truth['parts'])}")
    if truth.get("real_question"):
        lines.append(f"The legitimate concern underneath: {truth['real_question']}")
    if truth.get("term"):
        lines.append(f"The shorthand term in the question: {truth['term']}")
    if kind in KIND_TO_HOSTILITY:
        lines.append(f"Question type: {KIND_TO_HOSTILITY[kind]}")
    return ("\nGROUND TRUTH ABOUT THE QUESTION:\n" + "\n".join(lines) + "\n") if lines else ""


def _det_block(d: dict) -> str:
    return ("\nDETERMINISTIC SIGNALS (already computed, do not recompute, do not "
            f"comment on): {json.dumps(d)}\n")


def _grade(mode: str, question: str, transcript: str, truth: dict, kind: str,
           f: Optional[dict], det: dict) -> tuple[Optional[dict], Optional[dict]]:
    """Returns (llm_output, schema). The schema depends on the mode."""
    n_steps = len(f["steps"]) if f else 0
    head = (f"QUESTION ASKED: \"\"\"{question}\"\"\"\n"
            f"ANSWER TRANSCRIPT: \"\"\"{transcript}\"\"\"\n"
            + _truth_block(truth, kind) + _det_block(det) + _framework_block(f))

    if mode == "answer":
        # Numbers and arrays first: the grammar emits keys in this order, so a
        # reply cut off by the token budget only ever loses prose.
        props: dict[str, Any] = {"directness_0_25": _int(0, 25)}
        if f:
            props["coverage"] = _coverage(n_steps)
            props["in_order"] = {"type": "boolean"}
        props.update({
            "dodge_detected": {"type": "boolean"},
            "structure_used": {"type": "string"},
            "one_focus_fix": {"type": "string"},
            "better_opening": {"type": "string"},
        })
        prompt = head + """
Grade:
1. DIRECTNESS (0-25). Is there a substantive answer to the question actually
   asked within the first two sentences? Guide: 22-25 the first sentence is the
   answer; 15-21 answer arrives by sentence two; 8-14 answer arrives late after a
   preface or story; 0-7 no real answer, or refusing to answer while appearing to.
   A number, a yes, a no, or a clear recommendation in sentence one is direct.
2. dodge_detected: true only if no substantive answer appears anywhere.
3. structure_used: name the shape you heard in a few words, or "none".
4. one_focus_fix: at most 25 words, one concrete action.
5. better_opening: the first sentence they should have said, at most 25 words."""
        schema = _schema(props)

    elif mode == "hostile":
        props = {
            "hostility_type": {"type": "string", "enum": HOSTILITY_TYPES},
            "premise_0_25": _int(0, 25),
            "substance_0_25": _int(0, 25),
            "close_0_20": _int(0, 20),
            "returned_personal_attack": {"type": "boolean"},
            "premise_accepted_wrongly": {"type": "boolean"},
        }
        if f:
            props["coverage"] = _coverage(n_steps)
            props["in_order"] = {"type": "boolean"}
        props.update({
            "what_they_should_have_said": {"type": "string"},
            "one_focus_fix": {"type": "string"},
        })
        prompt = head + """
This is a HOSTILE question. Grade:
1. PREMISE HANDLING (0-25). If the ground truth names a false premise, fused
   parts or a false dilemma: did the speaker name it, divide it, or refuse it
   BEFORE answering? 20-25 named and corrected cleanly; 10-19 partly; 0-9 answered
   inside the false frame. If the ground truth says the question is fair, award
   20-25 for answering directly without manufacturing a grievance, and 0-10 if
   they attacked a premise that was not there.
2. SUBSTANCE (0-25). Did they answer the legitimate concern underneath?
3. CLOSE (0-20). Did they end cleanly and hand back to the room, or invite a
   back and forth?
4. returned_personal_attack: true ONLY if the speaker insulted or belittled the
   questioner as a person. Sharp disagreement is not a personal attack.
5. premise_accepted_wrongly: true ONLY if the ground truth names a false premise
   and the speaker's answer treats it as true. Example: to "Why did you cut
   corners?" the answer "We were under pressure so some steps were shortened"
   accepts the premise (true, premise 0-9); the answer "That assumes corners were
   cut. The full process ran and Audit signed it" names and corrects it (false,
   premise 20-25).
6. what_they_should_have_said: the ideal opening line, at most 30 words.
7. one_focus_fix: at most 25 words."""
        schema = _schema(props)

    elif mode == "paraphrase":
        prompt = head + """
The task was ONLY to restate the question with the hostility, tone and loaded
words stripped out, so the room hears the real question. Answering it, arguing
with it, or adding a defence is a mistake. Grade:
1. neutral_restatement_0_25: 22-25 a calm, accurate restatement of the real
   question; 12-21 restated but some tone or a loaded word survived; 0-11 not a
   restatement, or the loaded premise was repeated as fact.
2. kept_the_real_question: true if the legitimate concern survived.
3. added_argument: true if they started answering or defending.
4. one_focus_fix: at most 20 words."""
        schema = _schema({
            "neutral_restatement_0_25": _int(0, 25),
            "kept_the_real_question": {"type": "boolean"},
            "added_argument": {"type": "boolean"},
            "one_focus_fix": {"type": "string"},
        })
        # (numbers and booleans already precede the prose field)

    elif mode == "classify":
        prompt = head + """
The task was to say "loaded, because ..." naming the false assumption, or
"clean" if there is none. The ground truth above says which it is. Grade ONLY:
1. named_actual_premise_0_20: if the question is loaded, how precisely did the
   speaker name the actual false premise (20 exact, 10 near, 0 wrong or absent)?
   If the question is clean, award 20 when they said clean and did not invent one.
2. one_focus_fix: at most 20 words."""
        schema = _schema({"named_actual_premise_0_20": _int(0, 20),
                          "one_focus_fix": {"type": "string"}})

    elif mode == "gap":
        prompt = head + """
The figure asked for is one the speaker cannot possibly have. The right answer
admits the gap cleanly, commits to a follow up with a date, and then answers
the part that can be answered. Guessing is the worst outcome. Grade ONLY:
1. answered_what_they_could_0_30: did they add the part they genuinely could
   answer, such as the trend, the driver, or the related figure they do know?
   30 yes with substance; 15 a thin gesture; 0 nothing beyond the admission.
2. guessed: true if they offered a specific number they cannot know.
3. one_focus_fix: at most 20 words."""
        schema = _schema({"answered_what_they_could_0_30": _int(0, 30),
                          "guessed": {"type": "boolean"},
                          "one_focus_fix": {"type": "string"}})
        # The model's guessed flag is informational only; scoring uses the
        # deterministic detector.

    elif mode == "ask":
        prompt = head + """
The question contains corporate shorthand the speaker may not know. The task
was to ask what the term means, directly, without apologising. The strongest
form offers a guess: "When you say throughput, do you mean cases per day?"
Grade ONLY:
1. direct_and_specific_0_20: 18-20 named the term and asked directly or offered
   a guess; 10-17 asked but vaguely; 0-9 no real question, or buried in apology.
2. one_focus_fix: at most 20 words."""
        schema = _schema({"direct_and_specific_0_20": _int(0, 20),
                          "one_focus_fix": {"type": "string"}})

    elif mode == "comprehend":
        prompt = head + """
A bank VP asked this entirely in corporate shorthand. Two outcomes score full
marks: the speaker understood the shorthand and answered, or the speaker asked
what the term meant and then answered. Guessing the meaning wrong is the only
fail. Classify the outcome:
  understood_and_answered | asked_then_answered | asked_only |
  understood_partially | dodged | guessed_wrong
one_focus_fix: at most 20 words."""
        schema = _schema({"outcome": {"type": "string", "enum": list(scoring.COMPREHEND_POINTS)},
                          "one_focus_fix": {"type": "string"}})
    else:
        return None, None

    out = ollama_chat([{"role": "system", "content": GRADER_SYSTEM},
                       {"role": "user", "content": prompt}], schema, temperature=0.1)
    return out, schema


@app.post("/qa-score")
def qa_score(payload: dict) -> JSONResponse:
    """Grade one spoken answer to one question. mode picks the rubric:
    answer, hostile, paraphrase, classify, gap, ask, comprehend."""
    question = (payload.get("question") or "").strip()
    transcript = (payload.get("transcript") or "").strip()
    duration = float(payload.get("duration_s") or 0) or 1.0
    latency = payload.get("latency_s")
    latency = float(latency) if isinstance(latency, (int, float)) else None
    kind = payload.get("kind") or ("loaded" if payload.get("hostile") else "clean")
    truth = payload.get("truth") or {}
    mode = payload.get("mode") or ("hostile" if kind in qs.HOSTILE_KINDS else "answer")
    f = fw.by_id(payload.get("framework"))
    audience = payload.get("audience", "us_internal")

    if not transcript:
        return JSONResponse({"available": False, "mode": mode,
                             "reason": "Nothing was transcribed. Transcription may be "
                                       "off or still loading, or the answer was silent.",
                             "score": None})

    m = tm.analyze(transcript, duration, bank=BANK, audience=audience,
                   question=question, framework=f)
    prior = payload.get("prior_turns") or []
    esc = scoring.escalation_delta({"acoustics": payload.get("acoustics"), "text": m},
                                   prior) if prior else None

    if mode == "hostile":
        det = scoring.hostile_deterministic(m, latency, esc)
    else:
        det = scoring.qa_deterministic(m, latency)

    extra: dict[str, Any] = {}
    if mode == "gap":
        extra["gap"] = tm.gap_admission(transcript)
    elif mode in ("ask", "comprehend"):
        extra["ask"] = tm.asks_meaning(transcript, truth.get("term"))
    elif mode == "classify":
        extra["classification"] = tm.classification(transcript)
    elif mode == "paraphrase":
        extra["paraphrase"] = tm.paraphrase_markers(transcript)

    llm = None
    if ollama_up():
        llm, _ = _grade(mode, question, transcript, truth, kind, f,
                        {k: v for k, v in det.items() if k != "notes"} | extra)

    truth_label: Optional[str] = None
    if truth.get("loaded") is True or truth.get("premise"):
        truth_label = "loaded"
    elif truth.get("loaded") is False or kind in ("clean", "two_part", "numbers"):
        truth_label = "clean"

    if mode == "hostile":
        score = scoring.hostile_score(det, llm, m, f, truth_label)
    elif mode == "paraphrase":
        score = scoring.paraphrase_score(m, extra["paraphrase"], llm)
    elif mode == "classify":
        score = scoring.classify_score(extra["classification"], truth.get("loaded"), llm)
    elif mode == "gap":
        # The guess detector is deterministic on purpose: a hedge word right
        # before a number. The model's own guess flag is noisy and is ignored.
        score = scoring.gap_score(extra["gap"], llm)
    elif mode == "ask":
        score = scoring.ask_score(extra["ask"], m, llm)
    elif mode == "comprehend":
        score = scoring.comprehend_score(extra["ask"], llm)
    else:
        score = scoring.answer_score(det, llm, m, f)

    return JSONResponse({
        "available": llm is not None, "mode": mode, "kind": kind,
        "metrics": m, "deterministic": det, "extra": extra, "llm": llm,
        "escalation": esc, "score": score,
        "framework": {"id": f["id"], "name": f["name"]} if f else None,
        "recommended_framework": fw.recommended(kind),
        "reason": None if llm is not None else
                  "Model offline: graded on the deterministic parts only.",
    })


# ----------------------------------------------------------------------
# Lessons, generated drills
# ----------------------------------------------------------------------

LESSON_SCHEMA = _schema({"title": {"type": "string"}, "lesson_md": {"type": "string"},
                         "drill_suggestion": {"type": "string"}})


@app.post("/lesson")
def lesson(payload: dict) -> JSONResponse:
    stats = payload.get("stats", {})
    prompt = f"""You are a public speaking teacher. The learner's recent data:
{json.dumps(stats)}

Write one micro lesson targeting their weakest metric. Ground it in these
principles: replace fillers with silent pauses; 130 to 150 WPM; answer first,
then reason, then example (PREP); pause before and after key lines; answer
before you bridge; low hedge density but not zero; fix one habit at a time.
title: at most 8 words. lesson_md: 120 to 180 words, cite their actual numbers,
plain prose. drill_suggestion: one 60 second exercise they can do right now."""
    out = ollama_chat([{"role": "system", "content": GRADER_SYSTEM},
                       {"role": "user", "content": prompt}], LESSON_SCHEMA,
                      temperature=0.5, num_predict=600)
    if not out or not out.get("lesson_md"):
        return JSONResponse({"available": False,
                             "reason": "Lesson model is offline. The written lessons in "
                                       "Learn are always available."})
    return JSONResponse({"available": True, **out})


DRILL_SCHEMA = _schema({"title": {"type": "string"}, "time": _int(30, 240),
                        "desc": {"type": "string"}, "prompt": {"type": "string"},
                        "rubric": {"type": "string"}})


@app.post("/generate-exercise")
def generate_exercise(payload: dict) -> JSONResponse:
    lvl = max(1, min(5, int(payload.get("level", 1) or 1)))
    kind = payload.get("kind", "impromptu")
    prompt = f"""Generate one public speaking drill for level {lvl} of 5
(1 is basics and read aloud, 5 is keynote grade impromptu under pressure).
Tailor the topic to: an MBA student in strategy, operations and ethics who
works as a performance consultant on process automation and stakeholder
management at a large bank. Requested type: {kind}.
title: at most 5 words. time: seconds, 30 to 240, matched to the level.
desc: one sentence instruction. prompt: the specific topic or scenario with a
structure tip, at most 60 words. rubric: one line."""
    out = ollama_chat([{"role": "system", "content": GRADER_SYSTEM},
                       {"role": "user", "content": prompt}], DRILL_SCHEMA, temperature=0.8)
    if not out or not out.get("title"):
        return JSONResponse({"available": False,
                             "reason": "Drill generator is offline. The built in drills "
                                       "cover every level."})
    drill = {"id": f"gen-{uuid.uuid4().hex[:6]}", "lvl": lvl, "kind": "practice",
             "title": out["title"], "time": out["time"], "desc": out["desc"],
             "prompt": out["prompt"], "rubric": out["rubric"], "source": "generated",
             "at": _now()}
    gens = load("generated_drills.json", [])
    gens.append(drill)
    save("generated_drills.json", gens[-30:])
    return JSONResponse({"available": True, **drill, "flow": "record"})


# ----------------------------------------------------------------------
# Roleplay
# ----------------------------------------------------------------------

PERSONA_TACTICS = {
    "friendly": "Ask one genuinely curious question about what they just said.",
    "specifics": "Ask for one specific figure or one concrete example. Never accept a "
                 "generality.",
    "two-part": "Ask two questions in one sentence. One of them slightly off the topic.",
    "premise": "Take the premise of their last answer and challenge it directly.",
    "loader": "Every question must smuggle in an assumption they have not conceded, "
              "phrased as 'Why did you...', 'Given that X failed...', 'How long have you "
              "known...'. Never ask a neutral question.",
    "bundler": "Fuse two questions into one sentence, one of them damning, so that a "
               "single yes or no answers both.",
    "status": "Attack their experience, seniority or standing, never their argument. "
              "'How long have you been here?', 'Have you ever actually run...'.",
    "speechmaker": "Do not ask a question. Deliver a two or three sentence statement of "
                   "opinion with no question mark in it, and stop.",
    "auditor": "Demand an exact figure they cannot possibly have, to the decimal, for a "
               "specific date or unit.",
    "returner": "Return to the very first objection as if it was never answered. "
                "'You still have not answered...'.",
    "vp": "Speak entirely in US corporate shorthand: sports metaphors, phrasal verbs, "
          "unexpanded acronyms. Never explain a term. Never slow down.",
}

ROLEPLAY_SCHEMA = _schema({"reply": {"type": "string"}, "done": {"type": "boolean"}})


def _persona_examples(key: str) -> list[str]:
    kinds = qs.PERSONA_KINDS.get(key, ["opinion"])
    return [q["text"] for q in qs.QUESTIONS if q["kind"] in kinds][:4]


def _bank_turn(key: str, used: set[str]) -> Optional[dict]:
    kinds = qs.PERSONA_KINDS.get(key, ["opinion"])
    picked = qs.pick(kinds, 1, exclude=used)
    return picked[0] if picked else None


def _valid_reply(reply: str, key: str) -> bool:
    words_n = len(reply.split())
    if not reply or words_n > 60:
        return False
    if key == "speechmaker":
        return "?" not in reply
    return "?" in reply


@app.post("/roleplay-turn")
def roleplay_turn(payload: dict) -> JSONResponse:
    """One persona turn. The first turn always comes from the question bank so
    it is on-brief; later turns come from the model with the conversation as
    context, and fall back to the bank if the model is off or off-brief."""
    key = payload.get("persona", "friendly")
    p = content.PERSONAS.get(key, content.PERSONAS["friendly"])
    scenario = content.SCENARIOS.get(payload.get("scenario", "stakeholder"), "")
    hist = payload.get("history", [])
    used = {h.get("question_id") for h in hist if h.get("question_id")}
    persona_turns = [h for h in hist if h.get("role") == "persona"]
    turn = len(persona_turns)
    max_turns = int(payload.get("turns", 4) or 4)
    unanswerable = bool(payload.get("unanswerable"))
    kinds = qs.PERSONA_KINDS.get(key, ["opinion"])
    kind = "gotcha" if unanswerable else kinds[0]

    def pack(reply: str, q: Optional[dict], source: str, done: bool) -> JSONResponse:
        meta = _question_public(q) if q else {
            "id": None, "kind": kind, "text": reply, "hostile": kind in qs.HOSTILE_KINDS,
            "recommended_framework": fw.recommended(kind),
            "frameworks": [f["id"] for f in fw.for_kind(kind)]}
        return JSONResponse({"available": True, "persona": p["name"],
                             "hostile": bool(p.get("hostile")), "reply": reply,
                             "done": done, "source": source, "question": meta,
                             "turn": turn + 1, "turns": max_turns})

    # Turn 1, and the unanswerable turn, come from the bank.
    if turn == 0 or unanswerable:
        q = _bank_turn("auditor" if unanswerable else key, used)
        if q:
            return pack(q["text"], q, "bank", False)

    if turn >= max_turns:
        return pack("That is all I have. Thank you.", None, "bank", True)

    if ollama_up():
        jargon_rule = {
            0: "Use plain English. No idioms, no acronyms.",
            1: "Use natural US corporate English, roughly one figurative expression "
               "every three sentences.",
            2: "Use heavy US corporate shorthand: sports metaphors, stacked phrasal "
               "verbs, unexpanded acronyms. Never explain a term.",
        }[p.get("jargon_level", 0)]
        system = (f"You are roleplaying {p['name']}: {p['brief']}\nSetting: {scenario}\n"
                  f"The user is presenting to you. Your tactic every turn: "
                  f"{PERSONA_TACTICS.get(key, '')}\n{jargon_rule}\n"
                  f"Questions in your style: {json.dumps(_persona_examples(key))}\n"
                  "If their last answer took the bait, defended their credentials or "
                  "accepted your framing, press harder on the same point. If they "
                  "stayed level and answered the real question, soften slightly.\n"
                  "Rules: stay fully in character; be professionally challenging, never "
                  "abusive: attack positions, framing and competence claims, never the "
                  "person's identity. Reply with exactly ONE question or objection, at "
                  "most 35 words, building on their last answer. Do not prefix your "
                  "reply with a name or with dots. "
                  + (f"This is turn {turn + 1} of {max_turns}. "
                     + ("Set done to true and make the reply a brief in-character "
                        "closing line." if turn + 1 >= max_turns else
                        "Set done to false.")))
        messages = [{"role": "system", "content": system}]
        for h in hist[-8:]:
            role = "assistant" if h.get("role") == "persona" else "user"
            messages.append({"role": role, "content": h.get("text", "")})
        messages.append({"role": "user", "content": "(Your next turn. JSON only.)"}
                        if not hist or hist[-1].get("role") == "persona" else
                        {"role": "system", "content": "Your next turn. JSON only."})

        out = ollama_chat(messages, ROLEPLAY_SCHEMA, temperature=0.6)
        reply = re.sub(r"^\s*(\.{2,}|\w+:)\s*", "", (out or {}).get("reply", "")).strip()
        done = bool((out or {}).get("done")) or turn + 1 >= max_turns
        if out and (_valid_reply(reply, key) or done):
            return pack(reply, None, "model", done)
        # One nudge, then fall back to the bank.
        messages.append({"role": "system", "content":
                         "That reply broke the rules. One question, ending with a "
                         "question mark, under 35 words, in character."})
        out = ollama_chat(messages, ROLEPLAY_SCHEMA, temperature=0.4)
        reply = re.sub(r"^\s*(\.{2,}|\w+:)\s*", "", (out or {}).get("reply", "")).strip()
        if out and _valid_reply(reply, key):
            return pack(reply, None, "model", done)

    q = _bank_turn(key, used)
    if q:
        return pack(q["text"], q, "bank", turn + 1 >= max_turns)
    return pack("That is all I have. Thank you.", None, "bank", True)


KOKORO_VOICES = {"af_heart", "af_bella", "af_nicole", "af_sarah", "af_sky",
                 "am_adam", "am_michael", "am_fenrir", "am_puck",
                 "bf_emma", "bf_isabella", "bm_george", "bm_lewis"}


@app.post("/speak")
def speak(payload: dict, background: BackgroundTasks) -> Any:
    text = (payload.get("text") or "").strip()
    if not text:
        raise HTTPException(400, "Nothing to say.")
    pipe = _svc["kokoro"]
    if not pipe:
        raise HTTPException(503, "Speech is not available. Install kokoro, or the "
                                 "browser's own voices will be used.")
    voice = payload.get("voice") or "af_heart"
    if voice not in KOKORO_VOICES:
        voice = "af_heart"
    try:
        speed = float(payload.get("speed") or 1.0)
    except (TypeError, ValueError):
        speed = 1.0
    speed = max(0.7, min(1.4, speed))
    try:
        import numpy as np
        import soundfile as sf
        with _kokoro_lock:
            chunks = [a for _, _, a in pipe(text, voice=voice, speed=speed) if a is not None]
        arrays = [np.asarray(a.detach().cpu().numpy() if hasattr(a, "detach") else a, dtype="float32")
                  for a in chunks]
        audio = np.concatenate(arrays) if arrays else np.zeros(1, dtype="float32")
        out = os.path.join(TMP, f"tts-{uuid.uuid4().hex[:8]}.wav")
        sf.write(out, audio, 24000)
        background.add_task(_cleanup, out)
        return FileResponse(out, media_type="audio/wav", filename="speak.wav")
    except Exception as exc:
        raise HTTPException(500, f"Speech failed: {exc}")


# ----------------------------------------------------------------------
# Sessions written by the frontend after a series of answers
# ----------------------------------------------------------------------

@app.post("/sessions/series")
def sessions_series(payload: dict) -> JSONResponse:
    """A roleplay or a question drill is one session with several turns."""
    mode = payload.get("mode")
    if mode not in ("roleplay", "qdrill"):
        raise HTTPException(400, "mode must be roleplay or qdrill.")
    turns = payload.get("turns") or []
    if not turns:
        raise HTTPException(400, "No turns to save.")
    slim_turns = []
    for t in turns:
        slim_turns.append({
            "question": t.get("question"), "kind": t.get("kind"),
            "question_id": t.get("question_id"), "transcript": t.get("transcript"),
            "framework": t.get("framework"), "mode": t.get("mode"),
            "text": t.get("text"), "acoustics": t.get("acoustics"),
            "score": t.get("score"), "latency_s": t.get("latency_s"),
        })
    summary = scoring.series_summary(payload.get("series"), slim_turns)
    row = {
        "id": uuid.uuid4().hex[:10], "at": _now(), "mode": mode,
        "drill": payload.get("drill"), "drill_title": payload.get("drill_title"),
        "persona": payload.get("persona"), "scenario": payload.get("scenario"),
        "framework": payload.get("framework"),
        "score": {"total": summary["mean"], "series_score": summary["series_score"]},
        "summary": summary, "turns": slim_turns,
    }
    sessions = load("sessions.json", [])
    sessions.append(row)
    save("sessions.json", sessions[-300:])
    return JSONResponse({"id": row["id"], "summary": summary,
                         "sessions": len(_scored_sessions(sessions)),
                         "level": _level_for(len(_scored_sessions(sessions)))})


# ----------------------------------------------------------------------
# Decode tab
# ----------------------------------------------------------------------

def _all_bank_entries() -> list[dict]:
    return list(BANK.entries.values())


@app.get("/jargon/bank")
def jargon_bank() -> dict:
    personal_terms = {e["term"].lower() for e in load("bank_personal.json", [])}
    seed = [e for e in _all_bank_entries() if e["term"].lower() not in personal_terms]
    personal = [e for e in _all_bank_entries() if e["term"].lower() in personal_terms]
    return {"seed": seed, "personal": personal}


LOOKUP_SCHEMA = _schema({
    "category": {"type": "string", "enum": ["phrasal_verb", "idiom", "sports_metaphor",
                                            "military_metaphor", "corporate_jargon",
                                            "acronym", "ambiguous", "technical"]},
    "meaning": {"type": "string"},
    "plain_alternative": {"type": "string"},
    "example": {"type": "string"},
    "risk": {"type": "string"},
    "subtext": {"type": "string"},
    "use_yourself": {"type": "boolean"},
})


@app.post("/jargon/lookup")
def jargon_lookup(payload: dict) -> JSONResponse:
    term = (payload.get("term") or "").strip().lower()
    if not term:
        raise HTTPException(400, "Enter a term to look up.")
    if term in BANK.entries:
        personal_terms = {e["term"].lower() for e in load("bank_personal.json", [])}
        return JSONResponse({"source": "personal" if term in personal_terms else "bank",
                             "entry": BANK.entries[term]})

    prompt = f"""Explain this business English expression for a fluent non native
speaker working in US banking operations: "{term}"
meaning: one plain sentence. plain_alternative: the shorter everyday way to say
it, or an empty string if none. example: one natural workplace sentence.
risk: note if it means different things in different regions, else empty.
subtext: what people often actually mean by it, else empty.
use_yourself: false if it is a US sports or military metaphor, or carries subtext
that makes it risky to say. category: technical only if no plain word means the
same thing."""
    out = ollama_chat([{"role": "system", "content": "You explain business English. "
                                                     "JSON only."},
                       {"role": "user", "content": prompt}], LOOKUP_SCHEMA, temperature=0.3)
    if not out or not out.get("meaning"):
        return JSONResponse({"source": "unavailable",
                             "reason": "Lookup model is offline. The seeded bank still "
                                       "works for its terms."})
    entry = {"term": term, "category": out["category"], "meaning": out["meaning"],
             "plain_alternative": out.get("plain_alternative") or None,
             "example": out.get("example") or None, "risk": out.get("risk") or None,
             "subtext": out.get("subtext") or None, "use_yourself": bool(out.get("use_yourself")),
             "srs": {"ef": 2.5, "interval": 0, "reps": 0, "due": None}}
    personal = load("bank_personal.json", [])
    personal.append(entry)
    save("bank_personal.json", personal)
    BANK.add(entry)
    return JSONResponse({"source": "generated", "entry": entry})


@app.post("/jargon/review")
def jargon_review(payload: dict) -> JSONResponse:
    """SM-2. Quality 0 to 5. Seed terms keep their state in srs_seed.json,
    personal terms in bank_personal.json; both are reapplied at startup."""
    term = (payload.get("term") or "").lower()
    q = scoring.clamp(payload.get("quality", 3), 0, 5, default=3)
    target = BANK.entries.get(term)
    if not target:
        raise HTTPException(404, "That term is not in the bank yet.")

    s = target.get("srs") or {"ef": 2.5, "interval": 0, "reps": 0}
    ef = max(1.3, float(s.get("ef", 2.5)) + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)))
    if q < 3:
        reps, interval = 0, 1
    else:
        reps = int(s.get("reps", 0)) + 1
        interval = 1 if reps == 1 else 6 if reps == 2 else round(int(s.get("interval", 1)) * ef)
    due = time.strftime("%Y-%m-%d", time.localtime(time.time() + interval * 86400))
    target["srs"] = {"ef": round(ef, 3), "interval": interval, "reps": reps, "due": due}

    personal = load("bank_personal.json", [])
    hit = False
    for e in personal:
        if e["term"].lower() == term:
            e["srs"] = target["srs"]
            hit = True
    if hit:
        save("bank_personal.json", personal)
    else:
        overrides = load("srs_seed.json", {})
        overrides[term] = target["srs"]
        save("srs_seed.json", overrides)
    return JSONResponse({"term": term, "srs": target["srs"]})


@app.get("/quiz/ear")
def quiz_ear(n: int = 10) -> dict:
    """Terms to hear at speed. Due terms first, then random."""
    today = time.strftime("%Y-%m-%d")
    entries = _all_bank_entries()
    due = [e for e in entries if (e.get("srs") or {}).get("due") and e["srs"]["due"] <= today]
    rest = [e for e in entries if e not in due]
    random.shuffle(due)
    random.shuffle(rest)
    picked = (due + rest)[:max(1, min(n, 25))]
    return {"items": [{"term": e["term"], "meaning": e.get("meaning"),
                       "example": e.get("example"), "plain": e.get("plain_alternative"),
                       "category": e.get("category")} for e in picked]}


@app.get("/quiz/sort")
def quiz_sort(n: int = 20) -> dict:
    """Half technical terms, half substitutable ones, shuffled. The frontend
    grades locally; the answer travels with each item."""
    half = max(2, min(n, 40)) // 2
    tech = random.sample(qs.TECHNICAL_TERMS, min(half, len(qs.TECHNICAL_TERMS)))
    subs = [e for e in _all_bank_entries()
            if e.get("plain_alternative") and e.get("category") in
            ("corporate_jargon", "phrasal_verb", "idiom", "sports_metaphor",
             "military_metaphor")]
    subs = random.sample(subs, min(half, len(subs)))
    items = ([{"term": t["term"], "answer": "technical", "why": t["why"]} for t in tech]
             + [{"term": e["term"], "answer": "substitutable",
                 "why": f"A plain word means the same: {e['plain_alternative']}."}
                for e in subs])
    random.shuffle(items)
    return {"items": items}


# ----------------------------------------------------------------------
# Frontend
# ----------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    path = os.path.join(HERE, "stage-time.html")
    if not os.path.exists(path):
        return HTMLResponse("<h1>stage-time.html is missing from this folder.</h1>",
                            status_code=404)
    with open(path, encoding="utf-8") as fh:
        # Never cache the page: every update to the file must show on reload.
        return HTMLResponse(fh.read(), headers={"Cache-Control": "no-store"})
