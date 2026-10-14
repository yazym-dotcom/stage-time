"""
voice_metrics.py
Stage Time v3 - acoustic analysis module (volume + vocal steadiness)

Offline, CPU only, no network calls. Designed to run inside the existing
FastAPI backend alongside faster-whisper.

Design principle: absolute dB SPL cannot be measured without a calibrated
microphone, and jitter / shimmer thresholds from clinical literature do not
transfer cleanly to "is this speaker nervous". So every judgement here is
either (a) relative to the recording's own noise floor, or (b) relative to
the speaker's own stored calm baseline. Nothing is claimed that the numbers
cannot support.

Dependencies: praat-parselmouth, numpy, scipy
"""

from __future__ import annotations

import math
from typing import Optional

import numpy as np
import parselmouth
from parselmouth.praat import call
from scipy.signal import welch

# ----------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------

FRAME = 0.01          # 10 ms analysis hop
F0_FLOOR = 75         # Hz, Praat default for a male-range voice
F0_CEIL = 500         # Hz
SILENCE_GAP = 0.35    # s, minimum gap that separates two utterances
SPEECH_MARGIN = 10.0  # dB above noise floor to count a frame as speech
TREMOR_BAND = (4.0, 8.0)   # Hz, physiological / essential vocal tremor band


# ----------------------------------------------------------------------
# Volume
# ----------------------------------------------------------------------

def volume_metrics(snd: parselmouth.Sound) -> dict:
    """Loudness in relative dB. Values are uncalibrated, so only differences
    and ranges are meaningful, never the absolute number."""
    intensity = snd.to_intensity(minimum_pitch=F0_FLOOR, time_step=FRAME)
    db = np.asarray(intensity.values).flatten()
    db = db[np.isfinite(db)]
    if db.size < 10:
        return {"usable": False}

    noise_floor = float(np.percentile(db, 5))
    speech = db[db > noise_floor + SPEECH_MARGIN]
    if speech.size < 10:
        return {"usable": False}

    p10, p50, p95 = np.percentile(speech, [10, 50, 95])
    samples = snd.values.flatten()
    peak = float(np.max(np.abs(samples))) if samples.size else 0.0
    clip_ratio = float(np.mean(np.abs(samples) > 0.985)) if samples.size else 0.0

    return {
        "usable": True,
        "mean_db": round(float(np.mean(speech)), 2),
        "median_db": round(float(p50), 2),
        "noise_floor_db": round(noise_floor, 2),
        "snr_db": round(float(p50) - noise_floor, 2),
        "loudness_range_db": round(float(p95 - p10), 2),
        "consistency_sd_db": round(float(np.std(speech)), 2),
        "peak_amplitude": round(peak, 3),
        "clipping_ratio": round(clip_ratio, 5),
        "trail_off_db": trail_off(db, noise_floor),
    }


