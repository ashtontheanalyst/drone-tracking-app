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
    iconUrl: 'static/images/plane-icon.png',
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -16]
});

var droneMarkers = {};         // For all drones on left map
var singleDroneMarker = null;  // For selected drone on right map
var selectedDroneCallsign = null; // Store currently selected drone

// Fetch all drone data for the left map
function fetchAllDrones() {
    fetch('/drone-data')
        .then(res => res.json())
        .then(data => {
            if (Array.isArray(data)) {
                data.forEach(drone => {
                    if (!droneMarkers[drone.call_sign]) {
                        // Create new marker
                        let marker = L.marker([drone.latitude, drone.longitude], { icon: planeIcon }).addTo(mapAll);
                        marker.bindPopup(`Drone ${drone.call_sign}`);
                        marker.on('click', () => {
                            selectedDroneCallsign = drone.call_sign;
                            updateSingleDrone(drone);
                        });
                        droneMarkers[drone.call_sign] = marker;
                    } else {
                        // Update existing marker
                        droneMarkers[drone.call_sign].setLatLng([drone.latitude, drone.longitude]);
                    }

                    // If it's the selected drone, update the right map
                    if (drone.call_sign === selectedDroneCallsign) {
                        updateSingleDrone(drone);
                    }
                });
            }
        })
        .catch(err => console.error("Error fetching all drones:", err));
}

// Update the right map with a specific drone
function updateSingleDrone(drone) {
    if (!singleDroneMarker) {
        singleDroneMarker = L.marker([drone.latitude, drone.longitude], { icon: planeIcon }).addTo(mapSingle);
    } else {
        singleDroneMarker.setLatLng([drone.latitude, drone.longitude]);
    }

    mapSingle.setView([drone.latitude, drone.longitude], 15);
}

// Start updating every 4 seconds
setInterval(fetchAllDrones, 4000);
fetchAllDrones(); // Initial load
