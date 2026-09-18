# 品牌中英对照 / Brand Glossary

> 本表用于维护 `icons/` 目录下各品牌的 **英文文件夹名 ↔ 中文显示名** 映射，方便消费方（如 mihomo-rules）直接引用中文名。  
> 命名原则：优先采用品牌官方中文译名；若官方无中文名，则保留英文原名。

---

## 使用示例

```yaml
# mihomo-rules 策略组
proxy-groups:
  - name: "Apple / 苹果"
    type: select
    proxies: [ 🍎 Apple ]
```

---

## A

| 英文文件夹 / Folder | 中文显示名 / Display Name |
|---------------------|--------------------------|
| Anthropic | Anthropic |
| Apple | 苹果 |
| AppleNews | Apple 新闻 |
| AWS | AWS |
| Alibaba | 阿里巴巴 |

## C

| 英文文件夹 / Folder | 中文显示名 / Display Name |
|---------------------|--------------------------|
| ChatGPT | ChatGPT |
| Cloudflare | Cloudflare |
| Copilot | Copilot |
| Crypto | 加密货币 |

## G

| 英文文件夹 / Folder | 中文显示名 / Display Name |
|---------------------|--------------------------|
| GeneralAI | 通用 AI |
| Google | 谷歌 |
| GitHub | GitHub |

## M

| 英文文件夹 / Folder | 中文显示名 / Display Name |
|---------------------|--------------------------|
| Microsoft | 微软 |
| Meta | Meta |
| MusicJapan | 日本音乐 |

## P

| 英文文件夹 / Folder | 中文显示名 / Display Name |
|---------------------|--------------------------|
| Payment | 支付 |
| Podcasts | 播客 |

## S

| 英文文件夹 / Folder | 中文显示名 / Display Name |
|---------------------|--------------------------|
| Shopping | 购物 |
| Spotify | Spotify |
| Surge | Surge |

## T

| 英文文件夹 / Folder | 中文显示名 / Display Name |
|---------------------|--------------------------|
| Telecom | 电信运营商 |
| Twitch | Twitch |

## 补充规则

1. **国家/地区类**（`Country/`）采用中文全称：`China` → 中国、`Japan` → 日本、`HongKong` → 香港 等。
2. **流媒体类**（`Media/`）采用品牌官方中文译名：`Netflix` → Netflix / 奈飞、`Bilibili` → 哔哩哔哩 / B站。
3. **策略组别名**见 `docs/references/icon-research.md` 第 3 节。
