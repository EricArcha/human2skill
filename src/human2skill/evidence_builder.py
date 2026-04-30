from __future__ import annotations

import hashlib
import re

from human2skill.schemas import validate_document


def empty_evidence_pack(person_slug: str) -> dict:
    """Create a new empty evidence pack for a person."""
    return {
        "schema_version": "1",
        "person_slug": person_slug,
        "evidence": [],
        "claims": [],
        "conflicts": [],
    }


def next_evidence_id(pack: dict) -> str:
    """Generate the next sequential evidence ID in ev-0001 format."""
    n = len(pack["evidence"]) + 1
    return f"ev-{n:04d}"


def next_conflict_id(pack: dict) -> str:
    """Generate the next sequential conflict ID in cf-0001 format."""
    n = len(pack["conflicts"]) + 1
    return f"cf-{n:04d}"


def claim_id_from_text(text: str) -> str:
    """Generate a claim ID by slugifying the claim text.

    Strips non-alphanumeric characters, lowercases, and replaces whitespace
    with hyphens. Falls back to an 8-char hash if no alphanumeric chars remain
    (e.g. purely Chinese text).
    """
    slug = re.sub(r"[^a-z0-9\s]", "", text.lower())
    slug = re.sub(r"\s+", "-", slug.strip())
    slug = slug.strip("-")
    slug = re.sub(r"-+", "-", slug)

    if not slug:
        slug = hashlib.md5(text.encode()).hexdigest()[:8]

    return f"claim-{slug}"


def add_evidence(
    pack: dict,
    source_type: str,
    source_summary: str,
    retention: str,
    confidence: str,
    supports: list[str],
) -> dict:
    """Add an evidence item to the pack and validate."""
    evidence_id = next_evidence_id(pack)
    evidence = {
        "evidence_id": evidence_id,
        "source_type": source_type,
        "source_summary": source_summary,
        "retention": retention,
        "confidence": confidence,
        "supports": supports,
    }
    pack["evidence"].append(evidence)
    validate_document("evidence_pack.schema.json", pack)
    return evidence


def add_claim(
    pack: dict,
    claim: str,
    claim_type: str,
    confidence: str,
    evidence_ids: list[str],
    profile_scope: str | None = None,
) -> dict:
    """Add a claim to the pack, handling duplicate IDs, and validate."""
    base_id = claim_id_from_text(claim)

    existing_ids = {c["claim_id"] for c in pack["claims"]}
    claim_id = base_id
    counter = 2
    while claim_id in existing_ids:
        claim_id = f"{base_id}-{counter}"
        counter += 1

    claim_obj: dict = {
        "claim_id": claim_id,
        "claim": claim,
        "claim_type": claim_type,
        "confidence": confidence,
        "evidence_ids": evidence_ids,
        "status": "active",
    }
    if profile_scope is not None:
        claim_obj["profile_scope"] = profile_scope

    pack["claims"].append(claim_obj)
    validate_document("evidence_pack.schema.json", pack)
    return claim_obj


def add_conflict(
    pack: dict,
    claim_ids: list[str],
    evidence_ids: list[str],
    conflict_type: str,
    resolution: str,
    note: str = "",
) -> dict:
    """Add a conflict record to the pack and validate."""
    conflict_id = next_conflict_id(pack)
    conflict = {
        "conflict_id": conflict_id,
        "claim_ids": claim_ids,
        "evidence_ids": evidence_ids,
        "conflict_type": conflict_type,
        "resolution": resolution,
        "note": note,
    }
    pack["conflicts"].append(conflict)
    validate_document("evidence_pack.schema.json", pack)
    return conflict
