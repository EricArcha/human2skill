from pathlib import Path


def render_list(items: list[str]) -> str:
    if not items:
        return "- 证据不足，暂不生成高置信度结论。"
    return "\n".join(f"- {item}" for item in items)


def template_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "templates" / "skill"


def render_skill(meta: dict, distilled: dict, template_path: Path | None = None) -> str:
    template = (template_path or template_root() / "base-perspective-advisor.md").read_text(encoding="utf-8")
    skill_name = f"{meta['slug']}-perspective"
    return template.format(
        skill_name=skill_name,
        description=f"{meta['display_name']} 的视角顾问 Skill",
        display_name=meta["display_name"],
        mental_models=render_list(distilled.get("mental_models", [])),
        expression_dna=render_list(distilled.get("expression_dna", [])),
        decision_heuristics=render_list(distilled.get("decision_heuristics", [])),
        profile_specific=render_list(distilled.get("profile_specific", [])),
        pressure_response=render_list(distilled.get("pressure_response", [])),
        value_order=render_list(distilled.get("value_order", [])),
        anti_patterns=render_list(distilled.get("anti_patterns", [])),
        honest_boundaries=render_list(distilled.get("honest_boundaries", [])),
    )


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


def _confidence_summary(sections: dict) -> str:
    keys = _section_keys()
    populated = sum(1 for k in keys if sections.get(k))
    total = len(keys)
    return f"已提炼 {populated}/{total} 个维度。各维度置信度视证据层级而定，证据不足维度已标注。"


def render_skill_variant(meta: dict, sections: dict, variant: str = "advisor") -> str:
    template_path = template_root() / f"{variant}.md"
    template = template_path.read_text(encoding="utf-8")
    skill_name = f"{meta['slug']}-perspective"
    return template.format(
        skill_name=skill_name,
        description=f"{meta['display_name']} 的视角顾问 Skill",
        display_name=meta["display_name"],
        mental_models=render_list(sections.get("mental_models", [])),
        expression_dna=render_list(sections.get("expression_dna", [])),
        decision_heuristics=render_list(sections.get("decision_heuristics", [])),
        profile_specific=render_list(sections.get("profile_specific", [])),
        pressure_response=render_list(sections.get("pressure_response", [])),
        value_order=render_list(sections.get("value_order", [])),
        anti_patterns=render_list(sections.get("anti_patterns", [])),
        honest_boundaries=render_list(sections.get("honest_boundaries", [])),
        confidence_summary=_confidence_summary(sections),
    )


def render_skill_variants(meta: dict, sections: dict) -> dict[str, str]:
    voice_mode = meta.get("voice_mode", "both")
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
