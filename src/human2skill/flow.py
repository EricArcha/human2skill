from __future__ import annotations

import json
from pathlib import Path

from human2skill.distillation import (
    distillation_to_sections,
    find_overconfident_distillation_items,
    validate_distillation,
)
from human2skill.evidence import find_overconfident_claims
from human2skill.evidence_builder import empty_evidence_pack
from human2skill.generator import render_skill_variants, write_skill_variants
from human2skill.intake import create_person
from human2skill.reviewer import structured_review
from human2skill.scenario import build_scenario_replay_report
from human2skill.storage import snapshot_version, write_json
from human2skill.timeutils import utc_now_iso


BLOCKING_CONFLICT_RESOLUTIONS = {"halt_for_review"}


def blocking_conflicts(pack: dict) -> list[dict]:
    return [
        conflict
        for conflict in pack.get("conflicts", [])
        if conflict.get("resolution") in BLOCKING_CONFLICT_RESOLUTIONS
    ]


def create_project_person(
    *,
    root: Path,
    slug: str,
    display_name: str,
    profile_type: str | None,
    relationship_to_user: str,
    use_case: str,
    voice_mode: str | None = None,
    now: str | None = None,
) -> Path:
    """Initialize a complete person project at root/outputs/slug.

    Creates the full directory layout, person.meta.json, an empty evidence
    pack, and an empty source index.
    """
    base = create_person(
        root=root,
        slug=slug,
        display_name=display_name,
        profile_type=profile_type,
        relationship_to_user=relationship_to_user,
        use_case=use_case,
        voice_mode=voice_mode,
        now=now,
    )

    # Create empty evidence pack.
    pack = empty_evidence_pack(slug)
    write_json(base / "private_evidence" / "evidence_pack.json", pack)

    # Create empty source index.
    source_index = {
        "schema_version": "1",
        "person_slug": slug,
        "sources": [],
    }
    write_json(base / "private_evidence" / "source_index.json", source_index)

    return base


def _load_person_meta(base: Path) -> dict:
    return json.loads((base / "person.meta.json").read_text(encoding="utf-8"))


def _load_evidence_pack(base: Path) -> dict:
    return json.loads((base / "private_evidence" / "evidence_pack.json").read_text(encoding="utf-8"))


def build_from_distillation(
    base: Path,
    distillation: dict,
    generated_at: str | None = None,
) -> dict:
    """Orchestrate a full skill build from a distillation payload.

    1. Load and validate the evidence pack + distillation.
    2. Render skill variants and write them.
    3. Run structured review for each variant.
    4. Write review results and snapshot the version.

    Returns a result dict with keys ``review``, ``variants``, and ``snapshot``.
    """
    resolved_generated_at = generated_at or utc_now_iso()

    # Load person meta and evidence pack.
    meta = _load_person_meta(base)
    person_slug = meta["slug"]
    pack = _load_evidence_pack(base)

    # Collect available claim IDs and detect overconfident claims.
    available_claim_ids = {c["claim_id"] for c in pack.get("claims", [])}
    overconfident = find_overconfident_claims(pack) + find_overconfident_distillation_items(distillation, pack)

    # Validate the distillation payload.
    validate_distillation(distillation, available_claim_ids, person_slug)

    # Write distillation.json.
    write_json(base / "private_evidence" / "distillation.json", distillation)

    # Map distillation to sections and render variants.
    sections = distillation_to_sections(distillation)
    variants = write_skill_variants(base, meta, sections)

    # Run structured review for each rendered variant.
    reviews: dict[str, dict] = {}
    unresolved_conflicts = blocking_conflicts(pack)

    for variant_name, content in variants.items():
        reviews[variant_name] = structured_review(
            person_slug=person_slug,
            variant=variant_name,
            content=content,
            overconfident_claims=overconfident,
            unresolved_conflicts=unresolved_conflicts,
            generated_at=resolved_generated_at,
        )

    # Run scenario replay if scenario_tests are present in distillation.
    scenario_tests = distillation.get("scenario_tests", [])
    scenario_report = None
    if scenario_tests:
        scenario_report = build_scenario_replay_report(
            person_slug=person_slug,
            variant="advisor",
            generated_at=resolved_generated_at,
            scenarios=scenario_tests,
        )

    # Write each review into the reviews directory.
    reviews_dir = base / "private_evidence" / "reviews"
    for variant_name, report in reviews.items():
        review_path = reviews_dir / f"{variant_name}.json"
        write_json(review_path, report)

    # Write scenario report if available.
    if scenario_report is not None:
        write_json(reviews_dir / "scenario.json", scenario_report)

    # Only snapshot if all variant reviews passed AND scenario report passes.
    all_passed = all(report["passed"] for report in reviews.values())
    if scenario_report is not None:
        all_passed = all_passed and scenario_report.get("passed", False)
    if all_passed:
        lifecycle = meta.get("lifecycle", {})
        version = lifecycle.get("version", "v1")
        snapshot = snapshot_version(base, version)
    else:
        snapshot = None

    # For the result, return the advisor review as the primary 'review'.
    advisor_review = reviews.get("advisor", list(reviews.values())[0] if reviews else {})

    return {
        "review": advisor_review,
        "variants": variants,
        "snapshot": snapshot,
        "scenario": scenario_report,
    }


def detect_update_conflicts(pack: dict) -> dict:
    """Check the evidence pack for conflicts that block an incremental update.

    Any conflict with ``resolution == "halt_for_review"`` causes the update
    to be halted.  Returns a dict with two keys:

    * ``halted`` (bool) -- whether the update should be blocked
    * ``conflicts`` (list[dict]) -- the blocking conflict records
    """
    blocking = blocking_conflicts(pack)
    return {
        "halted": len(blocking) > 0,
        "conflicts": blocking,
    }


def summarize_update(
    added_sources: list[str],
    changed_claims: list[str],
    conflicts: list[str],
) -> str:
    """Produce a short Markdown summary of an incremental update.

    Each argument is a list of human-readable identifiers.
    """
    lines: list[str] = []

    if added_sources:
        lines.append("## 新增来源")
        for src in added_sources:
            lines.append(f"- {src}")
        lines.append("")

    if changed_claims:
        lines.append("## 变更声明")
        for claim in changed_claims:
            lines.append(f"- {claim}")
        lines.append("")

    if conflicts:
        lines.append("## 冲突")
        for conflict in conflicts:
            lines.append(f"- {conflict}")
        lines.append("")

    return "\n".join(lines).rstrip()
