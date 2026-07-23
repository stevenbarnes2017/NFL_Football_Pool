console.log("Notification JS loaded");

async function registerPush() {

    if (!("serviceWorker" in navigator)) {
        console.log("Service workers not supported.");
        return;
    }

    try {
        const registration = await navigator.serviceWorker.register(
            "/static/service-worker.js"
        );

        console.log("Service Worker registered.");

        const permission = await Notification.requestPermission();

        console.log("Permission:", permission);

        if (permission !== "granted") {
            console.log("Notification permission denied.");
            return;
        }

        let subscription = await registration.pushManager.getSubscription();

        if (!subscription) {

            subscription = await registration.pushManager.subscribe({

                userVisibleOnly: true,

                applicationServerKey:
                    urlBase64ToUint8Array(window.VAPID_PUBLIC_KEY)

            });

            console.log("New push subscription created.");

        } else {

            console.log("Existing push subscription found.");

        }


        console.log(subscription);


        const response = await fetch("/notifications/subscribe", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(subscription)

        });


        const result = await response.json();

        console.log("Subscription saved:", result);


    } catch (error) {

        console.error(
            "Push registration failed:",
            error
        );

    }
}


registerPush();



function urlBase64ToUint8Array(base64String) {

    const padding = "=".repeat(
        (4 - base64String.length % 4) % 4
    );

    const base64 = (base64String + padding)
        .replace(/-/g, "+")
        .replace(/_/g, "/");


    const rawData = window.atob(base64);


    return Uint8Array.from(
        [...rawData].map(
            char => char.charCodeAt(0)
        )
    );
}