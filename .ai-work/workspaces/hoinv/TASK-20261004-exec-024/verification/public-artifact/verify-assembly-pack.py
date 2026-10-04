#!/usr/bin/env python3
"""Compare every packed byte to the frozen joint assembly receipt."""
import hashlib
import json
import pathlib
import tarfile

base = pathlib.Path(__file__).resolve().parent
assembly = pathlib.Path('/tmp/gat-exec024-host-c1157f7e/artifacts/gat-durable-agent-final-01')
receipt = json.loads((assembly / 'assembly-receipt.json').read_text())
tarball = base / 'final-attempt-01/packed/vuhoi-gat-durable-agent-0.1.0.tgz'
files = {}
with tarfile.open(tarball, 'r:gz') as archive:
    for member in archive.getmembers():
        if not member.isfile():
            continue
        path = member.name.removeprefix('package/')
        contents = archive.extractfile(member).read()
        digest = hashlib.sha256(contents).hexdigest()
        assert receipt['outputs'].get(path) == digest, (path, digest, receipt['outputs'].get(path))
        files[path] = digest
assert {'package.json', 'README.md', 'lib/index.js', 'lib/composition.js',
        'lib/provider.js', 'lib/execution-composition.js'} <= files.keys()
assert not any(path.endswith('.tsbuildinfo') or path.startswith('lib/conformance/') for path in files)
print(json.dumps({'assemblyReceiptSha256': hashlib.sha256((assembly / 'assembly-receipt.json').read_bytes()).hexdigest(),
                  'tarballSha256': hashlib.sha256(tarball.read_bytes()).hexdigest(),
                  'packedFileCount': len(files), 'allPackedBytesMatchAssembly': True}, sort_keys=True))
