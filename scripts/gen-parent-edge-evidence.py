#!/usr/bin/env python3
"""生成 config/parent-edge-evidence.json + docs/references/parent-edge-semantic-audit.md。

能力边界（必须保留，不得含糊）
------------------------------
本脚本是 **evidence-text triage（证据文本分级）**，不是 real-world relationship proof。
它只回答「审计文档 §7 那一行证据文字描述的是哪一类关系」，不回答「现实世界是否真的如此」。

数据流（单向，禁止反向）：

    primary source → structured edge evidence → human decision
                   → brands.json → 本生成器 → audit / manifest

自证循环风险（已记录，未消除）
------------------------------
证据文字来自 `docs/references/brand-ownership-audit.md`（人工研究摘要）。生成器**不重新取证**，
因此无法独立验证该摘要本身。消除风险需逐边补 `source.url` 并人工复核；当前 0/115 有 URL。

决策规则（按顺序，先命中先判定；信号优先级 = developer > ownership > umbrella > platform）
--------------------------------------------------------------------------------------
  R1 泛化复述        → UNKNOWN              / OPEN_REVIEW
  R2 开发/推出       → DEVELOPER_PROVIDER   / OPEN_REVIEW
  R3 股权/控制/归属  → CORPORATE_OWNERSHIP  / OPEN_REVIEW
  R4 品牌伞状措辞    → BRAND_HIERARCHY      / CONFIRMED
  R5 平台集成语言    → PLATFORM_INTEGRATION / OPEN_REVIEW
  R6 未命中          → UNKNOWN              / OPEN_REVIEW

为什么顺序是这样：
- 归属/控制措辞（旗下/集团/全资）必须先于伞状措辞判定——只凭「旗下」不能证明 direct brand
  umbrella（旧版曾据此把 F1TV → LibertyMedia、NowE → PCCW 误判为品牌层级）。
- 开发/提供方措辞必须先于平台措辞判定——Grok 的证据同时含「开发」与「平台可访问」，
  旧版把它整条判成 platform，掩盖了 developer 事实。
- 平台措辞放最后：它只有在没有其它更强信号时才是对该 edge 的最佳描述。
"""
import json
import re
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MATRIX = REPO / 'docs/references/brand-ownership-audit.md'
RETRIEVED_AT = '2026-09-30'

RULES = [
    ('R1_GENERIC_RESTATEMENT', 'UNKNOWN', 'OPEN_REVIEW',
     "evidence is the generic restatement '既有 parent_brand 关系仍成立'"),
    ('R2_DEVELOPER_PROVIDER', 'DEVELOPER_PROVIDER', 'OPEN_REVIEW',
     "evidence contains developer/provider language (开发/推出)"),
    ('R3_CORPORATE_OWNERSHIP', 'CORPORATE_OWNERSHIP', 'OPEN_REVIEW',
     "evidence contains ownership/control language (旗下/全资/多数/控股/收购/持有/股权/子公司/归属/集团/属/运营)"),
    ('R4_BRAND_UMBRELLA', 'BRAND_HIERARCHY', 'CONFIRMED',
     "evidence contains brand-umbrella language (品牌/自有应用/自有产品/产品/服务) and no ownership/control or developer term"),
    ('R5_PLATFORM_INTEGRATION', 'PLATFORM_INTEGRATION', 'OPEN_REVIEW',
     "evidence contains platform-access language ('平台使用' / '可通过 X' / 'available on' / '平台可访问') and no other signal"),
    ('R6_DEFAULT', 'UNKNOWN', 'OPEN_REVIEW', 'no rule matched'),
]

GENERIC = '既有 parent_brand'
PLATFORM = ['平台使用', '可通过 X', 'available on', '平台可访问']
OWNERSHIP = ['旗下', '全资', '多数', '控股', '收购', '持有', '股权', '子公司', '归属', '集团', '属 ', '运营']
DEVELOPER = ['开发', '推出']
UMBRELLA = ['品牌', '自有应用', '自有产品', '产品', '服务']

RATIONALE = {
    'UNKNOWN': '证据文字为泛化复述或无法归类，不足以判断关系类型。',
    'CORPORATE_OWNERSHIP': '证据文字描述归属/控制，未直接说明品牌伞状关系。',
    'DEVELOPER_PROVIDER': '证据文字描述开发/提供方，未直接说明品牌伞状关系。',
    'PLATFORM_INTEGRATION': '证据文字描述平台可访问/托管，不构成品牌父级。',
    'BRAND_HIERARCHY': '证据文字以品牌伞状措辞描述子品牌/产品，符合当前 parent_brand 契约。',
}

# 来源类型：仅从证据文字的括号注记推断组织与类型，不推断 URL。
SOURCE_PATTERNS = [
    ('OFFICIAL_REPORT', r'官方财报|财报|年报|投资者关系'),
    ('OFFICIAL_SITE', r'官方'),
    ('PUBLIC_REPORTING', r'公开报道|公开资料|第三方核对'),
    ('SECONDARY', r'维基|百科'),
]


