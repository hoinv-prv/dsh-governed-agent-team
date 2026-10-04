#!/usr/bin/env python3
"""Read-only public artifact shape check for the four joint package entries."""
import hashlib
import json
import os
import pathlib
import re
import sys
import tarfile

base = pathlib.Path(os.environ.get('GAT_ARTIFACT_BASE', pathlib.Path(__file__).resolve().parent)).resolve()
tarball = base / 'packed' / 'vuhoi-gat-durable-agent-0.1.0.tgz'
package = base / 'consumer' / 'current'
if (package / 'package').is_dir():
    package /= 'package'
meta = json.loads((package / 'package.json').read_text())
entries = ['.', './composition', './provider', './execution-composition']
report = {'tarballSha256': hashlib.sha256(tarball.read_bytes()).hexdigest(), 'entries': {}, 'dependency': meta['dependencies'].get('@deepseek-ai/dsh-durable-agent')}
assert report['dependency'] == '0.1.0'
assert '@deepseek-ai/dsh-durable-agent' not in meta.get('peerDependencies', {})
with tarfile.open(tarball, 'r:gz') as archive:
    names = set(archive.getnames())
for key in entries:
    entry = meta['exports'][key]
    targets = {field: target.removeprefix('./') for field, target in entry.items()}
    assert all(f'package/{target}' in names for target in targets.values()), (key, targets)
    report['entries'][key] = targets
public_js = [package / meta['exports'][key]['default'].removeprefix('./') for key in entries]
texts = {path.name: path.read_text() for path in public_js}
initializer = next((package / 'lib').glob('initializer-*.js'))
tools = next((package / 'lib').glob('tools-*.js'))
assert len(list((package / 'lib').glob('tools-*.js'))) == 1
assert re.search(r'(?:class DurableOwnershipCoordinator\b|var DurableOwnershipCoordinator = class\b)', tools.read_text())
assert tools.name in texts['index.js'] and tools.name in texts['execution-composition.js']
assert initializer.name in texts['index.js'] and initializer.name in texts['composition.js']
assert tools.name in initializer.read_text()
assert '@deepseek-ai/dsh-durable-agent' in texts['provider.js']
assert '@deepseek-ai/dsh-durable-agent' in texts['execution-composition.js']
assert '@deepseek-ai/dsh-durable-agent/consumer' in initializer.read_text()
assert not any('class DurableAgentService' in text or 'class DurableAgentConsumer' in text for text in texts.values())
report['sharedOwnershipChunk'] = tools.name
report['sharedInitializerChunk'] = initializer.name
report['wkExternalized'] = True
report['noDefaultExecutionExportInDeclaration'] = not re.search(r'export\s+default', (package / meta['exports']['./execution-composition']['types'].removeprefix('./')).read_text())
assert report['noDefaultExecutionExportInDeclaration']
report['packIncludesTsbuildinfo'] = sorted(n for n in names if n.endswith('.tsbuildinfo'))
report['unshippedSrcExportPattern'] = meta['exports'].get('./src/*') if not any(n.startswith('package/src/') for n in names) else None
wk = (package / 'node_modules/@deepseek-ai/dsh-durable-agent').resolve()
host_cordis = (package / 'node_modules/@deepseek-ai/cordis').resolve()
wk_cordis = (wk / 'node_modules/@deepseek-ai/cordis').resolve()
wk_meta = json.loads((wk / 'package.json').read_text())
report['wkDeclaredCordis'] = wk_meta['dependencies'].get('@deepseek-ai/cordis')
report['hostCordisVersion'] = json.loads((host_cordis / 'package.json').read_text())['version']
report['wkResolvedCordisVersion'] = json.loads((wk_cordis / 'package.json').read_text())['version']
report['separateCordisInstances'] = os.path.realpath(host_cordis) != os.path.realpath(wk_cordis)
print(json.dumps(report, indent=2, sort_keys=True))
