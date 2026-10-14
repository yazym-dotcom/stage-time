"""
content.py
Stage Time v3 - all content as data

Progression is data, not code. Adding a level means adding a row.
"""

LEVELS = [
    {"lvl": 1, "name": "Find your voice", "unlock_sessions": 0,
     "filler_tolerance": 4.0,
     "goal": "Read aloud without rushing. Get a baseline for your own voice."},
    {"lvl": 2, "name": "Hold the room", "unlock_sessions": 5,
     "filler_tolerance": 3.5,
     "goal": "Project, land your sentence endings, stop trailing off."},
    {"lvl": 3, "name": "Think on your feet", "unlock_sessions": 12,
     "filler_tolerance": 3.0,
     "goal": "Structure an answer while you speak it. Cut the hedging."},
    {"lvl": 4, "name": "Take the pressure", "unlock_sessions": 22,
     "filler_tolerance": 2.5,
     "goal": "Answer challenges without matching their energy."},
    {"lvl": 5, "name": "Own the stage", "unlock_sessions": 35,
     "filler_tolerance": 2.0,
     "goal": "Keynote grade. Hostile questions, no notes, voice holds."},
]

EXERCISES = [
    # Level 1
    {"id": "vowel-hold", "lvl": 1, "title": "Sustained vowel", "time": 8,
     "kind": "calibrate",
     "desc": "Hold a steady 'ah' for eight seconds at a comfortable pitch.",
     "prompt": "Breathe in, then hold 'ahhh' evenly until the timer stops. Do "
               "not push. This is the only reading that measures shake "
               "accurately, so keep the microphone where it always sits.",
     "rubric": "Baseline capture. Not scored."},

    {"id": "read-steady", "lvl": 1, "title": "Read aloud", "time": 60,
     "kind": "practice",
     "desc": "Read any paragraph out loud at a deliberate pace.",
     "prompt": "Pick a paragraph from anything nearby. Read it as if one "
               "person at the back needs every word. Slower than feels right.",
     "rubric": "Pace 130 to 150 WPM. Fillers under 4 percent."},

    {"id": "volume-ladder", "lvl": 1, "title": "Volume ladder", "time": 45,
     "kind": "practice",
     "desc": "One sentence, three deliberate levels.",
     "prompt": "Say 'This is the number that changes the decision' three times: "
               "close conversation, room of twenty, room of two hundred. Pause "
               "two seconds between each.",
     "rubric": "Loudness range 8 to 20 dB. No clipping."},

    {"id": "catch-speed", "lvl": 1, "title": "Catch it at speed", "time": 180,
     "kind": "decode",
     "desc": "Twenty terms at meeting pace. Type what each one means.",
     "prompt": "Play each clip once. Type the meaning. Recognition at 1.25x is "
               "the goal, because that is how fast people actually talk.",
     "rubric": "Recognition, not memorisation."},

    # Level 2
    {"id": "back-row", "lvl": 2, "title": "Back row test", "time": 60,
     "kind": "practice",
     "desc": "Hold projection for a full minute without straining.",
     "prompt": "Explain what you did at work yesterday, out loud, as if the "
               "room is thirty people deep. If your throat hurts afterwards you "
               "were straining, not projecting. It comes from breath.",
     "rubric": "Signal to noise above 18 dB for the full minute."},

    {"id": "land-last-three", "lvl": 2, "title": "Land the last three words",
     "time": 60, "kind": "practice",
     "desc": "Kill the fade at the end of your sentences.",
     "prompt": "Describe a process you know well. Give the last three words of "
               "every sentence the same weight as the first three. Most people "
               "fade. You will hear it in the score.",
     "rubric": "Trail off under 3 dB."},

    {"id": "say-it-plain", "lvl": 2, "title": "Say it plain", "time": 60,
     "kind": "practice",
     "desc": "Deliver a jargon-heavy idea in plain English.",
     "prompt": "Take the last update you gave at work and say it again with no "
               "corporate shorthand at all. No leverage, no socialise, no "
               "circle back. If a plain word exists, use it.",
     "rubric": "Corporate density under 2 per 100 words."},

    {"id": "substitution-test", "lvl": 2, "title": "The substitution test",
     "time": 90, "kind": "decode",
     "desc": "Sort twenty terms into technical or substitutable.",
     "prompt": "If a plain word means the same thing, it is jargon. If the "
               "plain version loses precision, it is technical language. "
               "Leverage fails. Idempotent passes.",
     "rubric": "Judgement, not vocabulary."},

    # Level 3
    {"id": "prep-impromptu", "lvl": 3, "title": "PREP impromptu", "time": 60,
     "kind": "practice",
     "desc": "Sixty seconds on a topic you have not prepared.",
     "prompt": "Point, reason, example, point. Say your point in one sentence, "
               "give one reason, give one concrete example, then say the point "
               "again and stop.",
     "rubric": "Structure visible. Fillers under 3 percent."},

    {"id": "lightning", "lvl": 3, "title": "Lightning answers", "time": 30,
     "kind": "qa",
     "desc": "Thirty seconds per question. No preface, no ramble.",
     "prompt": "Answer in the first sentence. No 'that is a great question', no "
               "warm up, no restating your credentials. Answer, one support, "
               "stop.",
     "rubric": "Directness. Under 90 words."},

    {"id": "say-you-dont-know", "lvl": 3, "title": "Say what you do not know",
     "time": 45, "kind": "qa",
     "desc": "Three questions you cannot possibly answer.",
     "prompt": "You will not have these numbers. Say so cleanly, offer the "
               "follow up, then answer the part you can. Guessing costs more "
               "than not knowing.",
     "rubric": "Clean admission scores full marks. Guessing scores zero."},

    {"id": "neutralise", "lvl": 3, "title": "Neutralise it", "time": 30,
     "kind": "hostile",
     "desc": "Five hostile questions. Only paraphrase them. Do not answer.",
     "prompt": "Repeat each question back with the hostility stripped out and "
               "the tone removed. This is the highest leverage move in the "
               "whole app: it buys the beat, protects the room from the "
               "framing, and forces you to find the real question.",
     "rubric": "Neutral restatement. Nothing else."},

    {"id": "spot-premise", "lvl": 3, "title": "Spot the premise", "time": 20,
     "kind": "hostile",
     "desc": "Ten questions, half loaded. Call it.",
     "prompt": "For each one say 'loaded, because' and name the assumption, or "
               "say 'clean'. Manufacturing a grievance where none exists is "
               "also a fail.",
     "rubric": "Correct identification both ways."},

    {"id": "ask-cleanly", "lvl": 3, "title": "Ask cleanly", "time": 45,
     "kind": "decode",
     "desc": "Ask what a term means without apologising for asking.",
     "prompt": "The persona will use a term you do not know. Ask what it means. "
               "Compare 'Sorry, I might be missing something, but what does "
               "that mean?' with 'What do you mean by throughput here?' Same "
               "question, entirely different read.",
     "rubric": "Scored on voice, not content. No volume drop, no hedging."},

    # Level 4
    {"id": "divide-question", "lvl": 4, "title": "Divide the question",
     "time": 30, "kind": "hostile",
     "desc": "Compound questions. Split them, answer both parts.",
     "prompt": "'Did you know about the delay and hide it from the client?' No "
               "denies both, yes admits both. Say out loud that there are two "
               "questions, then take them separately.",
     "rubric": "Explicit division before answering."},

    {"id": "hold-the-line", "lvl": 4, "title": "Hold the line", "time": 45,
     "kind": "hostile",
     "desc": "Status attack. Answer without defending your credentials once.",
     "prompt": "They will go after your experience, not your argument. Concede "
               "the harmless part and go straight to the evidence. The moment "
               "you defend your background, the topic is you.",
     "rubric": "Zero credential defence. Substance capped at 10 otherwise."},

    {"id": "two-audiences", "lvl": 4, "title": "Two audiences", "time": 60,
     "kind": "practice",
     "desc": "The same update twice, for two different rooms.",
     "prompt": "Give a sixty second project update for your US team. Then give "
               "the same update for a call with Mumbai and Frankfurt. The "
               "second one has no sports metaphors and no idioms in it at all.",
     "rubric": "Figurative density at 0 for the international take."},

    {"id": "the-bridge", "lvl": 4, "title": "The bridge", "time": 60,
     "kind": "hostile",
     "desc": "Hostile question. Acknowledge, answer, then bridge.",
     "prompt": "Answer the question asked before you transition. Bridging "
               "first is what makes it read as dodging. 'What is more "
               "important to understand is' only works after a real answer.",
     "rubric": "Answer precedes bridge. Both present."},

    # Level 5
    {"id": "do-not-match", "lvl": 5, "title": "Do not match", "time": 180,
     "kind": "hostile",
     "desc": "The persona escalates each turn. You do not.",
     "prompt": "Scored only on your voice. Hold your volume within 2 dB of "
               "your own average, keep pitch at or below your baseline, and "
               "slow down about ten percent. Calm is contagious in both "
               "directions.",
     "rubric": "Escalation delta flat across all turns."},

    {"id": "clean-exit", "lvl": 5, "title": "The clean exit", "time": 60,
     "kind": "hostile",
     "desc": "They come back after being answered. Twice.",
     "prompt": "First return: answer briefly, break eye contact, move on. "
               "Second: name the pattern neutrally and offer the private "
               "channel. Third: hold it and do not renegotiate.",
     "rubric": "Boundary held without a back and forth."},

    {"id": "bank-meeting", "lvl": 5, "title": "The bank meeting", "time": 240,
     "kind": "decode",
     "desc": "A VP who speaks entirely in corporate shorthand.",
     "prompt": "Four turns, heavy jargon, no explanations offered. Two "
               "outcomes score equally: you understood and answered, or you "
               "asked what it meant and then answered. Guessing wrong is the "
               "only fail.",
     "rubric": "Comprehension or a clean question. Both full marks."},

    {"id": "hold-under-fire", "lvl": 5, "title": "Hold under fire", "time": 180,
     "kind": "hostile",
     "desc": "Level five persona, full session, scored on pressure delta.",
     "prompt": "Everything at once. Loaded premises, a status attack, a "
               "question you cannot answer. Your content matters less here "
               "than whether your voice holds.",
     "rubric": "Pressure delta, not content."},
]

