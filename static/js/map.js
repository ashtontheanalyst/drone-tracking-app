// Initialize map with a default center
var map = L.map('map').setView([27.7123, -97.3246], 14);

// Initialize an empty object to store drone markers
var droneMarkers = {};

// Create a custom plane icon
var planeIcon = L.icon({
    iconUrl: 'static/images/plane-icon.png', // Path to the plane icon image
    iconSize: [32, 32], // Adjust the size of the icon
    iconAnchor: [16, 16], // Anchor point of the icon
    popupAnchor: [0, -16] // Where the popup should appear relative to the icon
});

// Use an OpenMapTiles style from MapTiler
L.tileLayer('https://api.maptiler.com/maps/outdoor/{z}/{x}/{y}.png?key=3TdwoUdL48yWggYAxvAE', {
    attribution: '&copy; <a href="https://www.openmaptiles.org/">OpenMapTiles</a> contributors'
}).addTo(map);

// Function to determine which drone(s) to track
function fetchDroneData() {
    let url = window.location.pathname;  // Get current page URL
    let endpoint = "/drone-data";  // Default to all drones

    if (url === "/droneA") {
        endpoint = "/droneA-data";  // Only fetch Drone 1's data
    }

    if (url === "/droneB") {
        endpoint = "/droneB-data";  // Only fetch Drone 2's data
    }

    if (url === "/droneJ") {
        endpoint = "/droneJ-data";  // Fetch Drone J's data
    }

    fetch(endpoint)
        .then(response => response.json())
        .then(data => {
            // If it's an array (multiple drones), process them all
            if (Array.isArray(data)) {
                data.forEach(updateOrCreateMarker);
            } else {
                // Otherwise, it's a single drone
                updateOrCreateMarker(data);
            }
        })
        .catch(error => console.error("Error fetching drone data:", error));
}

// Function to update or create a drone marker
function updateOrCreateMarker(drone) {
    // Check if the drone has a position object (for Drone J)
    const lat = drone.position ? drone.position.latitude : drone.latitude;
    const lng = drone.position ? drone.position.longitude : drone.longitude;

    if (typeof lat !== 'number' || typeof lng !== 'number') {
        console.warn("Invalid coordinates for drone:", drone.call_sign, drone);
        return;
    }

    if (!droneMarkers[drone.call_sign]) {
        // Create new marker for drone
        droneMarkers[drone.call_sign] = L.marker([lat, lng], { icon: planeIcon }).addTo(map)
            .bindPopup(`Drone ${drone.call_sign}`);
    } else {
        // Update existing marker for drone
        let newLatLng = new L.LatLng(lat, lng);
        droneMarkers[drone.call_sign].setLatLng(newLatLng);
        droneMarkers[drone.call_sign].bindPopup(`Drone ${drone.call_sign}: ${lat.toFixed(4)}, ${lng.toFixed(4)}`);
    }

    // Ensure the map follows the drone by setting the view to the drone's position
    map.setView([lat, lng], 15);

    // Update the drone data box with current data (if it exists)
    const latEl = document.getElementById('drone-latitude');
    const lngEl = document.getElementById('drone-longitude');
    const altEl = document.getElementById('drone-altitude');
    const statusEl = document.getElementById('drone-status');

    if (latEl) latEl.textContent = lat.toFixed(4);
    if (lngEl) lngEl.textContent = lng.toFixed(4);
    if (altEl) altEl.textContent = drone.altitude || 'N/A';
    if (statusEl) statusEl.textContent = drone.status || 'Unknown';
}

// Refresh every 4 seconds
setInterval(fetchDroneData, 4000);

// Initial fetch
fetchDroneData();
