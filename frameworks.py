"""
frameworks.py
Stage Time v4 - answer frameworks as data

Every framework is a short list of steps with a cue per step, the kinds of
question it fits, a worked example in the user's own world, the signpost
words a listener hears when it is being used, and a one-line brief for the
grader. Sources are named. Nothing here is presented as invented by the app.

Groups
  answer    shapes for a direct answer to a question
  story     shapes for an experience or an example
  analysis  shapes for explaining a situation or a choice
  hostile   moves for questions that carry an attack, a trap or a gap
  process   what to do in the two seconds before any of the above
"""

from __future__ import annotations

# What each question kind means. Drills and the roleplay draw questions by
# kind, and every framework declares which kinds it fits.
KINDS = {
    "opinion": "What do you think, should we, is it a good idea",
    "explain": "How does it work, walk me through it, teach me",
    "update": "Where are we, what is the status",
    "decision": "A or B, which one, trade-off",
    "behavioral": "Tell me about a time when",
    "hypothetical": "What would you do if",
    "analysis": "Why is this happening, what is going on",
    "recommend": "What do you recommend, what should we do",
    "numbers": "A specific figure or example you may not have",
    "two_part": "Two questions in one, both fair",
    "clean": "Tough but fair, no trap in it",
    "loaded": "Carries a false premise",
    "compound": "Two questions fused, one of them damning",
    "status": "Attacks your standing instead of your argument",
    "gotcha": "Demands a figure you cannot possibly have",
    "statement": "A speech with no question in it",
    "off_topic": "Not about the subject at all",
    "false_dilemma": "Only two options offered, both bad",
    "jargon": "Asked entirely in corporate shorthand",
}

