import json
import os
import subprocess
import sys
from pathlib import Path


def run_cli(*args: str, cwd: Path):
    env = os.environ.copy()
    src_path = str(Path(__file__).resolve().parent.parent / "src")
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = src_path if not existing else f"{src_path}:{existing}"
    return subprocess.run(
        [sys.executable, "-m", "human2skill.cli", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=True,
        env=env,
    )


def test_cli_create_existing_slug_fails_without_force(tmp_path: Path):
    # Create once
    run_cli(
        "create", "--root", str(tmp_path), "--slug", "test-person",
        "--name", "Test", "--profile", "colleague",
        "--relationship", "coworker", "--use-case", "work",
        cwd=tmp_path,
    )
    # Create same slug without --force
    result = subprocess.run(
        [sys.executable, "-m", "human2skill.cli", "create",
         "--root", str(tmp_path), "--slug", "test-person",
         "--name", "Test", "--profile", "colleague",
         "--relationship", "coworker", "--use-case", "work"],
        cwd=tmp_path, text=True, capture_output=True,
    )
    assert result.returncode != 0
    assert "already exists" in result.stderr.lower()


def test_cli_create_existing_slug_with_force_overwrites(tmp_path: Path):
    run_cli(
        "create", "--root", str(tmp_path), "--slug", "test-person",
        "--name", "Before", "--profile", "colleague",
        "--relationship", "coworker", "--use-case", "work",
        cwd=tmp_path,
    )
    result = run_cli(
        "create", "--root", str(tmp_path), "--slug", "test-person",
        "--name", "After", "--profile", "colleague",
        "--relationship", "coworker", "--use-case", "work",
        "--force",
        cwd=tmp_path,
    )
    assert "created" in result.stdout.lower()
    meta = json.loads(
        (tmp_path / "outputs/test-person/person.meta.json").read_text(encoding="utf-8")
    )
    assert meta["display_name"] == "After"


def test_cli_status_shows_project_info(tmp_path: Path):
    run_cli(
        "create", "--root", str(tmp_path), "--slug", "test-person",
        "--name", "Test", "--profile", "colleague",
        "--relationship", "coworker", "--use-case", "work",
        cwd=tmp_path,
    )
    result = run_cli(
        "status", "--root", str(tmp_path), "--slug", "test-person",
        cwd=tmp_path,
    )
    assert "version:" in result.stdout.lower()
    assert "v1" in result.stdout


def test_cli_status_nonexistent(tmp_path: Path):
    result = subprocess.run(
        [sys.executable, "-m", "human2skill.cli", "status",
         "--root", str(tmp_path), "--slug", "nobody"],
        cwd=tmp_path, text=True, capture_output=True,
    )
    assert result.returncode == 0
    assert "does not exist" in result.stdout


def test_cli_create_and_ingest(tmp_path: Path):
    result = run_cli(
        "create",
        "--root",
        str(tmp_path),
        "--slug",
        "li-ming",
        "--name",
        "李明",
        "--profile",
        "colleague",
        "--relationship",
        "coworker",
        "--use-case",
        "work review",
        cwd=tmp_path,
    )

    assert "created" in result.stdout.lower()

    note = tmp_path / "note.txt"
    note.write_text("李明先问 impact。", encoding="utf-8")
    ingest = run_cli(
        "ingest",
        "--root", str(tmp_path),
        "--slug", "li-ming",
        "--file", str(note),
        cwd=tmp_path,
    )

    assert "src-0001" in ingest.stdout
    index = json.loads(
        (tmp_path / "outputs/li-ming/private_evidence/source_index.json").read_text(encoding="utf-8")
    )
    assert index["sources"][0]["source_id"] == "src-0001"


def test_cli_question_returns_next_dimension(tmp_path: Path):
    # First create a person
    run_cli(
        "create",
        "--root", str(tmp_path),
        "--slug", "li-ming",
        "--name", "李明",
        "--profile", "colleague",
        "--relationship", "coworker",
        "--use-case", "work review",
        cwd=tmp_path,
    )

    # Write an initial coverage file (all missing)
    coverage_path = tmp_path / "outputs/li-ming/private_evidence/interviews/coverage.json"
    coverage_path.parent.mkdir(parents=True, exist_ok=True)
    coverage_path.write_text(json.dumps({
        "identity_context": "missing",
        "mental_models": "missing",
        "expression_dna": "missing",
        "decision_heuristics": "missing",
        "pressure_response": "missing",
        "profile_specific": "missing",
        "honest_boundaries": "missing",
        "evaluation_scenarios": "missing",
        "value_order": "missing",
        "anti_patterns": "missing",
    }, ensure_ascii=False), encoding="utf-8")

    result = run_cli(
        "question",
        "--root", str(tmp_path),
        "--slug", "li-ming",
        "--profile", "colleague",
        "--perspective", "observer_answer",
        "--turn", "1",
        cwd=tmp_path,
    )

    # Should return a non-empty question string
    assert len(result.stdout.strip()) > 0
    assert "?" in result.stdout or "？" in result.stdout or "信息覆盖已经足够" in result.stdout


def test_cli_question_completes_when_covered(tmp_path: Path):
    run_cli(
        "create",
        "--root", str(tmp_path),
        "--slug", "li-ming",
        "--name", "李明",
        "--profile", "colleague",
        "--relationship", "coworker",
        "--use-case", "work review",
        cwd=tmp_path,
    )

    # All dimensions high — should return completion message
    coverage_path = tmp_path / "outputs/li-ming/private_evidence/interviews/coverage.json"
    coverage_path.parent.mkdir(parents=True, exist_ok=True)
    coverage_path.write_text(json.dumps({
        "identity_context": "high",
        "mental_models": "high",
        "expression_dna": "high",
        "decision_heuristics": "high",
        "pressure_response": "high",
        "profile_specific": "high",
        "honest_boundaries": "high",
        "evaluation_scenarios": "high",
        "value_order": "high",
        "anti_patterns": "high",
    }, ensure_ascii=False), encoding="utf-8")

    result = run_cli(
        "question",
        "--root", str(tmp_path),
        "--slug", "li-ming",
        "--profile", "colleague",
        "--perspective", "observer_answer",
        "--turn", "1",
        cwd=tmp_path,
    )

    assert "信息覆盖已经足够" in result.stdout


def test_cli_build_and_export(tmp_path: Path):
    from human2skill.evidence_builder import add_claim, add_evidence
    from human2skill.flow import create_project_person

    base = create_project_person(
        root=tmp_path,
        slug="li-ming",
        display_name="李明",
        profile_type="colleague",
        relationship_to_user="coworker",
        use_case="work review",
        voice_mode="advisor",
        now="2026-04-29T00:00:00+00:00",
    )

    # Build evidence pack with claims
    pack = {
        "schema_version": "1",
        "person_slug": "li-ming",
        "evidence": [],
        "claims": [],
        "conflicts": [],
    }
    ev = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary="先问 impact。",
        retention="summary_only",
        confidence="medium",
        supports=[],
    )
    add_claim(
        pack,
        claim="先问 impact。",
        claim_type="decision_heuristic",
        confidence="medium",
        evidence_ids=[ev["evidence_id"]],
    )
    (base / "private_evidence/evidence_pack.json").write_text(
        json.dumps(pack, ensure_ascii=False), encoding="utf-8"
    )

    # Write distillation
    distillation = {
        "schema_version": "1",
        "person_slug": "li-ming",
        "generated_at": "2026-04-29T00:00:00+00:00",
        "source_evidence_pack_version": "v1",
        "mental_models": [{
            "title": "Impact first",
            "content": "先问 impact，再讨论方案。",
            "claim_ids": [pack["claims"][0]["claim_id"]],
            "confidence": "medium",
            "evidence_summary": "观察者报告。",
            "limits": ["只覆盖工作评审。"],
        }],
        "decision_heuristics": [{
            "title": "Impact first",
            "content": "先问 impact。",
            "claim_ids": [pack["claims"][0]["claim_id"]],
            "confidence": "medium",
            "evidence_summary": "观察者报告。",
            "limits": ["只覆盖工作评审。"],
        }],
        "expression_dna": [{
            "title": "直接表达",
            "content": "结论先行。",
            "claim_ids": [pack["claims"][0]["claim_id"]],
            "confidence": "medium",
            "evidence_summary": "观察者报告。",
            "limits": ["只覆盖工作场景。"],
        }],
        "profile_specific": [],
        "pressure_response": [],
        "value_order": [],
        "anti_patterns": [],
        "honest_boundaries": [
            {
                "title": "关系不足",
                "content": "关系场景证据不足。",
                "claim_ids": [],
                "confidence": "low",
                "evidence_summary": "无证据。",
                "limits": ["不推断关系。"],
            },
            {
                "title": "技术细节有限",
                "content": "技术实现细节证据不足。",
                "claim_ids": [],
                "confidence": "low",
                "evidence_summary": "无技术讨论记录。",
                "limits": ["不推断技术偏好。"],
            },
            {
                "title": "时间范围有限",
                "content": "仅覆盖当年工作场景。",
                "claim_ids": [],
                "confidence": "medium",
                "evidence_summary": "仅当年材料。",
                "limits": ["历史变化未追踪。"],
            },
        ],
        "scenario_tests": [],
    }
    (base / "private_evidence/distillation.json").write_text(
        json.dumps(distillation, ensure_ascii=False), encoding="utf-8"
    )

    arg_root = str(tmp_path)
    # Run build via CLI
    result = run_cli(
        "build",
        "--root", arg_root,
        "--slug", "li-ming",
        cwd=tmp_path,
    )

    assert "built" in result.stdout.lower()
    assert (base / "public_skill/SKILL.md").exists()