LESSONS = [
    {"id": "pace", "title": "Pace is a choice, not a speed",
     "body": "Conversational delivery sits between 130 and 150 words a minute. "
             "Newsreaders run near 110 because every word carries. When nerves "
             "hit you will drift toward 180 without noticing, because your "
             "sense of time compresses. The fix is not talking slowly. It is "
             "putting silence where the filler wanted to go.",
     "tip": "Mark one line per section and give it deliberate slowness."},

    {"id": "fillers", "title": "Replace fillers with silence",
     "body": "Um and uh are not the problem. They are the symptom of a gap "
             "between finishing a thought and starting the next one. Trying to "
             "suppress them directly makes it worse. Practise stopping "
             "instead: when you feel the filler coming, close your mouth and "
             "let two seconds pass. It feels enormous to you and reads as "
             "confident to everyone else.",
     "tip": "Fix one habit at a time. Fillers first, then pace."},

    {"id": "project", "title": "Project, do not strain",
     "body": "Volume comes from breath support, not from the throat. If your "
             "throat hurts after speaking you were straining. Speaking too "
             "quietly makes the audience work, and they eventually give up. "
             "Speaking too loudly throughout exhausts them. The target is that "
             "the back row hears you comfortably.",
     "tip": "If you can feel it in your throat, drop the effort into your ribs."},

    {"id": "volume-punctuation", "title": "Volume is punctuation",
     "body": "An analysis of TED talks with over a million views found the most "
             "popular speakers used about twenty percent more volume variation "
             "than the least popular, and the variation tracked what mattered "
             "in the content rather than being random. Flat volume tells the "
             "audience that nothing is important. Deliberate contrast marks "
             "what is.",
     "tip": "Drop your volume for the line you most want remembered."},

    {"id": "shake", "title": "Why your voice shakes",
     "body": "Vocal tremor is a four to eight hertz oscillation of the muscles "
             "around the larynx, and it gets worse with stress. It is "
             "physiology, not weakness. Most speakers settle within thirty "
             "seconds of hearing their own voice, which is why the fix is "
             "breath and an over-rehearsed opening rather than willpower. "
             "Stage Time only measures this properly on the sustained vowel "
             "drill, because normal speech has a syllable rate sitting in the "
             "same frequency band.",
     "tip": "Over-rehearse the first thirty seconds until it is automatic."},

    {"id": "beat", "title": "The two second beat",
     "body": "When a hard question lands, wait one to two seconds before you "
             "speak. It reads as thoughtful, not slow, and it buys your brain "
             "the time to choose a structure instead of blurting. Untrained "
             "speakers rush to fill the silence and talk themselves into "
             "trouble. Get comfortable with the gap.",
     "tip": "Breathe out on the beat, not in."},

    {"id": "answer-first", "title": "Answer first, then bridge",
     "body": "Give the direct answer before you transition to your message. A "
             "single sentence is enough. Bridging before answering is exactly "
             "what makes it read as dodging, and audiences catch it every "
             "time. Once you have answered, 'what is more important to "
             "understand is' does real work.",
     "tip": "Skip 'that is a great question'. Trainers disagree on it, so "
            "treat it as neutral rather than a crutch."},

    {"id": "hedges", "title": "The hedge audit",
     "body": "I think, sort of, kind of, maybe, just. Hedges reduce how sound "
             "your argument seems and how credible you seem, and the habit is "
             "usually unconscious. It comes from politeness or from feeling "
             "uncertain about the room rather than about the claim. But do not "
             "overcorrect to zero: confident speakers lose more credibility "
             "when they turn out to be wrong, while hedged claims support more "
             "durable trust. Hedge when you are actually uncertain.",
     "tip": "Target is low hedge density, not none."},

    {"id": "dont-know", "title": "Saying you do not know",
     "body": "Nobody expects you to have every answer, and guessing damages "
             "you more than the gap does. Three sentences: I do not have that "
             "in front of me. I will get it to you today. Here is the part I "
             "can answer now. Then move on. Do not get into a back and forth.",
     "tip": "Handle it once and take the next question."},

    {"id": "triage", "title": "Hostile, or just hard",
     "body": "Skeptics attack your ideas, bring evidence, and will listen to "
             "your answer. Hecklers attack you and do not care about decorum. "
             "Treating a tough questioner as an attacker is a self-inflicted "
             "wound, because the room saw a thoughtful question. Get this "
             "right in the first two seconds and everything after it is "
             "easier.",
     "tip": "Depersonalise, detach, defuse."},

    {"id": "neutralise", "title": "Neutralise before you answer",
     "body": "Repeat a hostile question back with the tone and the loaded "
             "language stripped out. It buys you the beat, it protects the "
             "room from the framing, and it forces you to find the actual "
             "question underneath the attack. This one move is worth more than "
             "any clever comeback.",
     "tip": "Then move your eyes to the room, not back to the questioner."},

    {"id": "loaded", "title": "Loaded questions",
     "body": "'Why did you cut corners on this report?' Answer it as asked and "
             "you have agreed that corners were cut. Address the premise "
             "first, then answer: 'I would want to be careful about the "
             "framing there. What happened was X. But to your underlying "
             "question: Y.' If the framing is only mildly unfavourable and the "
             "questioner is genuinely probing, naming it reads as defensive. "
             "Judgement, not reflex.",
     "tip": "Compound questions get divided. False dilemmas get a third option."},

    {"id": "jargon-status", "title": "Jargon is a status signal, backwards",
     "body": "Nine studies at Columbia Business School found that low status "
             "causally increases jargon use. People who feel insecure about "
             "how they will be perceived use more jargon, more acronyms, more "
             "legalese. Higher status people use less, because they are "
             "optimising for being understood. An analysis of 64,000 "
             "dissertation titles found more jargon from lower-ranked schools. "
             "Loading up on corporate language to sound like you belong "
             "signals the opposite of what you intend.",
     "tip": "The honest caveat: the same research found that identical words "
            "from a lower-status speaker are more likely to be dismissed as "
            "jargon. The field is not level. The answer is still less jargon."},

    {"id": "technical-vs-jargon", "title": "Technical language is not jargon",
     "body": "BPMN gateway, swimlane, straight-through processing, exception "
             "queue. These are precise and have no plain substitute, and using "
             "them correctly is competence. The test is simple: if a plain "
             "word means the same thing, it is jargon. If the plain version "
             "loses precision, it is technical language. Leverage fails the "
             "test because use is right there. Idempotent passes.",
     "tip": "Stage Time never flags your domain vocabulary. Only the "
            "substitutable kind."},

    {"id": "phrasal", "title": "Phrasal verbs are the hard part",
     "body": "Not vocabulary. Phrasal verbs. Run it by, push back on, loop me "
             "in, flesh it out, tee that up, socialise it first. The meaning "
             "is not predictable from the parts, the particle changes "
             "everything, and they come out unstressed and fast. Knowing what "
             "one means and catching it live are different skills, which is "
             "why the drills here are audio at 1.25 speed rather than "
             "flashcards.",
     "tip": "Sports and military metaphors are the other arbitrary lookup "
            "table. Ballpark, punt, curveball, war room. Nothing to reason out."},

    {"id": "table-it", "title": "Terms that reverse",
     "body": "In American English, tabling something means postponing it, and "
             "tabling a motion often kills it. In British English it means the "
             "opposite: putting it on the agenda for discussion. During the "
             "Second World War the British and American staffs had a long "
             "argument over a paper the British wanted to table, before both "
             "sides realised they wanted the same thing. On a call with London "
             "and New York, this is live.",
     "tip": "Never say it. Say postpone, or say add to the agenda."},

    {"id": "nodding-along", "title": "The cost of nodding along",
     "body": "Research on international meetings found both native and "
             "non-native speakers gloss over garbled idioms to keep things "
             "moving, and rarely correct each other. Polite, practical, and it "
             "prevents nothing. Two failure modes follow: some people stop "
             "participating out of low confidence, and others miss key details "
             "while trying to look like they followed. The second is more "
             "expensive, because the next three sentences depend on the one "
             "you missed.",
     "tip": "Ask in the moment or ask within the hour. Never carry it."},

    {"id": "how-to-ask", "title": "How to ask",
     "body": "The strongest version offers a guess: 'When you say throughput, "
             "do you mean cases closed per day?' That turns the question into "
             "a competence display and gets you a faster, more precise answer. "
             "The room version works too and is usually true: 'Can we define "
             "that for everyone before we go on?' Both are things senior "
             "people say constantly.",
     "tip": "Never open with sorry. It is not an apology, it is a question."},

    {"id": "prepare", "title": "Prepare the question you fear",
     "body": "List the tough questions someone might ask, including "
             "specifically the one you do not want anyone to ask. Write it in "
             "the exact hostile wording they would use, not a softened "
             "version. If you are thinking it, they are thinking it. Work out "
             "the answers while you are still writing the talk, because these "
             "questions are the best gap-finder you have. Then decide which "
             "ones you pre-empt inside the talk, since answering an objection "
             "before it is raised removes the weapon.",
     "tip": "Write the exit script for off-topic moments before you go on."},
]

