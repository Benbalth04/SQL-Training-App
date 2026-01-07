// GLOBAL STATE
let lesson = null;
let currentTaskNumber = null;
let editor = null;
let resultsTable = null;
let debounceTimer = null;
let sqlContext = { tables: {} };
let popupTimeout = null;
let isUpdatingLessonMenu = false;

// ------------------------------------------------------------
// INITIALISATION
// ------------------------------------------------------------
window.addEventListener("DOMContentLoaded", async () => {
    let lessonId = null;

    const params = new URLSearchParams(window.location.search);
    if (params.has("lesson-id")) {
        lessonId = params.get("lesson-id");
    } else {
        // Extract from URL path: /lesson/lesson-1-basic-select
        const parts = window.location.pathname.split("/").filter(Boolean);
        const lessonIndex = parts.indexOf("lesson");
        if (lessonIndex !== -1 && parts.length > lessonIndex + 1) {
            lessonId = parts[lessonIndex + 1];
        }
    }

    if (!lessonId) {
        console.error("No lesson-id provided in URL");
        return;
    }
    await initMonaco();
    await loadLesson(lessonId);
    loadLessonMarkdown(lessonId);
    // renderInitialResultsTable();
    renderSourceTables();
    setupMenuToggle();
    await updateLessonMenu();

    let incomplete_task_exists = false;
    for (const task of lesson["exercise-tasks"]) {
        if (!task.completed) {
            incomplete_task_exists = true;
            break;
        }
    }

    const next_lesson_button = document.getElementById("next-lesson-btn");

    if (incomplete_task_exists) {
        next_lesson_button.classList.add("disabled");
    } else {
        const next_lesson_resp = await fetch(`/lessons/next_lesson/${lesson.id}/next`)
        const next_lesson_data = await next_lesson_resp.json();
        const next_lesson_id = next_lesson_data["next_lesson_id"];

        const lessons_resp = await fetch(`/lessons`)
        const lessons_data = await lessons_resp.json();
        let all_lessons_completed = true;
        for (const [lnsId, lsn] of Object.entries(lessons_data)) {
            if (!lsn.completed) {
                all_lessons_completed = false;
                break;
            }
        }
        
        if (all_lessons_completed) {
            next_lesson_button.innerText = "All Lessons Complete - Return Home";
            next_lesson_button.onclick = () => {
                window.location.href = `/`;
            };
        } else if (next_lesson_id != null ){
            next_lesson_button.innerText = "Next Lesson";
            next_lesson_button.onclick = () => {
                window.location.href = `/lesson/${next_lesson_id}`;
            };
        } else {
            next_lesson_button.innerText = "View Incomplete Lessons";
            next_lesson_button.onclick = () => {
                window.location.href = `/`;
            };
        }
    }
});

// ------------------------------------------------------------
// FETCH LESSON METADATA AND MARKDOWN CONTENT
// ------------------------------------------------------------
async function loadLesson(lessonId) {
    const res = await fetch(`/lessons/details/${lessonId}`);
    lesson = await res.json();

    document.getElementById("lesson-title").textContent = lesson.title + ': ' + lesson.subtitle;
    renderTaskList();
}

async function loadLessonMarkdown(lessonId) {
    const res = await fetch(`/lessons/content/${lessonId}`);
    const md = await res.text();

    const html = marked.parse(md, { breaks: true });
    const lessonBody = document.getElementById("lesson-body");
    lessonBody.innerHTML = html;

    // Apply Markdown SQL detection
    document.querySelectorAll("pre code").forEach((block) => {
        if (!/language-/.test(block.className) &&
            /(\bSELECT\b|\bFROM\b|\bWHERE\b|\bJOIN\b)/i.test(block.textContent)) {
            block.classList.add("language-sql");
        }
    });

    // Apply table styling ONLY to Markdown tables
    lessonBody.querySelectorAll("table").forEach((table) => {
        table.classList.add("markdown-table");
    });

    if (window.hljs) hljs.highlightAll();
}

// ------------------------------------------------------------
// DROPDOWN MENU
// ------------------------------------------------------------
function setupMenuToggle() {
    const menuToggle = document.getElementById("menu-toggle");
    const menuContainer = document.getElementById("menu-panel"); // corrected selector

    if (!menuToggle.dataset.listenerAdded) {
        menuToggle.addEventListener("click", () => {
            // Toggle visibility
            if (menuContainer.style.display === 'none' || menuContainer.style.display === '') {
                menuContainer.style.display = 'block';
            } else {
                menuContainer.style.display = 'none';
            }
        });
        menuToggle.dataset.listenerAdded = "true";
    }
}

