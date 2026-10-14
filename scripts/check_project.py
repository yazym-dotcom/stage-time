"""Lightweight release checks without starting the backend or downloading models."""
import ast
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import course
import frameworks
import questions

for path in ROOT.rglob('*.py'):
    if '.git' not in path.parts:
        ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path))
for label, rows in [('lessons', course.LESSONS), ('frameworks', frameworks.FRAMEWORKS), ('questions', questions.QUESTIONS)]:
    ids = [r['id'] for r in rows]
    assert len(ids) == len(set(ids)), f'Duplicate {label} IDs'
for lesson in course.LESSONS:
    if lesson.get('framework'):
        assert lesson['framework'] in frameworks.BY_ID, lesson['id']

export = (ROOT / 'demo/content.js').read_text(encoding='utf-8')
payload = json.loads(export.split('window.STAGE_CONTENT = ', 1)[1].rsplit(';', 1)[0])
assert payload['counts']['lessons'] == len(course.LESSONS)
assert payload['counts']['frameworks'] == len(frameworks.FRAMEWORKS)
assert payload['counts']['questions'] == len(questions.QUESTIONS)
html = (ROOT / 'demo/index.html').read_text(encoding='utf-8')
for ref in re.findall(r'(?:href|src)="(\./[^"]+)"', html):
    assert (ROOT / 'demo' / ref).is_file(), f'Missing demo asset: {ref}'
assert not re.search(r'getUserMedia|fetch\s*\(', (ROOT/'demo/app.js').read_text(encoding='utf-8'))
for path in list((ROOT/'demo').rglob('*')):
    assert path.name not in ('sessions.json', 'baseline.json', 'profile.json', 'plan.json')
print('PASS: Python syntax, curriculum references, demo content counts, local assets, no demo microphone/network calls.')

