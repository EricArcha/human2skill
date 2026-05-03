from pathlib import Path

from human2skill.schemas import resource_path


def template_root() -> Path:
    return resource_path("templates", "skill")


def render_list(items: list[str]) -> str:
    if not items:
        return "- 证据不足，暂不生成高置信度结论。"
    return "\n\n".join(f"- {item}" for item in items)


def _section_keys() -> tuple[str, ...]:
    return (
        "mental_models",
        "expression_dna",
        "decision_heuristics",
        "profile_specific",
        "pressure_response",
        "value_order",
        "anti_patterns",
        "honest_boundaries",
    )


def _collect_quotes(sections: dict) -> list[dict]:
    """Collect high-confidence items with quotes for the signature quotes section."""
    priority_order = (
        "mental_models",
        "expression_dna",
        "decision_heuristics",
        "profile_specific",
        "pressure_response",
        "value_order",
        "anti_patterns",
    )
    quotes: list[dict] = []
    for key in priority_order:
        for item in sections.get(key, []):
            # items are now formatted strings; we need the raw dicts.
            # _collect_quotes receives raw section dicts from _format_sections_dict.
            pass
    return quotes


def _render_quotes_section(quotes: list[dict]) -> str:
    if not quotes:
        return "_暂无高置信度原话引用。_"
    lines: list[str] = []
    for i, q in enumerate(quotes, 1):
        source = q.get("quote_source", "")
        line = f"> \"{q['quote']}\""
        if source:
            line += f" —— {source}"
        if i > 1:
            line = "\n" + line
        lines.append(line)
    return "\n".join(lines)


def _render_expression_dna(items: list[str]) -> str:
    if not items:
        return "- _证据不足，暂不生成。_"
    return "\n\n".join(f"- {item}" for item in items)


def _confidence_summary(sections: dict) -> str:
    keys = _section_keys()
    populated = sum(1 for k in keys if sections.get(k))
    total = len(keys)
    return f"已提炼 {populated}/{total} 个维度。各维度置信度视证据层级而定，证据不足维度已标注。"


def _parse_sections_for_quotes(sections: dict) -> list[dict]:
    """Walk formatted section items and extract those with embedded quotes.

    Since format_distilled_item embeds ``> "quote"`` markers, we parse them
    back out.  This avoids a second pass over the raw distillation payload.
    """
    quotes: list[dict] = []
    priority_sections = (
        "mental_models",
        "expression_dna",
        "decision_heuristics",
        "profile_specific",
        "pressure_response",
        "value_order",
        "anti_patterns",
    )
    for key in priority_sections:
        for item_text in sections.get(key, []):
            import re
            m = re.search(r'> "(.+?)"', item_text)
            if not m:
                continue
            quote_text = m.group(1)
            src_m = re.search(r' —— (.+?)$', item_text, re.MULTILINE)
            quotes.append({
                "quote": quote_text,
                "quote_source": src_m.group(1) if src_m else "",
                "section": key,
            })
    return quotes


def render_skill_variant(meta: dict, sections: dict, variant: str = "advisor") -> str:
    template_path = template_root() / f"{variant}.md"
    template = template_path.read_text(encoding="utf-8")
    skill_name = f"{meta['slug']}-lens"

    quotes_data = _parse_sections_for_quotes(sections)
    signature_quote = quotes_data[0]["quote"] if quotes_data else ""

    # Expression DNA uses block rendering (not flat list)
    expression_items = sections.get("expression_dna", [])

    return template.format(
        skill_name=skill_name,
        description=f"{meta['display_name']} 的视角顾问 Skill",
        display_name=meta["display_name"],
        signature_quote=signature_quote,
        mental_models=render_list(sections.get("mental_models", [])),
        expression_dna=_render_expression_dna(expression_items),
        decision_heuristics=render_list(sections.get("decision_heuristics", [])),
        profile_specific=render_list(sections.get("profile_specific", [])),
        pressure_response=render_list(sections.get("pressure_response", [])),
        value_order=render_list(sections.get("value_order", [])),
        anti_patterns=render_list(sections.get("anti_patterns", [])),
        honest_boundaries=render_list(sections.get("honest_boundaries", [])),
        signature_quotes=_render_quotes_section(quotes_data[:5]),
        key_quotes=_render_quotes_section(quotes_data),
        confidence_summary=_confidence_summary(sections),
    )


def render_skill_variants(meta: dict, sections: dict) -> dict[str, str]:
    voice_mode = meta.get("voice_mode", "advisor")
    result: dict[str, str] = {}
    if voice_mode in ("advisor", "both"):
        result["advisor"] = render_skill_variant(meta, sections, "advisor")
    if voice_mode in ("first_person", "both"):
        result["first_person"] = render_skill_variant(meta, sections, "first_person")
    return result


def write_skill_variants(base: Path, meta: dict, sections: dict) -> dict[str, str]:
    variants = render_skill_variants(meta, sections)
    public_skill = base / "public_skill"
    public_skill.mkdir(parents=True, exist_ok=True)

    # Write main SKILL.md; prefer advisor, fallback to first_person
    if "advisor" in variants:
        (public_skill / "SKILL.md").write_text(variants["advisor"], encoding="utf-8")
    elif "first_person" in variants:
        (public_skill / "SKILL.md").write_text(variants["first_person"], encoding="utf-8")

    # Write variant files
    for variant_name, content in variants.items():
        variant_dir = public_skill / "variants" / variant_name
        variant_dir.mkdir(parents=True, exist_ok=True)
        (variant_dir / "SKILL.md").write_text(content, encoding="utf-8")

    return variants
