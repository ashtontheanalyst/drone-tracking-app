// static/js/map.js  (individual‐drone page)
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
// flat‐earth bearing helper
let prevPt = null;
function bearingFlat(p1, p2) {
  const toRad = d => d * Math.PI / 180;
  const toDeg = r => r * 180 / Math.PI;
  const φ1   = toRad(p1.lat),
        φ2   = toRad(p2.lat),
        dLat = φ2 - φ1,
        dLon = toRad(p2.lng - p1.lng) * Math.cos((φ1 + φ2) / 2);
  let θ = Math.atan2(dLon, dLat);
  return (toDeg(θ) + 360) % 360;
}

const pathLine = L.polyline([], { color: 'darkblue', weight: 3 }).addTo(map);
let droneMarker = null;

function refreshDrone() {
  const cs = window.location.pathname.split('/').pop();
  fetch('/data/' + cs)
    .then(r => r.json())
    .then(history => {
      if (!Array.isArray(history) || !history.length) return;
      const coords = history.map(pt => [pt.position.latitude, pt.position.longitude]);
      pathLine.setLatLngs(coords);
      updateMarker(history[history.length - 1]);
    })
    .catch(console.error);
}

function updateMarker(pkt) {
  const lat = pkt.position.latitude;
  const lng = pkt.position.longitude;

  // direct bearing from last point
  const hdg = prevPt
    ? bearingFlat(prevPt, { lat, lng })
    : 0;
  prevPt = { lat, lng };

  if (!droneMarker) {
    droneMarker = L.marker([lat, lng], {
      icon: planeIcon,
      rotationAngle: hdg,
      rotationOrigin: 'center center'
    })
    .addTo(map)
    .bindPopup(`Drone ${pkt.call_sign}`);
  } else {
    droneMarker
      .setLatLng([lat, lng])
      .setRotationAngle(hdg)
      .getPopup().setContent(`Drone ${pkt.call_sign}<br>${lat.toFixed(4)}, ${lng.toFixed(4)}`);
  }
  map.panTo([lat, lng], { animate: false });
}

// kick it off
refreshDrone();
setInterval(refreshDrone, 1000);
