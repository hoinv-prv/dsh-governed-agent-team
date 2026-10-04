#!/usr/bin/env python3
"""Read-only hash, anchor, pin, and historical-preservation audit for AIP-EXEC-024 maps."""
import hashlib
import json
import pathlib
import subprocess

ROOT = pathlib.Path('/home/hoinv/work/dsh-governed-agent-team')
WS = ROOT / '.ai-work/workspaces/hoinv/TASK-20261004-exec-024/verification'
ARCHIVE = WS / 'map-before-exec024'

def load(path):
    return json.loads(path.read_text())

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def require(condition, message):
    if not condition:
        raise SystemExit(message)

old_map = load(ARCHIVE / 'source-code-map.json')
old_base = load(ARCHIVE / 'source-baseline.json')
old_verification = load(ARCHIVE / 'design-verification.json')
map_path = ROOT / 'docs/gat-design/source-code-map.json'
base_path = ROOT / 'docs/gat-design/source-baseline.json'
verification_path = ROOT / 'docs/gat-design/design-verification.json'
map_doc, baseline, verification = map(load, [map_path, base_path, verification_path])
require(map_doc['rows'] == old_map['rows'] and map_doc['iteration'] == old_map['iteration']
        and map_doc['wiki_documents'] == old_map['wiki_documents'], 'historical source-code-map fields changed')
require(baseline['files'] == old_base['files'] and baseline['repositories'] == old_base['repositories']
        and baseline['iteration'] == old_base['iteration'], 'historical source-baseline fields changed')
require(all(verification.get(k) == v for k, v in old_verification.items()), 'historical design-verification fields changed')
entry = map_doc['execution_composition']
scoped = baseline['execution_composition']
compatibility = load(ROOT / 'compatibility/execution-c1157f7e/manifest.json')
require(len(compatibility['source_mapping']) == 25 and len(compatibility['scenario_mapping']) == 17,
        'compatibility mapping counts changed')
require(len(scoped['files']) == len(entry['sources']) == 42, 'scoped source inventory is not 42 files')
require(scoped['mapped_source_file_count'] == 25 and scoped['mapped_scenario_file_count'] == 17,
        'scoped source/snapshot counts changed')
errors = []
for item in scoped['files']:
    path = ROOT / item['path']
    if not path.is_file() or sha(path) != item['sha256'] or path.stat().st_size != item['bytes']:
        errors.append(f"baseline hash/size mismatch: {item['path']}")
for item in entry['sources']:
    path = ROOT / item['path']
    if not path.is_file() or sha(path) != item['sha256']:
        errors.append(f"map hash mismatch: {item['path']}")
    if path.is_file():
        lines = path.read_text(errors='replace').splitlines()
        for symbol in item.get('symbols', []):
            line = symbol['line']
            if not (1 <= line <= len(lines)) or symbol['symbol'] not in lines[line - 1]:
                errors.append(f"symbol anchor mismatch: {item['path']}:{line} {symbol['symbol']}")
for test in entry['tests']:
    if not (ROOT / test['path']).is_file():
        errors.append(f"test path missing: {test['path']}")
for relative in [
    'production-attempt-03.json', 'direct-baseline-5c02ce9f/attempt-09.json',
    'assembly-final-01/assembly-receipt.json', 'public-artifact/final-attempt-01/receipt.json',
    'execution-snapshot/attempt-13-final-source.json', 'execution-snapshot/attempt-14-final-built.json',
    'execution-snapshot/candidate-copy-manifest.json', 'final-consistency.json',
    'host-runtime-build/tsc-host.json',
]:
    if not (WS / relative).is_file():
        errors.append(f'evidence receipt missing: {relative}')
for host, pin in [
    ('/tmp/gat-exec024-host-c1157f7e', 'c1157f7ed448b40c463c1a43fa595b12294fd50d'),
    ('/tmp/gat-exec024-direct-5c02ce9f', '5c02ce9f3e44dfce3f87498f65cf684194ad4572'),
]:
    actual = subprocess.run(['git', '-C', host, 'rev-parse', 'HEAD'], text=True, capture_output=True).stdout.strip()
    if actual != pin:
        errors.append(f'Host pin mismatch: {host} = {actual}')
require(entry['wiki_source_ids'] == [], 'unexpected wiki source IDs were added')
require(verification['execution_composition']['public_artifact']['reviewer_behavior_claimed'] is False,
        'packed reviewer behavior was claimed')
require(not errors, '\n'.join(errors))
print(json.dumps({
    'status': 'PASS',
    'historical_map_rows': len(old_map['rows']),
    'historical_map_iteration': old_map['iteration']['aip_id'],
    'historical_baseline_files': len(old_base['files']),
    'historical_baseline_iteration': old_base['iteration']['aip_id'],
    'historical_verification_aip': old_verification['aip'],
    'execution_composition': {
        'mapped_source_files': scoped['mapped_source_file_count'],
        'mapped_scenario_files': scoped['mapped_scenario_file_count'],
        'mapped_total': len(scoped['files']),
        'hashes_sizes_and_anchors_checked': sum(1 for _ in scoped['files']) + sum(len(x.get('symbols', [])) for x in entry['sources']),
        'test_paths_exist': len(entry['tests']),
        'wiki_source_ids': len(entry['wiki_source_ids']),
    },
}, indent=2))