async function updateLessonMenu() {
    const currentLessonId = lesson["id"];
    if (isUpdatingLessonMenu) return;  // prevent overlapping calls
    isUpdatingLessonMenu = true;

    try {
        const menuList = document.getElementById("lesson-menu-list");
        if (!menuList) return;

        menuList.innerHTML = ""; // clear existing items

        // --- Add Home button at the top ---
        const homeItem = document.createElement("a");
        homeItem.href = "/";  // root endpoint
        homeItem.textContent = "Home";
        homeItem.style.fontWeight = "bold";
        homeItem.style.textDecoration = "underline";
        homeItem.style.display = "block"; // ensures it stacks vertically with lessons
        homeItem.style.fontSize = "1.1rem"; // increase font size
        menuList.appendChild(homeItem);

        const res = await fetch("/lessons");
        const data = await res.json();

        const lessons = Object.entries(data)
            .map(([id, details]) => ({ id, ...details }))
            .sort((a, b) => a.order - b.order);

        const fragment = document.createDocumentFragment();

        lessons.forEach(lesson => {
            const item = document.createElement("a");
            item.href = `/lesson/${lesson.id}`;
            item.textContent = `${lesson.title}: ${lesson.subtitle}${lesson.completed ? " ✓" : ""}`;

            if (lesson.completed) item.classList.add("completed");
            if (lesson.id === currentLessonId) item.style.fontWeight = "bold";

            item.style.display = "block"; // make lessons stack vertically
            fragment.appendChild(item);
        });

        menuList.appendChild(fragment);
    } finally {
        isUpdatingLessonMenu = false;
    }
}

// ------------------------------------------------------------
// TASKS LIST
// ------------------------------------------------------------
function renderTaskList() {
    const taskList = document.getElementById("tasks-list");
    taskList.innerHTML = "";
    let firstTaskFound = false;

    // Sort by exercise order 
    let tasks = lesson["exercise-tasks"]
    tasks.sort((a,b) => (a["exercise-order"] || 0) - (b["exercise-order"] || 0))

    for (const task of tasks) {
        const element = document.createElement("div");
        element.className = "task-item";
        // grey out completed tasks 
        if (task.completed) {
            element.classList.add("task-completed");
        } else if (!firstTaskFound) {
            // Mark first uncompleted task as the selected task
            currentTaskNumber = task["exercise-order"];
            firstTaskFound = true;
            element.classList.add("task-selected");
            if (editor) {
                editor.setValue(`-- Press Ctrl + Enter to submit your query\n` +(task["initial-query"] || ""));
            };
            updateSqlContextForTask(task);
            scaleEditor(task["large-query"]);
            changeDataTableVisibility(task["preview-allowed"]);
            runLiveQuery(true);
        };

        // Display text 
        const text = document.createElement("span");
        text.textContent = `${task["exercise-order"]}: ${task.description}`
        element.appendChild(text);

        // Tick if completed
        if (task.completed) {
            const tick = document.createElement("span");
            tick.className = "task-tick";
            tick.textContent = " ✔";
            element.appendChild(tick);
        }

        // clicking switches selected task
        element.addEventListener("click", () => {
            if (task.completed) return;
            switchTask(currentTaskNumber, task["exercise-order"], false);
        });
        taskList.appendChild(element);
    };

    // Ensure the datatable is show even if there are no tasks to complete 
    if (!firstTaskFound) {
         editor.setValue(`-- Press Ctrl + Enter to submit your query\n` +(tasks[0]["initial-query"] || ""));
    }

}

