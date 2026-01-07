"""
Backend API for the internal SQL training platform.

This app exposes endpoints for:
- Loading lesson metadata and tasks
- Executing and validating user SQL submissions in a safe, sandboxed SQLite environment
- Comparing user results against expected outputs using temporary tables
- Returning structured feedback, errors, and execution results
- Supporting lesson progression, state management, and interactive editor features

Key Data Structures: 
    - DATABASE_TABLES: list of all the database tables that exists in the in-memory db after the database.sql file is run
    - LESSONS_LIST: list of lesson-ids that were successfully validated during the initialisation process
    - TASKS_LIST: list of task-ids that are contained in the validated lessons
    - COMPLETED_LESSONS: set of all lesson-ids that have been completed (all tasks for that lesson were correctly answered)
    - COMPLETED_TASKS: set of all task-ids that have been completed 

Initial Lessons Validation 
    - Potenital lessons are listed in the lessons-overview.json file 
    - For each lesson-id in the lessons-overview file:
        - Check that all required fields (as outlined in the \lessons\template-lesson\lesson.json) exist in the \lessons\{lesson-id}\lesson.json file
        - If validated, add the lesson-id to the LESSONS_LIST, and the task-ids to the TASKS_LIST
"""

import json
import re
import webbrowser
import sqlite3
import requests
import tempfile
import os
import concurrent.futures
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify, abort, send_from_directory

app = Flask(__name__, static_folder="static", static_url_path="/static")
APP_URL = "http://127.0.0.1:8000/"

LESSON_ROOT = Path(__file__).resolve().parent / "lessons"
INIT_SQL_PATH = Path(__file__).resolve().parent/ "lessons"/ "database.sql"
_db_initialized = False

# -------------------------------------
# Session variables
# -------------------------------------
COMPLETED_LESSONS = set()
COMPLETED_TASKS = set()

DATABASE_TABLES = []
LESSON_LIST = []
TASKS_LIST = []

CLOCK_START_TIME = None
PREVIOUS_COMPLETION_TIMES = []

# -------------------------------------
# Config / constants
# -------------------------------------
PREVIEW_ROW_LIMIT = 200
EVAL_ROW_LIMIT = 500
QUERY_TIMEOUT = 10 

# Forbidden read-only statements (writes, DDL, admin)
FORBIDDEN_SQL_RE = re.compile(
    r'\b(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|ATTACH|DETACH|PRAGMA|REINDEX|VACUUM|REPLACE|TRUNCATE)\b',
    re.IGNORECASE
)

