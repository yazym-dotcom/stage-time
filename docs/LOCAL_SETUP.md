# Stage Time

A public speaking coach that runs on your own laptop. Every day it lays out a
short session: a warm-up, one answer framework practised on three questions, a
delivery drill, and four turns against a character who pushes back. It listens,
measures your pace, filler words, hedging, volume and steadiness, checks
whether each step of the framework was heard, and gives you one thing to fix.

Nothing you say ever leaves your computer. There is no account, no
subscription, and no internet connection needed once it is set up.

**This guide assumes you have never used a terminal before.** The whole setup
is: install Python, install ffmpeg, double-click one file.

---

## Before you start

**Use your personal laptop.** Do not install this on a work machine. It needs
to install software and record audio, and most corporate laptops will either
block that or flag it.

**What you need:**

| | |
|---|---|
| A Mac or Windows laptop | Made in roughly the last six years |
| Free disk space | About 3 GB, 6 GB if you add the optional voices |
| Memory | 8 GB works, 16 GB is comfortable |
| Time | 20 minutes for a working app, about 40 for everything |
| Internet | Only during setup |
| A browser | Chrome, Edge or Firefox. They have built in voices the app uses. |

**How this guide is built.** The app installs in stages. Stage 1 gives you a
working app with every drill, every framework, the question bank and the
characters. Each stage after that adds something. You can stop after any stage
and come back another day.

| Stage | What it adds | Time |
|---|---|---|
| 1 | Everything that does not need a model: the daily session, drills, frameworks, questions, volume, steadiness | 20 min |
| 2 | Transcription: pace, fillers, hedges, jargon, framework checks | automatic, 5 min download |
| 3 | The coaching model: graded answers, coaching notes, roleplay follow-ups, lookups | 15 min |
| 4 | Optional spoken voices (Kokoro). Your browser's voices work without it. | 10 min |

---

# Part 1: Open the terminal

The terminal is a window where you type commands instead of clicking buttons.
It looks intimidating and it is not. You will paste about three things into it
in total.

### On a Mac

1. Press `Command` and `Space` at the same time.
2. Type `Terminal`.
3. Press `Enter`.

### On Windows

1. Click the Start button.
2. Type `PowerShell`.
3. Click **Windows PowerShell**.

A window opens with a blinking cursor. That is all it is.

> **Pasting into the terminal:** on Mac, `Command V` as normal. On Windows
> PowerShell, right-click pastes. After pasting anything, press `Enter` to run
> it.

---

# Part 2: Install Python

Python is the language the app is written in. Your computer needs it the same
way it needs a PDF reader to open a PDF.

**Install version 3.12 specifically.** The newest release is usually too new
for the audio and speech libraries, which take a year or so to catch up.

### On Windows

Easiest way, one command in PowerShell:

```
winget install Python.Python.3.12
```

If that does not work, go to **https://www.python.org/downloads/windows/**,
scroll to **Python 3.12**, and download the **Windows installer (64-bit)**.
On the first screen of the installer, tick the checkbox saying **Add
python.exe to PATH** before clicking Install. Miss it and nothing later works.

### On a Mac

Go to **https://www.python.org/downloads/macos/**, find **Python 3.12**, and
download the **macOS 64-bit universal2 installer**. Click through it normally.

### Check it worked

Close the terminal completely, open a new one, and paste this.

**Mac:** `python3.12 --version` **Windows:** `py -3.12 --version`

You should see something like `Python 3.12.10`. If you see "not recognized",
close the terminal, open a new one, and try again. That fixes it most of the
time.

---

# Part 3: Install ffmpeg

Your browser records audio in a format the analysis tools cannot read. ffmpeg
converts it. **Without this nothing works**, so do not skip it.

### On Windows

```
winget install ffmpeg
```

If it shows a list of several options, choose the one from **Gyan**. After it
finishes, **close the terminal window completely and open a new one.** Windows
will not find ffmpeg until you do.

### On a Mac

ffmpeg is easiest to get through Homebrew. Install Homebrew first if you do not
have it:

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

It will ask for your Mac password. You will not see the characters appear as
you type. That is normal. Then:

```
brew install ffmpeg
```

### Check it worked

```
ffmpeg -version
```

You want a paragraph of version information.

