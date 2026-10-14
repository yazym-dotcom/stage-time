"""Export public learning content only. Never imports main or reads data/."""
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import content
import course
import frameworks
import questions

public_framework_keys = ('id', 'name', 'group', 'tagline', 'steps', 'best_for',
                         'avoid', 'example_q', 'example_a', 'source')
payload = {
    'units': course.UNITS,
    'lessons': [{k: v for k, v in lesson.items() if k in
                 ('id', 'unit', 'title', 'goal', 'minutes', 'teach', 'framework')}
                for lesson in course.LESSONS],
    'frameworks': [{k: f[k] for k in public_framework_keys if k in f}
                   for f in frameworks.FRAMEWORKS],
    'personas': content.PERSONAS,
    'counts': {'lessons': len(course.LESSONS), 'frameworks': len(frameworks.FRAMEWORKS),
               'questions': len(questions.QUESTIONS), 'personas': len(content.PERSONAS)},
}
(ROOT / 'demo' / 'content.js').write_text(
    '/* Public curriculum exported from the original app. Examples are illustrative. */\n'
    + 'window.STAGE_CONTENT = ' + json.dumps(payload, ensure_ascii=False, indent=2) + ';\n',
    encoding='utf-8')
print('Exported public curriculum; no personal data included.')

