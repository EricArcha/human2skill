from pathlib import Path


def render_list(items: list[str]) -> str:
    if not items:
        return "- 证据不足，暂不生成高置信度结论。"
    return "\n".join(f"- {item}" for item in items)


def render_skill(meta: dict, distilled: dict, template_path: Path | None = None) -> str:
    template = (template_path or Path("templates/skill/base-perspective-advisor.md")).read_text(encoding="utf-8")
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
        honest_boundaries=render_list(distilled.get("honest_boundaries", [])),
    )
