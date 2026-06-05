// Push-Benachrichtigungen initialisieren (Service Worker Abhängig)
if ('serviceWorker' in navigator && 'PushManager' in window) {
navigator.serviceWorker.ready.then(function(registration) {
    Notification.requestPermission().then(function(permission) {
    if (permission === 'granted') {
        // Hier Push-Abo anlegen (z.B. mit VAPID-Key)
        // registration.pushManager.subscribe({userVisibleOnly: true, applicationServerKey: '<DEIN_PUBLIC_VAPID_KEY>'})
    }
    });
});
}