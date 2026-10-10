#!/usr/bin/env python3
"""Regression checks for release integrity and preservation of the installed formula."""
import copy
import hashlib
import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('sync_teleaf', Path(__file__).with_name('sync-teleaf.py'))
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


def fixture():
    formula = sync.TARGET.read_bytes()
    version = re.search(rb'^  version "([^"]+)"$', formula, re.MULTILINE)[1].decode()
    pairs = re.findall(rb'url "([^"]+)"\n\s+sha256 "([a-f0-9]{64})"', formula)
    assets = []
    sums = []
    for url, digest in pairs:
        url, digest = url.decode(), digest.decode()
        name = url.rsplit('/', 1)[1]
        sums.append(f'{digest}  {name}\n')
        assets.append({'name': name, 'browser_download_url': url, 'digest': 'sha256:' + digest})
    checksums = ''.join(sums).encode()
    for name, data in (('teleaf.rb', formula), ('SHA256SUMS', checksums)):
        assets.append({'name': name, 'browser_download_url': f'{sync.BASE}/releases/download/v{version}/{name}',
                       'digest': 'sha256:' + hashlib.sha256(data).hexdigest()})
    release = {'tag_name': 'v' + version, 'draft': False, 'prerelease': False, 'assets': assets}
    return release, formula, checksums


class SyncTests(unittest.TestCase):
    def test_valid_formula_is_copied_exactly_and_repeat_is_unchanged(self):
        release, formula, checksums = fixture()
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'Formula/teleaf.rb'
            fetcher = self.fetcher(release, formula, checksums)
            self.assertTrue(sync.sync(fetcher, target))
            self.assertEqual(target.read_bytes(), formula)
            self.assertFalse(sync.sync(fetcher, target))
            self.assertFalse(target.with_suffix('.rb.tmp').exists())

    @staticmethod
    def fetcher(release, formula, checksums):
        tag = release['tag_name']
        data = {sync.LATEST: json.dumps(release).encode(),
                f'{sync.BASE}/releases/download/{tag}/teleaf.rb': formula,
                f'{sync.BASE}/releases/download/{tag}/SHA256SUMS': checksums}
        return data.__getitem__

    def test_failed_validation_preserves_previous_formula(self):
        release, formula, checksums = fixture()
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'teleaf.rb'
            target.write_bytes(b'previous verified formula\n')
            release['assets'][0]['digest'] = 'sha256:' + '0' * 64
            with self.assertRaises(ValueError):
                sync.sync(self.fetcher(release, formula, checksums), target)
            self.assertEqual(target.read_bytes(), b'previous verified formula\n')

    def test_unstable_release_and_external_asset_url_are_rejected_before_download(self):
        release, _, _ = fixture()
        cases = []
        for key in ('draft', 'prerelease'):
            case = copy.deepcopy(release)
            case[key] = True
            cases.append(case)
        case = copy.deepcopy(release)
        case['assets'][-2]['browser_download_url'] = 'https://example.com/teleaf.rb'
        cases.append(case)
        for case in cases:
            calls = []
            def fetcher(url):
                calls.append(url)
                return json.dumps(case).encode()
            with self.subTest(case=case), self.assertRaises(ValueError):
                sync.sync(fetcher)
            self.assertEqual(calls, [sync.LATEST])

    def test_version_license_and_archive_corruption_are_rejected(self):
        release, formula, checksums = fixture()
        changed_formulae = (
            formula.replace(b'license "MIT"', b'license "GPL-3.0-only"'),
            re.sub(rb'version "[^"]+"', b'version "999.0.0"', formula),
            formula.replace(b'https://github.com/YoisakiKnd/teleaf/releases/', b'https://example.com/releases/'),
        )
        for changed in changed_formulae:
            with self.subTest(formula=changed), self.assertRaises(ValueError):
                sync.validate(release, changed, checksums)
        with self.assertRaises(ValueError):
            sync.validate(release, formula, checksums.replace(checksums[:64], b'0' * 64, 1))

    def test_wrong_architecture_missing_asset_and_duplicate_checksums_are_rejected(self):
        release, formula, checksums = fixture()
        pairs = re.findall(rb'url "([^"]+)"\n\s+sha256 "([a-f0-9]{64})"', formula)
        left = pairs[0][0] + b'"\n      sha256 "' + pairs[0][1]
        right = pairs[1][0] + b'"\n      sha256 "' + pairs[1][1]
        swapped = formula.replace(left, b'__swap__').replace(right, left).replace(b'__swap__', right)
        with self.assertRaises(ValueError):
            sync.validate(release, swapped, checksums)
        missing = copy.deepcopy(release)
        del missing['assets'][0]
        with self.assertRaises(KeyError):
            sync.validate(missing, formula, checksums)
        with self.assertRaises(ValueError):
            sync.validate(release, formula, checksums + checksums.splitlines(keepends=True)[0])


if __name__ == '__main__':
    unittest.main()
