#!/usr/bin/env python3
"""
Automated quality check for human2skill generated SKILL.md files.
Checks 6 pass criteria against the rendered skill content.

Usage:
    python3 quality_check.py <SKILL.md path>

Criteria (adapted from nuwa-skill):
    1. Mental model count: 3-7
    2. Limitations per model: each model has limits
    3. Expression DNA distinctiveness: >=3 markers
    4. Honest boundaries: >=3 items
    5. Internal tensions: >=2 conflicts or tensions
    6. Primary source ratio: >50% (when sources are tagged)
"""

import sys
import re
from pathlib import Path


def _section_items(content: str, section_name: str) -> list[str]:
    """Extract top-level list items from a markdown section (no indentation)."""
    pattern = rf'##\s+{section_name}\s*\n(.*?)(?=\n##\s|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return []
    items = []
    for line in match.group(1).split('\n'):
        if line.startswith('- ') and len(line) > 3:
            items.append(line[2:].strip())
    return items


def check_mental_models(content: str) -> tuple[bool, str]:
    count = len(_section_items(content, '核心思维模型'))
    if count == 0:
        return False, "未检测到心智模型条目"
    passed = 3 <= count <= 7
    return passed, f"{count}个心智模型 {'✅' if passed else '❌ (应为3-7个)'}"


def check_limitations(content: str) -> tuple[bool, str]:
    # Extract raw section text and count top-level items with a 限制 sub-item
    pattern = r'##\s+核心思维模型\s*\n(.*?)(?=\n##\s|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return False, "未找到核心思维模型section"

    section = match.group(1)
    top_items = re.findall(r'^- (.+?)(?=^- |\Z)', section, re.DOTALL | re.MULTILINE)
    if not top_items:
        return False, "无心智模型条目"

    with_limits = sum(1 for item in top_items if '限制:' in item)
    passed = with_limits == len(top_items)
    return passed, f"{with_limits}/{len(top_items)}个模型有限制声明 {'✅' if passed else '❌'}"


def check_expression_dna(content: str) -> tuple[bool, str]:
    items = _section_items(content, '表达 DNA')
    dna_keywords = (
        '句式', '词汇', '语气', '高频', '节奏', '引导', '问题',
        '认可', '数据', '直接', '反问', '短句', '长句', '幽默',
        '共情', '锚定', '开场', '建议',
    )
    markers = sum(1 for item in items
                  if any(kw in item for kw in dna_keywords))
    passed = markers >= 3
    return passed, f"表达DNA特征: {markers}项 {'✅' if passed else '❌ (应≥3项)'}"


def check_honest_boundary(content: str) -> tuple[bool, str]:
    items = _section_items(content, '诚实边界')
    count = len(items)
    passed = count >= 3
    return passed, f"诚实边界: {count}条 {'✅' if passed else '❌ (应≥3条)'}"


def check_tensions(content: str) -> tuple[bool, str]:
    tension_count = len(re.findall(r'张力|矛盾|冲突|tension|paradox|一方面.*另一方面|既.*又',
                                    content, re.IGNORECASE))
    passed = tension_count >= 2
    return passed, f"内在张力: {tension_count}处 {'✅' if passed else '❌ (应≥2处)'}"


def check_primary_sources(content: str) -> tuple[bool, str]:
    primary = len(re.findall(r'一手|primary|本人|原话|direct_quote', content, re.IGNORECASE))
    secondary = len(re.findall(r'二手|secondary|转述|observer_report|推断|inference',
                                content, re.IGNORECASE))
    total = primary + secondary
    if total == 0:
        return True, "未标记来源类型（跳过检查）"
    ratio = primary / total
    passed = ratio > 0.5
    return passed, f"一手来源占比: {primary}/{total} ({ratio:.0%}) {'✅' if passed else '❌ (应>50%)'}"


def main():
    if len(sys.argv) < 2:
        print("用法: python3 quality_check.py <SKILL.md路径>")
        sys.exit(1)

    skill_path = Path(sys.argv[1])
    if not skill_path.exists():
        print(f"❌ 文件不存在: {skill_path}")
        sys.exit(1)

    content = skill_path.read_text(encoding='utf-8')

    checks = [
        ("心智模型数量", check_mental_models),
        ("模型局限性", check_limitations),
        ("表达DNA辨识度", check_expression_dna),
        ("诚实边界", check_honest_boundary),
        ("内在张力", check_tensions),
        ("一手来源占比", check_primary_sources),
    ]

    print(f"质量检查: {skill_path.name}")
    print("=" * 50)

    passed_count = 0
    total = len(checks)

    for name, check_fn in checks:
        passed, detail = check_fn(content)
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {name:<12} {status}  {detail}")
        if passed:
            passed_count += 1

    print("=" * 50)
    print(f"结果: {passed_count}/{total} 通过")

    if passed_count == total:
        print("全部通过，可以交付")
    elif passed_count >= total - 1:
        print("基本通过，建议修复不通过项后交付")
    else:
        print("多项不通过，建议回到蒸馏阶段迭代")

    sys.exit(0 if passed_count == total else 1)


if __name__ == '__main__':
    main()