---

# Part 4: Start the app

Leave the `stage-time` folder wherever it is. Your Desktop is fine, even if
your Desktop lives in OneDrive or iCloud: the launcher keeps the heavy files
outside the synced folder on its own.

### On Windows

Open the `stage-time` folder and **double-click `start.bat`**.

### On a Mac

In the terminal, paste these two lines, pressing Enter after each:

```
cd ~/Desktop/stage-time
```
```
chmod +x start.sh && ./start.sh
```

> If you unzipped the folder somewhere else, type `cd ` with a space after it,
> then drag the folder from Finder straight into the terminal window, press
> Enter, and then run the second line.

### What happens on the first run

The first run creates the app's private workspace and downloads its parts.
Expect **5 to 15 minutes** and a wall of scrolling text. Scrolling text is
good. Let it run. If it stops with red text mentioning a download, run the
same thing again; it picks up where it left off.

Every later start takes a few seconds.

When it is ready you will see:

```
Uvicorn running on http://127.0.0.1:8000
```

and your browser opens on its own. If it does not, open a browser and go to
`http://127.0.0.1:8000`.

**Leave the terminal window open.** It is the app. Closing it turns the app
off. To stop the app at any time, click the window and press `Control` and
`C` together.

At the top right of the page is a small status word. **All set** means every
part is running. **Loading transcription** blinks while the app downloads its
transcription model the first time (about 500 MB, a few minutes) and then
turns to **All set** on its own. **Coaching model off** stays until Part 6,
and a line under the header explains what that limits.

---

# Part 5: Your first session

Everything happens on the **Today** page. The first time it opens it asks two
things: how many minutes a day you want to spend (five, ten or fifteen) and
what you mostly need this for. Check the microphone there, allow it when the
browser asks, play the test sound, then click **Start Lesson 1**.

> Hearing nothing from the test sound? Windows may be sending sound to a
> monitor or a dock instead of your speakers. Click the speaker icon in the
> taskbar, open the output device list beside the volume slider, and choose
> your speakers or headphones. The app cannot change this for you.

Stage Time is a path of twenty-nine lessons in five units, opened one at a
time. Every lesson has the same shape:

1. **Teach.** One screen that says what you will be able to do afterwards and
   how. Framework lessons show the steps of the shape you are about to use.
2. **Show.** A character answers a real question the way the lesson says, out
   loud, with the steps beside the face and the words underneath. **Hear it
   again** repeats it.
3. **Try.** You do the same thing. The app reads a question to you, gives you
   a few seconds to think, starts the recorder on its own, and scores what it
   hears. Press **Done** or `D` when you finish.
4. **Feedback.** A score, a one-line verdict, and the single most useful thing
   to change. Click **Details** for the full breakdown and the transcript.
   Reaching the lesson's pass mark earns its star. The next lesson unlocks
   either way, and a lesson still under its mark comes back as a review on a
   later day.

Lesson 1 is the warm-up: three held notes and a one-minute read. That is the
calm voice every later steadiness score is measured against, so do it sitting
where you normally sit, with the microphone where it normally is.

Come back tomorrow. **Today** shows the next lesson on the path, what fits in
your minutes, and one **Continue** button. Later units bring the harder
questions, the hostile characters and the video calls.

> Use the same laptop, the same microphone and roughly the same distance every
> time. A headset and a built-in microphone produce different numbers.

---

# Part 6: Add the coaching model (Stage 3)

This is what people mean by "the AI layer". It runs entirely on your laptop.
Nothing is sent anywhere. It unlocks: graded directness, premise handling and
framework coverage on every answer, written coaching notes on speaking drills,
characters who build on what you just said, a lesson written from your own
numbers, and lookups of any business phrase.

**Without it the app still works.** Every answer is graded on the measurable
parts, roleplay questions come from the built in bank, and the result card
says exactly which parts were not graded.

### Install Ollama

1. Go to **https://ollama.com/download**
2. Download the version for your computer and click through the installer.

### Download the model

Open a **new** terminal window, leaving the app running in the old one, and
paste:

```
ollama pull qwen2.5:3b
```

About 2 GB, 5 to 15 minutes. You will see a progress bar.

### Turn it on

