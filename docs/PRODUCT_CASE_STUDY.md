# Stage Time: from discovery to an AI-assisted prototype

## Overview

Stage Time explores structured public speaking practice through lessons, examples, roleplay, and feedback. Its intended audience is people preparing for situations such as interviews, stakeholder questions, and presentations. These are proposed use cases, not validated market segments.

## Process and contribution

The creator used BMAD for discovery and brainstorming, Claude for AI-assisted coding, and personal use to assess the resulting prototype. This is an independent project, not a claim of work performed for an employer or paying customer. Original BMAD session exports are not included in this repository; this case study is a retrospective account, not a reconstructed research record.

Codex later assisted with source review, repository preparation, the public browser demo, and this portfolio presentation.

## Product hypothesis

People who want to speak more clearly may benefit from a private place to rehearse, a structure for their answers, and one actionable next step. The core learning loop is: teach, demonstrate, practise, review.

## Scope

The local app contains 29 lessons across five units, 35 frameworks, 153 questions, and 11 personas. Speech transcription, voice measurements, and language-model coaching support the learning experience. The public demo provides a lower-friction view of selected flows and the framework library.

## Decisions visible in the implementation

### Guided learning plus free practice

A sequential path gives the user a next action. Free practice allows focused rehearsal. The intended benefit is clearer direction; whether it improves engagement remains untested.

### Separate rules from model judgments

Pace and filler metrics use explicit logic. Language models support qualitative coaching and structure assessment. This makes the boundary between measurement and interpretation more visible, but neither transcription nor qualitative grading is guaranteed accurate.

### Local processing

The main speech and coaching components run locally. This reduces reliance on hosted paid APIs and keeps the analysis on the user's device, at the expense of setup and hardware requirements. Google Fonts and browser-provided voices may involve network services; the app is not presented as a guarantee of zero network traffic. Keeping a project inside OneDrive can also sync its local files according to the user's OneDrive settings.

### Optional-service fallbacks

Built-in questions and available measurements remain usable when optional services are off. The product must explain which feedback is unavailable. Such fallback behavior is an implementation characteristic, not evidence of production reliability under load.

## What has been demonstrated

- A functional prototype assembled through an AI-assisted development process.
- A structured speaking-practice experience with curriculum and roleplay.
- A separation of deterministic metrics and model-supported interpretation.
- Personal use by the creator.

## What has not been demonstrated

External usability, repeated use, improved speaking ability, scoring accuracy against expert ratings, commercial demand, cost savings, and business impact have not been measured.

## Next step

Conduct a small usability pilot and use observed behavior to prioritize changes. See [the proposed validation plan](VALIDATION_PLAN.md).

