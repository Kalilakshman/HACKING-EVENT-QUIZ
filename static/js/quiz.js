let timer;
let timeLeft = 60;
let currentQuestionId = null;

async function loadQuestion() {
    const resp = await fetch('/get_question');
    const data = await resp.json();

    if (data.status === 'finished') {
        finishQuiz();
        return;
    }

    if (data.status === 'success') {
        const q = data.question;
        currentQuestionId = q.id;
        document.getElementById('question-text').innerText = `${q.id}. ${q.question}`;
        document.getElementById('progress').innerText = `Question ${data.current} / ${data.total}`;

        const optionsDiv = document.getElementById('options');
        optionsDiv.innerHTML = '';

        const labels = ['A', 'B', 'C', 'D'];
        q.options.forEach((opt, index) => {
            const btn = document.createElement('button');
            btn.className = 'option-btn';
            btn.innerText = `${labels[index]}. ${opt}`;
            btn.onclick = () => selectOption(btn, labels[index]);
            optionsDiv.appendChild(btn);
        });

        resetTimer();
    }
}

async function selectOption(btn, choice) {
    // Disable all buttons to prevent double-click
    const buttons = document.querySelectorAll('.option-btn');
    buttons.forEach(b => b.disabled = true);
    btn.classList.add('selected');

    await submitAnswer(choice);
}

async function submitAnswer(option) {
    clearInterval(timer);
    await fetch('/submit_answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ option: option })
    });
    loadQuestion();
}

function resetTimer() {
    clearInterval(timer);
    timeLeft = 60;
    document.getElementById('timer').innerText = timeLeft;

    timer = setInterval(() => {
        timeLeft--;
        document.getElementById('timer').innerText = timeLeft;
        if (timeLeft <= 0) {
            clearInterval(timer);
            // Auto submit with empty answer
            submitAnswer(null);
        }
    }, 1000);
}

async function finishQuiz() {
    clearInterval(timer);
    await fetch('/finish_quiz', { method: 'POST' });
    window.location.href = '/leaderboard';
}

// Global reference for security.js
window.finishQuiz = finishQuiz;

// Initialize
window.addEventListener('load', () => {
    fetch('/start_quiz', { method: 'POST' });
    loadQuestion();
});

// Prevent back button
window.history.pushState(null, null, window.location.href);
window.onpopstate = function () {
    window.history.go(1);
};
