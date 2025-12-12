// Fonction pour fermer automatiquement les notifications après un délai
function setupNotifications() {
    const notifications = document.querySelectorAll('.notification');
    
    notifications.forEach((notification, index) => {
        // Délai avant de commencer à fermer (en ms)
        const delay = 5000 + (index * 300);
        
        // Fermeture automatique après le délai
        const timeoutId = setTimeout(() => {
            notification.style.animation = 'slideOut 0.5s forwards';
            setTimeout(() => notification.remove(), 500);
        }, delay);
        
        // Annuler la fermeture automatique si la souris est sur la notification
        notification.addEventListener('mouseenter', () => {
            clearTimeout(timeoutId);
        });
        
        // Redémarrer le timer quand la souris quitte la notification
        notification.addEventListener('mouseleave', () => {
            setTimeout(() => {
                notification.style.animation = 'slideOut 0.5s forwards';
                setTimeout(() => notification.remove(), 500);
            }, 3000);
        });
    });
}

// Initialiser les notifications au chargement du DOM
document.addEventListener('DOMContentLoaded', setupNotifications);
