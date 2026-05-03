"""human2skill CLI entry point.

Subcommands: create, ingest, question, build, review, export, install.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from human2skill.constants import PROFILE_TYPES, VOICE_MODES
from human2skill.exporter import export_skill, load_review_for_variant
from human2skill.flow import build_from_distillation, create_project_person
from human2skill.ingest import ingest_file
from human2skill.installer import install_export
from human2skill.intake import project_exists, project_status
from human2skill.interview import (
    assess_coverage,
    initial_coverage,
    next_question_for_profile,
    run_interview_loop,
)
from human2skill.storage import person_dir


def _handle_error(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def _cmd_create(args: argparse.Namespace) -> None:
    base_dir = Path(args.root) / "outputs" / args.slug
    if base_dir.exists() and not args.force:
        print(
            f"error: project '{args.slug}' already exists at {base_dir}\n"
            f"  Use --force to overwrite (not recommended), or run an incremental update instead.",
            file=sys.stderr,
        )
        sys.exit(1)
    base = create_project_person(
        root=Path(args.root),
        slug=args.slug,
        display_name=args.name,
        profile_type=args.profile,
        relationship_to_user=args.relationship,
        use_case=args.use_case,
        voice_mode=args.voice_mode,
    )
    print(f"created: {base}")


def _cmd_ingest(args: argparse.Namespace) -> None:
    base = person_dir(Path(args.root), args.slug)
    source = ingest_file(base, Path(args.file))
    print(f"ingested: {source['source_id']}")


def _cmd_question(args: argparse.Namespace) -> None:
    base = person_dir(Path(args.root), args.slug)
    coverage_path = base / "private_evidence" / "interviews" / "coverage.json"

    if coverage_path.exists():
        try:
            coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            _handle_error(f"Failed to read coverage file: {coverage_path}: {exc}")
    else:
        coverage = initial_coverage()

    question = next_question_for_profile(
        coverage,
        profile_type=args.profile,
        perspective=args.perspective,
        turn_count=args.turn,
    )
    print(question)


def _cmd_interview(args: argparse.Namespace) -> None:
    base = person_dir(Path(args.root), args.slug)
    interviews_dir = base / "private_evidence" / "interviews"
    coverage_path = interviews_dir / "coverage.json"

    if coverage_path.exists():
        try:
            coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            _handle_error(f"Failed to read coverage file: {coverage_path}: {exc}")
    else:
        coverage = None

    run_interview_loop(
        profile_type=args.profile,
        perspective=args.perspective,
        output_dir=interviews_dir,
        coverage=coverage,
    )


def _cmd_check_coverage(args: argparse.Namespace) -> None:
    base = person_dir(Path(args.root), args.slug)
    coverage_path = base / "private_evidence" / "interviews" / "coverage.json"

    if not coverage_path.exists():
        coverage = initial_coverage()
    else:
        try:
            coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            _handle_error(f"Failed to read coverage file: {coverage_path}: {exc}")

    assessment = assess_coverage(coverage)

    print("=" * 60)
    print("⛔ Checkpoint A — 覆盖率审查")
    print("=" * 60)
    print(f"维度覆盖: {assessment['dimensions_covered']}/{assessment['total_dimensions']} ≥ medium")
    print(f"诚实边界: {'已标注' if assessment['has_boundary'] else '未标注'}")
    print(f"缺口维度: {', '.join(assessment['gaps']) if assessment['gaps'] else '无'}")
    print(f"状态: {'✅ 满足进入蒸馏条件' if assessment['sufficient'] else '❌ 建议继续补充或签署降级确认'}")
    print("=" * 60)


def _cmd_build(args: argparse.Namespace) -> None:
    base = person_dir(Path(args.root), args.slug)

    distillation_path = (
        Path(args.distillation)
        if args.distillation
        else base / "private_evidence" / "distillation.json"
    )
    if not distillation_path.exists():
        _handle_error(f"distillation file not found: {distillation_path}")

    try:
        distillation = json.loads(distillation_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        _handle_error(f"Failed to read distillation file: {distillation_path}: {exc}")

    result = build_from_distillation(base, distillation)
    passed = result["review"].get("passed", False)
    print(f"built: {base} (review passed={passed})")


def _cmd_review(args: argparse.Namespace) -> None:
    base = person_dir(Path(args.root), args.slug)
    reviews_dir = base / "private_evidence" / "reviews"

    if args.variant:
        review = load_review_for_variant(base, args.variant)
        print(json.dumps(review, ensure_ascii=False, indent=2))
        return

    if not reviews_dir.is_dir():
        _handle_error("no reviews directory found")

    review_files = sorted(reviews_dir.glob("*.json"))
    if not review_files:
        _handle_error("no review files found")

    # Print the latest review report as JSON
    latest_review = json.loads(review_files[-1].read_text(encoding="utf-8"))
    print(json.dumps(latest_review, ensure_ascii=False, indent=2))


def _cmd_export(args: argparse.Namespace) -> None:
    base = person_dir(Path(args.root), args.slug)
    export_dir = export_skill(base, host=args.host, variant=args.variant)
    print(f"exported: {export_dir}")


def _cmd_install(args: argparse.Namespace) -> None:
    force = not args.no_force
    target = install_export(
        Path(args.export_dir),
        Path(args.target),
        args.name,
        force=force,
    )
    print(f"installed: {target}")


def _cmd_status(args: argparse.Namespace) -> None:
    base = person_dir(Path(args.root), args.slug)
    status = project_status(base)
    if not status["exists"]:
        print(f"project '{args.slug}' does not exist")
        return

    print(f"slug:          {args.slug}")
    print(f"version:       {status['version']}")
    print(f"created:       {status['created_at']}")
    print(f"updated:       {status['updated_at']}")
    print(f"mental models: {status['mental_model_count']}")
    print(f"sources:       {status['source_count']}")
    print(f"snapshots:     {status['version_count']}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="human2skill")
    sub = parser.add_subparsers(dest="command")

    # ---- create ----
    p_create = sub.add_parser("create", help="Initialize a new person project")
    p_create.add_argument("--root", required=True, help="Root directory for people storage")
    p_create.add_argument("--slug", required=True, help="Person identifier slug")
    p_create.add_argument("--name", required=True, help="Display name")
    p_create.add_argument("--profile", default=None, choices=PROFILE_TYPES, help="Profile type")
    p_create.add_argument("--relationship", required=True, help="Relationship to user")
    p_create.add_argument("--use-case", required=True, help="Primary use case")
    p_create.add_argument("--voice-mode", default="advisor", choices=VOICE_MODES, help="Voice mode")
    p_create.add_argument("--force", action="store_true", help="Overwrite existing project")

    # ---- ingest ----
    p_ingest = sub.add_parser("ingest", help="Ingest a source file into a person project")
    p_ingest.add_argument("--root", required=True)
    p_ingest.add_argument("--slug", required=True)
    p_ingest.add_argument("--file", required=True, help="Path to the file to ingest (.md, .txt, .pdf)")

    # ---- question ----
    p_question = sub.add_parser("question", help="Get the next interview question for a person")
    p_question.add_argument("--root", required=True)
    p_question.add_argument("--slug", required=True)
    p_question.add_argument("--profile", required=True, choices=PROFILE_TYPES, help="Profile type")
    p_question.add_argument("--perspective", required=True, choices=("self_answer", "observer_answer"), help="Answer perspective")
    p_question.add_argument("--turn", type=int, required=True, help="Current interview turn number")

    # ---- interview ----
    p_interview = sub.add_parser("interview", help="Run the interactive 20-question interview")
    p_interview.add_argument("--root", required=True)
    p_interview.add_argument("--slug", required=True)
    p_interview.add_argument("--profile", required=True, choices=PROFILE_TYPES, help="Profile type")
    p_interview.add_argument("--perspective", required=True, choices=("self_answer", "observer_answer"), help="Answer perspective")

    # ---- check-coverage ----
    p_check = sub.add_parser("check-coverage", help="Show interview coverage summary")
    p_check.add_argument("--root", required=True)
    p_check.add_argument("--slug", required=True)

    # ---- build ----
    p_build = sub.add_parser("build", help="Build skill from a distillation payload")
    p_build.add_argument("--root", required=True)
    p_build.add_argument("--slug", required=True)
    p_build.add_argument("--distillation", default=None, help="Path to distillation JSON (default: private_evidence/distillation.json)")

    # ---- review ----
    p_review = sub.add_parser("review", help="Show a review report for a person")
    p_review.add_argument("--root", required=True)
    p_review.add_argument("--slug", required=True)
    p_review.add_argument("--variant", default=None, help="Review variant to show (advisor/first_person)")

    # ---- export ----
    p_export = sub.add_parser("export", help="Export a skill for a target host")
    p_export.add_argument("--root", required=True)
    p_export.add_argument("--slug", required=True)
    p_export.add_argument("--host", required=True, choices=("codex", "claude-code", "openclaw", "hermes"), help="Target host")
    p_export.add_argument("--variant", default="advisor", choices=("advisor", "first_person"), help="Skill variant")

    # ---- install ----
    p_install = sub.add_parser("install", help="Install an exported skill into a target directory")
    p_install.add_argument("--export", dest="export_dir", required=True, help="Path to export directory")
    p_install.add_argument("--target", required=True, help="Target directory to install into")
    p_install.add_argument("--name", required=True, help="Package name for the installed skill")
    p_install.add_argument("--no-force", action="store_true", help="Fail if target already exists")

    # ---- status ----
    p_status = sub.add_parser("status", help="Show project status summary")
    p_status.add_argument("--root", required=True)
    p_status.add_argument("--slug", required=True)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    dispatch: dict[str, callable] = {
        "create": _cmd_create,
        "ingest": _cmd_ingest,
        "question": _cmd_question,
        "interview": _cmd_interview,
        "check-coverage": _cmd_check_coverage,
        "build": _cmd_build,
        "review": _cmd_review,
        "export": _cmd_export,
        "install": _cmd_install,
        "status": _cmd_status,
    }

    dispatch[args.command](args)


if __name__ == "__main__":
    main()
