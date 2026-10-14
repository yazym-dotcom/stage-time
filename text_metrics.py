"""
text_metrics.py
Stage Time v4 - deterministic transcript analysis

Everything here is arithmetic on a transcript. No model calls, no randomness,
no network. Same input always gives the same numbers, which is what makes the
scores explainable to the person who earned them.

Covers: pace, fillers, hedges, jargon density, latinate register, question
echo, counterattack markers, credential defence, framework signposts, and the
small detectors the question drills need: an admitted gap, a commitment, a
guess, an apology, a request for meaning, a loaded-or-clean call.
"""

from __future__ import annotations

import json
import re
from typing import Optional

# ----------------------------------------------------------------------
# Lexicons
# ----------------------------------------------------------------------

# Only words that are fillers wherever they appear. "like", "right" and
# "actually" are ordinary content words most of the time and are handled
# separately, using the punctuation a transcriber puts around a verbal tic.
FILLERS = [
    "you know", "i mean", "um", "uh", "erm", "ah", "er", "hmm", "mm",
    "basically", "literally", "so yeah", "okay so",
]

# Verbal tics that are only fillers with a comma or question mark around them.
TIC_PATTERNS = {
    "like": re.compile(r",\s*like[,.]?|\blike\s*,"),
    "right?": re.compile(r"\bright\s*\?"),
}

HEDGES = [
    "i am not sure", "i'm not sure", "i do not know if", "i don't know if",
    "i would say", "i would think", "it seems like", "i feel like",
    "more or less", "pretty much", "i think", "i guess", "i believe",
    "sort of", "kind of", "a little bit", "somewhat", "perhaps", "maybe",
    "possibly", "probably", "might", "could be", "hopefully",
]

# Honest statements of a knowledge gap are not hedging. Sentences containing
# any of these are excluded from the hedge count entirely.
GAP_MARKERS = [
    "do not have that", "don't have that", "in front of me", "not in front of",
    "i will follow up", "i'll follow up", "get that to you", "get it to you",
    "i do not know", "i don't know", "outside my area", "i do not have the",
    "i don't have the", "i would have to check", "i'd have to check",
    "i cannot give you an exact", "i can't give you an exact",
    "i do not have an exact", "i don't have an exact", "not something i have",
    "i would need to check", "i'd need to check",
]

# A commitment to close the gap: what, by when, how.
COMMIT_MARKERS = [
    "follow up", "get back to you", "come back to you", "send you", "send it",
    "send that", "send the", "get that to you", "get it to you", "in writing",
    "by email", "by tomorrow", "by end of", "by close of", "by the end of",
    "by monday", "by tuesday", "by wednesday", "by thursday", "by friday",
    "today", "tomorrow", "this afternoon", "after this", "after the meeting",
    "within the hour", "later today",
]

APOLOGY_MARKERS = [
    "sorry", "apologies", "i apologise", "i apologize", "forgive me",
    "silly question", "dumb question", "stupid question", "i might be missing",
    "i may be missing", "bear with me", "excuse my ignorance",
]

# Asking what a term means, cleanly or otherwise.
ASK_MARKERS = [
    "what do you mean", "what does that mean", "what does it mean",
    "what did you mean", "mean by", "define", "when you say", "do you mean",
    "can you clarify", "could you clarify", "not familiar with", "what exactly",
    "what is a", "what is an", "what is the", "what's a", "what's an",
    "what's the", "in plain", "spell that out", "what is that", "what's that",
    "meaning of", "unpack that", "walk me through what",
]

# The signature of a guess: a hedge word right before a number.
GUESS_RE = re.compile(
    r"\b(about|around|roughly|approximately|i'd say|i would say|probably|maybe|"
    r"something like|ballpark|i think it's|i think it is|guess|guessing|"
    r"if i had to guess|off the top of my head)\b[^.?!]{0,25}?"
    r"\b(\d[\d,.]*|one|two|three|four|five|six|seven|eight|nine|ten|eleven|"
    r"twelve|fifteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|"
    r"hundred|thousand|million|half|quarter|a few|several|dozens)\b"
)