def test_cli_export_command(tmp_path: Path):
    from human2skill.evidence_builder import add_claim, add_evidence
    from human2skill.flow import create_project_person

    base = create_project_person(
        root=tmp_path,
        slug="li-ming",
        display_name="李明",
        profile_type="colleague",
        relationship_to_user="coworker",
        use_case="work review",
        voice_mode="advisor",
        now="2026-04-29T00:00:00+00:00",
    )

    # Minimal evidence pack + distillation
    pack = {
        "schema_version": "1",
        "person_slug": "li-ming",
        "evidence": [],
        "claims": [],
        "conflicts": [],
    }
    ev = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary="先问 impact。",
        retention="summary_only",
        confidence="medium",
        supports=[],
    )
    add_claim(
        pack,
        claim="先问 impact。",
        claim_type="decision_heuristic",
        confidence="medium",
        evidence_ids=[ev["evidence_id"]],
    )
    (base / "private_evidence/evidence_pack.json").write_text(
        json.dumps(pack, ensure_ascii=False), encoding="utf-8"
    )
    distillation = {
        "schema_version": "1",
        "person_slug": "li-ming",
        "generated_at": "2026-04-29T00:00:00+00:00",
        "source_evidence_pack_version": "v1",
        "mental_models": [{
            "title": "Impact first",
            "content": "先问 impact，再讨论方案。",
            "claim_ids": [pack["claims"][0]["claim_id"]],
            "confidence": "medium",
            "evidence_summary": "观察者报告。",
            "limits": ["只覆盖工作评审。"],
        }],
        "decision_heuristics": [{
            "title": "Impact first",
            "content": "先问 impact。",
            "claim_ids": [pack["claims"][0]["claim_id"]],
            "confidence": "medium",
            "evidence_summary": "观察者报告。",
            "limits": ["只覆盖工作评审。"],
        }],
        "expression_dna": [{
            "title": "直接表达",
            "content": "结论先行。",
            "claim_ids": [pack["claims"][0]["claim_id"]],
            "confidence": "medium",
            "evidence_summary": "观察者报告。",
            "limits": ["只覆盖工作场景。"],
        }],
        "profile_specific": [],
        "pressure_response": [],
        "value_order": [],
        "anti_patterns": [],
        "honest_boundaries": [
            {
                "title": "关系不足",
                "content": "关系场景证据不足。",
                "claim_ids": [],
                "confidence": "low",
                "evidence_summary": "无证据。",
                "limits": ["不推断关系。"],
            },
            {
                "title": "技术细节有限",
                "content": "技术实现细节证据不足。",
                "claim_ids": [],
                "confidence": "low",
                "evidence_summary": "无技术讨论记录。",
                "limits": ["不推断技术偏好。"],
            },
            {
                "title": "时间范围有限",
                "content": "仅覆盖当年工作场景。",
                "claim_ids": [],
                "confidence": "medium",
                "evidence_summary": "仅当年材料。",
                "limits": ["历史变化未追踪。"],
            },
        ],
        "scenario_tests": [],
    }
    (base / "private_evidence/distillation.json").write_text(
        json.dumps(distillation, ensure_ascii=False), encoding="utf-8"
    )

    arg_root = str(tmp_path)
    # Build first
    run_cli("build", "--root", arg_root, "--slug", "li-ming", cwd=tmp_path)

    # Export
    result = run_cli(
        "export",
        "--root", arg_root,
        "--slug", "li-ming",
        "--host", "codex",
        "--variant", "advisor",
        cwd=tmp_path,
    )

    assert "exported" in result.stdout.lower()
    assert (base / "exports/codex/SKILL.md").exists()
    assert (base / "exports/codex/export_manifest.json").exists()


