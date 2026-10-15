// Main JavaScript for RoyalMods

document.addEventListener('DOMContentLoaded', function() {
    initializeTheme();

    // Masquer les messages après 5 secondes
    const messages = document.querySelectorAll('.alert');
    messages.forEach(function(message) {
        setTimeout(function() {
            message.style.opacity = '0';
            setTimeout(function() {
                message.remove();
            }, 300);
        }, 5000);
    });
    setupThemeToggle();
});

function initializeTheme() {
    const body = document.getElementById('body');
    const savedTheme = localStorage.getItem('theme');
    const theme = (savedTheme === 'light-mode') ? 'light-mode' : 'dark-mode';

    body.className = theme;
    localStorage.setItem('theme', theme);

    updateToggleButton();
}

function setupThemeToggle() {
    const toggleBtn = document.getElementById('theme-toggle');

    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            const body = document.getElementById('body');
            const isDarkMode = body.classList.contains('dark-mode');

            if (isDarkMode) {
                body.className = 'light-mode';
                localStorage.setItem('theme', 'light-mode');
            } else {
                body.className = 'dark-mode';
                localStorage.setItem('theme', 'dark-mode');
            }

            updateToggleButton();
        });
    }
}

function updateToggleButton() {
    const toggleBtn = document.getElementById('theme-toggle');
    const body = document.getElementById('body');

    if (toggleBtn) {
        const icon = toggleBtn.querySelector('.toggle-icon');
        const text = toggleBtn.querySelector('.toggle-text');
        const isDarkMode = body.classList.contains('dark-mode');

        if (isDarkMode) {
            icon.textContent = '☀️';
            text.textContent = 'Mode clair';
        } else {
            icon.textContent = '🌙';
            text.textContent = 'Mode sombre';
        }
    }
}

function swapImage(thumbnail) {
    const card = thumbnail.closest('.mod-card');
    const mainImage = card && card.querySelector('.mod-main-image');
    if (!mainImage) return;
    const mainSrc = mainImage.src;
    mainImage.src = thumbnail.src;
    thumbnail.src = mainSrc;
}

window.addEventListener('pageshow', function(event) {
    if (event.persisted) {
        initializeTheme();
    }
});