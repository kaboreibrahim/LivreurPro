// Mon Livreur Pro — Abonnement aux notifications Web Push
(function () {
    var toggleBtn = document.getElementById('mlp-push-toggle');
    var pushSupported = ('serviceWorker' in navigator) && ('PushManager' in window) && ('Notification' in window);

    if (toggleBtn && !pushSupported) {
        toggleBtn.style.display = 'none';
    }

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function urlBase64ToUint8Array(base64String) {
        var padding = '='.repeat((4 - base64String.length % 4) % 4);
        var base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
        var rawData = window.atob(base64);
        var outputArray = new Uint8Array(rawData.length);
        for (var i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }

    function getVapidPublicKey() {
        var meta = document.querySelector('meta[name="mlp-vapid-key"]');
        return meta ? meta.content : '';
    }

    function postJSON(url, data) {
        return fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            credentials: 'same-origin',
            body: JSON.stringify(data),
        });
    }

    function setToggleState(subscribed) {
        if (!toggleBtn) return;
        toggleBtn.setAttribute('aria-pressed', subscribed ? 'true' : 'false');
        toggleBtn.classList.toggle('mlp-push-active', subscribed);
        toggleBtn.title = subscribed ? 'Désactiver les notifications push' : 'Activer les notifications push';
        toggleBtn.innerHTML = subscribed ? "<i class='bx bxs-bell-ring'></i>" : "<i class='bx bx-bell-plus'></i>";
    }

    function subscribeUser(registration) {
        var vapidKey = getVapidPublicKey();
        if (!vapidKey) {
            console.error('Clé publique VAPID manquante — impossible de s\'abonner.');
            return Promise.resolve();
        }
        return registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array(vapidKey),
        }).then(function (subscription) {
            var json = subscription.toJSON();
            return postJSON('/push/subscribe/', {
                endpoint: json.endpoint,
                keys: json.keys,
            });
        }).then(function () {
            setToggleState(true);
        });
    }

    function unsubscribeUser(subscription) {
        var endpoint = subscription.endpoint;
        return subscription.unsubscribe().then(function () {
            return postJSON('/push/unsubscribe/', { endpoint: endpoint });
        }).then(function () {
            setToggleState(false);
        });
    }

    if (toggleBtn && pushSupported) {
        // État initial du bouton — dès que le service worker est prêt, sans bloquer le clic (voir plus bas).
        navigator.serviceWorker.ready.then(function (registration) {
            return registration.pushManager.getSubscription();
        }).then(function (subscription) {
            setToggleState(!!subscription);
        }).catch(function (err) {
            console.error('Impossible de vérifier l\'état de l\'abonnement push:', err);
        });

        // Le clic est toujours actif dès le chargement de la page — il attend le service worker
        // lui-même si besoin, au lieu de dépendre d'une promesse résolue avant que l'utilisateur clique.
        toggleBtn.addEventListener('click', function (e) {
            e.stopPropagation();

            if (Notification.permission === 'denied') {
                alert('Les notifications sont bloquées pour ce site dans les réglages de votre navigateur.');
                return;
            }

            navigator.serviceWorker.ready.then(function (registration) {
                return registration.pushManager.getSubscription().then(function (currentSub) {
                    if (currentSub) {
                        return unsubscribeUser(currentSub);
                    }
                    return Notification.requestPermission().then(function (permission) {
                        if (permission === 'granted') {
                            return subscribeUser(registration);
                        }
                    });
                });
            }).catch(function (err) {
                console.error('Échec du basculement de l\'abonnement push:', err);
            });
        });
    }

    // ── Modal obligatoire ──────────────────────────────────────────────────
    // Bloque l'utilisation de l'app jusqu'à activation des notifications push.
    // Ne bloque pas si le navigateur/appareil ne supporte pas le push (rien à activer).
    var modal = document.getElementById('mlp-push-modal');
    if (modal && pushSupported) {
        var activateBtn = document.getElementById('mlp-push-modal-btn');
        var deniedBox = document.getElementById('mlp-push-modal-denied');
        var recheckBtn = document.getElementById('mlp-push-modal-recheck');
        var errorMsg = document.getElementById('mlp-push-modal-error');

        function showModal() {
            modal.classList.add('mlp-show');
            document.body.classList.add('mlp-push-modal-lock');
        }
        function hideModal() {
            modal.classList.remove('mlp-show');
            document.body.classList.remove('mlp-push-modal-lock');
        }
        function showDeniedState() {
            activateBtn.hidden = true;
            deniedBox.hidden = false;
            showModal();
        }

        navigator.serviceWorker.ready.then(function (registration) {
            return registration.pushManager.getSubscription().then(function (subscription) {
                if (subscription) {
                    // Le navigateur a déjà un abonnement actif : on s'assure qu'il est bien
                    // enregistré côté serveur (idempotent) sans rouvrir le modal.
                    var json = subscription.toJSON();
                    postJSON('/push/subscribe/', { endpoint: json.endpoint, keys: json.keys });
                    setToggleState(true);
                    return;
                }
                if (Notification.permission === 'denied') {
                    showDeniedState();
                    return;
                }
                if (Notification.permission === 'granted') {
                    // Permission déjà accordée mais aucun abonnement enregistré : on s'abonne
                    // silencieusement, sans bloquer l'utilisateur avec le modal.
                    subscribeUser(registration);
                    return;
                }
                showModal();
            });
        }).catch(function (err) {
            console.error('Impossible de vérifier l\'état des notifications:', err);
        });

        activateBtn.addEventListener('click', function () {
            navigator.serviceWorker.ready.then(function (registration) {
                return Notification.requestPermission().then(function (permission) {
                    if (permission === 'granted') {
                        return subscribeUser(registration).then(hideModal);
                    }
                    showDeniedState();
                });
            }).catch(function (err) {
                console.error('Échec de l\'activation des notifications:', err);
            });
        });

        recheckBtn.addEventListener('click', function () {
            if (Notification.permission === 'granted') {
                navigator.serviceWorker.ready.then(function (registration) {
                    return subscribeUser(registration).then(hideModal);
                });
            } else {
                errorMsg.hidden = false;
            }
        });
    }
})();
