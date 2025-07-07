// static/js/map.js  (for the individual‐drone page)
const map = L.map('map').setView([27.7123, -97.3246], 14);

const planeIcon = L.icon({
  iconUrl: '/static/images/plane-icon.png',
  iconSize: [32,32],
  iconAnchor: [16,16],
  popupAnchor: [0,-16]
});

L.tileLayer(
  'https://api.maptiler.com/maps/outdoor/{z}/{x}/{y}.png?key=jU54ne5D7wcPIuhFGLb4',
  { attribution: '&copy; <a href="https://www.openmaptiles.org/">OpenMapTiles</a> contributors' }
).addTo(map);

// this will hold our past positions
const pathLine = L.polyline([], { color: 'darkblue', weight: 3 }).addTo(map);
let droneMarker = null;

function refreshDrone() {
  const cs = window.location.pathname.split('/').pop();
  fetch('/data/' + cs)
    .then(r => r.json())
    .then(history => {
      if (!Array.isArray(history) || !history.length) return;
      // rebuild the entire trail
      const coords = history.map(pt => [pt.position.latitude, pt.position.longitude]);
      pathLine.setLatLngs(coords);
      // move/update the plane at the end
      const last = history[history.length-1];
      updateMarker(last);
    })
    .catch(console.error);
}

function updateMarker(pkt) {
  const { latitude:lat, longitude:lng } = pkt.position;
  const hdg = pkt.velocity.track;
  if (!droneMarker) {
    droneMarker = L.marker([lat,lng], {
      icon: planeIcon,
      rotationAngle: hdg,
      rotationOrigin: 'center center'
    })
    .addTo(map)
    .bindPopup(`Drone ${pkt.call_sign}`);
  } else {
    droneMarker
      .setLatLng([lat,lng])
      .setRotationAngle(hdg)
      .getPopup().setContent(`Drone ${pkt.call_sign}<br>${lat.toFixed(4)}, ${lng.toFixed(4)}`);
  }
  map.panTo([lat,lng], { animate: false });
}

// kick it off
refreshDrone();
setInterval(refreshDrone, 1000);