PERSONAS = {
    "friendly": {"name": "Curious colleague", "level": 1, "jargon_level": 0,
                 "brief": "Genuinely interested. One clear question per turn."},
    "specifics": {"name": "The numbers person", "level": 2, "jargon_level": 1,
                  "brief": "Asks for a specific figure or a concrete example "
                           "you may not have."},
    "two-part": {"name": "The multi-tasker", "level": 3, "jargon_level": 1,
                 "brief": "Two part questions, one part slightly off topic."},
    "premise": {"name": "The challenger", "level": 4, "jargon_level": 1,
                "brief": "Challenges the premise of whatever answer was just "
                         "given."},
    "loader": {"name": "The Loader", "level": 5, "jargon_level": 1,
               "hostile": True,
               "brief": "Every question carries a false premise. Escalates if "
                        "the user answers inside the frame."},
    "bundler": {"name": "The Bundler", "level": 5, "jargon_level": 1,
                "hostile": True,
                "brief": "Fuses two questions, one of them damning. Escalates "
                         "if the user answers only one."},
    "status": {"name": "The Status Checker", "level": 5, "jargon_level": 1,
               "hostile": True,
               "brief": "Attacks experience and standing, never the argument. "
                        "Escalates if the user defends their credentials."},
    "speechmaker": {"name": "The Speechmaker", "level": 5, "jargon_level": 1,
                    "hostile": True,
                    "brief": "Delivers long statements with no question in "
                             "them. Escalates if the user tries to answer."},
    "auditor": {"name": "The Auditor", "level": 5, "jargon_level": 2,
                "hostile": True,
                "brief": "Demands exact figures the user cannot possibly have. "
                         "Escalates if the user guesses."},
    "returner": {"name": "The Returner", "level": 5, "jargon_level": 1,
                 "hostile": True,
                 "brief": "Comes back to the same point after being answered, "
                          "twice. Escalates if the user reopens it."},
    "vp": {"name": "The bank VP", "level": 5, "jargon_level": 2,
           "brief": "Skeptical operations VP who speaks entirely in corporate "
                    "shorthand. Never explains a term. Not personally hostile."},
}

