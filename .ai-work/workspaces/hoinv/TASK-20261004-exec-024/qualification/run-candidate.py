"""Seal and run the converged real Host/WK qualification candidate."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timezone
ws = Path(__file__).resolve().parents[1]
host = Path('/tmp/gat-exec024-host-c1157f7e')
root = host / 'packages/experimental/gat-core/tests'
specs = ['task-memory-qualification.spec.ts', 'task-memory-publication-races.spec.ts',
         'task-memory-limits.spec.ts', 'task-memory-lifecycle-extra.spec.ts', 'task-review-qualification.spec.ts']
inputs = [host / 'vitest.exec024.config.ts', *[root / name for name in specs],
          *[root / name for name in ['task-memory-prototype.ts', 'task-memory-harness.ts',
             'task-memory-prototype-before-review.ts', 'task-review-prototype.ts',
             'qualification-shared/ownership.ts', 'qualification-shared/tools.ts']]]
label = sys.argv[1] if len(sys.argv) > 1 else '01'
if not label.isdigit(): raise SystemExit('numeric attempt required')
log = ws / f'verification/qualification-converged-attempt-{label}.log'
receipt = log.with_suffix('.json')
archive = ws / f'qualification/converged-attempt-{label}-inputs'
if log.exists() or receipt.exists() or archive.exists():
    raise SystemExit('refusing to replace a sealed attempt')
hashes = {}
for path in inputs:
    relative = str(path.relative_to(host))
    hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    target = archive / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path, target)
command = ['node', '/home/hoinv/deepseek-harness/node_modules/vitest/vitest.mjs', 'run',
           '--config', 'vitest.exec024.config.ts', *[str((root / name).relative_to(host)) for name in specs]]
started = datetime.now(timezone.utc).isoformat()
with log.open('w') as output:
    process = subprocess.run(command, cwd=host, stdout=output, stderr=subprocess.STDOUT, timeout=90)
drift = [name for name, digest in hashes.items() if hashlib.sha256((host / name).read_bytes()).hexdigest() != digest]
receipt.write_text(json.dumps({'command': command, 'cwd': str(host), 'started_at': started,
    'exit_code': process.returncode, 'source_hashes': hashes, 'source_drift': drift,
    'log_sha256': hashlib.sha256(log.read_bytes()).hexdigest()}, indent=2) + '\n')
print(log.read_text()[-10000:])
raise SystemExit(process.returncode or bool(drift))
