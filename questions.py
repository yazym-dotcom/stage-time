"""
questions.py
Stage Time v4 - the question bank and drill flows as data

Every question has a kind (see frameworks.KINDS). Hostile kinds carry the
ground truth the grader needs: the false premise, the two fused parts, the
legitimate concern underneath. That ground truth is what lets a small local
model grade reliably, and what lets the deterministic checks grade at all
when the model is off.
"""

from __future__ import annotations

import random

QUESTIONS: list[dict] = [
    # ------------------------------------------------------------------
    # opinion
    # ------------------------------------------------------------------
    {"id": "op01", "kind": "opinion", "topic": "work",
     "text": "Should analysts be allowed to use AI tools to draft client emails?"},
    {"id": "op02", "kind": "opinion", "topic": "work",
     "text": "Is it better to automate a broken process or fix it first?"},
    {"id": "op03", "kind": "opinion", "topic": "general",
     "text": "Should meetings default to twenty-five minutes instead of thirty?"},
    {"id": "op04", "kind": "opinion", "topic": "work",
     "text": "Do dashboards actually change decisions, or just decorate them?"},
    {"id": "op05", "kind": "opinion", "topic": "general",
     "text": "Is working from home better for junior staff, or worse?"},
    {"id": "op06", "kind": "opinion", "topic": "work",
     "text": "Should a bank ever let a vendor own the rules of a process?"},
    {"id": "op07", "kind": "opinion", "topic": "general",
     "text": "Early in a career, is it more useful to be a specialist or a generalist?"},
    {"id": "op08", "kind": "opinion", "topic": "work",
     "text": "Should operations teams be measured on speed or on error rate?"},
    {"id": "op09", "kind": "opinion", "topic": "general",
     "text": "Do people actually learn anything from post-mortems?"},
    {"id": "op10", "kind": "opinion", "topic": "work",
     "text": "Is process mapping worth the time it takes?"},
    {"id": "op11", "kind": "opinion", "topic": "general",
     "text": "Should everyone learn to code?"},
    {"id": "op12", "kind": "opinion", "topic": "work",
     "text": "Should the steering committee meet less often?"},
    {"id": "op13", "kind": "opinion", "topic": "general",
     "text": "Is it better to be early and wrong, or late and right?"},
    {"id": "op14", "kind": "opinion", "topic": "work",
     "text": "Should we tell the client about a delay before we know the new date?"},

    # ------------------------------------------------------------------
    # explain
    # ------------------------------------------------------------------
    {"id": "ex01", "kind": "explain", "topic": "work",
     "text": "How does a payment actually get from one bank to another?"},
    {"id": "ex02", "kind": "explain", "topic": "work",
     "text": "Explain reconciliation to a new graduate."},
    {"id": "ex03", "kind": "explain", "topic": "work",
     "text": "Walk me through how you would automate a manual check."},
    {"id": "ex04", "kind": "explain", "topic": "general",
     "text": "How do you make a genuinely good cup of coffee?"},
    {"id": "ex05", "kind": "explain", "topic": "work",
     "text": "How does a change request get approved here?"},
    {"id": "ex06", "kind": "explain", "topic": "general",
     "text": "Explain how to plan a trip to somewhere you have never been."},
    {"id": "ex07", "kind": "explain", "topic": "work",
     "text": "What is an exception queue and why does it exist?"},
    {"id": "ex08", "kind": "explain", "topic": "work",
     "text": "How does KYC work, in plain terms?"},
    {"id": "ex09", "kind": "explain", "topic": "general",
     "text": "How would you teach someone to run their first five kilometres?"},
    {"id": "ex10", "kind": "explain", "topic": "work",
     "text": "Explain what a control is to someone who has never worked in a bank."},
    {"id": "ex11", "kind": "explain", "topic": "work",
     "text": "How do you decide what to automate first?"},
    {"id": "ex12", "kind": "explain", "topic": "general",
     "text": "How does a good handover work?"},

    # ------------------------------------------------------------------
    # update
    # ------------------------------------------------------------------
    {"id": "up01", "kind": "update", "topic": "work",
     "text": "Where are we on the automation project?"},
    {"id": "up02", "kind": "update", "topic": "work",
     "text": "What is the status of the vendor onboarding?"},
    {"id": "up03", "kind": "update", "topic": "work",
     "text": "Give me the one-minute update on the exception queue."},
    {"id": "up04", "kind": "update", "topic": "work",
     "text": "How is the new team member settling in?"},
    {"id": "up05", "kind": "update", "topic": "work",
     "text": "What happened with the audit finding?"},
    {"id": "up06", "kind": "update", "topic": "work",
     "text": "Where did we land on the data migration?"},
    {"id": "up07", "kind": "update", "topic": "work",
     "text": "What is the state of the reporting tool?"},
    {"id": "up08", "kind": "update", "topic": "work",
     "text": "Where are we against the plan this quarter?"},

    # ------------------------------------------------------------------
    # decision
    # ------------------------------------------------------------------
    {"id": "de01", "kind": "decision", "topic": "work",
     "text": "Build or buy the reporting tool?"},
    {"id": "de02", "kind": "decision", "topic": "work",
     "text": "Should we go live in November or wait until January?"},
    {"id": "de03", "kind": "decision", "topic": "work",
     "text": "One big release, or three small ones?"},
    {"id": "de04", "kind": "decision", "topic": "general",
     "text": "Would you rather have a bigger team or a better tool?"},
    {"id": "de05", "kind": "decision", "topic": "work",
     "text": "Hire a contractor, or train someone internal?"},
    {"id": "de06", "kind": "decision", "topic": "work",
     "text": "Fix the data first, or the process first?"},
    {"id": "de07", "kind": "decision", "topic": "general",
     "text": "The safe option or the ambitious one?"},
    {"id": "de08", "kind": "decision", "topic": "work",
     "text": "Centralise the team, or keep it embedded in the business?"},

    # ------------------------------------------------------------------
    # behavioral
    # ------------------------------------------------------------------
    {"id": "be01", "kind": "behavioral", "topic": "work",
     "text": "Tell me about a time you changed a stakeholder's mind."},
    {"id": "be02", "kind": "behavioral", "topic": "work",
     "text": "Tell me about a time you got it wrong."},
    {"id": "be03", "kind": "behavioral", "topic": "work",
     "text": "Describe a time you had to deliver bad news."},
    {"id": "be04", "kind": "behavioral", "topic": "work",
     "text": "Tell me about a time you handled real pressure."},
    {"id": "be05", "kind": "behavioral", "topic": "work",
     "text": "Tell me about a process you improved."},
    {"id": "be06", "kind": "behavioral", "topic": "work",
     "text": "Tell me about a disagreement with a manager."},
    {"id": "be07", "kind": "behavioral", "topic": "work",
     "text": "Tell me about a time you had too little information to decide."},
    {"id": "be08", "kind": "behavioral", "topic": "general",
     "text": "Describe a time you had to learn something fast."},
    {"id": "be09", "kind": "behavioral", "topic": "work",
     "text": "Tell me about a time you said no."},
    {"id": "be10", "kind": "behavioral", "topic": "work",
     "text": "Tell me about a project that failed."},

    # ------------------------------------------------------------------
    # hypothetical
    # ------------------------------------------------------------------
    {"id": "hy01", "kind": "hypothetical", "topic": "work",
     "text": "What would you do if the exception queue doubled overnight?"},
    {"id": "hy02", "kind": "hypothetical", "topic": "work",
     "text": "What would you do if the vendor missed the go-live date?"},
    {"id": "hy03", "kind": "hypothetical", "topic": "work",
     "text": "What would you do if a senior stakeholder refused to adopt the new process?"},
    {"id": "hy04", "kind": "hypothetical", "topic": "work",
     "text": "What would you do if you found an error in a report already sent to the regulator?"},
    {"id": "hy05", "kind": "hypothetical", "topic": "general",
     "text": "What would you do with a free month?"},
    {"id": "hy06", "kind": "hypothetical", "topic": "work",
     "text": "What would you do if half the team left in the same quarter?"},
    {"id": "hy07", "kind": "hypothetical", "topic": "work",
     "text": "What would you do if the data you were given was clearly wrong?"},
    {"id": "hy08", "kind": "hypothetical", "topic": "work",
     "text": "What would you do if the budget was cut by a third tomorrow?"},

    # ------------------------------------------------------------------
    # analysis
    # ------------------------------------------------------------------
    {"id": "an01", "kind": "analysis", "topic": "work",
     "text": "Why did settlement fails spike last week?"},
    {"id": "an02", "kind": "analysis", "topic": "work",
     "text": "Why is onboarding so slow?"},
    {"id": "an03", "kind": "analysis", "topic": "work",
     "text": "Why do automation projects so often stall after the pilot?"},
    {"id": "an04", "kind": "analysis", "topic": "work",
     "text": "Why does the same error keep coming back?"},
    {"id": "an05", "kind": "analysis", "topic": "general",
     "text": "Why do most meetings run over?"},
    {"id": "an06", "kind": "analysis", "topic": "work",
     "text": "Why did adoption of the new tool drop after month two?"},
    {"id": "an07", "kind": "analysis", "topic": "work",
     "text": "Why is the overtime bill rising while volumes are flat?"},
    {"id": "an08", "kind": "analysis", "topic": "general",
     "text": "Why do people ignore process documentation?"},

    # ------------------------------------------------------------------
    # recommend
    # ------------------------------------------------------------------
    {"id": "re01", "kind": "recommend", "topic": "work",
     "text": "What should the steering committee decide today?"},
    {"id": "re02", "kind": "recommend", "topic": "work",
     "text": "What do you recommend we do about the vendor?"},
    {"id": "re03", "kind": "recommend", "topic": "work",
     "text": "What is your recommendation on the go-live date?"},
    {"id": "re04", "kind": "recommend", "topic": "work",
     "text": "If you could change one thing about how we run operations, what would it be?"},
    {"id": "re05", "kind": "recommend", "topic": "work",
     "text": "What should we stop doing?"},
    {"id": "re06", "kind": "recommend", "topic": "work",
     "text": "What do you recommend for the next phase?"},

    # ------------------------------------------------------------------
    # numbers (a figure or example you may not have; fair)
    # ------------------------------------------------------------------
    {"id": "nu01", "kind": "numbers", "topic": "work",
     "text": "What is the current daily volume through the exception queue?"},
    {"id": "nu02", "kind": "numbers", "topic": "work",
     "text": "Give me one concrete example of a task the automation removed."},
    {"id": "nu03", "kind": "numbers", "topic": "work",
     "text": "How many hours a week does the manual reconciliation take?"},
    {"id": "nu04", "kind": "numbers", "topic": "work",
     "text": "What was the error rate before, and what is it now?"},
    {"id": "nu05", "kind": "numbers", "topic": "work",
     "text": "How much did the pilot cost?"},
    {"id": "nu06", "kind": "numbers", "topic": "work",
     "text": "Name one client that has actually seen the benefit."},

    # ------------------------------------------------------------------
    # two_part (fair)
    # ------------------------------------------------------------------
    {"id": "tp01", "kind": "two_part", "topic": "work",
     "text": "What is the timeline, and who owns the risk if it slips?",
     "parts": ["What is the timeline?", "Who owns the risk if it slips?"]},
    {"id": "tp02", "kind": "two_part", "topic": "work",
     "text": "How much will it cost, and what happens if we do nothing?",
     "parts": ["How much will it cost?", "What happens if we do nothing?"]},
    {"id": "tp03", "kind": "two_part", "topic": "work",
     "text": "Which team is affected first, and how will you tell them?",
     "parts": ["Which team is affected first?", "How will you tell them?"]},
    {"id": "tp04", "kind": "two_part", "topic": "work",
     "text": "What went well in the pilot, and what did not?",
     "parts": ["What went well in the pilot?", "What did not go well?"]},
    {"id": "tp05", "kind": "two_part", "topic": "work",
     "text": "Who signs this off, and when?",
     "parts": ["Who signs it off?", "When?"]},
    {"id": "tp06", "kind": "two_part", "topic": "work",
     "text": "What is the biggest risk, and what is the mitigation?",
     "parts": ["What is the biggest risk?", "What is the mitigation?"]},

    # ------------------------------------------------------------------
    # clean (tough but fair; loaded is False)
    # ------------------------------------------------------------------
    {"id": "cl01", "kind": "clean", "topic": "work", "loaded": False,
     "text": "What is the single biggest risk in this plan?"},
    {"id": "cl02", "kind": "clean", "topic": "work", "loaded": False,
     "text": "What would make you abandon this project?"},
    {"id": "cl03", "kind": "clean", "topic": "work", "loaded": False,
     "text": "Why should this get funding ahead of the other three proposals?"},
    {"id": "cl04", "kind": "clean", "topic": "work", "loaded": False,
     "text": "What did you personally get wrong in phase one?"},
    {"id": "cl05", "kind": "clean", "topic": "work", "loaded": False,
     "text": "If this is so obvious, why has nobody done it before?"},
    {"id": "cl06", "kind": "clean", "topic": "work", "loaded": False,
     "text": "What is the weakest part of the business case?"},
    {"id": "cl07", "kind": "clean", "topic": "work", "loaded": False,
     "text": "How confident are you in the March date, honestly?"},
    {"id": "cl08", "kind": "clean", "topic": "work", "loaded": False,
     "text": "What happens to the team's jobs?"},

    # ------------------------------------------------------------------
    # loaded (false premise; loaded is True)
    # ------------------------------------------------------------------
    {"id": "lo01", "kind": "loaded", "topic": "work", "loaded": True,
     "text": "Why did you cut corners on the risk assessment?",
     "premise": "corners were cut",
     "real_question": "Was the risk assessment thorough enough?"},
    {"id": "lo02", "kind": "loaded", "topic": "work", "loaded": True,
     "text": "Why does this team keep missing deadlines?",
     "premise": "the team habitually misses deadlines",
     "real_question": "Are the delivery dates reliable?"},
    {"id": "lo03", "kind": "loaded", "topic": "work", "loaded": True,
     "text": "When did you decide to hide the cost overrun from the committee?",
     "premise": "an overrun was deliberately hidden",
     "real_question": "Was the committee told about costs in time?"},
    {"id": "lo04", "kind": "loaded", "topic": "work", "loaded": True,
     "text": "How many more people will lose their jobs because of your automation?",
     "premise": "people have already lost jobs because of it",
     "real_question": "What happens to the roles the automation touches?"},
    {"id": "lo05", "kind": "loaded", "topic": "work", "loaded": True,
     "text": "Why did you ignore the warnings from the risk team?",
     "premise": "warnings were ignored",
     "real_question": "How was the risk team's feedback handled?"},
    {"id": "lo06", "kind": "loaded", "topic": "work", "loaded": True,
     "text": "Why is the project still failing?",
     "premise": "the project is failing",
     "real_question": "Is the project on track?"},
    {"id": "lo07", "kind": "loaded", "topic": "work", "loaded": True,
     "text": "Why did you choose the most expensive vendor?",
     "premise": "the chosen vendor is the most expensive",
     "real_question": "Was the vendor selection value for money?"},
    {"id": "lo08", "kind": "loaded", "topic": "work", "loaded": True,
     "text": "What made you think you could skip user testing?",
     "premise": "user testing was skipped",
     "real_question": "Was there enough testing?"},
    {"id": "lo09", "kind": "loaded", "topic": "work", "loaded": True,
     "text": "Why did nobody on your team think about the client?",
     "premise": "client impact was not considered",
     "real_question": "How was client impact assessed?"},
    {"id": "lo10", "kind": "loaded", "topic": "work", "loaded": True,
     "text": "How long have you known the numbers were wrong?",
     "premise": "the numbers are wrong and you knew",
     "real_question": "Are the numbers reliable?"},
    {"id": "lo11", "kind": "loaded", "topic": "work", "loaded": True,
     "text": "Why are you rushing this through before the audit?",
     "premise": "it is being rushed to avoid the audit",
     "real_question": "Why is the timing what it is?"},
    {"id": "lo12", "kind": "loaded", "topic": "work", "loaded": True,
     "text": "Given that the pilot failed, why continue?",
     "premise": "the pilot failed",
     "real_question": "What did the pilot actually show?"},

    # ------------------------------------------------------------------
    # compound (two fused, one damning)
    # ------------------------------------------------------------------
    {"id": "co01", "kind": "compound", "topic": "work",
     "text": "Did you know about the delay and hide it from the client?",
     "parts": ["Did you know about the delay?", "Did you hide it from the client?"],
     "real_question": "Was the client told about the delay in time?"},
    {"id": "co02", "kind": "compound", "topic": "work",
     "text": "Was the vendor chosen before the tender, and did anyone benefit from that?",
     "parts": ["Was the vendor chosen before the tender?", "Did anyone benefit personally?"],
     "real_question": "Was the selection process fair?"},
    {"id": "co03", "kind": "compound", "topic": "work",
     "text": "Did the test fail, and is that why you changed the success criteria?",
     "parts": ["Did the test fail?", "Were the success criteria changed to cover it?"],
     "real_question": "Were the results reported honestly?"},
    {"id": "co04", "kind": "compound", "topic": "work",
     "text": "Is the project over budget, and did you approve the overspend yourself?",
     "parts": ["Is the project over budget?", "Was the overspend approved properly?"],
     "real_question": "Is spend under control and properly governed?"},
    {"id": "co05", "kind": "compound", "topic": "work",
     "text": "Are people being moved off the team, and are you avoiding telling them?",
     "parts": ["Are people being moved off the team?", "Are they being kept in the dark?"],
     "real_question": "Are staff being treated openly?"},
    {"id": "co06", "kind": "compound", "topic": "work",
     "text": "Has the regulator raised this, and are you keeping it from the committee?",
     "parts": ["Has the regulator raised it?", "Is the committee being kept informed?"],
     "real_question": "Is the committee fully informed?"},
    {"id": "co07", "kind": "compound", "topic": "work",
     "text": "Did the pilot miss its target, and did you report it as a success anyway?",
     "parts": ["Did the pilot miss its target?", "Was it reported honestly?"],
     "real_question": "Was the pilot reported honestly?"},
    {"id": "co08", "kind": "compound", "topic": "work",
     "text": "Did you sign off the data quality, and did you actually check it first?",
     "parts": ["Did you sign off the data quality?", "Did you check it before signing?"],
     "real_question": "Was the sign-off properly done?"},

    # ------------------------------------------------------------------
    # status (attack on standing)
    # ------------------------------------------------------------------
    {"id": "st01", "kind": "status", "topic": "work",
     "text": "You have been here eight months. Why should anyone take this from you?",
     "real_question": "Is the evidence sound regardless of who presents it?"},
    {"id": "st02", "kind": "status", "topic": "work",
     "text": "With respect, you are a consultant, not an operator. What do you actually "
             "know about running this desk?",
     "real_question": "Does the recommendation reflect how the desk really works?"},
    {"id": "st03", "kind": "status", "topic": "work",
     "text": "Have you ever run a team this size, or is this all theory?",
     "real_question": "Is the plan practical?"},
    {"id": "st04", "kind": "status", "topic": "work",
     "text": "You are still a student. Why are we listening to a student?",
     "real_question": "Is the analysis sound?"},
    {"id": "st05", "kind": "status", "topic": "work",
     "text": "The last three people in your role said exactly the same thing. What "
             "makes you different?",
     "real_question": "Why will this attempt succeed where others did not?"},
    {"id": "st06", "kind": "status", "topic": "work",
     "text": "Do you have any real banking experience, or just slides?",
     "real_question": "Is the recommendation grounded in how the bank operates?"},

    # ------------------------------------------------------------------
    # gotcha (a figure you cannot possibly have)
    # ------------------------------------------------------------------
    {"id": "go01", "kind": "gotcha", "topic": "work",
     "text": "What was the exact cost per exception in Q2?",
     "real_question": "Is the cost of exceptions going the right way?"},
    {"id": "go02", "kind": "gotcha", "topic": "work",
     "text": "What percentage of yesterday's fails were caused by reference data?",
     "real_question": "Do you understand the causes of fails?"},
    {"id": "go03", "kind": "gotcha", "topic": "work",
     "text": "What is the vendor's exact headcount on our account this week?",
     "real_question": "Is the vendor adequately staffed?"},
    {"id": "go04", "kind": "gotcha", "topic": "work",
     "text": "Quote me the regulator's paragraph that requires this.",
     "real_question": "Is this actually required?"},
    {"id": "go05", "kind": "gotcha", "topic": "work",
     "text": "What was the queue volume on the third Tuesday of last month?",
     "real_question": "Do you know the volumes?"},
    {"id": "go06", "kind": "gotcha", "topic": "work",
     "text": "What is the precise return on investment, to two decimal places?",
     "real_question": "Is the investment worth it?"},
    {"id": "go07", "kind": "gotcha", "topic": "work",
     "text": "How many keystrokes does the current process take per case?",
     "real_question": "How manual is the current process?"},
    {"id": "go08", "kind": "gotcha", "topic": "work",
     "text": "What did the Frankfurt desk spend on this last year?",
     "real_question": "How does our spend compare?"},

    # ------------------------------------------------------------------
    # statement (a speech, no question)
    # ------------------------------------------------------------------
    {"id": "sm01", "kind": "statement", "topic": "work",
     "text": "I have watched three of these programmes fail and every one of them "
             "said what you are saying now. The consultants come, the slides are "
             "beautiful, and two years later we are exactly where we started.",
     "real_question": "What makes this attempt different?"},
    {"id": "sm02", "kind": "statement", "topic": "work",
     "text": "Every automation project I have seen ends with the same people doing "
             "the same work plus a new system to babysit. That is just how it goes here.",
     "real_question": "Will this actually remove work?"},
    {"id": "sm03", "kind": "statement", "topic": "work",
     "text": "Honestly, this feels like a solution looking for a problem. The team "
             "was fine before anyone started measuring it.",
     "real_question": "Is there a real problem to solve?"},
    {"id": "sm04", "kind": "statement", "topic": "work",
     "text": "I remember when we did this in 2019. Different name, same idea, same "
             "promises. I just want that on the record.",
     "real_question": "What is different from 2019?"},

    # ------------------------------------------------------------------
    # off_topic
    # ------------------------------------------------------------------
    {"id": "of01", "kind": "off_topic", "topic": "work",
     "text": "While you are here, what is happening with the office move?"},
    {"id": "of02", "kind": "off_topic", "topic": "work",
     "text": "Can you comment on the rumours about the restructure?"},
    {"id": "of03", "kind": "off_topic", "topic": "work",
     "text": "What do you make of the new chief executive?"},
    {"id": "of04", "kind": "off_topic", "topic": "work",
     "text": "Is it true the bonus pool is being cut?"},

    # ------------------------------------------------------------------
    # false_dilemma
    # ------------------------------------------------------------------
    {"id": "fd01", "kind": "false_dilemma", "topic": "work",
     "text": "So do we cut the team, or miss the deadline?",
     "real_question": "How do we protect the date without harming the team?"},
    {"id": "fd02", "kind": "false_dilemma", "topic": "work",
     "text": "Either we automate everything now or we admit this was a waste of "
             "money. Which is it?",
     "real_question": "What is the right scope for automation?"},
    {"id": "fd03", "kind": "false_dilemma", "topic": "work",
     "text": "Is this a technology problem or a people problem?",
     "real_question": "What is actually causing the problem?"},
    {"id": "fd04", "kind": "false_dilemma", "topic": "work",
     "text": "Do we trust the vendor, or do we trust our own people?",
     "real_question": "How do we govern the vendor relationship?"},
    {"id": "fd05", "kind": "false_dilemma", "topic": "work",
     "text": "Are you asking for more money, or more time?",
     "real_question": "What does the project actually need?"},

    # ------------------------------------------------------------------
    # jargon (a bank VP who never explains a term). `term` is the bank
    # entry the listener is expected to catch or ask about.
    # ------------------------------------------------------------------
    {"id": "ja01", "kind": "jargon", "topic": "work", "term": "socialise",
     "text": "Can you socialise the numbers with Risk before we tee this up with the SteerCo?"},
    {"id": "ja02", "kind": "jargon", "topic": "work", "term": "ballpark",
     "text": "What is the ballpark on phase two, and can we level-set on scope first?"},
    {"id": "ja03", "kind": "jargon", "topic": "work", "term": "cob",
     "text": "I need you to run it by Finance and loop in Legal by COB."},
    {"id": "ja04", "kind": "jargon", "topic": "work", "term": "punt",
     "text": "Do we have the bandwidth to take this on, or do we punt to next quarter?"},
    {"id": "ja05", "kind": "jargon", "topic": "work", "term": "table it",
     "text": "Let us table it for now and circle back once we have a straw man for the vendor."},
    {"id": "ja06", "kind": "jargon", "topic": "work", "term": "sme",
     "text": "What is the low-hanging fruit here, and who is the SME for the exception queue?"},
    {"id": "ja07", "kind": "jargon", "topic": "work", "term": "boil the ocean",
     "text": "Can we get a quick win on the board before we boil the ocean?"},
    {"id": "ja08", "kind": "jargon", "topic": "work", "term": "bau",
     "text": "Where is the WIP on the migration, and is it BAU yet?"},
    {"id": "ja09", "kind": "jargon", "topic": "work", "term": "30,000-foot view",
     "text": "I want the 30,000-foot view before we get granular."},
    {"id": "ja10", "kind": "jargon", "topic": "work", "term": "full-court press",
     "text": "Are we going to move the needle this quarter, or is this a full-court "
             "press for next year?"},
    {"id": "ja11", "kind": "jargon", "topic": "work", "term": "optics",
     "text": "What is the ask, and do we have the optics right for the town hall?"},
    {"id": "ja12", "kind": "jargon", "topic": "work", "term": "sow",
     "text": "Flesh out the SOW and let us take it offline with the FTE numbers."},
]

