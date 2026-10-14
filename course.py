"""
course.py
Stage Time v5 - the guided path, as data

Five units, twenty-nine lessons, in order. Every lesson teaches one thing,
shows a model answer where one exists, has the learner try it, and marks
itself done. The next lesson unlocks when the previous one is finished, so
the home page always has exactly one thing to do next.

A lesson:
  id, unit, title, goal      what the learner will be able to do after it
  minutes                    honest estimate, used to size a day
  teach                      two to four sentences in the app's own voice
  teach_from                 id of a written lesson in content.LESSONS to show
  framework                  id in frameworks.py; its steps and example are shown,
                             and the character speaks the example as the demo
  demo                       {"question", "answer", "actor"} to override the demo
  try                        what the learner does:
      {"kind": "warmup"}
      {"kind": "record", "drill_id": ...}
      {"kind": "questions", "framework", "kinds", "n", "mode", "think_s", "answer_s"}
      {"kind": "drill", "drill_id": ..., "n": ...}   a question drill from DRILL_FLOWS
      {"kind": "roleplay", "persona", "scenario"}
      {"kind": "quiz", "drill_id": ...}
  pass                       score that earns a star (None for unscored lessons)
"""

from __future__ import annotations

UNITS = [
    {"n": 1, "name": "Find your voice",
     "goal": "Speak at a deliberate pace, without fillers, with a shape to every answer."},
    {"n": 2, "name": "Hold the room",
     "goal": "Project without straining, land your endings, drop the shorthand."},
    {"n": 3, "name": "Think on your feet",
     "goal": "Take the beat, answer first, and say what you do not know."},
    {"n": 4, "name": "Take the pressure",
     "goal": "Spot a loaded question and answer it without taking the bait."},
    {"n": 5, "name": "Own the stage",
     "goal": "Hold your voice steady while someone tries to move it."},
]

