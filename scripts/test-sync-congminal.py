#!/usr/bin/env python3
"""Regression checks for congminal cask synchronization."""
import hashlib
import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('sync_congminal', Path(__file__).with_name('sync-congminal.py'))
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)

DIGEST = 'a' * 64


def fixture(version='9.8.7', digest=DIGEST, separator='  '):
    tag = 'v' + version
    name = f'congminal-{version}-macos-universal.zip'
    sidecar = f'{digest}{separator}{name}\n'.encode()
    url = f'{sync.BASE}/releases/download/{tag}/'
    release = {'tag_name': tag, 'draft': False, 'prerelease': False, 'assets': [
        {'name': name, 'browser_download_url': url + name, 'digest': 'sha256:' + digest},
        {'name': name + '.sha256', 'browser_download_url': url + name + '.sha256',
         'digest': 'sha256:' + hashlib.sha256(sidecar).hexdigest()},
    ]}
    data = {sync.LATEST: json.dumps(release).encode(), url + name + '.sha256': sidecar}
    return release, data


def fetcher(release, data):
    data = dict(data)
    data[sync.LATEST] = json.dumps(release).encode()
    return data.__getitem__


class SyncTests(unittest.TestCase):
    def run_sync(self, release, data, cask=None):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'congminal.rb'
            target.write_text(cask or sync.TARGET.read_text(encoding='utf-8'), encoding='utf-8')
            before = target.read_text(encoding='utf-8')
            try:
                changed = sync.sync(fetcher(release, data), target)
            except ValueError:
                self.assertEqual(target.read_text(encoding='utf-8'), before)
                raise
            return changed, before, target.read_text(encoding='utf-8')

    def test_newer_release_changes_only_version_and_checksum(self):
        changed, before, after = self.run_sync(*fixture())
        self.assertTrue(changed)
        self.assertIn('  version "9.8.7"\n', after)
        self.assertIn(f'  sha256 "{DIGEST}"\n', after)
        strip = lambda text: re.sub(r'^  (version|sha256) "[^"]+"$', '', text, flags=re.MULTILINE)
        self.assertEqual(strip(before), strip(after))

    def test_binary_mode_checksum_line_is_accepted(self):
        changed, _, after = self.run_sync(*fixture(separator=' *'))
        self.assertTrue(changed)
        self.assertIn(DIGEST, str(after))

    def test_current_release_is_unchanged(self):
        cask = sync.TARGET.read_text(encoding='utf-8')
        version = re.search(r'^  version "([^"]+)"$', cask, re.MULTILINE)[1]
        digest = re.search(r'^  sha256 "([a-f0-9]{64})"$', cask, re.MULTILINE)[1]
        changed, before, after = self.run_sync(*fixture(version, digest))
        self.assertFalse(changed)
        self.assertEqual(before, after)

    def test_rejected_releases_keep_the_previous_cask(self):
        cases = []
        release, data = fixture()
        release['prerelease'] = True
        cases.append((release, data))
        release, data = fixture()
        release['assets'][0]['digest'] = 'sha256:' + 'b' * 64
        cases.append((release, data))
        release, data = fixture()
        del release['assets'][0]['digest']
        cases.append((release, data))
        release, data = fixture()
        release['assets'][1]['browser_download_url'] += '?x'
        cases.append((release, data))
        release, data = fixture()
        release['assets'].pop()
        cases.append((release, data))
        cases.append(fixture('0.0.1'))
        cask = sync.TARGET.read_text(encoding='utf-8')
        version = re.search(r'^  version "([^"]+)"$', cask, re.MULTILINE)[1]
        cases.append(fixture(version, 'c' * 64))
        for release, data in cases:
            with self.subTest(release=release['tag_name']), self.assertRaises(ValueError):
                self.run_sync(release, data)

    def test_tampered_sidecar_is_rejected(self):
        release, data = fixture()
        key = next(key for key in data if key.endswith('.sha256'))
        data[key] = data[key].replace(b'a', b'b', 1)
        with self.assertRaises(ValueError):
            self.run_sync(release, data)

    def test_unexpected_cask_layout_is_rejected(self):
        cask = sync.TARGET.read_text(encoding='utf-8').replace('macos-universal.zip"', 'macos.zip"')
        with self.assertRaises(ValueError):
            self.run_sync(*fixture(), cask=cask)


if __name__ == '__main__':
    unittest.main()