Reload the browser page. The status word turns to **All set** within half a
minute. Nothing needs restarting.

---

# Part 7: Optional spoken voices (Stage 4)

Without this stage the app uses the voices built into your browser to read
questions and to speak for the characters. They are usable but flat. The
Kokoro voices are natural: Dana speaks with one, Tom with another, every line
is made on your laptop, and playback starts after the first sentence while the
rest is still being made. Once installed, **Auto** in the voice picker under
Preferences means these voices; pick a browser voice by name to go back.

To install them, run this in the terminal from the `stage-time` folder:

**Windows:**
```
& "$env:LOCALAPPDATA\stage-time\venv\Scripts\python.exe" -m pip install -r requirements-voices.txt
```

**Mac:**
```
~/.stage-time/venv/bin/python -m pip install -r requirements-voices.txt
```

Then stop the app and start it again. Kokoro needs Python 3.12 or older and
downloads about 330 MB the first time it speaks. It is the most fragile piece
and the least important.

---

# Using the app day to day

## Starting it up tomorrow

Windows: double-click `start.bat`. Mac: `cd ~/Desktop/stage-time` then
`./start.sh`. The browser opens by itself.

## The four pages

**Today.** The path. The next lesson, what fits in today's minutes, and one
button that runs it. Under that, the whole path: five units, twenty-nine
lessons, which are done (with the best score and a star for the pass mark),
which is current, and which are still locked. Click a finished lesson to do it
again. To the right: your numbers with their trend, one sentence on what to
fix next, a button that writes a lesson from your numbers, and your recent
sessions.

**Practice.** Everything from the path, any time, in any order, in three
flavours: *Questions* (read to you, graded per answer), *Speaking* (a minute
of delivery, the full rubric) and *Decode* (typed). Levels unlock as sessions
add up. At the top, **Face someone**: pick a character and a setting, press
Start.

**Library.** Thirty-five answer frameworks grouped by what they are for, each
with its steps, a worked example and its source, and a **Practise** button
that runs three questions inside it. Nineteen lessons on delivery sit behind
the second tab.

**Words.** Look up any phrase, browse the bank, hear a term at meeting speed,
mark what you know, and drill by ear. Terms you miss come back sooner.

The gear at the top right holds preferences: theme, voices on or off, think
time, auto-advance, and the audience the jargon score assumes.

## Inside a session

- The question is read aloud, then a think timer, then the recorder starts by
  itself. The pause before your first word is measured.
- Press **Done** or `D` when you have finished. `Enter` or `Space` moves on.
  `Escape` exits.
- Each result is a score, a verdict, and one thing to fix. **Details** opens
  the breakdown. The next question follows on its own after a few seconds
  unless you turn auto-advance off.
- Every question drill and roleplay turn is graded on whether each step of a
  framework was heard, in order. The grader also sees the question's ground
  truth: the false premise it carries, the two questions it fuses, the real
  concern underneath.

## The characters

Roleplay runs as a video call. The character fills the main tile, your camera
shows in the corner, captions repeat what was said, and the panel on the
right holds the transcript with a score after each answer. The control bar
works like any meeting app: mic status, camera on or off, captions, voice on
or off, the coach hint, **Done answering**, and a red **Leave** button that
asks once and then ends the call, keeping your answers so far.

Two actors play eleven roles. Their pictures come from `Avatar pictures`
and are cut into talking-head frames by `build_avatars.py`. In the call and
in lesson demos the character is real video: each actor has a short
listening loop and a short talking loop under `avatars/<actor>/`
(`idle.mp4` and `talk.mp4`), made from one office picture of the actor with
Gemini's video tool in the browser and dropped in with
`python build_avatar_video.py --from <clip.mp4> man talk`, which trims the
clip, crops it to the tile and makes it loop. The tile switches between the
two loops as the character speaks. Without a clip the tile falls back to the
stills; with only the listening loop, that loop plays for both. To add an
actor, put a new set of pictures in a folder, add it to the table at the top
of `build_avatars.py`, run it, then make the two clips the same way.

## The frameworks to learn first

