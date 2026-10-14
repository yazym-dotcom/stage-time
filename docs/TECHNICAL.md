# Stage Time v5

A public speaking trainer that runs entirely on your own laptop. No account, no
API key, no recurring cost, and no audio ever leaves the machine.

Personal device only. Do not install this on a managed corporate laptop.

---

## What it measures

| | What | How |
|---|---|---|
| Pace | Words per minute against a 130 to 150 target | Deterministic |
| Fluency | Filler rate, tightening as levels rise | Deterministic |
| Volume | Signal to noise, loudness range, trail off, clipping | Deterministic |
| Steadiness | Jitter, shimmer, harmonics, 4 to 8 Hz tremor | Deterministic, against your own baseline |
| Language | Hedge density, jargon density, register | Deterministic |
| Composure | Beat before answering, escalation against your own earlier turns, counterattack phrases | Deterministic |
| Drill moves | Admitted gap, commitment, guess, apology, asked for meaning, loaded-or-clean call, premise named | Deterministic |
| Framework | Each step heard, in order; signposts blended in | Local model 60 percent, signposts 40 percent |
| Content | Directness, premise handling, substance | Local model, with ground truth |

Every question in the bank carries what the grader needs: the false premise it
smuggles in, the two questions it fuses, the legitimate concern underneath, the
shorthand term to catch. The model grades against that, and a cap it asks for
is only applied when a deterministic marker or the ground truth corroborates
it. If a loaded question's premise is never named in the answer, premise
handling is capped regardless of what the model says.

---

## Setup

```bash
# Windows: double-click start.bat        # Mac: ./start.sh
# Either one creates a venv outside the synced folder and installs requirements.txt

ffmpeg                          # winget install ffmpeg / brew install ffmpeg
ollama pull qwen2.5:3b          # coaching, grading, roleplay follow-ups, lookup
```

Open http://127.0.0.1:8000

The venv lives at `%LOCALAPPDATA%\stage-time\venv` on Windows and
`~/.stage-time/venv` on macOS. First start downloads the Whisper weights
(about 480 MB) in a background thread; `/health` reports `loading` until done.

Environment: `OLLAMA_URL` (default `http://127.0.0.1:11434`), `OLLAMA_MODEL`
(default `qwen2.5:3b`), `WHISPER_SIZE` (default `small`),
`STAGE_TIME_NO_BROWSER=1` to stop the launcher opening a browser.

---

## The interface

Four pages and one runner. **Today** is the guided path: onboarding on the
first visit (minutes a day, goal, microphone check), then the next lesson
with one button and the whole path underneath; **Practice** lists every drill
and the characters; **Library** holds the frameworks and written lessons;
**Words** is the jargon bank. The runner is a single focused screen with a
stepper, a stage and a fixed action bar with one primary action, a phase
indicator and a thin level meter. Deep links: `#train`, `#library`, `#words`,
`#lesson=<id>`, `#drill=<id>`, `#framework=<id>`,
`#roleplay=<persona>,<scenario>`, `#demo` (a static result card for design
checks). Query flags: `?theme=light|dark`, `?nomic=1` skips the microphone
check for screenshots.

Design rules the frontend follows (2026-09-05 pass with the frontend-design
skill): paper, Fraunces and the deep green stay; brass has one job, the small
italic Fraunces labels (`h3`, `.stage-kicker`, `.group-head`, `.phase`, the
score word, the call panel headings) and the marker on the current lesson.
Nothing is set in uppercase, nothing is tracked out, and meta text is written
as sentences rather than fragments joined with middle dots. The numbers panel
shows one sentence until something is measured, then each number carries a
plain word beside its label (solid, on target, a touch fast, under the bar).
The Today card and the welcome card are set like a programme: a thick-thin
rule at the top (`.programme`), the lesson's number as an italic brass numero
(`.hero-no`), and the path as a table of contents with serif numerals and
dotted leaders to the minutes or the best score. Lesson prose in the runner
is set in Fraunces at 18.5 px.

The path lives in `course.py`: five units and twenty-nine lessons, each with
a goal, a teaching paragraph (optionally pulled from a written lesson in
`content.LESSONS`), a framework whose worked example the character speaks as
the demonstration, an attempt (`warmup`, `record`, `questions`, `drill`,
`roleplay` or `quiz`, mapped onto the existing drill modules) and a pass mark.
Lessons open in order. `data/progress.json` keeps best score, attempts and
last date per lesson; `data/profile.json` keeps the onboarding answers.
`/course` returns the units with a status per lesson (done, current, locked)
and `/course/complete` records an attempt. The daily plan from `/plan` is the
next lessons on the path that fit the profile's minutes (at most three) plus,
on even days, one review of a finished lesson still under its pass mark,
generated once per day into `data/plan.json`. In the frontend the `Lesson`
module runs teach, demo, attempt and wrap; every drill module returns its
result so the lesson can be scored, and a scored lesson with nothing recorded
(a blocked microphone) offers a retry instead of completing.