def test_cli_install_command(tmp_path: Path):
    export_dir = tmp_path / "export"
    export_dir.mkdir(parents=True)
    (export_dir / "SKILL.md").write_text("# Test Skill", encoding="utf-8")

    target_dir = tmp_path / "skills"
    target_dir.mkdir(parents=True)

    result = run_cli(
        "install",
        "--export", str(export_dir),
        "--target", str(target_dir),
        "--name", "test-skill",
        cwd=tmp_path,
    )

    assert "installed" in result.stdout.lower()
    installed_skill = target_dir / "test-skill" / "SKILL.md"
    assert installed_skill.exists()
    assert installed_skill.read_text(encoding="utf-8") == "# Test Skill"


def test_cli_review_command(tmp_path: Path):
    from human2skill.evidence_builder import add_claim, add_evidence
    from human2skill.flow import create_project_person

    base = create_project_person(
        root=tmp_path,
        slug="li-ming",
        display_name="李明",
        profile_type="colleague",
        relationship_to_user="coworker",
        use_case="work review",
        voice_mode="advisor",
        now="2026-04-29T00:00:00+00:00",
    )

    # Set up evidence and distillation, then build, then review
    pack = {
        "schema_version": "1",
        "person_slug": "li-ming",
        "evidence": [],
        "claims": [],
        "conflicts": [],
    }
    ev = add_evidence(
        pack,
        source_type="direct_quote_or_behavior",
        source_summary="先问 impact。",
        retention="summary_only",
        confidence="medium",
        supports=[],
    )
    add_claim(
        pack,
        claim="先问 impact。",
        claim_type="decision_heuristic",
        confidence="medium",
        evidence_ids=[ev["evidence_id"]],
    )
    (base / "private_evidence/evidence_pack.json").write_text(
        json.dumps(pack, ensure_ascii=False), encoding="utf-8"
    )
    distillation = {
        "schema_version": "1",
        "person_slug": "li-ming",
        "generated_at": "2026-04-29T00:00:00+00:00",
        "source_evidence_pack_version": "v1",
        "mental_models": [{
            "title": "Impact first",
            "content": "先问 impact，再讨论方案。",
            "claim_ids": [pack["claims"][0]["claim_id"]],
            "confidence": "medium",
            "evidence_summary": "观察者报告。",
            "limits": ["只覆盖工作评审。"],
        }],
        "decision_heuristics": [{
            "title": "Impact first",
            "content": "先问 impact。",
            "claim_ids": [pack["claims"][0]["claim_id"]],
            "confidence": "medium",
            "evidence_summary": "观察者报告。",
            "limits": ["只覆盖工作评审。"],
        }],
        "expression_dna": [{
            "title": "直接表达",
            "content": "结论先行。",
            "claim_ids": [pack["claims"][0]["claim_id"]],
            "confidence": "medium",
            "evidence_summary": "观察者报告。",
            "limits": ["只覆盖工作场景。"],
        }],
        "profile_specific": [],
        "pressure_response": [],
        "value_order": [],
        "anti_patterns": [],
        "honest_boundaries": [
            {
                "title": "关系不足",
                "content": "关系场景证据不足。",
                "claim_ids": [],
                "confidence": "low",
                "evidence_summary": "无证据。",
                "limits": ["不推断关系。"],
            },
            {
                "title": "技术细节有限",
                "content": "技术实现细节证据不足。",
                "claim_ids": [],
                "confidence": "low",
                "evidence_summary": "无技术讨论记录。",
                "limits": ["不推断技术偏好。"],
            },
            {
                "title": "时间范围有限",
                "content": "仅覆盖当年工作场景。",
                "claim_ids": [],
                "confidence": "medium",
                "evidence_summary": "仅当年材料。",
                "limits": ["历史变化未追踪。"],
            },
        ],
        "scenario_tests": [],
    }
    (base / "private_evidence/distillation.json").write_text(
        json.dumps(distillation, ensure_ascii=False), encoding="utf-8"
    )

    arg_root = str(tmp_path)
    # Build first
    run_cli("build", "--root", arg_root, "--slug", "li-ming", cwd=tmp_path)

    # Run review
    result = run_cli(
        "review",
        "--root", arg_root,
        "--slug", "li-ming",
        cwd=tmp_path,
    )

    assert "pass" in result.stdout.lower()
    # Review summary should exist
    review = json.loads(result.stdout)
    assert "passed" in review


