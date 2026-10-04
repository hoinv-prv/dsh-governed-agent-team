"""Record exact test-only qualification inputs and the actual process receipt."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timezone
ws = Path(__file__).resolve().parents[1]
host = Path('/tmp/gat-exec024-host-c1157f7e')
label = sys.argv[1]
if not label.isdigit():
    raise SystemExit('numeric attempt label required')
paths = ['vitest.exec024.config.ts', 'packages/experimental/gat-core/tests/task-memory-prototype.ts',
         'packages/experimental/gat-core/tests/task-memory-qualification.spec.ts',
         'packages/experimental/gat-core/tests/task-memory-harness.ts',
         'packages/experimental/gat-core/tests/task-memory-publication-races.spec.ts',
         'packages/experimental/gat-core/tests/task-memory-prototype-before-review.ts',
         'packages/experimental/gat-core/tests/task-memory-limits.spec.ts',
         'packages/experimental/gat-core/tests/qualification-shared/tools.ts',
         'packages/experimental/gat-core/tests/qualification-shared/ownership.ts']
hashes = {}
for relative in paths:
    source = host / relative
    hashes[relative] = hashlib.sha256(source.read_bytes()).hexdigest()
    target = ws / 'qualification' / (relative if 'qualification-shared' in relative else source.name)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
tests = [paths[2], 'packages/experimental/gat-core/tests/task-memory-publication-races.spec.ts',
         'packages/experimental/gat-core/tests/task-memory-limits.spec.ts']
command = ['node', '/home/hoinv/deepseek-harness/node_modules/vitest/vitest.mjs', 'run', '--config', paths[0], *tests]
log = ws / 'verification' / f'task-memory-attempt-{label}.log'
receipt = log.with_suffix('.json')
if log.exists() or receipt.exists():
    raise SystemExit('refusing to replace an existing attempt')
started = datetime.now(timezone.utc).isoformat()
with log.open('w') as output:
    process = subprocess.run(command, cwd=host, stdout=output, stderr=subprocess.STDOUT)
receipt.write_text(json.dumps({'command': command, 'cwd': str(host), 'started_at': started,
    'exit_code': process.returncode, 'source_hashes': hashes,
    'log_sha256': hashlib.sha256(log.read_bytes()).hexdigest()}, indent=2) + '\n')
print(f'exit {process.returncode}')
print(log.read_text()[-15000:])
