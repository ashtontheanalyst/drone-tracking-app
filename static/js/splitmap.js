// static/js/splitmap.js
document.addEventListener('DOMContentLoaded', function() {
  // ─── CONFIG ────────────────────────────────────────────────────────────────
  var defaultCenter   = [27.7123, -97.3246];
  var defaultZoom     = 14;
  var pollIntervalAll = 2000;  // ms between full-map updates
  var pollIntervalOne = 1000;  // ms between single-map updates

  // ─── SETUP MAPS ────────────────────────────────────────────────────────────
  var mapAll    = L.map('map-all').setView(defaultCenter, defaultZoom);
  var mapSingle = L.map('map-single').setView(defaultCenter, defaultZoom);

  var tileUrl  = 'https://api.maptiler.com/maps/outdoor/{z}/{x}/{y}.png?key=3TdwoUdL48yWggYAxvAE';
  var tileOpts = { attribution: '&copy; <a href="https://www.openmaptiles.org/">OpenMapTiles</a> contributors' };
  L.tileLayer(tileUrl, tileOpts).addTo(mapAll);
  L.tileLayer(tileUrl, tileOpts).addTo(mapSingle);

  var planeIcon = L.icon({
    iconUrl: '/static/images/plane-icon.png',
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -16]
  });

  // ─── STATE ──────────────────────────────────────────────────────────────────
  var droneMarkersAll   = {};   // one marker per drone on the left map
  var droneMarkerSingle = null; // the selected drone on the right map
  var selectedCallSign  = null; // which drone we’re following

  // ─── BUILD LIST & CLICK HANDLERS ────────────────────────────────────────────
  var container = document.getElementById('drone-data-container');
  window.droneCallSigns.forEach(function(cs, i) {
    var el = document.createElement('div');
    el.className    = 'drone-summary';
    el.id           = 'summary-' + cs;
    el.style.cursor = 'pointer';
    el.innerHTML    = `<strong>${cs}</strong><br><span id="pos-${cs}">--</span>`;

    el.addEventListener('click', function() {
      // mark selection
      selectedCallSign = cs;
      document.querySelectorAll('.drone-summary')
              .forEach(d => d.classList.remove('selected'));
      el.classList.add('selected');

      // immediately fetch & center that one
      fetchSingle();
    });

    container.appendChild(el);

    // auto-select the first drone on load
    if (i === 0) {
      selectedCallSign = cs;
      el.classList.add('selected');
    }
  });

  // ─── FETCH & RENDER ALL DRONES ──────────────────────────────────────────────
  function fetchAll() {
    Promise.all(
      window.droneCallSigns.map(function(cs) {
        return fetch('/data/' + cs)
          .then(r => r.json())
          .then(hist => ({ cs, hist }))
          .catch(() => ({ cs, hist: [] }));
      })
    ).then(function(results) {
      results.forEach(function(item) {
        var cs   = item.cs;
        var hist = item.hist;
        if (Array.isArray(hist) && hist.length) {
          updateAll(hist[hist.length - 1]);
        }
      });
      fitAllBounds();
    });
  }

  function updateAll(pkt) {
    var lat = pkt.position.latitude,
        lng = pkt.position.longitude,
        hdg = pkt.velocity.track,
        cs  = pkt.call_sign;

    var m = droneMarkersAll[cs];
    if (!m) {
      m = L.marker([lat, lng], {
            icon: planeIcon,
            rotationAngle: hdg,
            rotationOrigin: 'center center'
          })
          .addTo(mapAll)
          .bindPopup(`Drone ${cs}`)
          .on('click', function() {
            // clicking a marker = clicking its summary
            document.getElementById('summary-' + cs).click();
          });
      droneMarkersAll[cs] = m;
    } else {
      m.setLatLng([lat, lng])
       .setRotationAngle(hdg)
       .getPopup()
       .setContent(`Drone ${cs}<br>${lat.toFixed(4)}, ${lng.toFixed(4)}`);
    }

    // update the little text under the summary
    var pe = document.getElementById('pos-' + cs);
    if (pe) pe.textContent = lat.toFixed(4) + ', ' + lng.toFixed(4);
  }

  function fitAllBounds() {
    var ms = Object.values(droneMarkersAll);
    if (!ms.length) return;
    var fg = L.featureGroup(ms);
    mapAll.fitBounds(fg.getBounds().pad(0.2));
  }

  // ─── FETCH & RENDER JUST THE SELECTED DRONE ────────────────────────────────
  function fetchSingle() {
    if (!selectedCallSign) return;
    fetch('/data/' + selectedCallSign)
      .then(r => r.json())
      .then(function(hist) {
        if (Array.isArray(hist) && hist.length) {
          updateSingle(hist[hist.length - 1]);
        }
      })
      .catch(console.error);
  }

  function updateSingle(pkt) {
    var lat = pkt.position.latitude,
        lng = pkt.position.longitude,
        hdg = pkt.velocity.track,
        cs  = pkt.call_sign;

    // create or move & rotate marker (mirror of map.js)
    if (!droneMarkerSingle) {
      droneMarkerSingle = L.marker([lat, lng], {
        icon: planeIcon,
        rotationAngle: hdg,
        rotationOrigin: 'center center'
      })
      .addTo(mapSingle)
      .bindPopup(`Drone ${cs}`);
    } else {
      droneMarkerSingle
        .setLatLng([lat, lng])
        .setRotationAngle(hdg)
        .getPopup()
        .setContent(`Drone ${cs}<br>${lat.toFixed(4)}, ${lng.toFixed(4)}`);
    }

    // — ensure the right map recenters on every update:
    mapSingle.panTo([lat, lng], { animate: false });
    droneMarkerSingle.openPopup();
  }

  // ─── START YOUR POLLING LOOPS ──────────────────────────────────────────────
  fetchAll();
  setInterval(fetchAll, pollIntervalAll);

  fetchSingle();
  setInterval(fetchSingle, pollIntervalOne);
});

