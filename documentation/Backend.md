# Table of contents

**-------- Please Note this Documentation is AI generated --------**

1. Overview
2. Global state & configuration
3. Files & expected lesson structure
4. Database initialization and connections
5. Security rules (SQL validation)
6. Sandbox creation & evaluation flows
7. Key helper functions (snippets + explanation)
8. HTTP endpoints (route list, inputs, outputs, status codes)
9. Data structures & JSON schemas (expected `lesson.json` / `lessons-overview.json` shapes)
10. Quick troubleshooting & debugging tips

---

# 1. Overview

This service provides a lightweight training environment where "lessons" (each with exercises/tasks) run against a pre-seeded SQLite database. Users can preview SELECT queries, submit solutions, run timed attempts, and the backend validates query results either by running read-only SELECTs or by creating a sandbox DB for DML/DDL checks.

Key characteristics:

* Flask app serving JSON endpoints and some static pages.
* Single shared in-memory initialized DB (`DB_INIT_CONN`) containing reference schema & data.
* Per-request sandboxing uses `sqlite3` + `backup()` to copy the "golden" DB into a temporary file for safe mutations.
* Strict protections to prevent unsafe SQL from being executed against the shared DB.
* Lessons are discovered/validated from `/lessons` folder structure.

---

# 2. Global state & configuration

Important module-level globals:

```python
APP_URL = "http://127.0.0.1:8000/"

LESSON_ROOT = Path(__file__).resolve().parent / "lessons"
INIT_SQL_PATH = Path(__file__).resolve().parent / "lessons"/ "database.sql"
_db_initialized = False

# In-memory session variables
COMPLETED_LESSONS = set()
COMPLETED_TASKS = set()

DATABASE_TABLES = []
LESSON_LIST = []
TASKS_LIST = []

CLOCK_START_TIME = None
PREVIOUS_COMPLETION_TIMES = []

# limits
PREVIEW_ROW_LIMIT = 200
EVAL_ROW_LIMIT = 500
```

* `DB_INIT_CONN` and `DB_PATH` are set at startup (see `if __name__ == "__main__"` at bottom).
* `COMPLETED_LESSONS` and `COMPLETED_TASKS` drive lesson completion state.
* `CLOCK_START_TIME` and `PREVIOUS_COMPLETION_TIMES` implement a simple timer/attempt tracking.

---

# 3. Files & expected lesson structure

The app expects a `lessons` directory sitting next to the module. Important expected files:

* `lessons/lessons-overview.json` — array of lesson references (contains `lesson-id` and `lesson-order`).
* For each lesson: directory `lessons/<lesson-id>/` contains:

  * `lesson.json` — metadata + tasks.
  * `content.md` — markdown content served via `/lessons/content/<lesson_id>`.
* A `lessons/template-lesson/lesson.json` is required and used to derive required fields.

`detect_and_validate_lessons()` scans `lessons-overview.json`, verifies each lesson directory, validates `lesson.json` against the template (ensures required keys exist), detects duplicate lesson IDs / task IDs, and constructs `LESSON_LIST` and `TASKS_LIST`.

---

# 4. Database initialization and connections

At startup (main block):

```python
DB_PATH = "file:shared_db?mode=memory&cache=shared"
DB_INIT_CONN = sqlite3.connect(DB_PATH, uri=True, check_same_thread=False)

detect_and_validate_lessons()
run_init_sql()
load_database_tables()
```

* `DB_INIT_CONN` is an in-memory shared DB (URI `file:shared_db?mode=memory&cache=shared`) used as the canonical seed DB.
* `run_init_sql()` reads `lessons/database.sql` (if present) and `executescript` into `DB_INIT_CONN`.
* `get_db_connection()` returns `sqlite3.connect(DB_PATH, uri=True)` for transient connections to the same in-memory DB; `.row_factory = sqlite3.Row` is applied by that helper.

`load_database_tables()` queries `sqlite_master` to populate `DATABASE_TABLES` for discovery.

---

# 5. Security rules (SQL validation)

The app enforces strict rules to avoid writes/DDL on the shared DB:

* A compiled regex `FORBIDDEN_SQL_RE` blocks keywords:

```python
FORBIDDEN_SQL_RE = re.compile(
    r'\b(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|ATTACH|DETACH|PRAGMA|REINDEX|VACUUM|REPLACE|TRUNCATE)\b',
    re.IGNORECASE
)
```

