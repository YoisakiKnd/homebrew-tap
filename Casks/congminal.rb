cask "congminal" do
  version "0.2.0"
  sha256 "71fc1862d94fc9f7c80cdad40497cdaa4464a3681be255c17e0e93572c76df88"

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
