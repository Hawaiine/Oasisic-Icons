#!/usr/bin/env python3
"""生成 config/parent-edge-evidence.json（确定性规则，可复现）。

规则顺序（先命中先判定，见 decision_rules）：
  R1 泛化复述        → AMBIGUOUS
  R2 平台集成语言    → PLATFORM_RELATION_ONLY
  R3 含「开发」      → DEVELOPER_PROVIDER_ONLY
  R4 品牌伞状名词    → BRAND_HIERARCHY_CONFIRMED
  R5 股权/控制词     → CORPORATE_OWNERSHIP_ONLY
  R6 未命中          → AMBIGUOUS
"""
import json
import re
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MATRIX = REPO / 'docs/references/brand-ownership-audit.md'

RULES = [
    ('R1_GENERIC_RESTATEMENT', 'AMBIGUOUS',
     "evidence contains the generic restatement '既有 parent_brand 关系仍成立'"),
    ('R2_PLATFORM_INTEGRATION', 'PLATFORM_RELATION_ONLY',
     "evidence contains platform-integration language ('平台使用' / '可通过 X' / 'available on')"),
    ('R3_DEVELOPER', 'DEVELOPER_PROVIDER_ONLY',
     "evidence contains '开发' (developer/provider statement)"),
    ('R4_BRAND_UMBRELLA', 'BRAND_HIERARCHY_CONFIRMED',
     "evidence contains an umbrella noun (品牌/产品/服务/应用/电视网/流媒体/OTT/旗下)"),
    ('R5_EQUITY_CONTROL', 'CORPORATE_OWNERSHIP_ONLY',
     "evidence contains an equity/control term (全资/多数/控股/收购/持有/股权/子公司/归属/运营/集团)"),
    ('R6_DEFAULT', 'AMBIGUOUS', 'no rule matched'),
]
UMBRELLA = ['品牌', '产品', '服务', '应用', '电视网', '流媒体', 'OTT', '旗下']
EQUITY = ['全资', '多数', '控股', '收购', '持有', '股权', '子公司', '归属', '运营', '集团']
PLATFORM = ['平台使用', '可通过 X', 'available on']


def classify(evidence):
    if not evidence:
        return 'R6_DEFAULT', 'AMBIGUOUS'
    if '既有 parent_brand' in evidence:
        return 'R1_GENERIC_RESTATEMENT', 'AMBIGUOUS'
    if any(k in evidence for k in PLATFORM):
        return 'R2_PLATFORM_INTEGRATION', 'PLATFORM_RELATION_ONLY'
    if '开发' in evidence:
        return 'R3_DEVELOPER', 'DEVELOPER_PROVIDER_ONLY'
    if any(k in evidence for k in UMBRELLA):
        return 'R4_BRAND_UMBRELLA', 'BRAND_HIERARCHY_CONFIRMED'
    if any(k in evidence for k in EQUITY):
        return 'R5_EQUITY_CONTROL', 'CORPORATE_OWNERSHIP_ONLY'
    return 'R6_DEFAULT', 'AMBIGUOUS'


