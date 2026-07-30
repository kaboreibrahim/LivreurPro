// Mon Livreur Pro — PWA: service worker registration + install banner
(function () {
    var SW_URL = '/service-worker.js';
    var LS_INSTALLED_KEY = 'mlp_pwa_installed';
    var SS_DISMISSED_KEY = 'mlp_pwa_dismissed';

    // ---- Service worker registration ----
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function () {
            navigator.serviceWorker.register(SW_URL, { scope: '/' }).catch(function (err) {
                console.error('Échec de l\'enregistrement du service worker:', err);
            });
        });
    }

    // ---- Install banner ----
    var banner = document.getElementById('mlp-install-banner');
    if (!banner) return;

    var installBtn = document.getElementById('mlp-install-btn');
    var dismissBtn = document.getElementById('mlp-install-dismiss');
    var msgEl = document.getElementById('mlp-install-banner-msg');
    var deferredPrompt = null;

    function isStandalone() {
        return window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;
    }

    function isIOS() {
        return /iphone|ipad|ipod/i.test(window.navigator.userAgent) && !window.MSStream;
    }

    function hideBanner() {
        banner.classList.remove('mlp-show');
    }

    function showBanner() {
        if (isStandalone()) return;
        if (localStorage.getItem(LS_INSTALLED_KEY) === '1') return;
        if (sessionStorage.getItem(SS_DISMISSED_KEY) === '1') return;
        banner.classList.add('mlp-show');
    }

    if (isStandalone()) {
        // Already installed/running standalone — remember it, never show the banner again.
        localStorage.setItem(LS_INSTALLED_KEY, '1');
    } else if (isIOS()) {
        // Safari has no beforeinstallprompt — show the manual "Add to Home Screen" instructions.
        banner.classList.add('mlp-ios');
        if (msgEl) {
            msgEl.textContent = 'Pour installer cette application, utilisez Partager puis "Ajouter à l’écran d’accueil".';
        }
        showBanner();
    }

    window.addEventListener('beforeinstallprompt', function (e) {
        e.preventDefault();
        deferredPrompt = e;
        showBanner();
    });

    if (installBtn) {
        installBtn.addEventListener('click', function () {
            if (!deferredPrompt) return;
            deferredPrompt.prompt();
            deferredPrompt.userChoice.finally(function () {
                deferredPrompt = null;
                hideBanner();
            });
        });
    }

    if (dismissBtn) {
        dismissBtn.addEventListener('click', function () {
            sessionStorage.setItem(SS_DISMISSED_KEY, '1');
            hideBanner();
        });
    }

    window.addEventListener('appinstalled', function () {
        localStorage.setItem(LS_INSTALLED_KEY, '1');
        hideBanner();
    });
})();
