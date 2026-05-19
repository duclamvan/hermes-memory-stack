#!/usr/bin/env python3
from __future__ import annotations

import argparse, json, subprocess, sys
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('task')
    ap.add_argument('--out', default='focus-brief.md')
    ap.add_argument('--router', default=str(Path(__file__).with_name('memory_stack_router.py')))
    args, rest = ap.parse_known_args()
    proc=subprocess.run([sys.executable,args.router,args.task,'--json']+rest, text=True, capture_output=True, check=False)
    data=json.loads(proc.stdout) if proc.returncode==0 and proc.stdout.strip() else {'results':[]}
    lines=[f"# Focus brief\n", f"Task: {args.task}\n", "## Retrieved context\n"]
    for i,r in enumerate(data.get('results',[])[:8],1):
        lines.append(f"{i}. **{r.get('title','untitled')}** ({r.get('source_type')})")
        if r.get('path'): lines.append(f"   - path: `{r['path']}`")
        if r.get('snippet'): lines.append(f"   - snippet: {r['snippet'][:500]}")
        lines.append('')
    lines.append('\n## Guardrail\nUse this brief as task-local context. Do not write it back into canonical memory unless a durable fact is explicitly confirmed.\n')
    out=Path(args.out); out.parent.mkdir(parents=True, exist_ok=True); out.write_text('\n'.join(lines))
    print(json.dumps({'status':'pass','out':str(out),'results':len(data.get('results',[]))}))
if __name__ == '__main__': main()