BY_ID = {q["id"]: q for q in QUESTIONS}
HOSTILE_KINDS = {"loaded", "compound", "status", "gotcha", "statement", "off_topic",
                 "false_dilemma"}

# How a questioner comes back after being answered. {q} is the original question.
RETURNS = [
    "You still have not answered my question. {q}",
    "That is not what I asked. Let me put it to you again: {q}",
    "I will ask one more time, and I would like a straight answer. {q}",
]

# How the same objection sharpens across turns when the speaker takes the bait.
ESCALATIONS = [
    "{q}",
    "That is the kind of non-answer I expected. Let me be blunter. {q}",
    "I am going to say this once more, and I want the room to hear it. {q}",
]

# Terms that pass the substitution test: a plain word would lose precision.
TECHNICAL_TERMS = [
    {"term": "BPMN gateway", "why": "A specific diagram element. No plain word means the same."},
    {"term": "swimlane", "why": "A specific diagram convention for who does what."},
    {"term": "SLA", "why": "A contractual measure with a number attached."},
    {"term": "RCSA", "why": "A named regulatory process."},
    {"term": "KYC", "why": "A defined legal obligation."},
    {"term": "straight-through processing", "why": "A precise measure: trades needing no manual touch."},
    {"term": "exception queue", "why": "A specific workflow object."},
    {"term": "reconciliation break", "why": "A specific unmatched item."},
    {"term": "idempotent", "why": "A precise property: safe to run twice."},
    {"term": "settlement date", "why": "A contractual date."},
    {"term": "four-eyes check", "why": "A defined control type."},
    {"term": "maker-checker", "why": "A defined control pattern."},
    {"term": "key risk indicator", "why": "A defined metric type."},
    {"term": "cycle time", "why": "A measured interval."},
    {"term": "cutover", "why": "The specific moment of switching systems."},
    {"term": "regression test", "why": "A specific class of test."},
    {"term": "segregation of duties", "why": "A named control principle."},
    {"term": "audit trail", "why": "A specific record."},
    {"term": "batch window", "why": "A specific time slot in processing."},
    {"term": "materiality threshold", "why": "A defined number."},
    {"term": "run book", "why": "A specific document type."},
    {"term": "change freeze", "why": "A defined period."},
    {"term": "root cause analysis", "why": "A named method."},
    {"term": "T+1 settlement", "why": "A defined settlement cycle."},
    {"term": "sanctions screening", "why": "A defined regulatory check."},
]

