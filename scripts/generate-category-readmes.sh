#!/usr/bin/env bash
# generate-category-readmes.sh — 为每个分类自动生成 README 清单
set -euo pipefail

# 切换到仓库根目录（scripts/ 的父目录）
cd "$(dirname "$0")/.."

ICONS_DIR="icons"

generate_readme() {
  local dir="$1"
  local name="$2"
  local desc="$3"

  local total=0
  local brands=()

  for f in "$dir"/*.png; do
    [ -f "$f" ] || continue
    total=$((total + 1))
    base=$(basename "$f" .png)
    clean=$(echo "$base" | sed -E 's/[-_][0-9]+$//; s/\([0-9]+\)$//')
    brands+=("$clean")
  done

  cat > "$dir/README.md" << README_EOF
# ${name} / ${desc}

> 共 **${total}** 个图标

| 文件名 | 说明 |
|:---|---|
README_EOF

  for f in "$dir"/*.png; do
    [ -f "$f" ] || continue
    base=$(basename "$f" .png)
    echo "| \`${base}.png\` | \`${base}\` |" >> "$dir/README.md"
  done

  echo "  ✓ $dir ($total icons)"
}

# 动态扫描所有分类目录
for dir in "$ICONS_DIR"/*/; do
  [ -d "$dir" ] || continue
  category=$(basename "$dir")
  case "$category" in
    AI)        generate_readme "$dir" "🤖 AI" "人工智能服务" ;;
    Apple)     generate_readme "$dir" "🍎 Apple" "苹果生态" ;;
    Country)   generate_readme "$dir" "🌍 Country" "国家与地区旗帜" ;;
    Crypto)    generate_readme "$dir" "₿ Crypto" "加密货币与区块链" ;;
    DevOps)    generate_readme "$dir" "🛠 DevOps" "开发运维与云服务" ;;
    Drive)     generate_readme "$dir" "☁️ Drive" "云盘与存储" ;;
    Education) generate_readme "$dir" "📚 Education" "教育平台" ;;
    Finance)   generate_readme "$dir" "💰 Finance" "金融理财" ;;
    Game)      generate_readme "$dir" "🎮 Game" "游戏平台" ;;
    General)   generate_readme "$dir" "🔧 General" "通用策略" ;;
    Google)    generate_readme "$dir" "🔎 Google" "Google 服务" ;;
    Health)    generate_readme "$dir" "🏥 Health" "健康与运动" ;;
    Media)     generate_readme "$dir" "🎬 Media" "影音流媒体" ;;
    Microsoft) generate_readme "$dir" "🪟 Microsoft" "微软服务" ;;
    Music)     generate_readme "$dir" "🎵 Music" "音乐服务" ;;
    News)      generate_readme "$dir" "📰 News" "新闻与资讯" ;;
    Payment)   generate_readme "$dir" "💳 Payment" "支付" ;;
    Proxy)     generate_readme "$dir" "🌐 Proxy" "代理线路与协议" ;;
    Shopping)  generate_readme "$dir" "🛒 Shopping" "购物" ;;
    Social)    generate_readme "$dir" "👥 Social" "社交" ;;
    Surge)     generate_readme "$dir" "⚡ Surge" "Surge 应用图标" ;;
    Telecom)   generate_readme "$dir" "📡 Telecom" "运营商" ;;
    Tool)      generate_readme "$dir" "🔩 Tool" "工具" ;;
    *)         generate_readme "$dir" "$category" "$category" ;;
  esac
done

echo ""
echo "全部 README 生成完毕"
