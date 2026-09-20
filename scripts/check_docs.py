"""Check relative Markdown links, image assets and bilingual entry points."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
errors = []
for path in [*root.glob('*.md'), *root.glob('docs/**/*.md'), *root.glob('licenses/*.md')]:
    for raw in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
        target = raw.split('#', 1)[0]
        if not target or '://' in target or target.startswith('mailto:'):
            continue
        if not (path.parent / target).exists():
            errors.append(f'{path.relative_to(root)}: missing {target}')
for language in ('en', 'zh'):
    file = root / 'assets' / f'tutorial-{language}.png'
    if not file.is_file():
        errors.append(f'Missing tutorial-{language}.png')
if errors:
    raise SystemExit('\n'.join(errors))
print('Relative documentation links and both tutorial images exist.')
