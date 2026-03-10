let tabSwitchCount = 0;
const MAX_TAB_SWITCHES = 3;

// Tab Switching Detection
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') {
        tabSwitchCount++;
        showWarning(`Tab switching detected (${tabSwitchCount}/${MAX_TAB_SWITCHES}). Warning: 3 violations will auto-submit the quiz.`);
        
        if (tabSwitchCount >= MAX_TAB_SWITCHES) {
            alert("Maximum tab switches reached. Auto-submitting quiz.");
            if (window.finishQuiz) window.finishQuiz();
        }
    }
});

// Disable Right Click
document.addEventListener('contextmenu', (e) => {
    e.preventDefault();
    showWarning("Right-click is disabled.");
});

// Disable Copy / Paste / DevTools shortcuts
document.addEventListener('keydown', (e) => {
    // CTRL+C, CTRL+V, CTRL+U, CTRL+SHIFT+I
    if (
        (e.ctrlKey && (e.key === 'c' || e.key === 'v' || e.key === 'u')) ||
        (e.ctrlKey && e.shiftKey && e.key === 'I') ||
        (e.key === 'F12')
    ) {
        e.preventDefault();
        showWarning("Security violation: Shortcut disabled.");
    }
});

// Fullscreen Mode Enforcement
function enterFullscreen() {
    const el = document.documentElement;
    if (el.requestFullscreen) el.requestFullscreen();
    else if (el.webkitRequestFullscreen) el.webkitRequestFullscreen();
    else if (el.msRequestFullscreen) el.msRequestFullscreen();
}

window.addEventListener('resize', () => {
    // Detect DevTools opening (simple check)
    const threshold = 160;
    const widthDiff = window.outerWidth - window.innerWidth;
    const heightDiff = window.outerHeight - window.innerHeight;

    if (widthDiff > threshold || heightDiff > threshold) {
        showWarning("Developer Tools detection triggered!");
    }
    
    // Check if exited fullscreen
    if (!document.fullscreenElement) {
        // We don't force it back immediately to avoid loops, but warn
        // showWarning("Please stay in fullscreen mode!");
    }
});

function showWarning(message) {
    const overlay = document.getElementById('overlay');
    const warningText = document.getElementById('warning-message');
    if (overlay && warningText) {
        warningText.innerText = message;
        overlay.style.display = 'flex';
        setTimeout(() => {
            overlay.style.display = 'none';
        }, 3000);
    }
}

// Matrix Animation logic (Global to be called from any page)
function initMatrix() {
    const canvas = document.getElementById('matrix-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()_+-=[]{}|;:,.<>?/π";
    const fontSize = 14;
    const columns = canvas.width / fontSize;

    const drops = [];
    for (let i = 0; i < columns; i++) {
        drops[i] = 1;
    }

    function draw() {
        ctx.fillStyle = "rgba(0, 0, 0, 0.05)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = "#00ff41";
        ctx.font = fontSize + "px monospace";

        for (let i = 0; i < drops.length; i++) {
            const text = characters.charAt(Math.floor(Math.random() * characters.length));
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);

            if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                drops[i] = 0;
            }
            drops[i]++;
        }
    }

    setInterval(draw, 33);
}

window.addEventListener('load', initMatrix);
