# Yoisaki Homebrew tap

This tap distributes [NakuruMusic](https://github.com/YoisakiKnd/NakuruMusic), a YouTube Music terminal client for macOS. The built-in audio player is enabled by default, so mpv is not required.

```sh
brew tap YoisakiKnd/tap
brew install nakuru-music
nakuru-music
```

Press `,` in the app to open Settings and switch to mpv if it is installed. The Formula installs the prebuilt release binary for Apple Silicon or Intel and verifies its SHA-256 checksum.
