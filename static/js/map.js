// static/js/map.js
// (for individual‐drone pages; rotates the plane to its track)
var map = L.map('map').setView([27.7123, -97.3246], 14);

var droneMarkers = {};

var planeIcon = L.icon({
  iconUrl: '/static/images/plane-icon.png',
  iconSize: [32, 32],
  iconAnchor: [16, 16],
  popupAnchor: [0, -16]
});

L.tileLayer(
  'https://api.maptiler.com/maps/outdoor/{z}/{x}/{y}.png?key=3TdwoUdL48yWggYAxvAE',
  { attribution: '&copy; <a href="https://www.openmaptiles.org/">OpenMapTiles</a> contributors' }
).addTo(map);

function fetchDroneData() {
  var callSign = window.location.pathname.split('/').pop();
  fetch('/data/' + callSign)
    .then(res => res.json())
    .then(history => {
      if (!Array.isArray(history) || history.length === 0) return;
      updateOrCreateMarker(history[history.length - 1]);
    })
    .catch(console.error);
}

function updateOrCreateMarker(pkt) {
  var lat = pkt.position.latitude,
      lng = pkt.position.longitude,
      cs  = pkt.call_sign,
      hdg = pkt.velocity.track;

  if (!droneMarkers[cs]) {
    droneMarkers[cs] = L.marker([lat, lng], {
      icon: planeIcon,
      rotationAngle: hdg,
      rotationOrigin: 'center center'
    })
    .addTo(map)
    .bindPopup(`Drone ${cs}`);
  } else {
    droneMarkers[cs]
      .setLatLng([lat, lng])
      .setRotationAngle(hdg)
      .getPopup()
      .setContent(`Drone ${cs}<br>${lat.toFixed(4)}, ${lng.toFixed(4)}`);
  }

  map.setView([lat, lng], 15);
}

setInterval(fetchDroneData, 1000);
fetchDroneData();

