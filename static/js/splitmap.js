// Initialize the left (all drones) map
var mapAll = L.map('map-all').setView([27.7623, -97.3246], 11);

// Initialize the right (single drone) map
var mapSingle = L.map('map-single').setView([27.7123, -97.3246], 11);

// Tile layers for both maps
L.tileLayer('https://api.maptiler.com/maps/outdoor/{z}/{x}/{y}.png?key=3TdwoUdL48yWggYAxvAE', {
    attribution: '&copy; <a href="https://www.openmaptiles.org/">OpenMapTiles</a> contributors'
}).addTo(mapAll);

L.tileLayer('https://api.maptiler.com/maps/outdoor/{z}/{x}/{y}.png?key=3TdwoUdL48yWggYAxvAE', {
    attribution: '&copy; <a href="https://www.openmaptiles.org/">OpenMapTiles</a> contributors'
}).addTo(mapSingle);

// Plane icon for markers
var planeIcon = L.icon({
    iconUrl: '/static/images/plane-icon.png', // leading slash
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -16]
});

// your four callsigns passed in via Jinja
const callsigns = JSON.parse('{{ drones | tojson | safe }}');

var droneMarkers      = {};  // markers on the all-drones map
var singleDroneMarker = null;
var selectedCallSign  = null;

// place empty markers for each drone on the left map
callsigns.forEach(cs => {
    const m = L.marker([0, 0], { icon: planeIcon })
        .addTo(mapAll)
        .bindPopup(`Drone ${cs}`)
        .on('click', () => {
            selectedCallSign = cs;
        });
    droneMarkers[cs] = m;
});

// fetch & update both maps every second
function updateMaps() {
    callsigns.forEach(cs => {
        fetch(`/data/${cs}`)
            .then(res => res.json())
            .then(history => {
                if (!Array.isArray(history) || history.length === 0) return;
                const last = history[history.length - 1];
                const { latitude: lat, longitude: lng } = last.position;

                // move left-map marker
                droneMarkers[cs].setLatLng([lat, lng]);

                // if this is the clicked drone, update the right map
                if (cs === selectedCallSign) {
                    if (!singleDroneMarker) {
                        singleDroneMarker = L.marker([lat, lng], { icon: planeIcon }).addTo(mapSingle);
                    } else {
                        singleDroneMarker.setLatLng([lat, lng]);
                    }
                    mapSingle.setView([lat, lng], 15);
                }
            })
            .catch(console.error);
    });
}

setInterval(updateMaps, 1000);
updateMaps();  // initial load