def main():
    brands = json.loads((REPO / 'config/brands.json').read_text(encoding='utf-8'))
    text = MATRIX.read_text(encoding='utf-8')
    evidence = {}
    for line in text.splitlines():
        m = re.match(
            r'^\| `([^`]+)` \| ([^|]*) \| ([^|]*) \| ([^|]*) \| (.*?) \|'
            r' (CONFIRMED_PARENT|NO_PARENT|AMBIGUOUS_JV|RETIRED|SPECIAL_ENTITY)'
            r'(?:（[^|]*）)? \|', line)
        if m:
            evidence[m.group(1)] = m.group(5).strip()

    edges = []
    for entry in sorted(brands['brands'], key=lambda e: e['id']):
        child = entry.get('parent_brand')
        if not child:
            continue
        quote = evidence.get(entry['id'], '')
        rule, cls = classify(quote)
        edges.append({
            'child': entry['id'],
            'parent': child,
            'classification': cls,
            'decision_rule': rule,
            'evidence_quote': quote or '(no matching audit matrix row)',
            'evidence_source': 'docs/references/brand-ownership-audit.md §7 全量矩阵',
            'review_status': ('CONFIRMED_UNDER_CURRENT_CONTRACT'
                              if cls == 'BRAND_HIERARCHY_CONFIRMED' else 'OPEN_REVIEW'),
        })

    doc = {
        'schema_version': 2,
        'description': ('Deterministic evidence classification for every live '
                        'config/brands.json parent_brand edge. Evidence/review layer '
                        'only; it does not replace the brands.json SSOT.'),
        'important_note': ('classification is a deterministic function of the literal '
                           'evidence string in brand-ownership-audit.md §7, applied '
                           'through the ordered decision_rules. It is a triage aid, not '
                           'proof of real-world brand hierarchy; reviewers must read '
                           'evidence_quote and review_status.'),
        'allowed_classifications': ['BRAND_HIERARCHY_CONFIRMED', 'CORPORATE_OWNERSHIP_ONLY',
                                    'DEVELOPER_PROVIDER_ONLY', 'PLATFORM_RELATION_ONLY',
                                    'AMBIGUOUS'],
        'decision_rules': [{'rule': r, 'classification': c, 'condition': d}
                           for r, c, d in RULES],
        'edges': edges,
    }
    (REPO / 'config/parent-edge-evidence.json').write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    counts = Counter(e['classification'] for e in edges)
    meaning = {
        'BRAND_HIERARCHY_CONFIRMED': 'The evidence string names the child as a brand/product/service under the parent (umbrella language).',
        'CORPORATE_OWNERSHIP_ONLY': 'The evidence string records equity/control/operation; it does not by itself state a brand umbrella.',
        'DEVELOPER_PROVIDER_ONLY': 'The evidence string records development/operation, not a brand umbrella.',
        'PLATFORM_RELATION_ONLY': 'The evidence string records platform access/hosting/distribution only.',
        'AMBIGUOUS': 'Generic restatement, organisation-unit language, or no matchable evidence.',
    }
    lines = [
        '# Parent Edge Semantic Evidence Audit',
        '',
        '> 本文档由 `scripts/gen-parent-edge-evidence.py` 生成，与 `config/parent-edge-evidence.json` 同源，'
        '请勿手工编辑。它是对全部 live `parent_brand` edge 的**证据分级**，不修改 `config/brands.json`。',
        '',
        '## Contract',
        '',
        '`parent_brand` is valid only when the child is presented as a sub-brand/product brand under the '
        'immediate parent, or the parent is the direct brand umbrella. Corporate ownership, '
        'developer/provider status, platform hosting, and distribution are **not** sufficient by themselves.',
        '',
        '## Decision rules（按顺序，先命中先判定）',
        '',
        '| # | Rule | Classification | Condition |',
        '|---:|---|---|---|',
    ]
    for i, (r, c, d) in enumerate(RULES, 1):
        lines.append('| %d | `%s` | `%s` | %s |' % (i, r, c, d))
    lines += [
        '',
        '> **重要限制**：分级是 evidence 字符串的确定性函数，不是现实世界归属的证明；'
        '`BRAND_HIERARCHY_CONFIRMED` 也只表示**证据文本**具备品牌伞状措辞，仍需人工按 primary source 复核。'
        '若后续修订 §7 矩阵的证据文本，必须重跑本生成器，计数会随之变化。',
        '',
        '## Results',
        '',
        '| Classification | Count | Interpretation |',
        '|---|---:|---|',
    ]
    for c in doc['allowed_classifications']:
        lines.append('| `%s` | %d | %s |' % (c, counts[c], meaning[c]))
    lines += [
        '| **Total** | **%d** | **All live edges extracted from `config/brands.json`.** |' % len(edges),
        '',
        '## Architecture finding',
        '',
        '**BLOCKER:** 旧方法论把「全资或多数控股」直接记为 `CONFIRMED_PARENT`，这只证明 corporate control，'
        '不必然证明 Brand / Product Hierarchy。因此本 manifest 不把 ownership-only、developer/provider-only '
        '与泛化复述的行静默升级为已闭合。',
        '',
        '当前 SSOT 的 115 条边**未被修改**。后续闭合必须逐边补 primary-source Brand Hierarchy 证据，'
        '或由人工明确裁决。',
        '',
    ]
    for c in doc['allowed_classifications']:
        vals = ['`%s → %s`' % (e['child'], e['parent']) for e in edges if e['classification'] == c]
        lines += ['### %s' % c, '', ', '.join(vals) if vals else '*(none)*', '']
    (REPO / 'docs/references/parent-edge-semantic-audit.md').write_text(
        '\n'.join(lines).rstrip('\n') + '\n', encoding='utf-8')
    print('edges', len(edges))
    print('classification', dict(counts))
    print('rules', dict(Counter(e['decision_rule'] for e in edges)))


if __name__ == '__main__':
    main()
