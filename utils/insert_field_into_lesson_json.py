import json
from pathlib import Path

current_dir = Path(__file__).resolve().parent
lessons_dir = current_dir.parent / "lessons"

INSERT_FIELD = "difficulty"
DEFAULT_VALUE = "Beginner"

lessons_overview_json = lessons_dir / "lessons-overview.json"

# Load overview
with open(lessons_overview_json, "r", encoding="utf-8") as f:
    lessons_overview = json.load(f)

if not lessons_overview:
    raise ValueError("Unable to load lessons-overview.json file")

for lesson in lessons_overview.get("lessons", []):
    lesson_id = lesson.get("lesson-id")
    item_dir = lessons_dir / lesson_id

    if not item_dir.is_dir():
        print(f"Lesson folder not found: {lesson_id}")
        continue

    lesson_json_path = item_dir / "lesson.json"
    if not lesson_json_path.exists():
        print(f"Unable to find lesson JSON for {lesson_id}")
        continue

    with open(lesson_json_path, "r", encoding="utf-8") as f:
        lesson_json = json.load(f)

    lesson_difficulty = lesson.get("difficulty", DEFAULT_VALUE)
    lesson_json[INSERT_FIELD] = lesson_difficulty

    with open(lesson_json_path, "w", encoding="utf-8") as f:
        json.dump(lesson_json, f, indent=4)

    print(f"Updated {lesson_json_path} successfully.")
