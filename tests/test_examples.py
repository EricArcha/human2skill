import json
from pathlib import Path


EXAMPLES = [
    Path("examples/colleague-li-ming"),
    Path("examples/relationship-chen-yu"),
    Path("examples/self-future-me"),
]


def test_examples_have_public_skill_private_evidence_and_review():
    for base in EXAMPLES:
        assert (base / "public_skill/SKILL.md").exists()
        assert (base / "private_evidence/evidence_pack.json").exists()
        assert (base / "private_evidence/reviews/review-v1.json").exists()


def test_examples_do_not_allow_private_quotes():
    for base in EXAMPLES:
        meta = json.loads((base / "person.meta.json").read_text(encoding="utf-8"))
        assert meta["privacy_policy"]["public_skill_allows_private_quotes"] is False


def test_examples_review_passed():
    for base in EXAMPLES:
        review = json.loads((base / "private_evidence/reviews/review-v1.json").read_text(encoding="utf-8"))
        assert review["passed"] is True
