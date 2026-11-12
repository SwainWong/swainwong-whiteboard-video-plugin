import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('updater', ROOT / 'scripts/update_latest.py')
u = importlib.util.module_from_spec(spec); spec.loader.exec_module(u)


class UpdateTests(unittest.TestCase):
    def fixture(self, base):
        source = base / 'remote'
        subprocess.run([sys.executable, ROOT / 'scripts/package_plugin.py', '--output', source], check=True, capture_output=True)
        repo = source / u.NAME
        subprocess.run(['git', 'init', str(repo)], check=True, capture_output=True)
        subprocess.run(['git', '-C', str(repo), 'add', '.'], check=True, capture_output=True)
        subprocess.run(['git', '-C', str(repo), '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-m', 'fixture'], check=True, capture_output=True)
        subprocess.run(['git', '-C', str(repo), 'branch', '-M', 'main'], check=True, capture_output=True)
        return repo

    def test_fresh_fetch_install_integrity_and_same_version_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); repo = self.fixture(base); home = base / 'codex'; state = base / 'state'
            calls = []; selected = []; real_run = u.run
            def fake(args):
                calls.append([str(a) for a in args])
                if args[0] != 'codex': return real_run(args)
                if args[2:4] == ['marketplace', 'list']: return '{"marketplaces": []}'
                if args[2] == 'marketplace': selected[:] = [Path(args[4])]; return '{}'
                package = selected[0] / u.NAME
                version = json.loads((package / 'plugin.json').read_text())['version']
                target = home / 'plugins/cache' / u.MARKETPLACE / u.NAME / version
                shutil.copytree(package, target, dirs_exist_ok=True)
                return '{}'
            with patch.object(u, 'REPOSITORY', str(repo)), patch.object(u, 'run', side_effect=fake):
                first = u.ensure_latest(state, home)
                second = u.ensure_latest(state, home)
                self.assertEqual(first['source_commit'], second['source_commit'])
                self.assertEqual(sum(c[:2] == ['git', 'clone'] for c in calls), 2)
                (repo / 'README.md').write_text('Changed without version bump\n')
                real_run(['git', '-C', repo, 'add', '.'])
                real_run(['git', '-C', repo, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-m', 'change'])
                third = u.ensure_latest(state, home)
                self.assertEqual(first['version'], third['version'])
                self.assertNotEqual(first['source_commit'], third['source_commit'])
                self.assertEqual((Path(third['plugin_root']) / 'README.md').read_text(), 'Changed without version bump\n')

    def test_offline_stops_even_with_previous_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / 'last-success.json').write_text('{}')
            with patch.object(u, 'run', side_effect=RuntimeError('offline')):
                with self.assertRaisesRegex(RuntimeError, 'offline'): u.ensure_latest(root, root / 'home')

    def test_installer_success_without_correct_bytes_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp); repo=self.fixture(base); real_run=u.run
            with patch.object(u, 'REPOSITORY', str(repo)), patch.object(u, 'run', side_effect=lambda a: ('{"marketplaces": []}' if a[2:4]==['marketplace','list'] else '{}') if a[0]=='codex' else real_run(a)):
                with self.assertRaisesRegex(RuntimeError, 'installed bytes'): u.ensure_latest(base/'state', base/'home')

    def test_marketplace_migration_and_rollback(self):
        previous={'marketplaces':[{'name':u.MARKETPLACE,'root':'/old/market'}]}
        with patch.object(u,'run',side_effect=[json.dumps(previous),'{}',RuntimeError('install failure'),'{}']) as runner:
            with self.assertRaisesRegex(RuntimeError,'install failure'): u.register_marketplace(Path('/new/market'))
            self.assertEqual(runner.call_args_list[1].args[0][2:4],['marketplace','remove'])
            self.assertEqual(runner.call_args_list[-1].args[0][4],'/old/market')

    def test_cli_does_not_init_when_update_fails(self):
        sys.path.insert(0, str(ROOT/'scripts'))
        import project
        import update_latest
        with tempfile.TemporaryDirectory() as tmp:
            destination=Path(tmp)/'new'
            with patch.object(sys, 'argv', ['project.py','init',str(destination)]), patch.object(update_latest,'ensure_latest',side_effect=RuntimeError('offline')):
                self.assertEqual(project.main(),1)
                self.assertFalse(destination.exists())

    def test_cli_delegates_to_verified_new_entrypoint(self):
        sys.path.insert(0, str(ROOT/'scripts'))
        import project
        import update_latest
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'scripts').mkdir()
            (root/'scripts/project.py').write_text('def main(verified_release=None):\n    return 23 if verified_release["version"] == "9.0.0" else 1\n')
            with patch.object(sys,'argv',['project.py','init',str(root/'new')]),patch.object(update_latest,'ensure_latest',return_value={'plugin_root':str(root),'version':'9.0.0'}):
                self.assertEqual(project.main(),23)
                self.assertFalse((root/'new').exists())


if __name__ == '__main__': unittest.main()