# -------------------------------------
# Setup
# -------------------------------------
def detect_and_validate_lessons():
    """
    Parses the lessons directory and populates the LESSONS and TASKS lists with lessons and tasks which have passed the validity checks
    The order of checks are: 
        - Check the template-lesson.json exists 
        - Check the lessons-overview.json exists
        - For each folder in the lessons directory (that is not the template lesson folder)
            - Check no duplicate lesson-ids, or task-ids exist
            - Check lesson.json and content.md files are in the folder
            - Check all fields in the template.json file are in the lesson.json file 
    
    """
    global LESSON_LIST, TASKS_LIST
    LESSON_LIST = []
    TASKS_LIST = []

    detected_lessons = set()
    detected_tasks = set()
    tmp_lessons = {}

    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RESET = '\033[0m'

    # -----------------------------------------
    # Load the template lesson
    # -----------------------------------------
    template_lesson_json = None
    for folder in LESSON_ROOT.iterdir():
        if folder.is_dir() and folder.name == "template-lesson":
            lesson_json_path = folder / "lesson.json"
            with open(lesson_json_path, "r", encoding="utf-8") as f:
                template_lesson_json = json.load(f)
            break

    if template_lesson_json is None:
        raise ImportError("No template lesson folder is included")

    required_fields = template_lesson_json.keys()
    required_task_fields = template_lesson_json["exercise-tasks"][0].keys()

    # -----------------------------------------
    # Load the lessons overview
    # -----------------------------------------
    lesson_overview_path = LESSON_ROOT / "lessons-overview.json"
    with open(lesson_overview_path, "r", encoding="utf-8") as lesson_overview_file:
        lesson_overview_json = json.load(lesson_overview_file)

    # -----------------------------------------
    # Validate all lessons
    # -----------------------------------------
    for lesson in lesson_overview_json["lessons"]:
        folder = LESSON_ROOT / lesson.get("lesson-id")

        # Duplicate lesson detection
        lesson_id = lesson.get("lesson-id")
        if lesson_id in detected_lessons:
            raise ImportError(f"Duplicate lesson ids found: {lesson_id}")
        detected_lessons.add(lesson_id)

        if not folder.is_dir():
            print(f"{RED}{lesson.get('lesson-id')} skipped: no folder exists in the lessons directory{RESET}")
            continue
        
        # Markdown file exists
        lesson_markdown_path = folder / "content.md"
        if not lesson_markdown_path.exists():
            print(f"{RED}{folder} skipped: missing content.md{RESET}")
            continue

        # lesson.json exists
        lesson_json_path = folder / "lesson.json"
        if not lesson_json_path.exists():
            print(f"{RED}{folder} skipped: missing lesson.json{RESET}")
            continue

        with open(lesson_json_path, "r", encoding="utf-8") as f:
            lesson_json = json.load(f)

        missing_field = False

        # Check required lesson fields
        for field in required_fields:
            if lesson_json.get(field) is None:
                print(f"{RED}{folder} skipped: missing '{field}' in lesson.json{RESET}")
                missing_field = True

        exercise_order = set()
        # Validate tasks
        for index, task in enumerate(lesson_json.get("exercise-tasks", [])):
            task_id = task.get("task-id")

            # Duplicate task check
            if task_id in detected_tasks:
                raise ImportError(f"Duplicate task ids found: {task_id}")
            detected_tasks.add(task_id)

            # Check required task fields
            for task_field in required_task_fields:
                if task.get(task_field) is None:
                    print(
                        f"{RED}{folder} skipped: missing task field '{task_field}' "
                        f"in task #{index}{RESET}"
                    )
                    missing_field = True

            if task.get("exercise-order") in exercise_order:
                print(
                        f"{RED}{folder} skipped: duplicate exercise-order field '{task.get("exercise-order")}' "
                        f"in task #{index}{RESET}"
                    )
                missing_field = True
            else:
                exercise_order.add(task.get("exercise-order"))


        if missing_field:
            continue

        # Valid lesson
        tmp_lessons[lesson_id] = {
            "order": lesson["lesson-order"],
            "lesson": lesson_id
        }

        print(f"{GREEN}Validated lesson: {lesson_id}{RESET}")

    # -----------------------------------------
    # Final ordering
    # -----------------------------------------
    sorted_lessons = sorted(tmp_lessons.values(), key=lambda item: item["order"])
    LESSON_LIST = [entry["lesson"] for entry in sorted_lessons]
    TASKS_LIST = list(detected_tasks)

    print(f"{YELLOW}Loaded {len(LESSON_LIST)} lessons successfully.{RESET}")

def run_init_sql():
    """
    Initializes the SQLite in-memory DB using the SQL startup script (INIT_SQL_PATH)
    Sets the global _db_initialised boolean flag to true to ensure database is only initialsed once.
    """
    global _db_initialized
    if _db_initialized:
        return
    _db_initialized = True

    if not INIT_SQL_PATH.exists():
        print("init.sql not found. Skipping database initialization.")
        return

    sql_script = INIT_SQL_PATH.read_text()

    try:
        cursor = DB_INIT_CONN.cursor()
        cursor.executescript(sql_script)
        DB_INIT_CONN.commit()
        print("SQLite in-memory database initialized successfully.")
    except Exception as e:
        print("Error running init.sql:", e)

def load_database_tables():
    """
    Detects all user-defined tables in the SQLite DB and populates DATABASE_TABLES list.
    """
    global DATABASE_TABLES
    try:
        cur = DB_INIT_CONN.cursor()
        cur.execute("""
            SELECT name 
            FROM sqlite_master 
            WHERE type='table' 
            ORDER BY name;
        """)
        tables = [row[0] for row in cur.fetchall()]
        if 'sqlite_sequence' in tables:
            tables.remove('sqlite_sequence')
        DATABASE_TABLES = tables
        return tables
    except Exception as e:
        print("Error loading tables:", e)
        DATABASE_TABLES = []
        return []

def check_if_running(url=APP_URL):
    """
    Makes a request to the APP_URL to determine if the app is already running 
    Returns True if app responds, False otherwise.
    """
    try:
        r = requests.get(url, timeout=0.5)
        return r.status_code == 200
    except requests.RequestException:
        return False

def get_db_connection():
    """
    Creates a database connection 
    Ensures the connection using row factory, which converts result tuples into more useful objects.
    """
    conn = sqlite3.connect(DB_PATH, uri=True)
    conn.row_factory = sqlite3.Row
    return conn

def create_sandbox_db(row_factory=False):
    """
    Creates a temporary sandbox SQLite DB file and copies 
    the entire schema + data from the main in-memory DB.
    Returns: (connection, temp_file_path)
    """
    # Create temp file for the sandbox database
    tmpfile = tempfile.NamedTemporaryFile(delete=False)
    tmpfile.close()  # SQLite requires the file to exist but not be open

    # Create connection to sandbox DB
    sandbox_conn = sqlite3.connect(tmpfile.name)

    # Enable row-as-dict mode if requested
    if row_factory:
        sandbox_conn.row_factory = sqlite3.Row

    # Copy schema + data from the main initialized DB
    source = DB_INIT_CONN
    source.backup(sandbox_conn)
    sandbox_conn.commit()

    return sandbox_conn, tmpfile.name

