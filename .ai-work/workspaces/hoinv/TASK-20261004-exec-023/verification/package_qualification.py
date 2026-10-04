"""Capture the isolated source patch without modifying its real Git index."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path('/home/hoinv/work/dsh-binding-prerequisites')
OUT = Path(__file__).resolve().parent
BASE = 'c291e7961a515f6d7af9304e7fd1d257929aef26'


def git(*args, env=None):
    return subprocess.check_output(['git', *args], cwd=ROOT, env=env)


assert git('rev-parse', 'HEAD').decode().strip() == BASE
before = git('diff', '--cached', '--binary')
changed = set(git('diff', '--name-only', '-z', 'HEAD').decode().split('\0'))
changed.update(git('ls-files', '--others', '--exclude-standard', '-z').decode().split('\0'))
files = sorted(p for p in changed if p and not p.startswith('.gat/')
               and '__pycache__' not in p
               and not p.startswith('website/.vitepress/.temp/')
               and not (p.startswith('native/system/packages/') and '/bin' in p))
with tempfile.TemporaryDirectory(prefix='exec023-source-patch-') as temporary:
    task_index = Path(temporary) / 'index'
    paths = Path(temporary) / 'paths'
    paths.write_bytes(b''.join(p.encode() + b'\0' for p in files))
    task_env = dict(os.environ, GIT_INDEX_FILE=str(task_index))
    git('read-tree', BASE, env=task_env)
    git('add', '-A', '--pathspec-from-file=' + str(paths), '--pathspec-file-nul', env=task_env)
    patch = git('diff', '--cached', '--binary', BASE, env=task_env)
assert git('diff', '--cached', '--binary') == before
(OUT / 'DSH-prerequisites.patch').write_bytes(patch)
receipt = {
    'baseline': BASE,
    'branch': git('branch', '--show-current').decode().strip(),
    'worktree': str(ROOT),
    'source_patch': 'DSH-prerequisites.patch',
    'patch_sha256': hashlib.sha256(patch).hexdigest(),
    'real_index_unchanged': True,
    'exclusions': ['operational .gat receipts', 'Python caches', 'VitePress build temporary files', 'built native platform bin'],
    'files': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
              if (ROOT / p).is_file() else None for p in files},
    'qualification_limit': 'Reviewable source plus installed GAT foundation on the approved baseline; no deployment, publication, parent binder acceptance or supported release approval.',
}
(OUT / 'source-patch-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'files': len(files), 'patch_sha256': receipt['patch_sha256'],
                  'real_index_unchanged': True}))