| Framework | Steps | Use it for |
|---|---|---|
| PREP | Point, Reason, Example, Point | Any opinion or decision question |
| 3-2-1 | 3 steps, 2 types, 1 thing | Explaining a topic when caught off guard |
| What, So What, Now What | The fact, why it matters, what happens next | Updates and findings |
| ADD | Answer, Detail, Describe | A direct question that wants a direct answer |
| Answer First | Headline, reasons, detail on request | Anything for a senior audience |
| STAR | Situation, Task, Action, Result | "Tell me about a time" |
| Honest Unknown | Acknowledge, boundary, commit, answer what you can | A figure you do not have |
| Neutralise, Answer, Bridge | Restate it neutrally, answer it, bridge | Any hostile question |
| Name the Premise | Name it, correct it, answer the real question | A question with a false assumption |
| Divide and Answer | Say there are two, answer each | Two questions fused into one |
| Concede, Evidence, Move On | Give up the harmless part, go to evidence | Attacks on your experience |

The full list, with sources, is in the Library.

---

# When something goes wrong

| What you see | What to do |
|---|---|
| `start.bat` flashes and closes | Open PowerShell in the folder and run `.\start.ps1` to see the message. |
| "running scripts is disabled" | Use `start.bat`, which bypasses that setting for this one window only. |
| "Could not create the workspace" | Python is not installed or not on PATH. Redo Part 2 and tick the PATH checkbox. |
| Red text mentioning a download during the first start | Run it again. Downloads resume. |
| "The app is not running" in the browser | The terminal closed or the app stopped. Start it again. |
| Status says Loading transcription for more than ten minutes | The first download is slow on your connection. Leave it; it finishes in the background. |
| Scores show only completion, volume and steadiness | Transcription is still loading or failed. Click the status word; the list says which part is off and why. |
| Status says Coaching model off | Ollama is not running. Open the Ollama app; the status updates by itself. |
| Questions are not read aloud | Your browser has no English voice installed, or Voices is off in preferences. Chrome and Edge ship voices; Firefox uses the system's. |
| The browser never asks for the microphone | Use Chrome, Edge or Firefox. Click the padlock in the address bar and allow the microphone. |
| "Address already in use" | The app is already running in another window. Use that one, or start with a different port: `.\start.ps1 8001` and open `http://127.0.0.1:8001`. |
| You want to start completely over | Delete the `data` folder inside `stage-time`. That wipes your sessions, calibration and personal bank and nothing else. |

**If you disagree with a score,** open Details and read the notes rather than
the number. Every deduction has a sentence explaining it. If that sentence is
wrong, then the measurement is wrong, and that is worth knowing.

---

# What this app does not do

**It cannot measure how loud you actually are.** A laptop microphone has no
reference point. Everything here is relative to your own background noise or
your own baseline. That is why the warm-up matters, and why switching
microphones invalidates it.

**It can only detect voice shake properly on the held note.** In normal
speech the rhythm of your syllables sits at the same frequency as a genuine
tremor. The app labels normal-speech readings as low confidence and will not
score them.

**The measurements behind steadiness are not lie detectors.** Jitter and
shimmer are clinical voice-quality measures and the research linking them to
nervousness is mixed. The app uses them only as votes in a group, only against
your own baseline, and never one at a time.

**The coaching model is small.** A three-billion-parameter model running on
your processor is a fair judge of whether a step was heard and whether a
premise was named, because it is given the steps and the premise. It is not a
communications coach. The measurable parts of every score are the part to
trust, and a cap the model asks for is only applied when a measurable signal
or a known ground truth agrees with it.

**Transcripts are close, not perfect.** The transcriber is primed to keep "um"
and "uh", and mostly does. Numbers said as words come through as words.

**Catch it at speed needs voices.** If your browser has no English voice and
Kokoro is not installed, that one drill is text only.

---

# Your privacy

- Every recording is analysed on your machine and deleted immediately after.
- Your transcripts, scores, calibration, plan and personal bank live in the
  `data` folder inside `stage-time`, in plain text you can open and read.
- No audio, no transcript and no score is ever uploaded anywhere.
- The only internet use is during setup, to download software and models, and
  the three typefaces the page loads from Google Fonts when you are online.
  Offline, the page uses your system fonts and everything still works.
- To delete everything the app knows about you, delete the `data` folder.

---

*A shorter, technical summary of the architecture, endpoints and file layout is
in `TECHNICAL.md`.*