* `is_select_only(sql: str)` checks:

  * SQL is not empty.
  * No forbidden keywords via the regex.
  * No multi-statement execution (counts semicolons — allows at most one trailing semicolon).
  * Query begins with `SELECT` or `WITH`.

This function returns `(True, "")` for valid SELECT-only queries or `(False, "message")` for invalid inputs.

`strip_sql_comments()` removes `/* ... */` and `--` comments before validation/execution.

**Important**: these checks are applied to endpoints that accept arbitrary SQL (preview and read-only evaluation). DML evaluations intentionally run in a sandbox DB created via `create_sandbox_db()` (see next).

---

# 6. Sandbox creation & evaluation flows

## create_sandbox_db(row_factory=False)

Creates a **temporary** on-disk SQLite database and copies the entire contents of the canonical in-memory DB into it:

```python
tmpfile = tempfile.NamedTemporaryFile(delete=False)
sandbox_conn = sqlite3.connect(tmpfile.name)
if row_factory:
    sandbox_conn.row_factory = sqlite3.Row
source = DB_INIT_CONN
source.backup(sandbox_conn)
sandbox_conn.commit()
return sandbox_conn, tmpfile.name
```

* Returned tuple: `(connection, tmp_file_path)`
* The temp file is not deleted automatically; callers are responsible for removing it after use.

## Evaluation variants

There are three evaluation flows:

