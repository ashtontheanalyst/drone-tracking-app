// splitmap.js
// Initialize left map (#map-all) with all drones
var mapAll = L.map('map-all').setView([27.7623, -97.3246], 11);
// Initialize right map (#map-single) with default view centered on first drone
var defaultCoords = [27.7123, -97.3246];
var mapSingle = L.map('map-single').setView(defaultCoords, 14);

// Retrieve all callsigns injected by index.html
const drones = window.droneCallSigns;

// Store markers keyed by callsign for both maps
var allMarkers    = {};
var singleMarker  = null;
var selectedCS    = drones[0];  // default to first in list

// Custom plane icon
var planeIcon = L.icon({
  iconUrl: '/static/images/plane-icon.png',
  iconSize: [32, 32],
  iconAnchor: [16, 16],
  popupAnchor: [0, -16]
});

// Tile layer for both maps
L.tileLayer('https://api.maptiler.com/maps/outdoor/{z}/{x}/{y}.png?key=3TdwoUdL48yWggYAxvAE', {
  attribution: '&copy; <a href="https://www.openmaptiles.org/">OpenMapTiles</a> contributors'
}).addTo(mapAll);
L.tileLayer('https://api.maptiler.com/maps/outdoor/{z}/{x}/{y}.png?key=3TdwoUdL48yWggYAxvAE', {
  attribution: '&copy; <a href="https://www.openmaptiles.org/">OpenMapTiles</a> contributors'
}).addTo(mapSingle);

// Place placeholder markers for each drone on left map
drones.forEach(cs => {
  // start each at defaultCoords until real data arrives
  var m = L.marker(defaultCoords, { icon: planeIcon })
            .addTo(mapAll)
            .bindPopup(`Drone ${cs}`)
            .on('click', () => {
              selectedCS = cs;
              // when clicked, move/zoom single map to that drone’s location
              if (allMarkers[cs]) {
                var latlng = allMarkers[cs].getLatLng();
                if (!singleMarker) {
                  singleMarker = L.marker(latlng, { icon: planeIcon }).addTo(mapSingle);
                } else {
                  singleMarker.setLatLng(latlng);
                }
                mapSingle.setView(latlng, 14);
              }
            });
  allMarkers[cs] = m;
});

// Fetch & update all markers every second
function updateAllDrones() {
  drones.forEach(cs => {
    fetch(`/data/${cs}`)
      .then(res => res.json())
      .then(history => {
        if (!Array.isArray(history) || history.length === 0) return;
        var latest = history[history.length - 1];
        var lat = latest.position.latitude;
        var lng = latest.position.longitude;
        var latlng = [lat, lng];

        // left-map marker update
        if (!allMarkers[cs]) {
          allMarkers[cs] = L.marker(latlng, { icon: planeIcon }).addTo(mapAll).bindPopup(`Drone ${cs}`);
        } else {
          allMarkers[cs].setLatLng(latlng).getPopup().setContent(`Drone ${cs}<br>${lat.toFixed(4)}, ${lng.toFixed(4)}`);
        }

        // adjust left map bounds to include all markers
        var bounds = L.latLngBounds(Object.values(allMarkers).map(m => m.getLatLng()));
        if (bounds.isValid()) {
          mapAll.fitBounds(bounds, { padding: [50, 50], maxZoom: 16 });
        }

        // if this is the currently selected drone, update right map as well
        if (cs === selectedCS) {
          if (!singleMarker) {
            singleMarker = L.marker(latlng, { icon: planeIcon }).addTo(mapSingle);
          } else {
            singleMarker.setLatLng(latlng);
          }
          mapSingle.setView(latlng, 14);
        }
      })
      .catch(console.error);
  });
}

setInterval(updateAllDrones, 1000);
updateAllDrones();

