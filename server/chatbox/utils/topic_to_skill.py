from pathlib import Path
from functools import lru_cache
import json

SKILLS_ROOT = Path(__file__).resolve().parent.parent / "chat_agents" / "skills"
ROUTER_CONFIG_PATH = SKILLS_ROOT / "router.json"
DEFAULT_SKILL_NAME = "general_question"


@lru_cache(maxsize=1)
def _load_router_config() -> tuple[str, list[tuple[str, tuple[str, ...]]]]:
    try:
        config = json.loads(ROUTER_CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Failed to load router config from {ROUTER_CONFIG_PATH}: {e}")
        return DEFAULT_SKILL_NAME, []

    default_skill = config.get("default_skill", DEFAULT_SKILL_NAME)
    if not isinstance(default_skill, str) or not default_skill.strip():
        default_skill = DEFAULT_SKILL_NAME
    default_skill = default_skill.strip()

    rules_raw = config.get("rules", [])
    rules: list[tuple[str, tuple[str, ...]]] = []
    if isinstance(rules_raw, list):
        for rule in rules_raw:
            if not isinstance(rule, dict):
                continue
            skill_name = rule.get("skill", "")
            keywords = rule.get("keywords", [])
            if not isinstance(skill_name, str) or not skill_name.strip():
                continue
            if not isinstance(keywords, list):
                continue
            normalized_keywords = tuple(
                keyword.strip().lower()
                for keyword in keywords
                if isinstance(keyword, str) and keyword.strip()
            )
            if not normalized_keywords:
                continue
            rules.append((skill_name.strip(), normalized_keywords))

    return default_skill, rules

def topic_to_skill_name(topic: str) -> str:
    topic_lower = (topic or "").strip().lower()
    if not topic_lower:
        default_skill, _ = _load_router_config()
        return default_skill

    default_skill, rules = _load_router_config()
    for skill_name, keywords in rules:
        if any(keyword in topic_lower for keyword in keywords):
            return skill_name
    return default_skill


@lru_cache(maxsize=8)
def load_prompt_by_skill(skill_name: str, prompt_filename: str) -> str:
    prompt_path = SKILLS_ROOT / skill_name / "prompts" / prompt_filename
    try:
        content = prompt_path.read_text(encoding="utf-8").strip()
        if content:
            return content
    except Exception as e:
        print(f"Failed to read prompt from {prompt_path}: {e}")
    fallback_path = SKILLS_ROOT / "general_question" / "prompts" / prompt_filename
    try:
        content = fallback_path.read_text(encoding="utf-8").strip()
        if content:
            return content
    except Exception as e:
        print(f"Failed to read fallback prompt from {fallback_path}: {e}")
    return ""
