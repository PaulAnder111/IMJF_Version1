// theme.js

// =============================================
// GESTION DU MODE SOMBRE/CLAIR
// =============================================
const darkModeKey = 'imjf_dark_mode';
const body = document.body;
const sidebar = document.getElementById('sidebar');
const modeText = document.getElementById('modeText');

function loadDarkModePreference() {
    const isDark = localStorage.getItem(darkModeKey) === 'true';
    if (isDark) {
        enableDarkMode();
    } else {
        enableLightMode();
    }
}

function enableDarkMode() {
    body.classList.remove('light-mode');
    body.classList.add('dark-mode');
    sidebar.classList.remove('sidebar-light');
    sidebar.classList.add('sidebar-dark');
    
    document.querySelectorAll('.header-light').forEach(el => {
        el.classList.remove('header-light');
        el.classList.add('header-dark');
    });
    
    document.querySelectorAll('.menu-item-light').forEach(item => {
        item.classList.remove('menu-item-light');
        item.classList.add('menu-item-dark');
    });
    
    document.querySelectorAll('.menu-icon-light').forEach(icon => {
        icon.classList.remove('menu-icon-light');
        icon.classList.add('menu-icon-dark');
    });
    
    modeText.textContent = 'Clair';
    localStorage.setItem(darkModeKey, 'true');
    
    // Mettre à jour les classes dynamiques
    updateDynamicClasses();
}

function enableLightMode() {
    body.classList.remove('dark-mode');
    body.classList.add('light-mode');
    sidebar.classList.remove('sidebar-dark');
    sidebar.classList.add('sidebar-light');
    
    document.querySelectorAll('.header-dark').forEach(el => {
        el.classList.remove('header-dark');
        el.classList.add('header-light');
    });
    
    document.querySelectorAll('.menu-item-dark').forEach(item => {
        item.classList.remove('menu-item-dark');
        item.classList.add('menu-item-light');
    });
    
    document.querySelectorAll('.menu-icon-dark').forEach(icon => {
        icon.classList.remove('menu-icon-dark');
        icon.classList.add('menu-icon-light');
    });
    
    modeText.textContent = 'Sombre';
    localStorage.setItem(darkModeKey, 'false');
    
    // Mettre à jour les classes dynamiques
    updateDynamicClasses();
}

// =============================================
// FONCTIONS POUR METTRE À JOUR LES CLASSES DYNAMIQUES
// =============================================

function updateDynamicClasses() {
    const isDark = body.classList.contains('dark-mode');
    
    // Mettre à jour les tableaux
    document.querySelectorAll('table').forEach(table => {
        if (!table.closest('.modal-content')) {
            table.className = isDark ? 
                'table-dark w-full rounded-lg overflow-hidden' : 
                'table-light w-full rounded-lg overflow-hidden';
        }
    });
    
    // Mettre à jour les en-têtes de tableau
    document.querySelectorAll('th').forEach(th => {
        th.className = isDark ? 
            'table-header-dark px-4 py-3 text-left font-semibold' : 
            'table-header-light px-4 py-3 text-left font-semibold';
    });
    
    // Mettre à jour les lignes de tableau
    document.querySelectorAll('tbody tr').forEach(tr => {
        if (!tr.closest('.modal-content')) {
            tr.className = isDark ? 
                'table-row-dark border-b border-gray-700' : 
                'table-row-light border-b border-gray-200';
        }
    });
    
    // Mettre à jour les cellules de tableau
    document.querySelectorAll('td').forEach(td => {
        td.className = isDark ? 
            'table-cell-dark px-4 py-3' : 
            'table-cell-light px-4 py-3';
    });
    
    // Mettre à jour les conteneurs de formulaire
    document.querySelectorAll('form').forEach(form => {
        if (!form.closest('.modal-content') && !form.id.includes('photoForm')) {
            form.className = isDark ? 
                'form-container-dark rounded-xl p-6 space-y-4' : 
                'form-container-light rounded-xl p-6 space-y-4';
        }
    });
    
    // Mettre à jour les labels
    document.querySelectorAll('label').forEach(label => {
        if (!label.closest('.modal-content')) {
            label.className = isDark ? 
                'form-label-dark block text-sm font-semibold mb-2' : 
                'form-label-light block text-sm font-semibold mb-2';
        }
    });
    
    // Mettre à jour les inputs
    document.querySelectorAll('input, select, textarea').forEach(input => {
        if (!input.closest('.modal-content') && input.type !== 'file') {
            input.className = isDark ? 
                'form-input-dark w-full px-4 py-2 rounded-lg focus:outline-none focus:ring-2' : 
                'form-input-light w-full px-4 py-2 rounded-lg focus:outline-none focus:ring-2';
        }
    });
    
    // Mettre à jour les cartes
    document.querySelectorAll('.card').forEach(card => {
        card.className = isDark ? 
            'card-dark rounded-xl p-6 shadow-lg' : 
            'card-light rounded-xl p-6 shadow-lg';
    });
    
    // Mettre à jour les boutons primaires
    document.querySelectorAll('.btn-primary').forEach(btn => {
        btn.className = isDark ? 
            'btn-primary-dark px-6 py-2 rounded-lg transition shadow-lg' : 
            'btn-primary-light px-6 py-2 rounded-lg transition shadow-lg';
    });
}

// Exporter les fonctions si nécessaire
window.loadDarkModePreference = loadDarkModePreference;
window.enableDarkMode = enableDarkMode;
window.enableLightMode = enableLightMode;
window.updateDynamicClasses = updateDynamicClasses;