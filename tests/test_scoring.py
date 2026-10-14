"""Small regression suite for deterministic behavior; no AI services required."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import scoring
import text_metrics as tm

class SpeakingMetricsTests(unittest.TestCase):
    def test_pace_uses_supplied_duration(self):
        self.assertEqual(tm.pace('one two three four five six', 3)['wpm'], 120.0)
        self.assertEqual(tm.pace('one two', 0)['wpm'], 0.0)

    def test_disfluencies_are_counted(self):
        self.assertEqual(tm.fillers('Um, I think, uh, we can start.')['total'], 2)
        self.assertEqual(tm.fillers('We can start with a small pilot.')['total'], 0)

    def test_missing_transcription_is_explicit(self):
        score = scoring.session_score(tm.analyze('', 60), None, 60)
        self.assertNotIn('pace', score['parts'])
        self.assertNotIn('fluency', score['parts'])
        self.assertLess(score['possible'], 100)
        self.assertTrue(any('not measured' in n for n in score['notes']))

    def test_sample_scores_stay_in_range(self):
        for text, duration in [('',0),('um '*30,10),('We recommend a small pilot because it limits risk.',30)]:
            score = scoring.session_score(tm.analyze(text,duration), None,60)
            self.assertGreaterEqual(score['total'],0)
            self.assertLessEqual(score['total'],100)

if __name__ == '__main__':
    unittest.main()

