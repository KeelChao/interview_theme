import json
from functools import lru_cache
from pathlib import Path
from typing import Any


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def fixture_path(name: str) -> Path:
    candidates = [
        Path.cwd() / "data" / "fixtures" / name,
        project_root() / "data" / "fixtures" / name,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    searched = ", ".join(str(candidate) for candidate in candidates)
    raise FileNotFoundError(f"fixture {name} not found; searched: {searched}")


@lru_cache
def load_fixture(name: str) -> list[dict[str, Any]]:
    path = fixture_path(name)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"fixture {name} must contain a JSON list")
    return data


def match_text(item: dict[str, Any], query: str) -> bool:
    haystack = " ".join(str(value) for value in item.values()).lower()
    return any(token for token in query.lower().split() if token in haystack)
