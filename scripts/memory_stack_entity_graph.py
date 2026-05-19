#!/usr/bin/env python3
from __future__ import annotations

import argparse, json, re, sqlite3
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

TOKEN_RE = re.compile(r"\b[A-Z][A-Za-z0-9_.-]{2,}\b|\b[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+\b")

def iter_markdown(paths: list[Path]) -> Iterable[tuple[str,str]]:
    for base in paths:
        base = base.expanduser()
        if not base.exists():
            continue
        for p in base.rglob('*.md') if base.is_dir() else [base]:
            try:
                yield str(p), p.read_text(encoding='utf-8', errors='ignore')
            except OSError:
                continue

def iter_lcm(db: Path, limit: int) -> Iterable[tuple[str,str]]:
    db = db.expanduser()
    if not db.exists():
        return
    con = sqlite3.connect(str(db))
    try:
        rows = con.execute("select rowid, content from messages order by rowid desc limit ?", (limit,)).fetchall()
    except sqlite3.Error:
        rows = []
    finally:
        con.close()
    for rowid, content in rows:
        yield f"lcm:{rowid}", content or ''

def extract_entities(text: str) -> list[str]:
    stop = {'The','This','That','And','For','With','From','Hermes','Agent'}
    out = []
    for m in TOKEN_RE.findall(text or ''):
        if len(m) < 3 or m in stop:
            continue
        out.append(m[:120])
    return out

def build_graph(docs: list[Path], lcm_db: Path|None, lcm_limit: int) -> dict:
    nodes = Counter()
    edges = Counter()
    sources = []
    for source, text in iter_markdown(docs):
        ents = sorted(set(extract_entities(text)))[:80]
        sources.append({'source': source, 'entities': ents})
        for e in ents:
            nodes[e] += 1
        for i, a in enumerate(ents):
            for b in ents[i+1:i+12]:
                edges[tuple(sorted((a,b)))] += 1
    if lcm_db:
        for source, text in iter_lcm(lcm_db, lcm_limit):
            ents = sorted(set(extract_entities(text)))[:40]
            sources.append({'source': source, 'entities': ents})
            for e in ents:
                nodes[e] += 1
            for i, a in enumerate(ents):
                for b in ents[i+1:i+8]:
                    edges[tuple(sorted((a,b)))] += 1
    return {
        'nodes': [{'id': k, 'weight': v} for k,v in nodes.most_common()],
        'edges': [{'source': a, 'target': b, 'weight': w} for (a,b),w in edges.most_common()],
        'sources_indexed': len(sources),
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--docs', action='append', default=[])
    ap.add_argument('--lcm-db')
    ap.add_argument('--lcm-limit', type=int, default=500)
    ap.add_argument('--out', default='data/entity-graph.json')
    args = ap.parse_args()
    graph = build_graph([Path(p) for p in args.docs], Path(args.lcm_db) if args.lcm_db else None, args.lcm_limit)
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(graph, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'status':'pass','nodes':len(graph['nodes']),'edges':len(graph['edges']),'out':str(out)}))
if __name__ == '__main__': main()
