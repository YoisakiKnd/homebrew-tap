cask "congminal" do
  version "0.1.1"
  sha256 "23632c91781ce01bfb056991c70f056bb311dc8a2dd65f28eebe4b1c3cdfbb63"

  url "https://github.com/YoisakiKnd/congminal/releases/download/v#{version}/congminal-#{version}-macos-universal.zip"
  name "congminal"
  desc "Native terminal emulator with SSH, SFTP, Git, and monitoring"
  homepage "https://github.com/YoisakiKnd/congminal"

  livecheck do
    url :url
    strategy :github_latest
  end

  depends_on macos: :big_sur

  app "congminal-#{version}-macos-universal/congminal.app"
  # Link the native binary; the Finder launcher resolves its own script directory.
  binary "#{appdir}/congminal.app/Contents/MacOS/congminal-bin", target: "congminal"

  caveats <<~EOS
    This app is ad-hoc signed and is not notarized. On first launch, allow it
    in System Settings > Privacy & Security if macOS blocks it.
    SSH/SFTP uses the system OpenSSH client; SFTP needs OpenSSH 8.7+ with askpass.
    The authentication helper remains inside the app bundle.
  EOS
end