FRAMEWORKS: list[dict] = [
    # ------------------------------------------------------------------
    # answer
    # ------------------------------------------------------------------
    {"id": "prep", "name": "PREP", "group": "answer",
     "tagline": "Point, Reason, Example, Point",
     "steps": [
         {"label": "Point", "cue": "Your answer in one plain sentence. No preface."},
         {"label": "Reason", "cue": "The single strongest reason it is true."},
         {"label": "Example", "cue": "One concrete case, number or moment that shows it."},
         {"label": "Point", "cue": "Say the answer again, shorter, and stop."},
     ],
     "best_for": ["opinion", "decision", "clean", "recommend"],
     "avoid": "Stories. PREP flattens a narrative into a claim.",
     "example_q": "Should analysts be allowed to draft client emails with AI tools?",
     "example_a": "Yes, with a human sign-off. The reason is where the hours go: drafting "
                  "takes the time, review carries the risk. Last quarter the pilot team "
                  "cut turnaround from two days to four hours with zero compliance "
                  "findings. So yes, allow it, and keep the sign-off.",
     "signposts": ["the reason is", "because", "for example", "so"],
     "time_s": 45,
     "source": "Toastmasters International; Matt Abrahams, Think Faster, Talk Smarter (2023).",
     "grader": "Answer in the first sentence, one reason, one concrete example, "
               "the answer restated at the end."},

    {"id": "three-two-one", "name": "3-2-1", "group": "answer",
     "tagline": "3 steps, 2 types, 1 thing",
     "steps": [
         {"label": "3 steps", "cue": "Break the topic into three chronological steps "
                                     "or parts of a process."},
         {"label": "2 types", "cue": "Split the subject into two categories, styles or "
                                     "approaches."},
         {"label": "1 thing", "cue": "Land on the single most important takeaway or "
                                     "core message."},
     ],
     "best_for": ["explain", "opinion", "recommend"],
     "avoid": "Questions that need a yes or no first. Give the answer, then use "
              "3-2-1 to support it.",
     "example_q": "How would you roll out automation to the reconciliation team?",
     "example_a": "Three steps: map the manual work, automate the two biggest queues, "
                  "then measure for a month before touching anything else. Two types "
                  "of task come out of the mapping: rule-based, which we automate, and "
                  "judgement-based, which we do not. The one thing that matters is that "
                  "the team owns the rules, not the vendor.",
     "signposts": ["three", "first", "second", "third", "two", "one thing",
                   "the one thing"],
     "time_s": 60,
     "source": "Vinh Giang, communication coach, the 3-2-1 method.",
     "grader": "Three ordered steps, then two categories, then one single takeaway. "
               "The counting should be audible."},

    {"id": "what-so-what", "name": "What, So What, Now What", "group": "answer",
     "tagline": "The fact, why it matters, what happens next",
     "steps": [
         {"label": "What", "cue": "The fact, finding or idea in one or two sentences."},
         {"label": "So what", "cue": "Why it matters to the people in front of you."},
         {"label": "Now what", "cue": "The next step, decision or ask."},
     ],
     "best_for": ["update", "analysis", "recommend", "opinion"],
     "avoid": "Nothing really. Abrahams calls it the Swiss Army knife.",
     "example_q": "What did the pilot show?",
     "example_a": "The pilot cleared eighty percent of exceptions without a human touch. "
                  "That matters because exceptions are where the overtime and the "
                  "errors both come from. Now I want approval to run it on the London "
                  "book for one quarter.",
     "signposts": ["that matters because", "which means", "so what", "now", "next"],
     "time_s": 45,
     "source": "Matt Abrahams, Think Faster, Talk Smarter (2023); Toastmasters magazine, "
               "September 2023.",
     "grader": "A clear fact first, an explicit reason it matters, then a concrete "
               "next step or ask."},

    {"id": "add", "name": "ADD", "group": "answer",
     "tagline": "Answer, Detail, Describe",
     "steps": [
         {"label": "Answer", "cue": "One direct sentence. Yes, no, a number, a name."},
         {"label": "Detail", "cue": "One specific example that makes it concrete."},
         {"label": "Describe", "cue": "Why that matters to the person asking."},
     ],
     "best_for": ["clean", "numbers", "decision", "opinion", "jargon"],
     "avoid": "Questions that are actually attacks. Use a hostile move first.",
     "example_q": "Is the vendor going to make the March date?",
     "example_a": "No, April. The detail: the entitlements review added three weeks "
                  "because two systems had no owner. Why it matters to you is that the "
                  "cutover moves out of quarter end, which is actually safer.",
     "signposts": ["yes", "no", "specifically", "for example", "which means",
                   "what that means for you"],
     "time_s": 30,
     "source": "Matt Abrahams, Think Faster, Talk Smarter (2023).",
     "grader": "A direct one-sentence answer first, one specific detail, then the "
               "relevance to the asker."},

    {"id": "rule-of-three", "name": "Rule of Three", "group": "answer",
     "tagline": "Three points, one support each",
     "steps": [
         {"label": "Name three", "cue": "Say there are three, and name them in one breath."},
         {"label": "Point one", "cue": "One sentence of support."},
         {"label": "Point two", "cue": "One sentence of support."},
         {"label": "Point three", "cue": "One sentence of support, then a one-line close."},
     ],
     "best_for": ["explain", "opinion", "recommend"],
     "avoid": "When you only have one real point. Padding to three is audible.",
     "example_q": "Why is onboarding so slow?",
     "example_a": "Three reasons. Documents: forty percent arrive incomplete. Handoffs: "
                  "each file crosses four teams. Systems: two of those teams re-key the "
                  "same data. Fix the documents first and the other two shrink.",
     "signposts": ["three", "first", "second", "third", "finally"],
     "time_s": 60,
     "source": "Classical rhetoric; VirtualSpeech, Rule of Three in speeches.",
     "grader": "Three points announced up front, each supported briefly, in order."},

    {"id": "answer-first", "name": "Answer First", "group": "answer",
     "tagline": "Headline, reasons, detail on request",
     "steps": [
         {"label": "Headline", "cue": "The recommendation or bottom line in one sentence."},
         {"label": "Reasons", "cue": "Two or three reasons, each one sentence, no overlap."},
         {"label": "Detail", "cue": "Offer the detail. Give it only if asked."},
     ],
     "best_for": ["recommend", "update", "decision"],
     "avoid": "Audiences that need the story before they will accept the answer. "
              "Use SCQA for those.",
     "example_q": "What should the steering committee decide today?",
     "example_a": "Approve phase two at the reduced scope. Three reasons: phase one hit "
                  "its numbers, the vendor risk is now contractually capped, and "
                  "waiting a quarter costs more than the reduced scope saves. I have "
                  "the figures behind each if you want them.",
     "signposts": ["bottom line", "my recommendation", "three reasons", "first",
                   "second", "third"],
     "time_s": 45,
     "source": "Barbara Minto, The Pyramid Principle. Also known as BLUF, bottom line up front.",
     "grader": "The conclusion comes first, followed by distinct reasons, with detail "
               "held back rather than front-loaded."},

    {"id": "scqa", "name": "SCQA", "group": "answer",
     "tagline": "Situation, Complication, Question, Answer",
     "steps": [
         {"label": "Situation", "cue": "The stable starting point everyone agrees on."},
         {"label": "Complication", "cue": "What changed or went wrong."},
         {"label": "Question", "cue": "The question that change raises, said out loud."},
         {"label": "Answer", "cue": "Your answer to it, then stop."},
     ],
     "best_for": ["recommend", "analysis", "update"],
     "avoid": "Quick questions. SCQA is a setup for a recommendation, not a reply.",
     "example_q": "Why are you asking for more budget?",
     "example_a": "We planned phase two on last year's volumes. Since then volumes are up "
                  "thirty percent and the manual backstop cannot absorb it. So the "
                  "question is whether we scale people or scale the automation. My "
                  "answer is automation, and that is what the extra budget buys.",
     "signposts": ["we started", "since then", "the question is", "my answer"],
     "time_s": 60,
     "source": "Barbara Minto, The Pyramid Principle (McKinsey).",
     "grader": "A shared starting point, a change, the question it raises stated "
               "explicitly, then a clear answer."},

    # ------------------------------------------------------------------
    # analysis
    # ------------------------------------------------------------------
    {"id": "ppf", "name": "Past, Present, Future", "group": "analysis",
     "tagline": "How we got here, where we are, what is next",
     "steps": [
         {"label": "Past", "cue": "What has been done, in one or two sentences."},
         {"label": "Present", "cue": "Where it stands now, including the blocker."},
         {"label": "Future", "cue": "The next step and when."},
     ],
     "best_for": ["update", "analysis", "explain"],
     "avoid": "Opinion questions. It describes, it does not argue.",
     "example_q": "Where are we on the new KYC workflow?",
     "example_a": "We finished the design and the first build in June. Right now it is "
                  "in testing and the blocker is the sanctions feed, which is late. "
                  "Next, the feed lands on the twelfth and we go live two weeks after.",
     "signposts": ["so far", "right now", "currently", "next", "by"],
     "time_s": 45,
     "source": "Toastmasters International, Table Topics structures.",
     "grader": "Clear chronology: what was done, where it stands including any blocker, "
               "what happens next with timing."},

    {"id": "psb", "name": "Problem, Solution, Benefit", "group": "analysis",
     "tagline": "Name it, fix it, show the gain",
     "steps": [
         {"label": "Problem", "cue": "The problem in one sentence, ideally with a number."},
         {"label": "Solution", "cue": "What you would do, in two or three concrete steps."},
         {"label": "Benefit", "cue": "What the room gains, stated plainly."},
     ],
     "best_for": ["hypothetical", "recommend", "opinion"],
     "avoid": "When you do not actually have a solution. Use Cause, Effect, Remedy "
              "to analyse instead.",
     "example_q": "What would you do if the exception queue doubled overnight?",
     "example_a": "The problem is that a doubled queue breaches the settlement window in "
                  "two days. I would triage by value, put the two senior analysts on "
                  "anything over a million, and switch the rest to the automated path. "
                  "The benefit is that the money at risk is handled first and the "
                  "window holds.",
     "signposts": ["the problem is", "what i would do", "the benefit", "which gets us"],
     "time_s": 60,
     "source": "Matt Abrahams, Think Faster, Talk Smarter (2023).",
     "grader": "A defined problem, a concrete solution, an explicit benefit to the audience."},

    {"id": "cer", "name": "Cause, Effect, Remedy", "group": "analysis",
     "tagline": "Why it happened, what it did, what fixes it",
     "steps": [
         {"label": "Cause", "cue": "The root cause, not the symptom."},
         {"label": "Effect", "cue": "What it is doing to the numbers or the people."},
         {"label": "Remedy", "cue": "The fix, and who owns it."},
     ],
     "best_for": ["analysis", "explain", "update"],
     "avoid": "When you are not sure of the cause. Say that instead of inventing one.",
     "example_q": "Why did settlement fails spike last week?",
     "example_a": "The cause was a reference data change on Tuesday that dropped a "
                  "field the matching engine needs. The effect was four hundred "
                  "unmatched trades and two late settlements. The remedy is a mandatory "
                  "field check on that feed, which Priya owns and lands Friday.",
     "signposts": ["the cause", "because", "the effect", "which meant", "the fix",
                   "the remedy"],
     "time_s": 60,
     "source": "Write Out Loud, impromptu speech outline patterns.",
     "grader": "Root cause named, consequences stated, a fix with an owner."},

    {"id": "pros-cons", "name": "Pros, Cons, Recommendation", "group": "analysis",
     "tagline": "Both sides, then your call",
     "steps": [
         {"label": "Pros", "cue": "The two strongest arguments for."},
         {"label": "Cons", "cue": "The two strongest arguments against."},
         {"label": "Recommendation", "cue": "Your call. Without this step it is a hedge."},
     ],
     "best_for": ["decision", "opinion", "recommend"],
     "avoid": "Questions with an obvious answer. Balance where none exists reads as evasion.",
     "example_q": "Should we build the reporting tool in-house or buy it?",
     "example_a": "For building: we own the roadmap and the data never leaves. Against: "
                  "it takes two engineers off the core platform for six months, and "
                  "vendors already have the regulatory templates. My recommendation is "
                  "buy, and keep the data layer in-house.",
     "signposts": ["on the one hand", "for", "against", "however", "my recommendation",
                   "on balance"],
     "time_s": 60,
     "source": "Write Out Loud, impromptu speech outline patterns, with the "
               "recommendation step added so it ends in a decision.",
     "grader": "Genuine arguments on both sides, then a clear recommendation."},

    {"id": "ccc", "name": "Compare, Contrast, Conclude", "group": "analysis",
     "tagline": "What they share, how they differ, what follows",
     "steps": [
         {"label": "Compare", "cue": "What the options have in common."},
         {"label": "Contrast", "cue": "The one or two differences that matter."},
         {"label": "Conclude", "cue": "What those differences imply."},
     ],
     "best_for": ["decision", "explain", "analysis"],
     "avoid": "Single-option questions.",
     "example_q": "How do the two vendors differ?",
     "example_a": "Both handle the volume and both pass the security review. They "
                  "differ on two things: one runs in our region, the other does not, "
                  "and only one has a live banking client. That points to vendor A, "
                  "unless data residency changes.",
     "signposts": ["both", "whereas", "the difference", "unlike", "which means",
                   "that points to"],
     "time_s": 60,
     "source": "Matt Abrahams, Think Faster, Talk Smarter (2023).",
     "grader": "Similarities, then the differences that matter, then a conclusion "
               "that follows from the differences."},

    {"id": "what-who-why", "name": "What, Who, Why", "group": "analysis",
     "tagline": "Define it, show it in use, say why it matters",
     "steps": [
         {"label": "What", "cue": "What the thing means, in your words."},
         {"label": "Who", "cue": "Who uses it and what happened when they did."},
         {"label": "Why", "cue": "Why the room should care or change anything."},
     ],
     "best_for": ["explain", "opinion"],
     "avoid": "Status questions.",
     "example_q": "What is straight-through processing and why does it matter?",
     "example_a": "It is a trade that settles with no human touching it after entry. "
                  "The Frankfurt desk runs at ninety-two percent straight-through and "
                  "has one analyst on exceptions; we run at seventy and have six. That "
                  "gap is the whole business case.",
     "signposts": ["it means", "is when", "for instance", "which is why", "that is why"],
     "time_s": 60,
     "source": "Ethos Debate, the best structure for impromptu speeches.",
     "grader": "A definition, a real use with an outcome, then the relevance."},

    {"id": "five-ws", "name": "Five Ws", "group": "analysis",
     "tagline": "Who, What, When, Where, Why",
     "steps": [
         {"label": "Who", "cue": "Who is involved."},
         {"label": "What", "cue": "What happened or what is proposed."},
         {"label": "When", "cue": "When, with a real date."},
         {"label": "Where", "cue": "Where, which system, team or market."},
         {"label": "Why", "cue": "Why it matters. Land on this one."},
     ],
     "best_for": ["update", "explain"],
     "avoid": "Opinions. It reports.",
     "example_q": "What is this change request?",
     "example_a": "Operations and Risk. A new four-eyes check on payments over five "
                  "million. From the first of November. The London payments hub "
                  "only. Because two near misses in Q3 got through on a single "
                  "approval.",
     "signposts": ["who", "what", "when", "where", "why", "because"],
     "time_s": 45,
     "source": "Journalistic convention; widely taught for impromptu structure.",
     "grader": "All five elements present, ending on why."},

    {"id": "local-global", "name": "Team, Firm, Industry", "group": "analysis",
     "tagline": "Zoom out in three steps",
     "steps": [
         {"label": "Team", "cue": "What it looks like where you sit."},
         {"label": "Firm", "cue": "What it looks like across the bank."},
         {"label": "Industry", "cue": "What it looks like everywhere. Then close."},
     ],
     "best_for": ["explain", "opinion", "analysis"],
     "avoid": "Narrow, specific questions.",
     "example_q": "Is manual reconciliation still a problem?",
     "example_a": "In my team it is a third of the week. Across the bank it is four "
                  "hundred people. Across the industry it is the single most "
                  "automated function of the last five years, which tells you where "
                  "this ends.",
     "signposts": ["in my team", "across the", "industry", "everywhere"],
     "time_s": 45,
     "source": "Write Out Loud, the local, national, international pattern, "
               "adapted to a workplace.",
     "grader": "Three widening lenses in order, closing on the widest."},

    # ------------------------------------------------------------------
    # story
    # ------------------------------------------------------------------
    {"id": "star", "name": "STAR", "group": "story",
     "tagline": "Situation, Task, Action, Result",
     "steps": [
         {"label": "Situation", "cue": "One or two sentences of context. No more."},
         {"label": "Task", "cue": "What you specifically were responsible for."},
         {"label": "Action", "cue": "What you did. First person, concrete verbs."},
         {"label": "Result", "cue": "What happened, with a number if one exists."},
     ],
     "best_for": ["behavioral"],
     "avoid": "Opinion questions. STAR turns a claim into a story nobody asked for.",
     "example_q": "Tell me about a time you had to change a stakeholder's mind.",
     "example_a": "The head of payments wanted to delay automation until after year "
                  "end. I owned the business case. I ran a two-week shadow test on his "
                  "own queue and walked him through his own numbers, not mine. He "
                  "approved a limited go-live in November and the queue dropped forty "
                  "percent before year end.",
     "signposts": ["the situation", "my role", "i was responsible", "so i", "i did",
                   "the result", "as a result"],
     "time_s": 90,
     "source": "Standard behavioural interview structure; Matt Abrahams also lists it.",
     "grader": "Brief context, a personal responsibility, first-person actions, a "
               "measurable result."},

    {"id": "soar", "name": "SOAR", "group": "story",
     "tagline": "Situation, Obstacle, Action, Result",
     "steps": [
         {"label": "Situation", "cue": "Context in one sentence."},
         {"label": "Obstacle", "cue": "The specific thing in the way."},
         {"label": "Action", "cue": "What you did about the obstacle."},
         {"label": "Result", "cue": "The outcome and what it proved."},
     ],
     "best_for": ["behavioral"],
     "avoid": "Stories where nothing was actually in the way.",
     "example_q": "Tell me about handling pressure.",
     "example_a": "Regulatory deadline, six weeks out. The obstacle was that the data "
                  "owner left mid-project with nothing documented. I rebuilt the "
                  "lineage from the code in ten days and had it signed off by Audit. "
                  "We filed on time and the lineage doc is now the standard.",
     "signposts": ["the obstacle", "the problem was", "in the way", "so i",
                   "the result"],
     "time_s": 90,
     "source": "Behavioural interview variant emphasising resilience (Treparo, "
               "answer frameworks beyond STAR).",
     "grader": "An obstacle clearly named, actions that address it, an outcome."},

    {"id": "starr", "name": "STARR", "group": "story",
     "tagline": "STAR plus Reflection",
     "steps": [
         {"label": "Situation", "cue": "Context in a sentence."},
         {"label": "Task", "cue": "Your responsibility."},
         {"label": "Action", "cue": "What you did."},
         {"label": "Result", "cue": "What happened, including if it went badly."},
         {"label": "Reflection", "cue": "One or two sentences on what you would do differently."},
     ],
     "best_for": ["behavioral"],
     "avoid": "Success stories. Reflection after a win sounds like false modesty.",
     "example_q": "Tell me about a time you got it wrong.",
     "example_a": "We were migrating the client master. I owned the cutover plan. I "
                  "scheduled it for a Friday to minimise disruption. It failed and we "
                  "had no weekend cover. Monday was ugly. What I do now is never cut "
                  "over into a period I cannot staff, and I say so in the plan.",
     "signposts": ["what i learned", "in hindsight", "what i do now", "differently"],
     "time_s": 90,
     "source": "Behavioural interview variant (Treparo, answer frameworks beyond STAR).",
     "grader": "A STAR story with an honest result and a specific, short reflection."},

    {"id": "car", "name": "CAR", "group": "story",
     "tagline": "Context, Action, Result, in thirty seconds",
     "steps": [
         {"label": "Context", "cue": "One sentence."},
         {"label": "Action", "cue": "One or two sentences, first person."},
         {"label": "Result", "cue": "One sentence with a number."},
     ],
     "best_for": ["behavioral", "numbers", "clean"],
     "avoid": "When the setup is genuinely complicated. Use STAR.",
     "example_q": "Give me one example of a process you improved.",
     "example_a": "Client onboarding took eleven days. I removed two duplicate "
                  "approvals and moved the document check to the front. Six days.",
     "signposts": ["i", "so i", "the result", "went from", "to"],
     "time_s": 30,
     "source": "Compressed STAR for follow-ups and short answers.",
     "grader": "Context, first-person action and a result in three or four sentences."},

    {"id": "before-event-result", "name": "Before, Event, Result", "group": "story",
     "tagline": "What it was, what changed, what it is now",
     "steps": [
         {"label": "Before", "cue": "The baseline, with a number if you have one."},
         {"label": "The event", "cue": "What changed and when."},
         {"label": "The result", "cue": "The new state, same measure as the baseline."},
     ],
     "best_for": ["update", "explain", "behavioral"],
     "avoid": "When nothing has actually changed yet.",
     "example_q": "What did the new control actually do?",
     "example_a": "Before, we caught about half of the duplicate payments and caught "
                  "them late. In March we added the pre-release match. Since then we "
                  "catch ninety-five percent, before the money moves.",
     "signposts": ["before", "then", "since then", "now", "went from"],
     "time_s": 45,
     "source": "Write Out Loud, impromptu speech outline patterns.",
     "grader": "A measured baseline, a change, and the after state measured the same way."},

    {"id": "smg", "name": "Story, Message, Gain", "group": "story",
     "tagline": "A short story, the point, what they get",
     "steps": [
         {"label": "Story", "cue": "A specific moment, thirty seconds at most."},
         {"label": "Message", "cue": "The point of the story in one sentence."},
         {"label": "Gain", "cue": "What the listener can take from it."},
     ],
     "best_for": ["opinion", "explain", "behavioral"],
     "avoid": "Numbers questions. Nobody wants a story about a figure.",
     "example_q": "Why do you care so much about plain language?",
     "example_a": "My first month, a VP said we should socialise the deck before we "
                  "tee it up with the SteerCo. I nodded and had no idea what to do "
                  "next. The message is that shorthand quietly excludes people. What "
                  "you gain by dropping it is a room where everyone can act.",
     "signposts": ["once", "my first", "the point is", "the message", "what you get"],
     "time_s": 60,
     "source": "Toastmasters International, impromptu speaking acronyms.",
     "grader": "A brief concrete story, one stated message, one gain for the listener."},

    {"id": "ieo", "name": "Idea, Emotion, Outcome", "group": "story",
     "tagline": "One idea, why they should care, where it leads",
     "steps": [
         {"label": "Idea", "cue": "The one thing you want them to remember."},
         {"label": "Emotion", "cue": "A short moment that makes them feel it."},
         {"label": "Outcome", "cue": "The action or future the idea points to."},
     ],
     "best_for": ["opinion", "recommend"],
     "avoid": "Technical explanations.",
     "example_q": "Say a few words to the team before go-live.",
     "example_a": "The idea is simple: this is the last month anyone re-keys a trade. "
                  "Remember February, Sam at his desk at nine at night typing "
                  "settlement instructions by hand. That ends Monday. Go home on time "
                  "and let the system do what it was built for.",
     "signposts": ["the idea", "remember", "imagine", "which means", "from now"],
     "time_s": 60,
     "source": "Toastmasters magazine, Speaking on the Spot, February 2025.",
     "grader": "One clear idea, a moment that carries feeling, a concrete outcome."},

    {"id": "feel-felt-found", "name": "Feel, Felt, Found", "group": "story",
     "tagline": "For pushback with emotion in it",
     "steps": [
         {"label": "Feel", "cue": "Name what they feel, without agreeing it is right."},
         {"label": "Felt", "cue": "Say that you, or others, felt the same."},
         {"label": "Found", "cue": "What you found that changed it, with evidence."},
     ],
     "best_for": ["statement", "opinion", "clean"],
     "avoid": "Overuse. Twice in one meeting and it sounds like a script.",
     "example_q": "This automation is going to cost people their jobs.",
     "example_a": "I understand that worry, and I take it seriously. The reconciliation "
                  "team felt exactly that in January. What they found is that nobody "
                  "left, the overtime did, and two of them now own the rules engine.",
     "signposts": ["i understand", "i hear", "felt the same", "what we found",
                   "what they found"],
     "time_s": 45,
     "source": "Classic objection-handling pattern from sales training.",
     "grader": "Acknowledgement of the feeling, shared experience, then evidence "
               "of what changed."},

    # ------------------------------------------------------------------
    # process
    # ------------------------------------------------------------------
    {"id": "the-beat", "name": "The Beat", "group": "process",
     "tagline": "Pause, Clarify, Respond, Bridge back",
     "steps": [
         {"label": "Pause", "cue": "Two seconds of silence. Breathe out, not in."},
         {"label": "Clarify", "cue": "If the question is unclear, ask one short question."},
         {"label": "Respond", "cue": "Pick one framework and use it."},
         {"label": "Bridge back", "cue": "End on the point you want the room to keep."},
     ],
     "best_for": ["clean", "loaded", "compound", "status", "gotcha", "statement",
                  "off_topic", "false_dilemma"],
     "avoid": "Nothing. This is what happens before every other framework.",
     "example_q": "Any hard question.",
     "example_a": "Silence for two seconds. Then: Do you mean the March figure or the "
                  "full year? Then the answer. Then: so the thing to hold onto is that "
                  "the trend is down.",
     "signposts": ["do you mean", "to be clear", "the thing to hold onto"],
     "time_s": 45,
     "source": "Winning Presentations, handling difficult questions; Matt Abrahams on "
               "the pause.",
     "grader": "Evidence of a beat before speaking, a clarification where needed, a "
               "structured response, and a closing line."},

    {"id": "know-feel-do", "name": "Know, Feel, Do", "group": "process",
     "tagline": "Ten seconds of planning before you speak",
     "steps": [
         {"label": "Know", "cue": "What should they understand when you stop?"},
         {"label": "Feel", "cue": "How should they feel about it?"},
         {"label": "Do", "cue": "What should they do next?"},
     ],
     "best_for": ["recommend", "update", "opinion"],
     "avoid": "Using it out loud. It is a private checklist, not a structure to announce.",
     "example_q": "Before any update to a senior audience.",
     "example_a": "Know: the date moved to April. Feel: relieved it is safer, not "
                  "alarmed. Do: approve the revised plan today. Then say exactly that.",
     "signposts": [],
     "time_s": 30,
     "source": "Toastmasters magazine, Improve Your Impromptu Speaking, September 2023.",
     "grader": "The answer leaves the listener with one thing to know, a clear tone, "
               "and one action."},

    # ------------------------------------------------------------------
    # hostile
    # ------------------------------------------------------------------
    {"id": "neutralise-answer-bridge", "name": "Neutralise, Answer, Bridge",
     "group": "hostile",
     "tagline": "The highest-value move in the app",
     "steps": [
         {"label": "Neutralise", "cue": "Repeat the question with the tone and the "
                                        "loaded words stripped out."},
         {"label": "Answer", "cue": "Answer the neutral version directly."},
         {"label": "Bridge", "cue": "One sentence to the point you want the room to keep. "
                                    "Only after a real answer."},
     ],
     "best_for": ["loaded", "clean", "statement", "false_dilemma"],
     "avoid": "Mild questions from a genuine questioner. Neutralising those reads "
              "as defensive.",
     "example_q": "Why does this team keep missing deadlines?",
     "example_a": "The question is whether our delivery dates are reliable. Two of "
                  "the last eight slipped, both on the same vendor dependency, and "
                  "that dependency is now gone. What I would ask you to watch is the "
                  "next two dates, which are ours alone.",
     "signposts": ["the question is", "what you are asking", "so the real question",
                   "what i would ask you to"],
     "time_s": 40,
     "source": "Media-training bridging (Acknowledge, Bridge, Communicate), with the "
               "neutral restatement from Stage Time's own lessons.",
     "grader": "A neutral restatement first, a direct answer to it, then a short bridge. "
               "Bridging before answering is a fail."},

    {"id": "name-the-premise", "name": "Name the Premise", "group": "hostile",
     "tagline": "For questions that smuggle in a false assumption",
     "steps": [
         {"label": "Name it", "cue": "Say what the question assumes, calmly."},
         {"label": "Correct it", "cue": "State what is actually true, briefly."},
         {"label": "Answer the real question", "cue": "The legitimate concern underneath."},
     ],
     "best_for": ["loaded"],
     "avoid": "Questions where the premise is basically fair. Manufacturing a "
              "grievance is also a fail.",
     "example_q": "Why did you cut corners on the risk assessment?",
     "example_a": "That assumes corners were cut. The assessment ran the full RCSA "
                  "process and Audit signed it. The fair question is whether it was "
                  "done fast, and yes, in three weeks, because we started it in "
                  "parallel with design rather than after.",
     "signposts": ["that assumes", "the premise", "what actually happened", "the fair "
                   "question", "the real question"],
     "time_s": 40,
     "source": "Effectiviology, loaded questions; Winning Presentations, the reframe.",
     "grader": "The false premise is named and corrected before answering, and the "
               "underlying legitimate concern is then answered."},

    {"id": "divide-and-answer", "name": "Divide and Answer", "group": "hostile",
     "tagline": "For two questions fused into one",
     "steps": [
         {"label": "Divide", "cue": "Say out loud that there are two questions."},
         {"label": "Answer one", "cue": "The first, on its own."},
         {"label": "Answer two", "cue": "The second, on its own. Then stop."},
     ],
     "best_for": ["compound", "two_part"],
     "avoid": "Single questions. Dividing what is not compound sounds like stalling.",
     "example_q": "Did you know about the delay and hide it from the client?",
     "example_a": "There are two questions there. Did we know about the delay: yes, "
                  "on the ninth. Did we hide it: no, the client had it in writing on "
                  "the tenth.",
     "signposts": ["two questions", "there are two", "first", "second", "the other"],
     "time_s": 30,
     "source": "Parliamentary practice of dividing the question; Stage Time lessons.",
     "grader": "Explicit division before answering, then both parts answered separately."},

    {"id": "concede-evidence", "name": "Concede, Evidence, Move On", "group": "hostile",
     "tagline": "For attacks on your standing, not your argument",
     "steps": [
         {"label": "Concede", "cue": "Give up the harmless part in half a sentence."},
         {"label": "Evidence", "cue": "Go straight to the evidence for the argument."},
         {"label": "Move on", "cue": "Return to the room. Do not defend your background."},
     ],
     "best_for": ["status"],
     "avoid": "Defending your credentials. The moment you do, the topic is you.",
     "example_q": "You have been here eight months. Why should anyone take this from you?",
     "example_a": "Eight months, that is right. The numbers are not mine, they are "
                  "the team's own queue data for the last year, and they show the "
                  "same thing every month. That is what I would ask the committee to "
                  "look at.",
     "signposts": ["that is right", "fair", "the numbers", "the evidence", "the data"],
     "time_s": 30,
     "source": "Winning Presentations, acknowledge and pivot; Stage Time hold-the-line drill.",
     "grader": "A brief concession, evidence for the argument, no defence of "
               "credentials or experience."},

    {"id": "honest-unknown", "name": "Honest Unknown", "group": "hostile",
     "tagline": "For the figure you do not have",
     "steps": [
         {"label": "Acknowledge", "cue": "Say cleanly that you do not have it. No apology."},
         {"label": "Boundary", "cue": "Say what you do know, and where the edge is."},
         {"label": "Commit", "cue": "Scope, date, channel: what, by when, how."},
         {"label": "Answer what you can", "cue": "The part of the question you can answer now."},
     ],
     "best_for": ["gotcha", "numbers"],
     "avoid": "Guessing. One follow-up exposes a guess, and it costs more than the gap.",
     "example_q": "What was the exact cost per exception in Q2?",
     "example_a": "I do not have the Q2 unit cost in front of me. I know the total "
                  "exception cost fell in Q2 and that volume rose. I will send the "
                  "exact figure and the top three drivers by email tomorrow. What I "
                  "can tell you now is that the trend is down.",
     "signposts": ["i do not have", "i don't have", "in front of me", "i will send",
                   "by", "what i can tell you"],
     "time_s": 30,
     "source": "Winning Presentations, four-step recovery for unanswerable questions.",
     "grader": "A clean admission with no apology, a boundary, a specific commitment "
               "with a date, and the answerable part answered. A guessed number is a fail."},

    {"id": "answer-bridge-close", "name": "Answer, Bridge, Close", "group": "hostile",
     "tagline": "Bridging done right",
     "steps": [
         {"label": "Answer", "cue": "Answer the question actually asked. One sentence."},
         {"label": "Bridge", "cue": "Then transition: what matters more is..."},
         {"label": "Close", "cue": "Land the point and stop. Do not invite a return."},
     ],
     "best_for": ["clean", "loaded", "off_topic", "false_dilemma"],
     "avoid": "Bridging first. That is what makes it read as dodging.",
     "example_q": "Is the project over budget?",
     "example_a": "Yes, by four percent. What matters more is where it went: the "
                  "whole overrun is the security review the regulator asked for, and "
                  "it is done. The remaining spend is on plan.",
     "signposts": ["yes", "no", "what matters more", "the bigger point",
                   "what is more important"],
     "time_s": 30,
     "source": "Media-training bridging (Acknowledge, Bridge, Communicate).",
     "grader": "A direct answer precedes the bridge. Both are present. The close does "
               "not reopen the question."},

    {"id": "find-the-question", "name": "Find the Question", "group": "hostile",
     "tagline": "For a speech with no question in it",
     "steps": [
         {"label": "Find it", "cue": "Say the one question hiding in the statement."},
         {"label": "Answer it", "cue": "Briefly."},
         {"label": "Return to the room", "cue": "Eyes to the audience, take the next question."},
     ],
     "best_for": ["statement"],
     "avoid": "Answering every point in the speech. That makes it a debate.",
     "example_q": "I have watched three of these programmes fail and every one of "
                  "them said what you are saying now.",
     "example_a": "I think the question is what makes this one different. Two things: "
                  "we are automating one queue, not the whole function, and the team "
                  "owns the rules. Happy to take the next question.",
     "signposts": ["i think the question", "the question in there", "if the question is"],
     "time_s": 30,
     "source": "Winning Presentations, the boundary; Stage Time lessons.",
     "grader": "One question extracted from the statement, answered briefly, "
               "then a return to the room."},

    {"id": "name-and-hold", "name": "Name and Hold", "group": "hostile",
     "tagline": "For the questioner who comes back a third time",
     "steps": [
         {"label": "Brief answer", "cue": "First return: a shorter answer than before."},
         {"label": "Name the pattern", "cue": "Second return: we have covered this, "
                                              "neutrally."},
         {"label": "Offer the channel", "cue": "Happy to go deeper after, one to one."},
         {"label": "Hold", "cue": "Do not renegotiate. Take the next question."},
     ],
     "best_for": ["clean", "loaded", "status"],
     "avoid": "Reopening the topic. Each reply should be shorter than the last.",
     "example_q": "You still have not answered my question about the vendor.",
     "example_a": "I have given the answer I have: the contract caps the risk. We have "
                  "been round this twice now, so let me offer to go through the "
                  "contract with you after this. Next question.",
     "signposts": ["as i said", "we have covered", "happy to", "after this", "next"],
     "time_s": 20,
     "source": "Stage Time clean-exit drill; Winning Presentations, the boundary.",
     "grader": "Replies shrink with each return, the pattern is named without heat, "
               "a private channel is offered, and the topic is not reopened."},

    {"id": "third-option", "name": "The Third Option", "group": "hostile",
     "tagline": "For questions that offer two bad choices",
     "steps": [
         {"label": "Reject the pair", "cue": "Those are not the only two options."},
         {"label": "Offer the third", "cue": "The option the question left out."},
         {"label": "Answer", "cue": "Why the third is the right one."},
     ],
     "best_for": ["false_dilemma"],
     "avoid": "Genuine binaries. If it really is A or B, pick one.",
     "example_q": "So do we cut the team or miss the deadline?",
     "example_a": "Neither. The third option is to cut scope: ship the two queues "
                  "that carry ninety percent of the volume on the date, and the "
                  "long tail a month later. Same team, same deadline, less risk.",
     "signposts": ["neither", "not the only", "the third option", "there is a third",
                   "a different option"],
     "time_s": 30,
     "source": "Stage Time lessons on loaded questions; standard false-dilemma handling.",
     "grader": "The dilemma is refused, a third option is offered, and it is justified."},

    {"id": "scope-and-path", "name": "Scope and Path", "group": "hostile",
     "tagline": "For off-topic or out-of-bounds questions",
     "steps": [
         {"label": "Acknowledge", "cue": "It is a fair question."},
         {"label": "Scope", "cue": "Why it does not belong here, in one sentence."},
         {"label": "Path", "cue": "Where and when it can be answered properly."},
     ],
     "best_for": ["off_topic"],
     "avoid": "Using it to duck a fair on-topic question. The room will notice.",
     "example_q": "While you are here, what is happening with the office move?",
     "example_a": "Fair question and I know people want to hear about it. It is not "
                  "mine to answer and it is not what this session is for. Facilities "
                  "are holding a session on Thursday and I will make sure the "
                  "invite goes round today.",
     "signposts": ["fair question", "not for today", "not mine to", "after this",
                   "the right place"],
     "time_s": 20,
     "source": "Winning Presentations, the boundary technique.",
     "grader": "Acknowledged, scoped out without dismissal, and a concrete path offered."},
]