COUNTERATTACK = [
    "with all due respect", "with respect", "as i already said",
    "as i said", "that is not fair", "that's not fair",
    "i never said", "you clearly", "if you had listened",
    "actually, no", "calm down", "you people", "obviously you",
    "that is ridiculous", "that's ridiculous", "you are wrong", "you're wrong",
]

# Over-formal words with a shorter, stronger swap. Register, not error.
LATINATE_SWAPS = {
    "utilise": "use", "utilize": "use", "utilisation": "use",
    "commence": "start", "commenced": "started", "commencing": "starting",
    "endeavour": "try", "endeavor": "try",
    "facilitate": "help", "facilitated": "helped",
    "terminate": "end", "terminated": "ended",
    "ascertain": "find out", "obtain": "get", "acquire": "get",
    "require": "need", "requires": "needs", "requirement": "need",
    "additional": "more", "sufficient": "enough", "numerous": "many",
    "demonstrate": "show", "demonstrates": "shows",
    "implement": "build", "implemented": "built",
    "subsequently": "then", "consequently": "so", "furthermore": "also",
    "approximately": "about", "currently": "now", "initiate": "start",
    "prior to": "before", "in order to": "to", "due to the fact that": "because",
    "at this point in time": "now", "in the event that": "if",
}

LATINATE_SUFFIXES = (
    "tion", "sion", "ment", "ance", "ence", "ity", "ise", "ize",
    "ate", "ous", "ive", "ial", "ual",
)

# Words that are long and Latinate but simply correct in a banking or process
# context. Never counted against register.
LATINATE_STOPLIST = {
    "operations", "operational", "regulation", "regulatory", "compliance",
    "automation", "documentation", "escalation", "reconciliation",
    "exception", "exceptions", "validation", "governance", "remediation",
    "authentication", "authorisation", "authorization", "transaction",
    "transactions", "allocation", "integration", "migration", "execution",
    "capacity", "quality", "priority", "activity", "capability",
}

ORDINALS = ["first", "second", "third", "finally", "lastly", "next", "then"]

_WORD = re.compile(r"[a-z0-9][a-z0-9'-]*")


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def norm(text: str) -> str:
    """Lowercase, hyphens and slashes to spaces, thousands separators removed,
    everything else that is not a letter, digit, apostrophe or space dropped.
    Used for phrase matching on both sides so that '30,000-foot view' in the
    bank and '30,000-foot view' in a transcript meet in the middle."""
    low = text.lower()
    low = re.sub(r"(\d),(?=\d)", r"\1", low)
    low = low.replace("-", " ").replace("/", " ")
    low = re.sub(r"[^a-z0-9' ]+", " ", low)
    return re.sub(r"\s+", " ", low).strip()


def words(text: str) -> list[str]:
    return _WORD.findall(norm(text))


def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    return [p for p in parts if p.strip()]


def _has_phrase(low: str, phrase: str) -> bool:
    """Whole-word phrase containment on already normalised text."""
    if not phrase:
        return False
    return re.search(r"(?<![a-z0-9'])" + re.escape(phrase) + r"(?![a-z0-9'])", low) is not None


def _phrase_pass(text: str, lexicon: list[str]) -> tuple[dict[str, int], str]:
    """Match longest phrases first and blank each hit so a multi word phrase
    is never also counted as its parts. Lexicon entries must be normalised.
    Returns counts and the masked text."""
    low = " " + norm(text) + " "
    counts: dict[str, int] = {}
    for term in sorted(lexicon, key=lambda t: -len(t)):
        pat = re.compile(r"(?<= )" + re.escape(term) + r"(?= )")
        n = len(pat.findall(low))
        if n:
            counts[term] = n
            low = pat.sub(" " + "\x00" * len(term) + " ", low)
    return counts, low


# ----------------------------------------------------------------------
# Pace and fluency
# ----------------------------------------------------------------------

