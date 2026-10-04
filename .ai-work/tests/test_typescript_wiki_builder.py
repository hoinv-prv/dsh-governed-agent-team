"""TS lexical extraction, dependencies, collision safety, dry-run and refresh checks."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
TOOLING = Path(__file__).resolve().parents[1] / 'tooling'
sys.path.insert(0, str(TOOLING))
from build_typescript_wiki_metas import extract_typescript_facts, resolve_import
from _common import parse_frontmatter, dump_frontmatter

class BuilderTests(unittest.TestCase):
    def test_imports(self):
        f = extract_typescript_facts('''// import './fake';
const s = "class Fake {}";
import type {Foo} from './foo.js';
export {Bar} from './bar';
import './side';
const lazy = import('./lazy');
export interface Thing {}
export function run() {}
''')
        self.assertEqual(set(f['imports']), {'./foo.js', './bar', './side', './lazy'})
        self.assertEqual(f['classes'], [])
        self.assertEqual(f['functions'], ['run'])
        self.assertIn('Thing', f['declarations']['interface'])

    def test_build_and_refresh(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / '.ai-work').mkdir()
            src = root / 'src'
            src.mkdir()
            for name, text in {'main.ts': "import {Foo} from './foo.js';", 'foo.ts': 'export interface Foo {}',
                               'foo-bar.ts': 'export type X = string;', 'foo_bar.ts': 'export type Y = string;',
                               'view.tsx': 'export const View = () => <div/>;'}.items():
                (src / name).write_text(text)
            self.assertEqual(resolve_import('./foo.js', src / 'main.ts', {(src / 'foo.ts'): 'FOO'}), 'FOO')
            args = [sys.executable, str(TOOLING / 'build_typescript_wiki_metas.py'), '--project-root', str(root),
                    '--root', str(src), '--source-prefix', 'TS-TEST', '--meta-subdir', 'typescript']
            subprocess.run(args + ['--dry-run'], check=True, capture_output=True)
            out = root / '.ai-work/wiki_sources/meta/typescript'
            self.assertFalse(out.exists())
            subprocess.run(args, check=True, capture_output=True)
            metas = list(out.glob('*.md'))
            self.assertEqual(len(metas), 5)
            main = next(p for p in metas if parse_frontmatter(p.read_text())[0]['module'] == 'main.ts')
            fm, body = parse_frontmatter(main.read_text())
            self.assertIn('role: imports', body)
            for section in ('Summary', 'Knowledge Targets', 'Lookup Keys'):
                self.assertIn('## ' + section, body)
            fm['promotion_status'] = 'reviewed'
            main.write_text(dump_frontmatter(fm) + body)
            subprocess.run(args, check=True, capture_output=True)
            self.assertEqual(parse_frontmatter(main.read_text())[0]['promotion_status'], 'reviewed')

if __name__ == '__main__':
    unittest.main()
