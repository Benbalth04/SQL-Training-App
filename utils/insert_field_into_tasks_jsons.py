import json
from pathlib import Path

# Current directory of this script
current_dir = Path(__file__).resolve().parent

# Path to lessons directory
lessons_dir = current_dir.parent / "lessons"

INSERT_FIELD = "chatgpt-prompt"
DEFAULT_VALUE = True

# Iterate over lesson directories
for item in lessons_dir.iterdir():
    if not item.is_dir() or "lesson" not in item.name.lower():
        continue

    lesson_json_path = item / "lesson.json"  # Use the specific lesson folder

    if not lesson_json_path.exists():
        print(f"Unable to find lesson JSON for {item.name}")
        continue

    # Load JSON
    with open(lesson_json_path, "r", encoding="utf-8") as f:
        lesson_json = json.load(f)

    exercise_list = lesson_json.get("exercise-tasks")
    if not exercise_list:
        print(f"No exercise tasks found for {item.name}")
        continue

    # Add the field to each task if it doesn't already exist
    for task in exercise_list:
        if INSERT_FIELD not in task:
            task[INSERT_FIELD] = DEFAULT_VALUE

    # Save JSON back to file
    with open(lesson_json_path, "w", encoding="utf-8") as f:
        json.dump(lesson_json, f, indent=4)

    print(f"Updated {lesson_json_path} successfully.")
