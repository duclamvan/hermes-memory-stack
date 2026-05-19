#!/usr/bin/env python3
from __future__ import annotations

import argparse, json, os, sqlite3
from pathlib import Path
import yaml
REQUIRED_ENV={
 'LCM_LARGE_OUTPUT_EXTERNALIZATION_ENABLED':'true',
 'LCM_LARGE_OUTPUT_EXTERNALIZATION_THRESHOLD_CHARS':'12000',
 'LCM_LARGE_OUTPUT_TRANSCRIPT_GC_ENABLED':'false',
 'LCM_CONTEXT_THRESHOLD':'0.70',
}
def parse_env(path):
    vals={}; path=Path(path).expanduser()
    if not path.exists(): return vals
    for line in path.read_text(errors='ignore').splitlines():
        if '=' in line and not line.lstrip().startswith('#'):
            k,v=line.split('=',1); vals[k.strip()]=v.strip().strip('"\'')
    return vals
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--hermes-home', default='~/.hermes')
    ap.add_argument('--workspace', default='.')
    ap.add_argument('--out')
    args=ap.parse_args(); home=Path(args.hermes_home).expanduser(); failures=[]
    cfg=home/'config.yaml'
    if cfg.exists():
        data=yaml.safe_load(cfg.read_text()) or {}
        if (data.get('memory') or {}).get('memory_enabled') is not True: failures.append('memory.memory_enabled is not true')
        if (data.get('context') or {}).get('engine') != 'lcm': failures.append('context.engine is not lcm')
    else: failures.append(f'missing {cfg}')
    env=parse_env(home/'.env')
    for k,v in REQUIRED_ENV.items():
        if env.get(k) != v: failures.append(f'{k}={env.get(k)!r}, expected {v!r}')
    lcm=Path(os.getenv('MEMORY_STACK_LCM_DB', str(home/'lcm.db'))).expanduser()
    lcm_ok=lcm.exists()
    report={'status':'pass' if not failures else 'fail','failures':failures,'lcm_db_exists':lcm_ok,'hermes_home':str(home)}
    if args.out: Path(args.out).write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report['status']=='pass' else 1)
if __name__=='__main__': main()