async function switchTask(current_task_number, next_task_number, complete_task) {
    const taskElements = document.querySelectorAll(".task-item");
    const currentEl = taskElements[current_task_number - 1];

    // 1. Mark current task as completed if complete task is true 
    if (complete_task) {
        if (currentEl && !currentEl.classList.contains("task-completed")) {
            currentEl.classList.add("task-completed");

            // Add tick ✔ if missing
            if (!currentEl.querySelector(".task-tick")) {
                const tick = document.createElement("span");
                tick.className = "task-tick";
                tick.textContent = " ✔";
                currentEl.appendChild(tick);
            }
        }
    };

    // 2. Clear all "selected" markers
    taskElements.forEach(el => el.classList.remove("task-selected"));

    // Do not transition if next task is completed
    if (lesson["exercise-tasks"][next_task_number-1]["completed"]) {
        return;
    }

    // 3. Mark next task as selected
    const nextEl = taskElements[next_task_number - 1];
    if (nextEl) {
        nextEl.classList.add("task-selected");
    }

    // 4. Update global pointer
    currentTaskNumber = next_task_number;

    // 5. Load corresponding starter SQL into Monaco
    const tasks = lesson["exercise-tasks"].sort(
        (a, b) => (a["exercise-order"] || 0) - (b["exercise-order"] || 0)
    );

    const newTask = tasks[next_task_number - 1];
    if (editor && newTask) {
        editor.setValue(newTask["initial-query"] || "");
    }
    updateSqlContextForTask(newTask);
    scaleEditor(newTask["large-query"]);

    // 6. Re-run preview query
    runLiveQuery(true);
    await updateLessonMenu();
    changeDataTableVisibility(newTask["preview-allowed"]);
}

async function revealTaskAnswer() {
    const task = lesson["exercise-tasks"][currentTaskNumber-1];
    const resp = await fetch(`/lessons/answer/${lesson["id"]}/${task["task-id"]}`);
    if (resp.status === 403) {
        // Not allowed because timer is active - show error popup 
        showAnswerPopup(true, null, "Unable to reveal answers when the timer is active.");
        return;
    } else if (resp.status == 404) {
        // Show error message 
        showAnswerPopup(true, null, "Unable to find an answer for this task.")
    }

    const data = await resp.json();
    const answer = data.answer;
    showAnswerPopup(false, task, answer);
    return;
}

function showAnswerPopup(error, task, message) {
    const popup = document.getElementById("answer-popup");
    const overlay = document.getElementById("answer-overlay");
    const popupText = document.getElementById("answer-popup-text");
    const popupSql = document.getElementById("answer-popup-sql");

    // Reset
    popupText.innerText = '';
    popupSql.innerHTML = '';
    popupSql.style.display = "none";

    popup.classList.remove("error", "success");
    
    // Show popup + overlay
    popup.classList.add("active");
    overlay.classList.add("active");

    if (error) {
        popup.classList.add("error");
        popupText.innerText = message;
        return;
    }

    popup.classList.add("success");
    popupText.innerText = `Task ${task["task-id"]} Answer: ${task["description"]}`;
    popupSql.style.display = "block";
    popupSql.innerHTML = `<pre><code class="language-sql">${message}</code></pre>`;
}

function closeAnswerPopup() {
    const popup = document.getElementById("answer-popup");
    const overlay = document.getElementById("answer-overlay");

    popup.classList.remove("active", "success", "error");
    overlay.classList.remove("active");
}

