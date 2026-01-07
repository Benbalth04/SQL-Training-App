let allLessons = [];

class LessonPreview {
    constructor(id, title, subtitle, order, completed, difficulty) {
        this.id = id; 
        this.title = title; 
        this.subtitle = subtitle;
        this.order = order;
        this.completed = completed;
        this.difficulty = difficulty;
    }
}

async function getLessons() {
    const response = await fetch('/lessons', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
        });

    if (response.status !== 200) {
        throw new Error("Unable to fetch lessons");
    }

    const data = await response.json();  // { "lesson1": {title, order}, ... }

    const lessons = [];

    for (const lessonId in data) {
        const { title, subtitle, order, completed, difficulty } = data[lessonId];
        lessons.push(new LessonPreview(lessonId, title, subtitle, order, completed, difficulty));
    }

    // Sort by the 'order' field (ascending)
    lessons.sort((a, b) => a.order - b.order);

    return lessons;
}

function populateDifficultyDropdown(lessons) {
    const select = document.getElementById("difficulty-filter");
    const difficulties = new Set(lessons.map(l => l.difficulty).filter(Boolean));

    difficulties.forEach(diff => {
        const option = document.createElement("option");
        option.value = diff;
        option.textContent = diff;
        select.appendChild(option);
    });

    select.addEventListener("change", () => {
        const selected = select.value;
        if (selected === "all") {
            renderLessons(allLessons);
        } else {
            const filtered = allLessons.filter(l => l.difficulty === selected);
            renderLessons(filtered);
        }
    });
}

function renderLessons(lessons) {
    const container = document.getElementById("lesson-container");
    container.innerHTML = ""; // clear previous cards

    lessons.forEach(lesson => {
        const card = document.createElement("div");
        card.className = "card";

        card.innerHTML = `
            <div class="card-title">${lesson.title}: ${lesson.subtitle} (${lesson.difficulty})</div>
            <a class=${lesson.completed ? 'card-button-complete': 'card-button'} href="lesson/${lesson.id}">
                ${lesson.completed ? 'Lesson Complete': 'Go to Lesson'}
            </a>
        `;

        container.appendChild(card);
    });
}

async function main() {
    allLessons = await getLessons();
    populateDifficultyDropdown(allLessons);
    renderLessons(allLessons);
}

main();