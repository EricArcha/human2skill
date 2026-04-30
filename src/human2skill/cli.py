"""human2skill CLI entry point.

Subcommands: create, ingest, question, build, review, export, install.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from human2skill.exporter import export_skill, load_review_for_variant
from human2skill.flow import build_from_distillation, create_project_person
from human2skill.ingest import ingest_file
from human2skill.installer import install_export
from human2skill.interview import initial_coverage, next_question_for_profile
from human2skill.storage import person_dir


def _cmd_create(args: argparse.Namespace) -> None:
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
        coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
    else:
        coverage = initial_coverage()

    question = next_question_for_profile(
        coverage,
        profile_type=args.profile,
        perspective=args.perspective,
        turn_count=args.turn,
    )
    print(question)


def _cmd_build(args: argparse.Namespace) -> None:
    base = person_dir(Path(args.root), args.slug)

    distillation_path = (
        Path(args.distillation)
        if args.distillation
        else base / "private_evidence" / "distillation.json"
    )
    if not distillation_path.exists():
        print(
            f"error: distillation file not found: {distillation_path}", file=sys.stderr
        )
        sys.exit(1)

    distillation = json.loads(distillation_path.read_text(encoding="utf-8"))
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
        print("error: no reviews directory found", file=sys.stderr)
        sys.exit(1)

    review_files = sorted(reviews_dir.glob("*.json"))
    if not review_files:
        print("error: no review files found", file=sys.stderr)
        sys.exit(1)

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


def main() -> None:
    parser = argparse.ArgumentParser(prog="human2skill")
    sub = parser.add_subparsers(dest="command")

    # ---- create ----
    p_create = sub.add_parser("create", help="Initialize a new person project")
    p_create.add_argument("--root", required=True, help="Root directory for people storage")
    p_create.add_argument("--slug", required=True, help="Person identifier slug")
    p_create.add_argument("--name", required=True, help="Display name")
    p_create.add_argument("--profile", default=None, help="Profile type (colleague/relationship/mentor/self)")
    p_create.add_argument("--relationship", required=True, help="Relationship to user")
    p_create.add_argument("--use-case", required=True, help="Primary use case")
    p_create.add_argument("--voice-mode", default="advisor", help="Voice mode (advisor/first_person/both)")

    # ---- ingest ----
    p_ingest = sub.add_parser("ingest", help="Ingest a source file into a person project")
    p_ingest.add_argument("--root", required=True)
    p_ingest.add_argument("--slug", required=True)
    p_ingest.add_argument("--file", required=True, help="Path to the file to ingest (.md, .txt, .pdf)")

    # ---- question ----
    p_question = sub.add_parser("question", help="Get the next interview question for a person")
    p_question.add_argument("--root", required=True)
    p_question.add_argument("--slug", required=True)
    p_question.add_argument("--profile", required=True, help="Profile type (colleague/relationship/mentor/self)")
    p_question.add_argument("--perspective", required=True, help="self_answer or observer_answer")
    p_question.add_argument("--turn", type=int, required=True, help="Current interview turn number")

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
    p_export.add_argument("--host", required=True, help="Target host (codex/claude-code/openclaw/hermes)")
    p_export.add_argument("--variant", default="advisor", help="Skill variant (default: advisor)")

    # ---- install ----
    p_install = sub.add_parser("install", help="Install an exported skill into a target directory")
    p_install.add_argument("--export", dest="export_dir", required=True, help="Path to export directory")
    p_install.add_argument("--target", required=True, help="Target directory to install into")
    p_install.add_argument("--name", required=True, help="Package name for the installed skill")
    p_install.add_argument("--no-force", action="store_true", help="Fail if target already exists")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    dispatch: dict[str, callable] = {
        "create": _cmd_create,
        "ingest": _cmd_ingest,
        "question": _cmd_question,
        "build": _cmd_build,
        "review": _cmd_review,
        "export": _cmd_export,
        "install": _cmd_install,
    }

    dispatch[args.command](args)


if __name__ == "__main__":
    main()
