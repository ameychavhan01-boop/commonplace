/* Commonplace service worker: caches the app files so it opens without internet.
   It never touches your cards; those live in IndexedDB. */
const CACHE = 'commonplace-app-v0.2.0';
const FILES = ['./', './index.html', './manifest.webmanifest', './icon-180.png', './icon-192.png', './icon-512.png', './icon-maskable-512.png'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(FILES)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys()
    .then((keys) => Promise.all(keys.filter((k) => k.startsWith('commonplace-app-') && k !== CACHE).map((k) => caches.delete(k))))
    .then(() => self.clients.claim()));
});
/* Answer from the cache first (works offline), then refresh the cache in the background
   so the next launch gets any update you uploaded. */
self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== self.location.origin) return;
  const key = req.mode === 'navigate' ? './index.html' : req;
  e.respondWith(caches.open(CACHE).then(async (cache) => {
    const cached = await cache.match(key, { ignoreSearch: true });
    const fresh = fetch(req).then((res) => {
      if (res && res.ok && res.type === 'basic') cache.put(key, res.clone());
      return res;
    }).catch(() => null);
    if (cached) { e.waitUntil(fresh); return cached; }
    const res = await fresh;
    return res || new Response('Commonplace is offline and this file is not cached yet.', { status: 503, headers: { 'Content-Type': 'text/plain' } });
  }));
});
