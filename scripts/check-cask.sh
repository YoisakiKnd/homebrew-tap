#!/usr/bin/env bash
# 装好的 NotionQuill.app 和 Casks/notionquill.rb 里写的是不是一回事。
#
# 由 .github/workflows/test-notionquill.yml 调用。输出会被包进 CI 的注解里 ——
# 写这个 cask 的人（在 Linux 上）读不到 job 日志，只能靠注解。
#
# 单独放成一个文件，是为了能本地 bash -n 一眼，而不是在 YAML 里套 heredoc。
set -euo pipefail

CASK_VERSION=$(ruby -e 'puts File.read("Casks/notionquill.rb")[/version "([^"]+)"/, 1]')
echo "cask 里写的版本：$CASK_VERSION"

# 装到哪儿去了问 brew，不假设 /Applications
APP=$(brew list --cask notionquill | grep -E '\.app$' | head -1 || true)
if [ -z "$APP" ]; then
  echo "brew list 里没有 .app："
  brew list --cask notionquill
  exit 1
fi
echo "装上的是：$APP"

# 读 Info.plist 用 PlistBuddy：defaults 对「带 .plist 后缀的路径」这种 domain
# 会说不存在，跟要查的字段没关系也照样失败
PLIST="$APP/Contents/Info.plist"
APP_VERSION=$(/usr/libexec/PlistBuddy -c "Print :CFBundleShortVersionString" "$PLIST")
echo "Info.plist 里的版本：$APP_VERSION"
if [ "$CASK_VERSION" != "$APP_VERSION" ]; then
  echo "版本和 cask 对不上"
  exit 1
fi

# 可执行文件叫什么从 Info.plist 读，不写死 —— 起名权在那边
EXEC=$(/usr/libexec/PlistBuddy -c "Print :CFBundleExecutable" "$PLIST")
BIN="$APP/Contents/MacOS/$EXEC"
if [ ! -x "$BIN" ]; then
  echo "可执行文件不在：$BIN"
  ls -la "$APP/Contents/MacOS"
  exit 1
fi

# universal dmg：一个可执行文件里得同时有 arm64 和 x86_64，
# 否则 Intel 的机器装上了也起不来
file "$BIN"
ARCHS=$(lipo -archs "$BIN")
echo "架构：$ARCHS"
case "$ARCHS" in
  *arm64*) ;;
  *) echo "缺 arm64（$ARCHS）"; exit 1 ;;
esac
case "$ARCHS" in
  *x86_64*) ;;
  *) echo "缺 x86_64（$ARCHS）"; exit 1 ;;
esac

# 未签名：把实际情况打出来，但不作为通过条件（Gatekeeper 拦的是第一次打开，不是装）
echo -n "quarantine: "
xattr -p com.apple.quarantine "$APP" 2>/dev/null || echo "（没有这个属性）"

echo "全部对上了。"