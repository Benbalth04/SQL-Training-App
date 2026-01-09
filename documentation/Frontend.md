# Front-End Documentation

**-------- Please Note this Documentation is AI generated --------**

## Front-End Folder Structure

```
static/
│
├── index.html            # Home Page (lists all lessons and links to them. This is the entry point for the app)
│
├── views/
│   └── lesson.html      # Main lesson interface and UI layout
│
├── styles/
│   └── ...               # CSS theme, layout, animations
│
├── assets/
│   └── ...               # Icons, images, branding files
│
└── scripts/
    ├── lesson.js         # Main interactive lesson engine (dynamically loads lesson content using lesson-id in the URL)
    ├── timer.js          # Handles all timer widget logic
    └── index.js          # Additional JS utilities
```

---

# Overview of the Front-End Application

The front-end is an interactive environment that:

* Loads a selected lesson and renders its Markdown content
* Displays task lists, expected tables, and user progress
* Provides a live Monaco SQL editor with autocompletion
* Executes user-written SQL queries in real time (preview mode)
* Submits final task answers for backend validation
* Handles task switching, state updates, and UI transitions

---

# Key JavaScript Components

## 1. Global State

`lesson.js` uses global variables to track the state of the lesson UI:

| Variable               | Purpose                                         |
| ---------------------- | ----------------------------------------------- |
| `lesson`               | Full lesson metadata loaded from backend        |
| `currentTaskNumber`    | 1+Index of active task in the lesson["exercise-tasks] list      |
| `editor`               | Monaco editor instance                          |
| `resultsTable`         | Latest preview results table                    |
| `debounceTimer`        | Prevents excessive live-query requests          |
| `sqlContext`           | Table + column metadata used for autocompletion |
| `popupTimeout`         | Timer for popup notifications                   |
| `isUpdatingLessonMenu` | Prevents duplicate lesson menu refresh calls    |

---

# 2. Initialisation Flow

On `DOMContentLoaded`, the app:

1. Extracts `lesson-id` from URL
2. Initialises Monaco editor
3. Fetches lesson metadata and Markdown content
4. Renders task list
5. Loads source database tables
6. Sets up dropdown menu
7. Updates lesson menu
8. Enables or disables the “Next Lesson” button based on task completion

---

# 3. Lesson & Markdown Loading

### `loadLesson(lessonId)`

* Fetches lesson metadata (`title`, `tasks`, `tables`)
* Renders the task list

### `loadLessonMarkdown(lessonId)`

* Fetches Markdown
* Converts to HTML using **marked**
* Syntax-highlights SQL using **highlight.js**
* Styles markdown tables
* Auto-tag SQL blocks based on keyword detection

---

# 4. Lesson Menu (Sidebar)

### `setupMenuToggle()`

* Handles slide-open/close for the left navigation menu

### `updateLessonMenu()`

* Fetches list of all lessons
* Renders them in sorted order
* Marks completed lessons with ✓
* Highlights current lesson
* Uses a lock (`isUpdatingLessonMenu`) to prevent double refresh

---

# 5. Task List Management

### `renderTaskList()`

* Builds clickable list of exercise tasks
* Automatically selects first incomplete task
* Preloads initial SQL into editor
* Triggers live preview and table rendering
* Supports “completed” UI state

### `switchTask(currentTaskNumber, nextTaskNumber, completeTask)`

* Visually switches tasks
* Updates Monaco with new starter SQL
* Refreshes SQL context
* Re-runs preview mode
* Updates menu and UI state

---

# 6. Answer Reveal System

### `revealTaskAnswer()`

* Fetches correct SQL answer from backend (if allowed)
* **Note that this is blocked when the timer is active**

### `showAnswerPopup() / closeAnswerPopup()`

* Displays model answer with syntax highlighting
* Handles error scenarios (e.g., timer active)

---

# 7. Monaco Editor

### `initMonaco()`

Initialises the Monaco editor:

* SQL syntax + theme
* Auto layout
* `Ctrl + Enter` submission
* Debounced `onDidChangeModelContent` triggers for live preview
* Registers SQL autocompletion provider using `sqlContext`

### SQL Autocomplete Logic

`sqlContext.tables` shape:

```js
{
  "table_name": ["col1", "col2", ...],
  ...
}
```

Autocomplete supports:

* Table suggestions after `FROM`, `JOIN`, `UPDATE`, `INTO`
* Column suggestions after `tableName.`
* Global column suggestions when ambiguous

### `updateSqlContextForTask(task)`

* Fetches metadata for tables relevant to the active task
* Refreshes autocomplete

---

# 8. Live SQL Preview

### `runLiveQuery(initial_load=false)`

* Sends editor SQL to `/lessons/preview/...`
* Renders result table
* Automatically disabled for tasks where preview is not permitted
* Presents popup messages on SQL errors

Debounced to avoid rapid backend calls.

---

# 9. SQL Submission & Task Completion

### `submitSQL()`

Full evaluation flow:

1. Sends SQL to backend
2. Checks whether user results match the expected answer
3. Shows success/error popup
4. Marks task completed
5. Finds next incomplete task
6. Marks lesson completed if appropriate
7. Refreshes lesson menu and “Next Lesson” button

### `markTaskComplete(taskNumber)`

Updates UI visual state + lesson object.

### `handleNextLessonButton()`

Enables navigation to:

* Next lesson
* Home (if all lessons complete)
* List of incomplete lessons

---

# 10. Data Table Rendering

### `updateDataTable(resultObj)`

Renders live preview results:

* Preserves backend’s column order
* Builds table `<thead>` and `<tbody>`
* Displays friendly “No results” message

### Source Table Rendering

`renderSourceTables()` + `updateSourceTable()`

Displays read-only tables used by the lesson:

* One block per table
* Auto-fetches table contents from backend
* Reuses table creation logic

---

# Summary

`lesson.js` is the **core engine** of the front-end SQL training experience.
It synchronizes:

* Lesson metadata
* Task progression
* Live SQL preview
* Monaco editor integration
* Answer validation
* UI transitions and navigation

Its design ensures a **smooth, fully interactive SQL learning environment** tightly integrated with your backend.

