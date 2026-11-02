#!/usr/bin/env python3
"""Point the congminal cask at the latest stable release after checking its checksum."""
import hashlib
import json
import os
import re
import urllib.request
from pathlib import Path

REPOSITORY = 'YoisakiKnd/congminal'
BASE = f'https://github.com/{REPOSITORY}'
LATEST = f'https://api.github.com/repos/{REPOSITORY}/releases/latest'
TARGET = Path(__file__).resolve().parents[1] / 'Casks/congminal.rb'
URL_LINE = ('  url "https://github.com/YoisakiKnd/congminal/releases/download/'
            'v#{version}/congminal-#{version}-macos-universal.zip"')


def fetch(url):
    headers = {'User-Agent': 'congminal-homebrew-tap'}
    # Do not forward credentials to release-asset downloads or their redirects.
    if url == LATEST and os.environ.get('GH_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GH_TOKEN']
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as response:
        return response.read()


def parse_version(text):
    return tuple(int(part) for part in text.split('.'))


def verified_package(release, fetcher):
    tag = release['tag_name']
    if release['draft'] or release['prerelease'] or not re.fullmatch(r'v\d+\.\d+\.\d+', tag):
        raise ValueError('Expected a stable congminal release')
    version = tag[1:]
    assets = {asset['name']: asset for asset in release['assets']}
    if len(assets) != len(release['assets']):
        raise ValueError('Duplicate release asset names')
    filename = f'congminal-{version}-macos-universal.zip'
    for name in (filename, filename + '.sha256'):
        if name not in assets:
            raise ValueError(f'Missing release asset {name}')
        if assets[name]['browser_download_url'] != f'{BASE}/releases/download/{tag}/{name}':
            raise ValueError(f'Unexpected {name} download URL')
    sidecar = fetcher(assets[filename + '.sha256']['browser_download_url'])
    if assets[filename + '.sha256'].get('digest') != 'sha256:' + hashlib.sha256(sidecar).hexdigest():
        raise ValueError('Missing or inconsistent GitHub digest for the .sha256 asset')
    # sha256sum writes ' *' before the name in binary mode, as the Windows build does.
    match = re.fullmatch(r'([a-f0-9]{64}) [ *]' + re.escape(filename) + r'\s*', sidecar.decode('utf-8'))
    if not match:
        raise ValueError('Invalid .sha256 asset')
    if assets[filename].get('digest') != 'sha256:' + match[1]:
        raise ValueError('Missing or inconsistent GitHub digest for the macOS package')
    return version, match[1]


def update(text, version, digest):
    current = re.findall(r'^  version "([^"]+)"$', text, re.MULTILINE)
    hashes = re.findall(r'^  sha256 "([a-f0-9]{64})"$', text, re.MULTILINE)
    if len(current) != 1 or len(hashes) != 1 or text.count(URL_LINE + '\n') != 1:
        raise ValueError('Cask version, sha256 or URL template is not in the expected form')
    if parse_version(version) < parse_version(current[0]):
        raise ValueError(f'Latest release {version} is older than the cask version {current[0]}')
    if version == current[0] and digest != hashes[0]:
        raise ValueError(f'Published checksum for {version} differs from the cask')
    text = re.sub(r'^  version "[^"]+"$', f'  version "{version}"', text, flags=re.MULTILINE)
    return re.sub(r'^  sha256 "[a-f0-9]{64}"$', f'  sha256 "{digest}"', text, flags=re.MULTILINE)


def sync(fetcher=fetch, target=TARGET):
    version, digest = verified_package(json.loads(fetcher(LATEST)), fetcher)
    text = target.read_text(encoding='utf-8')
    updated = update(text, version, digest)
    if updated == text:
        print(f'congminal {version} is already current')
        return False
    temporary = target.with_suffix('.rb.tmp')
    try:
        temporary.write_text(updated, encoding='utf-8')
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
    print(f'Updated congminal to {version} (GitHub digest and .sha256 asset agree)')
    return True


if __name__ == '__main__':
    sync()
