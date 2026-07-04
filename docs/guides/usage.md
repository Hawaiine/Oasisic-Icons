# PolicyIcons 使用指南

本节包含各代理工具的图标配置指南。

## Surge

在 Surge 配置的策略组中添加 `icon-url` 参数：

```ini
# Surge 配置文件策略组示例
Netflix = select, HK, TW, JP, SG
icon-url = https://raw.githubusercontent.com/Hawaiine/PolicyIcons/main/Media/Netflix.png

Telegram = select, SG, JP, US, HK
icon-url = https://raw.githubusercontent.com/Hawaiine/PolicyIcons/main/Social/Telegram(2).png
```

## Clash Meta / Mihomo

```yaml
proxy-groups:
  - name: Netflix
    type: select
    proxies: [HK, TW, JP, SG]
    icon: https://raw.githubusercontent.com/Hawaiine/PolicyIcons/main/Media/Netflix.png

  - name: Telegram
    type: select
    proxies: [SG, JP, US]
    icon: https://raw.githubusercontent.com/Hawaiine/PolicyIcons/main/Social/Telegram(2).png
```

## Loon

```ini
[Policy]
Netflix = select, HK, TW, JP, SG
icon = https://raw.githubusercontent.com/Hawaiine/PolicyIcons/main/Media/Netflix.png

Telegram = select, SG, JP, US, HK
icon = https://raw.githubusercontent.com/Hawaiine/PolicyIcons/main/Social/Telegram(2).png
```

## Quantumult X

```ini
[policy]
static=Netflix, HK, TW, JP, SG, img-url=https://raw.githubusercontent.com/Hawaiine/PolicyIcons/main/Media/Netflix.png
static=Telegram, SG, JP, US, HK, img-url=https://raw.githubusercontent.com/Hawaiine/PolicyIcons/main/Social/Telegram(2).png
```

## Stash

```yaml
proxy-groups:
  - name: Netflix
    type: select
    proxies: [HK, TW, JP, SG]
    icon: https://raw.githubusercontent.com/Hawaiine/PolicyIcons/main/Media/Netflix.png
```

## Egern

```yaml
proxies:
  Netflix:
    type: select
    proxies: [HK, TW, JP, SG]
    icon: https://raw.githubusercontent.com/Hawaiine/PolicyIcons/main/Media/Netflix.png
```

## CDN 加速（中国大陆）

```ini
# 使用 jsDelivr CDN 加速访问
icon-url = https://cdn.jsdelivr.net/gh/Hawaiine/PolicyIcons@main/Media/Netflix.png
```

## 图片直链格式

```
# 通用格式
https://raw.githubusercontent.com/Hawaiine/PolicyIcons/main/<Category>/<FileName>.png

# Surge 专用 JSON
https://raw.githubusercontent.com/Hawaiine/PolicyIcons/main/surge-icon.json
```