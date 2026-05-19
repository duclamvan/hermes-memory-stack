#!/usr/bin/env python3
from __future__ import annotations

import argparse, json, subprocess, sys, time
from pathlib import Path

def run(cmd, timeout=120):
    try:
        p=subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
        return {'cmd':cmd,'exit_code':p.returncode,'stdout':p.stdout[-2000:],'stderr':p.stderr[-2000:]}
    except subprocess.TimeoutExpired as e:
        return {'cmd':cmd,'exit_code':124,'stdout':str(e.stdout or '')[-2000:],'stderr':'timeout'}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true', help='run mutating index updates such as qmd update')
    ap.add_argument('--workspace', default='.')
    ap.add_argument('--hermes-home', default='~/.hermes')
    ap.add_argument('--out', default='reports/memory-stack-maintenance.json')
    args=ap.parse_args(); steps=[]; scripts=Path(__file__).parent
    if args.apply:
        steps.append(run(['qmd','update'], timeout=300))
    steps.append(run([sys.executable, str(scripts/'memory_stack_verify.py'), '--hermes-home', args.hermes_home], timeout=60))
    report={'status':'pass' if all(s['exit_code']==0 for s in steps) else 'fail', 'apply':args.apply, 'generated_at':time.time(), 'steps':steps}
    out=Path(args.out); out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'status':report['status'], 'out':str(out), 'steps':len(steps)}))
    raise SystemExit(0 if report['status']=='pass' else 1)
if __name__=='__main__': main()