# -------------------------------------
# Helpers
# -------------------------------------
# ------------- Lesson details -------------
def http_error(status, message):
    abort(status, description=message)

def load_lesson(lesson_id: str):
    """Load lesson folder + JSON definition."""
    if lesson_id not in LESSON_LIST:
        http_error(404, "Lesson not found")

    lesson_dir = LESSON_ROOT / lesson_id
    if not lesson_dir.exists():
        http_error(404, "Lesson not found")

    lesson_json_path = lesson_dir / "lesson.json"
    if not lesson_json_path.exists():
        http_error(500, "lesson.json missing")

    with open(lesson_json_path, "r") as f:
        lesson = json.load(f)

    return lesson, lesson_dir

def load_lesson_markdown(lesson_id: str):
    """
    Returns the content of a lesson's content.md file 
    """
    lesson_dir = LESSON_ROOT / lesson_id
    if not lesson_dir.exists():
        http_error(404, "Lesson not found")

    md_path = lesson_dir / "content.md"
    if not md_path.exists():
        http_error(500, "content.md missing")

    try:
        with open(md_path, "r", encoding="utf-8") as f:
            markdown = f.read()
    except Exception as e:
        http_error(500, f"Failed to read content.md: {e}")

    return markdown, lesson_dir

def get_lesson_difficulty(lesson_id: str): 
    if lesson_id not in LESSON_LIST:
        http_error(404, "Lesson not found")

    lesson_overview_json_path = LESSON_ROOT / "lessons-overview.json"
    if not lesson_overview_json_path.exists():
        http_error(404, "Lesson not found")

    lesson_overview = None
    with open(lesson_overview_json_path, "r") as f:
        lesson_overview = json.load(f)

    if not lesson_overview:
        return "Unable to find"
    
    lessons_list = lesson_overview.get("lessons") 
    for lesson in lessons_list: 
        if lesson.get("lesson-id") == lesson_id:
            return lesson.get("difficulty")
        
    return ""

# ------------- Database reads/writes -------------
def read_db_table(table_name: str):
    """
    Reads a database table and returns all rows as a JSON-serializable list of dicts.
    """
    if table_name not in DATABASE_TABLES:
        return {"status": 404, "error": f"Invalid table name: {table_name}"}

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = f"SELECT * FROM {table_name}"
        rows = cursor.execute(query).fetchall()

        results = []
        for row in rows:
            converted = {}
            for key, value in dict(row).items():
                converted[key] = "NULL" if value is None else value
            results.append(converted)

        return results

    except Exception as e:
        return {"error": str(e)}

