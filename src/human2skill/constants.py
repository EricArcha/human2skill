PROFILE_TYPES = ("colleague", "relationship", "mentor", "self")
VOICE_MODES = ("advisor", "first_person", "both")
RETENTION_POLICIES = ("no_raw_retention", "summary_only", "local_private_raw")
HOSTS = ("codex", "claude-code", "openclaw", "hermes")

SOURCE_KINDS = (
    "manual_text",
    "markdown",
    "txt",
    "pdf_text",
    "chat_excerpt",
    "meeting_note",
    "email_summary",
    "interview_answer",
    "screenshot_text",
)

CLAIM_TYPES = (
    "mental_model",
    "decision_heuristic",
    "expression_dna",
    "profile_specific",
    "pressure_response",
    "value_order",
    "anti_pattern",
    "boundary",
)

CONFLICT_TYPES = (
    "temporal",
    "contextual",
    "observer_conflict",
    "inherent_tension",
)

REVIEW_SCORE_KEYS = (
    "evidence_consistency",
    "confidence_calibration",
    "honest_boundary",
    "privacy_safety",
    "expression_similarity",
    "thinking_utility",
    "profile_fit",
)