SCENARIOS = {
    "interview": "A structured job interview for a senior product role.",
    "stakeholder": "A steering committee reviewing your automation project.",
    "audience": "Audience questions after a conference talk.",
    "pitch": "An internal pitch for funding a second phase.",
    "townhall": "A town hall where people are worried about their jobs.",
}

# The order frameworks are introduced by the daily plan. Weak ones come back
# before new ones are added.
CURRICULUM = [
    "prep", "three-two-one", "what-so-what", "add", "answer-first", "ppf",
    "honest-unknown", "star", "psb", "neutralise-answer-bridge",
    "name-the-premise", "divide-and-answer", "concede-evidence",
    "answer-bridge-close", "cer", "pros-cons", "third-option",
    "find-the-question", "name-and-hold", "scqa", "ccc", "soar", "rule-of-three",
]

# Which drills the daily plan draws from at each level, in rotation.
PLAN_DRILLS = {
    1: ["read-steady", "volume-ladder", "lightning"],
    2: ["land-last-three", "back-row", "say-it-plain", "lightning"],
    3: ["say-you-dont-know", "neutralise", "spot-premise", "prep-impromptu", "ask-cleanly"],
    4: ["divide-question", "hold-the-line", "the-bridge", "two-audiences"],
    5: ["do-not-match", "clean-exit", "hold-under-fire", "bank-meeting"],
}

# Which persona the daily plan puts you in front of at each level.
PLAN_PERSONAS = {
    1: ["friendly"], 2: ["specifics", "friendly"], 3: ["two-part", "premise"],
    4: ["loader", "bundler", "status"], 5: ["auditor", "speechmaker", "returner", "vp", "loader"],
}

# A neutral passage of about 140 words, one minute at conversational pace,
# for the calm read that becomes the steadiness baseline.
READ_PASSAGE = (
    "Every process in a bank starts as a conversation between two people who "
    "need the same thing done twice. The first time, it is a favour. The second "
    "time, it is a habit. By the tenth time, someone writes it down, and the "
    "written version quietly becomes the rule. Nobody decides that this is how "
    "it will work; it simply keeps working, until the day it does not. That is "
    "usually the day a new person arrives and asks why. The honest answer is "
    "that nobody remembers. The useful answer is to map it: who touches the "
    "work, in what order, and what they are waiting for. Most of the waiting "
    "turns out to be for information that already exists somewhere else. Once "
    "you can see that, the fix is rarely a new system. It is a shorter path "
    "between the people who already have what each other needs."
)
