import { useEffect, useRef, useState } from 'react';

const MAP_HTML = `<!DOCTYPE html>
<html><head>
<meta charset="utf-8"/>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<style>body{margin:0}#map{height:100vh;width:100%;cursor:crosshair}</style>
</head><body>
<div id="map"></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const map = L.map('map').setView([20, 0], 2);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {attribution: '© OpenStreetMap'}).addTo(map);
let marker = null;

function setMarker(lat, lng) {
  if (marker) { marker.setLatLng([lat, lng]); }
  else {
    marker = L.marker([lat, lng], {draggable: true}).addTo(map);
    marker.on('dragend', e => { const p = e.target.getLatLng(); send(p.lat, p.lng); });
  }
}
function send(lat, lng) { window.parent.postMessage({ type: 'coords', lat, lng }, '*'); }

map.on('click', e => { setMarker(e.latlng.lat, e.latlng.lng); send(e.latlng.lat, e.latlng.lng); });

window.addEventListener('message', e => {
  if (e.data?.type === 'panTo') {
    map.setView([e.data.lat, e.data.lng], 13);
    setMarker(e.data.lat, e.data.lng);
  }
});
</script>
</body></html>`;

export default function MapPicker({ lat, lng, onChange }) {
  const iframeRef = useRef(null);
  const onChangeRef = useRef(onChange);
  const initialRef = useRef({ lat, lng });
  const [search, setSearch] = useState('');
  const [searching, setSearching] = useState(false);
  const [noResults, setNoResults] = useState(false);

  useEffect(() => { onChangeRef.current = onChange; });

  useEffect(() => {
    function onMessage(e) {
      if (e.data?.type === 'coords') onChangeRef.current(e.data.lat, e.data.lng);
    }
    window.addEventListener('message', onMessage);
    return () => window.removeEventListener('message', onMessage);
  }, []);

  function handleLoad() {
    const { lat: initLat, lng: initLng } = initialRef.current;
    if (initLat != null && initLng != null) {
      iframeRef.current?.contentWindow?.postMessage(
        { type: 'panTo', lat: Number(initLat), lng: Number(initLng) }, '*'
      );
    }
  }

  async function handleSearch() {
    if (!search.trim()) return;
    setSearching(true);
    setNoResults(false);
    try {
      const res = await fetch(
        `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(search)}&format=json&limit=1`,
        { headers: { 'Accept-Language': 'en', 'User-Agent': 'sediment-sample-catalogue' } }
      );
      const data = await res.json();
      if (data.length > 0) {
        const newLat = parseFloat(data[0].lat);
        const newLng = parseFloat(data[0].lon);
        iframeRef.current?.contentWindow?.postMessage({ type: 'panTo', lat: newLat, lng: newLng }, '*');
        onChangeRef.current(newLat, newLng);
      } else {
        setNoResults(true);
      }
    } catch {
      setNoResults(true);
    } finally {
      setSearching(false);
    }
  }

  return (
    <div>
      <div className="inline-form-sm mb-2">
        <input
          type="search"
          value={search}
          onChange={e => { setSearch(e.target.value); setNoResults(false); }}
          onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); handleSearch(); } }}
          placeholder="Search for a location…"
          autoComplete="off"
          data-1p-ignore
          className="barcode-input"
        />
        <button type="button" className="btn btn-secondary" disabled={searching || !search.trim()} onClick={handleSearch}>
          {searching ? '…' : 'Search'}
        </button>
      </div>
      {noResults && <p className="form-error">No results found.</p>}
      <div className="map-container">
        <iframe
          ref={iframeRef}
          title="Pick location"
          width="100%"
          height="300"
          className="iframe-clean"
          srcDoc={MAP_HTML}
          onLoad={handleLoad}
        />
      </div>
      <p className="map-hint">Click the map or drag the pin to set coordinates.</p>
    </div>
  );
}
