class NakuruMusic < Formula
  desc "YouTube Music terminal client with built-in audio playback"
  homepage "https://github.com/YoisakiKnd/NakuruMusic"
  version "0.2.2"
  license "GPL-3.0-only"

  depends_on :macos

  if Hardware::CPU.arm?
    url "https://github.com/YoisakiKnd/NakuruMusic/releases/download/v0.2.2/nakuru-music-v0.2.2-aarch64-apple-darwin.tar.gz"
    sha256 "df346fe7ad86bf247c59ff14280e4a355bf06f0244551797d924f432b1759e2b"
  else
    url "https://github.com/YoisakiKnd/NakuruMusic/releases/download/v0.2.2/nakuru-music-v0.2.2-x86_64-apple-darwin.tar.gz"
    sha256 "dcdd876b8dc5d097fd4e4620c440939e0aa9a1703e32b36230a060a5137d6c60"
  end

  def install
    bin.install Dir["**/nakuru-music"].fetch(0)
  end

  test do
    assert_predicate bin/"nakuru-music", :executable?
  end
end
