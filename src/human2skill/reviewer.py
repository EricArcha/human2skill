from human2skill.constants import PRIVATE_MARKERS
from human2skill.schemas import validate_document

REVIEW_PASS_THRESHOLDS = {
    "evidence_consistency": 4,
    "confidence_calibration": 5,
    "honest_boundary": 5,
    "privacy_safety": 5,
    "expression_similarity": 4,
    "thinking_utility": 4,
    "profile_fit": 4,
}


def _score_evidence_consistency(content: str) -> int:
    """Score evidence consistency (1-5). Higher = more consistent structure."""
    lines = content.split("\n")
    section_count = sum(1 for l in lines if l.startswith("## "))

    if section_count >= 3:
        return 5
    elif section_count >= 2:
        return 4
    elif section_count >= 1:
        return 3
    else:
        return 2


def _score_confidence_calibration(overconfident_claims: list) -> int:
    """Score confidence calibration (1-5). Higher = better calibrated."""
    if not overconfident_claims:
        return 5
    count = len(overconfident_claims)
    if count <= 1:
        return 3
    elif count <= 3:
        return 2
    else:
        return 1


def _score_honest_boundary(content: str) -> int:
    """Score honest boundary quality (1-5). Higher = better defined boundaries."""
    lines = content.split("\n")
    in_boundary = False
    boundary_items = []

    for line in lines:
        if "诚实边界" in line and (line.startswith("##") or line.startswith("#")):
            in_boundary = True
            continue
        if in_boundary:
            if line.startswith("##"):
                break
            stripped = line.strip()
            if stripped.startswith("-") and len(stripped) > 5:
                content_text = stripped[1:].strip()
                if content_text and content_text not in ("不确定", "不确定。", "未知", "未知。"):
                    boundary_items.append(content_text)

    if not boundary_items:
        if "诚实边界" in content:
            return 2
        return 1

    if len(boundary_items) >= 3:
        return 5
    elif len(boundary_items) >= 2:
        return 4
    else:
        return 3


def _score_privacy_safety(content: str) -> int:
    """Score privacy safety (1-5). Higher = better privacy controls."""
    score = 1
    if "不代表本人观点" in content:
        score += 2
    if not any(marker in content for marker in PRIVATE_MARKERS):
        score += 2
    return min(score, 5)


def _score_expression_similarity(content: str) -> int:
    """Score expression similarity presence (1-5)."""
    if "表达 DNA" in content or "表达DNA" in content or "表达风格" in content:
        lines = content.split("\n")
        in_section = False
        count = 0
        for line in lines:
            if ("表达" in line and ("DNA" in line or "风格" in line)) and (
                line.startswith("##") or line.startswith("#")
            ):
                in_section = True
                continue
            if in_section:
                if line.startswith("##"):
                    break
                if line.strip().startswith("-") and len(line.strip()) > 3:
                    text = line.strip()[1:].strip()
                    if text and "证据不足" in text:
                        continue
                    count += 1
        if count >= 2:
            return 5
        elif count >= 1:
            return 4
        else:
            return 3
    return 2


def _score_thinking_utility(content: str) -> int:
    """Score thinking utility (1-5). Higher = more useful thinking models."""
    if "核心思维模型" in content or "思维模型" in content:
        lines = content.split("\n")
        in_section = False
        count = 0
        for line in lines:
            if "思维模型" in line and (line.startswith("##") or line.startswith("#")):
                in_section = True
                continue
            if in_section:
                if line.startswith("##"):
                    break
                if line.strip().startswith("-") and len(line.strip()) > 3:
                    text = line.strip()[1:].strip()
                    if text and "证据不足" in text:
                        continue
                    count += 1
        if count >= 2:
            return 5
        elif count >= 1:
            return 4
        else:
            return 3
    return 2


def _score_profile_fit(content: str) -> int:
    """Score profile fit (1-5). Higher = better matches expected profile structure."""
    key_sections = [
        "核心思维模型" in content or "思维模型" in content,
        "表达 DNA" in content or "表达DNA" in content or "表达风格" in content,
        "诚实边界" in content,
    ]
    count = sum(key_sections)
    if count == 3:
        return 5
    elif count == 2:
        return 4
    elif count == 1:
        return 2
    else:
        return 1


