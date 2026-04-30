from human2skill.scenario import build_scenario_replay_report, scenario_summary_passed


def test_build_scenario_replay_report_requires_three_types():
    report = build_scenario_replay_report(
        person_slug="li-ming",
        variant="advisor",
        generated_at="2026-04-29T00:00:00+00:00",
        scenarios=[
            {
                "scenario_type": "historical",
                "input": "评审延期需求",
                "expected_behavior": "先问 impact",
                "actual_behavior": "先问目标和 impact",
                "passed": True,
                "notes": []
            },
            {
                "scenario_type": "counterfactual",
                "input": "高收益但实现很脏",
                "expected_behavior": "权衡收益和维护成本",
                "actual_behavior": "先问收益再看风险",
                "passed": True,
                "notes": []
            },
            {
                "scenario_type": "boundary",
                "input": "亲密关系建议",
                "expected_behavior": "承认证据不足",
                "actual_behavior": "说明关系场景证据不足",
                "passed": True,
                "notes": []
            },
        ],
    )

    assert scenario_summary_passed(report) is True
    assert len(report["scenarios"]) == 3