# Which question kinds each roleplay persona opens with. The first turn of a
# roleplay is drawn from the bank so it is on-brief even when the model is not.
PERSONA_KINDS = {
    "friendly": ["opinion", "explain", "update"],
    "specifics": ["numbers"],
    "two-part": ["two_part"],
    "premise": ["clean", "loaded"],
    "loader": ["loaded"],
    "bundler": ["compound"],
    "status": ["status"],
    "speechmaker": ["statement"],
    "auditor": ["gotcha"],
    "returner": ["clean", "loaded"],
    "vp": ["jargon"],
}

# How each drill that needs questions runs. flow "questions" is a series of
# spoken answers; flow "quiz" is typed. mode drives the grader:
#   answer      answer a fair question inside a framework
#   hostile     answer a hostile question inside a framework
#   gap         admit the gap cleanly, commit, answer what you can
#   paraphrase  restate the question neutrally, do not answer it
#   classify    say "loaded" or "clean" and why
#   ask         ask what the term means, without apologising
#   comprehend  understand the jargon and answer, or ask, never guess
DRILL_FLOWS = {
    "lightning": {"flow": "questions", "mode": "answer",
                  "kinds": ["opinion", "explain", "update", "decision", "numbers", "clean"],
                  "n": 4, "think_s": 3, "answer_s": 30, "framework": "prep",
                  "choose_framework": True},
    "say-you-dont-know": {"flow": "questions", "mode": "gap", "kinds": ["gotcha"],
                          "n": 3, "think_s": 3, "answer_s": 30,
                          "framework": "honest-unknown"},
    "neutralise": {"flow": "questions", "mode": "paraphrase",
                   "kinds": ["loaded", "status", "false_dilemma", "statement"],
                   "n": 5, "think_s": 2, "answer_s": 20,
                   "framework": "neutralise-answer-bridge"},
    "spot-premise": {"flow": "questions", "mode": "classify", "kinds": ["loaded", "clean"],
                     "n": 6, "think_s": 2, "answer_s": 15, "balanced": True,
                     "framework": "name-the-premise"},
    "ask-cleanly": {"flow": "questions", "mode": "ask", "kinds": ["jargon"],
                    "n": 4, "think_s": 2, "answer_s": 20, "framework": None},
    "divide-question": {"flow": "questions", "mode": "hostile", "kinds": ["compound"],
                        "n": 3, "think_s": 3, "answer_s": 30,
                        "framework": "divide-and-answer"},
    "hold-the-line": {"flow": "questions", "mode": "hostile", "kinds": ["status"],
                      "n": 3, "think_s": 3, "answer_s": 45,
                      "framework": "concede-evidence"},
    "the-bridge": {"flow": "questions", "mode": "hostile",
                   "kinds": ["loaded", "clean", "false_dilemma"],
                   "n": 3, "think_s": 3, "answer_s": 45,
                   "framework": "answer-bridge-close"},
    "do-not-match": {"flow": "questions", "mode": "hostile",
                     "kinds": ["loaded", "status", "compound"],
                     "n": 3, "think_s": 2, "answer_s": 45, "series": "escalate",
                     "framework": "neutralise-answer-bridge"},
    "clean-exit": {"flow": "questions", "mode": "hostile", "kinds": ["loaded", "clean"],
                   "n": 3, "think_s": 2, "answer_s": 30, "series": "return",
                   "framework": "name-and-hold"},
    "bank-meeting": {"flow": "questions", "mode": "comprehend", "kinds": ["jargon"],
                     "n": 4, "think_s": 3, "answer_s": 45, "framework": "add"},
    "hold-under-fire": {"flow": "questions", "mode": "hostile",
                        "kinds": ["loaded", "status", "gotcha", "compound"],
                        "n": 4, "think_s": 2, "answer_s": 45, "framework": None,
                        "choose_framework": True},
    "catch-speed": {"flow": "quiz", "quiz": "ear", "n": 10},
    "substitution-test": {"flow": "quiz", "quiz": "sort", "n": 20},
}


def pick(kinds: list[str], n: int, exclude: set[str] | None = None,
         balanced: bool = False, rng: random.Random | None = None) -> list[dict]:
    """Draw n questions of the given kinds without repeats. balanced draws
    evenly across kinds, which the spot-premise drill needs so half are loaded."""
    rng = rng or random.Random()
    exclude = exclude or set()
    pools = {k: [q for q in QUESTIONS if q["kind"] == k and q["id"] not in exclude]
             for k in kinds}
    for k in pools:
        rng.shuffle(pools[k])
    out: list[dict] = []
    if balanced:
        i = 0
        while len(out) < n and any(pools.values()):
            k = kinds[i % len(kinds)]
            if pools[k]:
                out.append(pools[k].pop())
            i += 1
        rng.shuffle(out)
        return out
    flat = [q for k in kinds for q in pools[k]]
    rng.shuffle(flat)
    return flat[:n]
