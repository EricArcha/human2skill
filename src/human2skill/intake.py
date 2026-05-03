from __future__ import annotations

from pathlib import Path

from human2skill.constants import PROFILE_TYPES, VOICE_MODES
from human2skill.schemas import validate_document
from human2skill.storage import initialize_person_dir, write_json
from human2skill.timeutils import utc_now_iso


def normalize_profile(profile_type: str | None) -> str:
    if profile_type in PROFILE_TYPES:
        return profile_type
    return "relationship"


def normalize_voice_mode(voice_mode: str | None, profile_type: str | None = None) -> str:
    if voice_mode in VOICE_MODES:
        return voice_mode
    if profile_type in ("self", "relationship"):
        return "first_person"
    return "advisor"


def build_person_meta(
    *,
    slug: str,
    display_name: str,
    profile_type: str | None,
    relationship_to_user: str,
    use_case: str,
    voice_mode: str | None = None,
    now: str | None = None,
) -> dict:
    timestamp = now or utc_now_iso()
    resolved_voice_mode = normalize_voice_mode(voice_mode, profile_type)
    meta = {
        "schema_version": "1",
        "slug": slug,
        "display_name": display_name,
        "profile_type": normalize_profile(profile_type),
        "relationship_to_user": relationship_to_user,
        "use_case": use_case,
        "voice_mode": resolved_voice_mode,
        "consent_status": {
            "person_consented": False,
            "distribution_allowed": False,
            "notes": "local private use unless explicitly changed",
        },
        "privacy_policy": {
            "raw_retention": "summary_only",
            "public_skill_allows_private_quotes": resolved_voice_mode == "first_person",
        },
        "export_policy": {
            "default_visibility": "private",
            "shareable_variants": ["advisor"],
            "requires_privacy_review": True,
        },
        "lifecycle": {
            "version": "v1",
            "created_at": timestamp,
            "updated_at": timestamp,
        },
    }
    validate_document("person.meta.schema.json", meta)
    return meta


def create_person(
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
    base = initialize_person_dir(root, slug)
    meta = build_person_meta(
        slug=slug,
        display_name=display_name,
        profile_type=profile_type,
        relationship_to_user=relationship_to_user,
        use_case=use_case,
        voice_mode=voice_mode,
        now=now,
    )
    write_json(base / "person.meta.json", meta)
    return base
