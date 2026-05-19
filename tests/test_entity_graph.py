import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_entity_graph_docs(tmp_path):
    docs=tmp_path/'docs'; docs.mkdir(); (docs/'a.md').write_text('Hermes connects QMD and LCM for MemoryStack.')
    out=tmp_path/'graph.json'
    p=subprocess.run([sys.executable, str(ROOT/'scripts/memory_stack_entity_graph.py'), '--docs', str(docs), '--out', str(out)], text=True, capture_output=True)
    assert p.returncode == 0
    data=json.loads(out.read_text())
    assert data['nodes']