1. **Read-only comparison** (used when task doesn't allow DML nor create-tables)

   * `evaluate_read_only(user_query, verify_query, order_sensitive)`
   * Runs `run_readonly_query()` on both `user_query` and `verify_query` against the shared DB.
   * Compares result sets (either ordering-sensitive or order-insensitive).
   * `run_readonly_query()` automatically appends a `LIMIT` if the query lacks `LIMIT`.

2. **DML execution and verification** (when `allow-dml` is true)

   * `evaluate_dml(user_query, correct_query, verify_query, order_sensitive)`
   * Creates a sandbox DB (`create_sandbox_db(row_factory=True)`), executes `user_query` there.
   * Optionally executes `verify_query` on the same sandbox to capture results after mutation.
   * Separately creates another sandbox and executes `correct_query` to compute expected results.
   * Compares `user_rows` and `expected_rows`.
   * Cleans up sandbox files/connections.

3. **Table creation checks** (when `create-tables` is true)

   * `evaluate_created_table(user_query, correct_query, table_name)`
   * Executes `user_query` in a sandbox,
   * Checks presence/absence of `table_name` in `sqlite_master`.
   * Executes `correct_query` in another sandbox and compares expected table existence.

### Comparison helpers

* `rows_to_tuples(rows)` converts list-of-dicts into list-of-tuples for stable comparisons.
* `normalize_and_sort_rows(rows)` and `remap_rows_to_columns(rows, target_cols)` provide additional normalization utilities to make comparisons order-insensitive and comparable when column order differs.

**Notes on safety**:

* All DML/DDL are executed only in sandboxed temp DB copies that are created by `backup()` from the canonical DB — the real shared DB (`DB_INIT_CONN`) remains read-only at runtime unless `run_init_sql()` or other admin code runs on it.

---

# 7. Key helper functions (snippets + explanation)

### 1. `is_select_only(sql: str)`

Validates SQL is only a SELECT or WITH...SELECT (no writes/DDL, no multiple statements).

```python
def is_select_only(sql: str):
    if not sql or not isinstance(sql, str) or not sql.strip():
        return False, "Empty query."
    s = sql.strip()
    if FORBIDDEN_SQL_RE.search(s):
        return False, "Query contains forbidden statement (writes or DDL are not allowed)."
    sc_count = s.count(';')
    if sc_count > 1:
        return False, "Multiple statements not allowed."
    if sc_count == 1 and not s.rstrip().endswith(';'):
        return False, "Multiple statements not allowed."
    if s.endswith(';'):
        s = s.rstrip()[:-1].strip()
    if not re.match(r'^(WITH\s+|SELECT\s+)', s, re.IGNORECASE):
        return False, "Only SELECT queries are allowed."
    return True, ""
```

### 2. `run_readonly_query(sql: str, row_limit: int = 200)`

Runs a validated SELECT against the shared DB and returns `(columns, rows, error)`.

```python
conn = get_db_connection()
cur = conn.cursor()
# add LIMIT if missing
final_sql = f"{s} LIMIT {row_limit}" if 'LIMIT' not in s (case-insensitive) else s
cur.execute(final_sql)
col_order = [desc[0] for desc in cur.description]
rows_raw = cur.fetchall()
# convert sqlite types to JSON-friendly values
rows = [...]
return col_order, rows, None
```

### 3. `create_sandbox_db(row_factory=False)`

Creates a temp file database and copies the canonical DB using `backup()`.

```python
tmpfile = tempfile.NamedTemporaryFile(delete=False)
sandbox_conn = sqlite3.connect(tmpfile.name)
if row_factory:
    sandbox_conn.row_factory = sqlite3.Row
source = DB_INIT_CONN
source.backup(sandbox_conn)
sandbox_conn.commit()
return sandbox_conn, tmpfile.name
```

### 4. `strip_sql_comments(sql: str)`

Removes `/* ... */` and `--` comments (multi-line and single-line) before validation.

```python
sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
sql = re.sub(r"--.*?$", "", sql, flags=re.MULTILINE)
return sql.strip()
```

### 5. `dict_rows(cursor)` and `replace_nulls(obj)`

Utilities to convert DB rows to dicts and normalize `None` to empty string for safe frontend JSON usage.

---

# 8. HTTP Endpoints

Below is an ordered list of server routes with method, path, purpose, input (JSON path when applicable), and example outputs/status codes.

## Lesson listing & previewing

* `GET /lessons`
  Returns all lessons with `title`, `subtitle`, `order`, and `completed` flag.

  Response: `200 OK`

  ```json
  {
    "lesson-1": {
      "title": "Lesson 1",
      "subtitle": "SELECT queries 101",
      "order": 1,
      "completed": false
    },
    ...
  }
  ```

* `GET /lessons/details/<lesson_id>`
  Returns full lesson metadata including `exercise-tasks` where each task includes `completed` flag.

  Response: `200 OK` or `404`

* `GET /lessons/content/<lesson_id>`
  Returns raw lesson `content.md` (as text).
  Response: `200 OK` (text) or `404 / 500`

* `GET /lessons/next_lesson/<lesson_id>/<direction>`
  `direction` must be `previous` or `next`. Returns the `next_lesson_id` and `current_lesson_id`.
  Response: `200 OK`, or `400` for invalid direction, `404` for missing lesson.

* `GET /lessons/complete/<lesson_id>`
  Marks the lesson complete if *all* tasks for that lesson are in `COMPLETED_TASKS`.

  * Success: `200 {"status":"success"}`
  * Failure: `400` with message (if not all tasks completed)

## Query preview & submission

* `POST /lessons/preview/<lesson_id>/<float:task_id>`
  Body: `{ "query": "SELECT ..." }`
  Purpose: preview results for SELECT statement (debounced typing). Requires `task["preview-allowed"]` to be true.
  Validates: removes comments, runs `is_select_only()`.
  Response: `200 {"results": {"columns": [...], "rows":[...]}}` or `400/403` with error message.

* `POST /lessons/evaluate/<lesson_id>/<float:task_id>`
  Body: `{ "query": "..." }`
  Purpose: Evaluate a submission. Flow:

  1. Loads task metadata: `verify-query`, flags `allow-dml`, `create-tables`, `order-sensitive`.
  2. Calls the appropriate evaluation function (read-only, DML compare, or created-table check).
  3. On success marks `COMPLETED_TASKS.add(task_id)` and returns result.

  Response: `200`:

  ```json
  {
    "lessonId": "lesson-1",
    "taskNumber": 1.0,
    "userError": null,
    "resultsMatch": true
  }
  ```

  Errors: `400` for missing `query`, invalid task id, invalid SQL; `500` for internal errors.

* `GET /lessons/answer/<lesson_id>/<float:task_id>`
  Returns the correct answer SQL (`task["correct-query"]`) unless the countdown timer is active.

  * `403` if `CLOCK_START_TIME` is set (answers forbidden during active timer).
  * `404` if invalid task id.

## Timer and session management

* `GET /reset_session`
  Clears `COMPLETED_LESSONS`, `COMPLETED_TASKS`, resets `CLOCK_START_TIME` and `PREVIOUS_COMPLETION_TIMES`, and re-runs `run_init_sql()`.

  Response: `200 {"status":"reset"}`

* `GET /timer/start`
  Sets `CLOCK_START_TIME = datetime.now()`, clears completed state and returns the start datetime as ISO string.

  Response: `200 {"started": "2025-12-12T13:29:..."}`

* `GET /timer/cancel_attempt`
  Cancels the current attempt by setting `CLOCK_START_TIME = None`.

  Response: `200 {"message": "timer cancelled"}`

* `GET /timer/submit`
  If all lessons completed (every `LESSON_LIST` element in `COMPLETED_LESSONS`), records the elapsed time since start into `PREVIOUS_COMPLETION_TIMES` and resets the timer. Otherwise returns outstanding lessons and `400`.

* `GET /timer/value`
  Returns `timer_status` ("active"/"inactive") and `start_time` ISO string.

* `GET /timer/attempts`
  Returns number of attempts and `best_attempt` & `last_attempt` formatted `HH:MM:SS`.

## Database table endpoints

* `GET /tables/<table_name>`
  Returns rows and columns via `run_readonly_query` for the given table. 404 if not found.

* `GET /tables/meta/<table_name>`
  Returns `{"name": table_name, "columns": [ ... ]}`.

## Static routes

* `GET /` — serves `static/index.html`
* `GET /lesson/<lesson_id>` — serves a view `static/views/lesson.html`

---

# 9. Data structures & JSON schemas

The code expects consistent shapes for lesson metadata. Based on code usage, the important fields are:

## `lessons-overview.json` (expected top-level shape)

```json
{
  "lessons": [
    { "lesson-id": "lesson-1-basic-select", "lesson-order": 1 },
    { "lesson-id": "lesson-2-joins", "lesson-order": 2 }
  ]
}
```

`detect_and_validate_lessons()` expects `lessons-overview.json["lessons"]` to be iterable and each entry to have `lesson-id` and `lesson-order`.

## `lesson.json` (per-lesson)

The exact required fields are taken from the `template-lesson/lesson.json`. From how the code reads the lesson objects, the following fields are used and expected:

Top-level:

```json
{
  "lesson-id": "lesson-1-basic-select",
  "title": "Lesson 1",
  "subtitle": "SELECT queries 101",
  "lesson-order": 1,
  "database-tables": ["table1", "..."],
  "exercise-tasks": [ ... ]
}
```

Each task in `exercise-tasks` must include (inferred from code usage):

* `task-id` (unique across all lessons)
* `exercise-order` (unique within lesson)
* `preview-allowed` (bool)
* `verify-query` (SQL used to verify results)
* `allow-dml` (bool) — if true, run DML flow
* `create-tables` (bool) — if true, evaluate table create/drop
* `order-sensitive` (bool) — whether result order matters
* `correct-query` (answer SQL)

Example task:

```json
{
    "task-id": 1.1,
    "description": "Find the name of each country",
    "correct-query": "SELECT Name FROM Countries",
    "verify-query": "SELECT Name FROM Countries",
    "order-sensitive": false,
    "exercise-order": 1,
    "initial-query": "SELECT * FROM Countries",
    "large-query": false,
    "allow-dml": false,
    "create-tables": false,
    "preview-allowed": true
},
```

**Important**: `detect_and_validate_lessons()` uses `template_lesson_json["exercise-tasks"][0].keys()` to derive required task fields. Ensure the template has the canonical keys.

---
# 10. Quick troubleshooting & debugging tips

* **If lessons are not loaded**: Check `lessons/lessons-overview.json` and the presence of `lessons/template-lesson/lesson.json`. The startup routine will raise `ImportError("No template lesson folder is included")` if the template is missing.
* **If DB tables list empty**: Verify that `lessons/database.sql` exists and is syntactically valid; `run_init_sql()` prints exceptions on failure.
* **If preview returns 500 / nothing**: Confirm `preview-allowed` exists and ensure the `preview_query()` returns the `jsonify(...), 403` response rather than only calling `jsonify`.
* **If temp files persist**: Look at the sandbox creation code paths; ensure `os.remove(tmpdb)` is executed in every `finally` and that exceptions don't bypass cleanup.
* Use logging (e.g., `app.logger.debug(...)`) to trace evaluation flows and SQL executed in sandboxes.

---