LESSONS: list[dict] = [
    # ---------------------------------------------------------------- Unit 1
    {"id": "u1-l1", "unit": 1, "title": "Your calm voice", "minutes": 4, "pass": None,
     "goal": "Give the app the reference it needs to measure steadiness.",
     "teach": "Every steadiness score is a comparison with your own voice on a calm day, "
              "never with a population average. Three held notes and a one-minute read "
              "give the app that reference. Sit where you normally sit, with the "
              "microphone where it normally is, and do not push.",
     "try": {"kind": "warmup"}},

    {"id": "u1-l2", "unit": 1, "title": "Pace is a choice", "minutes": 3, "pass": 60,
     "goal": "Read at 130 to 150 words a minute without it feeling slow.",
     "teach": "Nerves compress your sense of time, so you speed up without noticing. "
              "The fix is not talking slowly; it is putting silence where the next word "
              "wants to go. Read as if one person at the back needs every word.",
     "teach_from": "pace",
     "try": {"kind": "record", "drill_id": "read-steady"}},

    {"id": "u1-l3", "unit": 1, "title": "PREP: the shape of a clear answer", "minutes": 5, "pass": 60,
     "goal": "Answer an opinion question with a point, a reason, an example, and the point again.",
     "teach": "Most rambling comes from starting to talk before you know where you will "
              "stop. PREP gives you the stop: say the answer, give one reason, give one "
              "example, say the answer again. It fits almost any opinion or decision question.",
     "framework": "prep",
     "try": {"kind": "questions", "framework": "prep", "kinds": ["opinion", "decision"], "n": 2,
             "mode": "answer", "think_s": 5, "answer_s": 45}},

    {"id": "u1-l4", "unit": 1, "title": "Replace fillers with silence", "minutes": 4, "pass": 60,
     "goal": "Keep fillers under four percent by pausing instead of bridging.",
     "teach": "Um and uh are the sound of a gap between one thought and the next. "
              "Suppressing them directly makes it worse. Practise stopping instead: when "
              "you feel the filler coming, close your mouth and let two seconds pass.",
     "teach_from": "fillers",
     "framework": "prep",
     "try": {"kind": "questions", "framework": "prep", "kinds": ["opinion", "explain"], "n": 2,
             "mode": "answer", "think_s": 5, "answer_s": 45}},

    {"id": "u1-l5", "unit": 1, "title": "Project, do not strain", "minutes": 3, "pass": 60,
     "goal": "Move between three deliberate volume levels without your throat doing the work.",
     "teach": "Volume comes from breath, not from the throat. If it hurts afterwards you "
              "were straining. One sentence, three rooms: across a table, a room of "
              "twenty, a room of two hundred.",
     "teach_from": "project",
     "try": {"kind": "record", "drill_id": "volume-ladder"}},

    # ---------------------------------------------------------------- Unit 2
    {"id": "u2-l1", "unit": 2, "title": "Land the last three words", "minutes": 3, "pass": 60,
     "goal": "Finish sentences at the same weight you started them.",
     "teach": "Fading at the end of a sentence is the most common projection fault "
              "there is, and the audience hears it as doubt. Give the last three words "
              "of every sentence the same weight as the first three.",
     "teach_from": "volume-punctuation",
     "try": {"kind": "record", "drill_id": "land-last-three"}},

    {"id": "u2-l2", "unit": 2, "title": "3-2-1: stop rambling", "minutes": 5, "pass": 60,
     "goal": "Explain a topic as three steps, two types and one thing.",
     "teach": "When you are asked to explain something and have nothing prepared, count. "
              "Three steps in order, two kinds of the thing, and the one point that "
              "matters. The counting is audible, and that is the point: the listener "
              "always knows where you are.",
     "framework": "three-two-one",
     "try": {"kind": "questions", "framework": "three-two-one", "kinds": ["explain"], "n": 2,
             "mode": "answer", "think_s": 8, "answer_s": 60}},

    {"id": "u2-l3", "unit": 2, "title": "What, So What, Now What", "minutes": 5, "pass": 60,
     "goal": "Give an update as a fact, why it matters, and what happens next.",
     "teach": "Updates fail when they are all What. Say the fact, say why it matters to "
              "the people in the room, and say what you want to happen next. Three "
              "sentences is often enough.",
     "framework": "what-so-what",
     "try": {"kind": "questions", "framework": "what-so-what", "kinds": ["update", "analysis"], "n": 2,
             "mode": "answer", "think_s": 5, "answer_s": 45}},

    {"id": "u2-l4", "unit": 2, "title": "Say it plain", "minutes": 3, "pass": 60,
     "goal": "Deliver a work update with no corporate shorthand at all.",
     "teach": "Jargon reads as insecurity, not seniority. The test is simple: if a plain "
              "word means the same thing, it is jargon; if the plain version loses "
              "precision, it is technical language and you keep it.",
     "teach_from": "jargon-status",
     "try": {"kind": "record", "drill_id": "say-it-plain"}},

    {"id": "u2-l5", "unit": 2, "title": "The back row", "minutes": 3, "pass": 60,
     "goal": "Hold projection for a full minute.",
     "teach": "Projection you can hold for a minute is projection from the ribs. Explain "
              "what you did at work yesterday as if the room is thirty people deep, and "
              "notice where the effort sits.",
     "teach_from": "project",
     "try": {"kind": "record", "drill_id": "back-row"}},

    # ---------------------------------------------------------------- Unit 3
    {"id": "u3-l1", "unit": 3, "title": "The two-second beat", "minutes": 4, "pass": 60,
     "goal": "Wait one to two seconds before every answer, on purpose.",
     "teach": "When a question lands, the untrained reflex is to fill the silence. Wait. "
              "One to two seconds reads as thoughtful, buys your brain the time to pick "
              "a structure, and is measured here: the app times the pause before your "
              "first word.",
     "teach_from": "beat",
     "framework": "add",
     "try": {"kind": "questions", "framework": "add", "kinds": ["opinion", "decision", "numbers"], "n": 3,
             "mode": "answer", "think_s": 0, "answer_s": 30}},

    {"id": "u3-l2", "unit": 3, "title": "Answer first, then bridge", "minutes": 4, "pass": 60,
     "goal": "Give the direct answer before you move to your message.",
     "teach": "Bridging before answering is exactly what makes it read as dodging. One "
              "sentence of real answer first, then the transition to the point you want "
              "the room to keep, then stop.",
     "teach_from": "answer-first",
     "framework": "answer-bridge-close",
     "try": {"kind": "questions", "framework": "answer-bridge-close", "kinds": ["clean"], "n": 2,
             "mode": "answer", "think_s": 3, "answer_s": 30}},

    {"id": "u3-l3", "unit": 3, "title": "ADD: direct answers", "minutes": 4, "pass": 60,
     "goal": "Answer a direct question in one sentence, then one detail, then why it matters.",
     "teach": "A direct question wants a direct answer: yes, no, a number, a name. Then "
              "one specific detail that makes it concrete, then what it means for the "
              "person asking. Anything before the answer is a preface, and prefaces cost.",
     "framework": "add",
     "try": {"kind": "questions", "framework": "add", "kinds": ["numbers", "clean", "decision"], "n": 2,
             "mode": "answer", "think_s": 3, "answer_s": 30}},

    {"id": "u3-l4", "unit": 3, "title": "The hedge audit", "minutes": 4, "pass": 60,
     "goal": "Keep hedges under two and a half per hundred words without dropping to zero.",
     "teach": "I think, sort of, maybe, kind of. Hedges come from politeness or from "
              "uncertainty about the room, not about the claim. Say the claim, then the "
              "caveat if it is real. Hedge when you are actually uncertain, and only then.",
     "teach_from": "hedges",
     "framework": "prep",
     "try": {"kind": "questions", "framework": "prep", "kinds": ["opinion"], "n": 2,
             "mode": "answer", "think_s": 5, "answer_s": 45}},

    {"id": "u3-l5", "unit": 3, "title": "Saying you do not know", "minutes": 4, "pass": 60,
     "goal": "Admit a gap cleanly, commit to a follow-up, and answer the part you can.",
     "teach": "Guessing damages you more than the gap does, because one follow-up "
              "exposes it. Three sentences: I do not have that in front of me. I will "
              "send it by tomorrow. Here is the part I can answer now.",
     "teach_from": "dont-know",
     "framework": "honest-unknown",
     "try": {"kind": "questions", "framework": "honest-unknown", "kinds": ["gotcha"], "n": 2,
             "mode": "gap", "think_s": 3, "answer_s": 30}},

    {"id": "u3-l6", "unit": 3, "title": "Neutralise before you answer", "minutes": 4, "pass": 60,
     "goal": "Restate a hostile question with the tone stripped out, without answering it.",
     "teach": "Repeat a hostile question back with the loaded words removed. It buys the "
              "beat, protects the room from the framing, and forces you to find the "
              "real question underneath. In this lesson you only restate. Answering is "
              "the mistake.",
     "teach_from": "neutralise",
     "framework": "neutralise-answer-bridge",
     "try": {"kind": "questions", "framework": "neutralise-answer-bridge", "kinds": ["loaded", "status"], "n": 3,
             "mode": "paraphrase", "think_s": 2, "answer_s": 20}},

    {"id": "u3-l7", "unit": 3, "title": "Face the numbers person", "minutes": 5, "pass": 55,
     "goal": "Hold everything from this unit together, live, for four turns.",
     "teach": "A character who asks for a specific figure or example every time. Take "
              "the beat, answer first, and when you do not have the number, say so and "
              "commit. The recorder starts when they finish speaking.",
     "try": {"kind": "roleplay", "persona": "specifics", "scenario": "stakeholder"}},

    # ---------------------------------------------------------------- Unit 4
    {"id": "u4-l1", "unit": 4, "title": "Hostile, or just hard", "minutes": 3, "pass": 60,
     "goal": "Tell a loaded question from a tough but fair one in two seconds.",
     "teach": "Treating a tough questioner as an attacker is a self-inflicted wound, "
              "because the room saw a fair question. Manufacturing a grievance is as "
              "costly as missing a real one. Say loaded, and why, or say clean.",
     "teach_from": "triage",
     "try": {"kind": "drill", "drill_id": "spot-premise", "n": 4}},

    {"id": "u4-l2", "unit": 4, "title": "Name the premise", "minutes": 5, "pass": 60,
     "goal": "Name and correct a false premise before answering the real question.",
     "teach": "Why did you cut corners? Answer it as asked and you have agreed that "
              "corners were cut. Name what the question assumes, say what is actually "
              "true, then answer the fair question underneath.",
     "teach_from": "loaded",
     "framework": "name-the-premise",
     "try": {"kind": "questions", "framework": "name-the-premise", "kinds": ["loaded"], "n": 2,
             "mode": "hostile", "think_s": 3, "answer_s": 40}},

    {"id": "u4-l3", "unit": 4, "title": "Divide the question", "minutes": 4, "pass": 60,
     "goal": "Split a fused question out loud and answer each half on its own.",
     "teach": "Did you know about the delay and hide it from the client? No denies both "
              "and yes admits both. Say out loud that there are two questions, then take "
              "them one at a time.",
     "framework": "divide-and-answer",
     "try": {"kind": "questions", "framework": "divide-and-answer", "kinds": ["compound"], "n": 2,
             "mode": "hostile", "think_s": 3, "answer_s": 30}},

    {"id": "u4-l4", "unit": 4, "title": "Hold the line", "minutes": 4, "pass": 60,
     "goal": "Answer an attack on your standing without defending your credentials once.",
     "teach": "They will go after your experience, not your argument. Concede the "
              "harmless part in half a sentence and go straight to the evidence. The "
              "moment you defend your background, the topic is you.",
     "framework": "concede-evidence",
     "try": {"kind": "questions", "framework": "concede-evidence", "kinds": ["status"], "n": 2,
             "mode": "hostile", "think_s": 3, "answer_s": 40}},

    {"id": "u4-l5", "unit": 4, "title": "The third option", "minutes": 4, "pass": 60,
     "goal": "Refuse a false choice and offer the option the question left out.",
     "teach": "Do we cut the team or miss the deadline? Neither is a complete answer. "
              "Say the pair is not the only choice, offer the third option, and say why "
              "it is the right one.",
     "framework": "third-option",
     "try": {"kind": "questions", "framework": "third-option", "kinds": ["false_dilemma"], "n": 2,
             "mode": "hostile", "think_s": 3, "answer_s": 30}},

    {"id": "u4-l6", "unit": 4, "title": "Face The Loader", "minutes": 5, "pass": 55,
     "goal": "Four loaded questions in a row, without answering inside the frame.",
     "teach": "Every question this character asks carries a false premise, and they "
              "press harder if you accept it. Name it, correct it, answer the real "
              "question, and keep your voice where it was.",
     "try": {"kind": "roleplay", "persona": "loader", "scenario": "stakeholder"}},

    # ---------------------------------------------------------------- Unit 5
    {"id": "u5-l1", "unit": 5, "title": "Do not match", "minutes": 5, "pass": 55,
     "goal": "Keep volume, pitch and pace flat while the questioner escalates.",
     "teach": "Calm is contagious in both directions. The same objection comes back "
              "three times, sharper each time. You are scored only on whether your "
              "voice followed theirs: hold volume within two decibels, pitch at "
              "baseline, and slow down about ten percent.",
     "teach_from": "shake",
     "try": {"kind": "drill", "drill_id": "do-not-match"}},

    {"id": "u5-l2", "unit": 5, "title": "The clean exit", "minutes": 4, "pass": 55,
     "goal": "Close down a questioner who comes back a third time, without reopening it.",
     "teach": "First return: a shorter answer than before. Second: name the pattern "
              "without heat and offer the private channel. Third: hold it. Each reply "
              "shorter than the last; reopening the topic is the trap.",
     "framework": "name-and-hold",
     "try": {"kind": "drill", "drill_id": "clean-exit"}},

    {"id": "u5-l3", "unit": 5, "title": "Find the question", "minutes": 4, "pass": 60,
     "goal": "Pull one question out of a speech that has none, answer it, and move on.",
     "teach": "Some people make a statement and wait. Answering every point makes it a "
              "debate. Say the one question hiding in it, answer that briefly, and turn "
              "back to the room.",
     "framework": "find-the-question",
     "try": {"kind": "questions", "framework": "find-the-question", "kinds": ["statement"], "n": 2,
             "mode": "hostile", "think_s": 3, "answer_s": 30}},

    {"id": "u5-l4", "unit": 5, "title": "The bank meeting", "minutes": 5, "pass": 55,
     "goal": "Understand a VP who speaks entirely in shorthand, or ask cleanly, and answer.",
     "teach": "Two outcomes score equally: you understood the shorthand and answered, "
              "or you asked what it meant and then answered. Guessing wrong is the only "
              "fail. Never open with sorry.",
     "teach_from": "phrasal",
     "try": {"kind": "drill", "drill_id": "bank-meeting"}},

    {"id": "u5-l5", "unit": 5, "title": "Hold under fire", "minutes": 5, "pass": 55,
     "goal": "Everything at once: a loaded premise, a status attack, a figure you cannot have.",
     "teach": "Four hostile questions of different kinds, back to back. Pick the right "
              "move for each and keep your voice level. Your content matters less here "
              "than whether your voice holds.",
     "try": {"kind": "drill", "drill_id": "hold-under-fire"}},

    {"id": "u5-l6", "unit": 5, "title": "Face the Status Checker", "minutes": 5, "pass": 55,
     "goal": "A full session against someone who attacks who you are, not what you said.",
     "teach": "Concede the harmless part, go to the evidence, return to the room. If "
              "you defend your credentials once, the substance score is capped. This "
              "is the last lesson; after it the path repeats what you were weakest at.",
     "try": {"kind": "roleplay", "persona": "status", "scenario": "townhall"}},
]

BY_ID = {l["id"]: l for l in LESSONS}
ORDER = [l["id"] for l in LESSONS]


def unit_of(n: int) -> dict:
    return next(u for u in UNITS if u["n"] == n)
