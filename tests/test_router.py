import json, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_router_docs(tmp_path):
    docs=tmp_path/'docs'; docs.mkdir(); (docs/'decision.md').write_text('We decided memory routing should check raw transcripts for old chats.')
    p=subprocess.run([sys.executable, str(ROOT/'scripts/memory_stack_router.py'), 'old chat memory routing', '--docs', str(docs), '--json'], text=True, capture_output=True)
    assert p.returncode == 0
    data=json.loads(p.stdout)
    assert data['results']
    assert data['results'][0]['source_type'] == 'curated_doc'