def classify(evidence):
    if not evidence:
        return 'R6_DEFAULT', 'UNKNOWN', 'OPEN_REVIEW'
    if GENERIC in evidence:
        return 'R1_GENERIC_RESTATEMENT', 'UNKNOWN', 'OPEN_REVIEW'
    if any(k in evidence for k in DEVELOPER):
        return 'R2_DEVELOPER_PROVIDER', 'DEVELOPER_PROVIDER', 'OPEN_REVIEW'
    if any(k in evidence for k in OWNERSHIP):
        return 'R3_CORPORATE_OWNERSHIP', 'CORPORATE_OWNERSHIP', 'OPEN_REVIEW'
    if any(k in evidence for k in UMBRELLA):
        return 'R4_BRAND_UMBRELLA', 'BRAND_HIERARCHY', 'CONFIRMED'
    if any(k in evidence for k in PLATFORM):
        return 'R5_PLATFORM_INTEGRATION', 'PLATFORM_INTEGRATION', 'OPEN_REVIEW'
    return 'R6_DEFAULT', 'UNKNOWN', 'OPEN_REVIEW'


def source_of(evidence):
    kind = 'UNRECORDED'
    for name, pat in SOURCE_PATTERNS:
        if re.search(pat, evidence):
            kind = name
            break
    org = None
    m = re.search(r'（([^（）]{2,40}?)官方', evidence)
    if m:
        org = m.group(1)
    elif kind == 'OFFICIAL_REPORT':
        org = 'company filing'
    return {
        'organization': org,
        'url': None,
        'title': None,
        'retrieved_at': RETRIEVED_AT,
        'kind': kind,
        'url_status': 'NOT_RECORDED',
    }


def read_matrix_evidence():
    text = MATRIX.read_text(encoding='utf-8')
    evidence = {}
    for line in text.splitlines():
        m = re.match(
            r'^\| `([^`]+)` \| ([^|]*) \| ([^|]*) \| ([^|]*) \| (.*?) \|'
            r' (CONFIRMED_PARENT|NO_PARENT|AMBIGUOUS_JV|RETIRED|SPECIAL_ENTITY)'
            r'(?:（[^|]*）)? \|', line)
        if m:
            evidence[m.group(1)] = m.group(5).strip()
    return evidence


def build_edges():
    brands = json.loads((REPO / 'config/brands.json').read_text(encoding='utf-8'))
    evidence = read_matrix_evidence()
    edges = []
    for entry in sorted(brands['brands'], key=lambda e: e['id']):
        parent = entry.get('parent_brand')
        if not parent:
            continue
        quote = evidence.get(entry['id'], '')
        rule, relation, validity = classify(quote)
        edges.append({
            'child': entry['id'],
            'parent': parent,
            'relation_type': relation,
            'parent_brand_validity': validity,
            'decision_rule': rule,
            'evidence_quote': quote or '(no matching audit matrix row)',
            'evidence_layer': 'docs/references/brand-ownership-audit.md §7 全量矩阵',
            'source': source_of(quote),
            'rationale': RATIONALE[relation],
            'review_status': ('CONFIRMED_UNDER_CURRENT_CONTRACT'
                              if validity == 'CONFIRMED' else 'OPEN_REVIEW'),
        })
    return edges


def build_doc(edges):
    return {
        'schema_version': 3,
        'generated_by': 'scripts/gen-parent-edge-evidence.py',
        'description': ('Structured relation-type evidence for every live config/brands.json '
                        'parent_brand edge. Evidence/review layer only; it does not replace '
                        'the brands.json SSOT.'),
        'capability_boundary': ('Evidence-text triage derived from the brand-ownership-audit.md '
                                'research summary. It is NOT real-world relationship proof and '
                                'does not independently re-verify any primary source.'),
        'self_reference_risk': ('Evidence quotes originate from a human research summary, so the '
                                'classifier cannot validate that summary. Removing this risk '
                                'requires a recorded source.url plus human review per edge; '
                                'currently 0/%d edges carry a source URL.' % len(edges)),
        'relation_types': ['BRAND_HIERARCHY', 'CORPORATE_OWNERSHIP', 'DEVELOPER_PROVIDER',
                           'PLATFORM_INTEGRATION', 'UNKNOWN'],
        'validity_values': ['CONFIRMED', 'OPEN_REVIEW', 'REJECTED'],
        'decision_rules': [{'rule': r, 'relation_type': rt, 'parent_brand_validity': v,
                            'condition': d} for r, rt, v, d in RULES],
        'edges': edges,
    }