BY_ID = {f["id"]: f for f in FRAMEWORKS}


def by_id(fid: str | None) -> dict | None:
    return BY_ID.get(fid or "")


def for_kind(kind: str) -> list[dict]:
    """Frameworks that fit a question kind, process group excluded."""
    hits = [f for f in FRAMEWORKS if kind in f["best_for"] and f["group"] != "process"]
    return hits or [BY_ID["prep"]]


def recommended(kind: str) -> str:
    """One default per kind. Hostile kinds map to their specific move."""
    table = {
        "loaded": "name-the-premise", "compound": "divide-and-answer",
        "two_part": "divide-and-answer", "status": "concede-evidence",
        "gotcha": "honest-unknown", "numbers": "add", "statement": "find-the-question",
        "off_topic": "scope-and-path", "false_dilemma": "third-option",
        "behavioral": "star", "update": "ppf", "hypothetical": "psb",
        "analysis": "cer", "decision": "pros-cons", "recommend": "answer-first",
        "explain": "three-two-one", "opinion": "prep", "clean": "answer-bridge-close",
        "jargon": "add",
    }
    return table.get(kind, "prep")


def brief(f: dict) -> str:
    """Compact text for a prompt: steps with cues and the grader line."""
    steps = "; ".join(f"{i + 1}. {s['label']}: {s['cue']}" for i, s in enumerate(f["steps"]))
    return f"{f['name']} ({f['tagline']}). Steps: {steps}. Grader: {f['grader']}"
