from human2skill.profiles import infer_profile_type, load_profile


def test_loads_all_profiles():
    for profile_type in ("colleague", "relationship", "mentor", "self"):
        profile = load_profile(profile_type)
        assert profile["profile_type"] == profile_type
        assert "core_sections" in profile
        assert "special_sections" in profile


def test_infers_colleague_from_work_context():
    assert infer_profile_type("字节同事，负责项目评审") == "colleague"


def test_infers_relationship_from_family_context():
    assert infer_profile_type("这是我的亲人，主要想理解关系和情绪") == "relationship"


def test_infers_mentor_from_expert_context():
    assert infer_profile_type("他是我的导师，擅长方法论") == "mentor"


def test_infers_self_from_self_context():
    assert infer_profile_type("我想蒸馏过去的我") == "self"
