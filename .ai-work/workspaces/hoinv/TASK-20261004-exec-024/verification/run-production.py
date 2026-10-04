"""Seal exact plugin candidate and run bounded production checks on qualified Host."""
import hashlib,json,shutil,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
ws=Path(__file__).resolve().parents[1]
root=Path('/home/hoinv/work/dsh-governed-agent-team')
host=Path('/tmp/gat-exec024-host-c1157f7e')
label=sys.argv[1]
if not label.isdigit():raise SystemExit('numeric attempt required')
archive=ws/f'verification/production-attempt-{label}-inputs'
receipt=ws/f'verification/production-attempt-{label}.json'
if archive.exists() or receipt.exists():raise SystemExit('sealed attempt already exists')
package=root/'packages/durable-agent'
inputs=[*package.glob('src/*.ts'),*package.glob('tests/execution-*.ts'),package/'package.json',package/'tsdown.config.ts',*package.glob('tsconfig*.json')]
root_hashes={}
for p in inputs:
 rel=p.relative_to(root);root_hashes[str(rel)]=hashlib.sha256(p.read_bytes()).hexdigest()
 dest=archive/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
 mirror=host/'packages/experimental/gat-durable-agent'/p.relative_to(package)
 if hashlib.sha256(mirror.read_bytes()).hexdigest()!=root_hashes[str(rel)]:raise SystemExit('Host mirror mismatch: '+str(rel))
config=host/'vitest.exec024.production.config.ts'
config_hash=hashlib.sha256(config.read_bytes()).hexdigest()
shutil.copyfile(config,archive/'vitest.exec024.production.config.ts')
commands=[['node','/home/hoinv/deepseek-harness/node_modules/vitest/vitest.mjs','run','--config','vitest.exec024.production.config.ts',*[f'packages/experimental/gat-durable-agent/tests/{p.name}' for p in sorted((package/'tests').glob('execution-*.spec.ts'))]],['node','/home/hoinv/deepseek-harness/node_modules/typescript/bin/tsc','-b','packages/experimental/gat-durable-agent/tsconfig.execution-conformance.json','--pretty','false']]
checks=[]
for i,cmd in enumerate(commands,1):
 log=ws/f'verification/production-attempt-{label}-check-{i}.log'
 with log.open('w') as output:r=subprocess.run(cmd,cwd=host,stdout=output,stderr=subprocess.STDOUT,timeout=150)
 checks.append({'command':cmd,'exit_code':r.returncode,'log':log.name,'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()})
 print(log.read_text()[-4000:])
 if r.returncode:break
changed=[p for p,d in root_hashes.items() if hashlib.sha256((root/p).read_bytes()).hexdigest()!=d]
receipt.write_text(json.dumps({'started_at':datetime.now(timezone.utc).isoformat(),'root_source_hashes':root_hashes,'host':str(host),'host_head':'c1157f7ed448b40c463c1a43fa595b12294fd50d','config_sha256':config_hash,'checks':checks,'root_source_drift':changed},indent=2)+'\n')
raise SystemExit(any(c['exit_code'] for c in checks) or bool(changed))