def render_audit(doc, edges):
    counts = Counter(e['relation_type'] for e in edges)
    vcounts = Counter(e['parent_brand_validity'] for e in edges)
    meaning = {
        'BRAND_HIERARCHY': '证据文字以品牌伞状措辞描述子品牌/产品 → 当前契约下判 CONFIRMED。',
        'CORPORATE_OWNERSHIP': '仅归属/控制/运营措辞 → 不足以证明 direct brand umbrella，OPEN_REVIEW。',
        'DEVELOPER_PROVIDER': '仅开发/提供方措辞 → 不足以证明 direct brand umbrella，OPEN_REVIEW。',
        'PLATFORM_INTEGRATION': '平台可访问/托管 → 不是 parent_brand，OPEN_REVIEW。',
        'UNKNOWN': '泛化复述或无法归类 → OPEN_REVIEW。',
    }
    lines = [
        '# Parent Edge Semantic Evidence Audit',
        '',
        '> 本文档由 `scripts/gen-parent-edge-evidence.py` 生成，与 `config/parent-edge-evidence.json` 同源，'
        '请勿手工编辑。它是对全部 live `parent_brand` edge 的**关系类型分级**，不修改 `config/brands.json`。',
        '',
        '## 能力边界 / Capability boundary',
        '',
        '本分级是 **evidence-text triage**：只回答「审计文档 §7 那一行证据文字描述的是哪一类关系」，',
        '**不回答**「现实世界是否真的如此」。`keyword hit ≠ relationship proof`。',
        '',
        '**自证循环风险（已记录，未消除）**：证据文字来自 `brand-ownership-audit.md` 这一人工研究摘要，'
        '生成器不重新取证，无法独立验证该摘要。消除风险需逐边补 `source.url` + 人工复核；'
        '当前 **0 / %d** 条 edge 记录了 source URL。' % len(edges),
        '',
        '## Decision rules（按顺序，先命中先判定）',
        '',
        '| # | Rule | relation_type | parent_brand_validity | Condition |',
        '|---:|---|---|---|---|',
    ]
    for i, (r, rt, v, d) in enumerate(RULES, 1):
        lines.append('| %d | `%s` | `%s` | `%s` | %s |' % (i, r, rt, v, d))
    lines += [
        '',
        '> **R3 必须在 R4 之前**：只凭「旗下」「集团」等归属措辞不能证明 direct brand umbrella。',
        '> 旧版把「旗下」当作伞状证据，曾把 `F1TV → LibertyMedia`、`NowE → PCCW` 等纯归属关系误判为品牌层级，本版已修正。',
        '> 同理，开发/提供方措辞（R2）先于平台措辞（R5）：Grok 的证据同时含两者，旧版整条判成 platform，掩盖了 developer 事实。',
        '',
        '## relation_type 分布',
        '',
        '| relation_type | Count | Interpretation |',
        '|---|---:|---|',
    ]
    for rt in doc['relation_types']:
        lines.append('| `%s` | %d | %s |' % (rt, counts[rt], meaning[rt]))
    lines += [
        '| **Total** | **%d** | **All live edges extracted from `config/brands.json`.** |' % len(edges),
        '',
        '## parent_brand_validity 分布',
        '',
        '| validity | Count |',
        '|---|---:|',
    ]
    for v in doc['validity_values']:
        lines.append('| `%s` | %d |' % (v, vcounts[v]))
    lines += [
        '| **Total** | **%d** |' % len(edges),
        '',
        '> `CONFIRMED` 只在 `relation_type = BRAND_HIERARCHY` 时给出，即证据文字本身已具备品牌伞状措辞。',
        '> 这不等于 primary-source 已闭合：全部 edge 的 `source.url` 仍为 `NOT_RECORDED`。',
        '',
        '## Architecture finding',
        '',
        '**BLOCKER A（未闭合）**：115 条 edge 的 `relation_type` 来自**证据文字**而非独立 primary source，'
        '分类可能受关键字影响。真正闭合需逐边补 `source.url` 并人工裁决；本轮 0/115 已记录 URL。',
        '',
        '**未修改 SSOT**：`config/brands.json` 的 115 条 `parent_brand` 本轮未被修改。',
        '',
    ]
    for rt in doc['relation_types']:
        vals = ['`%s → %s`' % (e['child'], e['parent']) for e in edges if e['relation_type'] == rt]
        lines += ['### %s' % rt, '', ', '.join(vals) if vals else '*(none)*', '']
    return '\n'.join(lines).rstrip('\n') + '\n'


def main():
    edges = build_edges()
    doc = build_doc(edges)
    (REPO / 'config/parent-edge-evidence.json').write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (REPO / 'docs/references/parent-edge-semantic-audit.md').write_text(
        render_audit(doc, edges), encoding='utf-8')
    print('edges', len(edges))
    print('relation_type', dict(Counter(e['relation_type'] for e in edges)))
    print('validity', dict(Counter(e['parent_brand_validity'] for e in edges)))
    print('rules', dict(Counter(e['decision_rule'] for e in edges)))


if __name__ == '__main__':
    main()
