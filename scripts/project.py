#!/usr/bin/env python3
"""Create an editable workspace, validate explicit inputs and render one recipe."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

PLUGIN_ROOT = Path(__file__).resolve().parents[1]


def run(args, cwd=None, capture=False):
    return subprocess.run([str(a) for a in args], cwd=cwd, check=True,
                          capture_output=capture, text=capture)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def project_path(project, path):
    path = Path(path).expanduser()
    return path.resolve() if path.is_absolute() else (Path(project) / path).resolve()


def local_asset(project, name):
    if not isinstance(name, str) or not name or '\\' in name or ':' in name:
        raise ValueError('Asset must be a public-relative local path')
    relative = Path(name)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('Asset path escapes public directory')
    public = (Path(project) / 'public').resolve()
    path = (public / relative).resolve()
    if not path.is_relative_to(public) or not path.is_file():
        raise ValueError(f'Asset missing or outside public: {name}')
    return path


def node_images(nodes):
    for node in nodes or []:
        asset = node.get('asset', {})
        if asset.get('type') == 'image':
            yield asset['src']
        if asset.get('type') == 'group':
            yield from node_images(asset.get('children', []))


def raw_rgba(path, frame=None):
    cmd = ['ffmpeg', '-v', 'error', '-i', str(path)]
    if frame is not None:
        cmd += ['-vf', f'select=eq(n\\,{frame})']
        # Match the PNG capture pipeline. Direct YUV→RGBA can round differently
        # from YUV→PNG(rgb24)→RGBA, despite representing the same source frame.
        cmd += ['-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-']
        encoded = subprocess.run(cmd, check=True, capture_output=True).stdout
        data = subprocess.run(['ffmpeg', '-v', 'error', '-i', 'pipe:0', '-frames:v', '1',
                               '-f', 'rawvideo', '-pix_fmt', 'rgba', '-'], input=encoded,
                              check=True, capture_output=True).stdout
    else:
        cmd += ['-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-']
        data = subprocess.run(cmd, check=True, capture_output=True).stdout
    if not data:
        raise ValueError(f'No frame decoded from {path}')
    return data


def check_assets(project, scene):
    project = Path(project).resolve()
    names = list(node_images(scene.get('objects'))) + list(node_images(scene.get('foreground')))
    names += list(node_images([n['object'] for n in scene.get('nodes', [])]))
    evidence = []
    for name in sorted(set(names)):
        path = local_asset(project, name)
        raw_rgba(path)
        evidence.append({'asset': name, 'sha256': sha(path)})
    for stage in scene.get('stages', []):
        snapshot = local_asset(project, stage['src'])
        proof = stage['provenance']
        composition = proof['sourceComposition']
        if not isinstance(composition, str) or not composition.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Invalid source composition identity')
        video = project / 'out' / f'{composition}.mp4'
        if not video.is_file() or sha(video) != proof['sourceVideoSHA256']:
            raise ValueError(f'Completed-stage source video missing or stale: {composition}')
        if sha(snapshot) != proof['snapshotSHA256']:
            raise ValueError(f'Snapshot hash mismatch: {stage["id"]}')
        frame = proof['frame']
        if not isinstance(frame, int) or isinstance(frame, bool) or frame < 0:
            raise ValueError('Completed-stage frame must be a nonnegative integer')
        pixels = raw_rgba(snapshot)
        if len(pixels) != 1920 * 1080 * 4 or pixels != raw_rgba(video, frame):
            raise ValueError(f'Snapshot is not the actual 1920x1080 completed frame: {stage["id"]}')
        evidence.append({'stage': stage['id'], 'source': composition, 'frame': frame,
                         'snapshot_sha256': sha(snapshot), 'pixel_equal': True})
    return evidence


def check_environment(install=False):
    required = ['node', 'ffmpeg'] + (['npm'] if install else [])
    for binary in required:
        if not shutil.which(binary):
            raise ValueError(f'{binary} is required on PATH')
    version = run(['node', '--version'], capture=True).stdout.strip()
    if int(version.lstrip('v').split('.')[0]) < 22:
        raise ValueError(f'Node 22 or newer required; current {version}')


def init_project(destination, install=False):
    destination = Path(destination).expanduser().resolve()
    if destination == PLUGIN_ROOT or destination.is_relative_to(PLUGIN_ROOT):
        raise ValueError('Create video workspaces outside the plugin source/install directory')
    if destination.exists():
        raise ValueError('Destination already exists; refusing to overwrite')
    shutil.copytree(PLUGIN_ROOT / 'runtime', destination,
                    ignore=shutil.ignore_patterns('node_modules', 'out', '.npm-cache',
                                                  '.whiteboard', '__pycache__', '*.log'))
    (destination / '.whiteboard-project.json').write_text(json.dumps({
        'plugin': 'swainwong-whiteboard-video-plugin', 'version': '0.1.0',
        'mutable_workspace': True}, indent=2) + '\n')
    if install:
        check_environment(install=True)
        run(['npm', 'ci', '--cache', str(destination / '.npm-cache')], cwd=destination)
    return destination


def check_scene(project, scene_file):
    project = Path(project).expanduser().resolve()
    if project == PLUGIN_ROOT / 'runtime' or project.is_relative_to(PLUGIN_ROOT / 'dist'):
        raise ValueError('Use an initialized editable workspace, not the installed runtime')
    check_environment()
    scene_file = project_path(project, scene_file)
    data = json.loads(scene_file.read_text())
    scene = data.get('scene', data)
    run(['node', 'check-scene.cjs', str(scene_file)], cwd=project)
    assets = check_assets(project, scene)
    return project, scene, {'scene_sha256': sha(scene_file), 'effect': scene['effectId'],
                            'input_contract_passed': True, 'assets': assets,
                            'visual_acceptance': False}


def render_scene(project, scene_file, output=None):
    project, scene, evidence = check_scene(project, scene_file)
    output = project_path(project, output) if output else project / 'out' / f'{scene["effectId"]}.mp4'
    if output.exists():
        raise ValueError('Output already exists; use a new revision filename')
    if output.is_relative_to(PLUGIN_ROOT):
        raise ValueError('Render output must stay outside the plugin package')
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='whiteboard-props-') as temporary:
        props = Path(temporary) / 'props.json'
        props.write_text(json.dumps({'scene': scene}, ensure_ascii=False))
        cli = project / 'node_modules' / '.bin' / 'remotion'
        if not cli.is_file():
            raise ValueError('Dependencies missing; run npm ci in the editable workspace')
        command = [cli, 'render', 'src/index.ts', 'WhiteboardRecipe', output,
                   '--props', props, '--concurrency=2']
        browser = os.environ.get('REMOTION_BROWSER_EXECUTABLE')
        if browser:
            command += ['--browser-executable', browser]
        run(command, cwd=project)
    run(['ffmpeg', '-v', 'error', '-i', output, '-f', 'null', '-'])
    evidence.update({'output': str(output), 'sha256': sha(output), 'decode_exit': 0,
                     'normal_speed_review': False, 'owner_acceptance': False})
    receipt = output.with_suffix('.receipt.json')
    receipt.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
    return evidence


def capture_stage(project, video_file, stage_id, frame=None):
    project = Path(project).expanduser().resolve()
    video = project_path(project, video_file)
    if not re.fullmatch(r'[A-Za-z0-9_-]+', stage_id):
        raise ValueError('Stage id must contain only letters, digits, hyphen or underscore')
    if video.parent != project / 'out' or not video.is_file() or video.suffix != '.mp4':
        raise ValueError('Completed source video must be PROJECT/out/CompositionName.mp4')
    if not re.fullmatch(r'[A-Za-z0-9_-]+', video.stem):
        raise ValueError('Source video stem must be a composition identifier')
    check_environment()
    probe = json.loads(run(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-count_frames', '-show_entries', 'stream=width,height,nb_read_frames',
        '-of', 'json', video], capture=True).stdout)['streams'][0]
    if (probe['width'], probe['height']) != (1920, 1080):
        raise ValueError('Overview snapshots currently require 1920x1080 source video')
    count = int(probe['nb_read_frames'])
    frame = count - 1 if frame is None else frame
    if not isinstance(frame, int) or frame < 0 or frame >= count:
        raise ValueError('Snapshot frame is outside source video')
    src = f'assets/completed-stages/{stage_id}.png'
    destination = project / 'public' / src
    receipt = destination.with_suffix('.stage.json')
    if destination.exists() or receipt.exists():
        raise ValueError('Stage already exists; use a new revision id')
    destination.parent.mkdir(parents=True, exist_ok=True)
    run(['ffmpeg', '-v', 'error', '-i', video, '-vf', f'select=eq(n\\,{frame})',
         '-frames:v', '1', destination])
    stage = {'id': stage_id, 'src': src, 'provenance': {
        'sourceComposition': video.stem, 'sourceVideoSHA256': sha(video),
        'frame': frame, 'snapshotSHA256': sha(destination)}}
    receipt.write_text(json.dumps(stage, ensure_ascii=False, indent=2) + '\n')
    return {'stage': stage, 'stage_record': str(receipt),
            'note': 'Verify that the selected frame is a completed stage; capture alone is not creative acceptance.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    init = subs.add_parser('init'); init.add_argument('destination'); init.add_argument('--install', action='store_true')
    snap = subs.add_parser('capture-stage'); snap.add_argument('project'); snap.add_argument('video')
    snap.add_argument('--id', required=True); snap.add_argument('--frame', type=int, help='Defaults to the last decoded frame')
    for command in ['check', 'render']:
        sub = subs.add_parser(command); sub.add_argument('project'); sub.add_argument('scene', help='JSON path, absolute or relative to PROJECT')
        if command == 'render': sub.add_argument('--output', help='New MP4 path, absolute or relative to PROJECT')
    args = parser.parse_args()
    try:
        if args.command == 'init':
            result = {'workspace': str(init_project(args.destination, args.install))}
        elif args.command == 'check':
            result = check_scene(args.project, args.scene)[2]
        elif args.command == 'capture-stage':
            result = capture_stage(args.project, args.video, args.id, args.frame)
        else:
            result = render_scene(args.project, args.scene, args.output)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, KeyError, TypeError, OSError, subprocess.CalledProcessError) as error:
        print(f'Whiteboard input/runtime error: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
