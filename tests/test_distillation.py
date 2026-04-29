import pytest

from human2skill.distillation import DistillationError, distillation_to_sections, format_distilled_item, validate_distillation


def valid_distillation():
    return {
        "schema_version": "1",
        "person_slug": "li-ming",
        "generated_at": "2026-04-29T00:00:00+00:00",
        "source_evidence_pack_version": "v1",
        "mental_models": [{
            "title": "Impact first",
            "content": "先问 impact，再讨论方案。",
            "claim_ids": ["claim-impact-first"],
            "confidence": "medium",
            "evidence_summary": "会议摘要支持。",
            "limits": ["只覆盖工作评审。"]
        }],
        "decision_heuristics": [],
        "expression_dna": [],
        "profile_specific": [],
        "pressure_response": [],
        "value_order": [],
        "anti_patterns": [],
        "honest_boundaries": [{
            "title": "关系场景不足",
            "content": "关系场景证据不足。",
            "claim_ids": [],
            "confidence": "low",
            "evidence_summary": "无直接证据。",
            "limits": ["不推断亲密关系。"]
        }],
        "scenario_tests": []
    }


def test_validate_distillation_accepts_claim_links():
    validate_distillation(valid_distillation(), available_claim_ids={"claim-impact-first"})


def test_validate_distillation_rejects_missing_claim_link():
    payload = valid_distillation()
    payload["mental_models"][0]["claim_ids"] = ["claim-missing"]

    with pytest.raises(DistillationError) as error:
        validate_distillation(payload, available_claim_ids={"claim-impact-first"})

    assert "claim-missing" in str(error.value)


def test_distillation_to_sections_maps_all_skill_sections():
    sections = distillation_to_sections(valid_distillation())

    assert "mental_models" in sections
    assert "honest_boundaries" in sections
    assert "Impact first" in sections["mental_models"][0]


def test_validate_distillation_rejects_missing_claim_ids_in_non_boundary_section():
    payload = valid_distillation()
    payload["mental_models"][0]["claim_ids"] = []

    with pytest.raises(DistillationError) as error:
        validate_distillation(payload, available_claim_ids={"claim-impact-first"})

    assert "mental_models[0]" in str(error.value)


def test_validate_distillation_rejects_missing_claim_ids_key():
    payload = valid_distillation()
    del payload["mental_models"][0]["claim_ids"]

    with pytest.raises(DistillationError) as error:
        validate_distillation(payload, available_claim_ids={"claim-impact-first"})

    assert "mental_models[0]" in str(error.value)


def test_validate_distillation_allows_empty_claim_ids_in_boundaries():
    payload = valid_distillation()
    validate_distillation(payload, available_claim_ids={"claim-impact-first"})


def test_validate_distillation_validates_boundary_claim_ids():
    payload = valid_distillation()
    payload["honest_boundaries"][0]["claim_ids"] = ["claim-nonexistent"]

    with pytest.raises(DistillationError) as error:
        validate_distillation(payload, available_claim_ids={"claim-impact-first"})

    assert "claim-nonexistent" in str(error.value)


def test_validate_distillation_rejects_invalid_schema():
    payload = {"not": "valid"}

    with pytest.raises(DistillationError):
        validate_distillation(payload, available_claim_ids=set())


def test_validate_distillation_rejects_wrong_person_slug():
    payload = valid_distillation()
    payload["person_slug"] = "other-person"

    with pytest.raises(DistillationError) as error:
        validate_distillation(payload, available_claim_ids={"claim-impact-first"}, person_slug="li-ming")

    assert "person_slug mismatch" in str(error.value)


def test_format_distilled_item_formats_basic_item():
    item = {
        "title": "Impact first",
        "content": "先问 impact，再讨论方案。",
        "confidence": "medium",
        "evidence_summary": "会议摘要支持。",
    }

    result = format_distilled_item(item)
    assert "Impact first: 先问 impact" in result
    assert "(medium; 会议摘要支持。)" in result


def test_format_distilled_item_includes_limits():
    item = {
        "title": "Impact first",
        "content": "先问 impact，再讨论方案。",
        "confidence": "medium",
        "evidence_summary": "会议摘要支持。",
        "limits": ["只覆盖工作评审。", "不适用于社交场景。"],
    }

    result = format_distilled_item(item)
    assert "只覆盖工作评审。" in result
    assert "不适用于社交场景。" in result


def test_format_distilled_item_handles_missing_optional_fields():
    item = {
        "title": "Simple model",
        "content": "简洁描述。",
    }

    result = format_distilled_item(item)
    assert result == "Simple model: 简洁描述。"


def test_format_distilled_item_formats_scenario_test():
    item = {
        "title": "评审场景",
        "content": "同事提交设计文档评审。",
        "expected_behavior": "先问 impact，再讨论方案。",
    }

    result = format_distilled_item(item)
    assert "评审场景" in result
    assert "期望行为: 先问 impact" in result


def test_distillation_to_sections_handles_empty_payload():
    payload = valid_distillation()
    for key in payload:
        if isinstance(payload[key], list):
            payload[key] = []

    sections = distillation_to_sections(payload)

    assert sections["mental_models"] == []
    assert sections["decision_heuristics"] == []
    assert sections["scenario_tests"] == []
