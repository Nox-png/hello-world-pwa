/* web/static/pwa/serviceworker.js */

const CACHE_VERSION = "v1.0.0";
const STATIC_CACHE = `static-${CACHE_VERSION}`;
const DYNAMIC_CACHE = `dynamic-${CACHE_VERSION}`;

const staticAssets = [
  "/",
  "/static/images/favicon.png",
];

function isCacheableRequest(request) {
  const requestUrl = new URL(request.url);

  return (
    request.method === "GET" &&
    (requestUrl.protocol === "http:" || requestUrl.protocol === "https:")
  );
}

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then(cache => cache.addAll(staticAssets))
  );

  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(cacheKeys =>
      Promise.all(
        cacheKeys
          .filter(cacheKey => !cacheKey.includes(CACHE_VERSION))
          .map(cacheKey => caches.delete(cacheKey))
      )
    )
  );

  self.clients.claim();
});

self.addEventListener("fetch", event => {
  const { request } = event;

  if (!isCacheableRequest(request)) {
    return;
  }

  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request)
        .then(response => {
          const responseClone = response.clone();

          caches.open(DYNAMIC_CACHE).then(cache => {
            cache.put(request, responseClone);
          });

          return response;
        })
        .catch(() =>
          caches.match(request).then(cachedResponse => {
            return cachedResponse || caches.match("/offline/");
          })
        )
    );

    return;
  }

  event.respondWith(
    fetch(request)
      .then(response => {
        const responseClone = response.clone();

        caches.open(DYNAMIC_CACHE).then(cache => {
          cache.put(request, responseClone);
        });

        return response;
      })
      .catch(() => caches.match(request))
  );
});

self.addEventListener("push", event => {
  let notificationData = {};

  if (event.data) {
    try {
      notificationData = event.data.json();
    } catch (error) {
      notificationData = {
        body: event.data.text(),
      };
    }
  }

  const title = notificationData.title || "Neue Benachrichtigung";

  const options = {
    body: notificationData.body || "Du hast eine neue Nachricht erhalten.",
    icon: "/static/images/favicon.png",
    badge: "/static/images/favicon.png",
  };

  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});