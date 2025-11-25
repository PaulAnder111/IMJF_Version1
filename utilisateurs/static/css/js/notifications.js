// notifications.js

const NOTIFICATION_REFRESH_INTERVAL = 30000; // 30 secondes

// =============================================
// SYSTÈME DE NOTIFICATIONS
// =============================================
async function loadNotifications() {
    try {
        const response = await fetch('/utilisateurs/get_notifications/'); // Assurez-vous que l'URL est correcte
        if (!response.ok) throw new Error('Erreur réseau');
        
        const data = await response.json();
        updateNotificationUI(data);
    } catch (error) {
        console.error('Erreur lors du chargement des notifications:', error);
        showNotificationError();
    }
}

function updateNotificationUI(data) {
    const notificationList = document.getElementById('notificationList');
    const notificationBadge = document.getElementById('notificationBadge');
    const notificationCount = document.getElementById('notificationCount');
    const markAllReadBtn = document.getElementById('markAllRead');
    
    const unreadCount = data.unread_count || 0;
    const notifications = data.notifications || [];
    
    // Mettre à jour le badge
    if (notificationBadge) {
        if (unreadCount > 0) {
            notificationBadge.textContent = unreadCount > 99 ? '99+' : unreadCount;
            notificationBadge.classList.remove('hidden');
        } else {
            notificationBadge.classList.add('hidden');
        }
    }
    
    // Mettre à jour le compteur
    if (notificationCount) {
        notificationCount.textContent = `${unreadCount} nouvelle${unreadCount > 1 ? 's' : ''}`;
    }
    
    // Activer/désactiver le bouton "Marquer tout comme lu"
    if (markAllReadBtn) {
        if (unreadCount > 0) {
            markAllReadBtn.disabled = false;
            markAllReadBtn.classList.remove('disabled:opacity-50');
        } else {
            markAllReadBtn.disabled = true;
            markAllReadBtn.classList.add('disabled:opacity-50');
        }
    }
    
    // Afficher les notifications
    if (notifications.length === 0) {
        notificationList.innerHTML = `
            <div class="text-center py-8 text-gray-500 dark:text-gray-400">
                <i class="fas fa-bell-slash text-3xl mb-2"></i>
                <p class="text-sm">Aucune notification</p>
            </div>
        `;
        return;
    }
    
    notificationList.innerHTML = notifications.map(notification => `
        <div class="notification-item ${notification.type} ${!notification.read ? 'unread' : ''} p-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer transition" 
             onclick="handleNotificationClick('${notification.id}', '${notification.target_url}')" data-id="${notification.id}">
            <div class="flex items-start gap-3">
                <div class="w-8 h-8 rounded-full flex items-center justify-center ${getNotificationIconClass(notification)} mt-1">
                    <i class="${getNotificationIcon(notification)} text-sm"></i>
                </div>
                <div class="flex-1">
                    <p class="text-sm font-semibold text-gray-800 dark:text-white">${escapeHtml(notification.title)}</p>
                    <p class="text-xs text-gray-600 dark:text-gray-300 mt-1">${escapeHtml(notification.message)}</p>
                    <div class="flex items-center justify-between mt-2">
                        <span class="text-xs text-gray-500 dark:text-gray-400">${formatTime(notification.timestamp)}</span>
                        ${!notification.read ? '<span class="w-2 h-2 bg-blue-500 rounded-full"></span>' : ''}
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

function showNotificationError() {
    const notificationList = document.getElementById('notificationList');
    notificationList.innerHTML = `
        <div class="text-center py-8 text-gray-500 dark:text-gray-400">
            <i class="fas fa-exclamation-triangle text-3xl mb-2 text-red-500"></i>
            <p class="text-sm">Erreur de chargement</p>
            <button onclick="loadNotifications()" class="text-yellow-600 text-xs mt-2 hover:underline">
                Réessayer
            </button>
        </div>
    `;
}

async function handleNotificationClick(notificationId, targetUrl) {
    await markAsRead(notificationId);
    
    // Rediriger si c'est une notification cliquable
    if (targetUrl && targetUrl !== '#' && targetUrl !== 'null') {
        window.location.href = targetUrl;
    }
}

async function markAsRead(notificationId) {
    try {
        const response = await fetch(`/utilisateurs/mark_notification_read/${notificationId}/`, {
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
        console.error('Erreur lors du marquage comme lu:', error);
    }
}

// Fonctions utilitaires pour les notifications
function getNotificationIcon(notification) {
    const icons = {
        'inscription': 'fas fa-user-plus',
        'action_secretaire': 'fas fa-user-edit',
        'action_archives': 'fas fa-archive',
        'connexion': 'fas fa-sign-in-alt',
        'deconnexion': 'fas fa-sign-out-alt',
        'systeme': 'fas fa-cog',
        'validation': 'fas fa-check-circle'
    };
    return icons[notification.type] || 'fas fa-bell';
}

function getNotificationIconClass(notification) {
    const classes = {
        'inscription': 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400',
        'action_secretaire': 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400',
        'action_archives': 'bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400',
        'connexion': 'bg-yellow-100 text-yellow-600 dark:bg-yellow-900/30 dark:text-yellow-400',
        'deconnexion': 'bg-orange-100 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400',
        'systeme': 'bg-gray-100 text-gray-600 dark:bg-gray-900/30 dark:text-gray-400',
        'validation': 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400'
    };
    return classes[notification.type] || 'bg-gray-100 text-gray-600 dark:bg-gray-900/30 dark:text-gray-400';
}

function formatTime(timestamp) {
    try {
        const now = new Date();
        const notificationTime = new Date(timestamp);
        const diff = now - notificationTime;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);

        if (minutes < 1) return 'À l\'instant';
        if (minutes < 60) return `Il y a ${minutes} min`;
        if (hours < 24) return `Il y a ${hours} h`;
        if (days < 7) return `Il y a ${days} j`;
        return notificationTime.toLocaleDateString();
    } catch (e) {
        return 'Date inconnue';
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getCSRFToken() {
    return document.querySelector('[name=csrf-token]').content;
}

// Exporter les fonctions
window.loadNotifications = loadNotifications;
window.handleNotificationClick = handleNotificationClick;