// ------------------------------------------------------------
// MONACO EDITOR
// ------------------------------------------------------------
function initMonaco() {
    return new Promise(resolve => {
        require.config({
            paths: {
                vs: "https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs"
            }
        });

        require(["vs/editor/editor.main"], () => {

            editor = monaco.editor.create(document.getElementById("editor"), {
                value: "",
                language: "sql",
                theme: "vs-light",
                automaticLayout: true,
                minimap: { enabled: false },
                autoFocus: false,
            });

            editor.onDidChangeModelContent(() => {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(runLiveQuery, 400);
            });

            // Register Ctrl+Enter shortcut
            editor.addCommand(
                monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter,
                () => {
                    submitSQL();   // your function
                }
            );

            // ---------------------------------------------------------
            // Completion provider
            // ---------------------------------------------------------
            monaco.languages.registerCompletionItemProvider("sql", {
                    triggerCharacters: [" ", ".", "\n"],

                    provideCompletionItems(model, position) {
                        const line = model.getLineContent(position.lineNumber);
                        const textUntilPos = line.slice(0, position.column);

                        const suggestions = [];

                        // ============================================
                        // 1️TABLE SUGGESTIONS after FROM / JOIN / INTO / UPDATE
                        // ============================================
                        if (/(\bFROM\b|\bJOIN\b|\bUPDATE\b|\bINTO\b)\s+$/i.test(textUntilPos)) {
                            for (const tableName of Object.keys(sqlContext.tables)) {
                                suggestions.push({
                                    label: tableName,
                                    kind: monaco.languages.CompletionItemKind.Class,
                                    insertText: tableName
                                });
                            }
                            return { suggestions };
                        }

                        // ============================================
                        // 2COLUMN SUGGESTIONS for tableName.
                        // ============================================
                        const tableDotMatch = textUntilPos.match(/([a-zA-Z_][a-zA-Z0-9_]*)\.$/);
                        if (tableDotMatch) {
                            const tableName = tableDotMatch[1];
                            const cols = sqlContext.tables[tableName] || [];

                            return {
                                suggestions: cols.map(col => ({
                                    label: col,
                                    kind: monaco.languages.CompletionItemKind.Field,
                                    insertText: col
                                }))
                            };
                        }

                        // ============================================
                        // COLUMN SUGGESTIONS WITHOUT TABLE NAME
                        //     ALWAYS suggest columns from ALL tables 
                        //     in the sqlContext data structure
                        // ============================================
                        let allCols = [];
                        for (const [tableName, cols] of Object.entries(sqlContext.tables)) {
                            allCols = allCols.concat(cols);
                        }

                        return {
                            suggestions: allCols.map(col => ({
                                label: col,
                                kind: monaco.languages.CompletionItemKind.Field,
                                insertText: col
                            }))
                        };
                    }
                });
            resolve();
        });
    });
}

async function updateSqlContextForTask(task) {
    sqlContext.tables = {};
    if (lesson["database-tables"].length == 0) {
        return;
    }

    const tables = task["tables"] || lesson["database-tables"] || [];
    for (const t of tables) {
        const res = await fetch(`/tables/meta/${t.name}`);
        const table_metadata = await res.json();
        sqlContext.tables[table_metadata.name] = table_metadata.columns;
    }

    if (editor) {
        editor.trigger("context-change", "editor.action.triggerSuggest", {});
    }
}

function resetMonaco() {
    if (editor) {
        editor.setValue(lesson["exercise-tasks"][currentTaskNumber-1]["initial-query"]);
    }
}

function scaleEditor(isLarge) {
    const container = document.querySelector('.exercise-container');
    if (!container) return;

    if (isLarge) {
        container.classList.add('large-editor');
    } else {
        container.classList.remove('large-editor');
    }
}

function showPopup(message, type = "error") {
    const popup = document.getElementById("sql-popup");

    // Reset existing timeout if popup is triggered again quickly
    if (popupTimeout) {
        clearTimeout(popupTimeout);
        popupTimeout = null;
    }

    // Reset class to ensure clean state
    popup.className = ""; 
    popup.classList.add(type === "success" ? "success" : "error");

    // Set message
    popup.textContent = message;

    // Show popup
    popup.style.display = "block";
    popup.classList.add("show");

    // Auto-hide after delay
    popupTimeout = setTimeout(() => {
        popup.classList.remove("show");

        // Wait for CSS fade-out to finish
        setTimeout(() => {
            popup.style.display = "none";
        }, 250);
    }, 2000);
}

// ------------------------------------------------------------
// LIVE SQL EXECUTION (NO SUBMISSION)
// ------------------------------------------------------------
async function runLiveQuery(initial_load=false) {
    if (!editor) return;
    
    const sql = editor.getValue();
    if (!sql.trim()) return;

    if (lesson && !lesson["exercise-tasks"][currentTaskNumber-1]["preview-allowed"]) {
        // Block live preview for DML tasks, but allow initial load preview
        return;
    }
        
    if (!currentTaskNumber && lesson) {
        // All lesson tasks are complete, just render the default query for the first task
        const preview_task = lesson["exercise-tasks"][0];
        const response = await fetch(`/lessons/preview/${lesson["id"]}/${lesson["exercise-tasks"][currentTaskNumber-1]["task-id"]}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: preview_task["initial-query"] })
        });
         if (response.status == 400) {
            showPopup(data.error, "error");
            return;
        }

        const data = await response.json();

        if (response.status == 400 && !data) {
            showPopup("Invalid SQL Query", "error");
            return;
        }

        if (data.error) {
            showPopup(data.error, "error");
            return;
        }
        updateDataTable(data.results);
    }
    
    const response = await fetch(`/lessons/preview/${lesson["id"]}/${lesson["exercise-tasks"][currentTaskNumber-1]["task-id"]}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: sql })
    });

    if (response.status == 400) {
        showPopup(data.error, "error");
        return;
    }

    const data = await response.json();

    if (response.status == 400 && !data) {
        showPopup("Invalid SQL Query", "error");
        return;
    }

    if (data.error) {
        showPopup(data.error, "error");
        return;
    }
    updateDataTable(data.results);
}

