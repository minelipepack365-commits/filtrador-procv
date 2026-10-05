/* Service worker do Filtrador PROCV.
 *
 * Estrategia: precache do app shell (index.html + SheetJS + icones) para o app
 * abrir e funcionar offline; navegacoes usam network-first com fallback para
 * o index.html em cache.
 *
 * Bump em CACHE_VERSION a cada mudanca no app para forcar a atualizacao.
 */

const CACHE_VERSION = 'filtrador-procv-v1';

const PRECACHE = [
  './',
  './index.html',
  './manifest.webmanifest',
  './favicon.png',
  './icons/favicon-32.png',
  './icons/apple-touch-icon.png',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/maskable-512.png',
  './xlsx.full.min.js'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_VERSION)
      .then(cache => cache.addAll(PRECACHE))
      .then(() => self.skipWaiting())
      .catch(err => console.warn('[sw] precache parcial:', err))
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys.filter(k => k !== CACHE_VERSION).map(k => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const req = event.request;

  if (req.method !== 'GET') return;

  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  // google.script.run do Apps Script nunca deve ser servido do cache.
  if (url.pathname.includes('/google.script.run')) return;

  // Navegacao: rede primeiro, cache como reserva (permite abrir offline).
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req)
        .then(res => {
          const copy = res.clone();
          caches.open(CACHE_VERSION).then(c => c.put(req, copy));
          return res;
        })
        .catch(() => caches.match(req)
          .then(r => r || caches.match('./index.html')))
    );
    return;
  }

  // Demais recursos: cache primeiro, revalidando em segundo plano.
  event.respondWith(
    caches.match(req).then(cached => {
      const network = fetch(req)
        .then(res => {
          if (res && res.ok && res.type === 'basic') {
            const copy = res.clone();
            caches.open(CACHE_VERSION).then(c => c.put(req, copy));
          }
          return res;
        })
        .catch(() => cached);

      return cached || network;
    })
  );
});

self.addEventListener('message', event => {
  if (event.data === 'skip-waiting') self.skipWaiting();
});