// Mon Livreur Pro — Service Worker (PWA shell: precache, offline fallback, cache cleanup)
// Bump CACHE_VERSION whenever precached assets change to force clients to refresh their cache.
const CACHE_VERSION = 'mlp-v2';
const PRECACHE = `${CACHE_VERSION}-precache`;
const RUNTIME = `${CACHE_VERSION}-runtime`;

const OFFLINE_URL = '/offline.html';

const PRECACHE_URLS = [
  OFFLINE_URL,
  '/manifest.json',
  '/static/site/img/logo.png',
  '/static/pwa/icons/icon-72.png',
  '/static/pwa/icons/icon-96.png',
  '/static/pwa/icons/icon-128.png',
  '/static/pwa/icons/icon-144.png',
  '/static/pwa/icons/icon-152.png',
  '/static/pwa/icons/icon-192.png',
  '/static/pwa/icons/icon-384.png',
  '/static/pwa/icons/icon-512.png',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(PRECACHE)
      .then((cache) => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys
          .filter((key) => key.startsWith('mlp-') && key !== PRECACHE && key !== RUNTIME)
          .map((key) => caches.delete(key))
      ))
      .then(() => self.clients.claim())
  );
});

function isSameOrigin(url) {
  return url.origin === self.location.origin;
}

function isStaticAsset(url) {
  return isSameOrigin(url) && url.pathname.startsWith('/static/');
}

// Navigations: network-first, falling back to cache, falling back to the offline page.
async function handleNavigation(request) {
  try {
    const response = await fetch(request);
    return response;
  } catch (err) {
    const cached = await caches.match(request);
    if (cached) return cached;
    return caches.match(OFFLINE_URL);
  }
}

// Same-origin static assets: cache-first, populating the runtime cache as they're seen.
async function handleStaticAsset(request) {
  const cached = await caches.match(request);
  if (cached) return cached;
  try {
    const response = await fetch(request);
    if (response && response.ok) {
      const cache = await caches.open(RUNTIME);
      cache.put(request, response.clone());
    }
    return response;
  } catch (err) {
    return cached || Response.error();
  }
}

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);

  if (request.mode === 'navigate') {
    event.respondWith(handleNavigation(request));
    return;
  }

  if (isStaticAsset(url)) {
    event.respondWith(handleStaticAsset(request));
  }
});

// ── Web Push ────────────────────────────────────────────────────────────
self.addEventListener('push', (event) => {
  let data = {};
  if (event.data) {
    try {
      data = event.data.json();
    } catch (err) {
      data = { title: 'Mon Livreur Pro', body: event.data.text() };
    }
  }

  const title = data.title || 'Mon Livreur Pro';
  const options = {
    body: data.body || '',
    icon: data.icon || '/static/pwa/icons/icon-192.png',
    badge: data.badge || '/static/pwa/icons/icon-96.png',
    image: data.image || undefined,
    tag: data.tag || undefined,
    renotify: !!data.renotify,
    timestamp: data.timestamp || Date.now(),
    actions: data.actions || [],
    data: { url: data.url || '/' },
  };

  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const url = (event.notification.data && event.notification.data.url) || '/';

  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      for (const client of clientList) {
        if (client.url === url && 'focus' in client) {
          return client.focus();
        }
      }
      if (self.clients.openWindow) {
        return self.clients.openWindow(url);
      }
    })
  );
});

self.addEventListener('notificationclose', (event) => {
  // Pas de suivi côté serveur pour l'instant — utile en dev pour vérifier que l'événement se déclenche.
  console.debug('Notification fermée:', event.notification.tag);
});
