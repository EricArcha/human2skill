#!/usr/bin/env python3
"""
Automated quality check for human2skill generated SKILL.md files.
Checks 7 pass criteria: 6 content checks + 1 corpus check.

Usage:
    python3 quality_check.py <SKILL.md path>

Criteria:
    1. Mental model count: 3-7
    2. Limitations per model: each model has limits
    3. Expression DNA distinctiveness: >=3 markers
    4. Honest boundaries: >=3 items
    5. Internal tensions: >=2 conflicts or tensions
    6. Primary source ratio: >50%
    7. Corpus archive: corpus/index.json exists with sources (when available)
"""

import json
import sys
import re
from pathlib import Path


def _find_corpus_index(skill_path: Path) -> Path | None:
    """Derive corpus/index.json path from SKILL.md location."""
    candidate = skill_path.resolve().parent.parent / "corpus" / "index.json"
    return candidate if candidate.exists() else None


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


def _model_items(content: str, section_name: str) -> list[str]:
    """Extract only the top-level model names (bolded lines) from a markdown section."""
    pattern = rf'##\s+{section_name}\s*\n(.*?)(?=\n##\s|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return []
    items = []
    for line in match.group(1).split('\n'):
        # Only count lines that start with "- **" (model titles with bold)
        # not sub-items like "- 证据:" or "- 限制:"
        if line.startswith('- **') and '**' in line[4:]:
            items.append(line[2:].strip())
    return items


def check_mental_models(content: str) -> tuple[bool, str]:
    count = len(_model_items(content, '核心思维模型'))
    if count == 0:
        return False, "未检测到心智模型条目"
    passed = 3 <= count <= 7
    return passed, f"{count}个心智模型 {'✅' if passed else '❌ (应为3-7个)'}"


def check_limitations(content: str) -> tuple[bool, str]:
    pattern = r'##\s+核心思维模型\s*\n(.*?)(?=\n##\s|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return False, "未找到核心思维模型section"

    section = match.group(1)
    # Only count lines beginning with "- **" (model name entries)
    top_items = [line for line in section.split('\n') if line.startswith('- **') and '**' in line[4:]]
    if not top_items:
        return False, "无心智模型条目"

    # Check if each model's entry (until next model or end) contains "限制:"
    entries = re.split(r'\n- \*\*', section)
    model_entries = [e for e in entries if e.strip()]
    # Skip the first split (text before first model)
    with_limits = sum(1 for e in model_entries if '限制:' in e)
    total = len(top_items)
    passed = with_limits == total
    return passed, f"{with_limits}/{total}个模型有限制声明 {'✅' if passed else '❌'}"


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


def check_primary_sources(content: str, corpus_index: dict | None = None) -> tuple[bool, str]:
    # If corpus/index.json is available, count actual sources
    if corpus_index:
        sources = corpus_index.get("sources", [])
        if not sources:
            return False, "corpus/index.json 存在但无来源记录"

        # Corpus stores file-type (txt, markdown, pdf_text), not evidence-type.
        # If types are file extensions, consider all as primary and fall back to
        # content-based keyword matching for the ratio.
        first_type = sources[0].get("type", "") if sources else ""
        if first_type in ("txt", "markdown", "pdf_text", None, ""):
            # Corpus types are file formats — fall back to content keyword matching
            return _check_primary_sources_keyword(content)

        primary_types = {"direct_quote_or_behavior", "observer_report"}
        primary = sum(1 for s in sources if s.get("type") in primary_types)
        total = len(sources)
        ratio = primary / total if total > 0 else 0
        passed = ratio > 0.5
        return passed, (
            f"一手来源: {primary}/{total} ({ratio:.0%}) "
            f"{'✅' if passed else '❌ (应>50%)'}"
        )

    return _check_primary_sources_keyword(content)


def _check_primary_sources_keyword(content: str) -> tuple[bool, str]:
    """Fallback: keyword matching in SKILL.md content."""
    primary = len(re.findall(r'一手|primary|本人|原话|direct_quote', content, re.IGNORECASE))
    secondary = len(re.findall(r'二手|secondary|转述|observer_report|推断|inference',
                                content, re.IGNORECASE))
    total = primary + secondary
    if total == 0:
        return True, "未标记来源类型（跳过检查）"
    ratio = primary / total
    passed = ratio > 0.5
    return passed, f"一手来源占比: {primary}/{total} ({ratio:.0%}) {'✅' if passed else '❌ (应>50%)'}"


def check_corpus(skill_path: Path) -> tuple[bool, str]:
    """Check if corpus/ directory exists with actual archived sources."""
    corpus_idx = _find_corpus_index(skill_path)
    if corpus_idx is None:
        return True, "无 corpus/（跳过检查，建议摄入时归档原文）"

    try:
        index = json.loads(corpus_idx.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        return False, "corpus/index.json 存在但无法解析"

    sources = index.get("sources", [])
    if not sources:
        return False, "corpus/index.json 存在但无来源记录"

    # Check each source has a corresponding raw file
    raw_dir = corpus_idx.parent / "raw"
    missing = []
    for s in sources:
        file_path = raw_dir / s.get("file", "").replace("raw/", "")
        if not file_path.exists():
            missing.append(s.get("source_id", "?"))

    if missing:
        return False, f"corpus/ 缺少原文文件: {', '.join(missing)}"

    return True, f"corpus/ 完整: {len(sources)}个来源, 原文文件齐全"


def main():
    if len(sys.argv) < 2:
        print("用法: python3 quality_check.py <SKILL.md路径>")
        sys.exit(1)

    skill_path = Path(sys.argv[1])
    if not skill_path.exists():
        print(f"❌ 文件不存在: {skill_path}")
        sys.exit(1)

    content = skill_path.read_text(encoding='utf-8')

    # Try to load corpus index for accurate primary source counting
    corpus_idx = _find_corpus_index(skill_path)
    corpus_index = None
    if corpus_idx:
        try:
            corpus_index = json.loads(corpus_idx.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, OSError):
            pass

    checks = [
        ("心智模型数量", lambda c: check_mental_models(c)),
        ("模型局限性", lambda c: check_limitations(c)),
        ("表达DNA辨识度", lambda c: check_expression_dna(c)),
        ("诚实边界", lambda c: check_honest_boundary(c)),
        ("内在张力", lambda c: check_tensions(c)),
        ("一手来源占比", lambda c: check_primary_sources(c, corpus_index)),
        ("原文归档", lambda p: check_corpus(p)),
    ]

    print(f"质量检查: {skill_path.name}")
    print("=" * 50)

    passed_count = 0
    total = len(checks)

    for name, check_fn in checks:
        if name == "原文归档":
            passed, detail = check_fn(skill_path)
        else:
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
