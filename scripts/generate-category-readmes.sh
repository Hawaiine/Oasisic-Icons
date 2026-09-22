#!/usr/bin/env bash
# generate-category-readmes.sh — 为每个分类自动生成 README 清单
# 新结构：icons/<分类>/<品牌>/<品牌>.png + <品牌>01.png...
set -euo pipefail

cd "$(dirname "$0")/.."
ICONS_DIR="icons"

generate_readme() {
  local dir="$1"
  local name="$2"
  local desc="$3"

  local total=0
  local brands=()

  # 新结构：每个品牌是一个子目录
  for brand_dir in "$dir"/*/; do
    [ -d "$brand_dir" ] || continue
    brand=$(basename "$brand_dir")
    # 统计该品牌下所有 .png 文件
    for f in "$brand_dir"*.png; do
      [ -f "$f" ] || continue
      total=$((total + 1))
    done
    brands+=("$brand")
  done

  cat > "$dir/README.md" << README_EOF
# ${name} / ${desc}

> 共 **${total}** 个图标，**${#brands[@]}** 个品牌

| 品牌 | 图标文件 |
|:---|:---|
README_EOF

  for brand in $(printf '%s\n' "${brands[@]}" | sort); do
    brand_dir="$dir/$brand"
    files=$(ls "$brand_dir"/*.png 2>/dev/null | xargs -I{} basename {} | sort | tr '\n' ' ' | sed 's/ $//')
    echo "| \`${brand}\` | \`${files}\` |" >> "$dir/README.md"
  done

  echo "  ✓ $dir ($total icons, ${#brands[@]} brands)"
}

for dir in "$ICONS_DIR"/*/; do
  [ -d "$dir" ] || continue
  category=$(basename "$dir")
  case "$category" in
    AI)        generate_readme "$dir" "🤖 AI" "人工智能服务" ;;
    Apple)     generate_readme "$dir" "🍎 Apple" "苹果生态" ;;
    Country)   generate_readme "$dir" "🌍 Country" "国家与地区旗帜" ;;
    Crypto)    generate_readme "$dir" "₿ Crypto" "加密货币与区块链" ;;
    DevOps)    generate_readme "$dir" "🛠 DevOps" "开发运维与云服务" ;;
    Development) generate_readme "$dir" "💻 Development" "开发工具" ;;
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
