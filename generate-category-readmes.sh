#!/usr/bin/env bash
# generate-category-readmes.sh — 为每个分类自动生成 README 清单
set -euo pipefail

cd "$(dirname "$0")"

generate_readme() {
  local dir="$1"
  local name="$2"
  local desc="$3"

  # 统计图标数
  local total=0
  local brands=()

  for f in "$dir"/*.png; do
    [ -f "$f" ] || continue
    total=$((total + 1))
    base=$(basename "$f" .png)
    # 去掉数字后缀（-1, -2, _1, _2, (1), (2) 等）去重
    clean=$(echo "$base" | sed -E 's/[-_][0-9]+$//; s/\([0-9]+\)$//')
    brands+=("$clean")
  done

  # 去重
  unique=($(printf "%s\n" "${brands[@]}" | sort -u))

  cat > "$dir/README.md" << EOF
# ${name} / ${desc}

> 共 **${total}** 个图标

| 文件名 | 说明 |
|:---|---|
EOF

  for f in "$dir"/*.png; do
    [ -f "$f" ] || continue
    base=$(basename "$f" .png)
    echo "| \`${base}.png\` | \`${base}\` |" >> "$dir/README.md"
  done

  echo "  ✓ $dir ($total icons)"
}

generate_readme "AI"         "🤖 AI"              "人工智能服务"
generate_readme "Apple"      "🍎 Apple"           "苹果生态"
generate_readme "Country"    "🌍 Country"         "国家与地区旗帜"
generate_readme "Crypto"     "₿ Crypto"           "加密货币与区块链"
generate_readme "DevOps"     "🛠 DevOps"           "开发运维与云服务"
generate_readme "Drive"      "☁️ Drive"           "云盘与存储"
generate_readme "Education"  "📚 Education"        "教育平台"
generate_readme "Finance"    "💰 Finance"          "金融理财"
generate_readme "Game"       "🎮 Game"            "游戏平台"
generate_readme "General"    "🔧 General"          "通用策略"
generate_readme "Google"     "🔎 Google"           "Google 服务"
generate_readme "Health"     "🏥 Health"           "健康与运动"
generate_readme "Media"      "🎬 Media"            "影音流媒体"
generate_readme "Microsoft"  "🪟 Microsoft"        "微软服务"
generate_readme "Music"      "🎵 Music"            "音乐服务"
generate_readme "News"       "📰 News"             "新闻与资讯"
generate_readme "Payment"    "💳 Payment"          "支付"
generate_readme "Proxy"      "🌐 Proxy"            "代理线路与协议"
generate_readme "Shopping"   "🛒 Shopping"         "购物"
generate_readme "Social"     "👥 Social"           "社交"
generate_readme "Surge"      "⚡ Surge"            "Surge 应用图标"
generate_readme "Telecom"    "📡 Telecom"          "运营商"
generate_readme "Tool"       "🔩 Tool"             "工具"

echo ""
echo "全部 README 生成完毕"