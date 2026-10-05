cask "nakuru-music" do
  arch arm: "aarch64", intel: "x86_64"

  version "0.2.0"
  sha256 arm: "c777edfe6bc5dc997286087989a915001213e822b728c9db688332dec867d7ca", intel: "a7f36c4f902e518028512de7e443769b8106592f4193edd4f955652b878199b2"

  url "https://github.com/YoisakiKnd/NakuruMusic/releases/download/v#{version}/nakuru-music-v#{version}-#{arch}-apple-darwin.tar.gz"
  name "NakuruMusic"
  desc "YouTube Music terminal client with built-in audio playback"
  homepage "https://github.com/YoisakiKnd/NakuruMusic"

  binary "nakuru-music-v#{version}-#{arch}-apple-darwin/nakuru-music"
end