def pace(text: str, duration_s: float) -> dict:
    n = len(words(text))
    wpm = (n / duration_s * 60.0) if duration_s > 0 else 0.0
    return {
        "word_count": n,
        "duration_s": round(duration_s, 2),
        "wpm": round(wpm, 1),
        "target_wpm": [130, 150],
    }


def fillers(text: str) -> dict:
    total = max(len(words(text)), 1)
    counts, _ = _phrase_pass(text, FILLERS)
    low = text.lower()
    for name, pat in TIC_PATTERNS.items():
        n = len(pat.findall(low))
        if n:
            counts[name] = counts.get(name, 0) + n
    hits = sum(counts.values())
    return {
        "counts": dict(sorted(counts.items(), key=lambda kv: -kv[1])),
        "total": hits,
        "pct": round(hits / total * 100, 2),
        "target_pct_max": 2.0,
    }


def hedges(text: str) -> dict:
    """Hedge density per 100 words, excluding honest knowledge gaps."""
    kept = []
    excluded = 0
    for s in sentences(text):
        low = s.lower()
        if any(m in low for m in GAP_MARKERS):
            excluded += 1
            continue
        kept.append(s)

    body = " ".join(kept)
    total = max(len(words(body)), 1)
    counts, _ = _phrase_pass(body, HEDGES)
    hits = sum(counts.values())
    return {
        "counts": dict(sorted(counts.items(), key=lambda kv: -kv[1])),
        "total": hits,
        "per_100w": round(hits / total * 100, 2),
        "sentences_excluded_as_honest_gaps": excluded,
        "target_per_100w_max": 2.5,
    }


def variety(text: str) -> dict:
    w = words(text)
    if not w:
        return {"unique_word_ratio": 0.0}
    return {"unique_word_ratio": round(len(set(w)) / len(w), 3)}


# ----------------------------------------------------------------------
# Jargon
# ----------------------------------------------------------------------

class JargonBank:
    """Loads jargon-bank-seed.json plus any personal additions."""

    def __init__(self, path: str):
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
        self.buckets: dict[str, str] = {}
        for bucket, cats in doc["buckets"].items():
            for c in cats:
                self.buckets[c] = bucket
        self.entries: dict[str, dict] = {}
        self.match: dict[str, str] = {}
        for e in doc["entries"]:
            self.add(e)

    @property
    def terms(self) -> list[str]:
        return list(self.entries)

    def add(self, entry: dict) -> None:
        key = entry["term"].lower()
        self.entries[key] = entry
        self.match[norm(entry["term"])] = key

    def bucket_of(self, key: str) -> str:
        cat = self.entries[key].get("category", "")
        return self.buckets.get(cat, "neutral")

    def analyze(self, text: str, audience: str = "us_internal") -> dict:
        total = max(len(words(text)), 1)
        counts, _ = _phrase_pass(text, list(self.match))

        by_bucket: dict[str, int] = {"corporate": 0, "figurative": 0,
                                     "neutral": 0, "flagged": 0}
        corporate_hits, figurative_hits, flagged_hits = [], [], []

        for normed, n in counts.items():
            key = self.match[normed]
            e = self.entries[key]
            b = self.bucket_of(key)
            by_bucket[b] = by_bucket.get(b, 0) + n
            row = {"term": e["term"], "count": n,
                   "plain": e.get("plain_alternative")}
            if b == "corporate":
                corporate_hits.append(row)
            elif b == "figurative":
                row["risk"] = e.get("risk")
                figurative_hits.append(row)
            elif b == "flagged":
                row["risk"] = e.get("risk")
                row["subtext"] = e.get("subtext")
                flagged_hits.append(row)

        def per100(n: int) -> float:
            return round(n / total * 100, 2)

        density = {k: per100(v) for k, v in by_bucket.items()}
        return {
            "audience": audience,
            "density_per_100w": density,
            "corporate_hits": sorted(corporate_hits, key=lambda r: -r["count"]),
            "figurative_hits": sorted(figurative_hits, key=lambda r: -r["count"]),
            "flagged_hits": flagged_hits,
            "latinate": latinate(text),
        }


