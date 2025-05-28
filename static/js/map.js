// Initialize map with a default center
var map = L.map('map').setView([27.7123, -97.3246], 14);

// Initialize an empty object to store drone markers
var droneMarkers = {};

// Create a custom plane icon
var planeIcon = L.icon({
    iconUrl: '/static/images/plane-icon.png', // leading slash so it always finds the file
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -16]
});

// Use an OpenMapTiles style from MapTiler
L.tileLayer('https://api.maptiler.com/maps/outdoor/{z}/{x}/{y}.png?key=3TdwoUdL48yWggYAxvAE', {
    attribution: '&copy; <a href="https://www.openmaptiles.org/">OpenMapTiles</a> contributors'
}).addTo(map);

// Fetch the latest telemetry for this drone every second
function fetchDroneData() {
    // derive the call_sign from the URL, e.g. "/drone/Disaster_City_Survey"
    const callSign = window.location.pathname.split('/').pop();

    fetch(`/data/${callSign}`)
        .then(res => res.json())
        .then(history => {
            if (!Array.isArray(history) || history.length === 0) return;
            const latest = history[history.length - 1];
            updateOrCreateMarker(latest);
        })
        .catch(console.error);
}

// Create or move the marker based on the latest packet
function updateOrCreateMarker(packet) {
    const lat = packet.position.latitude;
    const lng = packet.position.longitude;
    const cs  = packet.call_sign;

    if (!droneMarkers[cs]) {
        // first time: create
        droneMarkers[cs] = L.marker([lat, lng], { icon: planeIcon })
            .addTo(map)
            .bindPopup(`Drone ${cs}`);
    } else {
        // move existing marker
        droneMarkers[cs]
            .setLatLng([lat, lng])
            .getPopup()
            .setContent(`Drone ${cs}<br>${lat.toFixed(4)}, ${lng.toFixed(4)}`);
    }

    // keep the map centered on the drone
    map.setView([lat, lng], 15);
}

// kick off the polling
setInterval(fetchDroneData, 1000);
fetchDroneData();

