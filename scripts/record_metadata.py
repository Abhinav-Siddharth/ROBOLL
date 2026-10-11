"""Read Ollama identity/options; never request generation or overwrite old metadata."""
import argparse
import datetime
import hashlib
import json
import subprocess
import urllib.request
from pathlib import Path

MARKER = '\nPFR_PHASE2_PROVENANCE_JSON\n'


def get_json(path, payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    request = urllib.request.Request('http://127.0.0.1:11434/api/'+path, data=data,
                                     headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.load(response)


def snapshot(model):
    models = get_json('tags')['models']
    match = next(m for m in models if m['name'] == model)
    details = get_json('show', {'model': model})
    client = subprocess.run(['ollama', '--version'], check=True, capture_output=True, text=True)
    return {'recorded_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'model': model, 'model_digest': match['digest'],
            'ollama_server_version': get_json('version')['version'],
            'ollama_client_version_output': client.stdout.strip(),
            'details': match.get('details', {}),
            'template_sha256': hashlib.sha256(details.get('template', '').encode()).hexdigest(),
            'model_parameters': details.get('parameters', ''),
            'options': {'temperature': 0.7, 'num_ctx': 4096},
            'seed_rule': 'base_seed * 1000 + call_index',
            'legacy_cache_namespace': 'results/cache',
            'new_cache_namespace': 'results/cache_v2',
            'scope': 'Current installed model; historical v1 version not inferred'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', default='qwen2.5:7b')
    parser.add_argument('--out', default='results/meta.txt')
    args = parser.parse_args()
    out = Path(args.out)
    original = out.read_text() if out.exists() else ''
    if MARKER in original:
        raise SystemExit('Metadata already recorded; use a new output path to preserve provenance')
    metadata = snapshot(args.model)
    out.write_text(original.rstrip()+'\n'+MARKER+json.dumps(metadata, indent=2)+'\n')
    print(json.dumps(metadata, indent=2))
