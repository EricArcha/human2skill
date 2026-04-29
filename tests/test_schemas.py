import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator


def load_schema(name):
    return json.loads(Path("schemas", name).read_text(encoding="utf-8"))


def test_person_meta_schema_accepts_minimal_valid_document():
    schema = load_schema("person.meta.schema.json")
    document = {
        "schema_version": "1",
        "slug": "zhang-san",
        "display_name": "张三",
        "profile_type": "colleague",
        "relationship_to_user": "coworker",
        "use_case": "work perspective advisor",
        "voice_mode": "advisor",
        "consent_status": {
            "person_consented": False,
            "distribution_allowed": False,
            "notes": "local personal use"
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
            "created_at": "2026-04-29T00:00:00+08:00",
            "updated_at": "2026-04-29T00:00:00+08:00"
        }
    }

    Draft202012Validator(schema).validate(document)


def test_evidence_pack_schema_accepts_minimal_valid_document():
    schema = load_schema("evidence_pack.schema.json")
    document = {
        "schema_version": "1",
        "person_slug": "zhang-san",
        "evidence": [
            {
                "evidence_id": "ev-0001",
                "source_type": "observer_report",
                "source_summary": "User reports that Zhang San asks for impact before discussing plans.",
                "retention": "summary_only",
                "confidence": "medium",
                "supports": ["claim-impact-first"],
                "conflicts_with": [],
                "notes": "observer report"
            }
        ],
        "claims": [
            {
                "claim_id": "claim-impact-first",
                "claim": "He asks for impact before discussing plans.",
                "claim_type": "decision_heuristic",
                "profile_scope": "colleague",
                "confidence": "medium",
                "evidence_ids": ["ev-0001"],
                "status": "active"
            }
        ]
    }

    Draft202012Validator(schema).validate(document)


@pytest.mark.parametrize("field", ["schema_version", "slug", "display_name", "profile_type", "voice_mode", "privacy_policy", "export_policy", "lifecycle"])
def test_person_meta_rejects_missing_required(field):
    schema = load_schema("person.meta.schema.json")
    document = {
        "schema_version": "1",
        "slug": "zhang-san",
        "display_name": "张三",
        "profile_type": "colleague",
        "relationship_to_user": "coworker",
        "use_case": "work perspective advisor",
        "voice_mode": "advisor",
        "consent_status": {
            "person_consented": False,
            "distribution_allowed": False,
            "notes": "local personal use"
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
            "created_at": "2026-04-29T00:00:00+08:00",
            "updated_at": "2026-04-29T00:00:00+08:00"
        }
    }
    del document[field]
    with pytest.raises(Exception):
        Draft202012Validator(schema).validate(document)


@pytest.mark.parametrize("field,value", [
    ("profile_type", "stranger"),
    ("slug", "-starts-with-hyphen"),
])
def test_person_meta_rejects_invalid_value(field, value):
    schema = load_schema("person.meta.schema.json")
    document = {
        "schema_version": "1",
        "slug": "zhang-san",
        "display_name": "张三",
        "profile_type": "colleague",
        "relationship_to_user": "coworker",
        "use_case": "work perspective advisor",
        "voice_mode": "advisor",
        "consent_status": {
            "person_consented": False,
            "distribution_allowed": False,
            "notes": "local personal use"
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
            "created_at": "2026-04-29T00:00:00+08:00",
            "updated_at": "2026-04-29T00:00:00+08:00"
        }
    }
    document[field] = value
    with pytest.raises(Exception):
        Draft202012Validator(schema).validate(document)


@pytest.mark.parametrize("field", ["schema_version", "person_slug", "evidence", "claims"])
def test_evidence_pack_rejects_missing_required(field):
    schema = load_schema("evidence_pack.schema.json")
    document = {
        "schema_version": "1",
        "person_slug": "zhang-san",
        "evidence": [],
        "claims": []
    }
    del document[field]
    with pytest.raises(Exception):
        Draft202012Validator(schema).validate(document)


def test_evidence_pack_rejects_invalid_evidence_id():
    schema = load_schema("evidence_pack.schema.json")
    document = {
        "schema_version": "1",
        "person_slug": "zhang-san",
        "evidence": [
            {
                "evidence_id": "bad-id",
                "source_type": "observer_report",
                "source_summary": "summary",
                "retention": "summary_only",
                "confidence": "medium",
                "supports": [],
                "conflicts_with": [],
                "notes": ""
            }
        ],
        "claims": []
    }
    with pytest.raises(Exception):
        Draft202012Validator(schema).validate(document)
