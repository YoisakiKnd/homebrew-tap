#!/usr/bin/env python3
"""Sync Teleaf's published formula after checking all four platform assets."""
import hashlib
import json
import os
import re
import urllib.request
from pathlib import Path

REPOSITORY = 'YoisakiKnd/teleaf'
BASE = f'https://github.com/{REPOSITORY}'
LATEST = f'https://api.github.com/repos/{REPOSITORY}/releases/latest'
TARGET = Path(__file__).resolve().parents[1] / 'Formula/teleaf.rb'


def fetch(url):
    headers = {'User-Agent': 'teleaf-homebrew-tap'}
    # Do not forward credentials to release-asset downloads or their redirects.
    if url == LATEST and os.environ.get('GH_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GH_TOKEN']
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as response:
        return response.read()


def release_assets(release):
    tag = release['tag_name']
    if release['draft'] or release['prerelease'] or not re.fullmatch(r'v\d+\.\d+\.\d+', tag):
        raise ValueError('Expected a stable Teleaf release')
    assets = {asset['name']: asset for asset in release['assets']}
    if len(assets) != len(release['assets']):
        raise ValueError('Duplicate release asset names')
    for name in ('teleaf.rb', 'SHA256SUMS'):
        if assets[name]['browser_download_url'] != f'{BASE}/releases/download/{tag}/{name}':
            raise ValueError(f'Unexpected {name} download URL')
    return tag, assets


def check_asset(asset, content):
    digest = asset.get('digest')
    if digest and digest != 'sha256:' + hashlib.sha256(content).hexdigest():
        raise ValueError(f'GitHub digest mismatch for {asset["name"]}')


def validate(release, formula, checksums):
    tag, assets = release_assets(release)
    text = formula.decode('utf-8')
    required = (
        r'^class Teleaf < Formula$',
        r'^  homepage "' + re.escape(BASE) + r'"$',
        r'^  license "MIT"$',
        r'^  version "' + re.escape(tag[1:]) + r'"$',
    )
    if any(len(re.findall(pattern, text, re.MULTILINE)) != 1 for pattern in required):
        raise ValueError('Formula class, homepage, MIT license or version is incorrect')
    sums = {}
    for line in checksums.decode('utf-8').splitlines():
        match = re.fullmatch(r'([a-f0-9]{64})\s+(\S+)', line)
        if not match or match[2] in sums:
            raise ValueError('Invalid or duplicate SHA256SUMS entry')
        sums[match[2]] = match[1]
    blocks = re.findall(r'^  on_(macos|linux) do\n(.*?)^  end$', text, re.MULTILINE | re.DOTALL)
    if len(blocks) != 2 or {system for system, _ in blocks} != {'macos', 'linux'}:
        raise ValueError('Expected macOS and Linux formula blocks')
    if len(re.findall(r'^\s+url ', text, re.MULTILINE)) != 4:
        raise ValueError('Expected exactly four archive URLs')
    for system, block in blocks:
        architectures = re.findall(
            r'^    on_(arm|intel) do\n      url "([^"]+)"\n      sha256 "([a-f0-9]{64})"\n    end$',
            block, re.MULTILINE,
        )
        if len(architectures) != 2 or {cpu for cpu, _, _ in architectures} != {'arm', 'intel'}:
            raise ValueError(f'Missing or duplicate {system} architecture')
        for cpu, url, digest in architectures:
            arch = 'aarch64' if cpu == 'arm' else 'x86_64'
            filename = f'teleaf-{tag[1:]}-{system}-{arch}.tar.gz'
            asset = assets[filename]
            expected_url = f'{BASE}/releases/download/{tag}/{filename}'
            if url != expected_url or asset['browser_download_url'] != expected_url:
                raise ValueError(f'Unexpected archive URL for {system}-{arch}')
            if digest != sums.get(filename):
                raise ValueError(f'Formula checksum differs from SHA256SUMS: {filename}')
            if asset.get('digest') != 'sha256:' + digest:
                raise ValueError(f'Missing or inconsistent GitHub archive digest: {filename}')
    check_asset(assets['teleaf.rb'], formula)
    check_asset(assets['SHA256SUMS'], checksums)


def sync(fetcher=fetch, target=TARGET):
    release = json.loads(fetcher(LATEST))
    tag, assets = release_assets(release)
    formula = fetcher(assets['teleaf.rb']['browser_download_url'])
    checksums = fetcher(assets['SHA256SUMS']['browser_download_url'])
    validate(release, formula, checksums)
    if target.exists() and target.read_bytes() == formula:
        print(f'Teleaf {tag[1:]} is already current')
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix('.rb.tmp')
    try:
        temporary.write_bytes(formula)
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
    print(f'Updated Teleaf to {tag[1:]} (four platform URLs and SHA-256 digests verified)')
    return True


if __name__ == '__main__':
    sync()
