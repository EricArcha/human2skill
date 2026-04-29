from __future__ import annotations

from human2skill.schemas import SchemaValidationError, validate_document


class DistillationError(ValueError):
    """Raised when a distillation payload fails validation rules."""


# Sections whose items MUST have at least one claim_id.
_CLAIM_REQUIRED_SECTIONS = (
    "mental_models",
    "decision_heuristics",
    "expression_dna",
    "profile_specific",
    "pressure_response",
    "value_order",
    "anti_patterns",
    "scenario_tests",
)

# All array sections in distillation output, in canonical order.
_OUTPUT_SECTIONS = _CLAIM_REQUIRED_SECTIONS + ("honest_boundaries",)


def validate_distillation(payload: dict, available_claim_ids: set[str]) -> None:
    """Validate a distillation payload against the schema and claim-id integrity rules.

    Rules:
    - Schema must pass ``distillation.schema.json``.
    - Every item in every section except ``honest_boundaries`` must have at least
      one claim ID.
    - Every claim ID must exist in *available_claim_ids*.
    - ``honest_boundaries`` items may have zero claim IDs, but any present must
      also be valid.
    """
    # Schema validation first.
    try:
        validate_document("distillation.schema.json", payload)
    except SchemaValidationError as exc:
        raise DistillationError(str(exc)) from exc

    # Claim-id integrity for sections that require claim IDs.
    for section in _CLAIM_REQUIRED_SECTIONS:
        for i, item in enumerate(payload.get(section, [])):
            claim_ids = item.get("claim_ids", [])
            if len(claim_ids) < 1:
                raise DistillationError(
                    f"{section}[{i}] requires at least one claim_id, got {claim_ids!r}"
                )
            for cid in claim_ids:
                if cid not in available_claim_ids:
                    raise DistillationError(f"{cid}")

    # honest_boundaries: may have no claim IDs, but any present must be valid.
    for i, item in enumerate(payload.get("honest_boundaries", [])):
        for cid in item.get("claim_ids", []):
            if cid not in available_claim_ids:
                raise DistillationError(f"{cid}")


def format_distilled_item(item: dict) -> str:
    """Format a single distilled item as a human-readable string.

    Returns a string like::

        Title: content (confidence; evidence summary)
          - 限制: limit1

    ``scenario_tests`` items additionally include::

        期望行为: expected_behavior
    """
    result = f"{item['title']}: {item['content']}"

    confidence = item.get("confidence")
    evidence_summary = item.get("evidence_summary")
    if confidence and evidence_summary:
        result += f" ({confidence}; {evidence_summary})"
    elif confidence:
        result += f" ({confidence})"
    elif evidence_summary:
        result += f" ({evidence_summary})"

    for limit in item.get("limits", []):
        result += f"\n  - 限制: {limit}"

    if "expected_behavior" in item:
        result += f"\n  期望行为: {item['expected_behavior']}"

    return result


def distillation_to_sections(payload: dict) -> dict[str, list[str]]:
    """Map a distillation payload into a dictionary of formatted section strings.

    Each section key maps to a list of ``format_distilled_item`` results.
    """
    return {key: [format_distilled_item(item) for item in payload.get(key, [])] for key in _OUTPUT_SECTIONS}
