# SQL Training App

This repository provides a full-stack **Flask web application** for interactive SQL training, packaged as a single executable file.
It aims to go beyond publicly available SQL tools that often only cover basic concepts, offering advanced topics like **CTEs, Window Functions, Nested Queries, and Recursive CTEs**.

## Key Features

* **Interactive SQL Execution:** Run and preview SQL queries live in your browser for hands-on learning.
* **Gamified Learning:** Track lesson completion and measure progress with a built-in timer.
* **Guided Answers:** Access answers for all exercises and redirect to ChatGPT for detailed explanations with pre-built prompts.
* **Scalable Lessons:** Easily add new lessons by creating folders in the `/lessons` directory. All lessons are validated at startup to ensure consistency.

## Technical Overview

* **Backend:** Flask handles routing, lesson tracking, API endpoints, and SQL execution.
* **Database:** SQLite is used for executing queries and validating results against correct answers defined in `lesson.json` files.
* **Frontend:** HTML, CSS, and JavaScript dynamically render lessons and provide an interactive user experience.

## Project Structure

```
/dist
    └── SQL Training App executable file (.exe)
/documentation
    └── Detailed technical documentation for frontend, backend, and build processes
/lessons
    └── Lesson data in JSON and Markdown formats
    └── database.sql          # Defines initial database structure
    └── lesson-template-prompt.txt # Template for creating new lessons
    └── lessons-overview.json # Source-of-truth for all lesson definitions
/static
    └── Frontend assets (JS, CSS, images)
/utils
    └── Python utility functions for working with lesson JSON files
```

## Running the App

1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```
2. Navigate to the `dist` folder and run the executable:
   ```bash
   ./SQL_Training_App.exe
   ```
3. Your browswer will automatically open a tab displaying the app.

---

## Updating the App

1. Clone or pull the latest version of the repository.
2. If adding new lessons:
   * Create a new folder in `/lessons` using the insert_new_lesson.py file in utils/create_or_delete_lesson.
   * Navigate to /lessons and ensure the lesson.json file in the new lesson folder contains all fields defined in the lessons/template-lesson/lesson.json file. 
   * Run the app.py file locally to confirm all lessons are validated (see terminal for error messages)
3. If removing a lesson:
   * Run the archive_lesson.py file in utils/create_or_delete_lesson.
   * Run the app.py file locally to confirm all lessons are validated (see terminal for error messages)
4. Rebuild the executable following the build instructions in `/documentation`.

