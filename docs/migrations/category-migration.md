# 分类迁移记录 / Category Migration

> 方案 C 彻底重构（2026-09-29）。基线 `2d9af1f`（24 分类 / 280 品牌 / 367 PNG）→ 31 分类 / 280 品牌 / 367 PNG。
> 数量守恒已验证（git 移动，未改图片内容；SHA-256 前后一致）。

## 一级分类变化

| 旧分类 | 处置 | 说明 |
|---|---|---|
| DevOps | 已删除 | → 拆入 Cloud（Cloudflare/Docker/MikroTik/OpenWrt/Oracle/Synology）+ Amazon/AWS + Microsoft/Azure |
| Drive | 已删除 | → CloudStorage（云盘）+ Alibaba/AliCloud |
| General | 已删除 | → System（16 个系统图标）+ AI/Manus + Tencent/QQMail + Communication/NetEaseMail + Utilities/Baidu/MetaBrainz |
| Tool | 已删除 | → Development/GitHub、Education/Duolingo+Z-Library、Hardware/DJI、Transport/Airport+DiDi+Uber+SF-Express、Media/TMDB、Health/Keep、Utilities/其余 7 个 |
| Telecom | 重组 | → 只保留 4 家运营商；8 个手机品牌 → Hardware，Aqara/Mijia → Home |
| Media | 重组 | → 移出 PrimeVideo（Amazon）、TencentVideo/WeTV（Tencent）、Douyin（Social）、KKBOX（Music）、BBC（保留 Media） |
| Social | 重组 | → 移出通讯类 8 个 → Communication，腾讯系 4 个 → Tencent |

**新增分类（11）**：

| 分类 | 来源 | 品牌数 |
|---|---|---|
| Amazon | 新增 | 6 |
| Alibaba | 新增 | 5 |
| Tencent | 新增 | 7 |
| Cloud | 新增 | 6 |
| CloudStorage | 新增 | 8 |
| Communication | 新增 | 11 |
| Hardware | 新增 | 9 |
| Home | 新增 | 2 |
| System | 新增 | 19 |
| Transport | 新增 | 4 |
| Utilities | 新增 | 9 |
