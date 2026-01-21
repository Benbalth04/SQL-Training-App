import json
import shutil
from pathlib import Path
import re


# ---------- Update before running ---------
lesson_number_to_archive = 7  # e.g. 7
# ------------------------------------------

if not isinstance(lesson_number_to_archive, int) or lesson_number_to_archive <= 0:
    raise ValueError(f"Invalid lesson number: {lesson_number_to_archive}")

# Current directory of this script
current_dir = Path(__file__).resolve().parent

lessons_root = current_dir.parent.parent / "lessons"
archive_folder = lessons_root / "lessons-archive"
lesson_overview_file = lessons_root / "lessons-overview.json"

archive_folder.mkdir(parents=True, exist_ok=True)

# LOAD LESSON OVERVIEW
with open(lesson_overview_file, "r", encoding="utf-8") as f:
    overview = json.load(f)

lessons = overview.get("lessons", [])

# FIND TARGET LESSON
target_lesson = next(
    (l for l in lessons if l["lesson-order"] == lesson_number_to_archive),
    None
)

if not target_lesson:
    raise FileNotFoundError(f"Could not find lesson number {lesson_number_to_archive}")

target_lesson_id = target_lesson["lesson-id"]
target_lesson_folder = lessons_root / target_lesson_id

if not target_lesson_folder.exists():
    raise FileNotFoundError(f"Lesson folder not found: {target_lesson_folder}")

# ARCHIVE THE LESSON FOLDER
archive_destination = archive_folder / target_lesson_id

if archive_destination.exists():
    raise FileExistsError(f"Archive destination already exists: {archive_destination}")

shutil.copytree(target_lesson_folder, archive_destination)
shutil.rmtree(target_lesson_folder)

# REMOVE TARGET LESSON FROM OVERVIEW
lessons.remove(target_lesson)

# SHIFT FUTURE LESSONS DOWN
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


for lesson in lessons:
    old_order = lesson["lesson-order"]

    if old_order > lesson_number_to_archive:
        new_order = old_order - 1

        old_id = lesson["lesson-id"]
        new_id = re.sub(
            rf"^lesson-{old_order}\b",
            f"lesson-{new_order}",
            old_id
        )

        # Update overview fields
        lesson["lesson-order"] = new_order
        lesson["lesson-id"] = new_id
        lesson["title"] = f"Lesson {new_order}"

        # Rename folder
        old_folder = lessons_root / old_id
        new_folder = lessons_root / new_id

        if old_folder.exists():
            old_folder.rename(new_folder)
            update_folder_contents(new_folder, old_order, new_order)

# SORT & SAVE OVERVIEW
overview["lessons"] = sorted(lessons, key=lambda x: x["lesson-order"])

with open(lesson_overview_file, "w", encoding="utf-8") as f:
    json.dump(overview, f, indent=4)

print(f"Lesson {lesson_number_to_archive} archived successfully.")