def trail_off(db: np.ndarray, noise_floor: float) -> Optional[float]:
    """Median drop in dB between the first quarter and last quarter of each
    utterance. A positive number means the speaker fades out at the end of
    sentences, which is the single most common projection fault."""
    is_speech = db > noise_floor + SPEECH_MARGIN
    gap_frames = int(SILENCE_GAP / FRAME)

    segments, start, silence = [], None, 0
    for i, flag in enumerate(is_speech):
        if flag:
            if start is None:
                start = i
            silence = 0
        else:
            if start is not None:
                silence += 1
                if silence >= gap_frames:
                    segments.append((start, i - silence))
                    start = None
    if start is not None:
        segments.append((start, len(is_speech) - 1))

    drops = []
    for a, b in segments:
        n = b - a
        if n < 60:            # ignore utterances under ~600 ms
            continue
        q = max(1, n // 4)
        head = db[a:a + q]
        tail = db[b - q:b]
        drops.append(float(np.mean(head) - np.mean(tail)))

    return round(float(np.median(drops)), 2) if drops else None


# ----------------------------------------------------------------------
# Pitch
# ----------------------------------------------------------------------

def pitch_metrics(snd: parselmouth.Sound) -> dict:
    pitch = snd.to_pitch(time_step=FRAME, pitch_floor=F0_FLOOR, pitch_ceiling=F0_CEIL)
    f0 = pitch.selected_array["frequency"]
    voiced = f0[f0 > 0]
    if voiced.size < 20:
        return {"usable": False}

    median = float(np.median(voiced))
    semitones = 12.0 * np.log2(voiced / median)
    lo, hi = np.percentile(semitones, [5, 95])

    return {
        "usable": True,
        "median_hz": round(median, 1),
        "sd_hz": round(float(np.std(voiced)), 1),
        "pvq": round(float(np.std(voiced) / np.mean(voiced)), 4),
        "sd_semitones": round(float(np.std(semitones)), 2),
        "range_semitones": round(float(hi - lo), 2),
        "voiced_ratio": round(float(voiced.size / f0.size), 3),
    }


# ----------------------------------------------------------------------
# Voice quality
# ----------------------------------------------------------------------

def quality_metrics(snd: parselmouth.Sound) -> dict:
    """Jitter, shimmer, HNR. Interpret only against the speaker's own
    baseline. Population thresholds are clinical and do not map onto
    'nervous versus composed'."""
    try:
        pp = call(snd, "To PointProcess (periodic, cc)", F0_FLOOR, F0_CEIL)
        jitter = call(pp, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)
        shimmer = call([snd, pp], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
        harm = snd.to_harmonicity_cc(time_step=FRAME, minimum_pitch=F0_FLOOR)
        hnr = call(harm, "Get mean", 0, 0)
    except Exception:
        return {"usable": False}

    out = {
        "usable": True,
        "jitter_local_pct": round(float(jitter) * 100, 3) if jitter == jitter else None,
        "shimmer_local_pct": round(float(shimmer) * 100, 3) if shimmer == shimmer else None,
        "hnr_db": round(float(hnr), 2) if hnr == hnr else None,
    }
    if any(v is None for v in out.values() if not isinstance(v, bool)):
        out["usable"] = False
    return out


# ----------------------------------------------------------------------
# Tremor
# ----------------------------------------------------------------------

def _modulation_depth(signal: np.ndarray, fs: float) -> dict:
    """Find the strongest 4-8 Hz component in a contour and report its
    frequency and depth as a percentage of the contour mean."""
    if signal.size < int(fs * 1.0):
        return {"usable": False}

    x = signal - np.mean(signal)
    # 2 s window gives 0.5 Hz resolution, enough to separate 4 Hz from 8 Hz
    nper = min(len(x), int(fs * 2.0))
    freqs, psd = welch(x, fs=fs, nperseg=nper)
    band = (freqs >= TREMOR_BAND[0]) & (freqs <= TREMOR_BAND[1])
    if not band.any():
        return {"usable": False}

    idx = np.argmax(psd[band])
    peak_f = float(freqs[band][idx])
    peak_p = float(psd[band][idx])
    total = float(np.sum(psd[(freqs > 0.5) & (freqs <= 15.0)])) or 1e-12
    amp = math.sqrt(max(peak_p, 0.0) * 2.0)
    mean = float(np.mean(signal)) or 1e-12

    return {
        "usable": True,
        "rate_hz": round(peak_f, 2),
        "depth_pct": round(amp / abs(mean) * 100, 3),
        "band_dominance": round(peak_p / total, 4),
    }


def tremor_metrics(snd: parselmouth.Sound, sustained_vowel: bool = False) -> dict:
    """Only trustworthy on a sustained vowel. In connected speech the
    syllable rate sits at roughly 4 to 7 Hz, directly on top of the tremor
    band, so amplitude modulation there is mostly rhythm, not tremor."""
    pitch = snd.to_pitch(time_step=FRAME, pitch_floor=F0_FLOOR, pitch_ceiling=F0_CEIL)
    f0 = pitch.selected_array["frequency"]
    voiced_idx = np.where(f0 > 0)[0]
    if voiced_idx.size < 100:
        return {"usable": False, "reason": "not enough voiced frames"}

    seg = f0[voiced_idx[0]:voiced_idx[-1] + 1]
    seg = np.where(seg > 0, seg, np.nan)
    nans = np.isnan(seg)
    if nans.any():
        seg[nans] = np.interp(np.flatnonzero(nans), np.flatnonzero(~nans), seg[~nans])

    fs = 1.0 / FRAME
    win = int(fs * 0.5) | 1
    kernel = np.ones(win) / win
    trend = np.convolve(seg, kernel, mode="same")
    f0_tremor = _modulation_depth(seg - trend + float(np.mean(seg)), fs)

    intensity = snd.to_intensity(minimum_pitch=F0_FLOOR, time_step=FRAME)
    env = np.asarray(intensity.values).flatten()
    env = env[np.isfinite(env)]
    amp_tremor = _modulation_depth(env, fs) if sustained_vowel else {
        "usable": False,
        "reason": "amplitude tremor only measured on sustained vowel",
    }

    dom = f0_tremor.get("band_dominance", 0.0) if f0_tremor.get("usable") else 0.0
    if not sustained_vowel:
        verdict = "not assessed, run the sustained vowel drill"
    elif dom >= 0.25:
        verdict = "clear shake in the 4 to 8 Hz band"
    elif dom >= 0.12:
        verdict = "mild shake"
    else:
        verdict = "steady"

    return {
        "usable": True,
        "context": "sustained_vowel" if sustained_vowel else "connected_speech",
        "confidence": "high" if sustained_vowel else "low",
        "verdict": verdict,
        "f0_tremor": f0_tremor,
        "amplitude_tremor": amp_tremor,
    }


# ----------------------------------------------------------------------
# Baseline comparison and scoring
# ----------------------------------------------------------------------

BASELINE_KEYS = [
    ("pitch", "sd_semitones"),
    ("quality", "jitter_local_pct"),
    ("quality", "shimmer_local_pct"),
    ("quality", "hnr_db"),
    ("volume", "consistency_sd_db"),
]


def compare_to_baseline(result: dict, baseline: dict) -> dict:
    """Percent change against the speaker's calm baseline. Higher jitter,
    higher shimmer, lower HNR and higher volume variability together point
    toward an unsteady delivery. Any one of them alone does not."""
    deltas, flags = {}, []
    for group, key in BASELINE_KEYS:
        now = (result.get(group) or {}).get(key)
        was = (baseline.get(group) or {}).get(key)
        if now is None or was is None or was == 0:
            continue
        pct = (now - was) / abs(was) * 100.0
        deltas[f"{group}.{key}"] = round(pct, 1)

    j = deltas.get("quality.jitter_local_pct", 0)
    s = deltas.get("quality.shimmer_local_pct", 0)
    h = deltas.get("quality.hnr_db", 0)
    v = deltas.get("volume.consistency_sd_db", 0)

    votes = sum([j > 20, s > 20, h < -10, v > 25])
    if votes >= 3:
        flags.append("voice notably less steady than your calm baseline")
    elif votes == 2:
        flags.append("voice slightly less steady than your calm baseline")

    return {"deltas_pct": deltas, "unsteady_votes": votes, "flags": flags}


def volume_score(v: dict) -> dict:
    """0 to 100. Deterministic and explainable."""
    if not v.get("usable"):
        return {"score": None, "notes": ["audio too quiet or too short to score"]}

    score, notes = 100, []

    snr = v["snr_db"]
    if snr < 12:
        score -= 30
        notes.append("too quiet relative to room noise, move closer or project more")
    elif snr < 18:
        score -= 12
        notes.append("audible but thin, add breath support")

    lra = v["loudness_range_db"]
    if lra < 6:
        score -= 20
        notes.append("flat volume, nothing is being emphasised")
    elif lra > 22:
        score -= 10
        notes.append("volume swings are erratic rather than deliberate")

    t = v.get("trail_off_db")
    if t is not None and t > 6:
        score -= 20
        notes.append("you fade out at the end of sentences, land the last three words")
    elif t is not None and t > 3:
        score -= 8
        notes.append("slight fade at sentence ends")

    if v["clipping_ratio"] > 0.001:
        score -= 10
        notes.append("input is clipping, back off the microphone")

    return {"score": max(0, min(100, score)), "notes": notes}


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------

def analyze(path: str, baseline: Optional[dict] = None,
            sustained_vowel: bool = False) -> dict:
    snd = parselmouth.Sound(path)
    if snd.n_channels > 1:
        snd = snd.convert_to_mono()

    result = {
        "duration_s": round(snd.get_total_duration(), 2),
        "volume": volume_metrics(snd),
        "pitch": pitch_metrics(snd),
        "quality": quality_metrics(snd),
        "tremor": tremor_metrics(snd, sustained_vowel=sustained_vowel),
    }
    result["volume_score"] = volume_score(result["volume"])
    if baseline:
        result["baseline_comparison"] = compare_to_baseline(result, baseline)
    return result


if __name__ == "__main__":
    import json
    import sys
    print(json.dumps(analyze(sys.argv[1], sustained_vowel="--vowel" in sys.argv), indent=2))
