import json
from pathlib import Path

# Current directory of this script
current_dir = Path(__file__).resolve().parent

# Path to lessons directory
lessons_dir = current_dir.parent / "lessons"

REMOVE_FIELD = "difficulty"

# Iterate over lesson directories
for item in lessons_dir.iterdir():
    if not item.is_dir() or "lesson" not in item.name.lower():
        continue

    lesson_json_path = item / "lesson.json"

    if not lesson_json_path.exists():
        print(f"Unable to find lesson JSON for {item.name}")
        continue

    # Load JSON
    with open(lesson_json_path, "r", encoding="utf-8") as f:
        lesson_json = json.load(f)

    # Remove the field from each task if it exists
    if REMOVE_FIELD in lesson_json:
        del lesson_json[REMOVE_FIELD]

    # Save JSON back to file
    with open(lesson_json_path, "w", encoding="utf-8") as f:
        json.dump(lesson_json, f, indent=4)

    print(f"Removed '{REMOVE_FIELD}' from {lesson_json_path} successfully.")
