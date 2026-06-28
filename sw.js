// Lala Bahasa service worker — кэш для офлайна и установки иконки.
// Версию меняем при обновлении базы, чтобы телефон подхватил новые слова.
var CACHE = "lala-bahasa-v2";
var ASSETS = [
  "./",
  "./index.html",
  "./base.js",
  "./manifest.webmanifest",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/icon-maskable-512.png"
];

self.addEventListener("install", function(e){
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(function(c){ return c.addAll(ASSETS); }));
});

self.addEventListener("activate", function(e){
  e.waitUntil(
    caches.keys().then(function(keys){
      return Promise.all(keys.map(function(k){ if(k!==CACHE) return caches.delete(k); }));
    }).then(function(){ return self.clients.claim(); })
  );
});

// base.js — сеть в приоритете (свежая база), остальное — кэш в приоритете.
self.addEventListener("fetch", function(e){
  var url = e.request.url;
  if(url.indexOf("base.js") !== -1){
    e.respondWith(
      fetch(e.request).then(function(r){
        var copy = r.clone();
        caches.open(CACHE).then(function(c){ c.put(e.request, copy); });
        return r;
      }).catch(function(){ return caches.match(e.request); })
    );
    return;
  }
  e.respondWith(caches.match(e.request).then(function(r){ return r || fetch(e.request); }));
});
