class NakuruMusic < Formula
  desc "YouTube Music terminal client with built-in audio playback"
  homepage "https://github.com/YoisakiKnd/NakuruMusic"
  version "0.2.1"
  license "GPL-3.0-only"

  depends_on :macos

  if Hardware::CPU.arm?
    url "https://github.com/YoisakiKnd/NakuruMusic/releases/download/v0.2.1/nakuru-music-v0.2.1-aarch64-apple-darwin.tar.gz"
    sha256 "2f500ed5648faeb5ea6dcff4f0d932614add50a7c51e8b49864d27bff629c01c"
  else
    url "https://github.com/YoisakiKnd/NakuruMusic/releases/download/v0.2.1/nakuru-music-v0.2.1-x86_64-apple-darwin.tar.gz"
    sha256 "c9072ef611906aee60f30816ff0915f2dbb0d8b69e9d9fcbffabad65d0e33ea2"
  end

  def install
    bin.install Dir["**/nakuru-music"].fetch(0)
  end

  test do
    assert_predicate bin/"nakuru-music", :executable?
  end
end
