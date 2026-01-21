import json
from pathlib import Path

# Current directory of this script
current_dir = Path(__file__).resolve().parent

# Path to lessons-overview.json
lesson_overview_file = current_dir.parent.parent / "lessons" / "lessons-overview.json"

# Load JSON
with open(lesson_overview_file, "r", encoding="utf-8") as f:
    overview_lesson_json = json.load(f)

# Iterate lessons
for item in overview_lesson_json.get("lessons", []):
    lesson_id = item.get("lesson-id")
    if not lesson_id:
        continue

    # Folder path for this lesson
    lesson_folder = current_dir.parent / "lessons" / lesson_id

    # Create folder if missing
    if not lesson_folder.exists():
        print(f"Creating folder: {lesson_folder}")
        lesson_folder.mkdir(parents=True, exist_ok=True)
    else: 
        continue

    # Create content.md if missing
    content_file = lesson_folder / "content.md"
    if not content_file.exists():
        print(f"Creating file: {content_file}")
        content_file.write_text("", encoding="utf-8")

    # Create lesson.json if missing
    lesson_json_file = lesson_folder / "lesson.json"
    if not lesson_json_file.exists():
        print(f"Creating file: {lesson_json_file}")
        lesson_json_file.write_text("{}", encoding="utf-8")

