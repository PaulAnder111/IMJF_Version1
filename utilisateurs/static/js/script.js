// script.js

// =============================================
// CONFIGURATION DE BASE
// =============================================
const mobileOverlay = document.getElementById('mobileOverlay');

// =============================================
// GESTION DE LA SIDEBAR
// =============================================
const sidebarToggle = document.getElementById('sidebarToggle');
const mainContent = document.getElementById('mainContent');

function toggleSidebar() {
    const isMobile = window.innerWidth < 768;
    
    if (isMobile) {
        sidebar.classList.toggle('sidebar-expanded');
        sidebar.classList.toggle('sidebar-collapsed');
        mobileOverlay.classList.toggle('hidden');
    } else {
        sidebar.classList.toggle('sidebar-collapsed');
        sidebar.classList.toggle('sidebar-expanded');
        mainContent.classList.toggle('content-collapsed');
        mainContent.classList.toggle('content-expanded');
    }
}

if (sidebarToggle) {
    sidebarToggle.addEventListener('click', toggleSidebar);
}

if (mobileOverlay) {
    mobileOverlay.addEventListener('click', () => {
        if (window.innerWidth < 768) {
            sidebar.classList.remove('sidebar-expanded');
            sidebar.classList.add('sidebar-collapsed');
            mobileOverlay.classList.add('hidden');
        }
    });
}

// =============================================
// GESTION DES DROPDOWNS
// =============================================
const avatarBtn = document.getElementById('avatarBtn');
const avatarDropdown = document.getElementById('avatarDropdown');
const notificationBtn = document.getElementById('notificationBtn');
const notificationDropdown = document.getElementById('notificationDropdown');

// Avatar dropdown
if (avatarBtn) {
    avatarBtn.addEventListener('click', (e)=>{ 
        e.stopPropagation();
        avatarDropdown.classList.toggle('hidden'); 
    });
}

// Notification dropdown
if (notificationBtn) {
    notificationBtn.addEventListener('click', (e)=>{ 
        e.stopPropagation();
        notificationDropdown.classList.toggle('hidden'); 
        if (!notificationDropdown.classList.contains('hidden')) {
            loadNotifications();
        }
    });
}

// Fermer dropdowns si clic ailleurs
document.addEventListener('click', (e) => {
    if (avatarDropdown && !avatarDropdown.contains(e.target) && !avatarBtn.contains(e.target)) {
        avatarDropdown.classList.add('hidden');
    }
    if (notificationDropdown && !notificationDropdown.contains(e.target) && !notificationBtn?.contains(e.target)) {
        notificationDropdown.classList.add('hidden');
    }
});

// =============================================
// GESTION DES MODALS
// =============================================
const modalProfile = document.getElementById('modalProfile');
const modalPhoto = document.getElementById('modalPhoto');
const modalPassword = document.getElementById('modalPassword');

document.getElementById('modalProfileBtn')?.addEventListener('click', ()=>{ 
    modalProfile.classList.remove('hidden'); 
    avatarDropdown.classList.add('hidden'); 
});

document.getElementById('modalPhotoBtn')?.addEventListener('click', () => {
    modalPhoto.classList.remove('hidden');
    avatarDropdown.classList.add('hidden');
});

document.getElementById('modalPasswordBtn')?.addEventListener('click', ()=>{ 
    modalPassword.classList.remove('hidden'); 
    avatarDropdown.classList.add('hidden'); 
});

function closeModal(id){ 
    document.getElementById(id).classList.add('hidden'); 
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal-bg').forEach(modal => {
            modal.classList.add('hidden');
        });
    }
});

// =============================================
// GESTION DE LA PHOTO DE PROFIL
// =============================================
const photoInput = document.getElementById('photoInput');
const previewPhoto = document.getElementById('previewPhoto');
if (photoInput) {
    photoInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            if (file.size > 5 * 1024 * 1024) {
                alert('Le fichier est trop volumineux. Taille maximale: 5MB');
                photoInput.value = '';
                return;
            }
            
            const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
            if (!validTypes.includes(file.type)) {
                alert('Format de fichier non supporté. Utilisez JPG, JPEG ou PNG.');
                photoInput.value = '';
                return;
            }
            
            const reader = new FileReader();
            reader.onload = (e) => {
                previewPhoto.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    });
}

const photoForm = document.getElementById('photoForm');
if (photoForm) {
    photoForm.addEventListener('submit', function(e) {
        const fileInput = document.getElementById('photoInput');
        if (!fileInput.files || fileInput.files.length === 0) {
            e.preventDefault();
            alert('Veuillez sélectionner une photo.');
            return false;
        }
    });
}

// =============================================
// FONCTIONS UTILITAIRES
// =============================================
function getGreeting() {
    const hour = new Date().getHours();
    let greetingText = '';
    
    if (hour >= 5 && hour < 12) {
        greetingText = "☀️ Bon matin";
    } else if (hour >= 12 && hour < 18) {
        greetingText = "🌤️ Bon après-midi";
    } else {
        greetingText = "🌙 Bonsoir";
    }
    
    return `${greetingText}, <strong>${document.body.getAttribute('data-user-first-name') || 'Utilisateur'}</strong>!`;
}

// Appliquer le greeting
const greetingElement = document.getElementById('greeting');
if (greetingElement) {
    greetingElement.innerHTML = getGreeting();
}

// Highlight active menu
const currentPath = window.location.pathname;
document.querySelectorAll('aside a').forEach(link => {
    if (link.getAttribute('href') === currentPath) {
        link.classList.add('active');
    }
});

// Fermer sidebar quand on clique sur un lien (mobile)
document.querySelectorAll('aside a').forEach(link => {
    link.addEventListener('click', () => {
        if (window.innerWidth < 768) {
            sidebar.classList.remove('sidebar-expanded');
            sidebar.classList.add('sidebar-collapsed');
            mobileOverlay.classList.add('hidden');
        }
    });
});

// =============================================
// ÉVÉNEMENTS DE MODE SOMBRE/CLAIR
// =============================================
document.getElementById('darkModeBtn')?.addEventListener('click', ()=>{
    const isDark = body.classList.contains('dark-mode');
    if (isDark) {
        enableLightMode();
    } else {
        enableDarkMode();
    }
    
    // Forcer la mise à jour des classes
    setTimeout(updateDynamicClasses, 100);
});

// =============================================
// MARQUER TOUTES LES NOTIFICATIONS COMME LUES
// =============================================
document.getElementById('markAllRead')?.addEventListener('click', async function() {
    try {
        const response = await fetch('/utilisateurs/mark_all_notifications_read/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json',
            },
        });
        
        const data = await response.json();
        if (data.success) {
            await loadNotifications();
        }
    } catch (error) {
        console.error('Erreur lors du marquage de toutes les notifications:', error);
    }
});

// =============================================
// INITIALISATION
// =============================================
document.addEventListener('DOMContentLoaded', function() {
    // Charger le mode sombre/clair
    loadDarkModePreference();
    
    // Appliquer les classes dynamiques après le chargement
    setTimeout(updateDynamicClasses, 500);
    
    // Re-appliquer après un délai pour les éléments chargés dynamiquement
    setTimeout(updateDynamicClasses, 1000);

    // Charger les notifications si l'utilisateur est admin ou directeur
    const userRole = document.body.getAttribute('data-user-role');
    if (userRole === 'admin' || userRole === 'directeur') {
        loadNotifications();
        
        // Recharger périodiquement
        setInterval(loadNotifications, NOTIFICATION_REFRESH_INTERVAL);
    }
});

// Exporter les fonctions
window.toggleSidebar = toggleSidebar;
window.closeModal = closeModal;