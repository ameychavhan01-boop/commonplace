"""Parse script.md into chapters: narration paragraphs + visual cues (JSON)."""
import json, re, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, '..', 'script.md')).read()

def clean(t):
    t = re.sub(r'\{[A-Z0-9]+\}', '', t)
    t = t.replace('**', '').replace('*', '')
    return re.sub(r'\s+', ' ', t).strip()

chapters = []
cur = None
for line in src.split('\n'):
    if line.startswith('## '):
        m = re.match(r'## (\d+) · (.*)', line)
        cur = dict(id=int(m.group(1)), heading=m.group(2).strip(), items=[])
        chapters.append(cur)
        continue
    if cur is None or not line.strip() or line.startswith('---'):
        continue
    if line.startswith('[VISUAL]'):
        cur['items'].append(dict(kind='visual', text=line[len('[VISUAL]'):].strip()))
    else:
        cur['items'].append(dict(kind='para', text=clean(line)))
for c in chapters:
    c['narration'] = ' '.join(i['text'] for i in c['items'] if i['kind'] == 'para')
json.dump(chapters, open(os.path.join(HERE, 'chapters.json'), 'w'), indent=1, ensure_ascii=False)
for c in chapters:
    print(c['id'], c['heading'][:40], len(c['narration']), 'chars')
