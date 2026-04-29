import json
from pathlib import Path

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
        "consent_status": {
            "person_consented": False,
            "distribution_allowed": False,
            "notes": "local personal use"
        },
        "privacy_policy": {
            "raw_retention": "summary_only",
            "public_skill_allows_private_quotes": False
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