// ------------------------------------------------------------
// SUBMISSION (FULL VALIDATION)
// ------------------------------------------------------------
async function submitSQL() {
    if (currentTaskNumber == null) return;

    const currentTask = lesson["exercise-tasks"][currentTaskNumber - 1];
    if (currentTask.completed) return;

    const sql = editor.getValue();
    const taskNumber = currentTask["task-id"];
    const payload = {
        lesson_id: lesson.id,
        task_number: taskNumber,
        query: sql
    };

    // Evaluate user query
    const response = await fetch(`/lessons/evaluate/${lesson.id}/${taskNumber}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });
    const result = await response.json();
    console.log(result);
    console.log(result.userError);

    if (!result.resultsMatch) {
        if (result.userError != "") {
            showPopup(`Incorrect Answer: ${result.userError}`, "error");
        } else {
            showPopup(`Incorrect Answer`, "error");
        }
        return;
    }

    // Mark current task as completed visually
    markTaskComplete(currentTaskNumber);

    showPopup("Correct!", "success");

    // Find next incomplete task
    let nextTaskNumber = null;
    for (let i = currentTaskNumber-1; i < lesson["exercise-tasks"].length; i++) {
        if (!lesson["exercise-tasks"][i].completed) {
            nextTaskNumber = i + 1; 
            break;
        }
    }
    if (nextTaskNumber === null) {
        for (let i = 0; i < currentTaskNumber-1; i++) {
            if (!lesson["exercise-tasks"][i].completed) {
                nextTaskNumber = i + 1; 
                break;
            }
        }
    }
    

    // All tasks completed → mark lesson complete
    if (nextTaskNumber === null) {
        const resp = await fetch(`/lessons/complete/${lesson.id}`);
        const data = await resp.json();

        if (resp.status === 200 || data.status === "success") {
            await handleNextLessonButton();
        }
        return;
    }

    // Switch to next incomplete task
    switchTask(currentTaskNumber, nextTaskNumber, true);
}

async function markTaskComplete(taskNumber) {
    const taskElements = document.querySelectorAll(".task-item");
    const currentEl = taskElements[taskNumber - 1];
    if (!currentEl) return;

    currentEl.classList.add("task-completed");
    currentEl.classList.remove("task-selected");

    const tick = document.createElement("span");
    tick.className = "task-tick";
    tick.textContent = " ✔";
    currentEl.appendChild(tick);

    // Mark in lesson object
    lesson["exercise-tasks"][taskNumber - 1].completed = true;

    await updateLessonMenu();
}

async function handleNextLessonButton() {
    const next_lesson_resp = await fetch(`/lessons/next_lesson/${lesson.id}/next`);
    const next_lesson_data = await next_lesson_resp.json();
    const next_lesson_id = next_lesson_data.next_lesson_id;

    const next_lesson_button = document.getElementById("next-lesson-btn");
    next_lesson_button.classList.remove("disabled");

    const lessons_resp = await fetch(`/lessons`);
    const lessons_data = await lessons_resp.json();
    const all_lessons_completed = Object.values(lessons_data).every(lsn => lsn.completed);

    if (all_lessons_completed) {
        next_lesson_button.innerText = "All Lessons Complete - Return Home";
        next_lesson_button.onclick = () => { window.location.href = `/`; };
    } else if (next_lesson_id) {
        next_lesson_button.innerText = "Next Lesson";
        next_lesson_button.onclick = () => { window.location.href = `/lesson/${next_lesson_id}`; };
    } else {
        next_lesson_button.innerText = "View Incomplete Lessons";
        next_lesson_button.onclick = () => { window.location.href = `/`; };
    }
    await updateLessonMenu();
}

// ------------------------------------------------------------
// DATA TABLES
// ------------------------------------------------------------
function updateDataTable(resultObj) {
    try {
        const tableEl = document.getElementById("results-table-preview");
        tableEl.innerHTML = "";

        if (!resultObj || !resultObj.rows || resultObj.rows.length === 0) {
            tableEl.innerHTML = "<p>No results</p>";
            return;
        }

        const columns = resultObj.columns;  // <-- column order from backend
        const rows = resultObj.rows;

        const wrapper = document.createElement("div");
        wrapper.classList.add("datatable");

        const table = document.createElement("table");

        // ---- THEAD ----
        const thead = document.createElement("thead");
        const headerRow = document.createElement("tr");

        columns.forEach(col => {
            const th = document.createElement("th");
            th.textContent = col;
            th.classList.add("column_name");
            headerRow.appendChild(th);
        });

        thead.appendChild(headerRow);
        table.appendChild(thead);

        // ---- TBODY ----
        const tbody = document.createElement("tbody");

        rows.forEach(row => {
            const tr = document.createElement("tr");

            columns.forEach(col => {
                const td = document.createElement("td");
                td.textContent = row[col];
                tr.appendChild(td);
            });

            tbody.appendChild(tr);
        });

        table.appendChild(tbody);
        wrapper.appendChild(table);
        tableEl.appendChild(wrapper);
    } catch (err) {
        console.error(err);
        document.getElementById("table-results-preview").innerHTML =
            `<div class="error">Failed to load table.</div>`;
    }
}

async function renderSourceTables() {
    const container = document.querySelector(".table-preview-container");
    container.innerHTML = "";

    if (!lesson || !lesson["database-tables"] || lesson["database-tables"].length === 0) {
        return;
    }

    for (const tableMeta of lesson["database-tables"]) {
        const tableName = typeof tableMeta === "string" ? tableMeta : tableMeta.name;

        // Create the wrapper
        const tableBox = document.createElement("div");
        tableBox.className = "table-container";

        tableBox.innerHTML = `
            <div class="table-title">${tableName} (read only)</div>
            <div id="table-preview-${tableName}" class="datatable"></div>
        `;

        container.appendChild(tableBox);

        try {
            const res = await fetch(`/tables/${tableName}`);
            const data = await res.json();

            // Reuse your existing table builder logic
            updateSourceTable(`table-preview-${tableName}`, data.results);

        } catch (err) {
            console.error(err);
            document.getElementById(`table-preview-${tableName}`).innerHTML =
                `<div class="error">Failed to load table.</div>`;
        }
    }
}

function updateSourceTable(elementId, data) {
    const tableEl = document.getElementById(elementId);
    tableEl.innerHTML = "";
    if (!data || !data.rows || !data.rows.length === 0) {
        tableEl.innerHTML = "<p>No results</p>";
        return;
    }

    const columns = data.columns; 
    const rows = data.rows; 

    const tableElem = document.createElement("table");

    // Header
    const thead = document.createElement("thead");
    const headRow = document.createElement("tr");

    columns.forEach(col => {
        const th = document.createElement("th");
        th.textContent = col;
        th.classList.add("column_name");
        headRow.appendChild(th);
    });

    thead.appendChild(headRow);
    tableElem.appendChild(thead);

    // Body
    const tbody = document.createElement("tbody");

    rows.forEach(row => {
        const tr = document.createElement("tr");

        columns.forEach(col => {
            const td = document.createElement("td");
            td.textContent = row[col];
            tr.appendChild(td);
        });

        tbody.appendChild(tr);
    });

    tableElem.appendChild(tbody);
    tableEl.appendChild(tableElem);
}

function changeDataTableVisibility(set_visible) {
    const dataTable = document.getElementById("results-table-preview");
    if (!dataTable) return;

    if (set_visible === true) {
        dataTable.classList.remove("hidden-table-preview");
    } else if (set_visible === false) {
        dataTable.classList.add("hidden-table-preview");
    } 
}

// ------------------------------------------------------------
// BUTTON HANDLERS
// ------------------------------------------------------------
document.getElementById("run-sql-btn").addEventListener("click", submitSQL);
document.getElementById("reset-sql-btn").addEventListener("click", resetMonaco);
document.getElementById("reveal-answer-btn").addEventListener("click", revealTaskAnswer);
document.getElementById("close-answer-popup-btn").addEventListener("click", closeAnswerPopup);
