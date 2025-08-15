document.addEventListener('DOMContentLoaded', function() {
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const darkModeCSS = document.getElementById('dark-mode-css');
    const html = document.documentElement;
    
    // Vérifier le mode préféré de l'utilisateur
    const prefersDarkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    const savedMode = localStorage.getItem('theme');
    
    // Appliquer le mode sauvegardé ou le mode système
    if (savedMode === 'dark' || (!savedMode && prefersDarkMode)) {
        enableDarkMode();
    }
    
    // Écouter les changements de préférence système
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        if (!localStorage.getItem('theme')) {
            e.matches ? enableDarkMode() : disableDarkMode();
        }
    });
    
    // Gérer le clic sur le bouton de bascule
    darkModeToggle.addEventListener('click', function() {
        if (html.getAttribute('data-theme') === 'dark') {
            disableDarkMode();
        } else {
            enableDarkMode();
        }
    });
    
    function enableDarkMode() {
        html.setAttribute('data-theme', 'dark');
        darkModeCSS.disabled = false;
        darkModeToggle.innerHTML = '<i class="bi bi-sun-fill"></i>';
        localStorage.setItem('theme', 'dark');
    }
    
    function disableDarkMode() {
        html.setAttribute('data-theme', 'light');
        darkModeCSS.disabled = true;
        darkModeToggle.innerHTML = '<i class="bi bi-moon-fill"></i>';
        localStorage.setItem('theme', 'light');
    }
});