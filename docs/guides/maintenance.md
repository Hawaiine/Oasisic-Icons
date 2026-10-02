# 维护手册 / Maintenance Guide

> 本文件面向**长期维护者**：说明 Oasisic-Icons 的事实模型、一次改动的完整传播路径、
> 以及每一条命令的**真实来源**（全部从 `scripts/` 实际读取，不是猜的）。
>
> 若 CI 变红而不知从何下手：直接跳到 [§6 排障速查](#6-排障速查ci-红了怎么办)。

---

## 1. 事实模型（谁是真值，谁只是产物）

```
config/brands.json ──┐
config/categories.json ──┤  (唯二 SSOT：品牌 / 分类的事实来源)
                        │
        scripts/brand_relationships.py   ← 唯一规则引擎
        （expected_icon_path / 关系根 / 生态判定 / 父节点 README 渲染）
                        │
   ┌────────────────────┼─────────────────────┬──────────────────────┐
   ▼                    ▼                     ▼                      ▼
icons/<分类>/…/<id>/<id>.png   config/surge-icon.json   config/brand-relationships.json
（物理资产层）                  （消费面清单）            （关系派生导出）
                        │
                        ▼
README.md · docs/references/*.md · icons/**/README.md   （文档层，多为生成物）

        CI：scripts/ci-validate-icons.py（19 组）+ scripts/ci-validate-docs.py
```

三类文档的边界（混用必然腐烂）：

| 类型 | 例子 | 规则 |
|:---|:---|:---|
| **generated（生成物）** | `config/surge-icon.json`、`brand-glossary.md`、`physical-hierarchy-audit.md`、`icons/**/README.md`、README 的统计行 | 由生成器重算，CI 逐字节/逐值校验；**禁止手改**，要改就改 SSOT 或生成器 |
| **manual reference（人工参考）** | `docs/references/icon-research.md` | 可手写；快照类数字必须带日期，不得伪装成实时数据 |
| **historical / migration** | `docs/migrations/**`、`upstream-history.md`、`brand-ownership-audit.md` | 保留旧路径是其职责；被 docs 校验显式排除 |

**红线**：current 文档里的 concrete path（`icons/<…>/<file>.png`）是可验证的公开契约——
用户复制即用；路径不存在就**修文档**，绝不加永久豁免。

---

## 2. 契约（CI 强制，不是口号）

1. **1 brand = 1 canonical icon**：品牌目录内只允许 `<id>.png`；
   `Netflix01.png` / `Netflix-dark.png` / 任何第二张图都是违规。
2. **路径唯一推导**：`icon_path` 必须逐字等于 `expected_icon_path()` 的结果，
   禁止手写。物理层级：同分类中间父递归嵌套，graph root 的直系子品牌保持平铺，
   白名单母公司 / 跨分类父品牌不迁移。
3. **资产规范**：PNG / 512×512 / RGBA / 圆角 r=115 / 四角 alpha=0 / **保留原始底色**（白底必留）。
4. **全库 SHA-256 唯一**：同一图像内容不得服务两个品牌。
5. **派生文件必须自证来源**：`generated: true` + `source`；被 CI 逐项重算比对。
6. **无第二 SSOT**：任何脚本 / 文档都不得成为第二份品牌或分类真值（CI 有专项断言）。
7. **变体（variant）当前不支持**：`<id>NN.png`、`<id>-dark.png` 一律拒绝；
   要做必须先立正式 schema 再实现。

---

## 3. 新增品牌（最短正确路径）

```bash
# 0. 先同步到最新 main（不要在旧基线上改）
git fetch origin && git switch -c feat/add-<brand> origin/main

# 1. 把图标放进 icons/<分类>/<品牌名>/（深层子品牌放父品牌目录下，路径以引擎推导为准）
#    规范化（512×512 / RGBA / r=115 圆角）——只对新增/替换的图跑：
python3 scripts/normalize-icons.py --apply     # 按需；批量见 --report
python3 scripts/optimize-icons.py              # 无损重压缩（不降色型）

# 2. 用统一校验入口预检条目（确定性检查，不猜）
python3 scripts/validate-brand.py \
    --id BrandId --display-name "显示名" --category Category \
    --entity-type product_brand [--parent-brand ParentId]

# 3. 改 SSOT（config/brands.json）→ 重新生成全部派生文件
bash scripts/generate-icon-json.sh
bash scripts/generate-category-readmes.sh
python3 scripts/export-brand-relationships.py
python3 scripts/gen-physical-hierarchy-audit.py
python3 scripts/generate-brand-glossary.py
python3 scripts/update-readme-badges.py

# 4. 三件套校验 + 全量测试
python3 scripts/ci-validate-icons.py
python3 scripts/ci-validate-docs.py
python3 -m unittest discover -s tests

# 5. 提交 → 推送分支 → 开 PR（不直接推 main）
git add -A && git commit -F <提交信息文件> && git push -u origin HEAD
```

无法判定 `parent_brand`（现实归属歧义）时**不要猜**：写进
`config/brand-review-queue.json`（`is_ssot: false`）走人工裁决，裁决结论写回 SSOT 后
把队列项置 `RESOLVED` 并附 `resolved_note`。

---

## 4. 派生文件生成流程（顺序与幂等）

| 顺序 | 命令 | 产出 | 幂等性 |
|:---|:---|:---|:---|
| 1 | `bash scripts/generate-icon-json.sh` | `config/surge-icon.json` | 连续两次逐字节一致 |
| 2 | `bash scripts/generate-category-readmes.sh` | `icons/<分类>/README.md` + 父品牌 `README.md` | 同上 |
| 3 | `python3 scripts/export-brand-relationships.py` | `config/brand-relationships.json` | 同上 |
| 4 | `python3 scripts/gen-physical-hierarchy-audit.py` | `docs/references/physical-hierarchy-audit.md` | 同上 |
| 5 | `python3 scripts/generate-brand-glossary.py` | `docs/references/brand-glossary.md` | 同上 |
| 6 | `python3 scripts/update-readme-badges.py` | README 徽章/统计行 + `icon-quality-notes.md` 扫描范围句 | 命中失败即非 0 退出 |

顺序为什么是这样：1–2 直接读 SSOT；3–4 依赖关系引擎的重算结果；5–6 是最后一步的
展示层（统计口径必须基于最终状态）。全部**幂等**——重复执行 0 diff，因此可以无脑全跑。

```bash
# 一次性全跑（等价于上面 6 步，用于「不确定该跑哪个」时）
bash scripts/generate-icon-json.sh && \
bash scripts/generate-category-readmes.sh && \
python3 scripts/export-brand-relationships.py && \
python3 scripts/gen-physical-hierarchy-audit.py && \
python3 scripts/generate-brand-glossary.py && \
python3 scripts/update-readme-badges.py
```

---

## 5. 校验流程

```bash
python3 scripts/ci-validate-icons.py            # 19 组：SSOT / 命名 / 路径 / 派生物 / 文档统计 …
python3 scripts/ci-validate-icons.py --quiet    # 只输出失败项与结论（本地快速复检）
python3 scripts/ci-validate-icons.py --only Naming   # 只报告某一组（定位用）
python3 scripts/ci-validate-icons.py --json     # 机器可读（脚本消费）
python3 scripts/ci-validate-docs.py             # 文档里的 concrete path 是否真的存在
python3 -m unittest discover -s tests           # 全套单元/契约测试
```

`tests/test_mutation_matrix.py` 是**闸门健全性证据**：对仓库副本注入 32 种已知坏状态，
逐例断言校验器（必要时含生成器）非 0 退出**并报出对应归因**。它回答的是
「CI 真的会红吗」，而不是「CI 是绿的吗」——绿屏正是静默 no-op 的藏身处。

---

## 6. 排障速查（CI 红了怎么办）

| CI 报的组 | 含义 | 修复动作 |
|:---|:---|:---|
| `Brands SSOT` | SSOT 与磁盘不一致 / icon_path 违反路径规则 / JSON 解析失败 | 按报错里给出的「应为 …」修正 `config/brands.json`；解析失败会直接给出文件+行列 |
| `Naming` | 品牌目录内有非 canonical PNG | 删掉多余文件，或按契约重命名 |
| `Surge JSON` / `关系派生导出` | 派生文件与 SSOT 不一致（含手改） | 重跑第 4 节对应生成器，禁止手改产物 |
| `Glossary` / `README 统计` / `README 表格` / `README 父节点` | 文档层漂移 | 重跑 `generate-brand-glossary.py` / `update-readme-badges.py` / `generate-category-readmes.sh` |
| `物理路径` | `physical-hierarchy-audit.md` 与重算不一致 | `python3 scripts/gen-physical-hierarchy-audit.py` |
| `Category` | 分类不在 SSOT 白名单 / reserved 分类非空 | 更新 `config/categories.json` 或清理目录 |
| `Legacy paths` | 又出现了旧 ID / 旧路径段 | 见 `scripts/legacy_map.py` 与 `docs/migrations/` |
| `SHA-256 uniqueness` | 两个品牌用了同一张图 | 换掉其中一张；不得复用 |

**凡是「派生文件与 SSOT 不一致」类，修法永远是「改源头 + 重跑生成器」，不是改产物。**

---

## 7. 变更传播纪律（改任何事实之前）

任何事实变化（改名 / 移动 / 改分类 / 改 parent / 改规范值）都必须：
`changed source → dependency discovery → impact classification → synchronized changes
→ regeneration → old-value residue scan → validation`。

最少要搜一遍旧值与新值：identifier、display_name、目录名、文件名、icon_path、
category、parent_brand、对外 URL；把命中分类为
`CURRENT-SSOT / GENERATED / CURRENT-DOC / TEST / SCRIPT / HISTORICAL / MIGRATION / LEGACY / CONSUMER / FALSE-POSITIVE`
后再动手，**不允许**先 `s/OLD/NEW/g` 再想。

验收口径：`current` 侧的旧引用残留必须为 **0**（historical / migration / legacy 允许保留）。

---

## 8. 已知边界（不要「顺手修」）

- **5 个历史越界圆角资产**：`Blacklist` / `Final` / `NorthKorea` / `Airport` / `GeneralAI`
  的圆角不合当前规范，但暂无可靠高清源图——保持原样，不做有损重绘（明细见
  `docs/references/icon-quality-notes.md`）。
- **变体**：当前架构有意不支持，见 §2 第 7 条。
- **CI 绿灯 ≠ 现实语义正确**：ownnership / 合资 / 收购等现实归属无法自动计算，
  走 Review Queue 人工裁决后写回 SSOT。