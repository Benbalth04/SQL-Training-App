document.addEventListener("DOMContentLoaded", async () => {
    // Inject widget HTML
    const root = document.getElementById("timer-widget-root");
    root.innerHTML = `
        <div id="timer-widget">
            <div id="timer-header">
                <h3>Speed Challenge</h3>
                <button id="timer-close-btn"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div id="timer-display">00:00:00</div>
            <div id="attempt-stats">
                <div class="attempt-row"><span>Attempts:</span> <span id="stat-attempt-count">0</span></div>
                <div class="attempt-row"><span>Best:</span> <span id="stat-best">--</span></div>
                <div class="attempt-row"><span>Last:</span> <span id="stat-last">--</span></div>
            </div>
            <button id="start-btn" class="timer-btn">Start Timer</button>
            <button id="cancel-btn" class="timer-btn">Cancel Attempt</button>
            <button id="end-btn" class="timer-btn">Submit Attempt</button>
            <button id="reset-session-btn" class="timer-btn">Reset Session</button>
        </div>
        <div id="collapsed-timer" style="display:none; align-items:center; gap:5px;">
            <i class="fa-solid fa-clock" id="collapsed-clock-icon"></i>
            <span id="collapsed-timer-seconds" style="display:none;">0</span>
        </div>
    `;

    const display = document.getElementById("timer-display");
    const startBtn = document.getElementById("start-btn");
    const cancelBtn = document.getElementById("cancel-btn");
    const endBtn = document.getElementById("end-btn");
    const resetBtn = document.getElementById("reset-session-btn");
    const closeBtn = document.getElementById("timer-close-btn");
    const collapsedWidget = document.getElementById("collapsed-timer");
    const collapsedSeconds = document.getElementById("collapsed-timer-seconds");
    const collapsedClockIcon = document.getElementById("collapsed-clock-icon");
    const timerWidget = document.getElementById("timer-widget");

    let timerInterval = null;
    let startTime = null;
    let activeTimer = false;
    
    // Load saved widget state from localStorage
    const widgetState = localStorage.getItem("timerWidgetState") || "open";
    if (widgetState === "collapsed") {
        timerWidget.style.display = "none";
        collapsedWidget.style.display = "flex";
    } else {
        timerWidget.style.display = "block";
        collapsedWidget.style.display = "none";
    }

    function formatTime(ms) {
        const totalSecs = Math.floor(ms / 1000);
        const h = String(Math.floor(totalSecs / 3600)).padStart(2, "0");
        const m = String(Math.floor((totalSecs % 3600) / 60)).padStart(2, "0");
        const s = String(totalSecs % 60).padStart(2, "0");
        return `${h}:${m}:${s}`;
    }

    function startTicking() {
        if (timerInterval) clearInterval(timerInterval);
        timerInterval = setInterval(() => {
            const elapsed = Date.now() - startTime.getTime();
            display.textContent = formatTime(elapsed);
            collapsedSeconds.textContent = Math.floor(elapsed / 1000); // update collapsed
        }, 1000);
    }

    function updateButtons() {
        if (!activeTimer) {
            startBtn.textContent = "Start Attempt";
            endBtn.disabled = true;
            cancelBtn.disabled = true;
        } else {
            startBtn.textContent = "Restart Attempt";
            endBtn.disabled = false;
            cancelBtn.disabled = false;
        }
    }

    function updateCollapsedWidget() {
        if (activeTimer) {
            collapsedSeconds.style.display = "inline";
            collapsedClockIcon.style.display = "none";
        } else {
            collapsedSeconds.style.display = "none";
            collapsedClockIcon.style.display = "inline";
        }
    }

    async function syncTimerState() {
        const resp = await fetch("/timer/value");
        const data = await resp.json();

        if (data.timer_status === "active" && data.start_time) {
            activeTimer = true;
            startTime = new Date(data.start_time);
            startTicking();
        } else {
            activeTimer = false;
            startTime = null;
            display.textContent = "00:00:00";
        }

        updateButtons();
        updateCollapsedWidget();
    }

    async function loadAttemptStats() {
        const resp = await fetch("/timer/attempts");
        const data = await resp.json();
        document.getElementById("stat-attempt-count").textContent = data.number_of_attempts;
        document.getElementById("stat-best").textContent = data.best_attempt ?? "--";
        document.getElementById("stat-last").textContent = data.last_attempt ?? "--";
    }

    await syncTimerState();
    await loadAttemptStats();

    // ===== Collapse / Expand Logic =====
    closeBtn.addEventListener("click", () => {
        timerWidget.style.display = "none";
        collapsedWidget.style.display = "flex";
        updateCollapsedWidget();
        localStorage.setItem("timerWidgetState", "collapsed"); // save state
    });

    collapsedWidget.addEventListener("click", () => {
        timerWidget.style.display = "block";
        collapsedWidget.style.display = "none";
        localStorage.setItem("timerWidgetState", "open"); // save state
    });

    // ===== Timer Controls =====
    startBtn.addEventListener("click", async () => {
        const confirmed = confirm("Start a new attempt? This will reset all progress.");
        if (!confirmed) return;
        const resp = await fetch("/timer/start");
        const data = await resp.json();
        activeTimer = true;
        startTime = new Date(data.started);
        startTicking();
        updateButtons();
        updateCollapsedWidget();
        window.location.href = '/';
    });

    cancelBtn.addEventListener("click", async () => {
        if (!confirm("Cancel this attempt?")) return;
        await fetch("/timer/cancel_attempt");
        activeTimer = false;
        clearInterval(timerInterval);
        display.textContent = "00:00:00";
        startTime = null;
        updateButtons();
        updateCollapsedWidget();
        window.location.href = '/';
    });

    endBtn.addEventListener("click", async () => {
        if (!activeTimer) return;
        const resp = await fetch("/timer/submit");
        const data = await resp.json();
        if (resp.ok) {
            activeTimer = false;
            clearInterval(timerInterval);
            display.textContent = "00:00:00";
            startTime = null;
            await loadAttemptStats();
            updateButtons();
            updateCollapsedWidget();
            alert("Attempt Successfully Submitted!");
        } else {
            alert("Invalid submission. Some lessons are incomplete.");
        }
    });

    resetBtn.addEventListener("click", async () => {
        if (!confirm("Reset session? This will clear all progress.")) return;
        await fetch("/reset_session");
        clearInterval(timerInterval);
        display.textContent = "00:00:00";
        startTime = null;
        activeTimer = false;
        updateButtons();
        updateCollapsedWidget();
        window.location.href = '/';
    });
});
