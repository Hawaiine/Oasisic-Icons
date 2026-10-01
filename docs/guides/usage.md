# Oasisic-Icons 使用指南

本节包含各代理工具的图标配置指南。所有直链统一使用 `raw.githubusercontent.com`（**不使用 jsDelivr**）。

图标 URL 结构：

```
https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/<分类>/<品牌名>/<文件名>.png
```

- 默认图标：`<品牌名>.png`，例如 `icons/Media/Netflix/Netflix.png`
- 变体图标：命名规范保留 `<品牌名>NN.png`（两位零填充），但**当前不属于 canonical 资产模型**
  （1 brand = 1 canonical asset = 1 surge 条目），因此**不会**进入 `config/surge-icon.json`。
  品牌目录内出现非 canonical PNG 时，`scripts/generate-icon-json.sh` 会显式报错并退出非 0，
  `ci-validate-icons.py` 第 8 组同样会拦截；启用变体属独立架构变更，需同步改生成器 / 校验器 / 本文档。

---

## 批量图标订阅（JSON）

```
https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/config/surge-icon.json
```

在客户端的「策略组图标 / 图标订阅」入口中添加该 URL（Loon、Stash、Egern、Clash Meta 等支持图标订阅的版本）。

> `config/surge-icon.json` 是图标清单订阅，不是脚本，请勿填入 `script-path` 之类字段。

---

## Surge

在策略组**同一行的末尾**追加 `icon-url=`（Surge 的策略组参数必须与策略组写在同一行，不能另起一行）：

```ini
[Proxy Group]
Netflix = select, HK, TW, JP, SG, icon-url=https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/Media/Netflix/Netflix.png

Telegram = select, SG, JP, US, HK, icon-url=https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/Communication/Telegram/Telegram.png
```

## Clash Meta / Mihomo

字段是 `icon:`（单数，字符串）：

```yaml
proxy-groups:
  - name: Netflix
    type: select
    proxies: [HK, TW, JP, SG]
    icon: https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/Media/Netflix/Netflix.png

  - name: Telegram
    type: select
    proxies: [SG, JP, US]
    icon: https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/Communication/Telegram/Telegram.png
```

## Loon

在 `[Proxy Group]` 的策略组行末尾追加 `,img-url =`（注意是 `img-url`，不是 `icon`；同样必须写在同一行）：

```ini
[Proxy Group]
Netflix = select, HK, TW, JP, SG, img-url = https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/Media/Netflix/Netflix.png

Telegram = select, SG, JP, US, HK, img-url = https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/Communication/Telegram/Telegram.png
```

## Quantumult X

```ini
[policy]
static=Netflix, HK, TW, JP, SG, img-url=https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/Media/Netflix/Netflix.png
static=Telegram, SG, JP, US, HK, img-url=https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/Communication/Telegram/Telegram.png
```

> 图标 URL 只应出现在 `[policy]` 段，不要使用「URL 重写 / MITM 劫持」的写法。

## Stash

```yaml
proxy-groups:
  - name: Netflix
    type: select
    proxies: [HK, TW, JP, SG]
    icon: https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/Media/Netflix/Netflix.png
```

## Egern

Egern 的字段是 `policy_groups`（列表项按类型分键，如 `select:`／`auto_test:`），图标写在类型块内的 `icon:`，值可以是 SF Symbols 名或图片 URL：

```yaml
policy_groups:
  - select:
      name: Netflix
      policies: [HK, TW, JP, SG]
      icon: https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/Media/Netflix/Netflix.png
```

---

## 图片直链格式

```
# 通用格式
https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/<分类>/<品牌名>/<文件名>.png

# 图标订阅 JSON（清单）
https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/config/surge-icon.json
```

## 网络受限时的取舍

`raw.githubusercontent.com` 在国内可能不稳定。本仓库**不提供 jsDelivr 地址**，如需加速请自行在前置代理或镜像上处理，不要修改仓库内的示例为标准之外的 CDN 形式。