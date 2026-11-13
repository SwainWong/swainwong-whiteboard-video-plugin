#!/usr/bin/env python3
"""Build a clean, relocatable plugin and local marketplace without runtime state."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NAME = 'swainwong-whiteboard-video-plugin'
FOLDERS = ['skills', 'docs', 'scripts', 'tests', 'runtime/src', 'runtime/public',
           'runtime/examples', 'runtime/tests']
FILES = ['plugin.json', 'README.md', 'AGENTS.md', 'runtime/package.json',
         'runtime/package-lock.json', 'runtime/tsconfig.json', 'runtime/composition-map.json',
         'runtime/check-scene.cjs', 'runtime/render-all.py', 'runtime/build-stage-snapshots.py',
         'runtime/README.md']
BLOCKED = {'node_modules', '__pycache__', '.npm-cache', '.whiteboard', '.git', 'out'}


def package(output):
    output = Path(output).resolve()
    if output.exists():
        raise ValueError('Build output already exists; choose a fresh directory')
    staged = output / NAME
    staged.mkdir(parents=True)
    candidates = [ROOT / file for file in FILES if (ROOT / file).is_file()]
    for folder in FOLDERS:
        if (ROOT / folder).exists():
            candidates.extend((ROOT / folder).rglob('*'))
    version = json.loads((ROOT / 'plugin.json').read_text())['version']
    try:
        commit = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True, stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError:
        commit = None
    inventory = {}
    for source in sorted(set(candidates)):
        rel = source.relative_to(ROOT)
        if not source.is_file() or any(part in BLOCKED for part in rel.parts):
            continue
        if source.is_symlink() or not source.resolve().is_relative_to(ROOT):
            raise ValueError(f'Cannot package symlink/external file: {rel}')
        if source.suffix in {'.mp4', '.mov', '.wav', '.log', '.pyc', '.zip'} or source.name.startswith('.env'):
            continue
        target = staged / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        inventory[str(rel)] = hashlib.sha256(target.read_bytes()).hexdigest()
    (staged / 'PACKAGE-MANIFEST.json').write_text(json.dumps({
        'name': NAME, 'version': version, 'source_commit': commit, 'files': inventory,
        'excludes': ['dependencies', 'rendered videos', 'reference video', 'machine state', 'credentials']
    }, indent=2) + '\n')
    market = output / '.agents/plugins/marketplace.json'
    market.parent.mkdir(parents=True)
    market.write_text(json.dumps({'name': 'swainwong-whiteboard-local',
        'interface': {'displayName': 'SwainWong Whiteboard Video'},
        'plugins': [{'name': NAME, 'source': {'source': 'local', 'path': f'./{NAME}'},
                     'policy': {'installation': 'AVAILABLE', 'authentication': 'ON_INSTALL'},
                     'category': 'Productivity'}]}, indent=2) + '\n')
    archive = output / f'{NAME}-{version}.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as bundle:
        for path in staged.rglob('*'):
            if path.is_file(): bundle.write(path, path.relative_to(output))
        bundle.write(market, market.relative_to(output))
    from host_adapter import entry
    buddy=output/f'{NAME}-{version}-workbuddy.zip'
    with zipfile.ZipFile(buddy,'w',zipfile.ZIP_DEFLATED) as bundle:
        bundle.writestr('whiteboard-video/SKILL.md',entry('"<本Skill目录>/package/scripts/update_latest.py"'))
        for path in staged.rglob('*'):
            if path.is_file():bundle.write(path,Path('whiteboard-video/package')/path.relative_to(staged))
    return {'workbuddy_archive':str(buddy),'marketplace': str(output), 'plugin': str(staged), 'archive': str(archive),
            'file_count': len(inventory), 'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default=str(ROOT / 'dist'))
    args = parser.parse_args()
    print(json.dumps(package(args.output), indent=2))
