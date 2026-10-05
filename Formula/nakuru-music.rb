class NakuruMusic < Formula
  desc "YouTube Music terminal client with built-in audio playback"
  homepage "https://github.com/YoisakiKnd/NakuruMusic"
  version "0.2.0"
  license "GPL-3.0-only"

  depends_on :macos

  if Hardware::CPU.arm?
    url "https://github.com/YoisakiKnd/NakuruMusic/releases/download/v0.2.0/nakuru-music-v0.2.0-aarch64-apple-darwin.tar.gz"
    sha256 "c777edfe6bc5dc997286087989a915001213e822b728c9db688332dec867d7ca"
  else
    url "https://github.com/YoisakiKnd/NakuruMusic/releases/download/v0.2.0/nakuru-music-v0.2.0-x86_64-apple-darwin.tar.gz"
    sha256 "a7f36c4f902e518028512de7e443769b8106592f4193edd4f955652b878199b2"
  end

  def install
    bin.install Dir["**/nakuru-music"].fetch(0)
  end

  test do
    assert_predicate bin/"nakuru-music", :executable?
  end
end