Characters are talking heads inside a video-call screen. `build_avatars.py`
cuts the pictures in `Avatar pictures/Group A` into 3:4 frames per state
(idle, talk, blink, smile, skeptical, glance, surprised) under
`avatars/<actor>/` and writes `avatars/manifest.json`, which also maps
personas to actors. The call screen (speaker view) shows the character in the
main tile over a blurred backdrop, the user's camera as a picture-in-picture
tile with a live level bar and a green border while speaking, captions, a
conversation panel with per-turn scores, and a control bar (mic, camera,
captions, voice, coach, done, leave). The camera request is raced against a
six-second timeout so an unanswered prompt never blocks the call.

Motion comes from video, not from flipping stills. Each actor has
`avatars/<actor>/idle.mp4` (listening) and `talk.mp4` (talking): 4:3 like the
tile, 25 fps, played forward then backward so the loop has no seam. They were
generated from the actors' 16:9 office pictures with Gemini's video tool in
the browser (image to video, landscape, a plain description of the person
listening or talking on a call; a 9:16 request from a 3:4 crop came back as
an extreme close-up, and wording like "exact photo", "photoreal" or "webcam
recording" was refused, and a picture that still carries Gemini's own visible
sparkle fails with "Something went wrong (1099)" until the sparkle is painted
over; the cleaned 1280x720 sources are in `Avatar pictures/video sources/`)
and finished with
`python build_avatar_video.py --from <clip.mp4> <man|woman> <idle|talk>`,
which trims to 8 s, centre-crops to 4:3 (this also drops the sparkle
watermark in the corner), mirrors and encodes. The script keeps a LivePortrait
route (its own environment under `%LOCALAPPDATA%\stage-time\liveportrait`,
CPU PyTorch) but on this laptop it did not finish a two-second test in fifty
minutes, so it is not the route in use. `/content` advertises the clips in
the manifest under `video` whenever `idle.mp4` exists (the listening loop
stands in for a missing `talk.mp4`), and it looks at the folder on every
request, so adding clips needs only a reload. In the call and demo tiles the
`Avatar` class keeps two muted `<video>` elements and crossfades between the
idle loop and the talking loop on `speakStart` and `speakStop`, starting each
from a random offset. The lips follow the clip rather than the words; on a
video call at this size that reads as a person talking. Where the clips are
missing the tiles fall back to the stills, with a slow breathing transform
and a faint animated grain so a still reads as a camera feed, and the small
circles in the persona picker always use stills.

---

## What runs without what

Every service is optional and the status word at the top right says which
is off and why.

| Missing | You lose | You keep |
|---|---|---|
| Ollama | Directness, premise and framework grading; coaching notes; roleplay follow-ups; lookups; generated questions | All deterministic scoring, signpost-based structure, every drill, roleplay with bank questions |
| faster-whisper | Everything that needs words | Completion, volume, steadiness |
| parselmouth | Volume, steadiness, tremor, escalation delta | Everything word-based |
| kokoro | The natural voices | The browser's own voices via speechSynthesis (the frontend splits text into sentence groups and prefetches the next while one plays, so Kokoro's cost is one sentence of latency) |
| avatars/ | Faces | Initials in the circle |
| ffmpeg | All audio analysis | Nothing works well. Install it. |

---

## Endpoints

| Method | Path | What |
|---|---|---|
| GET | `/health` | Service state, loading flags, errors |
| GET | `/content` | Levels, drills with flows, lessons, personas, scenarios, frameworks, kinds, technical terms, avatar manifest, read passage, curriculum |
| GET | `/frameworks` | The framework library |
| GET | `/questions?kinds=&n=&balanced=&exclude=` | Draw from the bank |
| POST | `/questions/generate` | One new question of a kind, with ground truth (model) |
| GET | `/history` | Sessions, level, streak, week, trends, fix-next sentence, averages, pressure delta, framework stats, due terms |
| GET | `/course` | Units and lessons with status, best score, star, current lesson, counts |
| POST | `/course/complete` | Record a lesson attempt (`lesson`, `score`) and return the new course state |
| GET/POST | `/profile` | Onboarding answers: minutes a day, goal, onboarded flag |
| GET | `/plan?refresh=` | Today's plan: the next lessons on the path that fit the minutes, plus a review |
| POST | `/plan/step` | Mark a plan step done |
| POST | `/transcribe` | Transcribe and analyse one recording; `store=false` for drill turns |
| POST | `/calibrate` | Add a vowel or calm-read baseline take |
| POST | `/coach` | Content note on a speaking drill (model) |
| POST | `/qa-score` | Grade one answer: `mode` answer, hostile, paraphrase, classify, gap, ask, comprehend |
| POST | `/sessions/series` | Save a roleplay or question drill as one session with turns |
| POST | `/roleplay-turn` | Next persona turn: bank first, model follow-ups, bank fallback |
| POST | `/lesson` | A micro lesson from the user's numbers (model) |
| POST | `/generate-exercise` | A new speaking drill (model) |
| POST | `/speak` | Kokoro TTS for one sentence group: `text`, `voice` (fixed list, `af_heart` for Dana, `am_michael` for Tom), `speed` 0.7 to 1.4; 503 when absent so the browser speaks instead |
| GET | `/jargon/bank` | Seed and personal entries with spaced repetition state |
| POST | `/jargon/lookup` | Bank hit, or explained by the model and saved |
| POST | `/jargon/review` | SM-2 review, state persisted and reapplied at startup |
| GET | `/quiz/ear` | Terms to hear at speed, due ones first |
| GET | `/quiz/sort` | Technical versus substitutable terms |
| GET | `/avatars/...` | Static talking-head frames |
| GET | `/` | The single page frontend |

