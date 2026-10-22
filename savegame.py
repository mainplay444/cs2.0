"""Small JSON save/load helpers."""
import json
from pathlib import Path

SAVE_PATH = Path.home() / ".zombie_frontline_3d.json"

def save_progress(data: dict, path: Path = SAVE_PATH) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def load_progress(path: Path = SAVE_PATH) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