def test_cli_review_command_can_select_variant(tmp_path: Path):
    from human2skill.flow import create_project_person
    from human2skill.storage import write_json

    base = create_project_person(
        root=tmp_path,
        slug="li-ming",
        display_name="李明",
        profile_type="colleague",
        relationship_to_user="coworker",
        use_case="work review",
        voice_mode="both",
        now="2026-05-01T00:00:00+00:00",
    )

    def review_payload(variant: str, passed: bool) -> dict:
        return {
            "schema_version": "1",
            "person_slug": "li-ming",
            "variant": variant,
            "generated_at": "2026-05-01T00:00:00+00:00",
            "passed": passed,
            "hard_failures": [],
            "scores": {
                "evidence_consistency": 4,
                "confidence_calibration": 4,
                "honest_boundary": 5,
                "privacy_safety": 5,
                "expression_similarity": 4,
                "thinking_utility": 4,
                "profile_fit": 4,
            },
            "required_changes": [],
            "notes": [],
        }

    write_json(
        base / "private_evidence/reviews/advisor.json",
        review_payload("advisor", True),
    )
    write_json(
        base / "private_evidence/reviews/first_person.json",
        review_payload("first_person", False),
    )

    result = run_cli(
        "review",
        "--root", str(tmp_path),
        "--slug", "li-ming",
        "--variant", "first_person",
        cwd=tmp_path,
    )

    review = json.loads(result.stdout)
    assert review["variant"] == "first_person"
    assert review["passed"] is False