Handlers are synchronous functions run in FastAPI's thread pool, so a model
call never blocks the rest of the app. Whisper and Kokoro calls are serialised
with locks.

---

## Files

```
main.py                 FastAPI backend
voice_metrics.py        Acoustics: volume, pitch, quality, tremor
text_metrics.py         Fillers, hedges, jargon, register, echo, drill detectors
scoring.py              Every rubric, corroborated caps, series summaries
frameworks.py           35 answer frameworks with steps, examples, signposts, sources
questions.py            153 questions with ground truth, drill flows, technical terms
content.py              Levels, 22 drills, 19 lessons, 11 personas, 5 scenarios, curriculum, plan tables, read passage
course.py               The path: 5 units, 29 lessons (goal, teach, framework, demo, attempt, pass mark)
jargon-bank-seed.json   82 terms, US banking weighted
build_avatars.py        Cuts Avatar pictures/ into avatars/ frames and a manifest
build_avatar_video.py   Trims, crops and loops the character clips into avatars/<actor>/idle.mp4 and talk.mp4
avatars/                Generated talking-head frames and the video loops (a few MB)
stage-time.html         Frontend: onboarding, the path, the runner with the Lesson module, avatars, browser TTS fallback
start.ps1 / start.bat   Windows launcher (venv outside OneDrive)
start.sh                macOS and Linux launcher
REBUILD.md              How to restore what lives outside this folder and check the result, for an AI or a person rebuilding the app
requirements.lock.txt   Exact package versions of the last verified environment
tools/cdp.py            Headless browser driver for checks without a person at the keyboard; tools/flow_smoke.json is its smoke flow
data/                   Your sessions, baseline, plan, path progress, profile, personal bank, review state, generated drills
```

`data/sessions.json` holds three kinds of row: `practice` (one recording, main
rubric), `qdrill` and `roleplay` (one row per session with a `turns` list).
Levels count scored rows. Delete `data/` to start over.

---

## Model contract

Every model call goes through `/api/chat` with Ollama's structured output
(`format` set to a JSON schema), so the shape and the types are enforced by
the server; `_coerce` then clamps integers to their rubric ranges, fills
missing keys, validates enums and drops prose fields that are too short to be
advice. Schemas list scored numbers and arrays before free text, so a reply
cut off by the token budget loses prose, never a score, and `_salvage`
recovers a truncated object. Grading runs at temperature 0.1 with a fixed
seed, so the same answer always gets the same marks. Roleplay replies are
validated (one question, under 60 words, a question mark unless the persona is
the Speechmaker); an off-brief reply gets one nudge and then falls back to
the bank.

---

## Do this first

The warm-up in the first day's plan: three takes of the held note and one
calm read. Until you do, steadiness scores full marks by default and never
deducts.

Keep the microphone, the room and the distance constant between sessions.

---

## Honest limitations

- **No absolute loudness.** Everything is relative to your own noise floor or
  your own baseline.
- **Tremor needs the held note.** In connected speech the syllable rate sits
  on top of the tremor band.
- **Jitter and shimmer are not nervousness detectors.** Votes in a composite,
  only against your own baseline, never alone.
- **A different microphone invalidates the baseline.**
- **The model is small.** Given the steps and the premise it is a fair judge
  of whether they were heard. It is not a communications coach. Deterministic
  parts are the part to trust, and the notes say which parts the model graded.
- **Whisper is nearly verbatim, not verbatim.** It is primed with disfluencies
  and keeps most of them.
- **Two actors, eleven roles.** The faces are shared across personas until
  more picture sets are added.