def latinate(text: str) -> dict:
    """Register, not error. Reported, barely scored."""
    w = words(text)
    total = max(len(w), 1)
    swaps: dict[str, str] = {}
    low = text.lower()
    for term, plain in LATINATE_SWAPS.items():
        if re.search(r"(?<![a-z])" + re.escape(term) + r"(?![a-z])", low):
            swaps[term] = plain

    long_latinate = [
        x for x in w
        if len(x) >= 8
        and x not in LATINATE_STOPLIST
        and x.endswith(LATINATE_SUFFIXES)
    ]
    return {
        "ratio": round(len(long_latinate) / total, 3),
        "suggested_swaps": swaps,
        "note": "Register, not error. The plainer word usually lands harder.",
    }


# ----------------------------------------------------------------------
# Q&A specific
# ----------------------------------------------------------------------

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "of", "to", "in", "on",
    "for", "with", "is", "are", "was", "were", "be", "been", "do", "does",
    "did", "you", "your", "we", "our", "i", "my", "it", "that", "this",
    "what", "how", "why", "when", "who", "would", "could", "should", "can",
    "have", "has", "had", "will", "about", "from", "there", "here", "just",
}


def question_echo(question: str, answer: str, window: int = 18) -> dict:
    """Did the speaker repeat or reframe the question before answering?
    Content word overlap between the question and the answer's opening."""
    q = {w for w in words(question) if w not in STOPWORDS and len(w) > 3}
    a = words(answer)[:window]
    hit = {w for w in a if w in q}
    return {
        "echoed": len(hit) >= 2,
        "overlap_terms": sorted(hit),
        "window_words": window,
    }


def counterattack(text: str, window: int = 25) -> dict:
    """Flagged as evidence for the grader, never scored directly. One of
    these can be fine in context; three is a pattern."""
    opening = " ".join(words(text)[:window])
    hits = [p for p in COUNTERATTACK if _has_phrase(opening, norm(p))]
    return {"markers": hits, "window_words": window}


CREDENTIAL_PATTERNS = [
    r"\bi have (been|worked|spent)\b[^.?!]{0,30}\b(years?|months?)\b",
    r"\bi've (been|worked|spent|got|had)\b[^.?!]{0,30}\b(years?|months?)\b",
    r"(?<!in )\bmy (background|experience|track record|credentials|qualifications)\b",
    r"\bi have an? (degree|mba|certification|qualification|masters|phd)\b",
    r"\bi used to (work|run|lead|manage)\b",
    r"\bi am qualified\b", r"\bi'm qualified\b",
    r"\byears of experience\b", r"\byears in (this|the) (industry|business|bank)\b",
    r"\bi have run\b", r"\bi've run\b", r"\bi have led\b", r"\bi've led\b",
    r"\bi am not (just )?a student\b", r"\bi may be a student,? but\b",
    r"\bi know what i am talking about\b", r"\bi know what i'm talking about\b",
]


def credentials_defended(text: str) -> bool:
    """Detects the status attack trap: defending your own standing instead of
    supplying evidence. 'In my experience' is deliberately not included."""
    low = text.lower()
    return any(re.search(p, low) for p in CREDENTIAL_PATTERNS)


# ----------------------------------------------------------------------
# Frameworks and drill modes
# ----------------------------------------------------------------------

def signposts(text: str, framework: Optional[dict]) -> dict:
    """Which of the framework's listening cues appear, plus generic ordering
    markers. A proxy for structure when the model is off, a note when it is on."""
    low = norm(text)
    expected = list((framework or {}).get("signposts", []))
    found = [p for p in expected if _has_phrase(low, norm(p))]
    ordinals = [o for o in ORDINALS if _has_phrase(low, o)]
    return {
        "found": found,
        "expected": len(expected),
        "ratio": round(len(found) / len(expected), 2) if expected else None,
        "ordinal_markers": ordinals,
    }


