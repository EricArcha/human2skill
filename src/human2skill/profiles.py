import json
from pathlib import Path

from human2skill.constants import PROFILE_TYPES
from human2skill.schemas import resource_path


def profile_dir() -> Path:
    return resource_path("templates", "profiles")


def load_profile(profile_type: str) -> dict:
    if profile_type not in PROFILE_TYPES:
        raise ValueError(f"Unknown profile type: {profile_type}")
    return json.loads((profile_dir() / f"{profile_type}.json").read_text(encoding="utf-8"))


def infer_profile_type(text: str) -> str:
    normalized = text.lower()
    colleague_markers = ("公司", "同事", "上级", "下级", "项目", "评审", "prd", "review", "交付")
    relationship_markers = ("朋友", "亲人", "伴侣", "父母", "孩子", "关系", "情绪")
    mentor_markers = ("导师", "老师", "专家", "顾问", "课程", "方法论", "博主")
    self_markers = ("我自己", "过去的我", "未来的我", "self")

    if any(marker in normalized for marker in self_markers):
        return "self"
    if any(marker in normalized for marker in colleague_markers):
        return "colleague"
    if any(marker in normalized for marker in relationship_markers):
        return "relationship"
    if any(marker in normalized for marker in mentor_markers):
        return "mentor"
    return "relationship"