def _derive_required_changes(hard_failures: list[str], scores: dict[str, int]) -> list[str]:
    """Derive required changes from failures and low scores."""
    changes = []

    failure_to_change = {
        "claims_to_be_person": (
            "Remove or rephrase claims that present the skill as the person themselves."
        ),
        "missing_honest_boundaries": (
            "Add an honest boundaries (诚实边界) section listing known limitations."
        ),
        "contains_private_raw_material": (
            "Remove raw private material such as chat logs or personal identifiers."
        ),
        "missing_disclaimer": (
            "Add disclaimer stating the skill does not represent the person's own views."
        ),
        "unsupported_high_confidence_claims": (
            "Lower confidence on claims that lack supporting evidence."
        ),
        "unresolved_conflicts": (
            "Resolve or document conflicting evidence before publishing."
        ),
        "first_person_missing_disclaimer": (
            "First-person variant requires an explicit disclaimer."
        ),
    }

    for failure in hard_failures:
        if failure in failure_to_change:
            changes.append(failure_to_change[failure])

    score_to_change = {
        "honest_boundary": "Strengthen honest boundary statements with domain-specific limitations.",
        "privacy_safety": "Add privacy safeguards and disclaimers.",
        "evidence_consistency": "Improve evidence consistency across claims.",
        "confidence_calibration": "Calibrate confidence levels to match available evidence.",
        "expression_similarity": "Add or expand expression DNA details.",
        "thinking_utility": "Add or expand thinking models and decision frameworks.",
        "profile_fit": "Ensure all required profile sections are present and substantive.",
    }

    for dimension, score in scores.items():
        threshold = REVIEW_PASS_THRESHOLDS.get(dimension)
        if threshold is not None and score < threshold and dimension in score_to_change:
            changes.append(score_to_change[dimension])

    return changes


def _derive_notes(scores: dict[str, int], hard_failures: list[str]) -> list[str]:
    """Derive review notes from scores and failures."""
    notes = []

    if hard_failures:
        notes.append(f"Found {len(hard_failures)} hard failure(s): {', '.join(hard_failures)}")
    else:
        notes.append("No hard failures detected.")

    strong = [dim for dim, score in scores.items() if score == 5]
    if strong:
        notes.append(f"Strong dimensions: {', '.join(strong)}")

    weak = [
        dim
        for dim, score in scores.items()
        if score < REVIEW_PASS_THRESHOLDS.get(dim, 1)
    ]
    if weak:
        notes.append(f"Needs improvement: {', '.join(weak)}")

    return notes


def structured_review(
    person_slug: str,
    variant: str,
    content: str,
    overconfident_claims: list,
    unresolved_conflicts: list,
    generated_at: str,
) -> dict:
    """Perform a structured review of a generated skill.

    Returns a review report dict conforming to review_report.schema.json.
    Passes only when there are no hard failures AND all REVIEW_PASS_THRESHOLDS
    are met.
    """
    scores = {
        "evidence_consistency": _score_evidence_consistency(content),
        "confidence_calibration": _score_confidence_calibration(overconfident_claims),
        "honest_boundary": _score_honest_boundary(content),
        "privacy_safety": _score_privacy_safety(content),
        "expression_similarity": _score_expression_similarity(content),
        "thinking_utility": _score_thinking_utility(content),
        "profile_fit": _score_profile_fit(content),
    }

    hard_failures: list[str] = []
    if "我就是" in content:
        hard_failures.append("claims_to_be_person")
    if "诚实边界" not in content:
        hard_failures.append("missing_honest_boundaries")
    if any(marker in content for marker in PRIVATE_MARKERS):
        hard_failures.append("contains_private_raw_material")
    if "不代表本人观点" not in content:
        hard_failures.append("missing_disclaimer")
    if overconfident_claims:
        hard_failures.append("unsupported_high_confidence_claims")
    if unresolved_conflicts:
        hard_failures.append("unresolved_conflicts")
    if variant == "first_person" and "不代表本人观点" not in content:
        hard_failures.append("first_person_missing_disclaimer")

    threshold_failures = [
        dimension
        for dimension, threshold in REVIEW_PASS_THRESHOLDS.items()
        if scores[dimension] < threshold
    ]

    passed = not hard_failures and not threshold_failures

    required_changes = _derive_required_changes(hard_failures, scores)
    notes = _derive_notes(scores, hard_failures)

    report = {
        "schema_version": "1",
        "person_slug": person_slug,
        "variant": variant,
        "generated_at": generated_at,
        "passed": passed,
        "hard_failures": hard_failures,
        "scores": scores,
        "required_changes": required_changes,
        "notes": notes,
    }

    validate_document("review_report.schema.json", report)
    return report