def gap_admission(text: str) -> dict:
    """For the honest-unknown drill. A guess is a hedge word right before a
    number; a bare number is treated as knowledge."""
    low = text.lower()
    return {
        "admitted": any(m in low for m in GAP_MARKERS),
        "committed": any(m in low for m in COMMIT_MARKERS),
        "guessed": GUESS_RE.search(low) is not None,
        "apologised": any(m in low for m in APOLOGY_MARKERS),
    }


def asks_meaning(text: str, term: Optional[str] = None) -> dict:
    """For the ask-cleanly drill: did they ask what it means, name the term,
    and skip the apology."""
    low = text.lower()
    stripped = text.strip()
    term_named = bool(term) and _has_phrase(norm(text), norm(term))
    return {
        "asked": any(m in low for m in ASK_MARKERS),
        "term_named": term_named,
        "apologised": any(m in low for m in APOLOGY_MARKERS),
        "is_question": stripped.endswith("?")
                       or bool(re.match(r"^(what|which|when|do|does|can|could|is|are|"
                                        r"how|would|sorry)\b", low)),
    }


def classification(text: str) -> dict:
    """For the spot-the-premise drill: the first few words must carry the call."""
    head = " ".join(words(text)[:8])
    said = None
    if re.search(r"\bloaded\b", head):
        said = "loaded"
    elif re.search(r"\b(clean|fair|not loaded|straight|legitimate)\b", head):
        said = "clean"
    return {"said": said, "has_reason": "because" in text.lower()}


# Phrases that show a false premise was noticed rather than swallowed.
PREMISE_MARKERS = [
    "that assumes", "assumes that", "the assumption", "the premise", "the framing",
    "not the case", "that is not what happened", "that's not what happened",
    "there was no", "there were no", "nothing was", "no corners", "we did not",
    "we didn't", "i did not", "i didn't", "i would push back", "i'd push back",
    "the question is whether", "the fair question", "the real question",
    "let me correct", "to be clear", "that is not right", "that's not right",
    "not true", "i don't accept", "i do not accept", "two questions",
    "there are two", "neither", "not the only", "the third option",
    "i think the question", "if the question is",
]


def premise_addressed(text: str) -> bool:
    """Did the speaker name, divide or refuse the premise at any point?"""
    low = norm(text)
    return any(_has_phrase(low, norm(p)) for p in PREMISE_MARKERS)


ANSWERED_RE = re.compile(
    r"^(yes|no|yeah|nope)\b|\bthe answer is\b|\bbecause we\b|\bwe did not\b|"
    r"\bwe didn't\b|\bwe have not\b|\bwe haven't\b|\bi did not\b|\bi didn't\b"
)


def paraphrase_markers(text: str) -> dict:
    """For the neutralise drill, where answering is the mistake."""
    low = text.lower().strip()
    return {"answered": ANSWERED_RE.search(low) is not None}


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------

def analyze(text: str, duration_s: float, bank: Optional[JargonBank] = None,
            audience: str = "us_internal", question: Optional[str] = None,
            framework: Optional[dict] = None) -> dict:
    out = {
        "pace": pace(text, duration_s),
        "fillers": fillers(text),
        "hedges": hedges(text),
        "variety": variety(text),
    }
    if bank is not None:
        out["jargon"] = bank.analyze(text, audience=audience)
    if question is not None:
        out["question_echo"] = question_echo(question, text)
        out["counterattack"] = counterattack(text)
        out["credentials_defended"] = credentials_defended(text)
        out["premise_addressed"] = premise_addressed(text)
    if framework is not None:
        out["signposts"] = signposts(text, framework)
    return out


if __name__ == "__main__":
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    b = JargonBank(os.path.join(here, "jargon-bank-seed.json"))
    demo = ("So basically I think we should leverage the existing platform, "
            "um, and maybe circle back on the ballpark numbers. I would say "
            "we need to utilise what we have. I do not have that figure in "
            "front of me, I will follow up.")
    print(json.dumps(analyze(demo, 22.0, bank=b, audience="international"), indent=2))