def execute_with_timeout(func, *args, timeout=QUERY_TIMEOUT, **kwargs):
    """Run any function in a separate thread with a hard timeout."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            raise TimeoutError(f"Query exceeded {timeout} seconds limit")

def get_db_table_columns(table_name: str):
    """
    Returns a list of the columns in a database table
    """
    if table_name not in DATABASE_TABLES:
        return {"status": 404, "error": f"Invalid table name: {table_name}"}

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(f"PRAGMA table_info({table_name})")
        rows = cur.fetchall()

        if not rows:
            return {"status": 404, "error": f"Table not found or has no columns: {table_name}"}

        columns = [row[1] for row in rows]  # 'name' column

        return columns

    except Exception as e:
        return {"status": 500, "error": str(e)}

def is_select_only(sql: str):
    """
    Validate SQL is a single SELECT (or WITH ... SELECT), no writes/DDL, and no multiple statements.
    Returns (True, "") on ok, otherwise (False, message).
    """
    if not sql or not isinstance(sql, str) or not sql.strip():
        return False, "Empty query."

    s = sql.strip()

    # Quick reject forbidden keywords
    if FORBIDDEN_SQL_RE.search(s):
        return False, "Query contains forbidden statement (writes or DDL are not allowed)."

    # Disallow multiple statements: allow single trailing semicolon only
    # Count semicolons; if >1 reject. If 1, ensure it's trailing.
    sc_count = s.count(';')
    if sc_count > 1:
        return False, "Multiple statements not allowed."
    if sc_count == 1 and not s.rstrip().endswith(';'):
        return False, "Multiple statements not allowed."

    # Remove trailing semicolon for further checks
    if s.endswith(';'):
        s = s.rstrip()[:-1].strip()

    # Ensure it starts with SELECT or WITH
    if not re.match(r'^(WITH\s+|SELECT\s+)', s, re.IGNORECASE):
        return False, "Only SELECT queries are allowed."

    return True, ""

def run_readonly_query(sql: str, row_limit: int = 200):
    """
    Executes a validated SELECT query safely and returns
    ({ "columns": [...], "rows": [...] }, error_msg).
    Uses the shared in-memory DB connection.
    """
    try:
        s = sql.strip()
        if s.endswith(';'):
            s = s[:-1].strip()

        # Add LIMIT if missing
        if not re.search(r'\bLIMIT\b', s, re.IGNORECASE):
            final_sql = f"{s} LIMIT {row_limit}"
        else:
            final_sql = s

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(final_sql)

        col_order = [desc[0] for desc in cur.description]

        rows_raw = cur.fetchall()
        rows = []

        for row in rows_raw:
            row_dict = {}
            for col in col_order:
                val = row[col]
                row_dict[col] = "NULL" if val is None else val
            rows.append(row_dict)

        return col_order, rows, None

    except Exception as e:
        print(e)
        return None, None, str(e)

def safe_run_readonly(sql: str, row_limit=200):
    """Run a SELECT / read-only query safely with timeout."""
    return execute_with_timeout(run_readonly_query, sql, row_limit=row_limit)

def normalize_and_sort_rows(rows):
    """
    Normalize rows: convert each row dict to tuple of values in column order provided by row.keys().
    Return (columns_tuple, sorted_rows_tuple_of_tuples). Sorting uses stringification fallback.
    """
    if not rows:
        return (), tuple()

    cols = tuple(rows[0].keys())

    def convert_value(v):
        if isinstance(v, (bytes, bytearray)):
            return v.hex()
        return v

    tuple_rows = []
    for r in rows:
        tuple_rows.append(tuple(convert_value(r.get(c)) for c in cols))

    try:
        sorted_rows = tuple(sorted(tuple_rows))
    except TypeError:
        sorted_rows = tuple(sorted(tuple_rows, key=lambda t: tuple(str(x) for x in t)))

    return cols, sorted_rows

def remap_rows_to_columns(rows, target_cols):
    """
    Given rows as list[dict], and target_cols (iterable of column names),
    return sorted tuple of tuples where each inner tuple contains values in target_cols order.
    """
    if not rows:
        return tuple()
    mapped = []
    for r in rows:
        mapped.append(tuple(r.get(c) for c in target_cols))
    try:
        return tuple(sorted(mapped))
    except TypeError:
        return tuple(sorted(mapped, key=lambda t: tuple(str(x) for x in t)))

def format_timedelta(td):
    total_seconds = int(td.total_seconds())
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return f"{h:02}:{m:02}:{s:02}"

def strip_sql_comments(sql: str) -> str:
    """
    Removes any comments from an SQL query string
    """
    if not sql:
        return sql

    # Remove /* multi-line */ comments
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)

    # Remove -- single-line comments
    sql = re.sub(r"--.*?$", "", sql, flags=re.MULTILINE)

    # Strip whitespace
    return sql.strip()

def dict_rows(cursor):
    """Convert sqlite3.Row rows into plain dicts."""
    cols = [d[0] for d in cursor.description]
    return [{col: row[col] for col in cols} for row in cursor.fetchall()]

def replace_nulls(obj):
    """Recursively convert None → '' for safe frontend use."""
    if isinstance(obj, dict):
        return {k: replace_nulls(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [replace_nulls(v) for v in obj]
    if obj is None:
        return ""
    return obj

def rows_to_tuples(rows):
    """Convert dict → tuple(values) (column names ignored)."""
    return [tuple(row.values()) for row in rows]

def evaluate_read_only(user_query: str, verify_query: str, order_sensitive: bool) -> tuple[bool, str]:
    """
    Executes a read-only user query and compares it against the verification query.
    Returns (results_match, user_error). If no error occurs, user_error will be None
    """
    user_err = None
    try:
        _, user_rows, user_err = safe_run_readonly(user_query)
        if user_err:
            return False, user_err

        _, expected_rows, expected_err = safe_run_readonly(verify_query)
        if expected_err:
            return False, f"Internal error in verification query: {expected_err}"

        user_tuples = rows_to_tuples(user_rows)
        expected_tuples = rows_to_tuples(expected_rows)

        if order_sensitive:
            results_match = (user_tuples == expected_tuples)
        else:
            results_match = (sorted(user_tuples) == sorted(expected_tuples))

        return results_match, None

    except Exception as e:
        return False, str(e)

def evaluate_dml(user_query: str, correct_query: str, verify_query: str, order_sensitive: bool) -> tuple[bool, str]:
    """
    Executes a user DML query in a sandbox DB and compares the result against the correct query.
    Returns (results_match, user_error). If no error occurs, user_error will be None
    """
    user_rows = []
    expected_rows = []
    user_err = None
    results_match = False

    conn, tmpdb = create_sandbox_db(row_factory=True)
    try:
        cur = conn.cursor()

        # Execute user's DML
        cur.execute(user_query)
        conn.commit()

        # Safe verification (may fail if table dropped)
        if verify_query.strip():
            try:
                cur.execute(verify_query)
                user_rows = dict_rows(cur)
            except sqlite3.OperationalError as e:
                user_rows = [{"error": str(e)}]

        # Run expected query in a separate sandbox
        expected_conn, expected_tmp = create_sandbox_db(row_factory=True)
        try:
            ecur = expected_conn.cursor()
            ecur.execute(correct_query)
            expected_conn.commit()

            if verify_query.strip():
                try:
                    ecur.execute(verify_query)
                    expected_rows = dict_rows(ecur)
                except sqlite3.OperationalError as e:
                    expected_rows = [{"error": str(e)}]
        finally:
            expected_conn.close()
            os.remove(expected_tmp)

        # Compare results
        if order_sensitive:
            results_match = (user_rows == expected_rows)
        else:
            results_match = (sorted(user_rows, key=str) == sorted(expected_rows, key=str))

    except Exception as e:
        user_err = str(e)
        results_match = False
    finally:
        conn.close()
        try:
            os.remove(tmpdb)
        except:
            pass

    return results_match, user_err

def evaluate_created_table(user_query: str, correct_query: str, table_name: str) -> tuple[bool, str]:
    """
    Validates that a table was created exactly as expected:
    - Table existence
    - Column names & order
    - Column data types
    - Constraints (PK, NOT NULL, UNIQUE, DEFAULT, AUTOINCREMENT)

    Returns (match: bool, user_error: str | None)
    """

    def get_table_schema(conn, table):
        cur = conn.cursor()

        # Column info
        cur.execute(f"PRAGMA table_info({table})")
        columns = cur.fetchall()

        # Unique constraints
        cur.execute(f"PRAGMA index_list({table})")
        indexes = cur.fetchall()

        unique_cols = set()
        for idx in indexes:
            idx_name = idx["name"] if isinstance(idx, dict) else idx[1]
            is_unique = idx["unique"] if isinstance(idx, dict) else idx[2]
            if is_unique:
                cur.execute(f"PRAGMA index_info({idx_name})")
                for col in cur.fetchall():
                    unique_cols.add(col["name"] if isinstance(col, dict) else col[2])

        # Raw SQL (needed for AUTOINCREMENT)
        cur.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
            (table,)
        )
        sql_row = cur.fetchone()
        table_sql = sql_row["sql"] if sql_row else ""

        return {
            "columns": columns,
            "unique_cols": unique_cols,
            "sql": table_sql.upper()
        }

    def normalize_type(t):
        """SQLite is flexible with types — normalize common aliases."""
        if not t:
            return ""
        t = t.upper()
        if "INT" in t:
            return "INTEGER"
        if "CHAR" in t or "TEXT" in t or "CLOB" in t:
            return "TEXT"
        if "REAL" in t or "FLOA" in t or "DOUB" in t:
            return "REAL"
        if "BLOB" in t:
            return "BLOB"
        return t

    user_err = None

    conn, tmpdb = create_sandbox_db(row_factory=True)
    try:
        cur = conn.cursor()
        cur.execute(user_query)
        conn.commit()

        # Check table existence
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        if not cur.fetchone():
            return False, f"Table '{table_name}' was not created."

        # Build expected schema
        expected_conn, expected_tmp = create_sandbox_db(row_factory=True)
        try:
            ecur = expected_conn.cursor()
            ecur.execute(correct_query)
            expected_conn.commit()

            ecur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,)
            )
            if not ecur.fetchone():
                return False, "Expected table definition is invalid."

            user_schema = get_table_schema(conn, table_name)
            expected_schema = get_table_schema(expected_conn, table_name)

            user_cols = user_schema["columns"]
            expected_cols = expected_schema["columns"]

            # Column count
            if len(user_cols) != len(expected_cols):
                return False, "Incorrect number of columns."

            # Column-by-column comparison
            for u, e in zip(user_cols, expected_cols):
                u_name, e_name = u["name"], e["name"]
                print(u["notnull"])
                print(e["notnull"])
                if u_name != e_name:
                    return False, f"Column '{u_name}' should be '{e_name}'."

                if normalize_type(u["type"]) != normalize_type(e["type"]):
                    return False, f"Incorrect datatype for column '{u_name}'."

                if u["notnull"] != e["notnull"]:
                    return False, f"NOT NULL constraint mismatch on '{u_name}'."

                if bool(u["pk"]) != bool(e["pk"]):
                    return False, f"PRIMARY KEY constraint mismatch on '{u_name}'."

                if u["dflt_value"] != e["dflt_value"]:
                    return False, f"DEFAULT value mismatch on '{u_name}'."

            # UNIQUE constraints
            if user_schema["unique_cols"] != expected_schema["unique_cols"]:
                return False, "UNIQUE constraint mismatch."

            # AUTOINCREMENT (must inspect SQL)
            if ("AUTOINCREMENT" in expected_schema["sql"]) != (
                "AUTOINCREMENT" in user_schema["sql"]
            ):
                return False, "AUTOINCREMENT constraint mismatch."

            return True, None

        finally:
            expected_conn.close()
            os.remove(expected_tmp)

    except Exception as e:
        user_err = str(e)
        return False, user_err

    finally:
        conn.close()
        try:
            os.remove(tmpdb)
        except:
            pass

# -------------------------------------
# Endpoints
# -------------------------------------
# ------------- Lesson details -------------
@app.get("/lessons")
def get_all_lessons():
    """
    Returns basic features about each lesson in the LESSON_LIST.
    Title, subtitle, order and completed are the fields returned
    """
    results = {}
    for lesson_id in LESSON_LIST:
        lesson, _ = load_lesson(lesson_id)
        difficulty = get_lesson_difficulty(lesson_id)
        results[lesson_id] = {
            "title": lesson.get("title"),
            "subtitle": lesson.get("subtitle"),
            "order": lesson.get("lesson-order"),
            "completed": lesson_id in COMPLETED_LESSONS,
            "difficulty": difficulty
        }

    return jsonify(results)

@app.get("/lessons/details/<lesson_id>")
def get_lesson(lesson_id: str):
    """
    Returns lesson json details from the lesson.json file. 
    Injects a completed field in the lesson, and tasks if they are in the COMPLETED_LESSONS or COMPLETED_TASKS list.
    """
    lesson, _ = load_lesson(lesson_id)

    exercise_tasks = lesson.get("exercise-tasks")
    for task in exercise_tasks:
        task["completed"] = task.get("task-id") in COMPLETED_TASKS

    return jsonify({
        "id": lesson_id,
        "title": lesson.get("title"),
        "subtitle": lesson.get("subtitle"),
        "database-tables": lesson.get("database-tables"),
        "exercise-tasks": lesson.get("exercise-tasks"),
        "completed": lesson_id in COMPLETED_LESSONS
    })

@app.get("/lessons/next_lesson/<lesson_id>/<direction>")
def get_next_lesson(lesson_id: str, direction: str):
    """
    Returns the lesson_id of the previous or next lesson, depending on the direction field in the request URL.
    """
    if direction not in ('previous', 'next'):
        return jsonify({"error": "Invalid direction"}), 400
    
    # Find current index
    try:
        current_index = LESSON_LIST.index(lesson_id)
    except ValueError:
        return jsonify({"error": f"Lesson not found: {lesson_id}"}), 404

    next_lesson_id = None

    if direction == "next":
        if current_index < len(LESSON_LIST) - 1:
            next_lesson_id = LESSON_LIST[current_index + 1]
        else:
            next_lesson_id = None  # no next lesson

    elif direction == "previous":
        if current_index > 0:
            next_lesson_id = LESSON_LIST[current_index - 1]
        else:
            next_lesson_id = None  # no previous lesson

    return jsonify({
        "current_lesson_id": lesson_id,
        "next_lesson_id": next_lesson_id
    })

@app.get("/lessons/content/<lesson_id>")
def get_lesson_markdown(lesson_id: str):
    markdown, _ = load_lesson_markdown(lesson_id)
    return markdown

# ------------- SQL query execution and evaluation -------------
@app.get("/lessons/complete/<lesson_id>")
def complete_lesson(lesson_id: str):
    """
    Attempts to complete a lesson
    Checks that all the lesson's tasks were completed before adding to COMPLETED_LESSONS set
    """

    lesson, _ = load_lesson(lesson_id)
    lesson_tasks = lesson.get("exercise-tasks") or []
    for task in lesson_tasks:
        key = task.get('task-id')
        if key not in COMPLETED_TASKS:
            return {"status": "error", "message":"Failure: not all tasks have been completed for this lesson"}, 400

    COMPLETED_LESSONS.add(lesson_id)
    return {"status": "success"}, 200

@app.post("/lessons/preview/<lesson_id>/<float:task_id>")
def preview_query(lesson_id: str, task_id: float):
    """
    Preview endpoint for debounced typing. Body JSON: { "sql": "SELECT ..."}
    Returns rows & columns on success, or 400 with error.
    """
    lesson,_ = load_lesson(lesson_id)
    for task in lesson.get("exercise-tasks"):
        if task.get("id") == task_id:
            if not task.get("preview-allowed"):
                jsonify({"error": "Preview now allowed for this task"}), 403
            else: 
                break

    data = request.get_json(silent=True) or {}
    sql = data.get("query", "")

    user_raw_query = data["query"]
    user_query = strip_sql_comments(user_raw_query)

    ok, msg = is_select_only(user_query)
    if not ok:
        return jsonify({"error": "Not Allowed", "message": msg})

    columns, rows, err = safe_run_readonly(sql, row_limit=PREVIEW_ROW_LIMIT)
    if err:
        return jsonify({"error": "Invalid SQL query", "message": err})

    return jsonify({"results":{"columns": columns, "rows": rows}}), 200

@app.post("/lessons/evaluate/<lesson_id>/<float:task_id>")
def evaluate_submission(lesson_id: str, task_id: float):
    """
    Determines if the query submitted for a given task is correct.
    User submitted queries are always compared against the verify-query for the given task.
    For DML and table definition tasks, the correct-query is run (e.g. the CREATE TABLE query), and then the verify-query is ran to ensure
    the final states of the correct query are the same as the user query.
    Returns the lesson-id, task-id, userError (is "" if no errors), and results-match, which is True if the user is correct, False otherwise. 
    """

    data = request.get_json(silent=True)
    if not data or "query" not in data:
        return jsonify({"error": "Missing 'query' in request body."}), 400

    user_query = strip_sql_comments(data["query"])

    # Load lesson + task
    lesson, _ = load_lesson(lesson_id)
    tasks = lesson.get("exercise-tasks") or []

    if task_id not in TASKS_LIST:
        return jsonify({"error": f"Invalid task id {task_id}"}), 400

    task = next((t for t in tasks if t["task-id"] == task_id), None)
    if task is None:
        return jsonify({"error": f"Invalid task id {task_id}"}), 400

    verify_query = task.get("verify-query")
    correct_query = task.get("correct-query")
    is_dml_allowed = bool(task.get("allow-dml"))
    is_table_definition = bool(task.get("create-tables"))
    order_sensitive = bool(task.get("order-sensitive"))

    results_match = None
    user_error = None

    if not is_dml_allowed and not is_table_definition:
        # Standard read only test
        results_match, user_error = evaluate_read_only(user_query, verify_query, order_sensitive)
    elif is_dml_allowed and not is_table_definition:
        # DML Test
        results_match, user_error = evaluate_dml(user_query, correct_query, verify_query, order_sensitive)
    else:
        # Table definition test
        expected_table_name = task.get("expected-table-name")
        results_match, user_error = evaluate_created_table(user_query, verify_query, expected_table_name)
        
    if results_match is None: 
        return jsonify({"error": f"Internal server error: evaluate methods returned Null outcomes"}), 500
    
    if results_match and not user_error: 
        # Submission is valid, update COMPLETED_TASKS list 
        COMPLETED_TASKS.add(task_id)

    response = {
        "lessonId": lesson_id,
        "taskNumber": task_id,
        "userError": user_error,
        "resultsMatch": results_match
    }

    return jsonify(replace_nulls(response)), 200

@app.get("/lessons/answer/<lesson_id>/<float:task_id>")
def get_task_answer(lesson_id: str, task_id: float):
    """
    Returns the answer SQL code for a given task (correct-query field in the lesson.json)
    Will raise a 403 (forbidden error) if the timer is active
    Will raise a 404 (not found error) if the task number is not valid
    """
    if task_id not in TASKS_LIST:
        return jsonify({"error": f"Invalid task number: {task_id}"}), 404
    if CLOCK_START_TIME:
        # Countdown timer is active - answers not allowed 
        return jsonify({"error": "Cannot fetch answers when timer is active"}), 403

    # Valid state, return answer
    lesson, _ = load_lesson(lesson_id)
    tasks = lesson.get("exercise-tasks")
    for task in tasks:
        if task.get("task-id") == task_id:
            return jsonify({"answer": f"{task.get("correct-query")}"}), 200

    return jsonify({"error": f"unable to fetch an answer for task ({task_id})"}), 404

# ------------- Session and timer logic -------------
@app.get("/reset_session")
def reset_session():
    """
    Clears all completed tasks, lessons, and clock times.
    """
    global CLOCK_START_TIME, PREVIOUS_COMPLETION_TIMES
    COMPLETED_LESSONS.clear()
    COMPLETED_TASKS.clear()
    CLOCK_START_TIME = None
    PREVIOUS_COMPLETION_TIMES = []
    run_init_sql()
    return {"status": "reset"}, 200

@app.get("/timer/start")
def start_timer():
    """
    Clears all completed lessons and tasks, and resets the clock timer.
    """
    global CLOCK_START_TIME
    global COMPLETED_LESSONS
    global COMPLETED_TASKS

    CLOCK_START_TIME = datetime.now()
    COMPLETED_LESSONS = set()
    COMPLETED_TASKS = set()
    return {"started": CLOCK_START_TIME.isoformat()}, 200  

@app.get("/timer/cancel_attempt")
def cancel_timer():
    """
    Cancels the current running clock by setting CLOCK_START_TIME to None.
    """
    global CLOCK_START_TIME
    CLOCK_START_TIME = None
    return {"message": "timer cancelled"}, 200  

@app.get("/timer/submit")
def submit_time():
    """
    Checks if all tasks and lessons are complete. If they are, save completion time to PREVIOUS_COMPLETION_TIMES
    If there are outstanding tasks/lessons, a 400 error is raised.
    """
    global CLOCK_START_TIME
    if set(LESSON_LIST) == COMPLETED_LESSONS:
        # User has completed all lessons. Record the runtime if the clock was started
        if CLOCK_START_TIME:
            PREVIOUS_COMPLETION_TIMES.append(datetime.now() - CLOCK_START_TIME)
        COMPLETED_LESSONS.clear()
        CLOCK_START_TIME = None
        return {"message": "timer reset"}, 200
    else:
        missing_lessons = list(set(LESSON_LIST) - set(COMPLETED_LESSONS))
        return {
            "message": "invalid submission, incomplete lessons",
            "outstanding_lessons": missing_lessons
        }, 400

@app.get("/timer/value")
def get_timer():
    """
    Gets the current status of the timer.
    """
    if CLOCK_START_TIME:
        return {"timer_status": "active", "start_time": CLOCK_START_TIME.isoformat()}, 200
    else:
        return {"timer_status": "inactive", "start_time": None}, 200

@app.get("/timer/attempts")
def get_timer_attempts():
    if len(PREVIOUS_COMPLETION_TIMES) > 0:
        PREVIOUS_COMPLETION_TIMES.sort()
        best = PREVIOUS_COMPLETION_TIMES[0]
        last = PREVIOUS_COMPLETION_TIMES[-1]

        return {
            "number_of_attempts": len(PREVIOUS_COMPLETION_TIMES),
            "best_attempt": format_timedelta(best),
            "last_attempt": format_timedelta(last),
        }

    return {
        "number_of_attempts": 0,
        "best_attempt": None,
        "last_attempt": None,
    }

# ------------- Basic table reads of entire table, and metadata fetching -------------
@app.get("/tables/<table_name>")
def get_db_rows(table_name: str):
    if table_name not in DATABASE_TABLES:
        return {"status": f"Database table not found: {table_name}"}

    tmp_query = f"SELECT * FROM {table_name}"
    ok, _ = is_select_only(tmp_query)
    if ok: 
        columns, rows, err = safe_run_readonly(tmp_query, row_limit=PREVIEW_ROW_LIMIT)
        if not err:
            return jsonify({"results":{"columns": columns, "rows": rows}}), 200
    return jsonify({"error": "Failed to fetch the database table"}), 404

@app.get("/tables/meta/<table_name>")
def get_table_metadata(table_name: str):
    """
    Returns the table name and columns
    """
    column_names = get_db_table_columns(table_name)
    return {"name": table_name, "columns": column_names} 

# -------------------------------------
# Routes
# -------------------------------------
@app.route("/")
def root():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/lesson/<lesson_id>")
def lesson_page(lesson_id):
    return send_from_directory("static/views", "lesson.html")

if __name__ == "__main__":
    """
    Checks that an instance of the app is not already running on APP_URL.
    If there is already a running instance, just open a new webbrowswer tab.
    If there is no instance running, run full startup proccess.
    
    """
    if check_if_running():
        print("App already running. Skipping initialization...")
        webbrowser.open_new(APP_URL)
    else:
        print("No existing instance found. Running full startup...")
        DB_PATH = "file:shared_db?mode=memory&cache=shared"
        DB_INIT_CONN = sqlite3.connect(DB_PATH, uri=True, check_same_thread=False)

        detect_and_validate_lessons()
        run_init_sql()
        load_database_tables()
        print("Loaded tables:", DATABASE_TABLES)
        print(f"Loaded {len(LESSON_LIST)} lessons")
        print(f"Loaded {len(TASKS_LIST)} tasks")
        webbrowser.open_new(APP_URL)
        app.run(host="0.0.0.0", port=8000, debug=True, use_reloader=False)
