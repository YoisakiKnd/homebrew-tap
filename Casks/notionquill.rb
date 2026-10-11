# 这份 cask 的 version / url / sha256 要和 NotionQuill 的 Release 对得上。
# 目前没有同步脚本：NotionQuill 发新版本时，这三行跟着改一次，
# 校验和从 Release 里的 SHA256SUMS 抄（别手算，也别抄别人贴的）。
cask "notionquill" do
  version "0.2.1"
  sha256 "c6411a28a2b1da9b65f62fa9b44d5a53889cf99b13321910e1a9c2d9c11b80cd"

  url "https://github.com/YoisakiKnd/NotionQuill/releases/download/v#{version}/NotionQuill_#{version}_universal.dmg",
      verified: "github.com/YoisakiKnd/NotionQuill/"
  name "轻羽"
  desc "Thin shell around Notion's own web app"
  homepage "https://github.com/YoisakiKnd/NotionQuill"

  app "NotionQuill.app"

  caveats <<~EOS
    The app is not signed or notarised, so Gatekeeper blocks the first launch:
    right-click the icon and choose Open, or allow it in
    System Settings → Privacy & Security.
  EOS
end