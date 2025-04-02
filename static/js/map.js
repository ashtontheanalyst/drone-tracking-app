// Initialize map with a default center
var map = L.map('map').setView([27.7123, -97.3246], 12);

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

    if (url === "/drone1") {
        endpoint = "/drone1-data";  // Only fetch Drone 1's data
    }

    if (url === "/drone2") {
        endpoint = "/drone2-data";  // Only fetch Drone 2's data
    }

    if (url === "/drone3") {
        endpoint = "/drone3-data";  // Only fetch Drone 3's data
    }

    if (url === "/drone4") {
        endpoint = "/drone4-data";  // Only fetch Drone 4's data
    }

    if (url === "/droneJ") {
        endpoint = "/droneJ-data";// find the global var. for drone J
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
    if (!droneMarkers[drone.id]) {
        // Create new marker for drone
        droneMarkers[drone.id] = L.marker([drone.lat, drone.lon], { icon: planeIcon }).addTo(map)
            .bindPopup(`Drone ${drone.id}`);
    } else {
        // Update existing marker for drone
        let newLatLng = new L.LatLng(drone.lat, drone.lon);
        droneMarkers[drone.id].setLatLng(newLatLng);
        droneMarkers[drone.id].bindPopup(`Drone ${drone.id}: ${drone.lat.toFixed(4)}, ${drone.lon.toFixed(4)}`).openPopup();
    }
}

// Refresh every 4 seconds
setInterval(fetchDroneData, 4000);

// Initial fetch
fetchDroneData();

