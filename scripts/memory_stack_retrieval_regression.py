#!/usr/bin/env python3
from __future__ import annotations

import argparse, json, subprocess, sys
from pathlib import Path

def check_case(case, router, extra):
    proc=subprocess.run([sys.executable, router, case['query'], '--json']+extra, text=True, capture_output=True)
    data=json.loads(proc.stdout) if proc.returncode==0 and proc.stdout.strip() else {'results':[]}
    joined=json.dumps(data, ensure_ascii=False).lower()
    source_types={r.get('source_type') for r in data.get('results',[])}
    missing_sources=[s for s in case.get('required_source_types',[]) if s not in source_types]
    missing_hints=[h for h in case.get('required_hints',[]) if h.lower() not in joined]
    ok=not missing_sources and not missing_hints
    return {'name':case.get('name',case['query']), 'ok':ok, 'missing_sources':missing_sources, 'missing_hints':missing_hints, 'result_count':len(data.get('results',[]))}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--cases', required=True)
    ap.add_argument('--out')
    ap.add_argument('--router', default=str(Path(__file__).with_name('memory_stack_router.py')))
    args, extra=ap.parse_known_args()
    cases=json.loads(Path(args.cases).read_text())
    results=[check_case(c,args.router,extra) for c in cases]
    report={'status':'pass' if all(r['ok'] for r in results) else 'fail', 'passed':sum(r['ok'] for r in results), 'total':len(results), 'results':results}
    if args.out: Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n')
    print(json.dumps(report, indent=2, ensure_ascii=False))
    raise SystemExit(0 if report['status']=='pass' else 1)
if __name__ == '__main__': main()
