#!/usr/bin/env python3
from __future__ import annotations

import argparse, json, os, re, sqlite3, subprocess
from dataclasses import dataclass, asdict
from pathlib import Path

HISTORY_RE = re.compile(r"\b(earlier|previous|prior|conversation|transcript|compacted|forgot|what did we decide|what did i say)\b", re.I)
TOKEN_RE = re.compile(r"[\w./:@+-]{3,}")

@dataclass
class Candidate:
    id: str
    title: str
    source_type: str
    path: str = ''
    snippet: str = ''
    rank: int = 1
    score: float = 0.0

def tokens(q: str) -> set[str]:
    return {t.lower() for t in TOKEN_RE.findall(q or '') if len(t) > 2}

def score_text(qt: set[str], text: str) -> float:
    h = (text or '').lower()
    return sum(1 for t in qt if t in h) / max(1, len(qt))

def docs_candidates(query: str, docs: Path, limit: int) -> list[Candidate]:
    docs = docs.expanduser()
    if not docs.exists(): return []
    qt = tokens(query); scored = []
    files = docs.rglob('*.md') if docs.is_dir() else [docs]
    for p in files:
        try: txt = p.read_text(encoding='utf-8', errors='ignore')
        except OSError: continue
        s = score_text(qt, p.name + ' ' + txt[:4000])
        if s:
            scored.append((s,p,txt))
    scored.sort(reverse=True, key=lambda x:x[0])
    return [Candidate(f'doc:{p}', p.stem, 'curated_doc', str(p), txt[:350].replace('\n',' '), i+1, s) for i,(s,p,txt) in enumerate(scored[:limit])]

def lcm_candidates(query: str, db: Path, limit: int) -> list[Candidate]:
    db = db.expanduser()
    if not db.exists(): return []
    qt = tokens(query); rows=[]
    con = sqlite3.connect(str(db))
    try:
        for rowid, content in con.execute('select rowid, content from messages order by rowid desc limit 2000'):
            txt = content or ''
            s = score_text(qt, txt)
            if s: rows.append((s,rowid,txt))
    except sqlite3.Error:
        pass
    finally:
        con.close()
    rows.sort(reverse=True, key=lambda x:x[0])
    return [Candidate(f'lcm:{rid}', f'LCM message {rid}', 'raw_lcm', '', txt[:350].replace('\n',' '), i+1, s) for i,(s,rid,txt) in enumerate(rows[:limit])]

def qmd_candidates(query: str, limit: int) -> list[Candidate]:
    try:
        proc = subprocess.run(['qmd','search',query,'--limit',str(limit)], text=True, capture_output=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return []
    if proc.returncode != 0 or not proc.stdout.strip(): return []
    out=[]
    for i,line in enumerate(proc.stdout.splitlines()[:limit]):
        line=line.strip()
        if line:
            out.append(Candidate(f'qmd:{i}:{line[:80]}', line[:120], 'qmd', '', line, i+1, 0.5))
    return out

def graph_candidates(query: str, graph_path: Path, limit: int) -> list[Candidate]:
    graph_path = graph_path.expanduser()
    if not graph_path.exists(): return []
    data=json.loads(graph_path.read_text())
    qt=tokens(query); out=[]
    for n in data.get('nodes',[]):
        label=n.get('id','')
        if score_text(qt,label):
            out.append(Candidate(f'graph:{label}', label, 'entity_graph', str(graph_path), f"entity weight {n.get('weight')}", len(out)+1, float(n.get('weight',1))))
            if len(out)>=limit: break
    return out

def fuse(lists: dict[str,list[Candidate]], query: str, k: int=60) -> list[dict]:
    history = bool(HISTORY_RE.search(query or ''))
    priors = {'raw_lcm':0.16 if history else 0.01, 'curated_doc':0.02 if history else 0.07, 'qmd':0.02 if history else 0.06, 'entity_graph':0.01 if history else 0.03}
    merged={}
    for source, items in lists.items():
        for c in items:
            key=(c.source_type, c.path or c.title)
            row=merged.setdefault(key, asdict(c) | {'rrf_score':0.0, 'matched_sources':[]})
            row['rrf_score'] += 1.0/(k+c.rank)
            row['matched_sources'].append(source)
            row['score'] = row['rrf_score'] + priors.get(c.source_type,0.02) + min(c.score,1)*0.03
    return sorted(merged.values(), key=lambda r:r['score'], reverse=True)

def route(query: str, docs: str|None, lcm_db: str|None, graph: str|None, limit: int) -> dict:
    lists={}
    if docs: lists['docs']=docs_candidates(query, Path(docs), limit)
    if lcm_db: lists['lcm']=lcm_candidates(query, Path(lcm_db), limit)
    if graph: lists['graph']=graph_candidates(query, Path(graph), limit)
    lists['qmd']=qmd_candidates(query, limit)
    return {'query':query, 'intent':'conversation_history' if HISTORY_RE.search(query or '') else 'default', 'results':fuse(lists, query)[:limit], 'sources':{k:len(v) for k,v in lists.items()}}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('query')
    ap.add_argument('--docs', default=os.getenv('MEMORY_STACK_DOCS_PATH'))
    ap.add_argument('--lcm-db', default=os.getenv('MEMORY_STACK_LCM_DB'))
    ap.add_argument('--graph', default=os.getenv('MEMORY_STACK_GRAPH_PATH'))
    ap.add_argument('--limit', type=int, default=10)
    ap.add_argument('--json', action='store_true')
    args=ap.parse_args(); data=route(args.query,args.docs,args.lcm_db,args.graph,args.limit)
    if args.json: print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        for i,r in enumerate(data['results'],1): print(f"{i}. [{r['source_type']}] {r['title']}\n   {r['snippet'][:180]}")
if __name__ == '__main__': main()
