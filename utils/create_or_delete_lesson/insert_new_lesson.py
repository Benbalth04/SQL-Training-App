import json
import re
from pathlib import Path

# ------------------------------------------------------------
# Update before running 
lesson_number = 7
# ------------------------------------------------------------

if not isinstance(lesson_number, int) or lesson_number <= 0:
    raise ValueError(f"Invalid lesson number: {lesson_number}")

current_dir = Path(__file__).resolve().parent
lessons_root = current_dir.parent / "lessons"
overview_file = lessons_root / "lessons-overview.json"

# ------------------------------------------------------------
# LOAD OVERVIEW
# ------------------------------------------------------------
with open(overview_file, "r", encoding="utf-8") as f:
    overview = json.load(f)

lessons = overview.get("lessons", [])

# ------------------------------------------------------------
# SHIFT EXISTING LESSONS UP (>= INSERT POINT)
# ------------------------------------------------------------
def update_folder_contents(folder: Path, old_num: int, new_num: int):
    for file in folder.rglob("*"):
        if file.is_file():
            try:
                text = file.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue

            text = text.replace(f"Lesson {old_num}", f"Lesson {new_num}")
            text = re.sub(
                rf"\blesson-{old_num}\b",
                f"lesson-{new_num}",
                text
            )

            file.write_text(text, encoding="utf-8")

# Work backwards to avoid rename collisions
for lesson in sorted(lessons, key=lambda x: x["lesson-order"], reverse=True):
    old_order = lesson["lesson-order"]

    if old_order >= lesson_number:
        new_order = old_order + 1

        old_id = lesson["lesson-id"]
        new_id = re.sub(
            rf"^lesson-{old_order}\b",
            f"lesson-{new_order}",
            old_id
        )

        lesson["lesson-order"] = new_order
        lesson["lesson-id"] = new_id
        lesson["title"] = f"Lesson {new_order}"

        old_folder = lessons_root / old_id
        new_folder = lessons_root / new_id

        if old_folder.exists():
            old_folder.rename(new_folder)
            update_folder_contents(new_folder, old_order, new_order)

# ------------------------------------------------------------
# CREATE NEW LESSON
# ------------------------------------------------------------
new_lesson_id = f"lesson-{lesson_number}-new"
new_lesson_folder = lessons_root / new_lesson_id

if new_lesson_folder.exists():
    raise FileExistsError(f"Folder already exists: {new_lesson_folder}")

new_lesson_folder.mkdir(parents=True)

(new_lesson_folder / "content.md").write_text("", encoding="utf-8")

lesson_json = {
    "lesson-id": new_lesson_id,
    "title": f"Lesson {lesson_number}",
    "subtitle": "",
    "lesson-order": lesson_number,
    "key-topics": "",
    "difficulty": ""
}

with open(new_lesson_folder / "lesson.json", "w", encoding="utf-8") as f:
    json.dump(lesson_json, f, indent=4)

lessons.append(lesson_json)

# ------------------------------------------------------------
# SAVE OVERVIEW
# ------------------------------------------------------------
overview["lessons"] = sorted(lessons, key=lambda x: x["lesson-order"])

with open(overview_file, "w", encoding="utf-8") as f:
    json.dump(overview, f, indent=4)

print(f"Inserted new lesson at position {lesson_number}")
