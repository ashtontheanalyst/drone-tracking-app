// splitmap.js — Replaces map.js, shows ALL drones on one map

// Initialize map centered at a default location
var map = L.map('map-all').setView([27.7123, -97.3246], 14);

const drones = window.droneCallSigns;//gets all callsigns passed into class

// Store markers keyed by drone call sign
var droneMarkers = {};

// Custom plane icon
var planeIcon = L.icon({
    iconUrl: '/static/images/plane-icon.png',
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -16]
});

// Load map tiles
L.tileLayer('https://api.maptiler.com/maps/outdoor/{z}/{x}/{y}.png?key=3TdwoUdL48yWggYAxvAE', {
    attribution: '&copy; <a href="https://www.openmaptiles.org/">OpenMapTiles</a> contributors'
}).addTo(map);

// Fetch data for all drones
function fetchAllDrones() {
    drones.forEach(callSign => {
        fetch(`/data/${callSign}`)
            .then(res => res.json())
            .then(history => {
                if (!Array.isArray(history) || history.length === 0) return;
                const latest = history[history.length - 1];
                updateMarker(latest);
            })
            .catch(console.error);
    });
}

// Add or update a drone marker
function updateMarker(packet) {
    const lat = packet.position.latitude;
    const lng = packet.position.longitude;
    const cs  = packet.call_sign;

    if (!lat || !lng) return;

    if (!droneMarkers[cs]) {
        droneMarkers[cs] = L.marker([lat, lng], { icon: planeIcon })
            .addTo(map)
            .bindPopup(`Drone ${cs}`);
    } else {
        droneMarkers[cs]
            .setLatLng([lat, lng])
            .getPopup()
            .setContent(`Drone ${cs}<br>${lat.toFixed(4)}, ${lng.toFixed(4)}`);
    }

    // After updating or adding, try to fit bounds
    const bounds = L.latLngBounds(
        Object.values(droneMarkers).map(marker => marker.getLatLng())
    );

    if (bounds.isValid()) {
        map.fitBounds(bounds, { padding: [50, 50], maxZoom: 16 });
    }
}


setInterval(fetchAllDrones, 1000);
fetchAllDrones();
