REQUIRED_SCENARIO_TYPES = {"historical", "counterfactual", "boundary"}


def build_scenario_replay_report(
    person_slug: str,
    variant: str,
    generated_at: str,
    scenarios: list[dict],
) -> dict:
    """Build a scenario replay report for a generated skill.

    Required scenario types: historical, counterfactual, boundary.
    Report passes when all scenarios pass and all three types are present.
    """
    present_types = {s.get("scenario_type") for s in scenarios}
    missing_scenario_types = sorted(REQUIRED_SCENARIO_TYPES - present_types)

    all_scenarios_passed = all(s.get("passed") is True for s in scenarios)

    passed = all_scenarios_passed and not missing_scenario_types

    report = {
        "schema_version": "1",
        "person_slug": person_slug,
        "variant": variant,
        "generated_at": generated_at,
        "scenarios": scenarios,
        "passed": passed,
    }

    if missing_scenario_types:
        report["missing_scenario_types"] = missing_scenario_types

    return report


def scenario_summary_passed(report: dict) -> bool:
    """Return True if the scenario replay report passed."""
    return report.get("passed", False) is True
