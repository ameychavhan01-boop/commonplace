"""Extract TradingView OHLCV tool results from the session transcript into JSON files.
Usage: python grab_ohlcv.py OUTDIR  -> writes <symbol>_<interval>_<first>_<last>.json for each result found."""
import json, sys, os, glob
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
files = glob.glob(os.path.expanduser('~/.claude/projects/*/*.jsonl'))
seen = 0
for fn in files:
    for line in open(fn):
        try: rec = json.loads(line)
        except Exception: continue
        msg = rec.get('message') or {}
        content = msg.get('content')
        if not isinstance(content, list): continue
        for part in content:
            if not isinstance(part, dict) or part.get('type') != 'tool_result': continue
            items = part.get('content')
            texts = []
            if isinstance(items, str): texts = [items]
            elif isinstance(items, list): texts = [i.get('text','') for i in items if isinstance(i, dict)]
            for tx in texts:
                if '"bars"' not in tx or '"symbol"' not in tx: continue
                try: d = json.loads(tx)
                except Exception: continue
                b = d.get('bars')
                if isinstance(b, list):  # rows
                    cols = {k: [r[k] for r in b] for k in 'tohlcv'}
                else: cols = b
                if not cols or not cols.get('t'): continue
                sym = d['symbol'].replace(':', '_'); iv = d.get('interval', 'x')
                name = f"{sym}_{iv}_{cols['t'][0]}_{cols['t'][-1]}.json"
                json.dump(cols, open(os.path.join(out, name), 'w'))
                seen += 1
                print(name, len(cols['t']))
print('found', seen)
