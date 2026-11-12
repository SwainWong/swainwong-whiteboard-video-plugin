import importlib.util
import json
import shutil
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/project.py'
spec = importlib.util.spec_from_file_location('whiteboard_project', SCRIPT)
project = importlib.util.module_from_spec(spec)
spec.loader.exec_module(project)


class WorkspaceContracts(unittest.TestCase):
    @unittest.skipUnless(shutil.which('ffmpeg'), 'FFmpeg required for pixel pipeline regression')
    def test_png_capture_pixel_pipeline_matches_video_frame(self):
        with tempfile.TemporaryDirectory() as tmp:
            video = Path(tmp) / 'fixture.mp4'; png = Path(tmp) / 'frame.png'
            project.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'testsrc2=s=32x32:r=1',
                         '-frames:v', '1', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', video])
            project.run(['ffmpeg', '-v', 'error', '-i', video, '-frames:v', '1', png])
            self.assertEqual(project.raw_rgba(png), project.raw_rgba(video, 0))

    def test_relative_paths_resolve_in_workspace_not_invocation_cwd(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(project.project_path(tmp, 'out/clip.mp4'), (Path(tmp) / 'out/clip.mp4').resolve())
            self.assertEqual(project.project_path(tmp, 'examples/scene.json'), (Path(tmp) / 'examples/scene.json').resolve())

    def test_asset_path_and_nested_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / 'public').mkdir()
            asset = root / 'public' / 'image.png'; asset.write_bytes(b'fixture')
            self.assertEqual(project.local_asset(root, 'image.png'), asset.resolve())
            for bad in ['../image.png', 'assets/../../image.png', '/tmp/image.png',
                        'https://example.org/a.png', 'file:a.png', 'a\\b.png', 'missing.png']:
                with self.subTest(bad=bad), self.assertRaises(ValueError):
                    project.local_asset(root, bad)

    def test_symlink_escape_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / 'public').mkdir()
            secret = root / 'outside'; secret.write_text('fixture')
            (root / 'public' / 'alias').symlink_to(secret)
            with self.assertRaises(ValueError): project.local_asset(root, 'alias')

    def test_existing_workspace_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp); marker = target / 'keep'; marker.write_text('unchanged')
            with self.assertRaises(ValueError): project.init_project(target)
            self.assertEqual(marker.read_text(), 'unchanged')

    def test_snapshot_source_hash_and_pixels(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / 'public').mkdir(); (root / 'out').mkdir()
            picture = root / 'public' / 'stage.png'; picture.write_bytes(b'png-fixture')
            video = root / 'out' / 'Completed.mp4'; video.write_bytes(b'video-fixture')
            proof = {'sourceComposition': 'Completed', 'sourceVideoSHA256': project.sha(video),
                     'snapshotSHA256': project.sha(picture), 'frame': 25}
            scene = {'stages': [{'id': 'stage1', 'src': 'stage.png', 'provenance': proof}]}
            pixels = b'\0' * (1920 * 1080 * 4)
            with patch.object(project, 'raw_rgba', return_value=pixels):
                self.assertTrue(project.check_assets(root, scene)[0]['pixel_equal'])
            with patch.object(project, 'raw_rgba', side_effect=[pixels, b'wrong pixels']):
                with self.assertRaisesRegex(ValueError, 'actual'): project.check_assets(root, scene)
            video.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError, 'stale'): project.check_assets(root, scene)

    def test_pen_image_asset_identity_and_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'public').mkdir(); (root/'public'/'photo.png').write_bytes(b'fixture')
            scene={'pen':{'layers':[{'id':'photo','image':{'src':'photo.png'}}]}}
            with patch.object(project,'raw_rgba',return_value=b'pixels'):
                self.assertEqual(project.check_assets(root,scene)[0]['asset'],'photo.png')
            scene['pen']['layers'][0]['image']['src']='../outside.png'
            with self.assertRaises(ValueError): project.check_assets(root,scene)

    def test_recursive_image_discovery(self):
        nodes = [{'asset': {'type': 'group', 'children': [
            {'asset': {'type': 'image', 'src': 'photo.png'}}]}}]
        self.assertEqual(list(project.node_images(nodes)), ['photo.png'])


if __name__ == '__main__': unittest.main()
