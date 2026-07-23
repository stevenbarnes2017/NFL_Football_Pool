// service-worker.js

console.log("Sunday Pickems service worker loaded.");

self.addEventListener("install", (event) => {
    console.log("Service Worker installed.");
    self.skipWaiting();
});

self.addEventListener("activate", (event) => {
    console.log("Service Worker activated.");
    event.waitUntil(self.clients.claim());
});

self.addEventListener("push", event => {
    const data = event.data.json();
    event.waitUntil(
        self.registration.showNotification(
            data.title,
            {
                body: data.body,
                icon: data.icon
            }
        )
    );
});