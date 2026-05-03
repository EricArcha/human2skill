from human2skill.schemas import validate_document
import pytest


def test_person_meta_accepts_voice_and_export_policy():
    validate_document("person.meta.schema.json", {
        "schema_version": "1",
        "slug": "li-ming",
        "display_name": "李明",
        "profile_type": "colleague",
        "relationship_to_user": "coworker",
        "use_case": "work review perspective",
        "voice_mode": "both",
        "consent_status": {
            "person_consented": False,
            "distribution_allowed": False,
            "notes": "local private use"
        },
        "privacy_policy": {
            "raw_retention": "summary_only",
            "public_skill_allows_private_quotes": False
        },
        "export_policy": {
            "default_visibility": "private",
            "shareable_variants": ["advisor"],
            "requires_privacy_review": True
        },
        "lifecycle": {
            "version": "v1",
            "created_at": "2026-04-29T00:00:00+00:00",
            "updated_at": "2026-04-29T00:00:00+00:00"
        }
    })


def test_person_meta_accepts_quotes_for_any_voice_mode():
    # Both advisor and first_person can allow private quotes
    for voice_mode in ("advisor", "first_person", "both"):
        validate_document("person.meta.schema.json", {
            "schema_version": "1",
            "slug": "li-ming",
            "display_name": "李明",
            "profile_type": "colleague",
            "relationship_to_user": "coworker",
            "use_case": "work review",
            "voice_mode": voice_mode,
            "consent_status": {
                "person_consented": False,
                "distribution_allowed": False,
            },
            "privacy_policy": {
                "raw_retention": "summary_only",
                "public_skill_allows_private_quotes": True
            },
            "export_policy": {
                "default_visibility": "private",
                "shareable_variants": ["advisor"],
                "requires_privacy_review": True
            },
            "lifecycle": {
                "version": "v1",
                "created_at": "2026-04-29T00:00:00+00:00",
                "updated_at": "2026-04-29T00:00:00+00:00"
            }
        })


def test_source_index_accepts_summary_only_source():
    validate_document("source_index.schema.json", {
        "schema_version": "1",
        "person_slug": "li-ming",
        "sources": [{
            "source_id": "src-0001",
            "source_kind": "manual_text",
            "title": "手动摘要",
            "provided_by": "user",
            "retention": "summary_only",
            "contains_private_data": True,
            "allowed_in_public_skill": False,
            "summary": "用户提供了工作评审片段摘要。",
            "created_at": "2026-04-29T00:00:00+00:00"
        }]
    })


def test_distillation_requires_claim_links_for_model():
    validate_document("distillation.schema.json", {
        "schema_version": "1",
        "person_slug": "li-ming",
        "generated_at": "2026-04-29T00:00:00+00:00",
        "source_evidence_pack_version": "v1",
        "mental_models": [{
            "title": "Impact first",
            "content": "先问 impact，再讨论方案。",
            "claim_ids": ["claim-impact-first"],
            "confidence": "medium",
            "evidence_summary": "由会议摘要支持。",
            "limits": ["只覆盖工作评审场景。"]
        }],
        "decision_heuristics": [],
        "expression_dna": [],
        "profile_specific": [],
        "pressure_response": [],
        "value_order": [],
        "anti_patterns": [],
        "honest_boundaries": [],
        "scenario_tests": []
    })


def test_review_report_accepts_structured_scores():
    validate_document("review_report.schema.json", {
        "schema_version": "1",
        "person_slug": "li-ming",
        "variant": "advisor",
        "generated_at": "2026-04-29T00:00:00+00:00",
        "passed": True,
        "hard_failures": [],
        "scores": {
            "evidence_consistency": 4,
            "confidence_calibration": 4,
            "honest_boundary": 5,
            "privacy_safety": 5,
            "expression_similarity": 4,
            "thinking_utility": 4,
            "profile_fit": 4
        },
        "required_changes": [],
        "notes": []
    })


def test_export_manifest_accepts_codex_manifest():
    validate_document("export_manifest.schema.json", {
        "schema_version": "1",
        "host": "codex",
        "person_slug": "li-ming",
        "variant": "advisor",
        "created_at": "2026-04-29T00:00:00+00:00",
        "files": ["SKILL.md"],
        "install_hint": "~/.codex/skills/li-ming",
        "review_passed": True,
        "privacy_check_passed": True
    })


def test_source_index_rejects_invalid_source_id():
    with pytest.raises(Exception):
        validate_document("source_index.schema.json", {
            "schema_version": "1",
            "person_slug": "li-ming",
            "sources": [{
                "source_id": "bad-id",
                "source_kind": "manual_text",
                "title": "test",
                "provided_by": "user",
                "retention": "summary_only",
                "contains_private_data": True,
                "allowed_in_public_skill": False,
                "summary": "test",
                "created_at": "2026-04-29T00:00:00+00:00"
            }]
        })


def test_source_index_rejects_invalid_retention():
    with pytest.raises(Exception):
        validate_document("source_index.schema.json", {
            "schema_version": "1",
            "person_slug": "li-ming",
            "sources": [{
                "source_id": "src-0001",
                "source_kind": "manual_text",
                "title": "test",
                "provided_by": "user",
                "retention": "full_raw",
                "contains_private_data": True,
                "allowed_in_public_skill": False,
                "summary": "test",
                "created_at": "2026-04-29T00:00:00+00:00"
            }]
        })


def test_distillation_rejects_missing_section():
    with pytest.raises(Exception):
        validate_document("distillation.schema.json", {
            "schema_version": "1",
            "person_slug": "li-ming",
            "generated_at": "2026-04-29T00:00:00+00:00",
            "source_evidence_pack_version": "v1"
        })


def test_review_report_rejects_out_of_range_score():
    with pytest.raises(Exception):
        validate_document("review_report.schema.json", {
            "schema_version": "1",
            "person_slug": "li-ming",
            "variant": "advisor",
            "generated_at": "2026-04-29T00:00:00+00:00",
            "passed": True,
            "hard_failures": [],
            "scores": {
                "evidence_consistency": 0,
                "confidence_calibration": 4,
                "honest_boundary": 5,
                "privacy_safety": 5,
                "expression_similarity": 4,
                "thinking_utility": 4,
                "profile_fit": 4
            },
            "required_changes": [],
            "notes": []
        })


def test_export_manifest_rejects_unknown_host():
    with pytest.raises(Exception):
        validate_document("export_manifest.schema.json", {
            "schema_version": "1",
            "host": "unknown",
            "person_slug": "li-ming",
            "variant": "advisor",
            "created_at": "2026-04-29T00:00:00+00:00",
            "files": ["SKILL.md"],
            "install_hint": "~/.codex/skills/li-ming",
            "review_passed": True,
            "privacy_check_passed": True
        })
