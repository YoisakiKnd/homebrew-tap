# Yoisaki Homebrew tap

This tap distributes prebuilt releases of [Teleaf](https://github.com/YoisakiKnd/teleaf) and [NakuruMusic](https://github.com/YoisakiKnd/NakuruMusic).

## Teleaf · macOS / Linux

```sh
brew tap YoisakiKnd/tap
brew install YoisakiKnd/tap/teleaf
teleaf --check
```

Supports macOS 15+ and Ubuntu 24.04-compatible Linux, on ARM64 and x64. Packages include TDLib and third-party licenses; Teleaf uses MIT. No Rust toolchain or separate TDLib installation is needed.

Teleaf's formula is copied from the latest stable upstream Release after checking all four archive URLs, SHA256SUMS and GitHub asset digests. The **Sync Teleaf release** workflow runs hourly and can also be run manually; no personal access token is required. Updated formulae are tested with Homebrew on all four platforms. Failed verification leaves the previous formula intact.

Existing users of the old `YoisakiKnd/teleaf` tap should run `brew update` to apply its tap migration, then `brew upgrade YoisakiKnd/tap/teleaf`. The new tap must remain installed for future updates.

## NakuruMusic · macOS

NakuruMusic is a YouTube Music terminal client. The built-in audio player is enabled by default, so mpv is not required.

```sh
brew tap YoisakiKnd/tap
brew install nakuru-music
nakuru-music
```

Press `,` in the app to open Settings and switch to mpv if it is installed. The Formula installs the prebuilt release binary for Apple Silicon or Intel and verifies its SHA-256 checksum.
