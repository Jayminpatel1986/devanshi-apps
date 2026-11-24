const CACHE_VER = 'devanshi-erp-24-11-2026-001';
self.addEventListener('install', function(e) { self.skipWaiting(); });
self.addEventListener('activate', function(e) {
    e.waitUntil(caches.keys().then(function(keys) {
        return Promise.all(keys.filter(function(k){ return k !== CACHE_VER; }).map(function(k){ return caches.delete(k); }));
    }));
    self.clients.claim();
});
self.addEventListener('fetch', function(e) {
    if (e.request.method !== 'GET') return;
    e.respondWith(fetch(e.request).catch(function() { return caches.match(e.request); }));
});
