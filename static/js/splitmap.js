// static/js/splitmap.js
document.addEventListener('DOMContentLoaded', function() {
  // ─── CONFIG ────────────────────────────────────────────────────────────────
  const defaultCenter   = [27.7123, -97.3246];
  const defaultZoom     = 14;
  const pollIntervalAll = 2000;  // ms between full‐map updates
  const pollIntervalOne = 1000;  // ms between single‐map updates

  // ─── SETUP MAPS ────────────────────────────────────────────────────────────
  const mapAll    = L.map('map-all')   .setView(defaultCenter, defaultZoom);
  const mapSingle = L.map('map-single').setView(defaultCenter, defaultZoom);

  const tileUrl  = 'https://api.maptiler.com/maps/outdoor/{z}/{x}/{y}.png?key=jU54ne5D7wcPIuhFGLb4';
  const tileOpts = { attribution: '&copy; <a href="https://www.openmaptiles.org/">OpenMapTiles</a> contributors' };
  L.tileLayer(tileUrl, tileOpts).addTo(mapAll);
  L.tileLayer(tileUrl, tileOpts).addTo(mapSingle);

  const planeIcon = L.icon({
    iconUrl: '/static/images/plane-icon.png',
    iconSize: [32,32],
    iconAnchor: [16,16],
    popupAnchor: [0,-16]
  });

  // ─── STATE ──────────────────────────────────────────────────────────────────
  const droneMarkersAll   = {};   // one marker per drone
  let   droneMarkerSingle = null; // the one we follow
  let   selectedCallSign  = null; // current selection
  const pathSingle        = L.polyline([], { color: 'crimson', weight: 3 }).addTo(mapSingle); // <— add this line
  // label element + helper
  const labelEl = document.getElementById('zoomed-drone-label');
  function setFocusedDrone(cs){
    if (!labelEl) return;
    labelEl.textContent = cs ? `Zoomed drone: ${cs}` : 'Zoomed drone: —';
  }
  // ─── BUILD SUMMARY LIST ─────────────────────────────────────────────────────
  const container = document.getElementById('drone-data-container');
  window.droneCallSigns.forEach((cs, i) => {
    const el = document.createElement('div');
    el.className    = 'drone-summary';
    el.id           = 'summary-' + cs;
    el.style.cursor = 'pointer';
    el.innerHTML    = `<strong>${cs}</strong><br><span id="pos-${cs}">--</span>`;

    el.onclick = () => {
      // highlight
      document.querySelectorAll('.drone-summary').forEach(d => d.classList.remove('selected'));
      el.classList.add('selected');
      selectedCallSign = cs;
      setFocusedDrone(cs);
      // clear existing trail
      pathSingle.setLatLngs([]);
      // immediately fetch & draw new history+marker
      fetchSingle();
    };

    container.appendChild(el);

    // auto‐select first drone
    if (i === 0) {
      el.classList.add('selected');
      selectedCallSign = cs;
      setFocusedDrone(cs);
    }
  });


  // ─── ALL DRONES (left map) ─────────────────────────────────────────────────
  function fetchAll() {
    Promise.all(
      window.droneCallSigns.map(cs =>
        fetch('/data/'+cs).then(r=>r.json()).then(hist=>({cs,hist}))
      )
    )
    .then(results => {
      results.forEach(({cs,hist}) => {
        if (!Array.isArray(hist) || !hist.length) return;
        const last = hist[hist.length-1];
        updateAll(last);
      });
      fitAllBounds();
    });
  }

  function updateAll(pkt) {
    const { latitude:lat, longitude:lng } = pkt.position;
    const hdg = pkt.velocity.track;
    let m = droneMarkersAll[pkt.call_sign];
    if (!m) {
      m = L.marker([lat,lng], {
            icon: planeIcon,
            rotationAngle: hdg,
            rotationOrigin: 'center center'
          })
          .addTo(mapAll)
          .bindPopup(`Drone ${pkt.call_sign}`)
          .on('click', () => document.getElementById('summary-'+pkt.call_sign).click());
      droneMarkersAll[pkt.call_sign] = m;
    } else {
      m.setLatLng([lat,lng]).setRotationAngle(hdg)
       .getPopup().setContent(`Drone ${pkt.call_sign}<br>${lat.toFixed(4)}, ${lng.toFixed(4)}`);
    }
    document.getElementById('pos-'+pkt.call_sign).textContent = `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
  }

  function fitAllBounds() {
    const markers = Object.values(droneMarkersAll);
    if (!markers.length) return;
    const group = L.featureGroup(markers);
    mapAll.fitBounds(group.getBounds().pad(0.2));
  }


  // ─── SINGLE SELECTED DRONE (right map) ────────────────────────────────────
  function fetchSingle() {
    if (!selectedCallSign) return;
    fetch('/data/'+selectedCallSign)
      .then(r => r.json())
      .then(hist => {
        if (!Array.isArray(hist) || !hist.length) return;
        // draw full trail
        const coords = hist.map(pt => [pt.position.latitude, pt.position.longitude]);
        pathSingle.setLatLngs(coords);
        // update marker to last point
        updateSingle(hist[hist.length-1]);
      })
      .catch(console.error);
  }

  function updateSingle(pkt) {
    const { latitude:lat, longitude:lng } = pkt.position;
    const hdg = pkt.velocity.track;
    if (!droneMarkerSingle) {
      droneMarkerSingle = L.marker([lat,lng], {
        icon: planeIcon,
        rotationAngle: hdg,
        rotationOrigin: 'center center'
      })
      .addTo(mapSingle)
      .bindPopup(`Drone ${pkt.call_sign}`);
    } else {
      droneMarkerSingle
        .setLatLng([lat,lng])
        .setRotationAngle(hdg)
        .getPopup().setContent(`Drone ${pkt.call_sign}<br>${lat.toFixed(4)}, ${lng.toFixed(4)}`);
    }
    // center
    mapSingle.panTo([lat,lng], { animate: false });
    setFocusedDrone(pkt.call_sign);
  }


  // ─── START POLLING ────────────────────────────────────────────────────────
  fetchAll();
  setInterval(fetchAll, pollIntervalAll);

  fetchSingle();
  setInterval(fetchSingle, pollIntervalOne);
});
