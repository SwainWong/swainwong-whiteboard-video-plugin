#!/usr/bin/env python3
"""Fetch GitHub main and install/verify it before every production invocation."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

REPOSITORY = 'https://github.com/SwainWong/swainwong-whiteboard-video-plugin.git'
BRANCH = 'main'
NAME = 'swainwong-whiteboard-video-plugin'
MARKETPLACE = 'swainwong-whiteboard-local'
REQUIRED = ['SKILL.md', 'harness/HARNESS.md', 'harness/DRAWING-STYLE.md',
            'harness/PRODUCTION.md', 'harness/PRESENTATION.md', 'harness/BRAND-STATIONS.md', 'harness/PEN-SEMANTICS-CANVAS.md', 'harness/ATTENTION-SEMANTIC-REVIEW.md', 'harness/COMPOSITION-DEPTH-MIX.md']


def run(args):
    result = subprocess.run([str(a) for a in args], text=True, capture_output=True,
                            timeout=180, env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'})
    if result.returncode:
        raise RuntimeError(f'{args[0]} failed: {result.stderr.strip() or result.stdout.strip()}')
    return result.stdout


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_package(root, expected):
    """Verify all shipped bytes, not just the display version."""
    if not root.is_dir():
        return False
    try:
        manifest = json.loads((root / 'PACKAGE-MANIFEST.json').read_text())
        if manifest != expected:
            return False
        for name, sha in expected['files'].items():
            path = root / name
            if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()) or digest(path) != sha:
                return False
        for name in REQUIRED:
            if not (root / 'skills/whiteboard-video' / name).is_file():
                return False
        return json.loads((root / 'plugin.json').read_text())['version'] == expected['version']
    except (OSError, ValueError, KeyError):
        return False


def register_marketplace(market):
    entries = json.loads(run(['codex', 'plugin', 'marketplace', 'list', '--json']))['marketplaces']
    previous = next((e for e in entries if e['name'] == MARKETPLACE), None)
    changed = previous and Path(previous['root']).resolve() != market.resolve()
    if changed:
        run(['codex', 'plugin', 'marketplace', 'remove', MARKETPLACE, '--json'])
    try:
        run(['codex', 'plugin', 'marketplace', 'add', market, '--json'])
    except Exception:
        if changed:
            old_source = previous.get('marketplaceSource', {}).get('source', previous['root'])
            run(['codex', 'plugin', 'marketplace', 'add', old_source, '--json'])
        raise


def ensure_latest(state_root=None, codex_home=None):
    # Dedicated state; never pull/reset the author's checkout or edit installed caches.
    home = Path(codex_home or os.environ.get('CODEX_HOME', Path.home() / '.codex')).expanduser().resolve()
    state = Path(state_root or home / 'whiteboard-updates').expanduser().resolve()
    state.mkdir(parents=True, exist_ok=True)
    with (state / 'update.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        print('Whiteboard: fetching GitHub main before production...', file=sys.stderr)
        with tempfile.TemporaryDirectory(prefix='fetch-', dir=state) as tmp:
            checkout = Path(tmp) / 'source'
            run(['git', 'clone', '--depth', '1', '--single-branch', '--branch', BRANCH,
                 REPOSITORY, checkout])
            commit = run(['git', '-C', checkout, 'rev-parse', 'HEAD']).strip()
            version = json.loads((checkout / 'plugin.json').read_text())['version']
            if not re.fullmatch(r'\d+\.\d+\.\d+', version):
                raise RuntimeError('Remote plugin version must be a numeric semantic version')
            for name in REQUIRED:
                if not (checkout / 'skills/whiteboard-video' / name).is_file():
                    raise RuntimeError(f'Remote release is incomplete: {name}')
            market = state / 'releases' / commit
            if not market.exists():
                market.parent.mkdir(exist_ok=True)
                staged = Path(tmp) / 'market'
                run([sys.executable, checkout / 'scripts/package_plugin.py', '--output', staged])
                staged.rename(market)
            source = market / NAME
            expected = json.loads((source / 'PACKAGE-MANIFEST.json').read_text())
            if expected.get('source_commit') != commit or expected.get('version') != version:
                raise RuntimeError('Release identity does not match GitHub; production stopped')
            # Compare the cached package against a fresh build of the fetched commit.
            fresh = Path(tmp) / 'fresh'
            run([sys.executable, checkout / 'scripts/package_plugin.py', '--output', fresh])
            authoritative = json.loads((fresh / NAME / 'PACKAGE-MANIFEST.json').read_text())
            if expected != authoritative or not verify_package(source, authoritative):
                raise RuntimeError('Cached release differs from GitHub; production stopped')
            installed = home / 'plugins/cache' / MARKETPLACE / NAME / version
            register_marketplace(market)
            run(['codex', 'plugin', 'add', f'{NAME}@{MARKETPLACE}', '--json'])
            if not verify_package(installed, authoritative):
                raise RuntimeError('Codex installed bytes do not match GitHub; production stopped')
            latest = run(['git', 'ls-remote', REPOSITORY, f'refs/heads/{BRANCH}']).split()
            if not latest or latest[0] != commit:
                raise RuntimeError('GitHub main changed during update; retry before production')
            result = {'version': version, 'source_commit': commit, 'repository': REPOSITORY,
                      'branch': BRANCH, 'plugin_root': str(installed),
                      'skill': str(installed / 'skills/whiteboard-video/SKILL.md'),
                      'required_read': [str(installed / 'skills/whiteboard-video' / n) for n in REQUIRED],
                      'instruction': 'Read these current files before any planning/assets/rendering. '
                                     'Existing editable video workspaces are not overwritten.'}
            (state / 'last-success.json').write_text(json.dumps(result, indent=2) + '\n')
            return result


def main():
    try:
        print(json.dumps(ensure_latest(), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(f'Whiteboard update failed; DO NOT continue production: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
